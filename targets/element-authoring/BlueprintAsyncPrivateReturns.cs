using Confectory.Core;
using System.Text.Json.Nodes;

internal static partial class BlueprintAsyncTransition
{
    static void PushPrivateEnum(JsonObject node)
    {
        if(node["kind"]?.ToString()!="graph"||node["executionSource"] is not JsonValue source)return;
        var selected=node["graph"]!["nodes"]!.AsArray().Single(n=>n!["id"]?.ToString()==source.ToString())!.AsObject();
        selected["executionEnum"]=node["executionEnum"]!.DeepClone();PushPrivateEnum(selected);
    }
    static void RefreshPrivateEnums(JsonObject graph)
    {
        foreach(var value in graph["nodes"]!.AsArray().Where(n=>n!["kind"]?.ToString()=="graph")){
            var node=value!.AsObject();RefreshPrivateEnums(node["graph"]!.AsObject());
            if(node["executionSource"] is JsonValue source)node["executionEnum"]=node["graph"]!["nodes"]!.AsArray().Single(n=>n!["id"]?.ToString()==source.ToString())!["executionEnum"]!.DeepClone();
        }
    }
    // Materialize only the old implicit ends as explicit None returns. Original
    // wires, native values, leaf source and public IO remain intact. The new
    // ordinary completion result is chosen only by a subsequent explicit edit.
    static void PrivateReturnChoices(JsonObject node)
    {
        if(!BlueprintPrivateCompletion.OwnsResults(node))return;var graph=node["graph"]!.AsObject();
        if(graph["executionExitMode"]?.GetValue<bool>()==true)return;
        bool native=node["signature"]!["return"]?.ToString()!="void";var exits=graph["exits"]!.AsObject();
        JsonObject Choice(JsonNode? value)=>native?new(){["executionBranch"]="none",["value"]=value?.DeepClone()}:new(){["executionBranch"]="none"};
        foreach(string name in exits.Select(p=>p.Key).ToArray())exits[name]=Choice(exits[name]);
        string End(string identity){string prefix="completed_end_"+JsonData.Digest(identity)[..16],name=prefix;int n=2;while(exits.ContainsKey(name))name=prefix+"_"+n++;exits[name]=Choice(null);return "exit:"+name;}
        var wires=graph["edges"]!.AsArray();foreach(var wire in wires)if(wire!["to"]?.ToString().StartsWith("end:",StringComparison.Ordinal)==true)wire["to"]=End(wire["to"]!.ToString());
        if(graph["entry"]?.ToString() is null or "")graph["entry"]=End("entry");
        foreach(var current in graph["nodes"]!.AsArray())foreach(string port in current!["control"]?.ToString()=="branch"?new[]{"true","false"}:new[]{"next"}){
            if(wires.Any(e=>e!["from"]?.ToString()==current["id"]?.ToString()&&e["port"]?.ToString()==port))continue;
            string target=current["branchOwner"] is JsonValue owner?"return:"+owner:End(current["id"]!.ToString()+"/"+port);
            wires.Add(new JsonObject{["from"]=current["id"]!.DeepClone(),["port"]=port,["to"]=target});
        }
        graph["schema"]=2;graph["executionExitMode"]=true;
    }
}
