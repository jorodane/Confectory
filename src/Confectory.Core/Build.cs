using System.ComponentModel;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

namespace Confectory.Core;

public sealed class TargetTool
{
    public const int Protocol = 1;
    public Registry Registry { get; }
    public string Target { get; }
    public Element Element { get; }
    public string Path { get; }
    public string Identity { get; }
    public JsonObject Info { get; }

    public TargetTool(Registry registry, string target)
    {
        Registry = registry; Target = target;
        if (!registry.Project.Targets.TryGetValue(target, out var reference)) throw new BuildError("MISSING_TARGET", $"No build-target mapping for {target}", registry.Project.Loc);
        Element = registry.Effective(registry.Get(reference.Id, "buildtarget", registry.Project.Namespace + "::<project>", reference.Loc).Id);
        new Planner(registry, target).Structural(Element.Id);
        string root = System.IO.Path.GetDirectoryName(registry.Paths[PackPaths.Namespace(Element.ToolOrigin ?? Element.Id)])!;
        if (string.IsNullOrEmpty(Element.Tool)) throw new BuildError("MISSING_TOOL", "Build-target pack must declare its tool", Element.Loc);
        Path = PackPaths.Owned(root, Element.Tool, Element.Loc);
        if (!File.Exists(Path)) throw new BuildError("MISSING_TOOL", $"Build-target tool not found: {Path}; build its project first", Element.Loc);
        // Include adjacent host configuration as well as the tool assembly. DLL
        // tools must publish self-contained code or fingerprint their dependencies.
        var files = new Dictionary<string, string> { [System.IO.Path.GetFileName(Path)] = JsonData.HashBytes(File.ReadAllBytes(Path)) };
        if (System.IO.Path.GetExtension(Path) == ".dll")
        {
            foreach (string suffix in new[] { ".deps.json", ".runtimeconfig.json" })
            {
                string config = System.IO.Path.ChangeExtension(Path, null) + suffix;
                if (File.Exists(config)) files[System.IO.Path.GetFileName(config)] = JsonData.HashBytes(File.ReadAllBytes(config));
            }
        }
        Info = Invoke("fingerprint");
        if (Info["fingerprint"] is not JsonValue fingerprint || !fingerprint.TryGetValue<string>(out var value) || string.IsNullOrEmpty(value)) throw new BuildError("TOOL_PROTOCOL", "Tool did not return a configuration fingerprint", Element.Loc);
        Identity = JsonData.Digest(new object[] { Protocol, files, Element.Options, target, value });
    }
    public JsonObject Invoke(string operation, object? payload = null)
    {
        Registry.Statistics.TargetInvocations.TryGetValue(operation, out int count);
        Registry.Statistics.TargetInvocations[operation] = count + 1;
        var request = JsonData.Object(new { protocol = Protocol, operation, target = Target, options = Element.Options });
        if (payload is not null) foreach (var (key, value) in JsonData.Object(payload)) request[key] = value?.DeepClone();
        string[] command = System.IO.Path.GetExtension(Path) == ".dll" ? [Processes.DotNet(), Path] : [Path];
        ProcessResult response;
        try { response = Processes.Run(command, request.ToJsonString(JsonData.Options), System.IO.Path.GetDirectoryName(Path)); }
        catch (Exception ex) when (ex is IOException or Win32Exception or TimeoutException or UnauthorizedAccessException)
        { throw new BuildError("TOOL_EXECUTION", $"Target tool failed: {ex.Message}", Element.Loc); }
        JsonObject result;
        try { result = JsonNode.Parse(response.Stdout) as JsonObject ?? throw new JsonException("Response must be an object"); }
        catch (JsonException) { throw new BuildError("TOOL_PROTOCOL", $"Target tool returned invalid JSON: {response.Stderr}{response.Stdout}", Element.Loc); }
        if (result["protocol"] is not JsonValue protocol || !protocol.TryGetValue<int>(out int version) || version != Protocol) throw new BuildError("TOOL_PROTOCOL", "Target tool protocol mismatch", Element.Loc);
        if (response.ExitCode != 0 || result["ok"] is not JsonValue ok || !ok.TryGetValue<bool>(out bool success) || !success)
            throw new BuildError("TARGET_FAILURE", result["error"]?.ToString() ?? (string.IsNullOrEmpty(response.Stderr) ? "Tool failed" : response.Stderr), Element.Loc);
        if (operation.StartsWith("compile-", StringComparison.Ordinal) && result["artifacts"] is not JsonObject) throw new BuildError("TOOL_PROTOCOL", "Compile tool must return artifact paths", Element.Loc);
        return result;
    }
}

