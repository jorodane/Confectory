using Confectory.Core;
using System.Text.Json.Nodes;

// Pure, conservative preview for an existing wrapped call. No field/name guessing,
// provider-body reads, source writes or execution. The workspace owns apply/CAS.
internal static class BlueprintCallAbi
{
 public static JsonObject Prepare(JsonObject request,Func<Element,string> format)
 {
  var caller=new Parser(request["text"]!.GetValue<string>(),"<abi-caller>").ParseElement();var root=request["graph"]!.DeepClone().AsObject();string privatePath=request["privatePath"]?.GetValue<string>()??"";var graph=BlueprintTree.Select(root,privatePath);string nodeId=request["node"]!.GetValue<string>();
  if(caller.Kind!="implementation"||caller.Id!=request["id"]!.ToString()||caller.Parent is not null||root["feature"]?.ToString()!=caller.Function||caller.Bodies.Count!=1||caller.Bodies.Values.Single().SourceKind!="blueprint")throw new ArgumentException("One ordinary owned Blueprint root required for explicit ABI repair");
  var node=graph["nodes"]!.AsArray().Single(n=>n!["id"]!.ToString()==nodeId)!.AsObject();string feature=node["feature"]?.ToString()??throw new ArgumentException("Referenced function required");
  if(node["kind"]?.ToString()!="call"||node["control"]?.ToString()!="switch"||node["postCall"]?["mode"]?.ToString()!="execution-enum"||node["implementationContext"] is not null||node["forwardCallerStorage"]?.GetValue<bool>()==true||graph["nodes"]!.AsArray().Any(n=>n!["kind"]?.ToString()=="graph"||n["id"]!.ToString()!=nodeId&&(n["feature"]?.ToString()==feature||n["imports"]?.AsArray().Any(i=>i?.ToString()==feature)==true)))throw new ArgumentException("Repair all other uses explicitly; retain the existing caller");
  // One selected private use may update the caller's existing typed import.
  // Other frames and opaque whole-body contexts never receive an inferred repair.
  if(privatePath.Length>0&&BlueprintTree.Nodes(root).Any(e=>e.Key!=privatePath+"/"+nodeId&&(e.Node["implementationContext"] is not null||e.Node["feature"]?.ToString()==feature||e.Node["imports"]?.AsArray().Any(i=>i?.ToString()==feature)==true)))throw new ArgumentException("Every other private/import use needs its own coordinated contract; retain the snapshot");
  FunctionSignature Read(JsonNode value){var rows=value["args"]!.AsArray();if(rows.Count>64)throw new ArgumentException("ABI argument budget");return new(rows.Select(p=>new Parameter(p!["type"]!.ToString(),p["name"]!.ToString(),p["mode"]?.GetValue<string>())).ToList(),value["return"]!.ToString());}
  var before=Read(node["signature"]!);var after=Read(request["signature"]!);
  if(before.Args.Concat(after.Args).Any(p=>p.Mode is not (null or "ref" or "out"))||before.Args.Select(p=>p.Name).Distinct(StringComparer.Ordinal).Count()!=before.Args.Count||after.Args.Select(p=>p.Name).Distinct(StringComparer.Ordinal).Count()!=after.Args.Count)throw new ArgumentException("Unique native parameter identities and supported modes required");
  // A selected private call uses the same explicit input/output correspondence
  // as a root call. Rebind only this frame; the workspace validates the complete
  // resulting graph and typed import together before applying its candidate.
  bool matching=before.Return==after.Return&&before.Args.Count==after.Args.Count&&!before.Args.Where((a,i)=>a.Name!=after.Args[i].Name||a.Type!=after.Args[i].Type||a.IsOut!=after.Args[i].IsOut).Any();
  if(before.Return==after.Return&&before.Args.Select(p=>(p.Name,p.Type,p.Mode)).SequenceEqual(after.Args.Select(p=>(p.Name,p.Type,p.Mode))))throw new ArgumentException("A changed ABI must be explicitly reviewed");
  var arguments=node["arguments"]!.AsObject();if(arguments.Count!=before.Args.Count(p=>!p.IsOut)||before.Args.Where(p=>!p.IsOut).Any(p=>!arguments.ContainsKey(p.Name)))throw new ArgumentException("Every original input binding must be observed explicitly");
  string alias=FeatureBlueprint.ImportAlias(feature);if(caller.Imports.Count(p=>p.Value.Id==feature)!=1||!caller.Imports.TryGetValue(alias,out var imported)||!imported.Signature.Matches(before))throw new ArgumentException("Exact existing typed import and alias required");
  var oldOutputs=FeatureBlueprint.FeatureOutputs(before).Select(p=>p.Name).ToArray();var outputs=FeatureBlueprint.FeatureOutputs(after).Select(p=>p.Name).ToArray();
  if(request["previewRemap"]?.GetValue<bool>()==true&&!matching){
   var inputMap=new JsonObject();foreach(var arg in after.Args.Where(p=>!p.IsOut))inputMap[arg.Name]=before.Args.Any(p=>!p.IsOut&&p.Name==arg.Name)?JsonValue.Create(arg.Name):null;
   var outputMap=new JsonObject();foreach(string name in oldOutputs)outputMap[name]=outputs.Contains(name,StringComparer.Ordinal)?JsonValue.Create(name):null;
   return new(){["requiresRemap"]=true,["remap"]=new JsonObject{["inputs"]=inputMap,["outputs"]=outputMap},["before"]=FeatureBlueprint.SignatureDocument(before),["signature"]=FeatureBlueprint.SignatureDocument(after),["sourceWritten"]=false,["compiled"]=false};
  }
  if(request["remap"] is JsonObject remap){
   if(remap.Count!=2||remap["inputs"] is not JsonObject inputMap||remap["outputs"] is not JsonObject outputMap||inputMap.Count!=after.Args.Count(p=>!p.IsOut)||inputMap.Any(p=>!after.Args.Any(a=>!a.IsOut&&a.Name==p.Key))||outputMap.Count!=oldOutputs.Length||outputMap.Any(p=>!oldOutputs.Contains(p.Key,StringComparer.Ordinal)))throw new ArgumentException("Complete explicit input/output mapping required");
   var next=new JsonObject();var used=new HashSet<string>(StringComparer.Ordinal);
   foreach(var arg in after.Args.Where(p=>!p.IsOut)){
    var value=inputMap[arg.Name];if(value is JsonValue name&&name.TryGetValue<string>(out var old)&&arguments.ContainsKey(old)&&used.Add(old))next[arg.Name]=arguments[old]?.DeepClone();
    else if(value is JsonObject literal&&literal.Count==1&&literal["valueJson"] is JsonValue raw&&raw.TryGetValue<string>(out var json)&&json.Length<=65536&&!arg.IsRef){using var parsed=System.Text.Json.JsonDocument.Parse(json);next[arg.Name]=new JsonObject{["constant"]=JsonNode.Parse(parsed.RootElement.GetRawText())};}
    else throw new ArgumentException("Select an original input once or an explicit value; new ref inputs require existing storage");
   }
   if(arguments.Any(p=>!used.Contains(p.Key)&&p.Value is not null))throw new InvalidOperationException("A removed input still has a binding; retain every input and explicitly disconnect it first");
   var usedOutputs=new HashSet<string>(StringComparer.Ordinal);foreach(var pair in outputMap)if(pair.Value is not null&&(pair.Value is not JsonValue name||!name.TryGetValue<string>(out var target)||!outputs.Contains(target,StringComparer.Ordinal)||!usedOutputs.Add(target)))throw new ArgumentException("Explicit unique current output identities required");
   void Rebind(JsonNode? value){if(value is JsonObject obj){if(obj["node"]?.ToString()==nodeId){if(obj.Any(p=>p.Key is not ("node" or "output")))throw new ArgumentException("Exact existing data binding required");string old=obj["output"]?.GetValue<string>()??"return",target=outputMap[old]?.GetValue<string>()??throw new InvalidOperationException("A removed output still has consumers; no connection was dropped");if(!oldOutputs.Contains(old,StringComparer.Ordinal))throw new ArgumentException("Unknown original output");if(obj.ContainsKey("output")||target!="return")obj["output"]=target;}foreach(var child in obj.ToArray())if(child.Key!="constant")Rebind(child.Value);}else if(value is JsonArray array)foreach(var child in array)Rebind(child);}
   node["arguments"]=next;Rebind(graph);arguments=next;
  }else if(!matching)throw new ArgumentException("Explicit input/output mapping required; unknown remaps remain intact");
  foreach(var a in after.Args.Where(p=>p.IsRef))if(arguments[a.Name] is not JsonObject binding||!(binding.Count==1&&(binding["input"] is JsonValue||binding["local"] is JsonValue)||binding.Count is 1 or 2&&binding["node"] is JsonValue&&binding.All(p=>p.Key is "node" or "output")))throw new ArgumentException("New ref input requires explicitly selected existing storage; literals cannot be guessed into references");
  caller.Imports[alias]=imported with {Signature=after};node["signature"]=request["signature"]!.DeepClone();var post=node["postCall"]!.AsObject();post["contractHash"]=request["contractHash"]!.DeepClone();post["source"]=request["source"]?.DeepClone()??post["source"]!.DeepClone();post["helpers"]=request["helpers"]?.DeepClone()??post["helpers"]?.DeepClone()??JsonValue.Create("");if(request["executionEnum"] is not null)node["executionEnum"]=request["executionEnum"]!.DeepClone();
  if(request["remap"] is not null)post["returnMapping"]=after.Return=="void"?null:JsonValue.Create(BlueprintCallWrapper.NativeReturnMapping);
  return new(){["implementation"]=format(caller),["graph"]=root,["before"]=FeatureBlueprint.SignatureDocument(before),["signature"]=FeatureBlueprint.SignatureDocument(after),["feature"]=feature,["alias"]=alias,["scope"]=imported.Scope,["sourceWritten"]=false,["compiled"]=false,["executed"]=false};
 }
}
