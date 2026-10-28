using Confectory.Core;
using System.Text;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

// A saved information binding has a different lifetime from its provider. This
// candidate never removes a function, implementation, body, import or registration.
internal static class InformationBindingRetirement
{
    public const string Mode = "information-binding-v1";
    static string S(JsonNode node, string key) => node[key]!.GetValue<string>();
    static string Hash(string value) => JsonData.HashBytes(Encoding.UTF8.GetBytes(value));
    static bool Token(string value) => Regex.IsMatch(value, "^[a-f0-9]{64}$", RegexOptions.CultureInvariant);
    static readonly HashSet<string> Declarations = new(StringComparer.Ordinal) { "object", "schema", "concept", "category", "module", "function", "implementation" };

    public static bool Handles(JsonObject request) => request["mode"]?.ToString() == Mode
        || request["evidence"]?["mode"]?.ToString() == Mode || request["receipt"]?["mode"]?.ToString() == Mode
        || request["outcome"]?["result"]?["mode"]?.ToString() == Mode;

    public static bool RetainProvider(JsonObject request)
    {
        var units = request["units"]!.AsObject();
        var owner = new Parser(S(units[S(request, "owner")]!, "draft"), "<information-binding>").ParseElement();
        if (!owner.Provides.TryGetValue(S(request, "function"), out var provider)) return false;
        return units[provider.Id] is not JsonNode unit || unit["copySource"] is not null
            || new Parser(S(unit, "draft"), "<retained-implementation>").ParseElement().Parent is not null;
    }

