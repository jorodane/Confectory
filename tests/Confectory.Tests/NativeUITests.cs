using System.Text.Json.Nodes;
using Confectory.Core;
namespace Confectory.Tests;
public sealed class NativeUITests : TestCase
{
    public void test_native_gtk_standalone_original_directory_diagnostic()
    {
        if(string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISPLAY"))){Skip("standalone GTK diagnostic: no actual DISPLAY");}
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests","gui","gtk_chooser_diagnostic.py"),"3"},timeoutSeconds:180);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Standalone GTK original input/cancel/retry/exact selection PASS"));
        Console.Write(run.Stdout);
    }
    string Consumer()
    {
        string path=Path.Combine(f.Root,"native public consumer");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","native-input-game"),path);
        foreach(string file in Directory.GetFiles(path,"*.cpack"))File.WriteAllText(file,File.ReadAllText(file).Replace("../../",Fixture.Repo+"/",StringComparison.Ordinal));return path;
    }
    public void test_native_public_projection_target_selection_and_provider_locality()
    {
        string consumer=Consumer(),project=Path.Combine(consumer,"verify.cpack"),owned=Path.Combine(f.Root,"owned native-ui");Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","native-ui-desktop"),owned);File.WriteAllText(project,File.ReadAllText(project).Replace(Path.Combine(Fixture.Repo,"packs","native-ui-desktop","pack.cpack"),Path.Combine(owned,"pack.cpack"),StringComparison.Ordinal));
        foreach(string target in new[]{"linux","windows"})
        {
            var built=new Builder(project,target).Build();True(built["tool"]!["ok"]!.GetValue<bool>());var run=Processes.Run(Strings(built,"run"),timeoutSeconds:60);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Native public model projection PASS"));
        }
        var android=new Builder(project,"android").Build();True(android["tool"]!["ok"]!.GetValue<bool>());var androidCatalog=JsonNode.Parse(File.ReadAllText(Text(android,"publicCatalog")))!;Equal("android",androidCatalog["implementations"]!.AsArray().Single(x=>x!["id"]!.GetValue<string>()=="Confectory.NativeUI::RequestBody")!["bodySelection"]!.GetValue<string>());Error("MISSING_TARGET_IMPLEMENTATION",()=>new Builder(project,"web").Build());
        var desktopContract=JsonData.Digest(new Builder(project,"linux").Registry.Get("Confectory.NativeUI::Request","function").Signature!);string original=File.ReadAllText(project);File.WriteAllText(project,original.Replace(Path.Combine(owned,"pack.cpack"),Path.Combine(Fixture.Repo,"packs","native-ui","pack.cpack"),StringComparison.Ordinal));Equal(desktopContract,JsonData.Digest(new Builder(project,"linux").Registry.Get("Confectory.NativeUI::Request","function").Signature!));foreach(string target in new[]{"linux","android","web"})Error("MISSING_IMPLEMENTATION",()=>new Builder(project,target).Build());File.WriteAllText(project,original);
        new Builder(project,"linux").Build();File.AppendAllText(Path.Combine(owned,"Capabilities.linux.csbody"),"\n// selected provider locality\n");var changed=new Builder(project,"linux").Build();PackRebuilt(changed, new[]{"Confectory.NativeUI::CapabilitiesBody"});Equal(0,Strings(changed,"statistics","compiledContracts").Length);
    }
    public void test_native_gtk_actual_editing_picker_and_lifetime()
    {
        if(string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISPLAY"))){Skip("native service GUI: no actual DISPLAY");}
        string consumer=Consumer(),project=Path.Combine(consumer,"project.cpack");var built=new Builder(project,"linux").Build();string report=Path.Combine(f.Root,"native report.json");File.WriteAllText(report,built.ToJsonString());var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests","gui","native_input_x11.py"),report},timeoutSeconds:180);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("owner dialog cleanup PASS"));
        var windows=new Builder(project,"windows").Build();True(windows["tool"]!["ok"]!.GetValue<bool>());Console.WriteLine("Windows native provider managed compilation only; no Windows IME/dialog runtime claim");
    }
}
