using Confectory.Core;
using System.Text.Json.Nodes;

internal static partial class BlueprintAsyncTransition
{
    static (string Root,string Path) AsyncView(string id)
    {
        var parts=id.Split("/graph:",StringSplitOptions.None);
        string path=string.Join('/',parts.Skip(1));
        if(parts.Skip(1).Any(p=>p.Length==0||p.Contains('/')))throw new ArgumentException("Exact private async view required");
        return(parts[0],path);
    }
    static JsonObject PrivateNode(JsonObject graph,string path)
    {
        if(path.Length==0)throw new ArgumentException("Explicit owned private node required");
        var row=BlueprintTree.Nodes(graph).SingleOrDefault(n=>n.Key==path);
        if(row?.Node["kind"]?.ToString()!="graph")throw new ArgumentException("Observed private graph required");
        return row.Node;
    }
    static JsonObject? NodeDemotion(JsonObject graph,JsonObject node,string identity)
    {
        if(node["kind"]?.ToString()!="graph")return Demotion(node,identity);
        // An async-only completion wire cannot silently acquire another meaning.
        // Disconnect it explicitly before demoting this private Task boundary.
        return graph["edges"]!.AsArray().Any(e=>e!["from"]?.ToString()==node["id"]?.ToString()&&e["port"]?.ToString()=="completion")?null:new JsonObject{["privateTask"]=true};
    }
    static void SetNodeAsync(JsonObject graph,JsonObject node,bool enabled,string identity)
    {
        if(node["kind"]?.ToString()=="code") { BlueprintCompletionBranch.Set(node,enabled,identity);return; }
        if(node["kind"]?.ToString()!="graph"||node["signature"]!["args"]!.AsArray().Any(p=>p!["mode"]?.ToString() is not (null or "out"))||BlueprintTree.Nodes(node["graph"]!.AsObject()).Any(n=>n.Node["implementationContext"] is not null||n.Node["forwardCallerStorage"]?.GetValue<bool>()==true))throw new ArgumentException("Owned private Task cannot borrow ref storage or a native receiver");
        var child=node["graph"]!.AsObject();
        if(enabled){child["asyncOriginProfile"]??=child["profile"]?.ToString()==BlueprintAsync.Profile?JsonValue.Create(FeatureBlueprint.SwitchProfile):child["profile"]!.DeepClone();child["profile"]=BlueprintAsync.Profile;node["async"]=true;}
        else {
            if(NodeDemotion(graph,node,identity) is null)throw new ArgumentException("Disconnect this private Task completion wire explicitly before sync conversion; retain all input");
            if(BlueprintTree.Nodes(child).Any(n=>n.Node["async"]?.GetValue<bool>()==true))throw new ArgumentException("Explicitly convert the private async operations before their caller");
            string profile=child["asyncOriginProfile"]?.ToString()??FeatureBlueprint.SwitchProfile;
            if(!FeatureBlueprint.SupportsSwitches(profile)&&child["nodes"]!.AsArray().Any(n=>n!["control"]?.ToString()=="switch"))profile=FeatureBlueprint.SwitchProfile;
            child["profile"]=profile;child.Remove("asyncOriginProfile");node.Remove("async");
        }
    }
    static JsonArray AsyncNodes(JsonObject graph,string id)=>new(graph["nodes"]!.AsArray().Where(n=>n!["kind"]?.ToString() is "code" or "graph"&&n["implementationContext"] is null).Select(n=>(JsonNode)new JsonObject{["id"]=n!["id"]!.DeepClone(),["enabled"]=n["async"]?.GetValue<bool>()==true,["demotion"]=NodeDemotion(graph,n.AsObject(),id+"/node:"+n["id"]!.ToString())}).ToArray());
    static IEnumerable<JsonNode?> DefinitionRows(JsonObject definitions)=>definitions["nodes"]!.AsArray().Concat(definitions["nestedNodes"]?.AsArray()??new JsonArray());
}
