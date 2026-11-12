using Confectory.Core;
using System.Text.Json.Nodes;

// Compose explicit native out edits, never inferred conversions. Replacements
// and removals choose a compatible retained return for the affected consumers.
// Additions retain every old binding and append only explicitly authored outs.
// Existing single edits accept either the retained out name or explicit null
// replacement; both still require every original consumer/body choice.
internal static class InformationFunctionNativeOutputs
{
 static bool Scalar(string type)=>type is "bool" or "int" or "long" or "float" or "double" or "string";
 public static bool Types(FunctionSignature before,FunctionSignature next,JsonObject args)=>Replacement(before,next,args)||Removal(before,next,args)||Addition(before,next,args);
 static bool Replacement(FunctionSignature before,FunctionSignature next,JsonObject args)=>before.Return==next.Return&&Scalar(before.Return)&&before.Args.Count==next.Args.Count&&args.Count==before.Args.Count&&before.Args.Where((a,i)=>a.Name!=next.Args[i].Name||a.Mode!=next.Args[i].Mode||a.Mode is not (null or "out")||!Scalar(a.Type)||!Scalar(next.Args[i].Type)||!args.ContainsKey(a.Name)||(a.Type==next.Args[i].Type?args[a.Name]?.ToString()!=a.Name:!a.IsOut||a.Type!=before.Return||args[a.Name] is not null&&args[a.Name]?.ToString()!=a.Name)).Any()==false&&before.Args.Where((a,i)=>a.Type!=next.Args[i].Type).Any();
 static bool Removal(FunctionSignature before,FunctionSignature next,JsonObject args)=>before.Return==next.Return&&Scalar(before.Return)&&next.Args.Count<before.Args.Count&&args.Count==before.Args.Count&&before.Args.All(a=>Scalar(a.Type)&&(a.Mode is null or "out")&&args.ContainsKey(a.Name)&&(next.Args.Contains(a)?args[a.Name]?.ToString()==a.Name:a.IsOut&&a.Type==before.Return&&args[a.Name] is null))&&before.Args.Where(a=>next.Args.Any(b=>b.Name==a.Name)).SequenceEqual(next.Args);
 static bool Addition(FunctionSignature before,FunctionSignature next,JsonObject args)=>before.Return==next.Return&&Scalar(before.Return)&&next.Args.Count>before.Args.Count&&args.Count==before.Args.Count&&before.Args.All(a=>Scalar(a.Type)&&(a.Mode is null or "out")&&args[a.Name]?.ToString()==a.Name)&&next.Args.Take(before.Args.Count).SequenceEqual(before.Args)&&next.Args.Skip(before.Args.Count).All(a=>a.IsOut&&Scalar(a.Type))&&next.Args.Select(a=>a.Name).Distinct(StringComparer.Ordinal).Count()==next.Args.Count;
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
    if(plan.Count!=6||plan.Any(p=>p.Key is not ("graph" or "node" or "hash" or "inputs" or "disconnect" or "outputs"))||plan["inputs"] is not JsonObject inputs||inputs.Count!=before.Args.Count(a=>!a.IsOut)||before.Args.Where(a=>!a.IsOut).Any(a=>inputs[a.Name]?.ToString()!=a.Name)||plan["disconnect"] is not JsonObject disconnect||disconnect.Count!=0||plan["outputs"] is not JsonObject remap||remap.Count!=outputs.Length||outputs.Any(a=>remap[a.Name]?.ToString()!=(a.Name!="return"&&before.Args.Any(b=>b.Name==a.Name&&b.IsOut&&!next.Args.Any(c=>c.Name==b.Name&&c.Type==b.Type))?"return":a.Name)))throw new InvalidOperationException("Retain all input and unchanged output identities; explicitly choose the compatible retained return for every changed or removed out consumer");
   }
  }
  return InformationFunctionNativeInputs.PrepareSources(request,edits,units,format);
 }
}
