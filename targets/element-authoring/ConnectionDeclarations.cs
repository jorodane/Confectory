using System.Linq;
internal static class ConnectionDeclarations
{
 public static System.Text.Json.Nodes.JsonObject Query(string project,string? selected,Func<Confectory.Core.Manifest,string> format,Func<string,string> scope,System.Text.Json.Nodes.JsonObject? repair=null,string? presentationProject=null)
 {
 project=scope(System.IO.Path.GetFullPath(project));string root=System.IO.Path.GetDirectoryName(project)!;
 // Each query reads current declarations. Serializing/deserializing the persistent build
 // cache for a small metadata query cost more than parsing these bounded source files.
 // This reader also applies the declaration scope checks to every registered file.
 long bytesRead=0;int filesRead=0;
 var observed=new System.Collections.Generic.Dictionary<string,string>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);
 byte[] Read(string path){path=scope(path);byte[] bytes=System.IO.File.ReadAllBytes(path);string hash=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(bytes)).ToLowerInvariant();if(observed.TryGetValue(path,out string? before)&&before!=hash)throw new InvalidOperationException("Connection declaration changed during reading");observed[path]=hash;bytesRead+=bytes.Length;if(bytes.Length>1048576||bytesRead>16777216||++filesRead>2048)throw new ArgumentException("Connection metadata read budget");return bytes;}
 var stats=new Confectory.Core.BuildStatistics();var docs=new Confectory.Core.Documents("",stats,Read);var registry=new Confectory.Core.Registry(project,docs,stats);
 var rows=new System.Text.Json.Nodes.JsonArray();foreach(var pack in registry.Packs.OrderBy(p=>p.Key,StringComparer.Ordinal))foreach(var item in pack.Value.Elements.OrderBy(p=>p.Key,StringComparer.Ordinal)){
 if(item.Value.Kind!="object")continue;string id=pack.Key+"::"+item.Key;if(id=="Confectory.AIConnection::Connection")continue;
 string path=scope(Confectory.Core.PackPaths.Owned(System.IO.Path.GetDirectoryName(registry.Paths[pack.Key])!,item.Value.Path));var element=registry.Get(id);var current=element;var seen=new System.Collections.Generic.HashSet<string>(StringComparer.Ordinal);bool connection=false;
 while(current.Parent is string parent){if(!seen.Add(parent))throw new ArgumentException("Connection inheritance cycle");if(parent=="Confectory.AIConnection::Connection"){connection=true;break;}current=registry.Get(parent);}
 if(!connection)continue;if(rows.Count>=32)throw new ArgumentException("Connection catalogue bound");var effective=registry.Effective(id);var fields=Confectory.Core.SchemaContracts.Fields(registry,id);if(fields.Keys.Any(k=>System.Text.RegularExpressions.Regex.IsMatch(k,"apiKey|password|accessToken|refreshToken|secret",System.Text.RegularExpressions.RegexOptions.IgnoreCase)))throw new ArgumentException("Secrets cannot be ordinary connection schema fields");
 var values=new System.Text.Json.Nodes.JsonObject();foreach(var key in new[]{"transport","authentication","desktopSupported","browserSupported","androidSupported","functionTools","unsupportedReason","liveVerified"})if(effective.Values.TryGetValue(key,out var value))values[key]=System.Text.Json.JsonSerializer.SerializeToNode(value.Value);
 var methods=new System.Text.Json.Nodes.JsonArray();if(effective.Values.TryGetValue("connectionMethods",out var methodValue)){string declaration=methodValue.Value.ValueKind==System.Text.Json.JsonValueKind.String?methodValue.Value.GetString()??"[]":throw new ArgumentException("Connection methods must be declared JSON");if(declaration.Length>32768)throw new ArgumentException("Connection method declaration budget");methods=System.Text.Json.Nodes.JsonNode.Parse(declaration)?.AsArray()??throw new ArgumentException("Connection method list required");if(methods.Count>8)throw new ArgumentException("Connection method count budget");var ids=new System.Collections.Generic.HashSet<string>(StringComparer.Ordinal);foreach(var method in methods){string methodId=method?["id"]?.ToString()??"";if(!System.Text.RegularExpressions.Regex.IsMatch(methodId,@"^[a-z][a-z0-9-]{0,63}$")||!ids.Add(methodId))throw new ArgumentException("Unique bounded connection method ID required");foreach(var field in method?["fields"]?.AsArray()??new System.Text.Json.Nodes.JsonArray())if(!fields.ContainsKey(field!.ToString()))throw new ArgumentException("Method settings must use the inherited connection schema");}}
 string methodField=effective.Values.TryGetValue("connectionMethodField",out var methodFieldValue)?methodFieldValue.Value.ValueKind==System.Text.Json.JsonValueKind.String?methodFieldValue.Value.GetString()??"":"":"";if(methods.Count>0&&!fields.ContainsKey(methodField))throw new ArgumentException("Method selection must use a declared inherited setting");
 rows.Add(new System.Text.Json.Nodes.JsonObject{["id"]=id,["title"]=effective.Values.TryGetValue("displayName",out var display)&&display.Value.ValueKind==System.Text.Json.JsonValueKind.String?display.Value.GetString():id,["pack"]=pack.Key,["fields"]=System.Text.Json.JsonSerializer.SerializeToNode(fields),["methods"]=methods,["methodField"]=methodField,["capabilities"]=values});
 }
 if(selected is null)return new System.Text.Json.Nodes.JsonObject{["connections"]=rows,["bodyReads"]=stats.ReadDocuments.Count(path=>path.EndsWith(".csbody",StringComparison.Ordinal)),["executionPerformed"]=false};
 if(!rows.Any(row=>row!["id"]!.ToString()==selected))throw new ArgumentException("Select a declared registered connection descendant");
 var manifest=docs.Manifest(project);manifest.Namespace="Confectory.AISettings";manifest.Kind="project";manifest.Standalone=false;manifest.Entry=null;manifest.Targets.Clear();manifest.Always.Clear();manifest.Elements.Clear();foreach(string ns in manifest.Registry.Keys.ToArray()){var registration=manifest.Registry[ns];manifest.Registry[ns]=registration with{Path=System.IO.Path.GetFullPath(System.IO.Path.Combine(root,registration.Path))};}manifest.Elements.Add("Settings",new Confectory.Core.Locator("object","Settings.celem",new()));
 // A registered/discoverable Agent pack need not be a direct dependency of the
 // editor's root project. The new Settings object itself extends that pack, so
 // its own ProjectPack must declare the dependency, even on the very first run.
 string selectedPack=selected.Split("::")[0];var installed=registry.Packs[selectedPack];
 manifest.Dependencies.TryAdd(selectedPack,new Confectory.Core.Dependency(installed.Version,installed.Loc));
 // A private proof of the exact installed declaration model. Reuse is
 // optional: lexical links or an excessive ownership closure retain the
 // normal fresh query rather than changing which installations are allowed.
 System.Text.Json.Nodes.JsonObject? Proof(){
  try{
   var paths=new System.Collections.Generic.HashSet<string>(observed.Comparer){project};
   foreach(var pack in registry.Packs){string packPath=registry.Paths[pack.Key],packRoot=System.IO.Path.GetDirectoryName(packPath)!;paths.Add(packPath);
    foreach(var entry in pack.Value.Elements.Values){string full=System.IO.Path.GetFullPath(System.IO.Path.Combine(packRoot,entry.Path)),relative=System.IO.Path.GetRelativePath(packRoot,full);if(System.IO.Path.IsPathRooted(relative)||relative==".."||relative.StartsWith(".."+System.IO.Path.DirectorySeparatorChar,StringComparison.Ordinal))return null;paths.Add(full);if(paths.Count>2048)return null;}
   }
   var checkedPaths=new System.Collections.Generic.HashSet<string>(paths.Comparer);
   foreach(string full in paths)for(System.IO.FileSystemInfo? node=new System.IO.FileInfo(full);node is not null;node=node is System.IO.FileInfo file?file.Directory:((System.IO.DirectoryInfo)node).Parent){if(!checkedPaths.Add(node.FullName))break;if(node.LinkTarget is not null)return null;}
   var rows=new System.Text.Json.Nodes.JsonArray();foreach(var item in observed){var file=new System.IO.FileInfo(item.Key);if(!file.Exists||file.Length>1048576||Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.IO.File.ReadAllBytes(item.Key))).ToLowerInvariant()!=item.Value)return null;rows.Add(new System.Text.Json.Nodes.JsonObject{["path"]=item.Key,["hash"]=item.Value});}
   return new System.Text.Json.Nodes.JsonObject{["project"]=project,["paths"]=System.Text.Json.JsonSerializer.SerializeToNode(paths),["observations"]=rows};
  }catch(Exception error) when(error is System.IO.IOException or UnauthorizedAccessException or ArgumentException){return null;}
 }
 if(repair is not null){var proposal=ConnectionSettingsRepair.Propose(manifest,registry,selected,repair,format);if(proposal["state"]?.ToString() is "unchanged" or "repair")proposal["connectionModelProof"]=Proof();return proposal;}
 var generatedManifest=format(manifest);string generatedSource="object Confectory.AISettings::Settings extends "+selected+" {}\n";
 var result=new System.Text.Json.Nodes.JsonObject{["manifest"]=generatedManifest,["source"]=generatedSource,["connection"]=selected,["settingsDependency"]=new System.Text.Json.Nodes.JsonObject{["namespace"]=selectedPack,["version"]=installed.Version},["credentialRead"]=false,["executionPerformed"]=false};
 if(presentationProject is not null){
  // The projected root uses the exact declaration registry read above, not a
  // second registration pass or a settings file created solely for display.
  string ReadText(string path){if(new System.IO.FileInfo(path).Length>1048576)throw new System.IO.IOException("Manifest budget");return System.IO.File.ReadAllText(path);}
  var effective=EffectiveMetadata.Query(presentationProject,generatedManifest,"Confectory.AISettings::Settings",generatedSource,format,ReadText,schemaView:true,observeSources:true,schemaReuseProof:true,installation:registry);
  if(effective["status"]?.ToString()!="available")effective=EffectiveMetadata.Query(presentationProject,generatedManifest,"Confectory.AISettings::Settings",generatedSource,format,ReadText,schemaView:true);
  // Even installations that cannot produce a reusable lexical proof must not
  // publish a mixed read of the installed snapshot.
  foreach(var observation in observed){var file=new System.IO.FileInfo(observation.Key);if(!file.Exists||file.Length>1048576||Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.IO.File.ReadAllBytes(observation.Key))).ToLowerInvariant()!=observation.Value)throw new InvalidOperationException("Connection declaration changed during presentation");}
  result["presentation"]=effective;
 }
 result["connectionModelProof"]=Proof();return result;
 }
}
