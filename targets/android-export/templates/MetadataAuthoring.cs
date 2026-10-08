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
 if(operation=="catalog")return SemanticCatalogService.Query(S("project"),request["request"]!.AsObject(),path=>{string owned=PackPaths.Owned(ownerRoot,Path.GetRelativePath(ownerRoot,path));var file=new FileInfo(owned);if(!file.Exists||file.Length>1048576)throw new IOException("Owned document unavailable");return owned;}).ToJsonString();
 if(operation=="effective"){
 string selected=PackPaths.Owned(ownerRoot,Path.GetRelativePath(ownerRoot,Path.GetFullPath(S("project"))));
 return EffectiveMetadata.Query(selected,S("manifest"),S("id"),S("text"),FormatManifest,path=>Read(PackPaths.Owned(ownerRoot,Path.GetRelativePath(ownerRoot,path))),request["drafts"]?.AsArray()).ToJsonString();
 }
 if(operation=="locate"){
 string selected=PackPaths.Owned(ownerRoot,Path.GetRelativePath(ownerRoot,Path.GetFullPath(S("project"))));
 return RelationLocators.Query(S("manifest"),Path.GetDirectoryName(selected)!,request["ids"]!.AsArray().Select(x=>x!.GetValue<string>()).ToArray(),path=>Read(PackPaths.Owned(ownerRoot,Path.GetRelativePath(ownerRoot,path)))).ToJsonString();
 }
 if(operation=="inspect"){string text=S("text");if(text.Length>1048576)throw new ArgumentException("Declaration budget");var e=new Parser(text,"<draft>").ParseElement();return new JsonObject{["id"]=e.Id,["kind"]=e.Kind,["parent"]=e.Parent,["relations"]=DeclaredRelations.Describe(e),["description"]=e.Description,["signature"]=JsonSerializer.SerializeToNode(e.Signature),["values"]=JsonSerializer.SerializeToNode(e.Values.ToDictionary(x=>x.Key,x=>x.Value.Value))}.ToJsonString();}

 if(operation=="create"){string kind=S("kind"),id=S("id");if(kind is not ("category" or "concept" or "function" or "module" or "object" or "schema"))throw new ArgumentException("Unsupported authored kind");string text=kind+" "+id+(kind=="function"?" () -> int":"")+" { }\n";new Parser(text,"<new>").ParseElement();return JsonSerializer.Serialize(text);}
 if(operation=="setValue"){var element=new Parser(S("text"),"<draft>").ParseElement();var value=JsonSerializer.SerializeToElement(request["value"]);if(value.ValueKind is not (JsonValueKind.String or JsonValueKind.Number or JsonValueKind.True or JsonValueKind.False))throw new ArgumentException("Scalar metadata required");element.Values[S("field")]=new(value,element.Id,new());string text=Format(element);new Parser(text,"<draft>").ParseElement();return JsonSerializer.Serialize(text);}
 if(operation=="register"){var manifest=new Parser(S("text"),"<draft>").ParseManifest();string id=S("id"),path=S("path");if(!id.StartsWith(manifest.Namespace+"::",StringComparison.Ordinal))throw new ArgumentException("Creation belongs to selected namespace");if(Path.IsPathRooted(path)||path.Split('/', '\\').Any(x=>x==".."))throw new ArgumentException("Owned registration path required");manifest.Elements.Add(id[(manifest.Namespace.Length+2)..],new(S("kind"),path,new()));string text=FormatManifest(manifest);new Parser(text,"<draft>").ParseManifest();return JsonSerializer.Serialize(text);}
 if(operation!="describe")throw new PlatformNotSupportedException("This target supports source metadata and draft text only; compiler/Confirm operations require an explicit compiler provider.");
 string project=PackPaths.Owned(ownerRoot,Path.GetRelativePath(ownerRoot,Path.GetFullPath(S("project")))),root=Path.GetDirectoryName(project)!;var m=new Parser(Read(project),project).ParseManifest();var units=new JsonArray();
 units.Add(new JsonObject{["id"]=m.Namespace+(m.Kind=="project"?"::ProjectManifest":"::PackManifest"),["kind"]=m.Kind,["path"]=Path.GetFileName(project)});
 foreach(var item in m.Elements.OrderBy(x=>x.Key,StringComparer.Ordinal)){
 if(units.Count>=256)throw new ArgumentException("Owned source unit budget exceeded");string file=PackPaths.Owned(root,item.Value.Path);var e=new Parser(Read(file),file).ParseElement();if(e.Id!=m.Namespace+"::"+item.Key||e.Kind!=item.Value.Kind)throw new ArgumentException("Owned declaration identity mismatch");
 units.Add(new JsonObject{["id"]=e.Id,["kind"]=e.Kind,["path"]=Path.GetRelativePath(root,file)});
 foreach(var b in e.Bodies.OrderBy(x=>x.Key,StringComparer.Ordinal)){if(units.Count>=256)throw new ArgumentException("Owned source unit budget exceeded");string body=PackPaths.Owned(Path.GetDirectoryName(file)!,b.Value.Path);Read(body);units.Add(new JsonObject{["id"]=e.Id+"/body:"+b.Key,["kind"]= "body",["path"]=Path.GetRelativePath(root,body)});}}
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
    foreach(var (name,value) in element.Values)text.AppendLine("value "+name+" = "+value.Value.GetRawText()+";");
    foreach(var (alias,value) in element.Imports)text.AppendLine("import "+value.Id+" as "+alias+" "+Signature(value.Signature,false)+(value.Scope is null?"":" in "+value.Scope)+";");
    foreach(var (target,value) in element.Bodies)text.AppendLine("body "+target+" "+Quote(value.Path)+";");
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

}

