using Confectory.Core;
using System.Text;
using System.Text.Json.Nodes;

// Pure all-target preview/apply. The workspace must bind this candidate to its
// original owned sources, checkpoint CAS and an explicit all-target review.
internal static class BlueprintCallAbiGroup
{
 public static JsonObject ValidateGroup(JsonObject request)
 {
  var group=request["group"]!.AsArray();var units=request["units"]!.AsObject();string ns=request["namespace"]!.GetValue<string>();var ids=group.Select(n=>n!.GetValue<string>()).ToArray();
  if(ids.Length is <5 or >64||ids.Distinct(StringComparer.Ordinal).Count()!=ids.Length||ids.Any(id=>PackPaths.Namespace(id)!=ns||units[id] is null||!JsonNode.DeepEquals(units[id]!["rootContractGroup"],group)))throw new ArgumentException("Complete owned multi-target group required");
  if(units[ids[0]]!["kind"]?.ToString()!="function"||units[ids[1]]!["kind"]?.ToString()!="implementation")throw new ArgumentException("Public function and direct implementation required");
  var function=new Parser(units[ids[0]]!["draft"]!.GetValue<string>(),"<abi-group-function>").ParseElement();var caller=new Parser(units[ids[1]]!["draft"]!.GetValue<string>(),"<abi-group-implementation>").ParseElement();
  if(function.Kind!="function"||function.Id!=ids[0]||caller.Kind!="implementation"||caller.Id!=ids[1]||caller.Function!=function.Id||caller.Parent is not null||caller.Bodies.Count is <2 or >8||!function.Signature!.Matches(caller.Signature)||caller.Bodies.Any(p=>p.Value.SourceKind!="blueprint"))throw new ArgumentException("Exact all-Blueprint direct target declaration group required");
  var expected=new HashSet<string>(new[]{function.Id,caller.Id},StringComparer.Ordinal);var contracts=new JsonObject();
  var snapshot=units[caller.Id]!["rootAbiContracts"] as JsonObject;var registered=BlueprintAbiContracts.Validate(snapshot,caller,units[caller.Id]!["path"]!.ToString());
  if(units.Any(p=>p.Key!=caller.Id&&p.Value?["rootAbiContracts"] is not null))throw new ArgumentException("Registered evidence belongs only to the owned caller");
  if(snapshot is not null){string manifest=snapshot["manifest"]!.ToString();if(!ids.Contains(manifest,StringComparer.Ordinal)||units[manifest]?["kind"]?.ToString()!="project"||units[manifest]?["path"]?.ToString()!=snapshot["path"]?.ToString()||units[manifest]?["draft"]?.ToString()!=snapshot["text"]?.ToString())throw new ArgumentException("Owned manifest is a read-only coordinated member");expected.Add(manifest);if(request["verifyRegistered"]?.GetValue<bool>()==true)BlueprintAbiContracts.Verify(request["project"]!.GetValue<string>(),snapshot,units[caller.Id]!["draft"]!.GetValue<string>());}

  foreach(string feature in caller.Imports.Values.Select(i=>i.Id).Distinct(StringComparer.Ordinal)){
   if(PackPaths.Namespace(feature)!=ns){contracts[feature]=registered[feature]!.DeepClone();var external=new Parser(contracts[feature]!.GetValue<string>(),"<abi-registered-contract>").ParseElement();if(caller.Imports.Values.Any(i=>i.Id==feature&&!i.Signature.Matches(external.Signature)))throw new ArgumentException("Registered typed import must match its reviewed snapshot");continue;}
   if(!ids.Contains(feature,StringComparer.Ordinal)||units[feature]?["kind"]?.ToString()!="function")throw new ArgumentException("Every owned imported contract belongs in the coordinated group");var fn=new Parser(units[feature]!["draft"]!.GetValue<string>(),"<abi-group-contract>").ParseElement();if(fn.Kind!="function"||fn.Id!=feature)throw new ArgumentException("Exact contract identity required");expected.Add(feature);contracts[feature]=units[feature]!["draft"]!.DeepClone();
  }
  string root=Path.Combine(Path.GetTempPath(),"confectory-pure-abi-group");var paths=new HashSet<string>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);
  foreach(string declaration in expected)if(!paths.Add(PackPaths.Owned(root,units[declaration]!["path"]!.ToString())))throw new ArgumentException("Distinct group source locators required");
  foreach(var body in caller.Bodies){
   string id=caller.Id+"/body:"+body.Key;var unit=units[id];if(!expected.Add(id)||unit?["kind"]?.ToString()!="blueprint"||unit["path"]?.ToString()!=body.Value.Path||!paths.Add(PackPaths.Owned(root,body.Value.Path)))throw new ArgumentException("Every declared target graph belongs in the group");var graph=JsonNode.Parse(unit["draft"]!.GetValue<string>())!.AsObject();BlueprintDocuments.Validate(id,"blueprint",graph.ToJsonString());if(graph["copySource"] is not null||graph["nodes"]!.AsArray().Any(n=>n!["implementationContext"] is not null||n["kind"]?.ToString() is not ("call" or "code" or "export")))throw new ArgumentException("Ordinary independent target graphs required");var records=new JsonObject();
   foreach(var node in graph["nodes"]!.AsArray().Where(n=>n!["kind"]?.ToString()=="code")){string code=node!["id"]!.ToString(),recordId=id+"/node:"+code;var record=units[recordId];string path=PackPaths.Owned(Path.GetDirectoryName(PackPaths.Owned(root,body.Value.Path))!,node["implementation"]!.ToString());if(!expected.Add(recordId)||record?["kind"]?.ToString()!="blueprint-node"||!string.Equals(path,PackPaths.Owned(root,record["path"]!.ToString()),OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal)||!paths.Add(path))throw new ArgumentException("Every exact target code record belongs in the group");BlueprintDocuments.Validate(recordId,"blueprint-node",record["draft"]!.GetValue<string>());records[code]=JsonNode.Parse(record["draft"]!.GetValue<string>());}
   var ready=FeatureBlueprint.Execute(new JsonObject{["operation"]="featureBlueprintDescribe",["featureSource"]=units[function.Id]!["draft"]!.DeepClone(),["featureContracts"]=contracts.DeepClone(),["implementationContext"]=FeatureBlueprint.ImplementationContext(caller),["graph"]=graph,["implementations"]=records});if(ready["state"]?.ToString()!="source-ready"||ready["nodes"]!.AsArray().Any(n=>n!["status"]?.ToString() is "missing" or "stale"))throw new ArgumentException("Every grouped target must remain source-ready");
  }
  if(!expected.SetEquals(ids))throw new ArgumentException("No missing or unrelated multi-target group member permitted");
  return new JsonObject{["valid"]=true,["ids"]=group.DeepClone(),["sourceWritten"]=false,["executed"]=false};
 }
 public static JsonObject Prepare(JsonObject request,Func<Element,string> format)
 {
  string text=request["text"]!.GetValue<string>(),id=request["id"]!.GetValue<string>(),feature=request["feature"]!.GetValue<string>();
  if(Encoding.UTF8.GetByteCount(request.ToJsonString())>2097152)throw new ArgumentException("ABI target closure budget");
  var caller=new Parser(text,"<multi-abi-caller>").ParseElement();var function=new Parser(request["functionText"]!.GetValue<string>(),"<multi-abi-function>").ParseElement();
  var bodies=request["bodies"]!.AsObject();var contracts=request["featureContracts"]!.AsObject();
  if(caller.Id!=id||caller.Kind!="implementation"||caller.Parent is not null||caller.Bodies.Count is <2 or >8||bodies.Count!=caller.Bodies.Count||function.Kind!="function"||function.Id!=caller.Function||PackPaths.Namespace(function.Id)!=PackPaths.Namespace(id)||!function.Signature!.Matches(caller.Signature)||caller.Bodies.Any(p=>p.Value.SourceKind!="blueprint"||!bodies.ContainsKey(p.Key)))throw new ArgumentException("Complete direct owned Blueprint target closure required; opaque/inherited targets are retained");
  if(request["registeredContracts"] is JsonObject registeredSnapshot){var foreign=BlueprintAbiContracts.Validate(registeredSnapshot,caller,request["implementationPath"]!.GetValue<string>());foreach(var contract in foreign)if(!JsonNode.DeepEquals(contracts[contract.Key],contract.Value))throw new ArgumentException("Candidate registered snapshot differs");}
  else if(caller.Imports.Values.Any(i=>PackPaths.Namespace(i.Id)!=PackPaths.Namespace(id)))throw new ArgumentException("Registered all-target receipt required");
  var callee=new Parser(contracts[feature]!.GetValue<string>(),"<multi-abi-callee>").ParseElement();
  if(callee.Kind!="function"||callee.Id!=feature)throw new ArgumentException("Exact callee declaration required");
  var signature=FeatureBlueprint.SignatureDocument(callee.Signature!);var previews=new JsonObject();var originalProofs=new JsonArray();
  var paths=new HashSet<string>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);string root=Path.Combine(Path.GetTempPath(),"confectory-pure-abi-targets");
  JsonObject Definitions(JsonObject graph,Element context,bool inspect)=>FeatureBlueprint.Execute(new JsonObject{["operation"]="featureBlueprintNodes",["featureSource"]=request["functionText"]!.DeepClone(),["featureContracts"]=contracts.DeepClone(),["implementationContext"]=FeatureBlueprint.ImplementationContext(context),["graph"]=graph.DeepClone(),["inspectStalePostCalls"]=inspect});
  foreach(var body in caller.Bodies.OrderBy(p=>p.Key,StringComparer.Ordinal)){
   var row=bodies[body.Key]!.AsObject();if(row.Count!=3||row.Any(p=>p.Key is not ("path" or "graph" or "records"))||row["path"]?.ToString()!=body.Value.Path)throw new ArgumentException("Exact body target/locator required");
   string graphPath=PackPaths.Owned(root,body.Value.Path);if(!paths.Add(graphPath))throw new ArgumentException("Distinct target graph paths required");
   var graph=row["graph"]!.AsObject();BlueprintDocuments.Validate(id+"/body:"+body.Key,"blueprint",graph.ToJsonString());
   if(graph["copySource"] is not null||graph["nodes"]!.AsArray().Any(n=>n!["implementationContext"] is not null||n["kind"]?.ToString() is not ("call" or "code" or "export")))throw new ArgumentException("Independent ordinary graphs required; copied/private/opaque context needs a separate candidate");
   var selected=graph["nodes"]!.AsArray().Where(n=>n!["kind"]?.ToString()=="call"&&n["feature"]?.ToString()==feature).ToArray();
   if(selected.Length!=1)throw new ArgumentException("One explicitly bound callee use per target required");
   var definitions=Definitions(graph,caller,true);if(definitions["state"]?.ToString()!="node-definitions")throw new ArgumentException("Every original target must be inspectable");
   string node=selected[0]!["id"]!.ToString();var current=definitions["nodes"]!.AsArray().Single(n=>n!["id"]!.ToString()==node)!;
   if(current["postCallSignatureMatches"]?.GetValue<bool>()!=false||current["postCallStale"]?.GetValue<bool>()!=true||selected[0]!["control"]?.ToString()!="switch"||selected[0]!["postCall"]?["mode"]?.ToString()!="execution-enum")throw new ArgumentException("Each target needs its explicit stale value/ref wrapped call");
   var records=row["records"]!.AsObject();var codeNodes=graph["nodes"]!.AsArray().Where(n=>n!["kind"]?.ToString()=="code").ToArray();
   if(records.Count!=codeNodes.Length)throw new ArgumentException("Every target code record must be observed exactly once");
   foreach(var source in codeNodes){string codeId=source!["id"]!.ToString();var record=records[codeId]?.AsObject()??throw new ArgumentException("Complete target code records required");if(record.Count!=2||record.Any(p=>p.Key is not ("path" or "record")))throw new ArgumentException("Exact record locator and document required");string path=PackPaths.Owned(Path.GetDirectoryName(graphPath)!,source["implementation"]!.ToString());if(!string.Equals(path,PackPaths.Owned(root,record["path"]!.ToString()),OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal)||!paths.Add(path))throw new ArgumentException("Distinct owned record paths required");BlueprintDocuments.Validate(id+"/body:"+body.Key+"/node:"+codeId,"blueprint-node",record["record"]!.ToJsonString());if(record["record"]!["definitionHash"]?.ToString()!=definitions["nodes"]!.AsArray().Single(n=>n!["id"]!.ToString()==codeId)!["definitionHash"]?.ToString())throw new InvalidOperationException("An original target record is stale; all inputs retained");}
   // Probe the existing single-call rules on an isolated declaration projection.
   // Its body list is NEVER returned as the final implementation declaration.
   var one=new Parser(format(caller),"<abi-target-projection>").ParseElement();one.Bodies=new(){[body.Key]=body.Value};
   var remapPreview=BlueprintCallAbi.Prepare(new JsonObject{["id"]=id,["text"]=format(one),["graph"]=graph.DeepClone(),["node"]=node,["signature"]=signature.DeepClone(),["contractHash"]=current["postCallEditor"]!["contractHash"]!.DeepClone(),["previewRemap"]=true},format);
   previews[body.Key]=new JsonObject{["node"]=node,["source"]=selected[0]!["postCall"]!["source"]!.DeepClone(),["helpers"]=selected[0]!["postCall"]?["helpers"]?.DeepClone()??JsonValue.Create(""),["executionEnum"]=selected[0]!["executionEnum"]!.DeepClone(),["contractHash"]=current["postCallEditor"]!["contractHash"]!.DeepClone(),["refreshFrom"]=selected[0]!["postCall"]!["contractHash"]!.DeepClone(),["returnMapping"]=current["postCallEditor"]?["returnMapping"]?.DeepClone(),["remap"]=remapPreview["remap"]?.DeepClone(),["before"]=selected[0]!["signature"]!.DeepClone()};
   originalProofs.Add(new JsonObject{["target"]=body.Key,["path"]=body.Value.Path,["graphHash"]=JsonData.Digest(graph.ToJsonString()),["recordsHash"]=JsonData.Digest(records.ToJsonString())});
  }
  var binding=new JsonObject{["schema"]=1,["implementation"]=id,["implementationHash"]=JsonData.Digest(text),["functionHash"]=JsonData.Digest(request["functionText"]!.GetValue<string>()),["feature"]=feature,["sourceHash"]=JsonData.Digest(contracts[feature]!.GetValue<string>()),["signature"]=signature.DeepClone(),["contractsHash"]=JsonData.Digest(contracts.ToJsonString()),["targets"]=originalProofs};
  if(request["registeredContracts"] is not null)binding["registeredHash"]=JsonData.Digest(request["registeredContracts"]!.ToJsonString());
  if(request["plans"] is null)return new JsonObject{["binding"]=binding,["plans"]=previews,["sourceWritten"]=false,["compiled"]=false};
  if(!JsonNode.DeepEquals(request["binding"],binding))throw new InvalidOperationException("Reviewed all-target source closure changed; retain every input");
  var plans=request["plans"]!.AsObject();if(plans.Count!=previews.Count||plans.Any(p=>!previews.ContainsKey(p.Key)))throw new ArgumentException("Explicit plans for every affected target required");
  var graphs=new JsonObject();
  foreach(var body in caller.Bodies.OrderBy(p=>p.Key,StringComparer.Ordinal)){
   var plan=plans[body.Key]!.AsObject();var expected=previews[body.Key]!;
   if(plan.Count is <7 or >9||plan.Any(p=>p.Key is not ("node" or "source" or "helpers" or "executionEnum" or "contractHash" or "refreshFrom" or "returnMapping" or "remap" or "before"))||new[]{"node","contractHash","refreshFrom","returnMapping"}.Any(k=>!JsonNode.DeepEquals(plan[k],expected[k]))||plan["source"]!.GetValue<string>().Length>65536||plan["helpers"]!.GetValue<string>().Length>65536)throw new InvalidOperationException("Exact reviewed target wrapper plan required");
   var one=new Parser(text,"<abi-target-projection>").ParseElement();one.Bodies=new(){[body.Key]=body.Value};
   var prepared=BlueprintCallAbi.Prepare(new JsonObject{["id"]=id,["text"]=format(one),["graph"]=bodies[body.Key]!["graph"]!.DeepClone(),["node"]=plan["node"]!.DeepClone(),["signature"]=signature.DeepClone(),["contractHash"]=plan["contractHash"]!.DeepClone(),["source"]=plan["source"]!.DeepClone(),["helpers"]=plan["helpers"]!.DeepClone(),["executionEnum"]=plan["executionEnum"]!.DeepClone(),["remap"]=plan["remap"]?.DeepClone()},format);
   var candidate=new Parser(prepared["implementation"]!.GetValue<string>(),"<abi-target-result>").ParseElement();string alias=prepared["alias"]!.ToString();caller.Imports[alias]=candidate.Imports[alias];graphs[body.Key]=prepared["graph"]!.DeepClone();
  }
  foreach(var body in caller.Bodies){var records=new JsonObject();foreach(var record in bodies[body.Key]!["records"]!.AsObject())records[record.Key]=record.Value!["record"]!.DeepClone();var ready=FeatureBlueprint.Execute(new JsonObject{["operation"]="featureBlueprintDescribe",["featureSource"]=request["functionText"]!.DeepClone(),["featureContracts"]=contracts.DeepClone(),["implementationContext"]=FeatureBlueprint.ImplementationContext(caller),["graph"]=graphs[body.Key]!.DeepClone(),["implementations"]=records});if(ready["state"]?.ToString()!="source-ready"||ready["nodes"]!.AsArray().Any(n=>n!["status"]?.ToString() is "missing" or "stale"))throw new InvalidOperationException("Every final target must preserve valid records/import/wrapper bindings; no changes applied");}
  return new JsonObject{["binding"]=binding,["implementation"]=format(caller),["graphs"]=graphs,["sourceWritten"]=false,["compiled"]=false};
 }
}
