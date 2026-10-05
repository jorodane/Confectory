using System.Diagnostics;
using System.Text.Json.Nodes;
using Confectory.Core;

namespace Confectory.Tests;

public sealed class VerificationTests : TestCase
{
    private void ExtraImplementation(string body = "return n + 4;", string imports = "")
    {
        f.NewPack("Extra", new() { ["Api"] = "1", ["App"] = "1" });
        f.Packs["App"].Dependencies["Extra"] = "1";
        f.Add("Api", "function", "Extra", "function Api::Extra (int n) -> int {}");
        f.Add("Extra", "implementation", "Body", "implementation Extra::Body for Api::Extra (int n) -> int { " + imports + " body common \"extra.csbody\"; }");
        f.Body("Extra", "extra.csbody", body);
    }

    private void Route(string route, string extraBindings = "")
    {
        if (route == "always") f.Always = ["Extra::Body"];
        f.Main("provide Api::Value with Provider::ValueBody; " + extraBindings + (route == "always" ? "" : route + " implementation Extra::Body;"));
        f.Sync();
    }

    public void test_direct_implementation_inclusion_compiles_and_packages_all_routes()
    {
        foreach (string route in new[] { "always", "use", "contain" })
        {
            ExtraImplementation(); Route(route);
            var report = Build(); Output(report, "5");
            True(report["implementationArtifacts"]!.AsObject().ContainsKey("Extra"), $"{route}: included implementation DLL is missing");
            string assembly = Text(report, "implementationArtifacts", "Extra", "assembly");
            True(File.Exists(Path.Combine(Text(report, "output"), Path.GetFileName(assembly))));
            var catalog = JsonNode.Parse(File.ReadAllText(Text(report, "publicCatalog")))!;
            True(catalog["implementations"]!.AsArray().Any(x => Text(x!, "id") == "Extra::Body"));
            True(catalog["functions"]!.AsArray().Any(x => Text(x!, "id") == "Api::Extra"));
            Emit("direct-" + route, report);
            f.Always = [];
        }
    }

    public void test_direct_implementation_invalid_body_fails_all_routes()
    {
        foreach (string route in new[] { "always", "use", "contain" })
        {
            ExtraImplementation("return \"invalid\";"); Route(route);
            True(Error("TARGET_FAILURE", () => Build()).Message.Contains("extra.csbody", StringComparison.Ordinal));
            f.Always = [];
        }
    }

    public void test_direct_implementation_missing_target_body_fails()
    {
        ExtraImplementation();
        f.Add("Extra", "implementation", "Body", "implementation Extra::Body for Api::Extra (int n) -> int { body other \"extra.csbody\"; }");
        Route("always"); Error("MISSING_TARGET_IMPLEMENTATION", () => Build());
    }

    public void test_direct_implementation_validates_contract()
    {
        ExtraImplementation();
        f.Add("Extra", "implementation", "Body", "implementation Extra::Body for Api::Extra (string n) -> int { body common \"extra.csbody\"; }");
        Route("always"); Error("CONTRACT_MISMATCH", () => Build());
    }

    public void test_module_implementation_edge_compiles_and_validates_body()
    {
        ExtraImplementation();
        f.Add("App", "module", "Included", "module App::Included { use implementation Extra::Body; }");
        Route("always"); f.Always = []; f.Main("provide Api::Value with Provider::ValueBody; module App::Included;"); f.Sync();
        var report = Build(); Output(report, "5");
        Sequence(["App::MainBody", "Extra::Body", "Provider::ValueBody"], Strings(report, "statistics", "compiledImplementations").Order(StringComparer.Ordinal));
        f.Body("Extra", "extra.csbody", "return \"invalid\";");
        Error("TARGET_FAILURE", () => Build());
    }

    public void test_unused_invalid_body_is_pruned_but_local_check_rejects_it()
    {
        f.Add("App", "function", "Spare", "function App::Spare () -> int {}");
        f.Add("App", "implementation", "UnusedBody", "implementation App::UnusedBody for App::Spare () -> int { body common \"unused.csbody\"; }");
        f.Body("App", "unused.csbody", "return \"invalid\";"); f.Sync();
        var report = Build(); Output(report, "5");
        Sequence(["App::MainBody"], Strings(report, "implementationArtifacts", "App", "implementations"));
        Error("TARGET_FAILURE", () => new Builder(f.Project, "portable").Check("App"));
    }

    public void test_always_implementation_without_import_scope_is_rejected()
    {
        ExtraImplementation(imports: "import Api::Value as Value (int) -> int;");
        Route("always"); Error("IMPLEMENTATION_SCOPE", () => Build());
    }

