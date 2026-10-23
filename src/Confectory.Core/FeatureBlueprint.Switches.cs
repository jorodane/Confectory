using System.Text.Json.Nodes;

namespace Confectory.Core;

public static partial class FeatureBlueprint
{
    public const string SwitchProfile = "sync-acyclic-switch-v1", SwitchGenerator = "feature-blueprint-source-v13";
    public static bool SupportsMethods(string? profile) => profile is MethodsProfile or SwitchProfile or PropertySetProfile or PropertyRefProfile;
    static string Owner(Node node) => node.Definition["branchOwner"]?.GetValue<string>() ?? "";
    static bool WrappedReturn(Node node) => node.Kind == "call" && node.Control == "switch" && node.Signature.Return != "void";
    static string ExecutionType(Node node) => node.Control == "switch" ? "int" : node.Signature.Return;
    static JsonObject EnumContract(JsonNode value)
    {
        var input=value.AsObject();Need(input.All(p=>p.Key is "primary" or "members"),"GRAPH_ENUM_FIELD","executionEnum");
        var prepared=BlueprintEnumContract.Validate(new(){["schema"]=1,["kind"]="execution-enum-proposal",["sourceId"]="node-enum",["definitionHash"]=new string('0',64),["sourceHash"]=new string('0',64),["primary"]=input["primary"]?.DeepClone(),["members"]=input["members"]?.DeepClone()});
        return new(){["primary"]=prepared["primary"]!.DeepClone(),["members"]=prepared["members"]!.DeepClone()};
    }
    static string EnumDeclaration(Node node) => node.Control != "switch" ? "" : "public enum Result : int {\n"+string.Join("\n",node.Definition["executionEnum"]!["members"]!.AsArray().Select(m=>"    "+S(m,"name")+" = "+m!["value"]!.ToJsonString()+","))+"\n}\n";

    // Case regions return to an explicit main continuation. These are CFG edges,
    // not recursive node calls and not feature-end labels.
    static (Dictionary<string,string> Continuations,JsonArray Returns,Dictionary<(string,string),(string,string)> EndOrigins) SwitchFlow(Dictionary<string,Node> nodes, Dictionary<(string,string),string> edges)
    {
        foreach(var node in nodes.Values){
            string owner=Owner(node);var seen=new HashSet<string>(StringComparer.Ordinal){node.Id};int depth=0;
            while(owner.Length>0){Need(nodes.TryGetValue(owner,out var parent)&&parent.Control=="switch"&&seen.Add(owner)&&++depth<=8,"GRAPH_BRANCH_OWNER",node.Id);owner=Owner(parent!);}
        }
        string End(Node node,string port)=>Owner(node).Length>0?"return:"+Owner(node):"end:"+node.Id+"/"+port;
        foreach(var node in nodes.Values){
            var allowed=node.Control=="switch"?node.Definition["executionEnum"]!["members"]!.AsArray().Select(m=>"case:"+S(m,"id")).Concat(new[]{"next","default"}).ToArray():node.Control=="branch"?new[]{"true","false"}:new[]{"next"};
            Need(edges.Keys.Where(k=>k.Item1==node.Id).All(k=>allowed.Contains(k.Item2)),"GRAPH_PORTS",node.Id);
            foreach(string port in node.Control=="branch"?new[]{"true","false"}:new[]{"next"})edges.TryAdd((node.Id,port),End(node,port));
        }
        foreach(var edge in edges){
            var from=nodes[edge.Key.Item1];bool clause=from.Control=="switch"&&edge.Key.Item2!="next";string owner=clause?from.Id:Owner(from),to=edge.Value;
            if(to.StartsWith("return:",StringComparison.Ordinal))Need(owner.Length>0&&to[7..]==owner,"GRAPH_BRANCH_RETURN",from.Id+"/"+edge.Key.Item2);
            else if(nodes.TryGetValue(to,out var target))Need(Owner(target)==owner,"GRAPH_BRANCH_SCOPE",from.Id+"/"+edge.Key.Item2);
        }
        string Resolve(string target){var seen=new HashSet<string>(StringComparer.Ordinal);while(target.StartsWith("return:",StringComparison.Ordinal)){string owner=target[7..];Need(seen.Add(owner)&&nodes.TryGetValue(owner,out var node)&&node.Control=="switch","GRAPH_BRANCH_RETURN",owner);target=edges[(owner,"next")];}return target;}
        string ContinuationOwner(string owner){var seen=new HashSet<string>(StringComparer.Ordinal);while(edges[(owner,"next")].StartsWith("return:",StringComparison.Ordinal)){Need(seen.Add(owner),"GRAPH_BRANCH_RETURN",owner);owner=edges[(owner,"next")][7..];}return owner;}
        var continuationOwners=nodes.Values.Where(n=>n.Control=="switch").ToDictionary(n=>n.Id,n=>ContinuationOwner(n.Id),StringComparer.Ordinal);
        var continuations=nodes.Values.Where(n=>n.Control=="switch").ToDictionary(n=>n.Id,n=>Resolve(edges[(n.Id,"next")]),StringComparer.Ordinal);var returns=new JsonArray();var origins=new Dictionary<(string,string),(string,string)>();
        foreach(var key in edges.Keys.ToArray()){string original=edges[key];if(original.StartsWith("return:",StringComparison.Ordinal)){returns.Add(new JsonObject{["from"]=key.Item1,["port"]=key.Item2,["owner"]=original[7..],["target"]=Resolve(original)});origins[key]=(continuationOwners[original[7..]],"next");}edges[key]=Resolve(original);}
        foreach(var node in nodes.Values.Where(n=>n.Control=="switch")){
            edges.Remove((node.Id,"next"));if(!edges.ContainsKey((node.Id,"default"))){edges.Add((node.Id,"unmatched"),continuations[node.Id]);origins[(node.Id,"unmatched")]=(continuationOwners[node.Id],"next");}
        }
        return (continuations,returns,origins);
    }

