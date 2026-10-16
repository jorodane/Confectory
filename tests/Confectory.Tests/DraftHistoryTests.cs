using Confectory.Core;
namespace Confectory.Tests;

public sealed class DraftHistoryTests : TestCase
{
 public void test_shared_draft_history_atomic_inverse_cas_restart_branch_and_owner_boundaries()
 {
  f.Add("App","object","Item","object App::Item {value n = 0;}");f.Add("App","object","Other","object App::Other {value n = 0;}");f.Sync();
  string sample=Path.Combine(f.Root,"history-consumer");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples/edit-workspace"),sample);
  foreach(string name in new[]{"file-stream","schema-editing","edit-workspace","save","change-set"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",name),Path.Combine(f.Root,"packs",name));
  string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/").Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack"));
  string entry=Path.Combine(sample,"main.celem"),source=File.ReadAllText(entry);int end=source.LastIndexOf('}');source=source.Insert(end,"provide Confectory.EditWorkspace::History with Confectory.EditWorkspace::HistoryBody;provide Confectory.EditWorkspace::EditBatch with Confectory.EditWorkspace::EditBatchBody;provide Confectory.EditWorkspace::SetTextIfRevision with Confectory.EditWorkspace::SetTextIfRevisionBody;");File.WriteAllText(entry,source);
  File.WriteAllText(Path.Combine(sample,"main_body.celem"),"""
  implementation Example.EditWorkspace::MainBody for Example.EditWorkspace::Main () -> int {
  import Confectory.EditWorkspace::Open as Open (string,string,string) -> string;
  import Confectory.EditWorkspace::Read as Read (string,string) -> string[];
  import Confectory.EditWorkspace::SetTextIfRevision as Edit (string,string,string,long) -> bool;
  import Confectory.EditWorkspace::EditBatch as Batch (string,string[],string[],long[],string[]) -> bool;
  import Confectory.EditWorkspace::History as History (string,string,string) -> string;
  import Confectory.EditWorkspace::Export as Export (string) -> string;
  import Confectory.EditWorkspace::Restore as Restore (string,string) -> void;
  import Confectory.EditWorkspace::Create as Create (string,string,string) -> void;
  import Confectory.EditWorkspace::Close as Close (string) -> void;
  body common "main.csbody";}
  """);
  File.WriteAllText(Path.Combine(sample,"main.csbody"),"""
  void Check(bool ok,string reason){if(!ok)throw new Exception(reason);}
  string Hash(string text)=>Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(text))).ToLowerInvariant();
  string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT")!,root=System.IO.Path.GetDirectoryName(project)!,id="App::Item",other="App::Other",handle=calls.Open.Invoke(project,"owner","history");
  string initial=calls.Read.Invoke(handle,id)[3],otherInitial=calls.Read.Invoke(handle,other)[3],edited=initial.Replace("= 0","= 1"),otherEdited=otherInitial.Replace("= 0","= 2");
  System.Text.Json.Nodes.JsonNode Inspect()=>System.Text.Json.Nodes.JsonNode.Parse(calls.History.Invoke(handle,"inspect","{}"))!;
  System.Text.Json.Nodes.JsonNode Move(string direction,string token)=>System.Text.Json.Nodes.JsonNode.Parse(calls.History.Invoke(handle,direction,System.Text.Json.JsonSerializer.Serialize(new{token})))!;
  string Token(string direction)=>Inspect()[direction]!["token"]!.ToString();
  Check(Inspect()["undoCount"]!.GetValue<int>()==0,"Fresh history");Check(calls.Edit.Invoke(handle,id,edited,0),"First source edit");var one=Inspect();string old=one["undo"]!["token"]!.ToString();
  Check(one["undoCount"]!.GetValue<int>()==1&&!one.ToJsonString().Contains(edited,StringComparison.Ordinal)&&!one.ToJsonString().Contains(root,StringComparison.Ordinal),"History metadata has no source text or host paths");
  Check(calls.Edit.Invoke(handle,id,edited,1)&&!calls.Edit.Invoke(handle,id,initial,0)&&Token("undo")==old,"No-op and refused stale edit preserve history token");
  Check(calls.Edit.Invoke(handle,other,otherEdited,0),"Peer source edit");Check(!Move("undo",old)["accepted"]!.GetValue<bool>()&&calls.Read.Invoke(handle,id)[3]==edited,"Old displayed history refuses after peer edit");
  Check(Move("undo",Token("undo"))["accepted"]!.GetValue<bool>()&&calls.Read.Invoke(handle,other)[3]==otherInitial,"Undo peer source");
  Check(Move("undo",Token("undo"))["accepted"]!.GetValue<bool>()&&calls.Read.Invoke(handle,id)[3]==initial,"Undo original source");
  Check(Move("redo",Token("redo"))["accepted"]!.GetValue<bool>()&&calls.Read.Invoke(handle,id)[3]==edited,"Redo is new versioned draft edit");
  var a=calls.Read.Invoke(handle,id);var b=calls.Read.Invoke(handle,other);string next=edited.Replace("= 1","= 3"),nextOther=otherInitial.Replace("= 0","= 4");
  Check(calls.Batch.Invoke(handle,new[]{id,other},new[]{next,nextOther},new[]{long.Parse(a[4]),long.Parse(b[4])},new[]{Hash(a[3]),Hash(b[3])}),"Atomic batch edit");
  Check(Inspect()["redoCount"]!.GetValue<int>()==0&&Inspect()["undo"]!["units"]!.AsArray().Count==2,"New edit branches history and preserves transaction group");
  Check(Move("undo",Token("undo"))["accepted"]!.GetValue<bool>()&&calls.Read.Invoke(handle,id)[3]==edited&&calls.Read.Invoke(handle,other)[3]==otherInitial,"Both inverse drafts change atomically");
  Check(Move("redo",Token("redo"))["accepted"]!.GetValue<bool>()&&calls.Read.Invoke(handle,id)[3]==next&&calls.Read.Invoke(handle,other)[3]==nextOther,"Both redo drafts");
  string beforeRestartToken=Token("undo"),saved=calls.Export.Invoke(handle);calls.Close.Invoke(handle);handle=calls.Open.Invoke(project,"owner","history");calls.Restore.Invoke(handle,saved);
  Check(!Move("undo",beforeRestartToken)["accepted"]!.GetValue<bool>()&&Inspect()["undoCount"]!.GetValue<int>()==2,"Saved history restored with fresh owner token");
  Check(Move("undo",Token("undo"))["accepted"]!.GetValue<bool>()&&calls.Read.Invoke(handle,id)[3]==edited&&calls.Read.Invoke(handle,other)[3]==otherInitial,"Cold atomic inverse");
  var damaged=System.Text.Json.Nodes.JsonNode.Parse(saved)!;damaged["history"]!["undo"]![0]!["units"]![0]!["path"]="../outside.celem";bool refused=false;try{calls.Restore.Invoke(handle,damaged.ToJsonString());}catch(ArgumentException){refused=true;}Check(refused&&calls.Read.Invoke(handle,id)[3]==edited,"Invalid saved history refuses before changing sources");
  string independent=calls.Open.Invoke(project,"other-owner","history");Check(System.Text.Json.Nodes.JsonNode.Parse(calls.History.Invoke(independent,"inspect","{}"))!["undoCount"]!.GetValue<int>()==0,"Distinct owner history isolation");calls.Close.Invoke(independent);
  calls.Create.Invoke(handle,"object","App::Created");Check(Inspect()["undoCount"]!.GetValue<int>()==0&&Inspect()["boundary"]!.ToString()=="OWNERSHIP_CHANGED","Creation invalidates source-only history; no partial registration undo");
  string large="object App::Item {description \""+new string('\uac00',180000)+"\";}";Check(calls.Edit.Invoke(handle,id,large,long.Parse(calls.Read.Invoke(handle,id)[4])),"Large ordinary edit");Check(Inspect()["undoCount"]!.GetValue<int>()==0&&Inspect()["boundary"]!.ToString()=="ENTRY_BUDGET","Oversize history explicitly unavailable; accepted draft retained");
  Check(System.IO.File.ReadAllText(System.IO.Path.Combine(root,"Item.celem"))==initial&&System.IO.File.ReadAllText(System.IO.Path.Combine(root,"Other.celem"))==otherInitial,"History never changes final files");
  calls.Close.Invoke(handle);Console.WriteLine("Draft history actual owner atomic inverse/CAS/restart/branch/locality PASS");return 0;
  """);
  string? oldHost=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST"),oldProject=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT");
  try{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",f.Project);Output(new Builder(project,"portable").Build(),"Draft history actual owner atomic inverse/CAS/restart/branch/locality PASS");}
  finally{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",oldHost);Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",oldProject);}
 }
}
