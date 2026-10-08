using Confectory.Core;
namespace Confectory.Tests;
public sealed class SchemaEditingTests : TestCase
{
 public void test_signature_inputs_arrays_bounds_and_call_preflight_locality()
 {
  string sample=Path.Combine(f.Root,"schema-contract-consumer"),pack=Path.Combine(f.Root,"packs","schema-editing");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","schema-editing"),sample);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","schema-editing"),pack);
  string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/",StringComparison.Ordinal).Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));
  File.WriteAllText(Path.Combine(sample,"main_body.celem"),"""
  implementation Example.SchemaEditing::MainBody for Example.SchemaEditing::Main () -> int {
  import Confectory.SchemaEditing::DescribeInputs as DescribeInputs (string) -> string;
  import Confectory.SchemaEditing::ValidateArguments as ValidateArguments (string,string) -> string;
  import Confectory.SchemaEditing::CheckCall as CheckCall (string,string,string,string) -> string;
  body common "main.csbody";
  }
  """);
  File.WriteAllText(Path.Combine(sample,"main.csbody"),"""
  void Check(bool condition,string message){if(!condition)throw new Exception(message);}
  string Signature(string type)=>System.Text.Json.JsonSerializer.Serialize(new{args=new[]{new{type,name="input"}},@return="string[]"});
  foreach(var sample in new[]{new[]{"bool","[false]","[0]"},new[]{"string","[\"\"]","[null]"},new[]{"int","[0]","[2147483648]"},new[]{"long","[9223372036854775807]","[9223372036854775808]"},new[]{"float","[1e38]","[1e39]"},new[]{"double","[1e308]","[1e309]"},new[]{"bool[]","[[true,false]]","[[0]]"},new[]{"int[]","[[]]","[[1.5]]"},new[]{"string[]","[[\"\"]]","[[null]]"}}){
   var described=System.Text.Json.Nodes.JsonNode.Parse(calls.DescribeInputs.Invoke(Signature(sample[0])))!;Check(described["inputs"]![0]!["name"]!.ToString()=="input"&&described["return"]!["cardinality"]!.ToString()=="multiple"&&!described["executionAuthorized"]!.GetValue<bool>(),"signature-driven input and return description");
   var valid=System.Text.Json.Nodes.JsonNode.Parse(calls.ValidateArguments.Invoke(Signature(sample[0]),sample[1]))!;var invalid=System.Text.Json.Nodes.JsonNode.Parse(calls.ValidateArguments.Invoke(Signature(sample[0]),sample[2]))!;Check(valid["status"]!.ToString()=="valid"&&invalid["status"]!.ToString()=="invalid"&&!valid["executionAuthorized"]!.GetValue<bool>(),"typed positional argument boundary: "+sample[0]);
  }
  string signature=Signature("int");var row=new System.Text.Json.Nodes.JsonObject{["path"]=new System.Text.Json.Nodes.JsonArray("callback"),["kind"]="function",["cardinality"]="single",["type"]="Example::Fn",["state"]="present",["signature"]=System.Text.Json.Nodes.JsonNode.Parse(signature),["association"]=new System.Text.Json.Nodes.JsonObject{["status"]="valid",["id"]="Example::Body",["targets"]=new System.Text.Json.Nodes.JsonArray("common","linux")}};
  var view=new System.Text.Json.Nodes.JsonObject{["validation"]=new System.Text.Json.Nodes.JsonObject{["status"]="valid"},["rows"]=new System.Text.Json.Nodes.JsonArray(row),["targets"]=new System.Text.Json.Nodes.JsonArray("linux","android","windows")};
  var target=System.Text.Json.Nodes.JsonNode.Parse(calls.CheckCall.Invoke(view.ToJsonString(),"[\"callback\"]","[2]","linux"))!;Check(target["bodySelection"]!.ToString()=="linux"&&!target["executionAuthorized"]!.GetValue<bool>(),"specific target metadata wins common without invocation");
  var fallback=System.Text.Json.Nodes.JsonNode.Parse(calls.CheckCall.Invoke(view.ToJsonString(),"[\"callback\"]","[2]","android"))!;Check(fallback["bodySelection"]!.ToString()=="common","explicit common fallback preflight");
  row["association"]!["targets"]=new System.Text.Json.Nodes.JsonArray("linux");var unavailable=System.Text.Json.Nodes.JsonNode.Parse(calls.CheckCall.Invoke(view.ToJsonString(),"[\"callback\"]","[2]","windows"))!;Check(unavailable["code"]!.ToString()=="CALL_TARGET","missing target never pretends executable");
  Console.WriteLine("Schema signature inputs/arrays/bounds/read-only call checks PASS");return 0;
  """);
  var built=new Builder(project,"portable").Build();Output(built,"Schema signature inputs/arrays/bounds/read-only call checks PASS");
  File.AppendAllText(Path.Combine(pack,"ValidateArguments.csbody"),"\n// input validation owning-provider locality\n");var changed=new Builder(project,"portable").Build();PackRebuilt(changed,new[]{"Confectory.SchemaEditing::ValidateArgumentsBody"});Equal(0,Strings(changed,"statistics","compiledContracts").Length);
 }
 public void test_authoring_preservation_validation_and_locality()
 {
  string sample=Path.Combine(f.Root,"schema-sample"),pack=Path.Combine(f.Root,"packs","schema-editing");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","schema-editing"),sample);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","schema-editing"),pack);
  string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/",StringComparison.Ordinal).Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));
  string? host=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST"),selected=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT");
  try
  {
   Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets","element-authoring","bin","Release","net10.0","Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",f.Project);
   var built=new Builder(project,"portable").Build();var result=Processes.Run(Strings(built,"run"),timeoutSeconds:120);True(result.ExitCode==0,result.Stderr+result.Stdout);True(result.Stdout.Contains("SchemaEditing authoring/preservation/compiler PASS",StringComparison.Ordinal),result.Stderr);
   File.AppendAllText(Path.Combine(pack,"SetValue.csbody"),"\n// local authoring provider change\n");var changed=new Builder(project,"portable").Build();PackRebuilt(changed, new[]{"Confectory.SchemaEditing::SetValueBody"});Equal(0,Strings(changed,"statistics","compiledContracts").Length);
  }
  finally{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",selected);}
 }
}
