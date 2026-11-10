using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

namespace Confectory.Core;

public static class InformationEnums
{
    public const string Profile = "information-enum-int32-v1";
    public static string Member(string id) => "Member_" + Generation.Symbol(id);
    public static InformationStructs.Definition Generate(Element element)
    {
        var members = EnumDefinition.Members(element); var numbers = EnumNumbers.Read(element, members);
        var selected = members.Select(row => new { id = row!["id"]!.GetValue<string>(), value = numbers[row["id"]!.GetValue<string>()] }).OrderBy(row => row.id, StringComparer.Ordinal).ToArray();
        string hash = JsonData.Digest(new { profile = Profile, id = element.Id, underlying = "int", unselected = 0, members = selected });
        string symbol = Generation.Symbol(element.Id), type = InformationStructs.Type(element.Id);
        var code = new StringBuilder("// Generated information enum " + element.Id + "; " + Profile + "; " + hash + "\n#nullable disable\n");
        code.AppendLine("namespace Confectory.Information." + Generation.Symbol(PackPaths.Namespace(element.Id)) + " {");
        code.AppendLine("public enum " + symbol + " : int { Unselected = 0,");
        foreach (var member in selected) code.AppendLine(Member(member.id) + " = " + member.value + ",");
        code.AppendLine("}"); code.AppendLine("public static class " + symbol + "Ids {");
        code.AppendLine("public static string ToId(" + symbol + " value) => value switch {");
        code.AppendLine(symbol + ".Unselected => \"\",");
        foreach (var member in selected) code.AppendLine(symbol + "." + Member(member.id) + " => " + JsonSerializer.Serialize(member.id, JsonData.Options) + ",");
        code.AppendLine("_ => throw new global::System.ArgumentOutOfRangeException(nameof(value)) };");
        code.AppendLine("public static " + symbol + " FromId(string id) => id switch {");
        code.AppendLine("\"\" => " + symbol + ".Unselected,");
        foreach (var member in selected) code.AppendLine(JsonSerializer.Serialize(member.id, JsonData.Options) + " => " + symbol + "." + Member(member.id) + ",");
        code.AppendLine("_ => throw new global::System.ArgumentException(\"Unknown information enum member ID\", nameof(id)) };\n}\n}");
        var details = new JsonArray(members.Select(row => { var detail = row!.DeepClone().AsObject(); string id = detail["id"]!.GetValue<string>(); detail["value"] = numbers[id]; detail["clrMember"] = Member(id); return (JsonNode)detail; }).ToArray());
        return new(element.Id, type, hash, [], code.ToString().Replace("\r\n", "\n", StringComparison.Ordinal), [], "enum", Profile, details);
    }
}
