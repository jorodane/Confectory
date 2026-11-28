using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Text.Json;
using Microsoft.Win32.SafeHandles;

[assembly: InternalsVisibleTo("direct-data-exchange")]

namespace Confectory.Core;

// Standalone Linux experimental primitive, NOT connected to editor Save.
// It couples a single existing-file atomic exchange to a durable intent and
// two pinned inode witnesses. The journal never infers success from bytes.
public enum DurableLocalEditState
{
    NoIntent, SourceConflict, PendingUncertain, PreparedNotExchanged,
    WitnessedExchange, CompletedHistorical, ConflictingIdentity,
    BlockedByPending, RecoveryRequired, UnsupportedPlatform
}

public sealed record DurableLocalSource(string SourceIdentity, string BeforeHash);

public sealed class DurableLocalDataExchange
{
    private const int MaxBytes = 2 * 1024 * 1024;
    private const int MaxRecordBytes = 32768;
    private const string Format = "confectory-local-exchange-v1";
    private const int AT_FDCWD = -100, AT_SYMLINK_NOFOLLOW = 0x100, AT_EMPTY_PATH = 0x1000;
    private const int O_NONBLOCK = 0x800, O_DIRECTORY = 0x10000, O_NOFOLLOW = 0x20000, O_CLOEXEC = 0x80000;
    private const uint RENAME_EXCHANGE = 2, STATX_BASIC_STATS = 0x7ff;
    private readonly string root, relative, source, recovery, journalDirectory, operations, leasePath;
    private readonly string projectFingerprint, ownerFingerprint;
    private readonly DirectDataReceiptJournal journal;

    private sealed record Identity(uint DeviceMajor, uint DeviceMinor, ulong Inode);
    private sealed record FileFact(Identity Identity, string Hash, uint Uid, uint Gid, ushort Mode, uint Links);
    private sealed record Prepared(string IntentFingerprint, string Relative,
        FileFact Original, FileFact Candidate);
    private sealed record PreparedEnvelope(string Format, Prepared Payload, string Checksum);

    // The caller supplies an already-owned, private, existing recovery area
    // below .confectory, with existing "journal" and "operations" subfolders.
    // No production storage location/retention policy is chosen by this type.
    public DurableLocalDataExchange(string root, string relative, string recovery,
        string projectFingerprint, string ownerFingerprint)
    {
        if (!Path.IsPathFullyQualified(root) || !Path.IsPathFullyQualified(recovery) ||
            !Hash(projectFingerprint) || !Hash(ownerFingerprint))
            throw new ArgumentException("Explicit owned transaction scope required.");
        this.root = Path.GetFullPath(root);
        if (string.IsNullOrWhiteSpace(relative) || Path.IsPathRooted(relative))
            throw new ArgumentException("Explicit owned relative source required.");
        source = Path.GetFullPath(Path.Combine(this.root, relative));
        this.relative = Path.GetRelativePath(this.root, source);
        if (this.relative != relative || !Inside(this.root, source) ||
            this.relative.StartsWith(".confectory" + Path.DirectorySeparatorChar, StringComparison.Ordinal) ||
            !source.EndsWith(".celem", StringComparison.Ordinal))
            throw new ArgumentException("One existing local declaration source required.");
        this.recovery = Path.GetFullPath(recovery);
        string metadata = Path.Combine(this.root, ".confectory");
        if (!Inside(metadata, this.recovery))
            throw new ArgumentException("Recovery must remain in the owned private metadata area.");
        journalDirectory = Path.Combine(this.recovery, "journal");
        operations = Path.Combine(this.recovery, "operations");
        leasePath = Path.Combine(metadata, "source-transaction.lock");
        this.projectFingerprint = projectFingerprint;
        this.ownerFingerprint = ownerFingerprint;
        journal = new(journalDirectory, projectFingerprint, ownerFingerprint);
    }

    // Observe the exact existing inode and bytes before an explicit new edit.
    // This also rejects a same-byte replacement between capture and admission.
    public DurableLocalSource Capture()
    {
        RequireLinux();
        VerifyPaths();
        using var lease = AcquireLease();
        var fact = ReadFact(source);
        CheckOriginal(fact);
        return new(SourceFingerprint(fact), fact.Hash);
    }

    public DurableLocalEditState Commit(DirectDataSaveIntent intent, byte[] candidate) =>
        CommitCore(intent, candidate, null);

