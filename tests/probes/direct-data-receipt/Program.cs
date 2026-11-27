using System.Diagnostics;
using System.Text.Json;
using System.Text.Json.Nodes;
using Confectory.Core;
using State = Confectory.Core.DirectDataReceiptState;

static string Hash(string value) => JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(value));
static DirectDataSaveIntent Intent(string project = "project-a", string owner = "owner-a") =>
    new(Guid.NewGuid().ToString("N"), Hash(project), Hash(owner), Hash("owned-source"), Hash("before"),
        Hash("after"), Hash("checkpoint"), Hash("request"));
static DirectDataCommitEvidence Evidence(DirectDataSaveIntent intent) =>
    new(DirectDataReceiptJournal.Fingerprint(intent), intent.CandidateHash, Hash("authoritative-test-commit"));
static DirectDataReceiptJournal Journal(string directory, DirectDataSaveIntent intent) =>
    new(directory, intent.ProjectFingerprint, intent.OwnerFingerprint);
static void Check(bool actual, string message)
{
    if (!actual) throw new InvalidOperationException(message);
}
static void Expect(State actual, State expected)
{
    Check(actual == expected, $"Expected {expected}, got {actual}");
}
static string IntentFile(string root, DirectDataSaveIntent intent) =>
    Path.Combine(root, "recovery", intent.OperationId + ".intent.json");
static string CompletionFile(string root, DirectDataSaveIntent intent) =>
    Path.Combine(root, "recovery", intent.OperationId + ".completion.json");
static void SourceReplace(string root, string text)
{
    string source = Path.Combine(root, "source");
    string temp = source + ".test-temp";
    File.WriteAllText(temp, text);
    using (var stream = new FileStream(temp, FileMode.Open, FileAccess.ReadWrite, FileShare.None)) stream.Flush(true);
    File.Move(temp, source, true);
}
static void Cut(string wanted, string stage)
{
    if (wanted != stage) return;
    Console.WriteLine("CUT " + stage);
    Console.Out.Flush();
    Thread.Sleep(Timeout.Infinite);
}
static Process Worker(string root, DirectDataSaveIntent intent, string cut)
{
    var start = new ProcessStartInfo(Environment.ProcessPath!)
    {
        UseShellExecute = false,
        RedirectStandardOutput = true,
        RedirectStandardError = true
    };
    // The test may run through dotnet or as an apphost.
    if (Path.GetFileNameWithoutExtension(Environment.ProcessPath) == "dotnet")
        start.ArgumentList.Add(typeof(Program).Assembly.Location);
    foreach (var arg in new[] { "--worker", root, JsonSerializer.Serialize(intent), cut })
        start.ArgumentList.Add(arg);
    return Process.Start(start) ?? throw new IOException("Test worker did not start.");
}

if (args.Length == 4 && args[0] == "--admit-worker")
{
    string workerRoot = args[1];
    var workerIntent = JsonSerializer.Deserialize<DirectDataSaveIntent>(args[2])!;
    string gate = args[3];
    var deadline = Stopwatch.StartNew();
    while (!File.Exists(gate))
    {
        if (deadline.Elapsed > TimeSpan.FromSeconds(15)) throw new TimeoutException("Admission test gate.");
        Thread.Sleep(2);
    }
    Console.WriteLine(Journal(Path.Combine(workerRoot, "recovery"), workerIntent).Admit(workerIntent));
    return;
}

if (args.Length == 4 && args[0] == "--worker")
{
    string workerRoot = args[1], cut = args[3];
    var workerIntent = JsonSerializer.Deserialize<DirectDataSaveIntent>(args[2])!;
    var workerJournal = Journal(Path.Combine(workerRoot, "recovery"), workerIntent);
    Cut(cut, "before-intent");
    Expect(workerJournal.Admit(workerIntent), State.Admitted);
    Cut(cut, "after-intent");
    File.WriteAllText(Path.Combine(workerRoot, "test-staged"), "after");
    Cut(cut, "after-stage");
    // A stand-in for the authoritative existing commit, not a new product writer.
    SourceReplace(workerRoot, "after");
    Cut(cut, "after-replace");
    Expect(workerJournal.RecordCompletion(workerIntent, Evidence(workerIntent)), State.CompletedHistorical);
    Cut(cut, "after-receipt");
    return;
}

