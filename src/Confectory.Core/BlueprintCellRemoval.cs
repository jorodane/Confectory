using System.Text.Json.Nodes;

namespace Confectory.Core;

public static class BlueprintCellRemoval
{
    static string Value(JsonNode? row, string key) => row?[key]?.GetValue<string>() ?? "";
    static bool PlainAction(JsonNode node) =>
        Value(node, "control") == "next" &&
        new[] { "branchOwner", "executionEnum", "implementationContext", "contextBoundary", "retainedCode",
            "sourceIdentity", "postCall", "executionSource" }.All(field => node[field] is null) &&
        node["async"]?.GetValue<bool>() != true && node["forwardCallerStorage"]?.GetValue<bool>() != true;

    static bool NoValuePins(JsonNode node) =>
        node["signature"] is JsonObject signature && Value(signature, "return") == "void" &&
        signature["args"] is JsonArray { Count: 0 } && node["arguments"] is null or JsonObject { Count: 0 };

    internal static bool IsCompound(JsonObject graph, string id) =>
        !id.Contains('/') && graph["nodes"]!.AsArray().Any(node => Value(node, "id") == id && Value(node, "kind") == "graph");

    // The graph before the change is the authority for complete qualified membership.
    public static string[] SourceKeys(JsonObject graph, string id) => IsCompound(graph, id)
        ? BlueprintTree.Select(graph, id)["nodes"]!.AsArray().Select(node => id + "/" + Value(node, "id")).ToArray()
        : [id];

    public static string[] Options(JsonObject graph, string frame)
    {
        if (frame.Length == 0) return Options(graph);
        if (frame.Contains('/')) return [];
        try {
            return Options(BlueprintCellRegion.OwnedFrame(graph, frame));
        }
        catch (Exception error) when (error is ArgumentException or InvalidOperationException) {
            return [];
        }
    }

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

        bool compound = Value(graph, "profile") == FeatureBlueprint.NestedProfile &&
            nodes.Any(node => Value(node, "kind") == "graph");
        if (edges.Count != nodes.Count || nodes.Any(node => node is not JsonObject || !PlainAction(node) ||
            (Value(node, "kind") != "code" || node["graph"] is not null) &&
            (!compound || Value(node, "kind") != "graph")))
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
        return nodes.Where(node => NoValuePins(node!) && !referenced.Contains(Value(node, "id")) &&
            (compound ? Value(node, "kind") == "graph" && PlainCompound(graph, Value(node, "id")) : true))
            .Select(node => Value(node, "id")).ToArray();
    }

    static bool PlainCompound(JsonObject root, string id)
    {
        try {
            var child = BlueprintCellRegion.OwnedFrame(root, id);
            return child["schema"]?.GetValue<int>() == 1 && child["locals"] is null or JsonArray { Count: 0 } &&
                child["exits"] is JsonObject exits && exits.All(exit => exit.Value is null) &&
                child["nodes"]!.AsArray().All(node => PlainAction(node!) && NoValuePins(node!) &&
                    node!["implementation"] is JsonValue && node["graph"] is null);
        }
        catch (Exception error) when (error is ArgumentException or InvalidOperationException) {
            return false;
        }
    }

    public static JsonObject Remove(JsonObject graph, string id)
    {
        int separator = id.LastIndexOf('/');
        string frame = separator < 0 ? "" : id[..separator];
        string local = id[(separator + 1)..];
        if ((separator >= 0 && frame.Length == 0) || !Options(graph, frame).Contains(local, StringComparer.Ordinal))
            throw new ArgumentException("Only one unconnected void action in a supported owned serial flow can be removed");
        var result = graph.DeepClone().AsObject();
        var selected = frame.Length == 0 ? result : BlueprintCellRegion.OwnedFrame(result, frame);
        var nodes = selected["nodes"]!.AsArray();
        nodes.Remove(nodes.Single(node => Value(node, "id") == local));
        var edges = selected["edges"]!.AsArray();
        var outgoing = edges.Single(edge => Value(edge, "from") == local)!;
        var successor = outgoing["to"]!.DeepClone();
        if (Value(selected, "entry") == local) selected["entry"] = successor;
        else edges.Single(edge => Value(edge, "to") == local)!["to"] = successor;
        edges.Remove(outgoing);
        if (frame.Length > 0) BlueprintCellRegion.OwnedFrame(result, frame);
        return result;
    }
}
