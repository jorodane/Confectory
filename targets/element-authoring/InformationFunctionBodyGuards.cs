using Confectory.Core;
using System.Text.Json.Nodes;

// Keep the already observed owned source snapshot as read checks, never writes.
// The existing slot receipt and final source lease carry these checks unchanged.
internal static class InformationFunctionBodyGuards
{
 public static JsonObject Execute(JsonObject request)
 {
  string ns=request["namespace"]!.ToString();var units=request["units"]!.AsObject();
  bool PresentationOnly(JsonNode? declaration)=>declaration?["raw"] is null&&declaration?["changes"] is JsonArray changes&&changes.Count is >=1 and <=2&&changes.All(InformationFunctionBodyBatch.Presentation);
  bool NativeGroup(string owner)
  {
   if(units[owner]?["kind"]?.ToString()!="schema"||units[owner]?["atomicEditGroup"] is not JsonArray group||group.Count>64)return false;
   var ids=group.Select(value=>value!.ToString()).ToArray();if(!ids.Contains(owner)||!ids.Contains(ns+"::ProjectManifest"))return false;
   var functions=ids.Where(id=>units[id]?["kind"]?.ToString()=="function").ToArray();int bodies=ids.Count(id=>units[id]?["kind"]?.ToString()=="body");
   return functions.Length is >=2 and <=8&&functions.All(id=>id.StartsWith(owner+"_Function_",StringComparison.Ordinal))&&bodies>=functions.Length&&ids.Length==2+functions.Length+bodies;
  }
  (HashSet<string> Functions,string[] Bodies)? RetainedSources(string owner,JsonObject receipt)
  {
   bool native=NativeGroup(owner)&&(PresentationOnly(receipt["declaration"])||receipt["declaration"]?["changes"] is JsonArray saved&&InformationFunctionBodyBatch.Edits(saved) is not null);
   if(units[owner]?["kind"]?.ToString()!="schema"||receipt["declaration"]?["raw"] is not null||receipt["sources"] is not JsonObject proof||proof[owner]?["kind"]?.ToString()!="schema"||proof[ns+"::ProjectManifest"]?["kind"]?.ToString()!="project"){
    if(native)throw new InvalidOperationException("Retain the complete saved native body group proof; all input retained");return null;
   }
   var functions=proof.Where(p=>p.Value?["kind"]?.ToString()=="function").Select(p=>p.Key).ToHashSet(StringComparer.Ordinal);var bodies=proof.Where(p=>p.Value?["kind"]?.ToString()=="body").Select(p=>p.Key).ToArray();
   if(functions.Count is <2 or >8||bodies.Length<functions.Count||proof.Count>64||proof.Count!=2+functions.Count+bodies.Length||units[owner]?["atomicEditGroup"] is not JsonArray group||group.Count!=proof.Count||!proof.Select(p=>p.Key).ToHashSet(StringComparer.Ordinal).SetEquals(group.Select(id=>id!.ToString()))){
    if(native)throw new InvalidOperationException("Retain every saved native target proof and group member; all input retained");return null;
   }
   if(!(receipt["declaration"]?["changes"] is JsonArray edits&&InformationFunctionBodyBatch.Edits(edits) is not null)&&!PresentationOnly(receipt["declaration"]))return null;
   foreach(var source in proof)if(!source.Key.StartsWith(ns+"::",StringComparison.Ordinal)||units[source.Key]?["kind"]?.ToString()!=source.Value?["kind"]?.ToString()||units[source.Key]?["path"]?.ToString()!=source.Value?["path"]?.ToString())throw new InvalidOperationException("Retain the exact owned native group sources before editing its presentation");
   return(functions,bodies);
  }
  Element OriginalImplementation(string id)
  {
   var unit=units[id];if(!id.StartsWith(ns+"::",StringComparison.Ordinal)||unit?["kind"]?.ToString()!="implementation")throw new ArgumentException("Owned native implementation required");
   string? text=unit["original"]?.ToString();if(string.IsNullOrEmpty(text))text=unit["draft"]?.ToString();if(text is null)throw new InvalidOperationException("Read original native headers before reviewing the saved group");return new Parser(text,"<native-body-read-scope>").ParseElement();
  }
  bool ObservedScope(HashSet<string> functions,IEnumerable<(string Function,string Body)> targets)
  {
   bool observed=false;var seen=new HashSet<string>(StringComparer.Ordinal);var expected=new HashSet<string>(StringComparer.Ordinal);var selected=new HashSet<string>(StringComparer.Ordinal);
   // Candidate preparation already requires every known owned header. Cold
   // Review reads those same headers before checking the unchanged receipt.
   foreach(var pair in units.Where(p=>p.Key.StartsWith(ns+"::",StringComparison.Ordinal)&&p.Value?["kind"]?.ToString()=="implementation")){
    var implementation=OriginalImplementation(pair.Key);if(!functions.Contains(implementation.Function!))continue;
    if(implementation.Id!=pair.Key||!InformationFunctionBodyBatch.NativeTargets(implementation))throw new InvalidOperationException("Retain every original directly owned native target header");
    foreach(string target in implementation.Bodies.Keys)expected.Add(implementation.Id+"/body:"+target);
    observed|=implementation.Imports.Count>0||implementation.Bodies.Count>1;
   }
   foreach(var target in targets){
    if(units[target.Body]?["kind"]?.ToString()!="body")throw new ArgumentException("Exact native body source required");int at=target.Body.LastIndexOf("/body:",StringComparison.Ordinal);if(at<0)throw new ArgumentException("Exact native body owner required");string id=target.Body[..at];var implementation=OriginalImplementation(id);
    string name=target.Body[(at+6)..];if(!selected.Add(target.Body)||implementation.Id!=id||implementation.Function!=target.Function||!functions.Contains(target.Function)||!InformationFunctionBodyBatch.NativeTargets(implementation)||!implementation.Bodies.ContainsKey(name))throw new InvalidOperationException("Retain the original native body and contract scope");
    seen.Add(target.Function);
   }
   if(!seen.SetEquals(functions)||!selected.SetEquals(expected))throw new InvalidOperationException("Retain every original native target in the saved group");if(observed)return true;
   foreach(var pair in units.Where(p=>p.Key.StartsWith(ns+"::",StringComparison.Ordinal)&&p.Value?["kind"]?.ToString()=="implementation")){
    var implementation=OriginalImplementation(pair.Key);if(!implementation.Imports.Values.Any(import=>functions.Contains(import.Id)))continue;
    if(implementation.Bodies.Values.Any(body=>body.SourceKind=="csharp"))return true;
    foreach(var body in implementation.Bodies.Where(body=>body.Value.SourceKind=="blueprint")){
     string graphId=implementation.Id+"/body:"+body.Key;var unit=units[graphId];if(unit?["kind"]?.ToString()!="blueprint")throw new InvalidOperationException("Read the known ordinary caller graph before reviewing native bodies");
     string text=unit["original"]?.ToString()??unit["draft"]?.ToString()??throw new InvalidOperationException("Read the original ordinary caller graph before reviewing native bodies");var graph=JsonNode.Parse(text)!.AsObject();
     if(graph["locals"] is JsonArray locals&&locals.Count>0||graph["aliases"] is JsonObject aliases&&aliases.Count>0||graph["nodes"] is JsonArray nodes&&nodes.Any(node=>node?["kind"]?.ToString() is "code" or "graph"||node?["postCall"] is not null))return true;
    }
   }
   return false;
  }
  bool ObservedGroup(JsonNode? declaration)
  {
   if(declaration?["raw"] is not null||declaration?["changes"] is not JsonArray changes||InformationFunctionBodyBatch.Edits(changes) is not {} edits)return false;
   var functions=edits.Select(row=>row!["id"]!.ToString()).ToHashSet(StringComparer.Ordinal);return ObservedScope(functions,edits.SelectMany(row=>row!["mapping"]!["bodies"]!.AsObject().Select(body=>(row["id"]!.ToString(),body.Key))));
  }
  bool ObservedReceipt(string owner,JsonObject receipt)
  {
   if(ObservedGroup(receipt["declaration"]))return true;
   // A peer may remove the retained caller state after Save. The already bound
   // read scope still applies; never infer a new empty legacy receipt from it.
   if(receipt["declaration"]?["changes"] is JsonArray saved&&InformationFunctionBodyBatch.Edits(saved) is not null&&receipt["readGuards"] is JsonObject savedGuards&&savedGuards.Count>0)return true;
   if(!PresentationOnly(receipt["declaration"])||RetainedSources(owner,receipt) is not {} retained)return false;
   // A subsequent header Save keeps only an already saved, same-contract native
   // body group. No body edit or dependency baseline is reconstructed or rebased.
   foreach(string function in retained.Functions){var unit=units[function]!;string draft=unit["draft"]?.ToString()??throw new InvalidOperationException("Read the retained native function contract");string original=unit["original"]?.ToString()??draft;var before=new Parser(original,"<retained-function>").ParseElement();var after=new Parser(draft,"<retained-function>").ParseElement();if(before.Id!=function||after.Id!=function||before.Kind!="function"||before.Parent is not null||after.Parent is not null||before.Signature is null||after.Signature is null||!JsonNode.DeepEquals(FeatureBlueprint.SignatureDocument(before.Signature),FeatureBlueprint.SignatureDocument(after.Signature)))return false;}
   bool observed=ObservedScope(retained.Functions,retained.Bodies.Select(body=>{int at=body.LastIndexOf("/body:",StringComparison.Ordinal);if(at<0)throw new ArgumentException("Retained native body owner required");return(OriginalImplementation(body[..at]).Function!,body);}));return observed||receipt["readGuards"] is JsonObject retainedGuards&&retainedGuards.Count>0;
  }
  if(request["action"]?.ToString()=="headers"){
   var headerSelection=request["selected"]?.AsArray()??throw new ArgumentException("Selected native group required");if(headerSelection.Count>64)throw new ArgumentException("Native body header budget");bool native=false;var functions=new HashSet<string>(StringComparer.Ordinal);
   foreach(var id in headerSelection){string owner=id!.ToString();if(units[owner]?["slotSaveReceipt"] is not JsonObject receipt)continue;if(receipt["declaration"]?["changes"] is JsonArray changes&&InformationFunctionBodyBatch.Edits(changes) is not null)native=true;if(RetainedSources(owner,receipt) is {} retained){native=true;functions.UnionWith(retained.Functions);}}
   if(native&&units.Count>2048)throw new ArgumentException("Native body header budget");return new JsonObject{["ids"]=new JsonArray((native?units.Where(pair=>pair.Key.StartsWith(ns+"::",StringComparison.Ordinal)&&(pair.Value?["kind"]?.ToString()=="implementation"||functions.Contains(pair.Key))).Select(pair=>(JsonNode)JsonValue.Create(pair.Key)!):Enumerable.Empty<JsonNode>()).ToArray())};
  }
  if(request["action"]?.ToString()=="graphs"){
   var selection=request["selected"]?.AsArray()??throw new ArgumentException("Selected native group required");if(selection.Count>64)throw new ArgumentException("Native body review budget");var functions=new HashSet<string>(StringComparer.Ordinal);
   foreach(var selectedOwner in selection){string owner=selectedOwner!.ToString();if(units[owner]?["slotSaveReceipt"] is not JsonObject receipt)continue;if(receipt["declaration"]?["changes"] is JsonArray changes&&InformationFunctionBodyBatch.Edits(changes) is {} edits)functions.UnionWith(edits.Select(row=>row!["id"]!.ToString()));if(RetainedSources(owner,receipt) is {} retained)functions.UnionWith(retained.Functions);}
   var ids=new HashSet<string>(StringComparer.Ordinal);if(functions.Count>0)foreach(var pair in units.Where(pair=>pair.Key.StartsWith(ns+"::",StringComparison.Ordinal)&&pair.Value?["kind"]?.ToString()=="implementation")){
    var implementation=OriginalImplementation(pair.Key);if(!implementation.Imports.Values.Any(import=>functions.Contains(import.Id)))continue;
    foreach(var body in implementation.Bodies.Where(body=>body.Value.SourceKind=="blueprint")){string id=implementation.Id+"/body:"+body.Key;if(units[id]?["kind"]?.ToString()!="blueprint")throw new InvalidOperationException("Known owned caller graph required");ids.Add(id);}
   }
   if(ids.Count>240)throw new ArgumentException("Native body caller read budget");return new JsonObject{["ids"]=new JsonArray(ids.Select(id=>(JsonNode)JsonValue.Create(id)!).ToArray())};
  }
  bool Token(string value)=>value=="missing"||System.Text.RegularExpressions.Regex.IsMatch(value,"^[a-f0-9]{64}$");
  Dictionary<string,JsonObject> Sources(bool preparing)
  {
   if(units.Count>2048)throw new ArgumentException("Native body source budget");var result=new Dictionary<string,JsonObject>(StringComparer.Ordinal);foreach(var pair in units){if(!pair.Key.StartsWith(ns+"::",StringComparison.Ordinal))continue;var unit=pair.Value!;string path=unit["path"]?.ToString()??throw new ArgumentException("Known owned source path required");if(Path.IsPathRooted(path))throw new ArgumentException("Relative native source checks required");string? baseline=unit["baseline"]?.ToString();if(preparing&&(baseline is null||!Token(baseline)))throw new InvalidOperationException("Read the complete native source snapshot before Save");
    if(result.TryGetValue(path,out var prior)){if(preparing&&prior["hash"]?.ToString()!=baseline)throw new InvalidOperationException("Native source aliases disagree on their original baseline");continue;}result[path]=new JsonObject{["path"]=path,["hash"]=preparing?baseline:null};
   }
   if(result.Count is <1 or >240)throw new ArgumentException("Complete bounded native source checks required");return result;
  }
  JsonArray Checks(string owner,JsonObject receipt)
  {
   if(receipt["owner"]?.ToString()!=owner||receipt["version"]?.GetValue<int>()!=3||receipt["readGuards"] is not JsonObject guards)throw new InvalidOperationException("Save the native body group explicitly to bind its original dependencies; input retained");var expected=Sources(false);if(guards.Count!=expected.Count||expected.Keys.Any(path=>guards[path] is not JsonObject row||row.Count!=2||row["path"]?.ToString()!=path||row["hash"] is null||!Token(row["hash"]!.ToString())))throw new InvalidOperationException("Complete original native body source checks are missing or changed; retain the saved group");return new JsonArray(guards.Select(p=>p.Value!.DeepClone()).ToArray());
  }
  if(request["action"]?.ToString()=="prepare"){
   if(ObservedGroup(request["declaration"]))return new JsonObject{["required"]=true,["checks"]=new JsonArray(Sources(true).Values.Select(v=>(JsonNode)v).ToArray())};
   string? owner=request["declaration"]?["id"]?.ToString();if(owner is not null&&PresentationOnly(request["declaration"])&&units[owner]?["slotSaveReceipt"] is JsonObject prior&&RetainedSources(owner,prior) is not null&&prior["readGuards"] is JsonObject priorGuards&&priorGuards.Count>0)return new JsonObject{["required"]=true,["checks"]=Checks(owner,prior)};
   return new JsonObject{["required"]=false,["checks"]=new JsonArray()};
  }
  if(request["action"]?.ToString()!="validate")throw new ArgumentException("Native body guard action");var selected=request["selected"]?.AsArray()??throw new ArgumentException("Selected native group required");if(selected.Count>64)throw new ArgumentException("Native body review budget");
  foreach(var pair in units){var unit=pair.Value;if(unit?["atomicEditGroup"] is not JsonArray group||!selected.Any(id=>group.Any(member=>member!.ToString()==id!.ToString()))||unit["slotSaveReceipt"] is not JsonObject receipt||!ObservedReceipt(pair.Key,receipt))continue;Checks(pair.Key,receipt);}
  return new JsonObject{["validated"]=true};
 }
}
