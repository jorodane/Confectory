using Confectory.Core;
using System.Text;
using System.Text.Json.Nodes;

// One physical copy, one callee, every qualified ordinary wrapped use. No source
// writes or inferred C# edits. The workspace binds the result to its owned CAS.
internal static class BlueprintCallAbiUses
{
 public static JsonObject Prepare(JsonObject request,Func<Element,string> format)
 {
  if(Encoding.UTF8.GetByteCount(request.ToJsonString())>2097152)throw new ArgumentException("Call-use closure budget");
  string id=request["id"]!.ToString(),text=request["text"]!.GetValue<string>(),feature=request["feature"]!.ToString();
  var root=request["graph"]!.AsObject();var caller=new Parser(text,"<call-use-owner>").ParseElement();
  var fn=new Parser(request["functionText"]!.GetValue<string>(),"<call-use-function>").ParseElement();
  var records=request["records"]!.AsObject();var contracts=request["featureContracts"]!.AsObject();var callee=new Parser(contracts[feature]!.GetValue<string>(),"<call-use-callee>").ParseElement();
  if(caller.Id!=id||caller.Kind!="implementation"||caller.Parent is not null||caller.Bodies.Count!=1||caller.Bodies.Values.Single().SourceKind!="blueprint"||fn.Kind!="function"||fn.Id!=caller.Function||!fn.Signature!.Matches(caller.Signature)||callee.Kind!="function"||callee.Id!=feature)throw new ArgumentException("Exact single-target implementation and contracts required");
  var entries=BlueprintTree.Nodes(root).ToArray();var uses=entries.Where(e=>e.Node["feature"]?.ToString()==feature).OrderBy(e=>e.Key,StringComparer.Ordinal).ToArray();
  if(uses.Length is <2 or >32||entries.Any(e=>e.Node["implementationContext"] is not null||e.Node["imports"]?.AsArray().Any(i=>i?.ToString()==feature)==true)||uses.Any(e=>e.Node["kind"]?.ToString()!="call"||e.Node["control"]?.ToString()!="switch"||e.Node["postCall"]?["mode"]?.ToString()!="execution-enum"||e.Node["forwardCallerStorage"]?.GetValue<bool>()==true))throw new ArgumentException("Every ordinary wrapped use must be coordinated; opaque/import uses retain their input");
  var keys=uses.Select(e=>e.Key).ToHashSet(StringComparer.Ordinal);
  JsonObject Definitions(JsonObject graph,bool inspect)=>FeatureBlueprint.Execute(new JsonObject{["operation"]="featureBlueprintNodes",["featureSource"]=request["functionText"]!.DeepClone(),["featureContracts"]=contracts.DeepClone(),["implementationContext"]=FeatureBlueprint.ImplementationContext(caller),["bodyTarget"]=caller.Bodies.Keys.Single(),["graph"]=graph.DeepClone(),["inspectStalePostCalls"]=inspect});
  var definitions=Definitions(root,true);if(definitions["state"]?.ToString()!="node-definitions")throw new InvalidOperationException("Original call-use tree must remain inspectable");
  var rows=definitions["nodes"]!.AsArray().Concat(definitions["nestedNodes"]?.AsArray()??new JsonArray()).ToDictionary(n=>n!["id"]!.ToString(),n=>n!,StringComparer.Ordinal);
  var signature=FeatureBlueprint.SignatureDocument(callee.Signature!);var previews=new JsonObject();
  foreach(var use in uses){
   var row=rows[use.Key];if(row["postCallStale"]?.GetValue<bool>()!=true||row["postCallSignatureMatches"]?.GetValue<bool>()!=false||!JsonNode.DeepEquals(signature,row["currentCallSignature"]))throw new InvalidOperationException("Every use must explicitly refresh the same current callee");
   int split=use.Key.LastIndexOf('/');string path=split<0?"":use.Key[..split],local=split<0?use.Key:use.Key[(split+1)..];
   var preview=BlueprintCallAbi.Prepare(new JsonObject{["id"]=id,["text"]=text,["graph"]=root.DeepClone(),["privatePath"]=path,["node"]=local,["signature"]=signature.DeepClone(),["contractHash"]=row["postCallEditor"]!["contractHash"]!.DeepClone(),["previewRemap"]=true},format,keys);
   previews[use.Key]=new JsonObject{["node"]=local,["privatePath"]=path,["before"]=use.Node["signature"]!.DeepClone(),["source"]=use.Node["postCall"]!["source"]!.DeepClone(),["helpers"]=use.Node["postCall"]?["helpers"]?.DeepClone()??JsonValue.Create(""),["executionEnum"]=use.Node["executionEnum"]!.DeepClone(),["contractHash"]=row["postCallEditor"]!["contractHash"]!.DeepClone(),["refreshFrom"]=use.Node["postCall"]!["contractHash"]!.DeepClone(),["returnMapping"]=row["postCallEditor"]?["returnMapping"]?.DeepClone(),["remap"]=preview["remap"]?.DeepClone()};
  }
  if(Encoding.UTF8.GetByteCount(previews.ToJsonString())>262144)throw new ArgumentException("Bounded per-call approval plans required; retain original input");
  var binding=new JsonObject{["schema"]=1,["implementation"]=id,["implementationHash"]=JsonData.Digest(text),["graphHash"]=JsonData.Digest(root.ToJsonString()),["functionHash"]=JsonData.Digest(request["functionText"]!.GetValue<string>()),["contractsHash"]=JsonData.Digest(contracts.ToJsonString()),["recordsHash"]=JsonData.Digest(records.ToJsonString()),["feature"]=feature,["signature"]=signature.DeepClone(),["uses"]=new JsonArray(uses.Select(e=>(JsonNode)JsonValue.Create(e.Key)!).ToArray())};
  if(request["plans"] is null)return new JsonObject{["binding"]=binding,["plans"]=previews,["sourceWritten"]=false,["compiled"]=false};
  if(!JsonNode.DeepEquals(binding,request["binding"]))throw new InvalidOperationException("Observed call-use closure changed; retain every input");
  var plans=request["plans"]!.AsObject();if(plans.Count!=previews.Count||plans.Any(p=>!previews.ContainsKey(p.Key)))throw new ArgumentException("Explicit plans for every affected call required");
  var candidate=root.DeepClone().AsObject();string implementation=text;
  foreach(var use in uses){
   var expected=previews[use.Key]!;var plan=plans[use.Key]!.AsObject();
   if(plan.Count is <9 or >10||plan.Any(p=>p.Key is not ("node" or "privatePath" or "before" or "source" or "helpers" or "executionEnum" or "contractHash" or "refreshFrom" or "returnMapping" or "remap"))||new[]{"node","privatePath","before","contractHash","refreshFrom","returnMapping"}.Any(k=>!JsonNode.DeepEquals(plan[k],expected[k])))throw new InvalidOperationException("Exact per-call source and contract correspondence required");
   var wrapper=BlueprintCallWrapper.Prepare(callee,plan["executionEnum"]!.AsObject(),plan["contractHash"]!.ToString(),plan["source"]!.GetValue<string>(),plan["helpers"]!.GetValue<string>(),plan["returnMapping"]?.GetValue<string>());
   var next=BlueprintCallAbi.Prepare(new JsonObject{["id"]=id,["text"]=text,["graph"]=candidate,["privatePath"]=expected["privatePath"]!.DeepClone(),["node"]=expected["node"]!.DeepClone(),["signature"]=signature.DeepClone(),["contractHash"]=wrapper["contractHash"]!.DeepClone(),["source"]=wrapper["source"]!.DeepClone(),["helpers"]=wrapper["helpers"]!.DeepClone(),["executionEnum"]=wrapper["executionEnum"]!.DeepClone(),["remap"]=plan["remap"]?.DeepClone()},format,keys);
   candidate=next["graph"]!.DeepClone().AsObject();implementation=next["implementation"]!.GetValue<string>();
  }
  caller=new Parser(implementation,"<call-use-candidate>").ParseElement();
  var ready=FeatureBlueprint.Execute(new JsonObject{["operation"]="featureBlueprintDescribe",["featureSource"]=request["functionText"]!.DeepClone(),["featureContracts"]=contracts.DeepClone(),["implementationContext"]=FeatureBlueprint.ImplementationContext(caller),["bodyTarget"]=caller.Bodies.Keys.Single(),["graph"]=candidate.DeepClone(),["implementations"]=records.DeepClone()});
  if(ready["state"]?.ToString()!="source-ready")throw new InvalidOperationException("Complete call-use candidate is incompatible; no partial result: "+ready.ToJsonString());
  return new JsonObject{["implementation"]=implementation,["graph"]=candidate,["binding"]=binding,["uses"]=binding["uses"]!.DeepClone(),["sourceWritten"]=false,["compiled"]=false,["executed"]=false};
 }
}
