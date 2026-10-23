using System.Text.Json;
using System.Text.Json.Nodes;

namespace Confectory.Core;

public static partial class FeatureBlueprint
{
    public const string PropertyProfile = "sync-acyclic-property-v1", PropertyGenerator = "feature-blueprint-source-v10", PropertyReader = "Confectory.ObjectModel::Read";
    public const string PropertySetProfile = "sync-acyclic-property-set-v1", PropertySetGenerator = "feature-blueprint-source-v13", PropertySetter = "Confectory.ObjectModel::Set";
    public static bool SupportsPrivateGraphs(string? profile) => profile is NestedProfile or PropertyProfile or MethodsProfile or SwitchProfile or PropertySetProfile or PropertyRefProfile;
    public static bool IsPropertyNode(string? kind) => kind is "property" or "property-set" or "property-ref";
    public static bool SupportsSwitches(string? profile) => profile is SwitchProfile or PropertySetProfile or PropertyRefProfile;
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
        if(S(node,"kind")=="property-ref")Need(SafeFieldRef(field),"PROPERTY_REF_FIELD_UNSUPPORTED",owner+"/"+name);
        var result = field.DeepClone().AsObject();
        result["owner"] = owner; result["ownerContractHash"] = descriptor["hash"]!.DeepClone();
        result[S(node,"kind")=="property-ref"?"referenceTiming":S(node,"kind")=="property-set"?"writeTiming":"readTiming"] = "execution-node";
        return result;
    }

    static string PropertyBody(Node node)
    {
        var field = node.Definition["property"]!;
        string Literal(string value) => JsonSerializer.Serialize(value);
        string contract = "target," + Literal(S(field, "owner")) + "," + Literal(S(field, "id")) + "," + Literal(S(field, "hash"));
        return node.Kind=="property-set" ? ImportAlias(PropertySetter)+".Invoke("+contract+",value);" : "return (" + node.Signature.Return + ")" + ImportAlias(PropertyReader) + ".Invoke("+contract+");";
    }

    // Validate even disconnected Set/ref input contracts during preview. Execution
    // dominance is checked separately by the normal graph binding pass.
    static void CheckPropertyInputBindings(Node node,FunctionSignature feature,Dictionary<string,Node> nodes,Dictionary<string,JsonObject> locals)
    {
        Need(node.Arguments.Count==node.Signature.Args.Count&&node.Signature.Args.All(p=>node.Arguments.ContainsKey(p.Name)),"GRAPH_ARGUMENTS",node.Id);
        foreach(var parameter in node.Signature.Args){
            string subject=node.Id+"/"+parameter.Name,type=parameter.Type;
            var binding=node.Arguments[parameter.Name] as JsonObject??throw new Refusal("GRAPH_VALUE",subject);
            Need(binding.Count==1||binding.Count==2&&binding.ContainsKey("node")&&binding.ContainsKey("output"),"GRAPH_VALUE",subject);
            if(binding.ContainsKey("input"))Need(feature.Args.Any(p=>p.Name==S(binding,"input")&&!p.IsOut&&p.Type==type),"GRAPH_INPUT_TYPE",subject);
            else if(binding.ContainsKey("node"))Need(nodes.TryGetValue(S(binding,"node"),out var source)&&NodeOutputs(source).Any(p=>p.Name==(binding["output"]?.ToString()??"return")&&p.Type==type),"GRAPH_VALUE_UNAVAILABLE",subject);
            else if(binding.ContainsKey("local"))Need(locals.TryGetValue(S(binding,"local"),out var local)&&S(local,"type")==type,"GRAPH_LOCAL_TYPE",subject);
            else if(binding.ContainsKey("constant"))_ = ConstantLiteral(binding["constant"],type);
            else throw new Refusal("GRAPH_VALUE",subject);
        }
    }
}
