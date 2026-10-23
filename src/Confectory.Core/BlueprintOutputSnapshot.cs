using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

namespace Confectory.Core;

// v508's output eye describes the post-call C# context, never project/share authority.
// Pure contract/source preparation. A consumer must bind the exact receipt and call
// the original once before constructing this context; this helper invokes nothing.
public static class BlueprintOutputSnapshot
{
    public const string Metadata = "blueprintPublishedOutputs";

    public static string[] Read(Element feature)
    {
        if (feature.Kind != "function" || feature.Signature is null)
            throw new ArgumentException("Function output contract required");
        if (!feature.Values.TryGetValue(Metadata, out var stored)) return [];
        if (stored.Value.ValueKind != JsonValueKind.String)
            throw new ArgumentException("Explicit published-output metadata required");
        var rows = JsonNode.Parse(stored.Value.GetString()!) as JsonArray
            ?? throw new ArgumentException("Published-output list required");
        if (rows.Count > 65) throw new ArgumentException("Published-output budget");
        var names = rows.Select(row => row?.GetValue<string>()
            ?? throw new ArgumentException("Named published output required")).ToArray();
        var outputs = FeatureBlueprint.FeatureOutputs(feature.Signature).Select(p => p.Name).ToHashSet(StringComparer.Ordinal);
        if (names.Distinct(StringComparer.Ordinal).Count() != names.Length || names.Any(name => !outputs.Contains(name)))
            throw new ArgumentException("Publish each selected declared output at most once");
        return names;
    }

    public static void Set(Element feature, JsonArray selected)
    {
        // Validate a candidate before touching the declaration being prepared.
        var copy = new Element { Kind = feature.Kind, Id = feature.Id, Signature = feature.Signature };
        copy.Values[Metadata] = new(JsonSerializer.SerializeToElement(selected.ToJsonString()), feature.Id, new());
        _ = Read(copy);
        if (selected.Count == 0) feature.Values.Remove(Metadata);
        else feature.Values[Metadata] = copy.Values[Metadata];
    }

    public static JsonObject Prepare(Element feature, string? expected = null)
    {
        var names = Read(feature);
        var outputs = FeatureBlueprint.FeatureOutputs(feature.Signature!).ToDictionary(p => p.Name, StringComparer.Ordinal);
        var members = new Dictionary<string, string>(StringComparer.Ordinal);
        var used = new HashSet<string>(StringComparer.Ordinal) { "SourceContext" };
        foreach (string name in names) {
            string member = name; int suffix = 2;
            while (!used.Add(member)) member = name + "_" + suffix++;
            members.Add(name, member);
        }
        // Null is preserved under the native ABI; null-forgiving marks only that deliberate bridge case.
        string backing = "snapshot";
        while (names.Select((_, i) => backing + i).Any(used.Contains)) backing = "_" + backing;
        var fields = new JsonArray(names.Select(name => (JsonNode)new JsonObject { ["name"] = name, ["member"] = members[name], ["type"] = outputs[name].Type }).ToArray());
        string hash = Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(new JsonObject {
            ["feature"] = feature.Id, ["signature"] = FeatureBlueprint.SignatureDocument(feature.Signature!), ["published"] = fields.DeepClone()
        }.ToJsonString()))).ToLowerInvariant();
        if (expected is not null && expected != hash)
            throw new InvalidOperationException("The original output contract changed; review a new context before editing its consumer");
        var source = new StringBuilder("public sealed class SourceContext\n{\n");
        for (int i = 0; i < names.Length; i++) {
            var output = outputs[names[i]]; string name = "@" + members[output.Name], storage = backing + i;
            if (output.Type.EndsWith("[]", StringComparison.Ordinal))
                source.AppendLine("    private readonly " + output.Type + " " + storage + ";\n    public " + output.Type + " " + name + " { get { return " + storage + " == null ? null! : (" + output.Type + ")" + storage + ".Clone(); } }");
            else source.AppendLine("    public " + output.Type + " " + name + " { get; }");
        }
        source.AppendLine("    public SourceContext(" + string.Join(", ", names.Select((name, i) => outputs[name].Type + " value" + i)) + ")\n    {");
        for (int i = 0; i < names.Length; i++) {
            var output = outputs[names[i]];
            source.AppendLine("        " + (output.Type.EndsWith("[]", StringComparison.Ordinal)
                ? backing + i + " = value" + i + " == null ? null! : (" + output.Type + ")value" + i + ".Clone();"
                : "this.@" + members[output.Name] + " = value" + i + ";"));
        }
        source.AppendLine("    }\n}");
        // Fixed original-call prelude for the existing C# wrapper layout. Its
        // editable After body is separate; no user text can replace this call.
        var locals = new HashSet<string>(feature.Signature!.Args.Select(p => p.Name), StringComparer.Ordinal);
        string Local(string preferred) { while (!locals.Add(preferred)) preferred = "_" + preferred; return preferred; }
        string original = Local("original"), context = Local("context"), returned = Local("originalResult");
        string invocation = "@" + original + ".Invoke(" + string.Join(", ", feature.Signature.Args.Select(p => (p.Mode is "out" or "ref" ? p.Mode + " " : "") + "@" + p.Name)) + ");";
        string call = (feature.Signature.Return == "void" ? "" : feature.Signature.Return + " @" + returned + " = ") + invocation + "\nvar @" + context + " = new SourceContext(" + string.Join(", ", names.Select(name => "@" + (name == "return" ? returned : name))) + ");\n";
        return new JsonObject { ["feature"] = feature.Id, ["contractHash"] = hash, ["fields"] = fields,
            ["contextSource"] = source.ToString(), ["snapshot"] = "read-only-properties; shallow-array-copy-on-return-and-read",
            ["originalInterface"] = "public interface IOriginal { " + feature.Signature.Return + " Invoke(" + string.Join(", ", feature.Signature.Args.Select(p => (p.Mode is "out" or "ref" ? p.Mode + " " : "") + p.Type + " @" + p.Name)) + "); }\n",
            ["originalCall"] = call, ["sourceParameter"] = original, ["contextVariable"] = context, ["returnVariable"] = returned,
            ["sourceWritten"] = false, ["executed"] = false };
    }
}
