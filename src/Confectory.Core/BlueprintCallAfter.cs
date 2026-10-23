using System.Text.Json.Nodes;

namespace Confectory.Core;

// A serial original-call/After adapter. Ordinary outputs retain their native
// signature; SourceContext is additional read-only post-call presentation.
public static class BlueprintCallAfter
{
    public static JsonObject Prepare(Element feature, string? expected = null, string? source = null, string helpers = "")
    {
        var snapshot = BlueprintOutputSnapshot.Prepare(feature, expected);
        string body = source ?? (feature.Signature!.Return == "void" ? "" : "return @" + ReturnLocal(feature.Signature, snapshot) + ";");
        if (body.Length > 65536 || helpers.Length > 65536) throw new ArgumentException("Post-call source budget");
        return new JsonObject { ["contractHash"] = snapshot["contractHash"]!.DeepClone(), ["source"] = body,
            ["helpers"] = helpers, ["snapshot"] = snapshot, ["parts"] = Parts(feature.Signature!, snapshot, body, helpers, "Function", "IOriginal", true),
            ["sourceWritten"] = false, ["executed"] = false };
    }

    static string ReturnLocal(FunctionSignature signature, JsonObject snapshot)
    {
        var used = signature.Args.Select(p => p.Name).Concat(new[] { snapshot["sourceParameter"]!.ToString(), snapshot["contextVariable"]!.ToString() }).ToHashSet(StringComparer.Ordinal);
        string name = "originalResult"; while (used.Contains(name)) name = "_" + name; return name;
    }

    static JsonArray Parts(FunctionSignature signature, JsonObject snapshot, string body, string helpers, string type, string originalInterface, bool preview)
    {
        string original = snapshot["sourceParameter"]!.ToString(), context = snapshot["contextVariable"]!.ToString(), returned = ReturnLocal(signature, snapshot);
        string Args(bool declarations, bool inputsOnly = false) => string.Join(", ", signature.Args.Where(p => !inputsOnly || !p.IsOut).Select(p => (p.Mode is "out" or "ref" ? p.Mode + " " : "") + (declarations ? p.Type + " " : "") + "@" + p.Name));
        string result = signature.Return == "void" ? "" : "@" + returned + ", ";
        string after = result + "@" + context + (signature.Args.Any(p => !p.IsOut) ? ", " + Args(false, true) : "");
        string declaration = (signature.Return == "void" ? "" : signature.Return + " @" + returned + ", ") + "SourceContext @" + context + (signature.Args.Any(p => !p.IsOut) ? ", " + Args(true, true) : "");
        string prefix = (preview ? snapshot["originalInterface"]!.ToString() : "") + (preview ? "public" : "private") + " static class " + type + "\n{\n" + snapshot["contextSource"] + "\npublic static " + signature.Return + " Execute(" + originalInterface + " @" + original + (signature.Args.Count > 0 ? ", " + Args(true) : "") + ")\n{\n" + snapshot["originalCall"] + (signature.Return == "void" ? "" : "return ") + "After(" + after + ");\n}\nprivate static " + signature.Return + " After(" + declaration + ")\n{\n";
        return new JsonArray(new JsonObject { ["text"] = prefix }, new JsonObject { ["id"] = "body", ["text"] = body }, new JsonObject { ["text"] = "\n}\n" }, new JsonObject { ["id"] = "helpers", ["text"] = helpers }, new JsonObject { ["text"] = "\n}\n" });
    }

    public static string Member(Element feature, JsonObject postCall, string type, string originalInterface, string marker)
    {
        var snapshot = BlueprintOutputSnapshot.Prepare(feature, postCall["contractHash"]!.GetValue<string>());
        string source = postCall["source"]!.GetValue<string>();
        string helpers = postCall.ContainsKey("helpers") ? postCall["helpers"]!.GetValue<string>() : "";
        if (source.Length > 65536 || helpers.Length > 65536) throw new ArgumentException("Post-call source budget");
        var parts = Parts(feature.Signature!, snapshot, source, helpers, type, originalInterface, false);
        return string.Concat(parts.Select(p => p!["id"]?.ToString() is "body" or "helpers" ? "#line 1 " + System.Text.Json.JsonSerializer.Serialize(marker + (p["id"]!.ToString() == "helpers" ? "/helpers" : "")) + "\n" + p["text"] + "\n#line default\n" : p["text"]!.ToString()));
    }
}
