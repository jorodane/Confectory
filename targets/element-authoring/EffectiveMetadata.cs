using System.Linq;
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
   var schemaFields=effective.Kind=="object"?Confectory.Core.SchemaContracts.Fields(registry,id):effective.Fields;
   var functionContracts=new System.Text.Json.Nodes.JsonObject();foreach(var pair in schemaFields.Where(p=>p.Value.Kind=="function")){var fn=registry.Get(pair.Value.Type,"function",pair.Value.Origin,pair.Value.Loc);functionContracts[pair.Key]=new System.Text.Json.Nodes.JsonObject{["id"]=fn.Id,["signature"]=System.Text.Json.JsonSerializer.SerializeToNode(fn.Signature)};}
   return new System.Text.Json.Nodes.JsonObject{["scope"]="effective-metadata",["status"]="available",["id"]=id,["sourceKind"]=sourceKind,["fields"]=System.Text.Json.JsonSerializer.SerializeToNode(schemaFields),["functionContracts"]=functionContracts,["data"]=System.Text.Json.JsonSerializer.SerializeToNode(effective.Data),["values"]=values,["modules"]=modules,["requirements"]=requirements,["providers"]=providers,["providerSelection"]="not-performed",["declarationsLoaded"]=System.Text.Json.JsonSerializer.SerializeToNode(registry.Elements.Keys.Order(StringComparer.Ordinal).ToArray()),["registeredManifests"]=registry.Packs.Count,["bodyReads"]=statistics.ReadDocuments.Count(path=>registry.Elements.Values.Any(e=>e.Bodies.Values.Any(b=>Confectory.Core.PackPaths.Owned(System.IO.Path.GetDirectoryName(e.Loc.File)!,b.Path)==path))),["draftOverlayIDs"]=System.Text.Json.JsonSerializer.SerializeToNode(overlayIds.Order(StringComparer.Ordinal).ToArray()),["dependencySource"]="root-owned-drafts-and-confirmed-registered-files"};
  }
  catch(Confectory.Core.BuildError error){return new System.Text.Json.Nodes.JsonObject{["scope"]="effective-metadata",["status"]="unavailable",["id"]=id,["code"]=error.Diagnostic.Code,["message"]=error.Diagnostic.Message};}
  catch(Exception error){return new System.Text.Json.Nodes.JsonObject{["scope"]="effective-metadata",["status"]="unavailable",["id"]=id,["code"]="METADATA_UNAVAILABLE",["message"]=error.Message};}
  finally{if(System.IO.Directory.Exists(temporary))System.IO.Directory.Delete(temporary,true);}
 }
}
