using Confectory.Core;
using System.Text.Json.Nodes;

// A native return replacement owns its explicitly authored declaration/text.
// Existing consumers choose an exact compatible retained out pin. The single
// closure and shared-caller projection prove those original output choices.
internal static class InformationFunctionNativeReturns
{
 static bool Scalar(string type)=>type is "bool" or "int" or "long" or "float" or "double" or "string";
 public static bool Types(FunctionSignature before,FunctionSignature next,JsonObject args)=>before.Return!=next.Return&&Scalar(before.Return)&&(Scalar(next.Return)||next.Return=="void")&&before.Args.SequenceEqual(next.Args)&&args.Count==before.Args.Count&&before.Args.All(a=>Scalar(a.Type)&&(a.Mode is null or "out")&&args[a.Name]?.ToString()==a.Name)&&before.Args.Any(a=>a.IsOut&&a.Type==before.Return);
 public static JsonNode?[]? Edits(JsonArray changes)
 {
  if(changes.Count is <2 or >8)return null;
  return changes.All(row=>InformationFunctionBodyBatch.BodyPlan(row)&&row!["mapping"] is JsonObject map&&map.Count==4&&map.All(p=>p.Key is "before" or "args" or "bodies" or "callers")&&map["args"] is JsonObject args&&map["callers"] is JsonObject callers&&callers.Count>0&&Types(InformationFunctionBodies.Signature(map["before"]!),InformationFunctionBodies.Signature(row["signature"]!),args))?changes.ToArray():null;
 }
 public static HashSet<string>? Prepare(JsonObject request,JsonArray changes,JsonObject units,Func<Element,string> format)
 {
  if(Edits(changes) is not {} edits)return null;
  foreach(var row in edits){
   var before=InformationFunctionBodies.Signature(row!["mapping"]!["before"]!);var outputs=FeatureBlueprint.FeatureOutputs(before).ToArray();
   foreach(var selection in row["mapping"]!["callers"]!.AsObject()){
    var plan=selection.Value as JsonObject??throw new InvalidOperationException("Review every original native return consumer explicitly");
    if(plan.Count!=6||plan.Any(p=>p.Key is not ("graph" or "node" or "hash" or "inputs" or "disconnect" or "outputs"))||plan["inputs"] is not JsonObject inputs||inputs.Count!=before.Args.Count(a=>!a.IsOut)||before.Args.Where(a=>!a.IsOut).Any(a=>inputs[a.Name]?.ToString()!=a.Name)||plan["disconnect"] is not JsonObject disconnect||disconnect.Count!=0||plan["outputs"] is not JsonObject remap||remap.Count!=outputs.Length||before.Args.Where(a=>a.IsOut).Any(a=>remap[a.Name]?.ToString()!=a.Name)||remap["return"] is not JsonValue target||!target.TryGetValue<string>(out string? name)||!before.Args.Any(a=>a.IsOut&&a.Name==name&&a.Type==before.Return))throw new InvalidOperationException("Retain all inputs/out identities and explicitly choose a compatible original out for every old return consumer; no conversion is inferred");
   }
  }
  return InformationFunctionNativeInputs.PrepareSources(request,edits,units,format);
 }
}