    public void test_direct_implementation_imports_include_dependency_closure()
    {
        foreach (string route in new[] { "always", "use", "contain" })
        {
            f.NewPack("Helper", new() { ["Api"] = "1" });
            f.Packs["App"].Dependencies["Helper"] = "1";
            f.Add("Api", "function", "Helper", "function Api::Helper (int n) -> int {}");
            f.Add("Helper", "implementation", "Body", "implementation Helper::Body for Api::Helper (int n) -> int { body common \"helper.csbody\"; }");
            f.Body("Helper", "helper.csbody", "return n + 10;");
            string scope = route == "always" ? " in App::Main" : "";
            ExtraImplementation("return calls.Helper.Invoke(n);", "import Api::Helper as Helper (int) -> int" + scope + ";");
            Route(route, "provide Api::Helper with Helper::Body;");
            var report = Build(); Output(report, "5");
            True(report["implementationArtifacts"]!.AsObject().ContainsKey("Helper"));
            True(report["bindings"]!.AsArray().Any(x => Text(x!, "owner") == "App::Main" && Text(x!, "function") == "Api::Helper"));
            Emit("closure-" + route, report); f.Always = [];
        }
    }

    public void test_multi_implementation_check_and_final_reuse()
    {
        f.Add("App", "function", "Spare", "function App::Spare () -> int {}");
        f.Add("App", "implementation", "UnusedBody", "implementation App::UnusedBody for App::Spare () -> int { body common \"unused.csbody\"; }");
        f.Body("App", "unused.csbody", "return 1;"); f.Sync();
        var watch = Stopwatch.StartNew();
        var local = new Builder(f.Project, "portable").Check("App"); Emit("multi-check", local, watch.ElapsedMilliseconds);
        var first = Build(); Output(first, "5"); Emit("multi-final-after-check", first);
        string caller = Text(first, "implementationArtifacts", "App", "assembly");
        Equal(Text(local, "artifact", "assembly"), caller);
        Sequence(["Provider"], Strings(first, "statistics", "compiledPacks"));
        var before = (JsonData.HashBytes(File.ReadAllBytes(caller)), File.GetLastWriteTimeUtc(caller));
        var unchanged = Build(); Output(unchanged, "5"); Emit("multi-no-change", unchanged);
        Equal(0, Strings(unchanged, "statistics", "compiledPacks").Length);
        f.Body("App", "unused.csbody", "return 2;");
        var unused = Build(); Output(unused, "5"); Emit("multi-unused-body", unused);
        Equal(0, Strings(unused, "statistics", "compiledPacks").Length);
        var recheck = new Builder(f.Project, "portable").Check("App"); Emit("multi-check-unused-body", recheck);
        Sequence(["App::UnusedBody"], Strings(recheck, "statistics", "compiledImplementations"));
        Sequence(["App::MainBody"], Strings(recheck, "statistics", "reusedImplementations"));
        Equal(before, (JsonData.HashBytes(File.ReadAllBytes(caller)), File.GetLastWriteTimeUtc(caller)));
        var afterCheck = Build(); Emit("multi-final-after-recheck", afterCheck);
        Equal(0, Strings(afterCheck, "statistics", "compiledPacks").Length);
        f.Body("App", "main.csbody", "Console.WriteLine(\"changed\"); Console.WriteLine(calls.Value.Invoke(2)); return 0;");
        var used = Build(); Output(used, "changed\n5"); Emit("multi-used-body", used);
        Sequence(["App"], Strings(used, "statistics", "compiledPacks"));
        Sequence(["App::MainBody"], Strings(used, "statistics", "compiledImplementations"));
        f.Add("Api", "function", "Value", "function Api::Value (int n) -> long {}");
        f.Add("Provider", "implementation", "ValueBody", "implementation Provider::ValueBody for Api::Value (int n) -> long { body common \"value.csbody\"; }");
        Error("CONTRACT_MISMATCH", () => Build());
        f.Add("App", "implementation", "MainBody", "implementation App::MainBody for App::Main () -> int { import Api::Value as Value (int) -> long; body common \"main.csbody\"; }");
        var changedContract = Build(); Output(changedContract, "changed\n5"); Emit("multi-public-contract", changedContract);
        Sequence(["App", "Provider"], Strings(changedContract, "statistics", "compiledPacks"));
        Sequence(["Api::Value"], Strings(changedContract, "statistics", "compiledContracts"));
    }

    private static void Emit(string scenario, JsonObject report, long? elapsed = null)
    {
        Console.WriteLine("OBSERVATION " + JsonData.Object(new
        {
            scenario, elapsedMilliseconds = elapsed, statistics = report["statistics"],
            artifacts = report["implementationArtifacts"] ?? report["artifact"]
        }).ToJsonString());
    }
}