internal static class DeclaredRelations
{
 public static JsonObject Describe(Element e)
 {
  var rows=new System.Collections.Generic.List<(string Role,string Target,string? Function)>();
  if(e.Parent is not null)rows.Add(("parent",e.Parent,null));
  foreach(var r in e.Modules)rows.Add(("module",r.Id,null));
  foreach(var r in e.Includes)rows.Add(("include",r.Id,null));
  foreach(var r in e.Requires)rows.Add(("require",r.Key,null));
  foreach(var r in e.Defaults)rows.Add(("default",r.Value.Id,r.Key));
  foreach(var r in e.Provides)rows.Add(("provide",r.Value.Id,r.Key));
  var edges=new JsonArray();
  foreach(var r in System.Linq.Enumerable.ThenBy(System.Linq.Enumerable.ThenBy(System.Linq.Enumerable.OrderBy(rows,x=>x.Role,StringComparer.Ordinal),x=>x.Target,StringComparer.Ordinal),x=>x.Function,StringComparer.Ordinal))
  {
   var edge=new JsonObject{["role"]=r.Role,["target"]=r.Target,["function"]=r.Function};
   if(r.Role=="require")edge["signature"]=System.Text.Json.JsonSerializer.SerializeToNode(e.Requires[r.Target].Signature);
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
 public static System.Text.Json.Nodes.JsonObject Query(string project,string manifestText,string id,string text,Func<Confectory.Core.Manifest,string> format,Func<string,string> read,System.Text.Json.Nodes.JsonArray? drafts=null)
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
   var effective=registry.Effective(id);var planner=new Confectory.Core.Planner(registry,"metadata");
   var module=effective.Kind=="module"?planner.Module(id):planner.ModulesFor(id);
   var values=new System.Text.Json.Nodes.JsonArray();foreach(var pair in effective.Values.OrderBy(p=>p.Key,StringComparer.Ordinal))values.Add(new System.Text.Json.Nodes.JsonObject{["field"]=pair.Key,["value"]=System.Text.Json.JsonSerializer.SerializeToNode(pair.Value.Value),["origin"]=pair.Value.Origin});
   var requirements=new System.Text.Json.Nodes.JsonArray();foreach(var pair in module.Required.OrderBy(p=>p.Key,StringComparer.Ordinal))
   {
    var defaults=new System.Text.Json.Nodes.JsonArray();if(module.Defaults.TryGetValue(pair.Key,out var choices))foreach(var choice in choices.OrderBy(p=>p.Key,StringComparer.Ordinal))defaults.Add(new System.Text.Json.Nodes.JsonObject{["implementation"]=choice.Key,["origin"]=choice.Value.Origin});
    requirements.Add(new System.Text.Json.Nodes.JsonObject{["function"]=pair.Key,["signature"]=System.Text.Json.JsonSerializer.SerializeToNode(pair.Value.Signature),["origin"]=pair.Value.Origin,["defaults"]=defaults});
   }
   var providers=new System.Text.Json.Nodes.JsonArray();foreach(var pair in effective.Provides.OrderBy(p=>p.Key,StringComparer.Ordinal))providers.Add(new System.Text.Json.Nodes.JsonObject{["function"]=pair.Key,["implementation"]=pair.Value.Id,["origin"]=pair.Value.Origin});
   var modules=new System.Text.Json.Nodes.JsonArray();foreach(var reference in effective.Modules)modules.Add(new System.Text.Json.Nodes.JsonObject{["id"]=reference.Id,["origin"]=reference.Origin});
   return new System.Text.Json.Nodes.JsonObject{["scope"]="effective-metadata",["status"]="available",["id"]=id,["sourceKind"]=sourceKind,["values"]=values,["modules"]=modules,["requirements"]=requirements,["providers"]=providers,["providerSelection"]="not-performed",["declarationsLoaded"]=System.Text.Json.JsonSerializer.SerializeToNode(registry.Elements.Keys.Order(StringComparer.Ordinal).ToArray()),["registeredManifests"]=registry.Packs.Count,["bodyReads"]=statistics.ReadDocuments.Count(path=>registry.Elements.Values.Any(e=>e.Bodies.Values.Any(b=>Confectory.Core.PackPaths.Owned(System.IO.Path.GetDirectoryName(e.Loc.File)!,b.Path)==path))),["draftOverlayIDs"]=System.Text.Json.JsonSerializer.SerializeToNode(overlayIds.Order(StringComparer.Ordinal).ToArray()),["dependencySource"]="root-owned-drafts-and-confirmed-registered-files"};
  }
  catch(Confectory.Core.BuildError error){return new System.Text.Json.Nodes.JsonObject{["scope"]="effective-metadata",["status"]="unavailable",["id"]=id,["code"]=error.Diagnostic.Code,["message"]=error.Diagnostic.Message};}
  catch(Exception error){return new System.Text.Json.Nodes.JsonObject{["scope"]="effective-metadata",["status"]="unavailable",["id"]=id,["code"]="METADATA_UNAVAILABLE",["message"]=error.Message};}
  finally{if(System.IO.Directory.Exists(temporary))System.IO.Directory.Delete(temporary,true);}
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
    result["element"]=new System.Text.Json.Nodes.JsonObject{["id"]=element.Id,["kind"]=element.Kind,["parent"]=element.Parent,["description"]=element.Description,["signature"]=System.Text.Json.JsonSerializer.SerializeToNode(element.Signature),["values"]=System.Text.Json.JsonSerializer.SerializeToNode(element.Values.ToDictionary(x=>x.Key,x=>x.Value.Value)),["relations"]=DeclaredRelations.Describe(element),["metadataVersion"]=Confectory.Core.JsonData.Digest(element)};
   }else throw new ArgumentException("Unknown catalog operation.");
   result["reads"]=new System.Text.Json.Nodes.JsonObject{["manifest"]=statistics.ReadDocuments.Count(p=>p==project),["declarations"]=statistics.ReadDocuments.Count(p=>p!=project),["paths"]=System.Text.Json.JsonSerializer.SerializeToNode(statistics.ReadDocuments.Select(p=>System.IO.Path.GetRelativePath(root,p)).ToArray())};return result;
  }
  catch(Confectory.Core.BuildError error){return new System.Text.Json.Nodes.JsonObject{["status"]="unavailable",["scope"]="owned-declarations",["code"]=error.Diagnostic.Code,["message"]=error.Diagnostic.Message};}
  catch(Exception error){return new System.Text.Json.Nodes.JsonObject{["status"]="unavailable",["scope"]="owned-declarations",["code"]="CATALOG_UNAVAILABLE",["message"]=error.Message};}
 }
}