public sealed class Artifacts(string root)
{
    public Dictionary<string, string>? Get(string key)
    {
        string folder = Path.Combine(root, key);
        try
        {
            var record = JsonNode.Parse(File.ReadAllText(Path.Combine(folder, "artifact.json")))!.AsObject();
            if (record["key"]?.GetValue<string>() != key || record["files"] is not JsonObject files || files.Count == 0) return null;
            var artifacts = new Dictionary<string, string>(StringComparer.Ordinal);
            foreach (var (name, item) in files)
            {
                string path = PackPaths.Owned(folder, item!["path"]!.GetValue<string>());
                if (JsonData.HashBytes(File.ReadAllBytes(path)) != item["hash"]!.GetValue<string>()) return null;
                artifacts[name] = path;
            }
            return artifacts;
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or JsonException or InvalidOperationException or KeyNotFoundException or BuildError or FormatException or NullReferenceException) { return null; }
    }
    public Dictionary<string, string> Produce(string key, Func<string, JsonObject> callback)
    {
        string work = Path.Combine(root, $"{key}.{Guid.NewGuid():N}.pending"); Directory.CreateDirectory(work);
        try
        {
            var artifacts = callback(work);
            if (artifacts.Count == 0) throw new BuildError("TOOL_PROTOCOL", "Compiler did not return artifacts");
            var files = new JsonObject();
            foreach (var (name, value) in artifacts)
            {
                if (value is not JsonValue v || !v.TryGetValue<string>(out string? pathValue)) throw new BuildError("TOOL_PROTOCOL", "Compiler artifact path must be a string");
                string path = PackPaths.Owned(work, pathValue);
                if (!File.Exists(path)) throw new BuildError("TOOL_PROTOCOL", $"Compiler artifact is missing: {path}");
                files[name] = JsonData.Object(new { path = Path.GetRelativePath(work, path), hash = JsonData.HashBytes(File.ReadAllBytes(path)) });
            }
            JsonData.AtomicWrite(Path.Combine(work, "artifact.json"), new { key, files });
            string dest = Path.Combine(root, key);
            if (Directory.Exists(dest))
            {
                var existing = Get(key);
                if (existing is not null) { Directory.Delete(work, true); return existing; }
                Directory.Delete(dest, true);
            }
            Directory.Move(work, dest);
            return Get(key) ?? throw new BuildError("TOOL_PROTOCOL", "Produced artifacts could not be verified");
        }
        finally { if (Directory.Exists(work)) Directory.Delete(work, true); }
    }
}

public sealed class Builder
{
    public string Project { get; }
    public string Target { get; }
    public string State { get; }
    public BuildStatistics Statistics { get; } = new();
    public Documents Documents { get; }
    public Registry Registry { get; }
    public TargetTool Tool { get; }
    private readonly Artifacts cache;
    public Dictionary<string, JsonObject> Contracts { get; } = new(StringComparer.Ordinal);

