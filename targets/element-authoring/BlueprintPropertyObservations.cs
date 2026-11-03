using Confectory.Core;
using System.Text.Json.Nodes;

// Reuse the server-authored property candidate's existing observation receipt.
// No source ID/path in the receipt creates a writable unit or external grant.
internal static class BlueprintPropertyObservations
{
    static string S(JsonNode value,string key)=>value[key]?.GetValue<string>()??throw new ArgumentException("Missing property observation "+key);
    static IEnumerable<(string Id,JsonObject Unit,JsonObject Sources)> Receipts(JsonObject units)
    {
        foreach(var pair in units){
            if(pair.Value?["kind"]?.ToString()!="blueprint"||pair.Value?["draft"] is not JsonValue text||pair.Value?["authorSaveReceipt"] is not JsonObject receipt||!pair.Key.Contains("/body:",StringComparison.Ordinal)||pair.Key.Contains("/graph:",StringComparison.Ordinal))continue;
            var graph=JsonNode.Parse(text.GetValue<string>())!.AsObject();
            if(graph["copySource"] is not null||receipt["slotRequest"] is JsonObject slot&&slot.Count>0||!BlueprintTree.Nodes(graph).Any(n=>FeatureBlueprint.IsPropertyNode(n.Node["kind"]?.ToString())))continue;
            var sources=receipt["sources"] as JsonObject??throw new ArgumentException("Saved property observations required");
            if(receipt["version"]?.GetValue<int>()!=1||receipt["graph"]?.ToString()!=pair.Key||sources.Count is <3 or >64||!sources.ContainsKey(pair.Key)||!sources.ContainsKey(pair.Key[..pair.Key.IndexOf("/body:",StringComparison.Ordinal)]))throw new ArgumentException("Exact property observation closure required");
            yield return(pair.Key,pair.Value.AsObject(),sources);
        }
    }
    public static JsonObject Query(JsonObject request)
    {
        var units=request["units"]!.AsObject();string ns=S(request,"namespace");var receipts=Receipts(units).ToArray();
        var members=receipts.SelectMany(r=>r.Sources.Select(p=>p.Key)).Distinct(StringComparer.Ordinal).ToArray();
        if(members.Any(id=>!units.ContainsKey(id)||PackPaths.Namespace(id)!=ns))throw new ArgumentException("Only known owned property observations may be restored");
        if(request["action"]?.ToString()=="members")return new(){["ids"]=new JsonArray(members.Select(id=>JsonValue.Create(id)).ToArray())};
        var selected=request["selected"]?.AsArray().Select(id=>id!.ToString()).ToHashSet(StringComparer.Ordinal);var checks=new JsonArray();var paths=new HashSet<string>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);
        string root=Path.Combine(Path.GetTempPath(),"confectory-property-observations");
        foreach(var row in receipts){
            if(selected is not null&&!selected.Contains(row.Id))continue;
            string implementation=row.Id[..row.Id.IndexOf("/body:",StringComparison.Ordinal)],target=row.Id[(row.Id.IndexOf("/body:",StringComparison.Ordinal)+6)..];
            var owner=new Parser(S(units[implementation]!,"draft"),"<property-observation>").ParseElement();
            if(owner.Kind!="implementation"||owner.Id!=implementation||!owner.Bodies.TryGetValue(target,out var body)||body.SourceKind!="blueprint"||body.Origin!=implementation||body.Path!=row.Unit["path"]?.ToString()||units[implementation]?["copySource"] is not null)throw new ArgumentException("Explicit owned property body required; retain parent/copy originals");
            if(!row.Sources.Any(p=>units[p.Key]?["kind"]?.ToString() is "project" or "pack"))throw new ArgumentException("Property project registration observation required");
            var visited=new HashSet<string>(StringComparer.Ordinal);
            void Required(string id,bool declaration=false){
                string qualified=id.Contains("::",StringComparison.Ordinal)?id:ns+"::"+id;
                if(PackPaths.Namespace(qualified)!=ns)return;
                if(!row.Sources.ContainsKey(qualified)||units[qualified] is null)throw new ArgumentException("Complete property declaration/code observations required");
                if(!declaration||!visited.Add(qualified))return;if(visited.Count>64)throw new ArgumentException("Property observation closure budget exceeded");
                var element=new Parser(S(units[qualified]!,"draft"),"<property-dependency>").ParseElement();
                if(element.Id!=qualified)throw new ArgumentException("Exact owned property dependency identity required");
                if(element.Kind is "object" or "concept" or "schema"){
                    if(element.Parent is string parent)Required(parent,true);
                    foreach(var use in element.Uses.Where(u=>u.Kind=="schema"))Required(use.Id,true);
                    foreach(var field in element.Fields.Values){if(field.Kind is "reference" or "compound")Required(field.Type,true);else if(field.Kind is "function" or "enum")Required(field.Type);}
                }
            }
            Required(owner.Function!);foreach(var import in owner.Imports.Values)Required(import.Id);
            foreach(var node in BlueprintTree.Nodes(JsonNode.Parse(S(row.Unit,"draft"))!.AsObject())){
                if(node.Node["kind"]?.ToString()=="code")Required(BlueprintTree.SourceId(row.Id,node.Key));
                if(FeatureBlueprint.IsPropertyNode(node.Node["kind"]?.ToString()))Required(S(node.Node,"propertyOwner"),true);
            }
            var rowPaths=new HashSet<string>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);
            foreach(var source in row.Sources){
                if(selected is not null&&!selected.Contains(source.Key))throw new ArgumentException("Review the complete property body and its observed sources together");
                var unit=units[source.Key]!;var proof=source.Value as JsonObject??throw new ArgumentException("Exact property source receipt required");
                if(proof.Count!=3||proof.Any(p=>p.Key is not ("path" or "kind" or "hash"))||unit["draft"] is null||unit["original"] is null||unit["baseline"]?.ToString()=="missing"||S(unit,"path")!=S(proof,"path")||S(unit,"kind")!=S(proof,"kind")||JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(S(unit,"draft")))!=S(proof,"hash")||JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(S(unit,"original")))!=S(unit,"baseline"))throw new ArgumentException("Property source/receipt changed; preserve the saved candidate");
                _=PackPaths.Owned(root,S(unit,"path"));if(!rowPaths.Add(S(unit,"path")))throw new ArgumentException("Property source paths must not alias");if(paths.Add(S(unit,"path")))checks.Add(new JsonObject{["path"]=unit["path"]!.DeepClone(),["hash"]=unit["baseline"]!.DeepClone()});
            }
        }
        return new(){["checks"]=checks,["sourceWritten"]=false,["executed"]=false};
    }
}
