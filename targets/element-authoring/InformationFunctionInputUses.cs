using Confectory.Core;
using System.Text.Json.Nodes;

// Explicit ordinary value bindings only. Code parameter contracts and C# sources
// are never rewritten. The owner transaction validates and saves the full closure.
internal static class InformationFunctionInputUses
{
 static string Hash(string text)=>JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(text));
 // Calls retain their exact owned callee/import and immutable branch/wrapper
 // contract. Only value arguments are selected; no ref/out or source rewriting.
 static bool SupportedCall(JsonObject node,string function,Element implementation,JsonObject units)
 {
  string? called=node["feature"]?.ToString();if(node["kind"]?.ToString()!="call"||called is null||called==function||!called.StartsWith(PackPaths.Namespace(function)+"::",StringComparison.Ordinal)||units[called]?["kind"]?.ToString()!="function")return false;
  var target=new Parser(units[called]!["draft"]!.ToString(),"<input-use-callee>").ParseElement();var imports=implementation.Imports.Values.Where(i=>i.Id==called).ToArray();
  if(target.Id!=called||target.Parent is not null||target.Signature is null||imports.Length!=1||!imports[0].Signature.Matches(target.Signature)||!JsonNode.DeepEquals(node["signature"],FeatureBlueprint.SignatureDocument(target.Signature)))return false;
  string? control=node["control"]?.ToString();if(control is not ("next" or "branch" or "switch"))return false;
  if(node["postCall"] is not JsonObject post)return control!="switch"&&!node.ContainsKey("postCall");
  if(post.Any(p=>p.Key is not ("contractHash" or "source" or "helpers" or "mode" or "returnMapping"))||post["contractHash"] is not JsonValue expected||post["source"] is not JsonValue code||!expected.TryGetValue<string>(out var hash)||!code.TryGetValue<string>(out var source)||post.ContainsKey("helpers")&&post["helpers"] is not JsonValue)return false;
  try{if(control=="next"&&!post.ContainsKey("mode")&&!post.ContainsKey("returnMapping"))BlueprintCallAfter.Prepare(target,hash,source,post["helpers"]?.GetValue<string>()??"");
   else if(control=="switch"&&post["mode"]?.ToString()=="execution-enum"&&node["executionEnum"] is JsonObject execution)BlueprintCallWrapper.Prepare(target,execution,hash,source,post["helpers"]?.GetValue<string>()??"",post["returnMapping"]?.GetValue<string>());
   else return false;
  }catch(ArgumentException){return false;}catch(InvalidOperationException){return false;}
  return true;
 }
 // Enumerate semantic binding positions, never arbitrary JSON strings or literal
 // data. Replacing an expression is an explicit replacement of its whole value.
 sealed record Use(string Node,string Argument,string Type,JsonObject Container,string Property,bool Storage,string Label,bool InputOnly=false);
 static string[] Inputs(JsonNode? value,int depth=0)
 {
  if(depth>12)throw new ArgumentException("Input expression budget");
  if(value is not JsonObject binding)return [];
  if(binding.Count==1&&binding["input"] is JsonValue input)return [input.GetValue<string>()];
  if(binding.Count==1&&binding["binary"] is JsonObject binary&&binary["operands"] is JsonArray operands)return operands.SelectMany(v=>Inputs(v,depth+1)).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal).ToArray();
  return [];
 }
 static IEnumerable<Use> Uses(JsonObject graph,Element implementation,JsonObject units,FunctionSignature signature)
 {
  foreach(var item in graph["nodes"]!.AsArray()){
   var node=item!.AsObject();if(!(node["kind"]?.ToString() is "code" or "graph" or "set" or "export" or "property" or "property-set" or "property-ref"||SupportedCall(node,graph["feature"]!.ToString(),implementation,units))||node["control"]?.ToString() is not ("next" or "branch" or "switch")||node["implementationContext"] is not null||node["forwardCallerStorage"]?.GetValue<bool>()==true)continue;
   foreach(var argument in node["arguments"]!.AsObject()){
    var parameter=node["signature"]!["args"]!.AsArray().SingleOrDefault(a=>a!["name"]?.ToString()==argument.Key&&a["mode"]?.ToString()!="out");if(parameter is not null)yield return new(node["id"]!.ToString(),argument.Key,parameter["type"]!.ToString(),node["arguments"]!.AsObject(),argument.Key,parameter["mode"]?.ToString()=="ref",node["id"]!.ToString()+" · "+argument.Key,FeatureBlueprint.IsPropertyNode(node["kind"]?.ToString())&&parameter["type"]!.ToString()=="object");
   }
  }
  foreach(var item in graph["locals"]?.AsArray()??new JsonArray())if(item!["source"] is JsonObject source&&source.Count==1&&source["input"] is JsonValue)yield return new("$alias:"+item["id"]!.ToString(),"source",item["type"]!.ToString(),item.AsObject(),"source",true,"별칭 · "+item["name"]!.ToString());
  foreach(var output in graph["exits"]!.AsObject())if(output.Value is not null){var type=FeatureBlueprint.FeatureOutputs(signature).SingleOrDefault(p=>p.Name==output.Key)?.Type;if(type is not null)yield return new("$exit:"+output.Key,"value",type,graph["exits"]!.AsObject(),output.Key,false,"종료 · "+(output.Key=="return"?"반환값":output.Key));}
 }
 public static JsonObject Read(JsonObject request)
 {
  string owner=request["id"]!.ToString(),function=request["function"]!.ToString(),ns=PackPaths.Namespace(owner);var units=request["units"]!.AsObject();
  var schema=new Parser(units[owner]!["draft"]!.ToString(),"<input-use-owner>").ParseElement();
  if(units.Count>2048||schema.Kind!="schema"||!schema.Contains.Any(c=>c.Id==function&&c.Kind=="function")||!function.StartsWith(owner+"_Function_",StringComparison.Ordinal))throw new InvalidOperationException("Direct owned function input uses required");
  var fn=new Parser(units[function]!["draft"]!.ToString(),"<input-use-function>").ParseElement();var result=new JsonObject();
  foreach(var entry in units){if(entry.Value?["kind"]?.ToString()!="implementation")continue;var impl=new Parser(entry.Value["draft"]!.ToString(),"<input-use-implementation>").ParseElement();if(impl.Function!=function)continue;
   if(!entry.Key.StartsWith(ns+"::",StringComparison.Ordinal)||impl.Id!=entry.Key||impl.Parent is not null||impl.Bodies.Count is <1 or >8)throw new InvalidOperationException("Direct owned implementation and all targets required");
   foreach(var body in impl.Bodies){if(body.Value.SourceKind!="blueprint")continue;string id=impl.Id+"/body:"+body.Key;var unit=units[id]??throw new InvalidOperationException("Original input-use graph missing");var g=JsonNode.Parse(unit["draft"]!.ToString())!.AsObject();
    string? contracts=null;
    if(g["nodes"]!.AsArray().Any(n=>FeatureBlueprint.IsPropertyNode(n!["kind"]?.ToString()))){int bytes=0;var seen=new Dictionary<string,string>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);void Observe(string path){var info=new FileInfo(path);if(!info.Exists||info.Length>1048576)throw new ArgumentException("Bounded property source required");string text=File.ReadAllText(path),hash=Hash(text);if(seen.TryGetValue(path,out var before)){if(hash!=before)throw new InvalidOperationException("Property input dependencies changed");}else{seen[path]=hash;bytes=checked(bytes+System.Text.Encoding.UTF8.GetByteCount(text));if(seen.Count>256||bytes>2097152)throw new ArgumentException("Property input dependency budget");}}contracts=new InformationFunctionProperties(request,Observe).ForGraph(impl,g).Proof;}
    foreach(var use in Uses(g,impl,units,fn.Signature!)){
     var value=use.Container[use.Property];var names=Inputs(value);if(names.Length==0||names.Any(name=>!fn.Signature!.Args.Any(a=>a.Name==name&&!a.IsOut)))continue;
     var entryUse=new JsonObject{["graph"]=id,["node"]=use.Node,["argument"]=use.Argument,["type"]=use.Type,["input"]=names[0],["inputs"]=new JsonArray(names.Select(n=>JsonValue.Create(n)).ToArray()),["storageOnly"]=use.Storage,["inputOnly"]=use.InputOnly,["label"]=use.Label,["hash"]=Hash(unit["draft"]!.ToString()),["before"]=value!.ToJsonString()};if(contracts is not null)entryUse["contracts"]=contracts;result.Add(id+"#"+use.Node+"#"+use.Argument,entryUse);if(result.Count>64)throw new ArgumentException("Input use selection budget");
    }
   }
  }
  return result;
 }
 public static JsonArray Detach(string id,string text,JsonObject graph,JsonObject units,FunctionSignature old,FunctionSignature next,JsonObject remap,JsonObject plans,HashSet<string> used,string? contracts=null,IReadOnlySet<string>? replacedOutputs=null)
 {
  var restorations=new JsonArray();string implementationId=id[..id.LastIndexOf("/body:",StringComparison.Ordinal)];var implementation=new Parser(units[implementationId]!["draft"]!.ToString(),"<input-use-implementation>").ParseElement();var sites=Uses(graph,implementation,units,old).Where(u=>replacedOutputs?.Contains(u.Node+"#"+u.Argument)!=true).ToDictionary(u=>id+"#"+u.Node+"#"+u.Argument,StringComparer.Ordinal);
  foreach(var pair in plans){var p=pair.Value!.AsObject();if(p["graph"]?.ToString()!=id)continue;
   if(pair.Key!=id+"#"+p["node"]?.ToString()+"#"+p["argument"]?.ToString()||p.Count!=(contracts is null?6:7)||p["contracts"]?.ToString()!=contracts||p.Any(v=>v.Key is not ("graph" or "node" or "argument" or "hash" or "before" or "value" or "contracts"))||p["hash"]?.ToString()!=Hash(text)||!sites.TryGetValue(pair.Key,out var use))throw new InvalidOperationException("Exact original binding location required; all input retained");
   var binding=use.Container[use.Property];var names=Inputs(binding);
   if(binding is not JsonObject||p["before"]?.GetValue<string>()!=binding.ToJsonString()||names.Length==0||names.Any(name=>!old.Args.Any(a=>a.Name==name&&!a.IsOut))||!names.Any(name=>remap.ContainsKey(name)&&remap[name] is null))throw new InvalidOperationException("Select the whole original value or alias storage using the removed/replaced input explicitly");
   var choice=p["value"]!.AsObject();JsonObject replacement;
   if(choice.Count==1&&choice["input"] is JsonValue selected&&selected.TryGetValue<string>(out string? name)&&next.Args.Any(a=>a.Name==name&&a.Type==use.Type&&!a.IsOut))replacement=new JsonObject{["input"]=name};
   else if(!use.Storage&&!use.InputOnly&&choice.Count==1&&choice["valueJson"] is JsonValue literal&&literal.TryGetValue<string>(out var json)&&json.Length<=65536){using var parsed=System.Text.Json.JsonDocument.Parse(json);replacement=new JsonObject{["constant"]=JsonNode.Parse(parsed.RootElement.GetRawText())};}
   else throw new InvalidOperationException("An exact compatible current input storage or explicit value is required; aliases never become value copies");
   use.Container[use.Property]=null;restorations.Add(new JsonObject{["node"]=use.Node,["argument"]=use.Argument,["storage"]=use.Storage,["value"]=replacement});if(!used.Add(pair.Key))throw new ArgumentException("Duplicate binding selection");
  }
  return restorations;
 }
 public static void Restore(JsonObject graph,JsonArray rows,JsonObject? outputRemap=null)
 {
  foreach(var row in rows){string id=row!["node"]!.ToString(),arg=row["argument"]!.ToString(),name;JsonObject container;
   if(id.StartsWith("$alias:",StringComparison.Ordinal)){container=graph["locals"]!.AsArray().Single(v=>v!["id"]!.ToString()==id[7..])!.AsObject();name="source";}
   else if(id.StartsWith("$exit:",StringComparison.Ordinal)){container=graph["exits"]!.AsObject();string original=id[6..];name=original=="return"||outputRemap is null?original:outputRemap[original]?.GetValue<string>()??throw new InvalidOperationException("A removed output cannot restore an input binding");}
   else{container=graph["nodes"]!.AsArray().Single(n=>n!["id"]?.ToString()==id)!["arguments"]!.AsObject();name=arg;}
   if(!container.ContainsKey(name)||container[name] is not null)throw new InvalidOperationException("Selected binding changed during preparation");container[name]=row["value"]!.DeepClone();
  }
  foreach(var row in rows.Where(v=>v!["storage"]!.GetValue<bool>()&&v["node"]!.ToString().StartsWith("$alias:",StringComparison.Ordinal))){string id=row!["node"]!.ToString()[7..];var local=graph["locals"]!.AsArray().Single(v=>v!["id"]!.ToString()==id)!;if(graph["locals"]!.AsArray().Any(v=>v!["id"]!.ToString()!=id&&JsonNode.DeepEquals(v["source"],local["source"])))throw new InvalidOperationException("Selected storage already has an alias; preserve every existing name and use");}
 }
}
