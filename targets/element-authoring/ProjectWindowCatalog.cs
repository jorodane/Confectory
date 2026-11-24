using Confectory.Core;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

internal static class ProjectWindowCatalog
{
    internal static JsonObject Query(string project, string? requestedId, Func<string, string> scope,
        JsonObject? setting = null, bool main = false)
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

        JsonObject? Project(Element declaration, string? renderer = null)
        {
            if (!declaration.Values.TryGetValue("editorName", out var name) || name.Value.ValueKind != JsonValueKind.String ||
                name.Value.GetString() is not { Length: > 0 and <= 160 } title || string.IsNullOrWhiteSpace(title))
                return null;
            if (declaration.Uses.Count != 1 || declaration.Uses[0].Kind != "object") return null;
            var target = Owned(declaration.Uses[0].Id, "object");
            if (target is null) return null;
            if (renderer == RecipeRenderer)
            {
                var recipe = ReadRecipe(target, id => Owned(id, "object") is not null);
                if (recipe is null) return null;
                var projected = new JsonObject { ["id"] = declaration.Id, ["title"] = title };
                if (requestedId is not null)
                {
                    projected["recipe"] = recipe;
                    projected["editId"] = target.Id;
                }
                return projected;
            }
            if (target.Uses.Count != 1 || target.Uses[0].Kind != "schema") return null;
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
            if (main || requestedId is not null)
            {
                window["field"] = key;
                window["value"] = text;
            }
            return window;
        }

        JsonObject? ConfirmedWindow(string id)
        {
            var declaration = Owned(id, "view");
            if (declaration is null || Renderer(declaration, recipeMenu: true) is not { Length: > 0 } renderer)
                return null;
            var window = Project(declaration, renderer);
            if (requestedId is not null && window is not null) window["renderer"] = renderer;
            return window;
        }

        Element?[]? RegisteredViews()
        {
            var views = manifest.Elements.Where(row => row.Value.Kind == "view").Take(maxViews + 1).ToArray();
            return views.Length <= maxViews ? views.Select(row => Owned(prefix + row.Key, "view")).ToArray() : null;
        }

        Element? OtherOpeningView(string id, Element?[] views) =>
            views.FirstOrDefault(view => view is not null && view.Id != id &&
                Renderer(view, "editorMain") is { Length: > 0 });

