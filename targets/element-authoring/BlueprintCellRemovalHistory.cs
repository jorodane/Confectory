using Confectory.Core;
using System.Text;
using System.Text.Json.Nodes;

// The retained record is a read dependency only. The graph is the sole source
// this operation can edit. Never create an owned locator from history metadata.
internal static class BlueprintCellRemovalHistory
{
    static string S(JsonNode row, string key) => row[key]!.GetValue<string>();
    static string Digest(string text) => JsonData.HashBytes(Encoding.UTF8.GetBytes(text));
    static void Need(bool valid, string message)
    {
        if (!valid) throw new InvalidOperationException(message);
    }

    sealed record RetainedSource(string Id, string Path);

    static RetainedSource[] RetainedSources(JsonNode receipt)
    {
        if (receipt["version"]?.GetValue<int>() is 1 or 3)
            return [new(BlueprintTree.SourceId(S(receipt, "graph"), S(receipt, "node")), S(receipt, "source"))];

        Need(receipt["version"]?.GetValue<int>() == 2 &&
            receipt["sources"] is JsonArray { Count: > 0 and < 64 },
            "Exact compound source membership required");
        return receipt["sources"]!.AsArray().Select(row => {
            Need(row is JsonObject { Count: 2 }, "Qualified cell source identity and path required");
            return new RetainedSource(S(row!, "id"), S(row!, "path"));
        }).ToArray();
    }

    static void Transition(JsonNode entry)
    {
        var receipt = entry["cellRemoval"]!.AsObject();
        Need(receipt.Count == 7 && entry["units"] is JsonArray { Count: 1 },
            "Exact retained cell history required");
        var retained = RetainedSources(receipt);
        var graph = entry["units"]![0]!.AsObject();
        Need(S(graph, "kind") == "blueprint" && S(graph, "id") == S(receipt, "graph") &&
            !S(graph, "id").Contains("/graph:", StringComparison.Ordinal) && graph["hierarchyVersion"] is null,
            "Only the original physical root may be restored");
        string prior = S(graph, "before"), next = S(graph, "after");
        Need(Digest(prior) == S(receipt, "beforeHash") && Digest(next) == S(receipt, "afterHash"),
            "The exact saved root text is required");
        var before = JsonNode.Parse(prior)!.AsObject();
        var after = JsonNode.Parse(next)!.AsObject();
        BlueprintDocuments.Validate(S(graph, "id"), "blueprint", S(graph, "before"));
        BlueprintDocuments.Validate(S(graph, "id"), "blueprint", S(graph, "after"));
        string id = S(receipt, "node");
        Need(JsonNode.DeepEquals(after, BlueprintCellRemoval.Remove(before, id)),
            "Cell history may only restore its exact original nodes and connections");
        var keys = BlueprintCellRemoval.SourceKeys(before, id);
        bool childCase = BlueprintCellRemoval.IsChildCase(before, id);
        Need((childCase ? 3 : keys[0] == id ? 1 : 2) == receipt["version"]!.GetValue<int>() &&
            retained.Select(source => source.Id).SequenceEqual(keys.Select(key => BlueprintTree.SourceId(S(receipt, "graph"), key)),
                StringComparer.Ordinal), "Exact retained source membership required");
        var guards = receipt["proof"]!.AsObject();
        int sourceCount = childCase ? BlueprintTree.Nodes(before).Count(member =>
            member.Node["kind"]?.ToString() == "code" && member.Node["implementation"] is not null) : retained.Length;
        Need(guards.Count == 3 + sourceCount && guards.Count <= 96 &&
            retained.All(source => guards.ContainsKey(source.Path)) &&
            guards.All(pair => pair.Value is JsonValue hash &&
            hash.TryGetValue<string>(out string? value) && value is { Length: 64 } &&
            value.All(character => char.IsAsciiHexDigitLower(character))),
            "Bounded source ownership hashes required");
    }

