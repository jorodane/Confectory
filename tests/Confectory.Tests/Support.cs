using System.Text.Json;
using System.Text.Json.Nodes;
using Confectory.Core;

namespace Confectory.Tests;

public sealed class Fixture : IDisposable
{
    public sealed class Pack(string root, Dictionary<string, string> dependencies, string version)
    {
        public string Root { get; } = root;
        public Dictionary<string, string> Dependencies { get; } = dependencies;
        public string Version { get; set; } = version;
        public Dictionary<string, (string Kind, string Path)> Elements { get; } = new(StringComparer.Ordinal);
    }
    public static string Repo { get; } = FindRepo();
    private static string FindRepo()
    {
        var current = new DirectoryInfo(AppContext.BaseDirectory);
        while (current is not null)
        {
            if (File.Exists(Path.Combine(current.FullName, "Confectory.sln"))) return current.FullName;
            current = current.Parent;
        }
        throw new IOException("Run tests from the Confectory checkout");
    }
    public string Root { get; } = Path.Combine(Path.GetTempPath(), "confectory-test-" + Guid.NewGuid().ToString("N"));
    public Dictionary<string, Pack> Packs { get; } = new(StringComparer.Ordinal);
    public string? Entry { get; set; } = "App::Main";
    public List<string> Always { get; set; } = [];
    public Dictionary<string, string> Targets { get; } = new() { ["portable"] = "Confectory.Build.DotNet::Portable", ["linux"] = "Confectory.Build.DotNet::Linux" };
    public Dictionary<string, string> ExtraRegistry { get; } = new(StringComparer.Ordinal);
    public string Project => Path.Combine(Packs["App"].Root, "project.cpack");
    public string ToolPath => Path.Combine(Root, "target", "bin", "Release", "net10.0", "Confectory.Build.DotNet.dll");

