using Confectory.Core;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

// An editor-owned compound uses existing qualified schema declarations. Its
// two-sided owner/path identity never turns an ordinary named schema into a copy.
internal static class OwnedInformationDefinitions
{
 internal const string Marker="editorOwnedDefinition";
 static string Hash(string s)=>JsonData.HashBytes(Encoding.UTF8.GetBytes(s));
 static string ChildId(string owner,IEnumerable<string> path)=>owner+"_Properties_"+Hash(JsonSerializer.Serialize(path.ToArray()))[..24];
 static string Tag(string owner,IEnumerable<string> path)=>JsonSerializer.Serialize(new object[]{"owned-nested-v1",owner,path.ToArray()});
 static bool Marked(Element schema,string owner,string[] path)=>schema.Kind=="schema"&&schema.Parent is null&&schema.Id==ChildId(owner,path)&&schema.Values.TryGetValue(Marker,out var tag)&&tag.Value.ValueKind==JsonValueKind.String&&tag.Value.GetString()==Tag(owner,path);
 internal static bool PrivateSchema(Element schema)
 {
  if(!schema.Values.TryGetValue(Marker,out var marker)||marker.Value.ValueKind!=JsonValueKind.String)return false;
  try{var tag=JsonNode.Parse(marker.Value.GetString()!) as JsonArray;return tag?.Count==3&&tag[0]?.ToString()=="owned-nested-v1"&&tag[1] is JsonValue ownerValue&&ownerValue.TryGetValue<string>(out string? owner)&&owner is not null&&tag[2] is JsonArray steps&&steps.Count is >=1 and <=9&&steps.All(v=>v is JsonValue item&&item.TryGetValue<string>(out string? key)&&!string.IsNullOrEmpty(key)&&key.Length<=128)&&Marked(schema,owner,steps.Select(v=>v!.GetValue<string>()).ToArray());}catch(JsonException){return false;}
 }
 static string Label(Element e,string key)=>e.Values.TryGetValue("editorFieldName_"+key,out var v)&&v.Value.ValueKind==JsonValueKind.String?v.Value.GetString()!:key;
 static string Icon(Element e,string key){if(!e.Values.TryGetValue("editorFieldIcon_"+key,out var v))return "";if(v.Value.ValueKind!=JsonValueKind.String)throw new ArgumentException("Unknown owned icon metadata preserved");string value=v.Value.GetString()!;DeclarationAuthoring.PresentationIcon(value,true);return value;}
 static void Exact(JsonObject row,params string[] names){if(row.Count!=names.Length||row.Any(p=>!names.Contains(p.Key,StringComparer.Ordinal)))throw new ArgumentException("Exact owned definition required");}
 internal static bool Has(JsonArray changes)=>changes.Any(c=>c?["type"]?.ToString()=="owned-definition");
 internal static JsonObject Ownership(JsonObject request)
 {
  string owner=request["owner"]!.GetValue<string>(),id=request["id"]!.GetValue<string>();var schema=new Parser(request["text"]!.GetValue<string>(),"<owned-creation>").ParseElement();if(!schema.Values.TryGetValue(Marker,out var marker))return new(){["owned"]=false};
  var root=new Parser(request["ownerText"]!.GetValue<string>(),"<owned-creation-root>").ParseElement();if(marker.Value.ValueKind!=JsonValueKind.String)throw new ArgumentException("Owned definition profile changed");var tag=JsonNode.Parse(marker.Value.GetString()!)!.AsArray();if(tag.Count!=3||tag[0]?.ToString()!="owned-nested-v1"||tag[1]?.ToString()!=owner||tag[2] is not JsonArray steps||steps.Count is <1 or >9||steps.Any(v=>v is not JsonValue s||!s.TryGetValue<string>(out string? name)||string.IsNullOrEmpty(name)||name.Length>128)||root.Id!=owner||root.Kind is not ("object" or "schema")||schema.Id!=id||!Marked(schema,owner,steps.Select(v=>v!.GetValue<string>()).ToArray())||request["path"]?.ToString()!="elements/"+id[(PackPaths.Namespace(owner).Length+2)..]+".celem")throw new UnauthorizedAccessException("Exact owned schema creation owner/path required");return new(){["owned"]=true};
 }
 internal static JsonObject Project(Registry registry,Element owner,Dictionary<string,SchemaField> fields,Func<string,string> source)
 {
  var result=new JsonObject();int budget=0;JsonArray? choices=null;
  foreach(var field in fields){
   if(field.Value.Kind!="compound"||!Direct(field.Key,field.Value))continue;
   try{
    var sources=new JsonObject();var tree=Read(field.Value.Type,new[]{field.Key},sources,0);
    result[field.Key]=new JsonObject{["tree"]=tree,["sources"]=sources};
   }catch(ArgumentException){/* Unknown/shared information stays a value-only reference. */}
  }
  return result;
  bool Direct(string key,SchemaField field)=>field.Origin.StartsWith(PackPaths.Namespace(owner.Id)+"::",StringComparison.Ordinal)&&(owner.Kind=="schema"?field.Origin==owner.Id:owner.Uses.Any(u=>u.Kind=="schema"&&u.Id==field.Origin&&u.Origin==owner.Id)&&registry.Get(field.Origin,"schema").Fields.ContainsKey(key));
  JsonObject Read(string id,string[] path,JsonObject sources,int depth){
   if(depth>8||++budget>128)throw new ArgumentException("Owned definition budget");var schema=registry.Get(id,"schema");if(!Marked(schema,owner.Id,path))throw new ArgumentException("Not an owned compound");
   var pack=registry.Packs[PackPaths.Namespace(owner.Id)];string local=id[(pack.Namespace.Length+2)..];if(!pack.Elements.TryGetValue(local,out var at)||at.Path!="elements/"+local+".celem")throw new ArgumentException("Owned definition locator changed");
   sources[id]=Hash(source(id));var rows=new JsonArray();foreach(var item in schema.Fields){var field=item.Value;var row=new JsonObject{["key"]=item.Key,["name"]=Label(schema,item.Key),["icon"]=Icon(schema,item.Key),["sources"]=null,["definition"]=new JsonObject{["kind"]=field.Kind,["type"]=field.Type,["cardinality"]=field.Cardinality}};
    if(field.Kind=="compound"&&Marked(registry.Get(field.Type,"schema"),owner.Id,path.Append(item.Key).ToArray())){row["definition"]=new JsonObject{["kind"]="owned",["cardinality"]=field.Cardinality};row["children"]=Read(field.Type,path.Append(item.Key).ToArray(),sources,depth+1);}
    else if(field.Kind!="general"){choices??=FieldTypes.Project(registry,owner.Id,source);var choice=choices.SingleOrDefault(v=>v?["id"]?.ToString()==field.Type&&v?["kind"]?.ToString()==field.Kind);if(choice?["available"]?.GetValue<bool>()!=true)throw new ArgumentException("Owned leaf type unavailable");row["sources"]=choice["sources"]!.DeepClone();}
    rows.Add(row);
   }return new JsonObject{["fields"]=rows};
  }
 }
 internal static JsonObject Prepare(JsonObject request,Func<Element,string> format,Func<Manifest,string> formatManifest,Func<JsonObject,JsonObject> ordinary)
 {
  string project=request["project"]!.GetValue<string>(),manifest=request["manifest"]!.GetValue<string>(),id=request["id"]!.GetValue<string>(),original=request["text"]!.GetValue<string>();var registration=new Parser(manifest,"<owned-registration>").ParseManifest();var owner=new Parser(original,"<owned-root>").ParseElement();var drafts=request["drafts"]!.AsArray();var changes=request["changes"]!.AsArray();var own=changes.Where(c=>c?["type"]?.ToString()=="owned-definition").Select(c=>c!.AsObject()).ToArray();
  if(registration.Kind!="project"||owner.Kind is not ("schema" or "object")||!id.StartsWith(registration.Namespace+"::",StringComparison.Ordinal)||changes.Count>64||own.Length is <1 or >16||drafts.Count>255)throw new ArgumentException("Bounded directly owned definition candidate required");
  string Read(string path){var file=new FileInfo(path);if(!file.Exists||file.Length>1048576)throw new IOException("Owned definition source budget");return File.ReadAllText(path);}
  JsonObject Inspect(string text,string m,JsonArray ds,bool types=false)=>EffectiveMetadata.Query(project,m,id,text,formatManifest,Read,ds,schemaView:true,validateObjects:true,observeSources:true,definitionTypes:types);
  var before=Inspect(original,manifest,drafts,true);Valid(before);var model=before["schemaModel"]!.AsObject();var names=own.Select(r=>r["name"]!.GetValue<string>()).ToHashSet(StringComparer.Ordinal);if(names.Count!=own.Length)throw new ArgumentException("Distinct owned root fields required");
  var rest=new JsonArray(changes.Where(c=>c?["type"]?.ToString()!="owned-definition").Select(c=>c!.DeepClone()).ToArray());if(rest.Any(c=>names.Contains(c?["path"]?[0]?.ToString()??c?["name"]?.ToString()??"")))throw new ArgumentException("Resolve overlapping root definition/value input together");
  var ordinaryRequest=request.DeepClone().AsObject();ordinaryRequest["changes"]=rest;var result=rest.Count==0?new JsonObject{["text"]=original,["manifest"]=manifest,["additions"]=new JsonArray(),["updates"]=new JsonArray(),["observations"]=before["observations"]!.DeepClone(),["sourceWritten"]=false,["compiled"]=false}:ordinary(ordinaryRequest);
  owner=new Parser(result["text"]!.ToString(),"<owned-candidate>").ParseElement();registration=new Parser(result["manifest"]!.ToString(),"<owned-registration-candidate>").ParseManifest();var additions=result["additions"]!.AsArray();var updates=result["updates"]!.AsArray();var nextDrafts=drafts.DeepClone().AsArray();foreach(var u in updates.Concat(result["linkedUpdates"]?.AsArray()??new JsonArray()))Overlay(u!["id"]!.ToString(),u["text"]!.ToString());foreach(var a in additions)Overlay(a!["id"]!.ToString(),a["text"]!.ToString());
  var initial=new Dictionary<string,string>(StringComparer.Ordinal){{id,original}};foreach(var d in drafts)initial[d!["id"]!.ToString()]=d["text"]!.ToString();int nodes=0;
  foreach(var row in own){
   Exact(row,row.ContainsKey("definition")?new[]{"type","name","displayName","icon","cardinality","contract","schema","schemaHash","tree","sources","valueJson","definition","definitionSources"}:new[]{"type","name","displayName","icon","cardinality","contract","schema","schemaHash","tree","sources","valueJson"});if(row["cardinality"]?.ToString() is not ("single" or "multiple")||row.ToJsonString().Length>1048576)throw new ArgumentException("Bounded explicit owned definition required");string key=row["name"]!.GetValue<string>();var previous=model["fields"]?[key];Element rootSchema;string rootId;
   if(previous is not null){
    var shape=MixedOwnerCopyEdits.Field(model,new JsonArray(key));rootId=previous["origin"]!.ToString();if(!JsonNode.DeepEquals(shape,row["contract"])||row["schema"]?.ToString()!=rootId||row["schemaHash"]?.ToString()!=previous["schemaHash"]?.ToString()||before["fieldSources"]?[key]?.ToString()!=id||!initial.TryGetValue(rootId,out var raw))throw new InvalidOperationException("Owned root contract/source changed; retain all input");
    rootSchema=rootId==id?owner:new Parser(Current(rootId),"<owned-local-schema>").ParseElement();if(!rootSchema.Fields.ContainsKey(key)||rootSchema.Parent is not null&&rootId!=id||owner.Kind=="schema"&&rootId!=id||owner.Kind=="object"&&!owner.Uses.Any(u=>u.Kind=="schema"&&u.Id==rootId&&u.Origin==id))throw new UnauthorizedAccessException("Parent or reused root definitions are preserved");
    var expected=model["ownedDefinitions"]?[key];if(shape["kind"]?.ToString()=="compound"&&expected is null)throw new UnauthorizedAccessException("Named information is not an owned inline definition");if(!JsonNode.DeepEquals(expected?["sources"]??new JsonObject(),row["sources"]))throw new InvalidOperationException("Owned child source changed; all input retained");
   }else{
    if(row["contract"] is not null||row["schema"] is not null||row["schemaHash"] is not null||row["sources"] is not JsonObject proof||proof.Count!=0)throw new ArgumentException("New owned field must not claim an existing source");
    if(owner.Kind=="schema"){rootSchema=owner;rootId=id;}else{rootId=ChildId(id,new[]{"$properties",key});rootSchema=New(rootId,new[]{"$properties",key});owner.Uses.Add(new(rootId,new(),id,"schema"));}
   }
   var supplied=row["sources"]!.AsObject();foreach(var p in supplied){if(!initial.TryGetValue(p.Key,out var raw)||Hash(raw)!=p.Value?.ToString())throw new InvalidOperationException("Owned child proof changed");}
   JsonObject finalShape;if(row["definition"] is JsonObject selected){if(!JsonNode.DeepEquals(row["tree"],model["ownedDefinitions"]?[key]?["tree"]??new JsonObject{["fields"]=new JsonArray()}))throw new InvalidOperationException("Save or cancel nested definition input before changing its root type");FieldTypes.Validate(selected,row["definitionSources"],before["definitionTypes"]!.AsArray());if(selected["cardinality"]?.ToString()!=row["cardinality"]?.ToString())throw new ArgumentException("Root cardinality changed");finalShape=selected;}else{string child=Build(row["tree"]!.AsObject(),new[]{key},supplied,0);finalShape=new JsonObject{["kind"]="compound",["cardinality"]=row["cardinality"]!.DeepClone(),["type"]=child};}SchemaContracts.SetField(rootSchema,key,JsonSerializer.SerializeToElement(finalShape));Presentation(rootSchema,key,row["displayName"]!.GetValue<string>(),row["icon"]!.GetValue<string>());Distinct(rootSchema);
   string json=row["valueJson"]!.GetValue<string>();if(json.Length>65536)throw new ArgumentException("Owned compound value budget");using var value=JsonDocument.Parse(json);if(owner.Kind=="schema")InformationDefaults.Set(owner,key,SchemaContracts.FromTransport(value.RootElement,id));else SchemaContracts.SetData(owner,key,value.RootElement);
   if(rootId!=id)Store(rootSchema);
  }
  string text=DeclarationTextMerge.Merge(result["text"]!.ToString(),format(owner),result["text"]!.ToString(),format);string finalManifest=DeclarationTextMerge.MergeManifest(result["manifest"]!.ToString(),formatManifest(registration),formatManifest);var after=Inspect(text,finalManifest,nextDrafts);Valid(after);
  var observations=new SortedDictionary<string,JsonNode>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);foreach(var o in before["observations"]!.AsArray().Concat(result["observations"]!.AsArray()).Concat(after["observations"]!.AsArray())){string path=o!["path"]!.ToString();if(observations.TryGetValue(path,out var old)&&!JsonNode.DeepEquals(old,o))throw new InvalidOperationException("Owned source changed during candidate validation");observations[path]=o.DeepClone();}foreach(var o in observations)if(Hash(Read(o.Key))!=o.Value["hash"]!.ToString())throw new InvalidOperationException("Owned source changed after validation");
  result["text"]=text;result["manifest"]=finalManifest;result["observations"]=new JsonArray(observations.Values.ToArray());return result;
  string Current(string schema)=>nextDrafts.Single(d=>d!["id"]!.ToString()==schema)!["text"]!.ToString();
  void Overlay(string schema,string text){var d=nextDrafts.SingleOrDefault(d=>d!["id"]!.ToString()==schema);if(d is null)nextDrafts.Add(new JsonObject{["id"]=schema,["text"]=text});else d["text"]=text;}
  Element New(string schema,string[] path){if(registration.Elements.ContainsKey(schema[(registration.Namespace.Length+2)..]))throw new InvalidOperationException("Owned definition destination exists");var e=new Parser("schema "+schema+" {}","<new-owned-definition>").ParseElement();e.Values[Marker]=new(JsonSerializer.SerializeToElement(Tag(id,path)),id,new());return e;}
  void Store(Element e){string local=e.Id[(registration.Namespace.Length+2)..],path="elements/"+local+".celem",text=format(e);if(initial.TryGetValue(e.Id,out var originalText)){text=DeclarationTextMerge.Merge(originalText,text,originalText,format);var update=updates.SingleOrDefault(u=>u!["id"]!.ToString()==e.Id);if(update is null)updates.Add(new JsonObject{["id"]=e.Id,["hash"]=Hash(originalText),["text"]=text});else update["text"]=text;}else{if(!registration.Elements.ContainsKey(local))registration.Elements.Add(local,new("schema",path,new()));var addition=additions.SingleOrDefault(a=>a!["id"]!.ToString()==e.Id);if(addition is null)additions.Add(new JsonObject{["id"]=e.Id,["kind"]="schema",["path"]=path,["text"]=text});else addition["text"]=text;}Overlay(e.Id,text);}
  string Build(JsonObject tree,string[] path,JsonObject sources,int depth){
   Exact(tree,"fields");if(depth>8||tree["fields"] is not JsonArray rows||rows.Count>64)throw new ArgumentException("Bounded owned child fields required");string schema=ChildId(id,path);Element target;
   if(initial.TryGetValue(schema,out var raw)){target=new Parser(Current(schema),"<owned-child>").ParseElement();if(!Marked(target,id,path)||sources[schema]?.ToString()!=Hash(raw)||!registration.Elements.TryGetValue(schema[(registration.Namespace.Length+2)..],out var at)||at.Path!="elements/"+schema[(registration.Namespace.Length+2)..]+".celem")throw new UnauthorizedAccessException("Only the observed directly owned child may change");
    foreach(var source in initial){var declaration=new Parser(source.Value,"<owned-consumer>").ParseElement();foreach(var f in declaration.Fields)if(f.Value.Kind=="compound"&&f.Value.Type==schema&&(declaration.Id!=RootSource(path)||f.Key!=path[^1]))throw new InvalidOperationException("Shared child definition requires explicit separate editing; no source changed");}
   }else target=New(schema,path);
   target.Fields.Clear();foreach(string k in target.Values.Keys.Where(k=>k.StartsWith("editorFieldName_",StringComparison.Ordinal)||k.StartsWith("editorFieldIcon_",StringComparison.Ordinal)).ToArray())target.Values.Remove(k);
   var keys=new HashSet<string>(StringComparer.Ordinal);var labels=new HashSet<string>(StringComparer.OrdinalIgnoreCase);foreach(var node in rows){if(++nodes>128)throw new ArgumentException("Owned definition tree budget");var field=node!.AsObject();bool nested=field["definition"]?["kind"]?.ToString()=="owned";Exact(field,nested?new[]{"key","name","icon","definition","children","sources"}:new[]{"key","name","icon","definition","sources"});string key=field["key"]!.GetValue<string>(),name=field["name"]!.GetValue<string>().Trim();if(!keys.Add(key)||!labels.Add(name))throw new ArgumentException("Distinct owned field identity/display name required");var shape=field["definition"]!.AsObject();if(nested){Exact(shape,"kind","cardinality");if(shape["cardinality"]?.ToString() is not ("single" or "multiple")||field["sources"] is not null)throw new ArgumentException("Explicit owned cardinality required");shape=new JsonObject{["kind"]="compound",["cardinality"]=shape["cardinality"]!.DeepClone(),["type"]=Build(field["children"]!.AsObject(),path.Append(key).ToArray(),sources,depth+1)};}else FieldTypes.Validate(shape,field["sources"],before["definitionTypes"]!.AsArray());SchemaContracts.SetField(target,key,JsonSerializer.SerializeToElement(shape));Presentation(target,key,name,field["icon"]!.GetValue<string>());}
   foreach(string key in target.Values.Keys.Where(k=>k.StartsWith(InformationDefaults.Prefix,StringComparison.Ordinal)&&!target.Fields.ContainsKey(k[InformationDefaults.Prefix.Length..])).ToArray())target.Values.Remove(key);
   Store(target);return schema;
  }
  string RootSource(string[] path)=>path.Length>1?ChildId(id,path[..^1]):model["fields"]?[path[0]]?["origin"]?.ToString()??id;
 }
 static void Presentation(Element schema,string key,string name,string icon){name=name.Trim();if(name.Length is <1 or >60||name.Any(char.IsControl))throw new ArgumentException("Bounded owned field name required");DeclarationAuthoring.PresentationIcon(icon,true);if(name==key)schema.Values.Remove("editorFieldName_"+key);else schema.Values["editorFieldName_"+key]=new(JsonSerializer.SerializeToElement(name),schema.Id,new());if(icon.Length==0)schema.Values.Remove("editorFieldIcon_"+key);else schema.Values["editorFieldIcon_"+key]=new(JsonSerializer.SerializeToElement(icon),schema.Id,new());}
 static void Distinct(Element schema){if(schema.Fields.Keys.Select(k=>Label(schema,k)).Distinct(StringComparer.OrdinalIgnoreCase).Count()!=schema.Fields.Count)throw new ArgumentException("Distinct owned field names required");}
 static void Valid(JsonObject result){if(result["status"]?.ToString()!="available"||result["schemaModel"]?["validation"]?["status"]?.ToString()!="valid")throw new InvalidOperationException("Owned definition conflicts with existing defaults, values or consumers; all input retained");}
}
