using Confectory.Core;
using System.Text;
using System.Text.Json.Nodes;

// An inherited, data-only object registration does not introduce executable code.
// Refuse every other shape and retain the ordinary candidate build.
internal static class ExistingSchemaObjectCreationValidation
{
    internal static JsonObject Check(string originalProject,string candidateProject,JsonArray changes,Func<Element,string> format,Func<Manifest,string> formatManifest)
    {
        JsonObject No()=>new(){["eligible"]=false};
        string root=Path.GetDirectoryName(Path.GetFullPath(originalProject))!,copy=Path.GetDirectoryName(Path.GetFullPath(candidateProject))!;
        string Owned(string folder,string path){
            string lexical=Path.GetFullPath(Path.Combine(folder,path));
            if(!string.Equals(PackPaths.Owned(folder,path),lexical,OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal))throw new ArgumentException("Owned lexical source required");
            for(FileSystemInfo? n=new FileInfo(lexical);n is not null;n=n is FileInfo f?f.Directory:((DirectoryInfo)n).Parent)if(n.LinkTarget is not null)throw new ArgumentException("Linked source refused");
            return lexical;
        }
        (string Text,string Hash) Read(string path){
            var info=new FileInfo(path);if(!info.Exists||info.Length>1048576)throw new ArgumentException("Bounded source required");
            byte[] bytes=File.ReadAllBytes(path);return(new UTF8Encoding(false,true).GetString(bytes),JsonData.HashBytes(bytes));
        }
        try{
            if(changes.Count!=8)return No();
            string S(int i)=>changes[i]!.GetValue<string>();
            var original=Read(originalProject);
            var manifest=new Parser(original.Text,originalProject).ParseManifest();
            if(manifest.Kind!="project")return No();
            string prefix=manifest.Namespace+"::";
            int m=S(0)==prefix+"ProjectManifest"?0:S(4)==prefix+"ProjectManifest"?4:-1;
            if(m<0)return No();int c=4-m;
            string id=S(c),path=S(c+1);
            if(S(m+1)!=Path.GetFileName(originalProject)||S(m+2)!=original.Hash||S(c+2)!="missing"||!id.StartsWith(prefix,StringComparison.Ordinal))return No();
            string local=id[prefix.Length..];
            if(path!="elements/"+local+".celem"||manifest.Elements.ContainsKey(local)||manifest.Elements.Values.Any(v=>string.Equals(v.Path,path,StringComparison.OrdinalIgnoreCase))||File.Exists(Owned(root,path)))return No();
            var next=new Parser(S(m+3),"<reviewed-registration>").ParseManifest();
            if(!next.Elements.TryGetValue(local,out var loc)||loc.Kind!="object"||loc.Path!=path)return No();
            manifest.Elements.Add(local,loc);
            if(formatManifest(manifest)!=formatManifest(next))return No();
            var child=Read(Owned(copy,path));if(child.Text!=S(c+3))return No();
            var element=new Parser(child.Text,"<new-object>").ParseElement();
            if(element.Kind!="object"||element.Id!=id||element.Parent is not string parent||!parent.StartsWith(prefix,StringComparison.Ordinal)||parent==id||format(element)!=format(new Element{Kind="object",Id=id,Parent=parent}))return No();
            if(!manifest.Elements.TryGetValue(parent[prefix.Length..],out var pl)||pl.Kind!="object")return No();
            var parentSource=Read(Owned(root,pl.Path));if(parentSource.Hash!=Read(Owned(copy,pl.Path)).Hash)return No();
            var p=new Parser(parentSource.Text,"<parent>").ParseElement();
            if(p.Id!=parent||p.Kind!="object"||p.Parent is not null||p.Uses.Count!=1||p.Uses[0].Kind!="schema")return No();
            var pure=new Element{Kind="object",Id=parent,Uses=p.Uses,Data=p.Data,Description=p.Description,DescriptionPresent=p.DescriptionPresent};
            if(format(p)!=format(pure)||p.Data.Values.Any(d=>d.Kind!="general"))return No();
            string schema=p.Uses[0].Id;
            if(!schema.StartsWith(prefix,StringComparison.Ordinal)||!manifest.Elements.TryGetValue(schema[prefix.Length..],out var sl)||sl.Kind!="schema")return No();
            var schemaSource=Read(Owned(root,sl.Path));if(schemaSource.Hash!=Read(Owned(copy,sl.Path)).Hash)return No();
            var sc=new Parser(schemaSource.Text,"<schema>").ParseElement();
            if(sc.Id!=schema||sc.Kind!="schema"||sc.Parent is not null||sc.Fields.Count==0||sc.Fields.Values.Any(f=>f.Kind!="general"||f.Cardinality!="single"))return No();
            var pureSchema=new Element{Kind="schema",Id=schema,Fields=sc.Fields,Description=sc.Description,DescriptionPresent=sc.DescriptionPresent};
            if(format(sc)!=format(pureSchema))return No();
            var stats=new BuildStatistics();
            var registry=new Registry(candidateProject,new Documents(Path.Combine(Path.GetTempPath(),"confectory-data-validation",JsonData.Digest(candidateProject)),stats),stats);
            if(registry.Project.Namespace!=next.Namespace||!registry.Project.Elements.TryGetValue(local,out var actual)||actual.Kind!="object"||actual.Path!=path||!registry.Project.Elements.TryGetValue(parent[prefix.Length..],out var actualParent)||actualParent.Kind!="object"||actualParent.Path!=pl.Path||!registry.Project.Elements.TryGetValue(schema[prefix.Length..],out var actualSchema)||actualSchema.Kind!="schema"||actualSchema.Path!=sl.Path||registry.Get(id,"object").Id!=id)return No();
            SchemaContracts.Validate(registry,schema);SchemaContracts.Validate(registry,parent);SchemaContracts.Validate(registry,id);
            if(Read(originalProject).Hash!=original.Hash||Read(Owned(root,pl.Path)).Hash!=parentSource.Hash||Read(Owned(root,sl.Path)).Hash!=schemaSource.Hash)throw new InvalidOperationException("Creation validation sources changed");
            return new JsonObject{["eligible"]=true,["checks"]=new JsonArray(new JsonObject{["path"]=Path.GetFileName(originalProject),["hash"]=original.Hash},new JsonObject{["path"]=pl.Path,["hash"]=parentSource.Hash},new JsonObject{["path"]=sl.Path,["hash"]=schemaSource.Hash})};
        }catch(BuildError){return No();}catch(ArgumentException){return No();}
    }
}
