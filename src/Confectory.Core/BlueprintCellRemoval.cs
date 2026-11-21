using System.Text.Json.Nodes;

namespace Confectory.Core;

public static class BlueprintCellRemoval
{
    static string Value(JsonNode? row, string key) => row?[key]?.GetValue<string>() ?? "";

    public static string[] Options(JsonObject graph)
    {
        if (graph["schema"]?.GetValue<int>() != 1 ||
            Value(graph, "profile") is not (FeatureBlueprint.Profile or FeatureBlueprint.ImplicitProfile or
                FeatureBlueprint.MethodsProfile or FeatureBlueprint.NestedProfile or FeatureBlueprint.SwitchProfile) ||
            graph["copySource"] is not null || graph["executionExitMode"]?.GetValue<bool>() == true ||
            graph["locals"] is not (null or JsonArray { Count: 0 }) ||
            graph["nodes"] is not JsonArray nodes || nodes.Count is < 2 or > 63 ||
            graph["edges"] is not JsonArray edges ||
            graph["exits"] is not JsonObject exits)
            return [];

        if (Value(graph, "profile") == FeatureBlueprint.SwitchProfile &&
            nodes.Any(node => Value(node, "control") == "switch"))
            return BlueprintCellRegion.RemovableCaseCells(graph);

        if (edges.Count != nodes.Count || nodes.Any(node => Value(node, "kind") != "code" || Value(node, "control") != "next" ||
            new[] { "branchOwner", "executionEnum", "implementationContext", "contextBoundary", "retainedCode",
                "sourceIdentity", "postCall", "executionSource", "graph" }.Any(field => node?[field] is not null) ||
            node?["async"]?.GetValue<bool>() == true || node?["forwardCallerStorage"]?.GetValue<bool>() == true))
            return [];
        var ids = nodes.Select(node => Value(node, "id")).ToHashSet(StringComparer.Ordinal);
        if (ids.Count != nodes.Count || edges.Any(edge => Value(edge, "port") != "next" || !ids.Contains(Value(edge, "from"))) ||
            edges.Select(edge => Value(edge, "from")).Distinct(StringComparer.Ordinal).Count() != nodes.Count)
            return [];
        var links = edges.ToDictionary(edge => Value(edge, "from"), edge => Value(edge, "to"), StringComparer.Ordinal);
        var visited = new HashSet<string>(StringComparer.Ordinal);
        string next = Value(graph, "entry");
        while (links.TryGetValue(next, out var target) && visited.Add(next)) next = target;
        if (visited.Count != nodes.Count || !next.StartsWith("exit:", StringComparison.Ordinal) || !exits.ContainsKey(next[5..]))
            return [];

        var referenced = new HashSet<string>(StringComparer.Ordinal);
        void VisitValues(JsonNode? value)
        {
            if (value is JsonObject obj) {
                if (obj["node"] is JsonValue link && link.TryGetValue<string>(out var id)) referenced.Add(id);
                foreach (var pair in obj) VisitValues(pair.Value);
            }
            else if (value is JsonArray children) foreach (var child in children) VisitValues(child);
        }
        foreach (var node in nodes) VisitValues(node!["arguments"]);
        VisitValues(exits);
        return nodes.Where(node => node!["signature"] is JsonObject signature && Value(signature, "return") == "void" &&
            signature["args"] is JsonArray { Count: 0 } && node["arguments"] is null or JsonObject { Count: 0 } &&
            !referenced.Contains(Value(node, "id"))).Select(node => Value(node, "id")).ToArray();
    }

    public static JsonObject Remove(JsonObject graph, string id)
    {
        if (!Options(graph).Contains(id, StringComparer.Ordinal))
            throw new ArgumentException("Only one unconnected void action in an explicit serial root or case can be removed");
        var result = graph.DeepClone().AsObject();
        var nodes = result["nodes"]!.AsArray();
        nodes.Remove(nodes.Single(node => Value(node, "id") == id));
        var edges = result["edges"]!.AsArray();
        var outgoing = edges.Single(edge => Value(edge, "from") == id)!;
        var successor = outgoing["to"]!.DeepClone();
        if (Value(result, "entry") == id) result["entry"] = successor;
        else edges.Single(edge => Value(edge, "to") == id)!["to"] = successor;
        edges.Remove(outgoing);
        return result;
    }
}
