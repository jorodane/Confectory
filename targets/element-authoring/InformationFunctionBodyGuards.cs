using Confectory.Core;
using System.Text.Json.Nodes;

// Keep the already observed owned source snapshot as read checks, never writes.
// The existing slot receipt and final source lease carry these checks unchanged.
internal static class InformationFunctionBodyGuards
{
 public static JsonObject Execute(JsonObject request)
 {
  string ns=request["namespace"]!.ToString();var units=request["units"]!.AsObject();
  bool ImportedGroup(JsonNode? declaration)
  {
   if(declaration?["raw"] is not null||declaration?["changes"] is not JsonArray changes||changes.Count is <2 or >8)return false;
   bool imported=false;
   foreach(var row in changes){
    if(row?["type"]?.ToString()!="function-edit"||row["mapping"] is not JsonObject mapping||!JsonNode.DeepEquals(mapping["before"],row["signature"])||mapping["bodies"] is not JsonObject bodies||bodies.Count==0)return false;
    foreach(var body in bodies){
     if(body.Value?["whole"] is not null||body.Value?["wrapper"] is not null||units[body.Key]?["kind"]?.ToString()!="body")return false;
     int at=body.Key.LastIndexOf("/body:",StringComparison.Ordinal);if(at<0)throw new ArgumentException("Exact native body owner required");string id=body.Key[..at];var unit=units[id];if(!id.StartsWith(ns+"::",StringComparison.Ordinal)||unit?["kind"]?.ToString()!="implementation")throw new ArgumentException("Owned native implementation required");
     string? text=unit["original"]?.ToString();if(string.IsNullOrEmpty(text))text=unit["draft"]?.ToString();if(text is null)throw new InvalidOperationException("Read the original native implementation before reviewing its dependencies");var implementation=new Parser(text,"<native-body-read-scope>").ParseElement();
     if(implementation.Id!=id||implementation.Function!=row["id"]?.ToString()||implementation.Parent is not null||implementation.Bodies.Count!=1||implementation.Bodies.Single().Value.SourceKind!="csharp")throw new InvalidOperationException("Retain the original native body and contract scope");
     imported|=implementation.Imports.Count>0;
    }
   }
   return imported;
  }
  bool Token(string value)=>value=="missing"||System.Text.RegularExpressions.Regex.IsMatch(value,"^[a-f0-9]{64}$");
  Dictionary<string,JsonObject> Sources(bool preparing)
  {
   if(units.Count>2048)throw new ArgumentException("Native body source budget");var result=new Dictionary<string,JsonObject>(StringComparer.Ordinal);foreach(var pair in units){if(!pair.Key.StartsWith(ns+"::",StringComparison.Ordinal))continue;var unit=pair.Value!;string path=unit["path"]?.ToString()??throw new ArgumentException("Known owned source path required");if(Path.IsPathRooted(path))throw new ArgumentException("Relative native source checks required");string? baseline=unit["baseline"]?.ToString();if(preparing&&(baseline is null||!Token(baseline)))throw new InvalidOperationException("Read the complete native source snapshot before Save");
    if(result.TryGetValue(path,out var prior)){if(preparing&&prior["hash"]?.ToString()!=baseline)throw new InvalidOperationException("Native source aliases disagree on their original baseline");continue;}result[path]=new JsonObject{["path"]=path,["hash"]=preparing?baseline:null};
   }
   if(result.Count is <1 or >240)throw new ArgumentException("Complete bounded native source checks required");return result;
  }
  if(request["action"]?.ToString()=="prepare")return ImportedGroup(request["declaration"])?new JsonObject{["required"]=true,["checks"]=new JsonArray(Sources(true).Values.Select(v=>(JsonNode)v).ToArray())}:new JsonObject{["required"]=false,["checks"]=new JsonArray()};
  if(request["action"]?.ToString()!="validate")throw new ArgumentException("Native body guard action");var selected=request["selected"]?.AsArray()??throw new ArgumentException("Selected native group required");if(selected.Count>64)throw new ArgumentException("Native body review budget");
  foreach(var pair in units){var unit=pair.Value;if(unit?["atomicEditGroup"] is not JsonArray group||!selected.Any(id=>group.Any(member=>member!.ToString()==id!.ToString()))||unit["slotSaveReceipt"] is not JsonObject receipt||!ImportedGroup(receipt["declaration"]))continue;
   if(receipt["owner"]?.ToString()!=pair.Key||receipt["version"]?.GetValue<int>()!=3||receipt["readGuards"] is not JsonObject guards)throw new InvalidOperationException("Save the native body group explicitly to bind its original dependencies; input retained");var expected=Sources(false);if(guards.Count!=expected.Count||expected.Keys.Any(path=>guards[path] is not JsonObject row||row.Count!=2||row["path"]?.ToString()!=path||row["hash"] is null||!Token(row["hash"]!.ToString())))throw new InvalidOperationException("Complete original native body source checks are missing or changed; retain the saved group");
  }
  return new JsonObject{["validated"]=true};
 }
}
