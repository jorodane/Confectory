using System.Text.Json;
using System.Text.Json.Nodes;

namespace Confectory.Core;

// Optional acceleration artifact for the desktop editor's initial forms. The
// canonical authoring reader produces the projection; the linker embeds it in
// the application, never in mutable user settings. All installation paths are
// relocatable and the runtime must recheck the original read proof.
internal static class ConnectionPresentationResource
{
    internal const string Name = "connection-preview-v1.json";
    internal static JsonObject? Prepare(string project, string target, JsonObject linkage, string? authoringTool)
    {
        if (string.IsNullOrEmpty(authoringTool) || target is not ("linux" or "windows" or "portable") || linkage["project"]?.ToString() != "Confectory.EditorHome") return null;
        try
        {
            string editor = Path.GetDirectoryName(project)!;
            string? repo = Path.GetDirectoryName(Path.GetDirectoryName(editor));
            if (repo is null || Path.GetFileName(project) != "project.cpack" || Path.GetFileName(editor) != "editor-home" || Path.GetFileName(Path.GetDirectoryName(editor)) != "examples") return null;
            // Use only the explicitly selected authoring strategy (the desktop
            // packager supplies its already-required tool). Never execute a
            // program discovered merely by a user project's directory shape.
            string tool = Path.GetFullPath(authoringTool);
            string core = Path.Combine(Path.GetDirectoryName(tool)!, "Confectory.Core.dll");
            if (!File.Exists(tool) || !File.Exists(core)) return null;
            string ToolHash(string path) => JsonData.HashBytes(File.ReadAllBytes(path));
            string toolHash = ToolHash(tool), coreHash = ToolHash(core);
            string scratch = Path.Combine(Path.GetTempPath(), "confectory-link-preview-" + Guid.NewGuid().ToString("N"));
            var entries = new JsonObject();
            string Relative(string root, string path)
            {
                string relative = Path.GetRelativePath(root, Path.GetFullPath(path));
                if (Path.IsPathRooted(relative) || relative == ".." || relative.StartsWith(".." + Path.DirectorySeparatorChar, StringComparison.Ordinal)) throw new IOException("Connection presentation outside installation");
                return relative.Replace(Path.DirectorySeparatorChar, '/');
            }
            foreach (var row in linkage["elements"]!.AsArray())
            {
                if (row?["kind"]?.ToString() != "object" || row["metadataValues"]?["role"]?["value"]?.ToString() != "ai-connection") continue;
                string id = row["id"]!.GetValue<string>();
                if (id == "Confectory.AIConnection::Connection") continue;
                if (entries.Count >= 16) return null;
                string owner = Path.Combine(scratch, "ai-settings", JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(id))[..16]);
                string settings = Path.Combine(owner, "project.cpack");
                var reply = Processes.Run([Processes.DotNet(), tool], JsonSerializer.Serialize(new { operation = "connectionSettings", project, id, settingsProject = settings, presentation = true }), timeoutSeconds: 20);
                if (reply.ExitCode != 0 || reply.Stdout.Length > 2097152) continue;
                var envelope = JsonNode.Parse(reply.Stdout)!;
                if (envelope["ok"]?.GetValue<bool>() != true || envelope["result"] is not JsonObject generated || generated["connection"]?.ToString() != id || generated["credentialRead"]?.GetValue<bool>() != false || generated["executionPerformed"]?.GetValue<bool>() != false || generated["connectionModelProof"] is not JsonObject proof || generated["presentation"] is not JsonObject effective || effective["status"]?.ToString() != "available" || effective["schemaModel"]?["validation"]?["status"]?.ToString() != "valid" || effective["schemaModel"]?["executionAuthorized"]?.GetValue<bool>() != false) continue;
                string InstallPath(string path) => "install/" + Relative(repo, path);
                string PresentationPath(string path)
                {
                    string full = Path.GetFullPath(path);
                    if (full.StartsWith(owner + Path.DirectorySeparatorChar, OperatingSystem.IsWindows() ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal)) return "settings/" + Relative(owner, full);
                    return InstallPath(full);
                }
                string manifest = generated["manifest"]!.GetValue<string>();
                var parsed = new Parser(manifest, "<connection-presentation>").ParseManifest();
                if (parsed.Namespace != "Confectory.AISettings" || parsed.Kind != "project" || parsed.Elements.Count != 1) continue;
                var registryPaths = new JsonArray();
                foreach (var registration in parsed.Registry.Values)
                {
                    string relative = Relative(repo, registration.Path), token = "@install/" + relative;
                    string old = JsonSerializer.Serialize(registration.Path), replacement = JsonSerializer.Serialize(token);
                    if (!manifest.Contains(old, StringComparison.Ordinal)) throw new IOException("Connection manifest template path missing");
                    manifest = manifest.Replace(old, replacement, StringComparison.Ordinal);
                    registryPaths.Add(relative);
                }
                generated["manifest"] = manifest;
                proof["project"] = InstallPath(proof["project"]!.GetValue<string>());
                void Paths(JsonArray list, Func<string,string> normalize) { for (int i = 0; i < list.Count; i++) list[i] = normalize(list[i]!.GetValue<string>()); }
                void Observations(JsonArray list, Func<string,string> normalize) { foreach (var observation in list) observation!["path"] = normalize(observation["path"]!.GetValue<string>()); }
                Paths(proof["paths"]!.AsArray(), InstallPath); Observations(proof["observations"]!.AsArray(), InstallPath);
                Paths(effective["ownershipPaths"]!.AsArray(), PresentationPath); Observations(effective["observations"]!.AsArray(), InstallPath);
                // Only parser source locations contain physical paths outside
                // the proof. Keep values and user-facing metadata untouched.
                void Locations(JsonNode? node)
                {
                    if (node is JsonObject obj)
                    {
                        foreach (string locationKey in new[] { "Loc", "loc" })
                            if (obj[locationKey] is JsonObject loc)
                                foreach (string fileKey in new[] { "File", "file" })
                                    if (loc[fileKey] is JsonValue file && file.TryGetValue<string>(out var path)) loc[fileKey] = PresentationPath(path);
                        foreach (var child in obj) Locations(child.Value);
                    }
                    else if (node is JsonArray items) foreach (var child in items) Locations(child);
                }
                Locations(effective);
                entries[id] = new JsonObject { ["registryPaths"] = registryPaths, ["generated"] = generated.DeepClone() };
            }
            if (entries.Count == 0 || ToolHash(tool) != toolHash || ToolHash(core) != coreHash) return null;
            var artifact = new JsonObject { ["formatVersion"] = 1, ["authoringSha256"] = toolHash, ["coreSha256"] = coreHash, ["entries"] = entries };
            return artifact.ToJsonString().Length <= 1048576 ? artifact : null;
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or ArgumentException or InvalidOperationException or JsonException or BuildError or TimeoutException or System.ComponentModel.Win32Exception or NullReferenceException)
        { return null; }
    }
}
