using System.Text.Json.Nodes;
using Confectory.Core;
namespace Confectory.Tests;
public sealed class EditorTests : TestCase
{
    string Consumer()
    {
        string path=Path.Combine(f.Root,"owned editor consumer");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","editor"),path);
        foreach(string file in Directory.GetFiles(path,"*.cpack"))File.WriteAllText(file,File.ReadAllText(file).Replace("../../",Fixture.Repo+"/",StringComparison.Ordinal));
        return path;
    }
    void ExcludeOptional(JsonObject built)
    {
        foreach(string key in new[]{"compiledContracts","compiledImplementations"})True(!Strings(built,"statistics",key).Any(x=>new[]{"Confectory.Physics2D::","Confectory.Stage::","Confectory.RigMotion::","Confectory.RenderAuthoring::","Confectory.Helper::","Confectory.Agent::","Confectory.MultiPlay::"}.Any(prefix=>x.StartsWith(prefix,StringComparison.Ordinal))),"editor selected closure acquired optional domain/AI dependency");
    }
    void RunOwned(JsonObject built,string storage,string expected)
    {
        var env=new Dictionary<string,string?>();foreach(string name in new[]{"CONFECTORY_EDITOR_REPO","CONFECTORY_EDITOR_TEST_STORAGE","CONFECTORY_ELEMENT_AUTHORING_HOST","CONFECTORY_PROJECT_EXECUTION_HOST"})env[name]=Environment.GetEnvironmentVariable(name);
        try
        {
            Environment.SetEnvironmentVariable("CONFECTORY_EDITOR_REPO",Fixture.Repo);Environment.SetEnvironmentVariable("CONFECTORY_EDITOR_TEST_STORAGE",storage);Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets","element-authoring","bin","Release","net8.0","Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST",Path.Combine(Fixture.Repo,"targets","project-execution-host","bin","Release","net8.0","Confectory.ProjectExecutionHost.dll"));
            var run=Processes.Run(Strings(built,"run"),timeoutSeconds:300);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains(expected,StringComparison.Ordinal),run.Stdout);
        }
        finally{foreach(var item in env)Environment.SetEnvironmentVariable(item.Key,item.Value);}
    }
    public void test_editor_public_controls_folder_snapshot_and_navigation_consumer_locality()
    {
        string consumer=Consumer(),project=Path.Combine(consumer,"verify-contracts.cpack");
        foreach(string role in new[]{"base-ui","ui-navigation","source-editor","file-stream"})
        {
            string owned=Path.Combine(f.Root,"owned "+role);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",role),owned);File.WriteAllText(project,File.ReadAllText(project).Replace(Path.Combine(Fixture.Repo,"packs",role,"pack.cpack"),Path.Combine(owned,"pack.cpack"),StringComparison.Ordinal));
        }
        var built=new Builder(project,"linux").Build();RunOwned(built,Path.Combine(f.Root,"folder pages"),"Editor public controls ownership");ExcludeOptional(built);
        foreach(var policy in new[]{("base-ui","ControlState","Confectory.BaseUI::ControlStateBody"),("ui-navigation","Group","Confectory.UINavigation::GroupBody"),("source-editor","Snapshot","Confectory.SourceEditor::SnapshotBody"),("source-editor","Refresh","Confectory.SourceEditor::RefreshBody"),("file-stream","BrowseDirectory","Confectory.FileStream::BrowseDirectoryBody")})
        {
            File.AppendAllText(Path.Combine(f.Root,"owned "+policy.Item1,policy.Item2+".csbody"),"\n// owning public provider implementation locality probe\n");var changed=new Builder(project,"linux").Build();Sequence(new[]{policy.Item3},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
        }
    }
    public void test_editor_create_draft_restart_confirm_execute_errors_recovery_and_independent_contexts()
    {
        string consumer=Consumer();foreach(var example in new[]{("verify","Editor actual create/element/text/draft Save/Review/Confirm/run/stop/shared View workflow PASS"),("verify-errors","Editor invalid/compiler/stale/external conflict")})
        {
            var built=new Builder(Path.Combine(consumer,example.Item1+".cpack"),"linux").Build();RunOwned(built,Path.Combine(f.Root,example.Item1+" storage"),example.Item2);ExcludeOptional(built);
        }
        string project=Path.Combine(consumer,"verify.cpack");File.AppendAllText(Path.Combine(consumer,"Command.csbody"),"\n// owning editor workflow locality probe\n");var changed=new Builder(project,"linux").Build();Sequence(new[]{"Confectory.Editor::CommandBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
    }
    public void test_editor_native_designed_create_open_edit_save_review_confirm_run_stop_and_lifetime()
    {
        if(string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISPLAY"))){Console.WriteLine("SKIP native editor: no actual DISPLAY");return;}
        string consumer=Consumer();var built=new Builder(Path.Combine(consumer,"project.cpack"),"linux").Build();ExcludeOptional(built);string report=Path.Combine(f.Root,"editor native report.json");File.WriteAllText(report,built.ToJsonString());var run=Processes.Run(new[]{"python",Path.Combine(Fixture.Repo,"tests","gui","editor_x11_workflow.py"),report},timeoutSeconds:360);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Editor native create/folder-open",StringComparison.Ordinal),run.Stdout);
        File.AppendAllText(Path.Combine(consumer,"Main.csbody"),"\n// owning editor presentation locality probe\n");var changed=new Builder(Path.Combine(consumer,"project.cpack"),"linux").Build();Sequence(new[]{"Confectory.Editor::MainBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
    }
    public void test_editor_windows_and_android_managed_target_profiles_are_compile_only()
    {
        string consumer=Consumer();foreach(string target in new[]{"windows","android"})foreach(string entry in new[]{"project","verify-contracts"}){var built=new Builder(Path.Combine(consumer,entry+".cpack"),target).Build();True(built["tool"]!["ok"]!.GetValue<bool>());ExcludeOptional(built);}
    }
}
