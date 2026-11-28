using System.Runtime.InteropServices;
using System.Text.Json;

namespace Confectory.Core;

// Read-only recovery facts for a future host-owned direct-data transaction.
// This component neither stages nor writes project sources. In particular,
// inspecting a pending operation never authorizes retrying the source write.
public sealed record DirectDataSaveIntent(
    string OperationId,
    string ProjectFingerprint,
    string OwnerFingerprint,
    string SourceIdentity,
    string BeforeHash,
    string CandidateHash,
    string CheckpointFingerprint,
    string RequestFingerprint);

// The existing authoritative commit path must supply this after it actually
// commits the exact intent. A matching file hash alone is not commit evidence.
public sealed record DirectDataCommitEvidence(
    string IntentFingerprint,
    string CommittedHash,
    string AuthorityFingerprint);

public enum DirectDataReceiptState
{
    NoIntent,
    Admitted,
    Pending,
    CompletedHistorical,
    ConflictingIdentity,
    BlockedByPending,
    RecoveryRequired
}

// Foundation only: no editor IPC endpoint or product save caller uses this
// journal yet. A caller provides an already-owned private recovery directory
// for one exact project and owner. Linux writes have file and directory fsync;
// other platforms must provide a verified durability implementation first.
public sealed class DirectDataReceiptJournal
{
    private const string Format = "confectory-direct-data-receipt-v1";
    private const int MaxOperations = 64, MaxRecordBytes = 32768;
    private const string LockName = "journal.lock";
    private readonly string directory, projectFingerprint, ownerFingerprint;
    private sealed record Entry(DirectDataSaveIntent Intent, DirectDataCommitEvidence? Completion);

    public DirectDataReceiptJournal(string directory, string projectFingerprint, string ownerFingerprint)
    {
        if (!Path.IsPathFullyQualified(directory) || !Hash(projectFingerprint) || !Hash(ownerFingerprint))
            throw new ArgumentException("Explicit owned recovery scope required.");
        this.directory = Path.GetFullPath(directory);
        this.projectFingerprint = projectFingerprint;
        this.ownerFingerprint = ownerFingerprint;
    }

    public static string Fingerprint(DirectDataSaveIntent intent) => JsonData.Digest(intent);

    // NoIntent is an observation, not admission. A caller must not turn
    // recovery of a lost request into a new write merely because it is absent.
    public DirectDataReceiptState Inspect(DirectDataSaveIntent intent)
    {
        Validate(intent);
        return FailClosed(() =>
        {
            VerifyDirectory();
            if (!Exists(At(LockName)))
                return HasRecords() ? DirectDataReceiptState.RecoveryRequired : DirectDataReceiptState.NoIntent;
            using var guard = Acquire(false);
            return Find(Scan(), intent, out _);
        });
    }

    // A commit authority can inspect the exact expected attestation without
    // publishing a receipt or changing the existing journal. This is also
    // useful when a durable commit primitive has independently bound its
    // prepared record to the authority fingerprint.
    public DirectDataReceiptState InspectCompletion(DirectDataSaveIntent intent, DirectDataCommitEvidence expected)
    {
        Validate(intent);
        if (!Matches(intent, expected)) return DirectDataReceiptState.ConflictingIdentity;
        return FailClosed(() =>
        {
            VerifyDirectory();
            if (!Exists(At(LockName)))
                return HasRecords() ? DirectDataReceiptState.RecoveryRequired : DirectDataReceiptState.NoIntent;
            using var guard = Acquire(false);
            var status = Find(Scan(), intent, out var row);
            return status == DirectDataReceiptState.CompletedHistorical && row!.Completion != expected
                ? DirectDataReceiptState.ConflictingIdentity : status;
        });
    }

