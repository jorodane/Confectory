using System.Diagnostics;
using System.Text;
using System.Text.Json;
using Confectory.Core;
using State = Confectory.Core.DurableLocalEditState;

const string relative = "object.celem";
byte[] original = Encoding.UTF8.GetBytes("{\"value\":1,\"label\":\"한글\"}\n");
byte[] candidate = Encoding.UTF8.GetBytes("{\"value\":2,\"label\":\"한글\"}\n");
string Hash(string s) => JsonData.HashBytes(Encoding.UTF8.GetBytes(s));
string Recovery(string root) => Path.Combine(root, ".confectory", "probe");
DurableLocalDataExchange Exchange(string root) => new(root, relative, Recovery(root), Hash("project"), Hash("owner"));
string Source(string root) => Path.Combine(root, relative);
string Stage(string root, DirectDataSaveIntent i) => Path.Combine(Recovery(root), "operations", i.OperationId, "exchange.stage");
void Check(bool ok, string message) { if (!ok) throw new Exception(message); }
void Expect(State actual, State expected) => Check(actual == expected, $"Expected {expected}, got {actual}");
void Bytes(string path, byte[] expected) => Check(File.ReadAllBytes(path).SequenceEqual(expected), "Incorrect bytes: " + path);
void Replace(string path, byte[] bytes) { File.WriteAllBytes(path + ".new", bytes); File.Move(path + ".new", path, true); }
DirectDataSaveIntent Setup(string root)
{
    foreach (var dir in new[] { Recovery(root), Path.Combine(Recovery(root), "journal"), Path.Combine(Recovery(root), "operations") })
    {
        Directory.CreateDirectory(dir);
        if (OperatingSystem.IsLinux()) File.SetUnixFileMode(dir, UnixFileMode.UserRead | UnixFileMode.UserWrite | UnixFileMode.UserExecute);
    }
    File.WriteAllBytes(Source(root), original);
    File.WriteAllText(Path.Combine(root, "peer.celem"), "independent draft");
    var captured = Exchange(root).Capture();
    return new(Guid.NewGuid().ToString("N"), Hash("project"), Hash("owner"), captured.SourceIdentity,
        captured.BeforeHash, JsonData.HashBytes(candidate), Hash("checkpoint"), Hash("request"));
}
Process Worker(string root, DirectDataSaveIntent i, string action, string cut = "")
{
    var p = new ProcessStartInfo(Environment.ProcessPath!) { UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true };
    if (Path.GetFileNameWithoutExtension(Environment.ProcessPath) == "dotnet") p.ArgumentList.Add(typeof(Program).Assembly.Location);
    foreach (var arg in new[] { root, JsonSerializer.Serialize(i), action, cut }) p.ArgumentList.Add(arg);
    return Process.Start(p)!;
}
string Line(Process p) => p.StandardOutput.ReadLineAsync().WaitAsync(TimeSpan.FromSeconds(20)).GetAwaiter().GetResult() ?? throw new Exception(p.StandardError.ReadToEnd());
State Child(string root, DirectDataSaveIntent i, string action)
{
    using var p = Worker(root, i, action);
    string line = Line(p);
    Check(p.WaitForExit(20000) && p.ExitCode == 0, "Worker failed: " + p.StandardError.ReadToEnd());
    return Enum.Parse<State>(line);
}
void KillAt(string root, DirectDataSaveIntent i, string cut)
{
    using var p = Worker(root, i, "commit", cut);
    Check(Line(p) == "CUT " + cut, "Missing requested cut");
    p.Kill(true);
    Check(p.WaitForExit(20000) && p.ExitCode != 0, "Not killed");
}
if (!OperatingSystem.IsLinux()) { Console.WriteLine("SKIP: Linux-only primitive"); return; }
if (args.Length == 4)
{
    var i = JsonSerializer.Deserialize<DirectDataSaveIntent>(args[1])!;
    var x = Exchange(args[0]);
    Console.WriteLine(args[2] switch {
        "inspect" => x.Inspect(i), "seal" => x.SealWitnessed(i),
        "commit" => x.CommitForProbe(i, candidate, stage => {
            if (stage != args[3]) return;
            Console.WriteLine("CUT " + stage); Console.Out.Flush(); Thread.Sleep(Timeout.Infinite);
        }), _ => throw new Exception("Unknown worker")
    });
    return;
}
string tmp = Path.Combine(Path.GetTempPath(), "local-exchange-" + Guid.NewGuid().ToString("N"));
Directory.CreateDirectory(tmp);
try
{
    foreach (var (cut, expected, exchanged) in new[] {
        ("before-intent", State.NoIntent, false), ("after-intent", State.PendingUncertain, false),
        ("after-stage", State.PendingUncertain, false), ("after-prepared", State.PreparedNotExchanged, false),
        ("before-exchange", State.PreparedNotExchanged, false), ("after-exchange", State.WitnessedExchange, true),
        ("after-directory-sync", State.WitnessedExchange, true), ("after-receipt", State.CompletedHistorical, true)
    })
    {
        string root = Path.Combine(tmp, cut); var i = Setup(root);
        KillAt(root, i, cut);
        Expect(Child(root, i, "inspect"), expected);
        Bytes(Source(root), exchanged ? candidate : original);
        if (exchanged) Bytes(Stage(root, i), original);
        else if (expected != State.NoIntent) Expect(Child(root, i, "commit"), expected);
        if (expected == State.WitnessedExchange) Expect(Child(root, i, "seal"), State.CompletedHistorical);
        else Expect(Child(root, i, "seal"), expected);
        if (exchanged) Expect(Child(root, i, "commit"), State.CompletedHistorical);
        Check(File.ReadAllText(Path.Combine(root, "peer.celem")) == "independent draft", "Peer lost");
        Console.WriteLine("PASS crash " + cut);
    }
    {
        string root = Path.Combine(tmp, "conflict"); var i = Setup(root);
        Replace(Source(root), original);
        Expect(Child(root, i, "commit"), State.SourceConflict);
        Expect(Child(root, i, "inspect"), State.NoIntent);
        Bytes(Source(root), original);
    }
    foreach (string stage in new[] { "after-prepared", "before-exchange" })
    {
        string root = Path.Combine(tmp, "external-" + stage); var i = Setup(root);
        byte[] external = Encoding.UTF8.GetBytes("external edit");
        Expect(Exchange(root).CommitForProbe(i, candidate, s => { if (s == stage) Replace(Source(root), external); }), State.RecoveryRequired);
        if (stage == "before-exchange") { Bytes(Source(root), candidate); Bytes(Stage(root, i), external); }
        else Bytes(Source(root), external);
        Expect(Child(root, i, "seal"), State.RecoveryRequired);
        Console.WriteLine("PASS external " + stage);
    }
    foreach (byte[] replacement in new[] { original, candidate })
    {
        string root = Path.Combine(tmp, Guid.NewGuid().ToString("N")); var i = Setup(root);
        KillAt(root, i, "after-exchange");
        Replace(Source(root), replacement);
        Expect(Child(root, i, "inspect"), State.RecoveryRequired);
        Expect(Child(root, i, "seal"), State.RecoveryRequired);
        Bytes(Source(root), replacement); Bytes(Stage(root, i), original);
        Console.WriteLine("PASS same-byte/ABA replacement");
    }
    {
        string root = Path.Combine(tmp, "concurrent"); var i = Setup(root);
        using var p = Worker(root, i, "commit", "after-prepared");
        Check(Line(p) == "CUT after-prepared", "Missing concurrent gate");
        using var q = Worker(root, i, "commit");
        Thread.Sleep(200);
        Check(!q.HasExited, "Lease not held");
        p.Kill(true); p.WaitForExit();
        Check(Line(q) == State.PreparedNotExchanged.ToString(), "Duplicate replay");
        Check(q.WaitForExit(20000) && q.ExitCode == 0, "Duplicate worker failed");
        Bytes(Source(root), original);
        Console.WriteLine("PASS concurrent duplicate without replay");
    }
    {
        string root = Path.Combine(tmp, "history"); var i = Setup(root);
        Expect(Child(root, i, "commit"), State.CompletedHistorical);
        Expect(Child(root, i, "inspect"), State.CompletedHistorical);
        Replace(Source(root), original);
        Expect(Child(root, i, "commit"), State.CompletedHistorical);
        Bytes(Source(root), original);
        Expect(Child(root, i with { RequestFingerprint = Hash("different request") }, "inspect"), State.ConflictingIdentity);
        Console.WriteLine("PASS historical identity");
    }
    {
        string root = Path.Combine(tmp, "permission"); var i = Setup(root);
        if (OperatingSystem.IsLinux()) File.SetUnixFileMode(Source(root), UnixFileMode.UserRead);
        Expect(Child(root, i, "commit"), State.RecoveryRequired);
        Expect(Child(root, i, "inspect"), State.NoIntent);
        Bytes(Source(root), original);
        Console.WriteLine("PASS permission changed");
    }
    foreach (string corrupt in new[] { "prepared.json", "candidate.witness", "original.witness" })
    {
        string root = Path.Combine(tmp, "corrupt-" + corrupt); var i = Setup(root);
        KillAt(root, i, "after-exchange");
        string path = Path.Combine(Recovery(root), "operations", i.OperationId, corrupt);
        File.Delete(path);
        if (corrupt == "prepared.json") File.WriteAllText(path, "{invalid");
        Expect(Child(root, i, "inspect"), State.RecoveryRequired);
        Expect(Child(root, i, "seal"), State.RecoveryRequired);
        Bytes(Source(root), candidate); Bytes(Stage(root, i), original);
        Console.WriteLine("PASS corrupt " + corrupt);
    }
    Console.WriteLine("ALL durable exchange cases passed");
}
finally { Directory.Delete(tmp, true); }
