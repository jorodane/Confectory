using System.Globalization;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

namespace Confectory.Core;

// Information choices have opaque stable member identities, not execution ports
// or presentation ordinals. A separate versioned map supplies stable CLR numbers.
public static class EnumDefinition
{
    public const string ProfileKey = "editorEnumProfile";
    public const string Profile = "nominal-members-v1";
    public const string MembersKey = "editorEnumValues";

    public static JsonArray Members(Element element)
    {
        if (element.Kind != "enum") throw new BuildError("ENUM_KIND", "Information enum definition required", element.Loc);
        if (element.Parent is not null || element.Signature is not null || element.Modules.Count != 0 ||
            element.Includes.Count != 0 || element.Requires.Count != 0 || element.Defaults.Count != 0 ||
            element.Provides.Count != 0 || element.Uses.Count != 0 || element.Contains.Count != 0 ||
            element.Fields.Count != 0 || element.Data.Count != 0 || element.Imports.Count != 0 || element.Bodies.Count != 0)
            throw new BuildError("ENUM_BOUNDARY", "Information choices preserve their own nominal definition; no execution or inheritance contract", element.Loc);
        bool profile = element.Values.TryGetValue(ProfileKey, out var marker);
        bool members = element.Values.TryGetValue(MembersKey, out var value);
        if (!profile && !members) { if (element.Values.ContainsKey(EnumNumbers.Key)) throw new BuildError("ENUM_CLR_MAPPING", "Numeric reservations require their explicit profile", element.Loc); return new(); }
        if (!profile || !members || marker!.Value.ValueKind != JsonValueKind.String || marker.Value.GetString() is not (Profile or EnumNumbers.Profile) || value!.Value.ValueKind != JsonValueKind.String)
            throw new BuildError("ENUM_PROFILE", "Unknown information enum profile retained; explicit migration required", element.Loc);
        try { var result = Validate(value.Value.GetString()!); if (marker.Value.GetString() == EnumNumbers.Profile) EnumNumbers.Read(element, result); else if (element.Values.ContainsKey(EnumNumbers.Key)) throw new BuildError("ENUM_CLR_MAPPING", "Numeric reservations require their explicit versioned profile", element.Loc); return result; }
        catch (Exception error) when (error is JsonException or ArgumentException or InvalidOperationException)
        { throw new BuildError("ENUM_MEMBERS", error.Message, value.Loc); }
    }

    public static JsonArray Validate(string text)
    {
        if (Encoding.UTF8.GetByteCount(text) > 1048576) throw new ArgumentException("Information enum member byte budget");
        var rows = JsonNode.Parse(text, documentOptions: new() { MaxDepth = 8 }) as JsonArray ?? throw new ArgumentException("Explicit information enum member list required");
        if (rows.Count > 256) throw new ArgumentException("Information enum member count budget");
        var ids = new HashSet<string>(StringComparer.Ordinal); var names = new HashSet<string>(StringComparer.Ordinal);
        foreach (var row in rows)
        {
            if (row is not JsonObject item || item.Count is < 2 or > 3 || item.Any(p => p.Key is not ("id" or "name" or "icon")))
                throw new ArgumentException("Exact information member identity, name and optional icon required");
            string id = item["id"]?.GetValue<string>() ?? throw new ArgumentException("Member identity required"), name = item["name"]?.GetValue<string>() ?? throw new ArgumentException("Member name required");
            if (id.Length is < 1 or > 128 || id != id.Trim() || id.Any(char.IsControl) || !ids.Add(id))
                throw new ArgumentException("Unique stable information member identity required");
            if (name.Length is < 1 or > 60 || name != name.Trim() || name.Any(char.IsControl) || !names.Add(name))
                throw new ArgumentException("Nonempty distinct information member display names required");
            if (item.ContainsKey("icon"))
            {
                string icon = item["icon"]?.GetValue<string>() ?? throw new ArgumentException("Member icon string required");
                if (icon.Length != 0 && !RasterIcon.IsImage(icon) &&
                    (icon != icon.Trim() || icon.Length > 64 || StringInfo.ParseCombiningCharacters(icon).Length != 1 || icon.Any(c => char.IsControl(c) || c is '<' or '>' or '&')))
                    throw new ArgumentException("One information member symbol or normalized local image required");
            }
        }
        return rows;
    }

    public static void SetMembers(Element element, string text)
    {
        if (element.Kind != "enum") throw new ArgumentException("Information enum definition required");
        var after = Validate(text); var before = Members(element);
        var candidate = JsonData.Clone(element);
        EnumNumbers.Set(candidate, before, after);
        candidate.Values[MembersKey] = new(JsonSerializer.SerializeToElement(text), element.Id, new());
        Members(candidate);
        element.Values = candidate.Values;
    }
}
