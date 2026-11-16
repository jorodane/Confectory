using Confectory.Core;
using System.Text.Json.Nodes;

// An internal, request-local compiler view of jointly authored native sources.
// Original observations and source plans remain the authority. Never serializes
// a caller-provided bypass, rewrites C# text or stages a partial native header.
internal sealed class InformationFunctionNativeJoint
{
 readonly Dictionary<string,Element> features=new(StringComparer.Ordinal);
 readonly Dictionary<string,Element> headers=new(StringComparer.Ordinal);
 readonly Dictionary<string,JsonObject> bodies=new(StringComparer.Ordinal);
 readonly Dictionary<string,FunctionSignature> signatures=new(StringComparer.Ordinal);
 internal bool ReturnChanges {get; private set;}
 internal bool RoleChanges {get; private set;}
 internal JsonObject? TypeChoices {get; private set;}
 InformationFunctionNativeJoint(){}
 internal static InformationFunctionNativeJoint? Create(JsonObject request,JsonArray changes,JsonObject units)
 {
  var inputs=InformationFunctionNativeInputs.Edits(changes);var returns=inputs is null?InformationFunctionNativeReturns.Edits(changes):null;var roles=inputs is null&&returns is null?InformationFunctionNativeRoles.Edits(changes):null;var edits=inputs??returns??roles;if(edits is null)return null;var ids=edits.Select(row=>row!["id"]!.ToString()).ToHashSet(StringComparer.Ordinal);
  Element Read(string id)=>new Parser(units[id]?["draft"]?.ToString()??throw new InvalidOperationException("Read every original joint native source"),"<joint-native-original>").ParseElement();
  var implementations=units.Where(unit=>unit.Value?["kind"]?.ToString()=="implementation").Select(unit=>Read(unit.Key)).ToArray();
  if(!implementations.Any(d=>ids.Contains(d.Function!)&&d.Imports.Values.Any(import=>ids.Contains(import.Id))))return null;
  var result=new InformationFunctionNativeJoint{ReturnChanges=returns is not null,RoleChanges=roles is not null};
  foreach(var row in edits){
   string id=row!["id"]!.ToString();var original=Read(id);var selected=Read(id);DeclarationAuthoring.Apply(selected,new JsonObject{["action"]="signature",["value"]=row["signature"]!.DeepClone()});result.features.Add(id,selected);
   var targets=implementations.Where(d=>d.Function==id).ToArray();if(targets.Length!=1||!InformationFunctionBodyBatch.NativeTargets(targets[0])||targets[0].Bodies.Count!=1)throw new InvalidOperationException("Joint native contracts retain one directly owned implementation and target per function");
   var implementation=targets[0];string source=implementation.Id+"/body:"+implementation.Bodies.Keys.Single();var plans=row["mapping"]!["bodies"]!.AsObject();
   if(plans.Count!=1||plans[source] is not JsonObject plan||units[source] is not JsonObject unit||unit["kind"]?.ToString()!="body")throw new InvalidOperationException("Explicitly author each joint function's own native source once; retain the original source identity");
   var native=InformationFunctionBodies.Signature(plan["signature"]!);if(!implementation.Signature!.Matches(original.Signature)||!native.Matches(selected.Signature))throw new InvalidOperationException("Joint native declarations must match their original and explicitly selected public contracts");
   InformationFunctionBodies.Text(source,implementation.Bodies.Values.Single().Path,unit,implementation.Signature,native,selected.Signature!,plan);
   result.headers.Add(implementation.Id,implementation);result.bodies.Add(source,plan.DeepClone().AsObject());result.signatures.Add(implementation.Id,native);
  }
  return result;
 }
 // A shared nominal caller has its own unchanged ABI and one source plan.
 // Every selected function still authenticates that plan against its ORIGINAL
 // scope. Only equal authored source/signature plans may share this context.
 internal static InformationFunctionNativeJoint? SharedTypes(JsonObject request,JsonArray changes,JsonObject units)
 {
  if(InformationFunctionNativeTypes.Edits(changes) is not {} edits)return null;var ids=edits.Select(row=>row!["id"]!.ToString()).ToHashSet(StringComparer.Ordinal);
  Element Read(string id,string kind){var unit=units[id]??throw new InvalidOperationException("Read every shared nominal source");var value=new Parser(unit["draft"]?.ToString()??throw new InvalidOperationException("Original shared nominal source missing"),"<shared-nominal-original>").ParseElement();if(unit["kind"]?.ToString()!=kind||value.Id!=id||value.Kind!=kind)throw new InvalidOperationException("Retain direct owned nominal source identities");return value;}
  var implementations=units.Where(p=>p.Value?["kind"]?.ToString()=="implementation").Select(p=>Read(p.Key,"implementation")).ToArray();
  if(!implementations.Any(d=>d.Imports.Values.Count(i=>ids.Contains(i.Id))>(ids.Contains(d.Function!)?0:1)))return null;
  var typeChoices=new JsonObject();var result=new InformationFunctionNativeJoint{TypeChoices=typeChoices};var paths=new Dictionary<string,string>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);string root=Path.GetDirectoryName(Path.GetFullPath(request["project"]!.ToString()))!;
  foreach(var row in edits){string function=row!["id"]!.ToString();var selected=Read(function,"function");DeclarationAuthoring.Apply(selected,new JsonObject{["action"]="signature",["value"]=row["signature"]!.DeepClone()});if(!result.features.TryAdd(function,selected))throw new InvalidOperationException("One explicit nominal contract per selected function");}
  foreach(var row in edits){string function=row!["id"]!.ToString();var original=Read(function,"function");var selected=result.features[function];
   foreach(var choice in row["nativeTypes"]!.AsObject()){if(typeChoices[choice.Key]is JsonNode prior&&!JsonNode.DeepEquals(prior,choice.Value))throw new InvalidOperationException("Retain one original version of every selected nominal type proof");typeChoices[choice.Key]=choice.Value!.DeepClone();}if(typeChoices.Count>64)throw new ArgumentException("Shared nominal type proof budget");
   var affected=implementations.Where(d=>d.Function==function||d.Imports.Values.Any(i=>i.Id==function)).ToArray();var plans=row["mapping"]!["bodies"]!.AsObject();var expected=affected.Select(d=>d.Id+"/body:"+d.Bodies.Keys.Single()).ToHashSet(StringComparer.Ordinal);
   if(!expected.SetEquals(plans.Select(p=>p.Key)))throw new InvalidOperationException("Explicitly select every original shared nominal implementation/caller source");
   foreach(var header in affected){if(!InformationFunctionBodyBatch.NativeTargets(header)||header.Bodies.Count!=1)throw new InvalidOperationException("Joint nominal sources retain one directly owned C# target per implementation");
    string source=header.Id+"/body:"+header.Bodies.Keys.Single();var unit=units[source]?.AsObject()??throw new InvalidOperationException("Original shared nominal body missing");var plan=plans[source]!.AsObject();var signature=InformationFunctionBodies.Signature(plan["signature"]!);var beforeFeature=Read(header.Function!,"function");var feature=result.features.GetValueOrDefault(header.Function!)??beforeFeature;
    if(original.Parent is not null||beforeFeature.Parent is not null||feature.Parent is not null||BlueprintAsync.Has(beforeFeature)||BlueprintAsync.Has(feature)||BlueprintExecutionBranches.Has(beforeFeature)||BlueprintExecutionBranches.Has(feature)||!header.Signature!.Matches(beforeFeature.Signature)||!signature.Matches(feature.Signature))throw new InvalidOperationException("Retain original native declarations and explicitly selected synchronous nominal contracts");
    InformationFunctionBodies.Text(source,header.Bodies.Values.Single().Path,unit,header.Signature,signature,selected.Signature!,plan);
    string path=PackPaths.Owned(root,unit["path"]!.ToString());if(paths.TryGetValue(path,out var owner)&&owner!=source)throw new InvalidOperationException("Distinct native owners cannot alias a shared source path");paths[path]=source;
    if(result.bodies.TryGetValue(source,out var prior)){var a=prior.DeepClone().AsObject();var b=plan.DeepClone().AsObject();a.Remove("contract");b.Remove("contract");if(!JsonNode.DeepEquals(a,b))throw new InvalidOperationException("Explicit shared nominal source plans disagree; all input retained");}
    else{result.bodies.Add(source,plan.DeepClone().AsObject());result.headers.Add(header.Id,header);result.signatures.Add(header.Id,signature);}
    if(!ids.Contains(header.Function!))result.features.TryAdd(feature.Id,feature);
   }
  }
  return result;
 }
 // Cold/header discovery must retain the captured callee+consumer without
 // mistaking it for an unselected native caller. Authenticate only the saved
 // scalar input/return/role source shape and its exact permitted native header delta.
 internal static bool Retains(string id,JsonObject units,JsonObject proof,HashSet<string> functions,Func<Element,string> format)
 {
  string Original(string key)=>units[key]?["original"]?.ToString() is {Length:>0} text?text:throw new InvalidOperationException("Read every original joint native contract before review");
  string Captured(string key,string kind){var unit=units[key]??throw new InvalidOperationException("Captured joint native source missing");string text=unit["draft"]?.ToString()??throw new InvalidOperationException("Read the captured joint native source");if(unit["kind"]?.ToString()!=kind||proof[key]?["kind"]?.ToString()!=kind||proof[key]?["path"]?.ToString()!=unit["path"]?.ToString()||proof[key]?["hash"]?.ToString()!=JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(text)))throw new InvalidOperationException("Retain every exact captured joint source identity/hash");return text;}
  Element Feature(string function,bool after){var value=new Parser(after?Captured(function,"function"):Original(function),"<retained-joint-function>").ParseElement();if(!functions.Contains(function)||value.Id!=function||value.Kind!="function"||value.Parent is not null||BlueprintAsync.Has(value)||BlueprintExecutionBranches.Has(value)||value.Signature is null)throw new InvalidOperationException("Retain directly owned synchronous joint input contracts");return value;}
  string original=Original(id),current=Captured(id,"implementation");var before=new Parser(original,"<retained-joint-header>").ParseElement();var after=new Parser(current,"<retained-joint-header>").ParseElement();
  if(before.Id!=id||after.Id!=id||!InformationFunctionBodyBatch.NativeTargets(before)||before.Bodies.Count!=1||before.Signature is null||after.Signature is null)return false;
  string function=before.Function!;var old=Feature(function,false).Signature!;var next=Feature(function,true).Signature!;var args=new JsonObject(old.Args.Select(a=>KeyValuePair.Create<string,JsonNode?>(a.Name,next.Args.Contains(a)?JsonValue.Create(a.Name):null)));
  JsonObject Identity(FunctionSignature signature)=>new(signature.Args.Select(a=>KeyValuePair.Create<string,JsonNode?>(a.Name,JsonValue.Create(a.Name))));
  bool role=InformationFunctionNativeRoles.Types(old,next,Identity(old));
  if(role){string direction=InformationFunctionNativeRoles.Direction(old,next);foreach(string member in functions){var originalMember=Feature(member,false).Signature!;var selectedMember=Feature(member,true).Signature!;if(!InformationFunctionNativeRoles.Types(originalMember,selectedMember,Identity(originalMember))||InformationFunctionNativeRoles.Direction(originalMember,selectedMember)!=direction)throw new InvalidOperationException("Retain one captured role direction and every original public input/output identity");}if(!InformationFunctionNativeRoles.Types(before.Signature,after.Signature,Identity(before.Signature))||InformationFunctionNativeRoles.Direction(before.Signature,after.Signature)!=direction)throw new InvalidOperationException("Retain original native names, types, order and the exact selected role direction");}
  if(!(InformationFunctionNativeInputs.Types(old,next,args)||InformationFunctionNativeReturns.Types(old,next,args)||role)||!before.Signature.Matches(old)||!after.Signature.Matches(next))throw new InvalidOperationException("Retain the captured scalar input/return/role transition and its native declaration");
  string body=id+"/body:"+before.Bodies.Keys.Single();Captured(body,"body");before.Signature=after.Signature;
  foreach(string alias in before.Imports.Keys.ToArray()){var import=before.Imports[alias];if(!functions.Contains(import.Id))continue;if(!import.Signature.Matches(Feature(import.Id,false).Signature))throw new InvalidOperationException("Original joint import contract was stale");before.Imports[alias]=import with{Signature=Feature(import.Id,true).Signature!};}
  if(DeclarationTextMerge.MergeContract(original,format(before),format)!=current)throw new InvalidOperationException("Retain the exact captured native import/header delta; no source is inferred");return true;
 }
 internal bool Buffers(string id)=>headers.ContainsKey(id)||bodies.ContainsKey(id);
 internal bool Header(string id)=>headers.ContainsKey(id);
 internal FunctionSignature Signature(string id)=>signatures.GetValueOrDefault(id)??throw new InvalidOperationException("Joint native consumer must have its own complete explicit function/source plan");
 internal Element Feature(string id)=>features.GetValueOrDefault(id)??throw new InvalidOperationException("Joint native consumer must be explicitly selected");
 internal JsonObject Mapping(string function,JsonObject mapping)
 {
  var result=mapping.DeepClone().AsObject();var selected=result["bodies"]!.AsObject();
  foreach(var pair in headers.Where(pair=>pair.Value.Function==function||pair.Value.Imports.Values.Any(import=>import.Id==function))){
   string source=pair.Key+"/body:"+pair.Value.Bodies.Keys.Single();var plan=bodies[source].DeepClone().AsObject();plan["contract"]=FeatureBlueprint.SignatureDocument(Feature(function).Signature!);
   if(selected[source] is JsonObject prior&&!JsonNode.DeepEquals(prior,plan))throw new InvalidOperationException("Joint native selections disagree on the original or authored source");selected[source]=plan;
  }
  return result;
 }
 internal IReadOnlyDictionary<string,Element> Declarations(IReadOnlyDictionary<string,Element> original)
 {
  var result=original.ToDictionary(pair=>pair.Key,pair=>pair.Value,StringComparer.Ordinal);foreach(var pair in features)result[pair.Key]=pair.Value;return result;
 }
 internal void Imports(Element implementation)
 {
  if(!headers.ContainsKey(implementation.Id))throw new InvalidOperationException("Retain unselected C# callers; joint native sources require explicit selection");
  foreach(string alias in implementation.Imports.Keys.ToArray()){var import=implementation.Imports[alias];if(features.TryGetValue(import.Id,out var feature))implementation.Imports[alias]=import with{Signature=feature.Signature!};}
 }
}