        JsonObject ValidateOpeningAssignment(string id)
        {
            var prior = new Parser(setting!["original"]!.GetValue<string>(), "<opening-view-original>").ParseElement();
            var draft = new Parser(setting["text"]!.GetValue<string>(), "<opening-view-draft>").ParseElement();
            if (JsonNode.DeepEquals(MainValue(prior), MainValue(draft)) || !draft.Values.ContainsKey("editorMain"))
                return new JsonObject { ["status"] = "available" };
            if (draft.Id != id || draft.Kind != "view" || Owned(id, "view") is null ||
                Renderer(draft, "editorMain") is not { Length: > 0 } || Project(draft) is null ||
                RegisteredViews() is not { } views)
                throw new ArgumentException("Use one directly owned, supported project opening View.");
            if (OtherOpeningView(id, views) is { } conflict)
                throw new ArgumentException($"First clear and confirm the opening View {conflict.Id}.");
            var checks = new JsonArray();
            foreach (var (path, value) in observed)
                checks.Add(new JsonObject { ["path"] = path, ["hash"] =
                    Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(value)).ToLowerInvariant() });
            return new JsonObject { ["status"] = "available", ["assignment"] = true, ["checks"] = checks };
        }

        static JsonNode? MainValue(Element view) => view.Values.TryGetValue("editorMain", out var value)
            ? JsonNode.Parse(value.Value.GetRawText()) : null;

        JsonObject? EditSetting(string id)
        {
            bool mainSetting = setting!["placement"]?.GetValue<string>() == "main";
            string property = mainSetting ? "editorMain" : "editorWindow";
            bool recipeMenu = !mainSetting;
            var confirmed = Owned(id, "view");
            if (confirmed is null || (!mainSetting && Renderer(confirmed, recipeMenu: recipeMenu) is null))
                return null;
            bool card = Project(confirmed) is not null;
            bool recipe = recipeMenu && Project(confirmed, RecipeRenderer) is not null;
            if (!card && !recipe)
                return null;
            string text = setting!["text"]!.GetValue<string>();
            if (text.Length > maxDocumentBytes) return null;
            var draft = new Parser(text, "<project-window-draft>").ParseElement();
            if (draft.Id != id || draft.Kind != "view" || draft.Parent is not null ||
                Renderer(draft, property, recipeMenu) is not { } current)
                return null;
            card = card && Project(draft) is not null;
            recipe = recipe && Project(draft, RecipeRenderer) is not null;
            bool Allowed(string value) => value == "" ||
                (value == RecipeRenderer ? recipe : card && Supported(value));
            if ((!card && !recipe) || !Allowed(current)) return null;
            var result = new JsonObject { ["status"] = "available", ["renderer"] = current };
            if (recipe)
                result["choices"] = card
                    ? new JsonArray("", "element-view-card", "element-view-table", RecipeRenderer)
                    : new JsonArray("", RecipeRenderer);
            if (mainSetting)
            {
                var views = RegisteredViews();
                if (views is null) return null;
                var conflict = OtherOpeningView(id, views);
                if (conflict is not null) result["conflict"] = conflict.Id;
            }
            if (setting["renderer"] is { } choice)
            {
                string next = choice.GetValue<string>();
                if (!Allowed(next)) return null;
                if (next.Length != 0 && result["conflict"] is not null)
                    return new JsonObject { ["status"] = "conflict", ["conflict"] = result["conflict"]!.DeepClone() };
                result["text"] = next == current ? text : ReplaceSetting(text, draft, property, next);
            }
            return result;
        }

        // Resolve the exact requested ID again on open. Menu discovery is bounded and
        // reads only direct declarations in the current manifest.
        JsonObject? opened = requestedId is null ? null :
            setting is null ? ConfirmedWindow(requestedId) :
            setting["action"]?.ToString() == "validate-project-main-view" ? ValidateOpeningAssignment(requestedId) : EditSetting(requestedId);
        var windows = new JsonArray();
        if (main)
        {
            // Refuse ambiguous assignments, including assignments beyond the discovery budget.
            if (RegisteredViews() is { } views)
            {
                var declared = views
                    .Where(view => view?.Values.ContainsKey("editorMain") == true).ToArray();
                if (declared.Length == 1 &&
                    declared[0]!.Values["editorMain"].Value is { ValueKind: JsonValueKind.String } choice &&
                    choice.GetString() is "element-view-card" or "element-view-table")
                {
                    opened = Project(declared[0]!);
                    if (opened is not null) opened["renderer"] = choice.GetString();
                }
            }
        }
        else if (requestedId is null)
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
                catch (JsonException) { /* Malformed recipe metadata grants no menu entry. */ }
            }
        }
        foreach (var (path, value) in observed)
            if (!ReadCurrent(path).AsSpan().SequenceEqual(value))
                throw new IOException("Project window source changed during discovery.");

        if (setting is not null) return opened ?? new JsonObject { ["status"] = "unavailable" };
        return !main && requestedId is null ? new JsonObject { ["status"] = "available", ["windows"] = windows } :
            opened is null ? new JsonObject { ["status"] = "unavailable" } :
            new JsonObject { ["status"] = "available", ["window"] = opened };
    }

    private const string RecipeRenderer = "element-view-recipe";

    private static bool Supported(string value) => value is "" or "element-view-card" or "element-view-table";

    // An absent property is the existing opt-out. Unknown values are outside this editor's contract.
    private static string? Renderer(Element view, string property = "editorWindow", bool recipeMenu = false)
    {
        if (!view.Values.TryGetValue(property, out var value)) return "";
        return value.Value.ValueKind == JsonValueKind.String &&
            value.Value.GetString() is { Length: > 0 } renderer && (Supported(renderer) || recipeMenu && renderer == RecipeRenderer) ? renderer : null;
    }

    // Read the existing Recipe metadata without creating a runtime or touching stock.
    private static JsonObject? ReadRecipe(Element target, Func<string, bool> ownsResource)
    {
        if (target.Values.GetValueOrDefault("concept")?.Value is not { ValueKind: JsonValueKind.String } concept ||
            concept.GetString() != "recipe" ||
            target.Values.GetValueOrDefault("ingredients")?.Value is not { ValueKind: JsonValueKind.String } input ||
            input.GetString() is not { Length: > 0 and <= 8192 } ingredients ||
            target.Values.GetValueOrDefault("output")?.Value is not { ValueKind: JsonValueKind.String } output ||
            output.GetString() is not { Length: > 0 and <= 512 } outputId ||
            target.Values.GetValueOrDefault("outputCount")?.Value is not { ValueKind: JsonValueKind.Number } count ||
            !count.TryGetInt32(out int outputCount) || outputCount is <1 or >100)
            return null;

        using var document = JsonDocument.Parse(ingredients);
        if (document.RootElement.ValueKind != JsonValueKind.Object) return null;
        var rows = new JsonArray();
        var ids = new HashSet<string>(StringComparer.Ordinal);
        foreach (var row in document.RootElement.EnumerateObject())
        {
            if (rows.Count == 16 || row.Name.Length is <1 or >512 || !ids.Add(row.Name) ||
                row.Value.ValueKind != JsonValueKind.Number || !row.Value.TryGetInt32(out int amount) ||
                amount is <1 or >100 || !ownsResource(row.Name)) return null;
            rows.Add(new JsonObject { ["id"] = row.Name, ["count"] = amount });
        }
        if (rows.Count == 0 || !ownsResource(outputId)) return null;
        return new JsonObject { ["ingredients"] = rows,
            ["output"] = new JsonObject { ["id"] = outputId, ["count"] = outputCount } };
    }

    private static string ReplaceSetting(string text, Element draft, string property, string renderer)
    {
        const string trivia = @"(?:\s|//[^\n]*)*";
        string literal = JsonSerializer.Serialize(renderer);
        if (!draft.Values.TryGetValue(property, out var previous))
        {
            var closing = Regex.Match(text, @"\}" + trivia + @"\z", RegexOptions.NonBacktracking);
            if (!closing.Success) throw new InvalidOperationException("Missing View terminator.");
            return text.Insert(closing.Index, "value " + property + " = " + literal + "; ");
        }

        // The parsed location identifies the exact statement even if its spelling occurs in comments or strings.
        int offset = 0;
        for (int line = 1; line < previous.Loc.Line; line++) offset = text.IndexOf('\n', offset) + 1;
        offset += previous.Loc.Column - 1;
        string gap = property == "editorMain" ? "(?<gap>" + trivia + ")" : trivia;
        var clause = new Regex(@"\Gvalue" + gap + property + gap + "=" + gap +
            "(?<literal>\"(?:[^\"\\\\]|\\\\.)*\")" + gap + ";").Match(text, offset);
        if (!clause.Success) throw new InvalidOperationException("Missing View menu setting.");
        var span = renderer.Length == 0 ? clause : clause.Groups["literal"];
        string replacement = renderer.Length == 0
            ? string.Concat(clause.Groups["gap"].Captures.Where(g => g.Value.Contains("//", StringComparison.Ordinal)).Select(g => g.Value))
            : literal;
        return text.Remove(span.Index, span.Length).Insert(span.Index, replacement);
    }
}
