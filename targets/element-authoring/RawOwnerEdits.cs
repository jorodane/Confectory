using Confectory.Core;
using System.Text;
using System.Text.Json.Nodes;

// One pure candidate for the bound owner, including raw text and typed edits.
internal static class RawOwnerEdits
{
    public static JsonObject Prepare(JsonObject request, Func<Element, string> format, Func<Manifest, string> formatManifest)
    {
        string project = request["project"]!.GetValue<string>(), manifest = request["manifest"]!.GetValue<string>(), id = request["id"]!.GetValue<string>(), text = request["text"]!.GetValue<string>(), raw = request["rawText"]!.GetValue<string>();
        var declaration = new Parser(text, "<raw-owner>").ParseElement(); var changes = request["changes"]!.AsArray(); var drafts = request["drafts"]!.AsArray();
        if (declaration.Kind is not ("object" or "schema") || changes.Count > 64) throw new ArgumentException("Bounded owned raw/property candidate required");
        string Read(string path) { var file = new FileInfo(path); if (!file.Exists || file.Length > 1048576) throw new IOException("Raw source budget"); return File.ReadAllText(path); }
        JsonObject Inspect(string source, string registration, JsonArray overlays) => EffectiveMetadata.Query(project, registration, id, source, formatManifest, Read, overlays, schemaView: true, validateObjects: true, observeSources: true);
        void Valid(JsonObject model) { if (model["status"]?.ToString() != "available" || model["schemaModel"]?["validation"]?["status"]?.ToString() != "valid") throw new InvalidOperationException("Raw/property schema or reference invalid; all input retained"); }
        var before = Inspect(text, manifest, drafts); Valid(before);
        var prepared = changes.Count == 0 ? new JsonObject { ["text"] = text, ["manifest"] = manifest, ["additions"] = new JsonArray(), ["updates"] = new JsonArray(), ["observations"] = before["observations"]!.DeepClone(), ["sourceWritten"] = false, ["compiled"] = false }
            : declaration.Kind == "schema" ? InformationDefinitions.Prepare(request, format, formatManifest) : MixedOwnerCopyEdits.Prepare(request, format, formatManifest);
        string merged = DeclarationTextMerge.Merge(text, prepared["text"]!.GetValue<string>(), raw, format);
        var overlays = drafts.DeepClone().AsArray();
        foreach (var row in prepared["updates"]!.AsArray()) overlays.Single(d => d!["id"]!.ToString() == row!["id"]!.ToString())!["text"] = row!["text"]!.DeepClone();
        foreach (var row in prepared["additions"]!.AsArray()) overlays.Add(new JsonObject { ["id"] = row!["id"]!.DeepClone(), ["text"] = row["text"]!.DeepClone() });
        var final = Inspect(merged, prepared["manifest"]!.GetValue<string>(), overlays); Valid(final);
        var observations = new Dictionary<string, string>(OperatingSystem.IsWindows() ? StringComparer.OrdinalIgnoreCase : StringComparer.Ordinal);
        foreach (var group in new[] { prepared["observations"]!.AsArray(), final["observations"]!.AsArray() }) foreach (var row in group)
        {
            string path = row!["path"]!.ToString(), hash = row["hash"]!.ToString();
            if (observations.TryGetValue(path, out string? old) && old != hash) throw new InvalidOperationException("Raw dependency changed during preparation; no changes applied"); observations[path] = hash;
        }
        prepared["text"] = merged; prepared["observations"] = new JsonArray(observations.OrderBy(p => p.Key, StringComparer.Ordinal).Select(p => (JsonNode)new JsonObject { ["path"] = p.Key, ["hash"] = p.Value }).ToArray()); return prepared;
    }
}
