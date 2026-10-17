using Confectory.Core;
using System.Text.Json.Nodes;

namespace Confectory.Tests;

public sealed class BlueprintConversionTests : TestCase
{
    static string Host => Path.Combine(Fixture.Repo,"targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll");
    static JsonNode Metadata(JsonObject query)
    {
        var run=Processes.Run(new[]{Processes.DotNet(),Host},query.ToJsonString(),timeoutSeconds:60);
        if(run.ExitCode!=0)throw new Exception(run.Stderr);var result=JsonNode.Parse(run.Stdout)!;
        if(!result["ok"]!.GetValue<bool>())throw new InvalidOperationException(result.ToJsonString());return result["result"]!;
    }
    public void test_whole_body_context_preserves_calls_scope_this_recursion_names_targets_and_crlf()
    {
        f.Add("Api","function","Double","function Api::Double (int n) -> int {}");
        f.Add("Provider","implementation","DoubleBody","implementation Provider::DoubleBody for Api::Double (int n) -> int {body common \"double.csbody\";}");f.Body("Provider","double.csbody","return n * 2;");
        f.Add("Provider","implementation","TripleBody","implementation Provider::TripleBody for Api::Double (int n) -> int {body common \"triple.csbody\";}");f.Body("Provider","triple.csbody","return n * 3;");
        f.Add("Provider","object","DoubleScope","object Provider::DoubleScope {provide Api::Double with Provider::DoubleBody;}");
        f.Main("provide Api::Value with Provider::ValueBody;provide Api::Double with Provider::TripleBody;");
        // Different implementation argument name, original member calls/this/Invoke, and a literal CRLF.
        string body="if (input < 0) return this.Invoke(-input);\r\nIImports same = this.calls;\r\nstring literal = @\"a\r\nb\";\r\nint __fg_original = 0;\r\nstring File([global::System.Runtime.CompilerServices.CallerFilePath] string path = \"\") => global::System.IO.Path.GetFileName(path);\r\nreturn same.Double.Invoke(input) + __fg_original + (literal.Contains(\"\\r\\n\") && File() == \"값.csbody\" ? 0 : 100);";
        f.Body("Provider","값.csbody",body);f.Body("Provider","value_linux.csbody","return input + 30;");
        f.Add("Provider","implementation","ParentBody","implementation Provider::ParentBody for Api::Value (int input) -> int {import Api::Double as Double (int) -> int in Provider::DoubleScope;body common \"값.csbody\";body linux \"value_linux.csbody\";}");
        f.Add("Provider","implementation","ValueBody","implementation Provider::ValueBody for Api::Value (int input) -> int extends Provider::ParentBody { // preserve comment\n description \"existing declaration\"; }");f.Sync();
        f.Body("App","main.csbody","Console.WriteLine(calls.Value.Invoke(-2));return 0;");Output(Build(),"4");Output(Build("linux"),"28");
        string root=f.Packs["Provider"].Root,manifest=Path.Combine(f.Packs["Provider"].Root,"pack.cpack");
        // Conversion is owned by a ProjectPack, so use the same fixture with Provider as its project.
        string project=Path.Combine(root,"conversion.cpack");string source=File.ReadAllText(manifest).Replace("pack Provider", "project Provider");int close=source.LastIndexOf('}');
        source=source[..close]+"registry Api \""+Path.GetRelativePath(root,Path.Combine(f.Packs["Api"].Root,"pack.cpack")).Replace('\\','/')+"\";registry Confectory.Build.DotNet \""+Path.GetRelativePath(root,Path.Combine(f.Root,"target/pack.cpack")).Replace('\\','/')+"\";target portable Confectory.Build.DotNet::Portable;target linux Confectory.Build.DotNet::Linux;"+source[close..];File.WriteAllText(project,source);
        string implementation=Path.Combine(root,"ValueBody.celem"),originalImplementation=File.ReadAllText(implementation);byte[] original=File.ReadAllBytes(Path.Combine(root,"값.csbody"));
        var query=new JsonObject{["operation"]="blueprintConversion",["project"]=project,["id"]="Provider::ValueBody",["text"]=originalImplementation,["target"]="common",["graphPath"]="lift.graph.json",["nodePath"]="lift.node.json"};var prepared=Metadata(query);
        Equal(body+"\n",prepared["node"]!["source"]!.ToString());Equal(1,prepared["graph"]!["nodes"]!.AsArray().Count(n=>n!["kind"]!.ToString()=="code"));True(prepared["implementation"]!.ToString().Contains("// preserve comment"));
        File.WriteAllText(implementation,prepared["implementation"]!.ToString());File.WriteAllText(Path.Combine(root,"lift.graph.json"),prepared["graph"]!.ToJsonString());File.WriteAllText(Path.Combine(root,"lift.node.json"),prepared["node"]!.ToJsonString());
        Output(Build(),"4");Output(Build("linux"),"28");var probe=new Builder(f.Project,"portable").CheckBlueprintNode("Provider::ValueBody","common","body");True(probe["compiled"]!.GetValue<bool>());True(!probe["executed"]!.GetValue<bool>());
        Sequence(original,File.ReadAllBytes(Path.Combine(root,"값.csbody")));
        // Adding an ordinary call import remains editable, but requires a new independent body proof.
        string alias=FeatureBlueprint.ImportAlias("Api::Double");
        File.WriteAllText(implementation,File.ReadAllText(implementation).Replace("description ","import Api::Double as "+alias+" (int) -> int in Provider::DoubleScope; description "));
        Error("BLUEPRINT_NOT_READY",()=>Build());
        var registry=f.Registry();var effective=registry.Effective("Provider::ValueBody");
        var definitions=FeatureBlueprint.Execute(new JsonObject{["operation"]="featureBlueprintNodes",["featureSource"]=File.ReadAllText(Path.Combine(f.Packs["Api"].Root,"Value.celem")),["featureContracts"]=new JsonObject{["Api::Double"]=File.ReadAllText(Path.Combine(f.Packs["Api"].Root,"Double.celem"))},["implementationContext"]=FeatureBlueprint.ImplementationContext(effective),["graph"]=prepared["graph"]!.DeepClone()});
        Equal("node-definitions",definitions["state"]!.ToString());prepared["node"]!["definitionHash"]=definitions["nodes"]![0]!["definitionHash"]!.DeepClone();File.WriteAllText(Path.Combine(root,"lift.node.json"),prepared["node"]!.ToJsonString());Output(Build(),"4");
        // Explicitly changing a scoped import stales the context instead of silently changing providers.
        string parent=Path.Combine(root,"ParentBody.celem");File.WriteAllText(parent,File.ReadAllText(parent).Replace(" in Provider::DoubleScope",""));Error("BLUEPRINT_NOT_READY",()=>Build());
    }