    sealed class Observation(string project)
    {
        readonly string root = Path.GetDirectoryName(Path.GetFullPath(project))!;
        readonly StringComparer paths = OperatingSystem.IsWindows() ? StringComparer.OrdinalIgnoreCase : StringComparer.Ordinal;
        readonly Dictionary<string, (string Hash, string Text)> observed = new(
            OperatingSystem.IsWindows() ? StringComparer.OrdinalIgnoreCase : StringComparer.Ordinal);
        int bytes;

        public string Full(string relative)
        {
            Need(!Path.IsPathRooted(relative), "Project-relative cell source required");
            string full = Path.GetFullPath(Path.Combine(root, relative));
            Need(paths.Equals(relative, Path.GetRelativePath(root, full)), "Canonical owned cell path required");
            for (FileSystemInfo? item = new FileInfo(full); item is not null;
                 item = item is FileInfo file ? file.Directory : ((DirectoryInfo)item).Parent) {
                Need(item.LinkTarget is null, "Cell sources cannot traverse links");
                if (paths.Equals(item.FullName, root)) break;
            }
            Need(paths.Equals(full, PackPaths.Owned(root, relative)), "Owned cell path required");
            return full;
        }

        public string Relative(string full) => Path.GetRelativePath(root, full);

        public string Read(string path)
        {
            if (observed.TryGetValue(path, out var existing)) return existing.Text;
            var file = new FileInfo(Full(path));
            Need(file.Exists && file.Length <= 2_097_152 && observed.Count < 96, "Bounded existing cell sources required");
            byte[] raw = File.ReadAllBytes(file.FullName);
            bytes = checked(bytes + raw.Length);
            Need(bytes <= 16_777_216, "Cell ownership observations exceed their budget");
            using var reader = new StreamReader(new MemoryStream(raw), new UTF8Encoding(false, true), true);
            string text = reader.ReadToEnd();
            observed.Add(path, (JsonData.HashBytes(raw), text));
            return text;
        }

        public string Hash(string path) { Read(path); return observed[path].Hash; }
        public bool Same(string a, string b) => paths.Equals(a.Replace(Path.AltDirectorySeparatorChar, Path.DirectorySeparatorChar),
            b.Replace(Path.AltDirectorySeparatorChar, Path.DirectorySeparatorChar));
        public void Writable(string path)
        {
            string full = Full(path);
            Need((File.GetAttributes(full) & FileAttributes.ReadOnly) == 0 &&
                (OperatingSystem.IsWindows() || (File.GetUnixFileMode(full) &
                    (UnixFileMode.UserWrite | UnixFileMode.GroupWrite | UnixFileMode.OtherWrite)) != 0),
                "The cell and its containing root must be writable");
        }

        public IEnumerable<KeyValuePair<string, (string Hash, string Text)>> Reads => observed;
    }

