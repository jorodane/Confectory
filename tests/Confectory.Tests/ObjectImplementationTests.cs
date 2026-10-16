using Confectory.Core;
namespace Confectory.Tests;

public sealed class ObjectImplementationTests : TestCase
{
 public void test_owned_object_new_implementation_contract_group_cas_cold_and_actual_scope()
 {
  f.Add("App","function","Value","function App::Value (int n) -> int {provide App::Value with App::ValueBody;}");
  f.Add("App","implementation","ValueBody","implementation App::ValueBody for App::Value (int n) -> int {body common \"value.csbody\";}");f.Body("App","value.csbody","return n + 3;");
  f.Add("App","module","Rules","module App::Rules {require App::Value (int) -> int;default App::Value with App::ValueBody;}");
  f.Add("App","object","ParentConsumer","object App::ParentConsumer {provide App::Value with App::ValueBody;}");
  f.Add("App","object","Consumer","object App::Consumer extends App::ParentConsumer {module App::Rules;description \"Object implementation owner\";}");
  f.Main();f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int {import App::Value as Value (int) -> int in App::Consumer;body common \"main.csbody\";}");f.Body("App","main.csbody","Console.WriteLine(calls.Value.Invoke(2));return 0;");f.Sync();
  string sample=Path.Combine(f.Root,"object-implementation-consumer");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples/edit-workspace"),sample);
  foreach(string name in new[]{"file-stream","schema-editing","edit-workspace","save","change-set","pack-workspace"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",name),Path.Combine(f.Root,"packs",name));
  string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/").Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack").Replace("element Main function","registry Confectory.PackWorkspace \"../packs/pack-workspace/pack.cpack\";dependency Confectory.PackWorkspace version \"0.1.0\";\nelement Main function"));
  File.WriteAllText(Path.Combine(sample,"main_body.celem"),"""
  implementation Example.EditWorkspace::MainBody for Example.EditWorkspace::Main () -> int {
  import Confectory.PackWorkspace::Open as Open (string,string,string) -> string;
  import Confectory.PackWorkspace::Command as Command (string,string,string) -> string;
  import Confectory.PackWorkspace::Blueprint as Blueprint (string,string,string) -> string;
  import Confectory.PackWorkspace::Snapshot as Snapshot (string) -> string;
  import Confectory.PackWorkspace::Close as Close (string) -> void;
  import Confectory.PackWorkspace::BorrowDraft as BorrowDraft (string) -> string;
  import Confectory.EditWorkspace::Export as Export (string) -> string;
  import Confectory.EditWorkspace::Restore as Restore (string,string) -> void;
  import Confectory.EditWorkspace::BlueprintImplementation as PrepareOwnedImplementation (string,string,string,string,string[],long[],string[]) -> string;
  import Confectory.ChangeSet::ConfirmReviewed as ConfirmDirect (string,string[],string,string[]) -> string[];
  import Confectory.SchemaEditing::Call as Metadata (string,string) -> string;
  body common "main.csbody";}
  """);
  File.WriteAllText(Path.Combine(sample,"main.csbody"),"""
  void Check(bool value,string why){if(!value)throw new Exception(why);}
  System.Text.Json.Nodes.JsonNode Json(string text)=>System.Text.Json.Nodes.JsonNode.Parse(text)!;
  string Serialize(object value)=>System.Text.Json.JsonSerializer.Serialize(value);
  string Hash(string value)=>Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(value))).ToLowerInvariant();
  string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT")!,root=System.IO.Path.GetDirectoryName(project)!,owner="App::Consumer",feature="App::Value",implementation="App::ConsumerValueBody";
  string view=calls.Open.Invoke(project,"owner","object-implementation"),peer=calls.Open.Invoke(project,"owner","object-implementation");
  System.Text.Json.Nodes.JsonNode Cmd(string op,object value)=>Json(calls.Command.Invoke(view,op,Serialize(value)));
  System.Text.Json.Nodes.JsonNode Blueprint(string op,object value)=>Json(calls.Blueprint.Invoke(view,op,Serialize(value)));
  System.Text.Json.Nodes.JsonNode Current(string id)=>Cmd("select",new{id})["unit"]!;
  System.Text.Json.Nodes.JsonNode Prepare(){var unit=Current(owner);return Blueprint("readImplementation",new{id=owner,function=feature,implementation,revision=unit["revision"]!.GetValue<long>(),hash=Hash(unit["text"]!.ToString())});}
  System.Text.Json.Nodes.JsonNode Create(System.Text.Json.Nodes.JsonNode preview)=>Blueprint("createImplementation",new{id=owner,function=feature,implementation,basis=preview["basis"]!.ToString()});
  void Refused(Action action,string why){bool refused=false;try{action();}catch(InvalidOperationException){refused=true;}catch(ArgumentException){refused=true;}Check(refused,why);}
  void PeerWhitespace(string id){var unit=Json(calls.Command.Invoke(peer,"select",Serialize(new{id})))["unit"]!;calls.Command.Invoke(peer,"edit",Serialize(new{text=unit["text"]!.ToString()+" ",expectedRevision=unit["revision"]!.GetValue<long>()}));}
  void Run(string expected){var result=Json(calls.Metadata.Invoke("run",Serialize(new{project,target="portable"})));Check(result["exit"]!.GetValue<int>()==0&&result["stdout"]!.ToString().Trim()==expected,"actual object scope expected "+expected+": "+result);}
  string[] Group(System.Text.Json.Nodes.JsonNode graph)=>System.Linq.Enumerable.ToArray(System.Linq.Enumerable.Select(graph["reviewIds"]!.AsArray(),id=>id!.ToString()));
  string Confirm(string[] ids){var review=Cmd("review",new{ids,target="portable"})["review"]!;if(Array.IndexOf(ids,implementation)>=0)Check(System.Linq.Enumerable.Any(review["requiredIds"]!.AsArray(),id=>id!.ToString()==owner),"review carries the required owned object independent of primary selection");return Cmd("confirm",new{token=review["token"]!.ToString(),ids=System.Linq.Enumerable.ToArray(System.Linq.Enumerable.Select(review["units"]!.AsArray(),unit=>unit!["id"]!.ToString()))})["confirmation"]![0]!.ToString();}
  var originals=new System.Collections.Generic.Dictionary<string,byte[]>();foreach(string path in System.IO.Directory.GetFiles(root))originals[path]=System.IO.File.ReadAllBytes(path);
  try{
   Run("5");int count=Json(calls.Snapshot.Invoke(view))["ownedTotal"]!.GetValue<int>();
   foreach(string id in new[]{owner,feature}){var stale=Prepare();PeerWhitespace(id);Refused(()=>Create(stale),"same-semantic raw peer CAS: "+id);Check(Json(calls.Snapshot.Invoke(view))["ownedTotal"]!.GetValue<int>()==count,"CAS refusal added no sources");}
   var staleManifest=Prepare();calls.Command.Invoke(peer,"create",Serialize(new{kind="object",id="App::PeerRegistration"}));count++;Refused(()=>Create(staleManifest),"peer registration creation fences implementation without partial new sources");Check(Json(calls.Snapshot.Invoke(view))["ownedTotal"]!.GetValue<int>()==count,"registration CAS refusal added no sources");
   void Direct(string candidate){var objectUnit=Current(owner);var functionUnit=Current(feature);var manifestUnit=Current("App::ProjectManifest");calls.PrepareOwnedImplementation.Invoke(calls.BorrowDraft.Invoke(view),owner,feature,candidate,new[]{owner,feature,"App::ProjectManifest"},new[]{objectUnit["revision"]!.GetValue<long>(),functionUnit["revision"]!.GetValue<long>(),manifestUnit["revision"]!.GetValue<long>()},new[]{Hash(objectUnit["text"]!.ToString()),Hash(functionUnit["text"]!.ToString()),Hash(manifestUnit["text"]!.ToString())});}
   Refused(()=>Direct("App::"+new string('x',129)),"direct owner validates the bounded implementation identity with legitimate current preconditions");Check(Json(calls.Snapshot.Invoke(view))["ownedTotal"]!.GetValue<int>()==count,"invalid identity adds no units");
   string budgetHandle=calls.BorrowDraft.Invoke(view),beforeBudget=calls.Export.Invoke(budgetHandle);var budgetUnit=Current(owner);Cmd("edit",new{text="object App::Consumer extends App::ParentConsumer {module App::Rules;description "+Serialize(new string('x',1045000))+";}",expectedRevision=budgetUnit["revision"]!.GetValue<long>()});budgetUnit=Current(feature);Cmd("edit",new{text="function App::Value (int n) -> int {description "+Serialize(new string('y',10000))+";provide App::Value with App::ValueBody;}",expectedRevision=budgetUnit["revision"]!.GetValue<long>()});var budgetSaved=Json(calls.Export.Invoke(budgetHandle));foreach(var row in budgetSaved["changes"]!.AsArray())if(row!["id"]!.ToString()=="App::ProjectManifest"){string text=row["draft"]!.ToString();int at=text.IndexOf('{');row["draft"]=text[..(at+1)]+"description "+Serialize(new string('z',1045000))+";"+text[(at+1)..];}calls.Restore.Invoke(budgetHandle,budgetSaved.ToJsonString());bool budgetRefused=false;try{Direct(implementation);}catch(InvalidOperationException error){budgetRefused=error.Message.StartsWith("New implementation exceeds the Blueprint source budget",StringComparison.Ordinal);}Check(budgetRefused&&Json(calls.Snapshot.Invoke(view))["ownedTotal"]!.GetValue<int>()==count,"direct prospective two MiB guard refuses before any new source membership");calls.Restore.Invoke(budgetHandle,beforeBudget);
   var preview=Prepare();string destination=System.IO.Path.Combine(root,"elements/ConsumerValueBody.celem");System.IO.Directory.CreateDirectory(System.IO.Path.GetDirectoryName(destination)!);System.IO.File.WriteAllText(destination,"foreign destination");Refused(()=>Create(preview),"foreign destination refusal");Check(System.IO.File.ReadAllText(destination)=="foreign destination"&&Json(calls.Snapshot.Invoke(view))["ownedTotal"]!.GetValue<int>()==count,"collision preserves files and drafts");System.IO.File.Delete(destination);
   string linked=System.IO.Path.Combine(root,"blueprints"),outside=System.IO.Path.Combine(root,"link-target");System.IO.Directory.CreateDirectory(outside);System.IO.Directory.CreateSymbolicLink(linked,outside);preview=Prepare();try{Refused(()=>Create(preview),"linked graph directory refusal");}finally{System.IO.Directory.Delete(linked);}
   var function=Current(feature);string functionText=function["text"]!.ToString(),functionRevision=function["revision"]!.ToString();preview=Prepare();var created=Create(preview);string graphId=created["id"]!.ToString();
   System.Text.Json.Nodes.JsonNode Read()=>Blueprint("read",new{id=graphId});var graph=Read();var group=Group(graph);Check(group.Length==6&&Array.IndexOf(group,owner)>=0&&Array.IndexOf(group,"App::ProjectManifest")>=0,"five implementation sources plus the peer declaration share explicit registration review");
   Check(graph["sources"]!.AsArray().Count==6&&System.Linq.Enumerable.Any(graph["sources"]!.AsArray(),row=>row!["id"]!.ToString()==owner),"object context and existing function are observed without original body copies");
   Check(graph["nodes"]![0]!["source"]!.ToString()==""&&graph["diagnostics"]!["state"]!.ToString()=="needs-implementation"&&!created["compiled"]!.GetValue<bool>(),"new body starts explicitly unimplemented");
   var afterFunction=Current(feature);Check(afterFunction["text"]!.ToString()==functionText&&afterFunction["revision"]!.ToString()==functionRevision,"existing function identity, default and raw source are not rewritten");
   foreach(string omitted in Array.FindAll(group,id=>id!="App::PeerRegistration")){Refused(()=>Cmd("review",new{ids=Array.FindAll(group,id=>id!=omitted),target="portable"}),"partial group review refused: "+omitted);string draft=calls.BorrowDraft.Invoke(view);Check(calls.ConfirmDirect.Invoke(draft,Array.FindAll(group,id=>id!=omitted),"portable",Array.Empty<string>())[0]!="confirmed","direct compiler Confirm also refuses partial group");}
   Check(Confirm(group)=="invalid","unimplemented graph cannot publish");Check(System.Linq.Enumerable.All(originals,pair=>System.Linq.Enumerable.SequenceEqual(pair.Value,System.IO.File.ReadAllBytes(pair.Key))),"no source writes before successful compiler Confirm");Run("5");
   graph=Read();Blueprint("source",new{id=graphId,basis=graph["basis"]!.ToString(),node="body",text="return n + 100;"});
   string owned=calls.BorrowDraft.Invoke(view),saved=calls.Export.Invoke(owned);var damaged=Json(saved);foreach(var row in damaged["changes"]!.AsArray())if(row!["id"]!.ToString()==implementation)row!.AsObject().Remove("creationOwner");Refused(()=>calls.Restore.Invoke(owned,damaged.ToJsonString()),"restored alternative graph must retain its object group");Check(Array.IndexOf(Group(Read()),owner)>=0,"failed restore leaves original group intact");
   Cmd("save",new{});calls.Close.Invoke(peer);peer="";calls.Close.Invoke(view);view=calls.Open.Invoke(project,"owner","object-implementation");graph=Read();group=Group(graph);Check(group.Length==6&&Array.IndexOf(group,owner)>=0&&graph["nodes"]![0]!["source"]!.ToString()=="return n + 100;","true cold keeps object group and independent node source");Check(Confirm(group)=="confirmed","all required implementation and shared registration sources compiler Confirm");Run("102");
   var unit=Current(owner);Cmd("declaration",new{id=owner,expectedRevision=unit["revision"]!.GetValue<long>(),expectedHash=Hash(unit["text"]!.ToString()),edit=new{action="provide-function",function=feature,implementation=(string?)null}});Check(Confirm(new[]{owner})=="confirmed","explicit provider removal Confirm");Run("5");
   foreach(var pair in originals)if(pair.Key!=System.IO.Path.Combine(root,"Consumer.celem")&&pair.Key!=project)Check(System.Linq.Enumerable.SequenceEqual(pair.Value,System.IO.File.ReadAllBytes(pair.Key)),"original function, inherited object, module and old C# body remain byte exact: "+pair.Key);
  }finally{if(peer.Length>0)calls.Close.Invoke(peer);calls.Close.Invoke(view);}
  Console.WriteLine("Owned object new implementation/group/CAS/cold/compiler/Run5-102-5 PASS");return 0;
  """);
  string? host=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST"),selected=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT");
  try{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",f.Project);var built=new Builder(project,"portable").Build();var run=Processes.Run(Strings(built,"run"),timeoutSeconds:300);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Owned object new implementation/group/CAS/cold/compiler/Run5-102-5 PASS"));}
  finally{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",selected);}
 }
}
