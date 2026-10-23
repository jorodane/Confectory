using Confectory.Core;
using System.Text.Json.Nodes;

// Pure, conservative preview for an existing wrapped call. No field/name guessing,
// provider-body reads, source writes or execution. The workspace owns apply/CAS.
internal static class BlueprintCallAbi
{
 public static JsonObject Prepare(JsonObject request,Func<Element,string> format)
 {
  var caller=new Parser(request["text"]!.GetValue<string>(),"<abi-caller>").ParseElement();var graph=request["graph"]!.DeepClone().AsObject();string nodeId=request["node"]!.GetValue<string>();
  if(caller.Kind!="implementation"||caller.Id!=request["id"]!.ToString()||caller.Parent is not null||graph["feature"]?.ToString()!=caller.Function||caller.Bodies.Count!=1||caller.Bodies.Values.Single().SourceKind!="blueprint")throw new ArgumentException("One ordinary owned Blueprint root required for explicit ABI repair");
  var node=graph["nodes"]!.AsArray().Single(n=>n!["id"]!.ToString()==nodeId)!.AsObject();string feature=node["feature"]?.ToString()??throw new ArgumentException("Referenced function required");
  if(node["kind"]?.ToString()!="call"||node["control"]?.ToString()!="switch"||node["postCall"]?["mode"]?.ToString()!="execution-enum"||node["implementationContext"] is not null||node["forwardCallerStorage"]?.GetValue<bool>()==true||graph["nodes"]!.AsArray().Any(n=>n!["kind"]?.ToString()=="graph"||n["id"]!.ToString()!=nodeId&&(n["feature"]?.ToString()==feature||n["imports"]?.AsArray().Any(i=>i?.ToString()==feature)==true)))throw new ArgumentException("Repair all other uses explicitly; retain the existing caller");
  FunctionSignature Read(JsonNode value){var rows=value["args"]!.AsArray();if(rows.Count>64)throw new ArgumentException("ABI argument budget");return new(rows.Select(p=>new Parameter(p!["type"]!.ToString(),p["name"]!.ToString(),p["mode"]?.GetValue<string>())).ToList(),value["return"]!.ToString());}
  var before=Read(node["signature"]!);var after=Read(request["signature"]!);if(before.Return!=after.Return||before.Args.Count!=after.Args.Count||before.Args.Where((a,i)=>a.Name!=after.Args[i].Name||a.Type!=after.Args[i].Type||a.IsOut!=after.Args[i].IsOut||a.Mode is not (null or "ref" or "out")||after.Args[i].Mode is not (null or "ref" or "out")).Any()||before.Args.Select(p=>p.Mode).SequenceEqual(after.Args.Select(p=>p.Mode)))throw new ArgumentException("Explicit matching field identities/types and a value/ref ABI change required; unknown remaps remain intact");
  var arguments=node["arguments"]!.AsObject();if(arguments.Count!=after.Args.Count(p=>!p.IsOut)||after.Args.Where(p=>!p.IsOut).Any(p=>!arguments.ContainsKey(p.Name)))throw new ArgumentException("Every existing input binding must be preserved explicitly");
  foreach(var a in after.Args.Where(p=>p.IsRef))if(arguments[a.Name] is not JsonObject binding||!(binding.Count==1&&(binding["input"] is JsonValue||binding["local"] is JsonValue)||binding.Count is 1 or 2&&binding["node"] is JsonValue&&binding.All(p=>p.Key is "node" or "output")))throw new ArgumentException("New ref input requires explicitly selected existing storage; literals cannot be guessed into references");
  string alias=FeatureBlueprint.ImportAlias(feature);if(caller.Imports.Count(p=>p.Value.Id==feature)!=1||!caller.Imports.TryGetValue(alias,out var imported)||!imported.Signature.Matches(before))throw new ArgumentException("Exact existing typed import and alias required");
  caller.Imports[alias]=imported with {Signature=after};node["signature"]=request["signature"]!.DeepClone();var post=node["postCall"]!.AsObject();post["contractHash"]=request["contractHash"]!.DeepClone();post["source"]=request["source"]?.DeepClone()??post["source"]!.DeepClone();post["helpers"]=request["helpers"]?.DeepClone()??post["helpers"]?.DeepClone()??JsonValue.Create("");if(request["executionEnum"] is not null)node["executionEnum"]=request["executionEnum"]!.DeepClone();
  return new(){["implementation"]=format(caller),["graph"]=graph,["before"]=FeatureBlueprint.SignatureDocument(before),["signature"]=FeatureBlueprint.SignatureDocument(after),["feature"]=feature,["alias"]=alias,["scope"]=imported.Scope,["sourceWritten"]=false,["compiled"]=false,["executed"]=false};
 }
}
