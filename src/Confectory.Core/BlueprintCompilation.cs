using System.Text;
using System.Text.Json.Nodes;

namespace Confectory.Core;

// Build-scoped, immutable observations. This never edits graph/node/legacy sources.
internal sealed class BlueprintCompilation(Registry registry, string target, TargetTool tool)
{
    private readonly Dictionary<string, string> nodeOwners = new(StringComparer.Ordinal);
    private readonly Dictionary<string, string> observations = new(StringComparer.Ordinal);
    public JsonObject Receipts { get; } = new();
    public JsonArray Nodes { get; } = new();

    private string Read(string path)
    {
        byte[] bytes;
        try { bytes = File.ReadAllBytes(path); }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
        { throw new BuildError("BLUEPRINT_SOURCE_READ", ex.Message, new(path)); }
        string hash = JsonData.HashBytes(bytes);
        if (observations.TryGetValue(path, out var prior) && prior != hash)
            throw new BuildError("BLUEPRINT_SOURCE_CHANGED", "Input changed during this build", new(path));
        observations[path] = hash;
        try { return new UTF8Encoding(false, true).GetString(bytes); }
        catch (DecoderFallbackException ex) { throw new BuildError("BLUEPRINT_SOURCE_READ", ex.Message, new(path)); }
    }

    private string Contract(string id)
    {
        var known = registry.Get(id, "function");
        string root = Path.GetDirectoryName(registry.Paths[PackPaths.Namespace(id)])!;
        string path = PackPaths.Owned(root, registry.Packs[PackPaths.Namespace(id)].Elements[id.Split("::")[1]].Path);
        string source = Read(path);
        var current = new Parser(source, path).ParseElement();
        if (current.Kind != "function" || current.Id != id || FeatureBlueprint.ContractHash(current) != FeatureBlueprint.ContractHash(known))
            throw new BuildError("BLUEPRINT_SOURCE_CHANGED", "Function contract changed after planning", new(path));
        return source;
    }

