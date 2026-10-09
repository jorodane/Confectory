using System.Linq;
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
