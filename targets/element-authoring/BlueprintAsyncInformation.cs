using Confectory.Core;
using System.Text.Json.Nodes;

internal static partial class BlueprintAsyncTransition
{
    // A contained function owns its contract. An assigned requirement or a
    // reference implementation does not acquire that authority from this view.
    static string? InformationOwner(JsonObject units,string function,string implementation)
    {
        var owners=units.Where(p=>p.Value?["kind"]?.ToString()=="schema")
            .Select(p=>Element(units,p.Key,"schema"))
            .Where(e=>e.Contains.Any(c=>c.Kind=="function"&&c.Id==function)).ToArray();
        if(owners.Length==0)return null;
        if(owners.Length!=1)throw new ArgumentException("Unique direct information function owner required");
        var owner=owners[0];var unit=units[owner.Id]!;
        if(!function.StartsWith(owner.Id+"_Function_",StringComparison.Ordinal)||
           owner.Contains.Count(c=>c.Id==function)!=1||
           owner.Provides.GetValueOrDefault(function)?.Id!=implementation||
           units[function]?["copySource"] is not null||
           unit["baseline"]?.ToString()=="missing"||
           JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(S(unit,"original")))!=S(unit,"baseline"))
            throw new ArgumentException("Observed directly owned information contract and binding required");
        var assignments=units.Where(p=>p.Value?["kind"]?.ToString() is "object" or "schema")
            .SelectMany(p=>new Parser(S(p.Value!,"draft"),"<async-owner>").ParseElement().Provides.Select(v=>(Owner:p.Key,Function:v.Key,Implementation:v.Value.Id)))
            .Where(p=>p.Implementation==implementation).ToArray();
        if(assignments.Length!=1||assignments[0].Owner!=owner.Id||assignments[0].Function!=function)
            throw new ArgumentException("Exclusive owned information implementation required");
        return owner.Id;
    }
    static string? RequireInformationOwner(JsonObject request,JsonObject units,string function,string implementation)
    {
        string? owner=InformationOwner(units,function,implementation);
        if(request["owner"]?.ToString()!=owner)throw new ArgumentException("Explicit current information owner required; retain source and input");
        return owner;
    }
    static bool NewInformationCreation(JsonObject units,string id,string root,string path,string? function)
    {
        if(function is null||units[function] is not JsonObject fnUnit)return false;
        var implementations=units.Where(p=>p.Value?["kind"]?.ToString()=="implementation")
            .Select(p=>Element(units,p.Key,"implementation")).Where(e=>e.Function==function).ToArray();
        if(implementations.Length!=1)return false;
        var impl=implementations[0];string? ownerId=units[impl.Id]?["creationOwner"]?.ToString();
        if(ownerId is null||impl.Parent is not null||units[impl.Id]?["copySource"] is not null||
           units[impl.Id]?["baseline"]?.ToString()!="missing"||S(units[impl.Id]!,"original")!=""||
           InformationOwner(units,function,impl.Id)!=ownerId)return false;
        var fn=Element(units,function,"function");var owner=Element(units,ownerId,"schema");
        var originalOwner=new Parser(S(units[ownerId]!,"original"),"<original-information-owner>").ParseElement();
        bool newFunction=fnUnit["baseline"]?.ToString()=="missing";
        if(fn.Parent is not null||fn.Provides.Count!=0||originalOwner.Id!=ownerId||originalOwner.Kind!="schema"||
           originalOwner.Provides.ContainsKey(function)||
           (newFunction?(S(fnUnit,"original")!=""||fnUnit["creationOwner"]?.ToString()!=ownerId||originalOwner.Contains.Any(c=>c.Id==function)):
             (originalOwner.Contains.Count(c=>c.Kind=="function"&&c.Id==function)!=1||fnUnit["creationOwner"] is not null&&fnUnit["creationOwner"]?.ToString()!=ownerId)))return false;
        string ns=PackPaths.Namespace(function);var projects=units.Where(p=>p.Value?["kind"]?.ToString()=="project").ToArray();
        if(projects.Length!=1)return false;
        var project=projects[0];var manifest=project.Value!;
        if(manifest["baseline"]?.ToString()=="missing"||JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(S(manifest,"original")))!=S(manifest,"baseline"))return false;
        var before=new Parser(S(manifest,"original"),"<original-information-project>").ParseManifest();
        var after=new Parser(S(manifest,"draft"),"<information-project>").ParseManifest();
        if(before.Kind!="project"||after.Kind!="project"||before.Namespace!=ns||after.Namespace!=ns||PackPaths.Namespace(project.Key)!=ns)return false;
        bool Same(string a,string b)=>SameOwnedBodyPath(a,b);
        bool Registered(string key,string kind,bool missing){var u=units[key];if(u is null||PackPaths.Namespace(key)!=ns)return false;string name=key[(ns.Length+2)..];if(!after.Elements.TryGetValue(name,out var current)||current.Kind!=kind||!Same(current.Path,S(u,"path")))return false;if(!missing)return before.Elements.TryGetValue(name,out var old)&&old.Kind==kind&&Same(old.Path,S(u,"path"));return S(u,"original")==""&&u["baseline"]?.ToString()=="missing"&&!before.Elements.ContainsKey(name)&&!before.Elements.Values.Any(v=>Same(v.Path,S(u,"path")));}
        if(!Registered(ownerId,"schema",false)||!Registered(function,"function",newFunction)||!Registered(impl.Id,"implementation",true))return false;
        var memberIds=new HashSet<string>(StringComparer.Ordinal){function,impl.Id};
        foreach(string target in impl.Bodies.Keys){string graphId=impl.Id+"/body:"+target;var graphUnit=units[graphId];
            if(graphUnit?["baseline"]?.ToString()!="missing"||S(graphUnit,"original")!=""||graphUnit["creationOwner"] is not null||graphUnit["copySource"] is not null)return false;
            var graph=Root(units,graphId).Graph;if(graph["nodes"]!.AsArray().Any(n=>n!["implementationContext"] is not null||n["forwardCallerStorage"]?.GetValue<bool>()==true))return false;
            memberIds.Add(graphId);foreach(var row in BlueprintTree.Nodes(graph).Where(n=>n.Node["kind"]?.ToString()=="code")){
                if(row.Key.Contains('/'))return false;string key=BlueprintTree.SourceId(graphId,row.Key);var record=units[key];
                if(record?["kind"]?.ToString()!="blueprint-node"||record["baseline"]?.ToString()!="missing"||S(record,"original")!=""||record["creationOwner"] is not null||record["copySource"] is not null||!Same(Path.Combine(Path.GetDirectoryName(S(graphUnit!,"path"))??"",S(row.Node,"implementation")),S(record,"path")))return false;
                BlueprintDocuments.Validate(key,"blueprint-node",S(record,"draft"));if(JsonNode.Parse(S(record,"draft"))!["node"]?.ToString()!=row.Key)return false;memberIds.Add(key);
            }
        }
        var source=units[id];if(impl.Bodies.Count==0||!memberIds.Contains(id)||source?["baseline"]?.ToString()!="missing"||!Same(S(source,"path"),Path.GetRelativePath(root,path)))return false;
        foreach(var other in units.Where(p=>p.Key!=id&&p.Value?["baseline"]?.ToString()!="missing"&&p.Value?["path"] is not null)){
            if(Same(S(other.Value!,"path"),S(source,"path")))return false;
            if(other.Value?["kind"]?.ToString()=="implementation")foreach(var body in new Parser(S(other.Value!,"original"),"<original-body-locator>").ParseElement().Bodies.Values)if(Same(body.Path,S(source,"path")))return false;
        }
        return true;
    }
    static bool InformationCreationGroup(JsonObject units,string function,JsonArray group)
    {
        var impls=units.Where(p=>p.Value?["kind"]?.ToString()=="implementation").Select(p=>Element(units,p.Key,"implementation")).Where(i=>i.Function==function).ToArray();
        if(impls.Length!=1)return false;var impl=impls[0];string? owner=units[impl.Id]?["creationOwner"]?.ToString();if(owner is null)return false;
        string root=Path.Combine(Path.GetTempPath(),"confectory-async-scope");
        if(!NewInformationCreation(units,impl.Id,root,PackPaths.Owned(root,S(units[impl.Id]!,"path")),function))return false;
        var expected=Members(units,impl.Bodies.Keys.Select(t=>impl.Id+"/body:"+t),function).Concat(new[]{owner,units.Single(p=>p.Value?["kind"]?.ToString()=="project").Key}).ToHashSet(StringComparer.Ordinal);
        return group.Count==expected.Count&&group.All(x=>expected.Contains(x!.ToString())&&JsonNode.DeepEquals(units[x.ToString()]?["atomicEditGroup"],group));
    }
}
