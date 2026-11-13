using Confectory.Core;
using System.Text.Json.Nodes;

// Compose explicit whole-body, qualified private code and native sources. The original
// single-function validator remains the authority for each source and contract.
internal static class InformationFunctionWholeBodies
{
 const string Capture="nativeBodyContexts";
 static string Hash(string text)=>JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(text));
 internal static JsonNode?[]? Edits(JsonArray changes)
 {
  var rows=changes.Where(row=>!InformationFunctionBodyBatch.Presentation(row)).ToArray();
  if(rows.Length is <2 or >8||!rows.Any(row=>row?["mapping"]?["bodies"] is JsonObject bodies&&bodies.Any(body=>body.Value?["whole"] is JsonObject)))return null;
  if(rows.Any(row=>row?["type"]?.ToString()!="function-edit"||row["mapping"] is not JsonObject mapping||mapping["bodies"] is not JsonObject bodies||bodies.Count!=1||!JsonNode.DeepEquals(mapping["before"],row["signature"])||bodies.Any(body=>body.Value?["wrapper"] is not null||!JsonNode.DeepEquals(body.Value?["beforeSignature"],body.Value?["signature"]))))return null;
  return rows;
 }
 static Element Declaration(JsonObject units,string id)=>new Parser(units[id]?["draft"]?.ToString()??throw new InvalidOperationException("Read the complete original whole/native source"),"<whole-native-source>").ParseElement();
 internal static HashSet<string>? Prepare(JsonObject request,JsonArray changes,JsonObject units,Func<Element,string> format)
 {
  var rows=Edits(changes);if(rows is null)return null;
  string owner=request["id"]!.ToString();var functions=new HashSet<string>(StringComparer.Ordinal);var sources=new HashSet<string>(StringComparer.Ordinal);bool native=false;
  if(units[owner]?["kind"]?.ToString()!="schema"||units.Count>240)throw new InvalidOperationException("Keep the complete whole/native owner observation within its existing read budget");
  var information=Declaration(units,owner);
  foreach(var row in rows){
   string id=row!["id"]!.ToString();var original=Declaration(units,id);var mapping=row["mapping"]!.AsObject();var signature=original.Signature;
   if(row.AsObject().Any(p=>p.Key is not ("type" or "id" or "hash" or "name" or "description" or "signature" or "mapping" or "icon" or "returnName" or "argumentNames"))||!functions.Add(id)||!id.StartsWith(owner+"_Function_",StringComparison.Ordinal)||!information.Contains.Any(child=>child.Id==id&&child.Kind=="function")||original.Id!=id||original.Kind!="function"||original.Parent is not null||signature is null||!JsonNode.DeepEquals(mapping["before"],FeatureBlueprint.SignatureDocument(signature))||mapping.Count!=3+(mapping["callers"] is null?0:1)||mapping.Any(p=>p.Key is not ("before" or "args" or "bodies" or "callers"))||mapping["args"] is not JsonObject args||args.Count!=signature.Args.Count||signature.Args.Any(a=>args[a.Name]?.ToString()!=a.Name))throw new InvalidOperationException("Whole/native groups retain exact public contracts and explicit pin identities");
   foreach(var caller in mapping["callers"] as JsonObject??new()){
    var callerPlan=caller.Value?.AsObject()??throw new ArgumentException("Exact original caller plan required");var outputs=FeatureBlueprint.FeatureOutputs(signature).ToArray();
    if(callerPlan.Count!=5+(callerPlan["outputs"] is null?0:1)||callerPlan.Any(p=>p.Key is not ("graph" or "node" or "hash" or "inputs" or "disconnect" or "outputs"))||callerPlan["inputs"] is not JsonObject inputMap||inputMap.Count!=signature.Args.Count(arg=>!arg.IsOut)||signature.Args.Where(arg=>!arg.IsOut).Any(arg=>inputMap[arg.Name]?.ToString()!=arg.Name)||callerPlan["disconnect"] is not JsonObject disconnect||disconnect.Count!=0||callerPlan["outputs"] is JsonObject outputMap&&(outputMap.Count!=outputs.Length||outputs.Any(output=>outputMap[output.Name]?.ToString()!=output.Name)))throw new InvalidOperationException("Retain every original caller input/output binding; source-only groups do not rewire consumers");
   }
   var body=mapping["bodies"]!.AsObject().Single();string source=body.Key;var plan=body.Value!.AsObject();
   int marker=source.LastIndexOf("/body:",StringComparison.Ordinal);if(marker<0||!sources.Add(source))throw new ArgumentException("One explicit owned source per function required");
   string implementationId=source[..marker];var implementation=Declaration(units,implementationId);
   if(implementation.Id!=implementationId||implementation.Function!=id||implementation.Parent is not null||implementation.Imports.Count!=0||implementation.Bodies.Count!=1||!JsonNode.DeepEquals(plan["contract"],row["signature"]))throw new InvalidOperationException("Retain the exact direct source declaration; callee/import changes require their separate explicit plan");
   var target=implementation.Bodies.Single();string graphId=implementationId+"/body:"+target.Key;
   if(plan["whole"] is JsonObject whole){
    string key=whole["node"]!.ToString();
    if(target.Value.SourceKind!="blueprint"||units[graphId]?["kind"]?.ToString()!="blueprint"||units[source]?["kind"]?.ToString()!="blueprint-node"||whole["graph"]?.ToString()!=graphId||source!=BlueprintTree.SourceId(graphId,key))throw new InvalidOperationException("Keep the original exact whole-body graph and source receipt");
    var graph=JsonNode.Parse(units[graphId]!["draft"]!.ToString())!.AsObject();
    if(key.Contains('/')){
     // The qualified node owns its native ABI; the parent owns its frame.
     // The original single-source validator authenticates the receipt, code,
     // helper boundary and assembled context, without rewriting either ABI.
     var node=BlueprintTree.Nodes(graph).Single(entry=>entry.Key==key).Node;
     if(node["kind"]?.ToString()!="code"||node["control"]?.ToString() is not ("next" or "branch" or "switch")||node["implementationContext"] is not null||!JsonNode.DeepEquals(plan["beforeSignature"],node["signature"])||!JsonNode.DeepEquals(FeatureBlueprint.SignatureDocument(implementation.Signature!),row["signature"]))throw new InvalidOperationException("Retain the exact private code ABI and its parent frame/native declaration");
    }else if(!JsonNode.DeepEquals(plan["beforeSignature"],FeatureBlueprint.SignatureDocument(implementation.Signature!)))throw new InvalidOperationException("Retain the original whole-body native declaration");
    else if(!InformationFunctionRetained.IsLift(graph)){
     // Existing retained preparation owns every independent node/local/alias.
     // This group changes explicit source text only: keep the original native
     // outputs and positional storage, with no inferred consumer rewrite.
     var contexts=graph["nodes"]!.AsArray().Where(node=>node?["implementationContext"] is not null||node?["forwardCallerStorage"]?.GetValue<bool>()==true).ToArray();var outputs=FeatureBlueprint.FeatureOutputs(implementation.Signature!).ToArray();
     if(contexts.Length!=1||contexts[0]?["implementationContext"] is null||contexts[0]?["id"]?.ToString()!=whole["node"]?.ToString()||plan["outputs"] is not JsonObject selectedOutputs||selectedOutputs.Count!=outputs.Length||outputs.Any(output=>selectedOutputs[output.Name]?.ToString()!=output.Name))throw new InvalidOperationException("Explicitly retain each original output of one root context; private/storage or contract changes require their separate plan");
    }
   }else{
    native=true;if(target.Value.SourceKind!="csharp"||source!=graphId||units[source]?["kind"]?.ToString()!="body"||!JsonNode.DeepEquals(plan["beforeSignature"],FeatureBlueprint.SignatureDocument(implementation.Signature!)))throw new InvalidOperationException("Direct original native source required");
   }
   var implementations=units.Where(unit=>unit.Value?["kind"]?.ToString()=="implementation"&&Declaration(units,unit.Key).Function==id).Select(unit=>unit.Key).ToArray();
   if(implementations.Length!=1||implementations[0]!=implementationId)throw new InvalidOperationException("Review additional targets or implementations separately; no source is inferred");
   InformationFunctionContracts.Prepare(request,original,Declaration(units,id),mapping,format);
  }
  if(!native)throw new InvalidOperationException("This closure combines an existing whole-body source with an ordinary native body; retain other contexts separately");
  return functions;
 }
 static JsonObject Originals(JsonObject units)
 {
  var originals=units.DeepClone().AsObject();foreach(var unit in originals)if(unit.Value?["original"] is JsonValue text&&text.TryGetValue<string>(out string? value)&&value.Length>0)unit.Value!["draft"]=value;return originals;
 }
 static string Shape(string text,Func<Element,string> format)
 {
  var value=new Parser(text,"<whole-native-presentation>").ParseElement();value.Description="";value.DescriptionPresent=false;
  foreach(string key in new[]{"editorName","editorIcon",FunctionReturnName.Key,FunctionArgumentNames.Key})value.Values.Remove(key);
  return format(value);
 }
 static JsonArray Checks(JsonObject units,string ns,bool preparing)
 {
  if(units.Count>240)throw new ArgumentException("Whole/native source budget");var checks=new SortedDictionary<string,JsonNode>(StringComparer.Ordinal);
  foreach(var pair in units.Where(pair=>pair.Key.StartsWith(ns+"::",StringComparison.Ordinal))){var unit=pair.Value!;string path=unit["path"]!.ToString();if(Path.IsPathRooted(path)||path.Split('/','\\').Any(part=>part is ".." or "."))throw new ArgumentException("Original owned relative source required");string? hash=unit["baseline"]?.ToString();if(preparing&&(hash is null||!System.Text.RegularExpressions.Regex.IsMatch(hash,"^[a-f0-9]{64}$")))throw new InvalidOperationException("Read every existing whole/native source before Save");var check=new JsonObject{["path"]=path,["hash"]=preparing?hash:null};if(checks.TryGetValue(path,out var prior)&&!JsonNode.DeepEquals(prior,check))throw new InvalidOperationException("Source aliases disagree on their original version");checks[path]=check;}
  if(checks.Count is <1 or >240)throw new ArgumentException("Whole/native source budget");return new JsonArray(checks.Values.ToArray());
 }
 static JsonObject OriginalRequest(JsonObject request,string owner,JsonObject units)=>new(){["project"]=request["project"]!.DeepClone(),["manifest"]=units[request["namespace"]!.ToString()+"::ProjectManifest"]!["draft"]!.DeepClone(),["id"]=owner,["text"]=units[owner]!["draft"]!.DeepClone(),["drafts"]=new JsonArray(units.Where(row=>row.Key!=owner&&row.Value?["kind"]?.ToString() is "object" or "schema" or "function" or "implementation" or "module" or "category" or "concept" or "enum").Select(row=>(JsonNode)new JsonObject{["id"]=row.Key,["text"]=row.Value!["draft"]!.DeepClone()}).ToArray()),["units"]=units};
 static void Validate(JsonObject request,string owner,JsonObject receipt,Func<Element,string> format)
 {
  string ns=request["namespace"]!.ToString();var units=request["units"]!.AsObject();
  if(receipt["version"]?.GetValue<int>()!=3||receipt["owner"]?.ToString()!=owner||receipt[Capture] is not JsonArray plans||Edits(plans) is null||receipt["sources"] is not JsonObject proof||proof.Count>64||units[owner]?["atomicEditGroup"] is not JsonArray group||group.Count!=proof.Count||!proof.Select(p=>p.Key).ToHashSet(StringComparer.Ordinal).SetEquals(group.Select(id=>id!.ToString()))||receipt["readGuards"] is not JsonObject guards||new[]{"nativeBodyDependencies","nativeBodyDependencyReads","nativeBodyOwnerEdits","nativeBodyOwnerReads","nativeBodyValues","nativeBodyValueReads","nativeBodyCopies","nativeTypeProofs","nativeTypeReads"}.Any(receipt.ContainsKey))throw new InvalidOperationException("Retain the complete explicit whole/native receipt and atomic source group");
  var expected=Checks(units,ns,false);if(guards.Count!=expected.Count||expected.Any(row=>guards[row!["path"]!.ToString()] is not JsonObject read||read.Count!=2||read["path"]?.ToString()!=row["path"]!.ToString()||!System.Text.RegularExpressions.Regex.IsMatch(read["hash"]?.ToString()??"","^[a-f0-9]{64}$"))||guards.Count+proof.Count>240)throw new InvalidOperationException("Retain all original whole/native source checks without adding or dropping a path");
  var originals=Originals(units);var originalRequest=OriginalRequest(request,owner,originals);var functions=Prepare(originalRequest,plans,originals,format)??throw new InvalidOperationException("Original explicit whole/native plans required");
  var updates=new Dictionary<string,string>(StringComparer.Ordinal);var mandatory=new HashSet<string>(functions,StringComparer.Ordinal){owner,ns+"::ProjectManifest"};
  foreach(var row in plans){string id=row!["id"]!.ToString();if(row["hash"]?.ToString()!=Hash(originals[id]!["draft"]!.ToString()))throw new InvalidOperationException("Retain the original function plan basis");var candidate=InformationFunctionContracts.Prepare(originalRequest,Declaration(originals,id),Declaration(originals,id),row["mapping"]!.AsObject(),format);
   foreach(var update in candidate["updates"]!.AsArray()){string key=update!["id"]!.ToString(),text=update["text"]!.ToString();if(updates.TryGetValue(key,out string? prior)&&prior!=text)throw new InvalidOperationException("Original whole/native closures disagree on a retained source");updates[key]=text;if(text!=originals[key]!["draft"]!.ToString())mandatory.Add(key);}
   mandatory.UnionWith(row["mapping"]!["bodies"]!.AsObject().Select(body=>body.Key));
  }
  if(!mandatory.IsSubsetOf(proof.Select(p=>p.Key))||proof.Any(p=>!mandatory.Contains(p.Key)&&!updates.ContainsKey(p.Key)))throw new InvalidOperationException("Retain exactly the selected sources and their original closure members");
  foreach(var source in proof){var unit=units[source.Key]??throw new InvalidOperationException("Whole/native member missing");if(!source.Key.StartsWith(ns+"::",StringComparison.Ordinal)||source.Value?["path"]?.ToString()!=unit["path"]?.ToString()||source.Value?["kind"]?.ToString()!=unit["kind"]?.ToString()||source.Value?["hash"]?.ToString()!=Hash(unit["draft"]!.ToString())||unit["atomicEditGroup"] is not JsonArray members||!JsonNode.DeepEquals(members,group))throw new InvalidOperationException("Whole/native source identity, draft or group changed");}
  foreach(var unit in units.Where(p=>p.Key.StartsWith(ns+"::",StringComparison.Ordinal))){string id=unit.Key;string original=originals[id]?["draft"]?.ToString()??throw new InvalidOperationException("Hydrate every known original whole/native source before review");string current=unit.Value?["draft"]?.ToString()??throw new InvalidOperationException("Hydrate every known current whole/native source before review");
   if(id==owner||functions.Contains(id)){if(Shape(current,format)!=Shape(original,format))throw new InvalidOperationException("A whole/native presentation save cannot change contracts, ownership or structure");}
   else if(current!=(updates.GetValueOrDefault(id)??original))throw new InvalidOperationException("Retain the exact replayed whole/native source and unchanged surrounding graph");
  }
 }
 static bool Local(JsonNode? row,JsonObject units,JsonArray plans)
 {
  if(InformationFunctionBodyBatch.Presentation(row))return true;
  if(row?["type"]?.ToString()!="function-edit"||row["id"] is not JsonValue id)return false;
  var saved=plans.SingleOrDefault(p=>p?["id"]?.ToString()==id.ToString());if(saved is null||!JsonNode.DeepEquals(row["signature"],saved["signature"]))return false;
  if(row["mapping"] is not JsonObject mapping)return true;
  if(!JsonNode.DeepEquals(mapping["before"],saved["signature"])||!JsonNode.DeepEquals(mapping["args"],saved["mapping"]!["args"])||mapping.Any(p=>p.Key is not ("before" or "args" or "bodies" or "callers"))||mapping.ContainsKey("callers")&&!JsonNode.DeepEquals(mapping["callers"],saved["mapping"]!["callers"]))return false;
  if(mapping["bodies"] is not JsonObject bodies||bodies.Count==0)return true;
  var prior=saved["mapping"]!["bodies"]!.AsObject();if(bodies.Count!=prior.Count)return false;
  foreach(var body in bodies){if(prior[body.Key] is not JsonObject old||body.Value is not JsonObject next||next["hash"]?.ToString()!=Hash(units[body.Key]!["draft"]!.ToString())||old.ContainsKey("helpers")!=next.ContainsKey("helpers"))return false;var a=old.DeepClone().AsObject();var b=next.DeepClone().AsObject();foreach(string key in new[]{"hash","text","helpers"}){a.Remove(key);b.Remove(key);}if(!JsonNode.DeepEquals(a,b))return false;old["text"]=next["text"]!.DeepClone();if(next.ContainsKey("helpers"))old["helpers"]=next["helpers"]!.DeepClone();}return true;
 }
 internal static JsonObject? Guards(JsonObject request,Func<Element,string> formatElement,Func<Manifest,string> format)
 {
  string ns=request["namespace"]!.ToString(),action=request["action"]!.ToString();var units=request["units"]!.AsObject();
  if(action=="prepare"){
   string? owner=request["declaration"]?["id"]?.ToString();if(owner is null)return null;var declaration=request["declaration"]!;var prior=units[owner]?["slotSaveReceipt"] as JsonObject;
   if(prior?.ContainsKey(Capture)==true){
    Validate(request,owner,prior,formatElement);var plans=prior[Capture]!.DeepClone().AsArray();if(declaration["raw"] is not null||declaration["changes"] is not JsonArray changes||changes.Count is <1 or >10||!changes.All(row=>Local(row,units,plans)))throw new InvalidOperationException("Retain the explicit whole/native plans; review other contract or structure edits separately");
    return new JsonObject{["required"]=true,["contexts"]=plans,["checks"]=new JsonArray(prior["readGuards"]!.AsObject().Select(p=>p.Value!.DeepClone()).ToArray())};
   }
   if(declaration["raw"] is not null||declaration["changes"] is not JsonArray selected||Edits(selected) is not {} edits)return null;
   if(prior is not null)throw new InvalidOperationException("Retain the existing pending source group; do not replace it with a new context scope");
   var originalRequest=OriginalRequest(request,owner,units.DeepClone().AsObject());Prepare(originalRequest,selected,units,formatElement);
   return new JsonObject{["required"]=true,["contexts"]=new JsonArray(edits.Select(row=>row!.DeepClone()).ToArray()),["checks"]=Checks(units,ns,true)};
  }
  if(action is not ("headers" or "graphs" or "validate"))return null;
  var selection=request["selected"]?.AsArray()??throw new ArgumentException("Selected whole/native group required");if(selection.Count>64)throw new ArgumentException("Whole/native Review budget");
  bool Affected(string owner,JsonNode? unit)=>selection.Any(id=>id?.ToString()==owner||unit?["atomicEditGroup"] is JsonArray group&&group.Any(member=>member?.ToString()==id?.ToString())||unit?["slotSaveReceipt"]?["sources"] is JsonObject proof&&proof.ContainsKey(id!.ToString()));
  foreach(var pair in units){if(pair.Value?["slotSaveReceipt"] is not JsonObject receipt||receipt.ContainsKey(Capture)||!Affected(pair.Key,pair.Value)||receipt["sources"] is not JsonObject proof)continue;
   if(proof.Count(p=>p.Value?["kind"]?.ToString()=="function")>=2&&proof.Any(p=>p.Value?["kind"]?.ToString()=="body")&&proof.Any(p=>p.Value?["kind"]?.ToString()=="blueprint-node"))throw new InvalidOperationException("Explicit whole/native context receipt missing; retain the complete source group");
  }
  var owners=units.Where(p=>p.Value?["slotSaveReceipt"] is JsonObject receipt&&receipt.ContainsKey(Capture)&&Affected(p.Key,p.Value)).Select(p=>p.Key).ToArray();if(owners.Length==0)return null;
  var delegated=request.DeepClone().AsObject();foreach(string owner in owners){if(action=="validate")Validate(request,owner,units[owner]!["slotSaveReceipt"]!.AsObject(),formatElement);delegated["units"]![owner]!.AsObject().Remove("slotSaveReceipt");}
  var other=InformationFunctionBodyGuards.Execute(delegated,formatElement,format);if(action=="validate")return other;
  if(units.Count>240)throw new ArgumentException("Whole/native read budget");var ids=other["ids"]!.AsArray().Select(id=>id!.ToString()).ToHashSet(StringComparer.Ordinal);
  // Known registered owned units only. Cold restore rehydrates the same paths;
  // it neither discovers a new locator nor adopts a current physical baseline.
  if(action=="headers")ids.UnionWith(units.Where(p=>p.Key.StartsWith(ns+"::",StringComparison.Ordinal)).Select(p=>p.Key));
  return new JsonObject{["ids"]=new JsonArray(ids.Order(StringComparer.Ordinal).Select(id=>(JsonNode)JsonValue.Create(id)!).ToArray())};
 }
}
