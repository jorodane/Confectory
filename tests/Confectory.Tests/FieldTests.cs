using Confectory.Core;
namespace Confectory.Tests;
public sealed class FieldTests : TestCase
{
    public void test_shared_field_editor_free_geometry_input_lifetime_and_provider_locality()
    {
        string consumer=Path.Combine(f.Root,"owned field game"),owned=Path.Combine(f.Root,"owned fields"),window=Path.Combine(f.Root,"owned window");
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","field-game"),consumer);
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","base-ui"),owned);
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","window"),window);
        string project=Path.Combine(consumer,"project.cpack");
        File.WriteAllText(project,File.ReadAllText(project).Replace("../../",Fixture.Repo+"/",StringComparison.Ordinal).Replace(Path.Combine(Fixture.Repo,"packs","base-ui","pack.cpack"),Path.Combine(owned,"pack.cpack"),StringComparison.Ordinal).Replace(Path.Combine(Fixture.Repo,"packs","window","pack.cpack"),Path.Combine(window,"pack.cpack"),StringComparison.Ordinal));
        string? gui=Environment.GetEnvironmentVariable("CONFECTORY_FIELD_GAME_GUI");
        try
        {
            Environment.SetEnvironmentVariable("CONFECTORY_FIELD_GAME_GUI",null);
            var built=new Builder(project,"linux").Build();var run=Processes.Run(Strings(built,"run"),timeoutSeconds:120);
            True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Editor-free shared Field/Input/Stack",StringComparison.Ordinal));
            string[] forbidden={"Confectory.Editor","Confectory.SourceEditor","Confectory.EditWorkspace","Confectory.ProjectManager","Confectory.Agent","Confectory.Helper"};
            foreach(string key in new[]{"registeredPacks","includedPacks"})True(!Strings(built,key).Any(x=>forbidden.Contains(x)));
            foreach(string key in new[]{"compiledContracts","compiledImplementations"})True(!Strings(built,"statistics",key).Any(x=>forbidden.Any(prefix=>x.StartsWith(prefix+"::",StringComparison.Ordinal))));
            // Provider-body edits must rebuild precisely their own implementation, never contracts or consumers.
            foreach(var probe in new[]{(owned,"Confectory.BaseUI","Field"),(owned,"Confectory.BaseUI","FieldInput"),(owned,"Confectory.BaseUI","TextInput"),(owned,"Confectory.BaseUI","Stack"),(window,"Confectory.Window","MeasureText"),(window,"Confectory.Window","DrawText"),(window,"Confectory.Window","Pump"), (window,"Confectory.Window","CreateTextLayout"), (owned,"Confectory.BaseUI","TextLines")})
            {
                File.AppendAllText(Path.Combine(probe.Item1,probe.Item3+".csbody"),"\n// CP14 selected provider locality probe\n");
                var changed=new Builder(project,"linux").Build();PackRebuilt(changed, new[]{probe.Item2+"::"+probe.Item3+"Body"});Equal(0,Strings(changed,"statistics","compiledContracts").Length);
            }
            if(!string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISPLAY")))
            {
                string report=Path.Combine(f.Root,"field native report.json");File.WriteAllText(report,built.ToJsonString());
                foreach(string scale in new[]{"1","1.5"})
                {
                    string? prior=Environment.GetEnvironmentVariable("CONFECTORY_TEXT_SCALE");
                    try{Environment.SetEnvironmentVariable("CONFECTORY_TEXT_SCALE",scale);var native=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests","gui","field_game_x11.py"),report},timeoutSeconds:120);True(native.ExitCode==0,native.Stdout+native.Stderr);True(native.Stdout.Contains("Editor-free native Field measured font/caret pixels",StringComparison.Ordinal));}
                    finally{Environment.SetEnvironmentVariable("CONFECTORY_TEXT_SCALE",prior);}
                }
            }
            else Skip("native Field pixels/capture: no actual DISPLAY");
            foreach(string target in new[]{"windows","android"}){var compiled=new Builder(project,target).Build();True(compiled["tool"]!["ok"]!.GetValue<bool>());}
        }
        finally{Environment.SetEnvironmentVariable("CONFECTORY_FIELD_GAME_GUI",gui);}
    }
}
