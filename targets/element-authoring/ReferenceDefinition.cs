using Confectory.Core;
using System.Text.Json.Nodes;

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
