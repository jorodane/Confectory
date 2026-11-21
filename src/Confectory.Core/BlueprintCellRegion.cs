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

    static bool PlainCallContext(JsonNode node) =>
        new[]{"implementationContext","postCall","executionSource","retainedCode","contextBoundary"}.All(key=>node[key] is null)
        && node["async"]?.GetValue<bool>()!=true && node["forwardCallerStorage"]?.GetValue<bool>()!=true;

    // This child is an opaque unit to the parent order plan, but its existing
    // topology must be explicit and exclusive before that plan can move it.
    static string CheckCompoundSwitchChild(JsonObject graph, JsonArray nodes)
    {
        var selectors=nodes.Where(n=>S(n,"control")=="switch").ToArray();
        Need(selectors.Length==1,"Exactly one direct child switch required");
        var selector=selectors[0]!;
        string owner=S(selector,"id");
        Need(selector["executionEnum"] is JsonObject,"Declared switch cases required");
        var flow=selector["executionEnum"]!.AsObject();
        var members=flow["members"]!.AsArray();
        var cases=members.Where(member=>S(member,"id")!=S(flow,"primary")).ToArray();
        Need(members.Count==3&&cases.Length==2&&nodes.All(n=>S(n,"kind")=="code"&&PlainCallContext(n!)),
            "One owned switch with two explicit cases and plain code cells required");
        var edges=graph["edges"]!.AsArray();
        var casesByPort=cases.Select(member=>Read(graph,owner,"case:"+S(member,"id"))).ToArray();
        var branches=casesByPort.SelectMany(region=>region.Nodes).ToHashSet(StringComparer.Ordinal);
        Need(casesByPort.All(region=>region.Nodes.Count>0&&region.End=="return:"+owner)
            && branches.Count==casesByPort.Sum(region=>region.Nodes.Count)
            && edges.Count==nodes.Count+cases.Length
            && nodes.All(n=>edges.Count(e=>S(e,"from")==S(n,"id")&&S(e,"port")=="next")==1)
            && edges.All(e=>S(e,"port")=="next" ||
                S(e,"from")==owner&&casesByPort.Any(region=>region.Port==S(e,"port"))),
            "Keep explicit, disjoint case chains and their original switch return");

        var main=nodes.Where(n=>!branches.Contains(S(n,"id"))).ToDictionary(n=>S(n,"id"),n=>n!,StringComparer.Ordinal);
        string at=S(graph,"entry");
        var visited=new HashSet<string>(StringComparer.Ordinal);
        while(main.TryGetValue(at,out var node)){
            Need(visited.Add(at)&&node["branchOwner"] is null &&
                (at==owner || S(node,"control")=="next"&&node["executionEnum"] is null),
                "Keep the explicit serial switch continuation");
            at=S(edges.Single(e=>S(e,"from")==at&&S(e,"port")=="next"),"to");
        }
        Need(visited.Count==main.Count&&visited.Contains(owner)&&at.StartsWith("exit:",StringComparison.Ordinal)
            && graph["exits"]!.AsObject().ContainsKey(at[5..]),"Keep the switch child's existing exit");
        return at;
    }

    // Move an existing compound as one invocation. No descendant, signature or
    // storage binding is rewritten; the normal compiler checks value dominance.
    static JsonObject CompoundOrder(JsonObject graph, JsonArray edits, bool ordinaryFrame=false, bool allowSwitchChild=false)
    {
        int total=0, switchChildren=0;
        string Chain(JsonObject g,int depth)
        {
            bool switchChild=allowSwitchChild&&depth==1&&S(g,"profile")==FeatureBlueprint.SwitchProfile;
            Need(depth<=8 && (S(g,"profile")==FeatureBlueprint.NestedProfile||switchChild) && g["copySource"] is null
                && g["executionExitMode"]?.GetValue<bool>()!=true,"Direct synchronous compound chain required");
            var nodes=g["nodes"]!.AsArray(); total+=nodes.Count;
            Need(nodes.Count is >0 and <64 && total<=256,"Bounded complete compound chain required");
            if(switchChild){
                Need(++switchChildren==1,"At most one direct switch child per compound order");
                return CheckCompoundSwitchChild(g,nodes);
            }
            var names=nodes.Select(n=>S(n,"id")).ToHashSet(StringComparer.Ordinal);
            Need(names.Count==nodes.Count && nodes.All(n=>S(n,"kind") is "code" or "graph" && S(n,"control")=="next"
                && n!["branchOwner"] is null && n["executionEnum"] is null && PlainCallContext(n)),
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
    static JsonObject OwnedFrame(JsonObject root,string path)
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
        var routes=new JsonArray{new JsonObject{["action"]="entry",["node"]="$entry",["to"]=selected["entry"]!.DeepClone()}};
        foreach(var edge in selected["edges"]!.AsArray())routes.Add(new JsonObject{["action"]="route",["node"]=edge!["from"]!.DeepClone(),["port"]=edge["port"]!.DeepClone(),["to"]=edge["to"]!.DeepClone()});
        CompoundOrder(selected,routes,true);
        return selected;
    }
    static JsonObject FrameCreate(JsonObject root,string path,JsonArray edits)
    {
        var selected=OwnedFrame(root,path);
        Need(edits.Count==6,"Exactly one owned child insertion required");
        var creation=edits.Single(e=>S(e,"action")=="createNode")!;
        string id=S(creation,"node");var definition=creation["definition"]!.AsObject();
        Need(creation.AsObject().Count==3 && definition.Count==4
            && definition.All(p=>p.Key is "kind" or "control" or "intent" or "signature")
            && Ordinary(definition,"") && !string.IsNullOrWhiteSpace(S(definition,"intent"))
            && System.Text.RegularExpressions.Regex.IsMatch(id,@"\A[A-Za-z_][A-Za-z_0-9.-]{0,127}\z")
            && !selected["nodes"]!.AsArray().Any(n=>S(n,"id")==id)
            && definition["signature"] is JsonObject sig && sig.Count==2
            && sig["args"] is JsonArray{Count:0} && S(sig,"return")=="void",
            "One new local no-argument void code cell required");
        Need(new[]{"rename","intent","source"}.All(a=>edits.Count(e=>S(e,"action")==a)==1)
            && edits.Where(e=>S(e,"action")!="route").All(e=>S(e,"node")==id&&(ReferenceEquals(e,creation)
                ||e is JsonObject row&&row.Count==3&&S(e,"action") is "rename" or "intent" or "source"
                &&e["text"] is JsonValue value&&value.TryGetValue<string>(out _))),"Only the new child body/name may be edited");
        var routes=edits.Where(e=>S(e,"action")=="route").ToArray();
        Need(routes.Length==2&&routes.All(e=>e is JsonObject row&&row.Count==4
            &&row.All(p=>p.Key is "action" or "node" or "port" or "to")&&S(e,"port")=="next"),"Two exact insertion routes required");
        var incoming=routes.Single(e=>S(e,"node")!=id)!;var outgoing=routes.Single(e=>S(e,"node")==id)!;
        Need(S(incoming,"to")==id&&selected["nodes"]!.AsArray().Any(n=>S(n,"id")==S(incoming,"node"))
            &&selected["edges"]!.AsArray().Any(e=>S(e,"from")==S(incoming,"node")&&S(e,"port")=="next"&&S(e,"to")==S(outgoing,"to")),
            "Insert after one observed cell without changing its continuation");
        var candidate=root.DeepClone().AsObject();var child=OwnedFrame(candidate,path);
        var made=definition.DeepClone().AsObject();made["id"]=id;child["nodes"]!.AsArray().Add(made);
        var edge=child["edges"]!.AsArray().Single(e=>S(e,"from")==S(incoming,"node"))!;edge["to"]=id;
        child["edges"]!.AsArray().Add(new JsonObject{["from"]=id,["port"]="next",["to"]=S(outgoing,"to")});
        // Recheck the original depth/per-frame/global limits including the new cell.
        OwnedFrame(candidate,path);
        return new JsonObject{["entry"]=child["entry"]!.DeepClone(),["edges"]=child["edges"]!.DeepClone()};
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

    sealed record TransferScope(Region[] Cases, HashSet<string> Movable);

    static TransferScope ReadTransferScope(JsonObject graph, bool includeRoot=false, bool requirePair=true)
    {
        Need(graph["schema"]?.GetValue<int>()==1 && (graph["locals"] is null or JsonArray {Count:0}),
            "Transfer requires a standalone switch with no local storage");
        var nodes=graph["nodes"]!.AsArray();
        var selectors=nodes.Where(n=>S(n,"control")=="switch").ToArray();
        Need(selectors.Length==1 && nodes.All(n=>S(n,"kind")=="code" && PlainCallContext(n!)
            && S(n,"control") is "next" or "switch"),"Exactly one ordinary switch and ordinary code cells required");
        var selector=selectors[0]!;
        string owner=S(selector,"id");
        var execution=selector["executionEnum"]!.AsObject();
        var cases=execution["members"]!.AsArray().Where(m=>S(m,"id")!=S(execution,"primary"))
            .Select(m=>Read(graph,owner,"case:"+S(m,"id"))).ToArray();
        Need(requirePair ? cases.Length==2 : cases.Length is >0 and <64,
            requirePair ? "Exactly two explicit non-primary cases required" : "Bounded explicit non-primary cases required");
        var edges=graph["edges"]!.AsArray();
        var members=cases.SelectMany(region=>region.Nodes).ToHashSet(StringComparer.Ordinal);
        Need((includeRoot||members.Count>0) && members.Count==cases.Sum(region=>region.Nodes.Count)
            && nodes.Where(n=>n!["branchOwner"] is not null).All(n=>members.Contains(S(n,"id")))
            && edges.Where(e=>S(e,"from")==owner).All(e=>S(e,"port")=="next"||cases.Any(region=>region.Port==S(e,"port")))
            && edges.Any(e=>S(e,"from")==owner&&S(e,"port")=="next")
            && members.All(id=>edges.Any(e=>S(e,"from")==id&&S(e,"port")=="next")),
            "Keep unique explicitly linked cases and the original switch continuation");

        var referenced=new HashSet<string>(StringComparer.Ordinal);
        void ReadValueReferences(JsonNode? value)
        {
            if(value is JsonObject obj){
                if(obj["node"] is JsonValue node && node.TryGetValue<string>(out var id))referenced.Add(id);
                foreach(var property in obj)ReadValueReferences(property.Value);
            }else if(value is JsonArray array){
                foreach(var item in array)ReadValueReferences(item);
            }
        }
        foreach(var node in nodes)ReadValueReferences(node!["arguments"]);
        ReadValueReferences(graph["exits"]);
        var movable=nodes.Where(n=>(includeRoot||members.Contains(S(n,"id"))) && S(n,"control")=="next"
            && n!["signature"] is JsonObject signature
            && S(signature,"return")=="void" && signature["args"] is JsonArray {Count:0}
            && n["arguments"] is null or JsonObject {Count:0} && !referenced.Contains(S(n,"id")))
            .Select(n=>S(n,"id")).ToHashSet(StringComparer.Ordinal);
        return new(cases,movable);
    }

    sealed record Lane(string Id, string Anchor, string Port, List<string> Order, string Exit);
    sealed record ScopeTransfer(string Owner, List<Lane> Lanes, HashSet<string> Movable);

    static ScopeTransfer ReadScopeTransfer(JsonObject graph, bool requirePair=true)
    {
        var cases=ReadTransferScope(graph,true,requirePair);
        string owner=cases.Cases[0].Owner;
        var root=graph["nodes"]!.AsArray().Where(n=>n!["branchOwner"] is null)
            .Select(n=>S(n,"id")).ToHashSet(StringComparer.Ordinal);
        var edges=graph["edges"]!.AsArray();
        Need(edges.Count==graph["nodes"]!.AsArray().Count+cases.Cases.Length,
            "One authored continuation per ordinary node required");
        var links=edges.Where(e=>S(e,"port")=="next").ToDictionary(e=>S(e,"from"),e=>S(e,"to"),StringComparer.Ordinal);
        var seen=new HashSet<string>(StringComparer.Ordinal);
        string entry=S(graph,"entry"), at=entry, previous="";
        var before=new List<string>();
        var after=new List<string>();
        bool passedSwitch=false;
        while(root.Contains(at)){
            string here=at;
            Need(seen.Add(here) && edges.Where(e=>S(e,"to")==here)
                .All(e=>S(e,"from")==previous&&S(e,"port")=="next"),"Keep the exclusive root execution chain");
            if(here==owner)passedSwitch=true;
            else (passedSwitch?after:before).Add(here);
            previous=here;
            Need(links.TryGetValue(here,out string? next),"Keep every explicit root next route");
            at=next!;
        }
        Need(passedSwitch && seen.SetEquals(root) && at.StartsWith("exit:",StringComparison.Ordinal)
            && graph["exits"]!.AsObject().ContainsKey(at[5..]),"Retain the complete root chain and explicit exit");
        var lanes=new List<Lane>{new("root-before","$entry","next",before,owner)};
        // Keep the exact switch continuation. Its first cell may anchor an
        // insertion after itself, but may never move or acquire a predecessor.
        if(after.Count>0)lanes.Add(new("root-after",after[0],"next",after.Skip(1).ToList(),at));
        lanes.AddRange(cases.Cases.Select(c=>new Lane(c.Port,owner,c.Port,c.Nodes,c.End)));
        cases.Movable.IntersectWith(lanes.SelectMany(lane=>lane.Order));
        return new(owner,lanes,cases.Movable);
    }

    static bool Case(Lane lane) => lane.Id.StartsWith("case:",StringComparison.Ordinal);

    internal static string[] RemovableCaseCells(JsonObject graph)
    {
        // Reuse the same partition proof as root/case transfers. Exclude any
        // context whose code source is retained under a separate identity.
        if(graph["nodes"]!.AsArray().Any(n=>n?["sourceIdentity"] is not null))
            return [];
        try {
            var scope=ReadScopeTransfer(graph,requirePair:false);
            return scope.Lanes.Where(Case).SelectMany(lane=>lane.Order).Where(scope.Movable.Contains).ToArray();
        } catch(ArgumentException) {
            return [];
        }
    }

    static JsonObject ScopeTransferOptions(ScopeTransfer scope) => new(){
        ["owner"]=scope.Owner,
        ["lanes"]=new JsonArray(scope.Lanes.Select(lane=>(JsonNode)new JsonObject{
            ["id"]=lane.Id,["anchor"]=lane.Anchor,["port"]=lane.Port,["exit"]=lane.Exit,
            ["order"]=System.Text.Json.JsonSerializer.SerializeToNode(lane.Order)
        }).ToArray()),
        ["movable"]=System.Text.Json.JsonSerializer.SerializeToNode(scope.Movable.Order(StringComparer.Ordinal))
    };

    static JsonObject TransferScopeBoundary(JsonObject graph, JsonArray edits)
    {
        Need(edits.Count==1 && edits[0] is JsonObject row && row.Count==3
            && S(row,"action")=="crossCase" && row["definition"] is JsonObject plan && plan.Count==3,
            "One exact scope transfer placement required");
        var edit=edits[0]!;
        var destination=edit["definition"]!;
        string moved=S(edit,"node"), laneId=S(destination,"lane"), anchor=S(destination,"anchor"), side=S(destination,"side");
        var scope=ReadScopeTransfer(graph);
        Need(scope.Movable.Contains(moved),"Only one unconnected void cell may move between scopes");
        var source=scope.Lanes.Single(lane=>lane.Order.Contains(moved));
        var target=scope.Lanes.Single(lane=>lane.Id==laneId);
        Need(Case(source)!=Case(target) && side is "before" or "after","Select a placement in the other execution scope");
        int index=target.Order.IndexOf(anchor);
        if(index>=0)index+=side=="after"?1:0;
        else if(target.Id=="root-before"&&anchor==scope.Owner&&side=="before")index=target.Order.Count;
        else if(target.Id=="root-after"&&anchor==target.Anchor&&side=="after")index=0;
        else if(Case(target)&&target.Order.Count==0&&anchor=="$empty"&&side=="before")index=0;
        Need(index>=0,"Select a cell in the observed destination or the empty case position");

        source.Order.Remove(moved);
        target.Order.Insert(index,moved);
        var candidate=graph.DeepClone().AsObject();
        var edges=candidate["edges"]!.AsArray().ToDictionary(e=>(S(e,"from"),S(e,"port")));
        foreach(var lane in new[]{source,target}){
            string first=lane.Order.FirstOrDefault()??lane.Exit;
            if(lane.Anchor=="$entry")candidate["entry"]=first;
            else edges[(lane.Anchor,lane.Port)]!["to"]=first;
            for(int i=0;i<lane.Order.Count;i++)edges[(lane.Order[i],"next")]!["to"]=i+1<lane.Order.Count?lane.Order[i+1]:lane.Exit;
        }
        var node=candidate["nodes"]!.AsArray().Single(n=>S(n,"id")==moved)!.AsObject();
        if(Case(target))node["branchOwner"]=scope.Owner;
        else node.Remove("branchOwner");
        ReadScopeTransfer(candidate);
        return new JsonObject{["graph"]=candidate};
    }

    static JsonObject TransferOptions(TransferScope scope) => new(){
        ["owner"]=scope.Cases[0].Owner,
        ["cases"]=new JsonArray(scope.Cases.Select(region=>(JsonNode)new JsonObject{
            ["port"]=region.Port,["exit"]=region.End,
            ["order"]=System.Text.Json.JsonSerializer.SerializeToNode(region.Nodes)
        }).ToArray()),
        ["movable"]=System.Text.Json.JsonSerializer.SerializeToNode(scope.Movable.Order(StringComparer.Ordinal))
    };

    static JsonObject TransferOrder(JsonObject graph, JsonArray edits, TransferScope scope)
    {
        var owner=scope.Cases[0].Owner;
        var routes=edits.ToDictionary(e=>(S(e,"node"),S(e,"port")),e=>S(e,"to"));
        var members=scope.Cases.SelectMany(region=>region.Nodes).ToHashSet(StringComparer.Ordinal);
        Need(routes.Count==members.Count+2 && members.All(id=>routes.ContainsKey((id,"next")))
            && scope.Cases.All(region=>routes.ContainsKey((owner,region.Port))),"Both exact complete case routes required");
        var seen=new HashSet<string>(StringComparer.Ordinal);
        List<string> Candidate(Region region){
            var order=new List<string>();
            string at=routes[(owner,region.Port)];
            while(members.Contains(at)){
                Need(seen.Add(at),"Case plan cannot repeat or share a cell");
                order.Add(at);at=routes[(at,"next")];
            }
            Need(at==region.End,"Retain each case's original terminal");
            return order;
        }
        var result=scope.Cases.Select(Candidate).ToArray();
        Need(seen.Count==members.Count,"Retain the union of both original cases");
        bool MovedOneToEnd(int destination){
            int source=1-destination;
            if(result[destination].Count!=scope.Cases[destination].Nodes.Count+1)return false;
            string moved=result[destination][^1];
            return scope.Movable.Contains(moved) && scope.Cases[source].Nodes.Contains(moved)
                && result[source].SequenceEqual(scope.Cases[source].Nodes.Where(id=>id!=moved))
                && result[destination].SkipLast(1).SequenceEqual(scope.Cases[destination].Nodes);
        }
        Need(MovedOneToEnd(0)||MovedOneToEnd(1),"Move exactly one unconnected void cell to the other case's end");

        var edges=graph["edges"]!.DeepClone().AsArray();
        foreach(var edge in edges){
            if(routes.TryGetValue((S(edge,"from"),S(edge,"port")),out var to))edge!["to"]=to;
        }
        return new JsonObject{["edges"]=edges};
    }

    public static JsonObject Query(JsonObject request)
    {
        bool frame=S(request,"action") is "frame-order" or "frame-create";
        Need(request.Count==(3+(request.ContainsKey("operation")?1:0)+(frame?1:0)) && (request["operation"] is null || S(request,"operation")=="blueprintCellRegion") && request.All(p=>p.Key is "operation" or "action" or "graph" or "edits" ||frame&&p.Key=="path"),"Exact cell editor plan required");
        var graph=request["graph"]!.AsObject();var edits=request["edits"]!.AsArray();string action=S(request,"action");
        if(action=="transfer-options"){
            Need(edits.Count==0,"Read transfer options without edits");
            return TransferOptions(ReadTransferScope(graph));
        }
        if(action=="scope-transfer-options"){
            Need(edits.Count==0,"Read scope transfer options without edits");
            return ScopeTransferOptions(ReadScopeTransfer(graph));
        }
        if(action=="scope-transfer")return TransferScopeBoundary(graph,edits);
        Need(edits.Count is >0 and <=64,"Bounded branch edits required");
        if(frame)return action=="frame-create"?FrameCreate(graph,S(request,"path"),edits):CompoundOrder(OwnedFrame(graph,S(request,"path")),edits,true);
        if(action=="compound-order")return CompoundOrder(graph,edits,allowSwitchChild:true);
        if(action is "order" or "transfer"){
            Need(edits.All(e=>e is JsonObject row&&row.Count==4&&row.All(p=>p.Key is "action" or "node" or "port" or "to")
                &&S(e,"action")=="route"&&e["to"] is JsonValue v&&v.TryGetValue<string>(out _)),"Exact branch routes required");
            if(action=="transfer")return TransferOrder(graph,edits,ReadTransferScope(graph));
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
