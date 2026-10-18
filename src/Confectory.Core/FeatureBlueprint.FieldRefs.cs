using System.Text.Json;
using System.Text.Json.Nodes;
namespace Confectory.Core;
public static partial class FeatureBlueprint
{
    public const string PropertyRefProfile="sync-acyclic-property-ref-v1",PropertyRefGenerator="feature-blueprint-source-v14",PropertyRefAccessor="Confectory.ObjectModel::RefCell";
    public static bool SupportsPropertySets(string? profile)=>profile is PropertySetProfile or PropertyRefProfile;
    public static bool SafeFieldRef(JsonNode field)=>field["kind"]?.ToString()=="general"&&field["cardinality"]?.ToString()=="single"&&field["type"]?.ToString() is "bool" or "int" or "long";
    static string FieldCellType(Node node)=>"global::System.Runtime.CompilerServices.StrongBox<"+node.Signature.Return+">";
    static string FieldCellAccess(Node node,string target,string accessor)
    {
        var field=node.Definition["property"]!;
        return "("+FieldCellType(node)+")"+accessor+".Invoke("+target+","+JsonSerializer.Serialize(S(field,"owner"))+","+JsonSerializer.Serialize(S(field,"id"))+","+JsonSerializer.Serialize(S(field,"hash"))+") ?? throw new global::System.InvalidOperationException(\"Field ref accessor must return initialized compatible typed storage\")";
    }
}
