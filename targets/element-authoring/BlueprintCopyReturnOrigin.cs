using Confectory.Core;
using System.Text;
using System.Text.Json.Nodes;

// A first-save copy observes its selected donor through the existing registry.
// Saved paths are evidence only; verification never reads through those paths.
internal static class BlueprintCopyReturnOrigin
{
    static string Hash(string text)=>JsonData.HashBytes(Encoding.UTF8.GetBytes(text));
    public static string Identity(JsonObject origin)=>Hash(origin.ToJsonString());
    public static JsonObject Create(JsonObject snapshot,JsonObject current)=>new(){
        ["version"]=1,["owner"]=snapshot["owner"]!.DeepClone(),["implementation"]=snapshot["implementation"]!.DeepClone(),
        ["feature"]=snapshot["feature"]!.DeepClone(),["source"]=snapshot["source"]!.DeepClone(),["target"]=snapshot["target"]!.DeepClone(),
        ["ownerHash"]=snapshot["ownerHash"]!.DeepClone(),["featureSource"]=snapshot["featureSource"]!.DeepClone(),
        ["bodyOrigin"]=snapshot["bodyOrigin"]!.DeepClone(),["sourceKind"]=snapshot["sourceKind"]!.DeepClone(),["observations"]=current["observations"]!.DeepClone()};
    public static Element Validate(JsonObject origin,Element copy,Element owner,string ownerText,string manifestText,JsonObject graph)
    {
        var manifest=new Parser(manifestText,"<first-copy-project>").ParseManifest();string feature=graph["feature"]!.ToString(),ns=PackPaths.Namespace(feature);
        if(origin.Count!=11||origin.Any(p=>p.Key is not ("version" or "owner" or "implementation" or "feature" or "source" or "target" or "ownerHash" or "featureSource" or "bodyOrigin" or "sourceKind" or "observations"))||origin["version"]?.GetValue<int>()!=1||Encoding.UTF8.GetByteCount(origin.ToJsonString())>2097152||owner.Kind!="schema"||manifest.Kind!="project"||PackPaths.Namespace(owner.Id)!=manifest.Namespace||PackPaths.Namespace(copy.Id)!=manifest.Namespace||ns==manifest.Namespace||!manifest.Dependencies.ContainsKey(ns)||!manifest.Registry.ContainsKey(ns)||!manifest.Elements.TryGetValue(owner.Id[(manifest.Namespace.Length+2)..],out var declared)||declared.Kind!=owner.Kind||origin["owner"]?.ToString()!=owner.Id||origin["ownerHash"]?.ToString()!=Hash(ownerText)||origin["implementation"]?.ToString()!=copy.Id||origin["feature"]?.ToString()!=feature||copy.Function!=feature||copy.Parent is not null)throw new ArgumentException("Exact owned first-copy and registered function observation required");
        var provenance=graph["copySource"]??throw new ArgumentException("Retain first-copy provenance");
        if(origin["source"]?.ToString()!=provenance["implementation"]?.ToString()||origin["target"]?.ToString()!=provenance["target"]?.ToString()||origin["bodyOrigin"]?.ToString()!=provenance["bodyOrigin"]?.ToString()||origin["sourceKind"]?.ToString()!=provenance["sourceKind"]?.ToString()||!copy.Bodies.TryGetValue(origin["target"]!.ToString(),out var body)||body.SourceKind!="blueprint")throw new ArgumentException("Preserve the exact selected donor and target");
        var fn=new Parser(origin["featureSource"]!.GetValue<string>(),"<first-copy-contract>").ParseElement();
        if(fn.Kind!="function"||fn.Id!=feature||fn.Parent is not null||copy.Signature is null||fn.Signature is null||!copy.Signature.Matches(fn.Signature)||!BlueprintExecutionBranches.Has(fn)||graph["contractHash"]?.ToString()!=FeatureBlueprint.ContractHash(fn))throw new ArgumentException("Preserve the registered public execution contract");
        _=BlueprintExecutionBranches.Read(fn);
        var rows=origin["observations"]!.AsArray();var paths=new HashSet<string>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);
        if(rows.Count is <3 or >64)throw new ArgumentException("Complete bounded first-copy observations required");
        foreach(var row in rows){string path=row?["path"]?.ToString()??"";if(row is not JsonObject item||item.Count!=2||item.Any(p=>p.Key is not ("path" or "sha256"))||!Path.IsPathFullyQualified(path)||Path.GetFullPath(path)!=path||!paths.Add(path)||!System.Text.RegularExpressions.Regex.IsMatch(item["sha256"]?.ToString()??"",@"\A[a-f0-9]{64}\z"))throw new ArgumentException("Exact first-copy source observation required");}
        return fn;
    }
    public static void Verify(JsonObject origin,Element copy,Element owner,string ownerText,string manifestText,JsonObject graph,string project,Func<Element,string> format)
    {
        Validate(origin,copy,owner,ownerText,manifestText,graph);
        var manifest=new Parser(manifestText,"<first-copy-registration>").ParseManifest();string root=Path.GetDirectoryName(Path.GetFullPath(project))!;string path=PackPaths.Owned(root,manifest.Elements[owner.Id[(manifest.Namespace.Length+2)..]].Path);
        foreach(string filePath in new[]{Path.GetFullPath(project),path})for(FileSystemInfo? entry=new FileInfo(filePath);entry is not null;entry=entry is FileInfo f?f.Directory:((DirectoryInfo)entry).Parent)if(entry.LinkTarget is not null)throw new ArgumentException("First-copy source cannot traverse links");
        if(new FileInfo(project).Length>1048576||new FileInfo(path).Length>1048576||File.ReadAllText(project,new UTF8Encoding(false,true))!=manifestText||File.ReadAllText(path,new UTF8Encoding(false,true))!=ownerText)throw new InvalidOperationException("Original copy owner or registration changed; retain input");
        var observed=ImplementationCopy.Query(new(){["action"]="observe",["project"]=project,["owner"]=owner.Id,["ownerText"]=ownerText,["feature"]=origin["feature"]!.DeepClone(),["source"]=origin["source"]!.DeepClone(),["target"]=origin["target"]!.DeepClone(),["implementation"]=copy.Id},format);
        if(observed["featureSource"]?.ToString()!=origin["featureSource"]?.ToString()||observed["bodyOrigin"]?.ToString()!=origin["bodyOrigin"]?.ToString()||observed["sourceKind"]?.ToString()!=origin["sourceKind"]?.ToString()||!JsonNode.DeepEquals(observed["observations"],origin["observations"]))throw new InvalidOperationException("Selected copy sources changed; preserve the original receipt and input");
    }
}
