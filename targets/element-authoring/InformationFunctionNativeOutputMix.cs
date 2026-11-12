using Confectory.Core;
using System.Text.Json.Nodes;

// Combine the existing explicit out/return type choices against the original
// source. A changed output can use only an explicitly selected, retained output
// of its old type; no cast, default or consumer deletion is inferred.
internal static class InformationFunctionNativeOutputMix
{
 static bool Scalar(string type)=>type is "bool" or "int" or "long" or "float" or "double" or "string";
 public static bool Types(FunctionSignature before,FunctionSignature next,JsonObject args)=>Scalar(before.Return)&&Scalar(next.Return)&&before.Args.Count==next.Args.Count&&args.Count==before.Args.Count&&before.Args.Where((a,i)=>a.Name!=next.Args[i].Name||a.Mode!=next.Args[i].Mode||a.Mode is not (null or "out")||!Scalar(a.Type)||!Scalar(next.Args[i].Type)||!args.ContainsKey(a.Name)||(a.Type==next.Args[i].Type?args[a.Name]?.ToString()!=a.Name:!a.IsOut||args[a.Name] is not null&&args[a.Name]?.ToString()!=a.Name)).Any()==false&&(before.Return!=next.Return||before.Args.Where((a,i)=>a.Type!=next.Args[i].Type).Any());
 public static JsonNode?[]? Edits(JsonArray changes)
 {
  if(changes.Count is <2 or >8||!changes.All(row=>InformationFunctionBodyBatch.BodyPlan(row)&&row!["mapping"] is JsonObject map&&map.Count==4&&map.All(p=>p.Key is "before" or "args" or "bodies" or "callers")&&map["args"] is JsonObject args&&map["callers"] is JsonObject callers&&callers.Count>0&&Types(InformationFunctionBodies.Signature(map["before"]!),InformationFunctionBodies.Signature(row["signature"]!),args)))return null;
  var pairs=changes.Select(row=>(Before:InformationFunctionBodies.Signature(row!["mapping"]!["before"]!),Next:InformationFunctionBodies.Signature(row["signature"]!))).ToArray();
  return pairs.Any(p=>p.Before.Return!=p.Next.Return)&&pairs.Any(p=>p.Before.Args.Where((a,i)=>a.Type!=p.Next.Args[i].Type).Any())?changes.ToArray():null;
 }
 public static HashSet<string>? Prepare(JsonObject request,JsonArray changes,JsonObject units,Func<Element,string> format)
 {
  if(Edits(changes) is not {} edits)return null;
  foreach(var row in edits){
   var before=InformationFunctionBodies.Signature(row!["mapping"]!["before"]!);var next=InformationFunctionBodies.Signature(row["signature"]!);var outputs=FeatureBlueprint.FeatureOutputs(before).ToArray();var targets=FeatureBlueprint.FeatureOutputs(next).ToArray();
   foreach(var selection in row["mapping"]!["callers"]!.AsObject()){
    var plan=selection.Value as JsonObject??throw new InvalidOperationException("Review every original native out and return consumer explicitly");
    if(plan.Count!=6||plan.Any(p=>p.Key is not ("graph" or "node" or "hash" or "inputs" or "disconnect" or "outputs"))||plan["inputs"] is not JsonObject inputs||inputs.Count!=before.Args.Count(a=>!a.IsOut)||before.Args.Where(a=>!a.IsOut).Any(a=>inputs[a.Name]?.ToString()!=a.Name)||plan["disconnect"] is not JsonObject disconnect||disconnect.Count!=0||plan["outputs"] is not JsonObject remap||remap.Count!=outputs.Length||outputs.Any(a=>{
     if(remap[a.Name] is not JsonValue value||!value.TryGetValue<string>(out string? name))return true;
     if(targets.Any(b=>b.Name==a.Name&&b.Type==a.Type))return name!=a.Name;
     return !targets.Any(b=>b.Name==name&&b.Type==a.Type&&outputs.Any(c=>c.Name==b.Name&&c.Type==b.Type));
    }))throw new InvalidOperationException("Retain every input and unchanged output identity; select an exact compatible retained output for each changed out/return consumer");
   }
  }
  // Each member must still validate independently against the complete original
  // contract, native declaration/text, source guards and explicit caller plan.
  return InformationFunctionNativeInputs.PrepareSources(request,edits,units,format);
 }
}
