using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;

namespace Confectory.Core;

// A nominal readonly carrier for an explicitly bound live ObjectModel handle.
// The value struct and reference carrier have different CLR identities.
public static class InformationReferences
{
    public const string Profile = "information-reference-struct-v1";
    static readonly Regex ContractName = new(@"\AConfectory\.Reference\.E[0-9a-f]{24}\.E[0-9a-f]{24}\z", RegexOptions.CultureInvariant);
    public static string Type(string id) => "Confectory.Reference." + Generation.Symbol(PackPaths.Namespace(id)) + "." + Generation.Symbol(id);
    public static bool IsType(string type) => ContractName.IsMatch(InformationStructs.BaseType(type));
    internal static InformationStructs.Definition Generate(Element schema)
    {
        if (schema.Kind != "schema" || schema.Fields.Count > 256) throw new BuildError("INFORMATION_REFERENCE_SCHEMA", "A bounded information definition is required for a nominal reference", schema.Loc);
        var fields = schema.Fields.OrderBy(p => p.Key, StringComparer.Ordinal).Select(p => new { name = p.Key, p.Value.Kind, p.Value.Cardinality, p.Value.Type, p.Value.Origin }).ToArray();
        string hash = JsonData.Digest(new { profile = Profile, id = schema.Id, parent = schema.Parent, fields, bridge = JsonData.HashBytes(Encoding.UTF8.GetBytes(Kernel)) });
        string symbol = Generation.Symbol(schema.Id);
        var code = new StringBuilder("// Generated explicit information reference " + schema.Id + "; " + Profile + "; " + hash + "\n#nullable enable\nusing System;\n");
        code.AppendLine("namespace Confectory.Reference." + Generation.Symbol(PackPaths.Namespace(schema.Id)) + " {");
        code.AppendLine("    public readonly struct " + symbol + " {");
        code.AppendLine("        public readonly object Target; public readonly string Owner;");
        code.AppendLine("        public bool IsBound => Target is not null;");
        code.AppendLine("        private " + symbol + "(object target,string owner) { Target=target;Owner=owner; }");
        code.AppendLine("        public static " + symbol + " Bind(object target,string contract) { var same=Check(target,contract,out string owner);return new " + symbol + "(same,owner); }");
        code.AppendLine("        private static object Check(object target,string contract,out string owner) {");
        code.AppendLine(Kernel.Replace("/*SELECTED_INFORMATION_ID*/", JsonSerializer.Serialize(schema.Id, JsonData.Options), StringComparison.Ordinal));
        code.AppendLine("        }\n    }\n}");
        return new(schema.Id, Type(schema.Id), hash, [new(schema.Id + "/reference:Target", "Target", schema.Id, "object", "Target"), new(schema.Id + "/reference:Owner", "Owner", schema.Id, "string", "Owner")], code.ToString().Replace("\r\n", "\n", StringComparison.Ordinal), [], "reference", Profile);
    }
    // Same bounded metadata-only v1/v2 contract check as the published pack
    // bridge. Kept in generated contracts so binding selects no runtime provider.
    const string Kernel = """
if(contract is null||contract.Length>1048576)throw new ArgumentException("An explicit bounded information reference contract is required");
var expected=System.Text.Json.Nodes.JsonNode.Parse(contract)?.AsObject()??throw new ArgumentException("Information reference contract required");
if(expected["id"]?.ToString()!=/*SELECTED_INFORMATION_ID*/)throw new ArgumentException("Select the exact nominal information reference contract");
if(expected.Count!=8||expected["schema"]?.GetValue<int>()!=1||expected["profile"]?.ToString()!="information-object-reference-v1"||expected["kind"]?.ToString()!="schema"||expected["id"]is not System.Text.Json.Nodes.JsonValue idValue||!idValue.TryGetValue<string>(out string? id)||string.IsNullOrEmpty(id)||expected["lineage"]is not System.Text.Json.Nodes.JsonArray lineage||lineage.Count is <1 or >64||expected["fields"]is not System.Text.Json.Nodes.JsonArray fields||fields.Count>256||expected["dependencies"]is not System.Text.Json.Nodes.JsonArray dependencies||dependencies.Count>2048)throw new ArgumentException("Exact information reference profile and declaration required");
string Hash(System.Text.Json.Nodes.JsonNode value){
 using var stream=new System.IO.MemoryStream();using(var writer=new System.Text.Json.Utf8JsonWriter(stream,new(){Encoder=System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping})){
  void Canonical(System.Text.Json.JsonElement item){if(item.ValueKind==System.Text.Json.JsonValueKind.Object){writer.WriteStartObject();foreach(var row in System.Linq.Enumerable.OrderBy(item.EnumerateObject(),p=>p.Name,StringComparer.Ordinal)){writer.WritePropertyName(row.Name);Canonical(row.Value);}writer.WriteEndObject();}else if(item.ValueKind==System.Text.Json.JsonValueKind.Array){writer.WriteStartArray();foreach(var row in item.EnumerateArray())Canonical(row);writer.WriteEndArray();}else item.WriteTo(writer);}
  Canonical(System.Text.Json.JsonSerializer.SerializeToElement(value,new System.Text.Json.JsonSerializerOptions{Encoder=System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping}));
 }return Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(stream.ToArray())).ToLowerInvariant();
}
bool ExactHash(System.Text.Json.Nodes.JsonObject value){if(value["hash"]is not System.Text.Json.Nodes.JsonValue token||!token.TryGetValue<string>(out string? hash)||hash is null||!System.Text.RegularExpressions.Regex.IsMatch(hash,"\\A[a-f0-9]{64}\\z"))return false;var shape=value.DeepClone().AsObject();shape.Remove("hash");return Hash(shape)==hash;}
if(!ExactHash(expected))throw new ArgumentException("Information reference contract hash is invalid");
var requiredSchemas=new System.Collections.Generic.HashSet<string>(StringComparer.Ordinal);foreach(var row in lineage)if(row is not System.Text.Json.Nodes.JsonValue item||!item.TryGetValue<string>(out string? schema)||string.IsNullOrEmpty(schema)||!requiredSchemas.Add(schema))throw new ArgumentException("Distinct original information lineage required");if(!requiredSchemas.Contains(id))throw new ArgumentException("Information reference identity is missing from its lineage");
if(target is not object[] state||state.Length!=3||state[0]is not string format||format is not("Confectory.ObjectModel.Instance/v1" or "Confectory.ObjectModel.Instance/v2")||state[1]is not System.Text.Json.Nodes.JsonObject actual||state[2]is not System.Collections.Generic.Dictionary<string,object>||actual["schema"]?.GetValue<int>()!=1||actual["kind"]?.ToString()is not("object" or "concept")||actual["id"]is not System.Text.Json.Nodes.JsonValue actualId||!actualId.TryGetValue<string>(out string? actualOwner)||string.IsNullOrEmpty(actualOwner)||actual["lineage"]is not System.Text.Json.Nodes.JsonArray owners||owners.Count is <1 or >64||!System.Linq.Enumerable.Any(owners,row=>row?.ToString()==actualOwner)||actual["schemas"]is not System.Text.Json.Nodes.JsonArray schemas||schemas.Count>256||actual["fields"]is not System.Text.Json.Nodes.JsonArray declarations||declarations.Count>256)throw new ArgumentException("An actual caller-provided ObjectModel instance is required; IDs and value snapshots are not resolved");
if(!System.Linq.Enumerable.All(requiredSchemas,schema=>System.Linq.Enumerable.Any(schemas,row=>row?.ToString()==schema)))throw new InvalidOperationException("The actual instance does not apply the selected information definition");
var wanted=new System.Collections.Generic.Dictionary<string,System.Text.Json.Nodes.JsonObject>(StringComparer.Ordinal);foreach(var row in fields){if(row is not System.Text.Json.Nodes.JsonObject field||field["id"]is not System.Text.Json.Nodes.JsonValue fieldId||!fieldId.TryGetValue<string>(out string? name)||string.IsNullOrEmpty(name)||field["origin"]is not System.Text.Json.Nodes.JsonValue origin||!origin.TryGetValue<string>(out string? source)||source is null||!requiredSchemas.Contains(source)||name!=source+"/field:"+field["name"]?.ToString()||!ExactHash(field)||!wanted.TryAdd(name,field))throw new ArgumentException("Complete unique original information fields and hashes required");}
var found=new System.Collections.Generic.HashSet<string>(StringComparer.Ordinal);foreach(var row in declarations){if(row is not System.Text.Json.Nodes.JsonObject field||field["id"]is not System.Text.Json.Nodes.JsonValue fieldId||!fieldId.TryGetValue<string>(out string? name)||string.IsNullOrEmpty(name)||!found.Add(name))throw new InvalidOperationException("The actual instance field identity is invalid");if(wanted.TryGetValue(name,out var selected)){if(!System.Text.Json.Nodes.JsonNode.DeepEquals(selected,field))throw new InvalidOperationException("The actual information field contract changed; preserve the instance and select its exact contract");}else if(requiredSchemas.Contains(field["origin"]?.ToString()??""))throw new InvalidOperationException("The selected information definition has different fields; no automatic rebinding is performed");}
if(!System.Linq.Enumerable.All(wanted.Keys,found.Contains))throw new InvalidOperationException("The actual instance is missing an original information field");
// No value/getter access, initialization, snapshot, alias redirection or registry.
// The caller retains this same handle with ordinary CLR strong-reference lifetime.
owner=actualOwner;return target;
""";
}
