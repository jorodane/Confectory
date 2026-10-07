using Confectory.Core;

namespace Confectory.Tests;

public sealed class CoreTests : TestCase
{
    public void test_namespace_qualified_same_local_id()
    {
        f.Add("Api", "object", "Same", "object Api::Same {}"); f.Add("Provider", "object", "Same", "object Provider::Same {}");
        f.Main("provide Api::Value with Provider::ValueBody; use object Api::Same; use object Provider::Same;"); f.Sync();
        True(f.Plan().Reached.IsSupersetOf(["Api::Same", "Provider::Same"]));
    }
    public void test_duplicate_namespace() { f.ExtraRegistry["Alias"] = Path.Combine(f.Packs["Api"].Root, "pack.cpack"); f.Sync(); Error("DUPLICATE_NAMESPACE", () => f.Registry()); }
    public void test_duplicate_element()
    {
        File.WriteAllText(f.Project, File.ReadAllText(f.Project).Replace("element Main function \"Main.celem\";", "element Main function \"Main.celem\"; element Main object \"other.celem\";", StringComparison.Ordinal)); Error("DUPLICATE_DECLARATION", () => f.Registry());
    }
    public void test_wrong_locator_and_source_locations()
    {
        f.Add("Api", "function", "Value", "function Api::Other (int n) -> int {}"); var diag = Error("LOCATOR_MISMATCH", () => f.Plan()).Diagnostic;
        True(diag.Location.File.EndsWith("Value.celem", StringComparison.Ordinal)); Equal(1, diag.Location.Line);
    }
    public void test_missing_namespace() { f.Packs["App"].Dependencies["Absent"] = "1"; f.Sync(); Error("MISSING_NAMESPACE", () => f.Registry()); }
    public void test_missing_element() { f.Main("provide Api::Absent with Provider::ValueBody;"); Error("MISSING_ELEMENT", () => f.Plan()); }
    public void test_wrong_element_kind() { f.Main("provide Api::Value with Api::Value;"); Error("ELEMENT_KIND", () => f.Plan()); }
    public void test_undeclared_cross_pack_dependency() { f.Packs["App"].Dependencies.Remove("Api"); f.Sync(); Error("UNDECLARED_DEPENDENCY", () => f.Plan()); }
    public void test_provider_signature_mismatch()
    { f.Add("Provider", "implementation", "ValueBody", "implementation Provider::ValueBody for Api::Value (string n) -> int { body common \"value.csbody\"; }"); Error("CONTRACT_MISMATCH", () => f.Plan()); }
    public void test_import_signature_mismatch()
    { f.Add("App", "implementation", "MainBody", "implementation App::MainBody for App::Main () -> int { import Api::Value as Value (string) -> int; body common \"main.csbody\"; }"); Error("CONTRACT_MISMATCH", () => f.Plan()); }
    public void test_provider_wrong_function_identity()
    {
        f.Add("Api", "function", "Other", "function Api::Other (int n) -> int {}"); f.Add("Provider", "implementation", "ValueBody", "implementation Provider::ValueBody for Api::Other (int n) -> int { body common \"value.csbody\"; }"); f.Sync(); Error("IMPLEMENTATION_ID", () => f.Plan());
    }
    public void test_missing_final_provider() { f.Main(); Error("MISSING_IMPLEMENTATION", () => f.Plan()); }
    public void test_missing_target_and_common_body()
    { f.Add("Provider", "implementation", "ValueBody", "implementation Provider::ValueBody for Api::Value (int n) -> int { body other \"value.csbody\"; }"); Error("MISSING_TARGET_IMPLEMENTATION", () => f.Plan()); }
    public void test_duplicate_target_body_and_unknown_syntax()
    {
        Error("DUPLICATE_DECLARATION", () => new Parser("implementation X::F for X::Fn () -> int { body common \"a\"; body common \"b\"; }", "test.celem").ParseElement());
        Error("SYNTAX", () => new Parser("object X::O { delete field; }", "test.celem").ParseElement());
        Error("TYPE", () => new Parser("function X::F (object data) -> int {}", "test.celem").ParseElement());
    }
    public void test_single_module_default()
    { f.Module("M"); f.Main("module App::M;"); f.Sync(); Equal("Provider::ValueBody", f.Plan().Bindings[new("App::Main", "Api::Value")].Implementation); }
    public void test_explicit_binding_beats_multiple_defaults()
    {
        f.SecondProvider(); f.Module("M1"); f.Module("M2", "Provider::Second"); f.Main("module App::M1; module App::M2; provide Api::Value with Provider::ValueBody;"); f.Sync(); Equal("Provider::ValueBody", f.Plan().Bindings[new("App::Main", "Api::Value")].Implementation);
    }
    public void test_different_defaults_conflict()
    { f.SecondProvider(); f.Module("M1"); f.Module("M2", "Provider::Second"); f.Main("module App::M1; module App::M2;"); f.Sync(); Error("DEFAULT_CONFLICT", () => f.Plan()); }
    public void test_same_default_deduplicates_through_nested_modules()
    {
        f.Module("M1"); f.Module("M2"); f.Add("App", "module", "Combined", "module App::Combined { include App::M1; include App::M2; }"); f.Main("module App::Combined;"); f.Sync(); Equal("Provider::ValueBody", f.Plan().Bindings[new("App::Main", "Api::Value")].Implementation);
    }
    public void test_module_missing_default() { f.Module("M", null); f.Main("module App::M;"); f.Sync(); Error("MISSING_IMPLEMENTATION", () => f.Plan()); }
    public void test_invalid_default_cannot_hide_behind_explicit_binding()
    { f.Module("M", "Api::Value"); f.Main("module App::M; provide Api::Value with Provider::ValueBody;"); f.Sync(); Error("ELEMENT_KIND", () => f.Plan()); }
    public void test_default_not_in_module_contract()
    { f.Add("App", "module", "M", "module App::M { default Api::Value with Provider::ValueBody; }"); f.Main("module App::M; provide Api::Value with Provider::ValueBody;"); f.Sync(); Error("MODULE_CONTRACT", () => f.Plan()); }
    public void test_module_contract_signature()
    { f.Add("App", "module", "M", "module App::M { require Api::Value (long) -> int; }"); f.Main("module App::M; provide Api::Value with Provider::ValueBody;"); f.Sync(); Error("CONTRACT_MISMATCH", () => f.Plan()); }
    public void test_inherited_values_and_provenance_without_parent_mutation()
    {
        f.Add("App", "object", "Parent", "object App::Parent { value enabled = true; value count = 10; value label = \"parent\"; value inherited = 5; }");
        f.Add("App", "object", "Child", "object App::Child extends App::Parent { value enabled = false; value count = 0; value label = \"\"; value added = 2; }"); f.Add("App", "object", "Sibling", "object App::Sibling extends App::Parent {}"); f.Sync();
        var r = f.Registry(); string before = JsonData.Digest(r.Get("App::Parent")); var child = r.Effective("App::Child").Values;
        Equal(false, child["enabled"].Value.GetBoolean()); Equal(0, child["count"].Value.GetInt32()); Equal("", child["label"].Value.GetString());
        Equal("App::Parent", child["inherited"].Origin); Equal("App::Child", child["added"].Origin); Equal(10, r.Effective("App::Sibling").Values["count"].Value.GetInt32()); Equal(before, JsonData.Digest(r.Get("App::Parent")));
    }
    public void test_inherited_binding_beats_defaults()
    {
        f.SecondProvider(); f.Module("M", "Provider::Second"); f.Add("App", "object", "Parent", "object App::Parent { provide Api::Value with Provider::ValueBody; }"); f.Add("App", "object", "Child", "object App::Child extends App::Parent { module App::M; }"); f.Main("use object App::Child;");
        f.Add("App", "implementation", "MainBody", "implementation App::MainBody for App::Main () -> int { import Api::Value as Value (int) -> int in App::Child; body common \"main.csbody\"; }"); f.Sync(); Equal("Provider::ValueBody", f.Plan().Bindings[new("App::Child", "Api::Value")].Implementation);
    }
    public void test_explicit_empty_description_overrides_parent()
    {
        f.Add("App", "object", "Parent", "object App::Parent { description \"parent\"; }"); f.Add("App", "object", "Omitted", "object App::Omitted extends App::Parent {}"); f.Add("App", "object", "Empty", "object App::Empty extends App::Parent { description \"\"; }"); f.Sync(); var r = f.Registry(); Equal("parent", r.Effective("App::Omitted").Description); Equal("", r.Effective("App::Empty").Description);
    }
    public void test_changed_text_with_restored_mtime_is_not_a_stale_document_hit()
    {
        string p = f.Add("Unused", "object", "Dormant", "object Unused::Dormant { value n = 1; }"); f.Sync(); var before = File.GetLastWriteTimeUtc(p); Equal(1, f.Registry().Effective("Unused::Dormant").Values["n"].Value.GetInt32());
        File.WriteAllText(p, File.ReadAllText(p).Replace("= 1", "= 2", StringComparison.Ordinal)); File.SetLastWriteTimeUtc(p, before); Equal(2, f.Registry().Effective("Unused::Dormant").Values["n"].Value.GetInt32());
    }
    public void test_parent_missing_wrong_kind_and_multiple_parent_syntax()
    {
        f.Add("App", "object", "Child", "object App::Child extends Api::Missing {}"); f.Sync(); var r = f.Registry(); Error("MISSING_ELEMENT", () => r.Effective("App::Child"));
        f.Add("App", "object", "Child", "object App::Child extends Api::Value {}"); r = f.Registry(); Error("ELEMENT_KIND", () => r.Effective("App::Child"));
        Error("SYNTAX", () => new Parser("object App::Child extends App::A extends App::B {}", "child.celem").ParseElement());
    }
    public void test_inheritance_cycle()
    { f.Add("App", "object", "A", "object App::A extends App::B {}"); f.Add("App", "object", "B", "object App::B extends App::A {}"); f.Sync(); var r = f.Registry(); Error("INHERITANCE_CYCLE", () => r.Effective("App::A")); }
    public void test_containment_cycle()
    { f.Add("App", "object", "A", "object App::A { contain object App::B; }"); f.Add("App", "object", "B", "object App::B { contain object App::A; }"); f.Main("provide Api::Value with Provider::ValueBody; use object App::A;"); f.Sync(); Error("STRUCTURAL_CYCLE", () => f.Plan()); }
    public void test_module_inclusion_cycle()
    { f.Add("App", "module", "A", "module App::A { include App::B; }"); f.Add("App", "module", "B", "module App::B { include App::A; }"); f.Main("provide Api::Value with Provider::ValueBody; module App::A;"); f.Sync(); Error("STRUCTURAL_CYCLE", () => f.Plan()); }
    public void test_reference_cycle_is_allowed()
    { f.Add("App", "object", "A", "object App::A { use object App::B; }"); f.Add("App", "object", "B", "object App::B { use object App::A; }"); f.Main("provide Api::Value with Provider::ValueBody; use object App::A;"); f.Sync(); True(f.Plan().Reached.IsSupersetOf(["App::A", "App::B"])); }
    public void test_transitive_stage_view_inheritance_and_always()
    {
        f.Add("App", "stage", "Stage", "stage App::Stage { contain view App::Screen; }"); f.Add("App", "view", "Screen", "view App::Screen extends App::BaseScreen {}"); f.Add("App", "view", "BaseScreen", "view App::BaseScreen { use object Api::Thing; }"); f.Add("Api", "object", "Thing", "object Api::Thing {}"); f.Main("provide Api::Value with Provider::ValueBody; use stage App::Stage;"); f.Always = ["Unused::Dormant"]; f.Packs["App"].Dependencies["Unused"] = "1"; f.Sync(); True(f.Plan().Reached.IsSupersetOf(["App::Stage", "App::Screen", "App::BaseScreen", "Api::Thing", "Unused::Dormant"]));
    }
    public void test_unused_documents_are_not_read()
    { f.Add("Unused", "object", "Dormant", "not valid declaration text"); var plan = f.Plan(); True(!plan.Reached.Contains("Unused::Dormant")); True(!plan.Registry.Statistics.ReadDocuments.Any(p => p.EndsWith("Dormant.celem", StringComparison.Ordinal))); }
    public void test_version_ranges_are_pure_warnings_without_selection_changes()
    {
        foreach(string range in new[]{"^1.0.0",">=1.0.0 <2.0.0","1.*","~1.0"})
        { f.Packs["App"].Dependencies["Api"]=range;f.Sync();var registry=f.Registry();Equal(0,registry.Warnings.Count);Equal("1",registry.Packs["Api"].Version); }
        foreach(string range in new[]{"^2.0.0",">=2 <3","unsupported-range"})
        { f.Packs["App"].Dependencies["Api"]=range;f.Sync();var registry=f.Registry();Equal("VERSION_MISMATCH",registry.Warnings[0].Code);Equal("1",registry.Packs["Api"].Version); }
        True(VersionExpectation.Matches("^0.2.3","0.2.9"));True(!VersionExpectation.Matches("^0.2.3","0.3.0"));True(VersionExpectation.Matches("^0.0.3","0.0.3"));True(!VersionExpectation.Matches("^0.0.3","0.0.4"));
    }

