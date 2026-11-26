using Confectory.Core;
using System.Text;
using System.Text.Json.Nodes;

// The conservative fast path for one existing, directly owned long value.
// Other changes keep the normal candidate compile/link validation.
internal static class LongDataOnlyValidation
{
    internal static JsonObject Check(string originalProject,string candidateProject,string id,string relative,string baseline,string after,Func<Element,string> format)
    {
        JsonObject No()=>new(){["eligible"]=false};
        string root=Path.GetDirectoryName(Path.GetFullPath(originalProject))!,candidateRoot=Path.GetDirectoryName(Path.GetFullPath(candidateProject))!;
        string Owned(string folder,string path){string lexical=Path.GetFullPath(Path.Combine(folder,path));if(!string.Equals(PackPaths.Owned(folder,path),lexical,OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal))throw new ArgumentException("Owned lexical source required");for(FileSystemInfo? n=new FileInfo(lexical);n is not null;n=n is FileInfo f?f.Directory:((DirectoryInfo)n).Parent)if(n.LinkTarget is not null)throw new ArgumentException("Linked source refused");return lexical;}
        (string Text,string Hash) Read(string path){var info=new FileInfo(path);if(!info.Exists||info.Length>1048576)throw new ArgumentException("Bounded source required");byte[] bytes=File.ReadAllBytes(path);return(new UTF8Encoding(false,true).GetString(bytes),JsonData.HashBytes(bytes));}
        // Classification refusal is not validation success. The caller falls
        // back to full compilation for all ambiguous or unsupported shapes.
        try{
            var ownerManifest=Read(originalProject);var manifest=new Parser(ownerManifest.Text,originalProject).ParseManifest();
            if(manifest.Kind!="project"||!id.StartsWith(manifest.Namespace+"::",StringComparison.Ordinal)||!manifest.Elements.TryGetValue(id[(manifest.Namespace.Length+2)..],out var loc)||loc.Kind!="object"||loc.Path!=relative)return No();
            var original=Read(Owned(root,relative));var candidate=Read(Owned(candidateRoot,relative));
            if(original.Hash!=baseline||candidate.Text!=after)throw new InvalidOperationException("Reviewed data source changed");
            var before=new Parser(original.Text,"<old-data>").ParseElement();var next=new Parser(after,"<new-data>").ParseElement();
            if(before.Id!=id||next.Id!=id||before.Kind!="object"||next.Kind!="object"||before.Parent is not null||before.Uses.Count!=1||before.Uses[0].Kind!="schema"||before.Data.Count!=next.Data.Count||before.Contains.Count!=0||before.Modules.Count!=0||before.Provides.Count!=0)return No();
            var differences=before.Data.Keys.Where(k=>!next.Data.TryGetValue(k,out var n)||before.Data[k].Kind!=n.Kind||before.Data[k].Scalar?.GetRawText()!=n.Scalar?.GetRawText()).ToArray();
            if(differences.Length!=1||!next.Data.TryGetValue(differences[0],out var newDatum))return No();
            string field=differences[0];var oldDatum=before.Data[field];
            if(oldDatum.Kind!="general"||newDatum.Kind!="general"||oldDatum.Scalar is not System.Text.Json.JsonElement oldScalar||newDatum.Scalar is not System.Text.Json.JsonElement newScalar||!oldScalar.TryGetInt64(out long oldValue)||!newScalar.TryGetInt64(out long newValue)||oldValue==newValue)return No();
            before.Data[field]=newDatum;if(format(before)!=format(next))return No();
            string schemaId=before.Uses[0].Id;if(!schemaId.StartsWith(manifest.Namespace+"::",StringComparison.Ordinal)||!manifest.Elements.TryGetValue(schemaId[(manifest.Namespace.Length+2)..],out var schemaLoc)||schemaLoc.Kind!="schema")return No();
            var originalSchema=Read(Owned(root,schemaLoc.Path));var copiedSchema=Read(Owned(candidateRoot,schemaLoc.Path));if(originalSchema.Hash!=copiedSchema.Hash)throw new InvalidOperationException("Schema changed during candidate copy");
            var schema=new Parser(originalSchema.Text,"<data-schema>").ParseElement();if(schema.Id!=schemaId||schema.Kind!="schema"||schema.Parent is not null||schema.Fields.Values.Any(f=>f.Kind!="general"||f.Cardinality!="single")||!schema.Fields.TryGetValue(field,out var contract)||contract.Type!="long")return No();
            var stats=new BuildStatistics();var registry=new Registry(candidateProject,new Documents(Path.Combine(Path.GetTempPath(),"confectory-data-validation",JsonData.Digest(candidateProject)),stats),stats);
            if(registry.Project.Namespace!=manifest.Namespace||!registry.Project.Elements.TryGetValue(id[(manifest.Namespace.Length+2)..],out var candidateObject)||candidateObject.Path!=relative||candidateObject.Kind!="object"||!registry.Project.Elements.TryGetValue(schemaId[(manifest.Namespace.Length+2)..],out var candidateSchema)||candidateSchema.Path!=schemaLoc.Path||candidateSchema.Kind!="schema"||registry.Get(id,"object").Id!=id)return No();
            SchemaContracts.Validate(registry,id);
            if(Read(originalProject).Hash!=ownerManifest.Hash||Read(Owned(root,relative)).Hash!=original.Hash||Read(Owned(root,schemaLoc.Path)).Hash!=originalSchema.Hash)throw new InvalidOperationException("Data validation sources changed");
            return new JsonObject{["eligible"]=true,["checks"]=new JsonArray(new JsonObject{["path"]=Path.GetFileName(originalProject),["hash"]=ownerManifest.Hash},new JsonObject{["path"]=schemaLoc.Path,["hash"]=originalSchema.Hash})};
        }catch(BuildError){return No();}catch(ArgumentException){return No();}
    }
}
