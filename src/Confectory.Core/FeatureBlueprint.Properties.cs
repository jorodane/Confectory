using System.Text.Json;
using System.Text.Json.Nodes;

namespace Confectory.Core;

public static partial class FeatureBlueprint
{
    public const string PropertyProfile = "sync-acyclic-property-v1", PropertyGenerator = "feature-blueprint-source-v10", PropertyReader = "Confectory.ObjectModel::Read";
    public static bool SupportsPrivateGraphs(string? profile) => profile is NestedProfile or PropertyProfile;
    public static bool IsObjectType(string type) => type is "object" or "object[]";
    public static bool HasObjectSignature(FunctionSignature signature) => IsObjectType(signature.Return) || signature.Args.Any(p => IsObjectType(p.Type));

    static JsonObject PropertyContract(JsonObject request, JsonObject node)
    {
        string owner = S(node, "propertyOwner"), name = S(node, "field");
        var descriptor = request["propertyContracts"]?[owner] as JsonObject ?? throw new Refusal("PROPERTY_OWNER_MISSING", owner);
        Need(descriptor["id"]?.ToString() == owner, "PROPERTY_OWNER", owner);
        var field = descriptor["fields"]?.AsArray().SingleOrDefault(f => f?["name"]?.ToString() == name) as JsonObject ?? throw new Refusal("PROPERTY_FIELD_MISSING", owner + "/" + name);
        Need(field["supported"]?.GetValue<bool>() == true, "PROPERTY_FIELD_UNSUPPORTED", owner + "/" + name);
        Need(S(node, "fieldContractHash") == S(field, "hash"), "PROPERTY_FIELD_STALE", owner + "/" + name);
        var result = field.DeepClone().AsObject();
        result["owner"] = owner; result["ownerContractHash"] = descriptor["hash"]!.DeepClone();
        result["readTiming"] = "execution-node";
        return result;
    }

    static string PropertyBody(Node node)
    {
        var field = node.Definition["property"]!;
        string Literal(string value) => JsonSerializer.Serialize(value);
        return "return (" + node.Signature.Return + ")" + ImportAlias(PropertyReader) + ".Invoke(target," + Literal(S(field, "owner")) + "," + Literal(S(field, "id")) + "," + Literal(S(field, "hash")) + ");";
    }
}
