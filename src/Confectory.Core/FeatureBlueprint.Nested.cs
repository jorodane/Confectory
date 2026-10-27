using System.Text.Json.Nodes;

namespace Confectory.Core;

public static partial class FeatureBlueprint
{
    public const string NestedProfile = "sync-acyclic-nested-v1", NestedGenerator = "feature-blueprint-source-v9";
    static string RecordKey(JsonObject request, string id) => request["sourcePath"] is null ? id : S(request, "sourcePath") + "/" + id;

    static JsonObject PrivateRequest(JsonObject parent, JsonObject node, FunctionSignature signature)
    {
        string key = RecordKey(parent, S(node, "id"));
        string feature = "Blueprint.Private::N" + Hash(S(parent,"sourceOwner") + "/" + key)[..32];
        string source = "function " + feature + " " + signature.Format() + " {}";
        var graph = node["graph"]!.DeepClone().AsObject();
        graph["feature"] = feature;
        graph["contractHash"] = ContractHash(new Parser(source, "<private-contract>").ParseElement());
        string operation = S(parent, "operation");
        string? probe = parent["node"]?.ToString();
        bool selected = operation == "featureBlueprintNodeProbe" && probe!.StartsWith(S(node, "id") + "/", StringComparison.Ordinal);
        return new JsonObject
        {
            ["operation"] = operation == "featureBlueprintNodeProbe" && !selected ? "featureBlueprintNodes" : operation,
            ["node"] = selected ? probe![(S(node, "id").Length + 1)..] : null,
            ["featureSource"] = source, ["graph"] = graph, ["sourcePath"] = key, ["sourceOwner"] = parent["sourceOwner"]!.DeepClone(),
            ["featureContracts"] = parent["featureContracts"]?.DeepClone(), ["propertyContracts"] = parent["propertyContracts"]?.DeepClone(),
            ["inspectStalePostCalls"] = parent["inspectStalePostCalls"]?.DeepClone(),
            ["implementations"] = parent["implementations"]?.DeepClone()
        };
    }

    static JsonObject Process(JsonObject original)
    {
        var request = original.DeepClone().AsObject();
        request["privateChildren"] = new JsonObject();
        if(SupportsPrivateGraphs(request["graph"]?["profile"]?.ToString()) && request["sourceOwner"] is null){
            string owner=request["implementationContext"]?["implementation"]?.ToString()??S(request["graph"],"feature");
            request["sourceOwner"]=owner+(request["bodyTarget"] is null?"":"/body:"+S(request,"bodyTarget"));
        }
        JsonObject result;
        try { result = ProcessCore(request); }
        catch (Refusal refusal)
        {
            string? path = request["sourcePath"]?.ToString();
            if (path is not null && !refusal.Subject.StartsWith(path + "/", StringComparison.Ordinal)) throw new Refusal(refusal.Code, path + "/" + refusal.Subject);
            throw;
        }
        // A qualified independent leaf probe already carries its complete path.
        if (S(request, "operation") == "featureBlueprintNodeProbe" && request["node"]!.ToString().Contains('/')) return result;
        string? prefix = request["sourcePath"]?.ToString();
        if (prefix is not null)
        {
            if (result["node"] is not null) result["node"] = prefix + "/" + result["node"];
            foreach (var node in result["nodes"]?.AsArray() ?? new JsonArray()) node!["id"] = prefix + "/" + node["id"];
            foreach (var map in result["sourceMap"]?.AsArray() ?? new JsonArray()) map!["node"] = prefix + "/" + map["node"];
            foreach (var node in result["nodeSources"]?.AsArray() ?? new JsonArray()) node!["id"] = prefix + "/" + node["id"];
        }
        var descendants = new JsonArray();
        var summaries = new JsonObject();
        var nestedWarnings = new JsonArray();
        foreach (var child in request["privateChildren"]!.AsObject())
        {
            var value = child.Value!.AsObject();
            foreach(var warning in value["warnings"]?.AsArray()??new JsonArray()){
                var scoped=warning!.DeepClone().AsObject();scoped["privatePath"]=RecordKey(request,child.Key);nestedWarnings.Add(scoped);
            }
            foreach(var warning in value["nestedWarnings"]?.AsArray()??new JsonArray())nestedWarnings.Add(warning!.DeepClone());
            foreach (var node in value["nodes"]?.AsArray() ?? new JsonArray()) descendants.Add(node!.DeepClone());
            foreach (var node in value["nestedNodes"]?.AsArray() ?? new JsonArray()) descendants.Add(node!.DeepClone());
            foreach (string collection in new[] { "sourceMap", "nodeSources" })
                if (result[collection] is JsonArray target) foreach (var node in value[collection]?.AsArray() ?? new JsonArray()) target.Add(node!.DeepClone());
            if (result["members"] is not null && value["members"] is not null) result["members"] = result["members"]!.GetValue<string>() + value["members"]!.GetValue<string>();
            var summary = value.DeepClone().AsObject();
            foreach (string field in new[] { "body", "members", "sourceMap", "nodeSources" }) summary.Remove(field);
            summaries[child.Key] = summary;
        }
        if(result["body"] is not null && result["members"] is not null) result["bodyHash"] = Hash(result["body"]!.GetValue<string>() + result["members"]!.GetValue<string>());
        if (summaries.Count > 0) { result["children"] = summaries; result["nestedNodes"] = descendants; }
        if(nestedWarnings.Count>0)result["nestedWarnings"]=nestedWarnings;
        return result;
    }
}
