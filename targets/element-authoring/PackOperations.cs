using Confectory.Core;
using System.Text.Json.Nodes;

internal static class PackOperations
{
    internal static JsonNode Execute(string operation,JsonObject request,Func<Manifest,string> format)
    {
        string S(string name)=>request[name]!.GetValue<string>();
        if(operation=="packSource")
        {
            string path=Path.GetFullPath(S("path")),root=Path.GetDirectoryName(path)!;var manifest=new Parser(File.ReadAllText(path),path).ParseManifest();
            if(manifest.Kind!="pack")throw new ArgumentException("An imported library Pack is required, not another ProjectPack.");
            bool tool=false;foreach(var item in manifest.Elements.Values){var element=new Parser(File.ReadAllText(PackPaths.Owned(root,item.Path)),item.Path).ParseElement();if(element.Kind=="buildtarget"&&element.Tool is not null)tool=true;}
            return new JsonObject{["namespace"]=manifest.Namespace,["version"]=manifest.Version,["hash"]=Hash(root),["toolBootstrap"]=tool};
        }
        if(operation=="packManifest")
        {
            var manifest=new Parser(S("text"),"<pack-transaction>").ParseManifest();string ns=S("namespace"),action=S("action");
            if(action=="remove"){manifest.Registry.Remove(ns);manifest.Dependencies.Remove(ns);}
            else
            {
                if(action=="register"&&manifest.Registry.ContainsKey(ns))throw new ArgumentException("Namespace already registered; update must be explicit.");
                if(action=="update"&&!manifest.Registry.ContainsKey(ns))throw new ArgumentException("Update requires an existing registration.");
                manifest.Registry[ns]=new(S("path"),new());manifest.Dependencies[ns]=new(S("expectation"),new());
            }
            return JsonValue.Create(format(manifest))!;
        }
        if(operation=="packUsage")
        {
            var usage=Usage(S("project"),S("entry"),S("target"));string root=Path.GetDirectoryName(Path.GetFullPath(S("project")))!,path=Path.Combine(root,".pack-lock.json");
            var pins=File.Exists(path)?JsonNode.Parse(File.ReadAllText(path))!["pins"]!.DeepClone().AsObject():new JsonObject();
            foreach(var item in pins){string selected=Path.GetFullPath(Path.Combine(root,item.Value!["path"]!.GetValue<string>()));string hash=Hash(Path.GetDirectoryName(selected)!);item.Value["observedHash"]=hash;item.Value["locallyModified"]=hash!=item.Value["originHash"]!.GetValue<string>();}
            usage["pins"]=pins;return usage;
        }
        throw new ArgumentException("Unknown pack metadata operation.");
    }
    internal static JsonObject Usage(string project,string entry,string target)
    {
        string temporary=Path.Combine(Path.GetTempPath(),"confectory-discovery-"+Guid.NewGuid().ToString("N"));
        try
        {
            var statistics=new BuildStatistics();var registry=new Registry(project,new Documents(temporary,statistics),statistics);if(entry!="")registry.Project.Entry=entry;
            var plan=new Planner(registry,target).Plan();var used=plan.Reached.Select(PackPaths.Namespace).ToHashSet(StringComparer.Ordinal);var packs=new JsonArray();
            foreach(var (ns,manifest) in registry.Packs.OrderBy(x=>x.Key,StringComparer.Ordinal))packs.Add(new JsonObject{["namespace"]=ns,["version"]=manifest.Version,["used"]=used.Contains(ns),["path"]=registry.Paths[ns]});
            return new JsonObject{["project"]=Path.GetFullPath(project),["entry"]=registry.Project.Entry,["target"]=target,["packs"]=packs,["elements"]=System.Text.Json.JsonSerializer.SerializeToNode(plan.Reached.Order(StringComparer.Ordinal)),["warnings"]=System.Text.Json.JsonSerializer.SerializeToNode(registry.Warnings,JsonData.Options)};
        }
        finally{if(Directory.Exists(temporary))Directory.Delete(temporary,true);}
    }
    internal static string Hash(string root)
    {
        var files=new SortedDictionary<string,string>(StringComparer.Ordinal);
        void Walk(string folder)
        {
            if((File.GetAttributes(folder)&FileAttributes.ReparsePoint)!=0)throw new ArgumentException("Source pack symlinks are not imported.");
            foreach(string path in Directory.GetFiles(folder))
            {
                if((File.GetAttributes(path)&FileAttributes.ReparsePoint)!=0)throw new ArgumentException("Source pack symlinks are not imported.");
                if(Path.GetExtension(path).ToLowerInvariant() is ".dll" or ".exe" or ".apk" or ".pdb")continue;
                files[Path.GetRelativePath(root,path).Replace('\\','/')]=JsonData.HashBytes(File.ReadAllBytes(path));
            }
            foreach(string child in Directory.GetDirectories(folder))if(Path.GetFileName(child) is not (".git" or ".confectory" or "bin" or "obj"))Walk(child);
        }
        Walk(root);return JsonData.Digest(files);
    }
}
