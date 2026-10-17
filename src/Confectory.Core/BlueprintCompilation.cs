using System.Text;
using System.Text.Json.Nodes;

namespace Confectory.Core;

// Build-scoped, immutable observations. This never edits graph/node/legacy sources.
internal sealed class BlueprintCompilation(Registry registry, string target, TargetTool tool)
{
    private readonly Dictionary<string, string> nodeOwners = new(StringComparer.Ordinal);
    private readonly Dictionary<string, string> observations = new(StringComparer.Ordinal);
    private readonly HashSet<string> missingSources = new(StringComparer.Ordinal);
    public JsonObject Receipts { get; } = new();
    public Dictionary<string, string> Members { get; } = new(StringComparer.Ordinal);
    public Dictionary<string, FunctionSignature> EntrySignatures { get; } = new(StringComparer.Ordinal);
    public JsonArray Nodes { get; } = new();
    public JsonArray Warnings {
        get { var rows=new JsonArray();foreach(var pair in Receipts)foreach(var warning in (pair.Value?["warnings"]?.AsArray()??new JsonArray()).Concat(pair.Value?["nestedWarnings"]?.AsArray()??new JsonArray())){var row=warning!.DeepClone().AsObject();row["implementation"]=pair.Key;row["graphPath"]=pair.Value!["graphMap"]?["path"]?.DeepClone();rows.Add(row);}return rows; }
    }

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

