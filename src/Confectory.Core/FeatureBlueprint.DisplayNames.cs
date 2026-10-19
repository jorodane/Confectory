using System.Text.Json.Nodes;

namespace Confectory.Core;

public static partial class FeatureBlueprint
{
    // Authored presentation metadata. Never a callable identity, contract or body stamp.
    public static string DisplayName(JsonObject node)
    {
        if (!node.ContainsKey("displayName")) return node["id"]!.GetValue<string>();
        Need(node["displayName"] is JsonValue value && value.TryGetValue<string>(out _), "NODE_DISPLAY_NAME", node["id"]!.ToString());
        string name = node["displayName"]!.GetValue<string>();
        Need(name.Length is > 0 and <= 256 && name == name.Trim() && !name.Any(char.IsControl), "NODE_DISPLAY_NAME", node["id"]!.ToString());
        return name;
    }

    // Remove only the node label at declared graph positions. Argument, local,
    // property and execution-enum names remain part of the execution contract.
    static JsonObject SemanticGraph(JsonObject graph)
    {
        var result = graph.DeepClone().AsObject();
        void Strip(JsonObject current)
        {
            foreach (var item in current["nodes"]!.AsArray())
            {
                var node = item!.AsObject();
                node.Remove("displayName");
                if (node["kind"]?.ToString() == "graph") Strip(node["graph"]!.AsObject());
            }
        }
        Strip(result);
        return result;
    }
}
