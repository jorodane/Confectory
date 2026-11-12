using Confectory.Core;
using System.Text.Json.Nodes;

// Explicit value-to-out roles keep original names, types, order and C# text.
// Every removed input is selected against its ORIGINAL caller binding.
internal static class InformationFunctionNativeRoles
{
 static bool Scalar(string type)=>type is "bool" or "int" or "long" or "float" or "double" or "string";
 public static bool Types(FunctionSignature before,FunctionSignature next,JsonObject args)=>before.Return==next.Return&&Scalar(before.Return)&&before.Args.Count==next.Args.Count&&args.Count==before.Args.Count&&before.Args.Where((a,i)=>a.Name!=next.Args[i].Name||a.Type!=next.Args[i].Type||!Scalar(a.Type)||a.Mode is not (null or "out")||a.Mode!=next.Args[i].Mode&&!(a.Mode is null&&next.Args[i].IsOut)||args[a.Name]?.ToString()!=a.Name).Any()==false&&before.Args.Where((a,i)=>a.Mode is null&&next.Args[i].IsOut).Any();
 public static JsonNode?[]? Edits(JsonArray changes)
 {
  if(changes.Count is <2 or >8)return null;
  return changes.All(row=>InformationFunctionBodyBatch.BodyPlan(row)&&row!["mapping"] is JsonObject map&&map.Count==4&&map.All(p=>p.Key is "before" or "args" or "bodies" or "callers")&&map["args"] is JsonObject args&&map["callers"] is JsonObject callers&&callers.Count>0&&Types(InformationFunctionBodies.Signature(map["before"]!),InformationFunctionBodies.Signature(row["signature"]!),args))?changes.ToArray():null;
 }
 public static HashSet<string>? Prepare(JsonObject request,JsonArray changes,JsonObject units,Func<Element,string> format)
 {
  if(Edits(changes) is not {} edits)return null;
  foreach(var row in edits){
   var before=InformationFunctionBodies.Signature(row!["mapping"]!["before"]!);var next=InformationFunctionBodies.Signature(row["signature"]!);var removed=before.Args.Where((a,i)=>a.Mode is null&&next.Args[i].IsOut).Select(a=>a.Name).ToHashSet(StringComparer.Ordinal);var outputs=FeatureBlueprint.FeatureOutputs(before).ToArray();
   foreach(var selection in row["mapping"]!["bodies"]!.AsObject()){
    var plan=selection.Value!.AsObject();var nativeBefore=InformationFunctionBodies.Signature(plan["beforeSignature"]!);var nativeNext=InformationFunctionBodies.Signature(plan["signature"]!);var identity=new JsonObject(nativeBefore.Args.Select(a=>KeyValuePair.Create<string,JsonNode?>(a.Name,JsonValue.Create(a.Name))));
    if(!before.Matches(nativeBefore)||!next.Matches(nativeNext)||!Types(nativeBefore,nativeNext,identity))throw new InvalidOperationException("Native value-to-out roles retain exact original aliases, types, count, order and return");
   }
   foreach(var selection in row["mapping"]!["callers"]!.AsObject()){
    var plan=selection.Value as JsonObject??throw new InvalidOperationException("Review each original value-to-out caller explicitly");
    if(plan.Count!=6||plan.Any(p=>p.Key is not ("graph" or "node" or "hash" or "inputs" or "disconnect" or "outputs"))||plan["inputs"] is not JsonObject inputs||inputs.Count!=next.Args.Count(a=>!a.IsOut)||next.Args.Where(a=>!a.IsOut).Any(a=>inputs[a.Name]?.ToString()!=a.Name)||plan["disconnect"] is not JsonObject disconnect||disconnect.Count!=removed.Count||disconnect.Any(p=>!removed.Contains(p.Key))||plan["outputs"] is not JsonObject remap||remap.Count!=outputs.Length||outputs.Any(a=>remap[a.Name]?.ToString()!=a.Name))throw new InvalidOperationException("Explicitly disconnect converted inputs and retain every other input/output identity");
   }
  }
  // The existing single-function proof checks exact disconnect values and C#.
  return InformationFunctionNativeInputs.PrepareSources(request,edits,units,format);
 }
}