    public string Assemble(Element implementation, Body body, string path, string? nodeId = null)
    {
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
        string requestedProfile=graph["profile"]?.GetValue<string>()??"";
        if(tool.Info["blueprintProfile"]?.ToString()!=requestedProfile&&!(tool.Info["blueprintProfiles"] is JsonArray profiles&&profiles.Any(p=>p?.ToString()==requestedProfile)))throw new BuildError("BLUEPRINT_TARGET_UNSUPPORTED","Selected compiler does not validate this Blueprint profile",body.Loc);
        var implementations = new JsonObject();
        var nodePaths = new HashSet<string>(StringComparer.Ordinal);
        var tree = BlueprintTree.Nodes(graph).ToDictionary(e => e.Key, StringComparer.Ordinal);
        foreach (var entry in tree.Values)
        {
            var node = entry.Node;
            if (node?["kind"]?.ToString() != "code") continue;
            string id = node["id"]?.GetValue<string>() ?? throw new BuildError("BLUEPRINT_GRAPH", "Node ID required", new(path));
            if (node["implementation"] is not JsonValue file) continue; // Missing stays explicit, never synthesized.
            string nodePath = PackPaths.Owned(Path.GetDirectoryName(path)!, file.GetValue<string>());
            string ownerKey = implementation.Id + "/" + (graph["profile"]?.ToString()==FeatureBlueprint.NestedProfile ? path+"/" : "") + entry.Key;
            if (nodeOwners.TryGetValue(nodePath, out var owner) && owner != ownerKey) throw new BuildError("BLUEPRINT_NODE_OWNERSHIP", "Node source belongs to another feature node", new(nodePath));
            nodeOwners[nodePath] = ownerKey;
            if (!nodePaths.Add(nodePath)) throw new BuildError("BLUEPRINT_NODE_OWNERSHIP", "Each node owns a separate implementation file", new(nodePath));
            if (!File.Exists(nodePath)) { missingSources.Add(nodePath); continue; }
            var record = JsonNode.Parse(Read(nodePath))?.AsObject() ?? throw new BuildError("BLUEPRINT_NODE", "Node record object required", new(nodePath));
            if (record["schema"]?.GetValue<int>() != 1 || record["node"]?.ToString() != id)
                throw new BuildError("BLUEPRINT_NODE_OWNERSHIP", "Node record schema and stable node ID must match", new(nodePath));
            implementations[entry.Key] = record;
        }
        var contracts = new JsonObject();
        foreach (string id in implementation.Imports.Values.Select(i => i.Id).Distinct(StringComparer.Ordinal)) contracts[id] = Contract(id);
        var request = new JsonObject
        {
            ["operation"] = nodeId is null ? "featureBlueprintAssemble" : "featureBlueprintNodeProbe", ["node"] = nodeId, ["featureSource"] = Contract(implementation.Function!),
            ["implementationContext"] = FeatureBlueprint.ImplementationContext(implementation), ["bodyTarget"] = implementation.Bodies.First(p=>p.Value==body).Key, ["graph"] = graph, ["featureContracts"] = contracts, ["implementations"] = implementations
        };
        var result = FeatureBlueprint.Execute(request);
        if (result["state"]?.ToString() != (nodeId is null ? "source-assembled" : "node-source-assembled"))
            throw new BuildError("BLUEPRINT_NOT_READY", result.ToJsonString(), new(path));
        foreach (var import in result["imports"]!.AsArray())
        {
            string alias = import!["alias"]!.GetValue<string>(), feature = import["feature"]!.GetValue<string>();
            if (import["binding"]?.ToString() == "implementation-context") continue; // Exact aliases/scopes are fenced by the context definition above.
            if (!implementation.Imports.TryGetValue(alias, out var declared) || declared.Id != feature)
                throw new BuildError("BLUEPRINT_IMPORT", "Declare typed import " + feature + " as " + alias + " before building", implementation.Loc);
        }
        foreach (var node in result["nodeSources"]!.AsArray()) Nodes.Add(node!.DeepClone());
        var receipt = result.DeepClone().AsObject();
        receipt.Remove("body"); receipt.Remove("nodeSources"); receipt.Remove("members");
        if (result["explicitEntry"]?.GetValue<bool>() == true)
        {
            Members[implementation.Id] = result["members"]!.GetValue<string>();
            EntrySignatures[implementation.Id] = registry.Get(implementation.Function!, "function").Signature!;
        }
        receipt["state"] = result["state"]!.DeepClone();
        receipt["target"] = target;
        receipt["graphMap"]!["path"] = Path.GetRelativePath(Path.GetDirectoryName(registry.ProjectPath)!, path).Replace('\\', '/');
        receipt["compilerIdentity"] = tool.Identity;
        receipt["inputs"] = new JsonArray(observations.OrderBy(p => p.Key, StringComparer.Ordinal).Select(p => (JsonNode)new JsonObject
        {
            ["path"] = Path.GetRelativePath(Path.GetDirectoryName(registry.ProjectPath)!, p.Key).Replace('\\', '/'), ["sha256"] = p.Value
        }).ToArray());
        receipt["missingInputs"] = new JsonArray(missingSources.Order(StringComparer.Ordinal).Select(path => (JsonNode)new JsonObject
        {
            ["path"] = Path.GetRelativePath(Path.GetDirectoryName(registry.ProjectPath)!, path).Replace('\\', '/'), ["status"] = "missing"
        }).ToArray());
        // Node markers include stable ID and implementation content hash; JSON source pointer is explicit.
        foreach (var map in receipt["sourceMap"]!.AsArray())
        {
            string id = map!["node"]!.GetValue<string>();
            var entry = tree[id];
            var definition = entry.Node;
            bool code = definition["kind"]!.ToString() == "code";
            string sourcePath = code ? PackPaths.Owned(Path.GetDirectoryName(path)!, definition["implementation"]!.GetValue<string>()) : path;
            map["path"] = Path.GetRelativePath(Path.GetDirectoryName(registry.ProjectPath)!, sourcePath).Replace('\\', '/');
            map["sourceSha256"] = observations[sourcePath];
            map["jsonPointer"] = code ? "/source" : entry.Pointer;
        }
        Receipts[implementation.Id] = receipt;
        EnsureUnchanged();
        return result["body"]!.GetValue<string>();
    }

    public void EnsureUnchanged(bool verifyCompiler = false)
    {
        if (verifyCompiler && new TargetTool(registry, target).Identity != tool.Identity)
            throw new BuildError("BLUEPRINT_COMPILER_CHANGED", "Compiler profile changed during this build; retain the prior artifact", tool.Element.Loc);
        foreach (string path in missingSources)
            if (File.Exists(path)) throw new BuildError("BLUEPRINT_SOURCE_CHANGED", "A previously missing node source appeared during this build", new(path));
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