    static JsonArray Observe(JsonObject request, JsonNode entry, bool prepare, out JsonArray verifiedLocators,
        bool checkingChildDraftBlocker = false, bool published = false)
    {
        var receipt = entry["cellRemoval"]!.AsObject();
        var edited = entry["units"]![0]!;
        string graphId = S(receipt, "graph"), graphPath = S(edited, "path");
        var retained = RetainedSources(receipt);
        string project = S(request, "project");
        var files = new Observation(project);
        var manifestPath = Path.GetFileName(project);
        var manifest = new Parser(files.Read(manifestPath), project).ParseManifest();
        var units = request["units"]!.AsObject();
        Need(manifest.Namespace == S(request, "namespace") && manifest.Kind == "project", "Direct project ownership required");
        var graphUnit = units[graphId]!;
        Need(graphUnit?["path"]?.ToString() == graphPath && graphUnit["kind"]?.ToString() == "blueprint",
            "Existing owned root locator required");
        string onDisk = files.Read(graphPath);
        string expected = S(graphUnit!, published ? "draft" : "original");
        string expectedHash = published ? Digest(expected) : S(graphUnit!, "baseline");
        Need(onDisk == expected && files.Hash(graphPath) == expectedHash &&
            (onDisk == S(edited, "before") || !prepare && onDisk == S(edited, "after")),
            "The original Blueprint connections changed");
        int marker = graphId.IndexOf("/body:", StringComparison.Ordinal);
        Need(marker > 0, "Root implementation body required");
        string implementation = graphId[..marker], target = graphId[(marker+6)..];
        string feature = S(JsonNode.Parse(S(edited, "before"))!, "feature");
        string Declaration(string id, string kind)
        {
            string prefix = manifest.Namespace + "::";
            Need(id.StartsWith(prefix, StringComparison.Ordinal) && manifest.Elements.ContainsKey(id[prefix.Length..]),
                "Current direct declaration ownership required");
            var locator = manifest.Elements[id[prefix.Length..]];
            string path = files.Relative(files.Full(locator.Path.Replace(Path.AltDirectorySeparatorChar, Path.DirectorySeparatorChar)));
            Need(locator.Kind == kind && units[id]?["path"]?.ToString() == path,
                "The original owned declaration locator changed");
            return path;
        }
        string implementationPath = Declaration(implementation, "implementation");
        string functionPath = Declaration(feature, "function");
        var owner = new Parser(files.Read(implementationPath), files.Full(implementationPath)).ParseElement();
        var function = new Parser(files.Read(functionPath), files.Full(functionPath)).ParseElement();
        Need(owner.Id == implementation && owner.Kind == "implementation" && owner.Parent is null &&
            owner.Function == feature && function.Id == feature && function.Kind == "function" &&
            owner.Bodies.TryGetValue(target, out var body) && body.SourceKind == "blueprint" &&
            body.Origin == implementation && files.Same(body.Path, graphPath),
            "The original direct root ownership changed");
        var prior = BlueprintDocuments.NodeUnits(Path.GetDirectoryName(project)!, files.Full(graphPath), graphId, S(edited, "before"));
        var byId = retained.ToDictionary(source => source.Id, StringComparer.Ordinal);
        bool Retains(string path) => retained.Any(source => files.Same(source.Path, path));
        files.Writable(graphPath);
        var proof = new JsonObject();
        foreach (string path in new[] { manifestPath, functionPath, implementationPath }) proof.Add(path, files.Hash(path));
        var resolved = new JsonArray();
        foreach (var source in retained) {
            var locator = prior.SingleOrDefault(row => S(row!, "id") == source.Id);
            Need(locator is not null && files.Same(S(locator, "path"), source.Path) &&
                !files.Same(graphPath, source.Path), "An original cell source locator changed");
            files.Writable(source.Path);
            BlueprintDocuments.Validate(source.Id, "blueprint-node", files.Read(source.Path));
            proof.Add(source.Path, files.Hash(source.Path));
            resolved.Add(locator!.DeepClone());
        }
        bool childCase = receipt["version"]!.GetValue<int>() == 3;
        if (childCase) {
            // Keep the original frame and sibling code observation across cold
            // Save, Confirm and Undo. Read checks never grant source writes.
            foreach (var locator in prior) {
                string sourceId = S(locator!, "id"), path = S(locator!, "path");
                string hash = files.Hash(path);
                proof.TryAdd(path, JsonValue.Create(hash));
                if (prepare)
                    Need(units[sourceId] is JsonObject unit && S(unit, "path") == path &&
                        S(unit, "baseline") == hash, "An observed Blueprint body source changed");
            }
            if (prepare)
                Need(S(units[implementation]!, "baseline") == files.Hash(implementationPath) &&
                    S(units[feature]!, "baseline") == files.Hash(functionPath) &&
                    units.Any(pair => pair.Value?["kind"]?.ToString() == "project" &&
                        pair.Value["path"]?.ToString() == manifestPath &&
                        pair.Value["baseline"]?.ToString() == files.Hash(manifestPath)),
                    "An observed Blueprint declaration or project changed");
        }
        if (prepare) receipt["proof"] = proof;
        else Need(JsonNode.DeepEquals(proof, receipt["proof"]), "The retained C# sources or their owner changed; no changes applied");

        // A separate root or body cannot claim either of these paths. The
        // inspected registrations and graphs enter the same final CAS lease.
        foreach (var registration in manifest.Registry.Values) {
            string pack = PackPaths.Resolve(Path.Combine(Path.GetDirectoryName(project)!, registration.Path));
            foreach (var source in retained) {
                string relative = Path.GetRelativePath(Path.GetDirectoryName(pack)!, files.Full(source.Path));
                Need(Path.IsPathRooted(relative) || relative == ".." ||
                    relative.StartsWith(".." + Path.DirectorySeparatorChar, StringComparison.Ordinal),
                    "Cell source overlaps another registered pack's ownership");
            }
        }
        foreach (var declaration in manifest.Elements.Values) {
            Need(!files.Same(declaration.Path, graphPath) && !Retains(declaration.Path),
                "The graph or retained source aliases a declaration");
            if (declaration.Kind != "implementation") continue;
            string headerPath = declaration.Path.Replace(Path.AltDirectorySeparatorChar, Path.DirectorySeparatorChar);
            var header = new Parser(files.Read(headerPath), files.Full(headerPath)).ParseElement();
            Need(header.Kind == "implementation" && header.Id.StartsWith(manifest.Namespace+"::", StringComparison.Ordinal),
                "Owned implementation declaration required");
            foreach (var candidate in header.Bodies) {
                bool sameBody = header.Id == implementation && candidate.Key == target;
                string path = candidate.Value.Path;
                Need(sameBody || !files.Same(graphPath, path), "Shared root is outside cell removal scope");
                Need(!Retains(path), "Shared cell source is outside cell removal scope");
                if (sameBody || candidate.Value.SourceKind != "blueprint") continue;
                string relativeGraph = path.Replace(Path.AltDirectorySeparatorChar, Path.DirectorySeparatorChar);
                foreach (var locator in BlueprintDocuments.NodeUnits(Path.GetDirectoryName(project)!, files.Full(relativeGraph),
                             header.Id + "/body:" + candidate.Key, files.Read(relativeGraph)))
                    Need(!Retains(S(locator!, "path")) && !files.Same(graphPath, S(locator!, "path")),
                        "Another Blueprint claims the original graph or cell source");
            }
        }
        var physical = BlueprintDocuments.NodeUnits(Path.GetDirectoryName(project)!, files.Full(graphPath), graphId, onDisk);
        Need(physical.All(row => !files.Same(S(row!, "path"), graphPath) &&
            (!Retains(S(row!, "path")) || byId.TryGetValue(S(row!, "id"), out var source) &&
                files.Same(source.Path, S(row!, "path")))), "Cell source paths must be distinct");
        foreach (var row in prior) files.Read(S(row!, "path"));

        foreach (var member in units) {
            var unit = member.Value!;
            string path = S(unit, "path");
            if (byId.TryGetValue(member.Key, out var source))
                Need(S(unit, "kind") == "blueprint-node" && files.Same(source.Path, path),
                    "A retained cell identity now belongs to another locator");
            else if (receipt["version"]?.GetValue<int>() is 2 or 3)
                Need(!Retains(path), "A retained cell path now belongs to another locator");
            if (member.Key == graphId || unit["draft"] is null || JsonNode.DeepEquals(unit["draft"], unit["original"])) continue;
            if (checkingChildDraftBlocker && byId.ContainsKey(member.Key)) continue;
            Need(!files.Reads.Any(read => files.Same(read.Key, S(unit, "path"))),
                "Resolve other pending ownership or source changes before applying the cell edit");
        }
        verifiedLocators = resolved;
        return new JsonArray(files.Reads.Select(row => (JsonNode)new JsonObject {
            ["path"] = row.Key, ["hash"] = row.Value.Hash
        }).ToArray());
    }

