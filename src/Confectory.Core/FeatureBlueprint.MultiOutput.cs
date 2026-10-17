using System.Text.Json.Nodes;

namespace Confectory.Core;

public static partial class FeatureBlueprint
{
    public const string MultiOutputProfile="sync-acyclic-implicit-out-v1", MultiOutputGenerator="feature-blueprint-source-v4";
    public static IEnumerable<Parameter> FeatureOutputs(FunctionSignature signature) =>
        (signature.Return=="void"?Array.Empty<Parameter>():new[]{new Parameter(signature.Return,"return")}).Concat(signature.Args.Where(p=>p.IsOut));
    public static JsonArray OutputDocument(FunctionSignature signature) => new(FeatureOutputs(signature).Select(p=>(JsonNode)new JsonObject{["name"]=p.Name,["type"]=p.Type}).ToArray());

    private static (JsonArray Ends,JsonArray Warnings) DescribeMultiTerminations(string entry,Element feature,Dictionary<string,Node> nodes,Dictionary<(string,string),string> edges,List<string> order,Dictionary<string,string[]> predecessors,JsonObject exits,Dictionary<string,string[]>? forwardedOutputs=null)
    {
        var outputs=FeatureOutputs(feature.Signature!).ToArray();
        var must=new Dictionary<string,HashSet<string>>(StringComparer.Ordinal);var may=new Dictionary<string,HashSet<string>>(StringComparer.Ordinal);
        foreach(string id in order){
            var before=predecessors[id];var definite=before.Length==0?new HashSet<string>(StringComparer.Ordinal):new HashSet<string>(must[before[0]],StringComparer.Ordinal);foreach(string p in before.Skip(1))definite.IntersectWith(must[p]);
            var possible=new HashSet<string>(before.SelectMany(p=>may[p]),StringComparer.Ordinal);
            if(nodes[id].Kind=="export"){string name=S(nodes[id].Definition,"output");definite.Add(name);possible.Add(name);}
            if(forwardedOutputs is not null&&forwardedOutputs.TryGetValue(id,out var assigned))foreach(string name in assigned){definite.Add(name);possible.Add(name);}
            must[id]=definite;may[id]=possible;
        }
        JsonArray Witness(string id,string output){var path=new JsonArray();var before=predecessors[id].Where(p=>!must[p].Contains(output)).Order(StringComparer.Ordinal).ToArray();if(before.Length==0)path.Add(new JsonObject{["from"]=null,["port"]="entry",["to"]=id});else{string previous=before[0];foreach(var step in Witness(previous,output))path.Add(step?.DeepClone());string port=edges.Where(e=>e.Key.Item1==previous&&e.Value==id).OrderBy(e=>e.Key.Item2,StringComparer.Ordinal).First().Key.Item2;path.Add(new JsonObject{["from"]=previous,["port"]=port,["to"]=id});}return path;}
        var ends=new JsonArray();var warnings=new JsonArray();
        void End(string? from,string port,string target){
            bool direct=target.StartsWith("exit:",StringComparison.Ordinal)&&exits[target[5..]] is not null&&feature.Signature!.Return!="void";
            var missing=new JsonArray();var paths=new JsonObject();var assignments=new JsonObject();
            foreach(var output in outputs){bool assigned=direct&&output.Name=="return"||from is not null&&must[from].Contains(output.Name),possible=direct&&output.Name=="return"||from is not null&&may[from].Contains(output.Name);assignments[output.Name]=new JsonObject{["must"]=assigned,["may"]=possible};if(assigned)continue;
                string fallback=output.Type=="bool"?"false":output.Type is "string" or "object"||output.Type.EndsWith("[]",StringComparison.Ordinal)?"null":"0";
                var witness=from is null?new JsonArray():Witness(from,output.Name);witness.Add(new JsonObject{["from"]=from,["port"]=port,["to"]=target});paths[output.Name]=witness;
                missing.Add(new JsonObject{["name"]=output.Name,["type"]=output.Type,["assignedOnSomePaths"]=possible,["defaultValue"]=fallback});
            }
            var row=new JsonObject{["from"]=from,["port"]=port,["target"]=target,["missingOutputs"]=missing,["definitelyAssigned"]=missing.Count==0,["assignedOnSomePaths"]=missing.Any(p=>p!["assignedOnSomePaths"]!.GetValue<bool>()),["assignments"]=assignments};ends.Add(row);
            if(missing.Count>0)warnings.Add(new JsonObject{["severity"]="warning",["code"]="GRAPH_RETURN_UNASSIGNED",["subject"]=(from??"$entry")+"/"+port,["termination"]=row.DeepClone(),["missingOutputs"]=missing.DeepClone(),["exampleUnassignedPath"]=paths.First().Value!.DeepClone(),["outputPaths"]=paths,["runtimePolicy"]="csharp-type-default"});
        }
        if(entry.StartsWith("end:",StringComparison.Ordinal)||entry.StartsWith("exit:",StringComparison.Ordinal))End(null,"entry",entry);
        foreach(var edge in edges.Where(e=>must.ContainsKey(e.Key.Item1)&&(e.Value.StartsWith("end:",StringComparison.Ordinal)||e.Value.StartsWith("exit:",StringComparison.Ordinal))).OrderBy(e=>e.Key.Item1,StringComparer.Ordinal).ThenBy(e=>e.Key.Item2,StringComparer.Ordinal))End(edge.Key.Item1,edge.Key.Item2,edge.Value);
        return(ends,warnings);
    }
}
