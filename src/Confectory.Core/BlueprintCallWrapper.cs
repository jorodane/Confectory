using System.Text.Json.Nodes;

namespace Confectory.Core;

// First original v508 execution-enum wrapper adapter. The public function ABI has
// no exported execution outcome; native void completion maps ONLY to NoBranch.
// Native data returns use a separate explicit output storage mapping, never a cast.
public static class BlueprintCallWrapper
{
    public const string NativeReturnMapping = "native-return-out-v1";
    public static JsonObject Enum(JsonObject value)
    {
        if (value.Any(p => p.Key is not ("primary" or "members"))) throw new ArgumentException("Execution contract fields required");
        var checkedValue = BlueprintEnumContract.Validate(new JsonObject { ["schema"] = 1, ["kind"] = "execution-enum-proposal", ["sourceId"] = "wrapper-enum", ["definitionHash"] = new string('0', 64), ["sourceHash"] = new string('0', 64), ["primary"] = value["primary"]?.DeepClone(), ["members"] = value["members"]?.DeepClone() });
        return new JsonObject { ["primary"] = checkedValue["primary"]!.DeepClone(), ["members"] = checkedValue["members"]!.DeepClone() };
    }
    public static JsonObject Prepare(Element feature, JsonObject executionEnum, string? expected = null, string? source = null, string helpers = "", string? returnMapping = null)
    {
        if (feature.Signature is null || (feature.Signature.Return == "void" ? returnMapping is not null : returnMapping != NativeReturnMapping)) throw new ArgumentException("Exact native-return output mapping required; execution outcome is separate");
        var contract = Enum(executionEnum); var snapshot = BlueprintOutputSnapshot.Prepare(feature, expected);
        string primary = contract["primary"]!.ToString(), name = contract["members"]!.AsArray().Single(m => m!["id"]!.ToString() == primary)!["name"]!.ToString();
        string body = source ?? "return Result." + name + ";";
        if (body.Length > 65536 || helpers.Length > 65536) throw new ArgumentException("Wrapper source budget");
        return new JsonObject { ["mode"] = "execution-enum", ["contractHash"] = snapshot["contractHash"]!.DeepClone(), ["executionEnum"] = contract, ["source"] = body, ["helpers"] = helpers, ["snapshot"] = snapshot, ["originalOutcome"] = feature.Signature.Return == "void" ? "native-void-completion-only" : "native-data-completion-only", ["returnMapping"] = returnMapping, ["outputBindings"] = new JsonArray(FeatureBlueprint.FeatureOutputs(feature.Signature).Select(p => (JsonNode)new JsonObject { ["port"] = p.Name, ["type"] = p.Type, ["storage"] = p.Name == "return" ? "native-return" : "native-out" }).ToArray()), ["parts"] = Parts(feature.Signature, snapshot, contract, body, helpers, "Function", "IOriginal", true), ["sourceWritten"] = false, ["executed"] = false };
    }
    static JsonArray Parts(FunctionSignature signature, JsonObject snapshot, JsonObject contract, string body, string helpers, string type, string originalInterface, bool preview)
    {
        string original = snapshot["sourceParameter"]!.ToString(), context = snapshot["contextVariable"]!.ToString(), branch = "originalBranch";
        var used = signature.Args.Select(p => p.Name).Concat(new[] { original, context }).ToHashSet(StringComparer.Ordinal);
        while (!used.Add(branch)) branch = "_" + branch;
        used.Add(snapshot["returnVariable"]!.ToString()); string storage = "nativeReturn"; while (!used.Add(storage)) storage = "_" + storage;
        string outputParameter = signature.Return == "void" ? "" : ", out " + signature.Return + " @" + storage, capture = signature.Return == "void" ? "" : "@" + storage + " = @" + snapshot["returnVariable"] + ";\n";
        string Args(bool declarations, bool inputsOnly = false) => string.Join(", ", signature.Args.Where(p => !inputsOnly || !p.IsOut).Select(p => (p.Mode is "out" or "ref" ? p.Mode + " " : "") + (declarations ? p.Type + " " : "") + "@" + p.Name));
        string inputTail = signature.Args.Any(p => !p.IsOut) ? ", " + Args(false, true) : "", declarations = signature.Args.Any(p => !p.IsOut) ? ", " + Args(true, true) : "";
        string members = string.Join("\n", contract["members"]!.AsArray().Select(m => "    " + m!["name"] + " = " + m["value"] + ","));
        string fixedPrefix = (preview ? snapshot["originalInterface"]!.ToString() : "") + (preview ? "public" : "private") + " static class " + type + "\n{\npublic enum OriginalResult\n{\n    NoBranch = 0,\n}\n\n" + snapshot["contextSource"] + "\npublic enum Result\n{\n";
        string fixedCall = "\n}\npublic static Result Execute(" + originalInterface + " @" + original + (signature.Args.Count > 0 ? ", " + Args(true) : "") + outputParameter + ")\n{\n" + snapshot["originalCall"] + capture + "var @" + branch + " = OriginalResult.NoBranch;\nreturn After(@" + branch + ", @" + context + inputTail + ");\n}\nprivate static Result After(OriginalResult @" + branch + ", SourceContext @" + context + declarations + ")\n{\n";
        return new JsonArray(new JsonObject { ["text"] = fixedPrefix }, new JsonObject { ["id"] = "enum", ["text"] = members }, new JsonObject { ["text"] = fixedCall }, new JsonObject { ["id"] = "body", ["text"] = body }, new JsonObject { ["text"] = "\n}\n" }, new JsonObject { ["id"] = "helpers", ["text"] = helpers }, new JsonObject { ["text"] = "\n}\n" });
    }
    public static string Member(Element feature, JsonObject postCall, JsonObject executionEnum, string type, string originalInterface, string marker)
    {
        var prepared = Prepare(feature, executionEnum, postCall["contractHash"]!.GetValue<string>(), postCall["source"]!.GetValue<string>(), postCall["helpers"]?.GetValue<string>() ?? "", postCall["returnMapping"]?.GetValue<string>());
        var parts = Parts(feature.Signature!, prepared["snapshot"]!.AsObject(), prepared["executionEnum"]!.AsObject(), prepared["source"]!.ToString(), prepared["helpers"]!.ToString(), type, originalInterface, false);
        return string.Concat(parts.Select(p => p!["id"]?.ToString() is "enum" or "body" or "helpers" ? "#line 1 " + System.Text.Json.JsonSerializer.Serialize(marker + "/" + p["id"]) + "\n" + p["text"] + "\n#line default\n" : p["text"]!.ToString()));
    }
}
