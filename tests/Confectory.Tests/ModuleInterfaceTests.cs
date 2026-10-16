using Confectory.Core;
using System.Text.Json.Nodes;
namespace Confectory.Tests;
public sealed class ModuleInterfaceTests:TestCase
{
 public void test_owned_module_interface_contract_default_atomic_cas_cold_and_actual_consumer()
 {
  f.SecondProvider();f.Module("ParentRules");f.Add("App","module","Rules","module App::Rules extends App::ParentRules {description \"Owned module interface\";}");f.Main("module App::Rules;");f.Sync();
  string sample=Path.Combine(f.Root,"module-interface-consumer");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples/edit-workspace"),sample);
  foreach(string name in new[]{"file-stream","schema-editing","edit-workspace","save","change-set","pack-workspace"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",name),Path.Combine(f.Root,"packs",name));
  string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/").Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack").Replace("element Main function","registry Confectory.PackWorkspace \"../packs/pack-workspace/pack.cpack\";dependency Confectory.PackWorkspace version \"0.1.0\";\nelement Main function"));
  File.WriteAllText(Path.Combine(sample,"main_body.celem"),"""
  implementation Example.EditWorkspace::MainBody for Example.EditWorkspace::Main () -> int {
  import Confectory.PackWorkspace::Open as Open (string,string,string) -> string;
  import Confectory.PackWorkspace::Command as Command (string,string,string) -> string;
  import Confectory.PackWorkspace::History as History (string,string,string) -> string;
  import Confectory.PackWorkspace::Close as Close (string) -> void;
  import Confectory.SchemaEditing::Call as Metadata (string,string) -> string;
  body common "main.csbody";}
  """);
  File.WriteAllText(Path.Combine(sample,"main.csbody"),"""
  void Check(bool value,string why){if(!value)throw new Exception(why);}
  System.Text.Json.Nodes.JsonNode Json(string text)=>System.Text.Json.Nodes.JsonNode.Parse(text)!;
  string Serialize(object value)=>System.Text.Json.JsonSerializer.Serialize(value);
  string Hash(string value)=>Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(value))).ToLowerInvariant();
  string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT")!,root=System.IO.Path.GetDirectoryName(project)!,id="App::Rules";
  string view=calls.Open.Invoke(project,"owner","module-interface"),peer=calls.Open.Invoke(project,"owner","module-interface");
  System.Text.Json.Nodes.JsonNode Cmd(string op,object value)=>Json(calls.Command.Invoke(view,op,Serialize(value)));
  System.Text.Json.Nodes.JsonNode Current(){Cmd("select",new{id});return Cmd("effective",new{});}
  System.Text.Json.Nodes.JsonNode Edit(object edit,System.Text.Json.Nodes.JsonNode? shown=null){var unit=(shown??Current())["unit"]!;return Cmd("declaration",new{id,expectedRevision=unit["revision"]!.GetValue<long>(),expectedHash=Hash(unit["text"]!.ToString()),edit});}
  string Confirm(){var review=Cmd("review",new{ids=new[]{id},target="portable"})["review"]!;return Cmd("confirm",new{token=review["token"]!.ToString()})["confirmation"]![0]!.ToString();}
  void Run(string expected){var result=Json(calls.Metadata.Invoke("run",Serialize(new{project,target="portable"})));Check(result["exit"]!.GetValue<int>()==0&&result["stdout"]!.ToString().Trim()==expected,"actual module consumer result "+expected+": "+result.ToJsonString());}
  var original=new System.Collections.Generic.Dictionary<string,byte[]>();foreach(string path in System.IO.Directory.GetFiles(root))original[path]=System.IO.File.ReadAllBytes(path);
  try{
   var initial=Current();Check(initial["effective"]!["status"]!.ToString()=="available"&&initial["effective"]!["providerSelection"]!.ToString()=="not-performed"&&initial["effective"]!["bodyReads"]!.GetValue<int>()==0,"current module contract query reads declarations without choosing or executing a provider");var requirement=initial["effective"]!["requirements"]![0]!;Check(requirement["origin"]!.ToString()=="App::ParentRules"&&requirement["defaults"]![0]!["origin"]!.ToString()=="App::ParentRules","included parent contract and default retain their origin");Run("5");
   var stale=Current();var peerUnit=Json(calls.Command.Invoke(peer,"select",Serialize(new{id})))["unit"]!;calls.Command.Invoke(peer,"edit",Serialize(new{text=peerUnit["text"]!.ToString()+" ",expectedRevision=peerUnit["revision"]!.GetValue<long>()}));var refused=Edit(new{action="module-function",function="Api::Value",@default="Provider::Second"},stale);Check(refused["conflict"]!.GetValue<bool>()&&!Current()["unit"]!["text"]!.ToString().Contains("Provider::Second",StringComparison.Ordinal),"same-meaning peer changes fence row edit with no partial default");
   Edit(new{action="module-function",function="Api::Value",@default="Provider::Second"});var changed=Current();Check(changed["effective"]!["status"]!.ToString()=="available"&&changed["effective"]!["requirements"]![0]!["origin"]!.ToString()=="App::ParentRules"&&changed["effective"]!["requirements"]![0]!["defaults"]![0]!["implementation"]!.ToString()=="Provider::Second"&&!changed["unit"]!["text"]!.ToString().Contains("require Api::Value",StringComparison.Ordinal),"direct default override reuses inherited requirement without flattening or copying it");Check(System.Linq.Enumerable.SequenceEqual(original[System.IO.Path.Combine(root,"Rules.celem")],System.IO.File.ReadAllBytes(System.IO.Path.Combine(root,"Rules.celem"))),"edit stages module only");
   Cmd("save",new{});calls.Close.Invoke(peer);peer="";calls.Close.Invoke(view);view=calls.Open.Invoke(project,"owner","module-interface");Check(Current()["unit"]!["text"]!.ToString().Contains("Provider::Second",StringComparison.Ordinal)&&System.Linq.Enumerable.SequenceEqual(original[System.IO.Path.Combine(root,"Rules.celem")],System.IO.File.ReadAllBytes(System.IO.Path.Combine(root,"Rules.celem"))),"genuine cold restore retains the module draft without publication");Check(Confirm()=="confirmed","module source compiler Confirm");Run("102");string confirmed=System.IO.File.ReadAllText(System.IO.Path.Combine(root,"Rules.celem"));
   Edit(new{action="module-function",function="Api::Value",signature=new{args=new[]{new{type="long"}},@return="int"},@default="Provider::ValueBody"});var invalid=Current();Check(invalid["effective"]!["status"]!.ToString()=="unavailable"&&invalid["effective"]!["code"]!.ToString()=="CONTRACT_MISMATCH","unfinished contract/default batch is reported as an actual signature mismatch");Check(Confirm()=="invalid"&&System.IO.File.ReadAllText(System.IO.Path.Combine(root,"Rules.celem"))==confirmed,"invalid module cannot publish or overwrite the confirmed contract");
   Edit(new{action="module-function",function="Api::Value",signature=new{args=new[]{new{type="int"}},@return="int"},@default="Provider::Second"});var history=Json(calls.History.Invoke(view,"inspect","{}"));Check(history["undo"]!["units"]!.AsArray().Count==1,"contract and default are one source history entry");calls.History.Invoke(view,"undo",Serialize(new{token=history["undo"]!["token"]!.ToString()}));Check(Current()["effective"]!["status"]!.ToString()=="unavailable","atomic undo restores both old row values");history=Json(calls.History.Invoke(view,"inspect","{}"));calls.History.Invoke(view,"redo",Serialize(new{token=history["redo"]!["token"]!.ToString()}));Check(Current()["effective"]!["status"]!.ToString()=="available","atomic redo restores the complete typed row");
   Edit(new{action="module-function",function="Api::Value",signature=(object?)null});Check(Current()["effective"]!["requirements"]![0]!["origin"]!.ToString()=="App::ParentRules","explicit local contract removal reveals the original inherited requirement");Check(Current()["unit"]!["text"]!.ToString()==confirmed,"removing an unpublished local requirement returns to the already confirmed direct default");Run("102");Edit(new{action="module-function",function="Api::Value",@default=(string?)null});Check(Current()["effective"]!["requirements"]![0]!["defaults"]![0]!["implementation"]!.ToString()=="Provider::ValueBody","removing direct default reveals inherited candidate, without copying it");Check(Confirm()=="confirmed","default removal Confirm");Run("5");
   foreach(var pair in original)if(pair.Key!=System.IO.Path.Combine(root,"Rules.celem"))Check(System.Linq.Enumerable.SequenceEqual(pair.Value,System.IO.File.ReadAllBytes(pair.Key)),"parent, consumer and unrelated sources preserved");
  }finally{if(peer.Length>0)calls.Close.Invoke(peer);calls.Close.Invoke(view);}
  Console.WriteLine("Module interface contract/default/CAS/cold/compiler/Run5-102-5 PASS");return 0;
  """);
  string? host=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST"),selected=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT");
  try{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",f.Project);var built=new Builder(project,"portable").Build();var run=Processes.Run(Strings(built,"run"),timeoutSeconds:180);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Module interface contract/default/CAS/cold/compiler/Run5-102-5 PASS"));}
  finally{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",selected);}
 }
}