    public string Assemble(Element implementation, Body body, string path)
    {
        if (tool.Info["blueprintProfile"]?.GetValue<string>() != FeatureBlueprint.Profile)
            throw new BuildError("BLUEPRINT_TARGET_UNSUPPORTED", "Selected compiler does not validate this Blueprint profile", body.Loc);
        // The implementation selection and imports belong to normal declaration review/planning.
        for (Element? owner = registry.Get(implementation.Id); owner is not null; owner = owner.Parent is null ? null : registry.Get(owner.Parent))
        {
            string source = Read(owner.Loc.File);
            var current = new Parser(source, owner.Loc.File).ParseElement();
            if (JsonData.Digest(current) != JsonData.Digest(owner))
                throw new BuildError("BLUEPRINT_SOURCE_CHANGED", "Implementation declaration changed after planning", owner.Loc);
        }
        foreach (string manifest in registry.Paths.Values)
        {
            var current = new Parser(Read(manifest), manifest).ParseManifest();
            if (JsonData.Digest(current) != registry.ManifestDigests[manifest]) throw new BuildError("BLUEPRINT_SOURCE_CHANGED", "Manifest changed after selection", new(manifest));
        }
        for (Element? owner = registry.Get(tool.Element.Id); owner is not null; owner = owner.Parent is null ? null : registry.Get(owner.Parent))
        {
            var current = new Parser(Read(owner.Loc.File), owner.Loc.File).ParseElement();
            if (JsonData.Digest(current) != JsonData.Digest(owner)) throw new BuildError("BLUEPRINT_SOURCE_CHANGED", "Target declaration changed after selection", owner.Loc);
        }
        var graph = JsonNode.Parse(Read(path))?.AsObject() ?? throw new BuildError("BLUEPRINT_GRAPH", "Graph object required", new(path));
        var implementations = new JsonObject();
        var nodePaths = new HashSet<string>(StringComparer.Ordinal);
        foreach (var node in graph["nodes"]?.AsArray() ?? throw new BuildError("BLUEPRINT_GRAPH", "Graph nodes required", new(path)))
        {
            if (node?["kind"]?.ToString() != "code") continue;
            string id = node["id"]?.GetValue<string>() ?? throw new BuildError("BLUEPRINT_GRAPH", "Node ID required", new(path));
            if (node["implementation"] is not JsonValue file) continue; // Missing stays explicit, never synthesized.
            string nodePath = PackPaths.Owned(Path.GetDirectoryName(path)!, file.GetValue<string>());
            string ownerKey = implementation.Id + "/" + id;
            if (nodeOwners.TryGetValue(nodePath, out var owner) && owner != ownerKey) throw new BuildError("BLUEPRINT_NODE_OWNERSHIP", "Node source belongs to another feature node", new(nodePath));
            nodeOwners[nodePath] = ownerKey;
            if (!nodePaths.Add(nodePath)) throw new BuildError("BLUEPRINT_NODE_OWNERSHIP", "Each node owns a separate implementation file", new(nodePath));
            if (!File.Exists(nodePath)) continue;
            var record = JsonNode.Parse(Read(nodePath))?.AsObject() ?? throw new BuildError("BLUEPRINT_NODE", "Node record object required", new(nodePath));
            if (record["schema"]?.GetValue<int>() != 1 || record["node"]?.ToString() != id)
                throw new BuildError("BLUEPRINT_NODE_OWNERSHIP", "Node record schema and stable node ID must match", new(nodePath));
            implementations[id] = record;
        }
        var contracts = new JsonObject();
        foreach (string id in implementation.Imports.Values.Select(i => i.Id).Distinct(StringComparer.Ordinal)) contracts[id] = Contract(id);
        var request = new JsonObject
        {
            ["operation"] = "featureBlueprintAssemble", ["featureSource"] = Contract(implementation.Function!),
            ["graph"] = graph, ["featureContracts"] = contracts, ["implementations"] = implementations
        };
        var result = FeatureBlueprint.Execute(request);
        if (result["state"]?.ToString() != "source-assembled")
            throw new BuildError("BLUEPRINT_NOT_READY", result.ToJsonString(), new(path));
        foreach (var import in result["imports"]!.AsArray())
        {
            string alias = import!["alias"]!.GetValue<string>(), feature = import["feature"]!.GetValue<string>();
            if (!implementation.Imports.TryGetValue(alias, out var declared) || declared.Id != feature)
                throw new BuildError("BLUEPRINT_IMPORT", "Declare typed import " + feature + " as " + alias + " before building", implementation.Loc);
        }
        foreach (var node in result["nodeSources"]!.AsArray()) Nodes.Add(node!.DeepClone());
        var receipt = result.DeepClone().AsObject();
        receipt.Remove("body"); receipt.Remove("nodeSources");
        receipt["state"] = "source-assembled";
        receipt["target"] = target;
        receipt["graphMap"]!["path"] = Path.GetRelativePath(Path.GetDirectoryName(registry.ProjectPath)!, path).Replace('\\', '/');
        receipt["compilerIdentity"] = tool.Identity;
        receipt["inputs"] = new JsonArray(observations.OrderBy(p => p.Key, StringComparer.Ordinal).Select(p => (JsonNode)new JsonObject
        {
            ["path"] = Path.GetRelativePath(Path.GetDirectoryName(registry.ProjectPath)!, p.Key).Replace('\\', '/'), ["sha256"] = p.Value
        }).ToArray());
        // Node markers include stable ID and implementation content hash; JSON source pointer is explicit.
        foreach (var map in receipt["sourceMap"]!.AsArray())
        {
            string id = map!["node"]!.GetValue<string>();
            var definition = graph["nodes"]!.AsArray().Single(n => n!["id"]!.ToString() == id)!;
            bool code = definition["kind"]!.ToString() == "code";
            string sourcePath = code ? PackPaths.Owned(Path.GetDirectoryName(path)!, definition["implementation"]!.GetValue<string>()) : path;
            map["path"] = Path.GetRelativePath(Path.GetDirectoryName(registry.ProjectPath)!, sourcePath).Replace('\\', '/');
            map["sourceSha256"] = observations[sourcePath];
            map["jsonPointer"] = code ? "/source" : "/nodes/" + graph["nodes"]!.AsArray().IndexOf(definition);
        }
        Receipts[implementation.Id] = receipt;
        EnsureUnchanged();
        return result["body"]!.GetValue<string>();
    }

    public void EnsureUnchanged(bool verifyCompiler = false)
    {
        if (verifyCompiler && new TargetTool(registry, target).Identity != tool.Identity)
            throw new BuildError("BLUEPRINT_COMPILER_CHANGED", "Compiler profile changed during this build; retain the prior artifact", tool.Element.Loc);
        foreach (var (path, hash) in observations)
        {
            byte[] bytes;
            try { bytes = File.ReadAllBytes(path); }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
            { throw new BuildError("BLUEPRINT_SOURCE_CHANGED", ex.Message, new(path)); }
            if (hash != JsonData.HashBytes(bytes))
                throw new BuildError("BLUEPRINT_SOURCE_CHANGED", "Preserve the prior artifact; rebuild the new input explicitly", new(path));
        }
    }
}
