using Confectory.Core;
using System.Text.Json.Nodes;
namespace Confectory.Tests;
public sealed partial class LocalAuthoringTests : TestCase
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

    public void test_local_public_profile_cas_exact_initializers_cold_and_graph_only_compiler_confirm()
    {
        const string feature="function App::Value (long n,out long count) -> long {provide App::Value with App::ValueBody;}";
        f.Add("App","function","Value",feature);f.Add("App","implementation","ValueBody","implementation App::ValueBody for App::Value (long n,out long count) -> long {blueprint common \"value.graph.json\";}");
        f.Body("App","value.graph.json",new JsonObject{["schema"]=1,["profile"]=FeatureBlueprint.MultiOutputProfile,["feature"]="App::Value",["contractHash"]=FeatureBlueprint.ContractHash(new Parser(feature,"<local author>").ParseElement()),["entry"]="",["nodes"]=new JsonArray(),["edges"]=new JsonArray(),["exits"]=new JsonObject()}.ToJsonString());f.Main();
        f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import App::Value as Value (long,out long) -> long;body common \"main.csbody\";}");f.Body("App","main.csbody","long value=calls.Value.Invoke(2,out long count);Console.WriteLine(value+\",\"+count);return 0;");f.Sync();
        Consumer(""""
        void Check(bool value,string why){if(!value)throw new Exception(why);}
        System.Text.Json.Nodes.JsonNode Json(string text)=>System.Text.Json.Nodes.JsonNode.Parse(text)!;
        string Serialize(object value)=>System.Text.Json.JsonSerializer.Serialize(value);
        string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT")!,root=System.IO.Path.GetDirectoryName(project)!,graphId="App::ValueBody/body:common";
        string view=calls.Open.Invoke(project,"owner","locals"),peer="";
        System.Text.Json.Nodes.JsonNode Cmd(string op,object value)=>Json(calls.Command.Invoke(view,op,Serialize(value)));
        System.Text.Json.Nodes.JsonNode B(string op,object value)=>Json(calls.Blueprint.Invoke(view,op,Serialize(value)));
        System.Text.Json.Nodes.JsonNode Read()=>B("read",new{id=graphId});
        void Refused(Action action,string why){bool refused=false;try{action();}catch(ArgumentException){refused=true;}catch(InvalidOperationException){refused=true;}Check(refused,why);}
        void Run(string expected){var r=Json(calls.Metadata.Invoke("run",Serialize(new{project,target="portable"})));Check(r["exit"]!.GetValue<int>()==0&&r["stdout"]!.ToString().Trim()==expected,"actual local values "+expected+": "+r);}
        void Confirm(){var r=Cmd("review",new{ids=new[]{graphId},target="portable"})["review"]!;Check(Cmd("confirm",new{token=r["token"]!.ToString(),ids=new[]{graphId}})["confirmation"]![0]!.ToString()=="confirmed","graph-only compiler Confirm");}
        try{
         Run("0,0");var g=Read();Refused(()=>B("createLocal",new{id=graphId,basis=g["basis"]!.ToString(),local="counter",name="Count",type="long",initialJson="5"}),"explicit profile gate");Check(Read()["profile"]!.ToString()=="sync-acyclic-implicit-out-v1","read does not migrate");B("upgradeProfile",new{id=graphId,basis=g["basis"]!.ToString(),profile="sync-acyclic-locals-v1"});
         g=Read();peer=calls.Open.Invoke(project,"owner","locals");var u=Json(calls.Command.Invoke(peer,"select",Serialize(new{id=graphId})))["unit"]!;calls.Command.Invoke(peer,"edit",Serialize(new{text=u["text"]!.ToString()+" ",expectedRevision=u["revision"]!.GetValue<long>()}));Refused(()=>B("createLocal",new{id=graphId,basis=g["basis"]!.ToString(),local="counter",name="Count",type="long",initialJson="5"}),"raw peer graph CAS");calls.Close.Invoke(peer);peer="";Check(Read()["locals"]!.AsArray().Count==0,"refused CAS adds no local");
         g=Read();B("createLocal",new{id=graphId,basis=g["basis"]!.ToString(),local="counter",name="Count",type="long",initialJson="5"});g=Read();B("createLocal",new{id=graphId,basis=g["basis"]!.ToString(),local="exact",name="Exact integer",type="long",initialJson="9223372036854775807"});g=Read();Check(g["locals"]![1]!["initialJson"]!.ToString()=="9223372036854775807","large integer stays an exact JSON string");
         Refused(()=>B("createLocal",new{id=graphId,basis=g["basis"]!.ToString(),local="bad",name="Bad",type="int",initialJson="9223372036854775807"}),"invalid initializer refuses atomically");g=Read();B("createSet",new{id=graphId,basis=g["basis"]!.ToString(),local="counter",node="set"});g=Read();B("argument",new{id=graphId,basis=g["basis"]!.ToString(),node="set",name="value",valueJson="{\"input\":\"n\"}"});
         foreach(string output in new[]{"return","count"}){g=Read();B("createOutput",new{id=graphId,basis=g["basis"]!.ToString(),node="publish_"+output,output});g=Read();B("argument",new{id=graphId,basis=g["basis"]!.ToString(),node="publish_"+output,name="value",valueJson="{\"local\":\"counter\"}"});}
         g=Read();B("entry",new{id=graphId,basis=g["basis"]!.ToString(),node="set"});g=Read();B("route",new{id=graphId,basis=g["basis"]!.ToString(),node="set",port="next",to="publish_return"});g=Read();B("route",new{id=graphId,basis=g["basis"]!.ToString(),node="publish_return",port="next",to="publish_count"});g=Read();Check(g["nodes"]!.AsArray().Count==3&&g["diagnostics"]!["warnings"]!.AsArray().Count==0,"structural set and exports have no C# source");Check(g["nodes"]![0]!["sourceStatus"]!.ToString()=="local-assignment"&&g["nodes"]![0]!["sourceId"] is null,"set does not masquerade as C# or Task");Refused(()=>B("removeLocal",new{id=graphId,basis=g["basis"]!.ToString(),local="counter"}),"referenced storage cannot be removed");
         Cmd("save",new{});calls.Close.Invoke(view);view=calls.Open.Invoke(project,"owner","locals");Refused(()=>B("updateLocal",new{id=graphId,basis=g["basis"]!.ToString(),local="counter",name="Restored",type="long",initialJson="7"}),"cold basis authority is not replayed");g=Read();Check(g["locals"]!.AsArray().Count==2&&g["nodes"]!.AsArray().Count==3,"cold keeps graph declarations and set bindings");Confirm();Run("2,2");
         g=Read();B("entry",new{id=graphId,basis=g["basis"]!.ToString(),node="publish_return"});g=Read();B("removeLocal",new{id=graphId,basis=g["basis"]!.ToString(),local="exact"});Confirm();Run("5,5");Check(System.IO.File.ReadAllText(System.IO.Path.Combine(root,"main.csbody")).Contains("out long count"),"original caller C# unchanged");
        }finally{if(peer.Length>0)calls.Close.Invoke(peer);calls.Close.Invoke(view);}
        Console.WriteLine("Local public profile/CAS/exact initializer/cold/compiler/2-2-5-5 PASS");return 0;
        """","Local public profile/CAS/exact initializer/cold/compiler/2-2-5-5 PASS");
    }
}
