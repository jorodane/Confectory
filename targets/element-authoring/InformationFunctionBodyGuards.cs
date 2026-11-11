using Confectory.Core;
using System.Text.Json.Nodes;

// Keep the already observed owned source snapshot as read checks, never writes.
// The existing slot receipt and final source lease carry these checks unchanged.
internal static class InformationFunctionBodyGuards
{
 // Authenticate only an already captured source shape. This does not create
 // edit plans, adopt a current file as an original or infer a caller binding.
 static JsonObject PresentationMap(FunctionSignature before,FunctionSignature after)
 {
  var map=new JsonObject();
  if(before.Args.Count!=after.Args.Count){foreach(var arg in before.Args)map[arg.Name]=after.Args.Contains(arg)?arg.Name:null;return map;}
  for(int i=0;i<before.Args.Count;i++)map[before.Args[i].Name]=after.Args[i].Name;
  if(!InformationFunctionBodyBatch.ValueNames(before,after,map))for(int i=0;i<before.Args.Count;i++)if(before.Args[i].Type!=after.Args[i].Type)map[before.Args[i].Name]=null;
  return map;
 }
 public static JsonObject Execute(JsonObject request,Func<Manifest,string> format)
 {
  string ns=request["namespace"]!.ToString();var units=request["units"]!.AsObject();
  bool FunctionPresentation(string owner,JsonNode? row)
  {
   // The existing name/description editor sends a same-contract function row.
   // Keep its saved body scope; an ABI mapping is a separate explicit edit.
   if(row is not JsonObject value||value["type"]?.ToString()!="function-edit"||value.Count is <6 or >10||value.Any(p=>p.Key is not ("type" or "id" or "hash" or "name" or "description" or "signature" or "icon" or "returnName" or "argumentNames" or "mapping")))return false;
   string? id=value["id"]?.ToString();if(id is null||!id.StartsWith(owner+"_Function_",StringComparison.Ordinal)||units[id]?["kind"]?.ToString()!="function"||units[id]?["original"] is not JsonValue original||units[id]?["draft"] is not JsonValue draft)return false;
   // An unconfirmed declaration-only creation has no original native body
   // header. Its separate native type receipt still guards the selected source.
   // Never adopt a draft as an original or bypass a body-bearing group here.
   if(original.ToString().Length==0){
    if(units[id]?["baseline"]?.ToString()!="missing"||units[owner]?["atomicEditGroup"]is not JsonArray created||!created.Any(member=>member?.ToString()==id)||created.Any(member=>units[member!.ToString()]?["kind"]?.ToString() is "implementation" or "body" or "blueprint" or "blueprint-node"))throw new InvalidOperationException("A created native body group requires its original source proof; retain the group for explicit review");
    var pending=new Parser(draft.ToString(),"<created-function-presentation>").ParseElement();if(pending.Id!=id||pending.Kind!="function"||pending.Parent is not null||pending.Signature is null||!JsonNode.DeepEquals(FeatureBlueprint.SignatureDocument(pending.Signature),value["signature"]))throw new InvalidOperationException("Retain the exact created function contract before changing its presentation");
    return false;
   }
   var before=new Parser(original.ToString(),"<retained-native-header>").ParseElement();var after=new Parser(draft.ToString(),"<retained-native-header>").ParseElement();
   if(before.Id!=id||after.Id!=id||before.Kind!="function"||after.Kind!="function"||before.Parent is not null||after.Parent is not null||before.Signature is null||after.Signature is null||!JsonNode.DeepEquals(FeatureBlueprint.SignatureDocument(after.Signature),value["signature"]))return false;
   if(value["mapping"] is not null){
    if(value["mapping"]?["bodies"] is JsonObject bodies&&bodies.Count>0)return false;
    if(value["mapping"] is not JsonObject identity||identity.Count!=2||!JsonNode.DeepEquals(identity["before"],value["signature"])||identity["args"] is not JsonObject args||args.Count!=after.Signature.Args.Count||after.Signature.Args.Any(a=>args[a.Name]?.ToString()!=a.Name))throw new InvalidOperationException("Function presentation retains the exact current contract and identity map; all input retained");
   }
   if(JsonNode.DeepEquals(FeatureBlueprint.SignatureDocument(before.Signature),value["signature"]))return true;
   // A prior explicit value-name/body Save may already have captured this
   // different public spelling. Metadata editing retains that exact draft;
   // it cannot adopt a new contract or rebase the saved native read scope.
   var receipt=units[owner]?["slotSaveReceipt"];var proof=receipt?["sources"]?[id];
   if(proof?["kind"]?.ToString()!="function"||proof["path"]?.ToString()!=units[id]?["path"]?.ToString()||proof["hash"]?.ToString()!=JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(draft.ToString()))||before.Signature.Args.Count!=after.Signature.Args.Count&&!NativeGroup(owner)){if(NativeGroup(owner))throw new InvalidOperationException("Retain the exact captured function source before editing its presentation; all input retained");return false;}
   var map=PresentationMap(before.Signature,after.Signature);
   if(!InformationFunctionBodyBatch.ValueNames(before.Signature,after.Signature,map)){
    if(!NativeGroup(owner)||!(InformationFunctionNativeInputs.Types(before.Signature,after.Signature,map)||InformationFunctionNativeReturns.Types(before.Signature,after.Signature,map)||InformationFunctionNativeOutputs.Types(before.Signature,after.Signature,map))||!receipt!["sources"]!.AsObject().Any(p=>p.Value?["kind"]?.ToString()=="implementation"))throw new InvalidOperationException("Retain the captured explicit native contract before editing its presentation; all input retained");
   }return true;
  }
  bool PresentationOnly(JsonNode? declaration)=>declaration?["raw"] is null&&declaration?["id"] is JsonValue owner&&declaration?["changes"] is JsonArray changes&&changes.Count is >=1 and <=2&&changes.All(row=>InformationFunctionBodyBatch.Presentation(row)||FunctionPresentation(owner.ToString(),row));
  bool TypedFunction(string id)
  {
   if(units[id]?["kind"]?.ToString()!="function")return false;string? text=units[id]?["original"]?.ToString();if(string.IsNullOrEmpty(text))text=units[id]?["draft"]?.ToString();if(text is null)return false;var function=new Parser(text,"<information-value-source-scope>").ParseElement();return function.Kind=="function"&&function.Signature is not null&&InformationStructs.SignatureTypes(function.Signature).Any();
  }
  JsonNode?[]? NativeEdits(JsonArray changes)
  {
   if(InformationFunctionNativeOutputs.Edits(changes) is {} outputGroup)return outputGroup;
   if(InformationFunctionNativeReturns.Edits(changes) is {} returnGroup)return returnGroup;
   if(InformationFunctionNativeInputs.Edits(changes) is {} inputGroup)return inputGroup;
   if(InformationFunctionBodyBatch.Edits(changes) is {} group)return group;
   var edits=changes.Where(row=>!InformationFunctionBodyBatch.Presentation(row)).ToArray();return changes.Count<=3&&edits.Length==1&&InformationFunctionBodyBatch.BodyEdit(edits[0])&&TypedFunction(edits[0]!["id"]!.ToString())?edits:null;
  }
  bool NativeGroup(string owner)
  {
   if(units[owner]?["kind"]?.ToString()!="schema"||units[owner]?["atomicEditGroup"] is not JsonArray group||group.Count>64)return false;
   var ids=group.Select(value=>value!.ToString()).ToArray();if(!ids.Contains(owner)||!ids.Contains(ns+"::ProjectManifest"))return false;
   var functions=ids.Where(id=>units[id]?["kind"]?.ToString()=="function").ToArray();int bodies=ids.Count(id=>units[id]?["kind"]?.ToString()=="body"),callers=ids.Count(id=>units[id]?["kind"]?.ToString()=="blueprint");
   int implementations=ids.Count(id=>units[id]?["kind"]?.ToString()=="implementation");
   return functions.Length is >=1 and <=8&&(functions.Length>1||TypedFunction(functions[0]))&&(callers==0||functions.Length>1)&&functions.All(id=>id.StartsWith(owner+"_Function_",StringComparison.Ordinal))&&bodies>=functions.Length&&(implementations==0||functions.Length>1&&implementations<=bodies+callers)&&ids.Length==2+functions.Length+bodies+callers+implementations;
  }
  (HashSet<string> Functions,string[] Bodies)? RetainedSources(string owner,JsonObject receipt)
  {
   bool native=NativeGroup(owner)&&(PresentationOnly(receipt["declaration"])||receipt["declaration"]?["changes"] is JsonArray saved&&NativeEdits(saved) is not null);
   if(units[owner]?["kind"]?.ToString()!="schema"||receipt["declaration"]?["raw"] is not null||receipt["sources"] is not JsonObject proof||proof[owner]?["kind"]?.ToString()!="schema"||proof[ns+"::ProjectManifest"]?["kind"]?.ToString()!="project"){
    if(native)throw new InvalidOperationException("Retain the complete saved native body group proof; all input retained");return null;
   }
   var functions=proof.Where(p=>p.Value?["kind"]?.ToString()=="function").Select(p=>p.Key).ToHashSet(StringComparer.Ordinal);var bodies=proof.Where(p=>p.Value?["kind"]?.ToString()=="body").Select(p=>p.Key).ToArray();
   var callers=proof.Where(p=>p.Value?["kind"]?.ToString()=="blueprint").Select(p=>p.Key).ToArray();
   var implementations=proof.Where(p=>p.Value?["kind"]?.ToString()=="implementation").Select(p=>p.Key).ToArray();
   if(functions.Count is <1 or >8||functions.Count==1&&!TypedFunction(functions.Single())||bodies.Length<functions.Count||implementations.Length>0&&(functions.Count<2||implementations.Length>bodies.Length+callers.Length)||proof.Count>64||proof.Count!=2+functions.Count+bodies.Length+callers.Length+implementations.Length||units[owner]?["atomicEditGroup"] is not JsonArray group||group.Count!=proof.Count||!proof.Select(p=>p.Key).ToHashSet(StringComparer.Ordinal).SetEquals(group.Select(id=>id!.ToString()))){
    if(native)throw new InvalidOperationException("Retain every saved native target proof and group member; all input retained");return null;
   }
   if(!(receipt["declaration"]?["changes"] is JsonArray edits&&NativeEdits(edits) is not null)&&!PresentationOnly(receipt["declaration"]))return null;
   foreach(var source in proof)if(!source.Key.StartsWith(ns+"::",StringComparison.Ordinal)||units[source.Key]?["kind"]?.ToString()!=source.Value?["kind"]?.ToString()||units[source.Key]?["path"]?.ToString()!=source.Value?["path"]?.ToString())throw new InvalidOperationException("Retain the exact owned native group sources before editing its presentation");
   foreach(string id in implementations){
    if(request["action"]?.ToString()=="headers")continue;
    var d=OriginalImplementation(id);bool callee=functions.Contains(d.Function!),consumer=d.Imports.Values.Any(i=>functions.Contains(i.Id));
    if(d.Id!=id||d.Parent is not null||callee==consumer||d.Bodies.Count!=1||callee&&(!InformationFunctionBodyBatch.NativeTargets(d)||!bodies.Contains(id+"/body:"+d.Bodies.Keys.Single()))||consumer&&(d.Bodies.Values.Single().SourceKind!="blueprint"||!callers.Contains(id+"/body:"+d.Bodies.Keys.Single())))throw new InvalidOperationException("Retain only the captured native input declarations and ordinary caller import contracts");
   }
   // A saved explicit value-name edit also owns the changed caller graph.
   // Retain only ordinary owned consumers of this native group; qualified
   // C# records remain reads and never become additional write members.
   if(callers.Length>0){
    if(functions.Count<2||functions.Any(id=>!id.StartsWith(owner+"_Function_",StringComparison.Ordinal)))throw new InvalidOperationException("Retain the original named native group ownership");
    foreach(string id in callers){int at=id.LastIndexOf("/body:",StringComparison.Ordinal);if(at<0)throw new ArgumentException("Exact saved caller body required");
     // Cold header discovery precedes reading the owned declarations. The
     // graphs/prepare/validate phases below still prove their complete source.
     if(request["action"]?.ToString()=="headers")continue;
     var implementation=OriginalImplementation(id[..at]);string target=id[(at+6)..];string text=units[id]?["original"]?.ToString()??units[id]?["draft"]?.ToString()??throw new ArgumentException("Original saved caller graph required");
     if(implementation.Parent is not null||!implementation.Bodies.TryGetValue(target,out var body)||body.SourceKind!="blueprint"||!implementation.Imports.Values.Any(import=>functions.Contains(import.Id))||!InformationFunctionBodyBatch.NamedCaller(JsonNode.Parse(text)!.AsObject()))throw new InvalidOperationException("Retain the original ordinary named caller scope");
    }
   }
   return(functions,bodies);
  }
  Element OriginalImplementation(string id)
  {
   var unit=units[id];if(!id.StartsWith(ns+"::",StringComparison.Ordinal)||unit?["kind"]?.ToString()!="implementation")throw new ArgumentException("Owned native implementation required");
   string? text=unit["original"]?.ToString();if(string.IsNullOrEmpty(text))text=unit["draft"]?.ToString();if(text is null)throw new InvalidOperationException("Read original native headers before reviewing the saved group");return new Parser(text,"<native-body-read-scope>").ParseElement();
  }
  bool ObservedScope(HashSet<string> functions,IEnumerable<(string Function,string Body)> targets)
  {
   bool observed=functions.Any(TypedFunction);var seen=new HashSet<string>(StringComparer.Ordinal);var expected=new HashSet<string>(StringComparer.Ordinal);var selected=new HashSet<string>(StringComparer.Ordinal);
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
     if(graph["copySource"] is not null||graph["locals"] is JsonArray locals&&locals.Count>0||graph["aliases"] is JsonObject aliases&&aliases.Count>0||graph["nodes"] is JsonArray nodes&&nodes.Any(node=>node?["kind"]?.ToString() is "code" or "graph"||node?["postCall"] is not null))return true;
    }
   }
   return false;
  }
  bool ObservedGroup(JsonNode? declaration)
  {
   if(declaration?["raw"] is not null||declaration?["changes"] is not JsonArray changes||NativeEdits(changes) is not {} edits)return false;
   var functions=edits.Select(row=>row!["id"]!.ToString()).ToHashSet(StringComparer.Ordinal);bool observed=ObservedScope(functions,edits.SelectMany(row=>row!["mapping"]!["bodies"]!.AsObject().Select(body=>(row["id"]!.ToString(),body.Key))));return observed||InformationFunctionNativeInputs.Edits(changes) is not null||InformationFunctionNativeReturns.Edits(changes) is not null||InformationFunctionNativeOutputs.Edits(changes) is not null;
  }
  bool ObservedReceipt(string owner,JsonObject receipt)
  {
   if(ObservedGroup(receipt["declaration"]))return true;
   // A peer may remove the retained caller state after Save. The already bound
   // read scope still applies; never infer a new empty legacy receipt from it.
   if(receipt["declaration"]?["changes"] is JsonArray saved&&NativeEdits(saved) is not null&&receipt["readGuards"] is JsonObject savedGuards&&savedGuards.Count>0)return true;
   if(!PresentationOnly(receipt["declaration"])||RetainedSources(owner,receipt) is not {} retained)return false;
   // A subsequent header Save keeps only an already saved, same-contract native
   // body group. No body edit or dependency baseline is reconstructed or rebased.
   foreach(string function in retained.Functions){var unit=units[function]!;string draft=unit["draft"]?.ToString()??throw new InvalidOperationException("Read the retained native function contract");string original=unit["original"]?.ToString()??draft;var before=new Parser(original,"<retained-function>").ParseElement();var after=new Parser(draft,"<retained-function>").ParseElement();if(before.Id!=function||after.Id!=function||before.Kind!="function"||before.Parent is not null||after.Parent is not null||before.Signature is null||after.Signature is null)return false;
    if(!JsonNode.DeepEquals(FeatureBlueprint.SignatureDocument(before.Signature),FeatureBlueprint.SignatureDocument(after.Signature))){var map=PresentationMap(before.Signature,after.Signature);bool compatible=InformationFunctionBodyBatch.ValueNames(before.Signature,after.Signature,map);if(!compatible){compatible=receipt["sources"]!.AsObject().Any(source=>source.Value?["kind"]?.ToString()=="implementation")&&(InformationFunctionNativeInputs.Types(before.Signature,after.Signature,map)||InformationFunctionNativeReturns.Types(before.Signature,after.Signature,map)||InformationFunctionNativeOutputs.Types(before.Signature,after.Signature,map));}if(!receipt["sources"]!.AsObject().Any(source=>source.Value?["kind"]?.ToString()=="blueprint")||!compatible)return false;}
   }
   bool observed=ObservedScope(retained.Functions,retained.Bodies.Select(body=>{int at=body.LastIndexOf("/body:",StringComparison.Ordinal);if(at<0)throw new ArgumentException("Retained native body owner required");return(OriginalImplementation(body[..at]).Function!,body);}));return observed||receipt["sources"]!.AsObject().Any(source=>source.Value?["kind"]?.ToString()=="implementation")||receipt["readGuards"] is JsonObject retainedGuards&&retainedGuards.Count>0;
  }
  if(request["action"]?.ToString()=="headers"){
   var headerSelection=request["selected"]?.AsArray()??throw new ArgumentException("Selected native group required");if(headerSelection.Count>64)throw new ArgumentException("Native body header budget");bool native=false;var functions=new HashSet<string>(StringComparer.Ordinal);
   foreach(var id in headerSelection){string owner=id!.ToString();if(units[owner]?["slotSaveReceipt"] is not JsonObject receipt)continue;if(receipt["declaration"]?["changes"] is JsonArray changes&&NativeEdits(changes) is not null)native=true;if(RetainedSources(owner,receipt) is {} retained){native=true;functions.UnionWith(retained.Functions);}}
   bool copies=headerSelection.Any(id=>units[id!.ToString()]?["slotSaveReceipt"] is JsonObject receipt&&CopyProofs(receipt["declaration"],receipt).Count>0);
   if(native&&units.Count>2048)throw new ArgumentException("Native body header budget");return new JsonObject{["ids"]=new JsonArray((native?units.Where(pair=>pair.Key.StartsWith(ns+"::",StringComparison.Ordinal)&&(copies&&pair.Value?["kind"]?.ToString() is "function" or "object" or "schema" or "module" or "category" or "concept" or "enum"||pair.Value?["kind"]?.ToString()=="implementation"||functions.Contains(pair.Key))).Select(pair=>(JsonNode)JsonValue.Create(pair.Key)!):Enumerable.Empty<JsonNode>()).ToArray())};
  }
  if(request["action"]?.ToString()=="graphs"){
   var selection=request["selected"]?.AsArray()??throw new ArgumentException("Selected native group required");if(selection.Count>64)throw new ArgumentException("Native body review budget");var functions=new HashSet<string>(StringComparer.Ordinal);
   foreach(var selectedOwner in selection){string owner=selectedOwner!.ToString();if(units[owner]?["slotSaveReceipt"] is not JsonObject receipt)continue;if(receipt["declaration"]?["changes"] is JsonArray changes&&NativeEdits(changes) is {} edits)functions.UnionWith(edits.Select(row=>row!["id"]!.ToString()));if(RetainedSources(owner,receipt) is {} retained)functions.UnionWith(retained.Functions);}
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
  JsonObject CopyProofs(JsonNode? declaration,JsonObject? receipt=null)
  {
   var declared=new JsonObject();foreach(var change in declaration?["changes"] as JsonArray??new())if(change?["mapping"]?["copies"] is JsonObject copies&&copies.Count>0)declared.Add(change["id"]!.ToString(),copies.DeepClone());
   if(receipt?["nativeBodyCopies"] is JsonObject retained){if(declared.Count>0&&!JsonNode.DeepEquals(declared,retained))throw new InvalidOperationException("Retain the original native copy proofs across presentation saves");declared=retained.DeepClone().AsObject();}
   if(declared.Count>8||declared.Any(row=>row.Value is not JsonObject copies||copies.Count is <1 or >32))throw new ArgumentException("Bounded native copy proof group required");return declared;
  }
  JsonArray Checks(string owner,JsonObject receipt)
  {
   if(receipt["owner"]?.ToString()!=owner||receipt["version"]?.GetValue<int>()!=3||receipt["readGuards"] is not JsonObject guards)throw new InvalidOperationException("Save the native body group explicitly to bind its original dependencies; input retained");var expected=Sources(false);var copies=CopyProofs(receipt["declaration"],receipt);
   var nativeFunctions=(receipt["sources"] as JsonObject??new()).Where(source=>source.Value?["kind"]?.ToString()=="function").Select(source=>source.Key).ToHashSet(StringComparer.Ordinal);
   string GraphSource(JsonNode? unit)=>string.IsNullOrEmpty(unit?["original"]?.ToString())?unit?["draft"]?.ToString()??"{}":unit["original"]!.ToString();
   bool copyCaller=units.Any(source=>source.Value?["kind"]?.ToString()=="blueprint"&&JsonNode.Parse(GraphSource(source.Value))?["copySource"] is not null&&source.Key.Contains("/body:",StringComparison.Ordinal)&&OriginalImplementation(source.Key[..source.Key.LastIndexOf("/body:",StringComparison.Ordinal)]).Imports.Values.Any(import=>nativeFunctions.Contains(import.Id)));
   if(copies.Count>0||copyCaller){
    string project=request["project"]?.ToString()??throw new InvalidOperationException("Original native copy project context required"),root=Path.GetDirectoryName(Path.GetFullPath(project))!;var originals=units.DeepClone().AsObject();foreach(var source in originals)if(source.Value?["original"] is JsonValue text&&text.TryGetValue<string>(out string? original)&&original.Length>0)source.Value!["draft"]=original;
    var manifest=originals[ns+"::ProjectManifest"]??throw new InvalidOperationException("Original native copy registration required");var originalRequest=new JsonObject{["project"]=project,["manifest"]=manifest["draft"]!.DeepClone(),["units"]=originals};var reader=new InformationFunctionCopies(originalRequest);
    var verified=new JsonObject();foreach(string function in nativeFunctions){var proof=reader.Read(function);if(proof.Count>0)verified[function]=proof;}
    if(!JsonNode.DeepEquals(verified,copies))throw new InvalidOperationException("Original native copy observation proofs changed or are incomplete; retain the complete group");
    foreach(var copy in verified)foreach(var proof in copy.Value!.AsObject())foreach(var dependency in proof.Value!["context"]!.AsArray()){
     string path=Path.GetFullPath(dependency!["path"]!.ToString());if(!path.StartsWith(root+Path.DirectorySeparatorChar,OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal))continue;string relative=Path.GetRelativePath(root,path);expected.TryAdd(relative,new JsonObject{["path"]=relative});
    }
   }
   // A body edit can also retain the native type/usage selection receipt.
   // Re-resolve that existing read-only scope before adding its owned paths;
   // never accept arbitrary extra paths supplied in a saved body receipt.
   if(receipt["nativeTypeProofs"] is not null){
    var native=FunctionNativeTypes.Guards(new JsonObject{["action"]="validate",["project"]=request["project"]!.DeepClone(),["namespace"]=ns,["units"]=units.DeepClone(),["selected"]=new JsonArray(owner)},format);
    string root=Path.GetDirectoryName(Path.GetFullPath(request["project"]!.ToString()))!;
    foreach(var read in native["reads"]!.AsArray()){
     string path=Path.GetFullPath(read!["path"]!.ToString());
     if(path.StartsWith(root+Path.DirectorySeparatorChar,OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal)){string relative=Path.GetRelativePath(root,path);expected.TryAdd(relative,new JsonObject{["path"]=relative});}
    }
   }
   if(guards.Count!=expected.Count||expected.Keys.Any(path=>guards[path] is not JsonObject row||row.Count!=2||row["path"]?.ToString()!=path||row["hash"] is null||!Token(row["hash"]!.ToString())))throw new InvalidOperationException("Complete original native body source checks are missing or changed; retain the saved group");return new JsonArray(guards.Select(p=>p.Value!.DeepClone()).ToArray());
  }
  if(request["action"]?.ToString()=="prepare"){
   if(ObservedGroup(request["declaration"]))return new JsonObject{["required"]=true,["copies"]=CopyProofs(request["declaration"]),["checks"]=new JsonArray(Sources(true).Values.Select(v=>(JsonNode)v).ToArray())};
   string? owner=request["declaration"]?["id"]?.ToString();if(owner is not null&&PresentationOnly(request["declaration"])&&units[owner]?["slotSaveReceipt"] is JsonObject prior&&RetainedSources(owner,prior) is not null&&(ObservedReceipt(owner,prior)||prior["readGuards"] is JsonObject priorGuards&&priorGuards.Count>0))return new JsonObject{["required"]=true,["checks"]=Checks(owner,prior),["copies"]=CopyProofs(prior["declaration"],prior)};
   return new JsonObject{["required"]=false,["checks"]=new JsonArray()};
  }
  if(request["action"]?.ToString()!="validate")throw new ArgumentException("Native body guard action");var selected=request["selected"]?.AsArray()??throw new ArgumentException("Selected native group required");if(selected.Count>64)throw new ArgumentException("Native body review budget");
  foreach(var pair in units){var unit=pair.Value;if(unit?["atomicEditGroup"] is not JsonArray group||!selected.Any(id=>group.Any(member=>member!.ToString()==id!.ToString()))||unit["slotSaveReceipt"] is not JsonObject receipt||!ObservedReceipt(pair.Key,receipt))continue;Checks(pair.Key,receipt);}
  return new JsonObject{["validated"]=true};
 }
}
