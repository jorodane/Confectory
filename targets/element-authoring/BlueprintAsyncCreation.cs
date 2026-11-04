using Confectory.Core;
using System.Text.Json.Nodes;

internal static partial class BlueprintAsyncTransition
{
    static bool SameOwnedBodyPath(string a,string b){string root=Path.Combine(Path.GetTempPath(),"confectory-async-scope");return string.Equals(PackPaths.Owned(root,a),PackPaths.Owned(root,b),OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal);}
    // No on-disk function contract exists yet. Keep the user's first explicit
    // transition contract, and prove every new destination against the existing
    // ProjectPack registration; this never treats a missing old source as new.
    static string OriginalFunctionText(JsonObject units,string id)
    {
        var unit=units[id]!;
        if(unit["baseline"]?.ToString()!="missing")return S(unit,"original");
        string scope=Path.Combine(Path.GetTempPath(),"confectory-async-scope");
        if(!NewOwnedCreation(units,id,scope,PackPaths.Owned(scope,S(unit,"path")),id))throw new ArgumentException("Owned new function registration required");
        return unit[Receipt]?["creationFunction"]?.GetValue<string>()??S(unit,"draft");
    }
    static Element OriginalFunction(JsonObject units,string id)
    {
        var fn=new Parser(OriginalFunctionText(units,id),"<original-async-function>").ParseElement();
        if(fn.Kind!="function"||fn.Id!=id||fn.Parent is not null)throw new ArgumentException("Exact original function contract required");return fn;
    }
    static bool NewOwnedCreation(JsonObject units,string id,string root,string path,string? function)
    {
        if(NewInformationCreation(units,id,root,path,function))return true;
        if(function is null||units[function] is not JsonObject fnUnit||fnUnit["baseline"]?.ToString()!="missing"||S(fnUnit,"original")!=""||fnUnit["creationOwner"] is not null)return false;
        var fn=Element(units,function,"function");if(fn.Parent is not null)return false;
        var source=units[id];if(source is null||source["baseline"]?.ToString()!="missing"||S(source,"original")!=""||source["creationOwner"] is not null||source["copySource"] is not null)return false;
        string ns=PackPaths.Namespace(function);var projects=units.Where(p=>p.Value?["kind"]?.ToString()=="project").ToArray();if(projects.Length!=1)return false;
        var manifest=projects[0].Value!;
        if(manifest["baseline"]?.ToString()=="missing"||JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(S(manifest,"original")))!=S(manifest,"baseline"))return false;
        var before=new Parser(S(manifest,"original"),"<new-function-original-project>").ParseManifest();var after=new Parser(S(manifest,"draft"),"<new-function-project>").ParseManifest();
        if(before.Kind!="project"||after.Kind!="project"||before.Namespace!=ns||after.Namespace!=ns||PackPaths.Namespace(projects[0].Key)!=ns)return false;
        var comparison=OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal;
        bool Same(string a,string b)=>string.Equals(PackPaths.Owned(root,a),PackPaths.Owned(root,b),comparison);
        bool Registered(string key,string kind){var u=units[key];if(u is null||u["baseline"]?.ToString()!="missing"||S(u,"original")!=""||u["creationOwner"] is not null||u["copySource"] is not null||PackPaths.Namespace(key)!=ns)return false;string name=key[(ns.Length+2)..];return !before.Elements.ContainsKey(name)&&after.Elements.TryGetValue(name,out var locator)&&locator.Kind==kind&&Same(locator.Path,S(u,"path"))&&!before.Elements.Values.Any(v=>Same(v.Path,S(u,"path")));}
        if(!Registered(function,"function"))return false;
        var implementations=units.Where(p=>p.Value?["kind"]?.ToString()=="implementation").Select(p=>Element(units,p.Key,"implementation")).Where(i=>i.Function==function).ToArray();
        if(implementations.Length==0||!fn.Provides.TryGetValue(function,out var selected)||!implementations.Any(i=>i.Id==selected.Id))return false;
        var roots=new List<(string Id,JsonObject Graph,Element Implementation)>();
        foreach(var impl in implementations){if(impl.Parent is not null||!Registered(impl.Id,"implementation")||impl.Bodies.Count==0)return false;foreach(string target in impl.Bodies.Keys){string graphId=impl.Id+"/body:"+target;if(units[graphId]?["baseline"]?.ToString()!="missing"||units[graphId]?["original"]?.ToString()!="")return false;var owner=Root(units,graphId);if(owner.Graph["nodes"]!.AsArray().Any(n=>n!["implementationContext"] is not null||n["forwardCallerStorage"]?.GetValue<bool>()==true))return false;roots.Add((graphId,owner.Graph,impl));}}
        bool member=id==function||implementations.Any(i=>i.Id==id)||roots.Any(g=>g.Id==id);
        foreach(var g in roots){string prefix=g.Id+"/node:";if(!id.StartsWith(prefix,StringComparison.Ordinal))continue;string nodeId=id[prefix.Length..];if(nodeId.Contains('/'))return false;var node=g.Graph["nodes"]!.AsArray().SingleOrDefault(n=>n!["id"]?.ToString()==nodeId);if(node?["kind"]?.ToString()!="code"||source["kind"]?.ToString()!="blueprint-node")return false;string directory=Path.GetDirectoryName(S(units[g.Id]!,"path"))??"";if(!Same(Path.Combine(directory,S(node,"implementation")),S(source,"path")))return false;BlueprintDocuments.Validate(id,"blueprint-node",S(source,"draft"));if(JsonNode.Parse(S(source,"draft"))!["node"]?.ToString()!=nodeId)return false;member=true;}
        if(!member||!string.Equals(path,PackPaths.Owned(root,S(source,"path")),comparison))return false;
        // Preserve every original locator, including an old body whose physical
        // file is currently missing; no alias can silently acquire new meaning.
        foreach(var other in units.Where(p=>p.Key!=id&&p.Value?["baseline"]?.ToString()!="missing"&&p.Value?["path"] is not null)){
            if(string.Equals(PackPaths.Owned(root,S(other.Value!,"path")),path,comparison))return false;
            if(other.Value?["kind"]?.ToString()=="implementation")foreach(var body in new Parser(S(other.Value!,"original"),"<old-body-locator>").ParseElement().Bodies.Values)if(string.Equals(PackPaths.Owned(root,body.Path),path,comparison))return false;
        }
        return true;
    }
}
