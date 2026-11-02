using Confectory.Core;
using System.Text;
using System.Text.Json.Nodes;

// The external function is an existing registered declaration, never a draft
// member or a provider selection. Preserve both text and raw-file observations.
internal static class BlueprintPublicReturnContract
{
    static string Hash(string value)=>JsonData.HashBytes(Encoding.UTF8.GetBytes(value));
    public static JsonObject Query(JsonObject request)
    {
        string action=request["action"]!.GetValue<string>(),project=request["project"]!.GetValue<string>(),text=request["text"]!.GetValue<string>(),manifest=request["manifest"]!.GetValue<string>();
        var owner=new Parser(text,"<public-return-owner>").ParseElement();
        if(action=="validateReturnContract"){Validate(request["snapshot"]!.AsObject(),owner,manifest,text);return new(){["valid"]=true};}
        if(action is not ("readReturnContract" or "verifyReturnContract"))throw new ArgumentException("Explicit public return contract observation required");
        var declaration=new Parser(manifest,"<registered-return-project>").ParseManifest();
        if(owner.Kind!="implementation"||PackPaths.Namespace(owner.Id)!=declaration.Namespace||!declaration.Elements.TryGetValue(owner.Id[(declaration.Namespace.Length+2)..],out var source)||source.Kind!="implementation")throw new ArgumentException("Existing owned implementation registration required");
        string ownerPath=PackPaths.Owned(Path.GetDirectoryName(Path.GetFullPath(project))!,source.Path);
        foreach(string path in new[]{Path.GetFullPath(project),ownerPath})for(FileSystemInfo? file=new FileInfo(path);file is not null;file=file is FileInfo f?f.Directory:((DirectoryInfo)file).Parent)if(file.LinkTarget is not null)throw new ArgumentException("Public return source observations cannot traverse links");
        if(new FileInfo(project).Length>1048576||new FileInfo(ownerPath).Length>1048576||File.ReadAllText(project,new UTF8Encoding(false,true))!=manifest||File.ReadAllText(ownerPath,new UTF8Encoding(false,true))!=text)throw new InvalidOperationException("Owned registration changed before reading the external return contract; retain input");
        var result=BlueprintCallableContracts.Query(new(){["action"]="read",["project"]=project,["manifest"]=manifest,["text"]=text,["sourceId"]=owner.Id,["id"]=owner.Function});
        var observations=new JsonArray();int bytes=0;
        foreach(var observed in result["observations"]!.AsArray().OrderBy(r=>r!["path"]!.ToString(),StringComparer.Ordinal)){
            string path=observed!["path"]!.GetValue<string>();byte[] raw=File.ReadAllBytes(path);string current=File.ReadAllText(path,new UTF8Encoding(false,true));
            bytes=checked(bytes+raw.Length);if(bytes>2097152||Hash(current)!=observed["hash"]!.ToString())throw new InvalidOperationException("Registered public return declaration changed while reading");
            observations.Add(new JsonObject{["path"]=path,["hash"]=JsonData.HashBytes(raw),["textHash"]=Hash(current)});
        }
        var snapshot=new JsonObject{["version"]=1,["source"]=owner.Id,["id"]=owner.Function,["ownerHash"]=Hash(text),["manifestHash"]=Hash(manifest),["text"]=result["text"]!.DeepClone(),["receipt"]=result["receipt"]!.DeepClone(),["observations"]=observations};
        Validate(snapshot,owner,manifest,text);
        if(action=="verifyReturnContract"&&!JsonNode.DeepEquals(snapshot,request["snapshot"]))throw new InvalidOperationException("Registered public return contract changed; preserve input and explicitly refresh");
        return new(){["snapshot"]=snapshot,["registeredBytes"]=bytes,["bodyReads"]=0,["readOnly"]=true};
    }
    public static Element Validate(JsonObject snapshot,Element owner,string manifestText,string ownerText)
    {
        var manifest=new Parser(manifestText,"<return-project>").ParseManifest();string ns=PackPaths.Namespace(owner.Function!);
        if(owner.Kind!="implementation"||manifest.Kind!="project"||PackPaths.Namespace(owner.Id)!=manifest.Namespace||ns==manifest.Namespace||!manifest.Dependencies.ContainsKey(ns)||!manifest.Registry.ContainsKey(ns)||!manifest.Elements.TryGetValue(owner.Id[(manifest.Namespace.Length+2)..],out var locator)||locator.Kind!="implementation")throw new ArgumentException("Existing directly registered function and owned implementation required");
        if(snapshot.Count!=8||snapshot.Any(p=>p.Key is not ("version" or "source" or "id" or "ownerHash" or "manifestHash" or "text" or "receipt" or "observations"))||snapshot["version"]?.GetValue<int>()!=1||snapshot["source"]?.ToString()!=owner.Id||snapshot["id"]?.ToString()!=owner.Function||snapshot["ownerHash"]?.ToString()!=Hash(ownerText)||snapshot["manifestHash"]?.ToString()!=Hash(manifestText)||Encoding.UTF8.GetByteCount(snapshot.ToJsonString())>2097152)throw new ArgumentException("Exact public return contract receipt required");
        return ValidateSource(snapshot,owner,manifestText);
    }
    static Element ValidateSource(JsonObject snapshot,Element owner,string manifestText)
    {
        string text=snapshot["text"]!.GetValue<string>();var feature=new Parser(text,"<registered-return-contract>").ParseElement();
        if(feature.Kind!="function"||feature.Id!=owner.Function||feature.Signature is null||owner.Signature is null||!owner.Signature.Matches(feature.Signature)||!BlueprintExecutionBranches.Has(feature))throw new ArgumentException("Preserve the existing registered public execution contract");
        _=BlueprintExecutionBranches.Read(feature);
        var receipt=snapshot["receipt"]!.AsObject();var observations=snapshot["observations"]!.AsArray();
        if(receipt.Count!=4||receipt["id"]?.ToString()!=feature.Id||receipt["ownerManifestHash"]?.ToString()!=Hash(manifestText)||receipt["textHash"]?.ToString()!=Hash(text)||observations.Count!=2)throw new ArgumentException("Exact direct function receipt and two declaration observations required");
        var paths=new HashSet<string>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);
        foreach(var row in observations){var proof=row!.AsObject();string path=proof["path"]!.GetValue<string>();if(proof.Count!=3||proof.Any(p=>p.Key is not ("path" or "hash" or "textHash"))||!Path.IsPathFullyQualified(path)||Path.GetFullPath(path)!=path||!paths.Add(path)||new[]{"hash","textHash"}.Any(k=>!System.Text.RegularExpressions.Regex.IsMatch(proof[k]?.ToString()??"",@"\A[a-f0-9]{64}\z")))throw new ArgumentException("Exact read-only registered declaration observation required");}
        if(!observations.Any(r=>r!["textHash"]?.ToString()==Hash(text))||!observations.Any(r=>r!["textHash"]?.ToString()==receipt["manifestHash"]?.ToString()))throw new ArgumentException("Retain the registered function and manifest observations");
        return feature;
    }
}
