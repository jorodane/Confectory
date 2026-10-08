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
