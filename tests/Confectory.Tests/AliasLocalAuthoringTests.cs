using Confectory.Core;
using System.Text.Json.Nodes;
namespace Confectory.Tests;
public sealed class AliasLocalAuthoringTests : TestCase
{
    void Consumer(string body,string marker)
    {
        string sample=Path.Combine(f.Root,"multi-output-consumer");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples/edit-workspace"),sample);
        foreach(string name in new[]{"file-stream","schema-editing","edit-workspace","save","change-set","pack-workspace"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",name),Path.Combine(f.Root,"packs",name));
        string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/").Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack").Replace("element Main function","registry Confectory.PackWorkspace \"../packs/pack-workspace/pack.cpack\";dependency Confectory.PackWorkspace version \"0.1.0\";element Main function"));
        File.WriteAllText(Path.Combine(sample,"main_body.celem"),"""
        implementation Example.EditWorkspace::MainBody for Example.EditWorkspace::Main () -> int {
        import Confectory.PackWorkspace::Open as Open (string,string,string) -> string;
        import Confectory.PackWorkspace::Command as Command (string,string,string) -> string;
        import Confectory.PackWorkspace::Blueprint as Blueprint (string,string,string) -> string;
        import Confectory.PackWorkspace::Close as Close (string) -> void;
        import Confectory.PackWorkspace::BorrowDraft as BorrowDraft (string) -> string;
        import Confectory.EditWorkspace::Changes as Changes (string,string[]) -> string[];
        import Confectory.EditWorkspace::Export as Export (string) -> string;
        import Confectory.EditWorkspace::Restore as Restore (string,string) -> void;
        import Confectory.ChangeSet::ConfirmReviewed as Direct (string,string[],string,string[]) -> string[];
        import Confectory.SchemaEditing::Call as Metadata (string,string) -> string;
        body common "main.csbody";}
        """);
        File.WriteAllText(Path.Combine(sample,"main.csbody"),body);
        string? host=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST"),selected=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT");
        try{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",f.Project);var built=new Builder(project,"portable").Build();var run=Processes.Run(Strings(built,"run"),timeoutSeconds:420);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains(marker),run.Stdout+run.Stderr);}
        finally{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",selected);}
    }

    public void test_alias_public_source_cas_cold_delete_producer_and_graph_only_compiler_confirm()
    {
        const string feature="function App::Value (long n,out long snapshot) -> long {provide App::Value with App::ValueBody;}";
        f.Add("App","function","Value",feature);f.Add("App","implementation","ValueBody","implementation App::ValueBody for App::Value (long n,out long snapshot) -> long {blueprint common \"value.graph.json\";}");
        JsonObject Code(string id,JsonNode value)=>new(){["id"]=id,["kind"]="code",["control"]="next",["intent"]="Compute "+id,["signature"]=new JsonObject{["args"]=new JsonArray(new JsonObject{["name"]="value",["type"]="long"}),["return"]="long"},["arguments"]=new JsonObject{["value"]=value},["implementation"]=id+".node.json"};
        var graph=new JsonObject{["schema"]=1,["profile"]=FeatureBlueprint.ExternalRefsProfile,["feature"]="App::Value",["contractHash"]=FeatureBlueprint.ContractHash(new Parser(feature,"<author alias>").ParseElement()),["entry"]="body",["nodes"]=new JsonArray(Code("body",new JsonObject{["input"]="n"}),Code("capture",new JsonObject{["node"]="body"}),Code("extra",new JsonObject{["input"]="n"}),new JsonObject{["id"]="publish",["kind"]="export",["control"]="next",["intent"]="Export snapshot",["output"]="snapshot",["signature"]=new JsonObject{["args"]=new JsonArray(new JsonObject{["name"]="value",["type"]="long"}),["return"]="void"},["arguments"]=new JsonObject{["value"]=new JsonObject{["node"]="capture"}}}),["edges"]=new JsonArray(new JsonObject{["from"]="body",["port"]="next",["to"]="capture"},new JsonObject{["from"]="capture",["port"]="next",["to"]="publish"},new JsonObject{["from"]="publish",["port"]="next",["to"]="exit:done"}),["exits"]=new JsonObject{["done"]=new JsonObject{["node"]="body"}}};
        var defs=FeatureBlueprint.Execute(new JsonObject{["operation"]="featureBlueprintNodes",["featureSource"]=feature,["graph"]=graph.DeepClone()});foreach(var id in new[]{"body","capture","extra"}){var row=defs["nodes"]!.AsArray().Single(n=>n!["id"]!.ToString()==id)!;f.Body("App",id+".node.json",new JsonObject{["schema"]=1,["node"]=id,["definitionHash"]=row["definitionHash"]!.DeepClone(),["source"]=id=="body"?"return value+3;":"return value;"}.ToJsonString());}f.Body("App","value.graph.json",graph.ToJsonString());f.Main();f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import App::Value as Value (long,out long) -> long;body common \"main.csbody\";}");f.Body("App","main.csbody","long value=calls.Value.Invoke(2,out long snapshot);Console.WriteLine(value+\",\"+snapshot);return 0;");f.Sync();
        Consumer(""""
        void Check(bool value,string why){if(!value)throw new Exception(why);}
        System.Text.Json.Nodes.JsonNode Json(string text)=>System.Text.Json.Nodes.JsonNode.Parse(text)!;string Serialize(object value)=>System.Text.Json.JsonSerializer.Serialize(value);
        string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT")!,root=System.IO.Path.GetDirectoryName(project)!,graphId="App::ValueBody/body:common",view=calls.Open.Invoke(project,"owner","alias-locals"),peer="";
        System.Text.Json.Nodes.JsonNode Cmd(string op,object value)=>Json(calls.Command.Invoke(view,op,Serialize(value)));System.Text.Json.Nodes.JsonNode B(string op,object value)=>Json(calls.Blueprint.Invoke(view,op,Serialize(value)));System.Text.Json.Nodes.JsonNode Read()=>B("read",new{id=graphId});
        void Refused(Action action,string why){bool refused=false;try{action();}catch(ArgumentException){refused=true;}catch(InvalidOperationException){refused=true;}Check(refused,why);}
        void Run(string expected){var result=Json(calls.Metadata.Invoke("run",Serialize(new{project,target="portable"})));Check(result["exit"]!.GetValue<int>()==0&&result["stdout"]!.ToString().Trim()==expected,"actual alias output "+expected+": "+result);}
        var before=new System.Collections.Generic.Dictionary<string,byte[]>();foreach(string name in new[]{"body.node.json","capture.node.json","extra.node.json","main.csbody"})before[name]=System.IO.File.ReadAllBytes(System.IO.Path.Combine(root,name));
        try{
         Run("5,5");var g=Read();Refused(()=>B("createLocal",new{id=graphId,basis=g["basis"]!.ToString(),local="borrowed",name="Borrowed",type="long",sourceJson="{\"node\":\"body\",\"output\":\"return\"}"}),"explicit alias profile gate");B("upgradeProfile",new{id=graphId,basis=g["basis"]!.ToString(),profile="sync-acyclic-alias-locals-v1"});
         g=Read();peer=calls.Open.Invoke(project,"owner","alias-locals");var u=Json(calls.Command.Invoke(peer,"select",Serialize(new{id=graphId})))["unit"]!;calls.Command.Invoke(peer,"edit",Serialize(new{text=u["text"]!.ToString()+" ",expectedRevision=u["revision"]!.GetValue<long>()}));Refused(()=>B("createLocal",new{id=graphId,basis=g["basis"]!.ToString(),local="borrowed",name="Borrowed",type="long",sourceJson="{\"node\":\"body\"}"}),"raw peer graph CAS");calls.Close.Invoke(peer);peer="";Check(Read()["locals"]!.AsArray().Count==0,"refused CAS adds no alias");
         g=Read();B("createLocal",new{id=graphId,basis=g["basis"]!.ToString(),local="borrowed",name="Borrowed",type="long",sourceJson="{\"node\":\"body\",\"output\":\"return\"}"});g=Read();Check(g["locals"]![0]!["sourceJson"]!.ToString()=="{\"node\":\"body\",\"output\":\"return\"}"&&g["locals"]![0]!["initialJson"] is null,"alias source preserved, no copied initializer");string saved=calls.Export.Invoke(calls.BorrowDraft.Invoke(view));Refused(()=>B("updateLocal",new{id=graphId,basis=g["basis"]!.ToString(),local="borrowed",name="Borrowed",type="long",initialJson="7"}),"storage kind cannot change implicitly");Check(calls.Export.Invoke(calls.BorrowDraft.Invoke(view))==saved,"kind refusal is atomic");
         g=Read();B("createLocal",new{id=graphId,basis=g["basis"]!.ToString(),local="unused",name="Unused",type="long",sourceJson="{\"node\":\"extra\"}"});g=Read();saved=calls.Export.Invoke(calls.BorrowDraft.Invoke(view));Refused(()=>B("removeNode",new{id=graphId,basis=g["basis"]!.ToString(),node="extra"}),"even an unused alias protects its producer");Check(calls.Export.Invoke(calls.BorrowDraft.Invoke(view))==saved,"producer removal refusal is atomic");g=Read();B("removeLocal",new{id=graphId,basis=g["basis"]!.ToString(),local="unused"});g=Read();B("removeNode",new{id=graphId,basis=g["basis"]!.ToString(),node="extra"});
         g=Read();B("createSet",new{id=graphId,basis=g["basis"]!.ToString(),local="borrowed",node="set"});g=Read();B("argument",new{id=graphId,basis=g["basis"]!.ToString(),node="set",name="value",valueJson="{\"constant\":32}"});g=Read();B("route",new{id=graphId,basis=g["basis"]!.ToString(),node="capture",port="next",to="set"});g=Read();B("route",new{id=graphId,basis=g["basis"]!.ToString(),node="set",port="next",to="publish"});g=Read();Check(g["diagnostics"]!["state"]!.ToString()=="source-ready","alias target available after producer");Refused(()=>B("removeLocal",new{id=graphId,basis=g["basis"]!.ToString(),local="borrowed"}),"set target is a live alias use");Run("5,5");
         Cmd("save",new{});calls.Close.Invoke(view);view=calls.Open.Invoke(project,"owner","alias-locals");Refused(()=>B("updateLocal",new{id=graphId,basis=g["basis"]!.ToString(),local="borrowed",name="Restored",type="long",sourceJson="{\"input\":\"n\"}"}),"cold basis cannot mutate restored alias");g=Read();Check(g["profile"]!.ToString()=="sync-acyclic-alias-locals-v1"&&g["locals"]![0]!["sourceJson"]!.ToString().Contains("body"),"cold alias retains actual producer source");
         var contract=B("readContract",new{id=graphId});Check(contract["profile"]!.ToString()=="sync-acyclic-alias-locals-v1","explicit contract preview never downgrades aliases");g=Read();var review=Cmd("review",new{ids=new[]{graphId},target="portable"})["review"]!;Check(Cmd("confirm",new{token=review["token"]!.ToString(),ids=new[]{graphId}})["confirmation"]![0]!.ToString()=="confirmed","graph-only compiler Confirm");Run("32,5");foreach(var item in before)Check(System.Linq.Enumerable.SequenceEqual(item.Value,System.IO.File.ReadAllBytes(System.IO.Path.Combine(root,item.Key))),"original C# record/caller preserved "+item.Key);
        }finally{if(peer.Length>0)calls.Close.Invoke(peer);calls.Close.Invoke(view);}
        Console.WriteLine("Alias public source/CAS/cold/producer guard/graph compiler/32-5 PASS");return 0;
        """","Alias public source/CAS/cold/producer guard/graph compiler/32-5 PASS");
    }
}
