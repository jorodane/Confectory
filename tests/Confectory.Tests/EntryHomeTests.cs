using Confectory.Core;
using System.Text.Json.Nodes;
namespace Confectory.Tests;
public sealed class EntryHomeTests : TestCase
{
    string Consumer(string name)
    {
        string path=Path.Combine(f.Root,"owned "+name);Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples",name),path);
        foreach(string file in Directory.GetFiles(path,"*.cpack"))File.WriteAllText(file,File.ReadAllText(file).Replace("../../",Fixture.Repo+"/",StringComparison.Ordinal));
        if(name=="editor-home"){
            string owned=Path.Combine(path,"owned base-ui");Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","base-ui"),owned);
            foreach(string file in Directory.GetFiles(path,"*.cpack"))File.WriteAllText(file,File.ReadAllText(file).Replace(Path.Combine(Fixture.Repo,"packs","base-ui","pack.cpack"),Path.Combine(owned,"pack.cpack"),StringComparison.Ordinal));
        }
        return path;
    }
    void Offline(JsonObject built)
    {
        foreach(string key in new[]{"registeredPacks","includedPacks"})True(!Strings(built,key).Any(x=>new[]{"Confectory.Editor","Confectory.SourceEditor","Confectory.Agent","Confectory.Helper","Confectory.MultiPlay"}.Contains(x)),"fresh production composition acquired temporary editor or optional AI");
    }
    public void test_grid_editor_free_responsiveness_and_provider_locality()
    {
        string consumer=Consumer("grid-game"),project=Path.Combine(consumer,"project.cpack"),owned=Path.Combine(f.Root,"owned grid pack");Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","base-ui"),owned);File.WriteAllText(project,File.ReadAllText(project).Replace(Path.Combine(Fixture.Repo,"packs","base-ui","pack.cpack"),Path.Combine(owned,"pack.cpack"),StringComparison.Ordinal));
        var built=new Builder(project,"linux").Build();var run=Processes.Run(Strings(built,"run"));True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Editor-free Grid consumer"));Offline(built);
        File.AppendAllText(Path.Combine(owned,"Grid.csbody"),"\n// Grid owning provider locality probe\n");var changed=new Builder(project,"linux").Build();Sequence(new[]{"Confectory.BaseUI::GridBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
    }
    public void test_fresh_entry_home_project_contracts_and_consumer_locality()
    {
        string consumer=Consumer("editor-home"),project=Path.Combine(consumer,"verify.cpack"),manager=Path.Combine(f.Root,"owned project manager");Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","project-manager"),manager);File.WriteAllText(project,File.ReadAllText(project).Replace(Path.Combine(Fixture.Repo,"packs","project-manager","pack.cpack"),Path.Combine(manager,"pack.cpack"),StringComparison.Ordinal));var built=new Builder(project,"linux").Build();Offline(built);
        string? repo=Environment.GetEnvironmentVariable("CONFECTORY_EDITOR_REPO"),host=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST");try{Environment.SetEnvironmentVariable("CONFECTORY_EDITOR_REPO",Fixture.Repo);Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets","element-authoring","bin","Release","net8.0","Confectory.ElementAuthoring.dll"));var run=Processes.Run(Strings(built,"run"),timeoutSeconds:180);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Entry/home contracts:"));}finally{Environment.SetEnvironmentVariable("CONFECTORY_EDITOR_REPO",repo);Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",host);}
        File.AppendAllText(Path.Combine(manager,"PlanCreation.csbody"),"\n// naming policy provider locality probe\n");var naming=new Builder(project,"linux").Build();Sequence(new[]{"Confectory.ProjectManager::PlanCreationBody"},Strings(naming,"statistics","compiledImplementations"));Equal(0,Strings(naming,"statistics","compiledContracts").Length);
        File.AppendAllText(Path.Combine(consumer,"Command.csbody"),"\n// entry/home command locality probe\n");var changed=new Builder(project,"linux").Build();Sequence(new[]{"Confectory.EditorHome::CommandBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
    }
    public void test_entry_home_actual_linux_startup_navigation_create_folder_cards_resize_and_lifetime()
    {
        if(string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISPLAY"))){Console.WriteLine("SKIP native entry/home: no actual DISPLAY");return;}
        string consumer=Consumer("editor-home"),project=Path.Combine(consumer,"project.cpack");var built=new Builder(project,"linux").Build();Offline(built);string report=Path.Combine(f.Root,"home native report.json");File.WriteAllText(report,built.ToJsonString());var run=Processes.Run(new[]{"python",Path.Combine(Fixture.Repo,"tests","gui","entry_home_x11.py"),report},timeoutSeconds:240);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Entry/home actual X11"));
        File.AppendAllText(Path.Combine(consumer,"Main.csbody"),"\n// fresh presentation locality probe\n");var changed=new Builder(project,"linux").Build();Sequence(new[]{"Confectory.EditorHome::MainBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
    }
    public void test_entry_home_windows_android_managed_profiles_compile_only()
    {
        string consumer=Consumer("editor-home");foreach(string target in new[]{"windows"}){var built=new Builder(Path.Combine(consumer,"project.cpack"),target).Build();True(built["tool"]!["ok"]!.GetValue<bool>());Offline(built);}
        Error("MISSING_TARGET_IMPLEMENTATION",()=>new Builder(Path.Combine(consumer,"project.cpack"),"android").Build());
    }
}
