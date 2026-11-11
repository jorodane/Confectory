using Confectory.Core;
using System.Text.Json.Nodes;

// Carry the already selected property declaration closure through Review and
// the final read-only file lease. Saved paths never authorize a registration.
internal static class InformationFunctionPropertyGuards
{
 internal static JsonObject Execute(JsonObject request)
 {
  string ns=request["namespace"]!.ToString(),project=PackPaths.Resolve(request["project"]!.ToString());var units=request["units"]!.AsObject();
  string manifest=units[ns+"::ProjectManifest"]?["draft"]?.ToString()??throw new InvalidOperationException("Original property registration required");
  Registry? loaded=null;Registry Registry()=>loaded??=new Registry(project,new Documents(Path.Combine(Path.GetDirectoryName(project)!,".confectory","document-cache"),new BuildStatistics()),new BuildStatistics());
  string[] Scope(JsonNode? declaration)=> (declaration?["changes"] as JsonArray??new()).Where(row=>row?["type"]?.ToString()=="function-edit"&&row["mapping"]is JsonObject).Select(row=>row!["id"]!.ToString()).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal).ToArray();
  bool Presentation(JsonNode? declaration) {
   if(declaration?["raw"]is not null||declaration?["changes"]is not JsonArray changes||changes.Count is <1 or >3)return false;
   foreach(var row in changes){if(InformationFunctionBodyBatch.Presentation(row))continue;if(row is not JsonObject value||value["type"]?.ToString()!="function-edit"||value.Count is <6 or >8||value.Any(p=>p.Key is not("type" or "id" or "hash" or "name" or "description" or "signature" or "icon" or "returnName")))return false;
    string? id=value["id"]?.ToString();if(id is null||units[id]?["kind"]?.ToString()!="function"||units[id]?["draft"]is not JsonValue text)return false;var function=new Parser(text.ToString(),"<property-presentation>").ParseElement();if(function.Signature is null||!JsonNode.DeepEquals(FeatureBlueprint.SignatureDocument(function.Signature),value["signature"]))return false;
   }return true;
  }
  (JsonArray Reads,bool Required) Observe(string[] functions) {
   var registry=Registry();if(functions.Length is <1 or >8||functions.Any(id=>!id.StartsWith(ns+"::",StringComparison.Ordinal)||registry.Get(id).Kind!="function"))throw new ArgumentException("Existing owned property function scope required");
   var reads=new SortedDictionary<string,string>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);int bytes=0;
   void Read(string path){path=PackPaths.Resolve(path);for(FileSystemInfo? entry=new FileInfo(path);entry is not null;entry=entry is FileInfo file?file.Directory:((DirectoryInfo)entry).Parent)if(entry.LinkTarget is not null)throw new ArgumentException("Property source cannot traverse links");var info=new FileInfo(path);if(!info.Exists||info.Length>1048576)throw new ArgumentException("Bounded registered property source required");string hash=JsonData.HashBytes(File.ReadAllBytes(path));if(reads.TryGetValue(path,out var before)){if(before!=hash)throw new InvalidOperationException("Property source changed while observing; input retained");return;}bytes=checked(bytes+(int)info.Length);if(reads.Count>=240||bytes>2097152)throw new ArgumentException("Property source closure budget");reads.Add(path,hash);}
   var context=new InformationFunctionProperties(new JsonObject{["project"]=project,["manifest"]=manifest,["units"]=units.DeepClone()},Read);bool required=false;
   foreach(var locator in registry.Project.Elements.Where(row=>row.Value.Kind=="implementation")){
    string id=ns+"::"+locator.Key;var physical=registry.Get(id);var implementation=units[id]?["draft"]is JsonValue draft?new Parser(draft.ToString(),physical.Loc.File).ParseElement():physical;
    if(implementation.Id!=id||implementation.Kind!="implementation")throw new InvalidOperationException("Original property implementation identity required");if(!functions.Contains(implementation.Function!,StringComparer.Ordinal)&&!implementation.Imports.Values.Any(import=>functions.Contains(import.Id,StringComparer.Ordinal)))continue;
    foreach(var body in implementation.Bodies.Where(row=>row.Value.SourceKind=="blueprint")){
     string graphId=id+"/body:"+body.Key,path=PackPaths.Owned(Path.GetDirectoryName(physical.Loc.File)!,body.Value.Path);string text=units[graphId]?["draft"]?.ToString()??File.ReadAllText(path);if(text.Length>1048576)throw new ArgumentException("Bounded owned property graph required");var graph=JsonNode.Parse(text)!.AsObject();if(!graph["nodes"]!.AsArray().Any(node=>FeatureBlueprint.IsPropertyNode(node?["kind"]?.ToString())))continue;
     // The graph and header remain writes/ordinary source checks when edited;
     // the declaration closure is always a read, including registered packs.
     Read(physical.Loc.File);Read(path);context.ForGraph(implementation,graph);required=true;
    }
   }
   return(new JsonArray(reads.Select(row=>(JsonNode)new JsonObject{["path"]=row.Key,["hash"]=row.Value}).ToArray()),required);
  }
  JsonArray Validate(string owner,JsonObject receipt) {
   if(receipt["owner"]?.ToString()!=owner||receipt["version"]?.GetValue<int>()!=3||receipt["propertySourceScope"]is not JsonArray scope||scope.Count is <1 or >8||receipt["propertySourceReads"]is not JsonArray saved)throw new InvalidOperationException("Save the property group explicitly to bind its original source scope");
   string[] functions=scope.Select(id=>id!.ToString()).ToArray(),declared=Scope(receipt["declaration"]);if(!functions.SequenceEqual(functions.Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal))||declared.Any(id=>!functions.Contains(id,StringComparer.Ordinal))||declared.Length==0&&!Presentation(receipt["declaration"]))throw new InvalidOperationException("Retain the original property function scope");var actual=Observe(functions);if(!actual.Required||!JsonNode.DeepEquals(actual.Reads,saved))throw new InvalidOperationException("Original property sources changed; preserve the saved group and peer bytes");return saved.DeepClone().AsArray();
  }
  if(request["action"]?.ToString()=="prepare"){
   string owner=request["declaration"]?["id"]?.ToString()??"";string[] scope=Scope(request["declaration"]);var prior=units[owner]?["slotSaveReceipt"]as JsonObject;
   if(scope.Length==0&&prior?["propertySourceReads"]is not null&&Presentation(request["declaration"]))return new JsonObject{["required"]=true,["scope"]=prior["propertySourceScope"]!.DeepClone(),["reads"]=Validate(owner,prior)};
   if(scope.Length==0)return new JsonObject{["required"]=false,["reads"]=new JsonArray()};if(prior?["propertySourceReads"]is not null){Validate(owner,prior);scope=scope.Concat(prior["propertySourceScope"]!.AsArray().Select(id=>id!.ToString())).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal).ToArray();}var result=Observe(scope);return new JsonObject{["required"]=result.Required,["scope"]=new JsonArray(scope.Select(id=>JsonValue.Create(id)).ToArray()),["reads"]=result.Reads};
  }
  if(request["action"]?.ToString()!="validate")throw new ArgumentException("Property guard action");var selected=request["selected"]!.AsArray();if(selected.Count>64)throw new ArgumentException("Property review selection budget");var resultReads=new SortedDictionary<string,JsonNode>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);
  foreach(var pair in units){if(pair.Value?["atomicEditGroup"]is not JsonArray group||!selected.Any(id=>group.Any(member=>member!.ToString()==id!.ToString()))||pair.Value?["slotSaveReceipt"]is not JsonObject receipt)continue;
   if(receipt["propertySourceReads"]is null){var scope=Scope(receipt["declaration"]);if(scope.Length>0&&Observe(scope).Required)throw new InvalidOperationException("Save the property group explicitly with its original source proof; no automatic receipt migration");continue;}
   foreach(var read in Validate(pair.Key,receipt)){string path=read!["path"]!.ToString();if(resultReads.TryGetValue(path,out var prior)&&!JsonNode.DeepEquals(prior,read))throw new InvalidOperationException("Property group source versions differ");resultReads[path]=read.DeepClone();}
  }
  return new JsonObject{["reads"]=new JsonArray(resultReads.Values.ToArray())};
 }
}
