using System.Text.Json.Nodes;

namespace Confectory.Core;

public static partial class FeatureBlueprint
{
    public const string ImplicitProfile = "sync-acyclic-implicit-v1", ImplicitGenerator = "feature-blueprint-source-v3";

    private static (JsonArray Ends, JsonArray Warnings) DescribeImplicitTerminations(
        string entry, Element feature, Dictionary<string, Node> nodes,
        Dictionary<(string, string), string> edges, List<string> order,
        Dictionary<string, string[]> predecessors, JsonObject exits)
    {
        var must = new Dictionary<string, bool>(StringComparer.Ordinal);
        var may = new Dictionary<string, bool>(StringComparer.Ordinal);
        foreach (string id in order)
        {
            var before = predecessors[id];
            must[id] = nodes[id].Kind == "export" || before.Length > 0 && before.All(p => must[p]);
            may[id] = nodes[id].Kind == "export" || before.Any(p => may[p]);
        }
        JsonArray Witness(string id)
        {
            var path = new JsonArray();
            var before = predecessors[id].Where(p => !must[p]).Order(StringComparer.Ordinal).ToArray();
            if (before.Length > 0)
            {
                string previous = before[0];
                foreach (var step in Witness(previous)) path.Add(step?.DeepClone());
                string port = edges.Where(e => e.Key.Item1 == previous && e.Value == id).OrderBy(e => e.Key.Item2, StringComparer.Ordinal).First().Key.Item2;
                path.Add(new JsonObject { ["from"] = previous, ["port"] = port, ["to"] = id });
            }
            else path.Add(new JsonObject { ["from"] = null, ["port"] = "entry", ["to"] = id });
            return path;
        }
        string type = feature.Signature!.Return;
        string defaultValue = type == "bool" ? "false" : type is "string" or "object" || type.EndsWith("[]", StringComparison.Ordinal) ? "null" : "0";
        var ends = new JsonArray(); var warnings = new JsonArray();
        void End(string? from, string port, string target)
        {
            bool direct = target.StartsWith("exit:", StringComparison.Ordinal) && exits[target[5..]] is not null;
            bool assigned = type == "void" || direct || from is not null && must[from];
            bool assignedOnSomePaths = direct || from is not null && may[from];
            var missing = new JsonArray();
            if (!assigned) missing.Add(new JsonObject { ["name"] = "return", ["type"] = type, ["assignedOnSomePaths"] = assignedOnSomePaths, ["defaultValue"] = defaultValue });
            var row = new JsonObject { ["from"] = from, ["port"] = port, ["target"] = target, ["missingOutputs"] = missing, ["definitelyAssigned"] = assigned, ["assignedOnSomePaths"] = assignedOnSomePaths };
            ends.Add(row);
            if (!assigned)
            {
                var witness = from is null ? new JsonArray() : Witness(from);
                witness.Add(new JsonObject { ["from"] = from, ["port"] = port, ["to"] = target });
                warnings.Add(new JsonObject { ["severity"] = "warning", ["code"] = "GRAPH_RETURN_UNASSIGNED", ["subject"] = (from ?? "$entry") + "/" + port, ["termination"] = row.DeepClone(), ["missingOutputs"] = missing.DeepClone(), ["exampleUnassignedPath"] = witness, ["runtimePolicy"] = "csharp-type-default" });
            }
        }
        if (entry.StartsWith("end:", StringComparison.Ordinal) || entry.StartsWith("exit:", StringComparison.Ordinal)) End(null, "entry", entry);
        foreach (var edge in edges.Where(e => must.ContainsKey(e.Key.Item1) && (e.Value.StartsWith("end:", StringComparison.Ordinal) || e.Value.StartsWith("exit:", StringComparison.Ordinal))).OrderBy(e => e.Key.Item1, StringComparer.Ordinal).ThenBy(e => e.Key.Item2, StringComparer.Ordinal)) End(edge.Key.Item1, edge.Key.Item2, edge.Value);
        return (ends, warnings);
    }
}
