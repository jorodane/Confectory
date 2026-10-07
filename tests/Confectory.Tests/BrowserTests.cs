using Confectory.Core;
namespace Confectory.Tests;
public sealed class BrowserTests : TestCase
{
    public void test_local_browser_project_public_model_actual_chromium_and_provider_locality()
    {
        string consumer=Path.Combine(f.Root,"browser consumer"),provider=Path.Combine(f.Root,"owned browser-host");
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","editor-home-web"),consumer);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","browser-host"),provider);
        string project=Path.Combine(consumer,"project.cproj");File.WriteAllText(project,File.ReadAllText(project).Replace("../../",Fixture.Repo+"/",StringComparison.Ordinal).Replace(Path.Combine(Fixture.Repo,"packs","browser-host","pack.cpack"),Path.Combine(provider,"pack.cpack"),StringComparison.Ordinal));
        var built=new Builder(project,"web").Build();
        True(Strings(built,"includedPacks").Contains("Confectory.EditorHome.Model"));
        True(!Strings(built,"includedPacks").Any(x=>new[]{"Confectory.NativeUI","Confectory.Window","Confectory.Agent","Confectory.Helper"}.Contains(x)),"browser composition acquired native or AI providers");
        string output=built["output"]!.GetValue<string>();foreach(string asset in new[]{"index.html","app.js","style.css"})True(File.Exists(Path.Combine(output,"browser-assets",asset)),"browser bundle missing "+asset);
        string report=Path.Combine(f.Root,"browser report.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests","web","browser_entry.py"),Fixture.Repo,report},timeoutSeconds:150);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Actual Chromium Browser Entry/Home PASS"));
        File.AppendAllText(Path.Combine(provider,"Serve.csbody"),"\n// owned browser provider locality probe\n");var changed=new Builder(project,"web").Build();Sequence(new[]{"Confectory.BrowserHost::ServeBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
    }
}
