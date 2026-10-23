using System.Linq;
internal static class EffectiveMetadata
{
 public static System.Text.Json.Nodes.JsonObject Query(string project,string manifestText,string id,string text,Func<Confectory.Core.Manifest,string> format,Func<string,string> read,System.Text.Json.Nodes.JsonArray? drafts=null,bool schemaView=false,bool validateObjects=false,bool observeSources=false)
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
   long observationBytes=0;var observed=new System.Collections.Generic.Dictionary<string,string>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);
   string Observe(string path){
    path=System.IO.Path.GetFullPath(path);if(observeSources)for(System.IO.FileSystemInfo? entry=new System.IO.FileInfo(path);entry is not null;entry=entry is System.IO.FileInfo file?file.Directory:((System.IO.DirectoryInfo)entry).Parent)if(entry.LinkTarget is not null)throw new System.ArgumentException("Slot context cannot traverse links");
    string value=read(path);if(observeSources){if(observed.TryGetValue(path,out string? previous)&&previous!=value)throw new System.InvalidOperationException("Slot context changed during reading");if(!observed.ContainsKey(path)){observationBytes+=System.Text.Encoding.UTF8.GetByteCount(value);if(observed.Count>=2048||observationBytes>16777216)throw new System.ArgumentException("Slot context observation budget");}observed[path]=value;}return value;
   }
   foreach(var ns in manifest.Registry.Keys.ToArray())
   {
    var registration=manifest.Registry[ns];string registered=System.IO.Path.GetFullPath(System.IO.Path.Combine(root,registration.Path));Observe(registered);
    manifest.Registry[ns]=registration with{Path=registered};
   }
   string sourceKind=manifest.Kind;manifest.Kind="project";
   System.IO.Directory.CreateDirectory(temporary);string candidate=System.IO.Path.Combine(temporary,"project.cpack");System.IO.File.WriteAllText(candidate,format(manifest));
   // Metadata projections have a fresh registry and bounded byte reader per query;
   // no persistent document cache or project/permission result survives the request.
   long bytesRead=0;int filesRead=0;
   byte[] Read(string path){byte[] bytes=System.Text.Encoding.UTF8.GetBytes(path==candidate?read(path):Observe(path));bytesRead+=bytes.Length;if(bytes.Length>1048576||bytesRead>16777216||++filesRead>2048)throw new ArgumentException("Effective metadata read budget");return bytes;}
   var statistics=new Confectory.Core.BuildStatistics();var registry=new Confectory.Core.Registry(candidate,new Confectory.Core.Documents("",statistics,Read),statistics);
   registry.Paths[manifest.Namespace]=System.IO.Path.GetFullPath(project);
   // Public per-query declaration cache overlays only this explicitly owned draft.
   registry.Elements[id]=selected;var overlayIds=new System.Collections.Generic.HashSet<string>(StringComparer.Ordinal){id};int budget=text.Length;
   foreach(var item in drafts??new System.Text.Json.Nodes.JsonArray()){
    string ownedId=item!["id"]!.GetValue<string>(),source=item["text"]!.GetValue<string>();budget+=source.Length;
    if(budget>1048576||overlayIds.Count>=256||!ownedId.StartsWith(manifest.Namespace+"::",StringComparison.Ordinal)||!overlayIds.Add(ownedId))throw new ArgumentException("Owned draft overlay budget/identity mismatch.");
    if(!manifest.Elements.TryGetValue(ownedId[(manifest.Namespace.Length+2)..],out var ownedLocator))throw new ArgumentException("Draft overlay locator missing.");
    var owned=new Confectory.Core.Parser(source,Confectory.Core.PackPaths.Owned(root,ownedLocator.Path)).ParseElement();if(owned.Id!=ownedId||owned.Kind!=ownedLocator.Kind)throw new ArgumentException("Draft overlay identity/kind mismatch.");registry.Elements[ownedId]=owned;
   }
   var planner=new Confectory.Core.Planner(registry,"metadata");
   // A signature edit must preserve contracts of unselected owned modules too.
   // Module validates requirements/defaults without selecting providers or executing bodies.
   if(validateObjects)foreach(var declaration in manifest.Elements){string owned=manifest.Namespace+"::"+declaration.Key;if(declaration.Value.Kind is "object" or "schema")Confectory.Core.SchemaContracts.Validate(registry,owned);else if(declaration.Value.Kind=="module")planner.Module(owned);else if(declaration.Value.Kind=="implementation"){var implementation=registry.Get(owned,"implementation");if(implementation.Function is not null)registry.Implementation(implementation.Function,owned,owned,implementation.Loc);}}

   var effective=registry.Effective(id);var descriptionSource=selected;while(!descriptionSource.DescriptionPresent&&descriptionSource.Parent is not null)descriptionSource=registry.Get(descriptionSource.Parent,descriptionSource.Kind,descriptionSource.Id,descriptionSource.Loc);
