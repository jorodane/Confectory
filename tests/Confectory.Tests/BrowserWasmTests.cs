using Confectory.Core;
namespace Confectory.Tests;
public sealed class BrowserWasmTests : TestCase
{
    public void test_independent_browser_wasm_actual_chromium_and_owner_provider_locality()
    {
        string sdk=Path.GetDirectoryName(new FileInfo(Processes.DotNet()).ResolveLinkTarget(true)?.FullName??Processes.DotNet())!;
        if(!Directory.Exists(Path.Combine(sdk,"packs","Microsoft.NET.Runtime.WebAssembly.Sdk"))){Skip("independent WASM: install .NET10 wasm-tools; source/managed compilation is not runtime coverage");}
        string consumer=Path.Combine(f.Root,"browser wasm consumer"),provider=Path.Combine(f.Root,"owned browser runtime");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","editor-home-browser"),consumer);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","browser-runtime"),provider);
        string project=Path.Combine(consumer,"project.cproj");File.WriteAllText(project,File.ReadAllText(project).Replace("../../",Fixture.Repo+"/",StringComparison.Ordinal).Replace(Path.Combine(Fixture.Repo,"packs","browser-runtime","pack.cpack"),Path.Combine(provider,"pack.cpack"),StringComparison.Ordinal));
        var baseline=new Builder(project,"browser");var built=baseline.Build();
        True(Strings(built,"includedPacks").Contains("Confectory.EditorHome.Model"));True(!Strings(built,"includedPacks").Any(x=>new[]{"Confectory.Window","Confectory.NativeUI","Confectory.Agent","Confectory.Helper"}.Contains(x)));
        string site=Path.Combine(built["output"]!.GetValue<string>(),"site");True(File.Exists(Path.Combine(site,"_framework","dotnet.js")));True(Directory.GetFiles(site,"*.wasm",SearchOption.AllDirectories).Length>0);
        string report=Path.Combine(f.Root,"wasm browser report.json");File.WriteAllText(report,built.ToJsonString());var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests","web","browser_wasm.py"),Fixture.Repo,report},timeoutSeconds:120);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Independent Chromium WASM PASS"));
        File.AppendAllText(Path.Combine(provider,"Initialize.browser.csbody"),"\n// Browser owned initialization locality probe\n");var updated=new Builder(project,"browser");Equal(baseline.Tool.Identity,updated.Tool.Identity);var changed=updated.Build();PackRebuilt(changed, new[]{"Confectory.BrowserRuntime::InitializeBody"});Equal(0,Strings(changed,"statistics","compiledContracts").Length);
        // Browser target additions preserve target-specific Android and common desktop fallback.
        var android=new Planner(new Builder(Path.Combine(Fixture.Repo,"examples","editor-home","project.cpack"),"android").Registry,"android").Plan();True(android.Implementations["Confectory.EditorHome.Model::CreateSessionBody"].Bodies.ContainsKey("android"));
    }
}
