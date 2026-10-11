using Confectory.Core;
namespace Confectory.Tests;
public sealed class WebUITests : TestCase
{
    public void test_actual_editor_and_button_game_common_web_transport_chromium()
    {
        foreach(var (folder,kind) in new[]{("button-game","button"),("editor-home","editor")})
        {
            var built=new Builder(Path.Combine(Fixture.Repo,"examples",folder,"project.cpack"),"linux").Build();
            True(Strings(built,"includedPacks").Contains("Confectory.WebUI"));
            if(kind=="button")True(!Strings(built,"includedPacks").Any(x=>x.Contains("EditorHome",StringComparison.Ordinal)),"Generic consumer acquired editor dependency");
            string report=Path.Combine(f.Root,kind+".json");File.WriteAllText(report,built.ToJsonString());
            var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/web/web_ui.py"),Fixture.Repo,report,kind},timeoutSeconds:180);
            True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Actual common WebUI "+kind+" Chromium PASS"));
        }
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
        import Confectory.WebUI::Resource as Resource (string,string) -> string[];
        import Confectory.WebUI::Close as Close (string) -> bool;
        body common "main.csbody"; }
        """);
        f.Body("App","main.csbody",""""
        void Check(bool b,string message){if(!b)throw new Exception(message);}
        string context="unit-context";
        void State(string project="p",string helper="h",int revision=0){AppDomain.CurrentDomain.SetData(context,System.Text.Json.JsonSerializer.Serialize(new{scope=new{projectId=project,helperId=helper},revision,state=new{value=revision}}));}
        State();string descriptor="""{"id":"unit","version":"1","entry":"index.html","endpoints":["wait","done"],"resources":{"index.html":{"mime":"text/html","base64":"PGgxPnVuaXQ8L2gxPg=="}}}""";
        string owner=calls.Open.Invoke(context,descriptor);
        System.Text.Json.Nodes.JsonNode Send(object req)=>System.Text.Json.Nodes.JsonNode.Parse(calls.Request.Invoke(owner,System.Text.Json.JsonSerializer.Serialize(req)))!;
        var mount=Send(new{op="mount"});string view=mount["view"]!.ToString();var scope=mount["scope"]!.DeepClone();
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
