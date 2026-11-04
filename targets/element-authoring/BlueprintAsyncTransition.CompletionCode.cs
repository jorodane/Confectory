using Confectory.Core;
using System.Text.Json.Nodes;

internal static partial class BlueprintAsyncTransition
{
    public static JsonObject CompletionCode(JsonObject request)
    {
        var units=request["units"]!.DeepClone().AsObject();string id=S(request,"id"),ns=S(request,"namespace"),nodeId=S(request,"node");var root=Root(units,id);var targets=Targets(units,id);
        string? informationOwner=RequireInformationOwner(request,units,root.Function.Id,root.Implementation.Id);
        var node=root.Graph["nodes"]!.AsArray().Single(n=>n!["id"]?.ToString()==nodeId)!.AsObject();_=BlueprintCompletionAdapter.Read(node)??throw new ArgumentException("Observed completion adapter required");
        var plan=request["plan"]!.AsObject();if(plan.Count!=2||plan.Any(p=>p.Key is not ("source" or "completion"))||plan["source"] is not JsonValue source||!source.TryGetValue<string>(out var body)||System.Text.Encoding.UTF8.GetByteCount(body)>1048576||plan["completion"] is not JsonValue completion||!completion.TryGetValue<string>(out var selection))throw new ArgumentException("Exact original-body and completion selection source required");
        var members=Members(units,targets,root.Function.Id).Concat(Observations(units,root.Function.Id)).ToHashSet(StringComparer.Ordinal);
        // Retire only a byte-clean prior public contract boundary. Do not merge
        // unrelated in-flight contracts or take authority from a posted ID.
        foreach(string member in members.ToArray())if(units[member]?["rootContractGroup"] is JsonArray prior){if(prior.Any(x=>units[x!.ToString()]?["draft"]?.ToString()!=units[x!.ToString()]?["original"]?.ToString()))throw new ArgumentException("Confirm the existing public contract first");foreach(var x in prior)units[x!.ToString()]!.AsObject().Remove("rootContractGroup");}
        node[BlueprintCompletionAdapter.Metadata]!["source"]=selection;_=BlueprintCompletionAdapter.Read(node);units[id]!["draft"]=root.Graph.ToJsonString();
        string codeId=BlueprintTree.SourceId(id,nodeId);var record=JsonNode.Parse(S(units[codeId]!,"draft"))!.AsObject();record["source"]=body;
        var definitions=Definitions(units,id);if(definitions["state"]?.ToString()!="node-definitions")throw new ArgumentException("Original adapter contract changed");record["definitionHash"]=definitions["nodes"]!.AsArray().Single(n=>n!["id"]?.ToString()==nodeId)!["definitionHash"]!.DeepClone();units[codeId]!["draft"]=record.ToJsonString();
        if(units[root.Function.Id]?[Receipt] is null){
            if(S(units[root.Function.Id]!,"draft")!=S(units[root.Function.Id]!,"original")||targets.Any(t=>S(units[Root(units,t).Implementation.Id]!,"draft")!=S(units[Root(units,t).Implementation.Id]!,"original")))throw new ArgumentException("Private completion editing cannot change a public header or implementation contract");
            foreach(string member in members.ToArray())if(units[member]?["atomicEditGroup"] is JsonArray existing){if(existing.Any(x=>units[x!.ToString()]?[Receipt] is null))throw new ArgumentException("Confirm other pending atomic edits first");foreach(var x in existing)members.Add(x!.ToString());}
            Scope(units,members,ns);var group=new JsonArray(members.Order(StringComparer.Ordinal).Select(x=>JsonValue.Create(x)).ToArray());var reads=new JsonObject();foreach(string member in members)reads[member]=new JsonObject{["path"]=units[member]!["path"]!.DeepClone(),["hash"]=units[member]!["baseline"]!.DeepClone()};
            var profiles=new JsonObject();foreach(string target in targets)profiles[target]=Graph(units,target)["profile"]!.DeepClone();
            foreach(string member in members){units[member]!["atomicEditGroup"]=group.DeepClone();units[member]![Receipt]??=new JsonObject{["schema"]=1,["function"]=root.Function.Id};}
            units[root.Function.Id]![Receipt]=new JsonObject{["schema"]=1,["function"]=root.Function.Id,["bodyOnly"]=true,["graphs"]=new JsonArray(targets.Select(x=>JsonValue.Create(x)).ToArray()),["profiles"]=profiles,["callers"]=new JsonArray(),["reads"]=reads};
        }
        if(informationOwner is not null)units[root.Function.Id]![Receipt]!["informationOwner"]=informationOwner;
        Validate(new(){["namespace"]=ns,["units"]=units});var saved=units[root.Function.Id]!["atomicEditGroup"]!.DeepClone();var result=new JsonObject();foreach(var member in saved!.AsArray())result[member!.ToString()]=units[member.ToString()]!.DeepClone();return new(){["group"]=saved,["units"]=result,["sourceWritten"]=false,["executed"]=false};
    }
}
