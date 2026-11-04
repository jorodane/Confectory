using Confectory.Core;
using System.Text.Json.Nodes;
internal static partial class BlueprintAsyncTransition
{
    static string[] CompletionCallerIds(JsonObject units,string function)
    {
        if(BlueprintFunctionCompletion.Read(Element(units,function,"function")) is null)return Array.Empty<string>();
        // Unrelated body locators stay lazy after cold restore. Every declared
        // importing body is still required; skipping its missing draft is unsafe.
        var required=units.Where(p=>p.Value?["kind"]?.ToString()=="implementation").Select(p=>Element(units,p.Key,"implementation")).Where(i=>i.Imports.Values.Any(v=>v.Id==function)).SelectMany(i=>i.Bodies.Where(b=>b.Value.SourceKind=="blueprint").Select(b=>i.Id+"/body:"+b.Key)).ToArray();
        foreach(string id in required)_=Graph(units,id);
        return required.Concat(units.Where(p=>p.Value?["kind"]?.ToString()=="blueprint"&&p.Value?["draft"] is JsonValue).Select(p=>p.Key)).Distinct(StringComparer.Ordinal).Where(id=>BlueprintTree.Nodes(Graph(units,id)).Any(n=>n.Node["kind"]?.ToString()=="call"&&n.Node["feature"]?.ToString()==function)).ToArray();
    }
    static string[] CompletionCalls(JsonObject units,JsonObject before,string function)
    {
        var fn=Element(units,function,"function");var prior=Element(before,function,"function");if(BlueprintFunctionCompletion.Read(fn) is null&&BlueprintFunctionCompletion.Read(prior) is null)return Array.Empty<string>();
        foreach(var item in units.Where(p=>p.Value?["kind"]?.ToString()=="implementation")) {var impl=Element(units,item.Key,"implementation");if(impl.Imports.Values.Any(i=>i.Id==function)&&impl.Bodies.Any(b=>b.Value.SourceKind!="blueprint"))throw new ArgumentException("Retain native caller source; its explicit completion adapter is required");}
        var changed=new List<string>();foreach(var item in units.Where(p=>p.Value?["kind"]?.ToString()=="blueprint")){
            if(item.Value?["draft"] is not JsonValue)continue;var graph=Graph(units,item.Key);if(BlueprintTree.Nodes(graph).Any(p=>p.Node["kind"]?.ToString()=="code"&&p.Node["imports"] is JsonArray imports&&imports.Any(v=>v?.ToString()==function)))throw new ArgumentException("Retain explicit C# import calls; convert their source contract explicitly before this transition");var uses=BlueprintTree.Nodes(graph).Where(p=>p.Node["kind"]?.ToString()=="call"&&p.Node["feature"]?.ToString()==function).ToArray();if(uses.Length==0)continue;
            _=Root(units,item.Key);if(uses.Any(p=>p.Key.Contains('/')||p.Node["postCall"] is not null||p.Node["control"]?.ToString() is not ("next" or "switch")))throw new ArgumentException("Observed ordinary direct completion callers required; retain nested/wrapper originals");
            foreach(var use in uses){var call=use.Node;if(call["publicExecution"] is not null&&(call["publicExecution"]!.ToString()!=FeatureBlueprint.ContractHash(prior)||!JsonNode.DeepEquals(call["executionEnum"],BlueprintExecutionBranches.Enum(prior))))throw new ArgumentException("Retain the exact observed caller execution contract");call["control"]="switch";call["publicExecution"]=FeatureBlueprint.ContractHash(fn);call["executionEnum"]=BlueprintExecutionBranches.Enum(fn);}
            units[item.Key]!["draft"]=graph.ToJsonString();changed.Add(item.Key);
        }
        return changed.ToArray();
    }
    static void RefreshCode(JsonObject units,JsonObject before,string target)
    {
        var graph=Graph(units,target);var defs=Definitions(units,target);var old=Definitions(before,target);var original=Definitions(before,target,true);if(defs["state"]?.ToString()!="node-definitions")throw new ArgumentException("Async transition definitions refused: "+defs.ToJsonString());
        foreach(var entry in BlueprintTree.Nodes(graph).Where(n=>n.Node["kind"]?.ToString()=="code")){string source=BlueprintTree.SourceId(target,entry.Key);var unit=units[source]??throw new ArgumentException("Owned original C# record required");var record=JsonNode.Parse(S(unit,"draft"))!.AsObject();string prior=record["definitionHash"]!.ToString();bool Match(JsonObject d)=>d["state"]?.ToString()=="node-definitions"&&d["nodes"]!.AsArray().Any(n=>n!["id"]?.ToString()==entry.Key&&n["definitionHash"]?.ToString()==prior);
            string scope=Path.Combine(Path.GetTempPath(),"confectory-async-scope");bool blankNew=unit["baseline"]?.ToString()=="missing"&&prior==new string('0',64)&&record["source"]?.ToString()==""&&(record["helpers"]?.ToString()??"")==""&&(NewOwnedCode(before,source,scope,PackPaths.Owned(scope,S(unit,"path")))||NewOwnedCreation(before,source,scope,PackPaths.Owned(scope,S(unit,"path")),Root(before,target).Function.Id));
            if(!Match(old)&&!Match(original)&&!blankNew)throw new ArgumentException("Original C# definition changed; preserve all input");BlueprintDocuments.Validate(source,"blueprint-node",record.ToJsonString());record["definitionHash"]=defs["nodes"]!.AsArray().Single(n=>n!["id"]?.ToString()==entry.Key)!["definitionHash"]!.DeepClone();unit["draft"]=record.ToJsonString();}
    }
}
