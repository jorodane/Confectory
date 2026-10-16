using Confectory.Core;
namespace Confectory.Tests;

public sealed class SourceConflictTests : TestCase
{
 public void test_owned_three_way_conflict_hashes_rebase_restore_manifest_scope_and_locality()
 {
  f.Add("App","object","Item","object App::Item {value n = 0;description \"base\";}");f.Sync();
  string sample=Path.Combine(f.Root,"conflict-consumer");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples/edit-workspace"),sample);
  foreach(string name in new[]{"file-stream","schema-editing","edit-workspace","save","change-set"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",name),Path.Combine(f.Root,"packs",name));
  string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/").Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack"));
  string entry=Path.Combine(sample,"main.celem"),source=File.ReadAllText(entry);int end=source.LastIndexOf('}');source=source.Insert(end,"provide Confectory.EditWorkspace::Conflict with Confectory.EditWorkspace::ConflictBody;provide Confectory.EditWorkspace::SetTextIfRevision with Confectory.EditWorkspace::SetTextIfRevisionBody;");File.WriteAllText(entry,source);
  File.WriteAllText(Path.Combine(sample,"main_body.celem"),"""
  implementation Example.EditWorkspace::MainBody for Example.EditWorkspace::Main () -> int {
  import Confectory.EditWorkspace::Open as Open (string,string,string) -> string;
  import Confectory.EditWorkspace::Read as Read (string,string) -> string[];
  import Confectory.EditWorkspace::SetTextIfRevision as Edit (string,string,string,long) -> bool;
  import Confectory.EditWorkspace::Conflict as Conflict (string,string,string) -> string;
  import Confectory.EditWorkspace::Export as Export (string) -> string;
  import Confectory.EditWorkspace::Restore as Restore (string,string) -> void;
  import Confectory.EditWorkspace::Create as Create (string,string,string) -> void;
  import Confectory.EditWorkspace::Close as Close (string) -> void;
  body common "main.csbody";}
  """);
  File.WriteAllText(Path.Combine(sample,"main.csbody"),"""
  void Check(bool ok,string reason){if(!ok)throw new Exception(reason);}
  void Reject(Action action){bool refused=false;try{action();}catch(ArgumentException){refused=true;}catch(InvalidOperationException){refused=true;}Check(refused,"Unsafe candidate was accepted");}
  string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT")!,root=System.IO.Path.GetDirectoryName(project)!,path=System.IO.Path.Combine(root,"Item.celem");
  string id="App::Item",handle=calls.Open.Invoke(project,"owner","conflicts"),original=System.IO.File.ReadAllText(path);
  System.Text.Json.Nodes.JsonNode Inspect(string source)=>System.Text.Json.Nodes.JsonNode.Parse(calls.Conflict.Invoke(handle,"inspect",System.Text.Json.JsonSerializer.Serialize(new{id=source})))!;
  System.Text.Json.Nodes.JsonNode Resolve(string source,System.Text.Json.Nodes.JsonNode preview,string text,string? draftHash=null,string? fileHash=null)=>System.Text.Json.Nodes.JsonNode.Parse(calls.Conflict.Invoke(handle,"resolve",System.Text.Json.JsonSerializer.Serialize(new{id=source,text,revision=preview["revision"]!.GetValue<long>(),draftHash=draftHash??preview["draftHash"]!.ToString(),fileHash=fileHash??preview["fileHash"]!.ToString()})))!;
  calls.Read.Invoke(handle,id);string local="object App::Item {value n = 10;description \"base\";}";Check(calls.Edit.Invoke(handle,id,local,0),"Initial owned edit");
  string remote="object App::Item {value n = 0;description \"remote A\";}";System.IO.File.WriteAllText(path,remote);var first=Inspect(id);
  Check(first["baseText"]!.ToString()==original&&first["draftText"]!.ToString()==local&&first["fileText"]!.ToString()==remote&&first["status"]!.ToString()=="conflict","Actual three source versions");
  Check(!first.ToJsonString().Contains(root,StringComparison.Ordinal)&&calls.Read.Invoke(handle,id)[4]=="1","Read is private-path-free and read-only");
  string merged="object App::Item {value n = 10;description \"remote B\";}",remoteB=remote.Replace("remote A","remote B");System.IO.File.WriteAllText(path,remoteB);
  Check(!Resolve(id,first,merged)["accepted"]!.GetValue<bool>()&&calls.Read.Invoke(handle,id)[3]==local,"Changed file refuses without changing draft");
  var fresh=Inspect(id);Check(!Resolve(id,fresh,merged,new string('0',64))["accepted"]!.GetValue<bool>(),"Hash guard independent of matching revision");
  var accepted=Resolve(id,fresh,merged);Check(accepted["accepted"]!.GetValue<bool>()&&accepted["changed"]!.GetValue<bool>()&&System.IO.File.ReadAllText(path)==remoteB,"Explicit rebase updates draft only");
  var now=Inspect(id);Check(now["baseText"]!.ToString()==remoteB&&now["draftText"]!.ToString()==merged&&now["status"]!.ToString()=="current","New baseline and retained merged draft");
  var same=Resolve(id,now,merged);Check(same["accepted"]!.GetValue<bool>()&&!same["changed"]!.GetValue<bool>()&&same["revision"]!.ToString()==now["revision"]!.ToString(),"No-op keeps revision");
  Reject(()=>Resolve(id,now,merged.Replace("App::Item","App::Other")));Check(calls.Read.Invoke(handle,id)[3]==merged,"Identity rejection preserves draft");
  string saved=calls.Export.Invoke(handle);calls.Close.Invoke(handle);handle=calls.Open.Invoke(project,"owner","conflicts");calls.Restore.Invoke(handle,saved);
  var restored=Inspect(id);Check(restored["draftText"]!.ToString()==merged&&restored["baseText"]!.ToString()==remoteB,"Rebased baseline and candidate survive owner restart");
  Check(!Resolve(id,first,merged,fileHash:restored["fileHash"]!.ToString())["accepted"]!.GetValue<bool>(),"Cold numeric revision collision cannot rebase old input");
  var rootPreview=Inspect("App::ProjectManifest");string manifest=System.IO.File.ReadAllText(project),external=manifest.Replace("project App version \"1\"","project App version \"2\"");System.IO.File.WriteAllText(project,external);rootPreview=Inspect("App::ProjectManifest");
  Reject(()=>Resolve("App::ProjectManifest",rootPreview,manifest.Replace("\"Main.celem\"","\"elsewhere.celem\"")));Check(Resolve("App::ProjectManifest",rootPreview,manifest)["accepted"]!.GetValue<bool>()&&System.IO.File.ReadAllText(project)==external,"Manifest keeps exact owned locator set and never writes final file");
  calls.Create.Invoke(handle,"object","App::Pending");Check(Inspect("App::Pending")["code"]!.ToString()=="CREATION_WORKFLOW_REQUIRED","Pending creations remain their own workflow");
  System.IO.File.Delete(path);Check(Inspect(id)["code"]!.ToString()=="FILE_MISSING"&&calls.Read.Invoke(handle,id)[3]==merged,"Missing final file preserves local draft");System.IO.File.WriteAllText(path,remoteB);
  if(OperatingSystem.IsLinux()){
   string outside=System.IO.Path.Combine(System.IO.Path.GetDirectoryName(root)!,"outside-conflict.celem");System.IO.File.WriteAllText(outside,"must not be read");System.IO.File.Delete(path);System.IO.File.CreateSymbolicLink(path,outside);Reject(()=>Inspect(id));System.IO.File.Delete(path);System.IO.File.WriteAllText(path,remoteB);
  }
  calls.Close.Invoke(handle);Console.WriteLine("Owned source conflict three-way/CAS/rebase/restore/manifest/no-final-write PASS");return 0;
  """);
  string? oldHost=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST"),oldProject=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT");
  try{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",f.Project);Output(new Builder(project,"portable").Build(),"Owned source conflict three-way/CAS/rebase/restore/manifest/no-final-write PASS");}
  finally{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",oldHost);Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",oldProject);}
 }
}
