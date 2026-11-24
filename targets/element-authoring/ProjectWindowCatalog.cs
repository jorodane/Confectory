using Confectory.Core;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

internal static class ProjectWindowCatalog
{
    internal static JsonObject Query(string project, string? requestedId, Func<string, string> scope,
        JsonObject? setting = null)
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

        JsonObject? Project(Element declaration)
        {
            if (!declaration.Values.TryGetValue("editorName", out var name) || name.Value.ValueKind != JsonValueKind.String ||
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
            var window = new JsonObject { ["id"] = declaration.Id, ["title"] = title };
            if (requestedId is not null)
            {
                window["field"] = key;
                window["value"] = text;
            }
            return window;
        }

        JsonObject? ConfirmedWindow(string id)
        {
            var declaration = Owned(id, "view");
            if (declaration is null || Renderer(declaration) is not { Length: > 0 } renderer)
                return null;
            var window = Project(declaration);
            if (requestedId is not null && window is not null) window["renderer"] = renderer;
            return window;
        }

        JsonObject? EditSetting(string id)
        {
            var confirmed = Owned(id, "view");
            if (confirmed is null || Renderer(confirmed) is null || Project(confirmed) is null)
                return null;
            string text = setting!["text"]!.GetValue<string>();
            if (text.Length > maxDocumentBytes) return null;
            var draft = new Parser(text, "<project-window-draft>").ParseElement();
            if (draft.Id != id || draft.Kind != "view" || draft.Parent is not null ||
                Renderer(draft) is not { } current || Project(draft) is null)
                return null;
            var result = new JsonObject { ["status"] = "available", ["renderer"] = current };
            if (setting["renderer"] is { } choice)
            {
                string next = choice.GetValue<string>();
                if (!Supported(next)) return null;
                result["text"] = next == current ? text : ReplaceSetting(text, draft, next);
            }
            return result;
        }

        // Resolve the exact requested ID again on open. Menu discovery is bounded and
        // reads only direct declarations in the current manifest.
        JsonObject? opened = requestedId is null ? null :
            setting is null ? ConfirmedWindow(requestedId) : EditSetting(requestedId);
        var windows = new JsonArray();
        if (requestedId is null)
        {
            foreach (var (name, _) in manifest.Elements.Where(row => row.Value.Kind == "view")
                         .OrderBy(row => row.Key, StringComparer.Ordinal).Take(maxViews))
            {
                try
                {
                    if (ConfirmedWindow(prefix + name) is { } row) windows.Add(row);
                }
                catch (BuildError) { /* An unavailable declaration grants no menu entry. */ }
                catch (IOException) { /* A removed declaration grants no menu entry. */ }
            }
        }
        foreach (var (path, value) in observed)
            if (!ReadCurrent(path).AsSpan().SequenceEqual(value))
                throw new IOException("Project window source changed during discovery.");

        if (setting is not null) return opened ?? new JsonObject { ["status"] = "unavailable" };
        return requestedId is null ? new JsonObject { ["status"] = "available", ["windows"] = windows } :
            opened is null ? new JsonObject { ["status"] = "unavailable" } :
            new JsonObject { ["status"] = "available", ["window"] = opened };
    }

    private static bool Supported(string value) => value is "" or "element-view-card" or "element-view-table";

    // An absent property is the existing opt-out. Unknown values are outside this editor's contract.
    private static string? Renderer(Element view)
    {
        if (!view.Values.TryGetValue("editorWindow", out var value)) return "";
        return value.Value.ValueKind == JsonValueKind.String &&
            value.Value.GetString() is { Length: > 0 } renderer && Supported(renderer) ? renderer : null;
    }

    private static string ReplaceSetting(string text, Element draft, string renderer)
    {
        const string trivia = @"(?:\s|//[^\n]*)*";
        string literal = JsonSerializer.Serialize(renderer);
        if (!draft.Values.TryGetValue("editorWindow", out var previous))
        {
            var closing = Regex.Match(text, @"\}" + trivia + @"\z", RegexOptions.NonBacktracking);
            if (!closing.Success) throw new InvalidOperationException("Missing View terminator.");
            return text.Insert(closing.Index, "value editorWindow = " + literal + "; ");
        }

        // The parsed location identifies the exact statement even if its spelling occurs in comments or strings.
        int offset = 0;
        for (int line = 1; line < previous.Loc.Line; line++) offset = text.IndexOf('\n', offset) + 1;
        offset += previous.Loc.Column - 1;
        var clause = new Regex(@"\Gvalue" + trivia + "editorWindow" + trivia + "=" + trivia +
            "(?<literal>\"(?:[^\"\\\\]|\\\\.)*\")" + trivia + ";").Match(text, offset);
        if (!clause.Success) throw new InvalidOperationException("Missing View menu setting.");
        var span = renderer.Length == 0 ? clause : clause.Groups["literal"];
        return text.Remove(span.Index, span.Length).Insert(span.Index, renderer.Length == 0 ? "" : literal);
    }
}
