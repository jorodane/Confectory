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
 public static JsonObject Graphs(JsonObject request)
 {
  string owner=request["id"]!.ToString(),id=request["function"]!.ToString(),ns=PackPaths.Namespace(owner);var units=request["units"]!.AsObject();var schema=new Parser(units[owner]!["draft"]!.ToString(),"<output-owner>").ParseElement();
  if(schema.Kind!="schema"||!schema.Contains.Any(c=>c.Id==id&&c.Kind=="function")||!id.StartsWith(owner+"_Function_",StringComparison.Ordinal))throw new InvalidOperationException("Direct owned information function required");
  var function=new Parser(units[id]!["draft"]!.ToString(),"<output-contract>").ParseElement();var result=new JsonObject();
  foreach(var unit in units){if(unit.Value?["kind"]?.ToString()!="implementation")continue;var d=new Parser(unit.Value["draft"]!.ToString(),"<output-implementation>").ParseElement();if(d.Function!=id)continue;
   if(!d.Id.StartsWith(ns+"::",StringComparison.Ordinal)||d.Parent is not null||d.Bodies.Count is <1 or >8)throw new InvalidOperationException("Direct owned output implementation required");
   foreach(var body in d.Bodies){if(body.Value.SourceKind!="blueprint")continue;string graphId=d.Id+"/body:"+body.Key,text=units[graphId]!["draft"]!.ToString();var graph=JsonNode.Parse(text)!.AsObject();var writers=new JsonObject();foreach(var output in FeatureBlueprint.FeatureOutputs(function.Signature!))writers[output.Name]=new JsonArray(graph["nodes"]!.AsArray().Where(n=>n!["kind"]?.ToString()=="export"&&n["output"]?.ToString()==output.Name).Select(n=>n!["id"]!.DeepClone()).ToArray());
    result.Add(graphId,new JsonObject{["graph"]=graphId,["hash"]=Hash(text),["entry"]=graph["entry"]!.DeepClone(),["edges"]=graph["edges"]!.DeepClone(),["exits"]=new JsonObject(graph["exits"]!.AsObject().Select(p=>KeyValuePair.Create<string,JsonNode?>(p.Key,JsonValue.Create(p.Value?.ToJsonString()??"null")))),["writers"]=writers,["nodes"]=new JsonArray(graph["nodes"]!.AsArray().Select(n=>(JsonNode)new JsonObject{["id"]=n!["id"]!.DeepClone(),["kind"]=n["kind"]!.DeepClone(),["control"]=n["control"]!.DeepClone(),["label"]=n["intent"]?.DeepClone()??n["id"]!.DeepClone()}).ToArray()),["publicOutputs"]=new JsonArray(BlueprintOutputSnapshot.Read(function).Select(n=>JsonValue.Create(n)).ToArray())});if(result.Count>64)throw new ArgumentException("Output graph budget");
   }
  }
  return result;
 }
 static void Exact(JsonObject row,params string[] keys){if(row.Count!=keys.Length||row.Any(p=>!keys.Contains(p.Key,StringComparer.Ordinal)))throw new ArgumentException("Exact selected output graph required");}
 static JsonObject Structure(string id,string text,JsonObject graph,FunctionSignature old,FunctionSignature next,JsonObject remap,IReadOnlyList<string> published,JsonObject selected)
 {
  Exact(selected,"graph","hash","removes","creates","publicOutputs");if(selected["graph"]?.ToString()!=id||selected["hash"]?.ToString()!=Hash(text))throw new InvalidOperationException("Output graph changed; retain every input");
  var before=FeatureBlueprint.FeatureOutputs(old).ToDictionary(p=>p.Name,p=>p.Type,StringComparer.Ordinal);var after=FeatureBlueprint.FeatureOutputs(next).ToDictionary(p=>p.Name,p=>p.Type,StringComparer.Ordinal);
  var removed=before.Keys.Where(n=>!after.ContainsKey(n)).ToHashSet(StringComparer.Ordinal);var added=after.Keys.Where(n=>!before.ContainsKey(n)).ToHashSet(StringComparer.Ordinal);
  if(removed.Count+added.Count==0||!old.Args.Where(a=>!a.IsOut).SequenceEqual(next.Args.Where(a=>!a.IsOut))||old.Args.Any(a=>remap[a.Name]?.ToString()!=(a.IsOut&&removed.Contains(a.Name)?null:a.Name))||before.Any(p=>after.TryGetValue(p.Key,out var type)&&type!=p.Value)||!old.Args.Where(a=>a.IsOut&&!removed.Contains(a.Name)).SequenceEqual(next.Args.Where(a=>a.IsOut&&!added.Contains(a.Name))))throw new InvalidOperationException("Output definitions retain every other input, type, identity and role");
  var expectedPublic=new JsonArray(published.Where(after.ContainsKey).Select(n=>JsonValue.Create(n)).ToArray());if(!JsonNode.DeepEquals(selected["publicOutputs"],expectedPublic))throw new InvalidOperationException("Remove only the explicitly deleted publication; no new public output is inferred");
  var nodes=graph["nodes"]!.AsArray();if(nodes.Any(n=>n!["control"]?.ToString()!="next"))throw new InvalidOperationException("Select the existing serial output graph; branch regions stay protected");
  var removeRows=selected["removes"]!.AsArray();var createRows=selected["creates"]!.AsArray();if(removeRows.Count!=removed.Count||createRows.Count!=added.Count||removeRows.Count>65||createRows.Count>65)throw new ArgumentException("Select every removed definition and every new assignment");
  var selectedRemovals=new HashSet<string>(StringComparer.Ordinal);foreach(var item in removeRows){var row=item!.AsObject();Exact(row,"name","writers","before");string name=row["name"]!.GetValue<string>();var writers=new JsonArray(nodes.Where(n=>n!["kind"]?.ToString()=="export"&&n["output"]?.ToString()==name).Select(n=>n!["id"]!.DeepClone()).ToArray());if(!removed.Contains(name)||!selectedRemovals.Add(name)||!JsonNode.DeepEquals(row["writers"],writers)||row["before"]?.ToString()!=(graph["exits"]?[name]?.ToJsonString()??"null"))throw new InvalidOperationException("Confirm every original output writer and exit before deleting its definition");}
  var deleted=nodes.Where(n=>n!["kind"]?.ToString()=="export"&&removed.Contains(n["output"]!.ToString())).Select(n=>n!["id"]!.ToString()).ToHashSet(StringComparer.Ordinal);var edges=graph["edges"]!.AsArray();
  string Resolve(string target){var seen=new HashSet<string>(StringComparer.Ordinal);while(deleted.Contains(target)){if(!seen.Add(target))throw new InvalidOperationException("Output removal encountered a cycle");string at=target;target=edges.SingleOrDefault(e=>e!["from"]!.ToString()==at&&e["port"]?.ToString()=="next")?["to"]?.ToString()??"";}return target.StartsWith("exit:",StringComparison.Ordinal)&&removed.Contains(target[5..])?"":target;}
  var ids=nodes.Where(n=>!deleted.Contains(n!["id"]!.ToString())).Select(n=>n!["id"]!.ToString()).ToHashSet(StringComparer.Ordinal);var originalIds=nodes.Select(n=>n!["id"]!.ToString()).ToHashSet(StringComparer.Ordinal);var routes=ids.ToDictionary(n=>n,n=>Resolve(edges.SingleOrDefault(e=>e!["from"]!.ToString()==n&&e["port"]?.ToString()=="next")?["to"]?.ToString()??""),StringComparer.Ordinal);string entry=Resolve(graph["entry"]!.ToString());
  var unchangedRoutes=new Dictionary<string,string>(routes,StringComparer.Ordinal);
  var creates=new JsonArray();var selectedAdds=new HashSet<string>(StringComparer.Ordinal);var positions=new HashSet<string>(StringComparer.Ordinal);
  foreach(var item in createRows){var row=item!.AsObject();Exact(row,"node","name","type","source","after","next");string node=row["node"]!.GetValue<string>(),name=row["name"]!.GetValue<string>(),previous=row["after"]!.GetValue<string>();
   if(!added.Contains(name)||!selectedAdds.Add(name)||row["type"]?.ToString()!=after[name]||originalIds.Contains(node)||!ids.Add(node)||node.Length>128||!System.Text.RegularExpressions.Regex.IsMatch(node,@"\A[A-Za-z_][A-Za-z_0-9.-]*\z")||!positions.Add(previous))throw new InvalidOperationException("Select one distinct assignment and insertion position per new output");
   string following=previous=="$entry"?entry:routes.GetValueOrDefault(previous)??throw new InvalidOperationException("Select a retained predecessor or an earlier new assignment");if(row["next"]?.ToString()!=following)throw new InvalidOperationException("The selected output insertion route changed");
   var reachable=new HashSet<string>(StringComparer.Ordinal);string at=entry;while(ids.Contains(at)&&reachable.Add(at))at=routes.GetValueOrDefault(at)??"";if(previous!="$entry"&&!reachable.Contains(previous))throw new InvalidOperationException("The new output must be on the retained execution path");
   var source=row["source"]!.AsObject();JsonNode? value;if(source.Count==1&&source["input"] is JsonValue input&&input.TryGetValue<string>(out var inputName)&&next.Args.Any(a=>!a.IsOut&&a.Name==inputName&&a.Type==after[name]))value=source.DeepClone();else if(source.Count==1&&source["valueJson"] is JsonValue literal&&literal.TryGetValue<string>(out var raw)&&raw.Length<=65536&&after[name] is "int" or "long" or "float" or "double" or "bool" or "string"){using var parsed=System.Text.Json.JsonDocument.Parse(raw);value=new JsonObject{["constant"]=JsonNode.Parse(parsed.RootElement.GetRawText())};}else throw new InvalidOperationException("Select the exact typed root input or an explicit scalar value for the new output");
   creates.Add(new JsonObject{["node"]=node,["output"]=name,["valueJson"]=value.ToJsonString()});routes[node]=following;if(previous=="$entry")entry=node;else routes[previous]=node;
  }
  return new JsonObject{["args"]=FeatureBlueprint.SignatureDocument(next)["args"]!.DeepClone(),["returnType"]=next.Return,["removeOutputs"]=new JsonArray(removed.Select(n=>JsonValue.Create(n)).ToArray()),["outputCreates"]=creates,["outputRoutes"]=new JsonArray(routes.Where(p=>!unchangedRoutes.TryGetValue(p.Key,out var prior)||prior!=p.Value).Select(p=>(JsonNode)new JsonObject{["node"]=p.Key,["to"]=p.Value}).ToArray()),["outputEntry"]=entry,["publicOutputs"]=expectedPublic};
 }
 public static JsonObject Plan(string id,string text,JsonObject graph,FunctionSignature old,FunctionSignature next,JsonObject plans,HashSet<string> used,JsonObject remap,IReadOnlyList<string> published,JsonObject graphPlans,HashSet<string> usedGraphs)
 {
  if(graphPlans[id] is JsonObject structureSelection){var structural=Structure(id,text,graph,old,next,remap,published,structureSelection);usedGraphs.Add(id);return structural;}
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
