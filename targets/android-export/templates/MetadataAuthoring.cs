using System.Linq;
using Confectory.Core;
using System.Text.Json;
using System.Text;
using System.Text.Json.Nodes;
internal static class MetadataAuthoring
{
 public static string Call(string ownerRoot,string operation,string payload)
 {
 if(payload.Length>2097152)throw new ArgumentException("Metadata payload budget");
 var request=JsonNode.Parse(payload)!.AsObject();string S(string key)=>request[key]!.GetValue<string>();
 if(operation is "connectionCatalog" or "connectionSettings")return ConnectionDeclarations.Query(S("project"),operation=="connectionSettings"?S("id"):null,FormatManifest,path=>PackPaths.Owned(ownerRoot,Path.GetRelativePath(ownerRoot,path))).ToJsonString();
 if(operation=="catalog")return SemanticCatalogService.Query(S("project"),request["request"]!.AsObject(),path=>{string owned=PackPaths.Owned(ownerRoot,Path.GetRelativePath(ownerRoot,path));var file=new FileInfo(owned);if(!file.Exists||file.Length>1048576)throw new IOException("Owned document unavailable");return owned;}).ToJsonString();
 if(operation=="effective"){
 string selected=PackPaths.Owned(ownerRoot,Path.GetRelativePath(ownerRoot,Path.GetFullPath(S("project"))));
 return EffectiveMetadata.Query(selected,S("manifest"),S("id"),S("text"),FormatManifest,path=>Read(PackPaths.Owned(ownerRoot,Path.GetRelativePath(ownerRoot,path))),request["drafts"]?.AsArray(),request["schemaView"]?.GetValue<bool>()==true).ToJsonString();
 }
 if(operation=="referenceDefinition"){
 string selected=PackPaths.Owned(ownerRoot,Path.GetRelativePath(ownerRoot,Path.GetFullPath(S("project"))));
 return ReferenceDefinition.Query(selected,S("manifest"),S("sourceId"),S("text"),S("id"),path=>Read(PackPaths.Owned(ownerRoot,Path.GetRelativePath(ownerRoot,path)))).ToJsonString();
 }
 if(operation=="locate"){
 string selected=PackPaths.Owned(ownerRoot,Path.GetRelativePath(ownerRoot,Path.GetFullPath(S("project"))));
 return RelationLocators.Query(S("manifest"),Path.GetDirectoryName(selected)!,request["ids"]!.AsArray().Select(x=>x!.GetValue<string>()).ToArray(),path=>Read(PackPaths.Owned(ownerRoot,Path.GetRelativePath(ownerRoot,path)))).ToJsonString();
 }
 if(operation=="blueprintDescribeOwned"){request["project"]=PackPaths.Owned(ownerRoot,Path.GetRelativePath(ownerRoot,Path.GetFullPath(S("project"))));return BlueprintDocuments.DescribeOwned(request).ToJsonString();}
 if(operation=="blueprintSourceValidate")return BlueprintDocuments.Validate(S("id"),S("kind"),S("text")).ToJsonString();
 if(operation=="relationsMap")return RelationMapBatch.Query(request).ToJsonString();
 if(operation=="bodyUnits"){request["project"]=PackPaths.Owned(ownerRoot,Path.GetRelativePath(ownerRoot,Path.GetFullPath(S("project"))));return BodyUnitMetadata.Query(request).ToJsonString();}
 if(operation=="inspect"){string text=S("text");if(text.Length>1048576)throw new ArgumentException("Declaration budget");var e=new Parser(text,"<draft>").ParseElement();return new JsonObject{["id"]=e.Id,["kind"]=e.Kind,["parent"]=e.Parent,["function"]=e.Function,["descriptionDefined"]=e.DescriptionPresent,["relations"]=DeclaredRelations.Describe(e),["description"]=e.Description,["signature"]=JsonSerializer.SerializeToNode(e.Signature),["fields"]=JsonSerializer.SerializeToNode(e.Fields),["data"]=JsonSerializer.SerializeToNode(e.Data),["values"]=JsonSerializer.SerializeToNode(e.Values.ToDictionary(x=>x.Key,x=>x.Value.Value))}.ToJsonString();}

 if(operation=="create"){string kind=S("kind"),id=S("id");if(kind is not ("category" or "concept" or "function" or "module" or "object" or "schema"))throw new ArgumentException("Unsupported authored kind");string text=kind+" "+id+(kind=="function"?" () -> int":"")+" { }\n";new Parser(text,"<new>").ParseElement();return JsonSerializer.Serialize(text);}
 if(operation is "setDataPath" or "setField" or "setData"){var element=new Parser(S("text"),"<draft>").ParseElement();if(operation=="setDataPath")SchemaContracts.SetDataPath(element,JsonSerializer.SerializeToElement(request["path"]),JsonSerializer.SerializeToElement(request["value"]));else if(operation=="setField")SchemaContracts.SetField(element,S("field"),JsonSerializer.SerializeToElement(request["value"]));else SchemaContracts.SetData(element,S("field"),JsonSerializer.SerializeToElement(request["value"]));string text=Format(element);new Parser(text,"<draft>").ParseElement();return JsonSerializer.Serialize(text);}
 if(operation=="editDeclaration"){var element=new Parser(S("text"),"<draft>").ParseElement();string id=element.Id,kind=element.Kind;if(kind is not ("category" or "concept" or "function" or "module" or "object" or "schema" or "implementation"))throw new ArgumentException("Authored declaration required");DeclarationAuthoring.Apply(element,request["edit"]?.AsObject()??throw new ArgumentException("Declaration edit required"));string formatted=Format(element);var parsed=new Parser(formatted,"<draft>").ParseElement();if(parsed.Id!=id||parsed.Kind!=kind)throw new ArgumentException("Stable declaration ID and kind required");return JsonSerializer.Serialize(formatted);}
 if(operation=="reviewSummary")return ReviewSummary(S("kind"),S("before"),S("after")).ToJsonString();
 if(operation=="setDescription"){var element=new Parser(S("text"),"<draft>").ParseElement();element.Description=request["value"]?.GetValue<string>()??throw new ArgumentException("Description string required");element.DescriptionPresent=true;string text=Format(element);new Parser(text,"<draft>").ParseElement();return JsonSerializer.Serialize(text);}
 if(operation=="setValue"){var element=new Parser(S("text"),"<draft>").ParseElement();var value=JsonSerializer.SerializeToElement(request["value"]);if(value.ValueKind is not (JsonValueKind.String or JsonValueKind.Number or JsonValueKind.True or JsonValueKind.False))throw new ArgumentException("Scalar metadata required");element.Values[S("field")]=new(value,element.Id,new());string text=Format(element);new Parser(text,"<draft>").ParseElement();return JsonSerializer.Serialize(text);}
 if(operation=="register"){var manifest=new Parser(S("text"),"<draft>").ParseManifest();string id=S("id"),path=S("path");if(!id.StartsWith(manifest.Namespace+"::",StringComparison.Ordinal))throw new ArgumentException("Creation belongs to selected namespace");if(Path.IsPathRooted(path)||path.Split('/', '\\').Any(x=>x==".."))throw new ArgumentException("Owned registration path required");manifest.Elements.Add(id[(manifest.Namespace.Length+2)..],new(S("kind"),path,new()));string text=FormatManifest(manifest);new Parser(text,"<draft>").ParseManifest();return JsonSerializer.Serialize(text);}
 if(operation!="describe")throw new PlatformNotSupportedException("This target supports source metadata and draft text only; compiler/Confirm operations require an explicit compiler provider.");
 string project=PackPaths.Owned(ownerRoot,Path.GetRelativePath(ownerRoot,Path.GetFullPath(S("project")))),root=Path.GetDirectoryName(project)!;var m=new Parser(Read(project),project).ParseManifest();var units=new JsonArray();
 units.Add(new JsonObject{["id"]=m.Namespace+(m.Kind=="project"?"::ProjectManifest":"::PackManifest"),["kind"]=m.Kind,["path"]=Path.GetFileName(project)});
 foreach(var item in m.Elements.OrderBy(x=>x.Key,StringComparer.Ordinal)){
 if(units.Count>=256)throw new ArgumentException("Owned source unit budget exceeded");string file=PackPaths.Owned(root,item.Value.Path);if(request["metadataOnly"]?.GetValue<bool>()==true&&item.Value.Kind!="implementation"){units.Add(new JsonObject{["id"]=m.Namespace+"::"+item.Key,["kind"]=item.Value.Kind,["path"]=Path.GetRelativePath(root,file)});continue;}var e=new Parser(Read(file),file).ParseElement();if(e.Id!=m.Namespace+"::"+item.Key||e.Kind!=item.Value.Kind)throw new ArgumentException("Owned declaration identity mismatch");
 units.Add(new JsonObject{["id"]=e.Id,["kind"]=e.Kind,["path"]=Path.GetRelativePath(root,file)});
 foreach(var b in e.Bodies.OrderBy(x=>x.Key,StringComparer.Ordinal)){if(units.Count>=256)throw new ArgumentException("Owned source unit budget exceeded");string body=PackPaths.Owned(Path.GetDirectoryName(file)!,b.Value.Path);if(request["metadataOnly"]?.GetValue<bool>()!=true)Read(body);units.Add(new JsonObject{["id"]=e.Id+"/body:"+b.Key,["kind"]=b.Value.SourceKind=="blueprint"?"blueprint":"body",["path"]=Path.GetRelativePath(root,body)});if(b.Value.SourceKind=="blueprint")foreach(var node in BlueprintDocuments.NodeUnits(root,body,e.Id+"/body:"+b.Key))units.Add(node!.DeepClone());}}
 return new JsonObject{["project"]=project,["namespace"]=m.Namespace,["kind"]=m.Kind,["supportsStandalone"]=m.SupportsStandalone,["units"]=units}.ToJsonString();
 }
 static string Read(string file){var info=new FileInfo(file);if(info.Length>1048576)throw new ArgumentException("Owned source file budget exceeded");return File.ReadAllText(file);}
static string Quote(string text)=>JsonSerializer.Serialize(text);
static string Signature(FunctionSignature signature,bool named)=>"("+string.Join(", ",signature.Args.Select(x=>x.Type+(named?" "+x.Name:"")))+") -> "+signature.Return;
static string Format(Element element)
{
    var text=new StringBuilder(element.Kind+" "+element.Id);
    if(element.Kind=="implementation")text.Append(" for "+element.Function);
    if(element.Signature is not null)text.Append(" "+Signature(element.Signature,true));
    if(element.Parent is not null)text.Append(" extends "+element.Parent);
    text.AppendLine(" {");
    if(element.DescriptionPresent)text.AppendLine("description "+Quote(element.Description)+";");
    foreach(var value in element.Modules)text.AppendLine("module "+value.Id+";");
    foreach(var value in element.Includes)text.AppendLine("include "+value.Id+";");
    foreach(var (id,value) in element.Requires)text.AppendLine("require "+id+" "+Signature(value.Signature,false)+";");
    foreach(var (id,value) in element.Defaults)text.AppendLine("default "+id+" with "+value.Id+";");
    foreach(var (id,value) in element.Provides)text.AppendLine("provide "+id+" with "+value.Id+";");
    foreach(var value in element.Uses)text.AppendLine("use "+value.Kind+" "+value.Id+";");
    foreach(var value in element.Contains)text.AppendLine("contain "+value.Kind+" "+value.Id+";");
    text.Append(SchemaContracts.FormatDeclarations(element));
    foreach(var (name,value) in element.Values)text.AppendLine("value "+name+" = "+value.Value.GetRawText()+";");
    foreach(var (alias,value) in element.Imports)text.AppendLine("import "+value.Id+" as "+alias+" "+Signature(value.Signature,false)+(value.Scope is null?"":" in "+value.Scope)+";");
    foreach(var (target,value) in element.Bodies)text.AppendLine((value.SourceKind=="blueprint"?"blueprint":"body")+" "+target+" "+Quote(value.Path)+";");
    if(element.Tool is not null)text.AppendLine("tool "+Quote(element.Tool)+";");
    foreach(var (name,value) in element.Options)text.AppendLine("option "+name+" "+Quote(value)+";");
    return text.AppendLine("}").ToString();
}
static string FormatManifest(Manifest manifest)
{
    var text=new StringBuilder(manifest.Kind+" "+manifest.Namespace+" version "+Quote(manifest.Version)+" {\n");
    if(manifest.Description!="")text.AppendLine("description "+Quote(manifest.Description)+";");
    if(manifest.Standalone is not null)text.AppendLine("standalone "+(manifest.Standalone.Value?"true":"false")+";");
    if(manifest.Entry is not null)text.AppendLine("entry "+manifest.Entry+";");
    foreach(var (id,value) in manifest.Registry)text.AppendLine("registry "+id+" "+Quote(value.Path)+";");
    foreach(var (id,value) in manifest.Dependencies)text.AppendLine("dependency "+id+" version "+Quote(value.Version)+";");
    foreach(var (id,value) in manifest.Targets)text.AppendLine("target "+id+" "+value.Id+";");
    foreach(var value in manifest.Always)text.AppendLine("always "+value.Id+";");
    foreach(var (id,value) in manifest.Elements)text.AppendLine("element "+id+" "+value.Kind+" "+Quote(value.Path)+";");
    return text.AppendLine("}").ToString();
}

static JsonObject ReviewSummary(string kind,string before,string after)
{
 var changes=new JsonArray();bool additional=false;
 void Add(string label,JsonNode? oldValue,JsonNode? newValue,bool beforeDefined=true,bool afterDefined=true)=>changes.Add(new JsonObject{["label"]=label,["before"]=oldValue,["after"]=newValue,["beforeDefined"]=beforeDefined,["afterDefined"]=afterDefined});
 string Comments(string text)=>string.Join("\n",System.Text.RegularExpressions.Regex.Matches(text,@"""(?:[^""\\]|\\.)*""|(?<comment>//[^\n]*)").Cast<System.Text.RegularExpressions.Match>().Where(m=>m.Groups["comment"].Success).Select(m=>m.Value));
 JsonNode? Datum(SchemaDatum value)=>value.Kind=="reference"?new JsonObject{["참조 대상"]=value.Reference}:value.Items is not null?new JsonArray(value.Items.Select(Datum).ToArray()):value.Members is not null?new JsonObject(value.Members.Select(x=>new KeyValuePair<string,JsonNode?>(x.Key,Datum(x.Value)))):value.Scalar is not null?JsonNode.Parse(value.Scalar.Value.GetRawText()):null;
 try{
  if(kind is "project" or "pack"){
   var old=new Parser(before,"<review>").ParseManifest();var next=new Parser(after,"<review>").ParseManifest();
   foreach(var item in next.Elements)if(!old.Elements.ContainsKey(item.Key))Add("프로젝트에 등록",null,JsonValue.Create(item.Key+" · "+item.Value.Kind),false,true);
   foreach(var item in old.Elements)if(!next.Elements.ContainsKey(item.Key))Add("프로젝트 등록 해제",JsonValue.Create(item.Key+" · "+item.Value.Kind),null,true,false);
   foreach(var item in next.Elements)if(old.Elements.TryGetValue(item.Key,out var prior)&&(prior.Path!=item.Value.Path||prior.Kind!=item.Value.Kind))additional=true;
   additional|=!old.Elements.Keys.Where(k=>next.Elements.ContainsKey(k)).SequenceEqual(next.Elements.Keys.Where(k=>old.Elements.ContainsKey(k)));next.Elements=old.Elements;additional|=FormatManifest(next)!=FormatManifest(old)||Comments(before)!=Comments(after);
  }else if(kind is "body" or "blueprint" or "blueprint-node")additional=true;
  else{
   bool created=before.Length==0;var next=new Parser(after,"<review>").ParseElement();var old=created?new Element{Kind=next.Kind,Id=next.Id}:new Parser(before,"<review>").ParseElement();
   if(created)Add(kind=="object"?"개념 생성":kind=="schema"?"스키마 생성":"선언 생성",null,JsonValue.Create(next.Id.Split("::").Last()),false,true);
   // Explain declaration contracts without hiding changes to bodies, tools, identity or comments.
   void Contract(string label,JsonNode? prior,JsonNode? current){if(!JsonNode.DeepEquals(prior,current))Add(label,prior,current,prior is not null,current is not null);}
   JsonNode? Sig(FunctionSignature? signature)=>signature is null?null:JsonValue.Create(Signature(signature,true));
   JsonArray Refs(IEnumerable<ElementReference> refs)=>new(refs.Select(r=>(JsonNode)new JsonObject{["대상"]=r.Id,["종류"]=r.Kind}).ToArray());
   JsonArray Bindings(Dictionary<string,ElementReference> refs)=>new(refs.Select(r=>(JsonNode)new JsonObject{["기능"]=r.Key,["구현"]=r.Value.Id}).ToArray());
   JsonArray Requirements(Dictionary<string,RequiredFunction> refs)=>new(refs.Select(r=>(JsonNode)new JsonObject{["기능"]=r.Key,["계약"]=Sig(r.Value.Signature)}).ToArray());
   JsonArray Imports(Dictionary<string,Import> refs)=>new(refs.Select(r=>(JsonNode)new JsonObject{["별칭"]=r.Key,["기능"]=r.Value.Id,["계약"]=Sig(r.Value.Signature),["범위"]=r.Value.Scope}).ToArray());
   Contract("기능 계약",Sig(old.Signature),Sig(next.Signature));Contract("부모",JsonValue.Create(old.Parent),JsonValue.Create(next.Parent));
   Contract("모듈",Refs(old.Modules),Refs(next.Modules));Contract("포함",Refs(old.Includes),Refs(next.Includes));Contract("필요 기능",Requirements(old.Requires),Requirements(next.Requires));
   Contract("기본 구현",Bindings(old.Defaults),Bindings(next.Defaults));Contract("제공 구현",Bindings(old.Provides),Bindings(next.Provides));Contract("사용 관계",Refs(old.Uses),Refs(next.Uses));Contract("소속 관계",Refs(old.Contains),Refs(next.Contains));Contract("외부 기능",Imports(old.Imports),Imports(next.Imports));
   next.Signature=old.Signature;next.Parent=old.Parent;next.Modules=old.Modules;next.Includes=old.Includes;next.Requires=old.Requires;next.Defaults=old.Defaults;next.Provides=old.Provides;next.Uses=old.Uses;next.Contains=old.Contains;next.Imports=old.Imports;
   if(old.Description!=next.Description||old.DescriptionPresent!=next.DescriptionPresent)Add("설명",old.DescriptionPresent?JsonValue.Create(old.Description):null,next.DescriptionPresent?JsonValue.Create(next.Description):null,old.DescriptionPresent,next.DescriptionPresent);
   foreach(string name in old.Values.Keys.Union(next.Values.Keys)){var a=old.Values.TryGetValue(name,out var av)?JsonNode.Parse(av.Value.GetRawText()):null;var b=next.Values.TryGetValue(name,out var bv)?JsonNode.Parse(bv.Value.GetRawText()):null;if(a is not null&&b is not null&&JsonNode.DeepEquals(a,b)&&a.ToJsonString()!=b.ToJsonString())additional=true;if(old.Values.ContainsKey(name)!=next.Values.ContainsKey(name)||!JsonNode.DeepEquals(a,b))Add("값 · "+name,a,b,old.Values.ContainsKey(name),next.Values.ContainsKey(name));}
   foreach(string name in old.Data.Keys.Union(next.Data.Keys)){var a=old.Data.TryGetValue(name,out var av)?Datum(av):null;var b=next.Data.TryGetValue(name,out var bv)?Datum(bv):null;if(a is not null&&b is not null&&JsonNode.DeepEquals(a,b)&&a.ToJsonString()!=b.ToJsonString())additional=true;if(old.Data.ContainsKey(name)!=next.Data.ContainsKey(name)||!JsonNode.DeepEquals(a,b))Add("필드 값 · "+name,a,b,old.Data.ContainsKey(name),next.Data.ContainsKey(name));}
   foreach(string name in old.Fields.Keys.Union(next.Fields.Keys)){JsonNode? Field(SchemaField? f)=>f is null?null:JsonValue.Create(f.Type+" · "+f.Kind+" · "+f.Cardinality);var a=Field(old.Fields.GetValueOrDefault(name));var b=Field(next.Fields.GetValueOrDefault(name));if(!JsonNode.DeepEquals(a,b))Add("필드 정의 · "+name,a,b,old.Fields.ContainsKey(name),next.Fields.ContainsKey(name));}
   additional|=!old.Values.Keys.Where(k=>next.Values.ContainsKey(k)).SequenceEqual(next.Values.Keys.Where(k=>old.Values.ContainsKey(k)))||!old.Data.Keys.Where(k=>next.Data.ContainsKey(k)).SequenceEqual(next.Data.Keys.Where(k=>old.Data.ContainsKey(k)))||!old.Fields.Keys.Where(k=>next.Fields.ContainsKey(k)).SequenceEqual(next.Fields.Keys.Where(k=>old.Fields.ContainsKey(k)));next.Description=old.Description;next.DescriptionPresent=old.DescriptionPresent;next.Values=old.Values;next.Data=old.Data;next.Fields=old.Fields;
   additional|=Format(next)!=Format(old)||Comments(before)!=Comments(after);
  }
 }catch{additional=true;}
 if(changes.Count==0&&before!=after)additional=true;
 return new JsonObject{["changes"]=changes,["additionalChanges"]=additional};
}

}

internal static class DeclaredRelations
{
 public static JsonObject Describe(Element e)
 {
  var rows=new System.Collections.Generic.List<(string Role,string Target,string? Function,string? Kind,string? Alias,string? Scope,FunctionSignature? Signature)>();
  void Add(string role,string target,string? function=null,string? kind=null,string? alias=null,string? scope=null,FunctionSignature? signature=null)=>rows.Add((role,target,function,kind,alias,scope,signature));
  if(e.Parent is not null)Add("parent",e.Parent);
  foreach(var r in e.Modules)Add("module",r.Id);
  foreach(var r in e.Includes)Add("include",r.Id);
  foreach(var r in e.Requires)Add("require",r.Key,signature:r.Value.Signature);
  foreach(var r in e.Defaults)Add("default",r.Value.Id,r.Key);
  foreach(var r in e.Provides)Add("provide",r.Value.Id,r.Key);
  foreach(var r in e.Uses)Add("use",r.Id,kind:r.Kind);
  foreach(var r in e.Contains)Add("contain",r.Id,kind:r.Kind);
  foreach(var r in e.Imports)Add("import",r.Value.Id,kind:"function",alias:r.Key,scope:r.Value.Scope,signature:r.Value.Signature);
  foreach(var f in e.Fields.Where(x=>x.Value.Kind!="general"))Add("field",f.Value.Type,kind:f.Value.Kind=="function"?"function":"schema",alias:f.Key);
  void Datum(SchemaDatum d){if(d.Reference is not null)Add("data",d.Reference);if(d.Items is not null)foreach(var i in d.Items)Datum(i);if(d.Members is not null)foreach(var m in d.Members.Values)Datum(m);}
  foreach(var d in e.Data.Values)Datum(d);
  var edges=new JsonArray();
  foreach(var r in rows.OrderBy(x=>x.Role,StringComparer.Ordinal).ThenBy(x=>x.Target,StringComparer.Ordinal).ThenBy(x=>x.Function,StringComparer.Ordinal).ThenBy(x=>x.Kind,StringComparer.Ordinal).ThenBy(x=>x.Alias,StringComparer.Ordinal))
  {
   var edge=new JsonObject{["role"]=r.Role,["target"]=r.Target,["function"]=r.Function};
   if(r.Kind is not null)edge["kind"]=r.Kind;
   if(r.Role=="import"){edge["alias"]=r.Alias;edge["scope"]=r.Scope;}
   if(r.Signature is not null)edge["signature"]=System.Text.Json.JsonSerializer.SerializeToNode(r.Signature);
   edges.Add(edge);
  }
  return new JsonObject{["scope"]="declared",["owner"]=e.Id,["edges"]=edges};
 }
}

internal static class RelationLocators
{
 public static System.Text.Json.Nodes.JsonObject Query(string text,string root,string[] ids,Func<string,string> read)
 {
  if(text.Length>1048576||ids.Length>256)throw new ArgumentException("Locator query budget exceeded.");
  var rows=new System.Text.Json.Nodes.JsonArray();var manifests=new System.Collections.Generic.Dictionary<string,(Confectory.Core.Manifest? Manifest,string Reason)>(StringComparer.Ordinal);
  Confectory.Core.Manifest? owner=null;try{owner=new Confectory.Core.Parser(text,"<draft-manifest>").ParseManifest();}catch{ }
  foreach(string id in System.Linq.Enumerable.OrderBy(System.Linq.Enumerable.Distinct(ids,StringComparer.Ordinal),x=>x,StringComparer.Ordinal))
  {
   string status="unavailable",reason="project-manifest-invalid";bool? registered=null;string? kind=null;
   try
   {
    new Confectory.Core.Parser("object "+id+" {}","<locator-query>").ParseElement();
    if(owner is not null)
    {
     int split=id.IndexOf("::",StringComparison.Ordinal);string ns=id[..split],local=id[(split+2)..];Confectory.Core.Manifest? chosen=null;
     if(ns==owner.Namespace){registered=true;chosen=owner;reason="";}
     else if(!owner.Registry.TryGetValue(ns,out var locator)){registered=false;status="unregistered";reason="namespace-not-registered";}
     else
     {
      registered=true;
      if(!manifests.TryGetValue(ns,out var cached))
      {
       try{string content=read(System.IO.Path.GetFullPath(System.IO.Path.Combine(root,locator.Path)));if(content.Length>1048576)throw new ArgumentException();var m=new Confectory.Core.Parser(content,"<registered-manifest>").ParseManifest();cached=m.Namespace==ns&&m.Kind=="pack"?(m,""):(null,"manifest-identity-mismatch");}
       catch{cached=(null,"manifest-unavailable");}
       manifests.Add(ns,cached);
      }
      chosen=cached.Manifest;reason=cached.Reason;
     }
     if(chosen is not null){if(chosen.Elements.TryGetValue(local,out var element)){status="registered";reason="locator-present";kind=element.Kind;}else{status="unregistered";reason="element-not-declared";}}
    }
   }
   catch{reason="invalid-qualified-id";}
   rows.Add(new System.Text.Json.Nodes.JsonObject{["id"]=id,["status"]=status,["namespaceRegistered"]=registered,["kind"]=kind,["reason"]=reason});
  }
  return new System.Text.Json.Nodes.JsonObject{["scope"]="manifest-locators",["projectNamespace"]=owner?.Namespace,["targets"]=rows};
 }
}

internal static class EffectiveMetadata
{
 public static System.Text.Json.Nodes.JsonObject Query(string project,string manifestText,string id,string text,Func<Confectory.Core.Manifest,string> format,Func<string,string> read,System.Text.Json.Nodes.JsonArray? drafts=null,bool schemaView=false)
 {
  string temporary=System.IO.Path.Combine(System.IO.Path.GetTempPath(),"confectory-effective-"+Guid.NewGuid().ToString("N"));
  try
  {
   if(manifestText.Length>1048576||text.Length>1048576)throw new ArgumentException("Effective metadata budget exceeded.");
   string root=System.IO.Path.GetDirectoryName(System.IO.Path.GetFullPath(project))!;
   var manifest=new Confectory.Core.Parser(manifestText,"<draft-manifest>").ParseManifest();
   if(!id.StartsWith(manifest.Namespace+"::",StringComparison.Ordinal))throw new ArgumentException("Selected draft must belong to the root owner namespace.");
   string local=id[(manifest.Namespace.Length+2)..];if(!manifest.Elements.TryGetValue(local,out var locator))throw new ArgumentException("Selected declaration has no owned locator.");
   string path=Confectory.Core.PackPaths.Owned(root,locator.Path);var selected=new Confectory.Core.Parser(text,path).ParseElement();
   if(selected.Id!=id||selected.Kind!=locator.Kind)throw new ArgumentException("Selected draft identity/kind mismatch.");
   foreach(var ns in manifest.Registry.Keys.ToArray())
   {
    var registration=manifest.Registry[ns];string registered=System.IO.Path.GetFullPath(System.IO.Path.Combine(root,registration.Path));read(registered);
    manifest.Registry[ns]=registration with{Path=registered};
   }
   string sourceKind=manifest.Kind;manifest.Kind="project";
   System.IO.Directory.CreateDirectory(temporary);string candidate=System.IO.Path.Combine(temporary,"project.cpack");System.IO.File.WriteAllText(candidate,format(manifest));
   var statistics=new Confectory.Core.BuildStatistics();var registry=new Confectory.Core.Registry(candidate,new Confectory.Core.Documents(System.IO.Path.Combine(temporary,"cache"),statistics),statistics);
   registry.Paths[manifest.Namespace]=System.IO.Path.GetFullPath(project);
   // Public per-query declaration cache overlays only this explicitly owned draft.
   registry.Elements[id]=selected;var overlayIds=new System.Collections.Generic.HashSet<string>(StringComparer.Ordinal){id};int budget=text.Length;
   foreach(var item in drafts??new System.Text.Json.Nodes.JsonArray()){
    string ownedId=item!["id"]!.GetValue<string>(),source=item["text"]!.GetValue<string>();budget+=source.Length;
    if(budget>1048576||overlayIds.Count>=256||!ownedId.StartsWith(manifest.Namespace+"::",StringComparison.Ordinal)||!overlayIds.Add(ownedId))throw new ArgumentException("Owned draft overlay budget/identity mismatch.");
    if(!manifest.Elements.TryGetValue(ownedId[(manifest.Namespace.Length+2)..],out var ownedLocator))throw new ArgumentException("Draft overlay locator missing.");
    var owned=new Confectory.Core.Parser(source,Confectory.Core.PackPaths.Owned(root,ownedLocator.Path)).ParseElement();if(owned.Id!=ownedId||owned.Kind!=ownedLocator.Kind)throw new ArgumentException("Draft overlay identity/kind mismatch.");registry.Elements[ownedId]=owned;
   }
   var effective=registry.Effective(id);var descriptionSource=selected;while(!descriptionSource.DescriptionPresent&&descriptionSource.Parent is not null)descriptionSource=registry.Get(descriptionSource.Parent,descriptionSource.Kind,descriptionSource.Id,descriptionSource.Loc);
var planner=new Confectory.Core.Planner(registry,"metadata");
   var module=effective.Kind=="module"?planner.Module(id):planner.ModulesFor(id);
   var values=new System.Text.Json.Nodes.JsonArray();foreach(var pair in effective.Values.OrderBy(p=>p.Key,StringComparer.Ordinal))values.Add(new System.Text.Json.Nodes.JsonObject{["field"]=pair.Key,["value"]=System.Text.Json.JsonSerializer.SerializeToNode(pair.Value.Value),["origin"]=pair.Value.Origin});
   var requirements=new System.Text.Json.Nodes.JsonArray();foreach(var pair in module.Required.OrderBy(p=>p.Key,StringComparer.Ordinal))
   {
    var defaults=new System.Text.Json.Nodes.JsonArray();if(module.Defaults.TryGetValue(pair.Key,out var choices))foreach(var choice in choices.OrderBy(p=>p.Key,StringComparer.Ordinal))defaults.Add(new System.Text.Json.Nodes.JsonObject{["implementation"]=choice.Key,["origin"]=choice.Value.Origin});
    requirements.Add(new System.Text.Json.Nodes.JsonObject{["function"]=pair.Key,["signature"]=System.Text.Json.JsonSerializer.SerializeToNode(pair.Value.Signature),["origin"]=pair.Value.Origin,["defaults"]=defaults});
   }
   var providers=new System.Text.Json.Nodes.JsonArray();foreach(var pair in effective.Provides.OrderBy(p=>p.Key,StringComparer.Ordinal))providers.Add(new System.Text.Json.Nodes.JsonObject{["function"]=pair.Key,["implementation"]=pair.Value.Id,["origin"]=pair.Value.Origin});
   var modules=new System.Text.Json.Nodes.JsonArray();foreach(var reference in effective.Modules)modules.Add(new System.Text.Json.Nodes.JsonObject{["id"]=reference.Id,["origin"]=reference.Origin});
   var schemaFields=effective.Kind=="object"?Confectory.Core.SchemaContracts.Fields(registry,id):effective.Fields;
   var functionContracts=new System.Text.Json.Nodes.JsonObject();foreach(var pair in schemaFields.Where(p=>p.Value.Kind=="function")){var fn=registry.Get(pair.Value.Type,"function",pair.Value.Origin,pair.Value.Loc);functionContracts[pair.Key]=new System.Text.Json.Nodes.JsonObject{["id"]=fn.Id,["signature"]=System.Text.Json.JsonSerializer.SerializeToNode(fn.Signature)};}
   var schemaModel=schemaView?SchemaModel(registry,effective,schemaFields):null;
   return new System.Text.Json.Nodes.JsonObject{["scope"]="effective-metadata",["status"]="available",["id"]=id,["description"]=effective.Description,["descriptionOrigin"]=descriptionSource.DescriptionPresent?descriptionSource.Id:null,["sourceKind"]=sourceKind,["fields"]=System.Text.Json.JsonSerializer.SerializeToNode(schemaFields),["functionContracts"]=functionContracts,["schemaModel"]=schemaModel,["data"]=System.Text.Json.JsonSerializer.SerializeToNode(effective.Data),["values"]=values,["modules"]=modules,["requirements"]=requirements,["providers"]=providers,["providerSelection"]="not-performed",["declarationsLoaded"]=System.Text.Json.JsonSerializer.SerializeToNode(registry.Elements.Keys.Order(StringComparer.Ordinal).ToArray()),["registeredManifests"]=registry.Packs.Count,["bodyReads"]=statistics.ReadDocuments.Count(path=>registry.Elements.Values.Any(e=>e.Bodies.Values.Any(b=>Confectory.Core.PackPaths.Owned(System.IO.Path.GetDirectoryName(e.Loc.File)!,b.Path)==path))),["draftOverlayIDs"]=System.Text.Json.JsonSerializer.SerializeToNode(overlayIds.Order(StringComparer.Ordinal).ToArray()),["dependencySource"]="root-owned-drafts-and-confirmed-registered-files"};
  }
  catch(Confectory.Core.BuildError error){return new System.Text.Json.Nodes.JsonObject{["scope"]="effective-metadata",["status"]="unavailable",["id"]=id,["code"]=error.Diagnostic.Code,["message"]=error.Diagnostic.Message};}
  catch(Exception error){return new System.Text.Json.Nodes.JsonObject{["scope"]="effective-metadata",["status"]="unavailable",["id"]=id,["code"]="METADATA_UNAVAILABLE",["message"]=error.Message};}
  finally{if(System.IO.Directory.Exists(temporary))System.IO.Directory.Delete(temporary,true);}
 }
 static System.Text.Json.Nodes.JsonObject SchemaModel(Confectory.Core.Registry registry,Confectory.Core.Element element,System.Collections.Generic.Dictionary<string,Confectory.Core.SchemaField> fields)
 {
  var schemas=new System.Text.Json.Nodes.JsonObject();var functions=new System.Text.Json.Nodes.JsonObject();var implementations=new System.Text.Json.Nodes.JsonObject();
  System.Text.Json.Nodes.JsonNode Fields(System.Collections.Generic.Dictionary<string,Confectory.Core.SchemaField> items)=>Confectory.Core.JsonData.Object(items.ToDictionary(p=>p.Key,p=>new{cardinality=p.Value.Cardinality,kind=p.Value.Kind,type=p.Value.Type,origin=p.Value.Origin}));
  void Contracts(System.Collections.Generic.Dictionary<string,Confectory.Core.SchemaField> items)
  {
   foreach(var field in items.Values){
    if(field.Kind=="function"){var fn=registry.Get(field.Type,"function",field.Origin,field.Loc);functions[fn.Id]=System.Text.Json.JsonSerializer.SerializeToNode(fn.Signature,Confectory.Core.JsonData.Options);}
    else if(field.Kind=="compound"){
     if(schemas.ContainsKey(field.Type))continue;
     new Confectory.Core.Planner(registry,"metadata").Structural(field.Type);var schema=registry.Effective(registry.Get(field.Type,"schema",field.Origin,field.Loc).Id);
     schemas[field.Type]=new System.Text.Json.Nodes.JsonObject{["fields"]=Fields(schema.Fields)};Contracts(schema.Fields);
    }
   }
  }
  void Associations(System.Collections.Generic.Dictionary<string,Confectory.Core.SchemaField> items,System.Collections.Generic.Dictionary<string,Confectory.Core.SchemaDatum> data)
  {
   foreach(var pair in items){if(!data.TryGetValue(pair.Key,out var datum))continue;var field=pair.Value;
    foreach(var value in field.Cardinality=="multiple"?(datum.Items??[]):new System.Collections.Generic.List<Confectory.Core.SchemaDatum>{datum}){
     if(field.Kind=="compound"&&value.Members is not null)Associations(registry.Effective(field.Type).Fields,value.Members);
     if(field.Kind!="function"||value.Reference is null)continue;
     string key=System.Text.Json.JsonSerializer.Serialize(new[]{field.Type,value.Reference,value.Origin});
     try{var body=registry.Implementation(field.Type,value.Reference,value.Origin,value.Loc);implementations[key]=new System.Text.Json.Nodes.JsonObject{["status"]="valid",["id"]=body.Id,["function"]=body.Function,["targets"]=System.Text.Json.JsonSerializer.SerializeToNode(body.Bodies.Keys.Order(StringComparer.Ordinal).ToArray())};}
     catch(Confectory.Core.BuildError error){implementations[key]=new System.Text.Json.Nodes.JsonObject{["status"]="invalid",["code"]=error.Diagnostic.Code,["message"]=error.Message};}
    }
   }
  }
  Contracts(fields);Associations(fields,element.Data);
  System.Text.Json.Nodes.JsonObject validation;
  try{Confectory.Core.SchemaContracts.Validate(registry,element.Id);validation=new System.Text.Json.Nodes.JsonObject{["status"]="valid"};}
  catch(Confectory.Core.BuildError error){validation=new System.Text.Json.Nodes.JsonObject{["status"]="invalid",["code"]=error.Diagnostic.Code,["message"]=error.Message};}
  return new System.Text.Json.Nodes.JsonObject{["id"]=element.Id,["kind"]=element.Kind,["validation"]=validation,["fields"]=Fields(fields),["data"]=System.Text.Json.JsonSerializer.SerializeToNode(element.Data,Confectory.Core.JsonData.Options),["schemas"]=schemas,["functions"]=functions,["implementations"]=implementations,["targets"]=System.Text.Json.JsonSerializer.SerializeToNode(registry.Project.Targets.Keys.Order(StringComparer.Ordinal).ToArray()),["executionAuthorized"]=false};
 }

}

internal static class SemanticCatalogService
{
 public static System.Text.Json.Nodes.JsonObject Query(string project,System.Text.Json.Nodes.JsonObject request,Func<string,string> scope)
 {
  try{
   project=scope(System.IO.Path.GetFullPath(project));string root=System.IO.Path.GetDirectoryName(project)!;
   var statistics=new Confectory.Core.BuildStatistics();string cache=System.IO.Path.Combine(System.IO.Path.GetTempPath(),"confectory-semantic-catalog-v1",Confectory.Core.JsonData.Digest(project));
   var documents=new Confectory.Core.Documents(cache,statistics);var manifest=documents.Manifest(project);
   string action=request["action"]?.GetValue<string>()??"list",query=request["query"]?.GetValue<string>()??"",kind=request["kind"]?.GetValue<string>()??"";
   if(query.Length>256||kind.Length>64)throw new ArgumentException("Catalog filter budget exceeded.");
   var result=new System.Text.Json.Nodes.JsonObject{["status"]="available",["scope"]="owned-declarations",["sourceScope"]="confirmed-files",["namespace"]=manifest.Namespace,["version"]=manifest.Version,["metadataVersion"]=Confectory.Core.JsonData.Digest(manifest)};
   if(action=="list"){
    int page=request["page"]?.GetValue<int>()??0;if(page<0)throw new ArgumentOutOfRangeException("page");
    var rows=manifest.Elements.Where(e=>(manifest.Namespace+"::"+e.Key).Contains(query,StringComparison.OrdinalIgnoreCase)&&(kind.Length==0||e.Value.Kind==kind)).OrderBy(e=>e.Key,StringComparer.Ordinal).ToArray();
    page=Math.Min(page,Math.Max(0,(rows.Length-1)/32));var units=new System.Text.Json.Nodes.JsonArray();foreach(var row in rows.Skip(page*32).Take(32))units.Add(new System.Text.Json.Nodes.JsonObject{["id"]=manifest.Namespace+"::"+row.Key,["kind"]=row.Value.Kind});
    result["query"]=query;result["kind"]=kind;result["page"]=page;result["pageSize"]=32;result["total"]=rows.Length;result["units"]=units;
   }else if(action=="read"){
    string id=request["id"]!.GetValue<string>();if(!id.StartsWith(manifest.Namespace+"::",StringComparison.Ordinal))throw new ArgumentException("Catalog read requires selected owner namespace.");
    if(!manifest.Elements.TryGetValue(id[(manifest.Namespace.Length+2)..],out var locator))throw new ArgumentException("No owned declaration locator.");
    var element=documents.Element(scope(Confectory.Core.PackPaths.Owned(root,locator.Path)));if(element.Id!=id||element.Kind!=locator.Kind)throw new ArgumentException("Declaration locator identity/kind mismatch.");
    result["element"]=new System.Text.Json.Nodes.JsonObject{["id"]=element.Id,["kind"]=element.Kind,["parent"]=element.Parent,["description"]=element.Description,["signature"]=System.Text.Json.JsonSerializer.SerializeToNode(element.Signature),["fields"]=System.Text.Json.JsonSerializer.SerializeToNode(element.Fields),["data"]=System.Text.Json.JsonSerializer.SerializeToNode(element.Data),["values"]=System.Text.Json.JsonSerializer.SerializeToNode(element.Values.ToDictionary(x=>x.Key,x=>x.Value.Value)),["relations"]=DeclaredRelations.Describe(element),["metadataVersion"]=Confectory.Core.JsonData.Digest(element)};
   }else throw new ArgumentException("Unknown catalog operation.");
   result["reads"]=new System.Text.Json.Nodes.JsonObject{["manifest"]=statistics.ReadDocuments.Count(p=>p==project),["declarations"]=statistics.ReadDocuments.Count(p=>p!=project),["paths"]=System.Text.Json.JsonSerializer.SerializeToNode(statistics.ReadDocuments.Select(p=>System.IO.Path.GetRelativePath(root,p)).ToArray())};return result;
  }
  catch(Confectory.Core.BuildError error){return new System.Text.Json.Nodes.JsonObject{["status"]="unavailable",["scope"]="owned-declarations",["code"]=error.Diagnostic.Code,["message"]=error.Diagnostic.Message};}
  catch(Exception error){return new System.Text.Json.Nodes.JsonObject{["status"]="unavailable",["scope"]="owned-declarations",["code"]="CATALOG_UNAVAILABLE",["message"]=error.Message};}
 }
}

internal static class BodyUnitMetadata
{
 public static JsonObject Query(JsonObject request)
 {
 string root=Path.GetDirectoryName(Path.GetFullPath(request["project"]!.GetValue<string>()))!;
 string declaration=PackPaths.Owned(root,request["path"]!.GetValue<string>());
 string text=request["text"]!.GetValue<string>();if(text.Length>1048576)throw new ArgumentException("Declaration budget");
 var element=new Parser(text,declaration).ParseElement();if(element.Kind!="implementation"||element.Id!=request["id"]!.GetValue<string>())throw new ArgumentException("Owned implementation identity required.");
 if(element.Bodies.Count>256)throw new ArgumentException("Body locator budget");
 var units=new JsonArray();foreach(var item in element.Bodies.OrderBy(x=>x.Key,StringComparer.Ordinal)){
 string body=PackPaths.Owned(root,Path.GetRelativePath(root,Path.Combine(Path.GetDirectoryName(declaration)!,item.Value.Path)));
 units.Add(new JsonObject{["id"]=element.Id+"/body:"+item.Key,["kind"]=item.Value.SourceKind=="blueprint"?"blueprint":"body",["target"]=item.Key,["path"]=Path.GetRelativePath(root,body)});
 if(item.Value.SourceKind=="blueprint")foreach(var node in BlueprintDocuments.NodeUnits(root,body,element.Id+"/body:"+item.Key,request["blueprintDrafts"]?[element.Id+"/body:"+item.Key]?.GetValue<string>()))units.Add(node!.DeepClone());}
 return new JsonObject{["implementation"]=element.Id,["units"]=units};
 }
}

internal static class ConnectionDeclarations
{
 public static System.Text.Json.Nodes.JsonObject Query(string project,string? selected,Func<Confectory.Core.Manifest,string> format,Func<string,string> scope)
 {
 project=scope(System.IO.Path.GetFullPath(project));string root=System.IO.Path.GetDirectoryName(project)!;
 var stats=new Confectory.Core.BuildStatistics();var docs=new Confectory.Core.Documents(System.IO.Path.Combine(System.IO.Path.GetTempPath(),"confectory-connection-metadata-v1",Confectory.Core.JsonData.Digest(project)),stats);var registry=new Confectory.Core.Registry(project,docs,stats);
 var rows=new System.Text.Json.Nodes.JsonArray();foreach(var pack in registry.Packs.OrderBy(p=>p.Key,StringComparer.Ordinal))foreach(var item in pack.Value.Elements.OrderBy(p=>p.Key,StringComparer.Ordinal)){
 if(item.Value.Kind!="object")continue;string id=pack.Key+"::"+item.Key;if(id=="Confectory.AIConnection::Connection")continue;
 string path=scope(Confectory.Core.PackPaths.Owned(System.IO.Path.GetDirectoryName(registry.Paths[pack.Key])!,item.Value.Path));var element=registry.Get(id);var current=element;var seen=new System.Collections.Generic.HashSet<string>(StringComparer.Ordinal);bool connection=false;
 while(current.Parent is string parent){if(!seen.Add(parent))throw new ArgumentException("Connection inheritance cycle");if(parent=="Confectory.AIConnection::Connection"){connection=true;break;}current=registry.Get(parent);}
 if(!connection)continue;if(rows.Count>=32)throw new ArgumentException("Connection catalogue bound");var effective=registry.Effective(id);var fields=Confectory.Core.SchemaContracts.Fields(registry,id);if(fields.Keys.Any(k=>System.Text.RegularExpressions.Regex.IsMatch(k,"apiKey|password|accessToken|refreshToken|secret",System.Text.RegularExpressions.RegexOptions.IgnoreCase)))throw new ArgumentException("Secrets cannot be ordinary connection schema fields");
 var values=new System.Text.Json.Nodes.JsonObject();foreach(var key in new[]{"transport","authentication","desktopSupported","browserSupported","androidSupported","functionTools","unsupportedReason","liveVerified"})if(effective.Values.TryGetValue(key,out var value))values[key]=System.Text.Json.JsonSerializer.SerializeToNode(value.Value);
 rows.Add(new System.Text.Json.Nodes.JsonObject{["id"]=id,["pack"]=pack.Key,["fields"]=System.Text.Json.JsonSerializer.SerializeToNode(fields),["capabilities"]=values});
 }
 if(selected is null)return new System.Text.Json.Nodes.JsonObject{["connections"]=rows,["bodyReads"]=stats.ReadDocuments.Count(path=>path.EndsWith(".csbody",StringComparison.Ordinal)),["executionPerformed"]=false};
 if(!rows.Any(row=>row!["id"]!.ToString()==selected))throw new ArgumentException("Select a declared registered connection descendant");
 var manifest=docs.Manifest(project);manifest.Namespace="Confectory.AISettings";manifest.Kind="project";manifest.Standalone=false;manifest.Entry=null;manifest.Targets.Clear();manifest.Always.Clear();manifest.Elements.Clear();foreach(string ns in manifest.Registry.Keys.ToArray()){var registration=manifest.Registry[ns];manifest.Registry[ns]=registration with{Path=System.IO.Path.GetFullPath(System.IO.Path.Combine(root,registration.Path))};}manifest.Elements.Add("Settings",new Confectory.Core.Locator("object","Settings.celem",new()));
 return new System.Text.Json.Nodes.JsonObject{["manifest"]=format(manifest),["source"]="object Confectory.AISettings::Settings extends "+selected+" {}\n",["connection"]=selected,["credentialRead"]=false,["executionPerformed"]=false};
 }
}

// Ordinary declaration syntax transformations. The caller owns draft CAS and source publication.
internal static class DeclarationAuthoring
{
 public static void Apply(Element element, JsonObject edit)
 {
  if(edit.ToJsonString().Length>65536)throw new ArgumentException("Declaration edit budget");
  string Text(JsonNode node,string key)=>node[key]?.GetValue<string>()??throw new ArgumentException("Explicit "+key+" required");
  string action=Text(edit,"action");
  string Id(JsonNode node,string key){string id=Text(node,key);if(id.Length>256||!System.Text.RegularExpressions.Regex.IsMatch(id,@"\A[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*::[A-Za-z_][A-Za-z_0-9]*\z",System.Text.RegularExpressions.RegexOptions.CultureInvariant))throw new ArgumentException("Qualified declaration ID required");return id;}
  FunctionSignature Signature(JsonNode node,bool named)
  {
   var args=node["args"]?.AsArray()??throw new ArgumentException("Signature arguments required");if(args.Count>64)throw new ArgumentException("Signature argument budget");
   return new(args.Select((arg,index)=>new Parameter(Text(arg!,"type"),named?Text(arg!,"name"):"arg"+index)).ToList(),Text(node,"return"));
  }
  List<JsonNode> Entries(){var rows=edit["entries"]?.AsArray()??throw new ArgumentException("Relation entries required");if(rows.Count>128)throw new ArgumentException("Relation budget");return rows.Select(row=>row??throw new ArgumentException("Relation entry required")).ToList();}
  ElementReference Reference(JsonNode row,bool typed=false)=>new(Id(row,"id"),new(),element.Id,typed?Text(row,"kind"):null);
  Dictionary<string,T> Unique<T>(IEnumerable<(string Id,T Value)> rows){var result=new Dictionary<string,T>(StringComparer.Ordinal);foreach(var row in rows)if(!result.TryAdd(row.Id,row.Value))throw new ArgumentException("Duplicate declaration edit entry");return result;}
  (Dictionary<string,SchemaDatum>? Members,List<SchemaDatum>? Items,JsonNode Segment) Parent(JsonArray path)
  {
   if(element.Kind!="object"||path.Count<1||path.Count>64)throw new ArgumentException("Bounded local object data path required");
   Dictionary<string,SchemaDatum>? members=element.Data;List<SchemaDatum>? items=null;
   for(int i=0;i<path.Count-1;i++){
    SchemaDatum datum;if(members is not null&&path[i] is JsonValue member&&member.TryGetValue<string>(out var key)&&members.TryGetValue(key,out var found))datum=found;
    else if(items is not null&&path[i] is JsonValue index&&index.TryGetValue<int>(out int n)&&n>=0&&n<items.Count)datum=items[n];
    else throw new ArgumentException("Path has no local override; inherited data is not copied");
    members=datum.Members;items=datum.Items;
   }
   return(members,items,path[^1]??throw new ArgumentException("Path segment required"));
  }
  switch(action){
   case "properties":{
    var values=edit["values"]?.AsObject()??throw new ArgumentException("Explicit declaration properties required");if(values.Count<1||values.Count>4)throw new ArgumentException("Properties budget");
    foreach(var pair in values){
     if(pair.Key=="parent"){element.Parent=pair.Value is null?null:Id(values,"parent");continue;}
     string value=pair.Value?.GetValue<string>()??throw new ArgumentException("Property string required");
     if(pair.Key=="description"){if(value.Length>16384)throw new ArgumentException("Description budget");element.Description=value;element.DescriptionPresent=true;}
     else if(pair.Key is "displayName" or "icon"){if(value.Length>(pair.Key=="displayName"?256:64))throw new ArgumentException("Display metadata budget");element.Values[pair.Key=="displayName"?"editorName":"editorIcon"]=new(System.Text.Json.JsonSerializer.SerializeToElement(value),element.Id,new());}
     else throw new ArgumentException("Supported declaration property required");
    }break;
   }
   case "signature":if(element.Kind is not ("function" or "implementation"))throw new ArgumentException("Public function signature required");element.Signature=Signature(edit["value"]??throw new ArgumentException("Signature required"),true);break;
   case "parent":if(!edit.ContainsKey("value"))throw new ArgumentException("Explicit parent value required");element.Parent=edit["value"] is null?null:Id(edit,"value");break;
   case "relations":{
    string role=Text(edit,"role");var rows=Entries();
    switch(role){
     case "module":element.Modules=rows.Select(r=>Reference(r)).ToList();break;
     case "include":element.Includes=rows.Select(r=>Reference(r)).ToList();break;
     case "use":element.Uses=rows.Select(r=>Reference(r,true)).ToList();break;
     case "contain":element.Contains=rows.Select(r=>Reference(r,true)).ToList();break;
     case "require":element.Requires=Unique(rows.Select(r=>(Id(r,"id"),new RequiredFunction(Signature(r["signature"]??throw new ArgumentException("Required signature required"),false),new(),element.Id))));break;
     case "default":element.Defaults=Unique(rows.Select(r=>(Id(r,"function"),Reference(r))));break;
     case "provide":element.Provides=Unique(rows.Select(r=>(Id(r,"function"),Reference(r))));break;
     case "import":element.Imports=Unique(rows.Select(r=>(Text(r,"alias"),new Import(Id(r,"id"),Signature(r["signature"]??throw new ArgumentException("Import signature required"),false),r["scope"] is null?null:Id(r,"scope"),new(),element.Id))));break;
     default:throw new ArgumentException("Declared relation role required");
    }break;
   }
   case "unset-description":element.Description="";element.DescriptionPresent=false;break;
   case "unset-value":if(!element.Values.Remove(Text(edit,"field")))throw new ArgumentException("No local metadata override");break;
   case "remove-field":if(element.Kind!="schema"||!element.Fields.Remove(Text(edit,"field")))throw new ArgumentException("No local schema field");break;
   case "field-order":{
    var order=edit["order"]?.AsArray().Select(v=>v!.GetValue<string>()).ToArray()??throw new ArgumentException("Field order required");
    if(element.Kind!="schema"||order.Length!=element.Fields.Count||order.Distinct(StringComparer.Ordinal).Count()!=order.Length||order.Any(k=>!element.Fields.ContainsKey(k)))throw new ArgumentException("Exact local field order required");element.Fields=order.ToDictionary(k=>k,k=>element.Fields[k],StringComparer.Ordinal);break;
   }
   case "unset-data":{
    var p=Parent(edit["path"]?.AsArray()??throw new ArgumentException("Data path required"));
    if(p.Members is not null&&p.Segment is JsonValue member&&member.TryGetValue<string>(out var key)&&p.Members.Remove(key))break;
    if(p.Items is not null&&p.Segment is JsonValue index&&index.TryGetValue<int>(out int n)&&n>=0&&n<p.Items.Count){p.Items.RemoveAt(n);break;}
    throw new ArgumentException("Path has no local override");
   }
   case "move-data":{
    var path=edit["path"]?.AsArray()??throw new ArgumentException("Array path required");var p=Parent(path);SchemaDatum datum;
    if(p.Members is not null&&p.Segment is JsonValue member&&member.TryGetValue<string>(out var key)&&p.Members.TryGetValue(key,out var found))datum=found;
    else if(p.Items is not null&&p.Segment is JsonValue index&&index.TryGetValue<int>(out int n)&&n>=0&&n<p.Items.Count)datum=p.Items[n];
    else throw new ArgumentException("Array has no local override");
    int from=edit["from"]?.GetValue<int>()??-1,to=edit["to"]?.GetValue<int>()??-1;
    if(datum.Items is null||from<0||to<0||from>=datum.Items.Count||to>=datum.Items.Count)throw new ArgumentException("Existing local array positions required");var item=datum.Items[from];datum.Items.RemoveAt(from);datum.Items.Insert(to,item);break;
   }
   default:throw new ArgumentException("Supported declaration edit required");
  }
 }
}

internal static class RelationMapBatch
{
    public static JsonObject Query(JsonObject request)
    {
        var units = request["units"]?.AsArray() ?? throw new ArgumentException("Owned map source batch required");
        if (units.Count > 32) throw new ArgumentException("Map source batch budget");
        var nodes = new JsonArray(); var edges = new JsonArray();
        foreach (var source in units)
        {
            string id = source!["id"]!.GetValue<string>(), kind = source["kind"]!.GetValue<string>();
            var node = new JsonObject
            {
                ["id"] = id, ["kind"] = kind, ["title"] = id.Split("::").Last(),
                ["revision"] = source["revision"]!.DeepClone(), ["textHash"] = source["textHash"]!.DeepClone(),
                ["dirty"] = source["dirty"]!.DeepClone(), ["owned"] = true, ["valid"] = false
            };
            try
            {
                var element = new Parser(source["text"]!.GetValue<string>(), "<owned-map-draft>").ParseElement();
                if (element.Id != id || element.Kind != kind) throw new ArgumentException("Map declaration identity differs");
                if (element.Values.TryGetValue("editorName", out var label) && label.Value.ValueKind == System.Text.Json.JsonValueKind.String)
                    node["title"] = label.Value.GetString();
                node["description"] = element.Description;
                node["valid"] = true;
                foreach (var reference in DeclaredRelations.Describe(element)["edges"]!.AsArray())
                {
                    var edge = reference!.DeepClone().AsObject(); edge["source"] = id;
                    edges.Add(edge);
                }
            }
            catch (Exception error) when (error is BuildError or ArgumentException)
            {
                node["error"] = error is BuildError build ? build.Diagnostic.Code : "DECLARATION_IDENTITY";
            }
            nodes.Add(node);
        }
        return new JsonObject { ["nodes"] = nodes, ["edges"] = edges, ["sourceWritten"] = false, ["executed"] = false };
    }
}

// Resolve only the requested, directly declared reference. No provider selection,
// transitive registry traversal, implementation body read or editable owner is opened.
internal static class ReferenceDefinition
{
 public static JsonObject Query(string project,string manifestText,string sourceId,string sourceText,string id,Func<string,string> read)
 {
  JsonObject Unavailable(string code)=>new(){["scope"]="declared-reference-definition",["status"]="unavailable",["id"]=id,["sourceId"]=sourceId,["readOnly"]=true,["code"]=code};
  string Hash(string text)=>Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(text))).ToLowerInvariant();
  string Read(string path){string content=read(path);if(content.Length>1048576)throw new ArgumentException("Definition budget");return content;}
  try
  {
   if(manifestText.Length>1048576||sourceText.Length>1048576)throw new ArgumentException("Definition budget");
   var owner=new Parser(manifestText,"<owned-manifest>").ParseManifest();var source=new Parser(sourceText,"<owned-reference>").ParseElement();
   if(source.Id!=sourceId||PackPaths.Namespace(sourceId)!=owner.Namespace)return Unavailable("REFERENCE_OWNER_MISMATCH");
   if(!owner.Elements.TryGetValue(sourceId[(owner.Namespace.Length+2)..],out var sourceLocator)||sourceLocator.Kind!=source.Kind)return Unavailable("REFERENCE_OWNER_MISMATCH");
   new Parser("object "+id+" {}","<reference-id>").ParseElement();
   var edges=DeclaredRelations.Describe(source)["edges"]!.AsArray();
   if(!edges.Any(edge=>new[]{"target","function","scope"}.Any(key=>edge![key]?.ToString()==id)))return Unavailable("NOT_DECLARED_REFERENCE");
   string ns=PackPaths.Namespace(id);if(ns==owner.Namespace)return Unavailable("USE_OWNED_VIEW");
   if(!owner.Dependencies.ContainsKey(ns))return Unavailable("UNDECLARED_DEPENDENCY");
   if(!owner.Registry.TryGetValue(ns,out var registration))return Unavailable("UNREGISTERED_NAMESPACE");
   string root=Path.GetDirectoryName(Path.GetFullPath(project))!,manifestPath=PackPaths.Resolve(Path.Combine(root,registration.Path));
   string registeredText=Read(manifestPath);var pack=new Parser(registeredText,"<registered-manifest>").ParseManifest();
   if(pack.Kind!="pack"||pack.Namespace!=ns)return Unavailable("REGISTRY_IDENTITY_MISMATCH");
   string local=id[(ns.Length+2)..];if(!pack.Elements.TryGetValue(local,out var locator))return Unavailable("ELEMENT_NOT_DECLARED");
   string path=PackPaths.Owned(Path.GetDirectoryName(manifestPath)!,locator.Path);string text=Read(path);var element=new Parser(text,"<registered-definition>").ParseElement();
   if(element.Id!=id||element.Kind!=locator.Kind)return Unavailable("LOCATOR_IDENTITY_MISMATCH");
   if(Read(manifestPath)!=registeredText||Read(path)!=text)return Unavailable("DEFINITION_CHANGED_DURING_READ");
   return new(){["scope"]="declared-reference-definition",["status"]="available",["id"]=id,["sourceId"]=sourceId,["kind"]=element.Kind,["namespace"]=ns,["version"]=pack.Version,["readOnly"]=true,["origin"]="confirmed-registered-file",["text"]=text,["textHash"]=Hash(text),["manifestHash"]=Hash(registeredText),["ownerManifestHash"]=Hash(manifestText),["sourceHash"]=Hash(sourceText)};
  }
  catch(BuildError error){return Unavailable(error.Diagnostic.Code);}
  catch{return Unavailable("DEFINITION_UNAVAILABLE");}
 }
}
