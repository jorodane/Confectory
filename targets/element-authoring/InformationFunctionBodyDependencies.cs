using Confectory.Core;
using System.Text.Json.Nodes;

// Retain exact existing registration proofs across body and presentation Saves.
// External declarations/parents are observations; provider bodies are not read.
internal static class InformationFunctionBodyDependencies
{
 internal static JsonObject Plans(JsonNode? declaration,JsonObject? receipt=null)
 {
  var changes=declaration?["changes"] as JsonArray??new();var plans=new JsonObject();foreach(var row in changes.Count(row=>row?["mapping"]?["bodies"] is JsonObject bodies&&bodies.Count>0)>=2?changes:new JsonArray())if(row?["mapping"]?["dependencies"] is JsonObject proof&&proof.Count>0){string id=row["id"]!.ToString();if(!plans.TryAdd(id,proof.DeepClone()))throw new ArgumentException("One registered body proof per function required");}
  if(receipt?["nativeBodyDependencies"] is JsonObject retained){if(plans.Count>0&&!JsonNode.DeepEquals(plans,retained))throw new InvalidOperationException("Retain the exact original registered body proofs across presentation Saves");plans=retained.DeepClone().AsObject();}
  if(plans.Count>8||plans.Any(p=>p.Value is not JsonObject proof||proof.Count is <1 or >64))throw new ArgumentException("Bounded original registered body proofs required");return plans;
 }
 internal static JsonArray Reads(JsonObject request,IEnumerable<string> functions,JsonObject plans)
 {
  var units=request["units"]!.DeepClone().AsObject();string ns=request["namespace"]!.ToString();if(units.Count>2048)throw new ArgumentException("Original registered source budget");
  foreach(var pair in units)if(pair.Value?["original"] is JsonValue original)pair.Value!["draft"]=original.DeepClone();
  var ids=functions.Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal).ToArray();if(ids.Length==1&&plans.Count==0)return new JsonArray();if(ids.Length is <2 or >8)throw new ArgumentException("Exact native body function group required");
  // Existing local-only receipts stay pure and do not acquire registry I/O or
  // a new project-context requirement. Missing external proofs still reject.
  bool external=units.Where(p=>p.Value?["kind"]?.ToString()=="implementation").Select(p=>new Parser(p.Value!["draft"]!.ToString(),"<original-body-registration>").ParseElement()).Any(d=>(ids.Contains(d.Function,StringComparer.Ordinal)||d.Imports.Values.Any(i=>ids.Contains(i.Id,StringComparer.Ordinal)))&&d.Imports.Values.Any(i=>PackPaths.Namespace(i.Id)!=ns));
  if(!external){if(plans.Count>0)throw new InvalidOperationException("Unexpected registered body proofs");return new JsonArray();}
  var source=new JsonObject{["project"]=request["project"]!.DeepClone(),["manifest"]=units[ns+"::ProjectManifest"]!["draft"]!.DeepClone(),["units"]=units};var reader=new InformationFunctionDependencies(source);var actual=new JsonObject();
  foreach(string id in ids){if(!id.StartsWith(ns+"::",StringComparison.Ordinal)||units[id]?["kind"]?.ToString()!="function")throw new InvalidOperationException("Registered declarations never become owned body members");var proof=reader.Read(id,units);if(proof.Count>0)actual[id]=proof;}
  if(!JsonNode.DeepEquals(plans,actual))throw new InvalidOperationException("Original registered native import receipts changed or are incomplete; all input retained");return reader.Observations();
 }
}
