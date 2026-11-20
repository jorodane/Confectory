using System.Text.Json.Nodes;

namespace Confectory.Core;

// An editor plan over existing switch semantics. This grants no source ownership
// and adds no runtime or persisted graph format. The author batch owns the CAS.
public static class BlueprintCellRegion
{
    static void Need(bool condition, string message)
    { if (!condition) throw new ArgumentException(message); }
    static string S(JsonNode? node, string key) => node?[key]?.GetValue<string>() ?? "";
    static bool Ordinary(JsonNode n, string owner) => S(n,"kind")=="code" && S(n,"control")=="next"
        && S(n,"branchOwner")==owner && n["implementationContext"] is null && n["postCall"] is null
        && n["executionEnum"] is null && n["async"]?.GetValue<bool>()!=true && n["forwardCallerStorage"]?.GetValue<bool>()!=true;

    sealed record Region(string Owner, string Port, List<string> Nodes, string End);
    // Move an existing compound as one invocation. No descendant, signature or
    // storage binding is rewritten; the normal compiler checks value dominance.
    static JsonObject CompoundOrder(JsonObject graph, JsonArray edits, bool ordinaryFrame=false)
    {
        int total=0;
        string Chain(JsonObject g,int depth)
        {
            Need(depth<=8 && S(g,"profile")==FeatureBlueprint.NestedProfile && g["copySource"] is null
                && g["executionExitMode"]?.GetValue<bool>()!=true,"Direct synchronous compound chain required");
            var nodes=g["nodes"]!.AsArray(); total+=nodes.Count;
            Need(nodes.Count is >0 and <64 && total<=256,"Bounded complete compound chain required");
            var names=nodes.Select(n=>S(n,"id")).ToHashSet(StringComparer.Ordinal);
            Need(names.Count==nodes.Count && nodes.All(n=>S(n,"kind") is "code" or "graph" && S(n,"control")=="next"
                && new[]{"branchOwner","implementationContext","postCall","executionEnum","executionSource","retainedCode","contextBoundary"}.All(k=>n![k] is null)
                && n!["async"]?.GetValue<bool>()!=true && n["forwardCallerStorage"]?.GetValue<bool>()!=true),
                "Preserve branch, call, opaque, receiver and forwarded storage contexts");
            var edges=g["edges"]!.AsArray();
            Need(edges.Count==nodes.Count && edges.All(e=>S(e,"port")=="next"&&names.Contains(S(e,"from")))
                &&edges.Select(e=>S(e,"from")).Distinct(StringComparer.Ordinal).Count()==nodes.Count,"One exclusive next route per cell required");
            var links=edges.ToDictionary(e=>S(e,"from"),e=>S(e,"to"),StringComparer.Ordinal);
            var seen=new HashSet<string>(StringComparer.Ordinal);string at=S(g,"entry");
            while(names.Contains(at)){Need(seen.Add(at),"Compound chain cannot cycle");at=links[at];}
            Need(seen.Count==names.Count&&at.StartsWith("exit:",StringComparison.Ordinal)&&g["exits"]!.AsObject().ContainsKey(at[5..]),"Retain every cell and the original frame exit");
            foreach(var node in nodes.Where(n=>S(n,"kind")=="graph"))Chain(node!["graph"]!.AsObject(),depth+1);
            return at;
        }
        string terminal=Chain(graph,0);
        var original=graph["nodes"]!.AsArray();
        Need(ordinaryFrame?original.All(n=>S(n,"kind")=="code"):original.Any(n=>S(n,"kind")=="graph"),
            "Existing ordinary child cells or a compound invocation required");
        Need(edits.Count==original.Count+1 && edits.All(e=>e is JsonObject row&&row["to"] is JsonValue v&&v.TryGetValue<string>(out _)
            &&(row.Count==3&&S(row,"action")=="entry"&&S(row,"node")=="$entry"
            ||row.Count==4&&S(row,"action")=="route"&&S(row,"port")=="next"&&row.All(p=>p.Key is "action" or "node" or "port" or "to"))),"Exact complete compound order required");
        var entry=edits.Single(e=>S(e,"action")=="entry")!;
        var routes=edits.Where(e=>S(e,"action")=="route").ToDictionary(e=>S(e,"node"),e=>S(e,"to"),StringComparer.Ordinal);
        Need(routes.Count==original.Count&&original.All(n=>routes.ContainsKey(S(n,"id"))),"Keep the original compound node set and frame");
        string next=S(entry,"to");var visited=new HashSet<string>(StringComparer.Ordinal);
        while(routes.ContainsKey(next)){Need(visited.Add(next),"Compound order cannot cycle");next=routes[next];}
        Need(visited.Count==original.Count&&next==terminal,"Compound order cannot drop cells or retarget its exit");
        return new JsonObject{["entry"]=S(entry,"to"),["edges"]=new JsonArray(routes.Select(p=>(JsonNode)new JsonObject{["from"]=p.Key,["port"]="next",["to"]=p.Value}).ToArray())};
    }
    static JsonObject FrameOrder(JsonObject root,string path,JsonArray edits)
    {
        // Verify the entire owned tree, including every ancestor and sibling.
        // IDs remain local to each frame; the caller binds the physical root.
        var unchanged=new JsonArray{new JsonObject{["action"]="entry",["node"]="$entry",["to"]=root["entry"]!.DeepClone()}};
        foreach(var edge in root["edges"]!.AsArray())unchanged.Add(new JsonObject{["action"]="route",["node"]=edge!["from"]!.DeepClone(),["port"]=edge["port"]!.DeepClone(),["to"]=edge["to"]!.DeepClone()});
        CompoundOrder(root,unchanged);
        var parts=path.Split('/');Need(parts.Length is >0 and <=8 && parts.All(p=>p.Length>0),"Exact nonempty owned frame path required");
        var selected=root;
        foreach(string part in parts){
            var owner=selected["nodes"]!.AsArray().Single(n=>S(n,"id")==part)!;
            Need(S(owner,"kind")=="graph","Every frame path segment must be an owned compound");
            selected=owner["graph"]!.AsObject();
        }
        return CompoundOrder(selected,edits,true);
    }
    static Region Read(JsonObject graph, string owner, string port)
    {
        Need(S(graph,"profile")==FeatureBlueprint.SwitchProfile && graph["executionExitMode"]?.GetValue<bool>()!=true
            && graph["copySource"] is null, "Only an existing synchronous owned switch region is supported");
        var nodes=graph["nodes"]!.AsArray().ToDictionary(n=>S(n,"id"),n=>n!,StringComparer.Ordinal);
        Need(nodes.Count is >0 and <64 && nodes.TryGetValue(owner,out var parent),"Existing bounded branch owner required");
        parent=nodes[owner];
        Need(S(parent,"kind")=="code" && S(parent,"control")=="switch" && parent["branchOwner"] is null
            && parent["postCall"] is null && parent["implementationContext"] is null && parent["executionSource"] is null
            && parent["async"]?.GetValue<bool>()!=true && parent["forwardCallerStorage"]?.GetValue<bool>()!=true,
            "Direct ordinary root switch required; preserve nested, copied and opaque contexts");
        Need(parent["executionEnum"]?["members"] is JsonArray members && members.Any(m=>"case:"+S(m,"id")==port
            && S(m,"id")!=S(parent["executionEnum"],"primary")),"Select one declared non-primary branch");
        var edges=graph["edges"]!.AsArray();
        Need(edges.GroupBy(e=>(S(e,"from"),S(e,"port"))).All(g=>g.Count()==1),"Distinct original routes required");
        Need(edges.Any(e=>S(e,"from")==owner&&S(e,"port")==port),"An explicit original branch route is required; preserve implicit/default flow");
        string Next(string from,string p)=>edges.SingleOrDefault(e=>S(e,"from")==from&&S(e,"port")==p)?["to"]?.GetValue<string>()??"return:"+owner;
        var order=new List<string>();var seen=new HashSet<string>(StringComparer.Ordinal);string at=Next(owner,port);
        while(nodes.TryGetValue(at,out var node)){
            Need(Ordinary(node,owner)&&seen.Add(at),"Branch editing requires an acyclic ordinary chain in one region");
            order.Add(at);at=Next(at,"next");
        }
        Need(at=="return:"+owner || at.StartsWith("exit:",StringComparison.Ordinal)&&graph["exits"]!.AsObject().ContainsKey(at[5..]),
            "Retain this branch return or existing exit");
        for(int i=0;i<order.Count;i++){
            string from=i==0?owner:order[i-1],p=i==0?port:"next",id=order[i];
            Need(S(graph,"entry")!=id && edges.Where(e=>S(e,"to")==id).All(e=>S(e,"from")==from&&S(e,"port")==p),
                "Shared branch entries cannot be moved or extended");
            Need(edges.Where(e=>S(e,"from")==id).All(e=>S(e,"port")=="next"),"Retain non-serial routes");
        }
        return new(owner,port,order,at);
    }

