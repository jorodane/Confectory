using System.Text.Json;
using System.Text.Json.Nodes;

namespace Confectory.Core;

// The stored value remains an opaque member ID. CLR numbers are a separately
// versioned, persistent contract, including reservations for retired IDs.
public static class EnumNumbers
{
    public const string Profile = "nominal-members-native-v2";
    public const string Key = "editorEnumNumbers";
    public static SortedDictionary<string, int> Read(Element element, JsonArray members)
    {
        if (!element.Values.TryGetValue(EnumDefinition.ProfileKey, out var profile) || profile.Value.ValueKind != JsonValueKind.String || profile.Value.GetString() != Profile ||
            !element.Values.TryGetValue(Key, out var value) || value.Value.ValueKind != JsonValueKind.String)
            throw new BuildError("ENUM_CLR_MAPPING", "Explicitly save the information enum items to establish their stable C# numeric contract; existing IDs and source retained", element.Loc);
        try {
            string raw = value.Value.GetString()!;
            if (System.Text.Encoding.UTF8.GetByteCount(raw) > 1048576) throw new ArgumentException("Enum numeric mapping byte budget");
            using var document = JsonDocument.Parse(raw, new() { MaxDepth = 4 });
            if (document.RootElement.ValueKind != JsonValueKind.Object) throw new ArgumentException("Enum ID/number mapping required");
            var result = new SortedDictionary<string, int>(StringComparer.Ordinal); var used = new HashSet<int>();
            foreach (var row in document.RootElement.EnumerateObject()) {
                string id = row.Name;
                if (result.Count >= 16384 || id.Length is < 1 or > 128 || id != id.Trim() || id.Any(char.IsControl) ||
                    row.Value.ValueKind != JsonValueKind.Number || !row.Value.TryGetInt32(out int number) || number <= 0 || !used.Add(number) || !result.TryAdd(id, number))
                    throw new ArgumentException("Unique positive int32 reservations required; zero denotes the unselected ID");
            }
            if (members.Any(row => !result.ContainsKey(row!["id"]!.GetValue<string>()))) throw new ArgumentException("Every current member needs its original numeric reservation");
            return result;
        } catch (Exception error) when (error is JsonException or ArgumentException or InvalidOperationException) {
            throw new BuildError("ENUM_CLR_MAPPING", error.Message, element.Loc);
        }
    }
    internal static void Set(Element element, JsonArray before, JsonArray after)
    {
        bool active = element.Values.TryGetValue(EnumDefinition.ProfileKey, out var profile) && profile.Value.ValueKind == JsonValueKind.String && profile.Value.GetString() == Profile;
        var numbers = active ? Read(element, before) : new SortedDictionary<string, int>(StringComparer.Ordinal);
        int next = numbers.Count == 0 ? 0 : numbers.Values.Max();
        // First explicit conversion reserves all original IDs before additions
        // or removals. Subsequent rename/reorder never recalculate a number.
        foreach (var member in before.Concat(after)) {
            string id = member!["id"]!.GetValue<string>(); if (numbers.ContainsKey(id)) continue;
            if (numbers.Count >= 16384 || next == int.MaxValue) throw new BuildError("ENUM_CLR_BUDGET", "Enum numeric reservations exhausted; no existing value was reassigned", element.Loc);
            numbers.Add(id, checked(++next));
        }
        element.Values[Key] = new(JsonSerializer.SerializeToElement(JsonSerializer.Serialize(numbers, JsonData.Options)), element.Id, element.Loc);
        element.Values[EnumDefinition.ProfileKey] = new(JsonSerializer.SerializeToElement(Profile), element.Id, element.Loc);
    }
}
