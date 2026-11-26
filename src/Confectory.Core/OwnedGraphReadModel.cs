using System.Text.Json.Nodes;

namespace Confectory.Core;

// A derived, bounded model of one authoring transaction. It never owns a
// draft or a checkpoint; a changed input selects the ordinary validation path.
public sealed class OwnedGraphReadModel(string project)
{
    private readonly StringComparer paths=OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal;
    private readonly Dictionary<string,Context> contexts=new(StringComparer.Ordinal);
    private readonly Dictionary<string,JsonObject> projections=new(StringComparer.Ordinal);
    private int projectionBytes;
    private bool Owns(string path)=>paths.Equals(project,Path.GetFullPath(path));
    internal sealed record Context(Element Implementation,string FeatureSource,JsonObject Contracts,Observation Proof);
    internal Context? Get(string projectPath,string key)
    {
        if(!Owns(projectPath)||!contexts.TryGetValue(key,out var value))return null;
        if(value.Proof.Fresh())return value;
        contexts.Remove(key);
        return null;
    }
    internal void Put(string projectPath,string key,Context value)
    {
        if(!Owns(projectPath)||key.Length>262144||!value.Proof.Fresh())return;
        if(contexts.Count>=8)contexts.Clear();
        contexts[key]=value;
    }
    internal JsonObject Project(string projectPath,JsonObject input)
    {
        if(!Owns(projectPath))return FeatureBlueprint.Execute(input);
        string key=input.ToJsonString();
        if(projections.TryGetValue(key,out var existing))return existing.DeepClone().AsObject();
        var result=FeatureBlueprint.Execute(input);
        if(result["state"]?.ToString()=="invalid")return result;
        int size=key.Length+result.ToJsonString().Length;
        if(size>1048576)return result;
        if(projections.Count>=32||projectionBytes+size>2097152){projections.Clear();projectionBytes=0;}
        projections[key]=result.DeepClone().AsObject();projectionBytes+=size;
        return result;
    }
    // Track the exact bytes consumed by the ordinary Registry, plus its
    // logical locators, including locators not yet read as declarations.
    internal sealed class Observation
    {
        // Keep actual path spellings distinct even on Windows volumes that
        // enable case-sensitive directories. Stream ownership still follows
        // the existing platform project identity convention.
        private static readonly StringComparer comparer=StringComparer.Ordinal;
        private readonly Dictionary<string,string> files=new(comparer);
        private readonly Dictionary<string,string> paths=new(comparer);
        private bool reusable=true;
        internal byte[] Read(string path)
        {
            byte[] bytes=File.ReadAllBytes(path);
            string hash=JsonData.HashBytes(bytes);
            if(files.TryGetValue(path,out var prior)&&prior!=hash)throw new IOException("Declaration changed during graph projection");
            if(files.Count>=128||bytes.Length>1048576)reusable=false;
            files[path]=hash;
            return bytes;
        }
        internal string Text(string path)
        {
            using var reader=new StreamReader(new MemoryStream(Read(path)));
            return reader.ReadToEnd();
        }
        internal void BindPaths(string project,Registry registry)
        {
            void Bind(string logical,string resolved)
            {
                if(paths.Count>=2048){reusable=false;return;}
                paths[logical]=resolved;
            }
            Bind(project,registry.ProjectPath);
            foreach(var (ns,pack) in registry.Packs)
            {
                string physical=registry.Paths[ns],root=Path.GetDirectoryName(physical)!;
                if(ns!=registry.Project.Namespace)
                    Bind(Path.Combine(Path.GetDirectoryName(registry.ProjectPath)!,registry.Project.Registry[ns].Path),physical);
                foreach(var locator in pack.Elements.Values)
                    Bind(Path.Combine(root,locator.Path),PackPaths.Owned(root,locator.Path,locator.Loc));
            }
            // Bind every actually consumed declaration to its registry locator
            // at the time of the read, rather than a later resolved alias.
            foreach(var (id,element) in registry.Elements)
            {
                string ns=PackPaths.Namespace(id),local=id[(ns.Length+2)..];
                if(registry.Packs[ns].Elements.TryGetValue(local,out var locator))
                    Bind(Path.Combine(Path.GetDirectoryName(registry.Paths[ns])!,locator.Path),element.Loc.File);
            }
        }
        internal bool Fresh()
        {
            if(!reusable)return false;
            try
            {
                var components=new Dictionary<string,string>(comparer);
                foreach(var (logical,physical) in paths)
                    if(!comparer.Equals(PackPaths.Resolve(logical,components),physical))return false;
                foreach(var (path,hash) in files)
                    if(JsonData.HashBytes(File.ReadAllBytes(path))!=hash)return false;
                return true;
            }
            catch(Exception error) when(error is IOException or UnauthorizedAccessException or BuildError or ArgumentException or InvalidOperationException){return false;}
        }
    }
}
