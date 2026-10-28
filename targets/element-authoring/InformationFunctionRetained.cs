using Confectory.Core;
using System.Text.Json.Nodes;

// Existing graphs retain every independent node, route, local and alias. Only
// explicitly selected native sources, semantic bindings and output writers move.
internal static class InformationFunctionRetained
{
 internal static bool IsLift(JsonObject graph)
 {
  var nodes=graph["nodes"]!.AsArray();var context=nodes.SingleOrDefault(n=>n!["implementationContext"] is not null);
  if(context is null||graph["entry"]?.ToString()!=context["id"]!.ToString()||graph["locals"] is JsonArray locals&&locals.Count>0||graph["exits"]!.AsObject().Any(p=>p.Value is not null))return false;
  if(context["signature"]!["return"]?.ToString()=="void")return nodes.Count==1&&graph["edges"]!.AsArray().Count==0;
  if(nodes.Count!=2)return false;var writer=nodes.Single(n=>n!["id"]!.ToString()!=context["id"]!.ToString())!;var edges=graph["edges"]!.AsArray();return writer["kind"]?.ToString()=="export"&&writer["output"]?.ToString()=="return"&&JsonNode.DeepEquals(writer["arguments"],new JsonObject{["value"]=new JsonObject{["node"]=context["id"]!.DeepClone()}})&&edges.Count==1&&edges[0]?["from"]?.ToString()==context["id"]!.ToString()&&edges[0]?["port"]?.ToString()=="next"&&edges[0]?["to"]?.ToString()==writer["id"]!.ToString();
 }
 internal static JsonObject Prepare(string id,JsonObject originalGraph,Element original,Element requested,Element implementation,string target,JsonObject units,JsonObject bodyPlans,JsonObject remap,JsonObject implementationPlans,HashSet<string> selectedUses,JsonObject outputPlans,HashSet<string> selectedOutputs,JsonObject graphPlans,HashSet<string> selectedGraphs,string? propertyProof,Func<Element,string> format)
 {
  if(originalGraph["copySource"] is not null)throw new InvalidOperationException("Copy provenance requires its separate receipt; source retained");
  var graph=originalGraph.DeepClone().AsObject();var coordinated=new HashSet<string>(StringComparer.Ordinal);var sources=new JsonObject();var mappings=new List<(string Node,JsonObject Outputs)>();
  var one=new Parser(format(implementation),"<retained-whole-target>").ParseElement();one.Bodies=new(){[target]=implementation.Bodies[target]};one.Signature=requested.Signature;
  foreach(var item in originalGraph["nodes"]!.AsArray().Where(n=>n!["implementationContext"] is not null||n["forwardCallerStorage"]?.GetValue<bool>()==true)){
   var before=item!.AsObject();string nodeId=before["id"]!.ToString();var native=InformationFunctionBodies.Signature(before["signature"]!);bool context=before["implementationContext"] is not null;
   if(!native.Matches(original.Signature)||context&&(!JsonNode.DeepEquals(before["implementationContext"],FeatureBlueprint.ImplementationContext(implementation))||!JsonNode.DeepEquals(before["signature"],FeatureBlueprint.SignatureDocument(implementation.Signature!))))throw new InvalidOperationException("Exact original native/public storage and context required");
   var args=before["arguments"]!.AsObject();if(args.Count!=native.Args.Count(a=>!a.IsOut)||native.Args.Select((p,i)=>(p,i)).Where(x=>!x.p.IsOut).Any(x=>args[x.p.Name] is not JsonObject b||b.Count!=1||b["input"]?.ToString()!=original.Signature!.Args[x.i].Name))throw new InvalidOperationException("Original forwarded storage must be positional and unchanged");
   coordinated.Add(nodeId);var node=graph["nodes"]!.AsArray().Single(n=>n!["id"]!.ToString()==nodeId)!;
   if(before["kind"]?.ToString()=="call"){
    if(context||!native.Matches(requested.Signature))throw new InvalidOperationException("Forwarded call must retain its real callee types/roles; edit that contract explicitly first");
    node["arguments"]=new JsonObject(native.Args.Select((p,i)=>(p,i)).Where(x=>!x.p.IsOut).Select(x=>KeyValuePair.Create<string,JsonNode?>(x.p.Name,new JsonObject{["input"]=requested.Signature!.Args[x.i].Name})));continue;
   }
   if(before["kind"]?.ToString()!="code"||before["control"]?.ToString()!="next")throw new InvalidOperationException("Existing serial native code or forwarded call required");
   string recordId=id+"/node:"+nodeId;var plan=bodyPlans[recordId]?.AsObject()??throw new InvalidOperationException("Explicit native text and output mapping required for every stored body");var unit=units[recordId]!.AsObject();
   if(plan.Count!=8||!JsonNode.DeepEquals(plan["whole"],InformationFunctionWholeBody.Receipt(id,units[id]!["draft"]!.ToString(),originalGraph,before)))throw new InvalidOperationException("Exact retained graph and source receipt required");
   var selected=InformationFunctionBodies.Signature(plan["signature"]!);if(!selected.Matches(requested.Signature))throw new InvalidOperationException("Selected native/public parameter types, modes and order must match");
   var explicitPlan=plan.DeepClone().AsObject();explicitPlan.Remove("whole");explicitPlan.Remove("outputs");sources[recordId]=InformationFunctionBodies.Text(recordId,unit["path"]!.ToString(),unit,native,selected,requested.Signature!,explicitPlan);
   var outputs=plan["outputs"]!.AsObject();var oldOutputs=FeatureBlueprint.FeatureOutputs(native).ToArray();var newOutputs=FeatureBlueprint.FeatureOutputs(selected).ToArray();
   if(outputs.Count!=oldOutputs.Length||oldOutputs.Any(p=>!outputs.ContainsKey(p.Name))||outputs.Any(p=>p.Value is not null&&!newOutputs.Any(n=>n.Name==p.Value.GetValue<string>()&&n.Type==oldOutputs.Single(v=>v.Name==p.Key).Type)))throw new InvalidOperationException("Map each old native output to an exact compatible current output explicitly");
   mappings.Add((nodeId,outputs));node["signature"]=FeatureBlueprint.SignatureDocument(selected);node["arguments"]=new JsonObject(selected.Args.Select((p,i)=>(p,i)).Where(x=>!x.p.IsOut).Select(x=>KeyValuePair.Create<string,JsonNode?>(x.p.Name,new JsonObject{["input"]=requested.Signature!.Args[x.i].Name})));
   if(context){one.Signature=selected;node["implementationContext"]=FeatureBlueprint.ImplementationContext(one);}
  }
  var outputPlan=InformationFunctionOutputs.Plan(id,units[id]!["draft"]!.ToString(),originalGraph,original.Signature!,requested.Signature!,outputPlans,selectedOutputs,remap,BlueprintOutputSnapshot.Read(original),graphPlans,selectedGraphs,graph);
  var replacements=InformationFunctionInputUses.Detach(id,units[id]!["draft"]!.ToString(),graph,units,original.Signature!,requested.Signature!,remap,implementationPlans,selectedUses,propertyProof,InformationFunctionOutputs.ReplacedSlots(originalGraph,outputPlan));
  outputPlan["remap"]=remap.DeepClone();var modes=new JsonObject();foreach(var arg in original.Signature!.Args.Where(a=>!a.IsOut)){var current=requested.Signature!.Args.SingleOrDefault(a=>a.Name==remap[arg.Name]?.ToString());if(current is not null&&!current.IsOut&&current.Type==arg.Type&&current.Mode!=arg.Mode)modes[arg.Name]=current.IsRef?"ref":"value";}if(modes.Count>0)outputPlan["inputModes"]=modes;
  // Root preparation is still inaccessible to a public caller with a whitelist:
  // these exact coordinated IDs are supplied only after the native proof above.
  var prepared=BlueprintRootContract.Prepare(new JsonObject{["functionText"]=format(original),["text"]=format(one),["bodyTarget"]=target,["graph"]=graph,["plan"]=outputPlan},format,coordinated);graph=prepared["graph"]!.DeepClone().AsObject();InformationFunctionInputUses.Restore(graph,replacements,remap);
  var currentSlots=InformationFunctionOutputs.ReplacedSlots(originalGraph,outputPlan);var created=(outputPlan["outputCreates"] as JsonArray??new()).Select(n=>n!["node"]!.ToString()).ToHashSet(StringComparer.Ordinal);
  void Rebind(JsonNode? value,string nodeId,JsonObject outputs){if(value is JsonObject o){if(o["node"]?.ToString()==nodeId){string old=o["output"]?.ToString()??"return";string to=outputs[old]?.GetValue<string>()??throw new InvalidOperationException("A removed native output still has a consumer; retain every source");if(to=="return")o.Remove("output");else o["output"]=to;return;}foreach(var p in o)if(p.Key!="constant")Rebind(p.Value,nodeId,outputs);}else if(value is JsonArray a)foreach(var v in a)Rebind(v,nodeId,outputs);}
  foreach(var (nodeId,outputs) in mappings){foreach(var node in graph["nodes"]!.AsArray())if(!coordinated.Contains(node!["id"]!.ToString())&&!created.Contains(node["id"]!.ToString()))foreach(var binding in node["arguments"]!.AsObject())if(!currentSlots.Contains(node["id"]+"#"+binding.Key))Rebind(binding.Value,nodeId,outputs);foreach(var local in graph["locals"] as JsonArray??new())Rebind(local!["source"],nodeId,outputs);foreach(var exit in graph["exits"]!.AsObject())if(!currentSlots.Contains("$exit:"+exit.Key+"#value"))Rebind(exit.Value,nodeId,outputs);}
  if(requested.Signature!.Args.Any(a=>a.IsRef||a.IsOut)&&!FeatureBlueprint.SupportsExternalRefs(graph["profile"]?.ToString()))graph["profile"]=FeatureBlueprint.ExternalRefsProfile;
  return new JsonObject{["function"]=format(requested),["implementation"]=format(one),["graph"]=graph,["sources"]=sources};
 }
}
