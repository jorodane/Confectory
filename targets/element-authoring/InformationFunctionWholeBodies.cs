using Confectory.Core;
using System.Text.Json.Nodes;

// Compose explicit whole-body, qualified private code and native sources. The original
// single-function validator remains the authority for each source and contract.
internal static class InformationFunctionWholeBodies
{
 const string Capture="nativeBodyContexts";
 static string Hash(string text)=>JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(text));
 // A native source keeps its own ABI when one public value pin is explicitly
 // renamed. Private/whole frames retain their public contracts in this group.
 static bool Rename(JsonNode row)
 {
  if(row["mapping"]?["before"] is not JsonObject before||row["signature"] is not JsonObject next||row["mapping"]?["args"] is not JsonObject args||row["mapping"]?["bodies"] is not JsonObject bodies||bodies.Any(p=>p.Value?["whole"] is not null))return false;
  var a=InformationFunctionBodies.Signature(before);var b=InformationFunctionBodies.Signature(next);
  return a.Return==b.Return&&a.Args.Count==b.Args.Count&&a.Args.Count==args.Count&&a.Args.Where((pin,i)=>pin.Mode is not null||b.Args[i].Mode is not null||pin.Type!=b.Args[i].Type||args[pin.Name]?.ToString()!=b.Args[i].Name).Any()==false&&a.Args.Where((pin,i)=>pin.Name!=b.Args[i].Name).Count()==1&&b.Args.Where((pin,i)=>pin.Name!=a.Args[i].Name).All(pin=>!a.Args.Any(old=>old.Name==pin.Name));
 }
 // One existing information value is selected explicitly; no reference,
 // array, new pin or private frame conversion is inferred by this closure.
 static bool TypedInput(JsonNode row)
 {
  if(row["nativeTypes"] is not JsonObject types||types.Count!=2||types[FunctionNativeEdits.Prefix+row["id"]] is not JsonObject||row["mapping"]?["before"] is not JsonObject before||row["signature"] is not JsonObject next||row["mapping"]?["args"] is not JsonObject args||row["mapping"]?["bodies"] is not JsonObject bodies||bodies.Any(p=>p.Value?["whole"] is not null))return false;
  var a=InformationFunctionBodies.Signature(before);var b=InformationFunctionBodies.Signature(next);if(a.Return!=b.Return||!InformationFunctionNativeTypes.Types(a,b,args))return false;
  var changed=b.Args.Where((pin,i)=>pin.Type!=a.Args[i].Type).ToArray();return changed.Length==1&&changed[0].Type.StartsWith("Confectory.Information.",StringComparison.Ordinal)&&InformationStructs.IsType(changed[0].Type)&&!changed[0].Type.EndsWith("[]",StringComparison.Ordinal)&&types[changed[0].Type] is JsonObject;
 }
 static bool NativeInputSignature(JsonNode row,JsonNode plan)
 {
  if(!TypedInput(row))return false;var a=InformationFunctionBodies.Signature(plan["beforeSignature"]!);var b=InformationFunctionBodies.Signature(plan["signature"]!);
  return a.Matches(InformationFunctionBodies.Signature(row["mapping"]!["before"]!))&&b.Matches(InformationFunctionBodies.Signature(row["signature"]!))&&a.Return==b.Return&&a.Args.Count==b.Args.Count&&a.Args.Where((pin,i)=>pin.Name!=b.Args[i].Name||pin.Mode!=b.Args[i].Mode).Any()==false;
 }
 // One native value input becomes out through the existing explicit role
 // editor. Private frames, other roles and every original output stay intact.
 static bool ValueOut(JsonNode row)
 {
  if(row["nativeTypes"] is not null||row["mapping"]?["before"] is not JsonObject before||row["signature"] is not JsonObject next||row["mapping"]?["args"] is not JsonObject args||row["mapping"]?["bodies"] is not JsonObject bodies||bodies.Any(p=>p.Value?["whole"] is not null))return false;
  var a=InformationFunctionBodies.Signature(before);var b=InformationFunctionBodies.Signature(next);
  return a.Args.All(pin=>pin.Mode is null)&&InformationFunctionNativeRoles.Types(a,b,args)&&InformationFunctionNativeRoles.Direction(a,b)=="value-out"&&b.Args.Count(pin=>pin.IsOut)==1;
 }
 static bool OutValue(JsonNode row)
 {
  if(row["nativeTypes"] is not null||row["mapping"]?["before"] is not JsonObject before||row["signature"] is not JsonObject next||row["mapping"]?["args"] is not JsonObject args||row["mapping"]?["bodies"] is not JsonObject bodies||bodies.Any(p=>p.Value?["whole"] is not null))return false;
  var a=InformationFunctionBodies.Signature(before);var b=InformationFunctionBodies.Signature(next);
  return a.Args.Count(pin=>pin.IsOut)==1&&b.Args.All(pin=>pin.Mode is null)&&InformationFunctionNativeRoles.Types(a,b,args)&&InformationFunctionNativeRoles.Direction(a,b)=="out-value";
 }
 // Reading an original caller ref as a value never converts its contract or
 // storage. Only the explicitly selected native callee loses its ref role.
 static bool RefValue(JsonNode row)
 {
  if(row["nativeTypes"] is not null||row["mapping"]?["before"] is not JsonObject before||row["signature"] is not JsonObject next||row["mapping"]?["args"] is not JsonObject args||row["mapping"]?["bodies"] is not JsonObject bodies||bodies.Any(p=>p.Value?["whole"] is not null))return false;
  var a=InformationFunctionBodies.Signature(before);var b=InformationFunctionBodies.Signature(next);
  return a.Args.Count(pin=>pin.IsRef)==1&&b.Args.All(pin=>pin.Mode is null)&&InformationFunctionNativeRoles.Types(a,b,args)&&InformationFunctionNativeRoles.Direction(a,b)=="ref-value";
 }
 // A selected callee may replace its one original ref with out. Callers keep
 // their original ref storage and explicitly disconnect that old input.
 static bool RefOut(JsonNode row)
 {
  if(row["nativeTypes"] is not null||row["mapping"]?["before"] is not JsonObject before||row["signature"] is not JsonObject next||row["mapping"]?["args"] is not JsonObject args||row["mapping"]?["bodies"] is not JsonObject bodies||bodies.Any(p=>p.Value?["whole"] is not null))return false;
  var a=InformationFunctionBodies.Signature(before);var b=InformationFunctionBodies.Signature(next);
  return a.Args.Count(pin=>pin.IsRef)==1&&a.Args.All(pin=>pin.Mode is null||pin.IsRef)&&b.Args.Count(pin=>pin.IsOut)==1&&b.Args.All(pin=>pin.Mode is null||pin.IsOut)&&InformationFunctionNativeRoles.Types(a,b,args)&&InformationFunctionNativeRoles.Direction(a,b)=="ref-out";
 }
 // A new ref uses an explicitly reviewed original caller binding. The
 // ordinary role validator proves that binding is existing ref storage.
 static bool ValueRef(JsonNode row)
 {
  if(row["nativeTypes"] is not null||row["mapping"]?["before"] is not JsonObject before||row["signature"] is not JsonObject next||row["mapping"]?["args"] is not JsonObject args||row["mapping"]?["bodies"] is not JsonObject bodies||bodies.Any(p=>p.Value?["whole"] is not null))return false;
  var a=InformationFunctionBodies.Signature(before);var b=InformationFunctionBodies.Signature(next);
  return a.Args.All(pin=>pin.Mode is null)&&b.Args.Count(pin=>pin.IsRef)==1&&b.Args.All(pin=>pin.Mode is null||pin.IsRef)&&InformationFunctionNativeRoles.Types(a,b,args)&&InformationFunctionNativeRoles.Direction(a,b)=="value-ref";
 }
 static bool Role(JsonNode row)=>ValueOut(row)||OutValue(row)||RefValue(row)||RefOut(row)||ValueRef(row);
 // Replace one ordinary native scalar return, retaining every original input
 // and out. Original return consumers explicitly select a compatible old out.
 static bool ScalarReturn(JsonNode row)
 {
  if(row["nativeTypes"] is not null||row["mapping"]?["before"] is not JsonObject before||row["signature"] is not JsonObject next||row["mapping"]?["args"] is not JsonObject args||row["mapping"]?["bodies"] is not JsonObject bodies||bodies.Any(p=>p.Value?["whole"] is not null))return false;
  var a=InformationFunctionBodies.Signature(before);var b=InformationFunctionBodies.Signature(next);
  return a.Return!="void"&&b.Return!="void"&&InformationFunctionNativeReturns.Types(a,b,args);
 }
 static bool NativeReturnSignature(JsonNode row,JsonNode plan)
 {
  if(!ScalarReturn(row))return false;var a=InformationFunctionBodies.Signature(plan["beforeSignature"]!);var b=InformationFunctionBodies.Signature(plan["signature"]!);var identity=new JsonObject(a.Args.Select(pin=>KeyValuePair.Create<string,JsonNode?>(pin.Name,JsonValue.Create(pin.Name))));
  return a.Matches(InformationFunctionBodies.Signature(row["mapping"]!["before"]!))&&b.Matches(InformationFunctionBodies.Signature(row["signature"]!))&&InformationFunctionNativeReturns.Types(a,b,identity);
 }
 static bool ExplicitValue(JsonNode? value)=>value is JsonObject literal&&literal.Count==1&&literal["valueJson"] is JsonValue text&&text.TryGetValue<string>(out _);
 static bool NativeRoleSignature(JsonNode row,JsonNode plan)
 {
  if(!Role(row))return false;var a=InformationFunctionBodies.Signature(plan["beforeSignature"]!);var b=InformationFunctionBodies.Signature(plan["signature"]!);var identity=new JsonObject(a.Args.Select(pin=>KeyValuePair.Create<string,JsonNode?>(pin.Name,JsonValue.Create(pin.Name))));
  return a.Matches(InformationFunctionBodies.Signature(row["mapping"]!["before"]!))&&b.Matches(InformationFunctionBodies.Signature(row["signature"]!))&&InformationFunctionNativeRoles.Types(a,b,identity)&&InformationFunctionNativeRoles.Direction(a,b)==InformationFunctionNativeRoles.Direction(InformationFunctionBodies.Signature(row["mapping"]!["before"]!),InformationFunctionBodies.Signature(row["signature"]!));
 }
 internal static JsonNode?[]? Edits(JsonArray changes)
 {
  var rows=changes.Where(row=>!InformationFunctionBodyBatch.Presentation(row)).ToArray();
  if(rows.Length is <2 or >8||!rows.Any(row=>row?["mapping"]?["bodies"] is JsonObject bodies&&bodies.Any(body=>body.Value?["whole"] is JsonObject)))return null;
  if(rows.Any(row=>row?["type"]?.ToString()!="function-edit"||row["mapping"] is not JsonObject mapping||mapping["bodies"] is not JsonObject bodies||bodies.Count is <1 or >8||!JsonNode.DeepEquals(mapping["before"],row["signature"])&&!Rename(row)&&!TypedInput(row)&&!Role(row)&&!ScalarReturn(row)||row["nativeTypes"] is not null&&!TypedInput(row)||bodies.Any(body=>body.Value?["wrapper"] is not null||!JsonNode.DeepEquals(body.Value?["beforeSignature"],body.Value?["signature"])&&!NativeInputSignature(row,body.Value!)&&!NativeRoleSignature(row,body.Value!)&&!NativeReturnSignature(row,body.Value!)&&!InformationFunctionGraphs.Names(body.Value!)))||rows.Count(row=>TypedInput(row!))>1)return null;
  int contracts=rows.Count(row=>Role(row!)||ScalarReturn(row!));if(contracts>1||contracts==1&&rows.Any(row=>!Role(row!)&&!ScalarReturn(row!)&&!JsonNode.DeepEquals(row!["mapping"]!["before"],row["signature"])))return null;
  return rows;
 }
 // Prepare has already authenticated both original source scopes. A callee
 // pin rename, return or explicit role can change its caller graph before its private source
 // is visited; compose these original closures without rebasing their receipts.
 internal static bool ChangedCallee(JsonArray changes,JsonObject units)
 {
  var rows=Edits(changes);if(rows is null)return false;
  return rows.Where(row=>Rename(row!)||ScalarReturn(row!)||Role(row!)).Any(callee=>rows.Any(row=>row!["id"]!.ToString()!=callee!["id"]!.ToString()&&row["mapping"]!["bodies"]!.AsObject().Any(body=>Declaration(units,body.Key[..body.Key.LastIndexOf("/body:",StringComparison.Ordinal)]).Imports.Values.Any(import=>import.Id==callee["id"]!.ToString()))));
 }
 static Element Declaration(JsonObject units,string id)=>new Parser(units[id]?["draft"]?.ToString()??throw new InvalidOperationException("Read the complete original whole/native source"),"<whole-native-source>").ParseElement();
 // Preserve original owned imports as reads, including ordinary helper calls in
 // an original private graph. A selected native callee carries its own explicit
 // body plan; only explicit Rename, ScalarReturn or accepted role plans can change its ABI.
 static bool StableOwnedImports(Element implementation,JsonObject units,JsonNode?[] selected,string ns)
 {
  if(implementation.Imports.Count==0)return true;
  if(implementation.Bodies.Count!=1)return false;
  JsonObject? graph=null;
  if(!InformationFunctionBodyBatch.NativeTargets(implementation)){
   var target=implementation.Bodies.Single();string source=implementation.Id+"/body:"+target.Key;
   if(target.Value.SourceKind!="blueprint"||units[source]?["kind"]?.ToString()!="blueprint"||JsonNode.Parse(units[source]?["draft"]?.ToString()??"null") is not JsonObject originalGraph)return false;
   graph=originalGraph;
  }
  foreach(var pair in implementation.Imports){var import=pair.Value;
   if(!import.Id.StartsWith(ns+"::",StringComparison.Ordinal)||units[import.Id]?["kind"]?.ToString()!="function")return false;
   var dependency=Declaration(units,import.Id);
   if(dependency.Id!=import.Id||dependency.Kind!="function"||dependency.Parent is not null||!import.Signature.Matches(dependency.Signature))return false;
   var callee=selected.SingleOrDefault(row=>row?["id"]?.ToString()==import.Id);
   if(callee is not null&&(graph is null||!JsonNode.DeepEquals(callee["mapping"]?["before"],callee["signature"])&&!Rename(callee)&&!ScalarReturn(callee)&&!Role(callee)||callee["nativeTypes"] is not null||callee["mapping"]?["bodies"] is not JsonObject calleeBodies||calleeBodies.Count!=1||calleeBodies.Any(body=>body.Value?["whole"] is not null)))return false;
   if(graph is not null&&(pair.Key!=FeatureBlueprint.ImportAlias(import.Id)||!BlueprintTree.Nodes(graph).Any(entry=>entry.Node["kind"]?.ToString()=="call"&&entry.Node["control"]?.ToString()=="next"&&entry.Node["feature"]?.ToString()==import.Id&&entry.Node["implementationContext"] is null&&entry.Node["forwardCallerStorage"]?.GetValue<bool>()!=true&&entry.Node["signature"] is JsonObject signature&&import.Signature.Matches(InformationFunctionBodies.Signature(signature)))))return false;
  }
  return true;
 }
 static Element Selected(JsonObject units,JsonNode row){var value=Declaration(units,row["id"]!.ToString());DeclarationAuthoring.Apply(value,new JsonObject{["action"]="signature",["value"]=row["signature"]!.DeepClone()});return value;}
 internal static HashSet<string>? Prepare(JsonObject request,JsonArray changes,JsonObject units,Func<Element,string> format)
 {
  var rows=Edits(changes);if(rows is null)return null;
  string owner=request["id"]!.ToString(),ns=PackPaths.Namespace(owner);var functions=new HashSet<string>(StringComparer.Ordinal);var sources=new HashSet<string>(StringComparer.Ordinal);bool native=false;
  if(units[owner]?["kind"]?.ToString()!="schema"||units.Count>240)throw new InvalidOperationException("Keep the complete whole/native owner observation within its existing read budget");
  var information=Declaration(units,owner);
  foreach(var row in rows){
   string id=row!["id"]!.ToString();var original=Declaration(units,id);var mapping=row["mapping"]!.AsObject();var signature=original.Signature;var next=InformationFunctionBodies.Signature(row["signature"]!);bool typed=TypedInput(row),valueOut=ValueOut(row),outValue=OutValue(row),refOut=RefOut(row),role=Role(row),returned=ScalarReturn(row);
   if(row.AsObject().Any(p=>p.Key is not ("type" or "id" or "hash" or "name" or "description" or "signature" or "mapping" or "icon" or "returnName" or "argumentNames" or "nativeTypes"))||!functions.Add(id)||!id.StartsWith(owner+"_Function_",StringComparison.Ordinal)||!information.Contains.Any(child=>child.Id==id&&child.Kind=="function")||original.Id!=id||original.Kind!="function"||original.Parent is not null||signature is null||!JsonNode.DeepEquals(mapping["before"],FeatureBlueprint.SignatureDocument(signature))||mapping.Count!=3+(mapping["callers"] is null?0:1)||mapping.Any(p=>p.Key is not ("before" or "args" or "bodies" or "callers"))||mapping["args"] is not JsonObject args||args.Count!=signature.Args.Count||signature.Args.Where((a,i)=>a.Type==next.Args[i].Type?args[a.Name]?.ToString()!=next.Args[i].Name:args[a.Name] is not null).Any())throw new InvalidOperationException("Retain every original pin or explicitly select one information-value input");
   if(typed){string type=next.Args.Single(a=>!signature.Args.Any(b=>b.Name==a.Name&&b.Type==a.Type)).Type;var proof=row["nativeTypes"]![type]!["sources"]!.AsObject();if(!proof.Any(p=>p.Key.StartsWith(PackPaths.Namespace(owner)+"::",StringComparison.Ordinal)&&units[p.Key]?["kind"]?.ToString()=="schema"&&InformationStructs.Type(p.Key)==type)||mapping["callers"] is not JsonObject callers||callers.Count==0)throw new InvalidOperationException("Select an existing owned information value and every original caller explicitly");}
   if((role||returned)&&(mapping["callers"] is not JsonObject roleCallers||roleCallers.Count==0))throw new InvalidOperationException("Explicitly review every original caller input and output correspondence");
   foreach(var caller in mapping["callers"] as JsonObject??new()){
    var callerPlan=caller.Value?.AsObject()??throw new ArgumentException("Exact original caller plan required");var outputs=FeatureBlueprint.FeatureOutputs(signature).ToArray();
    var removed=signature.Args.Where(a=>args[a.Name] is null||(valueOut||refOut)&&next.Args.Any(b=>b.Name==a.Name&&b.IsOut)).Select(a=>a.Name).ToHashSet(StringComparer.Ordinal);var inputs=(role?next.Args:signature.Args).Where(a=>!a.IsOut).ToArray();
    if(callerPlan.Count!=5+(callerPlan["outputs"] is null?0:1)||callerPlan.Any(p=>p.Key is not ("graph" or "node" or "hash" or "inputs" or "disconnect" or "outputs"))||callerPlan["inputs"] is not JsonObject inputMap||inputMap.Count!=inputs.Length||inputs.Any(arg=>outValue&&signature.Args.Single(a=>a.Name==arg.Name).IsOut?!ExplicitValue(inputMap[arg.Name]):args[arg.Name] is null?inputMap[arg.Name] is not JsonObject choice||choice.Count!=1||choice["binding"] is not JsonObject:inputMap[args[arg.Name]!.ToString()]?.ToString()!=arg.Name)||callerPlan["disconnect"] is not JsonObject disconnect||disconnect.Count!=removed.Count||disconnect.Any(p=>!removed.Contains(p.Key)||p.Value is not JsonValue value||!value.TryGetValue<string>(out _))||(role||returned)&&callerPlan["outputs"] is not JsonObject||callerPlan["outputs"] is JsonObject outputMap&&(outputMap.Count!=outputs.Length||outputs.Any(output=>returned&&output.Name=="return"?!signature.Args.Any(pin=>pin.IsOut&&pin.Type==signature.Return&&outputMap[output.Name]?.ToString()==pin.Name):outputMap[output.Name]?.ToString()!=(outValue&&output.Name!="return"?"return":output.Name))))throw new InvalidOperationException("Retain unchanged inputs/out identities; explicitly review new inputs, removed inputs and compatible original outputs for changed returns or outs");
   }
   string? selectedImplementation=null;
   foreach(var body in mapping["bodies"]!.AsObject()){string source=body.Key;var plan=body.Value!.AsObject();
   int marker=source.LastIndexOf("/body:",StringComparison.Ordinal);if(marker<0||!sources.Add(source))throw new ArgumentException("Unique explicit owned sources required");
   string implementationId=source[..marker];var implementation=Declaration(units,implementationId);
   if(implementation.Id!=implementationId||implementation.Function!=id||implementation.Parent is not null||!StableOwnedImports(implementation,units,rows,ns)||implementation.Bodies.Count!=1||!JsonNode.DeepEquals(plan["contract"],row["signature"]))throw new InvalidOperationException("Retain the exact source, stable owned imports and original ordinary graph calls; changed callee contracts, foreign or retained-context imports require their separate explicit plan");
   if(selectedImplementation is not null&&selectedImplementation!=implementationId)throw new InvalidOperationException("Keep every explicit source in the same original owned implementation");selectedImplementation=implementationId;
   var target=implementation.Bodies.Single();string graphId=implementationId+"/body:"+target.Key;
   if(plan["whole"] is JsonObject whole){
    string key=whole["node"]!.ToString();
    if(target.Value.SourceKind!="blueprint"||units[graphId]?["kind"]?.ToString()!="blueprint"||units[source]?["kind"]?.ToString()!="blueprint-node"||whole["graph"]?.ToString()!=graphId||source!=BlueprintTree.SourceId(graphId,key))throw new InvalidOperationException("Keep the original exact whole-body graph and source receipt");
    var graph=JsonNode.Parse(units[graphId]!["draft"]!.ToString())!.AsObject();
    var selectedNode=BlueprintTree.Nodes(graph).Single(entry=>entry.Key==key).Node;
    if(key.Contains('/')||selectedNode["kind"]?.ToString()=="code"&&selectedNode["implementationContext"] is null&&selectedNode["forwardCallerStorage"]?.GetValue<bool>()!=true&&(InformationFunctionGraphs.RootCodeGraph(graph)||InformationFunctionGraphs.RetainedCodePlans(graphId,units[graphId]!["draft"]!.ToString(),graph,implementation,original,units,mapping["bodies"]!.AsObject()))){
     // Independent code owns its native ABI; the parent owns its frame.
     // The original single-source validator authenticates the receipt, code,
     // helper boundary and assembled context, without rewriting either ABI.
     var node=selectedNode;
     if(node["kind"]?.ToString()!="code"||node["control"]?.ToString() is not ("next" or "branch" or "switch")||node["implementationContext"] is not null||!JsonNode.DeepEquals(plan["beforeSignature"],node["signature"])||InformationFunctionGraphs.RootCodeGraph(graph)&&!JsonNode.DeepEquals(FeatureBlueprint.SignatureDocument(implementation.Signature!),row["signature"]))throw new InvalidOperationException("Retain the exact private code ABI and its parent frame/native declaration");
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
   }
   var implementations=units.Where(unit=>unit.Value?["kind"]?.ToString()=="implementation"&&Declaration(units,unit.Key).Function==id).Select(unit=>unit.Key).ToArray();
   if(implementations.Length!=1||implementations[0]!=selectedImplementation)throw new InvalidOperationException("Review additional targets or implementations separately; no source is inferred");
   InformationFunctionContracts.Prepare(request,original,Selected(units,row),mapping,format,row["nativeTypes"] as JsonObject);
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
 static void Validate(JsonObject request,string owner,JsonObject receipt,Func<Element,string> format,Func<Manifest,string> formatManifest)
 {
  string ns=request["namespace"]!.ToString();var units=request["units"]!.AsObject();
  if(receipt["version"]?.GetValue<int>()!=3||receipt["owner"]?.ToString()!=owner||receipt[Capture] is not JsonArray plans||Edits(plans) is null||receipt["sources"] is not JsonObject proof||proof.Count>64||units[owner]?["atomicEditGroup"] is not JsonArray group||group.Count!=proof.Count||!proof.Select(p=>p.Key).ToHashSet(StringComparer.Ordinal).SetEquals(group.Select(id=>id!.ToString()))||receipt["readGuards"] is not JsonObject guards||new[]{"nativeBodyDependencies","nativeBodyDependencyReads","nativeBodyOwnerEdits","nativeBodyOwnerReads","nativeBodyValues","nativeBodyValueReads","nativeBodyCopies"}.Any(receipt.ContainsKey))throw new InvalidOperationException("Retain the complete explicit whole/native receipt and atomic source group");
  var expected=Checks(units,ns,false);var types=new JsonObject();foreach(var row in plans)foreach(var type in row?["nativeTypes"] as JsonObject??new())types[type.Key]=type.Value!.DeepClone();
  if(types.Count==0){if(receipt.ContainsKey("nativeTypeProofs")||receipt.ContainsKey("nativeTypeReads"))throw new InvalidOperationException("No uncaptured type scope may enter a whole/native receipt");}
  else{
   if(!JsonNode.DeepEquals(types,receipt["nativeTypeProofs"])||receipt["nativeTypeReads"] is not JsonArray)throw new InvalidOperationException("Retain exactly the original context's selected type proofs and reads");
   var validation=request.DeepClone().AsObject();validation["action"]="validate";validation["selected"]=new JsonArray(owner);var reads=FunctionNativeTypes.Guards(validation,formatManifest)["reads"]!.AsArray();string root=Path.GetDirectoryName(Path.GetFullPath(request["project"]!.ToString()))!;
   foreach(var row in reads){string path=Path.GetFullPath(row!["path"]!.ToString());if(path.StartsWith(root+Path.DirectorySeparatorChar,OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal)){string relative=Path.GetRelativePath(root,path).Replace('\\','/');if(!expected.Any(p=>p!["path"]?.ToString()==relative))expected.Add(new JsonObject{["path"]=relative,["hash"]=null});}}
  }
  if(guards.Count!=expected.Count||expected.Any(row=>guards[row!["path"]!.ToString()] is not JsonObject read||read.Count!=2||read["path"]?.ToString()!=row["path"]!.ToString()||!System.Text.RegularExpressions.Regex.IsMatch(read["hash"]?.ToString()??"","^[a-f0-9]{64}$"))||guards.Count+proof.Count>240)throw new InvalidOperationException("Retain all original whole/native and selected type source checks without adding or dropping a path");
  var originals=Originals(units);var originalRequest=OriginalRequest(request,owner,originals);var functions=Prepare(originalRequest,plans,originals,format)??throw new InvalidOperationException("Original explicit whole/native plans required");
  var updates=new Dictionary<string,string>(StringComparer.Ordinal);var selectedFunctions=new Dictionary<string,string>(StringComparer.Ordinal);var mandatory=new HashSet<string>(functions,StringComparer.Ordinal){owner,ns+"::ProjectManifest"};
  foreach(var row in plans){string id=row!["id"]!.ToString();if(row["hash"]?.ToString()!=Hash(originals[id]!["draft"]!.ToString()))throw new InvalidOperationException("Retain the original function plan basis");var candidate=InformationFunctionContracts.Prepare(originalRequest,Declaration(originals,id),Selected(originals,row),row["mapping"]!.AsObject(),format,row["nativeTypes"] as JsonObject);selectedFunctions[id]=candidate["function"]!.ToString();
   foreach(var update in candidate["updates"]!.AsArray()){string key=update!["id"]!.ToString(),text=update["text"]!.ToString(),original=originals[key]!["draft"]!.ToString();if(updates.TryGetValue(key,out string? prior)&&prior!=text&&prior!=original&&text!=original)throw new InvalidOperationException("Original whole/native closures disagree on a changed source");if(prior is null||text!=original)updates[key]=text;if(text!=original)mandatory.Add(key);}
   mandatory.UnionWith(row["mapping"]!["bodies"]!.AsObject().Select(body=>body.Key));
  }
  if(!mandatory.IsSubsetOf(proof.Select(p=>p.Key))||proof.Any(p=>!mandatory.Contains(p.Key)&&!updates.ContainsKey(p.Key)))throw new InvalidOperationException("Retain exactly the selected sources and their original closure members");
  foreach(var source in proof){var unit=units[source.Key]??throw new InvalidOperationException("Whole/native member missing");if(!source.Key.StartsWith(ns+"::",StringComparison.Ordinal)||source.Value?["path"]?.ToString()!=unit["path"]?.ToString()||source.Value?["kind"]?.ToString()!=unit["kind"]?.ToString()||source.Value?["hash"]?.ToString()!=Hash(unit["draft"]!.ToString())||unit["atomicEditGroup"] is not JsonArray members||!JsonNode.DeepEquals(members,group))throw new InvalidOperationException("Whole/native source identity, draft or group changed");}
  foreach(var unit in units.Where(p=>p.Key.StartsWith(ns+"::",StringComparison.Ordinal))){string id=unit.Key;string original=originals[id]?["draft"]?.ToString()??throw new InvalidOperationException("Hydrate every known original whole/native source before review");string current=unit.Value?["draft"]?.ToString()??throw new InvalidOperationException("Hydrate every known current whole/native source before review");
   if(id==owner||functions.Contains(id)){if(Shape(current,format)!=Shape(selectedFunctions.GetValueOrDefault(id)??original,format))throw new InvalidOperationException("Retain the exact captured whole/native public contracts, ownership and structure");}
   else if(current!=(updates.GetValueOrDefault(id)??original))throw new InvalidOperationException("Retain the exact replayed whole/native source and unchanged surrounding graph");
  }
 }
 static bool CurrentWhole(JsonObject units,JsonObject original,JsonNode? receipt)
 {
  string id=original["graph"]!.ToString(),key=original["node"]!.ToString();
  if(units[id]?["kind"]?.ToString()!="blueprint"||units[id]?["draft"] is not JsonValue source||!source.TryGetValue<string>(out string? text)||JsonNode.Parse(text) is not JsonObject graph)return false;
  var node=BlueprintTree.Nodes(graph).SingleOrDefault(entry=>entry.Key==key)?.Node;
  return node is not null&&JsonNode.DeepEquals(receipt,InformationFunctionWholeBody.Receipt(id,text,graph,node,key));
 }
 static bool Local(JsonNode? row,JsonObject units,JsonArray plans)
 {
  if(InformationFunctionBodyBatch.Presentation(row))return true;
  if(row?["type"]?.ToString()!="function-edit"||row["id"] is not JsonValue id)return false;
  var saved=plans.SingleOrDefault(p=>p?["id"]?.ToString()==id.ToString());if(saved is null||!JsonNode.DeepEquals(row["signature"],saved["signature"]))return false;
  if(row["mapping"] is not JsonObject mapping)return true;
  var identity=new JsonObject(InformationFunctionBodies.Signature(saved["signature"]!).Args.Select(a=>KeyValuePair.Create<string,JsonNode?>(a.Name,JsonValue.Create(a.Name))));
  if(!JsonNode.DeepEquals(mapping["before"],saved["signature"])||!JsonNode.DeepEquals(mapping["args"],identity)||mapping.Any(p=>p.Key is not ("before" or "args" or "bodies" or "callers"))||mapping.ContainsKey("callers")&&!JsonNode.DeepEquals(mapping["callers"],saved["mapping"]!["callers"]))return false;
  if(mapping["bodies"] is not JsonObject bodies||bodies.Count==0)return true;
  var prior=saved["mapping"]!["bodies"]!.AsObject();if(bodies.Count!=prior.Count)return false;
  bool currentWhole=ChangedCallee(plans,Originals(units))||prior.Any(body=>InformationFunctionGraphs.Names(body.Value!));
  foreach(var body in bodies){if(prior[body.Key] is not JsonObject old||body.Value is not JsonObject next||next["hash"]?.ToString()!=Hash(units[body.Key]!["draft"]!.ToString())||old.ContainsKey("helpers")!=next.ContainsKey("helpers"))return false;var a=old.DeepClone().AsObject();var b=next.DeepClone().AsObject();
   // Validate the editor's current graph receipt against the exact pending
   // candidate already replayed by Validate. Keep the captured ORIGINAL graph
   // receipt for cold/final replay; only explicit source/helpers are replaced.
   if(currentWhole&&a["whole"] is JsonObject originalWhole){if(!CurrentWhole(units,originalWhole,b["whole"]))return false;b["whole"]=originalWhole.DeepClone();}
   if(TypedInput(saved)||Role(saved)||ScalarReturn(saved)||InformationFunctionGraphs.Names(old))a["beforeSignature"]=a["signature"]!.DeepClone();foreach(string key in new[]{"hash","text","helpers"}){a.Remove(key);b.Remove(key);}if(!JsonNode.DeepEquals(a,b))return false;old["text"]=next["text"]!.DeepClone();if(next.ContainsKey("helpers"))old["helpers"]=next["helpers"]!.DeepClone();}return true;
 }
 internal static JsonObject? Guards(JsonObject request,Func<Element,string> formatElement,Func<Manifest,string> format)
 {
  string ns=request["namespace"]!.ToString(),action=request["action"]!.ToString();var units=request["units"]!.AsObject();
  if(action=="prepare"){
   string? owner=request["declaration"]?["id"]?.ToString();if(owner is null)return null;var declaration=request["declaration"]!;var prior=units[owner]?["slotSaveReceipt"] as JsonObject;
   if(prior?.ContainsKey(Capture)==true){
    Validate(request,owner,prior,formatElement,format);var plans=prior[Capture]!.DeepClone().AsArray();if(declaration["raw"] is not null||declaration["changes"] is not JsonArray changes||changes.Count is <1 or >10||!changes.All(row=>Local(row,units,plans)))throw new InvalidOperationException("Retain the explicit whole/native plans; review other contract or structure edits separately");
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
  var delegated=request.DeepClone().AsObject();foreach(string owner in owners){if(action=="validate")Validate(request,owner,units[owner]!["slotSaveReceipt"]!.AsObject(),formatElement,format);delegated["units"]![owner]!.AsObject().Remove("slotSaveReceipt");}
  var other=InformationFunctionBodyGuards.Execute(delegated,formatElement,format);if(action=="validate")return other;
  if(units.Count>240)throw new ArgumentException("Whole/native read budget");var ids=other["ids"]!.AsArray().Select(id=>id!.ToString()).ToHashSet(StringComparer.Ordinal);
  // Known registered owned units only. Cold restore rehydrates the same paths;
  // it neither discovers a new locator nor adopts a current physical baseline.
  if(action=="headers")ids.UnionWith(units.Where(p=>p.Key.StartsWith(ns+"::",StringComparison.Ordinal)).Select(p=>p.Key));
  return new JsonObject{["ids"]=new JsonArray(ids.Order(StringComparer.Ordinal).Select(id=>(JsonNode)JsonValue.Create(id)!).ToArray())};
 }
}