    public static JsonObject Query(JsonObject request)
    {
        bool frame=S(request,"action")=="frame-order";
        Need(request.Count==(3+(request.ContainsKey("operation")?1:0)+(frame?1:0)) && (request["operation"] is null || S(request,"operation")=="blueprintCellRegion") && request.All(p=>p.Key is "operation" or "action" or "graph" or "edits" ||frame&&p.Key=="path"),"Exact cell editor plan required");
        var graph=request["graph"]!.AsObject();var edits=request["edits"]!.AsArray();string action=S(request,"action");
        Need(edits.Count is >0 and <=64,"Bounded branch edits required");
        if(frame)return FrameOrder(graph,S(request,"path"),edits);
        if(action=="compound-order")return CompoundOrder(graph,edits);
        if(action=="order"){
            Need(edits.All(e=>e is JsonObject row&&row.Count==4&&row.All(p=>p.Key is "action" or "node" or "port" or "to")
                &&S(e,"action")=="route"&&e["to"] is JsonValue v&&v.TryGetValue<string>(out _)),"Exact branch routes required");
            var anchor=edits.Single(e=>S(e,"port").StartsWith("case:",StringComparison.Ordinal))!;
            var region=Read(graph,S(anchor,"node"),S(anchor,"port"));
            var routes=edits.ToDictionary(e=>S(e,"node"),e=>e!,StringComparer.Ordinal);
            Need(routes.Count==region.Nodes.Count+1 && region.Nodes.All(routes.ContainsKey)
                &&edits.Where(e=>!ReferenceEquals(e,anchor)).All(e=>S(e,"port")=="next"&&region.Nodes.Contains(S(e,"node"))),
                "One complete original branch chain required");
            var seen=new HashSet<string>(StringComparer.Ordinal);string at=S(anchor,"to");
            while(region.Nodes.Contains(at)){Need(seen.Add(at),"Branch order cannot contain a cycle");at=S(routes[at],"to");}
            Need(seen.Count==region.Nodes.Count&&at==region.End,"Branch order cannot drop nodes or change its exit");
            var edges=graph["edges"]!.DeepClone().AsArray();
            foreach(var row in edits){
                foreach(var edge in edges.Where(e=>S(e,"from")==S(row,"node")&&S(e,"port")==S(row,"port")).ToArray())edges.Remove(edge);
                edges.Add(new JsonObject{["from"]=S(row,"node"),["port"]=S(row,"port"),["to"]=S(row,"to")});
            }
            return new JsonObject{["edges"]=edges,["owner"]=region.Owner,["port"]=region.Port};
        }
        Need(action=="create"&&edits.Count==6,"One ordinary branch insertion required");
        var creation=edits.Single(e=>S(e,"action")=="createNode")!;string created=S(creation,"node");var definition=creation["definition"]!.AsObject();string owner=S(definition,"branchOwner");
        Need(creation.AsObject().Count==3 && definition.Count==5 && definition.All(p=>p.Key is "kind" or "control" or "intent" or "signature" or "branchOwner")
            && Ordinary(definition,owner) && owner.Length>0 && !graph["nodes"]!.AsArray().Any(n=>S(n,"id")==created)
            && definition["signature"] is JsonObject sig && sig.Count==2 && sig["args"] is JsonArray{Count:0} && S(sig,"return")=="void",
            "New no-argument void cell with the original branch owner required");
        Need(edits.Where(e=>S(e,"action")!="route").All(e=>S(e,"node")==created&&(ReferenceEquals(e,creation)
            ||e is JsonObject row&&row.Count==3&&S(e,"action") is "rename" or "intent" or "source"&&e["text"] is JsonValue text&&text.TryGetValue<string>(out _)))
            &&new[]{"rename","intent","source"}.All(a=>edits.Count(e=>S(e,"action")==a)==1),"Exact new cell source and name required");
        var routesForCreation=edits.Where(e=>S(e,"action")=="route").ToArray();
        Need(routesForCreation.Length==2&&routesForCreation.All(e=>e is JsonObject row&&row.Count==4&&row.All(p=>p.Key is "action" or "node" or "port" or "to")),"Exact insertion routes required");
        var outgoing=routesForCreation.Single(e=>S(e,"node")==created)!;var incoming=routesForCreation.Single(e=>S(e,"node")!=created)!;
        Need(S(outgoing,"port")=="next"&&S(incoming,"to")==created,"One new serial cell required");
        var parent=graph["nodes"]!.AsArray().Single(n=>S(n,"id")==owner)!;
        var possibilities=parent["executionEnum"]!["members"]!.AsArray().Where(m=>S(m,"id")!=S(parent["executionEnum"],"primary"));
        bool accepted=false;
        foreach(var member in possibilities){
            string port="case:"+S(member,"id");
            if(S(incoming,"node")==owner&&S(incoming,"port")!=port)continue;
            Region region;try{region=Read(graph,owner,port);}catch(ArgumentException){continue;}
            int index=region.Nodes.IndexOf(S(incoming,"node"));
            if(!(S(incoming,"node")==owner&&S(incoming,"port")==port||index>=0&&S(incoming,"port")=="next"))continue;
            string next=index<0?(region.Nodes.FirstOrDefault()??region.End):index+1<region.Nodes.Count?region.Nodes[index+1]:region.End;
            if(S(outgoing,"to")==next){accepted=true;break;}
        }
        Need(accepted,"Insert inside one exclusive original branch without changing its continuation");
        return new JsonObject{["accepted"]=true};
    }
}
