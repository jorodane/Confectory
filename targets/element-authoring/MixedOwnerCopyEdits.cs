using Confectory.Core;
using System.Text.Json;
using System.Text.Json.Nodes;

// Declaration half of a staged copy transaction. It cannot edit identity,
// membership, ownership, schema or executable contracts. No source writes.
internal static class MixedOwnerCopyEdits
{
 public static JsonObject Prepare(JsonObject request,Func<Element,string> format,Func<Manifest,string> formatManifest)
 {
  string project=request["project"]!.GetValue<string>(),manifest=request["manifest"]!.GetValue<string>(),id=request["id"]!.GetValue<string>(),text=request["text"]!.GetValue<string>();
  var changes=request["changes"]!.AsArray();var element=new Parser(text,"<mixed-copy-owner>").ParseElement();
  if(element.Kind!="object"||element.Id!=id||changes.Count is <1 or >16)throw new ArgumentException("Bounded same-owner object changes required");
  var drafts=request["drafts"]!.AsArray();
  string Read(string path){var file=new FileInfo(path);if(!file.Exists||file.Length>1048576)throw new IOException("Mixed declaration source budget");return File.ReadAllText(path);}
  JsonObject Inspect(string source)=>EffectiveMetadata.Query(project,manifest,id,source,formatManifest,Read,drafts,schemaView:true,validateObjects:true,observeSources:true);
  var before=Inspect(text);void Valid(JsonObject result){if(result["status"]?.ToString()!="available"||result["schemaModel"]?["validation"]?["status"]?.ToString()!="valid")throw new InvalidOperationException("Mixed declaration/schema context invalid; retain all input");}Valid(before);
  var seen=new HashSet<string>(StringComparer.Ordinal);
  foreach(var change in changes){
   var row=change!.AsObject();string type=row["type"]!.GetValue<string>();
   if(type=="description"){
    if(row.Count!=2||row["text"] is null||!seen.Add("description"))throw new ArgumentException("One explicit description required");
    string value=row["text"]!.GetValue<string>();if(value.Length>16384)throw new ArgumentException("Mixed description budget");element.Description=value;element.DescriptionPresent=true;
   }else if(type=="scalar"){
    if(row.Count!=4||row.Any(p=>p.Key is not ("type" or "path" or "nativeType" or "valueJson"))||row["path"] is not JsonArray path||path.Count!=1||path[0] is not JsonValue||!seen.Add("data:"+path.ToJsonString()))throw new ArgumentException("One existing scalar path required");
    string field=path[0]!.GetValue<string>();var definition=before["fields"]?[field]??throw new ArgumentException("Existing effective field required");
    string kind=definition["Kind"]?.ToString()??definition["kind"]!.ToString(),cardinality=definition["Cardinality"]?.ToString()??definition["cardinality"]!.ToString(),nativeType=definition["Type"]?.ToString()??definition["type"]!.ToString();
    if(kind!="general"||cardinality!="single"||nativeType is not ("string" or "bool" or "int" or "long" or "float" or "double")||row["nativeType"]?.ToString()!=nativeType)throw new InvalidOperationException("Scalar schema changed or unsupported; retain all input");
    string value=row["valueJson"]!.GetValue<string>();if(value.Length>65536)throw new ArgumentException("Mixed scalar budget");using var parsed=JsonDocument.Parse(value);if(parsed.RootElement.ValueKind is not (JsonValueKind.Number or JsonValueKind.String or JsonValueKind.True or JsonValueKind.False))throw new ArgumentException("Explicit scalar value required");
    SchemaContracts.SetDataPath(element,JsonSerializer.SerializeToElement(path),parsed.RootElement);
   }else throw new ArgumentException("Mixed copy supports description and existing scalar data only");
  }
  string formatted=format(element);if(formatted.Length>1048576)throw new ArgumentException("Mixed owner budget");var after=Inspect(formatted);Valid(after);
  if(!JsonNode.DeepEquals(before["requirements"],after["requirements"])||!JsonNode.DeepEquals(before["providers"],after["providers"])||!JsonNode.DeepEquals(before["fields"],after["fields"]))throw new InvalidOperationException("Mixed declaration cannot change executable/schema contracts");
  return new JsonObject{["text"]=formatted,["observations"]=before["observations"]!.DeepClone(),["sourceWritten"]=false,["compiled"]=false};
 }
}
