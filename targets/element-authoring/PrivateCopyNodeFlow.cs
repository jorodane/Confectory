using Confectory.Core;
using System.Text.Json.Nodes;

// A first-save copy still uses its sealed donor snapshot. Wrapping changes only
// that isolated candidate; it does not register a copy or write a source file.
internal static class PrivateCopyNodeFlow
{
 internal static JsonObject Prepare(JsonObject snapshot, Element copy, JsonObject graph, JsonArray records, JsonObject contracts, string guard, JsonObject plan)
 {
  if(plan.Any(p=>p.Key is not ("node" or "nonce" or "binding" or "source" or "helpers" or "executionEnum"))||plan["node"] is not JsonValue||plan["nonce"] is not JsonValue)
   throw new ArgumentException("Exact first-save internal-flow proposal required");
  string node=plan["node"]!.GetValue<string>(),root=copy.Id+"/body:"+snapshot["target"]!.ToString();
  string path=node.Contains('/')?node[..node.LastIndexOf('/')]:"",local=path.Length==0?node:node[(path.Length+1)..];
  var before=BlueprintTree.Select(graph,path)["nodes"]!.AsArray().Single(n=>n!["id"]!.ToString()==local)!.AsObject();
  if(before["kind"]?.ToString()!="code"||before["control"]?.ToString() is not ("next" or "switch")||
   plan["executionEnum"] is not null&&!JsonNode.DeepEquals(plan["executionEnum"],before["executionEnum"])||
   plan["helpers"] is not null&&before["control"]?.ToString()!="switch")
   throw new InvalidOperationException("Observed first-save C# action and original execution contract required");
  var original=records.Single(r=>r!["id"]!.ToString()==node)!;
  string recordText=original["record"]!.ToJsonString();
  var binding=new JsonObject{["seed"]=snapshot["hash"]!.DeepClone(),["guard"]=guard,["root"]=root,["node"]=node,
   ["definitionHash"]=original["record"]!["definitionHash"]!.DeepClone(),["sourceHash"]=JsonData.Digest(recordText)};
  if(plan["binding"] is not null&&!JsonNode.DeepEquals(plan["binding"],binding))
   throw new InvalidOperationException("First-save C# snapshot or source changed; retain every input");
  var prepared=BlueprintNodeFlow.Prepare(new JsonObject{["id"]=root,["privatePath"]=path,["node"]=local,["nonce"]=plan["nonce"]!.DeepClone(),
   ["graph"]=graph.DeepClone(),["record"]=recordText,["featureSource"]=snapshot["featureSource"]!.DeepClone(),
   ["featureContracts"]=contracts.DeepClone(),["implementationContext"]=FeatureBlueprint.ImplementationContext(copy),["bodyTarget"]=snapshot["target"]!.DeepClone()});
  string relative=prepared["path"]!.ToString();
  if(records.Any(r=>r!["relative"]!.ToString()==relative))throw new InvalidOperationException("New internal C# path collides with a retained copy record");
  var code=prepared["record"]!.DeepClone();
  foreach(string field in new[]{"source","helpers"})if(plan[field] is not null){string text=plan[field]!.GetValue<string>();if(text.Length>1048576)throw new ArgumentException("Bounded explicit C# body/helpers required");code[field]=text;}
  // The old copy record is virtual, never a physical source. Its donor remains
  // guarded and unchanged; the original definition/hash stays in retainedCode.
  var nextRecords=new JsonArray(records.Where(r=>!ReferenceEquals(r,original)).Select(r=>r!.DeepClone()).ToArray());
  nextRecords.Add(new JsonObject{["id"]=prepared["childKey"]!.DeepClone(),["relative"]=relative,["record"]=code});
  return new JsonObject{["graph"]=prepared["graph"]!.DeepClone(),["records"]=nextRecords,["binding"]=binding};
 }
}
