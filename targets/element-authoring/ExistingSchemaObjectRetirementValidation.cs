using Confectory.Core;
using System.Text;
using System.Text.Json.Nodes;

// Only unregister a pure, unreachable data object. The retained original is
// checked, never deleted. Every observed declaration/body is tied to Confirm.
internal static class ExistingSchemaObjectRetirementValidation
{
    internal static JsonObject Check(string originalProject,string candidateProject,JsonArray changes,string target,Func<Element,string> format,Func<Manifest,string> formatManifest)
    {
        JsonObject No()=>new(){["eligible"]=false};
        var comparison=OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal;
        var comparer=OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal;
        string root=Path.GetDirectoryName(Path.GetFullPath(originalProject))!,copy=Path.GetDirectoryName(Path.GetFullPath(candidateProject))!;
        originalProject=Path.GetFullPath(originalProject);candidateProject=Path.GetFullPath(candidateProject);
        var observed=new Dictionary<string,byte[]>(comparer);long bytes=0;
        string Owned(string directory,string relative){
            string full=Path.GetFullPath(Path.Combine(directory,relative));
            if(!string.Equals(PackPaths.Owned(directory,relative),full,comparison))throw new ArgumentException("Lexical owned source required");
            return full;
        }
        byte[] Read(string full){
            for(FileSystemInfo? f=new FileInfo(full);f is not null;f=f is FileInfo file?file.Directory:((DirectoryInfo)f).Parent)
                if(f.LinkTarget is not null)throw new ArgumentException("Linked source refused");
            var info=new FileInfo(full);
            if(!info.Exists||info.Length>1048576)throw new ArgumentException("Bounded source required");
            return File.ReadAllBytes(full);
        }
        byte[] Observe(string path){
            if(observed.TryGetValue(path,out var prior))return prior;
            byte[] value=Read(path);bytes+=value.Length;
            if(observed.Count>=235||bytes>16*1048576)throw new ArgumentException("Retirement proof budget");
            observed.Add(path,value);return value;
        }
        string Text(byte[] raw)=>new UTF8Encoding(false,true).GetString(raw,raw.AsSpan().StartsWith(new byte[]{239,187,191})?3:0,raw.Length-(raw.AsSpan().StartsWith(new byte[]{239,187,191})?3:0));
        byte[] CandidateRead(string path){
            if(string.Equals(path,candidateProject,comparison))return Read(path);
            if(path.StartsWith(copy+Path.DirectorySeparatorChar,comparison)){
                byte[] before=Observe(Owned(root,Path.GetRelativePath(copy,path))),after=Read(path);
                if(!before.AsSpan().SequenceEqual(after))throw new ArgumentException("Candidate source differs");
                return after;
            }
            return Observe(path);
        }
        try{
            if(changes.Count!=8)return No();
            string S(int i)=>changes[i]!.GetValue<string>();
            byte[] oldManifest=Observe(originalProject);
            var manifest=new Parser(Text(oldManifest),originalProject).ParseManifest();
            if(manifest.Kind!="project")return No();
            string prefix=manifest.Namespace+"::";
            int m=S(0)==prefix+"ProjectManifest"?0:S(4)==prefix+"ProjectManifest"?4:-1;if(m<0)return No();int c=4-m;
            string id=S(c),path=S(c+1);
            if(S(m+1)!=Path.GetFileName(originalProject)||S(m+2)!=JsonData.HashBytes(oldManifest)||!id.StartsWith(prefix,StringComparison.Ordinal)||S(c+2)=="missing")return No();
            string local=id[prefix.Length..];
            if(!manifest.Elements.TryGetValue(local,out var locator)||locator.Kind!="object"||locator.Path!=path)return No();
            byte[] retained=Observe(Owned(root,path));
            if(JsonData.HashBytes(retained)!=S(c+2)||Text(retained)!=S(c+3)||!retained.AsSpan().SequenceEqual(CandidateRead(Owned(copy,path))))return No();
            var next=new Parser(S(m+3),"<reviewed-registration>").ParseManifest();
            manifest.Elements.Remove(local);
            if(formatManifest(manifest)!=formatManifest(next))return No();
            var stats=new BuildStatistics();
            var original=new Registry(originalProject,new Documents("",stats,Observe),stats);
            var candidate=new Registry(candidateProject,new Documents("",stats,CandidateRead),stats);
            // Prepare may only relocate registry paths, not change their authority.
            if(candidate.Packs.Count!=original.Packs.Count||original.Paths.Any(p=>p.Key!=original.Project.Namespace&&(!candidate.Paths.TryGetValue(p.Key,out var other)||!string.Equals(p.Value,other,comparison))))return No();
            foreach(var (ns,registration) in original.Project.Registry)
                if(!string.Equals(Path.GetFullPath(Path.Combine(root,registration.Path)),original.Paths[ns],comparison))return No();
            candidate.Project.Registry=next.Registry;
            if(formatManifest(candidate.Project)!=formatManifest(next))return No();
            var e=original.Get(id,"object");
            var pure=new Element{Kind="object",Id=id,Parent=e.Parent,Uses=e.Uses,Data=e.Data,Description=e.Description,DescriptionPresent=e.DescriptionPresent};
            if(format(e)!=format(pure)||e.Data.Values.Any(d=>d.Kind!="general"))return No();
            // Direct primitive schema or one direct pure parent; no executable or
            // reference-bearing inheritance is eligible.
            Element owner=e;
            if(e.Parent is string parent){
                if(!parent.StartsWith(prefix,StringComparison.Ordinal)||e.Uses.Count!=0)return No();
                owner=original.Get(parent,"object");
                if(owner.Parent is not null||owner.Data.Values.Any(d=>d.Kind!="general")||format(owner)!=format(new Element{Kind="object",Id=owner.Id,Uses=owner.Uses,Data=owner.Data,Description=owner.Description,DescriptionPresent=owner.DescriptionPresent}))return No();
            }
            if(owner.Uses.Count!=1||owner.Uses[0].Kind!="schema"||!owner.Uses[0].Id.StartsWith(prefix,StringComparison.Ordinal))return No();
            var schema=original.Get(owner.Uses[0].Id,"schema");
            if(schema.Parent is not null||schema.Fields.Count==0||schema.Fields.Values.Any(f=>f.Kind!="general"||f.Cardinality!="single")||format(schema)!=format(new Element{Kind="schema",Id=schema.Id,Fields=schema.Fields,Description=schema.Description,DescriptionPresent=schema.DescriptionPresent}))return No();
            SchemaContracts.Validate(original,id);
            if(!next.Targets.ContainsKey(target))return No();
            RegistryValidation.Validate(candidate,target);
            // Use the same Planner.Plan as Build for every declared target.
            // Any reached removed ID or changed binding requires normal validation.
            foreach(string t in next.Targets.Keys.OrderBy(t=>t==target?0:1)){
                var before=new Planner(original,t).Plan();
                Planner after;
                try{after=new Planner(candidate,t).Plan();}
                catch(BuildError error) when(t==target&&before.Reached.Contains(id)&&error.Diagnostic.Code=="MISSING_ELEMENT"&&error.Diagnostic.Message=="No declaration for "+id){
                    return new JsonObject{["eligible"]=false,["invalid"]=true,["message"]=error.Diagnostic.Message};
                }
                if(before.Reached.Contains(id)||!before.Reached.SetEquals(after.Reached)||!before.Implementations.Keys.ToHashSet(StringComparer.Ordinal).SetEquals(after.Implementations.Keys)||JsonData.Digest(before.Bindings.Values.OrderBy(b=>b.Owner).ThenBy(b=>b.Function).ToArray())!=JsonData.Digest(after.Bindings.Values.OrderBy(b=>b.Owner).ThenBy(b=>b.Function).ToArray()))return No();
                var selected=candidate.Get(next.Targets[t].Id,"buildtarget",next.Namespace+"::<project>");
                new Planner(candidate,t).Structural(selected.Id);
            }
            // Check all retained declarations and physical bodies, including
            // Blueprint node records. Unclear textual references fall back.
            bool Mentions(byte[] raw)=>Text(raw).Contains(local,StringComparison.Ordinal);
            foreach(var (ns,pack) in candidate.Packs)
            foreach(var (key,loc) in pack.Elements){
                string elementId=ns+"::"+key;
                string directory=Path.GetDirectoryName(candidate.Paths[ns])!;
                if(Mentions(CandidateRead(Owned(directory,loc.Path))))return No();
                var declaration=candidate.Get(elementId);
                foreach(var body in declaration.Bodies.Values){
                    string bodyRoot=Path.GetDirectoryName(candidate.Paths[PackPaths.Namespace(body.Origin)])!;
                    string bodyPath=Owned(bodyRoot,body.Path);byte[] raw=CandidateRead(bodyPath);
                    if(Mentions(raw))return No();
                    if(body.SourceKind!="blueprint")continue;
                    var graph=JsonNode.Parse(Text(raw))!.AsObject();
                    if(graph.ToJsonString().Contains(local,StringComparison.Ordinal))return No();
                    RuntimeObjectContracts.ForGraph(candidate,elementId,graph);
                    foreach(var node in BlueprintTree.Nodes(graph)){
                        if(node.Node["kind"]?.ToString()!="code"||node.Node["implementation"] is not JsonValue file)continue;
                        byte[] record=CandidateRead(Owned(Path.GetDirectoryName(bodyPath)!,file.GetValue<string>()));
                        if(Mentions(record)||JsonNode.Parse(Text(record))!.ToJsonString().Contains(local,StringComparison.Ordinal))return No();
                    }
                }
            }
            foreach(var row in observed)if(!row.Value.AsSpan().SequenceEqual(Read(row.Key)))throw new InvalidOperationException("Retirement proof source changed");
            return new JsonObject{["eligible"]=true,["checks"]=new JsonArray(new JsonObject{["path"]=Path.GetFileName(originalProject),["hash"]=S(m+2)},new JsonObject{["path"]=path,["hash"]=S(c+2)}),["reads"]=new JsonArray(observed.Where(p=>!string.Equals(p.Key,originalProject,comparison)&&!string.Equals(p.Key,Owned(root,path),comparison)).Select(p=>(JsonNode)new JsonObject{["path"]=p.Key,["hash"]=JsonData.HashBytes(p.Value)}).ToArray())};
        }catch(Exception error) when(error is BuildError or ArgumentException or IOException or UnauthorizedAccessException or InvalidOperationException or System.Text.Json.JsonException or KeyNotFoundException){return No();}
    }
}
