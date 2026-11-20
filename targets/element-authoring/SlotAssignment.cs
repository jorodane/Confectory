using Confectory.Core;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Security.Cryptography;

// A selection over existing provide semantics. No source/registration is created.
internal static class SlotAssignment
{
    static void Need(bool value, string message)
    { if (!value) throw new ArgumentException(message); }
    static string S(JsonNode? node, string key) => node?[key]?.ToString() ?? "";
    static string Hash(string value) => Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(value))).ToLowerInvariant();
    static JsonObject Scope(IEnumerable<KeyValuePair<string, string>> entries)
    {
        var result = new JsonObject();
        foreach (var entry in entries.OrderBy(p => p.Key, StringComparer.Ordinal))
        {
            Need(entry.Key.Length is > 0 and <= 512 && !Path.IsPathRooted(entry.Key)
                && !entry.Key.Replace('\\', '/').Split('/').Any(p => p is "" or "." or "..")
                && System.Text.RegularExpressions.Regex.IsMatch(entry.Value, "\\A[a-f0-9]{64}\\z"),
                "Bounded existing original source scope required");
            Need(result[entry.Key] is null || S(result, entry.Key) == entry.Value, "Original source aliases differ");
            result[entry.Key] = entry.Value;
        }
        Need(result.Count is > 0 and <= 240, "Bounded assignment read scope required");
        return result;
    }
    static string Fingerprint(string owner, string function, string previous, string target, JsonObject scope) =>
        Hash(new JsonObject { ["owner"] = owner, ["function"] = function, ["previous"] = previous,
            ["implementation"] = target, ["sources"] = scope.DeepClone() }.ToJsonString());

    public static JsonObject Prepare(JsonObject request, JsonObject? retainedScope = null)
    {
        var context = request["context"]!.AsObject();
        var units = context["guards"]!.AsObject();
        string owner = S(context, "owner"), function = S(request, "function"), target = S(request, "implementation");
        string prefix = owner.Split("::")[0] + "::";
        Need(units.Count is > 0 and <= 240 && Encoding.UTF8.GetByteCount(context.ToJsonString()) <= 16777216,
            "Bounded original slot observations required");
        JsonNode Unit(string id, string kind)
        {
            var unit = units[id];
            Need(id.StartsWith(prefix, StringComparison.Ordinal) && S(unit, "kind") == kind
                && S(unit, "baseline") is not ("" or "missing") && unit!["draft"] is not null
                && JsonNode.DeepEquals(unit["draft"], unit["original"]) && unit["copySource"] is null
                && unit["creationOwner"] is null && unit["atomicEditGroup"] is null,
                "Clean existing project-owned slot source required");
            return unit!;
        }
        var ownerUnit = Unit(owner, "object");
        var manifest = new Parser(S(Unit(units.Single(p => S(p.Value, "kind") == "project").Key, "project"), "draft"), "<slot-registration>").ParseManifest();
        Need(manifest.Namespace + "::" == prefix && manifest.Elements.Count <= 240, "Original project registration required");
        foreach (var entry in manifest.Elements)
            Need(units[prefix + entry.Key] is JsonNode header && S(header, "kind") == entry.Value.Kind
                && S(header, "path") == entry.Value.Path, "Retain every owned assignment header");
        foreach (var row in units) Need(row.Value!["draft"] is not null && JsonNode.DeepEquals(row.Value["draft"], row.Value["original"]),
            "Confirm or discard other saved source edits before selecting a slot implementation");
        var scope = retainedScope ?? Scope(units.Select(p => KeyValuePair.Create(S(p.Value, "path"), S(p.Value, "baseline"))));
        foreach (var row in units) Need(S(scope, S(row.Value, "path")) == S(row.Value, "baseline"), "Retain the original assignment read scope");
        var declaration = new Parser(S(ownerUnit, "draft"), "<slot-owner>").ParseElement();
        var provider = context["providers"]!.AsArray().Single(p => S(p, "function") == function)!;
        var requirement = context["requirements"]!.AsArray().Single(r => S(r, "function") == function)!;
        Unit(S(requirement, "origin"), "module");
        string module = S(requirement, "origin");
        declaration.Provides.TryGetValue(function, out var original);
        Need(S(provider, "origin") == owner && S(provider["contract"], "status") == "valid"
            && original is not null
            && original.Id == S(provider, "implementation") && S(request, "previous") == original.Id
            && original.Id != target && context["requirements"]!.AsArray().Any(r => S(r, "function") == function),
            "One existing directly provided module slot required");
        var feature = new Parser(S(Unit(function, "function"), "draft"), "<slot-contract>").ParseElement();
        var moduleDefinition = new Parser(S(Unit(module, "module"), "draft"), "<slot-module>").ParseElement();
        Need(declaration.Modules.Any(m => m.Id == module) && moduleDefinition.Requires.TryGetValue(function, out var required)
            && required.Signature.Matches(feature.Signature), "Directly attached owned module requirement required");
        Need(!BlueprintAsync.Has(feature) && !BlueprintExecutionBranches.Has(feature),
            "Preserve public async and execution-result provider contracts");
        var primitive = new HashSet<string>(["bool", "int", "long", "float", "double", "string"], StringComparer.Ordinal);
        Need(feature.Signature is not null && feature.Signature.Args.Count <= 16
            && feature.Signature.Args.All(a => primitive.Contains(a.Type) && a.Mode is null or "ref" or "out")
            && (feature.Signature.Return == "void" || primitive.Contains(feature.Signature.Return)),
            "Existing bounded primitive slot ABI required; preserve advanced type dependencies");
        var implementationUnit = Unit(target, "implementation");
        var implementation = new Parser(S(implementationUnit, "draft"), "<slot-selection>").ParseElement();
        Need(implementation.Id == target && implementation.Function == function && implementation.Parent is null
            && implementation.Tool is null
            && implementation.Signature is not null && feature.Signature is not null
            && implementation.Signature.Matches(feature.Signature) && implementation.Imports.Count == 0
            && implementation.Bodies.Count == 1 && implementation.Bodies.TryGetValue("common", out var body)
            && body.SourceKind == "csharp" && body.Origin == target,
            "Direct existing common native implementation with the unchanged contract required");
        var bodyUnit = Unit(target + "/body:common", "body");
        Need(S(bodyUnit, "path") == implementation.Bodies["common"].Path,
            "Preserve the observed implementation body locator");
        foreach (var row in units)
        {
            if (S(row.Value, "kind") is not ("object" or "schema" or "function" or "module" or "implementation")) continue;
            var source = new Parser(S(row.Value, "draft"), "<owned-slot-assignment>").ParseElement();
            Need(!source.Provides.Values.Any(p => p.Id == target) && !source.Defaults.Values.Any(p => p.Id == target)
                && !source.Contains.Any(p => p.Id == target),
                "A provider or default already assigned to another slot cannot be selected here");
        }
        return new JsonObject
        {
            ["implementation"] = target, ["previous"] = original!.Id,
            ["signature"] = JsonSerializer.SerializeToNode(implementation.Signature),
            ["description"] = implementation.Description,
            ["fingerprint"] = Fingerprint(owner, function, original.Id, target, scope)
        };
    }

    // Authenticate the existing receipt shape, never an invented native-body
    // marker or new checkpoint version. Read dependencies confer no write role.
    public static string[]? Saved(JsonObject units, string ns, string owner, JsonObject receipt,
        Func<Element, string> format, string action)
    {
        if (S(units[owner], "kind") != "object" || receipt["version"]?.GetValue<int>() != 1
            || S(receipt, "owner") != owner || S(receipt, "uiSurface") != ""
            || receipt["declaration"] is not null || receipt["priorOwner"] is not null
            || receipt.Count != 8 || receipt.Any(p => p.Key is not ("version" or "owner" or "uiSurface" or "declaration" or "priorOwner" or "intents" or "sources" or "readGuards")) || receipt["intents"] is not JsonArray { Count: 1 } intents
            || receipt["sources"] is not JsonObject { Count: 2 } proof
            || receipt["readGuards"] is not JsonObject guards || guards.Count == 0) return null;
        var intent = intents[0]!.AsObject();
        if (intent.Count != 8 || intent.Any(p => p.Key is not ("function" or "implementation" or "reference" or "remove" or "fingerprint" or "copySource" or "copyTarget" or "copyEditsHash")) || intent["reference"] is not null || intent["remove"]?.GetValue<bool>() != false
            || intent["copySource"] is not null || intent["copyTarget"] is not null || intent["copyEditsHash"] is not null) return null;
        string function = S(intent, "function"), target = S(intent, "implementation"), project = ns + "::ProjectManifest";
        Need(owner.StartsWith(ns + "::", StringComparison.Ordinal) && target.StartsWith(ns + "::", StringComparison.Ordinal)
            && S(proof[owner], "kind") == "object" && S(proof[project], "kind") == "project", "Exact saved object assignment proof required");
        var scope = Scope(guards.Select(p => { Need(S(p.Value, "path") == p.Key && p.Value!.AsObject().Count == 2, "Exact saved read guard required"); return KeyValuePair.Create(p.Key, S(p.Value, "hash")); }));
        foreach (string id in new[] { owner, project }) Need(S(proof[id], "path") == S(units[id], "path")
            && S(proof[id], "hash") == Hash(S(units[id], "draft")) && S(scope, S(units[id], "path")) == S(units[id], "baseline"),
            "Saved assignment owner/registration changed");
        var before = new Parser(S(units[owner], "original"), "<original-slot-owner>").ParseElement();
        var after = new Parser(S(units[owner], "draft"), "<saved-slot-owner>").ParseElement();
        Need(before.Id == owner && after.Id == owner && before.Kind == "object" && after.Kind == "object"
            && before.Provides.ContainsKey(function) && before.Provides[function].Id != target, "One saved local provider change required");
        string previous = before.Provides[function].Id;
        before.Provides[function] = new ElementReference(target, new(), owner);
        Need(format(before) == format(after)
            && Fingerprint(owner, function, previous, target, scope) == S(intent, "fingerprint"), "Retain only the exact saved provide mapping and original read scope");
        var manifest = new Parser(S(units[project], "original"), "<saved-slot-manifest>").ParseManifest();
        Need(manifest.Namespace == ns && manifest.Elements.Count <= 240 && JsonNode.DeepEquals(units[project]!["draft"], units[project]!["original"])
            && manifest.Elements.TryGetValue(target[(ns.Length + 2)..], out var locator) && locator.Kind == "implementation"
            && scope[locator.Path] is not null, "Existing registered implementation read required");
        if (action == "headers") return manifest.Elements.Keys.Select(id => ns + "::" + id).ToArray();
        var implementation = new Parser(S(units[target], "original"), "<saved-slot-target>").ParseElement();
        Need(implementation.Bodies.TryGetValue("common", out var body) && scope[body.Path] is not null, "Retain original common body observation");
        if (action == "graphs") return [target + "/body:common"];
        // SlotContext captures loaded reads; dormant draft:null units are not
        // pending edits. Keep all real drafts, and retain every saved file guard.
        var originalUnits = new JsonObject(units.Where(p => p.Value?["draft"] is not null)
            .Select(p => KeyValuePair.Create<string, JsonNode?>(p.Key, p.Value!.DeepClone())));
        originalUnits[owner]!["draft"] = originalUnits[owner]!["original"]!.DeepClone();
        var originalOwner = new Parser(S(units[owner], "original"), "<saved-slot-module-owner>").ParseElement();
        string module = originalOwner.Modules.Select(m => m.Id).First(id => units[id] is not null
            && new Parser(S(units[id], "original"), "<saved-slot-module>").ParseElement().Requires.ContainsKey(function));
        Prepare(new JsonObject { ["context"] = new JsonObject { ["owner"] = owner, ["guards"] = originalUnits,
            ["requirements"] = new JsonArray(new JsonObject { ["function"] = function, ["origin"] = module }),
            ["providers"] = new JsonArray(new JsonObject { ["function"] = function, ["implementation"] = previous,
                ["origin"] = owner, ["contract"] = new JsonObject { ["status"] = "valid" } }) },
            ["function"] = function, ["previous"] = previous, ["implementation"] = target }, scope);
        return [];
    }
}
