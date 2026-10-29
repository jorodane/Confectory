using System.Text.Json.Nodes;

namespace Confectory.Core;

public static partial class FeatureBlueprint
{
    // A local graph action's icon belongs to that definition, never its callee.
    // Like displayName, it is presentation only and cannot stale a body contract.
    public static string? Icon(JsonObject node)
    {
        if (!node.ContainsKey("icon")) return null;
        Need(node["icon"] is JsonValue value && value.TryGetValue<string>(out _), "NODE_ICON", node["id"]!.ToString());
        string icon = node["icon"]!.GetValue<string>();
        Need(RasterIcon.IsImage(icon) || icon.Length is > 0 and <= 64 && icon == icon.Trim() &&
            System.Globalization.StringInfo.ParseCombiningCharacters(icon).Length == 1 &&
            !icon.Any(c => char.IsControl(c) || c is '<' or '>' or '&'), "NODE_ICON", node["id"]!.ToString());
        return icon;
    }

    // Authored presentation metadata. Never a callable identity, contract or body stamp.
    public static string DisplayName(JsonObject node)
    {
        if (!node.ContainsKey("displayName")) return node["id"]!.GetValue<string>();
        Need(node["displayName"] is JsonValue value && value.TryGetValue<string>(out _), "NODE_DISPLAY_NAME", node["id"]!.ToString());
        string name = node["displayName"]!.GetValue<string>();
        Need(name.Length is > 0 and <= 256 && name == name.Trim() && !name.Any(char.IsControl), "NODE_DISPLAY_NAME", node["id"]!.ToString());
        return name;
    }

    // Remove only node presentation at declared graph positions. Argument, local,
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
                node.Remove("icon");
                if (node["kind"]?.ToString() == "graph") Strip(node["graph"]!.AsObject());
            }
        }
        Strip(result);
        return result;
    }
}
