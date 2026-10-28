using Confectory.Core;
using System.Text;
using System.Text.Json.Nodes;

// Read-only choices share the information editor's typed-default projection.
internal static class InformationTypes
{
 public static JsonArray Query(JsonObject request,Func<Manifest,string> formatManifest)
 {
  string project=request["project"]!.GetValue<string>(),manifest=request["manifest"]!.GetValue<string>();var registration=new Parser(manifest,"<information-registration>").ParseManifest();var drafts=request["drafts"]!.AsArray();if(drafts.Count>255)throw new ArgumentException("Information catalogue budget");var schemas=drafts.Where(row=>new Parser(row!["text"]!.GetValue<string>(),"<information-source>").ParseElement().Kind=="schema").ToArray();if(schemas.Length>64)throw new ArgumentException("Information choice budget");var result=new JsonArray();
  string Read(string path){var file=new FileInfo(path);if(!file.Exists||file.Length>1048576)throw new IOException("Information source budget");return File.ReadAllText(path);}
  JsonNode Transport(JsonNode datum)=>datum["kind"]!.ToString() switch{"reference"=>new JsonObject{["$ref"]=datum["reference"]!.DeepClone()},"multiple"=>new JsonArray(datum["items"]!.AsArray().Select(v=>Transport(v!)).ToArray()),"compound"=>new JsonObject(datum["members"]!.AsObject().Select(p=>KeyValuePair.Create<string,JsonNode?>(p.Key,Transport(p.Value!)))),_=>datum["scalar"]!.DeepClone()};
  foreach(var source in schemas){string id=source!["id"]!.ToString(),text=source["text"]!.ToString();if(!id.StartsWith(registration.Namespace+"::",StringComparison.Ordinal))throw new ArgumentException("Owned information choice required");var row=new JsonObject{["id"]=id,["available"]=false};result.Add(row);
   try{
    var effective=EffectiveMetadata.Query(project,manifest,id,text,formatManifest,Read,new JsonArray(drafts.Where(d=>d!["id"]!.ToString()!=id).Select(d=>d!.DeepClone()).ToArray()),schemaView:true);if(effective["status"]?.ToString()!="available")throw new ArgumentException("Information definition unavailable");var model=effective["schemaModel"]!.AsObject();if(model["information"]?["complete"]?.GetValue<bool>()!=true)throw new ArgumentException("Information reference/function default needs an explicit target");var types=model["schemas"]!.DeepClone().AsObject();types[id]=new JsonObject{["fields"]=model["fields"]!.DeepClone()};var proofs=new JsonObject();
    foreach(var sourceId in model["information"]!["sources"]!.AsArray()){string schema=sourceId!.ToString();if(!schema.StartsWith(registration.Namespace+"::",StringComparison.Ordinal))throw new ArgumentException("Imported information defaults are not connected");var observed=drafts.Single(d=>d!["id"]!.ToString()==schema)!;string raw=observed["text"]!.ToString();if(new Parser(raw,"<information-defaults>").ParseElement().Values.Keys.Any(key=>!InformationDefaults.Recognized(key)))throw new ArgumentException("Unknown custom information metadata retained");proofs[schema]=JsonData.HashBytes(Encoding.UTF8.GetBytes(raw));}
    var values=new JsonObject();foreach(var value in model["data"]!.AsObject())values[value.Key]=Transport(value.Value!);row["types"]=types;row["sources"]=proofs;row["valueJson"]=values.ToJsonString();row["available"]=true;
   }catch(ArgumentException){row["reason"]="이 정보의 기본값·참조 형식은 아직 연결되지 않았어요.";}catch(InvalidOperationException){row["reason"]="이 정보의 정의를 확인하지 못했어요. 입력은 유지됩니다.";}
  }
  return result;
 }
}