    public Fixture(string? root = null)
    {
        if (root is not null) Root = root;
        Directory.CreateDirectory(Root);
        NewPack("App", new() { ["Api"] = "1", ["Provider"] = "1", ["Confectory.Build.DotNet"] = "0.1.0" });
        NewPack("Api"); NewPack("Provider", new() { ["Api"] = "1" }); NewPack("Unused");
        CopyTree(Path.Combine(Repo, "targets", "dotnet"), Path.Combine(Root, "target"));
        ExtraRegistry["Confectory.Build.DotNet"] = Path.Combine(Root, "target", "pack.cpack");
        Main("provide Api::Value with Provider::ValueBody;");
        Add("App", "implementation", "MainBody", "implementation App::MainBody for App::Main () -> int { import Api::Value as Value (int) -> int; body common \"main.csbody\"; }");
        Body("App", "main.csbody", "Console.WriteLine(calls.Value.Invoke(2)); return 0;");
        Add("Api", "function", "Value", "function Api::Value (int n) -> int {}");
        Add("Provider", "implementation", "ValueBody", "implementation Provider::ValueBody for Api::Value (int n) -> int { body common \"value.csbody\"; body linux \"value_linux.csbody\"; }");
        Body("Provider", "value.csbody", "return n + 3;"); Body("Provider", "value_linux.csbody", "return n + 30;");
        Add("Unused", "object", "Dormant", "object Unused::Dormant { value note = \"unused\"; }"); Sync();
    }
    public void NewPack(string ns, Dictionary<string, string>? dependencies = null, string version = "1")
    {
        string root = Path.Combine(Root, ns.Replace('.', '_')); Directory.CreateDirectory(root);
        Packs[ns] = new(root, dependencies ?? new(StringComparer.Ordinal), version);
    }
    public string Add(string ns, string kind, string local, string text)
    {
        string filename = local + ".celem", path = Path.Combine(Packs[ns].Root, filename);
        Packs[ns].Elements[local] = (kind, filename); File.WriteAllText(path, text + "\n"); return path;
    }
    public string Body(string ns, string filename, string text)
    {
        string path = Path.Combine(Packs[ns].Root, filename); File.WriteAllText(path, text + "\n"); return path;
    }
    private static string Quote(string value) => JsonSerializer.Serialize(value, JsonData.Options);
    public void Sync()
    {
        foreach (var (ns, pack) in Packs)
        {
            bool project = ns == "App";
            List<string> lines = [$"{(project ? "project" : "pack")} {ns} version {Quote(pack.Version)} {{"];
            if (project)
            {
                if (Entry is not null) lines.Add($"entry {Entry};");
                var registrations = Packs.Where(x => x.Key != "App").ToDictionary(x => x.Key, x => Path.Combine(x.Value.Root, "pack.cpack"));
                foreach (var (other, path) in ExtraRegistry) registrations[other] = path;
                lines.AddRange(registrations.Select(x => $"registry {x.Key} {Quote(x.Value)};"));
                lines.AddRange(Targets.Select(x => $"target {x.Key} {x.Value};")); lines.AddRange(Always.Select(x => $"always {x};"));
            }
            lines.AddRange(pack.Dependencies.Select(x => $"dependency {x.Key} version {Quote(x.Value)};"));
            lines.AddRange(pack.Elements.Select(x => $"element {x.Key} {x.Value.Kind} {Quote(x.Value.Path)};"));
            lines.Add("}"); File.WriteAllText(Path.Combine(pack.Root, project ? "project.cpack" : "pack.cpack"), string.Join("\n", lines) + "\n");
        }
    }
    public Registry Registry()
    {
        var stats = new BuildStatistics(); return new(Project, new Documents(Path.Combine(Root, "document-cache"), stats), stats);
    }
    public Planner Plan(string target = "portable") => new Planner(Registry(), target).Plan();
    public string Main(string extras = "") => Add("App", "function", "Main", "function App::Main () -> int { provide App::Main with App::MainBody; " + extras + " }");
    public void Module(string name, string? provider = "Provider::ValueBody", string includes = "")
        => Add("App", "module", name, $"module App::{name} {{ require Api::Value (int) -> int; {includes}" + (provider is null ? "" : $"default Api::Value with {provider};") + "}");
    public void SecondProvider()
    {
        Add("Provider", "implementation", "Second", "implementation Provider::Second for Api::Value (int n) -> int { body common \"second.csbody\"; }"); Body("Provider", "second.csbody", "return n + 100;");
    }
    public void FakeTool(string reply)
    {
        string fake = Path.Combine(Root, "target", "fake"); Directory.CreateDirectory(fake);
        foreach (string file in Directory.GetFiles(AppContext.BaseDirectory)) File.Copy(file, Path.Combine(fake, Path.GetFileName(file)), true);
        File.WriteAllText(Path.Combine(fake, "fake-reply.txt"), reply);
        foreach (string name in new[] { "portable.celem", "linux.celem" })
        {
            string path = Path.Combine(Root, "target", name); File.WriteAllText(path, File.ReadAllText(path).Replace("bin/Release/net10.0/Confectory.Build.DotNet.dll", "fake/Confectory.Tests.dll", StringComparison.Ordinal));
        }
    }
    public static void CopyTree(string source, string destination)
    {
        Directory.CreateDirectory(destination);
        foreach (string file in Directory.GetFiles(source)) File.Copy(file, Path.Combine(destination, Path.GetFileName(file)), true);
        foreach (string directory in Directory.GetDirectories(source))
        {
            if (Path.GetFileName(directory) is "obj" or ".confectory") continue;
            CopyTree(directory, Path.Combine(destination, Path.GetFileName(directory)));
        }
    }
    public void Dispose() { if (Directory.Exists(Root)) Directory.Delete(Root, true); }
}

public sealed class SkippedException(string reason) : Exception(reason);

public abstract class TestCase : IDisposable
{
    protected static void Skip(string reason) => throw new SkippedException(reason);
    protected readonly Fixture f = new();
    protected static void True(bool condition, string message = "Assertion failed") { if (!condition) throw new Exception(message); }
    protected static void Equal<T>(T expected, T actual) { if (!EqualityComparer<T>.Default.Equals(expected, actual)) throw new Exception($"Expected {expected}; actual {actual}"); }
    protected static void Sequence<T>(IEnumerable<T> expected, IEnumerable<T> actual) { if (!expected.SequenceEqual(actual)) throw new Exception($"Expected [{string.Join(",", expected)}]; actual [{string.Join(",", actual)}]"); }
    protected static BuildError Error(string code, Action action)
    {
        try { action(); } catch (BuildError ex) { Equal(code, ex.Diagnostic.Code); return ex; }
        throw new Exception($"Expected BuildError {code}");
    }
    protected JsonObject Build(string target = "portable") => new Builder(f.Project, target).Build();
    protected static string[] Strings(JsonNode report, params string[] keys)
    {
        foreach (string key in keys) report = report[key]!;
        return report.AsArray().Select(x => x!.GetValue<string>()).ToArray();
    }
    protected static string Text(JsonNode report, params string[] keys)
    {
        foreach (string key in keys) report = report[key]!;
        return report.GetValue<string>();
    }
    protected static void Output(JsonObject report, string expected)
    {
        var result = Processes.Run(Strings(report, "run"), timeoutSeconds: 15);
        True(result.ExitCode == 0, result.Stderr); Equal(expected + "\n", result.Stdout.Replace("\r\n", "\n", StringComparison.Ordinal));
    }
    public void Dispose() => f.Dispose();
}
