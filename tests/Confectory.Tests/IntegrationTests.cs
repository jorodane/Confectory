using System.Text;
using System.Text.Json.Nodes;
using Confectory.Core;

namespace Confectory.Tests;

public sealed class IntegrationTests : TestCase
{
    public void test_actual_linked_output_and_public_catalog()
    {
        var report = Build(); Output(report, "5"); Sequence(["App", "Provider"], Strings(report, "statistics", "compiledPacks"));
        True(Strings(report, "excludedPacks").Contains("Unused")); True(Strings(report, "excludedPacks").Contains("Confectory.Build.DotNet")); True(!Strings(report, "statistics", "readDocuments").Any(p => p.EndsWith("Dormant.celem", StringComparison.Ordinal)));
        string text = File.ReadAllText(Text(report, "publicCatalog")); var catalog = JsonNode.Parse(text)!;
        Equal(1, catalog["formatVersion"]!.GetValue<int>()); Equal("linked-elements", Text(catalog, "surface"));
        Sequence(["Api::Value", "App::Main"], catalog["functions"]!.AsArray().Select(x => Text(x!, "id")).Order(StringComparer.Ordinal));
        True(catalog["implementations"]!.AsArray().Any(x => Text(x!, "id") == "Provider::ValueBody")); True(!catalog["coreProvidesRuntimeModLoader"]!.GetValue<bool>()); True(!text.Contains(f.Root, StringComparison.Ordinal));
        Equal(0, Directory.GetFiles(Text(report, "output"), "*.ref.dll").Length);
    }
    public void test_contract_only_compile_without_provider_and_reuse_at_final_link()
    {
        f.Packs.Remove("Provider"); f.Packs["App"].Dependencies.Remove("Provider"); f.Main(); f.Sync(); var local = new Builder(f.Project, "portable").Check("App");
        Equal("contract-only", Text(local, "mode")); Sequence(Encoding.ASCII.GetBytes("MZ"), File.ReadAllBytes(Text(local, "artifact", "assembly")).Take(2));
        True(!Strings(local, "statistics", "readDocuments").Any(p => p.Contains("Provider", StringComparison.Ordinal))); Error("MISSING_IMPLEMENTATION", () => Build());
        f.NewPack("Provider", new() { ["Api"] = "1" }); f.Add("Provider", "implementation", "ValueBody", "implementation Provider::ValueBody for Api::Value (int n) -> int { body common \"value.csbody\"; }"); f.Body("Provider", "value.csbody", "return n + 3;"); f.Packs["App"].Dependencies["Provider"] = "1"; f.Main("provide Api::Value with Provider::ValueBody;"); f.Sync();
        var final = Build(); Output(final, "5"); Equal(Text(local, "artifact", "assembly"), Text(final, "implementationArtifacts", "App", "assembly")); Sequence(["Provider"], Strings(final, "statistics", "compiledPacks"));
    }
    public void test_unchanged_build_and_provider_only_change()
    {
        var first = Build(); Output(first, "5"); string caller = Text(first, "implementationArtifacts", "App", "assembly"); var before = (JsonData.HashBytes(File.ReadAllBytes(caller)), File.GetLastWriteTimeUtc(caller));
        var second = Build(); Output(second, "5"); Equal(0, Strings(second, "statistics", "compiledPacks").Length); Equal(0, Strings(second, "statistics", "compiledContracts").Length);
        if (OperatingSystem.IsLinux()) Equal(0, Strings(second, "statistics", "readDocuments").Length);
        f.Body("Provider", "value.csbody", "return n + 9;"); var changed = Build(); Output(changed, "11"); Output(first, "5"); Sequence(["Provider"], Strings(changed, "statistics", "compiledPacks")); Sequence(["App"], Strings(changed, "statistics", "reusedPacks"));
        Equal(before, (JsonData.HashBytes(File.ReadAllBytes(caller)), File.GetLastWriteTimeUtc(caller)));
        if (OperatingSystem.IsLinux()) { Equal(0, Strings(changed, "statistics", "parsedDocuments").Length); Sequence([Path.Combine(f.Packs["Provider"].Root, "value.csbody")], Strings(changed, "statistics", "readDocuments")); }
    }
    public void test_contract_change_rechecks_consumers_and_rebuilds_only_affected_packs()
    {
        f.NewPack("Stable"); f.Packs["App"].Dependencies["Stable"] = "1";
        f.Add("Stable", "function", "Ping", "function Stable::Ping () -> int { provide Stable::Ping with Stable::PingBody; }"); f.Add("Stable", "implementation", "PingBody", "implementation Stable::PingBody for Stable::Ping () -> int { body common \"ping.csbody\"; }"); f.Body("Stable", "ping.csbody", "return 7;"); f.Always = ["Stable::Ping"]; f.Sync(); var first = Build();
        f.Add("Api", "function", "Value", "function Api::Value (int n) -> long {}"); f.Add("Provider", "implementation", "ValueBody", "implementation Provider::ValueBody for Api::Value (int n) -> long { body common \"value.csbody\"; }"); Error("CONTRACT_MISMATCH", () => Build());
        f.Add("App", "implementation", "MainBody", "implementation App::MainBody for App::Main () -> int { import Api::Value as Value (int) -> long; body common \"main.csbody\"; }"); var changed = Build(); Output(changed, "5");
        Sequence(["App", "Provider"], Strings(changed, "statistics", "compiledPacks")); Sequence(["Stable"], Strings(changed, "statistics", "reusedPacks")); Sequence(["Api::Value"], Strings(changed, "statistics", "compiledContracts")); Equal(Text(first, "implementationArtifacts", "Stable", "assembly"), Text(changed, "implementationArtifacts", "Stable", "assembly"));
        True(Strings(changed, "statistics", "checkedContracts").ToHashSet().IsSupersetOf(["App::Main", "Api::Value", "Stable::Ping"]));
    }
    public void test_unrelated_contract_in_same_pack_does_not_invalidate_consumers()
    {
        f.Add("Api", "function", "UnusedContract", "function Api::UnusedContract (int n) -> int {}"); f.Sync(); Build(); f.Add("Api", "function", "UnusedContract", "function Api::UnusedContract (string n) -> string {}"); var report = Build(); Output(report, "5");
        Equal(0, Strings(report, "statistics", "compiledPacks").Length); Equal(0, Strings(report, "statistics", "compiledContracts").Length); True(!Strings(report, "statistics", "readDocuments").Any(p => p.EndsWith("UnusedContract.celem", StringComparison.Ordinal)));
    }
    public void test_target_specific_common_fallback_and_linux_launcher()
    {
        Output(Build(), "5");
        if (!OperatingSystem.IsLinux()) return;
        var linux = Build("linux"); Output(linux, "32"); Equal("run", Path.GetFileName(Strings(linux, "run")[0])); f.Add("Provider", "implementation", "ValueBody", "implementation Provider::ValueBody for Api::Value (int n) -> int { body common \"value.csbody\"; }"); var fallback = Build("linux"); Output(fallback, "5");
        var catalog = JsonNode.Parse(File.ReadAllText(Text(fallback, "publicCatalog")))!; Equal("common", Text(catalog["implementations"]!.AsArray().Single(x => Text(x!, "id") == "Provider::ValueBody")!, "bodySelection"));
    }
    public void test_broken_selected_target_body_does_not_fall_back()
    {
        string target = OperatingSystem.IsLinux() ? "linux" : "portable";
        if (target == "portable") f.Add("Provider", "implementation", "ValueBody", "implementation Provider::ValueBody for Api::Value (int n) -> int { body common \"value.csbody\"; body portable \"value_linux.csbody\"; }");
        var good = Build(target); f.Body("Provider", "value_linux.csbody", "return \"wrong type\";"); var ex = Error("TARGET_FAILURE", () => Build(target)); True(ex.ToString().Contains("value_linux.csbody", StringComparison.Ordinal)); Output(good, "32");
    }
    public void test_recursive_function_calls_execute()
    { f.Add("Provider", "implementation", "ValueBody", "implementation Provider::ValueBody for Api::Value (int n) -> int { import Api::Value as Self (int) -> int; body common \"value.csbody\"; }"); f.Body("Provider", "value.csbody", "if (n <= 0) return 0; return n + calls.Self.Invoke(n - 1);"); Output(Build(), "3"); }
    public void test_independent_scopes_and_inherited_bindings_execute()
    {
        f.SecondProvider(); f.Module("Default", "Provider::Second"); f.Add("App", "object", "Parent", "object App::Parent { provide Api::Value with Provider::ValueBody; }"); f.Add("App", "object", "Child", "object App::Child extends App::Parent { module App::Default; }"); f.Add("App", "object", "Other", "object App::Other { module App::Default; }"); f.Main();
        f.Add("App", "implementation", "MainBody", "implementation App::MainBody for App::Main () -> int { import Api::Value as First (int) -> int in App::Child; import Api::Value as Second (int) -> int in App::Other; body common \"main.csbody\"; }"); f.Body("App", "main.csbody", "Console.WriteLine($\"{calls.First.Invoke(2)}/{calls.Second.Invoke(2)}\"); return 0;"); f.Sync(); Output(Build(), "5/102");
    }
    public void test_inherited_cross_pack_references_keep_original_owner_dependencies()
    {
        f.NewPack("Parents", new() { ["Api"] = "1", ["Provider"] = "1" }); f.Packs["App"].Dependencies["Parents"] = "1"; f.Packs["App"].Dependencies.Remove("Provider"); f.Add("Parents", "object", "Parent", "object Parents::Parent { provide Api::Value with Provider::ValueBody; }"); f.Add("App", "object", "Child", "object App::Child extends Parents::Parent {}"); f.Main();
        f.Add("App", "implementation", "MainBody", "implementation App::MainBody for App::Main () -> int { import Api::Value as Value (int) -> int in App::Child; body common \"main.csbody\"; }"); f.Sync(); Output(Build(), "5");
    }
    public void test_implementation_inherits_target_body_from_owning_pack()
    {
        f.NewPack("Derived", new() { ["Api"] = "1", ["Provider"] = "1" }); f.Packs["App"].Dependencies["Derived"] = "1"; f.Add("Derived", "implementation", "Body", "implementation Derived::Body for Api::Value (int n) -> int extends Provider::ValueBody {}"); f.Main("provide Api::Value with Derived::Body;"); f.Sync(); var report = Build(); Output(report, "5"); Sequence(["App", "Derived"], Strings(report, "statistics", "compiledPacks"));
    }
    public void test_private_implementation_class_cannot_be_an_authoring_reference()
    { f.Body("App", "main.csbody", $"return new {Generation.Implementation("Provider::ValueBody")}(null!).Invoke(2);"); True(Error("TARGET_FAILURE", () => Build()).ToString().Contains("main.csbody", StringComparison.Ordinal)); }
    public void test_csharp_body_is_type_checked_against_generated_contract()
    { f.Body("App", "main.csbody", "Console.WriteLine(calls.Value.Invoke(\"wrong argument\")); return 0;"); string error = Error("TARGET_FAILURE", () => Build()).ToString(); True(error.Contains("main.csbody", StringComparison.Ordinal)); True(error.Contains("CS1503", StringComparison.Ordinal)); }
    public void test_inherited_build_target_uses_parent_owned_tool()
    { f.NewPack("CustomTarget", new() { ["Confectory.Build.DotNet"] = "0.1.0" }); f.Packs["App"].Dependencies["CustomTarget"] = "1"; f.Add("CustomTarget", "buildtarget", "Portable", "buildtarget CustomTarget::Portable extends Confectory.Build.DotNet::Portable {}"); f.Targets["portable"] = "CustomTarget::Portable"; f.Sync(); Output(Build(), "5"); }
    public void test_distinct_module_defaults_and_missing_target_fail_before_execution()
    {
        f.SecondProvider(); f.Module("M1"); f.Module("M2", "Provider::Second"); f.Main("module App::M1; module App::M2;"); f.Sync(); Error("DEFAULT_CONFLICT", () => Build()); f.Main("provide Api::Value with Provider::ValueBody;"); f.Add("Provider", "implementation", "ValueBody", "implementation Provider::ValueBody for Api::Value (int n) -> int { body other \"value.csbody\"; }"); Error("MISSING_TARGET_IMPLEMENTATION", () => Build());
    }
    public void test_addition_of_a_newer_pack_does_not_change_project_selected_version()
    {
        var first = Build(); string newer = Path.Combine(f.Root, "engine-updates", "Api-2"); Directory.CreateDirectory(newer);
        File.WriteAllText(Path.Combine(newer, "pack.cpack"), "pack Api version \"2\" { element Value function \"Value.celem\"; }"); File.WriteAllText(Path.Combine(newer, "Value.celem"), "function Api::Value (string n) -> string {}"); var unchanged = Build(); Output(unchanged, "5");
        Equal(0, Strings(unchanged, "statistics", "compiledPacks").Length); Equal(Text(first, "contractArtifacts", "Api::Value", "assembly"), Text(unchanged, "contractArtifacts", "Api::Value", "assembly")); var catalog = JsonNode.Parse(File.ReadAllText(Text(unchanged, "publicCatalog")))!; Equal("1", Text(catalog["packs"]!.AsArray().Single(p => Text(p!, "namespace") == "Api")!, "version"));
    }
    public void test_corrupted_local_artifact_is_rebuilt()
    { var first = Build(); File.WriteAllBytes(Text(first, "implementationArtifacts", "App", "assembly"), "corrupted"u8.ToArray()); var repaired = Build(); Output(repaired, "5"); Sequence(["App"], Strings(repaired, "statistics", "compiledPacks")); Sequence(["Provider"], Strings(repaired, "statistics", "reusedPacks")); }
    public void test_tool_binary_change_invalidates_local_artifacts()
    {
        Build();
        // A PE overlay changes the owned tool fingerprint without changing its
        // execution. Real tool source edits take effect after rebuilding its DLL.
        using (var stream = new FileStream(f.ToolPath, FileMode.Append)) stream.Write("tool revision"u8);
        var changed = Build(); Output(changed, "5"); Sequence(["App", "Provider"], Strings(changed, "statistics", "compiledPacks"));
    }
    public void test_failure_preserves_latest_successful_runnable_output()
    {
        var first = Build(); string latest = Path.Combine(f.Packs["App"].Root, ".confectory", "outputs", "portable", "latest.json"); byte[] before = File.ReadAllBytes(latest); f.Body("Provider", "value.csbody", "this is not C#;"); Error("TARGET_FAILURE", () => Build()); Sequence(before, File.ReadAllBytes(latest)); Output(first, "5"); Equal(0, Directory.GetDirectories(Path.Combine(f.Packs["App"].Root, ".confectory"), "*.pending", SearchOption.AllDirectories).Length);
    }
    public void test_selected_versions_warn_without_breaking_executable()
    { f.Packs["App"].Dependencies["Api"] = "99"; f.Sync(); var report = Build(); Output(report, "5"); Equal("VERSION_MISMATCH", Text(report["warnings"]![0]!, "code")); }
    public void test_contract_location_move_keeps_identity_and_local_dlls()
    {
        var first = Build(); var pack = f.Packs["Api"]; File.Move(Path.Combine(pack.Root, "Value.celem"), Path.Combine(pack.Root, "moved.celem")); pack.Elements["Value"] = ("function", "moved.celem"); f.Sync(); var report = Build(); Output(report, "5"); Equal(0, Strings(report, "statistics", "compiledPacks").Length); Equal(Text(first, "contractArtifacts", "Api::Value", "assembly"), Text(report, "contractArtifacts", "Api::Value", "assembly"));
    }
    public void test_local_compilation_reads_do_not_grow_with_unrelated_element_documents()
    {
        var small = new Builder(f.Project, "portable").Check("App"); using var large = new Fixture();
        for (int i = 0; i < 40; i++) { string ns = "Extra" + i; large.NewPack(ns); large.Add(ns, "object", "Data", "invalid and deliberately unopened"); }
        large.Sync(); var big = new Builder(large.Project, "portable").Check("App"); static string[] Reads(JsonObject r) => Strings(r, "statistics", "readDocuments").Where(p => p.EndsWith(".celem", StringComparison.Ordinal) || p.EndsWith(".csbody", StringComparison.Ordinal)).ToArray(); Equal(Reads(small).Length, Reads(big).Length); True(!Reads(big).Any(p => p.Contains("Extra", StringComparison.Ordinal)));
    }
    public void test_bootstrap_projectpack_uses_identical_build_path()
    {
        string engine = Path.Combine(f.Root, "engine"); Fixture.CopyTree(Path.Combine(Fixture.Repo, "examples", "build-bootstrap"), engine); string project = Path.Combine(engine, "project.cpack"); File.WriteAllText(project, File.ReadAllText(project).Replace("../../targets/dotnet/pack.cpack", "../target/pack.cpack", StringComparison.Ordinal)); var report = new Builder(project, "portable").Build(); Output(report, "Confectory.Engine built as a ProjectPack"); Equal("Confectory.Engine::Boot", Text(report, "entry"));
    }
    public void test_missing_target_and_tool_protocol_errors()
    {
        Error("MISSING_TARGET", () => new Builder(f.Project, "unknown")); File.Delete(f.ToolPath); Error("MISSING_TOOL", () => new Builder(f.Project, "portable"));
        f.FakeTool("not json"); Error("TOOL_PROTOCOL", () => new Builder(f.Project, "portable"));
        f.FakeTool("{\"protocol\":999,\"ok\":true}"); Error("TOOL_PROTOCOL", () => new Builder(f.Project, "portable"));
        f.FakeTool("{\"protocol\":1,\"ok\":false,\"error\":\"intentional tool failure\"}"); Error("TARGET_FAILURE", () => new Builder(f.Project, "portable"));
    }
    public void test_cli_run_streams_output_propagates_exit_and_spaced_paths()
    {
        string cli=Path.Combine(Fixture.Repo,"src","Confectory.Cli","bin","Release","net10.0","Confectory.Cli.dll");
        // Windows environment names are case insensitive: a helper must not overwrite CONFECTORY_DOTNET.
        foreach(string batch in new[]{"build-windows.bat","run-engine-windows.bat"})
            True(!File.ReadAllText(Path.Combine(Fixture.Repo,batch)).Contains("set \"confectory_dotnet=",StringComparison.OrdinalIgnoreCase));
        using var spaced=new Fixture(Path.Combine(f.Root,"launch project with spaces"));
        spaced.Body("App","main.csbody","Console.WriteLine(\"launched project\"); Console.Error.WriteLine(\"visible diagnostic\"); return 7;");spaced.Sync();
        var result=Processes.Run([Processes.DotNet(),cli,"run",spaced.Project,"portable"],timeoutSeconds:90);
        Equal(7,result.ExitCode);True(result.Stdout.Contains("launched project",StringComparison.Ordinal));True(result.Stderr.Contains("visible diagnostic",StringComparison.Ordinal));True(result.Stderr.Contains("Resolving/building",StringComparison.Ordinal));True(result.Stderr.Contains("Project process started:",StringComparison.Ordinal));True(result.Stderr.Contains("Project exited: 7",StringComparison.Ordinal));
        string launcher=File.ReadAllText(Path.Combine(Fixture.Repo,"run-engine-windows.bat"));True(launcher.Contains("call \"%~dp0build-windows.bat\"",StringComparison.OrdinalIgnoreCase));True(launcher.Contains("call \"%confectory_launcher_dotnet%\"",StringComparison.OrdinalIgnoreCase));
        var missing=Processes.Run([Processes.DotNet(),cli,"run",spaced.Project,"missing"],timeoutSeconds:30);Equal(1,missing.ExitCode);True(missing.Stdout.Contains("MISSING_TARGET",StringComparison.Ordinal));
    }
    public void test_cli_preserves_json_reports_and_exit_codes()
    {
        string cli = Path.Combine(Fixture.Repo, "src", "Confectory.Cli", "bin", "Release", "net10.0", "Confectory.Cli.dll");
        var check = Processes.Run([Processes.DotNet(), cli, "check", f.Project, "portable", "App"]); Equal(0, check.ExitCode); Equal("contract-only", Text(JsonNode.Parse(check.Stdout)!, "mode"));
        var build = Processes.Run([Processes.DotNet(), cli, "build", f.Project, "portable"]); Equal(0, build.ExitCode); Output(JsonNode.Parse(build.Stdout)!.AsObject(), "5");
        var missing = Processes.Run([Processes.DotNet(), cli, "build", f.Project, "absent"]); Equal(1, missing.ExitCode); Equal("MISSING_TARGET", Text(JsonNode.Parse(missing.Stdout)!["diagnostics"]![0]!, "code")); True(missing.Stderr.Contains("MISSING_TARGET", StringComparison.Ordinal));
        Equal(2, Processes.Run([Processes.DotNet(), cli, "check", f.Project, "portable"]).ExitCode);
    }
    public void test_validate_checks_unreached_declarations_without_compiling()
    {
        var clean = new Builder(f.Project, "portable").Validate(); Equal("validate", Text(clean, "mode")); Equal(0, Strings(clean, "statistics", "compiledPacks").Length);
        f.Add("Unused", "object", "Dormant", "not valid declaration text"); Output(Build(), "5"); Error("KIND", () => new Builder(f.Project, "portable").Validate());
    }
    public void test_utf8_pack_and_body_paths_with_spaces_execute()
    {
        using var spaced = new Fixture(Path.Combine(f.Root, "한글 프로젝트 with spaces"));
        spaced.Body("Provider", "value.csbody", "Console.WriteLine(\"안녕하세요\"); return n + 3;");
        Output(new Builder(spaced.Project, "portable").Build(), "안녕하세요\n5");
    }
    public void test_compiler_artifacts_cannot_escape_requested_output()
    {
        string outside = Path.Combine(f.Root, "outside.dll"); File.WriteAllText(outside, "sentinel");
        f.FakeTool(JsonData.Object(new { protocol = 1, ok = true, fingerprint = "fake", artifacts = new { assembly = outside, reference = outside } }).ToJsonString());
        Error("OWNERSHIP", () => Build()); Equal("sentinel", File.ReadAllText(outside));
    }
}
