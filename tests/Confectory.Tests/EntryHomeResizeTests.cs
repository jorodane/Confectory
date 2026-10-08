using Confectory.Core;
namespace Confectory.Tests;
public sealed class EntryHomeResizeTests : TestCase
{
    public void test_entry_home_tiny_and_zero_client_suspend_restore_preserve_input_lifetimes()
    {
        if(string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISPLAY"))){Skip("native resize: no DISPLAY");}
        string consumer=Path.Combine(f.Root,"small client home"),window=Path.Combine(f.Root,"owned window");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","editor-home"),consumer);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","window"),window);
        string project=Path.Combine(consumer,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../",Fixture.Repo+"/").Replace(Path.Combine(Fixture.Repo,"packs","window","pack.cpack"),Path.Combine(window,"pack.cpack")));
        string flag=Path.Combine(f.Root,"zero-client.flag"),body=Path.Combine(window,"SurfaceDimensions.csbody");File.WriteAllText(body,"if(System.IO.File.Exists("+System.Text.Json.JsonSerializer.Serialize(flag)+"))return new[]{0,0};\n"+File.ReadAllText(body));
        var built=new Builder(project,"linux").Build();string report=Path.Combine(f.Root,"small-client.json");File.WriteAllText(report,built.ToJsonString());string? old=Environment.GetEnvironmentVariable("CONFECTORY_TEST_ZERO_FLAG");try{Environment.SetEnvironmentVariable("CONFECTORY_TEST_ZERO_FLAG",flag);var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests","gui","entry_home_resize_x11.py"),report},timeoutSeconds:240);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Entry/home transient layout:"));}finally{Environment.SetEnvironmentVariable("CONFECTORY_TEST_ZERO_FLAG",old);}
        File.AppendAllText(Path.Combine(consumer,"Main.csbody"),"\n// minimized layout consumer locality probe\n");var changed=new Builder(project,"linux").Build();PackRebuilt(changed, new[]{"Confectory.EditorHome::MainBody"});Equal(0,Strings(changed,"statistics","compiledContracts").Length);
        var windows=new Builder(project,"windows").Build();True(windows["tool"]!["ok"]!.GetValue<bool>());
    }
}
