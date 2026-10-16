using Confectory.Core;
namespace Confectory.Tests;
public sealed class WebUITests : TestCase
{
    public void test_actual_editor_original_v196_home_project_and_create_flow()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples","editor-home","project.cpack"),"linux").Build();
        string report=Path.Combine(f.Root,"original-layout.json"),reference=Path.Combine(f.Root,"original-v196");
        File.WriteAllText(report,built.ToJsonString());
        System.IO.Compression.ZipFile.ExtractToDirectory(Path.Combine(Fixture.Repo,"reference","site-ui","Confectory-Editor-Prototype-v196.zip"),reference);
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests","web","editor_home_original_layout.py"),Fixture.Repo,report,reference},timeoutSeconds:180);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS ordinary ProjectPack original Home"));
    }
    public void test_actual_editor_layout_periodic_checkpoints_and_flush()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples","editor-home","project.cpack"),"linux").Build();
        string report=Path.Combine(f.Root,"layout-saves.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/editor_layout_saves.py"),Fixture.Repo,report,"after"},timeoutSeconds:240);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS ordinary ProjectPack actual periodic layout"));
    }
    public void test_actual_editor_v318_yogi_owned_content_and_validation_restart()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples","editor-home","project.cpack"),"linux").Build();
        string report=Path.Combine(f.Root,"v318-yogi.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/editor_yogi_v318.py"),Fixture.Repo,report},timeoutSeconds:600);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS ordinary ProjectPack durable Yogi"));
    }
    public void test_actual_editor_v318_run_process_and_presentation_restart()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples","editor-home","project.cpack"),"linux").Build();
        string report=Path.Combine(f.Root,"v318-run.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/editor_run_v318.py"),Fixture.Repo,report},timeoutSeconds:600);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS ordinary ProjectPack actual Run"));
    }
    public void test_actual_editor_v318_helper_inputs_and_panels_cold_restart()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples","editor-home","project.cpack"),"linux").Build();
        string report=Path.Combine(f.Root,"v318-participants.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/editor_participants_v318.py"),Fixture.Repo,report},timeoutSeconds:240);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS ordinary ProjectPack actual Helper identity"));
    }
    public void test_actual_editor_v318_home_agent_connection_entry_and_saved_settings()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples","editor-home","project.cpack"),"linux").Build();
        string report=Path.Combine(f.Root,"v318-connection-entry.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/editor_connection_entry_v318.py"),Fixture.Repo,report},timeoutSeconds:360);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual Home AI Agent entry"));
    }
    public void test_actual_editor_v318_helper_connection_chat_state_and_ownership()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples","editor-home","project.cpack"),"linux").Build();
        string report=Path.Combine(f.Root,"v318-helper-ai.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/editor_helper_ai_v318.py"),Fixture.Repo,report},timeoutSeconds:360);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS ordinary ProjectPack helper connection settings"));
    }
    public void test_actual_editor_v318_codex_verification_and_helper_grants()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples","editor-home","project.cpack"),"linux").Build();
        string report=Path.Combine(f.Root,"v318-codex-verification.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/editor_codex_verification_v318.py"),Fixture.Repo,report},timeoutSeconds:480);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual Home Codex verification and Helper grants"));
    }
    public void test_actual_editor_v318_codex_discovery_and_official_model_selection()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples","editor-home","project.cpack"),"linux").Build();
        string report=Path.Combine(f.Root,"v318-codex-discovery.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/editor_codex_discovery_v318.py"),Fixture.Repo,report},timeoutSeconds:480);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual Home Codex candidate discovery"));
    }
    public void test_actual_editor_v318_legacy_codex_and_novice_installation_guide()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples","editor-home","project.cpack"),"linux").Build();
        string report=Path.Combine(f.Root,"v318-codex-installation-guide.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/editor_codex_install_guide_v318.py"),Fixture.Repo,report},timeoutSeconds:480);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual Home legacy Codex discovery and novice preparation guide"));
    }
    public void test_actual_editor_click_preparation_and_device_login_owned_fixtures()
    {
        string home=Path.Combine(f.Root,"home"),agent=Path.Combine(f.Root,"agent"),descriptor=Path.Combine(f.Root,"preparation.json");
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples/editor-home"),home);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs/agent-codex"),agent);
        string manifest=Path.Combine(home,"project.cpack");
        File.WriteAllText(manifest,System.Text.RegularExpressions.Regex.Replace(File.ReadAllText(manifest),"(registry [A-Za-z0-9_.]+ )\"([^\"]+)\"",match=>match.Groups[1].Value+System.Text.Json.JsonSerializer.Serialize(Path.GetFullPath(Path.Combine(Fixture.Repo,"examples/editor-home",match.Groups[2].Value)))));
        File.WriteAllText(manifest,File.ReadAllText(manifest).Replace(System.Text.Json.JsonSerializer.Serialize(Path.Combine(Fixture.Repo,"packs/agent-codex/pack.cpack")),System.Text.Json.JsonSerializer.Serialize(Path.Combine(agent,"pack.cpack")),StringComparison.Ordinal));
        // A normal copied-pack provider supplies ONLY this owned fixture's immutable authority; production has no test environment switch.
        File.WriteAllText(Path.Combine(agent,"PreparationInfo.csbody"),"return System.IO.File.ReadAllText("+System.Text.Json.JsonSerializer.Serialize(descriptor)+");\n");
        string storageBody=Path.Combine(agent,"PreparationStorage.csbody"),hold=Path.Combine(f.Root,"owned-hold-account"),ready=Path.Combine(f.Root,"owned-account-ready");
        string barrier="if(operation==\"allocate-account\"&&System.IO.File.Exists("+System.Text.Json.JsonSerializer.Serialize(hold)+")){System.IO.File.WriteAllText("+System.Text.Json.JsonSerializer.Serialize(ready)+",\"owned\");var deadline=DateTime.UtcNow.AddSeconds(20);while(System.IO.File.Exists("+System.Text.Json.JsonSerializer.Serialize(hold)+")){if(DateTime.UtcNow>deadline)throw new TimeoutException(\"Owned fixture allocation hold\");System.Threading.Thread.Sleep(5);}}";
        File.WriteAllText(storageBody,File.ReadAllText(storageBody).Replace("return new System.Text.Json.Nodes.JsonObject{[\"path\"]=directory",barrier+"return new System.Text.Json.Nodes.JsonObject{[\"path\"]=directory",StringComparison.Ordinal));
        string trace=Path.Combine(f.Root,"owned-model-status.txt"),webState=Path.Combine(home,"WebState.csbody");
        File.AppendAllText(webState,"\n");File.WriteAllText(webState,File.ReadAllText(webState).Replace("var selected=model[\"selected\"];","if(model[\"status\"]?.ToString().StartsWith(\"Error:\",StringComparison.Ordinal)==true)System.IO.File.AppendAllText("+System.Text.Json.JsonSerializer.Serialize(trace)+",model[\"status\"]!.ToString()+Environment.NewLine);var selected=model[\"selected\"];",StringComparison.Ordinal));
        var built=new Builder(manifest,"linux").Build();string report=Path.Combine(f.Root,"click-preparation-report.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/editor_codex_click_preparation.py"),Fixture.Repo,report,descriptor},timeoutSeconds:600);
        True(run.ExitCode==0,run.Stdout+run.Stderr+(File.Exists(trace)?File.ReadAllText(trace):""));True(run.Stdout.Contains("PASS actual Home click preparation and device login"),run.Stdout+run.Stderr);
    }

    public void test_actual_editor_v318_inventory_and_browser_instances_restart()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples","editor-home","project.cpack"),"linux").Build();
        string report=Path.Combine(f.Root,"v318-inventory.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/editor_inventory_v318.py"),Fixture.Repo,report},timeoutSeconds:240);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS ordinary ProjectPack actual local inventory"));
    }
    public void test_actual_editor_v318_workspace_lifecycle_presentation_restart()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples","editor-home","project.cpack"),"linux").Build();
        string report=Path.Combine(f.Root,"v318-workspace.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/editor_workspace_v318.py"),Fixture.Repo,report},timeoutSeconds:360);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS ordinary ProjectPack common Workspace"));
    }
    public void test_actual_editor_v318_home_search_favorite_restart_remove()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples","editor-home","project.cpack"),"linux").Build();
        string report=Path.Combine(f.Root,"v318-home.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/editor_home_v318.py"),Fixture.Repo,report},timeoutSeconds:240);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS ordinary ProjectPack v318 Home"));
    }
    public void test_v318_original_and_refactor_shared_workspace_characterization()
    {
        string reference=Path.Combine(f.Root,"v318-reference");
        string zip=Path.Combine(Fixture.Repo,"reference","site-ui","Confectory-Editor-Prototype-v318.zip");
        Equal("0a614fe2bf1ad3d8e10dfa8905bb6b61ea9f21b87b2492b2b87ca8566e9e6908",Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(File.ReadAllBytes(zip))).ToLowerInvariant());
        System.IO.Compression.ZipFile.ExtractToDirectory(zip,reference);
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/v318_characterization.py"),Fixture.Repo,Path.Combine(reference,"confectory-site"),"/tmp/confectory-v318-characterization"},timeoutSeconds:180);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS frozen v318 vs refactor"));
    }
    public void test_actual_editor_review_compact_numeric_and_subset_caption()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples","editor-home","project.cpack"),"linux").Build();
        string report=Path.Combine(f.Root,"review-presentation.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,"review-presentation"},timeoutSeconds:180);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual compact numeric row and fresh subset caption"));
    }
    public void test_actual_editor_startup_serializes_owned_restore_before_helper_refresh()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"linux").Build();string report=Path.Combine(f.Root,"startup-restore.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,"startup-restore"},timeoutSeconds:180);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual startup metadata delay"),run.Stdout+run.Stderr);
    }
    public void test_actual_editor_v480_blueprint_owned_graph_node_edit_and_cold_input()=>RunOwnedBlueprint("blueprint");
    public void test_actual_editor_v480_blueprint_node_creation_removal_and_cold_source_groups()=>RunOwnedBlueprint("blueprint-create");
    public void test_actual_editor_v480_new_feature_contract_graph_group_and_cold_source()=>RunOwnedBlueprint("feature-create");
    public void test_actual_editor_v480_existing_feature_reference_call_and_cold_contract()=>RunOwnedBlueprint("call-wrapper");
    public void test_actual_editor_v480_module_interface_contract_default_and_cold_rebase()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"linux").Build();
        string report=Path.Combine(f.Root,"v480-module-interface.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,"module-interface"},timeoutSeconds:420);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual v480 module interface"),run.Stdout+run.Stderr);
    }
    public void test_actual_editor_v480_object_module_provider_cold_contract_and_own_view()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"linux").Build();string report=Path.Combine(f.Root,"v480-object-module.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,"object-provide"},timeoutSeconds:420);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual v480 object module provider"),run.Stdout+run.Stderr);
    }
    public void test_actual_editor_v480_window_document_docking_cold_inputs_and_compiler_confirm()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"linux").Build();string report=Path.Combine(f.Root,"v480-window-documents.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,"window-documents"},timeoutSeconds:420);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual v480 window documents"),run.Stdout+run.Stderr);
    }
    public void test_actual_editor_v480_note_document_tabs_canonical_ownership_and_cold_source_input()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"linux").Build();string report=Path.Combine(f.Root,"v480-note-documents.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,"note-documents"},timeoutSeconds:420);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual v480 note documents"),run.Stdout+run.Stderr);
    }
    public void test_actual_editor_v480_rich_notes_title_format_paste_and_cold_source_preservation()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"linux").Build();string report=Path.Combine(f.Root,"v480-rich-notes.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,"rich-notes"},timeoutSeconds:420);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual v480 rich notes"),run.Stdout+run.Stderr);
    }
    public void test_actual_editor_v480_placed_text_find_workspace_blueprint_and_cold_scope()=>RunOwnedBlueprint("placed-find");
    private void RunOwnedBlueprint(string mode)
    {
        string feature="function Example.ButtonGame::NodeValue (long n) -> long {}";
        var graph=System.Text.Json.Nodes.JsonNode.Parse("""
        {"schema":1,"profile":"sync-acyclic-v1","feature":"Example.ButtonGame::NodeValue","entry":"condition","nodes":[{"id":"condition","kind":"code","control":"branch","intent":"Choose positive input","signature":{"args":[{"type":"long","name":"value"}],"return":"bool"},"arguments":{"value":{"input":"n"}},"implementation":"condition.node.json"},{"id":"calculate","kind":"code","control":"next","intent":"Add four to the input","signature":{"args":[{"type":"long","name":"value"}],"return":"long"},"arguments":{"value":{"input":"n"}},"implementation":"calculate.node.json"}],"edges":[{"from":"condition","port":"true","to":"calculate"},{"from":"condition","port":"false","to":"exit:fallback"},{"from":"calculate","port":"next","to":"exit:done"}],"exits":{"done":{"node":"calculate"},"fallback":{"constant":9223372036854775807}}}
        """)!;
        graph["contractHash"]=FeatureBlueprint.ContractHash(new Parser(feature,"<owned v480 UI fixture>").ParseElement());
        var described=FeatureBlueprint.Execute(new System.Text.Json.Nodes.JsonObject{["operation"]="featureBlueprintNodes",["featureSource"]=feature,["graph"]=graph.DeepClone()});
        var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"linux").Build();
        built["nodeTaskFixture"]=new System.Text.Json.Nodes.JsonObject{["feature"]=feature,["graph"]=graph,["node"]=new System.Text.Json.Nodes.JsonObject{["schema"]=1,["node"]="calculate",["definitionHash"]=described["nodes"]![0]!["definitionHash"]!.DeepClone(),["source"]="return value + 4;"}};
        built["additionalNodeFixture"]=new System.Text.Json.Nodes.JsonObject{["schema"]=1,["node"]="condition",["definitionHash"]=described["nodes"]![1]!["definitionHash"]!.DeepClone(),["source"]="return value > 0;"};
        string report=Path.Combine(f.Root,"v480-blueprint.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,mode},timeoutSeconds:420);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains(mode=="blueprint"?"PASS actual v480 Blueprint":mode=="feature-create"?"PASS actual v480 feature creation":mode=="call-wrapper"?"PASS actual v480 reference call":mode=="placed-find"?"PASS actual v480 placed text find":"PASS actual v480 node creation/removal"),run.Stdout+run.Stderr);
    }
    public void test_actual_editor_v424_node_task_plan_cas_approval_and_cold_history()
    {
        string feature="function Example.ButtonGame::NodeValue (int n) -> int {}";
        var graph=System.Text.Json.Nodes.JsonNode.Parse("""
        {"schema":1,"profile":"sync-acyclic-v1","feature":"Example.ButtonGame::NodeValue","entry":"calculate","nodes":[{"id":"calculate","kind":"code","control":"next","intent":"Add four to the input","signature":{"args":[{"type":"int","name":"value"}],"return":"int"},"arguments":{"value":{"input":"n"}},"implementation":"calculate.node.json"}],"edges":[{"from":"calculate","port":"next","to":"exit:done"}],"exits":{"done":{"node":"calculate"}}}
        """)!;
        graph["contractHash"]=FeatureBlueprint.ContractHash(new Parser(feature,"<owned UI fixture>").ParseElement());
        var described=FeatureBlueprint.Execute(new System.Text.Json.Nodes.JsonObject{["operation"]="featureBlueprintDescribe",["featureSource"]=feature,["graph"]=graph.DeepClone()});
        var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"linux").Build();
        built["nodeTaskFixture"]=new System.Text.Json.Nodes.JsonObject{["feature"]=feature,["graph"]=graph,["node"]=new System.Text.Json.Nodes.JsonObject{["schema"]=1,["node"]="calculate",["definitionHash"]=described["nodes"]![0]!["definitionHash"]!.DeepClone(),["source"]="return value + 4;"}};
        string report=Path.Combine(f.Root,"node-tasks.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,"node-tasks"},timeoutSeconds:420);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual node Task plan"),run.Stdout+run.Stderr);
    }
    public void test_actual_editor_v424_build_only_jobs_artifacts_cancel_and_cold_history()
    {
        string probe=Path.Combine(f.Root,"lease-probe");Directory.CreateDirectory(probe);
        File.WriteAllText(Path.Combine(probe,"project.cpack"),"project Job.LeaseProbe version \"1\" {entry Job.LeaseProbe::Main;registry Confectory.FileStream "+System.Text.Json.JsonSerializer.Serialize(Path.Combine(Fixture.Repo,"packs/file-stream/pack.cpack"))+";dependency Confectory.FileStream version \"0.1.0\";registry Confectory.Build.DotNet "+System.Text.Json.JsonSerializer.Serialize(Path.Combine(Fixture.Repo,"targets/dotnet/pack.cpack"))+";dependency Confectory.Build.DotNet version \"0.1.0\";target portable Confectory.Build.DotNet::Portable;element Main function \"Main.celem\";element Body implementation \"Body.celem\";}");
        File.WriteAllText(Path.Combine(probe,"Main.celem"),"function Job.LeaseProbe::Main () -> int {provide Job.LeaseProbe::Main with Job.LeaseProbe::Body;provide Confectory.FileStream::LeasePath with Confectory.FileStream::LeasePathBody;}");
        File.WriteAllText(Path.Combine(probe,"Body.celem"),"implementation Job.LeaseProbe::Body for Job.LeaseProbe::Main () -> int {import Confectory.FileStream::LeasePath as Lease (string) -> string;body common \"Body.csbody\";}");
        File.WriteAllText(Path.Combine(probe,"Body.csbody"),"Console.WriteLine(System.Text.Json.JsonSerializer.Serialize(calls.Lease.Invoke(Environment.GetCommandLineArgs()[1])));return 0;");
        var lease=new Builder(Path.Combine(probe,"project.cpack"),"portable").Build();
        var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"linux").Build();built["leaseProbe"]=lease["run"]!.DeepClone();string report=Path.Combine(f.Root,"build-jobs.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,"build-jobs"},timeoutSeconds:600);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual build-only jobs"),run.Stdout+run.Stderr);
    }
    public void test_actual_editor_v424_shared_draft_history_cas_and_cold_restart()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"linux").Build();string report=Path.Combine(f.Root,"draft-history.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,"draft-history"},timeoutSeconds:600);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual draft history"),run.Stdout+run.Stderr);
    }
    public void test_actual_editor_v424_source_conflict_real_files_cas_and_cold_restart()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"linux").Build();string report=Path.Combine(f.Root,"source-conflict.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,"source-conflict"},timeoutSeconds:600);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual source conflict"),run.Stdout+run.Stderr);
    }
    public void test_actual_editor_v424_owned_object_variation_atomic_creation_and_cold_restart()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"linux").Build();string report=Path.Combine(f.Root,"v424-object-variation.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,"object-variation"},timeoutSeconds:600);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual owned object variation"),run.Stdout+run.Stderr);
    }
    public void test_actual_editor_v424_schema_local_actions_and_compound_array_order()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"linux").Build();string report=Path.Combine(f.Root,"v424-schema-actions.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,"schema-actions"},timeoutSeconds:600);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual schema local unset"),run.Stdout+run.Stderr);
    }
    public void test_actual_editor_v424_schema_exact_numeric_hash_and_cold_restart()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"linux").Build();string report=Path.Combine(f.Root,"v424-schema-exact.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,"schema-exact"},timeoutSeconds:600);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS exact schema scalar"),run.Stdout+run.Stderr);
    }
    public void test_actual_editor_v424_instant_table_typed_fill_cas_and_cold_restart()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"linux").Build();string report=Path.Combine(f.Root,"v424-instant-table.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,"instant-table"},timeoutSeconds:600);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual versioned table"),run.Stdout+run.Stderr);
    }
    public void test_actual_editor_v424_registered_reference_definition_read_only_and_cold_restart()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"linux").Build();string report=Path.Combine(f.Root,"v424-reference-definition.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,"reference-definition"},timeoutSeconds:420);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual registered reference definition"),run.Stdout+run.Stderr);
    }
    public void test_actual_editor_v424_declared_relations_map_and_cold_restart()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"linux").Build();string report=Path.Combine(f.Root,"v424-relations-map.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,"relations-map"},timeoutSeconds:420);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual declaration map"),run.Stdout+run.Stderr);
    }
    public void test_actual_editor_v424_typed_declaration_views_cas_confirm_and_restart()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"linux").Build();string report=Path.Combine(f.Root,"v424-declaration-forms.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,"declaration-forms"},timeoutSeconds:900);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS typed declaration forms"),run.Stdout+run.Stderr);
    }
    public void test_actual_editor_v424_local_augment_without_account_or_model()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"linux").Build();string report=Path.Combine(f.Root,"v424-local-augment.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,"local-augment"},timeoutSeconds:360);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS v424 local custom proposal"),run.Stdout+run.Stderr);
    }
    public void test_actual_editor_v424_six_declaration_kinds_and_registration_review()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"linux").Build();string report=Path.Combine(f.Root,"v424-declarations.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,"declarations"},timeoutSeconds:900);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS v424 six declaration kinds"),run.Stdout+run.Stderr);
    }
    public void test_actual_editor_new_concept_creation_save_confirm_reopen()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples","editor-home","project.cpack"),"linux").Build();
        string report=Path.Combine(f.Root,"creation.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,"creation"},timeoutSeconds:600);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Actual common WebUI creation Chromium PASS"));
        True(run.Stdout.Contains("PASS new concept actual process reopen"));
    }
    public void test_actual_editor_and_button_game_common_web_transport_chromium()
    {
        foreach(var (folder,kind) in new[]{("button-game","button"),("editor-home","editor")})
        {
            var built=new Builder(Path.Combine(Fixture.Repo,"examples",folder,"project.cpack"),"linux").Build();
            True(Strings(built,"includedPacks").Contains("Confectory.WebUI"));
            if(kind=="button")True(!Strings(built,"includedPacks").Any(x=>x.Contains("EditorHome",StringComparison.Ordinal)),"Generic consumer acquired editor dependency");
            string report=Path.Combine(f.Root,kind+".json");File.WriteAllText(report,built.ToJsonString());
            var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,kind},timeoutSeconds:900);
            True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Actual common WebUI "+kind+" Chromium PASS"));
        }
    }
    public void test_editor_web_resources_windows_git_checkout_and_actual_startup()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples","editor-home","project.cpack"),"linux").Build();
        string report=Path.Combine(f.Root,"resource-checkout.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests","probes","web_resource_checkout.py"),Fixture.Repo,report},timeoutSeconds:180);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual EditorHome retained CRLF after attribute pull and fresh LF"));
    }
    public void test_web_ui_scope_revision_cancellation_disposal_and_pack_locality()
    {
        foreach(var (ns,path) in new[]{("Confectory.WebUI","web-ui"),("Confectory.RuntimeBase","runtime-base")})
        {
            string local=Path.Combine(f.Root,path);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",path),local);
            f.ExtraRegistry[ns]=Path.Combine(local,"pack.cpack");f.Packs["App"].Dependencies[ns]="0.1.0";
        }
        f.Main("provide Confectory.WebUI::State with App::State; provide Confectory.WebUI::Invoke with App::Invoke; "+string.Join(" ",new[]{"CreateOwner","CreateInstance","Write","Subscribe","Poll","Unsubscribe","DisposeOwner"}.Select(n=>$"provide Confectory.RuntimeBase::{n} with Confectory.RuntimeBase::{n}Body;")));
        f.Add("App","implementation","State","""
        implementation App::State for Confectory.WebUI::State (string context) -> string { body common "state.csbody"; }
        """);
        f.Body("App","state.csbody","""
        return (string)AppDomain.CurrentDomain.GetData(context)!;
        """);
        f.Add("App","implementation","Invoke","""
        implementation App::Invoke for Confectory.WebUI::Invoke (string context,string endpoint,string input,string cancellation) -> string {
        import Confectory.WebUI::Cancelled as Cancelled (string) -> bool;
        body common "invoke.csbody"; }
        """);
        f.Body("App","invoke.csbody","""
        AppDomain.CurrentDomain.SetData(context+"started",true);
        if(endpoint=="wait") {while(!calls.Cancelled.Invoke(cancellation))System.Threading.Thread.Sleep(1);throw new OperationCanceledException();}
        return "{\"done\":true}";
        """);
        f.Add("App","implementation","MainBody","""
        implementation App::MainBody for App::Main () -> int {
        import Confectory.WebUI::Open as Open (string,string) -> string;
        import Confectory.WebUI::Request as Request (string,string) -> string;
        import Confectory.WebUI::NativeRequest as NativeRequest (string,string,string) -> string;
        import Confectory.WebUI::Resource as Resource (string,string) -> string[];
        import Confectory.WebUI::Close as Close (string) -> bool;
        body common "main.csbody"; }
        """);
        f.Body("App","main.csbody",""""
        void Check(bool b,string message){if(!b)throw new Exception(message);}
        string context="unit-context";
        void State(string project="p",string helper="h",int revision=0){AppDomain.CurrentDomain.SetData(context,System.Text.Json.JsonSerializer.Serialize(new{scope=new{projectId=project,helperId=helper},revision,state=new{value=revision}}));}
        State();string descriptor="""{"id":"unit","version":"1","entry":"index.html","endpoints":["wait","done"],"resources":{"index.html":{"mime":"text/html","base64":"PGgxPnVuaXQ8L2gxPg=="}}}""";
        string assetRoot=System.IO.Path.Combine(System.IO.Path.GetTempPath(),"confectory-manifest-"+Guid.NewGuid().ToString("N"));System.IO.Directory.CreateDirectory(assetRoot);
        try{
         byte[] image=new byte[2097152];System.IO.File.WriteAllBytes(System.IO.Path.Combine(assetRoot,"portrait.png"),image);
         var declared=System.Text.Json.Nodes.JsonNode.Parse(descriptor)!.AsObject();declared["resourceDirectory"]=assetRoot;
         declared["resources"]!["portrait.png"]=new System.Text.Json.Nodes.JsonObject{["file"]="portrait.png",["mime"]="image/png",["size"]=image.Length,["sha256"]=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(image))};
         string fileOwner=calls.Open.Invoke(context,declared.ToJsonString());Check(Convert.FromBase64String(calls.Resource.Invoke(fileOwner,"portrait.png")[1]).Length==image.Length,"normal common manifest exceeds old 1MiB limit");Check(calls.Close.Invoke(fileOwner),"manifest owner close");
         void Rejected(string name,string diagnostic=""){try{string unexpected=calls.Open.Invoke(context,declared.ToJsonString());calls.Close.Invoke(unexpected);throw new Exception(name+" accepted");}catch(ArgumentException error){Check(error.Message.Contains(diagnostic,StringComparison.Ordinal),name+" diagnostic: "+error.Message);Check(!error.Message.Contains(assetRoot,StringComparison.Ordinal),"diagnostic exposes local path");}}
         string textPath=System.IO.Path.Combine(assetRoot,"text.js"),lf="const value = \"한글\";\n";byte[] textBytes=System.Text.Encoding.UTF8.GetBytes(lf),crlf=System.Text.Encoding.UTF8.GetBytes(lf.Replace("\n","\r\n"));
         var textRow=new System.Text.Json.Nodes.JsonObject{["file"]="text.js",["mime"]="text/javascript",["size"]=textBytes.Length,["sha256"]=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(textBytes))};declared["resources"]!["text.js"]=textRow;
         System.IO.File.WriteAllBytes(textPath,crlf);Rejected("exact text does not normalize","Resource 'text.js': size mismatch");
         textRow["bytePolicy"]="utf8-lf-v1";textRow["canonicalSize"]=textRow["size"]!.DeepClone();textRow["canonicalSha256"]=textRow["sha256"]!.DeepClone();textRow.Remove("size");textRow.Remove("sha256");
         foreach(byte[] raw in new[]{textBytes,crlf}){System.IO.File.WriteAllBytes(textPath,raw);string canonicalOwner=calls.Open.Invoke(context,declared.ToJsonString());Check(System.Linq.Enumerable.SequenceEqual(Convert.FromBase64String(calls.Resource.Invoke(canonicalOwner,"text.js")[1]),textBytes),"LF/CRLF canonical snapshot");Check(System.Linq.Enumerable.SequenceEqual(System.IO.File.ReadAllBytes(textPath),raw),"normalization changed original");Check(calls.Close.Invoke(canonicalOwner),"canonical owner close");}
         System.IO.File.WriteAllBytes(textPath,System.Text.Encoding.UTF8.GetBytes(lf.Replace("value","VALUE")));Rejected("same-size text change","SHA-256 mismatch for canonical UTF-8 LF");
         System.IO.File.WriteAllBytes(textPath,new byte[]{255});Rejected("invalid UTF-8","invalid UTF-8 encoding");
         System.IO.File.WriteAllBytes(textPath,System.Linq.Enumerable.ToArray(System.Linq.Enumerable.Concat(new byte[]{239,187,191},textBytes)));Rejected("BOM","forbids BOM");
         foreach(string invalid in new[]{"bare\rCR","nul\0text"}){System.IO.File.WriteAllBytes(textPath,System.Text.Encoding.UTF8.GetBytes(invalid));Rejected("invalid canonical text","forbids bare CR and NUL");}
         System.IO.File.WriteAllBytes(textPath,textBytes);textRow["size"]=textBytes.Length;Rejected("ambiguous identity","mixed raw and canonical identity");textRow.Remove("size");textRow["mime"]="image/png";Rejected("binary normalization","requires a declared text file");textRow["mime"]="text/javascript";textRow["bytePolicy"]="unknown";Rejected("unknown normalization","unknown byte policy");declared["resources"]!.AsObject().Remove("text.js");
         declared["resources"]!["portrait.png"]!["sha256"]=new string('0',64);Rejected("changed resource identity","Resource 'portrait.png': SHA-256 mismatch");
         declared["resources"]!["portrait.png"]!["size"]=4194305;Rejected("oversized resource","per-resource byte budget exceeded; declared=4194305, actual=2097152, limit=4194304");
         declared["resources"]!["portrait.png"]!["size"]=2097153;Rejected("changed resource size","Resource 'portrait.png': size mismatch; expected=2097153, actual=2097152");
         declared["resources"]!.AsObject().Remove("portrait.png");byte[] maximum=new byte[4194304];for(int n=0;n<8;n++){string id="budget"+n+".png";System.IO.File.WriteAllBytes(System.IO.Path.Combine(assetRoot,id),maximum);declared["resources"]![id]=new System.Text.Json.Nodes.JsonObject{["file"]=id,["mime"]="image/png",["size"]=maximum.Length,["sha256"]=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(maximum))};}Rejected("aggregate exhaustion","Resource 'budget7.png': aggregate byte budget exceeded");for(int n=0;n<8;n++)declared["resources"]!.AsObject().Remove("budget"+n+".png");
         byte[] canonicalLines=new byte[2097152];Array.Fill(canonicalLines,(byte)10);byte[] rawLines=new byte[4194304];for(int n=0;n<rawLines.Length;n+=2){rawLines[n]=13;rawLines[n+1]=10;}
         for(int n=0;n<8;n++){string id="raw"+n+".js";System.IO.File.WriteAllBytes(System.IO.Path.Combine(assetRoot,id),rawLines);declared["resources"]![id]=new System.Text.Json.Nodes.JsonObject{["file"]=id,["mime"]="text/javascript",["bytePolicy"]="utf8-lf-v1",["canonicalSize"]=canonicalLines.Length,["canonicalSha256"]=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(canonicalLines))};}Rejected("raw aggregate exhaustion","Resource 'raw7.js': raw aggregate byte budget exceeded");for(int n=0;n<8;n++)declared["resources"]!.AsObject().Remove("raw"+n+".js");

         declared["resources"]!.AsObject().Remove("portrait.png");declared["resources"]!["../escape.png"]=new System.Text.Json.Nodes.JsonObject{["file"]="../escape.png",["mime"]="image/png",["size"]=0,["sha256"]=""};Rejected("manifest traversal");
         declared["resources"]!.AsObject().Remove("../escape.png");for(int n=0;n<256;n++)declared["resources"]!["r"+n+".png"]=new System.Text.Json.Nodes.JsonObject{["mime"]="image/png",["base64"]=""};Rejected("resource count exhaustion");
        }finally{System.IO.Directory.Delete(assetRoot,true);}
        string owner=calls.Open.Invoke(context,descriptor);
        System.Text.Json.Nodes.JsonNode Send(object req)=>System.Text.Json.Nodes.JsonNode.Parse(calls.Request.Invoke(owner,System.Text.Json.JsonSerializer.Serialize(req)))!;
        var mount=Send(new{op="mount"});string view=mount["view"]!.ToString();var scope=mount["scope"]!.DeepClone();
        Check(System.Text.Json.Nodes.JsonNode.Parse(calls.NativeRequest.Invoke(owner,"done","{}"))!["error"]!["code"]!.ToString()=="host_action_denied","undeclared native action denied");
        var nativeDescriptor=System.Text.Json.Nodes.JsonNode.Parse(descriptor)!.AsObject();nativeDescriptor["hostActions"]=new System.Text.Json.Nodes.JsonArray("done");string nativeOwner=calls.Open.Invoke(context,nativeDescriptor.ToJsonString());
        Check(System.Text.Json.Nodes.JsonNode.Parse(calls.NativeRequest.Invoke(nativeOwner,"done","{}"))!["ok"]!.GetValue<bool>(),"declared native action");Check(calls.Close.Invoke(nativeOwner),"native owner close");AppDomain.CurrentDomain.SetData(context+"started",null);
        var resource=calls.Resource.Invoke(owner,"/");Check(resource[0]=="text/html"&&resource[2].Length==64,"resource identity");
        try{calls.Resource.Invoke(owner,"../index.html");throw new Exception("traversal accepted");}catch(ArgumentException){}
        var waiting=Send(new{op="invoke",view,scope,endpoint="wait",requestId="wait",expectedRevision=0,input=new{}});Check(waiting["status"]!.ToString()=="pending","async acceptance");
        var deadline=DateTime.UtcNow.AddSeconds(5);while(AppDomain.CurrentDomain.GetData(context+"started") is null&&DateTime.UtcNow<deadline)System.Threading.Thread.Sleep(1);Check(AppDomain.CurrentDomain.GetData(context+"started") is true,"consumer started");
        Check(Send(new{op="update",view,scope})["busy"]!.GetValue<bool>(),"poll must not block cancellation behind a running call");
        Check(Send(new{op="cancel",view,scope,requestId="wait"})["status"]!.ToString()=="cancellation_requested","cancellation acknowledgement");
        System.Text.Json.Nodes.JsonNode? completed=null;
        while(DateTime.UtcNow<deadline){var update=Send(new{op="update",view,scope});completed=System.Linq.Enumerable.FirstOrDefault(update["results"]!.AsArray());if(completed is not null)break;System.Threading.Thread.Sleep(1);}
        Check(completed?["status"]?.ToString()=="cancelled"&&completed["result"] is null,"no late result after cancellation");
        State(helper:"other");Check(Send(new{op="update",view,scope})["error"]!["code"]!.ToString()=="scope_changed","host Helper scope changed");
        Check(Send(new{op="invoke",view,scope,endpoint="wait",requestId="wait",expectedRevision=0,input=new{}})["error"]!["code"]!.ToString()=="scope_changed","dedup cannot bypass current host scope");
        State(revision:1);Check(Send(new{op="update",view,scope})["changed"]!.GetValue<bool>(),"revision subscription");Check(!Send(new{op="update",view,scope})["changed"]!.GetValue<bool>(),"revision consumed once");
        Check(Send(new{op="dispose",view})["ok"]!.GetValue<bool>(),"dispose view");Check(Send(new{op="dispose",view})["ok"]!.GetValue<bool>(),"idempotent view disposal");Check(Send(new{op="update",view,scope})["error"]!["code"]!.ToString()=="view_closed","disposed view rejected");
        var remount=Send(new{op="mount"});Check(remount["revision"]!.GetValue<int>()==1,"view disposal retained consumer state");
        view=remount["view"]!.ToString();AppDomain.CurrentDomain.SetData(context+"started",null);
        Send(new{op="invoke",view,scope,endpoint="wait",requestId="close-wait",expectedRevision=1,input=new{}});
        deadline=DateTime.UtcNow.AddSeconds(5);while(AppDomain.CurrentDomain.GetData(context+"started") is null&&DateTime.UtcNow<deadline)System.Threading.Thread.Sleep(1);
        while(!calls.Close.Invoke(owner)&&DateTime.UtcNow<deadline)System.Threading.Thread.Sleep(1);Check(calls.Close.Invoke(owner),"drain ownership before close");
        Check(calls.Close.Invoke(owner),"idempotent owner close");Check(Send(new{op="mount"})["error"]!["code"]!.ToString()=="owner_closed","late reply owner unavailable");
        Console.WriteLine("WebUI boundary PASS");return 0;
        """");
        f.Sync();var first=new Builder(f.Project,"portable").Build();Output(first,"WebUI boundary PASS");
        File.AppendAllText(Path.Combine(f.Root,"web-ui","Open.csbody"),"\n// owned boundary locality probe\n");
        var changed=new Builder(f.Project,"portable").Build();PackRebuilt(changed,new[]{"Confectory.WebUI::OpenBody"});Equal(0,Strings(changed,"statistics","compiledContracts").Length);
    }
}
