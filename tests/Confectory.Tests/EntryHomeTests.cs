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
        string? repo=Environment.GetEnvironmentVariable("CONFECTORY_EDITOR_REPO"),host=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST");try{Environment.SetEnvironmentVariable("CONFECTORY_EDITOR_REPO",Fixture.Repo);Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets","element-authoring","bin","Release","net10.0","Confectory.ElementAuthoring.dll"));var run=Processes.Run(Strings(built,"run"),timeoutSeconds:180);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Entry/home contracts:"));}finally{Environment.SetEnvironmentVariable("CONFECTORY_EDITOR_REPO",repo);Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",host);}
        File.AppendAllText(Path.Combine(manager,"PlanCreation.csbody"),"\n// naming policy provider locality probe\n");var naming=new Builder(project,"linux").Build();Sequence(new[]{"Confectory.ProjectManager::PlanCreationBody"},Strings(naming,"statistics","compiledImplementations"));Equal(0,Strings(naming,"statistics","compiledContracts").Length);
        File.AppendAllText(Path.Combine(consumer,"owned editor-home-model","Command.csbody"),"\n// entry/home command locality probe\n");var changed=new Builder(project,"linux").Build();Sequence(new[]{"Confectory.EditorHome.Model::CommandBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
    }
    public void test_entry_home_actual_linux_startup_navigation_create_folder_cards_resize_and_lifetime()
    {
        if(string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISPLAY"))){Skip("native entry/home: no actual DISPLAY");}
        string consumer=Consumer("editor-home"),project=Path.Combine(consumer,"project.cpack");var built=new Builder(project,"linux").Build();Offline(built);string report=Path.Combine(f.Root,"home native report.json");File.WriteAllText(report,built.ToJsonString());var run=Processes.Run(new[]{"python",Path.Combine(Fixture.Repo,"tests","gui","entry_home_x11.py"),report},timeoutSeconds:240);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Entry/home actual X11"));
        File.AppendAllText(Path.Combine(consumer,"Main.csbody"),"\n// fresh presentation locality probe\n");var changed=new Builder(project,"linux").Build();Sequence(new[]{"Confectory.EditorHome::MainBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
    }
    public void test_android_home_export_selects_activity_and_metadata_parser_without_engine_surface_sample()
    {
        string consumer=Consumer("editor-home"),project=Path.Combine(consumer,"project.cpack"),output=Path.Combine(f.Root,"home Android export");
        string exporter=Path.Combine(Fixture.Repo,"targets","android-export","bin","Release","net10.0","Confectory.AndroidExport.dll");
        var result=Processes.Run(new[]{Processes.DotNet(),exporter,project,output},timeoutSeconds:240);
        True(result.ExitCode==0,result.Stdout+result.Stderr);
        string activity=File.ReadAllText(Path.Combine(output,"MainActivity.cs")),sdk=File.ReadAllText(Path.Combine(output,"Confectory.Android.csproj"));
        True(activity.Contains("PackEntry.Run()",StringComparison.Ordinal)&&activity.Contains("Confectory.HostLoop.Run.android",StringComparison.Ordinal));
        True(!activity.Contains("PackCalls.CreateSession",StringComparison.Ordinal)&&!activity.Contains("PackCalls.Command",StringComparison.Ordinal)&&!activity.Contains("DrawHome",StringComparison.Ordinal),"Android host must not replace actual product controls/model commands");
        True(File.Exists(Path.Combine(output,"AndroidDocumentImport.cs")),"Generic granted import adapter missing");
        string entry=File.ReadAllText(Path.Combine(output,"Generated","PackEntry.cs"));
        True(entry.Contains("static int Run",StringComparison.Ordinal),"Generated actual ProjectPack entry bridge missing");
        True(!activity.Contains("public sealed class PackSurface",StringComparison.Ordinal),"Home received engine sample Activity");
        True(activity.Contains("LaunchMode.SingleTask",StringComparison.Ordinal)&&!activity.Contains("LaunchMode.SingleTop",StringComparison.Ordinal),"Product Activity must own one controller for repeated external entry");
        True(File.Exists(Path.Combine(output,"NativeFieldHost.cs"))&&File.Exists(Path.Combine(output,"Managed","Confectory.Core.dll")));
        True(sdk.Contains("Managed/Confectory.Core.dll",StringComparison.Ordinal));
        True(File.Exists(Path.Combine(output,"AndroidManifest.xml")),"Export omitted required Android manifest");
        var xml=System.Xml.Linq.XDocument.Parse(sdk);Equal("false",xml.Descendants("PublishTrimmed").Single().Value);Equal("true",xml.Descendants("JsonSerializerIsReflectionEnabledByDefault").Single().Value);
        var report=JsonNode.Parse(File.ReadAllText(Path.Combine(output,"export-report.json")))!;
        True(report["managedCompiled"]!.GetValue<bool>()&&!report["androidAppCompiled"]!.GetValue<bool>()&&!report["apkProduced"]!.GetValue<bool>());
        True(report["bodySelections"]!.AsArray().Any(row=>row!["id"]!.ToString()=="Confectory.EditorHome::MainBody"&&row["selection"]!.ToString()=="common"));
        True(!Directory.GetFiles(output,"*.apk",SearchOption.AllDirectories).Any()&&!Directory.GetFiles(output,"*.aab",SearchOption.AllDirectories).Any());
    }
    public void test_android_generic_export_accepts_renamed_no_window_int_and_void_entries()
    {
        foreach(bool returnsVoid in new[]{false,true})
        {
            string ns=returnsVoid?"Example.VoidEntry":"Example.RenamedProduct";
            string consumer=Path.Combine(f.Root,returnsVoid?"void Android product":"renamed Android product");Directory.CreateDirectory(consumer);
            string project=Path.Combine(consumer,"project.cpack"),output=Path.Combine(consumer,"export");
            File.WriteAllText(project,"project "+ns+" version \"0.1.0\" { standalone true; registry Confectory.Build.DotNet \""+Path.Combine(Fixture.Repo,"targets","dotnet","pack.cpack")+"\"; dependency Confectory.Build.DotNet version \"0.1.0\"; element Main function \"Main.celem\"; element MainBody implementation \"MainBody.celem\"; entry "+ns+"::Main; target android Confectory.Build.DotNet::Portable; }");
            string type=returnsVoid?"void":"int";
            File.WriteAllText(Path.Combine(consumer,"Main.celem"),"function "+ns+"::Main () -> "+type+" { provide "+ns+"::Main with "+ns+"::MainBody; }");
            File.WriteAllText(Path.Combine(consumer,"MainBody.celem"),"implementation "+ns+"::MainBody for "+ns+"::Main () -> "+type+" { body common \"Main.csbody\"; }");
            File.WriteAllText(Path.Combine(consumer,"Main.csbody"),returnsVoid?"Console.WriteLine(\"void product entry\");return;":"return 7;");
            string exporter=Path.Combine(Fixture.Repo,"targets","android-export","bin","Release","net10.0","Confectory.AndroidExport.dll");
            var result=Processes.Run(new[]{Processes.DotNet(),exporter,project,output},timeoutSeconds:180);True(result.ExitCode==0,result.Stdout+result.Stderr);
            string entry=File.ReadAllText(Path.Combine(output,"Generated","PackEntry.cs")),activity=File.ReadAllText(Path.Combine(output,"MainActivity.cs"));
            True(entry.Contains("static int Run",StringComparison.Ordinal)&&entry.Contains(".Invoke()",StringComparison.Ordinal));
            True(activity.Contains("PackEntry.Run()",StringComparison.Ordinal)&&activity.Contains("no presentation loop was registered",StringComparison.Ordinal));
            True(!activity.Contains("PackCalls.",StringComparison.Ordinal)&&!activity.Contains("DrawHome",StringComparison.Ordinal));
            True(!File.Exists(Path.Combine(output,"AndroidSurfaceBridge.cs")),"Generic entry acquired mandatory Window sample bridge");
            var report=JsonNode.Parse(File.ReadAllText(Path.Combine(output,"export-report.json")))!;Equal(ns+"::Main",report["entry"]!.ToString());
            var contracts=report["contracts"]!.AsArray();Equal(1,contracts.Count);Equal(ns+"::Main",contracts[0]!.ToString());
            var body=report["bodySelections"]!.AsArray().Single()!;Equal(ns+"::MainBody",body["id"]!.ToString());Equal("common",body["selection"]!.ToString());
            True(!Directory.GetFiles(output,"*.apk",SearchOption.AllDirectories).Any(),"Source export claimed package coverage");
        }
    }
    public void test_android_native_request_preserves_owner_release_and_rejects_unknown_close()
    {
        string consumer=Path.Combine(f.Root,"Android owner dispatch");Directory.CreateDirectory(consumer);string project=Path.Combine(consumer,"project.cpack");
        File.WriteAllText(project,"project Example.AndroidOwnerProbe version \"0.1.0\" { standalone true; registry Confectory.NativeUI \""+Path.Combine(Fixture.Repo,"packs","native-ui-desktop","pack.cpack")+"\"; dependency Confectory.NativeUI version \"0.1.0\"; registry Confectory.Build.DotNet \""+Path.Combine(Fixture.Repo,"targets","dotnet","pack.cpack")+"\"; dependency Confectory.Build.DotNet version \"0.1.0\"; element Main function \"Main.celem\";element MainBody implementation \"MainBody.celem\";entry Example.AndroidOwnerProbe::Main;target android Confectory.Build.DotNet::Portable; }");
        File.WriteAllText(Path.Combine(consumer,"Main.celem"),"function Example.AndroidOwnerProbe::Main () -> int { provide Example.AndroidOwnerProbe::Main with Example.AndroidOwnerProbe::MainBody; }");
        File.WriteAllText(Path.Combine(consumer,"MainBody.celem"),"implementation Example.AndroidOwnerProbe::MainBody for Example.AndroidOwnerProbe::Main () -> int { import Confectory.NativeUI::Request as Request (string,string,string,long) -> string;body common \"Main.csbody\"; }");
        File.WriteAllText(Path.Combine(consumer,"Main.csbody"),"""
string host=Guid.NewGuid().ToString("N"),ownerKey="Confectory.Android.NativeUI.Owner."+host,closedKey="Confectory.Android.NativeUI.Closed."+host;int attempts=0,wrongOwner=0;
AppDomain.CurrentDomain.SetData("Confectory.Android.NativeUI",(Func<string,string,string,long,string>)((h,o,p,n)=>{wrongOwner++;throw new Exception("New Activity must not release old owner");}));
AppDomain.CurrentDomain.SetData(ownerKey,(Func<string,string,string,long,string>)((h,o,p,n)=>{attempts++;if(attempts==1)throw new InvalidOperationException("Injected native release failure");AppDomain.CurrentDomain.SetData(closedKey,true);AppDomain.CurrentDomain.SetData(ownerKey,null);return "{}";}));
try{
 bool failed=false;try{calls.Request.Invoke(host,"close","{}",0);}catch(InvalidOperationException){failed=true;}if(!failed||AppDomain.CurrentDomain.GetData(ownerKey) is null)throw new Exception("Failed native release owner was lost");
 calls.Request.Invoke(host,"close","{}",0);calls.Request.Invoke(host,"close","{}",0);if(attempts!=2||wrongOwner!=0)throw new Exception("Owner dispatch or successful-close idempotence failed");
 bool unknown=false;try{calls.Request.Invoke(Guid.NewGuid().ToString("N"),"close","{}",0);}catch(PlatformNotSupportedException){unknown=true;}if(!unknown)throw new Exception("Unknown GUID owner was silently closed");
 Console.WriteLine("Android owner dispatch failure/retry/idempotence protocol passed; no native device execution");return 0;
}finally{AppDomain.CurrentDomain.SetData(ownerKey,null);AppDomain.CurrentDomain.SetData(closedKey,null);AppDomain.CurrentDomain.SetData("Confectory.Android.NativeUI",null);}
""");
        var built=new Builder(project,"android").Build();var run=Processes.Run(Strings(built,"run"));True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Android owner dispatch failure/retry/idempotence protocol passed",StringComparison.Ordinal));
    }
    public void test_android_export_owned_settings_formats_xml_and_rejects_credentials_before_build()
    {
        string consumer=Consumer("editor-home"),project=Path.Combine(consumer,"project.cpack"),settings=Path.Combine(consumer,"AndroidExport.celem");
        string exporter=Path.Combine(Fixture.Repo,"targets","android-export","bin","Release","net10.0","Confectory.AndroidExport.dll");
        string original=File.ReadAllText(settings);
        string declaration(string values)=>"object Confectory.EditorHome::AndroidExport extends Confectory.AndroidExport.Settings::Defaults { "+values+" }";
        foreach(string format in new[]{"apk","aab"})
        {
            string title="한글 App & < > $& $([System.Math]::Abs(-2))",version="1.2 & <beta> $&";
            File.WriteAllText(settings,declaration("value applicationId = "+System.Text.Json.JsonSerializer.Serialize("org.example.entry")+"; value applicationTitle = "+System.Text.Json.JsonSerializer.Serialize(title)+"; value versionName = "+System.Text.Json.JsonSerializer.Serialize(version)+"; value versionCode = 42; value packageFormat = "+System.Text.Json.JsonSerializer.Serialize(format)+";"));
            string framework="net10.0-android";
            File.WriteAllText(settings,File.ReadAllText(settings).Replace(" }"," value androidTargetFramework = "+System.Text.Json.JsonSerializer.Serialize(framework)+"; }"));
            string output=Path.Combine(f.Root,"settings "+format);
            var result=Processes.Run(new[]{Processes.DotNet(),exporter,project,output},timeoutSeconds:240);True(result.ExitCode==0,result.Stdout+result.Stderr);
            var xml=System.Xml.Linq.XDocument.Load(Path.Combine(output,"Confectory.Android.csproj"));
            string Text(string tag)=>Uri.UnescapeDataString(xml.Descendants(tag).Single().Value);
            Equal("org.example.entry",Text("ApplicationId"));Equal(title,Text("ApplicationTitle"));Equal(version,Text("ApplicationDisplayVersion"));Equal("42",Text("ApplicationVersion"));Equal(format,Text("AndroidPackageFormats"));Equal(format,Text("AndroidPackageFormat"));Equal(framework,Text("TargetFramework"));
            var evaluated=Processes.Run(new[]{Processes.DotNet(),"msbuild",Path.Combine(output,"Confectory.Android.csproj"),"-getProperty:ApplicationTitle"},timeoutSeconds:30);True(evaluated.ExitCode==0,evaluated.Stderr);Equal(title,evaluated.Stdout.TrimEnd('\r','\n'));
            string raw=File.ReadAllText(Path.Combine(output,"Confectory.Android.csproj"));True(raw.Contains("_CreateAndroidDebugSigningKey",StringComparison.Ordinal)&&raw.Contains("SignAndroidPackage",StringComparison.Ordinal),"Unsigned build lacks signing guard");
            True(!File.Exists(Path.Combine(output,"package-report.json")),"Source-only export claimed a package");
        }
        // Poisoned implementation proves rejected settings never reach managed source compilation.
        File.WriteAllText(Path.Combine(consumer,"Main.csbody"),"not valid C#");
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
    public void test_entry_home_windows_android_managed_profiles_compile_only()
    {
        string consumer=Consumer("editor-home");foreach(string target in new[]{"windows"}){var built=new Builder(Path.Combine(consumer,"project.cpack"),target).Build();True(built["tool"]!["ok"]!.GetValue<bool>());Offline(built);}
        var android=new Builder(Path.Combine(consumer,"project.cpack"),"android").Build();True(android["tool"]!["ok"]!.GetValue<bool>());Offline(android);
    }
}
