using Confectory.Core;
using System.Text.Json.Nodes;

// One direct owned synchronous contract, all ordinary owned providers/targets,
// and the explicit direct caller closure. This never chooses a runtime provider.
// Pure candidate preparation. The workspace owns checkpoint/physical CAS.
static class BlueprintRootExecution
{
    static string Hash(string text)=>JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(text));
    static Element Declaration(JsonObject units,string id,string kind) {
        var unit=units[id]??throw new ArgumentException("Owned execution source required");
        var value=new Parser(unit["draft"]!.GetValue<string>(),"<root-execution>").ParseElement();
        if(unit["kind"]?.ToString()!=kind||value.Id!=id||value.Kind!=kind)throw new ArgumentException("Exact owned declaration required");return value;
    }
    static JsonObject Graph(JsonObject units,string id) {
        if(units[id]?["kind"]?.ToString()!="blueprint")throw new ArgumentException("Owned Blueprint root required");
        var graph=JsonNode.Parse(units[id]!["draft"]!.GetValue<string>())!.AsObject();BlueprintDocuments.Validate(id,"blueprint",graph.ToJsonString());
        if(graph["profile"]?.ToString()!=FeatureBlueprint.SwitchProfile||graph["copySource"] is not null||BlueprintTree.Nodes(graph).Any(n=>n.Node["kind"]?.ToString() is not ("call" or "code" or "export" or "graph")||n.Node["control"]?.ToString()=="branch"||n.Node["postCall"] is not null))throw new ArgumentException("Existing switch-profile roots required; preserve other contexts");return graph;
    }
    static (Element Function,Element Implementation,JsonObject Graph) Root(JsonObject units,string graphId) {
        int marker=graphId.IndexOf("/body:",StringComparison.Ordinal);if(marker<0||graphId.Contains("/graph:",StringComparison.Ordinal))throw new ArgumentException("Direct root source required");
        string implementationId=graphId[..marker],target=graphId[(marker+6)..];var implementation=Declaration(units,implementationId,"implementation");var function=Declaration(units,implementation.Function!,"function");var graph=Graph(units,graphId);
        if(implementation.Parent is not null||function.Parent is not null||implementation.Bodies.Count==0||!implementation.Bodies.TryGetValue(target,out var body)||body.SourceKind!="blueprint"||body.Path!=units[graphId]!["path"]?.ToString()||!implementation.Signature!.Matches(function.Signature)||graph["feature"]?.ToString()!=function.Id)throw new ArgumentException("Directly owned Blueprint targets and original public contract required");return(function,implementation,graph);
    }
    static JsonObject Definitions(JsonObject units,string graphId,bool assemble=false) {
        var root=Root(units,graphId);var records=new JsonObject();var contracts=new JsonObject();
        foreach(var import in root.Implementation.Imports.Values)contracts[import.Id]=units[import.Id]?["draft"]?.DeepClone()??throw new ArgumentException("Owned exact imported contract required");
        string virtualRoot=Path.Combine(Path.GetTempPath(),"confectory-root-execution");
        foreach(var entry in BlueprintTree.Nodes(root.Graph).Where(n=>n.Node["kind"]?.ToString()=="code")) {
            var node=entry.Node;string id=BlueprintTree.SourceId(graphId,entry.Key);var unit=units[id];
            if(unit?["kind"]?.ToString()!="blueprint-node"||PackPaths.Owned(virtualRoot,unit["path"]!.ToString())!=PackPaths.Owned(Path.GetDirectoryName(PackPaths.Owned(virtualRoot,units[graphId]!["path"]!.ToString()))!,node["implementation"]!.ToString()))throw new ArgumentException("Exact owned original code record required");
            records[entry.Key]=JsonNode.Parse(unit["draft"]!.GetValue<string>());
        }
        var reply=FeatureBlueprint.Execute(new JsonObject { ["operation"]=assemble?"featureBlueprintDescribe":"featureBlueprintNodes",["featureSource"]=units[root.Function.Id]!["draft"]!.DeepClone(),["implementationContext"]=FeatureBlueprint.ImplementationContext(root.Implementation),["bodyTarget"]=graphId[(graphId.IndexOf("/body:",StringComparison.Ordinal)+6)..],["featureContracts"]=contracts,["graph"]=root.Graph,["implementations"]=records });
        if(reply["state"]?.ToString()!=(assemble?"source-ready":"node-definitions"))throw new InvalidOperationException("Root/caller source is not ready: "+reply.ToJsonString());return reply;
    }
    static string[] Targets(JsonObject units,string rootId) {
        var root=Root(units,rootId);
        var implementations=units.Where(p=>p.Value?["kind"]?.ToString()=="implementation").Select(p=>Declaration(units,p.Key,"implementation")).ToArray();
        var providers=implementations.Where(i=>i.Function==root.Function.Id).OrderBy(i=>i.Id,StringComparer.Ordinal).ToArray();
        var providerIds=providers.Select(i=>i.Id).ToHashSet(StringComparer.Ordinal);
        if(providers.Any(i=>i.Parent is not null)||implementations.Any(i=>i.Parent is not null&&providerIds.Contains(i.Parent)))throw new ArgumentException("Override contracts require their existing ownership boundary; preserve the sources");
        if(providers.Any(i=>i.Bodies.Count==0||i.Bodies.Values.Any(b=>b.SourceKind!="blueprint")))throw new ArgumentException("Every provider needs explicit ordinary Blueprint return mappings; preserve opaque sources");
        var ids=new[]{rootId}.Concat(providers.SelectMany(i=>i.Bodies.Keys.Order(StringComparer.Ordinal).Select(t=>i.Id+"/body:"+t))).Distinct(StringComparer.Ordinal).ToArray();
        foreach(string id in ids)_=Root(units,id);
        string virtualRoot=Path.Combine(Path.GetTempPath(),"confectory-root-execution-targets");
        if(ids.Select(id=>PackPaths.Owned(virtualRoot,units[id]!["path"]!.ToString())).Distinct(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal).Count()!=ids.Length)throw new ArgumentException("Aliased target files require one unambiguous owned draft; preserve the sources");return ids;
    }
    static string CallKey(JsonNode row)=>row["graph"]!.ToString()+"|node:"+row["node"]!.ToString();
    static (JsonObject Frame,string LocalId) CallerFrame(JsonObject graph,string key) {int slash=key.LastIndexOf('/');return(BlueprintTree.Select(graph,slash<0?"":key[..slash]),slash<0?key:key[(slash+1)..]);}
    static string[] ObservedContracts(JsonObject units,string rootId,IEnumerable<string> callerIds) {
        var roots=Targets(units,rootId).Concat(callerIds).Distinct(StringComparer.Ordinal).Select(id=>Root(units,id)).ToArray();
        var owners=roots.Select(r=>r.Function.Id).ToHashSet(StringComparer.Ordinal);
        var imports=roots.SelectMany(r=>r.Implementation.Imports.Values).ToArray();
        var observed=imports.Select(i=>i.Id).Concat(imports.Where(i=>i.Scope is not null).Select(i=>i.Scope!)).Where(id=>!owners.Contains(id)).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal).ToArray();
        foreach(string id in observed){if(PackPaths.Namespace(id)!=PackPaths.Namespace(rootId))throw new ArgumentException("Registered imported contracts need their readonly receipt boundary; preserve the sources");string kind=units[id]?["kind"]?.ToString()??"";if(kind is not ("function" or "object"))throw new ArgumentException("Observe an existing owned function or object scope without changing it");_=Declaration(units,id,kind);if(imports.Any(i=>i.Id==id)&&kind!="function")throw new ArgumentException("Exact imported function contract required");}
        return observed;
    }
    static JsonArray Members(JsonObject units,string rootId,IEnumerable<string> callerIds) {
        callerIds=callerIds.ToArray();
        var ids=new List<string>();foreach(string graphId in Targets(units,rootId).Concat(callerIds.Order(StringComparer.Ordinal)).Distinct(StringComparer.Ordinal)) {var root=Root(units,graphId);foreach(string id in new[]{root.Function.Id,root.Implementation.Id,graphId})if(!ids.Contains(id,StringComparer.Ordinal))ids.Add(id);foreach(var node in BlueprintTree.Nodes(root.Graph).Where(n=>n.Node["kind"]?.ToString()=="code")){string id=BlueprintTree.SourceId(graphId,node.Key);if(!ids.Contains(id,StringComparer.Ordinal))ids.Add(id);}}
        foreach(string id in ObservedContracts(units,rootId,callerIds))if(!ids.Contains(id,StringComparer.Ordinal))ids.Add(id);
        return new JsonArray(ids.Select(id=>JsonValue.Create(id)).ToArray());
    }
    public static JsonObject Candidates(JsonObject request) {
        var units=request["units"]!.AsObject();string rootId=request["id"]!.GetValue<string>();var root=Root(units,rootId);var targetIds=Targets(units,rootId);var targetSet=targetIds.ToHashSet(StringComparer.Ordinal);
        if(!BlueprintExecutionBranches.SupportsSignature(root.Function.Signature!))throw new ArgumentException("Direct synchronous root with existing value/ref/out parameters required");
        _=ObservedContracts(units,rootId,Array.Empty<string>());
        var rows=new JsonArray();var callerOwners=new HashSet<string>(StringComparer.Ordinal);
        foreach(var pair in units.Where(p=>p.Value?["kind"]?.ToString()=="blueprint"&&!targetSet.Contains(p.Key)).OrderBy(p=>p.Key,StringComparer.Ordinal)) {
            var graph=JsonNode.Parse(pair.Value!["draft"]!.GetValue<string>())!;
            var uses=BlueprintTree.Nodes(graph.AsObject()).Where(p=>p.Node["kind"]?.ToString()=="call"&&p.Node["feature"]?.ToString()==root.Function.Id).ToArray();if(uses.Length==0)continue;
            var caller=Root(units,pair.Key);
            if(caller.Function.Id==root.Function.Id||uses.Any(p=>p.Node["branchOwner"] is not null||p.Node["control"]?.ToString() is not ("next" or "switch")))throw new ArgumentException("Caller uses with explicit owned contracts required; preserve other contexts");
            if(uses.Any(p=>{var frame=CallerFrame(caller.Graph,p.Key).Frame;return frame["profile"]?.ToString()!=FeatureBlueprint.SwitchProfile||frame["executionExitMode"]?.GetValue<bool>()==true&&(!ReferenceEquals(frame,caller.Graph)||!BlueprintExecutionBranches.Has(caller.Function));}))throw new ArgumentException("Ordinary switch-profile caller frames required; preserve private forwarded contracts");
            _=ObservedContracts(units,rootId,new[]{pair.Key});
            _=Definitions(units,pair.Key,true);callerOwners.Add(caller.Implementation.Id);
            foreach(var use in uses.OrderBy(p=>p.Key,StringComparer.Ordinal)){var frame=CallerFrame(caller.Graph,use.Key).Frame;rows.Add(new JsonObject { ["graph"]=pair.Key,["node"]=use.Key,["name"]=caller.Function.Description.Length>0?caller.Function.Description:caller.Function.Id,["nodes"]=frame["nodes"]!.DeepClone(),["edges"]=frame["edges"]!.DeepClone() });}
        }

        if(units.Where(p=>p.Value?["kind"]?.ToString()=="implementation").Select(p=>Declaration(units,p.Key,"implementation")).Any(i=>!callerOwners.Contains(i.Id)&&i.Bodies.Values.Any(b=>b.SourceKind=="blueprint")&&i.Imports.Values.Any(import=>import.Id==root.Function.Id)))throw new ArgumentException("Other native/private/import callers require explicit coordination; preserve their sources");
        bool multipleProviders=targetIds.Select(id=>Root(units,id).Implementation.Id).Distinct(StringComparer.Ordinal).Count()>1;
        var targets=new JsonArray();foreach(string id in targetIds){_=Definitions(units,id,true);var selected=Root(units,id);string name=id[(id.IndexOf("/body:",StringComparison.Ordinal)+6)..];targets.Add(new JsonObject { ["graph"]=id,["name"]=multipleProviders?selected.Implementation.Id+" · "+name:name,["entry"]=selected.Graph["entry"]!.DeepClone(),["edges"]=selected.Graph["edges"]!.DeepClone(),["exits"]=selected.Graph["exits"]!.DeepClone() });}
        foreach(var row in rows)row!["key"]=CallKey(row);
        return new JsonObject { ["branches"]=BlueprintExecutionBranches.Read(root.Function),["targets"]=targets,["callers"]=rows,["observedContracts"]=new JsonArray(ObservedContracts(units,rootId,rows.Select(c=>c!["graph"]!.ToString())).Select(id=>JsonValue.Create(id)).ToArray()) };
    }
    public static JsonObject Prepare(JsonObject request,Func<Element,string> format) {
        var units=request["units"]!.DeepClone().AsObject();string rootId=request["id"]!.GetValue<string>();var choices=Candidates(new JsonObject { ["id"]=rootId,["units"]=units.DeepClone() });var plan=request["plan"]!.AsObject();var selectedCalls=new JsonArray();var selectedTargets=new JsonArray();
        bool legacy=plan.ContainsKey("caller");
        if(legacy){if(plan.Count!=5||plan.Any(p=>p.Key is not ("branches" or "entry" or "edges" or "exits" or "caller"))||choices["callers"]!.AsArray().Count!=1||choices["targets"]!.AsArray().Count!=1)throw new ArgumentException("Explicit complete caller/target mapping required");selectedCalls.Add(plan["caller"]!.DeepClone());}
        else {if(plan.Count!=6||plan.Any(p=>p.Key is not ("branches" or "entry" or "edges" or "exits" or "callers" or "targets")))throw new ArgumentException("Explicit branches, all target returns and all callers required");selectedCalls=plan["callers"]!.DeepClone().AsArray();selectedTargets=plan["targets"]!.DeepClone().AsArray();}
        if(selectedCalls.Any(c=>c is not JsonObject row||row.Count is <2 or >3||row.Any(p=>p.Key is not ("graph" or "node" or "routes"))||row["graph"] is null||row["node"] is null)||selectedCalls.Select(c=>CallKey(c!)).Distinct(StringComparer.Ordinal).Count()!=selectedCalls.Count||!selectedCalls.Select(c=>CallKey(c!)).ToHashSet(StringComparer.Ordinal).SetEquals(choices["callers"]!.AsArray().Select(c=>CallKey(c!))))throw new ArgumentException("Every affected caller must have one explicit mapping; no automatic selection");
        var extraTargets=choices["targets"]!.AsArray().Where(t=>t!["graph"]!.ToString()!=rootId).Select(t=>t!["graph"]!.ToString()).ToHashSet(StringComparer.Ordinal);
        if(selectedTargets.Any(t=>t is not JsonObject row||row.Count!=4||row.Any(p=>p.Key is not ("graph" or "entry" or "edges" or "exits"))||row["graph"] is null)||selectedTargets.Select(t=>t!["graph"]!.ToString()).Distinct(StringComparer.Ordinal).Count()!=selectedTargets.Count||!selectedTargets.Select(t=>t!["graph"]!.ToString()).ToHashSet(StringComparer.Ordinal).SetEquals(extraTargets))throw new ArgumentException("Every other implementation target requires explicit return mapping");
        var root=Root(units,rootId);var before=BlueprintExecutionBranches.Read(root.Function);var branches=plan["branches"]!.AsArray();
        foreach(var branch in branches) {var prior=before.SingleOrDefault(b=>b!["id"]?.ToString()==branch!["id"]?.ToString());if(prior is not null&&prior["value"]?.ToString()!=branch!["value"]?.ToString()||prior is null&&before.Any(b=>b!["value"]?.ToString()==branch!["value"]?.ToString()))throw new ArgumentException("Retain existing branch IDs and allocated values");}
        BlueprintExecutionBranches.Set(root.Function,branches);units[root.Function.Id]!["draft"]=format(root.Function);
        foreach(string id in Targets(units,rootId)) {var target=Root(units,id);JsonNode mapping=id==rootId?plan:selectedTargets.Single(t=>t!["graph"]!.ToString()==id)!;if(root.Function.Signature!.Return!="void") {
            var previous=target.Graph["exits"]!.AsObject();var next=mapping["exits"]!.AsObject();
            foreach(var pair in previous){var data=target.Graph["executionExitMode"]?.GetValue<bool>()==true?pair.Value?["value"]:pair.Value;if(!next.ContainsKey(pair.Key)&&data is not null||next.ContainsKey(pair.Key)&&(!next[pair.Key]!.AsObject().ContainsKey("value")||!JsonNode.DeepEquals(data,next[pair.Key]!["value"])))throw new ArgumentException("Preserve each original native return binding with its explicit branch selection");}
        }
        target.Graph["schema"]=2;target.Graph["executionExitMode"]=true;target.Graph["contractHash"]=FeatureBlueprint.ContractHash(root.Function);foreach(string key in new[]{"entry","edges","exits"})target.Graph[key]=mapping[key]!.DeepClone();units[id]!["draft"]=target.Graph.ToJsonString();}
        var allowed=branches.Select(b=>"case:"+b!["id"]).Append("case:none").ToHashSet(StringComparer.Ordinal);
        foreach(var selected in selectedCalls){string callerId=selected!["graph"]!.ToString();var caller=Root(units,callerId);var (frame,callId)=CallerFrame(caller.Graph,selected["node"]!.ToString());var call=frame["nodes"]!.AsArray().Single(n=>n!["id"]?.ToString()==callId)!;call["control"]="switch";call["publicExecution"]=FeatureBlueprint.ContractHash(root.Function);call["executionEnum"]=BlueprintExecutionBranches.Enum(root.Function);
            foreach(var route in selected["routes"]?.AsArray()??new JsonArray()) {
                if(route is not JsonObject row||row.Count!=2||row["branch"] is null||!row.ContainsKey("to")||!allowed.Contains("case:"+row["branch"])&&!(row["to"] is null&&before.Any(b=>b!["id"]?.ToString()==row["branch"]!.ToString())))throw new ArgumentException("Exact declared branch route/disconnection required");
                string? to=row["to"]?.ToString();var target=to is null?null:frame["nodes"]!.AsArray().SingleOrDefault(n=>n!["id"]?.ToString()==to);
                if(target is not null&&target["branchOwner"]?.ToString()!=callId)throw new ArgumentException("Route to an existing node of this caller branch; moving authored code between regions is separate");
                if(to is not null&&target is null&&to!="return:"+callId&&!to.StartsWith("exit:",StringComparison.Ordinal))throw new ArgumentException("Existing branch return target required");
                var edges=frame["edges"]!.AsArray();for(int i=edges.Count-1;i>=0;i--)if(edges[i]!["from"]?.ToString()==callId&&edges[i]!["port"]?.ToString()=="case:"+row["branch"])edges.RemoveAt(i);if(to is not null)edges.Add(new JsonObject { ["from"]=callId,["port"]="case:"+row["branch"],["to"]=to });
            }
            if(frame["edges"]!.AsArray().Any(e=>e!["from"]?.ToString()==callId&&e["port"]!.ToString().StartsWith("case:",StringComparison.Ordinal)&&!allowed.Contains(e["port"]!.ToString())))throw new ArgumentException("Disconnect removed caller branches explicitly before deleting their definitions");
            units[callerId]!["draft"]=caller.Graph.ToJsonString();
        }
        foreach(string id in Targets(units,rootId).Concat(selectedCalls.Select(c=>c!["graph"]!.ToString())).Distinct(StringComparer.Ordinal))_=Definitions(units,id,true);
        var group=Members(units,rootId,selectedCalls.Select(c=>c!["graph"]!.ToString()));var result=new JsonObject();foreach(var member in group){string id=member!.ToString();result[id]=units[id]!.DeepClone();result[id]!["rootContractGroup"]=group.DeepClone();}
        ValidateGroup(new JsonObject { ["namespace"]=request["namespace"]!.DeepClone(),["group"]=group.DeepClone(),["units"]=result.DeepClone() });return new JsonObject { ["group"]=group,["units"]=result,["observedContracts"]=choices["observedContracts"]!.DeepClone(),["sourceWritten"]=false,["executed"]=false };
    }
    public static JsonObject ValidateGroup(JsonObject request) {
        var units=request["units"]!.AsObject();var group=request["group"]!.AsArray();string ns=request["namespace"]!.ToString();var ids=group.Select(m=>m!.ToString()).ToArray();
        if(ids.Length is <3 or >64||ids.Distinct(StringComparer.Ordinal).Count()!=ids.Length||ids.Any(id=>PackPaths.Namespace(id)!=ns||units[id] is null||!JsonNode.DeepEquals(units[id]!["rootContractGroup"],group)))throw new ArgumentException("Complete owned execution branch review group required");
        string rootId=ids[2];var root=Root(units,rootId);if(root.Function.Id!=ids[0]||root.Implementation.Id!=ids[1]||!BlueprintExecutionBranches.Has(root.Function))throw new ArgumentException("Ordered root execution contract group required");
        var candidates=Candidates(new JsonObject { ["id"]=rootId,["units"]=units.DeepClone() });var callers=candidates["callers"]!.AsArray();
        if(!Members(units,rootId,callers.Select(c=>c!["graph"]!.ToString())).Select(n=>n!.ToString()).ToHashSet(StringComparer.Ordinal).SetEquals(ids))throw new ArgumentException("No missing/unrelated execution group member permitted");
        foreach(var selected in callers){var caller=Root(units,selected!["graph"]!.ToString());var node=BlueprintTree.Nodes(caller.Graph).Single(n=>n.Key==selected["node"]!.ToString()).Node;if(node["publicExecution"]?.ToString()!=FeatureBlueprint.ContractHash(root.Function))throw new ArgumentException("Exact public execution caller receipt required");}
        var observed=units[rootId]?["authorSaveReceipt"]?["sources"] as JsonObject;
        if(candidates["observedContracts"]!.AsArray().Count>0&&units[rootId]?["original"] is not null&&observed is null)throw new ArgumentException("Retain the observed imported-contract source receipt");
        foreach(var dependency in candidates["observedContracts"]!.AsArray()){string id=dependency!.ToString();var unit=units[id]!;if(unit["original"] is not null&&unit["draft"]?.ToString()!=unit["original"]?.ToString()||observed is not null&&observed[id]?["hash"]?.ToString()!=Hash(unit["draft"]!.ToString()))throw new ArgumentException("Imported contracts are readonly observations of this execution transaction");}
        return new JsonObject { ["valid"]=true,["ids"]=group.DeepClone(),["sourceWritten"]=false,["executed"]=false };
    }
    public static JsonObject Guards(JsonObject request) {
        var units=request["units"]!.AsObject();var checks=new JsonArray();var paths=new HashSet<string>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);
        var selected=request["selected"]?.AsArray().Select(n=>n!.ToString()).ToHashSet(StringComparer.Ordinal);
        foreach(var pair in units.Where(p=>p.Value?["kind"]?.ToString()=="function"&&p.Value?["rootContractGroup"] is JsonArray)) {
            var group=pair.Value!["rootContractGroup"]!.AsArray();if(group[0]?.ToString()!=pair.Key||selected is not null&&!selected.Contains(pair.Key)||!BlueprintExecutionBranches.Has(Declaration(units,pair.Key,"function")))continue;
            ValidateGroup(new JsonObject { ["namespace"]=request["namespace"]!.DeepClone(),["group"]=group.DeepClone(),["units"]=units.DeepClone() });
            var observed=units[group[2]!.ToString()]?["authorSaveReceipt"]?["sources"] as JsonObject;
            if(observed is not null && observed.Count>64)throw new ArgumentException("Bounded observed execution closure required");
            var guarded=group.Select(m=>m!.ToString()).Concat(observed?.Select(p=>p.Key)??Enumerable.Empty<string>()).Distinct(StringComparer.Ordinal);
            foreach(string member in guarded) {
                var unit=units[member]??throw new ArgumentException("Observed execution dependency disappeared");string path=unit["path"]!.ToString(),hash=unit["baseline"]!.ToString();
                if(observed?[member] is JsonObject proof && (proof["path"]?.ToString()!=path || proof["kind"]?.ToString()!=unit["kind"]?.ToString()))throw new ArgumentException("Observed execution dependency locator changed");
                _=PackPaths.Owned(Path.Combine(Path.GetTempPath(),"confectory-root-execution-guards"),path);
                if(!System.Text.RegularExpressions.Regex.IsMatch(hash,@"\A[a-f0-9]{64}\z"))throw new ArgumentException("Existing public root dependency baseline required");
                if(paths.Add(path))checks.Add(new JsonObject { ["path"]=path,["hash"]=hash });
            }
        }
        return new JsonObject { ["checks"]=checks,["sourceWritten"]=false,["executed"]=false };
    }
}
