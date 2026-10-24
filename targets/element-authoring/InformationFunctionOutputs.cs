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
    foreach(var output in FeatureBlueprint.FeatureOutputs(function.Signature!)){var writers=BlueprintOutputBindings.Writers(graph,output.Name).ToArray();foreach(var writer in writers){string key=graphId+"#"+output.Name+(writers.Length==1?"":"@"+writer.Node);result.Add(key,new JsonObject{["graph"]=graphId,["node"]=writer.Node,["name"]=output.Name,["type"]=output.Type,["hash"]=Hash(text),["before"]=writer.Value?.ToJsonString()??"null",["inputs"]=FeatureBlueprint.SignatureDocument(function.Signature!)["args"]!.DeepClone()});if(result.Count>512)throw new ArgumentException("Output assignment budget");}}

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
    result.Add(graphId,new JsonObject{["graph"]=graphId,["hash"]=Hash(text),["entry"]=graph["entry"]!.DeepClone(),["edges"]=graph["edges"]!.DeepClone(),["exits"]=new JsonObject(graph["exits"]!.AsObject().Select(p=>KeyValuePair.Create<string,JsonNode?>(p.Key,JsonValue.Create(p.Value?.ToJsonString()??"null")))),["writers"]=writers,["nodes"]=new JsonArray(graph["nodes"]!.AsArray().Select(n=>(JsonNode)new JsonObject{["id"]=n!["id"]!.DeepClone(),["kind"]=n["kind"]!.DeepClone(),["control"]=n["control"]!.DeepClone(),["label"]=n["intent"]?.DeepClone()??n["id"]!.DeepClone()}).ToArray()),["publicOutputs"]=new JsonArray(BlueprintOutputSnapshot.Read(function).Select(n=>JsonValue.Create(n)).ToArray()),["sources"]=Sources(graph,function.Signature!)});if(result.Count>64)throw new ArgumentException("Output graph budget");
   }
  }
  return result;
 }
 static JsonArray Sources(JsonObject graph,FunctionSignature signature)
 {
  var sources=new JsonArray();void Add(string key,string label,string type,JsonObject value){sources.Add(new JsonObject{["key"]=key,["label"]=label,["type"]=type,["source"]=value});if(sources.Count>512)throw new ArgumentException("Output source catalogue budget");}
  foreach(var arg in signature.Args.Where(a=>!a.IsOut))Add(arg.Name,arg.Name,arg.Type,new JsonObject{["input"]=arg.Name});
  foreach(var node in graph["nodes"]!.AsArray().OfType<JsonObject>())foreach(var output in BlueprintOutputBindings.Outputs(node)){string id=node["id"]!.ToString();Add("$node:"+id+"#"+output.Name,"노드 "+(node["displayName"]?.ToString()??node["intent"]?.ToString()??id)+" · "+output.Name,output.Type,new JsonObject{["node"]=id,["output"]=output.Name});}
  foreach(var local in (graph["locals"] as JsonArray??new()).OfType<JsonObject>()){string id=local["id"]!.ToString();Add("$local:"+id,"지역값 "+local["name"]!.ToString(),local["type"]!.ToString(),new JsonObject{["local"]=id});}
  return sources;
 }
 static void Exact(JsonObject row,params string[] keys){if(row.Count!=keys.Length||row.Any(p=>!keys.Contains(p.Key,StringComparer.Ordinal)))throw new ArgumentException("Exact selected output graph required");}
 static JsonObject Structure(string id,string text,JsonObject graph,FunctionSignature old,FunctionSignature next,JsonObject remap,IReadOnlyList<string> published,JsonObject selected)
 {
  Exact(selected,"graph","hash","removes","creates","publicOutputs");if(selected["graph"]?.ToString()!=id||selected["hash"]?.ToString()!=Hash(text))throw new InvalidOperationException("Output graph changed; retain every input");
  var before=FeatureBlueprint.FeatureOutputs(old).ToDictionary(p=>p.Name,p=>p.Type,StringComparer.Ordinal);var after=FeatureBlueprint.FeatureOutputs(next).ToDictionary(p=>p.Name,p=>p.Type,StringComparer.Ordinal);
  string? Destination(string name)=>name=="return"?next.Return!="void"?"return":null:remap[name]?.GetValue<string>();
  var removed=before.Keys.Where(n=>Destination(n) is not string to||!after.ContainsKey(to)).ToHashSet(StringComparer.Ordinal);var retained=before.Keys.Where(n=>!removed.Contains(n)).Select(n=>Destination(n)!).ToHashSet(StringComparer.Ordinal);var added=after.Keys.Where(n=>!retained.Contains(n)).ToHashSet(StringComparer.Ordinal);
  if(removed.Count+added.Count==0||!old.Args.Where(a=>!a.IsOut).SequenceEqual(next.Args.Where(a=>!a.IsOut))||old.Args.Any(a=>!a.IsOut&&remap[a.Name]?.ToString()!=a.Name||a.IsOut&&removed.Contains(a.Name)&&remap[a.Name] is not null)||!old.Args.Where(a=>a.IsOut&&!removed.Contains(a.Name)).Select(a=>(Name:Destination(a.Name)!,a.Mode)).SequenceEqual(next.Args.Where(a=>a.IsOut&&!added.Contains(a.Name)).Select(a=>(a.Name,a.Mode))))throw new InvalidOperationException("Output definitions retain every other input, type, identity and role");
  var expectedPublic=new JsonArray(published.Select(Destination).Where(n=>n is not null&&after.ContainsKey(n)).Select(n=>JsonValue.Create(n)).ToArray());if(!JsonNode.DeepEquals(selected["publicOutputs"],expectedPublic))throw new InvalidOperationException("Remove only the explicitly deleted publication; no new public output is inferred");
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
  string MappedTarget(string target)=>target.StartsWith("exit:",StringComparison.Ordinal)?"exit:"+Destination(target[5..]):target;
  return new JsonObject{["args"]=FeatureBlueprint.SignatureDocument(next)["args"]!.DeepClone(),["returnType"]=next.Return,["removeOutputs"]=new JsonArray(removed.Select(n=>JsonValue.Create(n)).ToArray()),["outputCreates"]=creates,["outputRoutes"]=new JsonArray(routes.Where(p=>!unchangedRoutes.TryGetValue(p.Key,out var prior)||prior!=p.Value).Select(p=>(JsonNode)new JsonObject{["node"]=p.Key,["to"]=MappedTarget(p.Value)}).ToArray()),["outputEntry"]=MappedTarget(entry),["publicOutputs"]=expectedPublic};
 }
 public static JsonObject Plan(string id,string text,JsonObject graph,FunctionSignature old,FunctionSignature next,JsonObject plans,HashSet<string> used,JsonObject remap,IReadOnlyList<string> published,JsonObject graphPlans,HashSet<string> usedGraphs)
 {
  var plan=graphPlans[id] is JsonObject structureSelection?Structure(id,text,graph,old,next,remap,published,structureSelection):new JsonObject{["args"]=FeatureBlueprint.SignatureDocument(next)["args"]!.DeepClone(),["returnType"]=next.Return};if(graphPlans[id] is not null)usedGraphs.Add(id);
  var after=FeatureBlueprint.FeatureOutputs(next).ToDictionary(p=>p.Name,p=>p.Type,StringComparer.Ordinal);var bindings=new JsonArray();
  foreach(var output in FeatureBlueprint.FeatureOutputs(old)){string? to=output.Name=="return"?next.Return!="void"?"return":null:remap[output.Name]?.GetValue<string>();if(to is null||!after.TryGetValue(to,out var type)||output.Type==type)continue;
   var writers=BlueprintOutputBindings.Writers(graph,output.Name).ToArray();foreach(var writer in writers){string key=id+"#"+output.Name+(writers.Length==1?"":"@"+writer.Node);var selected=plans[key]?.AsObject()??throw new InvalidOperationException("Select every changed output writer and exit explicitly; all input retained");
    Exact(selected,"graph","node","name","type","hash","before","source");if(selected["graph"]?.ToString()!=id||selected["node"]?.ToString()!=writer.Node||selected["name"]?.ToString()!=output.Name||selected["type"]?.ToString()!=type||selected["hash"]?.ToString()!=Hash(text)||selected["before"]?.ToString()!=(writer.Value?.ToJsonString()??"null"))throw new InvalidOperationException("Output assignment source changed; all input retained");
    var source=selected["source"]!.AsObject();JsonNode? value;if(source.Count==1&&source["valueJson"] is JsonValue literal&&literal.TryGetValue<string>(out var raw)&&raw.Length<=65536){using var parsed=System.Text.Json.JsonDocument.Parse(raw);value=new JsonObject{["constant"]=JsonNode.Parse(parsed.RootElement.GetRawText())};}else value=source.DeepClone();BlueprintOutputBindings.Value(graph,next,value,type);bindings.Add(new JsonObject{["node"]=writer.Node,["name"]=output.Name,["type"]=type,["before"]=writer.Value?.ToJsonString()??"null",["valueJson"]=value!.ToJsonString()});used.Add(key);
   }
  }
  if(bindings.Count>0)plan["outputBindings"]=bindings;return plan;
 }
}
