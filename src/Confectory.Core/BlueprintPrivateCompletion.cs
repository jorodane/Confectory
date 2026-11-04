using System.Text.Json.Nodes;

namespace Confectory.Core;

// A private frame may return native data and a local execution result together.
// This owns no public declaration and never rewrites its original leaf source.
public static class BlueprintPrivateCompletion
{
    public static bool OwnsResults(JsonObject node) => node["kind"]?.ToString()=="graph"&&node["control"]?.ToString()=="switch"&&node["executionSource"] is null&&node[BlueprintCompletionBranch.Metadata] is not null;
    public static void Attach(JsonObject node)
    {
        if(node["kind"]?.ToString()!="graph"||node["control"]?.ToString()!="next"||node["executionEnum"] is not null)throw new ArgumentException("Original private next boundary required");
        node["control"]="switch";node["executionEnum"]=new JsonObject{["primary"]="none",["members"]=new JsonArray(new JsonObject{["id"]="none",["name"]="None",["value"]=0})};
    }
    public static JsonArray CompletionIds(JsonObject node)
    {
        var ids=new HashSet<string>(StringComparer.Ordinal);
        void Read(JsonObject current){if(BlueprintCompletionBranch.Read(current) is JsonObject marker)ids.Add(marker["id"]!.ToString());if(current["kind"]?.ToString()=="graph"&&current["executionSource"] is JsonValue source){var child=current["graph"]!["nodes"]!.AsArray().Single(n=>n!["id"]?.ToString()==source.ToString())!.AsObject();Read(child);}}
        Read(node);return new JsonArray(ids.Order(StringComparer.Ordinal).Select(x=>JsonValue.Create(x)).ToArray());
    }
}
