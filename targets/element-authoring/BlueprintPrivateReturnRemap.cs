using Confectory.Core;
using System.Text.Json.Nodes;

internal static class BlueprintPrivateReturnRemap
{
    public static JsonObject Choices(JsonObject root, string path)
    {
        var result = new JsonObject();
        var frames = path.Split('/');
        if (frames.Length > 2 || frames.Any(string.IsNullOrEmpty)
            || root["profile"]?.ToString() != FeatureBlueprint.NestedProfile)
            return result;
        if (frames.Length == 1 ? Serial(root, path) is null : !SerialMethodTree(root, depth: 2))
            return result;
        var child = BlueprintTree.Select(root, path);
        if (child["profile"]?.ToString() != FeatureBlueprint.MethodsProfile) return result;
        var order = Serial(child, null);
        if (order is null) return result;

        for (int index = 0; index + 1 < order.Count; index++)
        {
            var producer = order[index];
            string id = producer["id"]!.ToString();
            string? originalType = producer["signature"]?["return"]?.ToString();
            string? returnType = originalType switch { "long" => "double", "double" => "long", _ => null };
            if (returnType is null) continue;
            var outputs = producer["signature"]!["args"]!.AsArray()
                .Where(arg => arg?["mode"]?.ToString() == "out" && arg["type"]?.ToString() == originalType)
                .ToArray();
            if (outputs.Length != 1) continue;
            var consumer = order[index + 1];
            var uses = order.SelectMany(node => ReturnUses(node["arguments"], id))
                .Concat(ReturnUses(child["exits"], id)).Concat(ReturnUses(child["locals"], id))
                .Take(2).ToArray();
            if (uses.Length != 1 || uses[0].Count != (uses[0].ContainsKey("output") ? 2 : 1)
                || uses[0].Parent is not JsonObject arguments || !ReferenceEquals(arguments, consumer["arguments"]))
                continue;
            string name = arguments.Single(entry => ReferenceEquals(entry.Value, uses[0])).Key;
            if (!consumer["signature"]!["args"]!.AsArray().Any(arg => arg?["name"]?.ToString() == name
                && arg["type"]?.ToString() == originalType && arg["mode"] is null)) continue;
            result[id] = new JsonObject
            {
                ["consumer"] = consumer["id"]!.DeepClone(), ["argument"] = name,
                ["output"] = outputs[0]!["name"]!.DeepClone(), ["returnType"] = returnType
            };
        }
        return result;
    }

    // A two-level edit keeps both ancestor contracts and the other serial frames intact.
    static bool SerialMethodTree(JsonObject graph, int depth)
    {
        string? profile = graph["profile"]?.ToString();
        bool methods = profile == FeatureBlueprint.MethodsProfile;
        if (!methods && (depth == 0 || profile != FeatureBlueprint.NestedProfile)) return false;
        return Serial(graph, null, allowGraphs: !methods) is { } order
            && order.All(node => node["retainedCode"] is null && node["sourceIdentity"] is null
                && node["postCall"] is null && node[BlueprintCompletionAdapter.Metadata] is null
                && (node["kind"]?.ToString() != "graph"
                    || node["graph"] is JsonObject child && SerialMethodTree(child, depth - 1)));
    }

    static List<JsonObject>? Serial(JsonObject graph, string? child, bool allowGraphs = false)
    {
        if (graph["schema"]?.GetValue<int>() != 1 || graph["copySource"] is not null
            || graph["executionExitMode"] is not null || graph["exits"] is not JsonObject { Count: 1 } exits
            || graph["nodes"] is not JsonArray { Count: > 0 and <= 32 } nodes
            || graph["edges"] is not JsonArray edges || edges.Count != nodes.Count)
            return null;
        var byId = nodes.Select(node => node!.AsObject()).ToDictionary(node => node["id"]!.ToString(), StringComparer.Ordinal);
        bool OrdinaryKind(JsonObject node) => node["id"]?.ToString() == child
            ? node["kind"]?.ToString() == "graph"
            : node["kind"]?.ToString() == "code" || allowGraphs && node["kind"]?.ToString() == "graph";
        if (byId.Values.Any(node => !OrdinaryKind(node)
            || node["control"]?.ToString() != "next" || new[] { "implementationContext", "contextBoundary", "forwardCallerStorage",
                "executionEnum", "executionSource", "completionBranch", "branchOwner", "async" }.Any(node.ContainsKey))) return null;
        var next = edges.Where(edge => edge?["port"]?.ToString() == "next")
            .ToDictionary(edge => edge!["from"]!.ToString(), edge => edge!["to"]!.ToString(), StringComparer.Ordinal);
        string at = graph["entry"]!.ToString();
        var order = new List<JsonObject>(nodes.Count);
        while (byId.Remove(at, out var node) && next.TryGetValue(at, out var after))
        {
            order.Add(node);
            at = after;
        }
        return order.Count == nodes.Count && at == "exit:" + exits.Single().Key
            && (child is null || order.Any(node => node["id"]?.ToString() == child)) ? order : null;
    }

    static IEnumerable<JsonObject> ReturnUses(JsonNode? value, string node)
    {
        if (value is JsonObject obj)
        {
            if (obj.ContainsKey("constant")) yield break;
            if (obj["node"]?.ToString() == node && (obj["output"]?.ToString() ?? "return") == "return") yield return obj;
            foreach (var field in obj)
                foreach (var use in ReturnUses(field.Value, node)) yield return use;
        }
        else if (value is JsonArray array)
            foreach (var item in array)
                foreach (var use in ReturnUses(item, node)) yield return use;
    }
}