if (!OperatingSystem.IsLinux()) throw new PlatformNotSupportedException("This durability probe requires Linux.");
int passed = 0;
void Run(string name, Action<string, DirectDataSaveIntent, DirectDataReceiptJournal> test)
{
    var root = Directory.CreateTempSubdirectory("confectory-direct-receipt-").FullName;
    try
    {
        string recovery = Path.Combine(root, "recovery");
        Directory.CreateDirectory(recovery);
        File.SetUnixFileMode(recovery, UnixFileMode.UserRead | UnixFileMode.UserWrite | UnixFileMode.UserExecute);
        File.WriteAllText(Path.Combine(root, "source"), "before");
        File.WriteAllText(Path.Combine(root, "independent-draft"), "unrelated unsaved input");
        var intent = Intent();
        test(root, intent, Journal(recovery, intent));
        Check(File.ReadAllText(Path.Combine(root, "independent-draft")) == "unrelated unsaved input", "Other draft modified");
        Console.WriteLine("PASS " + name);
        passed++;
    }
    finally { Directory.Delete(root, true); }
}

Run("no intent read and no inferred completion", (root, intent, journal) =>
{
    Expect(journal.Inspect(intent), State.NoIntent);
    SourceReplace(root, "after");
    Expect(journal.Inspect(intent), State.NoIntent);
    Expect(journal.RecordCompletion(intent, Evidence(intent)), State.NoIntent);
    Check(!Directory.EnumerateFileSystemEntries(Path.Combine(root, "recovery")).Any(), "Recovery inspection wrote files");
});

Run("explicit admission, duplicate, and completed history", (root, intent, journal) =>
{
    Expect(journal.Admit(intent), State.Admitted);
    byte[] original = File.ReadAllBytes(IntentFile(root, intent));
    Expect(journal.Admit(intent), State.Pending);
    Expect(journal.Admit(intent with { RequestFingerprint = Hash("different") }), State.ConflictingIdentity);
    Expect(journal.Admit(intent with { OperationId = Guid.NewGuid().ToString("N") }), State.BlockedByPending);
    Check(original.SequenceEqual(File.ReadAllBytes(IntentFile(root, intent))), "Intent overwritten");
    Expect(journal.RecordCompletion(intent, Evidence(intent) with { CommittedHash = Hash("other") }), State.ConflictingIdentity);
    Check(!File.Exists(CompletionFile(root, intent)), "Invalid completion written");
    SourceReplace(root, "after");
    Expect(journal.Inspect(intent), State.Pending);
    Expect(journal.RecordCompletion(intent, Evidence(intent)), State.CompletedHistorical);
    byte[] completion = File.ReadAllBytes(CompletionFile(root, intent));
    Expect(journal.Admit(intent), State.CompletedHistorical);
    Expect(journal.RecordCompletion(intent, Evidence(intent)), State.CompletedHistorical);
    Expect(journal.RecordCompletion(intent, Evidence(intent) with { AuthorityFingerprint = Hash("other") }), State.ConflictingIdentity);
    Check(completion.SequenceEqual(File.ReadAllBytes(CompletionFile(root, intent))), "Completion overwritten");
    SourceReplace(root, "external");
    Expect(journal.Inspect(intent), State.CompletedHistorical);
    Check(File.ReadAllText(Path.Combine(root, "source")) == "external", "Historical receipt rewrote source");
    var next = intent with { OperationId = Guid.NewGuid().ToString("N"), BeforeHash = Hash("external"), CandidateHash = Hash("next") };
    Expect(journal.Admit(next), State.Admitted);
    Expect(journal.Inspect(intent), State.CompletedHistorical);
});

