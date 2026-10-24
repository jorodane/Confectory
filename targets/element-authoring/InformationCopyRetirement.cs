using Confectory.Core;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

// Retire only a proven local copy closure. Donors and inherited/shared providers
// keep their separate binding lifetime. No source is physically written/deleted.
internal static class InformationCopyRetirement
{
    public const string Mode = "information-copy-v1";
    static string S(JsonNode n, string key) => n[key]!.GetValue<string>();
    static string Hash(string text) => JsonData.HashBytes(Encoding.UTF8.GetBytes(text));
    static bool Token(string text) => Regex.IsMatch(text, "^[a-f0-9]{64}$", RegexOptions.CultureInvariant);
    static readonly HashSet<string> Declarations = new(StringComparer.Ordinal) { "object", "schema", "concept", "category", "module", "function", "implementation" };
    static readonly string[] CoreFields = ["version", "mode", "workspace", "owner", "function", "implementation", "label", "manifest", "ids", "entries", "ownerBefore", "ownerAfter", "manifestBefore", "afterManifest", "bindingProof"];
    public static bool Handles(JsonObject r) => r["mode"]?.ToString() == Mode || r["evidence"]?["mode"]?.ToString() == Mode || r["receipt"]?["mode"]?.ToString() == Mode || r["outcome"]?["result"]?["mode"]?.ToString() == Mode;

