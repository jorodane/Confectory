using Confectory.Core;
using System.Text.Json.Nodes;

// Pure single-node wrapping, never a C# parser/decompiler or source writer.
internal static class BlueprintNodeFlow
{
    public static JsonObject Prepare(JsonObject request)
    {
        string rootId=request["id"]!.GetValue<string>(),path=request["privatePath"]?.GetValue<string>()??"",nodeId=request["node"]!.GetValue<string>();
        string nonce=request["nonce"]!.GetValue<string>(),recordText=request["record"]!.GetValue<string>();
        if(!System.Text.RegularExpressions.Regex.IsMatch(nonce,"\\A[a-f0-9]{32}\\z")||recordText.Length>1048576)throw new ArgumentException("Bounded explicit internal-flow proposal required");
        if(request["ownerRequest"] is JsonObject owner&&new Parser(owner["text"]!.GetValue<string>(),"<node-flow-owner>").ParseElement().Parent is not null)throw new InvalidOperationException("Preserve inherited implementation sources; a directly owned C# body is required");
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
        outer["retainedCode"]=new JsonObject{["version"]=1,["nonce"]=nonce,["sourceId"]=sourceId,["sourceTextHash"]=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(recordText))).ToLowerInvariant(),["definition"]=before.DeepClone()};
        parent["nodes"]![index]=outer;
        var described=Definitions(next);if(described["state"]?.ToString()!="node-definitions")throw new ArgumentException(described.ToJsonString());
        var code=record.DeepClone().AsObject();code["node"]="body";code["definitionHash"]=Find(described,childKey)["definitionHash"]!.DeepClone();
        BlueprintDocuments.Validate(rootId,"blueprint",next.ToJsonString());BlueprintDocuments.Validate(childId,"blueprint-node",code.ToJsonString());
        return new JsonObject{["graph"]=next,["record"]=code,["node"]=nodeId,["sourceId"]=sourceId,["childId"]=childId,["childKey"]=childKey,["path"]=inner["implementation"]!.DeepClone(),["nonce"]=nonce,["originalSourcePreserved"]=true,["sourceWritten"]=false,["compiled"]=false,["executed"]=false};
    }
}
