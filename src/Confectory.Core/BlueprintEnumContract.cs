using System.Globalization;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

namespace Confectory.Core;

// Authoring data only. This produces a declaration, never an Execute method or dispatcher.
public static class BlueprintEnumContract
{
    static readonly HashSet<string> Keywords = new(("abstract as base bool break byte case catch char checked class const continue decimal default delegate do double else enum event explicit extern false finally fixed float for foreach goto if implicit in int interface internal is lock long namespace new null object operator out override params private protected public readonly ref return sbyte sealed short sizeof stackalloc static string struct switch this throw true try typeof uint ulong unchecked unsafe ushort using virtual void volatile while").Split(' '), StringComparer.Ordinal);
    static void Need(bool ok, string reason) { if (!ok) throw new ArgumentException(reason); }
    static string Text(JsonNode? node, string key) => node?[key]?.GetValue<string>() ?? throw new ArgumentException("Required enum contract field: " + key);
    static string Hash(string value) => Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(value))).ToLowerInvariant();
    static bool Identifier(string value)
    {
        string name = value.StartsWith('@') ? value[1..] : value;
        return value.Length <= 128 && name == name.Normalize(NormalizationForm.FormKC) && name is not ("Result" or "value__") &&
            Regex.IsMatch(name, @"\A[\p{L}\p{Nl}_][\p{L}\p{Nl}\p{Nd}\p{Mn}\p{Mc}\p{Pc}_]*\z", RegexOptions.CultureInvariant) && (value.StartsWith('@') || !Keywords.Contains(name));
    }
    public static JsonObject Validate(JsonObject document)
    {
        Need(Encoding.UTF8.GetByteCount(document.ToJsonString()) <= 32768, "Enum contract byte budget exceeded");
        Need(document.All(p => p.Key is "schema" or "kind" or "sourceId" or "definitionHash" or "sourceHash" or "primary" or "members"), "Only authoring contract fields are supported; runtime policies are not part of this proposal");
        Need(document["schema"]?.GetValue<int>() == 1 && Text(document,"kind") == "execution-enum-proposal", "Enum authoring proposal schema required");
        Need(Text(document,"sourceId").Length is > 0 and <= 2048, "Owned node source identity required");
        foreach (string key in new[] { "definitionHash", "sourceHash" }) Need(Regex.IsMatch(Text(document,key), @"\A[a-f0-9]{64}\z", RegexOptions.CultureInvariant), "Current source/definition hash required");
        string primary = Text(document,"primary");
        var rows = document["members"]?.AsArray() ?? throw new ArgumentException("Explicit enum members required");
        Need(rows.Count is > 0 and <= 32, "Keep the primary execution member and at most 32 members");
        var ids = new HashSet<string>(StringComparer.Ordinal); var names = new HashSet<string>(StringComparer.Ordinal); var values = new HashSet<int>();
        var normalized = new JsonArray();
        foreach (var row in rows)
        {
            Need(row is JsonObject member && member.All(p => p.Key is "id" or "name" or "value"), "Each member requires an explicit stable id, C# name and int32 value");
            string id = Text(row,"id"), name = Text(row,"name");
            Need(id.Length <= 128 && Regex.IsMatch(id, @"\A[A-Za-z_][A-Za-z_0-9.-]*\z", RegexOptions.CultureInvariant) && ids.Add(id), "Unique stable execution port id required");
            Need(Identifier(name) && names.Add(name.TrimStart('@')), "Duplicate, reserved or invalid C# enum member name");
            var value = row!["value"];
            Need(value?.GetValueKind() == System.Text.Json.JsonValueKind.Number && int.TryParse(value.ToJsonString(), NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture, out _), "Explicit int32 integer value required");
            int number = int.Parse(value!.ToJsonString(), NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture);
            Need(values.Add(number), "Execution enum values must be distinct");
            normalized.Add(new JsonObject { ["id"] = id, ["name"] = name, ["value"] = number });
        }
        Need(ids.Contains(primary), "The primary execution port cannot be removed");
        var result = document.DeepClone().AsObject(); result["members"] = normalized; return result;
    }

    public static JsonObject Preview(JsonObject document, JsonObject binding)
    {
        var contract = Validate(document);
        foreach (string key in new[] { "sourceId", "definitionHash", "sourceHash" }) Need(Text(contract,key) == Text(binding,key), "Enum source binding is stale; explicitly rebind retained authoring input to the current source");
        Need(Text(contract,"primary") == Text(binding,"primary"), "The primary execution port identity cannot change");
        var rows = contract["members"]!.AsArray();
        string source = "public enum Result : int\n{\n" + string.Join("\n", rows.Select(row => "    " + Text(row,"name") + " = " + row!["value"]!.ToJsonString() + ", // port: " + Text(row,"id"))) + "\n}\n";
        // Visual order belongs to the declaration, not to member identity/value allocation.
        var identity = new JsonObject { ["primary"] = Text(contract,"primary"), ["members"] = new JsonArray(rows.OrderBy(row => Text(row,"id"), StringComparer.Ordinal).Select(row => row!.DeepClone()).ToArray()) };
        return new JsonObject
        {
            ["state"] = "enum-contract-preview", ["contract"] = contract, ["contractHash"] = Hash(identity.ToJsonString()), ["declaration"] = source, ["declarationHash"] = Hash(source),
            ["sourceBinding"] = binding.DeepClone(), ["runtimePolicy"] = "sequential-switch-continuation", ["executionEnabled"] = false,
            ["sourceWritten"] = false, ["compiled"] = false, ["executed"] = false
        };
    }
}
