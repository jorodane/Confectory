using Confectory.Core;
using System.Text.Json.Nodes;

// Explicit ordinary value bindings only. Code parameter contracts and C# sources
// are never rewritten. The owner transaction validates and saves the full closure.
internal static class InformationFunctionInputUses
{
 static string Hash(string text)=>JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(text));
 // Ordinary calls use the existing owned typed import and exact callee
 // signature. Never infer registered/inherited, recursive, wrapper or ref ABI.
 static bool SupportedCall(JsonObject node,string function,Element implementation,JsonObject units)
 {
  string? called=node["feature"]?.ToString();if(node["kind"]?.ToString()!="call"||node["postCall"] is not null||called is null||called==function||!called.StartsWith(PackPaths.Namespace(function)+"::",StringComparison.Ordinal)||units[called]?["kind"]?.ToString()!="function")return false;
  var target=new Parser(units[called]!["draft"]!.ToString(),"<input-use-callee>").ParseElement();var imports=implementation.Imports.Values.Where(i=>i.Id==called).ToArray();
  return target.Id==called&&target.Parent is null&&target.Signature is not null&&target.Signature.Args.All(a=>a.Mode is null)&&imports.Length==1&&imports[0].Signature.Matches(target.Signature)&&JsonNode.DeepEquals(node["signature"],FeatureBlueprint.SignatureDocument(target.Signature));
 }
 public static JsonObject Read(JsonObject request)
 {
  string owner=request["id"]!.ToString(),function=request["function"]!.ToString(),ns=PackPaths.Namespace(owner);var units=request["units"]!.AsObject();
  var schema=new Parser(units[owner]!["draft"]!.ToString(),"<input-use-owner>").ParseElement();
  if(units.Count>2048||schema.Kind!="schema"||!schema.Contains.Any(c=>c.Id==function&&c.Kind=="function")||!function.StartsWith(owner+"_Function_",StringComparison.Ordinal))throw new InvalidOperationException("Direct owned function input uses required");
  var fn=new Parser(units[function]!["draft"]!.ToString(),"<input-use-function>").ParseElement();var result=new JsonObject();
  foreach(var entry in units){if(entry.Value?["kind"]?.ToString()!="implementation")continue;var impl=new Parser(entry.Value["draft"]!.ToString(),"<input-use-implementation>").ParseElement();if(impl.Function!=function)continue;
   if(!entry.Key.StartsWith(ns+"::",StringComparison.Ordinal)||impl.Id!=entry.Key||impl.Parent is not null||impl.Bodies.Count is <1 or >8)throw new InvalidOperationException("Direct owned implementation and all targets required");
   foreach(var body in impl.Bodies){if(body.Value.SourceKind!="blueprint")throw new InvalidOperationException("C# body input replacement requires explicit source editing");string id=impl.Id+"/body:"+body.Key;var unit=units[id]??throw new InvalidOperationException("Original input-use graph missing");var g=JsonNode.Parse(unit["draft"]!.ToString())!.AsObject();
    foreach(var node in g["nodes"]!.AsArray().Where(n=>(n!["kind"]?.ToString()=="code"||SupportedCall(n.AsObject(),function,impl,units))&&n["control"]?.ToString()=="next"&&n["implementationContext"] is null&&n["forwardCallerStorage"]?.GetValue<bool>()!=true))foreach(var argument in node!["arguments"]!.AsObject()){
     if(argument.Value is not JsonObject value||value.Count!=1||value["input"] is not JsonValue input)continue;string name=input.GetValue<string>();var source=fn.Signature!.Args.SingleOrDefault(a=>a.Name==name&&!a.IsOut&&a.Mode is null);var parameter=node["signature"]!["args"]!.AsArray().SingleOrDefault(a=>a!["name"]!.ToString()==argument.Key&&a["mode"] is null);
     if(source is null||parameter?["type"]?.ToString()!=source.Type)continue;
     result.Add(id+"#"+node["id"]!.ToString()+"#"+argument.Key,new JsonObject{["graph"]=id,["node"]=node["id"]!.DeepClone(),["argument"]=argument.Key,["type"]=source.Type,["input"]=name,["hash"]=Hash(unit["draft"]!.ToString()),["before"]=value.ToJsonString()});if(result.Count>64)throw new ArgumentException("Input use selection budget");
    }
   }
  }
  return result;
 }
 public static JsonArray Detach(string id,string text,JsonObject graph,JsonObject units,FunctionSignature old,FunctionSignature next,JsonObject remap,JsonObject plans,HashSet<string> used)
 {
  var restorations=new JsonArray();string implementationId=id[..id.LastIndexOf("/body:",StringComparison.Ordinal)];var implementation=new Parser(units[implementationId]!["draft"]!.ToString(),"<input-use-implementation>").ParseElement();
  foreach(var pair in plans){var p=pair.Value!.AsObject();if(p["graph"]?.ToString()!=id)continue;
   if(pair.Key!=id+"#"+p["node"]?.ToString()+"#"+p["argument"]?.ToString()||p.Count!=6||p.Any(v=>v.Key is not ("graph" or "node" or "argument" or "hash" or "before" or "value"))||p["hash"]?.ToString()!=Hash(text))throw new InvalidOperationException("Exact original callee binding required; all input retained");
   string nodeId=p["node"]!.GetValue<string>(),arg=p["argument"]!.GetValue<string>();var node=graph["nodes"]!.AsArray().SingleOrDefault(n=>n!["id"]?.ToString()==nodeId) as JsonObject;var parameter=node?["signature"]?["args"]?.AsArray().SingleOrDefault(a=>a!["name"]?.ToString()==arg);
   var binding=node?["arguments"]?[arg] as JsonObject;
   if(node is null||(node["kind"]?.ToString()!="code"&&!SupportedCall(node,graph["feature"]!.ToString(),implementation,units))||node["control"]?.ToString()!="next"||node["implementationContext"] is not null||node["forwardCallerStorage"]?.GetValue<bool>()==true||parameter is null||parameter["mode"] is not null||binding is null||binding.Count!=1||binding["input"] is null||p["before"]?.GetValue<string>()!=binding.ToJsonString())throw new InvalidOperationException("Only the exact ordinary code/call input binding may be replaced");
   string source=binding["input"]!.GetValue<string>(),type=parameter["type"]!.ToString();if(!old.Args.Any(a=>a.Name==source&&a.Type==type&&a.Mode is null)||!remap.ContainsKey(source)||remap[source] is not null)throw new InvalidOperationException("Select the removed or replaced original value input explicitly");
   var choice=p["value"]!.AsObject();JsonObject replacement;
   if(choice.Count==1&&choice["input"] is JsonValue selected&&selected.TryGetValue<string>(out string? name)&&next.Args.Any(a=>a.Name==name&&a.Type==type&&a.Mode is null))replacement=new JsonObject{["input"]=name};
   else if(choice.Count==1&&choice["valueJson"] is JsonValue literal&&literal.TryGetValue<string>(out var json)&&json.Length<=65536){using var parsed=System.Text.Json.JsonDocument.Parse(json);replacement=new JsonObject{["constant"]=JsonNode.Parse(parsed.RootElement.GetRawText())};}
   else throw new InvalidOperationException("An exact compatible current input or explicit value is required; no conversion inferred");
   node["arguments"]![arg]=null;restorations.Add(new JsonObject{["node"]=nodeId,["argument"]=arg,["value"]=replacement});if(!used.Add(pair.Key))throw new ArgumentException("Duplicate callee binding selection");
  }
  return restorations;
 }
 public static void Restore(JsonObject graph,JsonArray rows)
 {
  foreach(var row in rows){var node=graph["nodes"]!.AsArray().Single(n=>n!["id"]?.ToString()==row!["node"]!.ToString())!;string name=row!["argument"]!.ToString();if(node["arguments"]![name] is not null)throw new InvalidOperationException("Selected callee input changed during preparation");node["arguments"]![name]=row["value"]!.DeepClone();}
 }
}
