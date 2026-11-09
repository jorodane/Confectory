using Confectory.Core;
using System.Text.Json.Nodes;

internal static class InformationStructMetadata
{
 public static JsonObject Query(JsonObject request)
 {
  var observations=new Dictionary<string,string>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);int bytes=0;
  byte[] Read(string path){path=PackPaths.Resolve(path);var file=new FileInfo(path);if(!file.Exists||file.Length>1048576)throw new ArgumentException("Bounded information definition source required");var raw=File.ReadAllBytes(path);string hash=JsonData.HashBytes(raw);if(observations.TryGetValue(path,out var before)){if(before!=hash)throw new InvalidOperationException("Information source changed during generation");}else{bytes=checked(bytes+raw.Length);if(bytes>16777216||observations.Count>=2048)throw new ArgumentException("Information source read budget");observations.Add(path,hash);}return raw;}
  var statistics=new BuildStatistics();var registry=new Registry(request["project"]!.GetValue<string>(),new Documents("",statistics,Read),statistics);
  var definition=InformationStructs.Describe(registry,request["id"]!.GetValue<string>(),registry.Project.Namespace+"::<project>");
  var result=InformationStructs.Document(definition);result["bodyReads"]=statistics.ReadDocuments.Count(path=>registry.Elements.Values.Any(element=>element.Bodies.Values.Any(body=>PackPaths.Owned(Path.GetDirectoryName(registry.Get(body.Origin).Loc.File)!,body.Path)==path)));result["observations"]=new JsonArray(observations.OrderBy(p=>p.Key,StringComparer.Ordinal).Select(p=>(JsonNode)new JsonObject{["path"]=p.Key,["sha256"]=p.Value}).ToArray());return result;
 }
}
