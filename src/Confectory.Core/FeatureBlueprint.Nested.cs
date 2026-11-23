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
        string source = "function " + feature + " " + signature.Format() + (node["async"]?.GetValue<bool>() == true
            ? " { value blueprintAsync = " + System.Text.Json.JsonSerializer.Serialize(new JsonObject { ["schema"]=1,["completion"]="private_completion" }.ToJsonString()) + "; }" : " {}");
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
            ["implementationContext"] = parent["implementationContext"]?.DeepClone(),
            ["executionForward"] = node["control"]?.ToString()=="switch" ? new JsonObject { ["source"]=node["executionSource"]?.DeepClone(), ["enum"]=node["executionEnum"]?.DeepClone(),["native"]=BlueprintPrivateCompletion.OwnsResults(node),["completionIds"]=BlueprintPrivateCompletion.CompletionIds(node) } : null,
            ["inspectStalePostCalls"] = parent["inspectStalePostCalls"]?.DeepClone(),
            ["inspectStaleAsyncCalls"] = parent["inspectStaleAsyncCalls"]?.DeepClone(),
            ["inspectPendingAsyncCaller"] = parent["inspectPendingAsyncCaller"]?.DeepClone(),
            ["implementations"] = parent["implementations"]?.DeepClone(),
            ["assemblyPath"] = parent["assemblyPath"]?.DeepClone()
        };
    }

    static JsonObject Process(JsonObject original)
    {
        var request = original.DeepClone().AsObject();
        request["privateChildren"] = new JsonObject();
        if (request["sourcePath"] is null && SupportsPrivateGraphs(request["graph"]?["profile"]?.ToString()))
            Need(BlueprintTree.Nodes(request["graph"]!.AsObject()).Count(entry => entry.Node["implementationContext"] is JsonObject) <= 1, "GRAPH_IMPLEMENTATION_CONTEXT_DUPLICATE", "physical implementation member");
        if(SupportsPrivateGraphs(request["graph"]?["profile"]?.ToString()) && request["sourceOwner"] is null){
            string owner=request["implementationContext"]?["implementation"]?.ToString()??S(request["graph"],"feature");
            request["sourceOwner"]=owner+(request["bodyTarget"] is null?"":"/body:"+S(request,"bodyTarget"));
        }
        string? prefix = request["sourcePath"]?.ToString();
        bool selected = prefix is not null && request["assemblyPath"]?.ToString() == prefix;
        List<(string Id, string Text)>? methodMembers = selected && request["graph"]?["profile"]?.ToString() is (MethodsProfile or SwitchProfile)
            ? [] : null;
        JsonObject result;
        try { result = ProcessCore(request, methodMembers); }
        catch (Refusal refusal)
        {
            string? path = request["sourcePath"]?.ToString();
            if (path is not null && !refusal.Subject.StartsWith(path + "/", StringComparison.Ordinal)) throw new Refusal(refusal.Code, path + "/" + refusal.Subject);
            throw;
        }
        result["usesImplementationContext"] = request["graph"]!["nodes"]!.AsArray().Any(node => node?["implementationContext"] is JsonObject) || request["privateChildren"]!.AsObject().Any(child => child.Value?["usesImplementationContext"]?.GetValue<bool>() == true);
        // A qualified independent leaf probe already carries its complete path.
        if (S(request, "operation") == "featureBlueprintNodeProbe" && request["node"]!.ToString().Contains('/')) return result;
        if (prefix is not null)
        {
            if (result["node"] is not null) result["node"] = prefix + "/" + result["node"];
            foreach (var node in result["nodes"]?.AsArray() ?? new JsonArray()) node!["id"] = prefix + "/" + node["id"];
            foreach (var map in result["sourceMap"]?.AsArray() ?? new JsonArray()) map!["node"] = prefix + "/" + map["node"];
            foreach (var node in result["nodeSources"]?.AsArray() ?? new JsonArray()) node!["id"] = prefix + "/" + node["id"];
        }
        JsonObject? selectedAssembly = null;
        var descendants = new JsonArray();
        var summaries = new JsonObject();
        var nestedWarnings = new JsonArray();
        foreach (var child in request["privateChildren"]!.AsObject())
        {
            var value = child.Value!.AsObject();
            if(value["selectedAssembly"] is JsonObject assembled){
                Need(selectedAssembly is null,"GRAPH_ASSEMBLY_PATH_DUPLICATE",assembled["path"]!.ToString());
                selectedAssembly=assembled.DeepClone().AsObject();
            }
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
            foreach (string field in new[] { "body", "members", "sourceMap", "nodeSources", "selectedAssembly" }) summary.Remove(field);
            summaries[child.Key] = summary;
        }
        if(result["body"] is not null && result["members"] is not null) result["bodyHash"] = Hash(result["body"]!.GetValue<string>() + result["members"]!.GetValue<string>());
        // Capture this instance after collecting its own descendants, before
        // an ancestor adds any siblings and removes source from child summaries.
        if (selected && prefix is not null && S(result, "state") == "source-assembled")
        {
            Need(selectedAssembly is null, "GRAPH_ASSEMBLY_PATH_DUPLICATE", prefix);
            var included = BlueprintTree.Nodes(request["graph"]!.AsObject()).ToArray();
            bool ExactPaths(string collection, string key, IEnumerable<BlueprintTree.Entry> expected)
            {
                var paths = expected.Select(entry => prefix + "/" + entry.Key).ToHashSet(StringComparer.Ordinal);
                var rows = result[collection]!.AsArray();
                return rows.Count == paths.Count && paths.SetEquals(rows.Select(row => S(row, key)));
            }
            var code = included.Where(entry => S(entry.Node, "kind") == "code").ToArray();
            string members = S(result, "members");
            // Method helpers are separate class members. Match the entire
            // member buffer to contributions captured at its regular emit site.
            bool exactMembers = methodMembers is null ? members.Length == 0
                : code.Length == included.Length && methodMembers.Count == code.Length
                    && code.Select(entry => entry.Key).ToHashSet(StringComparer.Ordinal)
                        .SetEquals(methodMembers.Select(member => member.Id))
                    && members == string.Concat(methodMembers.Select(member => member.Text));
            Need(exactMembers && ExactPaths("sourceMap", "node", included)
                && ExactPaths("nodeSources", "id", code),
                "GRAPH_ASSEMBLY_SCOPE", prefix);
            selectedAssembly = new JsonObject { ["path"] = prefix, ["body"] = result["body"]!.DeepClone(),
                ["members"] = result["members"]!.DeepClone(), ["bodyHash"] = result["bodyHash"]!.DeepClone() };
        }
        if (summaries.Count > 0) { result["children"] = summaries; result["nestedNodes"] = descendants; }
        if(nestedWarnings.Count>0)result["nestedWarnings"]=nestedWarnings;
        if(selectedAssembly is not null)result["selectedAssembly"]=selectedAssembly;
        return result;
    }
}
