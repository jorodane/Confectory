using Confectory.Core;
using System.Text;
using System.Text.Json.Nodes;

// Registered ancestors are observations, never writable workspace members.
// Re-derive every path through the existing registry before final source CAS.
internal static class BlueprintOverrideContracts
{
    static string Hash(string text)=>JsonData.HashBytes(Encoding.UTF8.GetBytes(text));
    public static JsonObject Query(JsonObject request)
    {
        if(request["action"]?.ToString() is "validateGroup" or "verifyGroup")return Group(request);
        string action=request["action"]!.GetValue<string>(),text=request["text"]!.GetValue<string>(),id=request["id"]!.GetValue<string>(),target=request["target"]!.GetValue<string>();
        var child=new Parser(text,"<owned-override>").ParseElement();
        if(child.Kind!="implementation"||child.Id!=id||!child.Bodies.TryGetValue(target,out var body)||body.SourceKind!="blueprint"||body.Origin!=id)throw new ArgumentException("Explicitly owned override target required");
        if(action=="validate") { Validate(request["snapshot"]!.AsObject(),child,target,text);return new(){["valid"]=true}; }
        if(action is not ("read" or "verify"))throw new ArgumentException("Explicit override observation operation required");
        string project=Path.GetFullPath(request["project"]!.GetValue<string>());
        var registry=new Registry(project,new Documents(Path.Combine(Path.GetDirectoryName(project)!,".confectory","document-cache"),new BuildStatistics()),new BuildStatistics());
        if(PackPaths.Namespace(id)!=registry.Project.Namespace)throw new ArgumentException("Owned project override required");
        var observations=new SortedDictionary<string,JsonObject>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);int bytes=0;
        string Read(string path){
            path=Path.GetFullPath(path);for(FileSystemInfo? file=new FileInfo(path);file is not null;file=file is FileInfo f?f.Directory:((DirectoryInfo)file).Parent)if(file.LinkTarget is not null)throw new ArgumentException("Override observations cannot traverse links");
            var info=new FileInfo(path);if(!info.Exists||info.Length>1048576)throw new ArgumentException("Bounded registered override declaration required");
            byte[] raw=File.ReadAllBytes(path);string hash=JsonData.HashBytes(raw);string value=File.ReadAllText(path,new UTF8Encoding(false,true));
            if(observations.TryGetValue(path,out var prior)){if(prior["hash"]!.ToString()!=hash||prior["textHash"]!.ToString()!=Hash(value))throw new InvalidOperationException("Override dependency changed while reading");return value;}
            bytes=checked(bytes+raw.Length);if(bytes>2097152||observations.Count>=128)throw new ArgumentException("Override observation budget exceeded");
            observations[path]=new(){["path"]=path,["hash"]=hash,["textHash"]=Hash(value)};return value;
        }
        void Manifest(string ns){Read(registry.Paths[ns]);}
        Manifest(registry.Project.Namespace);var published=registry.Get(id,"implementation");
        if(Read(published.Loc.File)!=text)throw new InvalidOperationException("Confirm the owned override declaration before entering its body");
        var ancestors=new JsonObject();var seen=new HashSet<string>(StringComparer.Ordinal){id};var current=child;
        var declarations=new List<Element>{child};bool registered=false;
        while(current.Parent is string parent){
            if(!seen.Add(parent)||seen.Count>64)throw new ArgumentException("Bounded acyclic override ancestry required");
            current=registry.Get(parent,"implementation",current.Id);Manifest(PackPaths.Namespace(parent));string value=Read(current.Loc.File);
            ancestors[parent]=new JsonObject{["text"]=value,["path"]=Path.GetFullPath(current.Loc.File)};declarations.Add(current);registered|=PackPaths.Namespace(parent)!=registry.Project.Namespace;
        }
        if(!registered)throw new ArgumentException("A registered ancestor observation is required");
        registry.Effective(id); // Preserve the existing inheritance/override contract.
        // Function and inherited import headers affect the same generated body.
        foreach(var declaration in declarations)foreach(string function in declaration.Imports.Values.Select(v=>v.Id).Append(declaration.Function!).Distinct(StringComparer.Ordinal)){
            var fn=registry.Get(function,"function",declaration.Id);var functionSeen=new HashSet<string>(StringComparer.Ordinal);
            while(true){if(!functionSeen.Add(fn.Id)||functionSeen.Count>16)throw new ArgumentException("Bounded function ancestry required");Manifest(PackPaths.Namespace(fn.Id));Read(fn.Loc.File);if(fn.Parent is not string parent)break;fn=registry.Get(parent,"function",fn.Id);}
        }
        foreach(string path in observations.Keys.ToArray())Read(path);
        var snapshot=new JsonObject{["version"]=1,["id"]=id,["target"]=target,["ownerHash"]=Hash(text),["ancestors"]=ancestors,["observations"]=new JsonArray(observations.Values.Select(v=>(JsonNode)v.DeepClone()).ToArray())};
        Validate(snapshot,child,target,text);
        if(action=="verify"&&!JsonNode.DeepEquals(snapshot,request["snapshot"]))throw new InvalidOperationException("Registered override dependency changed or receipt is missing; preserve every input and explicitly refresh");
        return new(){["snapshot"]=snapshot,["registeredBytes"]=bytes,["bodyReads"]=0,["readOnly"]=true};
    }
    static JsonObject Group(JsonObject request)
    {
        var units=request["units"]!.AsObject();var selected=request["selected"]?.AsArray();bool verify=request["action"]!.ToString()=="verifyGroup";
        var reads=new SortedDictionary<string,JsonNode>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);
        foreach(var flow in units){
            if(flow.Value?["nodeFlowOrigin"] is not JsonObject origin)continue;
            var group=flow.Value["atomicEditGroup"]?.AsArray()??throw new ArgumentException("Complete internal flow group required");
            if(selected is not null&&!selected.Any(s=>group.Any(m=>m!.ToString()==s!.ToString())))continue;
            int marker=flow.Key.IndexOf("/body:",StringComparison.Ordinal);if(marker<0)throw new ArgumentException("Owned body target required");string id=flow.Key[..marker],target=flow.Key[(marker+6)..],text=units[id]?["draft"]?.GetValue<string>()??throw new ArgumentException("Retain the owned override declaration");
            var child=new Parser(text,"<retained-override>").ParseElement();var seen=new HashSet<string>(StringComparer.Ordinal){id};var current=child;bool required=false;
            while(current.Parent is string parent){
                if(!seen.Add(parent)||seen.Count>64)throw new ArgumentException("Bounded override source closure required");
                if(PackPaths.Namespace(parent)!=PackPaths.Namespace(id)){required=true;break;}
                current=new Parser(units[parent]?["draft"]?.GetValue<string>()??throw new ArgumentException("Retain the complete owned ancestor group"),"<retained-parent>").ParseElement();
            }
            if(origin["registeredAncestry"] is not JsonObject snapshot){if(required)throw new ArgumentException("Saved registered override receipt missing; retain the original checkpoint");continue;}
            Validate(snapshot,child,target,text);
            foreach(var ancestor in snapshot["ancestors"]!.AsObject())if(PackPaths.Namespace(ancestor.Key)==PackPaths.Namespace(id)&&units[ancestor.Key]?["draft"]?.ToString()!=ancestor.Value!["text"]!.ToString())throw new ArgumentException("Retain the observed owned ancestor source");
            if(verify)Query(new(){["action"]="verify",["project"]=request["project"]!.DeepClone(),["id"]=id,["text"]=text,["target"]=target,["snapshot"]=snapshot.DeepClone()});
            foreach(var observation in snapshot["observations"]!.AsArray()){
                string path=observation!["path"]!.ToString();var row=new JsonObject{["path"]=path,["hash"]=observation["hash"]!.DeepClone()};
                if(reads.TryGetValue(path,out var prior)&&!JsonNode.DeepEquals(prior,row))throw new InvalidOperationException("Override dependency versions differ; preserve all input");reads[path]=row;
            }
        }
        if(reads.Count>128)throw new ArgumentException("Combined override observation budget exceeded");
        return new(){["reads"]=new JsonArray(reads.Values.Select(v=>v.DeepClone()).ToArray()),["readOnly"]=true};
    }
    static void Validate(JsonObject snapshot,Element child,string target,string text)
    {
        if(snapshot.Count!=6||snapshot.Any(p=>p.Key is not ("version" or "id" or "target" or "ownerHash" or "ancestors" or "observations"))||snapshot["version"]?.GetValue<int>()!=1||snapshot["id"]?.ToString()!=child.Id||snapshot["target"]?.ToString()!=target||snapshot["ownerHash"]?.ToString()!=Hash(text)||Encoding.UTF8.GetByteCount(snapshot.ToJsonString())>2097152)throw new ArgumentException("Exact bounded registered override receipt required");
        var ancestors=snapshot["ancestors"]!.AsObject();var observations=snapshot["observations"]!.AsArray();if(ancestors.Count is <1 or >63||observations.Count is <1 or >128)throw new ArgumentException("Complete override observation required");
        var paths=new Dictionary<string,JsonNode>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);
        foreach(var row in observations){var proof=row!.AsObject();string path=proof["path"]!.GetValue<string>();if(proof.Count!=3||proof.Any(p=>p.Key is not ("path" or "hash" or "textHash"))||!Path.IsPathFullyQualified(path)||Path.GetFullPath(path)!=path||!paths.TryAdd(path,proof)||new[]{"hash","textHash"}.Any(k=>!System.Text.RegularExpressions.Regex.IsMatch(proof[k]?.ToString()??"",@"\A[a-f0-9]{64}\z")))throw new ArgumentException("Exact read-only dependency observation required");}
        var seen=new HashSet<string>(StringComparer.Ordinal){child.Id};var current=child;bool registered=false;
        while(current.Parent is string parent){
            if(!seen.Add(parent)||seen.Count>64||ancestors[parent] is not JsonObject row||row.Count!=2||row.Any(p=>p.Key is not ("text" or "path"))||!paths.TryGetValue(row["path"]!.ToString(),out var observed)||observed["textHash"]?.ToString()!=Hash(row["text"]!.GetValue<string>()))throw new ArgumentException("Complete ordered ancestor source receipt required");
            var next=new Parser(row["text"]!.GetValue<string>(),"<observed-ancestor>").ParseElement();if(next.Kind!="implementation"||next.Id!=parent||next.Function!=child.Function||!child.Signature!.Matches(next.Signature))throw new ArgumentException("Preserve the inherited public contract");current=next;registered|=PackPaths.Namespace(parent)!=PackPaths.Namespace(child.Id);
        }
        if(!registered||ancestors.Count!=seen.Count-1)throw new ArgumentException("Exact registered ancestor receipt required");
    }
}