    static (JsonArray Ends,JsonArray Warnings) DescribeSwitchTerminations(string entry,Element feature,Dictionary<string,Node> nodes,Dictionary<(string,string),string> edges,List<string> order,Dictionary<string,string[]> predecessors,JsonObject exits,Dictionary<string,string[]> forwardedOutputs,Dictionary<(string,string),(string,string)> origins)
    {
        var raw=DescribeMultiTerminations(entry,feature,nodes,edges,order,predecessors,exits,forwardedOutputs);var ends=new JsonArray();var warnings=new JsonArray();
        (string?,string,string) Key(JsonNode? row){string? from=row!["from"]?.ToString();string port=S(row,"port");if(from is not null&&origins.TryGetValue((from,port),out var origin)){from=origin.Item1;port=origin.Item2;}return(from,port,S(row,"target"));}
        foreach(var group in raw.Ends.GroupBy(Key)){
            var (from,port,target)=group.Key;var assignments=new JsonObject();var missing=new JsonArray();var paths=new JsonObject();
            foreach(var output in FeatureOutputs(feature.Signature!)){
                bool must=group.All(row=>row!["assignments"]![output.Name]!["must"]!.GetValue<bool>()),may=group.Any(row=>row!["assignments"]![output.Name]!["may"]!.GetValue<bool>());assignments[output.Name]=new JsonObject{["must"]=must,["may"]=may};if(must)continue;
                var witness=raw.Warnings.First(w=>group.Any(row=>row!["from"]?.ToString()==w!["termination"]!["from"]?.ToString()&&S(row,"port")==S(w!["termination"],"port")&&S(row,"target")==S(w["termination"],"target"))&&w!["outputPaths"]?[output.Name] is not null)!;
                var path=witness["outputPaths"]![output.Name]!.DeepClone().AsArray();if(path.Count>0&&(path[^1]!["from"]?.ToString()!=from||S(path[^1],"port")!=port))path.Add(new JsonObject{["from"]=from,["port"]=port,["to"]=target});paths[output.Name]=path;
                var item=witness["missingOutputs"]!.AsArray().Single(m=>S(m,"name")==output.Name)!.DeepClone();item["assignedOnSomePaths"]=may;missing.Add(item);
            }
            var end=new JsonObject{["from"]=from,["port"]=port,["target"]=target,["missingOutputs"]=missing,["definitelyAssigned"]=missing.Count==0,["assignedOnSomePaths"]=missing.Any(m=>m!["assignedOnSomePaths"]!.GetValue<bool>()),["assignments"]=assignments};ends.Add(end);
            if(missing.Count>0)warnings.Add(new JsonObject{["severity"]="warning",["code"]="GRAPH_RETURN_UNASSIGNED",["subject"]=(from??"$entry")+"/"+port,["termination"]=end.DeepClone(),["missingOutputs"]=missing.DeepClone(),["exampleUnassignedPath"]=paths.First().Value!.DeepClone(),["outputPaths"]=paths,["runtimePolicy"]="csharp-type-default"});
        }
        return(ends,warnings);
    }
}
