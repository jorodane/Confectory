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
        if(name=="editor-home") { string model=Path.Combine(path,"owned editor-home-model");Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","editor-home-model"),model);foreach(string file in Directory.GetFiles(path,"*.cpack"))File.WriteAllText(file,File.ReadAllText(file).Replace(Path.Combine(Fixture.Repo,"packs","editor-home-model","pack.cpack"),Path.Combine(model,"pack.cpack"),StringComparison.Ordinal)); }
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
        File.AppendAllText(Path.Combine(consumer,"owned editor-home-model","Command.csbody"),"\n// entry/home command locality probe\n");var changed=new Builder(project,"linux").Build();Sequence(new[]{"Confectory.EditorHome.Model::CommandBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
    }
    public void test_entry_home_actual_linux_startup_navigation_create_folder_cards_resize_and_lifetime()
    {
        if(string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISPLAY"))){Console.WriteLine("SKIP native entry/home: no actual DISPLAY");return;}
        string consumer=Consumer("editor-home"),project=Path.Combine(consumer,"project.cpack");var built=new Builder(project,"linux").Build();Offline(built);string report=Path.Combine(f.Root,"home native report.json");File.WriteAllText(report,built.ToJsonString());var run=Processes.Run(new[]{"python",Path.Combine(Fixture.Repo,"tests","gui","entry_home_x11.py"),report},timeoutSeconds:240);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Entry/home actual X11"));
        File.AppendAllText(Path.Combine(consumer,"Main.csbody"),"\n// fresh presentation locality probe\n");var changed=new Builder(project,"linux").Build();Sequence(new[]{"Confectory.EditorHome::MainBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
    }
    public void test_android_home_export_selects_activity_and_metadata_parser_without_engine_surface_sample()
    {
        string consumer=Consumer("editor-home"),project=Path.Combine(consumer,"project.cpack"),output=Path.Combine(f.Root,"home Android export");
        string exporter=Path.Combine(Fixture.Repo,"targets","android-export","bin","Release","net8.0","Confectory.AndroidExport.dll");
        var result=Processes.Run(new[]{Processes.DotNet(),exporter,project,output},timeoutSeconds:240);
        True(result.ExitCode==0,result.Stdout+result.Stderr);
        string activity=File.ReadAllText(Path.Combine(output,"MainActivity.cs")),sdk=File.ReadAllText(Path.Combine(output,"Confectory.Android.csproj"));
        True(activity.Contains("PackCalls.CreateSession",StringComparison.Ordinal)&&activity.Contains("Intent.ActionOpenDocument",StringComparison.Ordinal));
        True(!activity.Contains("public sealed class PackSurface",StringComparison.Ordinal),"Home received engine sample Activity");
        True(File.Exists(Path.Combine(output,"NativeFieldHost.cs"))&&File.Exists(Path.Combine(output,"Managed","Confectory.Core.dll")));
        True(sdk.Contains("Managed/Confectory.Core.dll",StringComparison.Ordinal));
        var report=JsonNode.Parse(File.ReadAllText(Path.Combine(output,"export-report.json")))!;
        True(report["managedCompiled"]!.GetValue<bool>()&&!report["androidAppCompiled"]!.GetValue<bool>()&&!report["apkProduced"]!.GetValue<bool>());
        True(report["bodySelections"]!.AsArray().Any(row=>row!["id"]!.ToString()=="Confectory.EditorHome::MainBody"&&row["selection"]!.ToString()=="android"));
        True(!Directory.GetFiles(output,"*.apk",SearchOption.AllDirectories).Any()&&!Directory.GetFiles(output,"*.aab",SearchOption.AllDirectories).Any());
    }
    public void test_android_export_owned_settings_formats_xml_and_rejects_credentials_before_build()
    {
        string consumer=Consumer("editor-home"),project=Path.Combine(consumer,"project.cpack"),settings=Path.Combine(consumer,"AndroidExport.celem");
        string exporter=Path.Combine(Fixture.Repo,"targets","android-export","bin","Release","net8.0","Confectory.AndroidExport.dll");
        string original=File.ReadAllText(settings);
        string declaration(string values)=>"object Confectory.EditorHome::AndroidExport extends Confectory.AndroidExport.Settings::Defaults { "+values+" }";
        foreach(string format in new[]{"apk","aab"})
        {
            string title="한글 App & < > $& $([System.Math]::Abs(-2))",version="1.2 & <beta> $&";
            File.WriteAllText(settings,declaration("value applicationId = "+System.Text.Json.JsonSerializer.Serialize("org.example.entry")+"; value applicationTitle = "+System.Text.Json.JsonSerializer.Serialize(title)+"; value versionName = "+System.Text.Json.JsonSerializer.Serialize(version)+"; value versionCode = 42; value packageFormat = "+System.Text.Json.JsonSerializer.Serialize(format)+";"));
            string output=Path.Combine(f.Root,"settings "+format);
            var result=Processes.Run(new[]{Processes.DotNet(),exporter,project,output},timeoutSeconds:240);True(result.ExitCode==0,result.Stdout+result.Stderr);
            var xml=System.Xml.Linq.XDocument.Load(Path.Combine(output,"Confectory.Android.csproj"));
            string Text(string tag)=>Uri.UnescapeDataString(xml.Descendants(tag).Single().Value);
            Equal("org.example.entry",Text("ApplicationId"));Equal(title,Text("ApplicationTitle"));Equal(version,Text("ApplicationDisplayVersion"));Equal("42",Text("ApplicationVersion"));Equal(format,Text("AndroidPackageFormats"));Equal(format,Text("AndroidPackageFormat"));
            var evaluated=Processes.Run(new[]{Processes.DotNet(),"msbuild",Path.Combine(output,"Confectory.Android.csproj"),"-getProperty:ApplicationTitle"},timeoutSeconds:30);True(evaluated.ExitCode==0,evaluated.Stderr);Equal(title,evaluated.Stdout.TrimEnd('\r','\n'));
            string raw=File.ReadAllText(Path.Combine(output,"Confectory.Android.csproj"));True(raw.Contains("_CreateAndroidDebugSigningKey",StringComparison.Ordinal)&&raw.Contains("SignAndroidPackage",StringComparison.Ordinal),"Unsigned build lacks signing guard");
            True(!File.Exists(Path.Combine(output,"package-report.json")),"Source-only export claimed a package");
        }
        // Poisoned implementation proves rejected settings never reach managed source compilation.
        File.WriteAllText(Path.Combine(consumer,"Main.android.csbody"),"not valid C#");
        foreach(var invalid in new[]{("badid","value applicationId = \"not.an-app\";"),("badformat","value packageFormat = \"zip\";"),("password","value keystorePassword = \"must-not-be-stored\";"),("keystore","value keystorePath = \"must-not-be-stored\";")})
        {
            File.WriteAllText(settings,declaration(invalid.Item2));string output=Path.Combine(f.Root,invalid.Item1);
            var result=Processes.Run(new[]{Processes.DotNet(),exporter,project,output},timeoutSeconds:20);
            True(result.ExitCode!=0,"Invalid settings accepted");True(!Directory.Exists(output),"Rejected metadata created an export");
            True(!result.Stderr.Contains("must-not-be-stored",StringComparison.Ordinal),"Rejected credentials leaked into diagnostic");
            True(!result.Stderr.Contains("CS100",StringComparison.Ordinal),"Settings validation ran after source compilation");
        }
        File.WriteAllText(settings,original);
    }
    public void test_android_home_activity_dispatch_requires_adapter_and_preserves_public_domain()
    {
        string consumer=Consumer("editor-home"),project=Path.Combine(consumer,"project.cpack");
        File.WriteAllText(Path.Combine(consumer,"Main.android.csbody"),"""
            bool refused=false;try{calls.NativeRequest.Invoke("","android-home","{}",0);}catch(PlatformNotSupportedException){refused=true;}
            if(!refused)throw new Exception("Managed build claimed Android native runtime");
            bool initialized=false;AppDomain.CurrentDomain.SetData("Confectory.Android.NativeUI",(Func<string,string,string,long,string>)((h,op,p,owner)=>{if(op!="android-home")throw new Exception(op);initialized=true;return "{}";}));
            calls.NativeRequest.Invoke("","android-home","{}",0);if(!initialized)throw new Exception("Activity dispatch failed");
            string storage=System.IO.Path.Combine(System.IO.Path.GetTempPath(),"confectory-android-home-probe-"+Guid.NewGuid().ToString("N"));
            string library=System.IO.Path.Combine(storage,"library.cpack"),other=System.IO.Path.Combine(storage,"other.cpack");System.IO.Directory.CreateDirectory(storage);
            System.IO.File.WriteAllText(library,"pack Example.Library version \"1\" { standalone false; }");System.IO.File.WriteAllText(other,"pack Example.Other version \"1\" { standalone false; }");
            AppDomain.CurrentDomain.SetData("Confectory.Android.DescribeProject",(Func<string,string[]>)(path=>new[]{path==library?"Example.Library":"Example.Other","","","pack","false"}));
            string session=calls.CreateSession.Invoke(storage,storage);
            try
            {
                string Json(string path)=>System.Text.Json.JsonSerializer.Serialize(new{path});
                var opened=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(session,"open-request",Json(library)))!;
                string context=opened["selected"]!["context"]!.ToString();
                calls.Command.Invoke(session,"shell",System.Text.Json.JsonSerializer.Serialize(new{action="draft",value="unsaved 한글"}));
                var duplicate=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(session,"open-request",Json(library)))!;
                if(duplicate["selected"]!["context"]!.ToString()!=context||duplicate["shell"]!["draft"]!.ToString()!="unsaved 한글")throw new Exception("Duplicate replaced draft/context");
                var blocked=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(session,"open-request",Json(other)))!;
                if(blocked["selected"]!["path"]!.ToString()!=library||!blocked["status"]!.ToString().StartsWith("Error:"))throw new Exception("Different pack replaced active work");
                calls.Command.Invoke(session,"leave","{}");var next=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(session,"open-request",Json(other)))!;
                if(next["selected"]!["path"]!.ToString()!=other)throw new Exception("Explicit Leave did not permit next import");
            }
            finally{calls.CloseSession.Invoke(session);AppDomain.CurrentDomain.SetData("Confectory.Android.NativeUI",null);AppDomain.CurrentDomain.SetData("Confectory.Android.DescribeProject",null);System.IO.Directory.Delete(storage,true);}
            Console.WriteLine("Android Home managed domain and adapter gate PASS; Activity/device not exercised");return 0;
            """);
        var built=new Builder(project,"android").Build();Output(built,"Android Home managed domain and adapter gate PASS; Activity/device not exercised");
        File.AppendAllText(Path.Combine(consumer,"Main.android.csbody"),"\n// Android Home adapter locality probe\n");
        var changed=new Builder(project,"android").Build();Sequence(new[]{"Confectory.EditorHome::MainBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
    }
    public void test_entry_home_windows_android_managed_profiles_compile_only()
    {
        string consumer=Consumer("editor-home");foreach(string target in new[]{"windows"}){var built=new Builder(Path.Combine(consumer,"project.cpack"),target).Build();True(built["tool"]!["ok"]!.GetValue<bool>());Offline(built);}
        var android=new Builder(Path.Combine(consumer,"project.cpack"),"android").Build();True(android["tool"]!["ok"]!.GetValue<bool>());Offline(android);
    }
}
