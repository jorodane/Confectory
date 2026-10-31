using Confectory.Core;
using System.Text.Json.Nodes;

// Pure single-node wrapping, never a C# parser/decompiler or source writer.
internal static class BlueprintNodeFlow
{
    // Inheriting a contract does not transfer ownership of the parent's body.
    // An override may wrap only its own explicitly declared, published target.
    static void ValidateOwnedOverride(JsonObject owner,string rootId)
    {
        var declared=new Parser(owner["text"]!.GetValue<string>(),"<node-flow-owner>").ParseElement();
        if(declared.Parent is null)return;
        string target=owner["bodyTarget"]!.GetValue<string>(),project=Path.GetFullPath(owner["project"]!.GetValue<string>());
        if(owner["id"]?.ToString()!=declared.Id||rootId!=declared.Id+"/body:"+target||
           !declared.Bodies.TryGetValue(target,out var body)||body.SourceKind!="blueprint"||body.Origin!=declared.Id)
            throw new InvalidOperationException("Preserve inherited/reference sources; explicitly owned override body required");
        var observed=owner["ancestorSources"]?.AsObject()??throw new InvalidOperationException("Observe the owned override ancestry before entering its body");
        if(observed.Count>63||observed.ToJsonString().Length>2097152)throw new ArgumentException("Bounded override ancestry required");
        var registry=new Registry(project,new Documents(Path.Combine(Path.GetDirectoryName(project)!,".confectory","document-cache"),new BuildStatistics()),new BuildStatistics());
        if(PackPaths.Namespace(declared.Id)!=registry.Project.Namespace||File.ReadAllText(registry.Get(declared.Id,"implementation").Loc.File)!=owner["text"]!.ToString())
            throw new InvalidOperationException("Confirm the owned override declaration before entering its body");
        var seen=new HashSet<string>(StringComparer.Ordinal){declared.Id};var current=declared;
        while(current.Parent is string parent){
            if(!seen.Add(parent)||seen.Count>64||PackPaths.Namespace(parent)!=registry.Project.Namespace||observed[parent] is not JsonValue)
                throw new InvalidOperationException("Exact observable project override ancestry required; preserve parent sources");
            current=registry.Get(parent,"implementation",current.Id);
            if(File.ReadAllText(current.Loc.File)!=observed[parent]!.GetValue<string>())throw new InvalidOperationException("Override ancestry changed; retain input");
        }
        if(observed.Count!=seen.Count-1)throw new InvalidOperationException("Exact override ancestry receipt required");
        registry.Effective(declared.Id); // Existing function/signature inheritance rules remain authoritative.
    }
    public static JsonObject Prepare(JsonObject request)
    {
        string rootId=request["id"]!.GetValue<string>(),path=request["privatePath"]?.GetValue<string>()??"",nodeId=request["node"]!.GetValue<string>();
        string nonce=request["nonce"]!.GetValue<string>(),recordText=request["record"]!.GetValue<string>();
        if(!System.Text.RegularExpressions.Regex.IsMatch(nonce,"\\A[a-f0-9]{32}\\z")||recordText.Length>1048576)throw new ArgumentException("Bounded explicit internal-flow proposal required");
        if(request["ownerRequest"] is JsonObject owner)ValidateOwnedOverride(owner,rootId);
        var original=request["graph"]!.DeepClone().AsObject();string profile=original["profile"]!.GetValue<string>();
        if(!FeatureBlueprint.SupportsPrivateGraphs(profile))throw new InvalidOperationException("Review the existing private graph profile before wrapping a C# action");
        var frame=BlueprintTree.Select(original,path);string frameProfile=frame["profile"]!.GetValue<string>();var before=frame["nodes"]!.AsArray().Single(row=>row!["id"]!.ToString()==nodeId)!.AsObject();
        bool execution=before["control"]?.ToString()=="switch";
        if(before["kind"]?.ToString()!="code"||before["control"]?.ToString() is not ("next" or "switch")||!execution&&before.ContainsKey("executionEnum")||before.ContainsKey("retainedCode"))throw new InvalidOperationException("An owned C# action with its observed member and execution contract is required");
        string key=path.Length==0?nodeId:path+"/"+nodeId,sourceId=BlueprintTree.SourceId(rootId,key),childKey=key+"/body",childId=BlueprintTree.SourceId(rootId,childKey);
        var record=JsonNode.Parse(recordText)!.AsObject();BlueprintDocuments.Validate(sourceId,"blueprint-node",recordText);
        JsonObject Definitions(JsonObject graph){if(request["ownerRequest"] is JsonObject owned){var input=owned.DeepClone().AsObject();input["graph"]=graph.DeepClone();input["definitionsOnly"]=true;input.Remove("privatePath");return BlueprintDocuments.DescribeOwned(input);}return FeatureBlueprint.Execute(new JsonObject{["operation"]="featureBlueprintNodes",["featureSource"]=request["featureSource"]!.DeepClone(),["featureContracts"]=request["featureContracts"]?.DeepClone(),["propertyContracts"]=request["propertyContracts"]?.DeepClone(),["implementationContext"]=request["implementationContext"]?.DeepClone(),["bodyTarget"]=request["bodyTarget"]?.DeepClone(),["graph"]=graph.DeepClone()});}
        JsonNode Find(JsonObject descriptions,string wanted)=>descriptions["nodes"]!.AsArray().Concat(descriptions["nestedNodes"]?.AsArray()??new JsonArray()).Single(row=>row!["id"]!.ToString()==wanted)!;
        var initial=Definitions(original);if(initial["state"]?.ToString()!="node-definitions")throw new ArgumentException(initial.ToJsonString());
        if(record["definitionHash"]?.ToString()!=Find(initial,key)["definitionHash"]?.ToString())throw new InvalidOperationException("Read the current C# definition receipt before wrapping; source retained");
        var next=original.DeepClone().AsObject();var parent=BlueprintTree.Select(next,path);int index=parent["nodes"]!.AsArray().IndexOf(parent["nodes"]!.AsArray().Single(row=>row!["id"]!.ToString()==nodeId));
        var outer=before.DeepClone().AsObject();outer["kind"]="graph";outer.Remove("implementation");
        var inner=before.DeepClone().AsObject();inner["id"]="body";if(!execution)inner["control"]="next";inner.Remove("branchOwner");inner.Remove("forwardCallerStorage");inner["implementation"]="nodes/internal_"+nonce+".node.json";
        if(execution)outer["executionSource"]="body";
        bool callerStorage=before["signature"]!["args"]!.AsArray().Any(arg=>arg!["mode"]?.ToString() is "ref" or "out");if(callerStorage)inner["forwardCallerStorage"]=true;
        if(before["implementationContext"] is JsonObject){outer.Remove("implementationContext");outer.Remove("sourceIdentity");if(callerStorage)outer["forwardCallerStorage"]=true;}
        var arguments=new JsonObject();foreach(var argument in before["signature"]!["args"]!.AsArray().Where(arg=>arg!["mode"]?.ToString()!="out"))arguments[argument!["name"]!.ToString()]=new JsonObject{["input"]=argument["name"]!.DeepClone()};inner["arguments"]=arguments;
        var nodes=new JsonArray(inner);var edges=new JsonArray();string returns=before["signature"]!["return"]!.GetValue<string>();
        if(returns!="void"){
            nodes.Add(new JsonObject{["id"]="return",["kind"]="export",["intent"]="기존 C# 반환값 유지",["control"]="next",["output"]="return",["signature"]=new JsonObject{["args"]=new JsonArray(new JsonObject{["name"]="value",["type"]=returns}),["return"]="void"},["arguments"]=new JsonObject{["value"]=new JsonObject{["node"]="body"}}});
            edges.Add(new JsonObject{["from"]="body",["port"]="next",["to"]="return"});
        }
        outer["graph"]=new JsonObject{["schema"]=1,["profile"]=frameProfile,["entry"]="body",["nodes"]=nodes,["edges"]=edges,["exits"]=new JsonObject()};
        if(request["executionExits"] is JsonObject exitPlan){
            if(!execution||exitPlan.Count!=3||exitPlan.Any(p=>p.Key is not ("exits" or "edges" or "entry"))||exitPlan["exits"] is not JsonObject selected||selected.Count is <1 or >64||exitPlan["edges"] is not JsonArray wires||wires.Count>256)throw new ArgumentException("Exact bounded original execution exit plan required");
            foreach(var end in selected)if(!System.Text.RegularExpressions.Regex.IsMatch(end.Key,@"\A[A-Za-z_][A-Za-z_0-9.-]{0,127}\z"))throw new ArgumentException("Local exit identity required");
            foreach(var wire in wires)if(wire is not JsonObject link||link.Count!=3||link.Any(p=>p.Key is not ("from" or "port" or "to")))throw new ArgumentException("Exact local execution connections required");
            var selectedGraph=outer["graph"]!.AsObject();selectedGraph["schema"]=2;selectedGraph["executionExitMode"]=true;selectedGraph["entry"]=exitPlan["entry"]!.DeepClone();selectedGraph["exits"]=selected.DeepClone();selectedGraph["edges"]=wires.DeepClone();
        }
        outer["retainedCode"]=new JsonObject{["version"]=1,["nonce"]=nonce,["sourceId"]=sourceId,["sourceTextHash"]=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(recordText))).ToLowerInvariant(),["definition"]=before.DeepClone()};
        parent["nodes"]![index]=outer;
        var described=Definitions(next);if(described["state"]?.ToString()!="node-definitions")throw new ArgumentException(described.ToJsonString());
        var code=record.DeepClone().AsObject();code["node"]="body";code["definitionHash"]=Find(described,childKey)["definitionHash"]!.DeepClone();
        BlueprintDocuments.Validate(rootId,"blueprint",next.ToJsonString());BlueprintDocuments.Validate(childId,"blueprint-node",code.ToJsonString());
        return new JsonObject{["graph"]=next,["record"]=code,["node"]=nodeId,["sourceId"]=sourceId,["childId"]=childId,["childKey"]=childKey,["path"]=inner["implementation"]!.DeepClone(),["nonce"]=nonce,["originalSourcePreserved"]=true,["sourceWritten"]=false,["compiled"]=false,["executed"]=false};
    }
}
