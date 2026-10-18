using Confectory.Core;
namespace Confectory.Tests;
public sealed class NativeFieldViewTests : TestCase
{
 string Consumer(bool instrument)
 {
  string consumer=Path.Combine(f.Root,"native field consumer"),model=Path.Combine(f.Root,"native field model"),workspace=Path.Combine(f.Root,"native field workspace");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples/editor-home"),consumer);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs/editor-home-model"),model);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs/edit-workspace"),workspace);
  string project=Path.Combine(consumer,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../",Fixture.Repo+"/").Replace(Path.Combine(Fixture.Repo,"packs/editor-home-model/pack.cpack"),Path.Combine(model,"pack.cpack")).Replace(Path.Combine(Fixture.Repo,"packs/edit-workspace/pack.cpack"),Path.Combine(workspace,"pack.cpack")));
  if(instrument){
   string body=Path.Combine(model,"FieldDiscovery.csbody"),source=File.ReadAllText(body),needle="var view=System.Text.Json.Nodes.JsonNode.Parse(calls.Describe.Invoke(draft,id,\"\"))!;CheckCancel();";True(source.Contains(needle));
   source="""
string? fixtureLatePath=Environment.GetEnvironmentVariable("CONFECTORY_NATIVE_FIELD_LATE");bool fixtureLate=fixtureLatePath is not null&&System.IO.File.Exists(fixtureLatePath);if(fixtureLate){System.IO.File.Delete(fixtureLatePath!);cancellation="";}
"""+"\n"+source;
   source=source.Replace(needle,needle+"\n"+"""
string? probe=Environment.GetEnvironmentVariable("CONFECTORY_NATIVE_FIELD_PROBE"),hold=Environment.GetEnvironmentVariable("CONFECTORY_NATIVE_FIELD_HOLD"),entered=Environment.GetEnvironmentVariable("CONFECTORY_NATIVE_FIELD_ENTERED");if(probe is not null)System.IO.File.AppendAllText(probe,id+"\n");if(hold is not null&&System.IO.File.Exists(hold)){System.IO.File.WriteAllText(entered!,id);var deadline=DateTime.UtcNow.AddSeconds(20);while(System.IO.File.Exists(hold)){CheckCancel();if(DateTime.UtcNow>deadline)throw new TimeoutException("Owned native metadata barrier");System.Threading.Thread.Sleep(10);}}
"""+"\n");
   source=source.Replace("var encoding=new", """
string? fixtureMutation=Environment.GetEnvironmentVariable("CONFECTORY_NATIVE_FIELD_MUTATE");if(fixtureMutation is not null&&System.IO.File.Exists(fixtureMutation)){var change=System.Text.Json.Nodes.JsonNode.Parse(System.IO.File.ReadAllText(fixtureMutation))!;System.IO.File.Delete(fixtureMutation);string target=change["id"]!.ToString();if(!System.Linq.Enumerable.Contains(ids,target))throw new Exception("Owned mutation must name a selected object");var unit=calls.Read.Invoke(draft,target);if(!calls.FixtureSet.Invoke(draft,target,unit[3].Replace(change["from"]!.ToString(),change["to"]!.ToString(),StringComparison.Ordinal),long.Parse(unit[4],System.Globalization.CultureInfo.InvariantCulture)))throw new Exception("Owned competing writer conflict");}
"""+"\nvar encoding=new");
   source=source.Replace("CheckCancel();return output;", """
if(fixtureLate&&Environment.GetEnvironmentVariable("CONFECTORY_NATIVE_FIELD_LATE_DONE") is string done)System.IO.File.WriteAllText(done,new System.Text.Json.Nodes.JsonObject{["request"]=request,["query"]=query}.ToJsonString());CheckCancel();return output;
""");File.WriteAllText(body,source);
   string declaration=Path.Combine(model,"FieldDiscoveryBody.celem");File.WriteAllText(declaration,File.ReadAllText(declaration).Replace("body common", "import Confectory.EditWorkspace::SetTextIfRevision as FixtureSet (string,string,string,long) -> bool;\nbody common"));
  }
  string describe=Path.Combine(workspace,"DescribeSchema.csbody"),text=File.ReadAllText(describe);int at=text.LastIndexOf("return new System.Text.Json.Nodes.JsonObject",StringComparison.Ordinal);True(at>=0);text=text[..at]+text[at..].Replace("return new System.Text.Json.Nodes.JsonObject","var nullableReply=new System.Text.Json.Nodes.JsonObject");File.WriteAllText(describe,text+"\nvar nullableProjection=System.Text.Json.Nodes.JsonNode.Parse(nullableReply)!;foreach(var field in nullableProjection[\"values\"]!.AsArray())if(field![\"field\"]!.ToString()==\"nullish\"&&field[\"value\"]?.ToJsonString()==\"1\")field[\"value\"]=null;nullableProjection[\"viewHash\"]=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(nullableProjection[\"viewHash\"]!.ToString()+\"-owned-native-null-adapter\"))).ToLowerInvariant();return nullableProjection.ToJsonString();\n");
  return project;
 }
 public void test_native_field_view_same_readonly_model_states_pages_storage_cas_and_bounds()
 {
  f.Add("App","schema","Stats","schema App::Stats {field amount single general long;field unsetText single general string;}");f.Add("App","object","One","object App::One {use schema App::Stats;data amount = 9223372036854775807;value nullish = 1;value zero = 0;value falsey = false;value empty = \"\";}");f.Add("App","object","Bare","object App::Bare {}");f.Add("App","object","Broken","object App::Broken {}");f.Add("App","object","Many","object App::Many {"+string.Join("",Enumerable.Range(0,1050).Select(n=>"value field"+n.ToString("D4")+" = "+n+";"))+"}");f.Add("App","object","Tail","object App::Tail {value field1049 = 0;}");f.Add("App","object","Huge","object App::Huge {"+string.Join("",Enumerable.Range(0,5).Select(n=>"value blob"+n+" = \""+new string('x',60000)+"\";"))+"}");f.Sync();File.WriteAllText(Path.Combine(f.Packs["App"].Root,"Broken.celem"),"broken owned declaration");
  string project=Consumer(false),consumer=Path.GetDirectoryName(project)!;
  File.WriteAllText(Path.Combine(consumer,"MainBody.celem"),"implementation Confectory.EditorHome::MainBody for Confectory.EditorHome::Main () -> int {import Confectory.EditorHome.Model::NativeFieldView as View (string,string,string,string) -> string;import Confectory.EditorHome.Model::FieldDiscovery as Discover (string,string,string,string) -> string;import Confectory.EditorHome.Model::CreateSession as Create (string,string) -> string;import Confectory.EditorHome.Model::Command as Command (string,string,string) -> string;import Confectory.EditorHome.Model::Snapshot as Snapshot (string) -> string;import Confectory.EditorHome.Model::CloseSession as Close (string) -> void;body common \"Main.csbody\";}");
  File.WriteAllText(Path.Combine(consumer,"Main.csbody"),"string repo="+System.Text.Json.JsonSerializer.Serialize(Fixture.Repo)+",project="+System.Text.Json.JsonSerializer.Serialize(f.Project)+",storage="+System.Text.Json.JsonSerializer.Serialize(Path.Combine(f.Root,"native view storage"))+";\n"+File.ReadAllText(Path.Combine(Fixture.Repo,"tests/probes/native_field_view_contract.csbody")));
  string? prior=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST");try{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll"));var built=new Builder(project,"linux").Build();Output(built,"PASS native field view same readonly discovery, exact JSON/presence/unknown/limits, scoped settings CAS/corruption/symlink, no snapshot or write authority");}finally{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",prior);}
 }
 public void test_linux_native_field_union_explicit_input_cancel_lifetime_cas_and_latest_cold()
 {
  if(string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISPLAY")))Skip("native fields require live X11");string project=Consumer(true);var built=new Builder(project,"linux").Build();string report=Path.Combine(f.Root,"native-fields.json");File.WriteAllText(report,built.ToJsonString());
  var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/gui/entry_home_fields_x11.py"),report},timeoutSeconds:600);Console.WriteLine(run.Stdout.Trim());True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS native field union actual GTK input"),run.Stdout+run.Stderr);
 }
}
