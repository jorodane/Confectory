using Confectory.Core;
using System.Text.Json;
using System.Text.Json.Nodes;

internal static class ProjectWindowCatalog
{
    internal static JsonObject Query(string project, string? requestedId, Func<string, string> scope)
    {
        const int maxViews = 32;
        const int maxDocumentBytes = 1048576;
        project = PackPaths.Resolve(project);
        string root = Path.GetDirectoryName(project)!;
        Dictionary<string, byte[]> observed = new(StringComparer.Ordinal);
        int bytes = 0;

        byte[] Read(string path)
        {
            if (observed.TryGetValue(path, out var existing)) return existing;
            byte[] value = ReadCurrent(path);
            bytes += value.Length;
            if (observed.Count >= 1 + maxViews * 3 || bytes > 4194304)
                throw new ArgumentException("Project window declaration budget exceeded.");
            observed.Add(path, value);
            return value;
        }

        byte[] ReadCurrent(string path)
        {
            string relative = Path.GetRelativePath(root, path);
            if (Path.IsPathRooted(relative) || relative == ".." ||
                relative.StartsWith(".." + Path.DirectorySeparatorChar, StringComparison.Ordinal))
                throw new ArgumentException("Project window must use an owned declaration.");
            using var stream = File.OpenRead(scope(path));
            if (stream.Length > maxDocumentBytes) throw new ArgumentException("Project window declaration too large.");
            byte[] data = new byte[(int)stream.Length];
            stream.ReadExactly(data);
            if (stream.ReadByte() != -1) throw new IOException("Project window declaration changed.");
            return data;
        }

        var documents = new Documents("", new BuildStatistics(), Read);
        var manifest = documents.Manifest(project);
        string prefix = manifest.Namespace + "::";
        Element? Owned(string id, string kind)
        {
            if (!id.StartsWith(prefix, StringComparison.Ordinal) ||
                !manifest.Elements.TryGetValue(id[prefix.Length..], out var locator) || locator.Kind != kind)
                return null;
            var element = documents.Element(PackPaths.Owned(root, locator.Path));
            return element.Id == id && element.Kind == kind && element.Parent is null ? element : null;
        }

        JsonObject? Project(string id)
        {
            var declaration = Owned(id, "view");
            if (declaration is null || !declaration.Values.TryGetValue("editorWindow", out var choice) ||
                choice.Value.ValueKind != JsonValueKind.String ||
                choice.Value.GetString() is not ("element-view-card" or "element-view-table") ||
                !declaration.Values.TryGetValue("editorName", out var name) || name.Value.ValueKind != JsonValueKind.String ||
                name.Value.GetString() is not { Length: > 0 and <= 160 } title || string.IsNullOrWhiteSpace(title))
                return null;
            if (declaration.Uses.Count != 1 || declaration.Uses[0].Kind != "object") return null;
            var target = Owned(declaration.Uses[0].Id, "object");
            if (target is null || target.Uses.Count != 1 || target.Uses[0].Kind != "schema") return null;
            var schema = Owned(target.Uses[0].Id, "schema");
            // Initial projection borrows one explicitly declared field and value.
            if (schema is null || schema.Fields.Count != 1) return null;
            var (key, field) = schema.Fields.Single();
            if (field is not { Cardinality: "single", Kind: "general", Type: "string" } ||
                !target.Data.TryGetValue(key, out var datum) || datum.Kind != "general" ||
                datum.Scalar is not { ValueKind: JsonValueKind.String } value ||
                value.GetString() is not { Length: <= 4096 } text)
                return null;
            var window = new JsonObject { ["id"] = id, ["title"] = title };
            if (requestedId is not null)
            {
                window["renderer"] = choice.Value.GetString();
                window["field"] = key;
                window["value"] = text;
            }
            return window;
        }

        // Resolve the exact requested ID again on open. Menu discovery is bounded and
        // reads only direct declarations in the current manifest.
        JsonObject? opened = requestedId is null ? null : Project(requestedId);
        var windows = new JsonArray();
        if (requestedId is null)
        {
            foreach (var (name, _) in manifest.Elements.Where(row => row.Value.Kind == "view")
                         .OrderBy(row => row.Key, StringComparer.Ordinal).Take(maxViews))
            {
                try
                {
                    if (Project(prefix + name) is { } row) windows.Add(row);
                }
                catch (BuildError) { /* An unavailable declaration grants no menu entry. */ }
                catch (IOException) { /* A removed declaration grants no menu entry. */ }
            }
        }
        foreach (var (path, value) in observed)
            if (!ReadCurrent(path).AsSpan().SequenceEqual(value))
                throw new IOException("Project window source changed during discovery.");

        return requestedId is null ? new JsonObject { ["status"] = "available", ["windows"] = windows } :
            opened is null ? new JsonObject { ["status"] = "unavailable" } :
            new JsonObject { ["status"] = "available", ["window"] = opened };
    }
}
