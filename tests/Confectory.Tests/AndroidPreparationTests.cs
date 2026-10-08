using System.Text.Json.Nodes;
using Confectory.Core;

namespace Confectory.Tests;

public sealed class AndroidPreparationTests : TestCase
{
    public void test_android_managed_bindings_lifecycle_and_export()
    {
        string sample=Path.Combine(f.Root,"android-sample");
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","engine-android"),sample);
        foreach(string pack in new[]{"runtime-base","realtime-update","render-input","base-ui","window","android-export-settings"})
            Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",pack),Path.Combine(f.Root,"packs",pack));
        string project=Path.Combine(sample,"project.cpack");
        File.WriteAllText(project,File.ReadAllText(project)
            .Replace("../../packs/","../packs/",StringComparison.Ordinal)
            .Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));
        File.WriteAllText(Path.Combine(sample,"main.csbody"),"""
            void Check(bool condition,string message){if(!condition)throw new Exception(message);}
            Check(string.Join(",",calls.Capabilities.Invoke())=="0,1,1","Android capabilities claimed desktop windows");
            var state=new long[5];
            Check(!calls.SurfaceLifecycle.Invoke(state,"resume",0,0),"rendered before surface");
            Check(calls.SurfaceLifecycle.Invoke(state,"created",480,800),"not resumed");
            Check(!calls.SurfaceLifecycle.Invoke(state,"pause",0,0),"rendered paused");
            Check(calls.SurfaceLifecycle.Invoke(state,"resume",0,0),"resume failed");
            Check(!calls.SurfaceLifecycle.Invoke(state,"surfaceDestroyed",0,0),"rendered after surface loss");
            Check(calls.SurfaceLifecycle.Invoke(state,"created",800,480),"surface recreation");
            Check(!calls.SurfaceLifecycle.Invoke(state,"destroy",0,0),"destroy failed");
            Check(!calls.SurfaceLifecycle.Invoke(state,"created",1,1),"destroyed session resurrected");
            var token=new long[]{123,1,2};int rendered=-1;
            AppDomain.CurrentDomain.SetData("Confectory.Android.Surface.123",new object[]{(Action<int,int[],string[]>)((view,r,t)=>rendered=view),(Func<int[]>)(()=>new[]{1,11,0,0,0,7})});
            try
            {
                calls.Draw.Invoke(token,1,new[]{0,0,100,100,0},new[]{"test"});Check(rendered==1,"Android draw adapter not selected");
                Check(calls.Pump.Invoke(token)[1]==11,"Android pointer cancellation adapter not selected");
            }
            finally{AppDomain.CurrentDomain.SetData("Confectory.Android.Surface.123",null);}
            Console.WriteLine("Android managed contracts/lifecycle PASS; native app not exercised");return 0;
            """);
        var report=new Builder(project,"android").Build();
        Output(report,"Android managed contracts/lifecycle PASS; native app not exercised");
        var catalog=JsonNode.Parse(File.ReadAllText(Text(report,"publicCatalog")))!;
        foreach(string id in new[]{"Confectory.Window::DrawBody","Confectory.Window::PumpBody"})
            Equal("android",catalog["implementations"]!.AsArray().Single(x=>x!["id"]!.GetValue<string>()==id)!["bodySelection"]!.GetValue<string>());
        string exporter=Path.Combine(Fixture.Repo,"targets","android-export","bin","Release","net10.0","Confectory.AndroidExport.dll");
        string output=Path.Combine(f.Root,"android-export");
        var result=Processes.Run([Processes.DotNet(),exporter,project,output],timeoutSeconds:90);
        Equal(0,result.ExitCode);
        var export=JsonNode.Parse(File.ReadAllText(Path.Combine(output,"export-report.json")))!;
        True(export["managedCompiled"]!.GetValue<bool>());
        True(!export["androidAppCompiled"]!.GetValue<bool>()&&!export["apkProduced"]!.GetValue<bool>());
        string sdkProject=File.ReadAllText(Path.Combine(output,"Confectory.Android.csproj"));
        True(sdkProject.Contains("net10.0-android",StringComparison.Ordinal));
        True(sdkProject.Contains("Managed/Contracts_",StringComparison.Ordinal)&&sdkProject.Contains("Managed/Pack_",StringComparison.Ordinal));
        True(File.Exists(Path.Combine(output,"Generated","PackEntry.cs")));
        True(!File.Exists(Path.Combine(output,"Generated","PackCalls.cs")));
        var cached=new Builder(project,"android").Build();Equal(0,Strings(cached,"statistics","compiledImplementations").Length);
        File.AppendAllText(Path.Combine(f.Root,"packs","window","Draw.android.csbody"),"\n// Android provider locality\n");
        var changed=new Builder(project,"android").Build();
        PackRebuilt(changed, new[]{"Confectory.Window::DrawBody"});
        Equal(0,Strings(changed,"statistics","compiledContracts").Length);
        Output(changed,"Android managed contracts/lifecycle PASS; native app not exercised");
    }
}
