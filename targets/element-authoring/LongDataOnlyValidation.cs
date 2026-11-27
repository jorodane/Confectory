using Confectory.Core;
using System.Text;
using System.Text.Json.Nodes;

// Conservative proof for one existing, directly owned data value.
// Reference overlay is limited to exact local leaf objects; all other changes
// keep the usual compile/link validation. The operation names stay compatible.
internal static class LongDataOnlyValidation
{
    internal static JsonObject Check(string originalProject,string? candidateProject,string id,string relative,string baseline,string after,Func<Element,string> format)
    {
        JsonObject No()=>new(){["eligible"]=false};
        originalProject=Path.GetFullPath(originalProject);
        bool overlay=candidateProject is null;
        string root=Path.GetDirectoryName(originalProject)!,candidateRoot=overlay?root:Path.GetDirectoryName(Path.GetFullPath(candidateProject!))!;
        var comparison=OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal;
        var comparer=OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal;
        var observed=new Dictionary<string,(string Text,string Hash)>(comparer);
        string Owned(string folder,string path){string lexical=Path.GetFullPath(Path.Combine(folder,path));if(!string.Equals(PackPaths.Owned(folder,path),lexical,OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal))throw new ArgumentException("Owned lexical source required");for(FileSystemInfo? n=new FileInfo(lexical);n is not null;n=n is FileInfo f?f.Directory:((DirectoryInfo)n).Parent)if(n.LinkTarget is not null)throw new ArgumentException("Linked source refused");return lexical;}
        (string Text,string Hash) Read(string path){var info=new FileInfo(path);if(!info.Exists||info.Length>1048576)throw new ArgumentException("Bounded source required");byte[] bytes=File.ReadAllBytes(path);return(new UTF8Encoding(false,true).GetString(bytes),JsonData.HashBytes(bytes));}
        // Classification refusal is not validation success. The caller falls
        // back to full compilation for all ambiguous or unsupported shapes.
        try{
            var ownerManifest=Read(originalProject);var manifest=new Parser(ownerManifest.Text,originalProject).ParseManifest();
            if(manifest.Kind!="project"||!id.StartsWith(manifest.Namespace+"::",StringComparison.Ordinal)||!manifest.Elements.TryGetValue(id[(manifest.Namespace.Length+2)..],out var loc)||loc.Kind!="object"||loc.Path!=relative)return No();
            string objectPath=Owned(root,relative);
            var original=Read(objectPath);
            if(original.Hash!=baseline||(!overlay&&Read(Owned(candidateRoot,relative)).Text!=after))throw new InvalidOperationException("Reviewed data source changed");
            var before=new Parser(original.Text,"<old-data>").ParseElement();var next=new Parser(after,"<new-data>").ParseElement();
            if(before.Id!=id||next.Id!=id||before.Kind!="object"||next.Kind!="object"||before.Parent is not null||before.Uses.Count!=1||before.Uses[0].Kind!="schema"||before.Data.Count!=next.Data.Count||before.Contains.Count!=0||before.Modules.Count!=0||before.Provides.Count!=0)return No();
            var differences=before.Data.Keys.Where(k=>!next.Data.TryGetValue(k,out var n)||before.Data[k].Kind!=n.Kind||before.Data[k].Scalar?.GetRawText()!=n.Scalar?.GetRawText()||before.Data[k].Reference!=n.Reference).ToArray();
            if(differences.Length!=1||!next.Data.TryGetValue(differences[0],out var newDatum))return No();
            string field=differences[0];var oldDatum=before.Data[field];
            bool reference=overlay&&oldDatum.Kind=="reference"&&newDatum.Kind=="reference"&&oldDatum.Reference is string oldTarget&&newDatum.Reference is string nextTarget&&oldTarget!=nextTarget;
            string scalarType="";
            if(!reference){
                if(oldDatum.Kind!="general"||newDatum.Kind!="general"||oldDatum.Scalar is not System.Text.Json.JsonElement oldScalar||newDatum.Scalar is not System.Text.Json.JsonElement newScalar)return No();
                if(oldScalar.ValueKind==System.Text.Json.JsonValueKind.Number&&newScalar.ValueKind==System.Text.Json.JsonValueKind.Number&&oldScalar.TryGetInt64(out long oldValue)&&newScalar.TryGetInt64(out long newValue)&&oldValue!=newValue)scalarType="long";
                else if(oldScalar.ValueKind==System.Text.Json.JsonValueKind.String&&newScalar.ValueKind==System.Text.Json.JsonValueKind.String&&oldScalar.GetString()!=newScalar.GetString())scalarType="string";
                else return No();
            }
            before.Data[field]=newDatum;if(format(before)!=format(next))return No();
            string schemaId=before.Uses[0].Id;if(!schemaId.StartsWith(manifest.Namespace+"::",StringComparison.Ordinal)||!manifest.Elements.TryGetValue(schemaId[(manifest.Namespace.Length+2)..],out var schemaLoc)||schemaLoc.Kind!="schema")return No();
            string schemaPath=Owned(root,schemaLoc.Path);
            var originalSchema=Read(schemaPath);if(!overlay&&originalSchema.Hash!=Read(Owned(candidateRoot,schemaLoc.Path)).Hash)throw new InvalidOperationException("Schema changed during candidate copy");
            var schema=new Parser(originalSchema.Text,"<data-schema>").ParseElement();
            if(schema.Id!=schemaId||schema.Kind!="schema"||schema.Parent is not null||!schema.Fields.TryGetValue(field,out var contract)||contract.Cardinality!="single")return No();
            if(!reference&&(schema.Fields.Values.Any(f=>f.Kind!="general"||f.Cardinality!="single")||contract.Type!=scalarType))return No();
            if(reference){
                // A reference edge is traversed even for inactive metadata by Planner.Visit.
                // Only exact local leaf objects with the same primitive schema may change here;
                // no executable, inherited, imported, nested-reference or provider edge.
                bool Pure(Element e)=>format(e)==format(new Element{Kind=e.Kind,Id=e.Id,Uses=e.Uses,Fields=e.Fields,Data=e.Data,Values=e.Values,Description=e.Description,DescriptionPresent=e.DescriptionPresent})&&e.Values.Keys.All(k=>k is "editorName" or "editorIcon");
                if(contract.Kind!="reference"||!Pure(before)||!Pure(schema)||schema.Uses.Count!=0||schema.Fields.Any(p=>p.Value.Cardinality!="single"||(p.Key!=field&&p.Value.Kind!="general"))||before.Data.Any(p=>p.Key!=field&&p.Value.Kind!="general"))return No();
                if(!contract.Type.StartsWith(manifest.Namespace+"::",StringComparison.Ordinal)||contract.Type==schemaId)return No();
                (string Text,string Hash) Capture(string target,string kind){
                    if(target==id||!target.StartsWith(manifest.Namespace+"::",StringComparison.Ordinal)||!manifest.Elements.TryGetValue(target[(manifest.Namespace.Length+2)..],out var targetLoc)||targetLoc.Kind!=kind)throw new ArgumentException("Local registered reference leaf required");
                    string path=Owned(root,targetLoc.Path);
                    if(path==objectPath||path==schemaPath||observed.ContainsKey(path))throw new ArgumentException("Distinct reference source required");
                    var raw=Read(path);observed.Add(path,raw);return raw;
                }
                var leafSchema=new Parser(Capture(contract.Type,"schema").Text,"<reference-schema>").ParseElement();
                if(leafSchema.Id!=contract.Type||leafSchema.Kind!="schema"||!Pure(leafSchema)||leafSchema.Uses.Count!=0||leafSchema.Data.Count!=0||leafSchema.Fields.Values.Any(f=>f.Kind!="general"||f.Cardinality!="single"))return No();
                foreach(string target in new[]{oldDatum.Reference!,newDatum.Reference!}){
                    var leaf=new Parser(Capture(target,"object").Text,"<reference-leaf>").ParseElement();
                    if(leaf.Id!=target||leaf.Kind!="object"||!Pure(leaf)||leaf.Fields.Count!=0||leaf.Uses.Count!=1||leaf.Uses[0].Kind!="schema"||leaf.Uses[0].Id!=contract.Type||leaf.Data.Values.Any(d=>d.Kind!="general"))return No();
                }
            }
            var stats=new BuildStatistics();Registry registry;
            if(overlay){
                // Registry and SchemaContracts operate on the same captured manifest
                // and schema bytes as the reviewed delta; only the object's text is
                // substituted. No candidate directory or persistent parser cache.
                if(!string.Equals(PackPaths.Resolve(originalProject),originalProject,comparison))return No();
                observed.Add(originalProject,ownerManifest);observed.Add(schemaPath,originalSchema);
                int bytes=observed.Values.Sum(v=>Encoding.UTF8.GetByteCount(v.Text));
                foreach(var entry in manifest.Registry.Values){
                    string path=Path.GetFullPath(Path.Combine(root,entry.Path));
                    if(!string.Equals(PackPaths.Resolve(path),path,comparison)||observed.ContainsKey(path)||string.Equals(path,objectPath,comparison)||observed.Count>=235)return No();
                    var entrySource=Read(path);bytes=checked(bytes+Encoding.UTF8.GetByteCount(entrySource.Text));if(bytes>16*1048576)return No();
                    observed.Add(path,entrySource);
                }
                byte[] Source(string path){
                    if(string.Equals(path,objectPath,comparison))return Encoding.UTF8.GetBytes(after);
                    if(!observed.TryGetValue(path,out var captured))throw new ArgumentException("Unobserved overlay source");
                    return Encoding.UTF8.GetBytes(captured.Text);
                }
                registry=new Registry(originalProject,new Documents("",stats,Source),stats);
            }else registry=new Registry(candidateProject!,new Documents(Path.Combine(Path.GetTempPath(),"confectory-data-validation",JsonData.Digest(candidateProject)),stats),stats);
            if(registry.Project.Namespace!=manifest.Namespace||!registry.Project.Elements.TryGetValue(id[(manifest.Namespace.Length+2)..],out var candidateObject)||candidateObject.Path!=relative||candidateObject.Kind!="object"||!registry.Project.Elements.TryGetValue(schemaId[(manifest.Namespace.Length+2)..],out var candidateSchema)||candidateSchema.Path!=schemaLoc.Path||candidateSchema.Kind!="schema"||registry.Get(id,"object").Id!=id)return No();
            SchemaContracts.Validate(registry,id);
            if(reference)foreach(string target in new[]{oldDatum.Reference!,newDatum.Reference!})SchemaContracts.Validate(registry,target);
            if(Read(originalProject).Hash!=ownerManifest.Hash||Read(Owned(root,relative)).Hash!=original.Hash||Read(Owned(root,schemaLoc.Path)).Hash!=originalSchema.Hash)throw new InvalidOperationException("Data validation sources changed");
            var proof=new JsonObject{["eligible"]=true,["checks"]=new JsonArray(new JsonObject{["path"]=Path.GetFileName(originalProject),["hash"]=ownerManifest.Hash},new JsonObject{["path"]=schemaLoc.Path,["hash"]=originalSchema.Hash})};
            if(reference)proof["reference"]=true;
            if(overlay){
                foreach(var source in observed)if(Read(source.Key).Hash!=source.Value.Hash)throw new InvalidOperationException("Data overlay source changed");
                proof["reads"]=new JsonArray(observed.Where(p=>!string.Equals(p.Key,originalProject,comparison)&&!string.Equals(p.Key,schemaPath,comparison)).Select(p=>(JsonNode)new JsonObject{["path"]=p.Key,["hash"]=p.Value.Hash}).ToArray());
            }
            return proof;
        }catch(BuildError){return No();}catch(ArgumentException){return No();}
    }
}