foreach (var stage in new[] { "before-intent", "after-intent", "after-stage", "after-replace", "after-receipt" })
{
    Run("terminated " + stage, (root, intent, journal) =>
    {
        using var worker = Worker(root, intent, stage);
        try
        {
            var line = worker.StandardOutput.ReadLineAsync();
            Check(line.Wait(TimeSpan.FromSeconds(15)) && line.Result == "CUT " + stage, "Worker did not reach " + stage);
            worker.Kill();
            Check(worker.WaitForExit(10000) && worker.ExitCode != 0, "Worker was not terminated");
        }
        finally { if (!worker.HasExited) { worker.Kill(); worker.WaitForExit(); } }
        var recovered = Journal(Path.Combine(root, "recovery"), intent);
        var expected = stage == "before-intent" ? State.NoIntent : stage == "after-receipt" ? State.CompletedHistorical : State.Pending;
        byte[] source = File.ReadAllBytes(Path.Combine(root, "source"));
        Check(System.Text.Encoding.UTF8.GetString(source) == (stage is "after-replace" or "after-receipt" ? "after" : "before"), "Unexpected physical source");
        var before = Directory.EnumerateFiles(Path.Combine(root, "recovery")).ToDictionary(path => Path.GetFileName(path)!, File.ReadAllBytes);
        Expect(recovered.Inspect(intent), expected);
        Expect(recovered.Inspect(intent), expected);
        Check(source.SequenceEqual(File.ReadAllBytes(Path.Combine(root, "source"))), "Recovery wrote source");
        Check(before.Count == Directory.EnumerateFiles(Path.Combine(root, "recovery")).Count() &&
            before.All(pair => pair.Value.SequenceEqual(File.ReadAllBytes(Path.Combine(root, "recovery", pair.Key!)))), "Recovery modified journal");
        if (expected == State.Pending)
        {
            Expect(recovered.Admit(intent), State.Pending);
            Expect(recovered.Admit(intent with { OperationId = Guid.NewGuid().ToString("N") }), State.BlockedByPending);
        }
    });
}

Run("external same-after and ABA cannot complete pending intent", (root, intent, journal) =>
{
    Expect(journal.Admit(intent), State.Admitted);
    foreach (string value in new[] { "other", "before", "after", "other", "after" })
    {
        SourceReplace(root, value);
        Expect(journal.Inspect(intent), State.Pending);
        Check(!File.Exists(CompletionFile(root, intent)), "Source fingerprint inferred completion");
    }
});

Run("corrupt and orphan records fail closed", (root, intent, journal) =>
{
    Expect(journal.Admit(intent), State.Admitted);
    var original = File.ReadAllBytes(IntentFile(root, intent));
    File.WriteAllText(IntentFile(root, intent), "{");
    Expect(journal.Inspect(intent), State.RecoveryRequired);
    Expect(journal.Admit(intent with { OperationId = Guid.NewGuid().ToString("N") }), State.RecoveryRequired);
    Check(File.ReadAllText(IntentFile(root, intent)) == "{", "Corrupt record overwritten");
    File.WriteAllBytes(IntentFile(root, intent), original);
    SourceReplace(root, "after");
    Expect(journal.RecordCompletion(intent, Evidence(intent)), State.CompletedHistorical);
    File.Delete(IntentFile(root, intent));
    Expect(journal.Inspect(intent), State.RecoveryRequired);
    Expect(journal.Admit(intent), State.RecoveryRequired);
});

Run("mismatched receipt and missing lock fail closed", (root, intent, journal) =>
{
    Expect(journal.Admit(intent), State.Admitted);
    SourceReplace(root, "after");
    Expect(journal.RecordCompletion(intent, Evidence(intent)), State.CompletedHistorical);
    var completion = CompletionFile(root, intent);
    var original = File.ReadAllBytes(completion);
    File.WriteAllText(completion, File.ReadAllText(completion).Replace(intent.CandidateHash, Hash("wrong")));
    Expect(journal.Inspect(intent), State.RecoveryRequired);
    File.WriteAllBytes(completion, original);
    File.Delete(Path.Combine(root, "recovery", "journal.lock"));
    Expect(journal.Inspect(intent), State.RecoveryRequired);
    Expect(journal.Admit(intent), State.RecoveryRequired);
    Check(!File.Exists(Path.Combine(root, "recovery", "journal.lock")), "Destroyed lock silently recreated");
});

