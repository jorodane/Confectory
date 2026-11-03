using Confectory.Core;
using System.Text.Json.Nodes;

static partial class BlueprintRootExecution
{
    // An unused import alone does not change generated code. Native context
    // nodes do bind their implementation imports, even without a call card.
    static bool UsesFunction(Element implementation,JsonObject graph,string feature)=>BlueprintTree.Nodes(graph).Any(n=>
        n.Node["kind"]?.ToString()=="call"&&n.Node["feature"]?.ToString()==feature||
        n.Node["imports"]?.AsArray().Any(id=>id?.ToString()==feature)==true||
        n.Node["implementationContext"] is JsonObject&&implementation.Imports.Values.Any(i=>i.Id==feature));

    static string[] ReferencedFunctions(Element implementation,JsonObject graph)=>implementation.Imports.Values.Select(i=>i.Id)
        .Concat(BlueprintTree.Nodes(graph).Where(n=>n.Node["kind"]?.ToString()=="call").Select(n=>n.Node["feature"]!.ToString()))
        .Concat(BlueprintTree.Nodes(graph).SelectMany(n=>n.Node["imports"]?.AsArray().Select(id=>id!.ToString())??Enumerable.Empty<string>()))
        .Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal).ToArray();

    static string[] ContextIds(JsonObject choices)=>choices["targets"]!.AsArray().Select(t=>t!["graph"]!.ToString())
        .Concat(choices["callers"]!.AsArray().Select(c=>c!["graph"]!.ToString()))
        .Concat(choices["observers"]!.AsArray().Select(id=>id!.ToString())).Distinct(StringComparer.Ordinal).ToArray();

    static Dictionary<string,JsonNode> CodeDefinitions(JsonObject definitions)=>(definitions["nodes"]?.AsArray()??new JsonArray())
        .Concat(definitions["nestedNodes"]?.AsArray()??new JsonArray()).Where(n=>n?["definition"]?["kind"]?.ToString()=="code")
        .ToDictionary(n=>n!["id"]!.ToString(),n=>n!.DeepClone(),StringComparer.Ordinal);

    // This is receipt maintenance, never source repair. The complete original
    // graph was ready before mutation. Prove the only definition difference is
    // this callee's contract hash before retaining the original source/helpers.
    static void RefreshCodeReceipts(JsonObject units,string graphId,Dictionary<string,JsonNode> before,Dictionary<string,JsonNode> after,string feature,string oldHash,string newHash)
    {
        if(!before.Keys.ToHashSet(StringComparer.Ordinal).SetEquals(after.Keys))throw new ArgumentException("Preserve every original owned code node");
        foreach(var pair in before){var previous=pair.Value;var next=after[pair.Key];if(previous["definitionHash"]!.ToString()==next["definitionHash"]!.ToString())continue;
            var normalized=next["definition"]!.DeepClone().AsObject();var oldReferences=previous["definition"]?["featureContracts"] as JsonObject;var newReferences=normalized["featureContracts"] as JsonObject;
            if(oldReferences?[feature]?.ToString()!=oldHash||newReferences?[feature]?.ToString()!=newHash)throw new ArgumentException("Only the observed callee contract may change a code receipt");
            newReferences![feature]=oldReferences![feature]!.DeepClone();if(!JsonNode.DeepEquals(previous["definition"],normalized))throw new ArgumentException("Preserve original source ownership, signature, context and connections");
            string id=BlueprintTree.SourceId(graphId,pair.Key);var unit=units[id]??throw new ArgumentException("Exact original code source required");var record=JsonNode.Parse(unit["draft"]!.GetValue<string>())!.AsObject();
            if(unit["kind"]?.ToString()!="blueprint-node"||record["definitionHash"]?.ToString()!=previous["definitionHash"]!.ToString())throw new ArgumentException("Do not adopt a stale original code receipt");
            record["definitionHash"]=next["definitionHash"]!.DeepClone();unit["draft"]=record.ToJsonString();
        }
    }
    static void PublicWrapperChecks(JsonObject units,string ns,HashSet<string>? selected,HashSet<string> paths,JsonArray checks) {
        foreach(var pair in units.Where(p=>p.Value?["kind"]?.ToString()=="blueprint"&&(selected is null||selected.Contains(p.Key)))){
            var unit=pair.Value!;bool pending=unit["authorSaveReceipt"]?["publicWrapper"]?.GetValue<bool>()==true;
            if(!pending&&unit["draft"]?.ToString()==unit["original"]?.ToString())continue;
            var graph=JsonNode.Parse(unit["draft"]!.ToString())!.AsObject();var wrappers=BlueprintTree.Nodes(graph).Where(n=>n.Node["postCall"]?["originalExecution"] is not null).ToArray();if(wrappers.Length==0)continue;
            var group=unit["rootContractGroup"] as JsonArray;
            // The enclosing public definition transaction already guards these
            // members and readonly observations under the same final lease.
            if(group is not null&&units[group[0]!.ToString()]?["draft"]?.ToString().Contains(BlueprintExecutionBranches.Metadata,StringComparison.Ordinal)==true)continue;
            if(PackPaths.Namespace(pair.Key)!=ns)throw new ArgumentException("Owned public wrapper receipt required");
            var root=Root(units,pair.Key,false);_=Definitions(units,pair.Key,true);
            var original=unit["original"] is null?null:JsonNode.Parse(unit["original"]!.ToString()) as JsonObject;
            var previous=original?["nodes"] is JsonArray?BlueprintTree.Nodes(original).ToDictionary(n=>n.Key,n=>n.Node,StringComparer.Ordinal):new Dictionary<string,JsonObject>(StringComparer.Ordinal);
            bool changed=wrappers.Any(w=>!previous.TryGetValue(w.Key,out var old)||!JsonNode.DeepEquals(old["postCall"],w.Node["postCall"])||!JsonNode.DeepEquals(old["executionEnum"],w.Node["executionEnum"])||!JsonNode.DeepEquals(old["signature"],w.Node["signature"])||old["feature"]?.ToString()!=w.Node["feature"]?.ToString());
            if(changed&&!pending)throw new ArgumentException("Retain the atomic public wrapper checkpoint receipt");
            var features=wrappers.Select(n=>n.Node["feature"]!.ToString()).ToHashSet(StringComparer.Ordinal);
            var dependencies=features.Concat(root.Implementation.Imports.Values.Where(i=>features.Contains(i.Id)&&i.Scope is not null).Select(i=>i.Scope!)).Concat(new[]{root.Function.Id,root.Implementation.Id}).Distinct(StringComparer.Ordinal).ToArray();
            JsonObject? sources=null;
            if(pending){var receipt=unit["authorSaveReceipt"]!;sources=receipt["sources"] as JsonObject??throw new ArgumentException("Retain the complete wrapper source receipt");
                if(receipt["version"]?.GetValue<int>()!=1||receipt["graph"]?.ToString()!=pair.Key||sources.Count is <2 or >64||!sources.ContainsKey(pair.Key))throw new ArgumentException("Complete bounded public wrapper observation required");
                foreach(string id in dependencies)if(sources[id] is null||units[id] is null||sources[id]?["hash"]?.ToString()!=Hash(units[id]!["draft"]!.ToString()))throw new ArgumentException("The observed original wrapper contract or scope changed; retain input");
            }
            foreach(string id in sources?.Select(p=>p.Key)??dependencies){var member=units[id]??throw new ArgumentException("Missing observed wrapper source");string path=member["path"]!.ToString(),baseline=member["baseline"]!.ToString();var proof=sources?[id];
                if(PackPaths.Namespace(id)!=ns||proof is not null&&(proof["path"]?.ToString()!=path||proof["kind"]?.ToString()!=member["kind"]?.ToString()||!System.Text.RegularExpressions.Regex.IsMatch(proof["hash"]?.ToString()??"",@"\A[a-f0-9]{64}\z"))||baseline!="missing"&&!System.Text.RegularExpressions.Regex.IsMatch(baseline,@"\A[a-f0-9]{64}\z"))throw new ArgumentException("Exact owned wrapper dependency locator/baseline required");
                _=PackPaths.Owned(Path.Combine(Path.GetTempPath(),"confectory-public-wrapper-guards"),path);if(paths.Add(path))checks.Add(new JsonObject{["path"]=path,["hash"]=baseline});
            }
        }
    }

}
