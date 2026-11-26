using Confectory.Core;
using System.Text.Json.Nodes;

internal static class ProjectPackRegistration
{
    private static Registry Installed(string path)
    {
        var stats=new BuildStatistics();
        return new Registry(path,new Documents(Path.Combine(Path.GetTempPath(),"confectory-installed-pack-metadata",JsonData.Digest(path)),stats),stats);
    }
    internal static JsonObject Options(string installation,string project)
    {
        var installed=Installed(installation);
        var owner=new Parser(File.ReadAllText(project),project).ParseManifest();
        if(owner.Kind!="project")throw new ArgumentException("Explicit ProjectPack required");
        return new JsonObject{["options"]=new JsonArray(installed.Packs.Values.Where(pack=>pack.Kind=="pack"&&pack.Namespace!=owner.Namespace&&!owner.Dependencies.ContainsKey(pack.Namespace))
            .OrderBy(pack=>pack.Namespace,StringComparer.Ordinal).Select(pack=>(JsonNode)new JsonObject{["id"]=pack.Namespace,["version"]=pack.Version,["description"]=pack.Description}).ToArray())};
    }
    internal static string Prepare(string installation,string project,string original,string current,string id,Func<Manifest,string> format)
    {
        if(original.Length>1048576||current.Length>1048576)throw new InvalidOperationException("Resolve the existing registration draft first.");
        var owner=new Parser(original,project).ParseManifest();
        if(owner.Kind!="project"||owner.Namespace==id)throw new ArgumentException("Explicit distinct ProjectPack and installed pack required");
        var installed=Installed(installation);
        if(!installed.Packs.TryGetValue(id,out var selected)||selected.Kind!="pack"||owner.Dependencies.ContainsKey(id))throw new ArgumentException("New installed pack required");
        string root=Path.GetDirectoryName(Path.GetFullPath(project))!;
        var pending=new Queue<string>();var seen=new HashSet<string>(StringComparer.Ordinal);pending.Enqueue(id);
        while(pending.TryDequeue(out string? ns))
        {
            if(!seen.Add(ns))continue;
            if(seen.Count>256||ns==owner.Namespace||!installed.Packs.TryGetValue(ns,out var pack)||pack.Kind!="pack")throw new ArgumentException("Installed pack closure unavailable");
            string path=installed.Paths[ns];
            if(owner.Registry.TryGetValue(ns,out var prior))
            {
                if(!string.Equals(PackPaths.Resolve(Path.Combine(root,prior.Path)),PackPaths.Resolve(path),OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal))
                    throw new InvalidOperationException("Existing registration points to a different pack; no replacement.");
            }
            else owner.Registry.Add(ns,new PackRegistration(path,pack.Loc));
            foreach(var dep in pack.Dependencies)
            {
                if(!installed.Packs.TryGetValue(dep.Key,out var dependency)||!VersionExpectation.Matches(dep.Value.Version,dependency.Version))throw new InvalidOperationException("Installed dependency version mismatch");
                pending.Enqueue(dep.Key);
            }
        }
        owner.Dependencies.Add(id,new Dependency(selected.Version,selected.Loc));
        string next=DeclarationTextMerge.MergeManifest(original,format(owner),format);
        if(current!=original&&current!=next)throw new InvalidOperationException("Resolve the existing registration draft first.");
        return next;
    }
}
