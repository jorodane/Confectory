using Confectory.Core;
using System.Text;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

// Proofs for the existing version-1 retained declaration lifetime. No source
// rewrite, consumer remapping or C# enum representation is introduced here.
internal static class EnumDefinitionRetirementProof
{
    public const string Mode = "enum-definition-v1";
    static string S(JsonNode value, string key) => value[key]!.GetValue<string>();
    static string Hash(string text) => JsonData.HashBytes(Encoding.UTF8.GetBytes(text));
    static bool Digest(string value) => Regex.IsMatch(value, "^[a-f0-9]{64}$", RegexOptions.CultureInvariant);
    public static bool Handles(JsonObject request) => request["evidence"]?["mode"]?.ToString() == Mode || request["outcome"]?["result"]?["mode"]?.ToString() == Mode;

    public static JsonObject Execute(JsonObject request)
    {
        string project = Path.GetFullPath(S(request, "project")), ns = S(request, "namespace"), root = Path.GetDirectoryName(project)!;
        var units = request["units"]!.AsObject();
        var workspace = new JsonObject { ["project"] = OperatingSystem.IsWindows() ? project.ToUpperInvariant() : project,
            ["participant"] = request["scope"]!["participant"]!.DeepClone(), ["context"] = request["scope"]!["context"]!.DeepClone() };
        bool Owned(string id) => id.StartsWith(ns + "::", StringComparison.Ordinal);
        string PathOf(JsonNode unit)
        {
            string relative = S(unit, "path"), path = PackPaths.Owned(root, relative);
            if (Path.IsPathRooted(relative)) throw new UnauthorizedAccessException("Owned archive path required");
            for (FileSystemInfo? node = new FileInfo(path); node is not null; node = node is FileInfo file ? file.Directory : ((DirectoryInfo)node).Parent)
            {
                if (node.LinkTarget is not null) throw new UnauthorizedAccessException("Archive cannot traverse links");
                if (node.FullName.Equals(root, OperatingSystem.IsWindows() ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal)) break;
            }
            return path;
        }
        void Source(JsonNode unit)
        {
            string path = PathOf(unit);
            if (!Digest(S(unit, "baseline")) || !File.Exists(path) || JsonData.HashBytes(File.ReadAllBytes(path)) != S(unit, "baseline") || File.ReadAllText(path) != S(unit, "original"))
                throw new InvalidOperationException("Retained declaration changed; preserve archive and input");
        }
        void Receipt(JsonObject receipt)
        {
            if (receipt["version"]?.GetValue<int>() != 1 || S(receipt, "mode") != Mode || !Digest(S(receipt, "token")) || !JsonNode.DeepEquals(receipt["workspace"], workspace) || S(receipt, "state") is not ("pending" or "confirmed" or "restoring"))
                throw new ArgumentException("Owned enum archive receipt required");
            var ids = receipt["ids"]!.AsArray(); var entries = receipt["entries"]!.AsObject();
            if (ids.Count is < 1 or > 32 || entries.Count != ids.Count || !entries.Any(p => p.Value?["kind"]?.ToString() == "enum") || ids.Select(v => v!.ToString()).Distinct(StringComparer.Ordinal).Count() != ids.Count)
                throw new ArgumentException("Complete enum archive members required");
            foreach (var id in ids)
            {
                var unit = entries[id!.ToString()] ?? throw new ArgumentException("Missing archive member");
                if (!Owned(id.ToString()) || S(unit, "id") != id.ToString() || S(unit, "kind") is not ("object" or "schema" or "category" or "concept" or "module" or "function" or "enum")) throw new ArgumentException("Owned archive member required");
                Source(unit);
            }
        }
        void ValidateOutcome(JsonObject outcome)
        {
            if (outcome["version"]?.GetValue<int>() != 1 || !JsonNode.DeepEquals(outcome["workspace"], workspace) || !Digest(S(outcome, "token")) || S(outcome, "action") is not ("apply" or "recover" or "cancel") || S(outcome, "phase") is not ("" or "pending" or "confirmed" or "restoring")) throw new ArgumentException("Owned enum archive outcome required");
            var result = outcome["result"]!.AsObject(); var ids = result["ids"]!.AsArray(); string manifest = S(result, "manifest");
            if (S(result, "mode") != Mode || S(result, "state") != "staged" || result["checkpointSaved"]?.GetValue<bool>() != true || result["physicalSourceRemoved"]?.GetValue<bool>() != false || result["sourceConfirmed"]?.GetValue<bool>() != false || ids.Count is < 1 or > 32 || manifest != ns + "::ProjectManifest" && manifest != ns + "::PackManifest") throw new ArgumentException("Enum archive result scope");
            var expected = ids.Select(v => v!.GetValue<string>()).ToHashSet(StringComparer.Ordinal);
            if (expected.Count != ids.Count || expected.Contains(manifest) || expected.Any(id => !Owned(id))) throw new ArgumentException("Enum archive outcome members");
            expected.Add(manifest); var seen = new HashSet<string>(StringComparer.Ordinal); var sources = outcome["sources"]!.AsObject();
            if (sources[manifest]?["kind"]?.ToString() is not ("project" or "pack")) throw new ArgumentException("Enum archive registration proof");
            foreach (var pair in sources)
            {
                if (!seen.Add(pair.Key) || !expected.Contains(pair.Key) || pair.Value is not JsonObject proof || proof.Count != 3 || !Digest(S(proof, "hash")) || S(proof, "kind") is not ("object" or "schema" or "category" or "concept" or "module" or "function" or "enum" or "project" or "pack")) throw new ArgumentException("Enum archive source proof");
                PathOf(proof);
            }
            foreach (var id in outcome["absent"]!.AsArray()) if (!seen.Add(id!.ToString()) || !expected.Contains(id.ToString())) throw new ArgumentException("Enum archive absent proof");
            if (!seen.SetEquals(expected)) throw new ArgumentException("Complete enum archive outcome required");
        }
        string action = S(request, "action");
        if (action is "validate-outcome" or "settled")
        {
            var outcome = request["outcome"]!.AsObject(); ValidateOutcome(outcome);
            if (action == "validate-outcome") return new JsonObject { ["valid"] = true };
            string token = S(outcome, "token"), phase = request["retirements"]?[token]?["state"]?.ToString() ?? "";
            bool settled = phase == S(outcome, "phase") && outcome["absent"]!.AsArray().All(id => units[id!.ToString()] is null);
            foreach (var pair in outcome["sources"]!.AsObject())
            {
                var unit = units[pair.Key];
                if (unit?["draft"] is null || unit["path"]?.ToString() != pair.Value!["path"]!.ToString() || unit["kind"]?.ToString() != pair.Value["kind"]!.ToString() || Hash(S(unit, "draft")) != S(pair.Value, "hash")) { settled = false; continue; }
                Source(unit);
            }
            if (settled && phase.Length > 0) Receipt(request["retirements"]![token]!.AsObject());
            return new JsonObject { ["settled"] = settled };
        }
        if (action == "unapplied")
        {
            var evidence = request["evidence"]!.AsObject(); string transition = S(request, "transition");
            if (transition == "apply") return new JsonObject { ["unapplied"] = evidence["version"]?.GetValue<int>() == 1 && JsonNode.DeepEquals(evidence["workspace"], workspace) && JsonNode.DeepEquals(evidence["observed"], units) && evidence["references"]!.AsArray().Count == 0 };
            Receipt(evidence); string phase = S(evidence, "state");
            return new JsonObject { ["unapplied"] = transition == "recover" && phase is "pending" or "confirmed" || transition == "cancel" && phase == "restoring" };
        }
        throw new ArgumentException("Explicit enum archive proof action required");
    }
}
