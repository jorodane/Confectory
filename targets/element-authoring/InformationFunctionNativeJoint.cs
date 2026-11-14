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
 InformationFunctionNativeJoint(){}
 internal static InformationFunctionNativeJoint? Create(JsonObject request,JsonArray changes,JsonObject units)
 {
  var inputs=InformationFunctionNativeInputs.Edits(changes);var returns=inputs is null?InformationFunctionNativeReturns.Edits(changes):null;var edits=inputs??returns;if(edits is null)return null;var ids=edits.Select(row=>row!["id"]!.ToString()).ToHashSet(StringComparer.Ordinal);
  Element Read(string id)=>new Parser(units[id]?["draft"]?.ToString()??throw new InvalidOperationException("Read every original joint native source"),"<joint-native-original>").ParseElement();
  var implementations=units.Where(unit=>unit.Value?["kind"]?.ToString()=="implementation").Select(unit=>Read(unit.Key)).ToArray();
  if(!implementations.Any(d=>ids.Contains(d.Function!)&&d.Imports.Values.Any(import=>ids.Contains(import.Id))))return null;
  var result=new InformationFunctionNativeJoint{ReturnChanges=returns is not null};
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
 // Cold/header discovery must retain the captured callee+consumer without
 // mistaking it for an unselected native caller. Authenticate only the saved
 // scalar input/return source shape and its exact permitted native header delta.
 internal static bool Retains(string id,JsonObject units,JsonObject proof,HashSet<string> functions,Func<Element,string> format)
 {
  string Original(string key)=>units[key]?["original"]?.ToString() is {Length:>0} text?text:throw new InvalidOperationException("Read every original joint native contract before review");
  string Captured(string key,string kind){var unit=units[key]??throw new InvalidOperationException("Captured joint native source missing");string text=unit["draft"]?.ToString()??throw new InvalidOperationException("Read the captured joint native source");if(unit["kind"]?.ToString()!=kind||proof[key]?["kind"]?.ToString()!=kind||proof[key]?["path"]?.ToString()!=unit["path"]?.ToString()||proof[key]?["hash"]?.ToString()!=JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(text)))throw new InvalidOperationException("Retain every exact captured joint source identity/hash");return text;}
  Element Feature(string function,bool after){var value=new Parser(after?Captured(function,"function"):Original(function),"<retained-joint-function>").ParseElement();if(!functions.Contains(function)||value.Id!=function||value.Kind!="function"||value.Parent is not null||BlueprintAsync.Has(value)||BlueprintExecutionBranches.Has(value)||value.Signature is null)throw new InvalidOperationException("Retain directly owned synchronous joint input contracts");return value;}
  string original=Original(id),current=Captured(id,"implementation");var before=new Parser(original,"<retained-joint-header>").ParseElement();var after=new Parser(current,"<retained-joint-header>").ParseElement();
  if(before.Id!=id||after.Id!=id||!InformationFunctionBodyBatch.NativeTargets(before)||before.Bodies.Count!=1||before.Signature is null||after.Signature is null)return false;
  string function=before.Function!;var old=Feature(function,false).Signature!;var next=Feature(function,true).Signature!;var args=new JsonObject(old.Args.Select(a=>KeyValuePair.Create<string,JsonNode?>(a.Name,next.Args.Contains(a)?JsonValue.Create(a.Name):null)));
  if(!(InformationFunctionNativeInputs.Types(old,next,args)||InformationFunctionNativeReturns.Types(old,next,args))||!before.Signature.Matches(old)||!after.Signature.Matches(next))throw new InvalidOperationException("Retain the captured scalar input/return transition and its native declaration");
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
