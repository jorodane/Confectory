using Confectory.Core;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

// Private original serial authoring edits. Runs only on a new isolated copy candidate.
internal static class ImplementationCopyEdits
{
 public static HashSet<string> Apply(JsonObject graph,JsonArray records,JsonArray edits,Element copy,string implementation,FunctionSignature publicSignature)
 {
  if(edits.Count>128)throw new ArgumentException("Bounded private copy edits required");var unique=new HashSet<string>(StringComparer.Ordinal);var reapplied=new HashSet<string>(StringComparer.Ordinal);var nodes=graph["nodes"]!.AsArray();
  JsonNode Node(string id)=>nodes.SingleOrDefault(n=>n!["id"]!.ToString()==id)??throw new ArgumentException("Current copied node required");
  JsonNode? Input(JsonNode node,string name){if(node["kind"]?.ToString()!="export")return node["signature"]!["args"]!.AsArray().SingleOrDefault(a=>a!["name"]!.ToString()==name&&a["mode"]?.ToString()!="out");if(name!="value")return null;string output=node["output"]!.ToString(),type=output=="return"?publicSignature.Return:publicSignature.Args.Single(a=>a.Name==output&&a.IsOut).Type;if(type=="void")throw new ArgumentException("Declared copied output required");return new JsonObject{["name"]="value",["type"]=type};}
  bool Uses(JsonNode? value,string id){if(value is JsonObject obj){if(obj["node"]?.ToString()==id)return true;return obj.Any(p=>Uses(p.Value,id));}return value is JsonArray array&&array.Any(v=>Uses(v,id));}
  foreach(var edit in edits){string type=edit!["type"]!.GetValue<string>(),id=edit["node"]!.GetValue<string>(),text=edit["text"]!.GetValue<string>();if(text.Length>1048576||!unique.Add(id+"|"+type))throw new ArgumentException("Bounded distinct private edits required");}
  // Reuse the existing ordinary pin rules inside the exact selected frame.
  // Qualified identity never becomes a file path or a public override contract.
  var qualified=edits.Where(e=>e!["node"]!.ToString().Contains('/')).ToArray();
  foreach(var group in qualified.GroupBy(e=>e!["node"]!.ToString()[..e["node"]!.ToString().LastIndexOf('/')],StringComparer.Ordinal)){
   string path=group.Key;var frame=BlueprintTree.Select(graph,path);var localEdits=new JsonArray();
   bool Destination(string to)=>to.Length==0||frame["nodes"]!.AsArray().Any(n=>n!["id"]!.ToString()==to&&n["kind"]?.ToString()=="code"&&n["control"]?.ToString()=="next"&&n["implementationContext"] is null&&n["forwardCallerStorage"]?.GetValue<bool>()!=true&&n["branchOwner"] is null)||to.StartsWith("exit:",StringComparison.Ordinal)&&frame["exits"]!.AsObject().ContainsKey(to[5..]);
   foreach(var edit in group){string key=edit!["node"]!.ToString(),type=edit["type"]!.ToString(),local=key[(path.Length+1)..];var leaf=frame["nodes"]!.AsArray().SingleOrDefault(n=>n!["id"]!.ToString()==local);
    if((type is "entry" or "route")&&!Destination(edit["text"]!.GetValue<string>()))throw new ArgumentException("Same private frame serial destination required");
    if(type=="entry"&&local=="$entry"){var entryEdit=edit.DeepClone().AsObject();entryEdit["node"]=local;localEdits.Add(entryEdit);continue;}
    if(leaf is null)throw new ArgumentException("Exact copied private leaf required");
    if(leaf["kind"]?.ToString()!="code"||leaf["implementationContext"] is not null||type is not ("source" or "intent" or "parameters" or "route")&&!type.StartsWith("argument:",StringComparison.Ordinal)||(type is "parameters" or "route"||type.StartsWith("argument:",StringComparison.Ordinal))&&(leaf["control"]?.ToString()!="next"||leaf["forwardCallerStorage"]?.GetValue<bool>()==true))throw new InvalidOperationException("Ordinary private body/pins/value edits required; preserve public and caller-storage contracts");
    if(type=="route"&&leaf["branchOwner"] is not null)throw new InvalidOperationException("Preserve branch-owned private routes");
    var localEdit=edit.DeepClone().AsObject();localEdit["node"]=local;localEdits.Add(localEdit);
   }
   var rows=records.Where(row=>row!["id"]!.ToString().StartsWith(path+"/",StringComparison.Ordinal)&&!row["id"]!.ToString()[(path.Length+1)..].Contains('/')).ToArray();
   var localRecords=new JsonArray(rows.Select(row=>{var local=row!.DeepClone().AsObject();local["id"]=row["id"]!.ToString()[(path.Length+1)..];return (JsonNode)local;}).ToArray());
   var applied=Apply(frame,localRecords,localEdits,copy,implementation,publicSignature);
   foreach(var local in localRecords){var original=rows.Single(row=>row!["id"]!.ToString()==path+"/"+local!["id"]!.ToString());original!["record"]=local!["record"]!.DeepClone();}
   foreach(string id in applied)reapplied.Add(path+"/"+id);
  }
  edits=new JsonArray(edits.Where(e=>!e!["node"]!.ToString().Contains('/')).Select(e=>e!.DeepClone()).ToArray());
  // Membership is prepared before dependent input edits; IDs never become source paths.
  foreach(var edit in edits.Where(e=>e!["type"]!.ToString()=="create")){
   string id=edit!["node"]!.ToString();var definition=JsonNode.Parse(edit["text"]!.GetValue<string>())!.AsObject();if(!Regex.IsMatch(id,@"\A[A-Za-z_][A-Za-z_0-9.-]{0,127}\z")||nodes.Count>=64||nodes.Any(n=>n!["id"]!.ToString()==id)||definition["kind"]?.ToString()!="code"||definition["control"]?.ToString()!="next"||definition.Any(p=>p.Key is not ("kind" or "intent" or "control" or "signature")))throw new ArgumentException("Unique original serial code node definition required");
   string path="nodes/"+implementation[(implementation.IndexOf("::",StringComparison.Ordinal)+2)..]+"."+JsonData.Digest(id)[..12]+".node.json";
   nodes.Add(new JsonObject{["id"]=id,["kind"]="code",["control"]="next",["intent"]=definition["intent"]!.DeepClone(),["signature"]=definition["signature"]!.DeepClone(),["arguments"]=new JsonObject(),["implementation"]=path});records.Add(new JsonObject{["id"]=id,["relative"]=path,["record"]=new JsonObject{["schema"]=1,["node"]=id,["definitionHash"]=new string('0',64),["source"]=""}});
  }
  // A dropped pin may have an explicit disconnect in this same private transaction.
  // Apply only declared, ordinary null disconnects before remapping; never infer one.
  foreach(var edit in edits.Where(e=>e!["type"]!.ToString().StartsWith("argument:",StringComparison.Ordinal))){if(JsonNode.Parse(edit!["text"]!.GetValue<string>()) is not null)continue;string id=edit["node"]!.ToString(),name=edit["type"]!.ToString()[9..];var node=Node(id);var argument=Input(node,name);if(argument is null||argument["mode"]?.ToString()=="ref"||node["forwardCallerStorage"]?.GetValue<bool>()==true)throw new InvalidOperationException("Declared ordinary copy pin required for explicit disconnect");node["arguments"]??=new JsonObject();node["arguments"]![name]=null;}
  foreach(var edit in edits.Where(e=>e!["type"]!.ToString()=="parameters"))Parameters(graph,Node(edit!["node"]!.ToString()),JsonNode.Parse(edit["text"]!.GetValue<string>())!.AsObject());
  foreach(var edit in edits){string type=edit!["type"]!.ToString(),id=edit["node"]!.ToString(),text=edit["text"]!.GetValue<string>();
   if(type is "create" or "parameters" or "remove")continue;
   if(type=="implementation-description"&&id=="$implementation"){if(text.Length>16384)throw new ArgumentException("Description budget");copy.Description=text;copy.DescriptionPresent=true;continue;}
   if(type=="entry"&&id=="$entry"){if(text.Length>0&&!nodes.Any(n=>n!["id"]!.ToString()==text)&&!(text.StartsWith("exit:",StringComparison.Ordinal)&&graph["exits"]!.AsObject().ContainsKey(text[5..])))throw new ArgumentException("Declared copied entry required");graph["entry"]=text;continue;}
   if(type=="exit"&&id.StartsWith("$exit:",StringComparison.Ordinal)&&graph["exits"]!.AsObject().ContainsKey(id[6..])){graph["exits"]![id[6..]]=JsonNode.Parse(text);continue;}
   var node=Node(id);
   if(type=="wrapper"&&node["kind"]?.ToString()=="call"&&node["control"]?.ToString()=="switch"&&node["postCall"]?["mode"]?.ToString()=="execution-enum"){
    var plan=JsonNode.Parse(text)!.AsObject();var post=node["postCall"]!;
    if(plan.Any(p=>p.Key is not ("source" or "helpers" or "executionEnum" or "contractHash" or "returnMapping"))||plan["contractHash"]?.ToString()!=post["contractHash"]?.ToString()||plan["returnMapping"]?.ToString()!=post["returnMapping"]?.ToString()||plan["source"] is not JsonValue||plan["executionEnum"] is not JsonObject)throw new InvalidOperationException("Exact current copy wrapper contract required; stale ABI needs its separate plan");
    string source=plan["source"]!.GetValue<string>(),helpers=plan["helpers"]?.GetValue<string>()??"";if(source.Length>65536||helpers.Length>65536)throw new ArgumentException("Copied wrapper source budget");post["source"]=source;post["helpers"]=helpers;node["executionEnum"]=plan["executionEnum"]!.DeepClone();
   }
   else if(type=="source"&&node["kind"]!.ToString()=="code"){records.Single(n=>n!["id"]!.ToString()==id)!["record"]!["source"]=text;reapplied.Add(id);}
   else if(type=="intent"&&node["kind"]!.ToString()=="code"){if(text.Length>16384)throw new ArgumentException("Intent budget");node["intent"]=text;}
   else if(type=="rename"&&node["implementationContext"] is null&&node["kind"]!.ToString()=="code"){if(text.Length is <1 or >256||text!=text.Trim()||text.Any(char.IsControl))throw new ArgumentException("Trimmed copied display name required");node["displayName"]=text;}
   else if(type.StartsWith("argument:",StringComparison.Ordinal)){
    string name=type[9..];var argument=Input(node,name);if(argument is null){var remapEdit=edits.SingleOrDefault(e=>e!["type"]!.ToString()=="parameters"&&e["node"]!.ToString()==id);var remap=remapEdit is null?null:JsonNode.Parse(remapEdit["text"]!.GetValue<string>())!["remap"]?.AsObject();if(JsonNode.Parse(text) is null&&remap?.ContainsKey(name)==true&&remap[name] is null)continue;throw new ArgumentException("Declared copy input required");}if(argument["mode"]?.ToString()=="ref"||node["forwardCallerStorage"]?.GetValue<bool>()==true)throw new InvalidOperationException("Preserve caller-storage bindings; their external contract is not a private value edit");node["arguments"]??=new JsonObject();node["arguments"]![name]=JsonNode.Parse(text);
   }else if(type=="route"&&node["control"]!.ToString()=="next"){
    if(text.Length>0&&!nodes.Any(n=>n!["id"]!.ToString()==text)&&!(text.StartsWith("exit:",StringComparison.Ordinal)&&graph["exits"]!.AsObject().ContainsKey(text[5..])))throw new ArgumentException("Declared serial copy route required");var edges=graph["edges"]!.AsArray();foreach(var edge in edges.Where(e=>e!["from"]!.ToString()==id&&e["port"]!.ToString()=="next").ToArray())edges.Remove(edge);if(text.Length>0)edges.Add(new JsonObject{["from"]=id,["port"]="next",["to"]=text});
   }else throw new ArgumentException("This private copy edit is not connected; inputs retained");
  }
  foreach(var edit in edits.Where(e=>e!["type"]!.ToString()=="remove")){
   string id=edit!["node"]!.ToString();var node=Node(id);if(graph["entry"]?.ToString()==id||graph["edges"]!.AsArray().Any(e=>e!["from"]!.ToString()==id||e["to"]!.ToString()==id)||Uses(graph["exits"],id)||Uses(graph["locals"],id)||nodes.Any(n=>n!["id"]!.ToString()!=id&&Uses(n["arguments"],id)))throw new InvalidOperationException("Disconnect every copied node route/value before removal");nodes.Remove(node);foreach(var record in records.Where(n=>n!["id"]!.ToString()==id).ToArray())records.Remove(record);
  }
  return reapplied;
 }
 static void Parameters(JsonObject graph,JsonNode node,JsonObject plan)
 {
  if(node["kind"]?.ToString()!="code"||node["implementationContext"] is not null||node["forwardCallerStorage"]?.GetValue<bool>()==true)throw new InvalidOperationException("Only ordinary copied static node contracts are editable");
  var old=node["signature"]!.AsObject();var previous=old["args"]!.AsArray();var args=plan["args"]!.AsArray();var remap=plan["remap"]!.AsObject();if(args.Count>64||remap.Count!=previous.Count||previous.Any(a=>!remap.ContainsKey(a!["name"]!.ToString())))throw new ArgumentException("Explicit copy remap for each previous argument required");
  var names=new HashSet<string>(StringComparer.Ordinal);foreach(var arg in args){if(arg is not JsonObject obj||obj.Any(p=>p.Key is not ("name" or "type" or "mode"))||!names.Add(obj["name"]!.GetValue<string>()))throw new ArgumentException("Distinct typed copied parameters required");}
  var used=new HashSet<string>(StringComparer.Ordinal);var bindings=new JsonObject();foreach(var arg in args.Where(a=>a!["mode"]?.ToString()!="out"))bindings[arg!["name"]!.ToString()]=null;
  foreach(var arg in previous){string before=arg!["name"]!.ToString();var selected=remap[before];if(selected is null){if(arg["mode"]?.ToString()!="out"&&node["arguments"]?[before] is not null)throw new InvalidOperationException("Disconnect old copy input before dropping/changing its type");continue;}string after=selected.GetValue<string>();var target=args.SingleOrDefault(a=>a!["name"]!.ToString()==after);if(target is null||!used.Add(after)||target["type"]!.ToString()!=arg["type"]!.ToString()||target["mode"]?.ToString()!=arg["mode"]?.ToString())throw new ArgumentException("A copied pin remap must preserve exact type and mode");if(arg["mode"]?.ToString()!="out")bindings[after]=node["arguments"]?[before]?.DeepClone();}
  void Remap(JsonNode? value){if(value is JsonObject obj){if(obj["node"]?.ToString()==node["id"]!.ToString()){string output=obj["output"]?.ToString()??"return";if(output!="return"){if(!remap.ContainsKey(output)||remap[output] is null)throw new InvalidOperationException("Disconnect all copied output users before removing it");obj["output"]=remap[output]!.DeepClone();}return;}foreach(var pair in obj)Remap(pair.Value);}else if(value is JsonArray array)foreach(var item in array)Remap(item);}
  foreach(var other in graph["nodes"]!.AsArray())Remap(other!["arguments"]);Remap(graph["exits"]);Remap(graph["locals"]);
  string returns=plan["returnType"]!.GetValue<string>();if(returns!=old["return"]!.ToString()){
   bool Uses(JsonNode? value){if(value is JsonObject obj){if(obj["node"]?.ToString()==node["id"]!.ToString()&&(obj["output"]?.ToString()??"return")=="return")return true;return obj.Any(p=>Uses(p.Value));}return value is JsonArray array&&array.Any(Uses);}
   if(Uses(graph["exits"])||Uses(graph["locals"])||graph["nodes"]!.AsArray().Any(n=>n!["id"]!.ToString()!=node["id"]!.ToString()&&Uses(n["arguments"])))throw new InvalidOperationException("Disconnect every copied return user before changing type");
  }
  if(args.Any(a=>a!["mode"]?.ToString()=="out")&&graph["profile"]?.ToString() is FeatureBlueprint.Profile or FeatureBlueprint.ImplicitProfile)graph["profile"]=FeatureBlueprint.MultiOutputProfile;
  node["signature"]=new JsonObject{["args"]=args.DeepClone(),["return"]=returns};node["arguments"]=bindings;
 }
}
