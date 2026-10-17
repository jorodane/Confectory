using Confectory.Core;
namespace Confectory.Tests;
public sealed class ExternalRefAuthoringTests : TestCase
{
    static string Host=>Path.Combine(Fixture.Repo,"targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll");
    public void test_public_external_ref_conversion_atomic_group_cas_origin_cold_and_real_aliases()
    {
        f.Add("App","function","Value","function App::Value (ref int left,ref int right,out int audit) -> int {provide App::Value with App::ValueBody;}");f.Add("App","implementation","ValueBody","implementation App::ValueBody for App::Value (ref int left,ref int right,out int audit) -> int {body common \"blueprints/value.csbody\";}");Directory.CreateDirectory(Path.Combine(f.Packs["App"].Root,"blueprints"));f.Body("App","blueprints/value.csbody","left=10;right+=left;audit=left+right;return left+right+audit;");
        f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import App::Value as Value (ref int,ref int,out int) -> int;body common \"main.csbody\";}");f.Body("App","main.csbody","int cell=5;int value=calls.Value.Invoke(ref cell,ref cell,out cell);Console.WriteLine(value+\",\"+cell);return 0;");f.Main();f.Sync();
        string sample=Path.Combine(f.Root,"conversion-consumer");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples/edit-workspace"),sample);
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
        File.WriteAllText(Path.Combine(sample,"main.csbody"),"""
        void Check(bool value,string why){if(!value)throw new Exception(why);}
        System.Text.Json.Nodes.JsonNode Json(string text)=>System.Text.Json.Nodes.JsonNode.Parse(text)!;
        string Serialize(object value)=>System.Text.Json.JsonSerializer.Serialize(value);
        string Hash(string value)=>Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(value))).ToLowerInvariant();
        string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT")!,root=System.IO.Path.GetDirectoryName(project)!,impl="App::ValueBody",graphId=impl+"/body:common";
        string view=calls.Open.Invoke(project,"owner","body-conversion");
        System.Text.Json.Nodes.JsonNode Cmd(string op,object value)=>Json(calls.Command.Invoke(view,op,Serialize(value)));
        System.Text.Json.Nodes.JsonNode Blueprint(string op,object value)=>Json(calls.Blueprint.Invoke(view,op,Serialize(value)));
        System.Text.Json.Nodes.JsonNode Current(string id)=>Cmd("select",new{id})["unit"]!;
        System.Text.Json.Nodes.JsonNode Prepare(){var unit=Current(impl);return Blueprint("readConversion",new{id=impl,target="common",revision=unit["revision"]!.GetValue<long>(),hash=Hash(unit["text"]!.ToString())});}
        void Refused(Action action,string why){bool refused=false;try{action();}catch(InvalidOperationException){refused=true;}catch(ArgumentException){refused=true;}Check(refused,why);}
        void Run(){var result=Json(calls.Metadata.Invoke("run",Serialize(new{project,target="portable"})));Check(result["exit"]!.GetValue<int>()==0&&result["stdout"]!.ToString().Trim()=="120,40","actual execution equivalence: "+result);}
        string path=System.IO.Path.Combine(root,"blueprints/value.csbody"),original=System.IO.File.ReadAllText(path),originalImpl=System.IO.File.ReadAllText(System.IO.Path.Combine(root,"ValueBody.celem"));
        try{
         Run();System.IO.File.WriteAllText(path,"/*"+new string('Ω',220000)+"*/\nleft=10;right+=left;audit=left+right;return left+right+audit;");var oversized=Prepare();Refused(()=>Blueprint("convertBody",new{id=impl,target="common",basis=oversized["basis"]!.ToString()}),"escaped node JSON must remain inside the editable per-file budget");Check(calls.Export.Invoke(calls.BorrowDraft.Invoke(view)).Contains("\"changes\":[]"),"per-file budget refusal adds no sources");System.IO.File.WriteAllText(path,original);var prepared=Prepare();Check(calls.Export.Invoke(calls.BorrowDraft.Invoke(view)).Contains("\"changes\":[]"),"reading conversion does not create drafts");
         System.IO.File.AppendAllText(path," ");Refused(()=>Blueprint("convertBody",new{id=impl,target="common",basis=prepared["basis"]!.ToString()}),"raw original body CAS");System.IO.File.WriteAllText(path,original);
         prepared=Prepare();var converted=Blueprint("convertBody",new{id=impl,target="common",basis=prepared["basis"]!.ToString()});var graph=Blueprint("read",new{id=graphId});Check(graph["nodes"]!.AsArray().Count==2&&graph["nodes"]![0]!["source"]!.ToString()==original,"one independent code body and structural return");
         string unchanged=calls.Export.Invoke(calls.BorrowDraft.Invoke(view));Refused(()=>Blueprint("argument",new{id=graphId,basis=graph["basis"]!.ToString(),node="body",name="left",valueJson="{\"constant\":5}"}),"whole body caller-storage bindings cannot be replaced by a constant");Check(calls.Export.Invoke(calls.BorrowDraft.Invoke(view))==unchanged,"invalid forwarding edit is atomic");graph=Blueprint("read",new{id=graphId});
         string[] group=System.Linq.Enumerable.ToArray(System.Linq.Enumerable.Select(graph["reviewIds"]!.AsArray(),id=>id!.ToString()));Check(group.Length==3&&Array.IndexOf(group,impl)>=0,"exact mandatory three source conversion group");
         foreach(string omitted in group){Refused(()=>Cmd("review",new{ids=Array.FindAll(group,id=>id!=omitted),target="portable"}),"partial review "+omitted);Check(calls.Direct.Invoke(calls.BorrowDraft.Invoke(view),Array.FindAll(group,id=>id!=omitted),"portable",calls.Changes.Invoke(calls.BorrowDraft.Invoke(view),Array.FindAll(group,id=>id!=omitted)))[0]!="confirmed","direct partial Confirm refused");}
         string draft=calls.BorrowDraft.Invoke(view),saved=calls.Export.Invoke(draft);var forged=Json(saved);foreach(var row in forged["changes"]!.AsArray())if(row!["id"]!.ToString()==graphId)row.AsObject().Remove("conversionOrigin");Refused(()=>calls.Restore.Invoke(draft,forged.ToJsonString()),"missing cold conversion origin refused");
         var damage=Json(saved);var graphRow=System.Linq.Enumerable.Single(damage["changes"]!.AsArray(),r=>r!["id"]!.ToString()==graphId)!;var gd=Json(graphRow["draft"]!.ToString());var hijack=gd["nodes"]![0]!.DeepClone();hijack["id"]="hijack";hijack.AsObject().Remove("implementationContext");hijack.AsObject().Remove("sourceIdentity");hijack["implementation"]="value.csbody";gd["nodes"]!.AsArray().Add(hijack);graphRow["draft"]=gd.ToJsonString();
         damage["changes"]!.AsArray().Add(new System.Text.Json.Nodes.JsonObject{["id"]=graphId+"/node:hijack",["kind"]="blueprint-node",["path"]="blueprints/value.csbody",["baseline"]=prepared["origin"]!["originalBodyHash"]!.DeepClone(),["original"]="",["draft"]=new System.Text.Json.Nodes.JsonObject{["schema"]=1,["node"]="hijack",["definitionHash"]=new string('0',64),["source"]="left=99;right=99;audit=99;return 99;"}.ToJsonString(),["revision"]=1L});
         Refused(()=>calls.Restore.Invoke(draft,damage.ToJsonString()),"forged restored node cannot target the original C# even in the graph directory");Check(calls.Export.Invoke(draft)==saved&&System.IO.File.ReadAllText(path)==original,"forged origin-path restore is atomic and preserves original source");
         var relocated=Json(saved);foreach(var row in relocated["changes"]!.AsArray())if(row!["id"]!.ToString()==graphId+"/node:body")row["baseline"]=prepared["origin"]!["originalBodyHash"]!.DeepClone();Refused(()=>calls.Restore.Invoke(draft,relocated.ToJsonString()),"independent converted node keeps its missing baseline");
         Cmd("save",new{});calls.Close.Invoke(view);view=calls.Open.Invoke(project,"owner","body-conversion");graph=Blueprint("read",new{id=graphId});Check(graph["reviewIds"]!.AsArray().Count==3&&graph["nodes"]![0]!["source"]!.ToString()==original,"cold conversion group and body preserved");
         var review=Cmd("review",new{ids=group,target="portable"})["review"]!;System.IO.File.AppendAllText(path," ");var refused=Cmd("confirm",new{token=review["token"]!.ToString(),ids=group});Check(refused["confirmation"]![0]!.ToString()!="confirmed","original changed after Review cannot Confirm");Check(System.IO.File.ReadAllText(System.IO.Path.Combine(root,"ValueBody.celem"))==originalImpl,"failed Confirm writes no declaration");System.IO.File.WriteAllText(path,original);
         review=Cmd("review",new{ids=group,target="portable"})["review"]!;Check(Cmd("confirm",new{token=review["token"]!.ToString(),ids=group})["confirmation"]![0]!.ToString()=="confirmed","whole conversion compiler Confirm");Run();Check(System.IO.File.ReadAllText(path)==original,"original C# retained after conversion");
         graph=Blueprint("read",new{id=graphId});Blueprint("route",new{id=graphId,basis=graph["basis"]!.ToString(),node="body",port="next",to=""});graph=Blueprint("read",new{id=graphId});Check(graph["diagnostics"]!["warnings"]!.AsArray().Count==1&&graph["diagnostics"]!["warnings"]![0]!["subject"]!.ToString()=="body/next","per-end warnings in public editor projection");
         Blueprint("createOutput",new{id=graphId,basis=graph["basis"]!.ToString(),node="other_return"});graph=Blueprint("read",new{id=graphId});Check(System.Linq.Enumerable.Any(graph["nodes"]!.AsArray(),n=>n!["id"]!.ToString()=="other_return"&&n["sourceStatus"]!.ToString()=="output-assignment"),"structural output creation without C# source or Task");
        }finally{calls.Close.Invoke(view);}
        Console.WriteLine("Body conversion context/group/CAS/cold/compiler/actual120-40 PASS");return 0;
        """);
        string? host=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST"),selected=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT");
        try{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",f.Project);var built=new Builder(project,"portable").Build();var run=Processes.Run(Strings(built,"run"),timeoutSeconds:300);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Body conversion context/group/CAS/cold/compiler/actual120-40 PASS"));}
        finally{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",selected);}
    }

}