var module=effective.Kind=="module"?planner.Module(id):planner.ModulesFor(id);
   var values=new System.Text.Json.Nodes.JsonArray();foreach(var pair in effective.Values.OrderBy(p=>p.Key,StringComparer.Ordinal))values.Add(new System.Text.Json.Nodes.JsonObject{["field"]=pair.Key,["value"]=System.Text.Json.JsonSerializer.SerializeToNode(pair.Value.Value),["origin"]=pair.Value.Origin});
   var requirements=new System.Text.Json.Nodes.JsonArray();foreach(var pair in module.Required.OrderBy(p=>p.Key,StringComparer.Ordinal))
   {
    var defaults=new System.Text.Json.Nodes.JsonArray();if(module.Defaults.TryGetValue(pair.Key,out var choices))foreach(var choice in choices.OrderBy(p=>p.Key,StringComparer.Ordinal))defaults.Add(new System.Text.Json.Nodes.JsonObject{["implementation"]=choice.Key,["origin"]=choice.Value.Origin});
    // Module requirements constrain positional types/modes; the function owns pin names.
    // Read its public declaration only. Never infer names from a selected provider body.
    var requiredFunction=registry.Get(pair.Key,"function",pair.Value.Origin,pair.Value.Loc);var requiredSignature=requiredFunction.Signature??throw new System.ArgumentException("Required function must declare its named signature");if(!pair.Value.Signature.Matches(requiredSignature))throw new System.ArgumentException("Required module and function signatures differ");
    requirements.Add(new System.Text.Json.Nodes.JsonObject{["function"]=pair.Key,["signature"]=System.Text.Json.JsonSerializer.SerializeToNode(requiredSignature),["moduleSignature"]=System.Text.Json.JsonSerializer.SerializeToNode(pair.Value.Signature),["origin"]=pair.Value.Origin,["defaults"]=defaults});
   }
   var providers=new System.Text.Json.Nodes.JsonArray();foreach(var pair in effective.Provides.OrderBy(p=>p.Key,StringComparer.Ordinal)){
    var provider=new System.Text.Json.Nodes.JsonObject{["function"]=pair.Key,["implementation"]=pair.Value.Id,["origin"]=pair.Value.Origin};
    try{var body=registry.Implementation(pair.Key,pair.Value.Id,pair.Value.Origin??id,pair.Value.Loc);provider["contract"]=new System.Text.Json.Nodes.JsonObject{["status"]="valid",["signature"]=System.Text.Json.JsonSerializer.SerializeToNode(body.Signature),["targets"]=System.Text.Json.JsonSerializer.SerializeToNode(body.Bodies.Keys.Order(StringComparer.Ordinal).ToArray())};}
    catch(Confectory.Core.BuildError error){provider["contract"]=new System.Text.Json.Nodes.JsonObject{["status"]="invalid",["code"]=error.Diagnostic.Code,["message"]=error.Diagnostic.Message};}
    providers.Add(provider);
   }
   var modules=new System.Text.Json.Nodes.JsonArray();foreach(var reference in effective.Modules)modules.Add(new System.Text.Json.Nodes.JsonObject{["id"]=reference.Id,["origin"]=reference.Origin});
   var schemaFields=effective.Kind=="object"?Confectory.Core.SchemaContracts.Fields(registry,id):effective.Fields;
   var functionContracts=new System.Text.Json.Nodes.JsonObject();foreach(var pair in schemaFields.Where(p=>p.Value.Kind=="function")){var fn=registry.Get(pair.Value.Type,"function",pair.Value.Origin,pair.Value.Loc);functionContracts[pair.Key]=new System.Text.Json.Nodes.JsonObject{["id"]=fn.Id,["signature"]=System.Text.Json.JsonSerializer.SerializeToNode(fn.Signature)};}
   // The declaration that attaches a schema is distinct from the schema definition and a local value override.
   var fieldSources=new System.Text.Json.Nodes.JsonObject();
   if(effective.Kind=="object")foreach(var use in effective.Uses.Where(x=>x.Kind=="schema"))foreach(var field in registry.Effective(use.Id).Fields)fieldSources[field.Key]=use.Origin??id;
   else foreach(var field in schemaFields)fieldSources[field.Key]=field.Value.Origin;
   string DefinitionSource(string schemaId)=>schemaId==id?text:drafts?.FirstOrDefault(row=>row?["id"]?.ToString()==schemaId)?["text"]?.GetValue<string>()??Observe(registry.Get(schemaId,"schema").Loc.File);
   var schemaModel=schemaView?SchemaModel(registry,effective,schemaFields,DefinitionSource):null;
   var result=new System.Text.Json.Nodes.JsonObject{["scope"]="effective-metadata",["status"]="available",["id"]=id,["description"]=effective.Description,["descriptionOrigin"]=descriptionSource.DescriptionPresent?descriptionSource.Id:null,["sourceKind"]=sourceKind,["fields"]=System.Text.Json.JsonSerializer.SerializeToNode(schemaFields),["fieldSources"]=fieldSources,["functionContracts"]=functionContracts,["schemaModel"]=schemaModel,["data"]=System.Text.Json.JsonSerializer.SerializeToNode(effective.Data),["values"]=values,["modules"]=modules,["requirements"]=requirements,["providers"]=providers,["providerSelection"]="not-performed",["declarationsLoaded"]=System.Text.Json.JsonSerializer.SerializeToNode(registry.Elements.Keys.Order(StringComparer.Ordinal).ToArray()),["registeredManifests"]=registry.Packs.Count,["bodyReads"]=statistics.ReadDocuments.Count(path=>registry.Elements.Values.Any(e=>e.Bodies.Values.Any(b=>Confectory.Core.PackPaths.Owned(System.IO.Path.GetDirectoryName(e.Loc.File)!,b.Path)==path))),["draftOverlayIDs"]=System.Text.Json.JsonSerializer.SerializeToNode(overlayIds.Order(StringComparer.Ordinal).ToArray()),["dependencySource"]="root-owned-drafts-and-confirmed-registered-files"};
   if(observeSources){var observations=new System.Text.Json.Nodes.JsonArray();foreach(var input in observed.OrderBy(p=>p.Key,StringComparer.Ordinal)){if(read(input.Key)!=input.Value)throw new System.InvalidOperationException("Slot context changed after validation");observations.Add(new System.Text.Json.Nodes.JsonObject{["path"]=input.Key,["hash"]=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(input.Value))).ToLowerInvariant()});}result["observations"]=observations;}
   return result;
  }
  catch(Confectory.Core.BuildError error){return new System.Text.Json.Nodes.JsonObject{["scope"]="effective-metadata",["status"]="unavailable",["id"]=id,["code"]=error.Diagnostic.Code,["message"]=error.Diagnostic.Message,["namespaceDiagnostic"]=NamespaceDiagnostic.From(error)};}
  catch(Exception error){return new System.Text.Json.Nodes.JsonObject{["scope"]="effective-metadata",["status"]="unavailable",["id"]=id,["code"]="METADATA_UNAVAILABLE",["message"]=error.Message};}
  finally{if(System.IO.Directory.Exists(temporary))System.IO.Directory.Delete(temporary,true);}
 }
 static System.Text.Json.Nodes.JsonObject SchemaModel(Confectory.Core.Registry registry,Confectory.Core.Element element,System.Collections.Generic.Dictionary<string,Confectory.Core.SchemaField> fields,Func<string,string> definitionSource)
 {
  var schemas=new System.Text.Json.Nodes.JsonObject();var functions=new System.Text.Json.Nodes.JsonObject();var implementations=new System.Text.Json.Nodes.JsonObject();
  var sourceHashes=new System.Collections.Generic.Dictionary<string,string>(StringComparer.Ordinal);
  System.Text.Json.Nodes.JsonNode Fields(System.Collections.Generic.Dictionary<string,Confectory.Core.SchemaField> items){var result=new System.Text.Json.Nodes.JsonObject();foreach(var pair in items){var field=pair.Value;var definition=registry.Effective(field.Origin);string label=pair.Key;if(definition.Values.TryGetValue("editorFieldName_"+pair.Key,out var display)&&display.Value.ValueKind==System.Text.Json.JsonValueKind.String)label=display.Value.GetString()!;if(!sourceHashes.TryGetValue(field.Origin,out string? hash)){hash=Confectory.Core.JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(definitionSource(field.Origin)));sourceHashes[field.Origin]=hash;}result[pair.Key]=new System.Text.Json.Nodes.JsonObject{["cardinality"]=field.Cardinality,["kind"]=field.Kind,["type"]=field.Type,["origin"]=field.Origin,["displayName"]=label,["schemaHash"]=hash};}return result;}
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
