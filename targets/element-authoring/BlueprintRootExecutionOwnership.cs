using Confectory.Core;
using System.Text.Json.Nodes;

static partial class BlueprintRootExecution
{
    // Resolve only the already-owned declaration chain. Borrowed bodies retain
    // the declaring owner's target/source; they are never materialized as copies.
    static Element OwnedImplementation(JsonObject units,string id,HashSet<string>? chain=null) {
        chain??=new(StringComparer.Ordinal);
        if(!chain.Add(id)||chain.Count>64)throw new ArgumentException("Bounded owned implementation ancestry required");
        var declared=Declaration(units,id,"implementation");
        if(declared.Parent is string parent){
            if(PackPaths.Namespace(parent)!=PackPaths.Namespace(id))throw new ArgumentException("Retain the registered ancestry observation boundary");
            var ancestor=OwnedImplementation(units,parent,chain);
            if(ancestor.Function!=declared.Function||!ancestor.Signature!.Matches(declared.Signature))throw new ArgumentException("Preserve the inherited function and input/output contract");
            var imports=new Dictionary<string,Import>(ancestor.Imports,StringComparer.Ordinal);foreach(var p in declared.Imports)imports[p.Key]=p.Value;declared.Imports=imports;
            var bodies=new Dictionary<string,Body>(ancestor.Bodies,StringComparer.Ordinal);foreach(var p in declared.Bodies)bodies[p.Key]=p.Value;declared.Bodies=bodies;
        }
        return declared;
    }

    static string[] ProviderDeclarations(JsonObject units,string rootId) {
        var root=Root(units,rootId);
        return units.Where(p=>p.Value?["kind"]?.ToString()=="implementation")
            .Select(p=>Declaration(units,p.Key,"implementation")).Where(i=>i.Function==root.Function.Id)
            .Select(i=>i.Id).Order(StringComparer.Ordinal).ToArray();
    }

    internal static bool OwnsDefinitionTransaction(JsonObject units,string id) {
        if(units[id]?["rootContractGroup"] is not JsonArray group||group.Count<3||units[group[0]!.ToString()]?["kind"]?.ToString()!="function")return false;
        var function=Declaration(units,group[0]!.ToString(),"function");if(!BlueprintExecutionBranches.Has(function))return false;
        var members=new JsonObject();foreach(var member in group){string key=member!.ToString();members[key]=units[key]?.DeepClone()??throw new ArgumentException("Complete definition transaction ownership required");}
        ValidateGroup(new JsonObject{["namespace"]=PackPaths.Namespace(id),["group"]=group.DeepClone(),["units"]=members});return true;
    }

    static string[] OwnershipObservations(JsonObject units,string rootId,IEnumerable<string> contexts) {
        var ids=new HashSet<string>(StringComparer.Ordinal);bool copied=false;
        foreach(string provider in ProviderDeclarations(units,rootId)){
            var declared=Declaration(units,provider,"implementation");if(declared.Parent is null)continue;
            ids.Add(provider);for(var current=declared;current.Parent is string parent;current=Declaration(units,parent,"implementation"))ids.Add(parent);
        }
        foreach(string graphId in contexts.Distinct(StringComparer.Ordinal)){
            var root=Root(units,graphId,false);var declared=Declaration(units,root.Implementation.Id,"implementation");
            for(var current=declared;current.Parent is string parent;current=Declaration(units,parent,"implementation")){
                if(PackPaths.Namespace(parent)!=PackPaths.Namespace(graphId))throw new ArgumentException("Owned ancestry observations required");ids.Add(parent);
            }
            if(root.Graph["copySource"] is not JsonObject provenance)continue;
            copied=true;string target=graphId[(graphId.IndexOf("/body:",StringComparison.Ordinal)+6)..];
            if(declared.Parent is not null||provenance.Count!=4||provenance.Any(p=>p.Key is not ("implementation" or "target" or "bodyOrigin" or "sourceKind"))||provenance["target"]?.ToString()!=target||provenance["sourceKind"]?.ToString() is not ("blueprint" or "csharp")||provenance["implementation"]?.ToString()==declared.Id||new[]{"implementation","bodyOrigin"}.Any(k=>provenance[k]?.ToString().Split("::",StringSplitOptions.None).Length!=2))throw new ArgumentException("Retain the same-contract copy's exact donor provenance");
            if(units[graphId]?["original"] is JsonValue original&&original.ToString().Length>0&&!JsonNode.DeepEquals(JsonNode.Parse(original.ToString())?["copySource"],provenance))throw new ArgumentException("Public definition updates cannot replace copy provenance");
            var owners=units.Where(p=>p.Value?["kind"]?.ToString() is "schema" or "object").Select(p=>Declaration(units,p.Key,p.Value!["kind"]!.ToString())).Where(o=>o.Provides.TryGetValue(root.Function.Id,out var provider)&&provider.Id==declared.Id).ToArray();
            if(owners.Length==0)throw new ArgumentException("Observe the existing copied provider assignment");
        }
        if(copied){
            // Guard the complete owned assignment universe, including the
            // manifest, so a concurrent new/shared assignment cannot hide.
            var project=units.SingleOrDefault(p=>p.Value?["kind"]?.ToString()=="project");
            if(project.Value is null)throw new ArgumentException("Observe the owned project and all copy owner declarations");
            var manifest=new Parser(project.Value["draft"]!.ToString(),"<execution-copy-project>").ParseManifest();
            if(manifest.Kind!="project"||manifest.Namespace!=PackPaths.Namespace(rootId))throw new ArgumentException("Exact copy project namespace required");ids.Add(project.Key);
            foreach(var locator in manifest.Elements.Where(p=>p.Value.Kind is "schema" or "object" or "module")){
                string id=manifest.Namespace+"::"+locator.Key;var unit=units[id]??throw new ArgumentException("Complete copy assignment/module observation required");
                if(unit["kind"]?.ToString()!=locator.Value.Kind||unit["path"]?.ToString()!=locator.Value.Path)throw new ArgumentException("Exact copy owner declaration locator required");
                _=Declaration(units,id,locator.Value.Kind);ids.Add(id);
            }
        }
        return ids.Order(StringComparer.Ordinal).ToArray();
    }
}