    // Only an explicitly new host admission can create an intent. Pending or
    // historical duplicates are observations and never return Admitted again.
    public DirectDataReceiptState Admit(DirectDataSaveIntent intent)
    {
        Validate(intent);
        return FailClosed(() =>
        {
            RequireLinuxWriter();
            VerifyDirectory();
            if (!Exists(At(LockName)) && HasRecords()) return DirectDataReceiptState.RecoveryRequired;
            using var guard = Acquire(true);
            var entries = Scan();
            var existing = Find(entries, intent, out _);
            if (existing != DirectDataReceiptState.NoIntent) return existing;
            if (entries.Values.Any(row => row.Completion is null)) return DirectDataReceiptState.BlockedByPending;
            if (entries.Count >= MaxOperations) return DirectDataReceiptState.RecoveryRequired;
            Write(IntentPath(intent.OperationId), "intent", intent);
            return DirectDataReceiptState.Admitted;
        });
    }

    // This is a trusted commit-attestation boundary, not an operation that
    // checks current file bytes and guesses whether a commit happened.
    public DirectDataReceiptState RecordCompletion(DirectDataSaveIntent intent, DirectDataCommitEvidence evidence)
    {
        Validate(intent);
        if (!Matches(intent, evidence)) return DirectDataReceiptState.ConflictingIdentity;
        return FailClosed(() =>
        {
            RequireLinuxWriter();
            VerifyDirectory();
            if (!Exists(At(LockName)))
                return HasRecords() ? DirectDataReceiptState.RecoveryRequired : DirectDataReceiptState.NoIntent;
            using var guard = Acquire(false);
            var entries = Scan();
            var existing = Find(entries, intent, out var row);
            if (existing == DirectDataReceiptState.CompletedHistorical)
                return row!.Completion == evidence ? existing : DirectDataReceiptState.ConflictingIdentity;
            if (existing != DirectDataReceiptState.Pending) return existing;
            if (entries.Values.Count(value => value.Completion is null) != 1)
                return DirectDataReceiptState.RecoveryRequired;
            Write(CompletionPath(intent.OperationId), "completion", evidence);
            return DirectDataReceiptState.CompletedHistorical;
        });
    }

