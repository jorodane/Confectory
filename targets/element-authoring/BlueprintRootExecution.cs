using Confectory.Core;
using System.Text.Json.Nodes;

// One direct owned sync-void root and one explicitly selected direct caller.
// Pure candidate preparation. The workspace owns checkpoint/physical CAS.
static class BlueprintRootExecution
{
    static Element Declaration(JsonObject units,string id,string kind) {
        var unit=units[id]??throw new ArgumentException("Owned execution source required");
        var value=new Parser(unit["draft"]!.GetValue<string>(),"<root-execution>").ParseElement();
        if(unit["kind"]?.ToString()!=kind||value.Id!=id||value.Kind!=kind)throw new ArgumentException("Exact owned declaration required");return value;
    }
    static JsonObject Graph(JsonObject units,string id) {
        if(units[id]?["kind"]?.ToString()!="blueprint")throw new ArgumentException("Owned Blueprint root required");
        var graph=JsonNode.Parse(units[id]!["draft"]!.GetValue<string>())!.AsObject();BlueprintDocuments.Validate(id,"blueprint",graph.ToJsonString());
        if(graph["profile"]?.ToString()!=FeatureBlueprint.SwitchProfile||graph["copySource"] is not null||graph["nodes"]!.AsArray().Any(n=>n!["kind"]?.ToString() is not ("call" or "code")||n["control"]?.ToString()=="branch"||n["implementationContext"] is not null||n["postCall"] is not null))throw new ArgumentException("Existing ordinary switch-profile roots required; preserve other contexts");return graph;
    }
    static (Element Function,Element Implementation,JsonObject Graph) Root(JsonObject units,string graphId) {
        int marker=graphId.IndexOf("/body:",StringComparison.Ordinal);if(marker<0||graphId.Contains("/graph:",StringComparison.Ordinal))throw new ArgumentException("Direct root source required");
        string implementationId=graphId[..marker],target=graphId[(marker+6)..];var implementation=Declaration(units,implementationId,"implementation");var function=Declaration(units,implementation.Function!,"function");var graph=Graph(units,graphId);
        if(implementation.Parent is not null||function.Parent is not null||implementation.Bodies.Count!=1||!implementation.Bodies.TryGetValue(target,out var body)||body.SourceKind!="blueprint"||body.Path!=units[graphId]!["path"]?.ToString()||!implementation.Signature!.Matches(function.Signature)||graph["feature"]?.ToString()!=function.Id)throw new ArgumentException("One directly owned Blueprint target and original public contract required");return(function,implementation,graph);
    }
    static JsonObject Definitions(JsonObject units,string graphId,bool assemble=false) {
        var root=Root(units,graphId);var records=new JsonObject();var contracts=new JsonObject();
        foreach(var import in root.Implementation.Imports.Values)contracts[import.Id]=units[import.Id]?["draft"]?.DeepClone()??throw new ArgumentException("Owned exact imported contract required");
        string virtualRoot=Path.Combine(Path.GetTempPath(),"confectory-root-execution");
        foreach(var node in root.Graph["nodes"]!.AsArray().Where(n=>n!["kind"]?.ToString()=="code")) {
            string id=graphId+"/node:"+node!["id"];var unit=units[id];
            if(unit?["kind"]?.ToString()!="blueprint-node"||PackPaths.Owned(virtualRoot,unit["path"]!.ToString())!=PackPaths.Owned(Path.GetDirectoryName(PackPaths.Owned(virtualRoot,units[graphId]!["path"]!.ToString()))!,node["implementation"]!.ToString()))throw new ArgumentException("Exact owned original code record required");
            records[node["id"]!.ToString()]=JsonNode.Parse(unit["draft"]!.GetValue<string>());
        }
        var reply=FeatureBlueprint.Execute(new JsonObject { ["operation"]=assemble?"featureBlueprintDescribe":"featureBlueprintNodes",["featureSource"]=units[root.Function.Id]!["draft"]!.DeepClone(),["implementationContext"]=FeatureBlueprint.ImplementationContext(root.Implementation),["featureContracts"]=contracts,["graph"]=root.Graph,["implementations"]=records });
        if(reply["state"]?.ToString()!=(assemble?"source-ready":"node-definitions"))throw new InvalidOperationException("Root/caller source is not ready: "+reply.ToJsonString());return reply;
    }
    static JsonArray Members(JsonObject units,string rootId,string callerId) {
        var ids=new List<string>();foreach(string graphId in new[]{rootId,callerId}) {var root=Root(units,graphId);foreach(string id in new[]{root.Function.Id,root.Implementation.Id,graphId})if(!ids.Contains(id,StringComparer.Ordinal))ids.Add(id);foreach(var node in root.Graph["nodes"]!.AsArray().Where(n=>n!["kind"]?.ToString()=="code"))ids.Add(graphId+"/node:"+node!["id"]);}
        return new JsonArray(ids.Select(id=>JsonValue.Create(id)).ToArray());
    }
    public static JsonObject Candidates(JsonObject request) {
        var units=request["units"]!.AsObject();string rootId=request["id"]!.GetValue<string>();var root=Root(units,rootId);
        if(root.Function.Signature!.Return!="void"||root.Function.Signature.Args.Any(p=>p.Mode is not null)||root.Implementation.Imports.Count!=0)throw new ArgumentException("Direct synchronous void/value-input root without imported body context required");
        if(units.Where(p=>p.Value?["kind"]?.ToString()=="implementation").Select(p=>Declaration(units,p.Key,"implementation")).Count(i=>i.Function==root.Function.Id||i.Parent==root.Implementation.Id)!=1)throw new ArgumentException("A shared provider/override requires a separately coordinated contract; keep it unchanged");
        var rows=new JsonArray();
        foreach(var pair in units.Where(p=>p.Value?["kind"]?.ToString()=="blueprint"&&p.Key!=rootId)) {
            var graph=JsonNode.Parse(pair.Value!["draft"]!.GetValue<string>())!;
            var uses=BlueprintTree.Nodes(graph.AsObject()).Where(p=>p.Node["kind"]?.ToString()=="call"&&p.Node["feature"]?.ToString()==root.Function.Id).ToArray();if(uses.Length==0)continue;
            var caller=Root(units,pair.Key);
            if(BlueprintExecutionBranches.Has(caller.Function)||uses.Length!=1||caller.Function.Id==root.Function.Id||caller.Implementation.Imports.Values.Any(i=>i.Id!=root.Function.Id)||uses[0].Key!=uses[0].Node["id"]?.ToString()||uses[0].Node["branchOwner"] is not null||uses[0].Node["control"]?.ToString() is not ("next" or "switch"))throw new ArgumentException("Exactly one direct caller use required; other uses are retained");
            _=Definitions(units,pair.Key,true);
            rows.Add(new JsonObject { ["graph"]=pair.Key,["node"]=uses[0].Node["id"]!.DeepClone(),["name"]=caller.Function.Description.Length>0?caller.Function.Description:caller.Function.Id,["nodes"]=caller.Graph["nodes"]!.DeepClone(),["edges"]=caller.Graph["edges"]!.DeepClone() });
        }
        if(rows.Count!=1)throw new ArgumentException("One existing direct Blueprint caller must be explicitly selected");
        string selectedOwner=rows[0]!["graph"]!.ToString().Split("/body:",StringSplitOptions.None)[0];
        if(units.Where(p=>p.Value?["kind"]?.ToString()=="implementation").Select(p=>Declaration(units,p.Key,"implementation")).Any(i=>i.Id!=selectedOwner&&i.Imports.Values.Any(import=>import.Id==root.Function.Id)))throw new ArgumentException("Other native/private/import callers require explicit coordination; preserve their sources");
        _=Definitions(units,rootId,true);
        return new JsonObject { ["branches"]=BlueprintExecutionBranches.Read(root.Function),["callers"]=rows };
    }
    public static JsonObject Prepare(JsonObject request,Func<Element,string> format) {
        var units=request["units"]!.DeepClone().AsObject();string rootId=request["id"]!.GetValue<string>();var choices=Candidates(new JsonObject { ["id"]=rootId,["units"]=units.DeepClone() });var plan=request["plan"]!.AsObject();
        if(plan.Count!=5||plan.Any(p=>p.Key is not ("branches" or "entry" or "edges" or "exits" or "caller")))throw new ArgumentException("Explicit branches, root returns and caller required");
        var selected=plan["caller"]!.AsObject();if(selected.Any(p=>p.Key is not ("graph" or "node" or "routes"))||selected.Count is <2 or >3)throw new ArgumentException("Explicit caller and optional branch routes required");
        var choice=choices["callers"]!.AsArray().Single(c=>c!["graph"]?.ToString()==selected["graph"]?.ToString()&&c["node"]?.ToString()==selected["node"]?.ToString())!;
        string callerId=selected["graph"]!.ToString(),callId=selected["node"]!.ToString();var root=Root(units,rootId);var caller=Root(units,callerId);var before=BlueprintExecutionBranches.Read(root.Function);var branches=plan["branches"]!.AsArray();
        foreach(var branch in branches) {var prior=before.SingleOrDefault(b=>b!["id"]?.ToString()==branch!["id"]?.ToString());if(prior is not null&&prior["value"]?.ToString()!=branch!["value"]?.ToString()||prior is null&&before.Any(b=>b!["value"]?.ToString()==branch!["value"]?.ToString()))throw new ArgumentException("Retain existing branch IDs and allocated values");}
        BlueprintExecutionBranches.Set(root.Function,branches);units[root.Function.Id]!["draft"]=format(root.Function);root.Graph["schema"]=2;root.Graph["executionExitMode"]=true;root.Graph["contractHash"]=FeatureBlueprint.ContractHash(root.Function);root.Graph["entry"]=plan["entry"]!.DeepClone();root.Graph["edges"]=plan["edges"]!.DeepClone();root.Graph["exits"]=plan["exits"]!.DeepClone();units[rootId]!["draft"]=root.Graph.ToJsonString();
        var call=caller.Graph["nodes"]!.AsArray().Single(n=>n!["id"]?.ToString()==callId)!;call["control"]="switch";call["publicExecution"]=FeatureBlueprint.ContractHash(root.Function);call["executionEnum"]=BlueprintExecutionBranches.Enum(root.Function);
        var allowed=branches.Select(b=>"case:"+b!["id"]).Append("case:none").ToHashSet(StringComparer.Ordinal);
        if(caller.Graph["edges"]!.AsArray().Any(e=>e!["from"]?.ToString()==callId&&e["port"]!.ToString().StartsWith("case:",StringComparison.Ordinal)&&!allowed.Contains(e["port"]!.ToString())))throw new ArgumentException("Disconnect removed caller branches explicitly before deleting their definitions");
        foreach(var route in selected["routes"]?.AsArray()??new JsonArray()) {
            if(route is not JsonObject row||row.Count!=2||row["branch"] is null||row["to"] is null||!allowed.Contains("case:"+row["branch"]))throw new ArgumentException("Exact declared branch route required");
            string to=row["to"]!.ToString();var target=caller.Graph["nodes"]!.AsArray().SingleOrDefault(n=>n!["id"]?.ToString()==to);
            if(target is not null&&target["branchOwner"]?.ToString()!=callId)throw new ArgumentException("Route to an existing node of this caller branch; moving authored code between regions is separate");
            if(target is null&&to!="return:"+callId&&!to.StartsWith("exit:",StringComparison.Ordinal))throw new ArgumentException("Existing branch return target required");
            var edges=caller.Graph["edges"]!.AsArray();for(int i=edges.Count-1;i>=0;i--)if(edges[i]!["from"]?.ToString()==callId&&edges[i]!["port"]?.ToString()=="case:"+row["branch"])edges.RemoveAt(i);edges.Add(new JsonObject { ["from"]=callId,["port"]="case:"+row["branch"],["to"]=to });
        }
        units[callerId]!["draft"]=caller.Graph.ToJsonString();
        _=Definitions(units,rootId,true);_=Definitions(units,callerId,true);
        var group=Members(units,rootId,callerId);var result=new JsonObject();foreach(var member in group){string id=member!.ToString();result[id]=units[id]!.DeepClone();result[id]!["rootContractGroup"]=group.DeepClone();}
        ValidateGroup(new JsonObject { ["namespace"]=request["namespace"]!.DeepClone(),["group"]=group.DeepClone(),["units"]=result.DeepClone() });
        return new JsonObject { ["group"]=group,["units"]=result,["sourceWritten"]=false,["executed"]=false };
    }
    public static JsonObject ValidateGroup(JsonObject request) {
        var units=request["units"]!.AsObject();var group=request["group"]!.AsArray();string ns=request["namespace"]!.ToString();var ids=group.Select(m=>m!.ToString()).ToArray();
        if(ids.Length is <6 or >64||ids.Distinct(StringComparer.Ordinal).Count()!=ids.Length||ids.Any(id=>PackPaths.Namespace(id)!=ns||units[id] is null||!JsonNode.DeepEquals(units[id]!["rootContractGroup"],group)))throw new ArgumentException("Complete owned execution branch review group required");
        string rootId=ids[2];var root=Root(units,rootId);if(root.Function.Id!=ids[0]||root.Implementation.Id!=ids[1]||!BlueprintExecutionBranches.Has(root.Function))throw new ArgumentException("Ordered root execution contract group required");
        var graphIds=ids.Where(id=>units[id]?["kind"]?.ToString()=="blueprint").ToArray();if(graphIds.Length!=2)throw new ArgumentException("Root and one explicitly selected caller required");string callerId=graphIds.Single(id=>id!=rootId);
        if(!Members(units,rootId,callerId).Select(n=>n!.ToString()).ToHashSet(StringComparer.Ordinal).SetEquals(ids))throw new ArgumentException("No missing/unrelated execution group member permitted");
        var candidates=Candidates(new JsonObject { ["id"]=rootId,["units"]=units.DeepClone() });var caller=Root(units,callerId);var node=caller.Graph["nodes"]!.AsArray().Single(n=>n!["kind"]?.ToString()=="call"&&n["feature"]?.ToString()==root.Function.Id)!;
        if(node["publicExecution"]?.ToString()!=FeatureBlueprint.ContractHash(root.Function))throw new ArgumentException("Exact public execution caller receipt required");
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
