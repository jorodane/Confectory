using Confectory.Core;
using System.Text.Json.Nodes;
namespace Confectory.Tests;
public sealed class RefAuthoringTests : TestCase
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


    public void test_ref_public_typed_call_profile_cas_cold_alias_and_ref_conversion_refusal()
    {
        const string feature="function App::Value (int n,out int count) -> int {provide App::Value with App::ValueBody;}";
        f.Add("App","function","Value",feature);f.Add("App","implementation","ValueBody","implementation App::ValueBody for App::Value (int n,out int count) -> int {blueprint common \"value.graph.json\";}");f.Body("App","value.graph.json",new JsonObject{["schema"]=1,["profile"]=FeatureBlueprint.LocalsProfile,["feature"]="App::Value",["contractHash"]=FeatureBlueprint.ContractHash(new Parser(feature,"<ref author>").ParseElement()),["entry"]="",["locals"]=new JsonArray(new JsonObject{["id"]="cell",["name"]="Shared cell",["type"]="int",["initial"]=new JsonObject{["constant"]=5}}),["nodes"]=new JsonArray(),["edges"]=new JsonArray(),["exits"]=new JsonObject()}.ToJsonString());
        f.Add("App","function","Alias","function App::Alias (ref int first,ref int second,out int sum) -> int {provide App::Alias with App::AliasBody;}");f.Add("App","implementation","AliasBody","implementation App::AliasBody for App::Alias (ref int a,ref int b,out int audit) -> int {body common \"alias.csbody\";}");f.Body("App","alias.csbody","a=10;b+=a;audit=a+b;return a+b+audit;");f.Main();
        f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import App::Value as Value (int,out int) -> int;body common \"main.csbody\";}");f.Body("App","main.csbody","int value=calls.Value.Invoke(1,out int count);Console.WriteLine(value+\",\"+count);return 0;");f.Sync();
        Consumer(""""
        void Check(bool value,string why){if(!value)throw new Exception(why);}
        System.Text.Json.Nodes.JsonNode Json(string text)=>System.Text.Json.Nodes.JsonNode.Parse(text)!;
        string Serialize(object value)=>System.Text.Json.JsonSerializer.Serialize(value);
        string Hash(string text)=>Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(text))).ToLowerInvariant();
        string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT")!,root=System.IO.Path.GetDirectoryName(project)!,impl="App::ValueBody",graphId=impl+"/body:common";
        string view=calls.Open.Invoke(project,"owner","ref-call"),peer="";
        System.Text.Json.Nodes.JsonNode Cmd(string op,object value)=>Json(calls.Command.Invoke(view,op,Serialize(value)));
        System.Text.Json.Nodes.JsonNode B(string op,object value)=>Json(calls.Blueprint.Invoke(view,op,Serialize(value)));
        System.Text.Json.Nodes.JsonNode Read()=>B("read",new{id=graphId});
        void Refused(Action action,string why){bool refused=false;try{action();}catch(ArgumentException){refused=true;}catch(InvalidOperationException){refused=true;}Check(refused,why);}
        void Run(string expected){var r=Json(calls.Metadata.Invoke("run",Serialize(new{project,target="portable"})));Check(r["exit"]!.GetValue<int>()==0&&r["stdout"]!.ToString().Trim()==expected,"actual aliases "+expected+": "+r);}
        var definition=new{ id="mutate",feature="App::Alias",intent="Call existing C# refs",control="next"};
        try{
         Run("0,0");string original=System.IO.File.ReadAllText(System.IO.Path.Combine(root,"alias.csbody"));var u=Cmd("select",new{id="App::AliasBody"})["unit"]!;string before=calls.Export.Invoke(calls.BorrowDraft.Invoke(view));Refused(()=>B("readConversion",new{id="App::AliasBody",target="common",revision=u["revision"]!.GetValue<long>(),hash=Hash(u["text"]!.ToString())}),"external ref conversion is explicitly unsupported until caller alias preservation exists");Check(before==calls.Export.Invoke(calls.BorrowDraft.Invoke(view))&&System.IO.File.ReadAllText(System.IO.Path.Combine(root,"alias.csbody"))==original,"ref conversion refusal preserves original C# and adds no drafts");
         var g=Read();Refused(()=>B("readCall",new{id=graphId,definition}),"ref call requires explicit new profile");B("upgradeProfile",new{id=graphId,basis=g["basis"]!.ToString(),profile="sync-acyclic-ref-nodes-v1"});var preview=B("readCall",new{id=graphId,definition});Check(preview["signature"]!["args"]![0]!["mode"]!.ToString()=="ref"&&!preview["sourceWritten"]!.GetValue<bool>(),"read-only typed ref contract preview");
         peer=calls.Open.Invoke(project,"owner","ref-call");u=Json(calls.Command.Invoke(peer,"select",Serialize(new{id=graphId})))["unit"]!;calls.Command.Invoke(peer,"edit",Serialize(new{text=u["text"]!.ToString()+" ",expectedRevision=u["revision"]!.GetValue<long>()}));Refused(()=>B("createCall",new{id=graphId,definition,basis=preview["basis"]!.ToString()}),"peer graph CAS after ref preview");calls.Close.Invoke(peer);peer="";preview=B("readCall",new{id=graphId,definition});B("createCall",new{id=graphId,definition,basis=preview["basis"]!.ToString()});g=Read();Check(g["nodes"]![0]!["arguments"]!.AsArray().Count==2&&g["nodes"]![0]!["arguments"]![0]!["mode"]!.ToString()=="ref","ref inputs are distinct from fresh out results");
         foreach(string name in new[]{"first","second"}){g=Read();B("argument",new{id=graphId,basis=g["basis"]!.ToString(),node="mutate",name,valueJson="{\"local\":\"cell\"}"});}
         foreach(string output in new[]{"return","count"}){g=Read();B("createOutput",new{id=graphId,basis=g["basis"]!.ToString(),node="publish_"+output,output});g=Read();B("argument",new{id=graphId,basis=g["basis"]!.ToString(),node="publish_"+output,name="value",valueJson=output=="return"?"{\"node\":\"mutate\",\"output\":\"return\"}":"{\"local\":\"cell\"}"});}
         g=Read();B("entry",new{id=graphId,basis=g["basis"]!.ToString(),node="mutate"});g=Read();B("route",new{id=graphId,basis=g["basis"]!.ToString(),node="mutate",port="next",to="publish_return"});g=Read();B("route",new{id=graphId,basis=g["basis"]!.ToString(),node="publish_return",port="next",to="publish_count"});g=Read();Cmd("save",new{});calls.Close.Invoke(view);view=calls.Open.Invoke(project,"owner","ref-call");Refused(()=>B("argument",new{id=graphId,basis=g["basis"]!.ToString(),node="mutate",name="first",valueJson="{\"constant\":5}"}),"cold ref edit authority is not replayed");g=Read();Check(g["nodes"]![0]!["arguments"]![0]!["valueJson"]!.ToString()==g["nodes"]![0]!["arguments"]![1]!["valueJson"]!.ToString(),"cold stores the exact same alias bindings");Run("0,0");
         var review=Cmd("review",new{ids=new[]{impl,graphId},target="portable"})["review"]!;Check(Cmd("confirm",new{token=review["token"]!.ToString(),ids=new[]{impl,graphId}})["confirmation"]![0]!.ToString()=="confirmed","typed ref import and graph compiler Confirm");Run("80,20");Check(System.IO.File.ReadAllText(System.IO.Path.Combine(root,"alias.csbody"))==original,"callee C# source remains byte exact");
        }finally{if(peer.Length>0)calls.Close.Invoke(peer);calls.Close.Invoke(view);}
        Console.WriteLine("Ref public typed call/profile/CAS/cold/alias/compiler/no-conversion/80-20 PASS");return 0;
        """","Ref public typed call/profile/CAS/cold/alias/compiler/no-conversion/80-20 PASS");
    }
}