    public static JsonObject Query(JsonObject request)
    {
        string action = S(request, "action");
        if (action == "options") {
            var graph = request["graph"]!.AsObject();
            string frame = request["path"]?.GetValue<string>() ?? "";
            var nodes = BlueprintCellRemoval.Options(graph, frame);
            var sources = new JsonObject();
            foreach (string id in nodes) {
                string qualified = frame.Length == 0 ? id : frame + "/" + id;
                sources[id] = System.Text.Json.JsonSerializer.SerializeToNode(BlueprintCellRemoval.SourceKeys(graph, qualified));
            }
            return new() { ["nodes"] = System.Text.Json.JsonSerializer.SerializeToNode(nodes), ["sources"] = sources };
        }
        if (action == "validate") { Transition(request["entry"]!); return new(); }
        if (action == "entry") {
            var entry = request["entry"]!;
            Transition(entry);
            var checks = Observe(request, entry, false, out var locators);
            return new() { ["checks"] = checks, ["locators"] = locators,
                ["locator"] = entry["cellRemoval"]!["version"]!.GetValue<int>() != 2 ? locators[0]!.DeepClone() : null };
        }
        var units = request["units"]!.AsObject();
        if (action is "prepare" or "checkChildDraftBlocker") {
            bool checkingChildDraftBlocker = action == "checkChildDraftBlocker";
            string id = S(request, "id"), node = S(request, "node");
            var graph = units[id]!;
            string before = S(graph, "draft");
            Need(before == S(graph, "original") && graph["cellRemovalPending"] is null &&
                new[] { "propertyObservations", "atomicEditGroup", "rootContractGroup", "nodeFlowOrigin",
                    "hierarchyGroup", "retirementGroup", "conversionOrigin" }.All(field => graph[field] is null),
                "Confirm pending source changes before removing a cell");
            var original = JsonNode.Parse(before)!.AsObject();
            string after = BlueprintCellRemoval.Remove(original, node).ToJsonString();
            var keys = BlueprintCellRemoval.SourceKeys(original, node);
            bool compound = keys[0] != node;
            bool hasChildDraft = false;
            var retained = new JsonArray();
            foreach (string key in keys) {
                string leafId = BlueprintTree.SourceId(id, key);
                var leaf = units[leafId];
                bool dirty = !JsonNode.DeepEquals(leaf?["draft"], leaf?["original"]);
                Need(leaf?["kind"]?.ToString() == "blueprint-node" && leaf["baseline"]?.ToString() != "missing" &&
                    (!dirty || checkingChildDraftBlocker && compound), "An existing clean cell source is required");
                hasChildDraft |= dirty;
                retained.Add(new JsonObject { ["id"] = leafId, ["path"] = S(leaf!, "path") });
            }
            if (checkingChildDraftBlocker)
                Need(compound && hasChildDraft, "An existing compound child draft is required");
            var entry = new JsonObject {
                ["id"] = Guid.NewGuid().ToString("N"), ["label"] = "source-edit",
                ["units"] = new JsonArray(new JsonObject {
                    ["id"] = id, ["kind"] = "blueprint", ["path"] = S(graph, "path"), ["before"] = before, ["after"] = after
                }),
                ["cellRemoval"] = new JsonObject {
                    ["version"] = compound ? 2 : BlueprintCellRemoval.IsChildCase(original, node) ? 3 : 1,
                    ["graph"] = id, ["node"] = node,
                    ["beforeHash"] = Digest(before), ["afterHash"] = Digest(after)
                }
            };
            var receipt = entry["cellRemoval"]!.AsObject();
            if (compound) receipt["sources"] = retained;
            else receipt["source"] = retained[0]!["path"]!.DeepClone();
            Observe(request, entry, true, out var locators, checkingChildDraftBlocker);
            Transition(entry);
            foreach (var source in RetainedSources(receipt))
                Need(S(units[source.Id]!, "baseline") == S(receipt["proof"]!, source.Path), "Cell observation changed");
            // The read check can explain the blocker but cannot issue a removal receipt.
            if (checkingChildDraftBlocker) return new() { ["blocked"] = entry.ToJsonString().Length <= 1048576 };
            return new() { ["entry"] = entry, ["locators"] = locators };
        }
        Need(action is "pending" or "restore", "Explicit cell history action required");
        var selected = request["selected"]?.AsArray().Select(id => id!.ToString()).ToHashSet(StringComparer.Ordinal);
        var checksByPath = new Dictionary<string, JsonNode>(OperatingSystem.IsWindows() ? StringComparer.OrdinalIgnoreCase : StringComparer.Ordinal);
        var detached = new JsonArray();
        var restored = new JsonArray();
        var published = new JsonObject();
        foreach (var row in units) {
            if (row.Value?["cellRemovalPending"] is not JsonNode pending) continue;
            var receipt = pending["receipt"]!.AsObject();
            bool restoring = pending["restoring"]!.GetValue<bool>();
            string draft = S(row.Value!, "draft"), original = S(row.Value!, "original");
            var entry = new JsonObject {
                ["units"] = new JsonArray(new JsonObject {
                    ["id"] = row.Key, ["kind"] = S(row.Value!, "kind"), ["path"] = S(row.Value!, "path"),
                    ["before"] = restoring ? draft : original, ["after"] = restoring ? original : draft
                }),
                ["cellRemoval"] = receipt.DeepClone()
            };
            Transition(entry);
            var retained = RetainedSources(receipt);
            int version = receipt["version"]!.GetValue<int>();
            if (action == "restore") {
                // A compound Confirm writes only its owned graph. After a process stop,
                // verify its exact outgoing bytes and the existing retained-source proof
                // before treating the graph as physically current in memory.
                if (version == 2 && request["history"]?[restoring ? "redo" : "undo"] is JsonArray history &&
                    history.Any(item => JsonNode.DeepEquals(item?["cellRemoval"], receipt))) {
                    try {
                        Observe(request, entry, false, out _, published: true);
                        published.Add(row.Key, Digest(draft));
                        // The physical graph already supplied its current child locators.
                        continue;
                    }
                    catch (Exception e) when (e is IOException or ArgumentException or InvalidOperationException or BuildError or UnauthorizedAccessException) { }
                }
                if (!restoring)
                    foreach (var source in retained)
                        detached.Add(new JsonObject { ["id"] = source.Id, ["path"] = source.Path });
                else {
                    // Newer receipts verify their original observation before
                    // staging restored locators. If a compound observation is no longer
                    // provable, keep the saved candidate and only the physical locators.
                    try {
                        Observe(request, entry, false, out var locators);
                        foreach (var locator in locators) restored.Add(locator!.DeepClone());
                    }
                    catch (Exception e) when ((version is 1 or 2 && e is (IOException or ArgumentException or InvalidOperationException or BuildError)) ||
                                              (version == 2 && e is UnauthorizedAccessException)) { }
                }
                continue;
            }
            if (selected is not null && !selected.Contains(row.Key)) {
                var comparison = OperatingSystem.IsWindows() ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal;
                Need(!selected.Any(id => units[id]?["path"]?.ToString() is string path &&
                    retained.Any(source => string.Equals(path, source.Path, comparison))),
                    "The retained C# source cannot be written while its cell edit is pending");
                continue;
            }
            foreach (var check in Observe(request, entry, false, out _)) {
                string path = S(check!, "path");
                if (checksByPath.TryGetValue(path, out var other))
                    Need(JsonNode.DeepEquals(check, other), "Cell source observations disagree");
                else checksByPath.Add(path, check!.DeepClone());
            }
        }
        return new() { ["checks"] = new JsonArray(checksByPath.Values.ToArray()), ["detached"] = detached, ["restored"] = restored, ["published"] = published };
    }
}
