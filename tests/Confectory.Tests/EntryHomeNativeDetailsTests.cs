using Confectory.Core;
namespace Confectory.Tests;
public sealed class EntryHomeNativeDetailsTests : TestCase
{
 public void test_linux_native_home_information_profile_cas_cancel_and_project_input_lifetimes()
 {
  if(string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISPLAY")))Skip("native details need a live X11 display");
  var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"linux").Build();string report=Path.Combine(f.Root,"native-details.json");File.WriteAllText(report,built.ToJsonString());
  var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/gui/entry_home_details_x11.py"),report},timeoutSeconds:360);Console.WriteLine(run.Stdout.Trim());True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS native Home information/profile"),run.Stdout+run.Stderr);
 }
 public void test_native_tree_projection_webui_parity_storage_cas_and_bounds()
 {
  string consumer=Path.Combine(f.Root,"tree-contract"),fixture=Path.Combine(f.Root,"tree-contract.json");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples/editor-home"),consumer);
  var prepared=Processes.Run(new[]{"node",Path.Combine(Fixture.Repo,"tests/web/native_tree_contract.mjs"),Fixture.Repo,fixture});True(prepared.ExitCode==0,prepared.Stdout+prepared.Stderr);
  string project=Path.Combine(consumer,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../",Fixture.Repo+"/"));
  File.WriteAllText(Path.Combine(consumer,"MainBody.celem"),"implementation Confectory.EditorHome::MainBody for Confectory.EditorHome::Main () -> int {import Confectory.EditorHome.Model::NativeTree as Tree (string,string,string,string) -> string;body common \"Main.csbody\";}");
  File.WriteAllText(Path.Combine(consumer,"Main.csbody"),"string fixture="+System.Text.Json.JsonSerializer.Serialize(fixture)+";string storage="+System.Text.Json.JsonSerializer.Serialize(Path.Combine(f.Root,"tree-state"))+";\n"+"""
  System.IO.Directory.CreateDirectory(storage);
  void Check(bool b,string message){if(!b)throw new Exception(message);}
  System.Text.Json.Nodes.JsonNode Call(string op,System.Text.Json.Nodes.JsonObject args,string project="tree-one")=>System.Text.Json.Nodes.JsonNode.Parse(calls.Tree.Invoke(storage,project,op,args.ToJsonString()))!;
  void Refused(Action action,string label){try{action();}catch(ArgumentException){return;}catch(InvalidOperationException){return;}throw new Exception("accepted "+label);}
  var data=System.Text.Json.Nodes.JsonNode.Parse(System.IO.File.ReadAllText(fixture))!;var loaded=Call("load",new());var value=loaded["value"]!.DeepClone().AsObject();value["expanded"]=new System.Text.Json.Nodes.JsonArray("root","ns:Owned","ns:Owned.Api","decl:Owned.Api::Root","decl:Owned.Api::Middle");value["selection"]="decl:Owned.Api::Leaf";
  var args=new System.Text.Json.Nodes.JsonObject{["inventory"]=data["inventory"]!.DeepClone(),["relationsMap"]=data["relationsMap"]!.DeepClone(),["value"]=value.DeepClone()};var projection=Call("project",args);
  foreach(var pair in data["expected"]!.AsObject()){var actual=projection["parents"]![pair.Key]!;foreach(string field in new[]{"parent","status","declaredParent"})Check(actual[field]!.ToString()==pair.Value![field]!.ToString(),"WebUI parity "+pair.Key+" "+field);}
  var rows=projection["rows"]!.AsArray();Check(System.Linq.Enumerable.Single(rows,n=>n!["key"]!.ToString()=="decl:Owned.Api::Leaf")!["depth"]!.GetValue<int>()==5,"three level parent path");Check(System.Linq.Enumerable.Single(rows,n=>n!["key"]!.ToString()=="decl:Owned.Api::Contained")!["depth"]!.GetValue<int>()==3,"contain not parent");Check(projection["selected"]!["row"]!["relationships"]!.AsArray().Count==2,"separate schema/contain");Check(!projection.ToJsonString().Contains("decl:Missing::Parent"),"no fabricated missing node");
  value["query"]="Foreign.Api::Parent";args["value"]=value.DeepClone();projection=Call("project",args);Check(System.Linq.Enumerable.Single(projection["rows"]!.AsArray(),n=>n!["key"]!.ToString()=="decl:Foreign.Api::Parent")!["row"]!["source"]!["sourceId"]!.ToString()=="Owned.Api::Cross","owned direct gate source");Check(!projection.ToJsonString().Contains("decl:Foreign.Api::Unused"),"query narrowed external identities");
  value["selection"]="decl:Missing::Selection";args["value"]=value.DeepClone();var missing=Call("project",args);Check(missing["missingSelection"]!.GetValue<bool>()&&missing["selected"] is null,"missing selection retained without replacement");value["selection"]="decl:Owned.Api::Leaf";
  var saved=Call("save",new(){["revision"]=loaded["revision"]!.DeepClone(),["value"]=value.DeepClone()});Check(System.Text.Json.Nodes.JsonNode.DeepEquals(saved["value"],Call("load",new())["value"]),"explicit cold state");Check(Call("load",new(),"tree-two")["value"]!["selection"]!.ToString()=="root","project isolation");
  string path=System.Linq.Enumerable.Single(System.IO.Directory.GetFiles(System.IO.Path.Combine(storage,"native-trees")));string before=System.IO.File.ReadAllText(path);System.IO.File.WriteAllText(path,before+"\n");Refused(()=>Call("save",new(){["revision"]=saved["revision"]!.DeepClone(),["value"]=value.DeepClone()}),"stale state CAS");Check(System.IO.File.ReadAllText(path)==before+"\n","CAS bytes preserved");System.IO.File.WriteAllText(path,"{broken");try{Call("load",new());throw new Exception("corrupt accepted");}catch(System.Text.Json.JsonException){}Check(System.IO.File.ReadAllText(path)=="{broken","corrupt preserved");System.IO.File.WriteAllText(path,before);
  var wrong=value.DeepClone().AsObject();wrong["projectId"]="tree-two";Refused(()=>Call("save",new(){["revision"]=saved["revision"]!.DeepClone(),["value"]=wrong}),"foreign state");wrong=value.DeepClone().AsObject();wrong["query"]=new string('x',257);args["value"]=wrong;Refused(()=>Call("project",args),"query budget");
  var many=data["inventory"]!.DeepClone().AsObject();var declarations=new System.Text.Json.Nodes.JsonArray();for(int n=0;n<2100;n++)declarations.Add(new System.Text.Json.Nodes.JsonObject{["id"]="Owned.Api::Many"+n,["kind"]="object",["owned"]=false});many["declarations"]=declarations;value["query"]="";value["group"]="";args["inventory"]=many;args["value"]=value.DeepClone();projection=Call("project",args);Check(projection["truncated"]!.GetValue<bool>()&&projection["rows"]!.AsArray().Count==2048,"visible row budget");
  Console.WriteLine("PASS native tree WebUI parent/status parity, contain/schema/direct-source fences, bounded rows and state, explicit load/save CAS/corruption/project isolation");return 0;
  """);
  var built=new Builder(project,"linux").Build();Output(built,"PASS native tree WebUI parent/status parity, contain/schema/direct-source fences, bounded rows and state, explicit load/save CAS/corruption/project isolation");
 }
 public void test_linux_native_tree_input_reopen_latest_state_and_pending_source_chat()
 {
  if(string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISPLAY")))Skip("native tree needs a live X11 display");
  var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"linux").Build();string report=Path.Combine(f.Root,"native-tree.json");File.WriteAllText(report,built.ToJsonString());
  var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/gui/entry_home_tree_x11.py"),report},timeoutSeconds:360);Console.WriteLine(run.Stdout.Trim());True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS native declaration tree input"),run.Stdout+run.Stderr);
 }
 public void test_windows_native_information_and_profile_composition_builds()
 {
  var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"windows").Build();True(built["tool"]!["ok"]!.GetValue<bool>());Console.WriteLine("PASS Windows managed native composition compile only; no Windows device run");
 }
}
