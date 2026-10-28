using Confectory.Core;
using System.Text.Json.Nodes;

// The existing owner transaction may change only direct function presentation.
// Signature, relations, registration, implementations and caller sources stay fixed.
internal static class FunctionPresentation
{
 public static JsonObject Prepare(JsonObject request,Func<Element,string> format,Func<Manifest,string> formatManifest)
 {
  string project=request["project"]!.GetValue<string>(),manifest=request["manifest"]!.GetValue<string>(),id=request["id"]!.GetValue<string>(),text=request["text"]!.GetValue<string>();
  var function=new Parser(text,"<function-presentation>").ParseElement();var registration=new Parser(manifest,"<function-presentation-project>").ParseManifest();var changes=request["changes"]!.AsArray();
  if(registration.Kind!="project"||function.Id!=id||function.Kind!="function"||!id.StartsWith(registration.Namespace+"::",StringComparison.Ordinal)||changes.Count is <1 or >2)throw new ArgumentException("Direct owned function presentation required");
  string local=id[(registration.Namespace.Length+2)..];if(!registration.Elements.TryGetValue(local,out var locator)||locator.Kind!="function")throw new ArgumentException("Registered owned function required");
  var drafts=request["drafts"]!.AsArray();if(drafts.Count>255)throw new ArgumentException("Function presentation source budget");
  string Read(string path){var file=new FileInfo(path);if(!file.Exists||file.Length>1048576)throw new IOException("Presentation source budget");return File.ReadAllText(path);}
  JsonObject Inspect(string source)=>EffectiveMetadata.Query(project,manifest,id,source,formatManifest,Read,drafts,schemaView:true,validateObjects:true,observeSources:true);
  void Valid(JsonObject value){if(value["status"]?.ToString()!="available"||value["schemaModel"]?["validation"]?["status"]?.ToString()!="valid")throw new InvalidOperationException("Function presentation context changed; retain input");}
  var before=Inspect(text);Valid(before);var seen=new HashSet<string>(StringComparer.Ordinal);
  foreach(var row in changes){if(row is not JsonObject edit||edit.Count!=2||edit.Any(pair=>pair.Key is not ("type" or "text"))||edit["type"] is not JsonValue kind||!kind.TryGetValue<string>(out var type)||!seen.Add(type)||edit["text"] is not JsonValue value||!value.TryGetValue<string>(out var content))throw new ArgumentException("Exact distinct presentation edits required");if(type=="icon")DeclarationAuthoring.Icon(function,content);else if(type=="description"){if(content.Length>240)throw new ArgumentException("Function description budget");function.Description=content;function.DescriptionPresent=true;}else throw new ArgumentException("Only glyph and description may use this function transaction");}
  string next=DeclarationTextMerge.MergeFunction(text,format(function),format);Valid(Inspect(next));
  return new JsonObject{["text"]=next,["manifest"]=manifest,["additions"]=new JsonArray(),["updates"]=new JsonArray(),["observations"]=before["observations"]!.DeepClone(),["sourceWritten"]=false,["compiled"]=false};
 }
}