    sealed class Context(JsonObject request, Func<Element, string> format, Func<Manifest, string> formatManifest)
    {
        readonly string project = Path.GetFullPath(S(request, "project"));
        readonly string ns = S(request, "namespace");
        readonly JsonObject scope = request["scope"]!.AsObject();
        JsonObject units = request["units"]!.DeepClone().AsObject();
        string Root => Path.GetDirectoryName(project)!;
        JsonObject Workspace() => new() { ["project"] = OperatingSystem.IsWindows() ? project.ToUpperInvariant() : project, ["participant"] = scope["participant"]!.DeepClone(), ["context"] = scope["context"]!.DeepClone() };
        string PathOf(JsonNode unit)
        {
            string relative = S(unit, "path"), path = PackPaths.Owned(Root, relative);
            if (Path.IsPathRooted(relative)) throw new UnauthorizedAccessException("Owned binding source required");
            for (FileSystemInfo? entry = new FileInfo(path); entry is not null; entry = entry is FileInfo file ? file.Directory : ((DirectoryInfo)entry).Parent)
            {
                if (entry.LinkTarget is not null) throw new UnauthorizedAccessException("Binding sources cannot traverse links");
                if (entry.FullName.Equals(Root, OperatingSystem.IsWindows() ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal)) break;
            }
            return path;
        }
        JsonObject Located(string id)
        {
            if (!id.StartsWith(ns + "::", StringComparison.Ordinal) || units[id] is not JsonObject unit || S(unit, "id") != id)
                throw new UnauthorizedAccessException("Exact owned information source required");
            PathOf(unit); return unit;
        }
        JsonObject Unit(string id) { var unit = Located(id); if (unit["draft"] is null) throw new InvalidOperationException("Read the owned binding source first"); return unit; }
        Element Parse(string id) => new Parser(S(Unit(id), "draft"), "<information-binding>").ParseElement();
        public void Guards()
        {
            foreach (var pair in units)
            {
                var unit = pair.Value!; if (unit["draft"] is null) continue;
                string path = PathOf(unit), baseline = S(unit, "baseline");
                if (baseline == "missing") { if (File.Exists(path) || Directory.Exists(path)) throw new InvalidOperationException("Binding destination changed; preserve input"); }
                else { var bytes = File.ReadAllBytes(path); if (bytes.Length > 1048576 || JsonData.HashBytes(bytes) != baseline || File.ReadAllText(path) != S(unit, "original")) throw new InvalidOperationException("Binding source changed; preserve input"); }
            }
        }
        JsonObject Retained(string function, string implementation)
        {
            var result = new JsonObject(); var seen = new HashSet<string>(StringComparer.Ordinal);
            void Include(string id)
            {
                if (!id.StartsWith(ns + "::", StringComparison.Ordinal) || !seen.Add(id)) return;
                var unit = Unit(id); if (result.Count >= 64) throw new ArgumentException("Retained binding source budget");
                result[id] = new JsonObject { ["kind"] = unit["kind"]!.DeepClone(), ["path"] = unit["path"]!.DeepClone(), ["hash"] = Hash(S(unit, "draft")) };
                var element = Parse(id); if (element.Parent is not null) Include(element.Parent);
                if (element.Kind == "implementation")
                {
                    var graphs = new JsonObject(); foreach (var row in units.Where(row => row.Key.StartsWith(id + "/body:", StringComparison.Ordinal) && row.Value?["kind"]?.ToString() == "blueprint")) graphs[row.Key] = row.Value!["draft"]!.DeepClone();
                    var bodies = BodyUnitMetadata.Query(new JsonObject { ["project"] = project, ["id"] = id, ["path"] = unit["path"]!.DeepClone(), ["text"] = unit["draft"]!.DeepClone(), ["blueprintDrafts"] = graphs });
                    foreach (var row in bodies["units"]!.AsArray())
                    {
                        string bodyId = S(row!, "id"), bodyPath = PathOf(row!); var loaded = units[bodyId];
                        if (loaded is not null && (S(loaded, "kind") != S(row!, "kind") || S(loaded, "path") != S(row!, "path"))) throw new InvalidOperationException("Retained body locator changed");
                        if (loaded is null && (!File.Exists(bodyPath) || new FileInfo(bodyPath).Length > 1048576)) throw new IOException("Retained body unavailable");
                        result[bodyId] = new JsonObject { ["kind"] = row!["kind"]!.DeepClone(), ["path"] = row["path"]!.DeepClone(), ["hash"] = Hash(loaded is null ? File.ReadAllText(bodyPath) : S(loaded, "draft")) };
                    }
                }
            }
            Include(function); Include(implementation); if (result.Count > 64) throw new ArgumentException("Retained binding source budget"); return result;
        }
        JsonObject Core(string owner, string function, string implementation, bool requireOwnedFunction = false, bool contractOnly = false)
        {
            var ownerUnit = Unit(owner); var info = Parse(owner); string manifestId = ns + "::ProjectManifest"; var manifestUnit = Unit(manifestId);
            var manifest = new Parser(S(manifestUnit, "draft"), "<binding-registration>").ParseManifest();
            if (S(ownerUnit, "kind") != "schema" || info.Id != owner || info.Kind != "schema" || manifest.Kind != "project" || manifest.Namespace != ns || S(manifestUnit, "path") != Path.GetFileName(project)) throw new UnauthorizedAccessException("Owned information and project registration required");
            if (!manifest.Elements.TryGetValue(owner[(ns.Length + 2)..], out var locator) || locator.Kind != "schema" || locator.Path != S(ownerUnit, "path")) throw new UnauthorizedAccessException("Exact information registration required");
            if (!info.Provides.TryGetValue(function, out var provider) || provider.Id != implementation) throw new InvalidOperationException("Only the current information's explicit provider can be detached");
            foreach (string id in new[] { owner, manifestId }) if (Unit(id)["hierarchyGroup"] is not null || Unit(id)["rootContractGroup"] is not null || Unit(id)["retirementGroup"] is not null) throw new InvalidOperationException("Finish the current binding transaction first");
            var overlays = new JsonArray(); foreach (var row in units) if (row.Key != owner && row.Value?["draft"] is not null && Declarations.Contains(S(row.Value, "kind"))) overlays.Add(new JsonObject { ["id"] = row.Key, ["text"] = row.Value["draft"]!.DeepClone() });
            var effective = EffectiveMetadata.Query(project, S(manifestUnit, "draft"), owner, S(ownerUnit, "draft"), formatManifest,
                path => { var file = new FileInfo(path); if (!file.Exists || file.Length > 1048576) throw new IOException("Binding contract unavailable"); return File.ReadAllText(path); }, overlays, observeSources: true);
            if (effective["status"]?.ToString() != "available") throw new InvalidOperationException("Binding contract unavailable; preserve input");
            var method = effective["ownFunctions"]!.AsArray().SingleOrDefault(row => row!["id"]?.ToString() == function && row["origin"]?.ToString() == owner && row["writable"]?.GetValue<bool>() == true);
            var requirement = effective["requirements"]!.AsArray().SingleOrDefault(row => row!["function"]?.ToString() == function);
            var resolved = effective["providers"]!.AsArray().SingleOrDefault(row => row!["function"]?.ToString() == function && row["implementation"]?.ToString() == implementation && row["origin"]?.ToString() == owner && row["contract"]?["status"]?.ToString() == "valid");
            if (resolved is null || method is null && requirement is null || requireOwnedFunction && method is null) throw new UnauthorizedAccessException("This information's declared function or module binding required");
            if (requireOwnedFunction || method is not null) { var fn = Unit(function); string prefix = owner + "_Function_"; if (!function.StartsWith(prefix, StringComparison.Ordinal) || !Regex.IsMatch(function[prefix.Length..], "^[a-f0-9]{32}$", RegexOptions.CultureInvariant) || S(fn, "path") != "elements/" + function[(ns.Length + 2)..] + ".celem" || Parse(function).Parent is not null || S(fn, "baseline") == "missing" || S(fn, "draft") != S(fn, "original")) throw new InvalidOperationException("Confirm the unchanged owned function declaration first"); }
            info.Provides.Remove(function); string after = DeclarationTextMerge.Merge(S(ownerUnit, "draft"), format(info), S(ownerUnit, "draft"), format);
            var retained = Retained(function, implementation); var review = new SortedSet<string>(StringComparer.Ordinal) { owner, manifestId }; var creation = new JsonObject();
            foreach (var row in retained.Where(_ => !contractOnly))
            {
                if (units[row.Key]?["baseline"]?.ToString() != "missing") continue;
                var unit = Unit(row.Key);
                if (S(unit, "original") != "" || row.Key != implementation && !row.Key.StartsWith(implementation + "/body:", StringComparison.Ordinal) || Unit(implementation)["creationOwner"]?.ToString() != owner) throw new InvalidOperationException("Preserve another owner's unpublished source before detaching a binding");
                review.Add(row.Key); creation[row.Key] = unit.DeepClone();
            }
            if (creation.Count > 0 && !creation.ContainsKey(implementation)) throw new InvalidOperationException("Retain the complete unpublished implementation");
            foreach (string id in review.Where(_ => !contractOnly)) if (Unit(id)["atomicEditGroup"] is JsonArray group && group.Any(member => !review.Contains(member!.ToString()) || !JsonNode.DeepEquals(Unit(member.ToString())["atomicEditGroup"], group))) throw new InvalidOperationException("Preserve the complete existing review group");
            if (review.Count > 33) throw new ArgumentException("Retained binding review budget");
            return new JsonObject { ["version"] = 2, ["mode"] = Mode, ["workspace"] = Workspace(), ["owner"] = owner, ["function"] = function, ["implementation"] = implementation,
                ["label"] = method?["name"]?.DeepClone() ?? JsonValue.Create(function.Split("::")[^1]), ["manifest"] = manifestId, ["ids"] = new JsonArray(), ["entries"] = new JsonObject(),
                ["ownerBefore"] = ownerUnit.DeepClone(), ["ownerAfter"] = after, ["manifestBefore"] = manifestUnit.DeepClone(), ["afterManifest"] = manifestUnit["draft"]!.DeepClone(), ["references"] = new JsonArray(),
                ["reviewIds"] = System.Text.Json.JsonSerializer.SerializeToNode(review.ToArray()), ["reviewCreation"] = creation,
                ["binding"] = new JsonObject { ["signature"] = (method ?? requirement)!["signature"]!.DeepClone(), ["provider"] = resolved.DeepClone(), ["retained"] = retained, ["observations"] = effective["observations"]!.DeepClone() } };
        }
        public JsonObject Plan(bool requireOwnedFunction)
        {
            string owner = S(request, "owner"), function = S(request, "function"); if (Hash(S(Unit(owner), "draft")) != S(request, "ownerHash")) throw new InvalidOperationException("Information changed before binding removal");
            string implementation = request["implementation"]?.ToString() ?? Parse(owner).Provides.GetValueOrDefault(function)?.Id ?? throw new InvalidOperationException("Local provider unavailable");
            Guards(); var plan = Core(owner, function, implementation, requireOwnedFunction); plan["observed"] = units.DeepClone(); plan["checkpointHash"] = request["checkpointHash"]!.DeepClone(); plan["token"] = Hash(plan.ToJsonString()); return plan;
        }
        JsonObject Receipt(JsonObject receipt)
        {
            if (receipt["version"]?.GetValue<int>() != 2 || receipt["mode"]?.ToString() != Mode || !Token(S(receipt, "token")) || S(receipt, "state") is not ("pending" or "confirmed" or "restoring") || receipt["ids"] is not JsonArray ids || ids.Count != 0 || receipt["entries"] is not JsonObject entries || entries.Count != 0 || !JsonNode.DeepEquals(receipt["workspace"], Workspace())) throw new ArgumentException("Exact retained-binding receipt required");
            string owner = S(receipt, "owner"), function = S(receipt, "function"), implementation = S(receipt, "implementation"); var before = receipt["ownerBefore"]!; var manifestBefore = receipt["manifestBefore"]!;
            if (S(before, "id") != owner || S(before, "kind") != "schema" || S(before, "path") != S(Unit(owner), "path") || S(receipt, "manifest") != ns + "::ProjectManifest" || S(manifestBefore, "id") != S(receipt, "manifest") || S(manifestBefore, "kind") != "project" || S(manifestBefore, "path") != Path.GetFileName(project) || S(receipt, "afterManifest") != S(manifestBefore, "draft")) throw new ArgumentException("Retained binding identity changed");
            PathOf(before); PathOf(manifestBefore); var info = new Parser(S(before, "draft"), "<binding-receipt>").ParseElement(); var manifest = new Parser(S(manifestBefore, "draft"), "<binding-receipt-registration>").ParseManifest();
            if (info.Id != owner || info.Kind != "schema" || manifest.Namespace != ns || manifest.Kind != "project" || !manifest.Elements.TryGetValue(owner[(ns.Length + 2)..], out var locator) || locator.Kind != "schema" || locator.Path != S(before, "path") || !info.Provides.TryGetValue(function, out var provider) || provider.Id != implementation) throw new ArgumentException("Retained local provide proof required");
            info.Provides.Remove(function); if (DeclarationTextMerge.Merge(S(before, "draft"), format(info), S(before, "draft"), format) != S(receipt, "ownerAfter")) throw new ArgumentException("Only the selected local binding may change");
            if (receipt["binding"] is not JsonObject binding || binding.Count != 4 || binding["retained"] is not JsonObject retained || retained.Count > 64 || binding["observations"] is not JsonArray observations || observations.Count > 2048 || binding["signature"] is not JsonObject || binding["provider"]?["function"]?.ToString() != function || binding["provider"]?["implementation"]?.ToString() != implementation || binding["provider"]?["origin"]?.ToString() != owner || binding["provider"]?["contract"]?["status"]?.ToString() != "valid") throw new ArgumentException("Retained binding contract proof required");
            foreach (var row in retained) { if (!row.Key.StartsWith(ns + "::", StringComparison.Ordinal) || row.Value is not JsonObject proof || proof.Count != 3 || !Token(S(proof, "hash"))) throw new ArgumentException("Bounded retained source proof"); PathOf(proof); }
            foreach (var row in observations) if (row is not JsonObject proof || proof.Count != 2 || !Path.IsPathFullyQualified(S(proof, "path")) || !Token(S(proof, "hash"))) throw new ArgumentException("Bounded observed contract proof");
            var review = receipt["reviewIds"]!.AsArray().Select(id => id!.GetValue<string>()).ToArray(); var creation = receipt["reviewCreation"]!.AsObject();
            if (review.Length is < 2 or > 33 || review.Distinct(StringComparer.Ordinal).Count() != review.Length || !review.Contains(owner) || !review.Contains(S(receipt, "manifest")) || creation.Count != review.Length - 2 || creation.Count > 0 && (creation[implementation]?["kind"]?.ToString() != "implementation" || creation[implementation]?["creationOwner"]?.ToString() != owner)) throw new ArgumentException("Complete owned binding review required");
            foreach (var row in creation)
            {
                var unit = row.Value!; if (!review.Contains(row.Key) || row.Key != implementation && !row.Key.StartsWith(implementation + "/body:", StringComparison.Ordinal) || retained[row.Key] is null || S(unit, "id") != row.Key || S(unit, "baseline") != "missing" || S(unit, "original") != "" || S(unit, "path") != S(retained[row.Key]!, "path") || S(unit, "kind") != S(retained[row.Key]!, "kind") || Hash(S(unit, "draft")) != S(retained[row.Key]!, "hash")) throw new ArgumentException("Unpublished provider remains in its owned review"); PathOf(unit);
            }
            return receipt;
        }
        void CurrentContract(JsonObject receipt)
        {
            var saved = units; try { units = units.DeepClone().AsObject(); units[S(receipt, "owner")] = receipt["ownerBefore"]!.DeepClone(); units[S(receipt, "manifest")] = receipt["manifestBefore"]!.DeepClone(); foreach (string id in new[] { S(receipt, "owner"), S(receipt, "manifest") }) { Unit(id).Remove("atomicEditGroup"); Unit(id).Remove("retirementGroup"); } var current = Core(S(receipt, "owner"), S(receipt, "function"), S(receipt, "implementation"), contractOnly: true); if (!JsonNode.DeepEquals(current["binding"], receipt["binding"])) throw new InvalidOperationException("Retained provider contract or source changed; preserve archive and input"); } finally { units = saved; }
        }
        public JsonObject ValidateState(JsonObject receipt)
        {
            Receipt(receipt); var info = Parse(S(receipt, "owner")); var manifest = new Parser(S(Unit(S(receipt, "manifest")), "draft"), "<current-binding-registration>").ParseManifest();
            if (info.Kind != "schema" || info.Id != S(receipt, "owner") || manifest.Kind != "project" || manifest.Namespace != ns) throw new ArgumentException("Current binding owner changed");
            if (S(receipt, "state") == "restoring" && info.Provides.GetValueOrDefault(S(receipt, "function"))?.Id != S(receipt, "implementation")) throw new InvalidOperationException("Restored binding changed");
            // A stale provider remains a readable archive, never an automatic grant
            // to restore it. The actual transition revalidates its current sources.
            return new JsonObject { ["valid"] = true, ["ids"] = new JsonArray() };
        }
        public bool Unapplied(string action, JsonObject evidence)
        {
            Guards(); if (action == "apply") { if (!JsonNode.DeepEquals(evidence["observed"], units)) return false; var core = Core(S(evidence, "owner"), S(evidence, "function"), S(evidence, "implementation")); return SameCore(core, evidence); }
            Receipt(evidence); ValidateState(evidence); CurrentContract(evidence);
            string owner = S(evidence, "owner"), manifest = S(evidence, "manifest"); string expected = S(evidence, "state") == "restoring" ? S(evidence["ownerBefore"]!, "draft") : S(evidence, "ownerAfter"); return S(Unit(owner), "draft") == expected
                && S(Unit(manifest), "draft") == S(evidence, "afterManifest");
        }
        static bool SameCore(JsonObject left, JsonObject right) => new[] { "version", "mode", "workspace", "owner", "function", "implementation", "label", "manifest", "ids", "entries", "ownerBefore", "ownerAfter", "manifestBefore", "afterManifest", "binding", "reviewIds", "reviewCreation", "references" }.All(key => JsonNode.DeepEquals(left[key], right[key]));
        public JsonObject Transition(string action, JsonObject evidence)
        {
            var archives = request["retirements"]!.DeepClone().AsObject(); string token = S(evidence, "token"); JsonObject receipt;
            if (action == "apply") { if (archives.Any(row => row.Value?["state"]?.ToString() is "pending" or "restoring") || !JsonNode.DeepEquals(evidence["observed"], units)) throw new InvalidOperationException("Binding removal plan changed; preserve input"); var core = Core(S(evidence, "owner"), S(evidence, "function"), S(evidence, "implementation")); if (!SameCore(core, evidence)) throw new InvalidOperationException("Binding removal candidate changed"); receipt = core; receipt.Remove("references"); receipt["token"] = token; receipt["state"] = "pending"; }
            else { if (archives[token] is not JsonObject found || !JsonNode.DeepEquals(found, evidence) || archives.Any(row => row.Key != token && row.Value?["state"]?.ToString() is "pending" or "restoring")) throw new InvalidOperationException("Binding recovery receipt changed"); receipt = found; ValidateState(receipt); CurrentContract(receipt); }
            Guards(); string owner = S(receipt, "owner"), manifest = S(receipt, "manifest");
            void Require(string id, string text) { if (S(Unit(id), "draft") != text) throw new InvalidOperationException("Binding owner or registration changed; all input retained"); }
            void Rev(JsonObject unit, long prior = 0) => unit["revision"] = Math.Max(unit["revision"]!.GetValue<long>(), prior) + 1;
            var reviewIds = receipt["reviewIds"]!.AsArray().Select(id => id!.ToString()).ToArray();
            void Group() { foreach (string id in reviewIds) Unit(id)["retirementGroup"] = receipt["reviewIds"]!.DeepClone(); }
            if (action == "apply") { Unit(owner)["draft"] = receipt["ownerAfter"]!.DeepClone(); Rev(Unit(owner)); Group(); archives[token] = receipt; }
            else if (S(receipt, "state") == "pending") { Require(owner, S(receipt, "ownerAfter")); Require(manifest, S(receipt, "afterManifest")); foreach (string id in reviewIds) Unit(id).Remove("retirementGroup"); foreach (var pair in new[] { (owner, "ownerBefore"), (manifest, "manifestBefore") }) { long revision = Unit(pair.Item1)["revision"]!.GetValue<long>(); units[pair.Item1] = receipt[pair.Item2]!.DeepClone(); Rev(Unit(pair.Item1), revision); } archives.Remove(token); }
            else if (S(receipt, "state") == "confirmed" && action == "recover") { Require(owner, S(receipt, "ownerAfter")); Require(manifest, S(receipt, "afterManifest")); receipt["beforeRestoreOwner"] = Unit(owner)["draft"]!.DeepClone(); receipt["beforeRestoreManifest"] = Unit(manifest)["draft"]!.DeepClone(); Unit(owner)["draft"] = receipt["ownerBefore"]!["draft"]!.DeepClone(); Rev(Unit(owner)); Group(); receipt["state"] = "restoring"; }
            else if (S(receipt, "state") == "restoring" && action == "cancel") { Require(owner, S(receipt["ownerBefore"]!, "draft")); Require(manifest, S(receipt["manifestBefore"]!, "draft")); Unit(owner)["draft"] = receipt["beforeRestoreOwner"]!.DeepClone(); Rev(Unit(owner)); foreach (string id in reviewIds) Unit(id).Remove("retirementGroup"); receipt["state"] = "confirmed"; }
            else throw new InvalidOperationException("Binding recovery action does not match phase");
            if (archives.Count > 32 || Encoding.UTF8.GetByteCount(archives.ToJsonString()) > 8388608) throw new ArgumentException("Binding archive budget");
            return new JsonObject { ["units"] = units.DeepClone(), ["retirements"] = archives, ["mode"] = Mode, ["owner"] = owner, ["manifest"] = manifest, ["function"] = receipt["function"]!.DeepClone(), ["implementation"] = receipt["implementation"]!.DeepClone(), ["ids"] = new JsonArray(), ["physicalSourceRemoved"] = false, ["sourceConfirmed"] = false };
        }
        public void ValidateOutcome(JsonObject outcome)
        {
            var result = outcome["result"]!; string owner = S(result, "owner"), manifest = ns + "::ProjectManifest";
            if (outcome["version"]?.GetValue<int>() != 1 || !Token(S(outcome, "token")) || !JsonNode.DeepEquals(outcome["workspace"], Workspace()) || S(outcome, "action") is not ("apply" or "recover" or "cancel") || S(outcome, "phase") is not ("" or "pending" or "confirmed" or "restoring") || result["mode"]?.ToString() != Mode || S(result, "state") != "staged" || result["checkpointSaved"]?.GetValue<bool>() != true || result["physicalSourceRemoved"]?.GetValue<bool>() != false || result["sourceConfirmed"]?.GetValue<bool>() != false || result["ids"] is not JsonArray ids || ids.Count != 0 || S(result, "manifest") != manifest || result["function"] is not JsonValue || result["implementation"] is not JsonValue) throw new ArgumentException("Exact binding outcome required");
            if (S(Located(owner), "kind") != "schema" || S(Located(manifest), "kind") != "project" || S(Located(manifest), "path") != Path.GetFileName(project)) throw new ArgumentException("Owned binding outcome identity"); var sources = outcome["sources"]!.AsObject(); if (sources.Count != 2 || outcome["absent"]!.AsArray().Count != 0 || sources[owner]?["kind"]?.ToString() != "schema" || sources[manifest]?["kind"]?.ToString() != "project") throw new ArgumentException("Binding outcome changes owner only");
            foreach (string id in new[] { owner, manifest }) { var proof = sources[id]!; if (proof.AsObject().Count != 3 || !Token(S(proof, "hash")) || S(proof, "path") != S(Located(id), "path")) throw new ArgumentException("Binding outcome source identity"); PathOf(proof); }
        }
        public bool Settled(JsonObject outcome)
        {
            ValidateOutcome(outcome); string token = S(outcome, "token"); if ((request["retirements"]?[token]?["state"]?.ToString() ?? "") != S(outcome, "phase")) return false;
            foreach (var source in outcome["sources"]!.AsObject()) if (Hash(S(Unit(source.Key), "draft")) != S(source.Value!, "hash")) return false;
            if (S(outcome, "phase").Length > 0) ValidateState(request["retirements"]![token]!.AsObject()); return true;
        }
        public JsonObject Run(bool requireOwnedFunction)
        {
            string action = S(request, "action"); return action switch {
                "plan" => Plan(requireOwnedFunction), "validate" => ValidateState(request["receipt"]!.AsObject()),
                "validate-outcome" => ValidateOutcomeResult(), "settled" => new() { ["settled"] = Settled(request["outcome"]!.AsObject()) },
                "unapplied" => new() { ["unapplied"] = Unapplied(S(request, "transition"), request["evidence"]!.AsObject()) },
                "apply" or "recover" or "cancel" => Transition(action, request["evidence"]!.AsObject()), _ => throw new ArgumentException("Explicit binding archive action required") };
        }
        JsonObject ValidateOutcomeResult() { ValidateOutcome(request["outcome"]!.AsObject()); return new() { ["valid"] = true }; }
    }
    public static JsonObject Execute(JsonObject request, Func<Element, string> format, Func<Manifest, string> formatManifest, bool requireOwnedFunction = false)
        => new Context(request, format, formatManifest).Run(requireOwnedFunction);
}
