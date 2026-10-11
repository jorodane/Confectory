using Confectory.Core;
namespace Confectory.Tests;
public sealed class WebUITests : TestCase
{
    public void test_actual_editor_original_v196_home_project_and_create_flow()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples","editor-home","project.cpack"),"linux").Build();
        string report=Path.Combine(f.Root,"original-layout.json"),reference=Path.Combine(f.Root,"original-v196");
        File.WriteAllText(report,built.ToJsonString());
        System.IO.Compression.ZipFile.ExtractToDirectory(Path.Combine(Fixture.Repo,"reference","site-ui","Confectory-Editor-Prototype-v196.zip"),reference);
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests","web","editor_home_original_layout.py"),Fixture.Repo,report,reference},timeoutSeconds:180);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS ordinary ProjectPack original Home"));
    }
    public void test_actual_editor_review_compact_numeric_and_subset_caption()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples","editor-home","project.cpack"),"linux").Build();
        string report=Path.Combine(f.Root,"review-presentation.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,"review-presentation"},timeoutSeconds:180);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual compact numeric row and fresh subset caption"));
    }
    public void test_actual_editor_new_concept_creation_save_confirm_reopen()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples","editor-home","project.cpack"),"linux").Build();
        string report=Path.Combine(f.Root,"creation.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,"creation"},timeoutSeconds:600);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Actual common WebUI creation Chromium PASS"));
        True(run.Stdout.Contains("PASS new concept actual process reopen"));
    }
    public void test_actual_editor_and_button_game_common_web_transport_chromium()
    {
        foreach(var (folder,kind) in new[]{("button-game","button"),("editor-home","editor")})
        {
            var built=new Builder(Path.Combine(Fixture.Repo,"examples",folder,"project.cpack"),"linux").Build();
            True(Strings(built,"includedPacks").Contains("Confectory.WebUI"));
            if(kind=="button")True(!Strings(built,"includedPacks").Any(x=>x.Contains("EditorHome",StringComparison.Ordinal)),"Generic consumer acquired editor dependency");
            string report=Path.Combine(f.Root,kind+".json");File.WriteAllText(report,built.ToJsonString());
            var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,kind},timeoutSeconds:900);
            True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Actual common WebUI "+kind+" Chromium PASS"));
        }
    }
    public void test_editor_web_resources_windows_git_checkout_and_actual_startup()
    {
        var built=new Builder(Path.Combine(Fixture.Repo,"examples","editor-home","project.cpack"),"linux").Build();
        string report=Path.Combine(f.Root,"resource-checkout.json");File.WriteAllText(report,built.ToJsonString());
        var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests","probes","web_resource_checkout.py"),Fixture.Repo,report},timeoutSeconds:180);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual EditorHome retained CRLF after attribute pull and fresh LF"));
    }
    public void test_web_ui_scope_revision_cancellation_disposal_and_pack_locality()
    {
        foreach(var (ns,path) in new[]{("Confectory.WebUI","web-ui"),("Confectory.RuntimeBase","runtime-base")})
        {
            string local=Path.Combine(f.Root,path);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",path),local);
            f.ExtraRegistry[ns]=Path.Combine(local,"pack.cpack");f.Packs["App"].Dependencies[ns]="0.1.0";
        }
        f.Main("provide Confectory.WebUI::State with App::State; provide Confectory.WebUI::Invoke with App::Invoke; "+string.Join(" ",new[]{"CreateOwner","CreateInstance","Write","Subscribe","Poll","Unsubscribe","DisposeOwner"}.Select(n=>$"provide Confectory.RuntimeBase::{n} with Confectory.RuntimeBase::{n}Body;")));
        f.Add("App","implementation","State","""
        implementation App::State for Confectory.WebUI::State (string context) -> string { body common "state.csbody"; }
        """);
        f.Body("App","state.csbody","""
        return (string)AppDomain.CurrentDomain.GetData(context)!;
        """);
        f.Add("App","implementation","Invoke","""
        implementation App::Invoke for Confectory.WebUI::Invoke (string context,string endpoint,string input,string cancellation) -> string {
        import Confectory.WebUI::Cancelled as Cancelled (string) -> bool;
        body common "invoke.csbody"; }
        """);
        f.Body("App","invoke.csbody","""
        AppDomain.CurrentDomain.SetData(context+"started",true);
        if(endpoint=="wait") {while(!calls.Cancelled.Invoke(cancellation))System.Threading.Thread.Sleep(1);throw new OperationCanceledException();}
        return "{\"done\":true}";
        """);
        f.Add("App","implementation","MainBody","""
        implementation App::MainBody for App::Main () -> int {
        import Confectory.WebUI::Open as Open (string,string) -> string;
        import Confectory.WebUI::Request as Request (string,string) -> string;
        import Confectory.WebUI::NativeRequest as NativeRequest (string,string,string) -> string;
        import Confectory.WebUI::Resource as Resource (string,string) -> string[];
        import Confectory.WebUI::Close as Close (string) -> bool;
        body common "main.csbody"; }
        """);
        f.Body("App","main.csbody",""""
        void Check(bool b,string message){if(!b)throw new Exception(message);}
        string context="unit-context";
        void State(string project="p",string helper="h",int revision=0){AppDomain.CurrentDomain.SetData(context,System.Text.Json.JsonSerializer.Serialize(new{scope=new{projectId=project,helperId=helper},revision,state=new{value=revision}}));}
        State();string descriptor="""{"id":"unit","version":"1","entry":"index.html","endpoints":["wait","done"],"resources":{"index.html":{"mime":"text/html","base64":"PGgxPnVuaXQ8L2gxPg=="}}}""";
        string assetRoot=System.IO.Path.Combine(System.IO.Path.GetTempPath(),"confectory-manifest-"+Guid.NewGuid().ToString("N"));System.IO.Directory.CreateDirectory(assetRoot);
        try{
         byte[] image=new byte[2097152];System.IO.File.WriteAllBytes(System.IO.Path.Combine(assetRoot,"portrait.png"),image);
         var declared=System.Text.Json.Nodes.JsonNode.Parse(descriptor)!.AsObject();declared["resourceDirectory"]=assetRoot;
         declared["resources"]!["portrait.png"]=new System.Text.Json.Nodes.JsonObject{["file"]="portrait.png",["mime"]="image/png",["size"]=image.Length,["sha256"]=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(image))};
         string fileOwner=calls.Open.Invoke(context,declared.ToJsonString());Check(Convert.FromBase64String(calls.Resource.Invoke(fileOwner,"portrait.png")[1]).Length==image.Length,"normal common manifest exceeds old 1MiB limit");Check(calls.Close.Invoke(fileOwner),"manifest owner close");
         void Rejected(string name,string diagnostic=""){try{string unexpected=calls.Open.Invoke(context,declared.ToJsonString());calls.Close.Invoke(unexpected);throw new Exception(name+" accepted");}catch(ArgumentException error){Check(error.Message.Contains(diagnostic,StringComparison.Ordinal),name+" diagnostic: "+error.Message);Check(!error.Message.Contains(assetRoot,StringComparison.Ordinal),"diagnostic exposes local path");}}
         string textPath=System.IO.Path.Combine(assetRoot,"text.js"),lf="const value = \"한글\";\n";byte[] textBytes=System.Text.Encoding.UTF8.GetBytes(lf),crlf=System.Text.Encoding.UTF8.GetBytes(lf.Replace("\n","\r\n"));
         var textRow=new System.Text.Json.Nodes.JsonObject{["file"]="text.js",["mime"]="text/javascript",["size"]=textBytes.Length,["sha256"]=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(textBytes))};declared["resources"]!["text.js"]=textRow;
         System.IO.File.WriteAllBytes(textPath,crlf);Rejected("exact text does not normalize","Resource 'text.js': size mismatch");
         textRow["bytePolicy"]="utf8-lf-v1";textRow["canonicalSize"]=textRow["size"]!.DeepClone();textRow["canonicalSha256"]=textRow["sha256"]!.DeepClone();textRow.Remove("size");textRow.Remove("sha256");
         foreach(byte[] raw in new[]{textBytes,crlf}){System.IO.File.WriteAllBytes(textPath,raw);string canonicalOwner=calls.Open.Invoke(context,declared.ToJsonString());Check(System.Linq.Enumerable.SequenceEqual(Convert.FromBase64String(calls.Resource.Invoke(canonicalOwner,"text.js")[1]),textBytes),"LF/CRLF canonical snapshot");Check(System.Linq.Enumerable.SequenceEqual(System.IO.File.ReadAllBytes(textPath),raw),"normalization changed original");Check(calls.Close.Invoke(canonicalOwner),"canonical owner close");}
         System.IO.File.WriteAllBytes(textPath,System.Text.Encoding.UTF8.GetBytes(lf.Replace("value","VALUE")));Rejected("same-size text change","SHA-256 mismatch for canonical UTF-8 LF");
         System.IO.File.WriteAllBytes(textPath,new byte[]{255});Rejected("invalid UTF-8","invalid UTF-8 encoding");
         System.IO.File.WriteAllBytes(textPath,System.Linq.Enumerable.ToArray(System.Linq.Enumerable.Concat(new byte[]{239,187,191},textBytes)));Rejected("BOM","forbids BOM");
         foreach(string invalid in new[]{"bare\rCR","nul\0text"}){System.IO.File.WriteAllBytes(textPath,System.Text.Encoding.UTF8.GetBytes(invalid));Rejected("invalid canonical text","forbids bare CR and NUL");}
         System.IO.File.WriteAllBytes(textPath,textBytes);textRow["size"]=textBytes.Length;Rejected("ambiguous identity","mixed raw and canonical identity");textRow.Remove("size");textRow["mime"]="image/png";Rejected("binary normalization","requires a declared text file");textRow["mime"]="text/javascript";textRow["bytePolicy"]="unknown";Rejected("unknown normalization","unknown byte policy");declared["resources"]!.AsObject().Remove("text.js");
         declared["resources"]!["portrait.png"]!["sha256"]=new string('0',64);Rejected("changed resource identity","Resource 'portrait.png': SHA-256 mismatch");
         declared["resources"]!["portrait.png"]!["size"]=4194305;Rejected("oversized resource","per-resource byte budget exceeded; declared=4194305, actual=2097152, limit=4194304");
         declared["resources"]!["portrait.png"]!["size"]=2097153;Rejected("changed resource size","Resource 'portrait.png': size mismatch; expected=2097153, actual=2097152");
         declared["resources"]!.AsObject().Remove("portrait.png");byte[] maximum=new byte[4194304];for(int n=0;n<8;n++){string id="budget"+n+".png";System.IO.File.WriteAllBytes(System.IO.Path.Combine(assetRoot,id),maximum);declared["resources"]![id]=new System.Text.Json.Nodes.JsonObject{["file"]=id,["mime"]="image/png",["size"]=maximum.Length,["sha256"]=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(maximum))};}Rejected("aggregate exhaustion","Resource 'budget7.png': aggregate byte budget exceeded");for(int n=0;n<8;n++)declared["resources"]!.AsObject().Remove("budget"+n+".png");
         byte[] canonicalLines=new byte[2097152];Array.Fill(canonicalLines,(byte)10);byte[] rawLines=new byte[4194304];for(int n=0;n<rawLines.Length;n+=2){rawLines[n]=13;rawLines[n+1]=10;}
         for(int n=0;n<8;n++){string id="raw"+n+".js";System.IO.File.WriteAllBytes(System.IO.Path.Combine(assetRoot,id),rawLines);declared["resources"]![id]=new System.Text.Json.Nodes.JsonObject{["file"]=id,["mime"]="text/javascript",["bytePolicy"]="utf8-lf-v1",["canonicalSize"]=canonicalLines.Length,["canonicalSha256"]=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(canonicalLines))};}Rejected("raw aggregate exhaustion","Resource 'raw7.js': raw aggregate byte budget exceeded");for(int n=0;n<8;n++)declared["resources"]!.AsObject().Remove("raw"+n+".js");

         declared["resources"]!.AsObject().Remove("portrait.png");declared["resources"]!["../escape.png"]=new System.Text.Json.Nodes.JsonObject{["file"]="../escape.png",["mime"]="image/png",["size"]=0,["sha256"]=""};Rejected("manifest traversal");
         declared["resources"]!.AsObject().Remove("../escape.png");for(int n=0;n<256;n++)declared["resources"]!["r"+n+".png"]=new System.Text.Json.Nodes.JsonObject{["mime"]="image/png",["base64"]=""};Rejected("resource count exhaustion");
        }finally{System.IO.Directory.Delete(assetRoot,true);}
        string owner=calls.Open.Invoke(context,descriptor);
        System.Text.Json.Nodes.JsonNode Send(object req)=>System.Text.Json.Nodes.JsonNode.Parse(calls.Request.Invoke(owner,System.Text.Json.JsonSerializer.Serialize(req)))!;
        var mount=Send(new{op="mount"});string view=mount["view"]!.ToString();var scope=mount["scope"]!.DeepClone();
        Check(System.Text.Json.Nodes.JsonNode.Parse(calls.NativeRequest.Invoke(owner,"done","{}"))!["error"]!["code"]!.ToString()=="host_action_denied","undeclared native action denied");
        var nativeDescriptor=System.Text.Json.Nodes.JsonNode.Parse(descriptor)!.AsObject();nativeDescriptor["hostActions"]=new System.Text.Json.Nodes.JsonArray("done");string nativeOwner=calls.Open.Invoke(context,nativeDescriptor.ToJsonString());
        Check(System.Text.Json.Nodes.JsonNode.Parse(calls.NativeRequest.Invoke(nativeOwner,"done","{}"))!["ok"]!.GetValue<bool>(),"declared native action");Check(calls.Close.Invoke(nativeOwner),"native owner close");AppDomain.CurrentDomain.SetData(context+"started",null);
        var resource=calls.Resource.Invoke(owner,"/");Check(resource[0]=="text/html"&&resource[2].Length==64,"resource identity");
        try{calls.Resource.Invoke(owner,"../index.html");throw new Exception("traversal accepted");}catch(ArgumentException){}
        var waiting=Send(new{op="invoke",view,scope,endpoint="wait",requestId="wait",expectedRevision=0,input=new{}});Check(waiting["status"]!.ToString()=="pending","async acceptance");
        var deadline=DateTime.UtcNow.AddSeconds(5);while(AppDomain.CurrentDomain.GetData(context+"started") is null&&DateTime.UtcNow<deadline)System.Threading.Thread.Sleep(1);Check(AppDomain.CurrentDomain.GetData(context+"started") is true,"consumer started");
        Check(Send(new{op="update",view,scope})["busy"]!.GetValue<bool>(),"poll must not block cancellation behind a running call");
        Check(Send(new{op="cancel",view,scope,requestId="wait"})["status"]!.ToString()=="cancellation_requested","cancellation acknowledgement");
        System.Text.Json.Nodes.JsonNode? completed=null;
        while(DateTime.UtcNow<deadline){var update=Send(new{op="update",view,scope});completed=System.Linq.Enumerable.FirstOrDefault(update["results"]!.AsArray());if(completed is not null)break;System.Threading.Thread.Sleep(1);}
        Check(completed?["status"]?.ToString()=="cancelled"&&completed["result"] is null,"no late result after cancellation");
        State(helper:"other");Check(Send(new{op="update",view,scope})["error"]!["code"]!.ToString()=="scope_changed","host Helper scope changed");
        Check(Send(new{op="invoke",view,scope,endpoint="wait",requestId="wait",expectedRevision=0,input=new{}})["error"]!["code"]!.ToString()=="scope_changed","dedup cannot bypass current host scope");
        State(revision:1);Check(Send(new{op="update",view,scope})["changed"]!.GetValue<bool>(),"revision subscription");Check(!Send(new{op="update",view,scope})["changed"]!.GetValue<bool>(),"revision consumed once");
        Check(Send(new{op="dispose",view})["ok"]!.GetValue<bool>(),"dispose view");Check(Send(new{op="dispose",view})["ok"]!.GetValue<bool>(),"idempotent view disposal");Check(Send(new{op="update",view,scope})["error"]!["code"]!.ToString()=="view_closed","disposed view rejected");
        var remount=Send(new{op="mount"});Check(remount["revision"]!.GetValue<int>()==1,"view disposal retained consumer state");
        view=remount["view"]!.ToString();AppDomain.CurrentDomain.SetData(context+"started",null);
        Send(new{op="invoke",view,scope,endpoint="wait",requestId="close-wait",expectedRevision=1,input=new{}});
        deadline=DateTime.UtcNow.AddSeconds(5);while(AppDomain.CurrentDomain.GetData(context+"started") is null&&DateTime.UtcNow<deadline)System.Threading.Thread.Sleep(1);
        while(!calls.Close.Invoke(owner)&&DateTime.UtcNow<deadline)System.Threading.Thread.Sleep(1);Check(calls.Close.Invoke(owner),"drain ownership before close");
        Check(calls.Close.Invoke(owner),"idempotent owner close");Check(Send(new{op="mount"})["error"]!["code"]!.ToString()=="owner_closed","late reply owner unavailable");
        Console.WriteLine("WebUI boundary PASS");return 0;
        """");
        f.Sync();var first=new Builder(f.Project,"portable").Build();Output(first,"WebUI boundary PASS");
        File.AppendAllText(Path.Combine(f.Root,"web-ui","Open.csbody"),"\n// owned boundary locality probe\n");
        var changed=new Builder(f.Project,"portable").Build();PackRebuilt(changed,new[]{"Confectory.WebUI::OpenBody"});Equal(0,Strings(changed,"statistics","compiledContracts").Length);
    }
}