    sealed class Context(JsonObject request, Func<Element, string> format, Func<Manifest, string> formatManifest)
    {
        readonly string project = Path.GetFullPath(S(request, "project")), ns = S(request, "namespace");
        JsonObject units = request["units"]!.DeepClone().AsObject();
        string Root => Path.GetDirectoryName(project)!;
        JsonObject Workspace() => new() { ["project"] = OperatingSystem.IsWindows() ? project.ToUpperInvariant() : project, ["participant"] = request["scope"]!["participant"]!.DeepClone(), ["context"] = request["scope"]!["context"]!.DeepClone() };
        string PathOf(JsonNode unit)
        {
            string relative = S(unit, "path"), path = PackPaths.Owned(Root, relative);
            if (Path.IsPathRooted(relative)) throw new UnauthorizedAccessException("Owned copy path required");
            for (FileSystemInfo? entry = new FileInfo(path); entry is not null; entry = entry is FileInfo file ? file.Directory : ((DirectoryInfo)entry).Parent)
            { if (entry.LinkTarget is not null) throw new UnauthorizedAccessException("Copy archive cannot traverse links"); if (entry.FullName.Equals(Root, OperatingSystem.IsWindows() ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal)) break; }
            return path;
        }
        JsonObject Unit(string id)
        {
            if (!id.StartsWith(ns + "::", StringComparison.Ordinal) || units[id] is not JsonObject unit || S(unit, "id") != id || unit["draft"] is null) throw new InvalidOperationException("Read the exact owned copy source first");
            PathOf(unit); return unit;
        }
        Element Parse(string id) => new Parser(S(Unit(id), "draft"), "<information-copy>").ParseElement();
        void Guards()
        {
            foreach (var row in units)
            {
                var unit = row.Value!; if (unit["draft"] is null) continue;
                string path = PathOf(unit);
                if (S(unit, "baseline") == "missing") { if (File.Exists(path) || Directory.Exists(path)) throw new InvalidOperationException("Copy destination changed; preserve input"); }
                else if (new FileInfo(path).Length > 1048576 || JsonData.HashBytes(File.ReadAllBytes(path)) != S(unit, "baseline") || File.ReadAllText(path) != S(unit, "original")) throw new InvalidOperationException("Copy archive source changed; preserve input");
            }
        }
        JsonObject BindingRequest(string action) { var r = request.DeepClone().AsObject(); r["units"] = units.DeepClone(); r["mode"] = InformationBindingRetirement.Mode; r["action"] = action; return r; }
        JsonObject Core(string owner, string function, string implementation, JsonObject? savedProof = null)
        {
            JsonObject binding;
            if (savedProof is null)
            {
                var r = BindingRequest("plan"); r["owner"] = owner; r["function"] = function; r["implementation"] = implementation; r["ownerHash"] = Hash(S(Unit(owner), "draft"));
                r["checkpointHash"] = request["checkpointHash"]?.DeepClone() ?? JsonValue.Create("missing");
                binding = InformationBindingRetirement.Execute(r, format, formatManifest); binding.Remove("observed"); binding.Remove("checkpointHash"); binding.Remove("references"); binding["state"] = "pending"; binding.Remove("token"); binding["token"] = Hash(binding.ToJsonString());
            }
            else
            {
                binding = savedProof.DeepClone().AsObject(); var r = BindingRequest("validate"); r["receipt"] = binding.DeepClone();
                InformationBindingRetirement.Execute(r, format, formatManifest);
            }
            if (S(binding, "owner") != owner || S(binding, "function") != function || S(binding, "implementation") != implementation || !JsonNode.DeepEquals(binding["ownerBefore"], Unit(owner))) throw new ArgumentException("Exact copy binding proof required");
            var implUnit = Unit(implementation); var impl = Parse(implementation); string local = implementation[(ns.Length + 2)..], manifestId = ns + "::ProjectManifest";
            if (S(implUnit, "kind") != "implementation" || impl.Id != implementation || impl.Kind != "implementation" || impl.Function != function || impl.Parent is not null || S(implUnit, "path") != "elements/" + local + ".celem" || implUnit["creationOwner"] is not null && implUnit["creationOwner"]!.ToString() != owner || !JsonNode.DeepEquals(JsonSerializer.SerializeToNode(impl.Signature), binding["binding"]!["signature"])) throw new UnauthorizedAccessException("Exact locally owned copy implementation required");
            var manifest = new Parser(S(Unit(manifestId), "draft"), "<copy-registration>").ParseManifest();
            if (!manifest.Elements.TryGetValue(local, out var locator) || locator.Kind != "implementation" || locator.Path != S(implUnit, "path")) throw new UnauthorizedAccessException("Exact owned copy registration required");
            var graphs = new JsonObject(); foreach (var row in units.Where(row => row.Key.StartsWith(implementation + "/body:", StringComparison.Ordinal) && row.Value?["kind"]?.ToString() == "blueprint")) graphs[row.Key] = row.Value!["draft"]!.DeepClone();
            var bodies = BodyUnitMetadata.Query(new JsonObject { ["project"] = project, ["id"] = implementation, ["path"] = implUnit["path"]!.DeepClone(), ["text"] = implUnit["draft"]!.DeepClone(), ["blueprintDrafts"] = graphs.DeepClone() });
            var members = new SortedSet<string>(StringComparer.Ordinal) { implementation }; bool copy = false;
            foreach (var body in bodies["units"]!.AsArray())
            {
                string id = S(body!, "id"); var unit = Unit(id);
                if (S(unit, "path") != S(body!, "path") || S(unit, "kind") != S(body!, "kind")) throw new InvalidOperationException("Complete copy body locator required");
                if (S(unit, "kind") is "blueprint" or "blueprint-node") BlueprintDocuments.Validate(id, S(unit, "kind"), S(unit, "draft"));
                if (S(unit, "kind") == "blueprint" && JsonNode.Parse(S(unit, "draft")) is JsonObject graph && graph["copySource"] is JsonObject provenance)
                {
                    string target = S(body!, "target");
                    if (provenance.Count != 4 || provenance["implementation"] is not JsonValue || string.IsNullOrWhiteSpace(S(provenance, "implementation")) || S(provenance, "implementation") == implementation || provenance["bodyOrigin"] is not JsonValue || string.IsNullOrWhiteSpace(S(provenance, "bodyOrigin")) || S(provenance, "bodyOrigin") == implementation || S(provenance, "target") != target || provenance["sourceKind"]?.ToString() is not ("csharp" or "blueprint") || graph["feature"]?.ToString() != function || S(unit, "path") != "blueprints/" + local + ".graph.json" || implUnit["copySource"] is not null && !JsonNode.DeepEquals(implUnit["copySource"], provenance)) throw new ArgumentException("Stable private copy provenance required");
                    copy = true;
                }
                members.Add(id);
            }
            if (!copy || members.Count is <2 or >29 || units.Any(row => row.Key.StartsWith(implementation + "/body:", StringComparison.Ordinal) && !members.Contains(row.Key))) throw new InvalidOperationException("Complete proven copy closure required");
            var all = members.Concat(new[] { owner, manifestId }).ToHashSet(StringComparer.Ordinal); var paths = new HashSet<string>(OperatingSystem.IsWindows() ? StringComparer.OrdinalIgnoreCase : StringComparer.Ordinal);
            foreach (string id in all)
            {
                var unit = Unit(id);
                if (!paths.Add(PathOf(unit)) || unit["retirementGroup"] is not null || unit["rootContractGroup"] is not null || unit["hierarchyGroup"] is not null || unit["atomicEditGroup"] is JsonArray group && (group.Count > 64 || group.Any(member => !all.Contains(member!.ToString()) || !JsonNode.DeepEquals(Unit(member.ToString())["atomicEditGroup"], group)))) throw new InvalidOperationException("Preserve the complete exclusive copy source group");
                if (members.Contains(id))
                {
                    var proof = binding["binding"]!["retained"]?[id] ?? throw new ArgumentException("Every copy closure member needs retained source proof");
                    if (S(proof, "path") != S(unit, "path") || S(proof, "kind") != S(unit, "kind") || S(proof, "hash") != Hash(S(unit, "draft"))) throw new ArgumentException("Copy body proof changed");
                }
            }
            foreach (var row in units) if (!all.Contains(row.Key) && paths.Contains(PathOf(row.Value!))) throw new InvalidOperationException("Another source owns a copy destination");
            var references = new JsonArray();
            void Add(string source, string target, string role) { if (references.Count >= 128) throw new ArgumentException("Copy reference budget"); references.Add(new JsonObject { ["source"] = source, ["target"] = target, ["role"] = role }); }
            void Values(JsonNode? node, string source) { if (node is JsonValue value && value.TryGetValue<string>(out string? text) && text is not null && members.Contains(text)) Add(source, text, "copy-reference"); else if (node is JsonObject obj) foreach (var child in obj) Values(child.Value, source); else if (node is JsonArray array) foreach (var child in array) Values(child, source); }
            if (savedProof is null) foreach (var row in units)
            {
                if (members.Contains(row.Key) || row.Value?["draft"] is null) continue;
                if (Declarations.Contains(S(row.Value, "kind")))
                {
                    var element = new Parser(row.Key == owner ? S(binding, "ownerAfter") : S(row.Value, "draft"), "<copy-users>").ParseElement();
                    if (element.Function is string fn && members.Contains(fn)) Add(row.Key, fn, "implementation");
                    Values(DeclaredRelations.Describe(element), row.Key);
                    foreach (var value in element.Values.Where(v => v.Key.StartsWith(InformationDefaults.Prefix, StringComparison.Ordinal) && v.Value.Value.ValueKind == JsonValueKind.String)) Values(JsonNode.Parse(value.Value.Value.GetString()!), row.Key);
                    if (element.Kind == "implementation")
                    {
                        var locations = BodyUnitMetadata.Query(new JsonObject { ["project"] = project, ["id"] = row.Key, ["path"] = row.Value["path"]!.DeepClone(), ["text"] = row.Value["draft"]!.DeepClone(), ["blueprintDrafts"] = graphs.DeepClone() });
                        foreach (var location in locations["units"]!.AsArray()) if (members.Any(id => PathOf(Unit(id)).Equals(PathOf(location!), OperatingSystem.IsWindows() ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal))) Add(row.Key, implementation, "shared-body");
                    }
                }
                else if (S(row.Value, "kind") is "blueprint" or "blueprint-node") Values(JsonNode.Parse(S(row.Value, "draft")), row.Key);
            }
            manifest.Elements.Remove(local); var entries = new JsonObject(); foreach (string id in members) entries[id] = Unit(id).DeepClone();
            return new JsonObject { ["version"] = 2, ["mode"] = Mode, ["workspace"] = Workspace(), ["owner"] = owner, ["function"] = function, ["implementation"] = implementation, ["label"] = binding["label"]!.DeepClone(), ["manifest"] = manifestId, ["ids"] = JsonSerializer.SerializeToNode(members.ToArray()), ["entries"] = entries, ["ownerBefore"] = Unit(owner).DeepClone(), ["ownerAfter"] = binding["ownerAfter"]!.DeepClone(), ["manifestBefore"] = Unit(manifestId).DeepClone(), ["afterManifest"] = DeclarationTextMerge.MergeManifest(S(Unit(manifestId), "draft"), formatManifest(manifest), formatManifest), ["bindingProof"] = binding, ["references"] = references };
        }
        bool IsCopy(string implementation) => units[implementation] is JsonObject && units.Any(row => row.Key.StartsWith(implementation + "/body:", StringComparison.Ordinal) && row.Value?["kind"]?.ToString() == "blueprint" && row.Value?["draft"] is not null && JsonNode.Parse(S(row.Value, "draft"))?["copySource"] is not null);
        public JsonObject? Plan()
        {
            string owner = S(request, "owner"), function = S(request, "function");
            string implementation = request["implementation"]?.ToString() ?? Parse(owner).Provides.GetValueOrDefault(function)?.Id ?? "";
            if (!IsCopy(implementation)) return null;
            if (Unit(implementation)["creationOwner"] is JsonValue creator && creator.ToString() != owner) return null;
            if (Hash(S(Unit(owner), "draft")) != S(request, "ownerHash")) throw new InvalidOperationException("Information changed before copy archive");
            Guards(); var core = Core(owner, function, implementation); if (core["references"]!.AsArray().Count > 0) return null;
            core["observed"] = units.DeepClone(); core["checkpointHash"] = request["checkpointHash"]!.DeepClone(); core["token"] = Hash(core.ToJsonString()); return core;
        }
        JsonObject Restored(JsonObject receipt)
        {
            var restored = units.DeepClone().AsObject(); restored[S(receipt, "owner")] = receipt["ownerBefore"]!.DeepClone(); restored[S(receipt, "manifest")] = receipt["manifestBefore"]!.DeepClone();
            foreach (var row in receipt["entries"]!.AsObject()) { if (S(row.Value!, "id") != row.Key) throw new ArgumentException("Copy archive entry identity"); restored[row.Key] = row.Value!.DeepClone(); }
            return restored;
        }
        JsonObject Receipt(JsonObject receipt)
        {
            if (receipt["version"]?.GetValue<int>() != 2 || receipt["mode"]?.ToString() != Mode || !Token(S(receipt, "token")) || S(receipt, "state") is not ("pending" or "confirmed" or "restoring") || !JsonNode.DeepEquals(receipt["workspace"], Workspace()) || receipt["ids"] is not JsonArray ids || ids.Count is <2 or >29 || receipt["entries"] is not JsonObject entries || entries.Count != ids.Count || ids.Select(id => id!.ToString()).Distinct(StringComparer.Ordinal).Count() != ids.Count || ids.Any(id => entries[id!.ToString()] is null) || !ids.Any(id => id!.ToString() == S(receipt, "implementation"))) throw new ArgumentException("Exact bounded copy archive required");
            var saved = units; try { units = Restored(receipt); var core = Core(S(receipt, "owner"), S(receipt, "function"), S(receipt, "implementation"), receipt["bindingProof"]!.AsObject()); if (CoreFields.Any(key => !JsonNode.DeepEquals(core[key], receipt[key]))) throw new ArgumentException("Copy archive proof changed"); return core; } finally { units = saved; }
        }
        public JsonObject ValidateState(JsonObject receipt)
        {
            Receipt(receipt); string owner = S(receipt, "owner"), manifestId = S(receipt, "manifest"), phase = S(receipt, "state");
            var info = Parse(owner); var manifest = new Parser(S(Unit(manifestId), "draft"), "<current-copy-registration>").ParseManifest();
            if (info.Kind != "schema" || info.Id != owner || manifest.Kind != "project" || manifest.Namespace != ns || S(Unit(owner), "path") != S(receipt["ownerBefore"]!, "path")) throw new ArgumentException("Current copy owner identity changed");
            foreach (var row in receipt["entries"]!.AsObject())
            {
                if (phase == "restoring") { if (S(Unit(row.Key), "path") != S(row.Value!, "path") || S(Unit(row.Key), "kind") != S(row.Value!, "kind")) throw new ArgumentException("Recovered copy identity changed"); }
                else if (units[row.Key] is not null) throw new InvalidOperationException("Archived copy identity already exists");
            }
            string local = S(receipt, "implementation")[(ns.Length + 2)..];
            if (phase == "restoring" ? !manifest.Elements.TryGetValue(local, out var locator) || locator.Path != S(receipt["entries"]![S(receipt, "implementation")]!, "path") || info.Provides.GetValueOrDefault(S(receipt, "function"))?.Id != S(receipt, "implementation") : manifest.Elements.ContainsKey(local)) throw new InvalidOperationException("Copy archive registration changed");
            return new JsonObject { ["valid"] = true, ["ids"] = receipt["ids"]!.DeepClone() };
        }
        void Revalidate(JsonObject receipt)
        {
            Guards(); var saved = units; try
            {
                units = Restored(receipt);
                // Recreate the old logical binding against the current disk baseline.
                // Confirm changes registration/owner bytes, never the archived copy bytes.
                foreach (string id in new[] { S(receipt, "owner"), S(receipt, "manifest") }) foreach (string field in new[] { "baseline", "original", "revision" }) units[id]![field] = saved[id]![field]!.DeepClone();
                Guards(); var current = Core(S(receipt, "owner"), S(receipt, "function"), S(receipt, "implementation"));
                if (current["references"]!.AsArray().Count > 0 || !JsonNode.DeepEquals(current["bindingProof"]!["binding"], receipt["bindingProof"]!["binding"])) throw new InvalidOperationException("Copy references or callable contract changed; preserve archive and input");
            } finally { units = saved; }
        }
        public bool Unapplied(string action, JsonObject evidence)
        {
            Guards(); if (action == "apply") { if (!JsonNode.DeepEquals(evidence["observed"], units)) return false; var core = Core(S(evidence, "owner"), S(evidence, "function"), S(evidence, "implementation")); return CoreFields.All(key => JsonNode.DeepEquals(core[key], evidence[key])) && core["references"]!.AsArray().Count == 0; }
            ValidateState(evidence); Revalidate(evidence); bool restoring = S(evidence, "state") == "restoring";
            return S(Unit(S(evidence, "owner")), "draft") == (restoring ? S(evidence["ownerBefore"]!, "draft") : S(evidence, "ownerAfter")) && S(Unit(S(evidence, "manifest")), "draft") == (restoring ? S(evidence["manifestBefore"]!, "draft") : S(evidence, "afterManifest")) && (!restoring || evidence["entries"]!.AsObject().All(row => JsonNode.DeepEquals(Unit(row.Key)["draft"], row.Value!["draft"])));
        }
        public JsonObject Transition(string action, JsonObject evidence)
        {
            var archives = request["retirements"]!.DeepClone().AsObject(); string token = S(evidence, "token"); JsonObject receipt;
            if (action == "apply") { if (!JsonNode.DeepEquals(evidence["observed"], units) || archives.Any(row => row.Value?["state"]?.ToString() is "pending" or "restoring")) throw new InvalidOperationException("Copy archive plan changed"); var core = Core(S(evidence, "owner"), S(evidence, "function"), S(evidence, "implementation")); if (CoreFields.Any(key => !JsonNode.DeepEquals(core[key], evidence[key])) || core["references"]!.AsArray().Count > 0) throw new InvalidOperationException("Copy archive candidate changed"); Guards(); receipt = core; receipt.Remove("references"); receipt["token"] = token; receipt["state"] = "pending"; }
            else { if (archives[token] is not JsonObject found || !JsonNode.DeepEquals(found, evidence) || archives.Any(row => row.Key != token && row.Value?["state"]?.ToString() is "pending" or "restoring")) throw new InvalidOperationException("Copy recovery receipt changed"); receipt = found; ValidateState(receipt); Revalidate(receipt); }
            string owner = S(receipt, "owner"), manifest = S(receipt, "manifest"); var ids = receipt["ids"]!.AsArray().Select(id => id!.ToString()).ToArray();
            void Rev(JsonObject unit, long prior = 0) => unit["revision"] = Math.Max(unit["revision"]!.GetValue<long>(), prior) + 1;
            void Require(string id, string text) { if (S(Unit(id), "draft") != text) throw new InvalidOperationException("Copy owner changed; preserve every input"); }
            void Group(IEnumerable<string> names) { var list = JsonSerializer.SerializeToNode(names.Order(StringComparer.Ordinal).ToArray())!; foreach (string id in names) { Unit(id).Remove("atomicEditGroup"); Unit(id)["retirementGroup"] = list.DeepClone(); } }
            if (action == "apply") { foreach (string id in ids) units.Remove(id); Unit(owner)["draft"] = receipt["ownerAfter"]!.DeepClone(); Unit(manifest)["draft"] = receipt["afterManifest"]!.DeepClone(); Rev(Unit(owner)); Rev(Unit(manifest)); Group([owner, manifest]); archives[token] = receipt; }
            else if (S(receipt, "state") == "pending") { Require(owner, S(receipt, "ownerAfter")); Require(manifest, S(receipt, "afterManifest")); foreach (string id in ids) units[id] = receipt["entries"]![id]!.DeepClone(); foreach (var pair in new[] { (owner, "ownerBefore"), (manifest, "manifestBefore") }) { long revision = Unit(pair.Item1)["revision"]!.GetValue<long>(); units[pair.Item1] = receipt[pair.Item2]!.DeepClone(); Rev(Unit(pair.Item1), revision); } archives.Remove(token); }
            else if (S(receipt, "state") == "confirmed" && action == "recover") { Require(owner, S(receipt, "ownerAfter")); Require(manifest, S(receipt, "afterManifest")); foreach (string id in ids) { units[id] = receipt["entries"]![id]!.DeepClone(); Rev(Unit(id)); } receipt["beforeRestoreOwner"] = Unit(owner)["draft"]!.DeepClone(); receipt["beforeRestoreManifest"] = Unit(manifest)["draft"]!.DeepClone(); Unit(owner)["draft"] = receipt["ownerBefore"]!["draft"]!.DeepClone(); Unit(manifest)["draft"] = receipt["manifestBefore"]!["draft"]!.DeepClone(); Rev(Unit(owner)); Rev(Unit(manifest)); Group(ids.Concat([owner, manifest])); receipt["state"] = "restoring"; }
            else if (S(receipt, "state") == "restoring" && action == "cancel") { Require(owner, S(receipt["ownerBefore"]!, "draft")); Require(manifest, S(receipt["manifestBefore"]!, "draft")); foreach (string id in ids) { if (!JsonNode.DeepEquals(Unit(id)["draft"], receipt["entries"]![id]!["draft"])) throw new InvalidOperationException("Recovered copy has newer input"); units.Remove(id); } Unit(owner)["draft"] = receipt["beforeRestoreOwner"]!.DeepClone(); Unit(manifest)["draft"] = receipt["beforeRestoreManifest"]!.DeepClone(); Rev(Unit(owner)); Rev(Unit(manifest)); Unit(owner).Remove("retirementGroup"); Unit(manifest).Remove("retirementGroup"); receipt["state"] = "confirmed"; }
            else throw new InvalidOperationException("Explicit copy recovery phase required");
            if (archives.Count > 32 || Encoding.UTF8.GetByteCount(archives.ToJsonString()) > 8388608) throw new ArgumentException("Copy archive budget");
            return new JsonObject { ["units"] = units.DeepClone(), ["retirements"] = archives, ["mode"] = Mode, ["owner"] = owner, ["manifest"] = manifest, ["function"] = receipt["function"]!.DeepClone(), ["implementation"] = receipt["implementation"]!.DeepClone(), ["ids"] = receipt["ids"]!.DeepClone(), ["physicalSourceRemoved"] = false, ["sourceConfirmed"] = false };
        }
        void ValidateOutcome(JsonObject outcome)
        {
            var result = outcome["result"]!; var ids = result["ids"]!.AsArray(); string owner = S(result, "owner"), manifest = S(result, "manifest"), implementation = S(result, "implementation");
            if (outcome["version"]?.GetValue<int>() != 1 || !Token(S(outcome, "token")) || !JsonNode.DeepEquals(outcome["workspace"], Workspace()) || S(outcome, "action") is not ("apply" or "recover" or "cancel") || S(outcome, "phase") is not ("" or "pending" or "confirmed" or "restoring") || result["mode"]?.ToString() != Mode || result["state"]?.ToString() != "staged" || result["checkpointSaved"]?.GetValue<bool>() != true || result["physicalSourceRemoved"]?.GetValue<bool>() != false || result["sourceConfirmed"]?.GetValue<bool>() != false || ids.Count is <2 or >29 || manifest != ns + "::ProjectManifest" || result["function"] is not JsonValue) throw new ArgumentException("Exact copy outcome required");
            var expected = ids.Select(id => id!.ToString()).ToHashSet(StringComparer.Ordinal); if (expected.Count != ids.Count || !expected.Contains(implementation) || expected.Contains(owner) || expected.Contains(manifest) || expected.Any(id => !id.StartsWith(ns + "::", StringComparison.Ordinal))) throw new ArgumentException("Copy outcome closure identity"); expected.Add(owner); expected.Add(manifest);
            var seen = new HashSet<string>(StringComparer.Ordinal); var sources = outcome["sources"]!.AsObject();
            if (sources[owner]?["kind"]?.ToString() != "schema" || sources[manifest]?["kind"]?.ToString() != "project") throw new ArgumentException("Copy outcome owner identity");
            foreach (var row in sources) { if (!expected.Contains(row.Key) || !seen.Add(row.Key) || row.Value is not JsonObject proof || proof.Count != 3 || !Token(S(proof, "hash")) || S(proof, "kind") is not ("schema" or "project" or "implementation" or "body" or "blueprint" or "blueprint-node")) throw new ArgumentException("Bounded copy outcome proof"); PathOf(proof); }
            foreach (var id in outcome["absent"]!.AsArray()) if (!expected.Contains(id!.ToString()) || !seen.Add(id.ToString())) throw new ArgumentException("Copy outcome absent identity");
            if (!seen.SetEquals(expected)) throw new ArgumentException("Complete copy outcome required");
        }
        bool Settled(JsonObject outcome)
        {
            ValidateOutcome(outcome); string token = S(outcome, "token"); if ((request["retirements"]?[token]?["state"]?.ToString() ?? "") != S(outcome, "phase")) return false;
            foreach (var id in outcome["absent"]!.AsArray()) if (units[id!.ToString()] is not null) return false;
            foreach (var row in outcome["sources"]!.AsObject()) if (units[row.Key] is not JsonObject unit || S(unit, "kind") != S(row.Value!, "kind") || S(unit, "path") != S(row.Value!, "path") || Hash(S(Unit(row.Key), "draft")) != S(row.Value!, "hash")) return false;
            if (S(outcome, "phase").Length > 0) ValidateState(request["retirements"]![token]!.AsObject()); return true;
        }
        public JsonObject Execute() => S(request, "action") switch { "validate" => ValidateState(request["receipt"]!.AsObject()), "validate-outcome" => ValidateOutcomeResult(), "settled" => new() { ["settled"] = Settled(request["outcome"]!.AsObject()) }, "unapplied" => new() { ["unapplied"] = Unapplied(S(request, "transition"), request["evidence"]!.AsObject()) }, "apply" or "recover" or "cancel" => Transition(S(request, "action"), request["evidence"]!.AsObject()), _ => throw new ArgumentException("Explicit copy archive action required") };
        JsonObject ValidateOutcomeResult() { ValidateOutcome(request["outcome"]!.AsObject()); return new() { ["valid"] = true }; }
    }
    public static JsonObject? TryPlan(JsonObject request, Func<Element, string> format, Func<Manifest, string> formatManifest) => new Context(request, format, formatManifest).Plan();
    public static JsonObject Execute(JsonObject request, Func<Element, string> format, Func<Manifest, string> formatManifest) => new Context(request, format, formatManifest).Execute();
}
