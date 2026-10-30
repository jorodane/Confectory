using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

namespace Confectory.Core;

// A private graph has no global declaration, receiver or source-file authority.
// All leaf paths remain relative to the physical root graph's directory.
public static class BlueprintTree
{
    public sealed record Entry(string Key, JsonObject Node, string Pointer);
    public static IEnumerable<Entry> Nodes(JsonObject root)
    {
        int count = 0;
        IEnumerable<Entry> Walk(JsonObject graph, string path, string pointer, int depth)
        {
            if (depth > 8) throw new ArgumentException("Private graph depth budget exceeded");
            var ids = new HashSet<string>(StringComparer.Ordinal);
            foreach (var value in graph["nodes"]!.AsArray())
            {
                var node = value!.AsObject();
                string id = node["id"]!.GetValue<string>();
                if (++count > (FeatureBlueprint.SupportsPrivateGraphs(root["profile"]?.ToString()) ? 256 : int.MaxValue) || id.Length > 128 || !Regex.IsMatch(id, @"\A[A-Za-z_][A-Za-z_0-9.-]*\z") || !ids.Add(id))
                    throw new ArgumentException("Bounded unique private node identity required");
                string key = path.Length == 0 ? id : path + "/" + id;
                if(key.Length>768)throw new ArgumentException("Qualified private node path budget exceeded");
                string at = pointer + "/nodes/" + graph["nodes"]!.AsArray().IndexOf(node);
                yield return new(key, node, at);
                if (node["kind"]?.ToString() == "graph")
                {
                    if (!FeatureBlueprint.SupportsPrivateGraphs(root["profile"]?.ToString()) || node["graph"] is not JsonObject child || (child["schema"]?.GetValue<int>() != 1 && !(child["schema"]?.GetValue<int>()==2 && child["executionExitMode"]?.GetValue<bool>()==true && node["control"]?.ToString()=="switch" && node["executionSource"] is not null)) || child.ContainsKey("feature") || child.ContainsKey("contractHash") || !FeatureBlueprint.SupportsPrivateGraphs(child["profile"]?.ToString()))
                        throw new ArgumentException("Private graph contract is owned by its parent node signature");
                    foreach (var nested in Walk(child, key, at + "/graph", depth + 1)) yield return nested;
                }
            }
        }
        return Walk(root, "", "", 0);
    }
    public static string SourceId(string bodyId, string key) => bodyId + "/node:" + key.Replace("/", "/node:", StringComparison.Ordinal);

    public static JsonObject Select(JsonObject root, string path)
    {
        var current = root;
        if (path.Length == 0) return current;
        var segments = path.Split('/');
        if (segments.Length > 8) throw new ArgumentException("Private graph depth budget exceeded");
        foreach (string segment in segments)
        {
            var node = current["nodes"]!.AsArray().Single(n => n!["id"]!.ToString() == segment)!;
            if (node["kind"]?.ToString() != "graph") throw new ArgumentException("Owned private graph required");
            current = node["graph"]!.AsObject();
        }
        return current;
    }

    public static JsonObject SelectDescription(JsonObject root, string path)
    {
        var current = root;
        if (path.Length == 0) return current;
        foreach (string segment in path.Split('/')) current = current["children"]![segment]!.AsObject();
        var result = current.DeepClone().AsObject();
        foreach (var node in result["nodes"]!.AsArray()) node!["id"] = node["id"]!.ToString()[(path.Length + 1)..];
        result["contractVersions"] = root["contractVersions"]!.DeepClone();
        return result;
    }
}
