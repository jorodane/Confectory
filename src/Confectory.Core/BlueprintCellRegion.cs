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
    static JsonObject CompoundOrder(JsonObject graph, JsonArray edits, bool ordinaryFrame=false, bool allowSwitchChild=false,
        int methodPreviewDepth=0, bool methodFrameOrder=false, bool previewOutParameters=false, JsonObject? detachedFrame=null,
        JsonObject? nestedSwitchFrame=null)
    {
        int total=0, switchChildren=0;
        string Chain(JsonObject g,int depth)
        {
            bool switchChild=allowSwitchChild&&(depth==1||depth==2&&ReferenceEquals(g,nestedSwitchFrame))
                &&S(g,"profile")==FeatureBlueprint.SwitchProfile;
            bool methodLeaf=S(g,"profile")==FeatureBlueprint.MethodsProfile
                && (depth>0&&depth<=methodPreviewDepth || depth==0&&methodFrameOrder);
            Need(depth<=8 && (S(g,"profile")==FeatureBlueprint.NestedProfile||switchChild||methodLeaf) && g["copySource"] is null
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
            if(methodPreviewDepth>0||methodLeaf)
                Need(nodes.All(node=>node!["sourceIdentity"] is null && node["completionBranch"] is null
                    && node[BlueprintCompletionAdapter.Metadata] is null), "Ordinary synchronous method frame required");
            if(methodLeaf)
            {
                bool previewOutLeaf=previewOutParameters && nodes.Any(HasOutParameter);
                Need((g["locals"] is null or JsonArray {Count:0} ||
                        previewOutLeaf && NumericConstantLocals(g["locals"]))
                    && nodes.All(node=>S(node,"kind")=="code" && ValueParameters(node!, previewOutLeaf)),
                    "Method frame requires ordinary code leaves and supported parameter storage");
            }
            var edges=g["edges"]!.AsArray();
            Need(edges.Count==nodes.Count && edges.All(e=>S(e,"port")=="next"&&names.Contains(S(e,"from")))
                &&edges.Select(e=>S(e,"from")).Distinct(StringComparer.Ordinal).Count()==nodes.Count,"One exclusive next route per cell required");
            var links=edges.ToDictionary(e=>S(e,"from"),e=>S(e,"to"),StringComparer.Ordinal);
            var seen=new HashSet<string>(StringComparer.Ordinal);string at=S(g,"entry");
            while(names.Contains(at)){Need(seen.Add(at),"Compound chain cannot cycle");at=links[at];}
            bool reconnect = ReferenceEquals(g, detachedFrame);
            Need((reconnect||seen.Count==names.Count)&&at.StartsWith("exit:",StringComparison.Ordinal)
                &&g["exits"]!.AsObject().ContainsKey(at[5..]),"Retain every cell and the original frame exit");
            if (reconnect)
            {
                Need(seen.Count>0&&nodes.All(n=>S(n,"kind")=="code"&&ValueParameters(n!)&&n!["sourceIdentity"] is null
                    &&n["completionBranch"] is null&&n[BlueprintCompletionAdapter.Metadata] is null)&&g["locals"] is null or JsonArray {Count:0},
                    "Detached reconnect requires ordinary code cells, value parameters and an explicit entry");
                foreach (string id in names.Where(id=>!seen.Contains(id)))
                {
                    var detached = new HashSet<string>(StringComparer.Ordinal);
                    string next = id;
                    while (links.TryGetValue(next,out var continuation)&&!seen.Contains(next))
                    {
                        Need(detached.Add(next),"Detached cells cannot cycle");
                        next = continuation;
                    }
                    Need(next==at||seen.Contains(next),"Preserve the existing detached cell continuation and exit");
                }
            }
            foreach(var node in nodes.Where(n=>S(n,"kind")=="graph")){
                var child=node!["graph"]!.AsObject();
                if(methodPreviewDepth>0&&S(child,"profile")==FeatureBlueprint.MethodsProfile)
                    Need(ValueParameters(node!),"Method preview requires an ordinary value-parameter frame");
                Chain(child,depth+1);
            }
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

    static bool ValueParameters(JsonNode node, bool previewOutParameters=false) => node["signature"]?["args"] is JsonArray args
        && args.All(arg=>S(arg,"mode")=="" ||
            previewOutParameters && S(arg,"mode")=="out" && S(arg,"type") is "long" or "double");

    static bool HasOutParameter(JsonNode? node) => node?["signature"]?["args"] is JsonArray args &&
        args.Any(arg=>S(arg,"mode")=="out");

    static bool NumericConstantLocals(JsonNode? value) => value is JsonArray {Count: <=64} locals
        && locals.All(local=>local is JsonObject {Count:4} declaration
            && declaration.ContainsKey("id") && declaration.ContainsKey("name")
            && S(declaration,"type") is "long" or "double"
            && declaration["initial"] is JsonObject {Count:1} initial && initial.ContainsKey("constant"));

    static JsonArray CurrentRoutes(JsonObject graph)
    {
        var routes=new JsonArray{new JsonObject{["action"]="entry",["node"]="$entry",["to"]=graph["entry"]!.DeepClone()}};
        foreach(var edge in graph["edges"]!.AsArray())routes.Add(new JsonObject{["action"]="route",["node"]=edge!["from"]!.DeepClone(),["port"]=edge["port"]!.DeepClone(),["to"]=edge["to"]!.DeepClone()});
        return routes;
    }

    internal static JsonObject OwnedPreviewFrame(JsonObject root, string path, bool previewOutParameters=false, bool allowDetached=false)
    {
        var segments = path.Split('/');
        Need(segments.All(part => part.Length > 0), "Exact nonempty owned frame path required");
        var selected = BlueprintTree.Select(root, path);
        if (segments.Length == 1 && S(selected, "profile") == FeatureBlueprint.SwitchProfile)
        {
            OwnedSwitchFrame(root, path);
            Need(selected["nodes"]!.AsArray().All(node => node!["sourceIdentity"] is null
                && node["completionBranch"] is null && node[BlueprintCompletionAdapter.Metadata] is null),
                "Ordinary synchronous switch preview required");
            return selected;
        }
        // Verify the entire owned tree, including every ancestor and sibling.
        // IDs remain local to each frame; the caller binds the physical root.
        bool methodFrame = S(selected, "profile") == FeatureBlueprint.MethodsProfile;
        JsonObject[] methodChildren = segments.Length == 1 && IsCompoundFrame(selected)
            ? selected["nodes"]!.AsArray().Where(node => S(node, "kind") == "graph")
                .Select(node => node?["graph"]).OfType<JsonObject>()
                .Where(child => S(child, "profile") == FeatureBlueprint.MethodsProfile).ToArray()
            : [];
        int methodDepth = methodFrame ? segments.Length : methodChildren.Length > 0 ? 2 : 0;
        Need(methodDepth <= 2, "Method preview requires an owned frame at depth one or two");
        bool selectedOutFrame = previewOutParameters && (methodFrame
            ? selected["nodes"]!.AsArray().Any(HasOutParameter)
            : methodChildren.Any(child => child["nodes"]!.AsArray().Any(HasOutParameter)));
        CompoundOrder(root, CurrentRoutes(root), methodPreviewDepth: methodDepth, previewOutParameters: selectedOutFrame,
            detachedFrame: allowDetached ? selected : null);
        return selected;
    }

    internal static JsonObject OwnedFrame(JsonObject root,string path)
    {
        CompoundOrder(root,CurrentRoutes(root));
        Need(path.Split('/').All(part => part.Length > 0), "Exact nonempty owned frame path required");
        var selected = BlueprintTree.Select(root, path);
        CompoundOrder(selected,CurrentRoutes(selected),true);
        return selected;
    }

    static JsonObject EditableFrame(JsonObject root, string path, bool allowDesktopFrames)
    {
        var selected = BlueprintTree.Select(root, path);
        if (S(selected, "profile") != FeatureBlueprint.MethodsProfile)
            return OwnedFrame(root, path);

        Need(allowDesktopFrames, "Owned method frame editing requires desktop authoring");
        return OwnedPreviewFrame(root, path);
    }

    static JsonObject FrameOrder(JsonObject root, string path, JsonArray edits, bool allowDesktopFrames)
    {
        if (allowDesktopFrames && path.Length > 0 && !path.Contains('/') &&
            IsCompoundFrame(BlueprintTree.Select(root, path)))
        {
            var parent = OwnedCompoundFrame(root, path);
            return CompoundOrder(parent, edits, methodPreviewDepth: 1);
        }
        var selected = EditableFrame(root, path, allowDesktopFrames);
        return CompoundOrder(selected, edits, ordinaryFrame: true,
            methodFrameOrder: S(selected, "profile") == FeatureBlueprint.MethodsProfile);
    }

    static JsonObject FrameReconnect(JsonObject root, string path, JsonArray edits)
    {
        Need(path.Split('/').Length is 1 or 2 && edits.Count<=1,"Select one existing edge of an owned child frame");
        var selected = BlueprintTree.Select(root, path);
        if (S(selected,"profile")==FeatureBlueprint.SwitchProfile)
            return FrameCaseReconnect(root, path, selected, edits);
        Need(S(selected,"profile") is FeatureBlueprint.MethodsProfile or FeatureBlueprint.NestedProfile,
            "Ordinary serial child frame required");
        OwnedPreviewFrame(root,path,allowDetached:true);
        var edges = selected["edges"]!.AsArray();
        var links = edges.ToDictionary(e=>S(e,"from"),e=>S(e,"to"),StringComparer.Ordinal);
        string entry = S(selected,"entry");
        var active = new List<string>{"$entry"};
        for (string next=entry;links.TryGetValue(next,out var continuation);next=continuation) active.Add(next);
        var incoming = links.Values.ToHashSet(StringComparer.Ordinal);
        var targets = new JsonObject();
        foreach (string source in active)
        {
            string current = source=="$entry" ? entry : links[source];
            var choices = links.Where(link=>link.Value==current&&!active.Contains(link.Key)&&!incoming.Contains(link.Key))
                .Select(link=>(JsonNode?)JsonValue.Create(link.Key)).ToArray();
            if (choices.Length>0) targets[source]=new JsonArray(choices);
        }
        if (edits.Count==0) return targets;

        var edit = edits[0]!.AsObject();
        string from = S(edit,"node"), to = S(edit,"to");
        bool entryEdit = from=="$entry" && S(edit,"action")=="entry" && edit.Count==3;
        bool routeEdit = from!="$entry" && S(edit,"action")=="route" && S(edit,"port")=="next" && edit.Count==4;
        Need((entryEdit||routeEdit)&&targets[from] is JsonArray allowed&&allowed.Any(id=>id!.GetValue<string>()==to),
            "Choose an existing detached cell in the observed child frame with the same continuation");
        var routes = edges.DeepClone().AsArray();
        if (routeEdit) routes.Single(edge=>S(edge,"from")==from)!["to"]=to;
        return new JsonObject{["entry"]=entryEdit ? to : entry,["edges"]=routes};
    }
    static JsonObject FrameCaseReconnect(JsonObject root, string path, JsonObject child, JsonArray edits)
    {
        var options = BranchReconnect(child, new JsonArray());
        var choices = options.SelectMany(owner => owner.Value!.AsObject().SelectMany(port =>
            port.Value!.AsArray().Select(target => new JsonObject
            {
                ["action"] = "route", ["node"] = owner.Key, ["port"] = port.Key, ["to"] = target!.DeepClone(),
            }))).ToArray();
        Need(choices.Length==1, "Restore one empty case to its detached, same-owner continuation");
        var plan = BranchReconnect(child, new JsonArray(choices[0]));
        // Check the complete physical hierarchy with only this edge restored.
        // The same planner already used for child switch edits must accept it.
        var candidate = root.DeepClone().AsObject();
        BlueprintTree.Select(candidate,path)["edges"] = plan["edges"]!.DeepClone();
        OwnedSwitchFrame(candidate,path, allowNested: true);
        if (edits.Count==0) return options;
        Need(JsonNode.DeepEquals(edits[0],choices[0]), "Exact observed child case target required");
        plan["entry"] = child["entry"]!.DeepClone();
        return plan;
    }

    static string RootStart(JsonObject graph,out bool compound)
    {
        string entry=S(graph,"entry");
        var nodes=graph["nodes"]!.AsArray();
        compound=nodes.Any(n=>S(n,"id")==entry&&S(n,"kind")=="graph");
        if(compound){
            CompoundOrder(graph,CurrentRoutes(graph));
            return entry;
        }
        Need(S(graph,"profile").StartsWith("sync-acyclic-",StringComparison.Ordinal)&&graph["copySource"] is null
            &&graph["executionExitMode"]?.GetValue<bool>()!=true&&nodes.Count is >0 and <64
            &&nodes.All(n=>Ordinary(n!,"")&&PlainCallContext(n!)),"A nonempty ordinary serial root is required");
        var names=nodes.Select(n=>S(n,"id")).ToHashSet(StringComparer.Ordinal);
        var edges=graph["edges"]!.AsArray();
        Need(names.Count==nodes.Count&&edges.Count==nodes.Count&&edges.All(e=>S(e,"port")=="next"&&names.Contains(S(e,"from"))),
            "One next route per original root cell required");
        var routes=edges.ToDictionary(e=>S(e,"from"),e=>S(e,"to"),StringComparer.Ordinal);
        string at=entry;
        var visited=new HashSet<string>(StringComparer.Ordinal);
        while(routes.TryGetValue(at,out var next)){Need(visited.Add(at),"Root chain cannot cycle");at=next;}
        Need(visited.Count==nodes.Count&&at.StartsWith("exit:",StringComparison.Ordinal)&&graph["exits"]!.AsObject().ContainsKey(at[5..]),
            "The current root entry, complete chain and explicit exit are required");
        return entry;
    }

    static JsonObject FrameCreate(JsonObject root, string path, JsonArray edits, bool allowDesktopFrames)
    {
        var candidate=root.DeepClone().AsObject();
        var child=EditableFrame(candidate,path,allowDesktopFrames);
        InsertCell(child,edits,InsertionAnchor.FrameCell);
        // Recheck the original depth/per-frame/global limits including the new cell.
        EditableFrame(candidate,path,allowDesktopFrames);
        return new JsonObject{["entry"]=child["entry"]!.DeepClone(),["edges"]=child["edges"]!.DeepClone()};
    }

    static bool IsCompoundFrame(JsonObject frame) => S(frame, "profile") == FeatureBlueprint.NestedProfile
        && frame["nodes"]!.AsArray().Any(node => S(node, "kind") == "graph");

    static JsonObject OwnedCompoundFrame(JsonObject root, string path)
    {
        Need(path.Length > 0 && !path.Contains('/'), "One directly owned compound parent required");
        var selected = OwnedPreviewFrame(root, path);
        Need(IsCompoundFrame(selected),
            "An existing compound invocation in the selected serial frame is required");
        return selected;
    }

    enum InsertionAnchor { FrameCell, RootStart, CompoundCall }

    static void InsertCell(JsonObject selected,JsonArray edits,InsertionAnchor anchor)
    {
        Need(edits.Count==6,"Exactly one owned cell insertion required");
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
            && edits.Where(e=>S(e,"action") is not ("route" or "entry")).All(e=>S(e,"node")==id&&(ReferenceEquals(e,creation)
                ||e is JsonObject row&&row.Count==3&&S(e,"action") is "rename" or "intent" or "source"
                &&e["text"] is JsonValue value&&value.TryGetValue<string>(out _))),"Only the new cell body/name may be edited");
        var routes=edits.Where(e=>S(e,"action") is "route" or "entry").ToArray();
        Need(routes.Length==2&&routes.All(e=>e is JsonObject row&&row["to"] is JsonValue value&&value.TryGetValue<string>(out _)
            &&(S(row,"action")=="entry"&&row.Count==3&&S(row,"node")=="$entry"
                ||S(row,"action")=="route"&&row.Count==4&&S(row,"port")=="next"
                    &&row.All(p=>p.Key is "action" or "node" or "port" or "to"))),"Exact insertion connections required");
        var incoming=routes.Single(e=>S(e,"node")!=id)!;var outgoing=routes.Single(e=>S(e,"node")==id)!;
        bool atStart=S(incoming,"action")=="entry";
        string successor=S(outgoing,"to");
        Need(anchor switch {
            InsertionAnchor.RootStart=>atStart,
            InsertionAnchor.CompoundCall=>!atStart&&selected["nodes"]!.AsArray().Any(n=>S(n,"id")==S(incoming,"node")&&S(n,"kind")=="graph"),
            _=>true
        },"The insertion anchor must be the selected start or compound call");
        Need(S(outgoing,"action")=="route"&&S(incoming,"to")==id
            &&(atStart?successor==S(selected,"entry"):selected["edges"]!.AsArray().Any(e=>S(e,"from")==S(incoming,"node")&&S(e,"port")=="next"&&S(e,"to")==successor)),
            "Insert on one observed connection without changing its continuation");
        var made=definition.DeepClone().AsObject();made["id"]=id;selected["nodes"]!.AsArray().Add(made);
        if(atStart)selected["entry"]=id;
        else selected["edges"]!.AsArray().Single(e=>S(e,"from")==S(incoming,"node"))!["to"]=id;
        selected["edges"]!.AsArray().Add(new JsonObject{["from"]=id,["port"]="next",["to"]=successor});
    }
    static Region Read(JsonObject graph, string owner, string port, bool firstWrappedCase = false)
    {
        Need(S(graph,"profile")==FeatureBlueprint.SwitchProfile && graph["executionExitMode"]?.GetValue<bool>()!=true
            && graph["copySource"] is null, "Only an existing synchronous owned switch region is supported");
        var nodes=graph["nodes"]!.AsArray().ToDictionary(n=>S(n,"id"),n=>n!,StringComparer.Ordinal);
        Need(nodes.Count is >0 and <64 && nodes.TryGetValue(owner,out var parent),"Existing bounded branch owner required");
        parent=nodes[owner];
        if(firstWrappedCase && S(parent,"kind")=="call"){
            var wrapper=parent["postCall"];
            var enumeration=parent["executionEnum"];
            var routes=graph["edges"]!.AsArray().Where(edge=>S(edge,"from")==owner).ToArray();
            Need(graph["schema"]?.GetValue<int>()==1 && S(parent,"control")=="switch"
                && parent["branchOwner"] is null && parent["publicExecution"] is null
                && parent["implementationContext"] is null && parent["executionSource"] is null
                && parent["contextBoundary"] is null && parent["completionBranch"] is null
                && parent["async"]?.GetValue<bool>()!=true && parent["forwardCallerStorage"]?.GetValue<bool>()!=true
                && S(wrapper,"mode")=="execution-enum" && wrapper!["originalExecution"] is null
                && enumeration?["members"] is JsonArray {Count:2} firstMembers
                && firstMembers.Any(member=>"case:"+S(member,"id")==port && S(member,"id")!=S(enumeration,"primary"))
                && routes.Length==1 && S(routes[0],"port")=="next",
                "Select the first empty wrapped-call case with its existing next continuation");
            // An unmatched local enum result already continues on next. A new
            // case action must rejoin that same continuation through its owner.
            return new(owner,port,[],"return:"+owner);
        }
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

    internal static string[] RemovableCaseCells(JsonObject graph, bool terminalOnly = false)
    {
        // Reuse the same partition proof as root/case transfers. Exclude any
        // context whose code source is retained under a separate identity.
        if(graph["nodes"]!.AsArray().Any(n=>n?["sourceIdentity"] is not null))
            return [];
        try {
            var scope=ReadScopeTransfer(graph,requirePair:false);
            return scope.Lanes.Where(lane => Case(lane) && (!terminalOnly || lane.Order.Count > 1))
                .SelectMany(lane => terminalOnly ? lane.Order.TakeLast(1) : lane.Order)
                .Where(scope.Movable.Contains).ToArray();
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

    static void ExactBranchRoutes(JsonArray edits)
    {
        Need(edits.All(e=>e is JsonObject row&&row.Count==4&&row.All(p=>p.Key is "action" or "node" or "port" or "to")
            &&S(e,"action")=="route"&&e["to"] is JsonValue v&&v.TryGetValue<string>(out _)),"Exact branch routes required");
    }

    static JsonObject BranchReconnect(JsonObject graph, JsonArray edits)
    {
        Need(edits.Count <= 1, "Reconnect exactly one declared branch");
        Need(S(graph, "profile") == FeatureBlueprint.SwitchProfile && graph["executionExitMode"]?.GetValue<bool>() != true
            && graph["copySource"] is null && graph["schema"]?.GetValue<int>() == 1,
            "An existing owned synchronous switch is required");
        var nodes = graph["nodes"]!.AsArray();
        var edges = graph["edges"]!.AsArray();
        Need(nodes.Count is > 0 and < 64 && edges.GroupBy(e => (S(e, "from"), S(e, "port"))).All(g => g.Count() == 1),
            "A bounded switch with distinct routes is required");

        var choices = new JsonObject();
        foreach (var selector in nodes.Where(n => S(n, "kind") == "code" && S(n, "control") == "switch"
            && n!["branchOwner"] is null && n[BlueprintCompletionBranch.Metadata] is null && PlainCallContext(n)))
        {
            string owner = S(selector, "id"), continuation = "return:" + owner;
            var outgoing = edges.Where(e => S(e, "from") == owner).ToDictionary(e => S(e, "port"), e => S(e, "to"));
            var detached = nodes.Where(n => Ordinary(n!, owner) && PlainCallContext(n!))
                .Select(n => S(n, "id"))
                .Where(id => S(graph, "entry") != id && !edges.Any(e => S(e, "to") == id)
                    && edges.Any(e => S(e, "from") == id && S(e, "port") == "next" && S(e, "to") == continuation))
                .ToArray();
            if (detached.Length == 0) continue;

            var contract = selector!["executionEnum"]!;
            var ports = new JsonObject();
            foreach (var member in contract["members"]!.AsArray().Where(m => S(m, "id") != S(contract, "primary")))
            {
                string port = "case:" + S(member, "id");
                // An unconnected member uses the switch fallback. Preserve that continuation.
                if (outgoing.GetValueOrDefault(port, outgoing.GetValueOrDefault("default", continuation)) == continuation)
                    ports[port] = new JsonArray(detached.Select(id => (JsonNode?)JsonValue.Create(id)).ToArray());
            }
            if (ports.Count > 0) choices[owner] = ports;
        }
        if (edits.Count == 0) return choices;

        ExactBranchRoutes(edits);
        var edit = edits[0]!;
        string from = S(edit, "node"), selected = S(edit, "port"), target = S(edit, "to");
        Need(choices[from]?[selected] is JsonArray targets && targets.Any(id => id!.GetValue<string>() == target),
            "Select a detached cell in the same switch that keeps the original continuation");
        var result = edges.DeepClone().AsArray();
        var previous = result.SingleOrDefault(e => S(e, "from") == from && S(e, "port") == selected);
        if (previous is null) result.Add(new JsonObject { ["from"] = from, ["port"] = selected, ["to"] = target });
        else previous["to"] = target;
        return new JsonObject { ["edges"] = result };
    }

    static JsonObject OrderBranch(JsonObject graph, JsonArray edits, bool frame = false)
    {
        var anchor=edits.Single(e=>S(e,"port").StartsWith("case:",StringComparison.Ordinal))!;
        var region=Read(graph,S(anchor,"node"),S(anchor,"port"));
        Need(!frame || region.Nodes.Count >= 2, "At least two existing case cells required");
        var routes=edits.ToDictionary(e=>S(e,"node"),e=>e!,StringComparer.Ordinal);
        Need(routes.Count==region.Nodes.Count+1 && region.Nodes.All(routes.ContainsKey)
            &&edits.Where(e=>!ReferenceEquals(e,anchor)).All(e=>S(e,"port")=="next"&&region.Nodes.Contains(S(e,"node"))),
            "One complete original branch chain required");
        var seen=new HashSet<string>(StringComparer.Ordinal);string at=S(anchor,"to");
        while(region.Nodes.Contains(at)){Need(seen.Add(at),"Branch order cannot contain a cycle");at=S(routes[at],"to");}
        Need(seen.Count==region.Nodes.Count&&at==region.End,"Branch order cannot drop nodes or change its exit");
        var edges=graph["edges"]!.DeepClone().AsArray();
        foreach(var row in edits){
            if (frame)
            {
                edges.Single(e => S(e, "from") == S(row, "node") && S(e, "port") == S(row, "port"))!["to"] = S(row, "to");
                continue;
            }
            foreach(var edge in edges.Where(e=>S(e,"from")==S(row,"node")&&S(e,"port")==S(row,"port")).ToArray())edges.Remove(edge);
            edges.Add(new JsonObject{["from"]=S(row,"node"),["port"]=S(row,"port"),["to"]=S(row,"to")});
        }
        return new JsonObject{["edges"]=edges,["owner"]=region.Owner,["port"]=region.Port};
    }

    internal static JsonObject OwnedSwitchFrame(JsonObject root, string path, bool allowNested = false)
    {
        var segments = path.Split('/');
        Need(segments.All(part => part.Length > 0) && (segments.Length == 1 || allowNested && segments.Length == 2),
            "One switch child within the supported owned depth required");
        var child = BlueprintTree.Select(root, path);
        Need(S(child, "profile") == FeatureBlueprint.SwitchProfile, "Owned switch child required");
        CompoundOrder(root, CurrentRoutes(root), allowSwitchChild: true, nestedSwitchFrame: segments.Length == 2 ? child : null);
        return child;
    }

    static JsonObject CreateBranchCell(JsonObject graph, JsonArray edits, bool frame = false)
    {
        Need(edits.Count==6,"One ordinary branch insertion required");
        var creation=edits.Single(e=>S(e,"action")=="createNode")!;string created=S(creation,"node");var definition=creation["definition"]!.AsObject();string owner=S(definition,"branchOwner");
        Need(creation.AsObject().Count==3 && definition.Count==5 && definition.All(p=>p.Key is "kind" or "control" or "intent" or "signature" or "branchOwner")
            && Ordinary(definition,owner) && owner.Length>0
            && (!frame || (!string.IsNullOrWhiteSpace(S(definition, "intent"))
                && System.Text.RegularExpressions.Regex.IsMatch(created, @"\A[A-Za-z_][A-Za-z_0-9.-]{0,127}\z"))) && !graph["nodes"]!.AsArray().Any(n=>S(n,"id")==created)
            && definition["signature"] is JsonObject sig && sig.Count==2 && sig["args"] is JsonArray{Count:0} && S(sig,"return")=="void",
            "New no-argument void cell with the original branch owner required");
        Need(edits.Where(e=>S(e,"action")!="route").All(e=>S(e,"node")==created&&(ReferenceEquals(e,creation)
            ||e is JsonObject row&&row.Count==3&&S(e,"action") is "rename" or "intent" or "source"&&e["text"] is JsonValue text&&text.TryGetValue<string>(out _)))
            &&new[]{"rename","intent","source"}.All(a=>edits.Count(e=>S(e,"action")==a)==1),"Exact new cell source and name required");
        var routesForCreation=edits.Where(e=>S(e,"action")=="route").ToArray();
        Need(routesForCreation.Length==2&&routesForCreation.All(e=>e is JsonObject row&&row.Count==4&&row.All(p=>p.Key is "action" or "node" or "port" or "to")
            &&(!frame || row["to"] is JsonValue value&&value.TryGetValue<string>(out _))),"Exact insertion routes required");
        var outgoing=routesForCreation.Single(e=>S(e,"node")==created)!;var incoming=routesForCreation.Single(e=>S(e,"node")!=created)!;
        Need(S(outgoing,"port")=="next"&&S(incoming,"to")==created,"One new serial cell required");
        var parent=graph["nodes"]!.AsArray().Single(n=>S(n,"id")==owner)!;
        var possibilities=parent["executionEnum"]!["members"]!.AsArray().Where(m=>S(m,"id")!=S(parent["executionEnum"],"primary"));
        bool accepted=false;
        foreach(var member in possibilities){
            string port="case:"+S(member,"id");
            if(S(incoming,"node")==owner&&S(incoming,"port")!=port)continue;
            Region region;try{region=Read(graph,owner,port,firstWrappedCase: !frame);}catch(ArgumentException){continue;}
            if (frame && region.Nodes.Count == 0) continue;
            int index=region.Nodes.IndexOf(S(incoming,"node"));
            if(!(S(incoming,"node")==owner&&S(incoming,"port")==port||index>=0&&S(incoming,"port")=="next"))continue;
            string next=index<0?(region.Nodes.FirstOrDefault()??region.End):index+1<region.Nodes.Count?region.Nodes[index+1]:region.End;
            if(S(outgoing,"to")==next){accepted=true;break;}
        }
        Need(accepted,"Insert inside one exclusive original branch without changing its continuation");
        if (!frame) return new JsonObject{["accepted"]=true};

        var newNode = definition.DeepClone().AsObject();
        newNode["id"] = created;
        graph["nodes"]!.AsArray().Add(newNode);
        var edges = graph["edges"]!.AsArray();
        edges.Single(e => S(e, "from") == S(incoming, "node") && S(e, "port") == S(incoming, "port"))!["to"] = created;
        edges.Add(new JsonObject { ["from"] = created, ["port"] = "next", ["to"] = S(outgoing, "to") });
        return new JsonObject { ["entry"] = graph["entry"]!.DeepClone(), ["edges"] = edges.DeepClone() };
    }

    public static JsonObject Query(JsonObject request) => Query(request, allowDesktopFrames: false);

    public static JsonObject Query(JsonObject request, bool allowDesktopFrames)
    {
        string action = S(request, "action");
        bool preview = allowDesktopFrames && action == "frame-preview";
        bool frameCase = allowDesktopFrames && action is "frame-case-order" or "frame-case-create";
        bool frameCompound = allowDesktopFrames && action is "frame-compound-insert-options" or "frame-compound-insert";
        bool frameReconnect = allowDesktopFrames && action == "frame-reconnect";
        bool frame=action is "frame-order" or "frame-create" || preview || frameCase || frameCompound || frameReconnect;
        Need(request.Count==(3+(request.ContainsKey("operation")?1:0)+(frame?1:0)) && (request["operation"] is null || S(request,"operation")=="blueprintCellRegion") && request.All(p=>p.Key is "operation" or "action" or "graph" or "edits" ||frame&&p.Key=="path"),"Exact cell editor plan required");
        var graph=request["graph"]!.AsObject();var edits=request["edits"]!.AsArray();
        if (frameReconnect) return FrameReconnect(graph,S(request,"path"),edits);
        if (preview)
        {
            Need(edits.Count == 0, "Observe a preview frame without edits");
            OwnedPreviewFrame(graph, S(request, "path"), previewOutParameters: true);
            return new JsonObject();
        }
        if (frameCompound)
        {
            string path = S(request, "path");
            if (action == "frame-compound-insert-options")
            {
                Need(edits.Count == 0, "Observe the selected compound frame without edits");
                var selected = OwnedCompoundFrame(graph, path);
                return new JsonObject { ["nodes"] = new JsonArray(selected["nodes"]!.AsArray()
                    .Where(node => S(node, "kind") == "graph").Select(node => node!["id"]!.DeepClone()).ToArray()) };
            }
            var candidate = graph.DeepClone().AsObject();
            var frameGraph = OwnedCompoundFrame(candidate, path);
            InsertCell(frameGraph, edits, InsertionAnchor.CompoundCall);
            OwnedCompoundFrame(candidate, path);
            return new JsonObject { ["entry"] = frameGraph["entry"]!.DeepClone(), ["edges"] = frameGraph["edges"]!.DeepClone() };
        }
        if (frameCase)
        {
            string path = S(request, "path");
            if (action == "frame-case-create")
            {
                var candidate = graph.DeepClone().AsObject();
                var plan = CreateBranchCell(OwnedSwitchFrame(candidate, path), edits, frame: true);
                OwnedSwitchFrame(candidate, path);
                return plan;
            }
            var child = OwnedSwitchFrame(graph, path);
            if (edits.Count == 0) return new JsonObject();
            Need(edits.Count <= 64, "Bounded branch order required");
            ExactBranchRoutes(edits);
            return OrderBranch(child, edits, frame: true);
        }
        if(action=="transfer-options"){
            Need(edits.Count==0,"Read transfer options without edits");
            return TransferOptions(ReadTransferScope(graph));
        }
        if(action=="scope-transfer-options"){
            Need(edits.Count==0,"Read scope transfer options without edits");
            return ScopeTransferOptions(ReadScopeTransfer(graph));
        }
        if(action=="scope-transfer")return TransferScopeBoundary(graph,edits);
        if(action=="root-start-options"){
            Need(edits.Count==0,"Read the original root start without edits");
            return new JsonObject{["entry"]=RootStart(graph,out _)};
        }
        if(action=="compound-insert-options"){
            Need(edits.Count==0,"Read the original compound calls without edits");
            CompoundOrder(graph,CurrentRoutes(graph));
            return new JsonObject{["nodes"]=new JsonArray(graph["nodes"]!.AsArray().Where(n=>S(n,"kind")=="graph").Select(n=>n!["id"]!.DeepClone()).ToArray())};
        }
        if(action=="branch-reconnect")return BranchReconnect(graph,edits);
        Need(edits.Count is >0 and <=64,"Bounded branch edits required");
        if(action=="root-start-create"){
            RootStart(graph,out bool compound);
            var candidate=graph.DeepClone().AsObject();
            InsertCell(candidate,edits,InsertionAnchor.RootStart);
            if(compound)CompoundOrder(candidate,CurrentRoutes(candidate));
            else RootStart(candidate,out _);
            return new JsonObject{["entry"]=candidate["entry"]!.DeepClone(),["edges"]=candidate["edges"]!.DeepClone(),
                ["rootTopology"]=compound?"compound-insert-options":"root-start-options"};
        }
        if(action=="compound-insert"){
            CompoundOrder(graph,CurrentRoutes(graph));
            var candidate=graph.DeepClone().AsObject();
            InsertCell(candidate,edits,InsertionAnchor.CompoundCall);
            CompoundOrder(candidate,CurrentRoutes(candidate));
            return new JsonObject{["entry"]=candidate["entry"]!.DeepClone(),["edges"]=candidate["edges"]!.DeepClone()};
        }
        if(frame)return action=="frame-create"?FrameCreate(graph,S(request,"path"),edits,allowDesktopFrames):FrameOrder(graph,S(request,"path"),edits,allowDesktopFrames);
        if(action=="compound-order")return CompoundOrder(graph,edits,allowSwitchChild:true);
        if(action is "order" or "transfer"){
            ExactBranchRoutes(edits);
            if(action=="transfer")return TransferOrder(graph,edits,ReadTransferScope(graph));
            return OrderBranch(graph, edits);
        }
        Need(action=="create","One ordinary branch insertion required");
        return CreateBranchCell(graph, edits);
    }
}
