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

    static JsonObject Transition(JsonNode entry)
    {
        var receipt = entry["cellRemoval"]!.AsObject();
        Need(receipt.Count == 7 && receipt["version"]?.GetValue<int>() == 1 &&
            entry["units"] is JsonArray { Count: 1 }, "Exact retained cell history required");
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
        Need(JsonNode.DeepEquals(after, BlueprintCellRemoval.Remove(before, S(receipt, "node"))),
            "Cell history may only restore its exact original nodes and connections");
        var guards = receipt["proof"]!.AsObject();
        Need(guards.Count == 4 && guards.All(pair => pair.Value is JsonValue hash &&
            hash.TryGetValue<string>(out string? value) && value is { Length: 64 } &&
            value.All(character => char.IsAsciiHexDigitLower(character))),
            "Bounded source ownership hashes required");
        return graph;
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

    static JsonArray Observe(JsonObject request, JsonNode entry, bool prepare, out JsonObject verifiedLocator)
    {
        var receipt = entry["cellRemoval"]!.AsObject();
        var edited = entry["units"]![0]!;
        string graphId = S(receipt, "graph"), node = S(receipt, "node");
        string graphPath = S(edited, "path"), leafPath = S(receipt, "source");
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
        string original = S(graphUnit!, "original");
        Need(onDisk == original && files.Hash(graphPath) == S(graphUnit!, "baseline") &&
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
        string leafId = BlueprintTree.SourceId(graphId, node);
        var originalLocator = prior.SingleOrDefault(row => S(row!, "id") == leafId);
        Need(originalLocator is not null && files.Same(S(originalLocator, "path"), leafPath) &&
            !files.Same(graphPath, leafPath), "The original cell source locator changed");
        files.Writable(graphPath);
        files.Writable(leafPath);
        string leafText = files.Read(leafPath);
        BlueprintDocuments.Validate(leafId, "blueprint-node", leafText);
        var proof = new JsonObject();
        foreach (string path in new[] { manifestPath, functionPath, implementationPath, leafPath }) proof.Add(path, files.Hash(path));
        if (prepare) receipt["proof"] = proof;
        else Need(JsonNode.DeepEquals(proof, receipt["proof"]), "The retained C# source or its owner changed; no changes applied");

        // A separate root or body cannot claim either of these paths. The
        // inspected registrations and graphs enter the same final CAS lease.
        foreach (var registration in manifest.Registry.Values) {
            string pack = PackPaths.Resolve(Path.Combine(Path.GetDirectoryName(project)!, registration.Path));
            string relative = Path.GetRelativePath(Path.GetDirectoryName(pack)!, files.Full(leafPath));
            Need(Path.IsPathRooted(relative) || relative == ".." ||
                relative.StartsWith(".." + Path.DirectorySeparatorChar, StringComparison.Ordinal),
                "Cell source overlaps another registered pack's ownership");
        }
        foreach (var declaration in manifest.Elements.Values) {
            Need(!files.Same(declaration.Path, graphPath) && !files.Same(declaration.Path, leafPath),
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
                Need(!files.Same(leafPath, path), "Shared cell source is outside cell removal scope");
                if (sameBody || candidate.Value.SourceKind != "blueprint") continue;
                string relativeGraph = path.Replace(Path.AltDirectorySeparatorChar, Path.DirectorySeparatorChar);
                foreach (var locator in BlueprintDocuments.NodeUnits(Path.GetDirectoryName(project)!, files.Full(relativeGraph),
                             header.Id + "/body:" + candidate.Key, files.Read(relativeGraph)))
                    Need(!files.Same(leafPath, S(locator!, "path")) && !files.Same(graphPath, S(locator!, "path")),
                        "Another Blueprint claims the original graph or cell source");
            }
        }
        var physical = BlueprintDocuments.NodeUnits(Path.GetDirectoryName(project)!, files.Full(graphPath), graphId, onDisk);
        Need(physical.All(row => !files.Same(S(row!, "path"), graphPath) &&
            (!files.Same(S(row!, "path"), leafPath) || S(row!, "id") == leafId)), "Cell source paths must be distinct");
        foreach (var row in prior) files.Read(S(row!, "path"));

        foreach (var member in units) {
            var unit = member.Value!;
            if (member.Key == graphId || unit["draft"] is null || JsonNode.DeepEquals(unit["draft"], unit["original"])) continue;
            Need(!files.Reads.Any(read => files.Same(read.Key, S(unit, "path"))),
                "Resolve other pending ownership or source changes before applying the cell edit");
        }
        verifiedLocator = originalLocator!.DeepClone().AsObject();
        return new JsonArray(files.Reads.Select(row => (JsonNode)new JsonObject {
            ["path"] = row.Key, ["hash"] = row.Value.Hash
        }).ToArray());
    }

    public static JsonObject Query(JsonObject request)
    {
        string action = S(request, "action");
        if (action == "options") return new() {
            ["nodes"] = new JsonArray(BlueprintCellRemoval.Options(
                request["graph"]!.AsObject(), request["path"]?.GetValue<string>() ?? "")
                .Select(id => (JsonNode)JsonValue.Create(id)!).ToArray())
        };
        if (action == "validate") { Transition(request["entry"]!); return new(); }
        if (action == "entry") {
            var entry = request["entry"]!;
            Transition(entry);
            var checks = Observe(request, entry, false, out var locator);
            return new() { ["checks"] = checks, ["locator"] = locator };
        }
        var units = request["units"]!.AsObject();
        if (action == "prepare") {
            string id = S(request, "id"), node = S(request, "node");
            var graph = units[id]!;
            string before = S(graph, "draft");
            Need(before == S(graph, "original") && graph["cellRemovalPending"] is null &&
                new[] { "propertyObservations", "atomicEditGroup", "rootContractGroup", "nodeFlowOrigin",
                    "hierarchyGroup", "retirementGroup", "conversionOrigin" }.All(field => graph[field] is null),
                "Confirm pending source changes before removing a cell");
            string leafId = BlueprintTree.SourceId(id, node);
            var leaf = units[leafId]!;
            Need(leaf?["kind"]?.ToString() == "blueprint-node" && leaf["baseline"]?.ToString() != "missing" &&
                JsonNode.DeepEquals(leaf["draft"], leaf["original"]), "An existing clean cell source is required");
            string after = BlueprintCellRemoval.Remove(JsonNode.Parse(before)!.AsObject(), node).ToJsonString();
            var entry = new JsonObject {
                ["id"] = Guid.NewGuid().ToString("N"), ["label"] = "source-edit",
                ["units"] = new JsonArray(new JsonObject {
                    ["id"] = id, ["kind"] = "blueprint", ["path"] = S(graph, "path"), ["before"] = before, ["after"] = after
                }),
                ["cellRemoval"] = new JsonObject {
                    ["version"] = 1, ["graph"] = id, ["node"] = node, ["source"] = S(leaf!, "path"),
                    ["beforeHash"] = Digest(before), ["afterHash"] = Digest(after)
                }
            };
            Observe(request, entry, true, out _);
            Transition(entry);
            Need(S(leaf!, "baseline") == S(entry["cellRemoval"]!["proof"]!, S(leaf!, "path")), "Cell observation changed");
            return new() { ["entry"] = entry };
        }
        Need(action is "pending" or "restore", "Explicit cell history action required");
        var selected = request["selected"]?.AsArray().Select(id => id!.ToString()).ToHashSet(StringComparer.Ordinal);
        var checksByPath = new Dictionary<string, JsonNode>(OperatingSystem.IsWindows() ? StringComparer.OrdinalIgnoreCase : StringComparer.Ordinal);
        var detached = new JsonArray();
        var restored = new JsonArray();
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
            string leaf = BlueprintTree.SourceId(row.Key, S(receipt, "node"));
            if (action == "restore") {
                if (!restoring) detached.Add(new JsonObject { ["id"] = leaf, ["path"] = S(receipt, "source") });
                else {
                    // Preserve a conflicting draft for inspection. Only a currently
                    // valid observation may reintroduce its normal body locator.
                    try { Observe(request, entry, false, out var locator); restored.Add(locator); }
                    catch (Exception e) when (e is IOException or ArgumentException or InvalidOperationException or BuildError) { }
                }
                continue;
            }
            if (selected is not null && !selected.Contains(row.Key)) {
                var comparison = OperatingSystem.IsWindows() ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal;
                Need(!selected.Any(id => units[id]?["path"]?.ToString() is string path &&
                    string.Equals(path, S(receipt, "source"), comparison)),
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
        return new() { ["checks"] = new JsonArray(checksByPath.Values.ToArray()), ["detached"] = detached, ["restored"] = restored };
    }
}
