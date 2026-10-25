using Confectory.Core;
using System.Text.Json.Nodes;

// Explicit whole-body text joins the owner's existing candidate/CAS. This
// adapter never infers a C# edit, a new cell, an alias or a caller binding.
internal static class InformationFunctionWholeBody
{
 internal static JsonObject Prepare(string id, JsonObject graph, Element original, Element requested, Element implementation, string target, JsonObject units, JsonObject plans, JsonObject remap, Func<Element,string> format)
 {
  if(graph["copySource"] is not null)throw new InvalidOperationException("Copy provenance requires its separate explicit source receipt; original copy retained");
  var node=graph["nodes"]!.AsArray().SingleOrDefault(n=>n!["implementationContext"] is not null)??throw new InvalidOperationException("One explicit whole-body context required");
  string recordId=id+"/node:"+node["id"]!.ToString();var unit=units[recordId]?.AsObject()??throw new InvalidOperationException("Original whole-body source missing");
  var plan=plans[recordId]?.AsObject()??throw new InvalidOperationException("Explicitly review the whole C# body and caller storage before changing its contract");
  var before=implementation.Signature!;var selected=InformationFunctionBodies.Signature(plan["signature"]!);
  if(plan["whole"] is JsonObject whole)return Contract(id,graph,original,requested,implementation,target,units,plan,whole,remap,format);

  var expected=new FunctionSignature(before.Args.Select((p,i)=>new Parameter(p.Type,p.Name,requested.Signature!.Args.ElementAtOrDefault(i)?.Mode)).ToList(),before.Return);
  if(!JsonNode.DeepEquals(FeatureBlueprint.SignatureDocument(selected),FeatureBlueprint.SignatureDocument(expected)))throw new InvalidOperationException("Keep exact native names, types, order and out roles; select value/ref explicitly");
  string text=InformationFunctionBodies.Text(recordId,unit["path"]!.ToString(),unit,before,selected,requested.Signature!,plan);
  var modes=new JsonObject(original.Signature!.Args.Where(a=>!a.IsOut).Select(a=>KeyValuePair.Create<string,JsonNode?>(a.Name,JsonValue.Create(requested.Signature!.Args.Single(p=>p.Name==a.Name).IsRef?"ref":"value"))));
  var one=new Parser(format(implementation),"<whole-body-target>").ParseElement();one.Bodies=new(){[target]=implementation.Bodies[target]};
  return BlueprintRootContract.Prepare(new JsonObject{["functionText"]=format(original),["text"]=format(one),["bodyTarget"]=target,["graph"]=graph.DeepClone(),["plan"]=new JsonObject{["args"]=FeatureBlueprint.SignatureDocument(requested.Signature!)["args"]!.DeepClone(),["returnType"]=requested.Signature!.Return,["remap"]=remap.DeepClone(),["inputModes"]=modes,["rootBody"]=new JsonObject{["node"]=node["id"]!.DeepClone(),["source"]=text}}},format);
 }
 // The original graph is first proved to be the exact whole-body lift. Only
 // explicit native text/signature and its positional public storage contract
 // may replace it; no independent nodes, aliases or control routes are erased.
 static JsonObject Contract(string id,JsonObject originalGraph,Element original,Element requested,Element implementation,string target,JsonObject units,JsonObject plan,JsonObject whole,JsonObject remap,Func<Element,string> format)
 {
  string Hash(string text)=>JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(text));
  var node=originalGraph["nodes"]!.AsArray().Single(n=>n!["implementationContext"] is not null)!;
  string nodeId=node["id"]!.ToString(),recordId=id+"/node:"+nodeId;
  var unit=units[recordId]!.AsObject();var originalRecord=JsonNode.Parse(unit["draft"]!.ToString())!;
  if(plan.Count!=7||whole.Count!=4||whole.Any(p=>p.Key is not ("graph" or "hash" or "node" or "returnNode"))||whole["graph"]?.ToString()!=id||whole["hash"]?.ToString()!=Hash(units[id]!["draft"]!.ToString())||whole["node"]?.ToString()!=nodeId||!whole.ContainsKey("returnNode"))throw new InvalidOperationException("Exact original whole-body flow and explicit current return required");
  var selected=InformationFunctionBodies.Signature(plan["signature"]!);
  if(!selected.Matches(requested.Signature))throw new InvalidOperationException("Explicit C# parameters/return must exactly match current public types, roles and order");
  var bodyPlan=plan.DeepClone().AsObject();bodyPlan.Remove("whole");
  string text=InformationFunctionBodies.Text(recordId,unit["path"]!.ToString(),unit,implementation.Signature!,selected,requested.Signature!,bodyPlan);
  var one=new Parser(format(implementation),"<original-whole-target>").ParseElement();one.Bodies=new(){[target]=implementation.Bodies[target]};
  var signature=FeatureBlueprint.SignatureDocument(original.Signature!);
  var proved=BlueprintRootContract.Prepare(new JsonObject{["functionText"]=format(original),["text"]=format(one),["bodyTarget"]=target,["graph"]=originalGraph.DeepClone(),["plan"]=new JsonObject{["args"]=signature["args"]!.DeepClone(),["returnType"]=original.Signature!.Return,["remap"]=new JsonObject(original.Signature.Args.Select(a=>KeyValuePair.Create<string,JsonNode?>(a.Name,JsonValue.Create(a.Name)))),["rootBody"]=new JsonObject{["node"]=nodeId,["source"]=originalRecord["source"]!.DeepClone()}}},format);
  var graph=proved["graph"]!.DeepClone().AsObject();var code=graph["nodes"]!.AsArray().Single(n=>n!["id"]!.ToString()==nodeId)!;
  var priorReturn=graph["nodes"]!.AsArray().SingleOrDefault(n=>n!["kind"]?.ToString()=="export");
  string? returnId=whole["returnNode"]?.GetValue<string>();
  if(requested.Signature!.Return=="void"?returnId is not null:returnId is null||returnId==nodeId||returnId.Length>128||!System.Text.RegularExpressions.Regex.IsMatch(returnId,@"\A[A-Za-z_][A-Za-z_0-9.-]*\z")||priorReturn is not null&&returnId!=priorReturn["id"]!.ToString())throw new InvalidOperationException("Retain the original return writer or explicitly select the new whole-body return; void has no writer");
  one.Signature=selected;code["signature"]=FeatureBlueprint.SignatureDocument(selected);code["implementationContext"]=FeatureBlueprint.ImplementationContext(one);
  code["arguments"]=new JsonObject(selected.Args.Select((p,i)=>(p,i)).Where(x=>!x.p.IsOut).Select(x=>KeyValuePair.Create<string,JsonNode?>(x.p.Name,new JsonObject{["input"]=requested.Signature.Args[x.i].Name})));
  // Out parameters are forwarded cells from the explicit public/native ABI.
  // Their node values remain snapshots; no export value substitutes for a cell.
  var nodes=new JsonArray(code.DeepClone());var edges=new JsonArray();
  if(returnId is not null){var writer=priorReturn?.DeepClone().AsObject()??new JsonObject{["id"]=returnId,["kind"]="export",["intent"]="Assign the existing body's return",["control"]="next",["output"]="return"};writer["signature"]=new JsonObject{["args"]=new JsonArray(new JsonObject{["name"]="value",["type"]=selected.Return}),["return"]="void"};writer["arguments"]=new JsonObject{["value"]=new JsonObject{["node"]=nodeId}};nodes.Add(writer);edges.Add(new JsonObject{["from"]=nodeId,["port"]="next",["to"]=returnId});}
  graph["nodes"]=nodes;graph["edges"]=edges;graph["entry"]=nodeId;
  graph["exits"]=new JsonObject(FeatureBlueprint.FeatureOutputs(requested.Signature).Select(p=>KeyValuePair.Create<string,JsonNode?>(p.Name,null)));if(!graph["exits"]!.AsObject().ContainsKey("return"))graph["exits"]!["return"]=null;
  graph["contractHash"]=FeatureBlueprint.ContractHash(requested);
  if(selected.Args.Any(a=>a.IsRef||a.IsOut)&&!FeatureBlueprint.SupportsExternalRefs(graph["profile"]?.ToString()))graph["profile"]=FeatureBlueprint.ExternalRefsProfile;
  if(graph["outputOrder"] is JsonArray order){var names=FeatureBlueprint.FeatureOutputs(requested.Signature).Select(a=>a.Name).ToArray();var retained=order.Select(a=>a!.ToString()=="return"?"return":remap[a.ToString()]?.GetValue<string>()).Where(n=>n is not null&&names.Contains(n)).Select(n=>n!).Distinct(StringComparer.Ordinal).ToList();retained.AddRange(names.Where(n=>!retained.Contains(n,StringComparer.Ordinal)));graph["outputOrder"]=new JsonArray(retained.Select(n=>JsonValue.Create(n)).ToArray());}
  return new JsonObject{["function"]=format(requested),["implementation"]=format(one),["graph"]=graph,["rootBody"]=new JsonObject{["node"]=nodeId,["source"]=text}};
 }

 internal static JsonObject Receipt(string id,string text,JsonObject graph,JsonObject node)
 {
  var returns=graph["nodes"]!.AsArray().Where(n=>n!["kind"]?.ToString()=="export"&&n["output"]?.ToString()=="return").ToArray();
  return new JsonObject{["graph"]=id,["hash"]=JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(text)),["node"]=node["id"]!.DeepClone(),["returnNode"]=returns.Length==1?returns[0]!["id"]!.DeepClone():null};
 }
 internal static string Caller(string id,JsonObject graph,Element implementation,Element feature,Element changed,JsonObject units,JsonObject plan,JsonObject? selectedNode=null)
 {
  if(graph["copySource"] is not null||implementation.Parent is not null||implementation.Function!=feature.Id||!implementation.Signature!.Matches(feature.Signature))throw new InvalidOperationException("Direct owned caller context required; source retained");
  var node=selectedNode??graph["nodes"]!.AsArray().Single(n=>n!["implementationContext"] is not null)!.AsObject();var native=InformationFunctionBodies.Signature(node["signature"]!);bool context=node["implementationContext"] is not null;
  if(node["kind"]?.ToString()!="code"||!native.Matches(implementation.Signature)||context&&(!JsonNode.DeepEquals(node["implementationContext"],FeatureBlueprint.ImplementationContext(implementation))||!JsonNode.DeepEquals(node["signature"],FeatureBlueprint.SignatureDocument(implementation.Signature)))||!context&&node["forwardCallerStorage"]?.GetValue<bool>()!=true)throw new InvalidOperationException("Original caller native/context contract changed");
  foreach(var import in implementation.Imports.Values)if(PackPaths.Namespace(import.Id)!=PackPaths.Namespace(implementation.Id)||units[import.Id]?["kind"]?.ToString()!="function")throw new InvalidOperationException("Registered caller imports require their separate read-only receipts");
  if(plan.Count!=7||!JsonNode.DeepEquals(plan["whole"],Receipt(id,units[id]!["draft"]!.ToString(),graph,node)))throw new InvalidOperationException("Original caller graph and manual body receipt required");
  var explicitPlan=plan.DeepClone().AsObject();explicitPlan.Remove("whole");string recordId=id+"/node:"+node["id"]!.ToString();var unit=units[recordId]!.AsObject();
  return InformationFunctionBodies.Text(recordId,unit["path"]!.ToString(),unit,native,native,changed.Signature!,explicitPlan);
 }

}
