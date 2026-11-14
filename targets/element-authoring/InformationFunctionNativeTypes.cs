using Confectory.Core;
using System.Text.Json.Nodes;

// Compose disjoint, explicitly authored native nominal input transitions.
// Scope/type proofs are validated before entering this compiler view. Neither
// a shared source nor a selected callee/consumer may borrow another edit.
internal static class InformationFunctionNativeTypes
{
 static bool Scalar(string type)=>type is "bool" or "int" or "long" or "float" or "double" or "string";
 internal static bool Types(FunctionSignature before,FunctionSignature next,JsonObject args)=>Scalar(before.Return)&&before.Return==next.Return&&before.Args.Count==next.Args.Count&&args.Count==before.Args.Count&&before.Args.Where((a,i)=>a.Name!=next.Args[i].Name||a.Mode is not null||next.Args[i].Mode is not null||!Scalar(a.Type)||!args.ContainsKey(a.Name)||(a.Type==next.Args[i].Type?args[a.Name]?.ToString()!=a.Name:args[a.Name] is not null||!InformationStructs.IsType(next.Args[i].Type)||InformationReferences.IsType(next.Args[i].Type)||next.Args[i].Type.EndsWith("[]",StringComparison.Ordinal))).Any()==false&&before.Args.Where((a,i)=>a.Type!=next.Args[i].Type).Any();
 internal static JsonNode?[]? Edits(JsonArray changes)
 {
  if(changes.Count is <2 or >8)return null;
  return changes.All(row=>InformationFunctionBodyBatch.BodyPlan(row)&&row!["nativeTypes"] is JsonObject types&&types[FunctionNativeEdits.Prefix+row["id"]] is JsonObject&&row["mapping"] is JsonObject map&&map.Count==3&&map.All(p=>p.Key is "before" or "args" or "bodies")&&map["args"] is JsonObject args&&Types(InformationFunctionBodies.Signature(map["before"]!),InformationFunctionBodies.Signature(row["signature"]!),args))?changes.ToArray():null;
 }
 internal static HashSet<string>? Prepare(JsonObject request,JsonArray changes,JsonObject units,Func<Element,string> format)
 {
  if(Edits(changes) is not {} edits)return null;var functions=edits.Select(row=>row!["id"]!.ToString()).ToHashSet(StringComparer.Ordinal);if(functions.Count!=edits.Length)throw new ArgumentException("One original native type transition per function");
  Element Read(string id)=>new Parser(units[id]?["draft"]?.ToString()??throw new InvalidOperationException("Read every original native type source"),"<native-type-group>").ParseElement();
  var headers=units.Where(p=>p.Value?["kind"]?.ToString()=="implementation").Select(p=>Read(p.Key)).ToArray();var sources=new HashSet<string>(StringComparer.Ordinal);var paths=new HashSet<string>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);string root=Path.GetDirectoryName(Path.GetFullPath(request["project"]!.ToString()))!;
  foreach(var row in edits){string function=row!["id"]!.ToString();var original=Read(function);var selected=Read(function);DeclarationAuthoring.Apply(selected,new JsonObject{["action"]="signature",["value"]=row["signature"]!.DeepClone()});
   if(original.Parent is not null||BlueprintAsync.Has(original)||BlueprintExecutionBranches.Has(original))throw new InvalidOperationException("Retain direct synchronous native type contracts");
   var affected=headers.Where(d=>d.Function==function||d.Imports.Values.Any(i=>i.Id==function)).ToArray();if(!affected.Any(d=>d.Function==function)||affected.Any(d=>!InformationFunctionBodyBatch.NativeTargets(d)||d.Bodies.Count!=1||d.Function!=function&&functions.Contains(d.Function!)||d.Imports.Values.Count(i=>functions.Contains(i.Id))>1))throw new InvalidOperationException("Review shared or joint native type source plans separately; retain direct disjoint targets");
   var plans=row["mapping"]!["bodies"]!.AsObject();var expected=affected.Select(d=>d.Id+"/body:"+d.Bodies.Keys.Single()).ToHashSet(StringComparer.Ordinal);if(!expected.SetEquals(plans.Select(p=>p.Key))||expected.Any(id=>!sources.Add(id)||!paths.Add(PackPaths.Owned(root,units[id]?["path"]?.ToString()??throw new InvalidOperationException("Read original native body paths")))))throw new InvalidOperationException("Explicitly author every disjoint original native implementation and caller once");
   foreach(var header in affected){var plan=plans[header.Id+"/body:"+header.Bodies.Keys.Single()]!;var before=InformationFunctionBodies.Signature(plan["beforeSignature"]!);var next=InformationFunctionBodies.Signature(plan["signature"]!);if(header.Function==function){var identity=new JsonObject(before.Args.Select(a=>KeyValuePair.Create<string,JsonNode?>(a.Name,next.Args.SingleOrDefault(b=>b.Name==a.Name)?.Type==a.Type?JsonValue.Create(a.Name):null)));if(!Types(before,next,identity))throw new InvalidOperationException("Retain native parameter aliases, order, roles and scalar return");}else if(!before.Matches(next)||!JsonNode.DeepEquals(plan["beforeSignature"],plan["signature"]))throw new InvalidOperationException("Retain the original C# caller ABI");}
   InformationFunctionContracts.Prepare(request,original,selected,row["mapping"]!.AsObject(),format,row["nativeTypes"]!.AsObject());
  }
  return functions;
 }
 internal static bool Retained(JsonNode receipt,HashSet<string> functions)=>functions.Count is >=2 and <=8&&receipt["nativeTypeProofs"] is JsonObject types&&types.Where(p=>p.Key.StartsWith(FunctionNativeEdits.Prefix,StringComparison.Ordinal)).Select(p=>p.Key[FunctionNativeEdits.Prefix.Length..]).ToHashSet(StringComparer.Ordinal).SetEquals(functions);
 internal static void Retains(string id,JsonObject units,JsonObject proof,HashSet<string> functions,JsonObject types,Func<Element,string> format)
 {
  string Original(string key)=>units[key]?["original"]?.ToString()??throw new InvalidOperationException("Read original native type sources before Review");
  string Captured(string key,string kind){var unit=units[key]??throw new InvalidOperationException("Captured native type source missing");string text=unit["draft"]?.ToString()??throw new InvalidOperationException("Read captured native type source");if(unit["kind"]?.ToString()!=kind||proof[key]?["kind"]?.ToString()!=kind||proof[key]?["path"]?.ToString()!=unit["path"]?.ToString()||proof[key]?["hash"]?.ToString()!=JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(text)))throw new InvalidOperationException("Retain every captured native type source identity/hash");return text;}
  Element Feature(string fn,bool after){var value=new Parser(after?Captured(fn,"function"):Original(fn),"<retained-native-type-function>").ParseElement();if(value.Id!=fn||value.Kind!="function"||value.Parent is not null||BlueprintAsync.Has(value)||BlueprintExecutionBranches.Has(value)||value.Signature is null)throw new InvalidOperationException("Retain direct synchronous native type functions");return value;}
  JsonObject Map(FunctionSignature before,FunctionSignature after)=>new(before.Args.Select(a=>KeyValuePair.Create<string,JsonNode?>(a.Name,after.Args.SingleOrDefault(b=>b.Name==a.Name)?.Type==a.Type?JsonValue.Create(a.Name):null)));
  foreach(string fn in functions){var before=Feature(fn,false).Signature!;var after=Feature(fn,true).Signature!;if(!Types(before,after,Map(before,after))||InformationStructs.SignatureTypes(after).Any(type=>types[type] is null))throw new InvalidOperationException("Retain captured nominal inputs and their selected native type proofs");}
  string original=Original(id),current=Captured(id,"implementation");var old=new Parser(original,"<retained-native-type-header>").ParseElement();var selected=new Parser(current,"<captured-native-type-header>").ParseElement();
  bool callee=functions.Contains(old.Function!);var imports=old.Imports.Values.Where(i=>functions.Contains(i.Id)).ToArray();if(old.Id!=id||selected.Id!=id||!InformationFunctionBodyBatch.NativeTargets(old)||old.Bodies.Count!=1||callee&&imports.Length>0||imports.Length>1||!callee&&imports.Length!=1)throw new InvalidOperationException("Retain disjoint native type implementations and callers");
  if(callee){var before=Feature(old.Function!,false).Signature!;var after=Feature(old.Function!,true).Signature!;if(!old.Signature!.Matches(before)||!selected.Signature!.Matches(after)||!Types(old.Signature,selected.Signature,Map(old.Signature,selected.Signature)))throw new InvalidOperationException("Retain native aliases, roles, order and return with the selected nominal input");}
  else if(!JsonNode.DeepEquals(FeatureBlueprint.SignatureDocument(old.Signature!),FeatureBlueprint.SignatureDocument(selected.Signature!)))throw new InvalidOperationException("Retain the original native caller ABI");
  Captured(id+"/body:"+old.Bodies.Keys.Single(),"body");old.Signature=selected.Signature;
  foreach(string alias in old.Imports.Keys.ToArray()){var import=old.Imports[alias];if(!functions.Contains(import.Id))continue;if(!import.Signature.Matches(Feature(import.Id,false).Signature))throw new InvalidOperationException("Original native type import was stale");old.Imports[alias]=import with{Signature=Feature(import.Id,true).Signature!};}
  if(DeclarationTextMerge.MergeContract(original,format(old),format)!=current)throw new InvalidOperationException("Retain exact captured nominal native header/import changes only");
 }

}
