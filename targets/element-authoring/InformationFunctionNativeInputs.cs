using Confectory.Core;
using System.Text.Json.Nodes;

// Compose explicit single-function native input types and definition changes.
// New values, removed bindings, native signatures and C# text remain choices
// made against each complete ORIGINAL source, never inferred conversions.
internal static class InformationFunctionNativeInputs
{
 static bool Scalar(string type)=>type is "bool" or "int" or "long" or "float" or "double" or "string";
 public static bool Types(FunctionSignature before,FunctionSignature next,JsonObject args)=>Replacement(before,next,args)||Addition(before,next,args)||Removal(before,next,args)||Definitions(before,next,args);
 static bool Replacement(FunctionSignature before,FunctionSignature next,JsonObject args)=>before.Return==next.Return&&(before.Return=="void"||Scalar(before.Return))&&before.Args.Count==next.Args.Count&&args.Count==before.Args.Count&&before.Args.Where((a,i)=>a.Name!=next.Args[i].Name||a.Mode is not null||next.Args[i].Mode is not null||!Scalar(a.Type)||!Scalar(next.Args[i].Type)||!args.ContainsKey(a.Name)||(a.Type==next.Args[i].Type?args[a.Name]?.ToString()!=a.Name:args[a.Name] is not null)).Any()==false&&before.Args.Where((a,i)=>a.Type!=next.Args[i].Type).Any();
 static bool Addition(FunctionSignature before,FunctionSignature next,JsonObject args)=>before.Return==next.Return&&(before.Return=="void"||Scalar(before.Return))&&next.Args.Count>before.Args.Count&&args.Count==before.Args.Count&&before.Args.All(a=>a.Mode is null&&Scalar(a.Type)&&args[a.Name]?.ToString()==a.Name)&&next.Args.Take(before.Args.Count).SequenceEqual(before.Args)&&next.Args.Skip(before.Args.Count).All(a=>a.Mode is null&&Scalar(a.Type))&&next.Args.Select(a=>a.Name).Distinct(StringComparer.Ordinal).Count()==next.Args.Count;
 static bool Removal(FunctionSignature before,FunctionSignature next,JsonObject args)=>before.Return==next.Return&&(before.Return=="void"||Scalar(before.Return))&&next.Args.Count<before.Args.Count&&args.Count==before.Args.Count&&before.Args.All(a=>a.Mode is null&&Scalar(a.Type)&&args.ContainsKey(a.Name)&&(next.Args.Contains(a)?args[a.Name]?.ToString()==a.Name:args[a.Name] is null))&&next.Args.SequenceEqual(before.Args.Where(a=>next.Args.Contains(a)));
 static bool Definitions(FunctionSignature before,FunctionSignature next,JsonObject args)=>before.Return==next.Return&&(before.Return=="void"||Scalar(before.Return))&&args.Count==before.Args.Count&&before.Args.Any(a=>!next.Args.Any(b=>b.Name==a.Name))&&next.Args.Any(a=>!before.Args.Any(b=>b.Name==a.Name))&&before.Args.All(a=>a.Mode is null&&Scalar(a.Type)&&args.ContainsKey(a.Name)&&(next.Args.Contains(a)?args[a.Name]?.ToString()==a.Name:args[a.Name] is null))&&next.Args.All(a=>a.Mode is null&&Scalar(a.Type))&&next.Args.SequenceEqual(before.Args.Where(a=>next.Args.Contains(a)).Concat(next.Args.Where(a=>!before.Args.Any(b=>b.Name==a.Name))))&&next.Args.Select(a=>a.Name).Distinct(StringComparer.Ordinal).Count()==next.Args.Count;
 static bool ExplicitValue(JsonNode? value)=>value is JsonObject literal&&literal.Count==1&&literal["valueJson"] is JsonValue text&&text.TryGetValue<string>(out _);
 public static JsonNode?[]? Edits(JsonArray changes)
 {
  if(changes.Count is <2 or >8)return null;
  return changes.All(row=>InformationFunctionBodyBatch.BodyPlan(row)&&row!["mapping"] is JsonObject map&&map.Count==4&&map.All(p=>p.Key is "before" or "args" or "bodies" or "callers")&&map["args"] is JsonObject args&&map["callers"] is JsonObject&&Types(InformationFunctionBodies.Signature(map["before"]!),InformationFunctionBodies.Signature(row["signature"]!),args))?changes.ToArray():null;
 }
 public static HashSet<string>? Prepare(JsonObject request,JsonArray changes,JsonObject units,Func<Element,string> format)
 {
  if(Edits(changes) is not {} edits)return null;
  foreach(var row in edits){
   var before=InformationFunctionBodies.Signature(row!["mapping"]!["before"]!);var next=InformationFunctionBodies.Signature(row["signature"]!);
   if(Definitions(before,next,row["mapping"]!["args"]!.AsObject())){
    var removed=before.Args.Where(a=>!next.Args.Contains(a)).Select(a=>a.Name).ToArray();var added=next.Args.Where(a=>!before.Args.Any(b=>b.Name==a.Name)).ToArray();
    if(row["mapping"]!["callers"]!.AsObject().Count==0)throw new InvalidOperationException("Review original callers, disconnect removed inputs and select every new value explicitly");
    foreach(var selection in row["mapping"]!["bodies"]!.AsObject()){
     var plan=selection.Value!.AsObject();var nativeBefore=InformationFunctionBodies.Signature(plan["beforeSignature"]!);var nativeNext=InformationFunctionBodies.Signature(plan["signature"]!);
     if(!before.Matches(nativeBefore)||!next.Matches(nativeNext)||!nativeNext.Args.Take(next.Args.Count-added.Length).SequenceEqual(before.Args.Select((a,i)=>(a,i)).Where(p=>next.Args.Contains(p.a)).Select(p=>nativeBefore.Args[p.i]))||nativeNext.Args.Select(a=>a.Name).Distinct(StringComparer.Ordinal).Count()!=nativeNext.Args.Count)throw new InvalidOperationException("Retain surviving native aliases, types and order; explicitly select the appended value declarations and body");
    }
    foreach(var selection in row["mapping"]!["callers"]!.AsObject()){
     if(selection.Value is not JsonObject plan||plan.Count!=5||plan.Any(p=>p.Key is not ("graph" or "node" or "hash" or "inputs" or "disconnect"))||plan["inputs"] is not JsonObject inputs||inputs.Count!=next.Args.Count||next.Args.Where(a=>before.Args.Contains(a)).Any(a=>inputs[a.Name]?.ToString()!=a.Name)||added.Any(a=>!ExplicitValue(inputs[a.Name]))||plan["disconnect"] is not JsonObject disconnect||disconnect.Count!=removed.Length||removed.Any(name=>disconnect[name] is not JsonValue value||!value.TryGetValue<string>(out _)))throw new InvalidOperationException("Retain surviving bindings and outputs; explicitly select every new value and disconnect each exact original removed binding");
    }
    continue;
   }
   if(next.Args.Count==before.Args.Count)continue;
   if(next.Args.Count<before.Args.Count){
    var removed=before.Args.Where(a=>!next.Args.Contains(a)).Select(a=>a.Name).ToArray();
    if(row["mapping"]!["callers"]!.AsObject().Count==0)throw new InvalidOperationException("Review original callers and explicitly disconnect every removed input");
    foreach(var selection in row["mapping"]!["bodies"]!.AsObject()){
     var plan=selection.Value!.AsObject();var nativeBefore=InformationFunctionBodies.Signature(plan["beforeSignature"]!);var nativeNext=InformationFunctionBodies.Signature(plan["signature"]!);
     if(!before.Matches(nativeBefore)||!next.Matches(nativeNext)||!nativeNext.Args.SequenceEqual(before.Args.Select((a,i)=>(a,i)).Where(p=>next.Args.Contains(p.a)).Select(p=>nativeBefore.Args[p.i])))throw new InvalidOperationException("Retain surviving native parameter names, types and order when removing explicit scalar inputs");
    }
    foreach(var selection in row["mapping"]!["callers"]!.AsObject()){
     if(selection.Value is not JsonObject plan||plan.Count!=5||plan.Any(p=>p.Key is not ("graph" or "node" or "hash" or "inputs" or "disconnect"))||plan["inputs"] is not JsonObject inputs||inputs.Count!=next.Args.Count||next.Args.Any(a=>inputs[a.Name]?.ToString()!=a.Name)||plan["disconnect"] is not JsonObject disconnect||disconnect.Count!=removed.Length||removed.Any(name=>disconnect[name] is not JsonValue value||!value.TryGetValue<string>(out _)))throw new InvalidOperationException("Retain surviving bindings and outputs; explicitly disconnect each exact original removed input");
    }
    continue;
   }
   if(row["mapping"]!["callers"]!.AsObject().Count==0)throw new InvalidOperationException("Review original callers and choose every new input value explicitly");
   foreach(var selection in row["mapping"]!["bodies"]!.AsObject()){
    var plan=selection.Value!.AsObject();var nativeBefore=InformationFunctionBodies.Signature(plan["beforeSignature"]!);var nativeNext=InformationFunctionBodies.Signature(plan["signature"]!);var identity=new JsonObject(nativeBefore.Args.Select(a=>KeyValuePair.Create<string,JsonNode?>(a.Name,JsonValue.Create(a.Name))));
    if(!before.Matches(nativeBefore)||!next.Matches(nativeNext)||!Addition(nativeBefore,nativeNext,identity))throw new InvalidOperationException("Retain original native parameter names, types and order when adding explicit scalar values");
   }
   foreach(var selection in row["mapping"]!["callers"]!.AsObject()){
    if(selection.Value is not JsonObject plan||plan.Count!=5||plan.Any(p=>p.Key is not ("graph" or "node" or "hash" or "inputs" or "disconnect"))||plan["inputs"] is not JsonObject inputs||inputs.Count!=next.Args.Count||before.Args.Any(a=>inputs[a.Name]?.ToString()!=a.Name)||next.Args.Skip(before.Args.Count).Any(a=>!ExplicitValue(inputs[a.Name]))||plan["disconnect"] is not JsonObject disconnect||disconnect.Count!=0)throw new InvalidOperationException("Retain original bindings and outputs; choose an explicit value for every appended input without disconnecting source");
   }
  }
  return PrepareSources(request,edits,units,format);
 }
 internal static HashSet<string> PrepareSources(JsonObject request,JsonNode?[] edits,JsonObject units,Func<Element,string> format)
 {
  string ns=PackPaths.Namespace(request["id"]!.ToString());var functions=new HashSet<string>(StringComparer.Ordinal);var bodies=new HashSet<string>(StringComparer.Ordinal);
  Element Read(string id)=>new Parser(units[id]?["draft"]?.ToString()??throw new InvalidOperationException("Read the complete original native input source"),"<native-input-group>").ParseElement();
  foreach(var row in edits){
   string id=row!["id"]!.ToString();var original=Read(id);var map=row["mapping"]!.AsObject();
   if(!functions.Add(id)||!id.StartsWith(ns+"::",StringComparison.Ordinal)||original.Id!=id||original.Kind!="function"||original.Parent is not null||BlueprintAsync.Has(original)||BlueprintExecutionBranches.Has(original)||original.Signature is null||!JsonNode.DeepEquals(map["before"],FeatureBlueprint.SignatureDocument(original.Signature)))throw new InvalidOperationException("Native input groups require exact directly owned synchronous scalar contracts");
   foreach(var body in map["bodies"]!.AsObject()){
    int at=body.Key.LastIndexOf("/body:",StringComparison.Ordinal);if(at<0||!bodies.Add(body.Key)||units[body.Key]?["kind"]?.ToString()!="body")throw new InvalidOperationException("Review each exact original native input body");var implementation=Read(body.Key[..at]);
    if(implementation.Function!=id||!InformationFunctionBodyBatch.NativeTargets(implementation)||implementation.Bodies.Count!=1||!implementation.Bodies.ContainsKey(body.Key[(at+6)..]))throw new InvalidOperationException("Native input groups retain one directly owned native target per implementation");
   }
  }
  foreach(var unit in units.Where(p=>p.Value?["kind"]?.ToString()=="implementation")){
   var d=Read(unit.Key);bool callee=functions.Contains(d.Function!),consumer=d.Imports.Values.Any(i=>functions.Contains(i.Id));if(!callee&&!consumer)continue;
   if(d.Id!=unit.Key||!d.Id.StartsWith(ns+"::",StringComparison.Ordinal)||d.Parent is not null||callee&&consumer||d.Bodies.Count!=1)throw new InvalidOperationException("Review native dependency composition separately; preserve direct ownership and targets");
   foreach(var import in d.Imports.Values){var dependency=Read(import.Id);if(!import.Id.StartsWith(ns+"::",StringComparison.Ordinal)||dependency.Kind!="function"||dependency.Parent is not null||!import.Signature.Matches(dependency.Signature))throw new InvalidOperationException("Retain exact owned imports; no dependency contract or permission is inferred");}
   if(callee){if(!InformationFunctionBodyBatch.NativeTargets(d)||!bodies.Contains(d.Id+"/body:"+d.Bodies.Keys.Single()))throw new InvalidOperationException("Explicitly review every affected native input target");continue;}
   var target=d.Bodies.Single();string id=d.Id+"/body:"+target.Key;var graph=JsonNode.Parse(units[id]?["draft"]?.ToString()??throw new InvalidOperationException("Read every original native input caller"))!.AsObject();
   if(target.Value.SourceKind!="blueprint"||graph["copySource"] is not null||graph["profile"]?.ToString().StartsWith("sync-",StringComparison.Ordinal)!=true||graph["aliases"] is JsonObject aliases&&aliases.Count>0||graph["nodes"] is not JsonArray nodes||nodes.Any(node=>node?["kind"]?.ToString()!="call"||node["control"]?.ToString()!="next"||node["graph"] is not null||node["implementationContext"] is not null||node["forwardCallerStorage"] is not null||node["postCall"] is not null))throw new InvalidOperationException("Native input replacements retain ordinary direct Blueprint callers; review opaque/private source plans separately");
  }
  // No candidate may borrow another member's changes to validate its choices.
  foreach(var row in edits){var original=Read(row!["id"]!.ToString());var next=Read(original.Id);DeclarationAuthoring.Apply(next,new JsonObject{["action"]="signature",["value"]=row["signature"]!.DeepClone()});InformationFunctionContracts.Prepare(request,original,next,row["mapping"]!.AsObject(),format);}
  return functions;
 }
}
