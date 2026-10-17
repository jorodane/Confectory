using System.Text.Json;
using System.Text.Json.Nodes;
using System.Globalization;
using System.Text.RegularExpressions;

namespace Confectory.Core;
public static partial class FeatureBlueprint
{
    public const string LocalsProfile="sync-acyclic-locals-v1",LocalsGenerator="feature-blueprint-source-v5";
    static Dictionary<string,JsonObject> ReadLocals(JsonObject graph,bool enabled,bool aliases=false)
    {
        var result=new Dictionary<string,JsonObject>(StringComparer.Ordinal);var rows=graph["locals"]?.AsArray()??new JsonArray();Need(enabled||rows.Count==0,"GRAPH_LOCALS_PROFILE","locals");Need(rows.Count<=64,"GRAPH_LOCALS_BUDGET","locals");
        foreach(var row in rows){
            var local=row!.AsObject();string id=S(local,"id"),name=S(local,"name"),type=S(local,"type");
            bool alias=local.ContainsKey("source");Need(!alias||aliases,"GRAPH_LOCAL_ALIAS_PROFILE",id);
            Need(local.Count==4&&local.All(p=>p.Key is "id" or "name" or "type" || p.Key==(alias?"source":"initial"))&&id.Length<=128&&Regex.IsMatch(id,@"\A[A-Za-z_][A-Za-z_0-9.-]*\z")&&!result.ContainsKey(id)&&name.Length<=256&&!string.IsNullOrWhiteSpace(name),"GRAPH_LOCAL_ID",id);
            new Parser("function Blueprint.Validation::Local ("+type+" value) -> void {}","<local-contract>").ParseElement();
            if(alias){var source=local["source"] as JsonObject;Need(source is not null&&(source.Count==1&&(source.ContainsKey("input")||source.ContainsKey("node"))||source.Count==2&&source.ContainsKey("node")&&source.ContainsKey("output")),"GRAPH_LOCAL_ALIAS_SOURCE",id);}
            else{Need(local["initial"] is JsonObject initial&&initial.Count==1&&initial.ContainsKey("constant"),"GRAPH_LOCAL_INITIALIZER",id);ConstantLiteral(local["initial"]!["constant"],type);}
            result.Add(id,local);
        }
        return result;
    }
    static JsonArray LocalDocument(Dictionary<string,JsonObject> locals)=>new(locals.OrderBy(p=>p.Key,StringComparer.Ordinal).Select(p=>(JsonNode)p.Value.DeepClone()).ToArray());
    static string ConstantLiteral(JsonNode? value, string type)
        {
            if (type.EndsWith("[]", StringComparison.Ordinal))
            {
                Need(value is JsonArray, "GRAPH_CONSTANT_TYPE", type);
                return "new " + type[..^2] + "[]{" + string.Join(",", value!.AsArray().Select(v => ConstantLiteral(v, type[..^2]))) + "}";
            }

            var datum = JsonSerializer.SerializeToElement(value);
            return type switch
            {
                "object" when datum.ValueKind==JsonValueKind.Null => "null!",
                "string" when datum.ValueKind == JsonValueKind.String => JsonSerializer.Serialize(datum.GetString()),
                "bool" when datum.ValueKind is JsonValueKind.True or JsonValueKind.False => datum.GetBoolean() ? "true" : "false",
                "int" when datum.ValueKind == JsonValueKind.Number && datum.TryGetInt32(out int n) => n.ToString(CultureInfo.InvariantCulture),
                "long" when datum.ValueKind == JsonValueKind.Number && datum.TryGetInt64(out long n) => n == long.MinValue ? "long.MinValue" : n.ToString(CultureInfo.InvariantCulture) + "L",
                "float" when datum.ValueKind == JsonValueKind.Number && datum.TryGetSingle(out float n) && float.IsFinite(n) => n.ToString("R", CultureInfo.InvariantCulture) + "F",
                "double" when datum.ValueKind == JsonValueKind.Number && datum.TryGetDouble(out double n) && double.IsFinite(n) => n.ToString("R", CultureInfo.InvariantCulture) + "D",
                _ => throw new Refusal("GRAPH_CONSTANT_TYPE", type)};
        }

}