    public void test_version_mismatch_is_only_warning_and_is_pinned()
    { f.Packs["App"].Dependencies["Api"] = "999"; f.Sync(); var plan = f.Plan(); Equal("VERSION_MISMATCH", plan.Registry.Warnings[0].Code); Equal("1", plan.Registry.Packs["Api"].Version); }
    public void test_owned_source_path_cannot_escape_pack()
    { f.Packs["Api"].Elements["Value"] = ("function", "../outside.celem"); f.Sync(); Error("OWNERSHIP", () => f.Registry()); }
    public void test_entry_is_required_and_typed()
    { f.Entry = null; f.Sync(); Error("MISSING_ENTRY", () => f.Plan()); f.Entry = "Api::Value"; f.Sync(); Error("ENTRY_CONTRACT", () => f.Plan()); }
    public void test_project_input_cannot_be_a_regular_pack()
    { File.WriteAllText(f.Project, "pack App version \"1\" {}"); Error("PROJECT_INPUT", () => f.Registry()); }
    public void test_corrupted_document_cache_is_reparsed()
    {
        f.Registry().Effective("Api::Value");
        foreach (string cache in Directory.GetFiles(Path.Combine(f.Root, "document-cache"), "*.json")) File.WriteAllText(cache, "broken json");
        var registry = f.Registry(); Equal("Api::Value", registry.Get("Api::Value").Id); True(registry.Statistics.ParsedDocuments.Count > 0);
    }
    public void test_non_utf8_source_reports_owned_location()
    {
        string path = Path.Combine(f.Packs["Api"].Root, "Value.celem"); File.WriteAllBytes(path, [0xff, 0xfe]);
        var error = Error("SOURCE_READ", () => f.Plan()); Equal(path, error.Diagnostic.Location.File);
    }
    public void test_owned_source_symlink_cannot_escape_pack()
    {
        if (!OperatingSystem.IsLinux()) Skip("Requires Linux fixture host");
        string outside = Path.Combine(f.Root, "outside.celem"); File.WriteAllText(outside, "function Api::Value (int n) -> int {}");
        string link = Path.Combine(f.Packs["Api"].Root, "linked.celem"); File.CreateSymbolicLink(link, outside);
        f.Packs["Api"].Elements["Value"] = ("function", "linked.celem"); f.Sync(); Error("OWNERSHIP", () => f.Registry());
    }
}