Run("unpublished torn temporary record is not authority", (root, intent, journal) =>
{
    string temp = Path.Combine(root, "recovery", "." + intent.OperationId + ".intent.json." + Guid.NewGuid().ToString("N") + ".tmp");
    File.WriteAllText(temp, """{"partial":""");
    Expect(journal.Inspect(intent), State.NoIntent);
    Check(File.ReadAllText(temp) == """{"partial":""", "Torn file removed or interpreted");
    Expect(journal.RecordCompletion(intent, Evidence(intent)), State.NoIntent);
});

Run("different project and owner are isolated", (root, intent, journal) =>
{
    Expect(journal.Admit(intent), State.Admitted);
    string peer = Path.Combine(root, "peer");
    Directory.CreateDirectory(Path.Combine(peer, "recovery"));
    File.SetUnixFileMode(Path.Combine(peer, "recovery"), UnixFileMode.UserRead | UnixFileMode.UserWrite | UnixFileMode.UserExecute);
    File.WriteAllText(Path.Combine(peer, "source"), "before");
    var other = intent with { ProjectFingerprint = Hash("project-b") };
    var peerJournal = Journal(Path.Combine(peer, "recovery"), other);
    Expect(peerJournal.Inspect(other), State.NoIntent);
    Expect(peerJournal.Admit(other), State.Admitted);
    SourceReplace(peer, "after");
    Expect(peerJournal.RecordCompletion(other, Evidence(other)), State.CompletedHistorical);
    Expect(journal.Inspect(intent), State.Pending);
    bool rejected = false;
    try { _ = journal.Inspect(other); } catch (ArgumentException) { rejected = true; }
    Check(rejected, "Cross-project intent accepted");
    rejected = false;
    try { _ = journal.Admit(intent with { OwnerFingerprint = Hash("other-owner") }); } catch (ArgumentException) { rejected = true; }
    Check(rejected, "Cross-owner admission accepted");
});

Run("symlink and non-private recovery fail closed", (root, intent, journal) =>
{
    string recovery = Path.Combine(root, "recovery"), link = Path.Combine(root, "link");
    Directory.CreateSymbolicLink(link, recovery);
    Expect(Journal(link, intent).Admit(intent), State.RecoveryRequired);
    File.SetUnixFileMode(recovery, UnixFileMode.UserRead | UnixFileMode.UserWrite | UnixFileMode.UserExecute | UnixFileMode.OtherWrite);
    try { Expect(journal.Admit(intent), State.RecoveryRequired); }
    finally { File.SetUnixFileMode(recovery, UnixFileMode.UserRead | UnixFileMode.UserWrite | UnixFileMode.UserExecute); }
    Expect(journal.Admit(intent), State.Admitted);
    string path = CompletionFile(root, intent);
    File.CreateSymbolicLink(path, Path.Combine(root, "source"));
    Expect(journal.Inspect(intent), State.RecoveryRequired);
    Expect(journal.RecordCompletion(intent, Evidence(intent)), State.RecoveryRequired);
    Check(File.ReadAllText(Path.Combine(root, "source")) == "before", "Symlink target written");
});

Run("concurrent explicit admissions cannot create two pending intents", (root, intent, journal) =>
{
    var other = intent with { OperationId = Guid.NewGuid().ToString("N") };
    using var barrier = new Barrier(2);
    var first = Task.Run(() => { barrier.SignalAndWait(); return journal.Admit(intent); });
    var second = Task.Run(() => { barrier.SignalAndWait(); return Journal(Path.Combine(root, "recovery"), other).Admit(other); });
    Task.WaitAll(first, second);
    Check(new[] { first.Result, second.Result }.Count(result => result == State.Admitted) == 1, "Two or no admitted operations");
    Check(Directory.GetFiles(Path.Combine(root, "recovery"), "*.intent.json").Length == 1, "Multiple durable pending intents");
});

