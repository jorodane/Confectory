using Confectory.Core;
using System.Text.Json.Nodes;

internal static class InformationStructMetadata
{
 public static JsonObject Query(JsonObject request)
 {
  var observations=new Dictionary<string,string>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);int bytes=0;
  byte[] Read(string path){path=PackPaths.Resolve(path);var file=new FileInfo(path);if(!file.Exists||file.Length>1048576)throw new ArgumentException("Bounded information definition source required");var raw=File.ReadAllBytes(path);string hash=JsonData.HashBytes(raw);if(observations.TryGetValue(path,out var before)){if(before!=hash)throw new InvalidOperationException("Information source changed during generation");}else{bytes=checked(bytes+raw.Length);if(bytes>16777216||observations.Count>=2048)throw new ArgumentException("Information source read budget");observations.Add(path,hash);}return raw;}
  var statistics=new BuildStatistics();var registry=new Registry(request["project"]!.GetValue<string>(),new Documents("",statistics,Read),statistics);
  if(request["operation"]?.ToString()=="informationStruct")registry.Get(request["id"]!.GetValue<string>(),"schema",registry.Project.Namespace+"::<project>");
  JsonObject result;
  if(request["operation"]?.ToString()=="informationReference")result=RuntimeObjectContracts.DescribeReference(registry,request["id"]!.GetValue<string>(),registry.Project.Namespace+"::<project>");
  else result=InformationStructs.Document(request["operation"]?.ToString()=="informationReferenceType"?InformationStructs.DescribeReference(registry,request["id"]!.GetValue<string>(),registry.Project.Namespace+"::<project>"):InformationStructs.Describe(registry,request["id"]!.GetValue<string>(),registry.Project.Namespace+"::<project>"));int bodyReads=statistics.ReadDocuments.Count(path=>registry.Elements.Values.Any(element=>element.Bodies.Values.Any(body=>PackPaths.Owned(Path.GetDirectoryName(registry.Get(body.Origin).Loc.File)!,body.Path)==path)));var reads=new JsonArray(observations.OrderBy(p=>p.Key,StringComparer.Ordinal).Select(p=>(JsonNode)new JsonObject{["path"]=p.Key,["sha256"]=p.Value}).ToArray());
  if(request["operation"]?.ToString()=="informationReference")return new JsonObject{["descriptor"]=result,["bodyReads"]=bodyReads,["observations"]=reads,["runtimeValuesRead"]=false,["sourceWritten"]=false};
  result["bodyReads"]=bodyReads;result["observations"]=reads;return result;
 }
}
