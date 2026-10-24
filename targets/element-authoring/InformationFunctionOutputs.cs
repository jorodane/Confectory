using Confectory.Core;
using System.Text.Json.Nodes;

// Read-only output assignments, then an exact selected replacement inside the
// existing owned-function candidate. Neither operation writes or executes code.
internal static class InformationFunctionOutputs
{
 internal static string Hash(string text)=>JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(text));
 public static JsonObject Read(JsonObject request)
 {
  string owner=request["id"]!.ToString(),id=request["function"]!.ToString(),ns=PackPaths.Namespace(owner);var units=request["units"]!.AsObject();
  var schema=new Parser(units[owner]!["draft"]!.ToString(),"<output-owner>").ParseElement();
  if(schema.Kind!="schema"||!schema.Contains.Any(c=>c.Id==id&&c.Kind=="function")||!id.StartsWith(owner+"_Function_",StringComparison.Ordinal))throw new InvalidOperationException("Direct owned information function required");
  var function=new Parser(units[id]!["draft"]!.ToString(),"<output-contract>").ParseElement();var result=new JsonObject();
  foreach(var unit in units){if(unit.Value?["kind"]?.ToString()!="implementation")continue;var d=new Parser(unit.Value["draft"]!.ToString(),"<output-implementation>").ParseElement();if(d.Function!=id)continue;
   if(!d.Id.StartsWith(ns+"::",StringComparison.Ordinal)||d.Parent is not null||d.Bodies.Count is <1 or >8)throw new InvalidOperationException("Direct owned output implementation required");
   foreach(var body in d.Bodies){if(body.Value.SourceKind!="blueprint")continue;string graphId=d.Id+"/body:"+body.Key,text=units[graphId]!["draft"]!.ToString();var graph=JsonNode.Parse(text)!.AsObject();
    foreach(var output in FeatureBlueprint.FeatureOutputs(function.Signature!)){var writers=graph["nodes"]!.AsArray().Where(n=>n!["kind"]?.ToString()=="export"&&n["output"]?.ToString()==output.Name).ToArray();if(writers.Length>1||writers.Length==1&&graph["exits"]?[output.Name] is not null)continue;
     string node=writers.Length==0?"$exit:"+output.Name:writers[0]!["id"]!.ToString();var value=writers.Length==0?graph["exits"]?[output.Name]:writers[0]!["arguments"]?["value"];
     result.Add(graphId+"#"+output.Name,new JsonObject{["graph"]=graphId,["node"]=node,["name"]=output.Name,["type"]=output.Type,["hash"]=Hash(text),["before"]=value?.ToJsonString()??"null",["inputs"]=FeatureBlueprint.SignatureDocument(function.Signature!)["args"]!.DeepClone()});if(result.Count>64)throw new ArgumentException("Output assignment budget");
    }
   }
  }
  return result;
 }
 public static JsonObject Plan(string id,string text,JsonObject graph,FunctionSignature old,FunctionSignature next,JsonObject plans,HashSet<string> used)
 {
  var plan=new JsonObject{["args"]=FeatureBlueprint.SignatureDocument(next)["args"]!.DeepClone(),["returnType"]=next.Return};
  var before=FeatureBlueprint.FeatureOutputs(old).ToArray();var after=FeatureBlueprint.FeatureOutputs(next).ToArray();var changed=before.Where(p=>after.Any(q=>q.Name==p.Name&&q.Type!=p.Type)).ToArray();
  if(changed.Length==0)return plan;
  if(changed.Length!=1||before.Length!=after.Length||old.Args.Count!=next.Args.Count||old.Args.Where((p,i)=>p.Name!=next.Args[i].Name||p.Mode!=next.Args[i].Mode||p.Type!=next.Args[i].Type&&(!p.IsOut||p.Name!=changed[0].Name)).Any())throw new InvalidOperationException("Select one existing output type; keep all other root identities and roles");
  string name=changed[0].Name,to=after.Single(p=>p.Name==name).Type,key=id+"#"+name;var selected=plans[key]?.AsObject()??throw new InvalidOperationException("Select the changed output assignment explicitly; all input retained");
  if(selected.Count!=7||selected.Any(p=>p.Key is not ("graph" or "node" or "name" or "type" or "hash" or "before" or "source"))||selected["graph"]?.ToString()!=id||selected["name"]?.ToString()!=name||selected["type"]?.ToString()!=to||selected["hash"]?.ToString()!=Hash(text))throw new InvalidOperationException("Output assignment source changed; all input retained");
  string node=selected["node"]!.GetValue<string>();var writer=graph["nodes"]!.AsArray().SingleOrDefault(n=>n!["id"]?.ToString()==node);var value=node=="$exit:"+name?graph["exits"]?[name]:writer?["kind"]?.ToString()=="export"&&writer["output"]?.ToString()==name?writer["arguments"]?["value"]:throw new InvalidOperationException("Exact original output assignment required");
  if(selected["before"]?.ToString()!=(value?.ToJsonString()??"null"))throw new InvalidOperationException("Original output binding changed; all input retained");
  var source=selected["source"]?.AsObject();if(source is null||source.Count!=1||source["input"] is not JsonValue input||!input.TryGetValue<string>(out var inputName)||!next.Args.Any(p=>!p.IsOut&&p.Name==inputName&&p.Type==to))throw new InvalidOperationException("Select an exact typed current root input for this output");
  plan["adaptOutput"]=new JsonObject{["node"]=node,["name"]=name,["type"]=to,["path"]=new JsonArray(),["baseJson"]=selected["before"]!.DeepClone(),["sourceJson"]=source.ToJsonString()};used.Add(key);return plan;
 }
}
