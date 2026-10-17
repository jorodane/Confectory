using Confectory.Core;
using System.Text.Json;
using System.Text.Json.Nodes;
namespace Confectory.Tests;
public sealed class PropertyAuthoringTests : TestCase
{
    void Consumer(string body,string marker)
    {
        string sample=Path.Combine(f.Root,"multi-output-consumer");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples/edit-workspace"),sample);
        foreach(string name in new[]{"file-stream","schema-editing","edit-workspace","save","change-set","pack-workspace","development-tools"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",name),Path.Combine(f.Root,"packs",name));
        string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/").Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack").Replace("element Main function","registry Confectory.PackWorkspace \"../packs/pack-workspace/pack.cpack\";dependency Confectory.PackWorkspace version \"0.1.0\";element Main function"));
        File.WriteAllText(project,File.ReadAllText(project).Replace("element Main function","registry Confectory.DevelopmentTools \"../packs/development-tools/pack.cpack\";dependency Confectory.DevelopmentTools version \"0.1.0\";element Main function"));
        string composition=Path.Combine(sample,"main.celem"),compositionText=File.ReadAllText(composition);File.WriteAllText(composition,compositionText.Insert(compositionText.LastIndexOf('}'),"provide Confectory.FileStream::BrowseDirectory with Confectory.FileStream::BrowseDirectoryBody;"));
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
        import Confectory.DevelopmentTools::OpenNode as OpenNode (string,string,string,string,string,string) -> string;
        import Confectory.DevelopmentTools::Snapshot as ToolSnapshot (string) -> string;
        import Confectory.DevelopmentTools::Invoke as ToolInvoke (string,string,string,string) -> string;
        import Confectory.DevelopmentTools::Close as CloseTool (string) -> void;
        import Confectory.SchemaEditing::Call as Metadata (string,string) -> string;
        body common "main.csbody";}
        """);
        File.WriteAllText(Path.Combine(sample,"main.csbody"),body);
        string? host=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST"),selected=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT");
        try{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",f.Project);var built=new Builder(project,"portable").Build();var run=Processes.Run(Strings(built,"run"),timeoutSeconds:420);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains(marker),run.Stdout+run.Stderr);}
        finally{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",selected);}
    }

    public void test_property_source_preview_schema_cas_cold_reader_group_and_explicit_rebind()
    {
        const string ns="Confectory.ObjectModel",feature="function App::Value (object target) -> int {provide App::Value with App::ValueBody;}";
        f.ExtraRegistry[ns]=Path.Combine(Fixture.Repo,"packs/object-model/pack.cpack");f.Packs["App"].Dependencies[ns]="0.1.0";
        f.Add("App","schema","Vitals","schema App::Vitals {field health single general int;field reads single general int;}");f.Add("App","object","Monster","object App::Monster {use schema App::Vitals;data health = 999;}");f.Add("App","function","Value",feature);f.Add("App","implementation","ValueBody","implementation App::ValueBody for App::Value (object target) -> int {blueprint common \"value.graph.json\";}");
        var signature=FeatureBlueprint.SignatureDocument(new(new(){new("object","target")},"int"));
        var graph=new JsonObject{["schema"]=1,["profile"]=FeatureBlueprint.PropertyProfile,["feature"]="App::Value",["contractHash"]=FeatureBlueprint.ContractHash(new Parser(feature,"<property-author>").ParseElement()),["entry"]="body",["nodes"]=new JsonArray(new JsonObject{["id"]="body",["kind"]="code",["control"]="next",["intent"]="Preserved original body",["signature"]=signature,["arguments"]=new JsonObject{["target"]=new JsonObject{["input"]="target"}},["implementation"]="body.node.json"}),["edges"]=new JsonArray(new JsonObject{["from"]="body",["port"]="next",["to"]="exit:done"}),["exits"]=new JsonObject{["done"]=new JsonObject{["node"]="body"}}};
        var defs=FeatureBlueprint.Execute(new(){["operation"]="featureBlueprintNodes",["featureSource"]=feature,["graph"]=graph.DeepClone()});Equal("node-definitions",Text(defs,"state"));f.Body("App","value.graph.json",graph.ToJsonString());f.Body("App","body.node.json",new JsonObject{["schema"]=1,["node"]="body",["definitionHash"]=defs["nodes"]![0]!["definitionHash"]!.DeepClone(),["source"]="return -1;"}.ToJsonString());
        f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import App::Value as Value (object) -> int;import Confectory.ObjectModel::Create as Create (string,string[],object[]) -> object;body common \"main.csbody\";}");f.Sync();var descriptor=RuntimeObjectContracts.Describe(f.Registry(),"App::Monster");string Field(string name)=>descriptor["fields"]!.AsArray().Single(f=>f!["name"]!.ToString()==name)!["id"]!.ToString();f.Body("App","main.csbody","object target=calls.Create.Invoke("+JsonSerializer.Serialize(descriptor.ToJsonString())+",new[]{"+JsonSerializer.Serialize(Field("health"))+","+JsonSerializer.Serialize(Field("reads"))+"},new object[]{23,7});Console.WriteLine(calls.Value.Invoke(target));return 0;");
        Consumer(""""
        void Check(bool value,string why){if(!value)throw new Exception(why);}
        System.Text.Json.Nodes.JsonNode J(string text)=>System.Text.Json.Nodes.JsonNode.Parse(text)!;string S(object value)=>System.Text.Json.JsonSerializer.Serialize(value);
        string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT")!,root=System.IO.Path.GetDirectoryName(project)!,graph="App::ValueBody/body:common",impl="App::ValueBody",schema="App::Vitals",view=calls.Open.Invoke(project,"owner","property"),peer="";
        System.Text.Json.Nodes.JsonNode C(string op,object value)=>J(calls.Command.Invoke(view,op,S(value)));System.Text.Json.Nodes.JsonNode B(string op,object value)=>J(calls.Blueprint.Invoke(view,op,S(value)));System.Text.Json.Nodes.JsonNode Read()=>B("read",new{id=graph});
        void Refused(Action action,string why){bool refused=false;try{action();}catch(ArgumentException){refused=true;}catch(InvalidOperationException){refused=true;}catch(UnauthorizedAccessException){refused=true;}Check(refused,why);}
        void Run(string expected){var result=J(calls.Metadata.Invoke("run",S(new{project,target="portable"})));Check(result["exit"]!.GetValue<int>()==0&&result["stdout"]!.ToString().Trim()==expected,"actual property output "+result);}
        System.Text.Json.Nodes.JsonNode Preview(string field="health",bool rebind=false)=>B("readProperty",new{id=graph,owner="App::Monster",field,node="health",targetJson="""{"input":"target"}""",rebind});
        string original=System.IO.File.ReadAllText(System.IO.Path.Combine(root,"body.node.json"));
        try{
         Run("-1");var catalog=B("propertyCatalog",new{id=graph});Check(System.Linq.Enumerable.Any(catalog["rows"]!.AsArray(),r=>r!["id"]!.ToString()=="App::Monster"),"published owner catalog");var preview=Preview();Check(preview["readTiming"]!.ToString()=="execution-node"&&preview["runtimeValuesRead"]!.GetValue<bool>()==false,"preview never reads a live instance");Check(Read()["nodes"]!.AsArray().Count==1,"preview has no source mutation");
         peer=calls.Open.Invoke(project,"owner","property");var unit=J(calls.Command.Invoke(peer,"select",S(new{id=schema})))["unit"]!;calls.Command.Invoke(peer,"edit",S(new{text=unit["text"]!.ToString()+" ",expectedRevision=unit["revision"]!.GetValue<long>()}));Refused(()=>B("createProperty",new{id=graph,basis=preview["basis"]!.ToString()}),"field declaration raw revision participates in preview CAS");calls.Close.Invoke(peer);peer="";
         preview=Preview();B("createProperty",new{id=graph,basis=preview["basis"]!.ToString()});var g=Read();Check(g["nodes"]!.AsArray().Count==2&&g["nodes"]![1]!["sourceId"] is null,"property is structural and has no C# Task source");B("entry",new{id=graph,basis=g["basis"]!.ToString(),node="health"});g=Read();B("route",new{id=graph,basis=g["basis"]!.ToString(),node="health",port="next",to="exit:done"});g=Read();B("exit",new{id=graph,basis=g["basis"]!.ToString(),name="done",valueJson="""{"node":"health"}"""});Check(Read()["diagnostics"]!["state"]!.ToString()=="source-ready","typed current field and actual receiver binding");Run("-1");
         string leaf=graph+"/node:body",capability=calls.OpenNode.Invoke(project,"fixture","App","owner","property",leaf);try{var scope=J(calls.ToolSnapshot.Invoke(capability));Check(scope["rights"]!.AsArray().Count==4&&scope["nodeScope"]!["observations"]![schema] is not null&&scope["nodeScope"]!["observations"]!["App::Monster"] is not null,"property supporting declarations observed without broadening four Worker rights");var tool=J(calls.ToolInvoke.Invoke(capability,"read","workspace_read",S(new{projectId="fixture",id=leaf})));Refused(()=>calls.ToolInvoke.Invoke(capability,"wrong","workspace_read",S(new{projectId="fixture",id=schema})),"code node capability cannot read schema sources");peer=calls.Open.Invoke(project,"owner","property");unit=J(calls.Command.Invoke(peer,"select",S(new{id=schema})))["unit"]!;calls.Command.Invoke(peer,"edit",S(new{text=unit["text"]!.ToString()+" ",expectedRevision=unit["revision"]!.GetValue<long>()}));calls.Close.Invoke(peer);peer="";Refused(()=>calls.ToolInvoke.Invoke(capability,"stale","workspace_stage",S(new{projectId="fixture",id=leaf,text=tool["text"]!.ToString(),expectedRevision=tool["revision"]!.GetValue<long>(),expectedHash=tool["textHash"]!.ToString()})),"changed property declaration invalidates code-node stage capability");}finally{calls.CloseTool.Invoke(capability);}
         var partial=C("review",new{ids=new[]{graph},target="portable"})["review"]!;Check(C("confirm",new{token=partial["token"]!.ToString(),ids=new[]{graph}})["confirmation"]![0]!.ToString()=="invalid","compiler Confirm refuses property without its typed reader import");C("save",new{});calls.Close.Invoke(view);view=calls.Open.Invoke(project,"owner","property");Refused(()=>B("createProperty",new{id=graph,basis=preview["basis"]!.ToString()}),"property preview cannot replay after cold restore");g=Read();Check(g["nodes"]![1]!["property"]!["readTiming"]!.ToString()=="execution-node","cold property contract retained");
         var ids=new[]{graph,impl,schema};var review=C("review",new{ids,target="portable"})["review"]!;Check(C("confirm",new{token=review["token"]!.ToString(),ids})["confirmation"]![0]!.ToString()=="confirmed","graph/import/schema compiler Confirm");Run("23");
         peer=calls.Open.Invoke(project,"owner","property");unit=J(calls.Command.Invoke(peer,"select",S(new{id=schema})))["unit"]!;calls.Command.Invoke(peer,"edit",S(new{text=unit["text"]!.ToString().Replace("health single general int","health single general long"),expectedRevision=unit["revision"]!.GetValue<long>()}));calls.Close.Invoke(peer);peer="";g=Read();Check(g["nodes"]![1]!["propertyError"]!.ToString()=="PROPERTY_FIELD_STALE"&&g["diagnostics"]!["state"]!.ToString()=="invalid","field drift stays visible without a fake successful read");partial=C("review",new{ids=new[]{schema},target="portable"})["review"]!;Check(C("confirm",new{token=partial["token"]!.ToString(),ids=new[]{schema}})["confirmation"]![0]!.ToString()=="invalid","schema-only compiler Confirm refuses stale property contract");
         preview=Preview("reads",true);Check(preview["node"]!["signature"]!["return"]!.ToString()=="int","explicit compatible rebind preview");B("createProperty",new{id=graph,basis=preview["basis"]!.ToString()});g=Read();Check(g["nodes"]![1]!["field"]!.ToString()=="reads"&&g["diagnostics"]!["state"]!.ToString()=="source-ready","explicit field rebind retains node and receiver binding");review=C("review",new{ids=new[]{graph,schema},target="portable"})["review"]!;Check(C("confirm",new{token=review["token"]!.ToString(),ids=new[]{graph,schema}})["confirmation"]![0]!.ToString()=="confirmed","rebound property/schema Confirm");Run("7");Check(original==System.IO.File.ReadAllText(System.IO.Path.Combine(root,"body.node.json")),"original C# record preserved");
        }finally{if(peer.Length>0)calls.Close.Invoke(peer);calls.Close.Invoke(view);}
        Console.WriteLine("Property preview/schema CAS/cold/reader import/rebind/actual 23 then 7 PASS");return 0;
        """","Property preview/schema CAS/cold/reader import/rebind/actual 23 then 7 PASS");
    }
    public void test_unpublished_object_owner_stays_editable_without_becoming_a_property_contract()
    {
        f.Add("App","function","OwnValue","function App::OwnValue (int n) -> int {}");f.Sync();
        Consumer("""
        void Check(bool value,string why){if(!value)throw new Exception(why);}
        System.Text.Json.Nodes.JsonNode J(string text)=>System.Text.Json.Nodes.JsonNode.Parse(text)!;string S(object value)=>System.Text.Json.JsonSerializer.Serialize(value);
        string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT")!,view=calls.Open.Invoke(project,"owner","new-object");
        System.Text.Json.Nodes.JsonNode C(string op,object value)=>J(calls.Command.Invoke(view,op,S(value)));System.Text.Json.Nodes.JsonNode B(string op,object value)=>J(calls.Blueprint.Invoke(view,op,S(value)));
        try{
         C("create",new{kind="object",id="App::Fresh"});var unit=C("select",new{id="App::Fresh"})["unit"]!;string hash=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(unit["text"]!.ToString()))).ToLowerInvariant();var preview=B("readImplementation",new{id="App::Fresh",function="App::OwnValue",implementation="App::FreshBody",revision=unit["revision"]!.GetValue<long>(),hash});var created=B("createImplementation",new{id="App::Fresh",function="App::OwnValue",implementation="App::FreshBody",basis=preview["basis"]!.ToString()});string graph=created["id"]!.ToString();var g=B("read",new{id=graph});Check(System.Linq.Enumerable.Any(g["sources"]!.AsArray(),row=>row!["id"]!.ToString()=="App::Fresh"),"new owner participates in existing source group");
         B("createNode",new{id=graph,basis=g["basis"]!.ToString(),node="spare",definition=new{intent="Independent new code",control="next",signature=new{args=Array.Empty<object>(),@return="void"}}});g=B("read",new{id=graph});Check(System.Linq.Enumerable.Any(g["nodes"]!.AsArray(),row=>row!["id"]!.ToString()=="spare"),"code node under unpublished object remains editable");
         var call=B("readCall",new{id=graph,definition=new{id="reference",feature="Api::Value",intent="Existing typed function",control="next"}});B("createCall",new{id=graph,basis=call["basis"]!.ToString()});g=B("read",new{id=graph});Check(System.Linq.Enumerable.Any(g["nodes"]!.AsArray(),row=>row!["id"]!.ToString()=="reference"),"typed call under unpublished object remains editable");Check(g["profile"]!.ToString()=="sync-acyclic-v1","ordinary legacy graph is not upgraded implicitly");
        }finally{calls.Close.Invoke(view);}
        Console.WriteLine("Unpublished object owner/code/call grouped source remains editable PASS");return 0;
        ""","Unpublished object owner/code/call grouped source remains editable PASS");
    }

}
