using Confectory.Core;
namespace Confectory.Tests;

public sealed class MultiOutputAuthoringTests : TestCase
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
    public void test_contract_append_out_is_explicit_cas_cold_body_preserving_and_compiler_confirmed()
    {
        f.Add("App","function","Value","function App::Value (int n) -> int {provide App::Value with App::ValueBody;}");f.Add("App","implementation","ValueBody","implementation App::ValueBody for App::Value (int original) -> int {body common \"blueprints/value.csbody\";}");Directory.CreateDirectory(Path.Combine(f.Packs["App"].Root,"blueprints"));f.Body("App","blueprints/value.csbody","return original + 3;");f.Main();
        f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import App::Value as Value (int) -> int;body common \"main.csbody\";}");f.Body("App","main.csbody","Console.WriteLine(calls.Value.Invoke(2));return 0;");f.Sync();
        Consumer("""
        void Check(bool value,string why){if(!value)throw new Exception(why);}
        System.Text.Json.Nodes.JsonNode Json(string text)=>System.Text.Json.Nodes.JsonNode.Parse(text)!;
        string Serialize(object value)=>System.Text.Json.JsonSerializer.Serialize(value);
        string Hash(string value)=>Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(value))).ToLowerInvariant();
        string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT")!,root=System.IO.Path.GetDirectoryName(project)!,impl="App::ValueBody",graphId=impl+"/body:common";
        string view=calls.Open.Invoke(project,"owner","multi-contract"),peer="";
        System.Text.Json.Nodes.JsonNode Cmd(string op,object value)=>Json(calls.Command.Invoke(view,op,Serialize(value)));
        System.Text.Json.Nodes.JsonNode Blueprint(string op,object value)=>Json(calls.Blueprint.Invoke(view,op,Serialize(value)));
        System.Text.Json.Nodes.JsonNode Current(string id)=>Cmd("select",new{id})["unit"]!;
        void Edit(string id,string text){var u=Current(id);Cmd("edit",new{text,expectedRevision=u["revision"]!.GetValue<long>()});}
        void Refused(Action action,string why){bool refused=false;try{action();}catch(InvalidOperationException){refused=true;}catch(ArgumentException){refused=true;}Check(refused,why);}
        void Run(string expected){var r=Json(calls.Metadata.Invoke("run",Serialize(new{project,target="portable"})));Check(r["exit"]!.GetValue<int>()==0&&r["stdout"]!.ToString().Trim()==expected,"actual execution "+expected+": "+r);}
        void Confirm(string[] ids){var r=Cmd("review",new{ids,target="portable"})["review"]!;Check(Cmd("confirm",new{token=r["token"]!.ToString(),ids=System.Linq.Enumerable.ToArray(System.Linq.Enumerable.Select(r["units"]!.AsArray(),u=>u!["id"]!.ToString()))})["confirmation"]![0]!.ToString()=="confirmed","compiler Confirm "+r);}
        string original=System.IO.File.ReadAllText(System.IO.Path.Combine(root,"blueprints/value.csbody"));
        try{
         Run("5");var unit=Current(impl);var preview=Blueprint("readConversion",new{id=impl,target="common",revision=unit["revision"]!.GetValue<long>(),hash=Hash(unit["text"]!.ToString())});Blueprint("convertBody",new{id=impl,target="common",basis=preview["basis"]!.ToString()});var graph=Blueprint("read",new{id=graphId});Confirm(System.Linq.Enumerable.ToArray(System.Linq.Enumerable.Select(graph["reviewIds"]!.AsArray(),x=>x!.ToString())));
         var function=Current("App::Value");Cmd("declaration",new{id="App::Value",expectedRevision=function["revision"]!.GetValue<long>(),expectedHash=Hash(function["text"]!.ToString()),edit=new{action="signature",value=new{args=new[]{new{type="int",name="n",mode=(string?)null},new{type="int",name="copied",mode=(string?)"out"}},@return="int"}}});
         Edit(impl,Current(impl)["text"]!.ToString().Replace("(int original)","(int original, out int different)"));Edit("App::MainBody",Current("App::MainBody")["text"]!.ToString().Replace("(int) -> int","(int, out int) -> int"));Edit("App::MainBody/body:common","int value=calls.Value.Invoke(2,out int copy);Console.WriteLine(value+\",\"+copy);return 0;");
         Refused(()=>Blueprint("read",new{id=graphId}),"ordinary read refuses stale contract and never migrates");string savedBefore=calls.Export.Invoke(calls.BorrowDraft.Invoke(view));var contract=Blueprint("readContract",new{id=graphId});Check(contract["profile"]!.ToString()=="sync-acyclic-implicit-out-v1"&&!contract["sourceWritten"]!.GetValue<bool>()&&calls.Export.Invoke(calls.BorrowDraft.Invoke(view))==savedBefore,"contract preview reads without source mutation");
         peer=calls.Open.Invoke(project,"owner","multi-contract");var peerUnit=Json(calls.Command.Invoke(peer,"select",Serialize(new{id="App::Value"})))["unit"]!;calls.Command.Invoke(peer,"edit",Serialize(new{text=peerUnit["text"]!.ToString()+" ",expectedRevision=peerUnit["revision"]!.GetValue<long>()}));Refused(()=>Blueprint("rebindContract",new{id=graphId,basis=contract["basis"]!.ToString()}),"peer raw contract CAS");calls.Close.Invoke(peer);peer="";
         contract=Blueprint("readContract",new{id=graphId});Cmd("save",new{});calls.Close.Invoke(view);view=calls.Open.Invoke(project,"owner","multi-contract");Refused(()=>Blueprint("rebindContract",new{id=graphId,basis=contract["basis"]!.ToString()}),"cold restore does not replay contract preview authority");
         contract=Blueprint("readContract",new{id=graphId});Blueprint("rebindContract",new{id=graphId,basis=contract["basis"]!.ToString()});graph=Blueprint("read",new{id=graphId});Check(graph["nodes"]![0]!["source"]!.ToString()==original&&graph["nodes"]![0]!["signature"]!["args"]!.AsArray().Count==1&&graph["nodes"]![0]!["sourceStatus"]!.ToString()=="stale","old public body and exact source preserved; changed interface requires fresh proof");
         Blueprint("source",new{id=graphId,basis=graph["basis"]!.ToString(),node="body",text=original});graph=Blueprint("read",new{id=graphId});Check(graph["diagnostics"]!["warnings"]![0]!["missingOutputs"]![0]!["name"]!.ToString()=="copied","new named output is warning only at existing end");Confirm(new[]{"App::Value",impl,graphId,graphId+"/node:body","App::MainBody","App::MainBody/body:common"});Run("5,0");
         graph=Blueprint("read",new{id=graphId});Blueprint("createOutput",new{id=graphId,basis=graph["basis"]!.ToString(),node="copy_return",output="copied"});graph=Blueprint("read",new{id=graphId});Blueprint("argument",new{id=graphId,basis=graph["basis"]!.ToString(),node="copy_return",name="value",valueJson="{\"node\":\"body\",\"output\":\"return\"}"});graph=Blueprint("read",new{id=graphId});string last=System.Linq.Enumerable.Single(graph["nodes"]!.AsArray(),n=>n!["kind"]!.ToString()=="export"&&n["id"]!.ToString()!="copy_return")!["id"]!.ToString();Blueprint("route",new{id=graphId,basis=graph["basis"]!.ToString(),node=last,port="next",to="copy_return"});graph=Blueprint("read",new{id=graphId});Check(graph["diagnostics"]!["warnings"]!.AsArray().Count==0,"every declared output explicitly assigned");Confirm(new[]{graphId});Run("5,5");Check(System.IO.File.ReadAllText(System.IO.Path.Combine(root,"blueprints/value.csbody"))==original,"original C# remains byte exact through append-out migration");
        }finally{if(peer.Length>0)calls.Close.Invoke(peer);calls.Close.Invoke(view);}
        Console.WriteLine("MultiOutput public contract/CAS/cold/body/compiler/5-0-5-5 PASS");return 0;
        ""","MultiOutput public contract/CAS/cold/body/compiler/5-0-5-5 PASS");
    }
    public void test_object_blank_and_reference_factories_preserve_out_modes_and_positional_output_names()
    {
        f.Add("App","function","Value","function App::Value (int n,out int count,out bool ready) -> int {provide App::Value with App::ValueBody;}");f.Add("App","implementation","ValueBody","implementation App::ValueBody for App::Value (int n,out int count,out bool ready) -> int {body common \"value.csbody\";}");f.Body("App","value.csbody","count=n+1;ready=false;return n+3;");
        f.Add("App","module","Rules","module App::Rules {require App::Value (int,out int,out bool) -> int;default App::Value with App::ValueBody;}");f.Add("App","object","Consumer","object App::Consumer {module App::Rules;}");
        f.Add("App","function","Donor","function App::Donor (int input,out int amount,out bool active) -> int {provide App::Donor with App::DonorBody;}");f.Add("App","implementation","DonorBody","implementation App::DonorBody for App::Donor (int original,out int result,out bool flag) -> int {body common \"donor.csbody\";}");f.Body("App","donor.csbody","result=original*2;flag=true;return original+20;");f.Add("App","function","Wrong","function App::Wrong (int input,int amount,out bool active) -> int {}");f.Main();
        f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import App::Value as Value (int,out int,out bool) -> int in App::Consumer;body common \"main.csbody\";}");f.Body("App","main.csbody","int value=calls.Value.Invoke(2,out int count,out bool ready);Console.WriteLine(value+\",\"+count+\",\"+ready);return 0;");f.Sync();
        Consumer("""
        void Check(bool value,string why){if(!value)throw new Exception(why);}
        System.Text.Json.Nodes.JsonNode Json(string text)=>System.Text.Json.Nodes.JsonNode.Parse(text)!;
        string Serialize(object value)=>System.Text.Json.JsonSerializer.Serialize(value);
        string Hash(string value)=>Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(value))).ToLowerInvariant();
        string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT")!,root=System.IO.Path.GetDirectoryName(project)!,owner="App::Consumer",feature="App::Value";string view=calls.Open.Invoke(project,"owner","multi-factories");
        System.Text.Json.Nodes.JsonNode Cmd(string op,object value)=>Json(calls.Command.Invoke(view,op,Serialize(value)));
        System.Text.Json.Nodes.JsonNode Blueprint(string op,object value)=>Json(calls.Blueprint.Invoke(view,op,Serialize(value)));
        System.Text.Json.Nodes.JsonNode Preview(string implementation,string reference=""){var u=Cmd("select",new{id=owner})["unit"]!;return Blueprint("readImplementation",new{id=owner,function=feature,implementation,reference,revision=u["revision"]!.GetValue<long>(),hash=Hash(u["text"]!.ToString())});}
        string Create(string implementation,string reference=""){var p=Preview(implementation,reference);return Blueprint("createImplementation",new{id=owner,function=feature,implementation,reference,basis=p["basis"]!.ToString()})["id"]!.ToString();}
        void Confirm(System.Text.Json.Nodes.JsonNode graph){var ids=System.Linq.Enumerable.ToArray(System.Linq.Enumerable.Select(graph["reviewIds"]!.AsArray(),x=>x!.ToString()));var r=Cmd("review",new{ids,target="portable"})["review"]!;Check(Cmd("confirm",new{token=r["token"]!.ToString(),ids})["confirmation"]![0]!.ToString()=="confirmed","all source group compiler Confirm");}
        void Run(string expected){var r=Json(calls.Metadata.Invoke("run",Serialize(new{project,target="portable"})));Check(r["exit"]!.GetValue<int>()==0&&r["stdout"]!.ToString().Trim()==expected,"actual scoped out results "+expected+": "+r);}
        var originals=new System.Collections.Generic.Dictionary<string,byte[]>();foreach(string path in System.IO.Directory.GetFiles(root))originals[path]=System.IO.File.ReadAllBytes(path);
        try{
         Run("5,3,False");bool refused=false;try{Preview("App::BadReference","App::Wrong");}catch(ArgumentException){refused=true;}catch(InvalidOperationException){refused=true;}Check(refused,"input and out modes are part of positional reference compatibility");
         string graphId=Create("App::BlankOut");var graph=Blueprint("read",new{id=graphId});Check(graph["profile"]!.ToString()=="sync-acyclic-implicit-out-v1"&&graph["reviewIds"]!.AsArray().Count==5&&graph["nodes"]!.AsArray().Count==4,"blank out factory has independent C# plus three structural outputs");Check(graph["nodes"]![0]!["arguments"]!.AsArray().Count==1&&graph["nodes"]![0]!["outputs"]!.AsArray().Count==3,"out fields are result pins, never value inputs");Blueprint("source",new{id=graphId,basis=graph["basis"]!.ToString(),node="body",text="count=n*3;ready=true;return n+10;"});Cmd("save",new{});calls.Close.Invoke(view);view=calls.Open.Invoke(project,"owner","multi-factories");graph=Blueprint("read",new{id=graphId});Confirm(graph);Run("12,6,True");
         graphId=Create("App::ReferenceOut","App::Donor");graph=Blueprint("read",new{id=graphId});Check(graph["reviewIds"]!.AsArray().Count==4&&graph["nodes"]!.AsArray().Count==1&&graph["nodes"]![0]!["kind"]!.ToString()=="call"&&graph["profile"]!.ToString()=="sync-acyclic-ref-v1","reference out factory has typed call and no C# body copy");Check(graph["nodes"]![0]!["signature"]!["args"]![1]!["name"]!.ToString()=="amount"&&graph["signature"]!["args"]![1]!["name"]!.ToString()=="count","distinct function names are preserved and mapped by position");Confirm(graph);Run("22,4,True");
         foreach(var pair in originals)if(pair.Key!=System.IO.Path.Combine(root,"Consumer.celem")&&pair.Key!=project)Check(System.Linq.Enumerable.SequenceEqual(pair.Value,System.IO.File.ReadAllBytes(pair.Key)),"existing Fn/module/donor/original bodies preserved: "+pair.Key);
        }finally{calls.Close.Invoke(view);}
        Console.WriteLine("MultiOutput blank/reference factories/group/cold/scoped/12-6-22-4 PASS");return 0;
        ""","MultiOutput blank/reference factories/group/cold/scoped/12-6-22-4 PASS");
    }

}
