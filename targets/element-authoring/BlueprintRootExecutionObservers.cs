using Confectory.Core;
using System.Text.Json.Nodes;

static partial class BlueprintRootExecution
{
    // An unused import alone does not change generated code. Native context
    // nodes do bind their implementation imports, even without a call card.
    static bool UsesFunction(Element implementation,JsonObject graph,string feature)=>BlueprintTree.Nodes(graph).Any(n=>
        n.Node["kind"]?.ToString()=="call"&&n.Node["feature"]?.ToString()==feature||
        n.Node["imports"]?.AsArray().Any(id=>id?.ToString()==feature)==true||
        n.Node["implementationContext"] is JsonObject&&implementation.Imports.Values.Any(i=>i.Id==feature));

    static string[] ReferencedFunctions(Element implementation,JsonObject graph)=>implementation.Imports.Values.Select(i=>i.Id)
        .Concat(BlueprintTree.Nodes(graph).Where(n=>n.Node["kind"]?.ToString()=="call").Select(n=>n.Node["feature"]!.ToString()))
        .Concat(BlueprintTree.Nodes(graph).SelectMany(n=>n.Node["imports"]?.AsArray().Select(id=>id!.ToString())??Enumerable.Empty<string>()))
        .Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal).ToArray();

    static string[] ContextIds(JsonObject choices)=>choices["targets"]!.AsArray().Select(t=>t!["graph"]!.ToString())
        .Concat(choices["callers"]!.AsArray().Select(c=>c!["graph"]!.ToString()))
        .Concat(choices["observers"]!.AsArray().Select(id=>id!.ToString())).Distinct(StringComparer.Ordinal).ToArray();

    static Dictionary<string,JsonNode> CodeDefinitions(JsonObject definitions)=>(definitions["nodes"]?.AsArray()??new JsonArray())
        .Concat(definitions["nestedNodes"]?.AsArray()??new JsonArray()).Where(n=>n?["definition"]?["kind"]?.ToString()=="code")
        .ToDictionary(n=>n!["id"]!.ToString(),n=>n!.DeepClone(),StringComparer.Ordinal);

    // This is receipt maintenance, never source repair. The complete original
    // graph was ready before mutation. Prove the only definition difference is
    // this callee's contract hash before retaining the original source/helpers.
    static void RefreshCodeReceipts(JsonObject units,string graphId,Dictionary<string,JsonNode> before,Dictionary<string,JsonNode> after,string feature,string oldHash,string newHash)
    {
        if(!before.Keys.ToHashSet(StringComparer.Ordinal).SetEquals(after.Keys))throw new ArgumentException("Preserve every original owned code node");
        foreach(var pair in before){var previous=pair.Value;var next=after[pair.Key];if(previous["definitionHash"]!.ToString()==next["definitionHash"]!.ToString())continue;
            var normalized=next["definition"]!.DeepClone().AsObject();var oldReferences=previous["definition"]?["featureContracts"] as JsonObject;var newReferences=normalized["featureContracts"] as JsonObject;
            if(oldReferences?[feature]?.ToString()!=oldHash||newReferences?[feature]?.ToString()!=newHash)throw new ArgumentException("Only the observed callee contract may change a code receipt");
            newReferences![feature]=oldReferences![feature]!.DeepClone();if(!JsonNode.DeepEquals(previous["definition"],normalized))throw new ArgumentException("Preserve original source ownership, signature, context and connections");
            string id=BlueprintTree.SourceId(graphId,pair.Key);var unit=units[id]??throw new ArgumentException("Exact original code source required");var record=JsonNode.Parse(unit["draft"]!.GetValue<string>())!.AsObject();
            if(unit["kind"]?.ToString()!="blueprint-node"||record["definitionHash"]?.ToString()!=previous["definitionHash"]!.ToString())throw new ArgumentException("Do not adopt a stale original code receipt");
            record["definitionHash"]=next["definitionHash"]!.DeepClone();unit["draft"]=record.ToJsonString();
        }
    }
}
