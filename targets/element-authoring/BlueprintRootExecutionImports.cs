using Confectory.Core;
using System.Text;
using System.Text.Json.Nodes;

// Registered import/scope headers are immutable evidence, never writable units.
// No body source is opened and no provider is selected by this observation.
internal static class BlueprintRootExecutionImports
{
    static string Hash(string text)=>JsonData.HashBytes(Encoding.UTF8.GetBytes(text));
    static readonly StringComparer Paths=OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal;
    static bool Digest(string? value)=>System.Text.RegularExpressions.Regex.IsMatch(value??"",@"\A[a-f0-9]{64}\z");
    static void Closure(Element owner,Func<string,string?,string,Element> get)
    {
        var seen=new HashSet<string>(StringComparer.Ordinal);
        void Visit(string id,string? kind,string source){
            var value=get(id,kind,source);if(!seen.Add(id))return;
            if(seen.Count>64)throw new ArgumentException("Bounded registered import/scope header closure required");
            if(value.Parent is string parent)Visit(parent,value.Kind,value.Id);
            // Structural context of a scoped import, including its existing
            // assignment headers, is observed without resolving a runtime call.
            foreach(var reference in value.Modules)Visit(reference.Id,"module",value.Id);
            foreach(var reference in value.Includes)Visit(reference.Id,"module",value.Id);
            foreach(var reference in value.Contains)Visit(reference.Id,reference.Kind,value.Id);
            foreach(var reference in value.Uses)Visit(reference.Id,reference.Kind??"schema",value.Id);
            foreach(string function in value.Requires.Keys.Concat(value.Provides.Keys).Concat(value.Defaults.Keys).Concat(value.Function is null?Array.Empty<string>():new[]{value.Function}))if(PackPaths.Namespace(function)!=PackPaths.Namespace(owner.Id))Visit(function,"function",value.Id);
            foreach(var reference in value.Provides.Values.Concat(value.Defaults.Values))Visit(reference.Id,"implementation",value.Id);
            foreach(var field in value.Fields.Values)if(field.Type.Contains("::",StringComparison.Ordinal))Visit(field.Type,field.Kind is "function" or "enum"?field.Kind:"schema",value.Id);
            foreach(var import in value.Imports.Values){
                if(PackPaths.Namespace(import.Id)!=PackPaths.Namespace(owner.Id))Visit(import.Id,"function",value.Id);
                if(import.Scope is string scope)Visit(scope,null,value.Id);
            }
        }
        if(owner.Parent is string parent)Visit(parent,"implementation",owner.Id);
        foreach(var import in owner.Imports.Values){
            if(PackPaths.Namespace(import.Id)!=PackPaths.Namespace(owner.Id))Visit(import.Id,"function",owner.Id);
            if(import.Scope is string scope)Visit(scope,null,owner.Id);
        }
    }
    public static JsonObject Query(JsonObject request)
    {
        string action=request["action"]!.ToString(),text=request["text"]!.GetValue<string>();var owner=new Parser(text,"<registered-root-owner>").ParseElement();
        if(action=="validateRootImports"){Validate(request["snapshot"]!.AsObject(),owner,text);return new(){["valid"]=true};}
        if(action is not ("readRootImports" or "verifyRootImports"))throw new ArgumentException("Explicit registered root observation operation required");
        string project=Path.GetFullPath(request["project"]!.ToString());var statistics=new BuildStatistics();
        var registry=new Registry(project,new Documents(Path.Combine(Path.GetDirectoryName(project)!,".confectory","document-cache"),statistics),statistics);
        if(owner.Kind!="implementation"||PackPaths.Namespace(owner.Id)!=registry.Project.Namespace)throw new ArgumentException("Existing owned implementation required");
        var observations=new SortedDictionary<string,JsonObject>(Paths);var headers=new JsonObject();var manifests=new JsonObject();int bytes=0;
        string Read(string path){
            path=Path.GetFullPath(path);for(FileSystemInfo? entry=new FileInfo(path);entry is not null;entry=entry is FileInfo file?file.Directory:((DirectoryInfo)entry).Parent)if(entry.LinkTarget is not null)throw new ArgumentException("Registered observations cannot traverse links");
            if(!File.Exists(path)||new FileInfo(path).Length>1048576)throw new ArgumentException("Bounded registered declaration required");
            byte[] raw=File.ReadAllBytes(path);using var reader=new StreamReader(new MemoryStream(raw),new UTF8Encoding(false,true),true);string value=reader.ReadToEnd();
            var proof=new JsonObject{["path"]=path,["hash"]=JsonData.HashBytes(raw),["textHash"]=Hash(value)};
            if(observations.TryGetValue(path,out var prior)){if(!JsonNode.DeepEquals(prior,proof))throw new InvalidOperationException("Registered header changed while reading; retain input");}
            else {bytes=checked(bytes+raw.Length);if(bytes>2097152||observations.Count>=128)throw new ArgumentException("Registered observation budget exceeded");observations[path]=proof;}
            return value;
        }
        void Manifest(string ns){if(manifests.ContainsKey(ns))return;string path=registry.Paths[ns];manifests[ns]=new JsonObject{["path"]=Path.GetFullPath(path),["text"]=Read(path)};}
        Manifest(registry.Project.Namespace);var published=registry.Get(owner.Id,"implementation");
        if(Read(published.Loc.File)!=text)throw new InvalidOperationException("Owned import declaration changed; retain input");
        Closure(owner,(id,kind,source)=>{var element=registry.Get(id,kind,source);Manifest(PackPaths.Namespace(id));string value=Read(element.Loc.File);if(!headers.ContainsKey(id))headers[id]=new JsonObject{["path"]=Path.GetFullPath(element.Loc.File),["text"]=value};return element;});
        bool foreign=headers.Any(p=>PackPaths.Namespace(p.Key)!=registry.Project.Namespace);
        if(!foreign){if(action=="verifyRootImports"&&request["snapshot"] is not null)throw new InvalidOperationException("Registered import observation disappeared");return new(){["snapshot"]=null,["bodyReads"]=0,["readOnly"]=true};}
        foreach(string path in observations.Keys.ToArray())Read(path);
        var snapshot=new JsonObject{["version"]=1,["id"]=owner.Id,["ownerHash"]=Hash(text),["project"]=project,["headers"]=headers,["manifests"]=manifests,["observations"]=new JsonArray(observations.Values.Select(v=>(JsonNode)v.DeepClone()).ToArray())};
        Validate(snapshot,owner,text);
        if(action=="verifyRootImports"&&!JsonNode.DeepEquals(snapshot,request["snapshot"]))throw new InvalidOperationException("Registered import/scope changed or receipt missing; retain input and explicitly refresh");
        return new(){["snapshot"]=snapshot,["registeredBytes"]=bytes,["bodyReads"]=0,["readOnly"]=true};
    }
    public static JsonObject Validate(JsonObject snapshot,Element owner,string text)
    {
        if(snapshot.Count!=7||snapshot.Any(p=>p.Key is not ("version" or "id" or "ownerHash" or "project" or "headers" or "manifests" or "observations"))||snapshot["version"]?.GetValue<int>()!=1||snapshot["id"]?.ToString()!=owner.Id||snapshot["ownerHash"]?.ToString()!=Hash(text)||owner.Kind!="implementation"||Encoding.UTF8.GetByteCount(snapshot.ToJsonString())>4194304)throw new ArgumentException("Exact bounded registered root receipt required");
        string project=snapshot["project"]!.GetValue<string>(),ns=PackPaths.Namespace(owner.Id);if(!Path.IsPathFullyQualified(project)||Path.GetFullPath(project)!=project)throw new ArgumentException("Canonical registered project path required");
        var headers=snapshot["headers"]!.AsObject();var manifests=snapshot["manifests"]!.AsObject();var observations=snapshot["observations"]!.AsArray();
        if(headers.Count is <1 or >64||manifests.Count is <2 or >65||observations.Count is <3 or >128)throw new ArgumentException("Complete registered header receipt required");
        var proofs=new Dictionary<string,JsonNode>(Paths);foreach(var node in observations){var row=node!.AsObject();string path=row["path"]!.ToString();if(row.Count!=3||row.Any(p=>p.Key is not ("path" or "hash" or "textHash"))||!Path.IsPathFullyQualified(path)||Path.GetFullPath(path)!=path||!Digest(row["hash"]?.ToString())||!Digest(row["textHash"]?.ToString())||!proofs.TryAdd(path,row))throw new ArgumentException("Exact raw registered observation required");}
        var usedPaths=new HashSet<string>(Paths);var usedManifests=new HashSet<string>(StringComparer.Ordinal);var usedHeaders=new HashSet<string>(StringComparer.Ordinal);var contracts=new JsonObject();
        string Proof(JsonNode node,string path){if(node is not JsonObject row||row.Count!=2||row.Any(p=>p.Key is not ("path" or "text"))||row["path"]?.ToString()!=path||!proofs.TryGetValue(path,out var proof)||proof["textHash"]?.ToString()!=Hash(row["text"]!.GetValue<string>()))throw new ArgumentException("Registered locator/text observation mismatch");usedPaths.Add(path);return row["text"]!.GetValue<string>();}
        var projectRow=manifests[ns]??throw new ArgumentException("Owned manifest receipt required");var ownManifest=new Parser(Proof(projectRow,project),"<root-import-project>").ParseManifest();
        if(ownManifest.Kind!="project"||ownManifest.Namespace!=ns)throw new ArgumentException("Exact owned project manifest required");
        Manifest Manifest(string key){usedManifests.Add(key);if(key==ns)return ownManifest;if(!ownManifest.Registry.TryGetValue(key,out var registration))throw new ArgumentException("Existing namespace registration required");string path=Path.GetFullPath(Path.Combine(Path.GetDirectoryName(project)!,registration.Path));var m=new Parser(Proof(manifests[key]??throw new ArgumentException("Registered manifest missing"),path),"<root-import-manifest>").ParseManifest();if(m.Kind!="pack"||m.Namespace!=key)throw new ArgumentException("Exact registered pack manifest required");return m;}
        var own=Manifest(ns);if(!own.Elements.TryGetValue(owner.Id[(ns.Length+2)..],out var locator)||locator.Kind!="implementation")throw new ArgumentException("Existing owned source locator required");string ownerPath=PackPaths.Owned(Path.GetDirectoryName(project)!,locator.Path);if(!proofs.TryGetValue(ownerPath,out var ownerProof)||ownerProof["textHash"]?.ToString()!=Hash(text))throw new ArgumentException("Owned import source receipt required");usedPaths.Add(ownerPath);
        Closure(owner,(id,kind,source)=>{string target=PackPaths.Namespace(id),origin=PackPaths.Namespace(source);if(target!=origin&&!Manifest(origin).Dependencies.ContainsKey(target))throw new ArgumentException("Registered import requires an existing direct dependency");var m=Manifest(target);if(!m.Elements.TryGetValue(id[(target.Length+2)..],out var loc)||kind is not null&&kind!=loc.Kind)throw new ArgumentException("Exact registered declaration kind required");string basePath=target==ns?project:manifests[target]!["path"]!.ToString();string path=PackPaths.Owned(Path.GetDirectoryName(basePath)!,loc.Path);string value=Proof(headers[id]??throw new ArgumentException("Registered header missing"),path);var element=new Parser(value,"<root-import-header>").ParseElement();if(element.Id!=id||element.Kind!=loc.Kind)throw new ArgumentException("Registered header identity mismatch");usedHeaders.Add(id);if(element.Kind=="function")contracts[id]=value;return element;});
        if(!usedHeaders.SetEquals(headers.Select(p=>p.Key))||!usedManifests.SetEquals(manifests.Select(p=>p.Key))||!usedPaths.SetEquals(proofs.Keys)||!usedHeaders.Any(id=>PackPaths.Namespace(id)!=ns))throw new ArgumentException("No missing/unrelated registered observations permitted");
        return contracts;
    }
    public static JsonObject Contracts(JsonObject units,string id)
    {
        var unit=units[id]!;var owner=new Parser(unit["draft"]!.ToString(),"<root-import-owner>").ParseElement();
        return unit["rootExecutionImports"] is JsonObject snapshot?Validate(snapshot,owner,unit["draft"]!.ToString()):new();
    }
    public static void Group(JsonObject request,SortedDictionary<string,JsonNode> reads)
    {
        var units=request["units"]!.AsObject();var selected=request["selected"]?.AsArray();
        foreach(var pair in units){var unit=pair.Value;if(unit?["rootContractGroup"] is not JsonArray group||unit["kind"]?.ToString()!="implementation"||selected is not null&&!selected.Any(s=>group.Any(m=>m!.ToString()==s!.ToString())))continue;
            string text=unit["draft"]!.ToString();var snapshot=unit["rootExecutionImports"] as JsonObject;
            // Re-query even an absent receipt: a registered dependency may be
            // reached transitively through a local scope/module header.
            if(request["action"]?.ToString()=="verifyGroup")Query(new(){["action"]="verifyRootImports",["project"]=request["project"]!.DeepClone(),["text"]=text,["snapshot"]=snapshot?.DeepClone()});
            if(snapshot is null)continue;
            _=Contracts(units,pair.Key);
            foreach(var proof in snapshot["observations"]!.AsArray()){string path=proof!["path"]!.ToString();var row=new JsonObject{["path"]=path,["hash"]=proof["hash"]!.DeepClone()};if(reads.TryGetValue(path,out var prior)&&!JsonNode.DeepEquals(prior,row))throw new InvalidOperationException("Registered execution observation versions differ");reads[path]=row;}
        }
    }
}
