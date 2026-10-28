using Confectory.Core;
using System.Text.Json.Nodes;

// Explicit whole-value replacement only. A changed output never inherits a
// guessed conversion, and every original assignment/exit keeps its identity.
internal static class BlueprintOutputBindings
{
 internal sealed record Assignment(string Name,string Type,JsonNode Value);
 internal static IEnumerable<(string Node,JsonNode? Value)> Writers(JsonObject graph,string name)
 {
  var writers=graph["nodes"]!.AsArray().Where(n=>n!["kind"]?.ToString()=="export"&&n["output"]?.ToString()==name).ToArray();
  foreach(var node in writers)yield return(node!["id"]!.ToString(),node["arguments"]?["value"]);
  if(writers.Length==0||graph["exits"]?[name] is not null)yield return("$exit:"+name,graph["exits"]?[name]);
 }
 internal static IEnumerable<(string Name,string Type)> Outputs(JsonObject node)
 {
  if(node["kind"]?.ToString()=="set"&&node["outputLocal"] is not null){yield return("stored",node["signature"]!["args"]![0]!["type"]!.ToString());yield break;}
  string type=node["signature"]!["return"]!.ToString();if(type!="void")yield return("return",type);
  foreach(var arg in node["signature"]!["args"]!.AsArray().Where(p=>p!["mode"]?.ToString()=="out"))yield return(arg!["name"]!.ToString(),arg["type"]!.ToString());
 }
 internal static void Value(JsonObject graph,FunctionSignature signature,JsonNode? value,string type,int depth=0)
 {
  if(depth>12||value is not JsonObject binding)throw new ArgumentException("Bounded explicit typed output value required");
  if(binding.ContainsKey("constant")){if(binding.Count!=1)throw new ArgumentException("A replacement literal has its selected exact output type");FeatureBlueprint.ValidateConstant(binding["constant"],type);return;}
  if(binding.Count==1&&binding["input"] is JsonValue input&&input.TryGetValue<string>(out var name)&&signature.Args.Any(a=>!a.IsOut&&a.Name==name&&a.Type==type))return;
  if(binding["node"] is JsonValue source&&source.TryGetValue<string>(out var node)&&binding.Count is 1 or 2&&binding.All(p=>p.Key is "node" or "output")){var found=graph["nodes"]!.AsArray().OfType<JsonObject>().SingleOrDefault(n=>n["id"]?.ToString()==node);if(found is not null&&Outputs(found).Any(p=>p.Name==(binding["output"]?.ToString()??"return")&&p.Type==type))return;}
  // A selected alias keeps its declared type and identity. Its source is checked
  // by the complete graph validator after explicit input restorations, so an
  // intermediate old source never substitutes for the final current binding.
  if(binding.Count==1&&binding["local"] is JsonValue local&&local.TryGetValue<string>(out var id)&&(graph["locals"] as JsonArray??new()).OfType<JsonObject>().Any(n=>n["id"]?.ToString()==id&&n["type"]?.ToString()==type))return;
  if(binding.Count==1&&binding["binary"] is JsonObject binary&&binary.Count is 2 or 3&&binary.All(p=>p.Key is "operator" or "operands" or "type")&&(binary["type"] is null||binary["type"]!.ToString()==type)&&binary["operands"] is JsonArray operands&&operands.Count==2){
   string op=binary["operator"]?.ToString()??"";
   if(!(type is "int" or "long" or "float" or "double"?op is "+" or "-" or "*" or "/" or "%":type=="string"?op=="+":type=="bool"&&op is "AND" or "OR" or "XOR"))throw new InvalidOperationException("Unsupported output expression operator");
   if(op is "/" or "%"&&operands[1] is JsonObject divisor&&divisor["constant"] is JsonValue constant){var number=System.Text.Json.JsonSerializer.SerializeToElement(constant);if(number.ValueKind==System.Text.Json.JsonValueKind.Number&&number.GetDouble()==0)throw new InvalidOperationException("Output expression divisor is zero");}
   foreach(var operand in operands)Value(graph,signature,operand,type,depth+1);return;
  }
  throw new InvalidOperationException("Select an exact compatible output value; implicit conversions are not applied");
 }
 internal static Dictionary<string,Assignment> Prepare(JsonObject graph,FunctionSignature old,FunctionSignature next,JsonObject remap,JsonArray rows)
 {
  if(rows.Count>384)throw new ArgumentException("Output assignment budget");
  var wanted=new Dictionary<string,(string Name,string Type,JsonNode? Before)>(StringComparer.Ordinal);var after=FeatureBlueprint.FeatureOutputs(next).ToDictionary(p=>p.Name,p=>p.Type,StringComparer.Ordinal);
  foreach(var output in FeatureBlueprint.FeatureOutputs(old)){string? name=output.Name=="return"?next.Return!="void"?"return":null:remap[output.Name]?.GetValue<string>();if(name is null||!after.TryGetValue(name,out string? type)||type==output.Type)continue;foreach(var writer in Writers(graph,output.Name))wanted.Add(writer.Node,(output.Name,type,writer.Value));}
  if(rows.Count!=wanted.Count)throw new InvalidOperationException("Select every writer and exit of every changed output");var result=new Dictionary<string,Assignment>(StringComparer.Ordinal);
  foreach(var item in rows){var row=item!.AsObject();if(row.Count!=5||row.Any(p=>p.Key is not ("node" or "name" or "type" or "before" or "valueJson")))throw new ArgumentException("Exact original output assignment and replacement required");string id=row["node"]!.GetValue<string>();if(!wanted.TryGetValue(id,out var expected)||row["name"]?.ToString()!=expected.Name||row["type"]?.ToString()!=expected.Type||row["before"]?.ToString()!=(expected.Before?.ToJsonString()??"null")||result.ContainsKey(id))throw new InvalidOperationException("Original output assignment changed; retain every input");string text=row["valueJson"]!.GetValue<string>();if(text.Length>65536)throw new ArgumentException("Output value budget");var value=JsonNode.Parse(text);Value(graph,next,value,expected.Type);result.Add(id,new(expected.Name,expected.Type,value!));}
  return result;
 }
}
