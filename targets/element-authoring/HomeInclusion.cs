using Confectory.Core;
using System.Text.Json.Nodes;

// The same target-specific reachability as Builder.Build(). No TargetTool,
// compiler, implementation body, provider or project process is executed.
internal static class HomeInclusion
{
    internal static JsonObject Query(string project)
    {
        const int maxDocuments = 16384, maxBytes = 32 * 1024 * 1024;
        var snapshots = new Dictionary<string, byte[]>(StringComparer.Ordinal);
        int total = 0;
        byte[] Read(string path)
        {
            if (snapshots.TryGetValue(path, out var prior)) return prior;
            if (snapshots.Count >= maxDocuments) throw new IOException("Inclusion document budget");
            for (FileSystemInfo? node = new FileInfo(path); node is not null; node = node is FileInfo file ? file.Directory : ((DirectoryInfo)node).Parent)
                if (node.LinkTarget is not null) throw new IOException("Inclusion source symlink");
            var info = new FileInfo(path);
            if (!info.Exists || info.Length > 1048576 || total + info.Length > maxBytes) throw new IOException("Inclusion byte budget");
            using var stream = File.OpenRead(path);
            var raw = new byte[(int)info.Length]; stream.ReadExactly(raw);
            if (stream.ReadByte() != -1) throw new IOException("Inclusion source changed while reading");
            total += raw.Length; snapshots.Add(path, raw); return raw;
        }
        var statistics = new BuildStatistics();
        var documents = new Documents("", statistics, Read);
        var manifest = documents.Manifest(project);
        var result = new JsonObject { ["status"] = "available", ["scope"] = "confirmed-entry-target-reachability", ["sourceScope"] = "confirmed-files" };
        if (manifest.Kind != "project" || manifest.Entry is null || manifest.Targets.Count == 0)
        { result["packsStatus"] = "unsupported"; return result; }
        if (manifest.Registry.Count >= 256 || manifest.Targets.Count > 16) throw new IOException("Inclusion registry/target budget");
        var registry = new Registry(project, documents, statistics);
        if (registry.Packs.Sum(p => p.Value.Elements.Count) > maxDocuments) throw new IOException("Inclusion locator budget");
        if (registry.Packs.Keys.Any(ns => ns.Length > 256) || manifest.Targets.Keys.Any(t => t.Length > 64)) throw new IOException("Inclusion identifier budget");
        var targets = new JsonArray();
        foreach (string target in manifest.Targets.Keys.Order(StringComparer.Ordinal))
        {
            var planner = new Planner(registry, target);
            var targetReference = manifest.Targets[target];
            var targetElement = registry.Effective(registry.Get(targetReference.Id, "buildtarget", manifest.Namespace + "::<project>", targetReference.Loc).Id);
            planner.Structural(targetElement.Id);
            if (string.IsNullOrEmpty(targetElement.Tool)) throw new IOException("Inclusion target tool declaration missing");
            var plan = planner.Plan();
            string[] included = plan.Reached.Select(PackPaths.Namespace).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal).ToArray();
            targets.Add(new JsonObject { ["target"] = target, ["count"] = included.Length, ["included"] = System.Text.Json.JsonSerializer.SerializeToNode(included) });
        }
        // Reject a mixture of source versions, including changed manifests.
        foreach (var (path, bytes) in snapshots)
        {
            var info = new FileInfo(path);
            if (!info.Exists || info.Length != bytes.Length || info.LinkTarget is not null)
                throw new IOException("Inclusion source changed during observation");
            using var stream = File.OpenRead(path);
            var observed = new byte[bytes.Length]; stream.ReadExactly(observed);
            if (stream.ReadByte() != -1 || !observed.AsSpan().SequenceEqual(bytes)) throw new IOException("Inclusion source changed during observation");
        }
        int[] counts = targets.Select(t => t!["count"]!.GetValue<int>()).Distinct().ToArray();
        result["packsStatus"] = counts.Length == 1 ? "available" : "target-dependent";
        if (counts.Length == 1) result["packs"] = counts[0];
        result["targets"] = targets;
        if (System.Text.Encoding.UTF8.GetByteCount(result.ToJsonString()) > 65536) throw new IOException("Inclusion response budget");
        return result;
    }
}
