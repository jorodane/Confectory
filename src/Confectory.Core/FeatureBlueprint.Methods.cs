using System.Text.Json;
using System.Text.Json.Nodes;

namespace Confectory.Core;

public static partial class FeatureBlueprint
{
    public const string MethodsProfile = "sync-acyclic-methods-v1", MethodsGenerator = "feature-blueprint-source-v11";
    public static bool SupportsProperties(string? profile) => profile is PropertyProfile or MethodsProfile;
    static string Helpers(JsonNode? record, string profile, Node node)
    {
        string helpers = record?["helpers"]?.GetValue<string>() ?? "";
        Need(helpers.Length == 0 || profile == MethodsProfile, "NODE_HELPERS_PROFILE", node.Id);
        Need(helpers.Length == 0 || !HasContext(node), "NODE_HELPERS_CONTEXT", node.Id);
        return helpers.Replace("\r\n", "\n");
    }
    static string NodeCodeHash(Node node, string body, string helpers) => helpers.Length == 0
        ? Hash(HasContext(node) ? body : body.Replace("\r\n", "\n"))
        : Hash(CanonicalText(new JsonObject { ["source"] = body.Replace("\r\n", "\n"), ["helpers"] = helpers }));
    static string MethodClass(JsonObject request, string id) => "__fg_methods_" + Hash((request["sourceOwner"]?.ToString() ?? S(request["graph"], "feature")) + "/" + RecordKey(request, id))[..32];
    static string MethodsMember(string type, Node node, string declarations, string source, string helpers, string marker) =>
        "private static class " + type + " {\npublic static " + node.Signature.Return + " Execute(" + declarations + ") {\n#line 1 " + JsonSerializer.Serialize(marker) + "\n" + source +
        "\n#line default\n}\n#line 1 " + JsonSerializer.Serialize(marker + "/helpers") + "\n" + helpers + "\n#line default\n}\n";
}