    private static DirectDataReceiptState FailClosed(Func<DirectDataReceiptState> action)
    {
        // Unknown, unreadable or corrupt recovery state is never an empty
        // journal and never an instruction to re-execute the source mutation.
        try { return action(); }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or JsonException or
            InvalidOperationException or ArgumentException or NotSupportedException or DllNotFoundException or EntryPointNotFoundException)
        { return DirectDataReceiptState.RecoveryRequired; }
    }

    private void Validate(DirectDataSaveIntent intent)
    {
        ArgumentNullException.ThrowIfNull(intent);
        if (!Id(intent.OperationId) || intent.ProjectFingerprint != projectFingerprint ||
            intent.OwnerFingerprint != ownerFingerprint || !Hash(intent.SourceIdentity) ||
            !Hash(intent.BeforeHash) || !Hash(intent.CandidateHash) ||
            intent.BeforeHash == intent.CandidateHash || !Hash(intent.CheckpointFingerprint) ||
            !Hash(intent.RequestFingerprint))
            throw new ArgumentException("Exact existing-source transaction identity required.");
    }

    private static bool Matches(DirectDataSaveIntent intent, DirectDataCommitEvidence? evidence) =>
        evidence is not null && evidence.IntentFingerprint == Fingerprint(intent) &&
        evidence.CommittedHash == intent.CandidateHash && Hash(evidence.AuthorityFingerprint);

    private static bool Id(string? value) => value is not null &&
        Guid.TryParseExact(value, "N", out var id) && id != Guid.Empty && id.ToString("N") == value;
    private static bool Hash(string? value) => value is { Length: 64 } &&
        value.All(c => c is >= '0' and <= '9' or >= 'a' and <= 'f');

    private static DirectDataReceiptState Find(Dictionary<string, Entry> entries, DirectDataSaveIntent intent, out Entry? row)
    {
        if (!entries.TryGetValue(intent.OperationId, out row)) return DirectDataReceiptState.NoIntent;
        if (row.Intent != intent) return DirectDataReceiptState.ConflictingIdentity;
        return row.Completion is null ? DirectDataReceiptState.Pending : DirectDataReceiptState.CompletedHistorical;
    }

    private string At(string name) => Path.Combine(directory, name);
    private string IntentPath(string id) => At(id + ".intent.json");
    private string CompletionPath(string id) => At(id + ".completion.json");

    private void VerifyDirectory()
    {
        for (DirectoryInfo? entry = new(directory); entry is not null; entry = entry.Parent)
        {
            if (!entry.Exists || entry.LinkTarget is not null || (entry.Attributes & FileAttributes.ReparsePoint) != 0)
                throw new IOException("Recovery directory must be existing and physically owned.");
        }
        if (OperatingSystem.IsLinux() &&
            (File.GetUnixFileMode(directory) & (UnixFileMode.GroupRead | UnixFileMode.GroupWrite | UnixFileMode.GroupExecute |
                UnixFileMode.OtherRead | UnixFileMode.OtherWrite | UnixFileMode.OtherExecute)) != 0)
            throw new UnauthorizedAccessException("Recovery directory must be private.");
    }

    private static bool Exists(string path)
    {
        if (new FileInfo(path).LinkTarget is not null) throw new IOException("Recovery link is not allowed.");
        try
        {
            var attributes = File.GetAttributes(path);
            if ((attributes & (FileAttributes.Directory | FileAttributes.ReparsePoint)) != 0)
                throw new IOException("Expected ordinary recovery record.");
            if (OperatingSystem.IsLinux())
            {
                var mode = File.GetUnixFileMode(path);
                if ((mode & UnixFileMode.UserRead) == 0 || (mode & (UnixFileMode.GroupWrite | UnixFileMode.OtherWrite)) != 0)
                    throw new UnauthorizedAccessException("Recovery record is unreadable or shared writable.");
            }
            return true;
        }
        catch (FileNotFoundException) { return false; }
    }

    private bool HasRecords() => Entries().Any(name => name != LockName && !Temporary(name));

    private FileStream Acquire(bool create)
    {
        string path = At(LockName);
        bool existed = Exists(path);
        var stream = new FileStream(path, create ? FileMode.OpenOrCreate : FileMode.Open, FileAccess.ReadWrite, FileShare.None);
        try
        {
            if (!Exists(path)) throw new IOException("Recovery lock unavailable.");
            if (!existed)
            {
                if (OperatingSystem.IsLinux()) File.SetUnixFileMode(path, UnixFileMode.UserRead | UnixFileMode.UserWrite);
                stream.Flush(true);
                FlushDirectory();
            }
            return stream;
        }
        catch { stream.Dispose(); throw; }
    }

    private string[] Entries()
    {
        var names = Directory.EnumerateFileSystemEntries(directory).Select(Path.GetFileName).Take(MaxOperations * 2 + 34).ToArray();
        if (names.Length >= MaxOperations * 2 + 34) throw new IOException("Recovery record budget exceeded.");
        return names.Select(name => name ?? throw new IOException("Recovery record name unavailable.")).ToArray();
    }

    private static bool Temporary(string name)
    {
        // A torn unpublished atomic write is not an intent or completion.
        // Never delete it or infer execution from its content.
        var parts = name.Split('.');
        return parts.Length == 6 && parts[0] == "" && Id(parts[1]) &&
            parts[2] is "intent" or "completion" && parts[3] == "json" && Id(parts[4]) && parts[5] == "tmp";
    }

    private Dictionary<string, Entry> Scan()
    {
        var entries = new Dictionary<string, Entry>(StringComparer.Ordinal);
        var completions = new HashSet<string>(StringComparer.Ordinal);
        foreach (string name in Entries())
        {
            if (name == LockName || Temporary(name)) continue;
            var parts = name.Split('.');
            if (parts.Length != 3 || !Id(parts[0]) || parts[2] != "json" ||
                parts[1] is not ("intent" or "completion")) throw new IOException("Unknown recovery record.");
            if (parts[1] == "completion") { completions.Add(parts[0]); continue; }
            var intent = Read<DirectDataSaveIntent>(At(name), "intent");
            Validate(intent);
            if (intent.OperationId != parts[0] || !entries.TryAdd(parts[0], new(intent, null)) || entries.Count > MaxOperations)
                throw new IOException("Recovery intent identity mismatch.");
        }
        foreach (string id in completions)
        {
            if (!entries.TryGetValue(id, out var row)) throw new IOException("Completion without durable intent.");
            var receipt = Read<DirectDataCommitEvidence>(CompletionPath(id), "completion");
            if (!Matches(row.Intent, receipt)) throw new IOException("Recovery completion identity mismatch.");
            entries[id] = row with { Completion = receipt };
        }
        if (entries.Values.Count(row => row.Completion is null) > 1)
            throw new IOException("Ambiguous concurrent recovery intents.");
        return entries;
    }

    private static T Read<T>(string path, string kind)
    {
        if (!Exists(path)) throw new IOException("Recovery record disappeared.");
        using var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read);
        if (stream.Length is <= 0 or > MaxRecordBytes) throw new IOException("Recovery record budget.");
        var raw = new byte[(int)stream.Length];
        stream.ReadExactly(raw);
        if (stream.ReadByte() != -1) throw new IOException("Recovery record changed.");
        using var document = JsonDocument.Parse(raw);
        var root = document.RootElement;
        if (root.ValueKind != JsonValueKind.Object || root.EnumerateObject().Count() != 4 ||
            root.EnumerateObject().Select(item => item.Name).Distinct(StringComparer.Ordinal).Count() != 4 ||
            !root.TryGetProperty("format", out var format) || format.GetString() != Format ||
            !root.TryGetProperty("kind", out var actualKind) || actualKind.GetString() != kind ||
            !root.TryGetProperty("payload", out var payload) || !root.TryGetProperty("checksum", out var checksum))
            throw new IOException("Invalid recovery record envelope.");
        var value = payload.Deserialize<T>(JsonData.Options) ?? throw new IOException("Missing recovery payload.");
        if (JsonData.Digest(payload) != JsonData.Digest(value) ||
            checksum.GetString() != JsonData.Digest(new { format = Format, kind, payload }))
            throw new IOException("Recovery record checksum or shape mismatch.");
        return value;
    }

    private void Write<T>(string path, string kind, T value)
    {
        var payload = JsonSerializer.SerializeToNode(value, JsonData.Options);
        var checksum = JsonData.Digest(new { format = Format, kind, payload });
        byte[] raw = JsonSerializer.SerializeToUtf8Bytes(new { format = Format, kind, payload, checksum }, JsonData.Options);
        if (raw.Length > MaxRecordBytes) throw new IOException("Recovery record budget.");
        string temp = At("." + Path.GetFileName(path) + "." + Guid.NewGuid().ToString("N") + ".tmp");
        try
        {
            using (var stream = new FileStream(temp, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            {
                if (OperatingSystem.IsLinux()) File.SetUnixFileMode(temp, UnixFileMode.UserRead | UnixFileMode.UserWrite);
                stream.Write(raw);
                stream.Flush(true);
            }
            // Never replace an existing intent or receipt, including an
            // operation with the same ID but a different payload.
            File.Move(temp, path, false);
            FlushDirectory();
        }
        finally { if (File.Exists(temp)) File.Delete(temp); }
    }

    private static void RequireLinuxWriter()
    {
        if (!OperatingSystem.IsLinux()) throw new PlatformNotSupportedException("Verified directory durability is Linux-only in this foundation.");
    }

    private void FlushDirectory()
    {
        RequireLinuxWriter();
        // Linux O_DIRECTORY ensures the handle names a directory. fsync
        // persists the atomic name publication, not just the file contents.
        int fd = Open(directory, 0x10000);
        if (fd < 0) throw new IOException("Cannot open recovery directory for sync.");
        try { if (Sync(fd) != 0) throw new IOException("Cannot sync recovery directory."); }
        finally { _ = Close(fd); }
    }

    [DllImport("libc", EntryPoint = "open", SetLastError = true)] private static extern int Open(string path, int flags);
    [DllImport("libc", EntryPoint = "fsync", SetLastError = true)] private static extern int Sync(int fd);
    [DllImport("libc", EntryPoint = "close", SetLastError = true)] private static extern int Close(int fd);
}
