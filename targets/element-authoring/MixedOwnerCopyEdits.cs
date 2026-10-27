using Confectory.Core;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

// The declaration half of one copy transaction. It never writes sources or
// edits an external schema, parent, imported implementation or external owner.
internal static class MixedOwnerCopyEdits
{
 static string Hash(string text)=>JsonData.HashBytes(Encoding.UTF8.GetBytes(text));
 static void Exact(JsonObject row,params string[] keys){if(row.Count!=keys.Length||row.Any(p=>!keys.Contains(p.Key,StringComparer.Ordinal)))throw new ArgumentException("Exact mixed declaration operation required");}
 static void Definition(JsonObject row,params string[] keys){Exact(row,row.ContainsKey("icon")?keys.Append("icon").ToArray():keys);if(row.ContainsKey("icon"))DeclarationAuthoring.Glyph(row["icon"]!.GetValue<string>(),true);}
 static JsonObject Shape(JsonNode field)=>new(){["kind"]=(field["kind"]??field["Kind"])!.DeepClone(),["cardinality"]=(field["cardinality"]??field["Cardinality"])!.DeepClone(),["type"]=(field["type"]??field["Type"])!.DeepClone()};
 internal static JsonObject Field(JsonObject model,JsonArray path)
 {
  if(path.Count is <1 or >64||path[0] is not JsonValue)throw new ArgumentException("Bounded typed path required");
  var field=model["fields"]?[path[0]!.GetValue<string>()]??throw new ArgumentException("Existing effective field required");var shape=Shape(field);
  foreach(var segment in path.Skip(1)){
   if(shape["cardinality"]!.ToString()=="multiple"){if(segment is not JsonValue index||!index.TryGetValue<int>(out int n)||n<0)throw new ArgumentException("Existing array position required");shape["cardinality"]="single";}
   else if(shape["kind"]!.ToString()=="compound"&&segment is JsonValue name&&name.TryGetValue<string>(out var key))shape=Shape(model["schemas"]?[shape["type"]!.ToString()]?["fields"]?[key]??throw new ArgumentException("Existing compound member required"));
   else throw new ArgumentException("Typed path cannot edit another referenced owner");
  }
  if(shape["kind"]!.ToString() is not ("general" or "compound" or "reference" or "function"))throw new ArgumentException("Supported typed value required");return shape;
 }
 public static JsonObject Prepare(JsonObject request,Func<Element,string> format,Func<Manifest,string> formatManifest)
 {
  string project=request["project"]!.GetValue<string>(),manifest=request["manifest"]!.GetValue<string>(),id=request["id"]!.GetValue<string>(),text=request["text"]!.GetValue<string>();var changes=request["changes"]!.AsArray();var element=new Parser(text,"<mixed-copy-owner>").ParseElement();var registration=new Parser(manifest,"<mixed-copy-registration>").ParseManifest();string ns=registration.Namespace;
  if(element.Kind!="object"||element.Id!=id||!id.StartsWith(ns+"::",StringComparison.Ordinal)||registration.Kind!="project"||changes.Count is <1 or >64)throw new ArgumentException("Bounded same-owner object changes required");
  var drafts=request["drafts"]!.AsArray();if(drafts.Count>255)throw new ArgumentException("Mixed source graph budget");
  string Read(string path){var file=new FileInfo(path);if(!file.Exists||file.Length>1048576)throw new IOException("Mixed declaration source budget");return File.ReadAllText(path);}
  JsonObject Inspect(string source,string currentManifest,JsonArray overlays,bool types=false)=>EffectiveMetadata.Query(project,currentManifest,id,source,formatManifest,Read,overlays,schemaView:true,validateObjects:true,observeSources:true,definitionTypes:types);
  void Valid(JsonObject result){if(result["status"]?.ToString()!="available"||result["schemaModel"]?["validation"]?["status"]?.ToString()!="valid")throw new InvalidOperationException("Mixed declaration/schema context invalid; retain all input");}
  var before=Inspect(text,manifest,drafts,changes.Any(c=>c?["type"]?.ToString()=="typed-definition"||c?["definition"] is not null));Valid(before);var seen=new HashSet<string>(StringComparer.Ordinal);var paths=new List<JsonArray>();var definitions=new JsonArray();var schemaChanges=new List<JsonObject>();
  void Unique(string value){if(!seen.Add(value))throw new ArgumentException("Duplicate mixed operation");}
  JsonArray Path(JsonObject row){var path=row["path"]!.AsArray();Field(before["schemaModel"]!.AsObject(),path);foreach(var prior in paths)if(prior.Take(Math.Min(prior.Count,path.Count)).Select(p=>p!.ToJsonString()).SequenceEqual(path.Take(Math.Min(prior.Count,path.Count)).Select(p=>p!.ToJsonString())))throw new ArgumentException("Overlapping typed operations require explicit reconciliation");paths.Add(path);return path;}
  foreach(var change in changes){
   var row=change!.AsObject();string type=row["type"]!.GetValue<string>();
   if(type=="description"){Exact(row,"type","text");Unique(type);string value=row["text"]!.GetValue<string>();if(value.Length>16384)throw new ArgumentException("Mixed description budget");element.Description=value;element.DescriptionPresent=true;}
   else if(type=="icon"){Exact(row,"type","text");Unique(type);DeclarationAuthoring.Icon(element,row["text"]!.GetValue<string>());}
   else if(type is "scalar" or "data" or "unset"){
    Exact(row,type=="scalar"?new[]{"type","path","nativeType","valueJson"}:type=="data"?new[]{"type","path","contract","valueJson"}:new[]{"type","path","contract"});var path=Path(row);var shape=Field(before["schemaModel"]!.AsObject(),path);
    if(type=="scalar"){if(path.Count!=1||shape["kind"]!.ToString()!="general"||shape["cardinality"]!.ToString()!="single"||shape["type"]!.ToString() is not ("string" or "bool" or "int" or "long" or "float" or "double")||row["nativeType"]?.ToString()!=shape["type"]!.ToString())throw new InvalidOperationException("Scalar schema changed; input retained");}
    else if(!JsonNode.DeepEquals(row["contract"],shape))throw new InvalidOperationException("Typed schema changed; input retained");
    if(type=="unset")DeclarationAuthoring.Apply(element,new(){["action"]="unset-data",["path"]=path.DeepClone()});
    else{string value=row["valueJson"]!.GetValue<string>();if(value.Length>65536)throw new ArgumentException("Mixed typed value budget");using var parsed=JsonDocument.Parse(value);SchemaContracts.SetDataPath(element,JsonSerializer.SerializeToElement(path),parsed.RootElement);}
   }else if(type=="parent"){
    Exact(row,"type","value");Unique(type);string? parent=row["value"]?.GetValue<string>();if(parent is not null&&(parent==id||!parent.StartsWith(ns+"::",StringComparison.Ordinal)||!drafts.Any(d=>d?["id"]?.ToString()==parent&&new Parser(d["text"]!.GetValue<string>(),"<mixed-parent>").ParseElement().Kind=="object")))throw new ArgumentException("Different owned parent or Root required");DeclarationAuthoring.Apply(element,new(){["action"]="parent",["value"]=parent});
   }else if(type=="modules"){
    Exact(row,"type","ids");Unique(type);var ids=row["ids"]!.AsArray();if(ids.Count>32||ids.Select(n=>n!.GetValue<string>()).Distinct(StringComparer.Ordinal).Count()!=ids.Count)throw new ArgumentException("Unique bounded module attachments required");DeclarationAuthoring.Apply(element,new(){["action"]="relations",["role"]="module",["entries"]=new JsonArray(ids.Select(n=>(JsonNode)new JsonObject{["id"]=n!.DeepClone()}).ToArray())});
   }else if(type=="information-definition"){
    Definition(row,"type","name","schema","sources","valueJson");string name=row["name"]!.GetValue<string>();Unique("definition:"+name);if(before["fields"]?[name] is not null)throw new ArgumentException("New information property required");var catalogue=InformationTypes.Query(request,formatManifest);var choice=catalogue.SingleOrDefault(item=>item!["id"]!.ToString()==row["schema"]!.ToString());if(choice?["available"]?.GetValue<bool>()!=true||!JsonNode.DeepEquals(choice["sources"],row["sources"]))throw new InvalidOperationException("Selected information definition changed; retain all input");definitions.Add(row.DeepClone());
   }else if(type=="typed-definition"){
    Definition(row,"type","name","contract","sources","valueJson");string name=row["name"]!.GetValue<string>();Unique("definition:"+name);if(before["fields"]?[name] is not null)throw new ArgumentException("New stable field identity required");FieldTypes.Validate(row["contract"]!.AsObject(),row["sources"],before["definitionTypes"]!.AsArray());definitions.Add(row.DeepClone());
   }else if(type=="definition"){
    Definition(row,"type","name","nativeType","valueJson");string name=row["name"]!.GetValue<string>();Unique("definition:"+name);if(before["fields"]?[name] is not null||row["nativeType"]!.ToString() is not ("string" or "bool" or "int" or "long" or "float" or "double"))throw new ArgumentException("New primitive property required; existing definitions are immutable");definitions.Add(row.DeepClone());
   }else if(type is "schema-name" or "schema-remove" or "schema-icon"){
    Exact(row,type=="schema-name"?new[]{"type","path","contract","schema","schemaHash","name"}:type=="schema-icon"?new[]{"type","path","contract","schema","schemaHash","text"}:new[]{"type","path","contract","schema","schemaHash"});var path=row["path"]!.AsArray();if(path.Count!=1)throw new ArgumentException("Direct local field definition required");Unique(type+":"+path.ToJsonString());var shape=Field(before["schemaModel"]!.AsObject(),path);if(!JsonNode.DeepEquals(shape,row["contract"]))throw new InvalidOperationException("Original field contract changed; retain all input");string schema=row["schema"]!.GetValue<string>();if(!schema.StartsWith(ns+"::",StringComparison.Ordinal)||!element.Uses.Any(use=>use.Kind=="schema"&&use.Id==schema))throw new ArgumentException("Direct owned schema required; inherited/external definitions preserved");
    if(type=="schema-name"){string label=row["name"]!.GetValue<string>().Trim();if(label.Length is <1 or >60||label.Any(char.IsControl))throw new ArgumentException("Nonempty bounded property display name required; original data identity unchanged");}else if(type=="schema-icon")DeclarationAuthoring.Glyph(row["text"]!.GetValue<string>(),true);schemaChanges.Add(row);
   }else if(type=="schema-field"){
    Exact(row,row["definition"] is null?new[]{"type","path","contract","schema","schemaHash","nativeType"}:new[]{"type","path","contract","schema","schemaHash","definition","sources"});var path=row["path"]!.AsArray();if(path.Count!=1)throw new ArgumentException("Explicit root field contract required");Unique("schema:"+path.ToJsonString());var shape=Field(before["schemaModel"]!.AsObject(),path);if(!JsonNode.DeepEquals(shape,row["contract"]))throw new InvalidOperationException("Original field contract changed; retain original input");FieldTypes.Validate(FieldTypes.Contract(row),row["sources"],before["definitionTypes"] as JsonArray??new());
    string schema=row["schema"]!.GetValue<string>();if(!schema.StartsWith(ns+"::",StringComparison.Ordinal)||!element.Uses.Any(use=>use.Kind=="schema"&&use.Id==schema))throw new ArgumentException("Direct owned local schema required; inherited/external definitions preserved");schemaChanges.Add(row);
   }else throw new ArgumentException("Mixed operation is not connected by the object UI");
  }
  var additions=new JsonArray();var updates=new JsonArray();string finalManifest=manifest;var finalDrafts=drafts.DeepClone().AsArray();
  foreach(var group in schemaChanges.GroupBy(row=>row["schema"]!.GetValue<string>(),StringComparer.Ordinal)){
   var source=drafts.SingleOrDefault(row=>row?["id"]?.ToString()==group.Key)??throw new InvalidOperationException("Observed schema declaration missing");string original=source["text"]!.GetValue<string>();var schema=new Parser(original,"<mixed-owned-schema>").ParseElement();if(schema.Kind!="schema"||schema.Id!=group.Key||group.Any(row=>row["schemaHash"]!.ToString()!=Hash(original)))throw new InvalidOperationException("Schema source changed; no changes applied");
   var originalFields=schema.Fields.ToDictionary(pair=>pair.Key,pair=>pair.Value,StringComparer.Ordinal);
   foreach(var row in group){string field=row["path"]![0]!.GetValue<string>(),action=row["type"]!.ToString();if(!originalFields.TryGetValue(field,out var existing)||!JsonNode.DeepEquals(Shape(JsonSerializer.SerializeToNode(existing,JsonData.Options)!),row["contract"]))throw new InvalidOperationException("Local field declaration changed; no changes applied");
    if(action=="schema-name"){string label=row["name"]!.GetValue<string>().Trim();if(label==field)schema.Values.Remove("editorFieldName_"+field);else schema.Values["editorFieldName_"+field]=new(JsonSerializer.SerializeToElement(label),schema.Id,new());}
    else if(action=="schema-icon"){string value=row["text"]!.GetValue<string>();if(value.Length==0)schema.Values.Remove("editorFieldIcon_"+field);else schema.Values["editorFieldIcon_"+field]=new(JsonSerializer.SerializeToElement(value),schema.Id,new());}
    else if(action=="schema-remove"){if(schemaChanges.Any(other=>!ReferenceEquals(row,other)&&JsonNode.DeepEquals(row["path"],other["path"]))||changes.Any(other=>other is JsonObject value&&value["type"]?.ToString() is "scalar" or "data" or "unset"&&value["path"]?[0]?.ToString()==field))throw new ArgumentException("Keep pending field input before explicit removal; no changes applied");schema.Fields.Remove(field);schema.Values.Remove("editorFieldName_"+field);schema.Values.Remove("editorFieldIcon_"+field);element.Data.Remove(field);}
    else SchemaContracts.SetField(schema,field,JsonSerializer.SerializeToElement(FieldTypes.Contract(row)));
   }
   if(schema.Fields.Select(pair=>schema.Values.TryGetValue("editorFieldName_"+pair.Key,out var value)&&value.Value.ValueKind==JsonValueKind.String?value.Value.GetString():pair.Key).Distinct(StringComparer.OrdinalIgnoreCase).Count()!=schema.Fields.Count)throw new ArgumentException("Distinct property display names required; all inputs retained");
   string updated=DeclarationTextMerge.Merge(original,format(schema),original,format);finalDrafts.Single(row=>row?["id"]?.ToString()==group.Key)!["text"]=updated;updates.Add(new JsonObject{["id"]=group.Key,["hash"]=Hash(original),["text"]=updated});
  }
  if(definitions.Count>0){
   if(definitions.Count>32)throw new ArgumentException("New property budget");string schemaId=id+"_Properties_"+Hash(definitions.ToJsonString())[..12],name=schemaId[(ns.Length+2)..],relative="elements/"+name+".celem";
   if(registration.Elements.ContainsKey(name)||drafts.Any(d=>d?["id"]?.ToString()==schemaId)||File.Exists(System.IO.Path.Combine(System.IO.Path.GetDirectoryName(System.IO.Path.GetFullPath(project))!,relative)))throw new InvalidOperationException("Property destination exists; retain input");var schema=new Parser("schema "+schemaId+" {}","<mixed-properties>").ParseElement();
   foreach(var row in definitions){string field=row!["name"]!.GetValue<string>(),value=row["valueJson"]!.GetValue<string>();if(value.Length>65536)throw new ArgumentException("New property default budget");var contract=row["type"]!.ToString()=="typed-definition"?row["contract"]!.DeepClone():JsonSerializer.SerializeToNode(new{cardinality="single",kind=row["type"]!.ToString()=="information-definition"?"compound":"general",type=(row["nativeType"]??row["schema"])!.GetValue<string>()});SchemaContracts.SetField(schema,field,JsonSerializer.SerializeToElement(contract));if(row["icon"] is JsonValue glyph&&glyph.GetValue<string>() is {Length:>0} icon)schema.Values["editorFieldIcon_"+field]=new(JsonSerializer.SerializeToElement(icon),schema.Id,new());using var parsed=JsonDocument.Parse(value);SchemaContracts.SetData(element,field,parsed.RootElement);}
   element.Uses.Add(new(schemaId,new(),id,"schema"));registration.Elements.Add(name,new("schema",relative,new()));finalManifest=DeclarationTextMerge.MergeManifest(manifest,formatManifest(registration),formatManifest);string schemaText=format(schema);additions.Add(new JsonObject{["id"]=schemaId,["kind"]="schema",["path"]=relative,["text"]=schemaText});finalDrafts.Add(new JsonObject{["id"]=schemaId,["text"]=schemaText});
  }
  string formatted=DeclarationTextMerge.Merge(text,format(element),text,format);if(formatted.Length>1048576)throw new ArgumentException("Mixed owner budget");var after=Inspect(formatted,finalManifest,finalDrafts);Valid(after);
  return new JsonObject{["text"]=formatted,["manifest"]=finalManifest,["additions"]=additions,["updates"]=updates,["observations"]=before["observations"]!.DeepClone(),["sourceWritten"]=false,["compiled"]=false};
 }
}
