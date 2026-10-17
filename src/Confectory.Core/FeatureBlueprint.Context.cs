using System.Text.Json;
using System.Text.Json.Nodes;

namespace Confectory.Core;

public static partial class FeatureBlueprint
{
    // An explicit whole-body lift keeps the original implementation method boundary.
    // It does not lend this context to ordinary static nodes.
    public static JsonObject ImplementationContext(Element implementation) => new()
    {
        ["implementation"] = implementation.Id,
        ["feature"] = implementation.Function,
        ["signature"] = SignatureNode(implementation.Signature!),
        ["imports"] = new JsonObject(implementation.Imports.OrderBy(p => p.Key, StringComparer.Ordinal).Select(p =>
            new KeyValuePair<string, JsonNode?>(p.Key, new JsonObject
            {
                ["feature"] = p.Value.Id, ["scope"] = p.Value.Scope,
                ["signature"] = SignatureNode(p.Value.Signature)
            })))
    };

    static bool HasContext(Node node) => node.Definition["implementationContext"] is JsonObject;
    static string ContextMarker(Node node,string fallback) => node.Definition["sourceIdentity"]?.GetValue<string>() ?? fallback;
    static string ContextMember(Node node, string source, string marker) =>
        "public " + node.Signature.Return + " Invoke(" + string.Join(",", node.Signature.Args.Select(p => p.Declaration())) + ") {\n#line 1 " +
        JsonSerializer.Serialize(marker, JsonData.Options) + "\n" + source + "\n#line default\n}\n";
}
