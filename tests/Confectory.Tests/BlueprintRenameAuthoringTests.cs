using Confectory.Core;
using System.Text.Json.Nodes;

namespace Confectory.Tests;

public sealed partial class LocalAuthoringTests
{
    public void test_rename_owned_display_metadata_raw_cas_cold_and_compiler_confirm()
    {
        const string feature="function App::Value (long n) -> long {provide App::Value with App::ValueBody;}";
        var graph=JsonNode.Parse("""
        {"schema":1,"profile":"sync-acyclic-v1","feature":"App::Value","entry":"body","nodes":[{"id":"body","kind":"code","control":"next","intent":"Add three","signature":{"args":[{"name":"value","type":"long"}],"return":"long"},"arguments":{"value":{"input":"n"}},"implementation":"body.node.json"}],"edges":[{"from":"body","port":"next","to":"exit:done"}],"exits":{"done":{"node":"body"}}}
        """)!.AsObject();
        graph["contractHash"]=FeatureBlueprint.ContractHash(new Parser(feature,"<rename author>").ParseElement());
        var definitions=FeatureBlueprint.Execute(new(){["operation"]="featureBlueprintNodes",["featureSource"]=feature,["graph"]=graph.DeepClone()});
        f.Add("App","function","Value",feature);f.Add("App","implementation","ValueBody","implementation App::ValueBody for App::Value (long n) -> long {blueprint common \"value.graph.json\";}");
        f.Body("App","value.graph.json",graph.ToJsonString());f.Body("App","body.node.json",new JsonObject{["schema"]=1,["node"]="body",["definitionHash"]=definitions["nodes"]![0]!["definitionHash"]!.DeepClone(),["source"]="return value+3;"}.ToJsonString());
        f.Main();f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import App::Value as Value (long) -> long;body common \"main.csbody\";}");f.Body("App","main.csbody","Console.WriteLine(calls.Value.Invoke(2));return 0;");f.Sync();
        Consumer(""""
        void Check(bool ok,string why){if(!ok)throw new Exception(why);}
        System.Text.Json.Nodes.JsonNode Json(string text)=>System.Text.Json.Nodes.JsonNode.Parse(text)!;
        string Serialize(object o)=>System.Text.Json.JsonSerializer.Serialize(o);
        void Refused(Action action,string why){bool refused=false;try{action();}catch(ArgumentException){refused=true;}catch(InvalidOperationException){refused=true;}Check(refused,why);}
        string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT")!,root=System.IO.Path.GetDirectoryName(project)!,id="App::ValueBody/body:common",leaf=id+"/node:body",view=calls.Open.Invoke(project,"owner","rename"),peer="";
        System.Text.Json.Nodes.JsonNode Cmd(string op,object o)=>Json(calls.Command.Invoke(view,op,Serialize(o)));
        System.Text.Json.Nodes.JsonNode B(string op,object o)=>Json(calls.Blueprint.Invoke(view,op,Serialize(o)));
        System.Text.Json.Nodes.JsonNode Read()=>B("read",new{id});
        void Rename(System.Text.Json.Nodes.JsonNode basis,string text)=>B("rename",new{id,basis=basis["basis"]!.ToString(),node="body",text});
        void Confirm(){var r=Cmd("review",new{ids=new[]{id},target="portable"})["review"]!;var result=Cmd("confirm",new{token=r["token"]!.ToString(),ids=new[]{id}});if(result["confirmation"]![0]!.ToString()!="confirmed")throw new InvalidOperationException("compiler Confirm refused: "+result["confirmation"]);}
        try{
         string nodeText=System.IO.File.ReadAllText(System.IO.Path.Combine(root,"body.node.json")),caller=System.IO.File.ReadAllText(System.IO.Path.Combine(root,"main.csbody"));var g=Read();string definition=g["nodes"]![0]!["definitionHash"]!.ToString(),profile=g["profile"]!.ToString();Check(g["nodes"]![0]!["displayName"]!.ToString()=="body"&&g["nodes"]![0]!["renameable"]!.GetValue<bool>(),"safe legacy fallback");
         foreach(string invalid in new[]{""," "," padded","line\nname",new string('x',257)})Refused(()=>Rename(g,invalid),"bounded display metadata");
         Rename(g,"한글 계산");Refused(()=>Rename(g,"같은 basis 재사용"),"storage revision changes on name-only edits");g=Read();Check(g["nodes"]![0]!["displayName"]!.ToString()=="한글 계산"&&g["nodes"]![0]!["definitionHash"]!.ToString()==definition&&g["nodes"]![0]!["sourceStatus"]!.ToString()=="available","name independent from intent and completion");
         Cmd("save",new{});calls.Close.Invoke(view);view=calls.Open.Invoke(project,"owner","rename");Refused(()=>Rename(g,"cold replay"),"cold basis carries no authority");g=Read();Check(g["nodes"]![0]!["displayName"]!.ToString()=="한글 계산"&&g["profile"]!.ToString()==profile,"cold metadata and legacy profile preserved");Confirm();
         Check(System.IO.File.ReadAllText(System.IO.Path.Combine(root,"body.node.json"))==nodeText&&System.IO.File.ReadAllText(System.IO.Path.Combine(root,"main.csbody"))==caller,"rename does not restamp body or rewrite caller");
         var run=Json(calls.Metadata.Invoke("run",Serialize(new{project,target="portable"})));Check(run["stdout"]!.ToString().Trim()=="5","stable actual execution");
         foreach(string changedId in new[]{id,leaf}){g=Read();peer=calls.Open.Invoke(project,"owner","rename");var u=Json(calls.Command.Invoke(peer,"select",Serialize(new{id=changedId})))["unit"]!;calls.Command.Invoke(peer,"edit",Serialize(new{text=u["text"]!.ToString()+" ",expectedRevision=u["revision"]!.GetValue<long>()}));Refused(()=>Rename(g,"CAS must refuse"),"peer raw graph/node CAS");calls.Close.Invoke(peer);peer="";Check(Read()["nodes"]![0]!["displayName"]!.ToString()=="한글 계산","CAS refuses atomically");}
         g=Read();B("intent",new{id,basis=g["basis"]!.ToString(),node="body",text="A changed behavioral contract"});g=Read();Check(g["nodes"]![0]!["sourceStatus"]!.ToString()=="stale","changed intent invalidates body");Rename(g,"미완성 유지");Check(Read()["nodes"]![0]!["sourceStatus"]!.ToString()=="stale","Rename cannot resurrect stale completion");Refused(Confirm,"name plus contract edit needs reapplication");
        }finally{if(peer.Length>0)calls.Close.Invoke(peer);calls.Close.Invoke(view);}
        Console.WriteLine("Rename metadata/CAS/cold/compiler/stale completion PASS");return 0;
        """","Rename metadata/CAS/cold/compiler/stale completion PASS");
    }
}
