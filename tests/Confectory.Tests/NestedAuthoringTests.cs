using Confectory.Core;
using System.Text.Json.Nodes;
namespace Confectory.Tests;
public sealed class NestedAuthoringTests : TestCase
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

    public void test_private_nested_owned_sources_cold_peer_cas_and_atomic_compiler_confirm()
    {
        const string source="function App::Value (int n) -> int {provide App::Value with App::ValueBody;}";
        JsonObject Sig()=>new(){["args"]=new JsonArray(new JsonObject{["type"]="int",["name"]="value"}),["return"]="int"};
        var child=new JsonObject{["schema"]=1,["profile"]=FeatureBlueprint.NestedProfile,["entry"]="body",["nodes"]=new JsonArray(new JsonObject{["id"]="body",["kind"]="code",["control"]="next",["intent"]="Private body",["signature"]=Sig(),["arguments"]=new JsonObject{["value"]=new JsonObject{["input"]="value"}},["implementation"]="private-body.node.json"}),["edges"]=new JsonArray(new JsonObject{["from"]="body",["port"]="next",["to"]="exit:done"}),["exits"]=new JsonObject{["done"]=new JsonObject{["node"]="body"}}};
        var graph=new JsonObject{["schema"]=1,["profile"]=FeatureBlueprint.NestedProfile,["feature"]="App::Value",["contractHash"]=FeatureBlueprint.ContractHash(new Parser(source,"<nested-author>").ParseElement()),["entry"]="private",["nodes"]=new JsonArray(new JsonObject{["id"]="private",["kind"]="graph",["control"]="next",["intent"]="Private child",["signature"]=Sig(),["arguments"]=new JsonObject{["value"]=new JsonObject{["input"]="n"}},["graph"]=child}),["edges"]=new JsonArray(new JsonObject{["from"]="private",["port"]="next",["to"]="exit:done"}),["exits"]=new JsonObject{["done"]=new JsonObject{["node"]="private"}}};
        var defs=FeatureBlueprint.Execute(new(){["operation"]="featureBlueprintNodes",["featureSource"]=source,["graph"]=graph.DeepClone(),["bodyTarget"]="common",["implementationContext"]=new JsonObject{["implementation"]="App::ValueBody"}});Equal("node-definitions",Text(defs,"state"));
        f.Add("App","function","Value",source);f.Add("App","implementation","ValueBody","implementation App::ValueBody for App::Value (int n) -> int {blueprint common \"value.graph.json\";}");
        f.Body("App","value.graph.json",graph.ToJsonString());f.Body("App","private-body.node.json",new JsonObject{["schema"]=1,["node"]="body",["definitionHash"]=defs["nestedNodes"]![0]!["definitionHash"]!.DeepClone(),["source"]="return value+3;"}.ToJsonString());
        f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import App::Value as Value (int) -> int;body common \"main.csbody\";}");f.Body("App","main.csbody","Console.WriteLine(calls.Value.Invoke(2));return 0;");f.Sync();
        Consumer(""""
        void Check(bool value,string why){if(!value)throw new Exception(why);}
        System.Text.Json.Nodes.JsonNode J(string text)=>System.Text.Json.Nodes.JsonNode.Parse(text)!;string S(object value)=>System.Text.Json.JsonSerializer.Serialize(value);
        string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT")!,root=System.IO.Path.GetDirectoryName(project)!,graph="App::ValueBody/body:common",child=graph+"/graph:private",leaf=graph+"/node:private/node:body",view=calls.Open.Invoke(project,"owner","nested"),peer="";
        System.Text.Json.Nodes.JsonNode B(string op,object value)=>J(calls.Blueprint.Invoke(view,op,S(value)));System.Text.Json.Nodes.JsonNode C(string op,object value)=>J(calls.Command.Invoke(view,op,S(value)));System.Text.Json.Nodes.JsonNode Read(string id)=>B("read",new{id});
        void Refused(Action action,string why){bool refused=false;try{action();}catch(ArgumentException){refused=true;}catch(InvalidOperationException){refused=true;}catch(UnauthorizedAccessException){refused=true;}Check(refused,why);}
        void Run(string expected){var result=J(calls.Metadata.Invoke("run",S(new{project,target="portable"})));Check(result["exit"]!.GetValue<int>()==0&&result["stdout"]!.ToString().Trim()==expected,"runtime "+result);}
        try{
         Run("5");var parent=Read(graph);var g=Read(child);Check(g["privatePath"]!.ToString()=="private"&&g["nodes"]![0]!["sourceId"]!.ToString()==leaf,"qualified private source");Check(g["diagnostics"]!["state"]!.ToString()=="source-ready","current child sources");
         string capability=calls.OpenNode.Invoke(project,"fixture","App","owner","nested",leaf);try{var scope=J(calls.ToolSnapshot.Invoke(capability));Check(scope["rights"]!.AsArray().Count==4&&scope["nodeScope"]!["definition"]!["ownerPath"]!.ToString()=="App::ValueBody/body:common/private","nested capability exact owner path and four rights");var tool=J(calls.ToolInvoke.Invoke(capability,"read","workspace_read",S(new{projectId="fixture",id=leaf})));Refused(()=>calls.ToolInvoke.Invoke(capability,"wrong","workspace_read",S(new{projectId="fixture",id=graph})),"private capability cannot read parent graph");B("intent",new{id=graph,basis=parent["basis"]!.ToString(),node="private",text="Private child reviewed"});Refused(()=>calls.ToolInvoke.Invoke(capability,"stale","workspace_stage",S(new{projectId="fixture",id=leaf,text=tool["text"]!.ToString(),expectedRevision=tool["revision"]!.GetValue<long>(),expectedHash=tool["textHash"]!.ToString()})),"changed ancestor invalidates private stage capability");}finally{calls.CloseTool.Invoke(capability);}parent=Read(graph);g=Read(child);
         B("source",new{id=child,basis=g["basis"]!.ToString(),node="body",text="return value+7;"});Refused(()=>B("intent",new{id=graph,basis=parent["basis"]!.ToString(),node="private",text="stale"}),"child edit invalidates parent basis");Run("5");
         g=Read(child);peer=calls.Open.Invoke(project,"owner","nested");var u=J(calls.Command.Invoke(peer,"select",S(new{id=leaf})))["unit"]!;calls.Command.Invoke(peer,"edit",S(new{text=u["text"]!.ToString()+" ",expectedRevision=u["revision"]!.GetValue<long>()}));Refused(()=>B("source",new{id=child,basis=g["basis"]!.ToString(),node="body",text="return 999;"}),"peer leaf revision protects private edit");calls.Close.Invoke(peer);peer="";
         g=Read(child);B("createNode",new{id=child,basis=g["basis"]!.ToString(),node="spare",definition=new{intent="Disconnected private body",control="next",signature=new{args=Array.Empty<object>(),@return="void"}}});g=Read(child);string spare=graph+"/node:private/node:spare";Check(System.Linq.Enumerable.Any(g["nodes"]!.AsArray(),n=>n!["sourceId"]?.ToString()==spare),"new leaf is discovered under full owner path");
         B("source",new{id=child,basis=g["basis"]!.ToString(),node="spare",text="int x=1;_ = x;"});g=Read(child);string path=System.Linq.Enumerable.Single(g["sources"]!.AsArray(),n=>n!["id"]!.ToString()==spare)!["path"]!.ToString();Check(!System.IO.File.Exists(System.IO.Path.Combine(root,path)),"creation is draft only");
         Refused(()=>C("review",new{ids=new[]{spare},target="portable"}),"new private leaf requires changed root graph");Refused(()=>C("review",new{ids=new[]{graph},target="portable"}),"new private leaf cannot be omitted");
         string saved=calls.Export.Invoke(calls.BorrowDraft.Invoke(view));Refused(()=>B("removeNode",new{id=graph,basis=Read(graph)["basis"]!.ToString(),node="private"}),"private ownership removal cannot discard descendants");Check(saved==calls.Export.Invoke(calls.BorrowDraft.Invoke(view)),"removal refusal atomic");
         C("save",new{});calls.Close.Invoke(view);view=calls.Open.Invoke(project,"owner","nested");Refused(()=>B("source",new{id=child,basis=g["basis"]!.ToString(),node="body",text="return 0;"}),"cold tokens do not replay");g=Read(child);Check(System.Linq.Enumerable.Single(g["nodes"]!.AsArray(),n=>n!["id"]!.ToString()=="body")!["source"]!.ToString()=="return value+7;","cold private source retained");
         var ids=new[]{graph,leaf,spare};var review=C("review",new{ids,target="portable"})["review"]!;Check(C("confirm",new{token=review["token"]!.ToString(),ids})["confirmation"]![0]!.ToString()=="confirmed","nested atomic compiler Confirm");Run("9");Check(System.IO.File.Exists(System.IO.Path.Combine(root,path)),"reviewed leaf published");
        }finally{if(peer.Length>0)calls.Close.Invoke(peer);calls.Close.Invoke(view);}
        Console.WriteLine("Nested source ownership/CAS/cold/atomic compiler/actual 9 PASS");return 0;
        """","Nested source ownership/CAS/cold/atomic compiler/actual 9 PASS");
    }
}
