using Confectory.Core;
using System.Text.Json.Nodes;

// Qualified record keys are graph identities, never filesystem paths.
internal static class ImplementationCopyTree
{
 internal static IEnumerable<JsonObject> Rows(JsonObject definitions)=>
  (definitions["nodes"]?.AsArray()??new JsonArray()).Concat(definitions["nestedNodes"]?.AsArray()??new JsonArray()).Select(n=>n!.AsObject());
 internal static JsonObject Definition(JsonObject definitions,string key)=>Rows(definitions).Single(n=>n["id"]!.ToString()==key);
}
