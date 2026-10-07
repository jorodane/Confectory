using Confectory.Core;
namespace Confectory.Tests;
public sealed class ProjectNavigationTests : TestCase
{
    public void test_shared_ui_order_independent_consumer_and_provider_locality()
    {
        string consumer=Path.Combine(f.Root,"order game"), pack=Path.Combine(f.Root,"order pack");
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","ui-order-game"),consumer);
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","ui-order"),pack);
        string project=Path.Combine(consumer,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/ui-order/pack.cpack",Path.Combine(pack,"pack.cpack")).Replace("../../",Fixture.Repo+"/"));
        var built=new Builder(project,"portable").Build();Output(built,"Shared UI Order game consumer PASS");
        True(!Strings(built,"includedPacks").Any(x=>x.Contains("Editor")||x.Contains("ProjectShell")),"UI order remains independent of editor presentation");
        File.AppendAllText(Path.Combine(pack,"Compose.csbody"),"\n// ordered-frame provider locality probe\n");var changed=new Builder(project,"portable").Build();Sequence(new[]{"Confectory.UIOrder::ComposeBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);Output(changed,"Shared UI Order game consumer PASS");
    }
    public void test_editor_free_rounded_widgets_edge_placement_occlusion_and_provider_locality()
    {
        string consumer=Path.Combine(f.Root,"rounded game");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","rounded-game"),consumer);
        string pack=Path.Combine(consumer,"base-ui");Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","base-ui"),pack);
        string project=Path.Combine(consumer,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../",Fixture.Repo+"/").Replace(Path.Combine(Fixture.Repo,"packs","base-ui","pack.cpack"),Path.Combine(pack,"pack.cpack")));
        var built=new Builder(project,"linux").Build();var run=Processes.Run(Strings(built,"run"),timeoutSeconds:120);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Editor-free rounded game:"));
        foreach(string body in new[]{"RoundedBox","RoundedHit","RoundedButton","RoundedInput","AnchorPanel","ClipRegions"}){File.AppendAllText(Path.Combine(pack,body+".csbody"),"\n// owning rounded provider locality probe\n");var next=new Builder(project,"linux").Build();Sequence(new[]{"Confectory.BaseUI::"+body+"Body"},Strings(next,"statistics","compiledImplementations"));Equal(0,Strings(next,"statistics","compiledContracts").Length);}
        foreach(string target in new[]{"windows","android"}){var other=new Builder(project,target).Build();True(other["tool"]!["ok"]!.GetValue<bool>());}
    }
    public void test_project_navigation_actual_linux_context_keyboard_pointer_resize_and_cleanup()
    {
        if(string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISPLAY"))){Console.WriteLine("SKIP native navigation: no DISPLAY");return;}
        string consumer=Path.Combine(f.Root,"navigation home");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","editor-home"),consumer);
        string project=Path.Combine(consumer,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../",Fixture.Repo+"/"));var built=new Builder(project,"linux").Build();string report=Path.Combine(f.Root,"navigation.json");File.WriteAllText(report,built.ToJsonString());var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests","gui","project_navigation_x11.py"),report},timeoutSeconds:240);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Project navigation actual X11:"));
        File.AppendAllText(Path.Combine(consumer,"Main.csbody"),"\n// project navigation presentation locality probe\n");var changed=new Builder(project,"linux").Build();Sequence(new[]{"Confectory.EditorHome::MainBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
    }
}