    // Deterministic process-kill seam, only available to the isolated probe.
    internal DurableLocalEditState CommitForProbe(DirectDataSaveIntent intent, byte[] candidate, Action<string> boundary) =>
        CommitCore(intent, candidate, boundary);

    private DurableLocalEditState CommitCore(DirectDataSaveIntent intent, byte[] candidate, Action<string>? boundary)
    {
        ValidateIntent(intent);
        ArgumentNullException.ThrowIfNull(candidate);
        // Caller memory cannot change the candidate after hashing/admission.
        if (candidate.Length is <= 0 or > MaxBytes) throw new ArgumentException("Bounded candidate bytes required.");
        candidate = (byte[])candidate.Clone();
        if (JsonData.HashBytes(candidate) != intent.CandidateHash)
            throw new ArgumentException("Exact bounded candidate bytes required.");
        if (!OperatingSystem.IsLinux()) return DurableLocalEditState.UnsupportedPlatform;
        return FailClosed(() =>
        {
            VerifyPaths();
            using var lease = AcquireLease();
            var existing = journal.Inspect(intent);
            if (existing != DirectDataReceiptState.NoIntent)
                return InspectLocked(intent, existing);
            boundary?.Invoke("before-intent");
            var original = ReadFact(source);
            CheckOriginal(original);
            if (SourceFingerprint(original) != intent.SourceIdentity || original.Hash != intent.BeforeHash)
                return DurableLocalEditState.SourceConflict;
            var admitted = journal.Admit(intent);
            if (admitted != DirectDataReceiptState.Admitted)
                return InspectLocked(intent, admitted);
            boundary?.Invoke("after-intent");

            string op = Operation(intent), stage = Stage(intent);
            if (Mkdir(op, 0x1c0) != 0) throw Error("Create private operation directory");
            VerifyPrivate(op);
            FlushDirectory(operations);

            // Retain the actual old inode, not a detached byte-only backup.
            LinkExact(source, OldWitness(intent));
            using (var stream = new FileStream(stage, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            {
                if (OperatingSystem.IsLinux()) File.SetUnixFileMode(stage, (UnixFileMode)(original.Mode & 0x1ff));
                stream.Write(candidate);
                stream.Flush(true);
            }
            LinkExact(stage, NewWitness(intent));
            var oldWitness = ReadFact(OldWitness(intent));
            var newWitness = ReadFact(NewWitness(intent));
            var prepared = new Prepared(DirectDataReceiptJournal.Fingerprint(intent), relative, oldWitness, newWitness);
            if (!SameContentIdentity(original, oldWitness) || oldWitness.Links != 2 ||
                newWitness.Hash != intent.CandidateHash || newWitness.Links != 2 ||
                newWitness.Identity == oldWitness.Identity || newWitness.Mode != oldWitness.Mode ||
                newWitness.Uid != oldWitness.Uid || newWitness.Gid != oldWitness.Gid)
                return DurableLocalEditState.RecoveryRequired;
            // Persist the witness directory and the actual original file.
            FlushFile(OldWitness(intent));
            FlushDirectory(op);
            boundary?.Invoke("after-stage");
            WritePrepared(intent, prepared);
            boundary?.Invoke("after-prepared");
            // The complete intent and witnesses must be durable before the
            // exchange. A changed source is never admitted as successful.
            if (InspectPair(intent, prepared) != DurableLocalEditState.PreparedNotExchanged)
                return DurableLocalEditState.RecoveryRequired;
            boundary?.Invoke("before-exchange");

            // Atomic swap preserves the displaced inode even if a writer
            // outside the cooperative lease races the final comparison.
            // Such a race is explicitly uncertain; never auto-rollback.
            if (RenameExchange(AT_FDCWD, stage, AT_FDCWD, source, RENAME_EXCHANGE) != 0)
                throw Error("Atomic exchange unavailable");
            boundary?.Invoke("after-exchange");
            return SealLocked(intent, prepared, boundary);
        });
    }

    // Pure recovery classification: no source write, no receipt publication,
    // no new admission, no automatic replay.
    public DurableLocalEditState Inspect(DirectDataSaveIntent intent)
    {
        ValidateIntent(intent);
        if (!OperatingSystem.IsLinux()) return DurableLocalEditState.UnsupportedPlatform;
        return FailClosed(() =>
        {
            VerifyPaths();
            using var lease = AcquireLease(create: false);
            return InspectLocked(intent, journal.Inspect(intent));
        });
    }

    // Explicit recovery action. Only seals an already witnessed exchange;
    // never performs or retries a source replacement.
    public DurableLocalEditState SealWitnessed(DirectDataSaveIntent intent)
    {
        ValidateIntent(intent);
        if (!OperatingSystem.IsLinux()) return DurableLocalEditState.UnsupportedPlatform;
        return FailClosed(() =>
        {
            VerifyPaths();
            using var lease = AcquireLease(create: false);
            var status = journal.Inspect(intent);
            if (status != DirectDataReceiptState.Pending)
                return InspectLocked(intent, status);
            if (!File.Exists(PreparedPath(intent))) return DurableLocalEditState.PendingUncertain;
            var prepared = ReadPrepared(intent);
            var pair = InspectPair(intent, prepared);
            if (pair != DurableLocalEditState.WitnessedExchange) return pair;
            return SealLocked(intent, prepared, null);
        });
    }

    private DurableLocalEditState SealLocked(DirectDataSaveIntent intent, Prepared prepared, Action<string>? boundary)
    {
        if (InspectPair(intent, prepared) != DurableLocalEditState.WitnessedExchange)
            return DurableLocalEditState.RecoveryRequired;
        // The staged data was already flushed. Recheck and flush the exact
        // named files and both directories after atomic exchange, then
        // publish only the attestation bound to this prepared inode pair.
        FlushFile(source);
        FlushFile(Stage(intent));
        FlushDirectory(Path.GetDirectoryName(source)!);
        FlushDirectory(Operation(intent));
        boundary?.Invoke("after-directory-sync");
        if (InspectPair(intent, prepared) != DurableLocalEditState.WitnessedExchange)
            return DurableLocalEditState.RecoveryRequired;
        var result = journal.RecordCompletion(intent, Evidence(intent, prepared));
        if (result == DirectDataReceiptState.CompletedHistorical) boundary?.Invoke("after-receipt");
        return Translate(result);
    }

    private DurableLocalEditState InspectLocked(DirectDataSaveIntent intent, DirectDataReceiptState state)
    {
        if (state == DirectDataReceiptState.CompletedHistorical)
        {
            // Completion is historical, not proof the live source remains
            // current. Require the exact durable prepared record/attestation.
            var prepared = ReadPrepared(intent);
            return Translate(journal.InspectCompletion(intent, Evidence(intent, prepared)));
        }
        if (state != DirectDataReceiptState.Pending) return Translate(state);
        if (!File.Exists(PreparedPath(intent))) return DurableLocalEditState.PendingUncertain;
        return InspectPair(intent, ReadPrepared(intent));
    }

    private DurableLocalEditState InspectPair(DirectDataSaveIntent intent, Prepared p)
    {
        VerifyPaths();
        VerifyPrivate(Operation(intent));
        var old = ReadFact(OldWitness(intent));
        var next = ReadFact(NewWitness(intent));
        var destination = ReadFact(source);
        var stage = ReadFact(Stage(intent));
        if (old != p.Original || next != p.Candidate)
            return DurableLocalEditState.RecoveryRequired;
        if (destination == p.Original && stage == p.Candidate)
            return DurableLocalEditState.PreparedNotExchanged;
        if (destination == p.Candidate && stage == p.Original)
            return DurableLocalEditState.WitnessedExchange;
        return DurableLocalEditState.RecoveryRequired;
    }

    private DirectDataCommitEvidence Evidence(DirectDataSaveIntent intent, Prepared p) =>
        new(DirectDataReceiptJournal.Fingerprint(intent), intent.CandidateHash,
            JsonData.Digest(new { format = Format, phase = "exact-exchanged-inode-pair", prepared = p }));

    private void WritePrepared(DirectDataSaveIntent intent, Prepared prepared)
    {
        string path = PreparedPath(intent);
        var record = new PreparedEnvelope(Format, prepared,
            JsonData.Digest(new { format = Format, prepared }));
        byte[] raw = JsonSerializer.SerializeToUtf8Bytes(record, JsonData.Options);
        if (raw.Length > MaxRecordBytes) throw new IOException("Prepared record budget.");
        string temp = Path.Combine(Operation(intent), "." + Guid.NewGuid().ToString("N") + ".tmp");
        using (var stream = new FileStream(temp, FileMode.CreateNew, FileAccess.Write, FileShare.None))
        {
            if (OperatingSystem.IsLinux()) File.SetUnixFileMode(temp, UnixFileMode.UserRead | UnixFileMode.UserWrite);
            stream.Write(raw);
            stream.Flush(true);
        }
        File.Move(temp, path, false);
        FlushDirectory(Operation(intent));
    }

    private Prepared ReadPrepared(DirectDataSaveIntent intent)
    {
        VerifyPrivate(Operation(intent));
        byte[] raw = ReadBounded(PreparedPath(intent), MaxRecordBytes, out _);
        using var doc = JsonDocument.Parse(raw);
        var record = doc.RootElement.Deserialize<PreparedEnvelope>(JsonData.Options) ??
            throw new IOException("Missing prepared exchange.");
        var p = record.Payload;
        if (record.Format != Format || p is null ||
            JsonData.Digest(doc.RootElement) != JsonData.Digest(record) ||
            record.Checksum != JsonData.Digest(new { format = Format, prepared = p }) ||
            p.IntentFingerprint != DirectDataReceiptJournal.Fingerprint(intent) || p.Relative != relative ||
            p.Original is null || p.Candidate is null ||
            p.Original.Hash != intent.BeforeHash || p.Candidate.Hash != intent.CandidateHash ||
            SourceFingerprint(p.Original) != intent.SourceIdentity ||
            p.Original.Identity == p.Candidate.Identity || p.Original.Links != 2 || p.Candidate.Links != 2 ||
            p.Original.Mode != p.Candidate.Mode || p.Original.Uid != p.Candidate.Uid || p.Original.Gid != p.Candidate.Gid)
            throw new IOException("Prepared exchange identity mismatch.");
        return p;
    }

    private string SourceFingerprint(FileFact fact) => JsonData.Digest(new
    {
        root, relative, projectFingerprint, ownerFingerprint, fact.Identity, fact.Uid, fact.Gid, fact.Mode
    });

    private void ValidateIntent(DirectDataSaveIntent intent)
    {
        ArgumentNullException.ThrowIfNull(intent);
        if (!Guid.TryParseExact(intent.OperationId, "N", out var id) || id == Guid.Empty ||
            id.ToString("N") != intent.OperationId || intent.ProjectFingerprint != projectFingerprint ||
            intent.OwnerFingerprint != ownerFingerprint || !Hash(intent.SourceIdentity) ||
            !Hash(intent.BeforeHash) || !Hash(intent.CandidateHash) || intent.BeforeHash == intent.CandidateHash ||
            !Hash(intent.CheckpointFingerprint) || !Hash(intent.RequestFingerprint))
            throw new ArgumentException("Exact scoped data intent required.");
    }

    private static DurableLocalEditState Translate(DirectDataReceiptState state) => state switch
    {
        DirectDataReceiptState.NoIntent => DurableLocalEditState.NoIntent,
        DirectDataReceiptState.CompletedHistorical => DurableLocalEditState.CompletedHistorical,
        DirectDataReceiptState.ConflictingIdentity => DurableLocalEditState.ConflictingIdentity,
        DirectDataReceiptState.BlockedByPending => DurableLocalEditState.BlockedByPending,
        DirectDataReceiptState.Pending => DurableLocalEditState.PendingUncertain,
        _ => DurableLocalEditState.RecoveryRequired
    };

    private static DurableLocalEditState FailClosed(Func<DurableLocalEditState> action)
    {
        try { return action(); }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or ArgumentException or
            InvalidOperationException or JsonException or NotSupportedException or DllNotFoundException or EntryPointNotFoundException)
        { return DurableLocalEditState.RecoveryRequired; }
    }

    private static bool Hash(string? value) => value is { Length: 64 } &&
        value.All(c => c is >= '0' and <= '9' or >= 'a' and <= 'f');
    private static bool Inside(string folder, string path) =>
        path.StartsWith(folder.TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar, StringComparison.Ordinal);
    private string Operation(DirectDataSaveIntent intent) => Path.Combine(operations, intent.OperationId);
    private string Stage(DirectDataSaveIntent intent) => Path.Combine(Operation(intent), "exchange.stage");
    private string OldWitness(DirectDataSaveIntent intent) => Path.Combine(Operation(intent), "original.witness");
    private string NewWitness(DirectDataSaveIntent intent) => Path.Combine(Operation(intent), "candidate.witness");
    private string PreparedPath(DirectDataSaveIntent intent) => Path.Combine(Operation(intent), "prepared.json");

    private void VerifyPaths()
    {
        VerifyDirectory(root);
        VerifyDirectory(Path.GetDirectoryName(source)!);
        VerifyPrivate(recovery);
        VerifyPrivate(journalDirectory);
        VerifyPrivate(operations);
        VerifyDirectory(Path.GetDirectoryName(leasePath)!);
    }

    private static void RequireLinux()
    {
        if (!OperatingSystem.IsLinux())
            throw new PlatformNotSupportedException("Verified atomic exchange primitive is Linux-only.");
    }

    private static void VerifyDirectory(string path)
    {
        for (DirectoryInfo? entry = new(path); entry is not null; entry = entry.Parent)
            if (!entry.Exists || entry.LinkTarget is not null || (entry.Attributes & FileAttributes.ReparsePoint) != 0)
                throw new IOException("Existing lexical owned directory required.");
    }

    private static void VerifyPrivate(string path)
    {
        VerifyDirectory(path);
        var stat = StatPath(path);
        if ((stat.Mode & 0xf000) != 0x4000 || stat.Uid != EffectiveUid() || (stat.Mode & 0x3f) != 0)
            throw new UnauthorizedAccessException("Private owner-only recovery directory required.");
    }

    private FileStream AcquireLease(bool create = true)
    {
        if (new FileInfo(leasePath).LinkTarget is not null)
            throw new UnauthorizedAccessException("Source lease cannot traverse links.");
        // Same cooperative source lease as FileStream.CommitPlan.
        if (!create && !File.Exists(leasePath)) throw new IOException("Existing source lease required for recovery.");
        var watch = System.Diagnostics.Stopwatch.StartNew();
        while (true)
        {
            try
            {
                var lease = new FileStream(leasePath, create ? FileMode.OpenOrCreate : FileMode.Open, FileAccess.ReadWrite, FileShare.None);
                try
                {
                    var status = StatFd(lease.SafeFileHandle);
                    if ((status.Mode & 0xf000) != 0x8000 || status.Uid != EffectiveUid() ||
                        status.Links != 1 || FileIdentity(status) != FileIdentity(StatPath(leasePath)))
                        throw new UnauthorizedAccessException("Exact owned source lease required.");
                    return lease;
                }
                catch { lease.Dispose(); throw; }
            }
            catch (IOException) when (watch.ElapsedMilliseconds < 5000) { Thread.Sleep(10); }
        }
    }

    private static void CheckOriginal(FileFact fact)
    {
        if (fact.Links != 1 || fact.Uid != EffectiveUid() || (fact.Mode & 0x80) == 0 ||
            (fact.Mode & 0xe00) != 0)
            throw new UnauthorizedAccessException("Existing owner-writable, unaliased ordinary source required.");
    }

    private static bool SameContentIdentity(FileFact a, FileFact b) =>
        a.Identity == b.Identity && a.Hash == b.Hash && a.Mode == b.Mode && a.Uid == b.Uid && a.Gid == b.Gid;

    private static FileFact ReadFact(string path)
    {
        byte[] bytes = ReadBounded(path, MaxBytes, out var status);
        if (ListAttributes(path, IntPtr.Zero, 0) != 0)
            throw new UnauthorizedAccessException("Extended source attributes require an explicit metadata adapter.");
        return new(FileIdentity(status), JsonData.HashBytes(bytes), status.Uid, status.Gid, status.Mode, status.Links);
    }

    private static byte[] ReadBounded(string path, int max, out LinuxStatx status)
    {
        VerifyDirectory(Path.GetDirectoryName(path)!);
        using var handle = OpenOwned(path, O_NONBLOCK | O_NOFOLLOW | O_CLOEXEC);
        var before = StatFd(handle);
        if ((before.Mode & 0xf000) != 0x8000 || before.Size > (ulong)max)
            throw new IOException("Bounded ordinary file required.");
        using var stream = new FileStream(handle, FileAccess.Read);
        byte[] bytes = new byte[(int)before.Size];
        stream.ReadExactly(bytes);
        if (stream.ReadByte() != -1) throw new IOException("Source changed during read.");
        status = StatFd(handle);
        var named = StatPath(path);
        if (!StableRead(before, status) || !StableRead(status, named))
            throw new IOException("Source identity changed during read.");
        return bytes;
    }

    private static bool StableRead(LinuxStatx a, LinuxStatx b) =>
        FileIdentity(a) == FileIdentity(b) && a.Size == b.Size && a.Mode == b.Mode &&
        a.Links == b.Links && a.Uid == b.Uid && a.Gid == b.Gid &&
        a.ChangeSeconds == b.ChangeSeconds && a.ChangeNanos == b.ChangeNanos &&
        a.ModifySeconds == b.ModifySeconds && a.ModifyNanos == b.ModifyNanos;

    private static void FlushFile(string path)
    {
        using var file = OpenOwned(path, O_NONBLOCK | O_NOFOLLOW | O_CLOEXEC);
        if ((StatFd(file).Mode & 0xf000) != 0x8000 || Sync(Fd(file)) != 0)
            throw Error("Flush ordinary source");
    }

    private static void FlushDirectory(string path)
    {
        VerifyDirectory(path);
        using var directory = OpenOwned(path, O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
        if (Sync(Fd(directory)) != 0) throw Error("Flush directory");
    }

    private static void LinkExact(string from, string to)
    {
        if (Link(from, to) != 0) throw Error("Create inode witness");
        if (FileIdentity(StatPath(from)) != FileIdentity(StatPath(to)))
            throw new IOException("Witness identity differs.");
    }

    private static SafeFileHandle OpenOwned(string path, int flags)
    {
        int fd = Open(path, flags);
        if (fd < 0) throw Error("Open owned source");
        return new SafeFileHandle((IntPtr)fd, ownsHandle: true);
    }

    private static int Fd(SafeFileHandle handle) => checked((int)handle.DangerousGetHandle());
    private static IOException Error(string operation) =>
        new($"{operation} failed (errno {Marshal.GetLastPInvokeError()}).");

    // Linux statx is an explicitly versioned 256-byte kernel ABI across the
    // supported architectures, unlike libc's platform-dependent struct stat.
    [StructLayout(LayoutKind.Explicit, Size = 256)]
    private struct LinuxStatx
    {
        [FieldOffset(0)] public uint Mask;
        [FieldOffset(16)] public uint Links;
        [FieldOffset(20)] public uint Uid;
        [FieldOffset(24)] public uint Gid;
        [FieldOffset(28)] public ushort Mode;
        [FieldOffset(32)] public ulong Inode;
        [FieldOffset(40)] public ulong Size;
        [FieldOffset(96)] public long ChangeSeconds;
        [FieldOffset(104)] public uint ChangeNanos;
        [FieldOffset(112)] public long ModifySeconds;
        [FieldOffset(120)] public uint ModifyNanos;
        [FieldOffset(136)] public uint DeviceMajor;
        [FieldOffset(140)] public uint DeviceMinor;
    }

    private static LinuxStatx StatPath(string path) => Stat(AT_FDCWD, path, AT_SYMLINK_NOFOLLOW);
    private static LinuxStatx StatFd(SafeFileHandle file) => Stat(Fd(file), "", AT_EMPTY_PATH | AT_SYMLINK_NOFOLLOW);
    private static LinuxStatx Stat(int fd, string path, int flags)
    {
        if (Statx(fd, path, flags, STATX_BASIC_STATS, out var status) != 0 ||
            (status.Mask & 0x3df) != 0x3df)
            throw Error("Read exact Linux file identity");
        return status;
    }
    private static Identity FileIdentity(LinuxStatx stat) => new(stat.DeviceMajor, stat.DeviceMinor, stat.Inode);

    [DllImport("libc", EntryPoint = "statx", SetLastError = true)] private static extern int Statx(int fd, string path, int flags, uint mask, out LinuxStatx stat);
    [DllImport("libc", EntryPoint = "open", SetLastError = true)] private static extern int Open(string path, int flags);
    [DllImport("libc", EntryPoint = "fsync", SetLastError = true)] private static extern int Sync(int fd);
    [DllImport("libc", EntryPoint = "link", SetLastError = true)] private static extern int Link(string from, string to);
    [DllImport("libc", EntryPoint = "mkdir", SetLastError = true)] private static extern int Mkdir(string path, uint mode);
    [DllImport("libc", EntryPoint = "renameat2", SetLastError = true)] private static extern int RenameExchange(int fromFd, string from, int toFd, string to, uint flags);
    [DllImport("libc", EntryPoint = "geteuid")] private static extern uint EffectiveUid();
    [DllImport("libc", EntryPoint = "llistxattr", SetLastError = true)] private static extern nint ListAttributes(string path, IntPtr list, nuint size);
}