    public void test_public_body_conversion_atomic_group_cas_origin_cold_and_compiler_confirm()
    {
        f.Add("App","function","Value","function App::Value (int n) -> int {provide App::Value with App::ValueBody;}");f.Add("App","implementation","ValueBody","implementation App::ValueBody for App::Value (int n) -> int {body common \"blueprints/value.csbody\";}");Directory.CreateDirectory(Path.Combine(f.Packs["App"].Root,"blueprints"));f.Body("App","blueprints/value.csbody","return n + 3;");
        f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import App::Value as Value (int) -> int;body common \"main.csbody\";}");f.Body("App","main.csbody","Console.WriteLine(calls.Value.Invoke(2));return 0;");f.Main();f.Sync();
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
        void Run(){var result=Json(calls.Metadata.Invoke("run",Serialize(new{project,target="portable"})));Check(result["exit"]!.GetValue<int>()==0&&result["stdout"]!.ToString().Trim()=="5","actual execution equivalence: "+result);}
        string path=System.IO.Path.Combine(root,"blueprints/value.csbody"),original=System.IO.File.ReadAllText(path),originalImpl=System.IO.File.ReadAllText(System.IO.Path.Combine(root,"ValueBody.celem"));
        try{
         Run();System.IO.File.WriteAllText(path,"/*"+new string('Ω',220000)+"*/\nreturn n + 3;");var oversized=Prepare();Refused(()=>Blueprint("convertBody",new{id=impl,target="common",basis=oversized["basis"]!.ToString()}),"escaped node JSON must remain inside the editable per-file budget");Check(calls.Export.Invoke(calls.BorrowDraft.Invoke(view)).Contains("\"changes\":[]"),"per-file budget refusal adds no sources");System.IO.File.WriteAllText(path,original);var prepared=Prepare();Check(calls.Export.Invoke(calls.BorrowDraft.Invoke(view)).Contains("\"changes\":[]"),"reading conversion does not create drafts");
         System.IO.File.AppendAllText(path," ");Refused(()=>Blueprint("convertBody",new{id=impl,target="common",basis=prepared["basis"]!.ToString()}),"raw original body CAS");System.IO.File.WriteAllText(path,original);
         prepared=Prepare();var converted=Blueprint("convertBody",new{id=impl,target="common",basis=prepared["basis"]!.ToString()});var graph=Blueprint("read",new{id=graphId});Check(graph["nodes"]!.AsArray().Count==2&&graph["nodes"]![0]!["source"]!.ToString()==original,"one independent code body and structural return");
         string[] group=System.Linq.Enumerable.ToArray(System.Linq.Enumerable.Select(graph["reviewIds"]!.AsArray(),id=>id!.ToString()));Check(group.Length==3&&Array.IndexOf(group,impl)>=0,"exact mandatory three source conversion group");
         foreach(string omitted in group){Refused(()=>Cmd("review",new{ids=Array.FindAll(group,id=>id!=omitted),target="portable"}),"partial review "+omitted);Check(calls.Direct.Invoke(calls.BorrowDraft.Invoke(view),Array.FindAll(group,id=>id!=omitted),"portable",calls.Changes.Invoke(calls.BorrowDraft.Invoke(view),Array.FindAll(group,id=>id!=omitted)))[0]!="confirmed","direct partial Confirm refused");}
         string draft=calls.BorrowDraft.Invoke(view),saved=calls.Export.Invoke(draft);var forged=Json(saved);foreach(var row in forged["changes"]!.AsArray())if(row!["id"]!.ToString()==graphId)row.AsObject().Remove("conversionOrigin");Refused(()=>calls.Restore.Invoke(draft,forged.ToJsonString()),"missing cold conversion origin refused");
         var damage=Json(saved);var graphRow=System.Linq.Enumerable.Single(damage["changes"]!.AsArray(),r=>r!["id"]!.ToString()==graphId)!;var gd=Json(graphRow["draft"]!.ToString());var hijack=gd["nodes"]![0]!.DeepClone();hijack["id"]="hijack";hijack.AsObject().Remove("implementationContext");hijack.AsObject().Remove("sourceIdentity");hijack["implementation"]="value.csbody";gd["nodes"]!.AsArray().Add(hijack);graphRow["draft"]=gd.ToJsonString();
         damage["changes"]!.AsArray().Add(new System.Text.Json.Nodes.JsonObject{["id"]=graphId+"/node:hijack",["kind"]="blueprint-node",["path"]="blueprints/value.csbody",["baseline"]=prepared["origin"]!["originalBodyHash"]!.DeepClone(),["original"]="",["draft"]=new System.Text.Json.Nodes.JsonObject{["schema"]=1,["node"]="hijack",["definitionHash"]=new string('0',64),["source"]="return n + 99;"}.ToJsonString(),["revision"]=1L});
         Refused(()=>calls.Restore.Invoke(draft,damage.ToJsonString()),"forged restored node cannot target the original C# even in the graph directory");Check(calls.Export.Invoke(draft)==saved&&System.IO.File.ReadAllText(path)==original,"forged origin-path restore is atomic and preserves original source");
         var relocated=Json(saved);foreach(var row in relocated["changes"]!.AsArray())if(row!["id"]!.ToString()==graphId+"/node:body")row["baseline"]=prepared["origin"]!["originalBodyHash"]!.DeepClone();Refused(()=>calls.Restore.Invoke(draft,relocated.ToJsonString()),"independent converted node keeps its missing baseline");
         Cmd("save",new{});calls.Close.Invoke(view);view=calls.Open.Invoke(project,"owner","body-conversion");graph=Blueprint("read",new{id=graphId});Check(graph["reviewIds"]!.AsArray().Count==3&&graph["nodes"]![0]!["source"]!.ToString()==original,"cold conversion group and body preserved");
         var review=Cmd("review",new{ids=group,target="portable"})["review"]!;System.IO.File.AppendAllText(path," ");var refused=Cmd("confirm",new{token=review["token"]!.ToString(),ids=group});Check(refused["confirmation"]![0]!.ToString()!="confirmed","original changed after Review cannot Confirm");Check(System.IO.File.ReadAllText(System.IO.Path.Combine(root,"ValueBody.celem"))==originalImpl,"failed Confirm writes no declaration");System.IO.File.WriteAllText(path,original);
         review=Cmd("review",new{ids=group,target="portable"})["review"]!;Check(Cmd("confirm",new{token=review["token"]!.ToString(),ids=group})["confirmation"]![0]!.ToString()=="confirmed","whole conversion compiler Confirm");Run();Check(System.IO.File.ReadAllText(path)==original,"original C# retained after conversion");
         graph=Blueprint("read",new{id=graphId});Blueprint("route",new{id=graphId,basis=graph["basis"]!.ToString(),node="body",port="next",to=""});graph=Blueprint("read",new{id=graphId});Check(graph["diagnostics"]!["warnings"]!.AsArray().Count==1&&graph["diagnostics"]!["warnings"]![0]!["subject"]!.ToString()=="body/next","per-end warnings in public editor projection");
         Blueprint("createOutput",new{id=graphId,basis=graph["basis"]!.ToString(),node="other_return"});graph=Blueprint("read",new{id=graphId});Check(System.Linq.Enumerable.Any(graph["nodes"]!.AsArray(),n=>n!["id"]!.ToString()=="other_return"&&n["sourceStatus"]!.ToString()=="output-assignment"),"structural output creation without C# source or Task");
        }finally{calls.Close.Invoke(view);}
        Console.WriteLine("Body conversion context/group/CAS/cold/compiler/actual5 PASS");return 0;
        """);
        string? host=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST"),selected=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT");
        try{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",f.Project);var built=new Builder(project,"portable").Build();var run=Processes.Run(Strings(built,"run"),timeoutSeconds:300);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Body conversion context/group/CAS/cold/compiler/actual5 PASS"));}
        finally{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",selected);}
    }

    public void test_whole_void_body_conversion_runs_once_and_probe_does_not_execute()
    {
        f.Add("App","function","Notify","function App::Notify () -> void {provide App::Notify with App::NotifyBody;}");
        f.Add("App","implementation","NotifyBody","implementation App::NotifyBody for App::Notify () -> void {body common \"notify.csbody\";}");f.Body("App","notify.csbody","Console.WriteLine(\"void\");return;");f.Main();
        f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import App::Notify as Notify () -> void;body common \"main.csbody\";}");f.Body("App","main.csbody","calls.Notify.Invoke();return 0;");f.Sync();Output(Build(),"void");
        string root=f.Packs["App"].Root,implementation=Path.Combine(root,"NotifyBody.celem");byte[] original=File.ReadAllBytes(Path.Combine(root,"notify.csbody"));
        var prepared=Metadata(new JsonObject{["operation"]="blueprintConversion",["project"]=f.Project,["id"]="App::NotifyBody",["text"]=File.ReadAllText(implementation),["target"]="common",["graphPath"]="notify.graph.json",["nodePath"]="notify.node.json"});
        Equal(1,prepared["graph"]!["nodes"]!.AsArray().Count);File.WriteAllText(implementation,prepared["implementation"]!.ToString());File.WriteAllText(Path.Combine(root,"notify.graph.json"),prepared["graph"]!.ToJsonString());File.WriteAllText(Path.Combine(root,"notify.node.json"),prepared["node"]!.ToJsonString());Output(Build(),"void");
        var probe=new Builder(f.Project,"portable").CheckBlueprintNode("App::NotifyBody","common","body");True(probe["compiled"]!.GetValue<bool>());True(!probe["executed"]!.GetValue<bool>());Sequence(original,File.ReadAllBytes(Path.Combine(root,"notify.csbody")));
    }
    public void test_whole_out_body_conversion_preserves_original_member_scoped_import_and_other_target()
    {
        f.Add("Api","function","Value","function Api::Value (int n,out int count) -> int {}");f.Add("Api","function","Double","function Api::Double (int n) -> int {}");
        f.Add("Provider","implementation","DoubleBody","implementation Provider::DoubleBody for Api::Double (int n) -> int {body common \"double.csbody\";}");f.Body("Provider","double.csbody","return n*2;");f.Add("Provider","implementation","WrongBody","implementation Provider::WrongBody for Api::Double (int n) -> int {body common \"wrong.csbody\";}");f.Body("Provider","wrong.csbody","return n*9;");f.Add("Provider","object","Selected","object Provider::Selected {provide Api::Double with Provider::DoubleBody;}");f.Main("provide Api::Value with Provider::ValueBody;provide Api::Double with Provider::WrongBody;");
        string body="if (original < 0) return this.Invoke(-original,out copied);\r\ncopied=original*10;\r\nIImports same=this.calls;\r\nstring File([global::System.Runtime.CompilerServices.CallerFilePath] string path=\"\")=>global::System.IO.Path.GetFileName(path);\r\nreturn same.Double.Invoke(original)+(File()==\"값.csbody\"?0:100);";
        f.Add("Provider","implementation","ValueBody","implementation Provider::ValueBody for Api::Value (int original,out int copied) -> int {import Api::Double as Double (int) -> int in Provider::Selected;body common \"값.csbody\";body linux \"other.csbody\";}");f.Body("Provider","값.csbody",body);f.Body("Provider","other.csbody","copied=original;return original+30;");f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import Api::Value as Value (int,out int) -> int;body common \"main.csbody\";}");f.Body("App","main.csbody","int value=calls.Value.Invoke(-2,out int count);Console.WriteLine(value+\",\"+count);return 0;");f.Sync();Output(Build(),"4,20");Output(Build("linux"),"28,-2");
        string root=f.Packs["Provider"].Root,project=Path.Combine(root,"conversion.cpack"),source=File.ReadAllText(Path.Combine(root,"pack.cpack")).Replace("pack Provider","project Provider");int close=source.LastIndexOf('}');source=source[..close]+"registry Api "+System.Text.Json.JsonSerializer.Serialize(Path.GetRelativePath(root,Path.Combine(f.Packs["Api"].Root,"pack.cpack")).Replace('\\','/'))+";registry Confectory.Build.DotNet "+System.Text.Json.JsonSerializer.Serialize(Path.GetRelativePath(root,Path.Combine(f.Root,"target/pack.cpack")).Replace('\\','/'))+";target portable Confectory.Build.DotNet::Portable;"+source[close..];File.WriteAllText(project,source);
        string path=Path.Combine(root,"ValueBody.celem");byte[] original=File.ReadAllBytes(Path.Combine(root,"값.csbody")),other=File.ReadAllBytes(Path.Combine(root,"other.csbody"));var prepared=Metadata(new JsonObject{["operation"]="blueprintConversion",["project"]=project,["id"]="Provider::ValueBody",["text"]=File.ReadAllText(path),["target"]="common",["graphPath"]="out.graph.json",["nodePath"]="out.node.json"});Equal(FeatureBlueprint.ExternalRefsProfile,prepared["graph"]!["profile"]!.ToString());Equal(2,prepared["graph"]!["nodes"]!.AsArray().Count);Equal(body+"\n",prepared["node"]!["source"]!.ToString());
        File.WriteAllText(path,prepared["implementation"]!.ToString());File.WriteAllText(Path.Combine(root,"out.graph.json"),prepared["graph"]!.ToJsonString());File.WriteAllText(Path.Combine(root,"out.node.json"),prepared["node"]!.ToJsonString());Output(Build(),"4,20");Output(Build("linux"),"28,-2");var proof=new Builder(f.Project,"portable").CheckBlueprintNode("Provider::ValueBody","common","body");True(proof["compiled"]!.GetValue<bool>()&&!proof["executed"]!.GetValue<bool>());Sequence(original,File.ReadAllBytes(Path.Combine(root,"값.csbody")));Sequence(other,File.ReadAllBytes(Path.Combine(root,"other.csbody")));
    }

}
