using Confectory.Core;
namespace Confectory.Tests;

public sealed class InstantTableVersionTests : TestCase
{
 public void test_versioned_table_atomic_fill_schema_fences_precision_and_borrowed_lifetime()
 {
  f.Add("App","schema","Stats","schema App::Stats {field amount single general long;field enabled single general bool;field tags multiple general int;field peer single reference App::Stats;}");
  f.Add("App","object","Base","object App::Base {description \"Inherited description\";value description = \"Inherited metadata\";use schema App::Stats;data amount = 9223372036854775807;data enabled = true;data tags = [1,2];value rating = 3;}");
  f.Add("App","object","One","object App::One extends App::Base {}");
  f.Add("App","object","Two","object App::Two extends App::Base {}");f.Sync();
  string sample=Path.Combine(f.Root,"table-consumer");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples/edit-workspace"),sample);
  foreach(string name in new[]{"file-stream","schema-editing","edit-workspace","save","change-set","pack-workspace","instant-table"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",name),Path.Combine(f.Root,"packs",name));
  string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/").Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack").Replace("element Main function","registry Confectory.PackWorkspace \"../packs/pack-workspace/pack.cpack\";dependency Confectory.PackWorkspace version \"0.1.0\";registry Confectory.InstantTable \"../packs/instant-table/pack.cpack\";dependency Confectory.InstantTable version \"0.1.0\";\nelement Main function"));
  File.WriteAllText(Path.Combine(sample,"main_body.celem"),"""
  implementation Example.EditWorkspace::MainBody for Example.EditWorkspace::Main () -> int {
  import Confectory.PackWorkspace::Open as Open (string,string,string) -> string;
  import Confectory.PackWorkspace::BorrowDraft as Borrow (string) -> string;
  import Confectory.PackWorkspace::Command as Command (string,string,string) -> string;
  import Confectory.PackWorkspace::Close as Close (string) -> void;
  import Confectory.EditWorkspace::DescribeSchema as Describe (string,string,string) -> string;
  import Confectory.EditWorkspace::Read as Read (string,string) -> string[];
  import Confectory.EditWorkspace::EditBatch as Batch (string,string[],string[],long[],string[]) -> bool;
  import Confectory.EditWorkspace::SetTextIfRevision as Edit (string,string,string,long) -> bool;
  import Confectory.InstantTable::Create as Create (string,string[],string[],string) -> string;
  import Confectory.InstantTable::SnapshotVersioned as Snapshot (string) -> string;
  import Confectory.InstantTable::EditCellsVersioned as EditCells (string,string[],string,string,string,string) -> bool;
  import Confectory.InstantTable::FillVersioned as Fill (string,string[],string,string,string) -> bool;
  import Confectory.InstantTable::SetCellAtVersion as Set (string,string,string,string,long,string,string) -> bool;
  import Confectory.InstantTable::Poll as Poll (string) -> string[];
  import Confectory.InstantTable::Close as CloseTable (string) -> void;
  body common "main.csbody";}
  """);
  File.WriteAllText(Path.Combine(sample,"main.csbody"),"""
  void Check(bool ok,string message){if(!ok)throw new Exception(message);}
  string Hash(string text)=>Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(text))).ToLowerInvariant();
  System.Text.Json.Nodes.JsonNode Row(System.Text.Json.Nodes.JsonNode snapshot,string id)=>System.Linq.Enumerable.First(snapshot["rows"]!.AsArray(),r=>r!["id"]!.ToString()==id)!;
  string Versions(System.Text.Json.Nodes.JsonNode snapshot){var obj=new System.Text.Json.Nodes.JsonObject();foreach(var row in snapshot["rows"]!.AsArray())obj[row!["id"]!.ToString()]=new System.Text.Json.Nodes.JsonObject{["revision"]=row["revision"]!.DeepClone(),["textHash"]=row["textHash"]!.DeepClone(),["viewHash"]=row["viewHash"]!.DeepClone()};return obj.ToJsonString();}
  void Refused(Action action,string label){try{action();}catch(ArgumentException){return;}throw new Exception(label);}
  string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT")!,root=System.IO.Path.GetDirectoryName(project)!,oneSource=System.IO.Path.Combine(root,"One.celem"),twoSource=System.IO.Path.Combine(root,"Two.celem"),oneOriginal=System.IO.File.ReadAllText(oneSource),twoOriginal=System.IO.File.ReadAllText(twoSource);
  string owner=calls.Open.Invoke(project,"owner","table"),workspace=calls.Borrow.Invoke(owner),amount="data:[\"amount\"]",tags="data:[\"tags\"]";
  calls.Describe.Invoke(workspace,"App::One","");
  string table=calls.Create.Invoke(workspace,new[]{"App::One","App::Two"},new[]{"description","value:\"description\"","rating",amount,tags,"data:[\"peer\"]"},"Owned typed rows");
  var first=System.Text.Json.Nodes.JsonNode.Parse(calls.Snapshot.Invoke(table))!;var row=Row(first,"App::One");
  Check(row["state"]!.ToString()=="available","schema available: "+first.ToJsonString());
  Check(row["cellInfo"]![amount]!["valueJson"]!.ToString()=="9223372036854775807","exact int64 string");
  Check(row["cells"]!["description"]!.ToString()=="Inherited description"&&row["cellInfo"]!["description"]!["origin"]!.ToString()=="App::Base","inherited description origin");
  Check(calls.Fill.Invoke(table,new[]{"App::One","App::Two"},amount,"9223372036854775806",Versions(first)),"atomic typed fill");
  Check(calls.Poll.Invoke(table).Length==2,"both subscriptions observe shared drafts");
  var changed=System.Text.Json.Nodes.JsonNode.Parse(calls.Snapshot.Invoke(table))!;Check(Row(changed,"App::Two")["cellInfo"]![amount]!["valueJson"]!.ToString()=="9223372036854775806","fresh typed snapshot");
  Check(!calls.Fill.Invoke(table,new[]{"App::One","App::Two"},amount,"4",Versions(first)),"displayed stale rows refused");
  Refused(()=>calls.Fill.Invoke(table,new[]{"App::One","App::Two"},tags,"[1,\"invalid\"]",Versions(changed)),"invalid descendant must refuse all rows");
  Check(calls.Snapshot.Invoke(table)==changed.ToJsonString(),"invalid fill has no partial draft writes");
  string one=calls.Read.Invoke(workspace,"App::One")[3],two=calls.Read.Invoke(workspace,"App::Two")[3];
  Refused(()=>calls.Batch.Invoke(workspace,new[]{"App::One","App::Two"},new[]{one.Replace("9223372036854775806","5"),"object App::Wrong {}"},new[]{1L,1L},new[]{Hash(one),Hash(two)}),"invalid second identity refused");
  Check(calls.Read.Invoke(workspace,"App::One")[3]==one,"batch prevalidation no partial writes");
  Check(!calls.Batch.Invoke(workspace,new[]{"App::One","App::Two"},new[]{one.Replace("9223372036854775806","5"),two},new[]{1L,0L},new[]{Hash(one),Hash(two)}),"stale second row refuses entire batch");
  Check(calls.Read.Invoke(workspace,"App::One")[3]==one,"batch stale second no partial write");
  row=Row(changed,"App::One");Check(!calls.Set.Invoke(table,"App::One",amount,"4",1,new string('0',64),row["viewHash"]!.ToString()),"source hash required even at current revision");
  var schema=calls.Read.Invoke(workspace,"App::Stats");Check(calls.Edit.Invoke(workspace,"App::Stats",schema[3].Replace("long","int"),0),"schema shared draft edit");
  Check(!calls.Fill.Invoke(table,new[]{"App::One","App::Two"},amount,"6",Versions(changed)),"changed schema view refuses old table version");
  Check(calls.Edit.Invoke(workspace,"App::Stats",schema[3],1),"restore schema draft");
  var current=System.Text.Json.Nodes.JsonNode.Parse(calls.Snapshot.Invoke(table))!;
  Check(calls.Fill.Invoke(table,new[]{"App::One","App::Two"},"description","\"Edited description\"",Versions(current)),"description fill drafts");
  current=System.Text.Json.Nodes.JsonNode.Parse(calls.Snapshot.Invoke(table))!;
  Check(calls.Fill.Invoke(table,new[]{"App::One","App::Two"},tags,"[3,4]",Versions(current)),"typed array fill");
  current=System.Text.Json.Nodes.JsonNode.Parse(calls.Snapshot.Invoke(table))!;
  Check(calls.EditCells.Invoke(table,new[]{"App::One","App::Two"},amount,"null",Versions(current),"unset"),"remove local typed overrides");
  current=System.Text.Json.Nodes.JsonNode.Parse(calls.Snapshot.Invoke(table))!;Check(Row(current,"App::One")["cellInfo"]![amount]!["valueJson"]!.ToString()=="9223372036854775807"&&!Row(current,"App::One")["cellInfo"]![amount]!["localOverride"]!.GetValue<bool>(),"reset reveals inherited exact value");
  Check(calls.Fill.Invoke(table,new[]{"App::One","App::Two"},amount,"9223372036854775806",Versions(current)),"set typed values again");
  current=System.Text.Json.Nodes.JsonNode.Parse(calls.Snapshot.Invoke(table))!;
  Check(calls.Fill.Invoke(table,new[]{"App::One","App::Two"},"rating","7",Versions(current)),"metadata override");current=System.Text.Json.Nodes.JsonNode.Parse(calls.Snapshot.Invoke(table))!;
  Check(calls.EditCells.Invoke(table,new[]{"App::One","App::Two"},"rating","null",Versions(current),"unset"),"metadata reset");current=System.Text.Json.Nodes.JsonNode.Parse(calls.Snapshot.Invoke(table))!;Check(Row(current,"App::Two")["cells"]!["rating"]!.GetValue<int>()==3,"metadata inheritance restored");
  Check(calls.EditCells.Invoke(table,new[]{"App::One","App::Two"},"description","null",Versions(current),"unset"),"description reset");current=System.Text.Json.Nodes.JsonNode.Parse(calls.Snapshot.Invoke(table))!;Check(Row(current,"App::One")["cells"]!["description"]!.ToString()=="Inherited description","description origin restored");
  Check(calls.Fill.Invoke(table,new[]{"App::One","App::Two"},"description","\"Edited description\"",Versions(current)),"description set after reset");current=System.Text.Json.Nodes.JsonNode.Parse(calls.Snapshot.Invoke(table))!;
  Check(calls.Fill.Invoke(table,new[]{"App::One","App::Two"},"value:\"description\"","\"Changed metadata\"",Versions(current)),"reserved metadata name has explicit alias");current=System.Text.Json.Nodes.JsonNode.Parse(calls.Snapshot.Invoke(table))!;
  Check(Row(current,"App::One")["cells"]!["description"]!.ToString()=="Edited description"&&Row(current,"App::One")["cells"]!["value:\"description\""]!.ToString()=="Changed metadata","metadata does not overwrite declaration description");
  Check(calls.EditCells.Invoke(table,new[]{"App::One","App::Two"},"value:\"description\"","null",Versions(current),"unset"),"reserved metadata alias reset");current=System.Text.Json.Nodes.JsonNode.Parse(calls.Snapshot.Invoke(table))!;Check(Row(current,"App::Two")["cells"]!["value:\"description\""]!.ToString()=="Inherited metadata","metadata alias reset reveals its own inherited value");
  Refused(()=>calls.Fill.Invoke(table,new[]{"App::One","App::Two"},"data:[\"peer\"]","{\"$ref\":\"App::Missing\"}",Versions(current)),"unresolved schema reference rejected");
  Check(System.IO.File.ReadAllText(oneSource)==oneOriginal&&System.IO.File.ReadAllText(twoSource)==twoOriginal,"all table edits preserve final source before confirmation");
  calls.Command.Invoke(owner,"save","{}");calls.CloseTable.Invoke(table);Check(calls.Read.Invoke(workspace,"App::One")[0]=="App::One","closing table preserves borrowed draft lifetime");calls.Close.Invoke(owner);
  owner=calls.Open.Invoke(project,"owner","table");workspace=calls.Borrow.Invoke(owner);table=calls.Create.Invoke(workspace,new[]{"App::One","App::Two"},new[]{"description",amount,tags},"Restored");
  var restored=System.Text.Json.Nodes.JsonNode.Parse(calls.Snapshot.Invoke(table))!;Check(Row(restored,"App::One")["cells"]!["description"]!.ToString()=="Edited description"&&Row(restored,"App::Two")["cellInfo"]![tags]!["valueJson"]!.ToString()=="[3,4]","durable Save restoration");
  var reviewed=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(owner,"review","{\"target\":\"portable\",\"ids\":[\"App::One\",\"App::Two\"]}"))!;string token=reviewed["review"]!["token"]!.ToString();
  Check(System.IO.File.ReadAllText(oneSource)==oneOriginal,"review preserves source");
  calls.Command.Invoke(owner,"confirm",System.Text.Json.JsonSerializer.Serialize(new{token,ids=new[]{"App::One","App::Two"}}));
  Check(System.IO.File.ReadAllText(oneSource).Contains("9223372036854775806",StringComparison.Ordinal)&&System.IO.File.ReadAllText(twoSource).Contains("Edited description",StringComparison.Ordinal),"real compiler Confirm publishes both selected rows");
  calls.CloseTable.Invoke(table);calls.Close.Invoke(owner);Console.WriteLine("Versioned table typed precision/atomic fill/source and schema fences/Save/Confirm/borrowed lifetime PASS");return 0;
  """);
  string? host=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST"),selected=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT");
  try{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",f.Project);var built=new Builder(project,"portable").Build();var run=Processes.Run(Strings(built,"run"),timeoutSeconds:120);Equal(0,run.ExitCode);Equal("Versioned table typed precision/atomic fill/source and schema fences/Save/Confirm/borrowed lifetime PASS",run.Stdout.Trim());}
  finally{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",selected);}
 }
}
