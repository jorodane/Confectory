using Confectory.Core;
using System.Text.Json.Nodes;

// Pure owned-source preparation. Physical writes and execution remain behind
// the workspace checkpoint, complete Review, compiler validation and final CAS.
internal static partial class BlueprintAsyncTransition
{
    const string Receipt = "asyncTransition";
    static string S(JsonNode n,string key)=>n[key]?.GetValue<string>()??throw new ArgumentException("Missing async transition "+key);
    static Element Element(JsonObject units,string id,string kind) {
        var unit=units[id]??throw new ArgumentException("Owned async declaration required");var e=new Parser(S(unit,"draft"),"<async-transition>").ParseElement();
        if(S(unit,"kind")!=kind||e.Kind!=kind||e.Id!=id)throw new ArgumentException("Exact owned async declaration required");return e;
    }
    static JsonObject Graph(JsonObject units,string id) {
        if(units[id]?["kind"]?.ToString()!="blueprint")throw new ArgumentException("Owned async Blueprint root required");var graph=JsonNode.Parse(S(units[id]!,"draft"))!.AsObject();BlueprintDocuments.Validate(id,"blueprint",graph.ToJsonString());return graph;
    }
    static (Element Function,Element Implementation,JsonObject Graph) Root(JsonObject units,string id) {
        int marker=id.IndexOf("/body:",StringComparison.Ordinal);if(marker<1||id.Contains("/graph:",StringComparison.Ordinal))throw new ArgumentException("Direct owned root transition required");
        var impl=Element(units,id[..marker],"implementation");var fn=Element(units,impl.Function!,"function");var graph=Graph(units,id);string target=id[(marker+6)..];
        if(impl.Parent is not null||fn.Parent is not null||!impl.Signature!.Matches(fn.Signature)||!impl.Bodies.TryGetValue(target,out var body)||body.SourceKind!="blueprint"||body.Origin!=impl.Id||body.Path!=units[id]!["path"]?.ToString()||graph["feature"]?.ToString()!=fn.Id||graph["copySource"] is not null||units[impl.Id]?["copySource"] is not null)
            throw new ArgumentException("Direct owned ordinary implementation required; retain parent/reference/native originals");
        if(!FeatureBlueprint.SupportsMethods(graph["profile"]?.ToString())||graph["nodes"]!.AsArray().Any(n=>n!["kind"]?.ToString() is not ("code" or "call" or "export" or "set")||n["implementationContext"] is not null||n["postCall"] is not null||n["forwardCallerStorage"]?.GetValue<bool>()==true))throw new ArgumentException("Ordinary method/switch flow required; retain legacy/context source semantics");
        return(fn,impl,graph);
    }
    static string[] Targets(JsonObject units,string id) {
        var root=Root(units,id);var providers=units.Where(p=>p.Value?["kind"]?.ToString()=="implementation").Select(p=>Element(units,p.Key,"implementation")).Where(e=>e.Function==root.Function.Id).ToArray();
        if(providers.Any(e=>e.Parent is not null||e.Bodies.Count==0||e.Bodies.Any(p=>p.Value.SourceKind!="blueprint")))throw new ArgumentException("Explicit ordinary owned targets required before async conversion");
        var targets=providers.SelectMany(e=>e.Bodies.Keys.Order(StringComparer.Ordinal).Select(t=>e.Id+"/body:"+t)).Distinct(StringComparer.Ordinal).ToArray();foreach(string target in targets)_=Root(units,target);return targets;
    }
    static Dictionary<string,string> Contracts(JsonObject units,bool previous=false) => units.Where(p=>p.Value?["kind"]?.ToString()=="function").ToDictionary(p=>p.Key,p=>previous&&p.Value?["original"] is JsonValue old?old.GetValue<string>():S(p.Value!,"draft"),StringComparer.Ordinal);
    static string WithoutAsync(Element fn) {var copy=JsonData.Clone(fn);copy.Values.Remove(BlueprintAsync.Metadata);return FeatureBlueprint.ContractHash(copy);}
    static bool AsyncOnly(string before,string after) {var a=new Parser(before,"<before-async>").ParseElement();var b=new Parser(after,"<after-async>").ParseElement();return a.Id==b.Id&&WithoutAsync(a)==WithoutAsync(b);}
    static void RefreshCalls(JsonObject units,JsonObject graph,string changedFunction) {
        foreach(var call in graph["nodes"]!.AsArray().Where(n=>n!["kind"]?.ToString()=="call"&&n["publicExecution"] is not null)) {
            string fn=S(call!,"feature");var current=Element(units,fn,"function");string hash=FeatureBlueprint.ContractHash(current);if(call!["publicExecution"]!.ToString()==hash)continue;
            if(fn==changedFunction&&BlueprintFunctionCompletion.Read(current) is not null)continue;
            string prior=units[fn]?["original"]?.GetValue<string>()??throw new ArgumentException("Original async callee observation required");var old=new Parser(prior,"<original-callee>").ParseElement();
            if(!AsyncOnly(prior,S(units[fn]!,"draft"))||call["publicExecution"]!.ToString()!=FeatureBlueprint.ContractHash(old)||!JsonNode.DeepEquals(call["executionEnum"],BlueprintExecutionBranches.Enum(current)))throw new ArgumentException("Only the explicitly observed async contract may be rebound; retain other contract changes");
            call["publicExecution"]=hash;
        }
    }
    static JsonObject Definitions(JsonObject units,string id,bool previous=false,bool describe=false) {
        var root=Root(units,id);var contracts=Contracts(units,previous);foreach(var import in root.Implementation.Imports.Values)if(!contracts.ContainsKey(import.Id))throw new ArgumentException("Registered/foreign async contexts retain their separate read-only receipt boundary");
        var records=new JsonObject();if(describe)foreach(var node in root.Graph["nodes"]!.AsArray().Where(n=>n!["kind"]?.ToString()=="code"))records[node!["id"]!.ToString()]=JsonNode.Parse(S(units[BlueprintTree.SourceId(id,node["id"]!.ToString())]!,"draft"));
        return FeatureBlueprint.Execute(new(){["operation"]=describe?"featureBlueprintDescribe":"featureBlueprintNodes",["implementations"]=records,["featureSource"]=S(units[root.Function.Id]!,"draft"),["implementationContext"]=FeatureBlueprint.ImplementationContext(root.Implementation),["bodyTarget"]=id[(id.IndexOf("/body:",StringComparison.Ordinal)+6)..],["graph"]=root.Graph,["featureContracts"]=new JsonObject(contracts.Select(p=>new KeyValuePair<string,JsonNode?>(p.Key,JsonValue.Create(p.Value)))),["inspectStaleAsyncCalls"]=!previous&&!describe});
    }
    static string[] Members(JsonObject units,IEnumerable<string> targets,string function) {
        var ids=new List<string>{function};foreach(string id in targets){var root=Root(units,id);ids.Add(root.Implementation.Id);ids.Add(id);ids.AddRange(BlueprintTree.Nodes(root.Graph).Where(n=>n.Node["kind"]?.ToString()=="code").Select(n=>BlueprintTree.SourceId(id,n.Key)));}return ids.Distinct(StringComparer.Ordinal).ToArray();
    }
    static string[] Observations(JsonObject units,string function) {
        // Headers select providers/scopes. Caller bodies remain observations;
        // this does not set their function/node async flags.
        var ids=units.Where(p=>p.Value?["kind"]?.ToString() is "function" or "implementation" or "project" or "module" or "object" or "schema").Select(p=>p.Key).ToHashSet(StringComparer.Ordinal);
        foreach(var item in units.Where(p=>p.Value?["kind"]?.ToString()=="implementation")) {
            var impl=Element(units,item.Key,"implementation");if(!impl.Imports.Values.Any(i=>i.Id==function))continue;
            foreach(string target in impl.Bodies.Keys){string id=impl.Id+"/body:"+target;if(units[id] is null)throw new ArgumentException("Every observed caller target required");ids.Add(id);if(units[id]?["kind"]?.ToString()=="blueprint")foreach(var n in BlueprintTree.Nodes(Graph(units,id)).Where(n=>n.Node["kind"]?.ToString()=="code"))ids.Add(BlueprintTree.SourceId(id,n.Key));}
        }
        return ids.ToArray();
    }
    static void Scope(JsonObject units,IEnumerable<string> ids,string ns) {
        var paths=new HashSet<string>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);string root=Path.Combine(Path.GetTempPath(),"confectory-async-scope");
        foreach(string id in ids){var unit=units[id]??throw new ArgumentException("Complete async member required");if(PackPaths.Namespace(id)!=ns||unit["baseline"]?.ToString()=="missing"||unit["draft"] is null||unit["original"] is null)throw new ArgumentException("Existing owned async sources required");string path=PackPaths.Owned(root,S(unit,"path"));if(!paths.Add(path))throw new ArgumentException("Async target paths must not alias");if(JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(S(unit,"original")))!=S(unit,"baseline"))throw new ArgumentException("Original async source baseline required");}
    }
    static JsonObject? FunctionDemotion(Element fn){try{return BlueprintFunctionCompletion.Preview(fn);}catch(ArgumentException){return null;}}
    static JsonObject? Demotion(JsonObject node,string identity) {try{return BlueprintCompletionBranch.Preview(node,identity);}catch(ArgumentException){return null;}}
    public static JsonObject Candidates(JsonObject request) {
        var units=request["units"]!.AsObject();string id=S(request,"id");var root=Root(units,id);var targets=Targets(units,id);Scope(units,Members(units,targets,root.Function.Id),PackPaths.Namespace(root.Function.Id));
        foreach(string target in targets){var defs=Definitions(units,target);if(defs["state"]?.ToString()!="node-definitions")throw new ArgumentException("Current async definitions required: "+defs.ToJsonString());}
        var asynchronous=BlueprintAsync.Read(root.Function);return new(){["enabled"]=asynchronous is not null,["completion"]=asynchronous?["completion"]?.DeepClone(),["rootCompletion"]=FunctionDemotion(root.Function),["targets"]=new JsonArray(targets.Select(x=>JsonValue.Create(x)).ToArray()),["nodes"]=new JsonArray(root.Graph["nodes"]!.AsArray().Where(n=>n!["kind"]?.ToString()=="code").Select(n=>(JsonNode)new JsonObject{["id"]=n!["id"]!.DeepClone(),["enabled"]=n["async"]?.GetValue<bool>()==true,["demotion"]=Demotion(n!.AsObject(),id+"/node:"+n["id"]!.ToString())}).ToArray()),["sourceWritten"]=false};
    }
    public static JsonObject Prepare(JsonObject request,Func<Element,string> format) {
        var units=request["units"]!.DeepClone().AsObject();var before=units.DeepClone().AsObject();string id=S(request,"id"),ns=S(request,"namespace");var root=Root(units,id);var targets=Targets(units,id);var plan=request["plan"]!.AsObject();
        if(plan.Count!=2||plan.Any(p=>p.Key is not ("enabled" or "nodes"))||plan["enabled"] is not JsonValue flag||!flag.TryGetValue<bool>(out bool enabled)||plan["nodes"] is not JsonArray changes||changes.Count>64)throw new ArgumentException("Explicit async flag and node transitions required");
        var seen=new HashSet<string>(StringComparer.Ordinal);foreach(var change in changes){if(change is not JsonObject row||row.Count!=2||row.Any(p=>p.Key is not ("node" or "enabled"))||row["enabled"] is not JsonValue state||!state.TryGetValue<bool>(out _)||!seen.Add(S(row,"node")))throw new ArgumentException("Unique explicit node async flags required");}
        var profileMap=new JsonObject();foreach(string target in targets){var g=Graph(units,target);profileMap[target]=g["asyncOriginProfile"]?.DeepClone()??JsonValue.Create(g["profile"]!.ToString()==BlueprintAsync.Profile?FeatureBlueprint.SwitchProfile:g["profile"]!.ToString());}
        bool was=BlueprintAsync.Has(root.Function);if(enabled){var originalFunction=new Parser(S(units[root.Function.Id]!,"original"),"<original-async-function>").ParseElement();string completion=BlueprintAsync.Read(root.Function)?["completion"]?.ToString()??BlueprintFunctionCompletion.Promote(root.Function)??BlueprintAsync.Read(originalFunction)?["completion"]?.ToString()??"async_complete_"+JsonData.Digest(root.Function.Id)[..16];BlueprintAsync.Set(root.Function,completion);}else if(was)BlueprintFunctionCompletion.Demote(root.Function);else root.Function.Values.Remove(BlueprintAsync.Metadata);
        units[root.Function.Id]!["draft"]=format(root.Function);
        if(!enabled&&was)foreach(string target in targets)profileMap[target]=FeatureBlueprint.SwitchProfile;
        foreach(string target in targets){var g=Graph(units,target);g["profile"]=enabled?BlueprintAsync.Profile:profileMap[target]!.DeepClone();if(enabled)g["asyncOriginProfile"]=profileMap[target]!.DeepClone();else g.Remove("asyncOriginProfile");g["contractHash"]=FeatureBlueprint.ContractHash(root.Function);RefreshCalls(units,g,root.Function.Id);
            if(target==id)foreach(var change in changes){var node=g["nodes"]!.AsArray().SingleOrDefault(n=>n!["id"]?.ToString()==change!["node"]?.ToString());if(node?["kind"]?.ToString()!="code")throw new ArgumentException("Own ordinary C# node required");bool value=change!["enabled"]!.GetValue<bool>();if(value&&!enabled)throw new ArgumentException("Explicitly convert this caller function before enabling an async node");if(value&&node["async"]?.GetValue<bool>()!=true||!value)BlueprintCompletionBranch.Set(node.AsObject(),value,target+"/node:"+node["id"]!.ToString());}
            if(BlueprintExecutionBranches.Has(root.Function)&&g["executionExitMode"]?.GetValue<bool>()!=true){var exits=g["exits"]!.AsObject();foreach(string name in exits.Select(p=>p.Key).ToArray())exits[name]=root.Function.Signature!.Return=="void"?new JsonObject{["executionBranch"]="none"}:new JsonObject{["executionBranch"]="none",["value"]=exits[name]?.DeepClone()};g["schema"]=2;g["executionExitMode"]=true;}
            units[target]!["draft"]=g.ToJsonString();
        }
        var callers=CompletionCalls(units,before,root.Function.Id);var changed=targets.Concat(callers).Distinct(StringComparer.Ordinal).ToArray();
        foreach(string target in changed){RefreshCode(units,before,target);var status=Definitions(units,target,describe:true);if(status["state"]?.ToString()=="invalid")throw new ArgumentException("Async execution shape refused: "+status.ToJsonString());}
        var members=Members(units,targets,root.Function.Id).Concat(Observations(units,root.Function.Id)).ToHashSet(StringComparer.Ordinal);
        foreach(string member in members.ToArray())if(units[member]?["rootContractGroup"] is JsonArray priorRoot) {
            if(priorRoot.Any(x=>units[x!.ToString()]?["draft"]?.ToString()!=units[x!.ToString()]?["original"]?.ToString()))throw new ArgumentException("Confirm the previous public contract group first; async input is retained");
            foreach(var x in priorRoot)units[x!.ToString()]!.AsObject().Remove("rootContractGroup");
        }
        foreach(string member in members.ToArray())if(units[member]?["atomicEditGroup"] is JsonArray existing){if(existing.Any(x=>units[x!.ToString()]?[Receipt] is null))throw new ArgumentException("Confirm other pending atomic edits before an async transition");foreach(var x in existing)members.Add(x!.ToString());}
        Scope(units,members,ns);var group=new JsonArray(members.Order(StringComparer.Ordinal).Select(x=>JsonValue.Create(x)).ToArray());var reads=new JsonObject();foreach(var pair in before.Where(p=>members.Contains(p.Key))){if(pair.Value?["path"] is null||pair.Value?["baseline"] is null||pair.Value?["original"] is null)continue;if(PackPaths.Namespace(pair.Key)!=ns)throw new ArgumentException("Owned async closure required");reads[pair.Key]=new JsonObject{["path"]=pair.Value["path"]!.DeepClone(),["hash"]=pair.Value["baseline"]!.DeepClone()};}
        var receipt=new JsonObject{["schema"]=1,["function"]=root.Function.Id,["graphs"]=new JsonArray(targets.Select(x=>JsonValue.Create(x)).ToArray()),["profiles"]=profileMap,["callers"]=new JsonArray(callers.Select(x=>JsonValue.Create(x)).ToArray()),["reads"]=reads};foreach(string member in members){units[member]!["atomicEditGroup"]=group.DeepClone();units[member]![Receipt]??=new JsonObject{["schema"]=1,["function"]=root.Function.Id};}units[root.Function.Id]![Receipt]=receipt;
        var result=new JsonObject();foreach(string member in members)result[member]=units[member]!.DeepClone();Validate(new(){["units"]=units.DeepClone(),["namespace"]=ns});return new(){["group"]=group,["units"]=result,["sourceWritten"]=false,["executed"]=false};
    }
    public static JsonObject Validate(JsonObject request) {
        var units=request["units"]!.AsObject();string ns=S(request,"namespace");var selected=request["selected"]?.AsArray().Select(x=>x!.ToString()).ToHashSet(StringComparer.Ordinal);var checks=new JsonArray();var paths=new HashSet<string>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);
        foreach(var member in units.Where(p=>p.Value?[Receipt] is not null)) {
            var marker=member.Value![Receipt]!;var group=member.Value["atomicEditGroup"] as JsonArray??throw new ArgumentException("Async marker requires its complete group");
            if(selected is not null&&!group.Any(x=>selected.Contains(x!.ToString())))continue;
            string function=S(marker,"function");if(marker["schema"]?.GetValue<int>()!=1||units[function]?[Receipt]?["graphs"] is not JsonArray||!JsonNode.DeepEquals(units[function]!["atomicEditGroup"],group))throw new ArgumentException("Missing/tampered primary async receipt");
        }
        foreach(var pair in units.Where(p=>p.Value?["kind"]?.ToString()=="function"&&p.Value?[Receipt]?["graphs"] is JsonArray)) {
            var receipt=pair.Value![Receipt]!.AsObject();var group=pair.Value["atomicEditGroup"] as JsonArray??throw new ArgumentException("Complete async atomic group required");if(selected is not null&&!group.Any(x=>selected.Contains(x!.ToString())))continue;var ids=group.Select(x=>x!.ToString()).ToArray();if(ids.Length is <3 or >64||ids.Distinct(StringComparer.Ordinal).Count()!=ids.Length||ids.Any(id=>units[id]?[Receipt] is null||!JsonNode.DeepEquals(units[id]!["atomicEditGroup"],group)))throw new ArgumentException("Missing/tampered async group member");Scope(units,ids,ns);
            var fn=Element(units,pair.Key,"function");var original=new Parser(S(pair.Value,"original"),"<original-async-function>").ParseElement();if(receipt["schema"]?.GetValue<int>()!=1||receipt["function"]?.ToString()!=fn.Id||fn.Parent is not null||fn.Signature!.Format()!=original.Signature!.Format()||!BlueprintFunctionCompletion.SameBranches(original,fn))throw new ArgumentException("Preserve original async IO/branch contract");
            var targets=receipt["graphs"]!.AsArray().Select(x=>x!.ToString()).ToArray();if(targets.Length==0||targets.Distinct().Count()!=targets.Length||!targets.ToHashSet(StringComparer.Ordinal).SetEquals(Targets(units,targets[0])))throw new ArgumentException("All original async targets required");if(Members(units,targets,fn.Id).Any(id=>!ids.Contains(id,StringComparer.Ordinal)))throw new ArgumentException("Async original code/target group incomplete");
            foreach(string target in targets){var g=Graph(units,target);if(g["feature"]?.ToString()!=fn.Id||g["contractHash"]?.ToString()!=FeatureBlueprint.ContractHash(fn)||g["profile"]?.ToString()!=(BlueprintAsync.Has(fn)?BlueprintAsync.Profile:receipt["profiles"]?[target]?.ToString()))throw new ArgumentException("Async root contract/profile mismatch");var defs=Definitions(units,target);if(defs["state"]?.ToString()!="node-definitions")throw new ArgumentException("Async definitions invalid");foreach(var entry in BlueprintTree.Nodes(g).Where(n=>n.Node["kind"]?.ToString()=="code")){var record=JsonNode.Parse(S(units[BlueprintTree.SourceId(target,entry.Key)]!,"draft"))!;if(record["definitionHash"]?.ToString()!=defs["nodes"]!.AsArray().Single(n=>n!["id"]?.ToString()==entry.Key)!["definitionHash"]?.ToString())throw new ArgumentException("Async code receipt changed");}}
            var callerIds=(receipt["callers"] as JsonArray??new JsonArray()).Select(x=>x!.ToString()).ToArray();if(callerIds.Distinct().Count()!=callerIds.Length||callerIds.Any(id=>!ids.Contains(id,StringComparer.Ordinal))||!callerIds.ToHashSet(StringComparer.Ordinal).SetEquals(CompletionCallerIds(units,fn.Id)))throw new ArgumentException("Exact owned completion caller group required");
            foreach(string caller in callerIds){var defs=Definitions(units,caller,describe:true);if(defs["state"]?.ToString()=="invalid")throw new ArgumentException("Completion caller source invalid");foreach(var entry in BlueprintTree.Nodes(Graph(units,caller)).Where(n=>n.Node["kind"]?.ToString()=="code")){var record=JsonNode.Parse(S(units[BlueprintTree.SourceId(caller,entry.Key)]!,"draft"))!;if(record["definitionHash"]?.ToString()!=defs["nodes"]!.AsArray().Single(n=>n!["id"]?.ToString()==entry.Key)!["definitionHash"]?.ToString())throw new ArgumentException("Completion caller source receipt changed");}}
            var reads=receipt["reads"] as JsonObject??throw new ArgumentException("Original async reads required");
            if(reads.Any(p=>!ids.Contains(p.Key,StringComparer.Ordinal))||Members(units,targets,fn.Id).Concat(Observations(units,fn.Id)).Any(id=>!reads.ContainsKey(id)))throw new ArgumentException("Complete original async observations required");
            foreach(var read in reads){var unit=units[read.Key]??throw new ArgumentException("Async observed source missing");if(PackPaths.Namespace(read.Key)!=ns||read.Value?["path"]?.ToString()!=unit["path"]?.ToString()||read.Value?["hash"]?.ToString()!=unit["baseline"]?.ToString())throw new ArgumentException("Async original read receipt changed");Scope(units,new[]{read.Key},ns);string path=S(unit,"path");_=PackPaths.Owned(Path.Combine(Path.GetTempPath(),"confectory-async-reads"),path);if(paths.Add(path))checks.Add(new JsonObject{["path"]=path,["hash"]=unit["baseline"]!.DeepClone()});}
        }
        return new(){["valid"]=true,["checks"]=checks,["sourceWritten"]=false,["executed"]=false};
    }
}
