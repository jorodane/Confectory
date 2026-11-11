using Confectory.Core;
using System.Text.Json.Nodes;

// Compose explicit native out type replacements, never inferred conversions.
// Every old consumer chooses the retained compatible return; input contracts,
// other out identities and original single-source body proofs stay unchanged.
// Existing single edits accept either the retained out name or explicit null
// replacement; both still require every original consumer/body choice.
internal static class InformationFunctionNativeOutputs
{
 static bool Scalar(string type)=>type is "bool" or "int" or "long" or "float" or "double" or "string";
 public static bool Types(FunctionSignature before,FunctionSignature next,JsonObject args)=>before.Return==next.Return&&Scalar(before.Return)&&before.Args.Count==next.Args.Count&&args.Count==before.Args.Count&&before.Args.Where((a,i)=>a.Name!=next.Args[i].Name||a.Mode!=next.Args[i].Mode||a.Mode is not (null or "out")||!Scalar(a.Type)||!Scalar(next.Args[i].Type)||!args.ContainsKey(a.Name)||(a.Type==next.Args[i].Type?args[a.Name]?.ToString()!=a.Name:!a.IsOut||a.Type!=before.Return||args[a.Name] is not null&&args[a.Name]?.ToString()!=a.Name)).Any()==false&&before.Args.Where((a,i)=>a.Type!=next.Args[i].Type).Any();
 public static JsonNode?[]? Edits(JsonArray changes)
 {
  if(changes.Count is <2 or >8)return null;
  return changes.All(row=>InformationFunctionBodyBatch.BodyPlan(row)&&row!["mapping"] is JsonObject map&&map.Count==4&&map.All(p=>p.Key is "before" or "args" or "bodies" or "callers")&&map["args"] is JsonObject args&&map["callers"] is JsonObject callers&&callers.Count>0&&Types(InformationFunctionBodies.Signature(map["before"]!),InformationFunctionBodies.Signature(row["signature"]!),args))?changes.ToArray():null;
 }
 public static HashSet<string>? Prepare(JsonObject request,JsonArray changes,JsonObject units,Func<Element,string> format)
 {
  if(Edits(changes) is not {} edits)return null;
  foreach(var row in edits){
   var before=InformationFunctionBodies.Signature(row!["mapping"]!["before"]!);var next=InformationFunctionBodies.Signature(row["signature"]!);var outputs=FeatureBlueprint.FeatureOutputs(before).ToArray();
   foreach(var selection in row["mapping"]!["callers"]!.AsObject()){
    var plan=selection.Value as JsonObject??throw new InvalidOperationException("Review every original native out consumer explicitly");
    if(plan.Count!=6||plan.Any(p=>p.Key is not ("graph" or "node" or "hash" or "inputs" or "disconnect" or "outputs"))||plan["inputs"] is not JsonObject inputs||inputs.Count!=before.Args.Count(a=>!a.IsOut)||before.Args.Where(a=>!a.IsOut).Any(a=>inputs[a.Name]?.ToString()!=a.Name)||plan["disconnect"] is not JsonObject disconnect||disconnect.Count!=0||plan["outputs"] is not JsonObject remap||remap.Count!=outputs.Length||outputs.Any(a=>remap[a.Name]?.ToString()!=(a.Name!="return"&&before.Args.Any(b=>b.Name==a.Name&&b.IsOut&&b.Type!=next.Args.Single(c=>c.Name==b.Name).Type)?"return":a.Name)))throw new InvalidOperationException("Retain all input and unchanged output identities; explicitly choose the compatible retained return for every changed out consumer");
   }
  }
  return InformationFunctionNativeInputs.PrepareSources(request,edits,units,format);
 }
}
