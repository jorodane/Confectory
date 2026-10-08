using Confectory.Core;
namespace Confectory.Tests;
public sealed class ButtonTests : TestCase
{
    public void test_shared_button_game_without_editor_state_input_navigation_native_targets_and_locality()
    {
        string consumer=Path.Combine(f.Root,"owned button game"),owned=Path.Combine(f.Root,"owned shared buttons");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","button-game"),consumer);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","base-ui"),owned);
        string project=Path.Combine(consumer,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../",Fixture.Repo+"/",StringComparison.Ordinal).Replace(Path.Combine(Fixture.Repo,"packs","base-ui","pack.cpack"),Path.Combine(owned,"pack.cpack"),StringComparison.Ordinal));
        string? gui=Environment.GetEnvironmentVariable("CONFECTORY_BUTTON_GAME_GUI");
        try
        {
            Environment.SetEnvironmentVariable("CONFECTORY_BUTTON_GAME_GUI",null);var built=new Builder(project,"linux").Build();var run=Processes.Run(Strings(built,"run"),timeoutSeconds:120);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Editor-free game shared Button presentation/hit/state/activation",StringComparison.Ordinal));True(!Strings(built,"includedPacks").Any(x=>x.Contains("Editor",StringComparison.Ordinal)||x.Contains("EditWorkspace",StringComparison.Ordinal)||x.Contains("SourceEditor",StringComparison.Ordinal)||x.Contains("ProjectManager",StringComparison.Ordinal)));
            foreach(string key in new[]{"compiledContracts","compiledImplementations"})True(!Strings(built,"statistics",key).Any(x=>new[]{"Confectory.Editor::","Confectory.EditWorkspace::","Confectory.SourceEditor::","Confectory.ProjectManager::","Confectory.Helper::","Confectory.Agent::"}.Any(prefix=>x.StartsWith(prefix,StringComparison.Ordinal))));
            foreach(string name in new[]{"Button","ButtonInput"}){File.AppendAllText(Path.Combine(owned,name+".csbody"),"\n// shared button provider locality probe\n");var changed=new Builder(project,"linux").Build();PackRebuilt(changed, new[]{"Confectory.BaseUI::"+name+"Body"});Equal(0,Strings(changed,"statistics","compiledContracts").Length);}
            if(!string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISPLAY"))){string report=Path.Combine(f.Root,"button native report.json");File.WriteAllText(report,built.ToJsonString());var native=Processes.Run(new[]{"python",Path.Combine(Fixture.Repo,"tests","gui","button_game_x11.py"),report},timeoutSeconds:120);True(native.ExitCode==0,native.Stdout+native.Stderr);True(native.Stdout.Contains("Editor-free native game shares BaseUI Button",StringComparison.Ordinal));}
            else Skip("native button game: no actual DISPLAY");
            foreach(string target in new[]{"windows","android"}){var compiled=new Builder(project,target).Build();True(compiled["tool"]!["ok"]!.GetValue<bool>());}
        }
        finally{Environment.SetEnvironmentVariable("CONFECTORY_BUTTON_GAME_GUI",gui);}
    }
}