    public Builder(string project, string target)
    {
        Project = PackPaths.Resolve(project); Target = target; State = Path.Combine(Path.GetDirectoryName(Project)!, ".confectory");
        Documents = new(Path.Combine(State, "cache", "declarations"), Statistics);
        Registry = new(Project, Documents, Statistics); Tool = new(Registry, target);
        cache = new(Path.Combine(State, "cache", "artifacts"));
    }
    private static string WriteSource(string path, string text)
    { File.WriteAllText(path, text, new UTF8Encoding(false)); return path; }
    public JsonObject Contract(string id)
    {
        if (Contracts.TryGetValue(id, out var cached)) return cached;
        string code = Generation.ContractSource(Registry.Get(id, "function")), name = "Contract_" + Generation.Symbol(id);
        string key = JsonData.Digest(new[] { Generation.Abi, Tool.Identity, "contract", code });
        var artifact = cache.Get(key);
        if (artifact is not null) Statistics.ReusedContracts.Add(id);
        else
        {
            artifact = cache.Produce(key, work => Tool.Invoke("compile-contract", new { output = work, name, sources = new[] { WriteSource(Path.Combine(work, name + ".cs"), code) }, references = Array.Empty<string>() })["artifacts"]!.AsObject());
            Statistics.CompiledContracts.Add(id);
        }
        if (!artifact.ContainsKey("assembly") || !artifact.ContainsKey("reference")) throw new BuildError("TOOL_PROTOCOL", "Contract compilation must return assembly and reference");
        var result = JsonData.Object(artifact); result["key"] = key; Contracts[id] = result; return result;
    }
    public JsonObject CompilePack(string ns, IEnumerable<Element> implementations)
    {
        var artifacts = new Dictionary<string, JsonObject>(StringComparer.Ordinal);
        bool compiled = false;
        foreach (var e in implementations.OrderBy(x => x.Id, StringComparer.Ordinal))
        {
            Registry.Implementation(e.Function!, e.Id, e.Id, e.Loc);
            if (!e.Bodies.TryGetValue(Target, out var body) && !e.Bodies.TryGetValue("common", out body)) throw new BuildError("MISSING_TARGET_IMPLEMENTATION", $"No {Target}/common body for {e.Id}", e.Loc);
            string path = PackPaths.Owned(Path.GetDirectoryName(Registry.Paths[PackPaths.Namespace(body.Origin)])!, body.Path, body.Loc);
            string code = Generation.ImplementationSource(e, Documents.Body(path), path);
            var refs = new Dictionary<string, JsonObject>(StringComparer.Ordinal);
            foreach (string id in new[] { e.Function! }.Concat(e.Imports.Values.Select(x => x.Id))) refs[id] = Contract(id);
            // Cache each owned implementation independently. A contract-only
            // check of the whole pack and a final subset use identical keys.
            string key = JsonData.Digest(new object[] { Generation.Abi, Tool.Identity, "implementation-v1", ns, e.Id, code,
                refs.OrderBy(x => x.Key, StringComparer.Ordinal).Select(x => new[] { x.Key, x.Value["key"]!.GetValue<string>() }).ToArray() });
            var artifact = cache.Get(key);
            if (artifact is not null) Statistics.ReusedImplementations.Add(e.Id);
            else
            {
                artifact = cache.Produce(key, work => Tool.Invoke("compile-pack", new
                {
                    output = work, name = "Pack_" + Generation.Symbol(ns) + "_" + Generation.Symbol(e.Id),
                    sources = new[] { WriteSource(Path.Combine(work, Generation.Symbol(e.Id) + ".cs"), code) },
                    references = refs.Values.Select(x => x["reference"]!.GetValue<string>()).ToArray()
                })["artifacts"]!.AsObject());
                Statistics.CompiledImplementations.Add(e.Id); compiled = true;
            }
            if (!artifact.ContainsKey("assembly")) throw new BuildError("TOOL_PROTOCOL", "Pack compilation must return an assembly");
            var item = JsonData.Object(artifact); item["key"] = key; artifacts[e.Id] = item;
        }
        if (artifacts.Count == 0) throw new BuildError("LOCAL_INPUT", $"No implementation declarations in {ns}");
        if (compiled) Statistics.CompiledPacks.Add(ns); else Statistics.ReusedPacks.Add(ns);
        string composition = JsonData.Digest(new object[] { "pack-composition-v1", ns, artifacts.Select(x => new[] { x.Key, x.Value["key"]!.GetValue<string>() }).ToArray() });
        // 'assembly'/'reference' are legacy aliases for the first implementation;
        // consumers of a multi-implementation pack must use the complete list.
        var result = artifacts.Values.First().DeepClone().AsObject();
        result["key"] = composition;
        result["implementations"] = JsonSerializer.SerializeToNode(artifacts.Keys.ToArray());
        result["assemblies"] = JsonSerializer.SerializeToNode(artifacts.Values.Select(x => x["assembly"]!.GetValue<string>()).ToArray());
        result["implementationArtifacts"] = JsonSerializer.SerializeToNode(artifacts, JsonData.Options);
        return result;
    }
    public JsonObject Check(string ns)
    {
        if (!Registry.Packs.TryGetValue(ns, out var pack)) throw new BuildError("MISSING_NAMESPACE", $"Pack {ns} is not selected");
        List<Element> implementations = []; var planner = new Planner(Registry, Target);
        foreach (var (local, locator) in pack.Elements)
        {
            if (locator.Kind != "implementation") continue;
            string id = ns + "::" + local; var e = Registry.Effective(id); planner.Structural(id);
            implementations.Add(Registry.Implementation(e.Function!, id, id, e.Loc));
        }
        if (implementations.Count == 0) throw new BuildError("LOCAL_INPUT", $"No implementation declarations in {ns}", pack.Loc);
        return JsonData.Object(new { mode = "contract-only", pack = ns, target = Target, artifact = CompilePack(ns, implementations), warnings = Registry.Warnings, statistics = Statistics });
    }
    public JsonObject Build()
    {
        var plan = new Planner(Registry, Target).Plan(); var packs = new Dictionary<string, JsonObject>(StringComparer.Ordinal);
        foreach (var group in plan.Implementations.Values.GroupBy(x => PackPaths.Namespace(x.Id)).OrderBy(x => x.Key, StringComparer.Ordinal)) packs[group.Key] = CompilePack(group.Key, group);
        foreach (var node in plan.Bindings.Values) Contract(node.Function);
        string code = Generation.FinalSource(plan);
        string key = JsonData.Digest(new object[] { Generation.Abi, Tool.Identity, "link", code, packs.ToDictionary(x => x.Key, x => x.Value["key"]!.GetValue<string>()), Contracts.ToDictionary(x => x.Key, x => x.Value["key"]!.GetValue<string>()) });
        string outputRoot = Path.Combine(State, "outputs", Target), work = Path.Combine(outputRoot, $"{key}.{Guid.NewGuid():N}.pending"); Directory.CreateDirectory(work);
        try
        {
            string source = WriteSource(Path.Combine(work, "Bindings.cs"), code), catalog = Path.Combine(work, "sources", "public-linkage.json");
            JsonData.AtomicWrite(catalog, Generation.PublicCatalog(plan, packs, Contracts, Target));
            var result = Tool.Invoke("link", new { output = work, name = "Confectory.App", sources = new[] { source },
                references = Contracts.Values.Select(x => x["assembly"]!.GetValue<string>()).Concat(packs.Values.SelectMany(x => x["assemblies"]!.AsArray().Select(a => a!.GetValue<string>()))).ToArray(),
                resources = new[] { new { path = catalog, name = "public-linkage.json" } } });
            if (result["run"] is not JsonArray runArray || runArray.Count == 0 || runArray.Any(x => x is not JsonValue v || !v.TryGetValue<string>(out _))) throw new BuildError("TOOL_PROTOCOL", "Link tool must return an executable command");
            if (result["artifacts"] is not JsonObject artifacts || !artifacts.ContainsKey("application")) throw new BuildError("TOOL_PROTOCOL", "Link tool must return an application artifact");
            foreach (var (_, value) in artifacts)
            {
                if (value is not JsonValue v || !v.TryGetValue<string>(out var path)) throw new BuildError("TOOL_PROTOCOL", "Final artifact path must be a string");
                if (!File.Exists(PackPaths.Owned(work, path))) throw new BuildError("TOOL_PROTOCOL", $"Missing final artifact {path}");
            }
            if (artifacts["publicCatalog"] is null || JsonData.HashBytes(File.ReadAllBytes(PackPaths.Owned(work, artifacts["publicCatalog"]!.GetValue<string>()))) != JsonData.HashBytes(File.ReadAllBytes(catalog))) throw new BuildError("TOOL_PROTOCOL", "Target must preserve the public linkage catalog");
            string dest = Path.Combine(outputRoot, key + "-" + Guid.NewGuid().ToString("N")[..12]); Directory.Move(work, dest);
            var reached = plan.Reached.Select(PackPaths.Namespace).ToHashSet(StringComparer.Ordinal);
            var report = JsonData.Object(new
            {
                mode = "final", project = Registry.Project.Namespace, target = Target, entry = Registry.Project.Entry, key, output = dest,
                run = runArray.Select(x => x!.GetValue<string>().Replace(work, dest, StringComparison.Ordinal)).ToArray(), publicCatalog = artifacts["publicCatalog"]!.GetValue<string>().Replace(work, dest, StringComparison.Ordinal),
                registeredPacks = Registry.Packs.Keys.Order(StringComparer.Ordinal).ToArray(), includedPacks = reached.Order(StringComparer.Ordinal).ToArray(), excludedPacks = Registry.Packs.Keys.Except(reached).Order(StringComparer.Ordinal).ToArray(),
                implementationArtifacts = packs, contractArtifacts = Contracts, bindings = plan.Bindings.Values.ToArray(), warnings = Registry.Warnings, statistics = Statistics, tool = Tool.Info
            });
            JsonData.AtomicWrite(Path.Combine(dest, "build-report.json"), report);
            JsonData.AtomicWrite(Path.Combine(outputRoot, "latest.json"), report); return report;
        }
        finally { if (Directory.Exists(work)) Directory.Delete(work, true); }
    }
    public JsonObject Validate()
    {
        var planner = new Planner(Registry, Target);
        foreach (var (ns, manifest) in Registry.Packs)
        foreach (string local in manifest.Elements.Keys)
        {
            string id = ns + "::" + local; var e = Registry.Effective(id); planner.Structural(id);
            if (e.Kind == "implementation") Registry.Implementation(e.Function!, id, id, e.Loc);
            else if (e.Kind == "module") planner.Module(id);
            foreach (var reference in e.Uses.Concat(e.Contains)) Registry.Get(reference.Id, reference.Kind, reference.Origin ?? id, reference.Loc);
            foreach (var (fn, provider) in e.Provides) Registry.Implementation(fn, provider.Id, provider.Origin ?? id, provider.Loc);
        }
        return JsonData.Object(new { mode = "validate", warnings = Registry.Warnings, statistics = Statistics });
    }
}
