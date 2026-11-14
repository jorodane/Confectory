using Confectory.Core;
using System.Text.Json.Nodes;

// Explicit value/ref/out roles retain original names, types, order and C# text.
// Removed inputs, newly selected values and lost output consumers are proved
// against ORIGINAL sources; the implementation never invents a binding.
internal static class InformationFunctionNativeRoles
{
 static bool Scalar(string type)=>type is "bool" or "int" or "long" or "float" or "double" or "string";
 static bool Role(FunctionSignature before,FunctionSignature next,JsonObject args,bool toValue)=>before.Return==next.Return&&Scalar(before.Return)&&before.Args.Count==next.Args.Count&&args.Count==before.Args.Count&&before.Args.Where((a,i)=>a.Name!=next.Args[i].Name||a.Type!=next.Args[i].Type||!Scalar(a.Type)||a.Mode is not (null or "out")||a.Mode!=next.Args[i].Mode&&!(toValue?a.IsOut&&next.Args[i].Mode is null&&a.Type==before.Return:a.Mode is null&&next.Args[i].IsOut)||args[a.Name]?.ToString()!=a.Name).Any()==false&&before.Args.Where((a,i)=>a.Mode!=next.Args[i].Mode).Any();
 static bool RefOut(FunctionSignature before,FunctionSignature next,JsonObject args)=>before.Return==next.Return&&Scalar(before.Return)&&before.Args.Count==next.Args.Count&&args.Count==before.Args.Count&&before.Args.Where((a,i)=>a.Name!=next.Args[i].Name||a.Type!=next.Args[i].Type||!Scalar(a.Type)||a.Mode is not (null or "out" or "ref")||a.Mode!=next.Args[i].Mode&&!(a.IsRef&&next.Args[i].IsOut)||args[a.Name]?.ToString()!=a.Name).Any()==false&&before.Args.Where((a,i)=>a.IsRef&&next.Args[i].IsOut).Any();
 static bool RefValue(FunctionSignature before,FunctionSignature next,JsonObject args)=>before.Return==next.Return&&Scalar(before.Return)&&before.Args.Count==next.Args.Count&&args.Count==before.Args.Count&&before.Args.Where((a,i)=>a.Name!=next.Args[i].Name||a.Type!=next.Args[i].Type||!Scalar(a.Type)||a.Mode is not (null or "out" or "ref")||a.Mode!=next.Args[i].Mode&&!(a.IsRef&&next.Args[i].Mode is null)||args[a.Name]?.ToString()!=a.Name).Any()==false&&before.Args.Where((a,i)=>a.IsRef&&next.Args[i].Mode is null).Any();
 static bool ValueRef(FunctionSignature before,FunctionSignature next,JsonObject args)=>before.Return==next.Return&&Scalar(before.Return)&&before.Args.Count==next.Args.Count&&args.Count==before.Args.Count&&before.Args.Where((a,i)=>a.Name!=next.Args[i].Name||a.Type!=next.Args[i].Type||!Scalar(a.Type)||a.Mode is not (null or "out" or "ref")||a.Mode!=next.Args[i].Mode&&!(a.Mode is null&&next.Args[i].IsRef)||args[a.Name]?.ToString()!=a.Name).Any()==false&&before.Args.Where((a,i)=>a.Mode is null&&next.Args[i].IsRef).Any();
 static bool OutRef(FunctionSignature before,FunctionSignature next,JsonObject args)=>before.Return==next.Return&&Scalar(before.Return)&&before.Args.Count==next.Args.Count&&args.Count==before.Args.Count&&before.Args.Where((a,i)=>a.Name!=next.Args[i].Name||a.Type!=next.Args[i].Type||!Scalar(a.Type)||a.Mode is not (null or "out" or "ref")||a.Mode!=next.Args[i].Mode&&!(a.IsOut&&next.Args[i].IsRef&&a.Type==before.Return)||args[a.Name]?.ToString()!=a.Name).Any()==false&&before.Args.Where((a,i)=>a.IsOut&&next.Args[i].IsRef).Any();
 public static bool Types(FunctionSignature before,FunctionSignature next,JsonObject args)=>Role(before,next,args,false)||Role(before,next,args,true)||RefOut(before,next,args)||RefValue(before,next,args)||ValueRef(before,next,args)||OutRef(before,next,args);
 static bool ToValue(FunctionSignature before,FunctionSignature next)=>before.Args.Where((a,i)=>a.IsOut&&next.Args[i].Mode is null).Any();
 internal static string Direction(FunctionSignature before,FunctionSignature next)=>before.Args.Where((a,i)=>a.IsRef&&next.Args[i].IsOut).Any()?"ref-out":before.Args.Where((a,i)=>a.IsRef&&next.Args[i].Mode is null).Any()?"ref-value":before.Args.Where((a,i)=>a.Mode is null&&next.Args[i].IsRef).Any()?"value-ref":before.Args.Where((a,i)=>a.IsOut&&next.Args[i].IsRef).Any()?"out-ref":ToValue(before,next)?"out-value":"value-out";
 static bool ExplicitValue(JsonNode? value)=>value is JsonObject literal&&literal.Count==1&&literal["valueJson"] is JsonValue text&&text.TryGetValue<string>(out _);
 static bool ExplicitRef(JsonNode? value)=>value is JsonObject choice&&choice.Count==1&&choice["binding"] is JsonObject source&&source.Count==1&&source["input"] is JsonValue name&&name.TryGetValue<string>(out _);
 public static JsonNode?[]? Edits(JsonArray changes)
 {
  if(changes.Count is <2 or >8||!changes.All(row=>InformationFunctionBodyBatch.BodyPlan(row)&&row!["mapping"] is JsonObject map&&map.Count==4&&map.All(p=>p.Key is "before" or "args" or "bodies" or "callers")&&map["args"] is JsonObject args&&map["callers"] is JsonObject callers&&callers.Count>0&&Types(InformationFunctionBodies.Signature(map["before"]!),InformationFunctionBodies.Signature(row["signature"]!),args)))return null;
  // One direction per transaction retains independent original input/output
  // proofs; mixed role directions are not inferred or rebased.
  return changes.Select(row=>Direction(InformationFunctionBodies.Signature(row!["mapping"]!["before"]!),InformationFunctionBodies.Signature(row["signature"]!))).Distinct().Count()==1?changes.ToArray():null;
 }
 public static HashSet<string>? Prepare(JsonObject request,JsonArray changes,JsonObject units,Func<Element,string> format,InformationFunctionNativeJoint? joint=null)
 {
  if(Edits(changes) is not {} edits)return null;
  foreach(var row in edits){
   var before=InformationFunctionBodies.Signature(row!["mapping"]!["before"]!);var next=InformationFunctionBodies.Signature(row["signature"]!);bool toValue=ToValue(before,next),toRef=Direction(before,next)=="out-ref";var removed=before.Args.Where((a,i)=>(a.Mode is null||a.IsRef)&&next.Args[i].IsOut).Select(a=>a.Name).ToHashSet(StringComparer.Ordinal);var outputs=FeatureBlueprint.FeatureOutputs(before).ToArray();
   foreach(var selection in row["mapping"]!["bodies"]!.AsObject()){
    var plan=selection.Value!.AsObject();var nativeBefore=InformationFunctionBodies.Signature(plan["beforeSignature"]!);var nativeNext=InformationFunctionBodies.Signature(plan["signature"]!);var identity=new JsonObject(nativeBefore.Args.Select(a=>KeyValuePair.Create<string,JsonNode?>(a.Name,JsonValue.Create(a.Name))));
    if(!before.Matches(nativeBefore)||!next.Matches(nativeNext)||!Types(nativeBefore,nativeNext,identity))throw new InvalidOperationException("Native value/out/ref roles retain exact original aliases, types, count, order and return");
   }
   foreach(var selection in row["mapping"]!["callers"]!.AsObject()){
    var plan=selection.Value as JsonObject??throw new InvalidOperationException("Review each original value/out/ref caller explicitly");
    if(plan.Count!=6||plan.Any(p=>p.Key is not ("graph" or "node" or "hash" or "inputs" or "disconnect" or "outputs"))||plan["inputs"] is not JsonObject inputs||inputs.Count!=next.Args.Count(a=>!a.IsOut)||next.Args.Where(a=>!a.IsOut).Any(a=>before.Args.Single(b=>b.Name==a.Name).IsOut?!(a.IsRef?ExplicitRef(inputs[a.Name]):ExplicitValue(inputs[a.Name])):inputs[a.Name]?.ToString()!=a.Name)||plan["disconnect"] is not JsonObject disconnect||disconnect.Count!=removed.Count||disconnect.Any(p=>!removed.Contains(p.Key))||plan["outputs"] is not JsonObject remap||remap.Count!=outputs.Length||outputs.Any(a=>remap[a.Name]?.ToString()!=((toValue||toRef)&&a.Name!="return"&&!next.Args.Any(b=>b.Name==a.Name&&b.IsOut)?"return":a.Name)))throw new InvalidOperationException("Explicitly select new inputs, disconnect removed inputs and map lost outs to the compatible return; retain all other identities");
   }
  }
  // The existing single-function proof checks exact values/disconnections, compatible output consumers and C#.
  return InformationFunctionNativeInputs.PrepareSources(request,edits,units,format,joint);
 }
}