Run("unreadable record and removed completion remain recovery-only", (root, intent, journal) =>
{
    Expect(journal.Admit(intent), State.Admitted);
    string path = IntentFile(root, intent);
    var original = File.ReadAllBytes(path);
    File.SetUnixFileMode(path, UnixFileMode.None);
    try { Expect(journal.Inspect(intent), State.RecoveryRequired); }
    finally { File.SetUnixFileMode(path, UnixFileMode.UserRead | UnixFileMode.UserWrite); }
    Check(original.SequenceEqual(File.ReadAllBytes(path)), "Unreadable intent rewritten");
    SourceReplace(root, "after");
    Expect(journal.RecordCompletion(intent, Evidence(intent)), State.CompletedHistorical);
    File.Delete(CompletionFile(root, intent));
    Expect(journal.Inspect(intent), State.Pending);
    Expect(journal.Admit(intent), State.Pending);
    Check(!File.Exists(CompletionFile(root, intent)), "Missing receipt invented");
});

Run("cross-process admissions preserve one durable pending operation", (root, intent, journal) =>
{
    string gate = Path.Combine(root, "start");
    Process AdmitWorker(DirectDataSaveIntent request)
    {
        var start = new ProcessStartInfo(Environment.ProcessPath!)
        {
            UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true
        };
        if (Path.GetFileNameWithoutExtension(Environment.ProcessPath) == "dotnet")
            start.ArgumentList.Add(typeof(Program).Assembly.Location);
        foreach (var arg in new[] { "--admit-worker", root, JsonSerializer.Serialize(request), gate })
            start.ArgumentList.Add(arg);
        return Process.Start(start) ?? throw new IOException("Admission worker not started.");
    }
    var other = intent with { OperationId = Guid.NewGuid().ToString("N") };
    using var first = AdmitWorker(intent);
    using var second = AdmitWorker(other);
    try
    {
        File.WriteAllText(gate, "start");
        Check(first.WaitForExit(15000) && second.WaitForExit(15000), "Admission workers did not finish");
        Check(first.ExitCode == 0 && second.ExitCode == 0, "Admission worker failed");
        var results = new[] { first.StandardOutput.ReadToEnd().Trim(), second.StandardOutput.ReadToEnd().Trim() };
        Check(results.Count(result => result == State.Admitted.ToString()) == 1, "Cross-process duplicate admission");
        Check(Directory.GetFiles(Path.Combine(root, "recovery"), "*.intent.json").Length == 1, "Multiple durable intents");
    }
    finally
    {
        foreach (var process in new[] { first, second })
            if (!process.HasExited) { process.Kill(); process.WaitForExit(); }
    }
});

Run("unknown payload fields fail closed even with recomputed checksum", (root, intent, journal) =>
{
    Expect(journal.Admit(intent), State.Admitted);
    string path = IntentFile(root, intent);
    var envelope = JsonNode.Parse(File.ReadAllText(path))!.AsObject();
    envelope["payload"]!.AsObject()["unknown"] = "not a defined record field";
    envelope["checksum"] = JsonData.Digest(new
    {
        format = envelope["format"]!.ToString(),
        kind = envelope["kind"]!.ToString(),
        payload = envelope["payload"]
    });
    File.WriteAllText(path, envelope.ToJsonString());
    Expect(journal.Inspect(intent), State.RecoveryRequired);
    Expect(journal.RecordCompletion(intent, Evidence(intent)), State.RecoveryRequired);
});

Run("bounded history is retained rather than silently pruned", (root, intent, journal) =>
{
    string previous = "before";
    for (int i = 0; i < 64; i++)
    {
        string next = "synthetic-" + i;
        var request = intent with { OperationId = Guid.NewGuid().ToString("N"), BeforeHash = Hash(previous), CandidateHash = Hash(next) };
        Expect(journal.Admit(request), State.Admitted);
        SourceReplace(root, next);
        Expect(journal.RecordCompletion(request, Evidence(request)), State.CompletedHistorical);
        previous = next;
    }
    var additional = intent with { OperationId = Guid.NewGuid().ToString("N"), BeforeHash = Hash(previous) };
    Expect(journal.Admit(additional), State.RecoveryRequired);
    Check(Directory.GetFiles(Path.Combine(root, "recovery"), "*.json").Length == 128, "Historical records were silently removed");
});

Console.WriteLine($"PASS {passed} direct-data receipt foundation scenarios");
