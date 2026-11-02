using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

namespace Confectory.Core;

// Public execution ports are nominal IDs, separate from ordinary value outputs
// and from a code node's private Result enum. Zero means no selected branch.
public static class BlueprintExecutionBranches
{
    public const string Metadata = "blueprintExecutionBranches";
    public static bool Has(Element function) => function.Values.ContainsKey(Metadata);
    public static bool SupportsSignature(FunctionSignature signature) => signature.Return == "void"
        && signature.Args.All(p => p.Mode is null or "out" or "ref");
    public static JsonArray Read(Element function)
    {
        if (!function.Values.TryGetValue(Metadata, out var value)) return new();
        if (function.Kind != "function" || function.Signature is not { } signature || !SupportsSignature(signature) || function.Parent is not null)
            throw new ArgumentException("Public execution branches require a direct synchronous void contract with existing value/ref/out parameters");
        if (value.Value.ValueKind != JsonValueKind.String || JsonNode.Parse(value.Value.GetString()!) is not JsonObject document || document.Count != 2 || document["schema"]?.GetValue<int>() != 1 || document["branches"] is not JsonArray branches || branches.Count > 31)
            throw new ArgumentException("Versioned public execution branch contract required");
        var ids = new HashSet<string>(StringComparer.Ordinal); var names = new HashSet<string>(StringComparer.Ordinal); var numbers = new HashSet<int>();
        foreach (var row in branches) {
            if (row is not JsonObject branch || branch.Count != 3 || branch.Any(p => p.Key is not ("id" or "name" or "value"))) throw new ArgumentException("Exact execution branch ID/name/value required");
            string id = branch["id"]?.GetValue<string>() ?? throw new ArgumentException("Execution branch ID required"), name = branch["name"]?.GetValue<string>() ?? throw new ArgumentException("Execution branch display name required"); int number = branch["value"]?.GetValue<int>() ?? throw new ArgumentException("Execution branch value required");
            if (id.Length > 128 || !Regex.IsMatch(id, @"\A[A-Za-z_][A-Za-z_0-9.-]*\z") || id == "none" || string.IsNullOrWhiteSpace(name) || name.Length > 128 || name.Any(char.IsControl) || !ids.Add(id) || !names.Add(name) || number <= 0 || !numbers.Add(number))
                throw new ArgumentException("Distinct stable execution branch IDs, display names and positive values required");
        }
        return branches.DeepClone().AsArray();
    }
    public static void Set(Element function, JsonArray branches)
    {
        var copy = new Element { Kind = function.Kind, Id = function.Id, Parent = function.Parent, Signature = function.Signature };
        copy.Values[Metadata] = new(JsonSerializer.SerializeToElement(new JsonObject { ["schema"] = 1, ["branches"] = branches.DeepClone() }.ToJsonString()), function.Id, new());
        _ = Read(copy);
        function.Values[Metadata] = copy.Values[Metadata];
    }
    public static JsonObject Enum(Element function)
    {
        var rows = Read(function);
        var members = new JsonArray(new JsonObject { ["id"] = "none", ["name"] = "None", ["value"] = 0 });
        foreach (var row in rows) members.Add(new JsonObject { ["id"] = row!["id"]!.DeepClone(), ["name"] = Member(row["id"]!.GetValue<string>()), ["value"] = row["value"]!.DeepClone() });
        return new() { ["primary"] = "none", ["members"] = members };
    }
    public static string Member(string id) => "Branch_" + JsonData.Digest(id)[..24];
    public static string Interface(string id) => "global::Confectory.Contracts." + Generation.Symbol(id) + ".IExecutionInvoke";
    public static string Result(string id) => "global::Confectory.Contracts." + Generation.Symbol(id) + ".ExecutionResult";
}
