using Confectory.Core;
using System.Text;
using System.Text.Json.Nodes;

// Return routing edits own a body, never the inherited public contract.
internal static class BlueprintPublicBodyReturns
{
    static string Hash(string value)=>JsonData.HashBytes(Encoding.UTF8.GetBytes(value));
    public static JsonObject Prepare(JsonObject request)
    {
        var owner=request["ownerRequest"]!.AsObject();string id=request["id"]!.GetValue<string>();
        var declared=new Parser(owner["text"]!.GetValue<string>(),"<owned-return-body>").ParseElement();
        if(declared.Parent is null&&owner["registeredFunction"] is null)throw new ArgumentException("An owned child or registered-contract Blueprint target is required");
        if(!declared.Bodies.TryGetValue(owner["bodyTarget"]!.ToString(),out var ownedBody)||ownedBody.SourceKind!="blueprint"||ownedBody.Origin!=declared.Id)throw new ArgumentException("Preserve the explicitly owned target");
        if(owner["registeredFunction"] is JsonObject external){BlueprintPublicReturnContract.Validate(external,declared,owner["manifest"]!.ToString(),owner["text"]!.ToString());BlueprintPublicReturnContract.Query(new(){["action"]="verifyReturnContract",["project"]=owner["project"]!.DeepClone(),["manifest"]=owner["manifest"]!.DeepClone(),["text"]=owner["text"]!.DeepClone(),["snapshot"]=external.DeepClone()});}
        BlueprintNodeFlow.ValidateOwnedOverride(owner,id);
        var graph=request["graph"]!.AsObject();
        if(graph["schema"]?.GetValue<int>()!=2||graph["executionExitMode"]?.GetValue<bool>()!=true||graph["copySource"] is not null||graph["profile"]?.ToString()!="sync-acyclic-switch-v1"||graph["nodes"]!.AsArray().Any(n=>n!["kind"]?.ToString() is not ("code" or "export")||n["implementationContext"] is not null||n["postCall"] is not null))throw new ArgumentException("Preserve the existing public execution body and profile");
        return new(){["valid"]=true};
    }
    public static JsonArray Guards(JsonObject units,JsonArray? selected)
    {
        var checks=new SortedDictionary<string,JsonNode>(StringComparer.Ordinal);
        foreach(var flow in units){
            if(flow.Value?["kind"]?.ToString()!="blueprint"||flow.Value["draft"] is null)continue;
            var graph=JsonNode.Parse(flow.Value["draft"]!.GetValue<string>())!.AsObject();
            if(graph["executionExitMode"]?.GetValue<bool>()!=true)continue;
            int marker=flow.Key.IndexOf("/body:",StringComparison.Ordinal);if(marker<0)continue;
            var implementation=units[flow.Key[..marker]];if(implementation?["draft"] is null)continue;
            var owner=new Parser(implementation["draft"]!.GetValue<string>(),"<retained-return-owner>").ParseElement();
            bool externalFunction=PackPaths.Namespace(owner.Function!)!=PackPaths.Namespace(owner.Id);
            if(owner.Parent is null&&!externalFunction||flow.Value["nodeFlowOrigin"] is not null)continue;
            if(flow.Value["draft"]!.ToString()==flow.Value["original"]?.ToString()&&flow.Value["publicBodyOrigin"] is null)continue;
            if(graph["profile"]?.ToString()!="sync-acyclic-switch-v1"||graph["nodes"]!.AsArray().Any(n=>n!["kind"]?.ToString() is not ("code" or "export")||n["implementationContext"] is not null||n["postCall"] is not null))throw new ArgumentException("Review the existing imported/private/native body boundary separately");
            var origin=flow.Value["publicBodyOrigin"]?.AsObject()??throw new ArgumentException("Retain the child public return source receipt");
            var group=flow.Value["atomicEditGroup"]?.AsArray()??throw new ArgumentException("Complete public return review group required");
            if(selected is not null&&!selected.Any(v=>group.Any(m=>m!.ToString()==v!.ToString())))continue;
            if(origin.Count!=(externalFunction?4:3)||origin["version"]?.GetValue<int>()!=1||origin.Any(p=>p.Key is not ("version" or "sources" or "registeredAncestry" or "registeredFunction"))||origin["sources"] is not JsonObject sources||sources.Count is <3 or >64||group.Count!=sources.Count||group.Select(v=>v!.ToString()).Distinct(StringComparer.Ordinal).Count()!=group.Count)throw new ArgumentException("Exact bounded public return receipt required");
            string target=flow.Key[(marker+6)..];
            if(!owner.Bodies.TryGetValue(target,out var body)||body.SourceKind!="blueprint"||body.Origin!=owner.Id||graph["copySource"] is not null)throw new ArgumentException("Preserve parent/reference body ownership");
            foreach(var member in group){
                string id=member!.ToString();var unit=units[id]??throw new ArgumentException("Retain every observed public return source");var proof=sources[id]?.AsObject()??throw new ArgumentException("Complete observed source receipt required");
                if(!id.StartsWith(PackPaths.Namespace(owner.Id)+"::",StringComparison.Ordinal)||unit["baseline"]?.ToString()=="missing"||!JsonNode.DeepEquals(unit["atomicEditGroup"],group)||proof.Count!=3||proof["path"]?.ToString()!=unit["path"]?.ToString()||proof["kind"]?.ToString()!=unit["kind"]?.ToString()||proof["hash"]?.ToString()!=Hash(unit["original"]!.GetValue<string>()))throw new ArgumentException("Public return source ownership or original receipt changed");
                if(id!=flow.Key&&unit["draft"]!.ToString()!=unit["original"]!.ToString())throw new ArgumentException("Public return editing cannot change contracts or retained sources");
                string path=unit["path"]!.ToString();var check=new JsonObject{["path"]=path,["hash"]=unit["baseline"]!.DeepClone()};
                if(checks.TryGetValue(path,out var prior)&&!JsonNode.DeepEquals(prior,check))throw new ArgumentException("Observed return source versions differ");checks[path]=check;
            }
            var before=JsonNode.Parse(flow.Value["original"]!.GetValue<string>())!.AsObject();var after=graph.DeepClone().AsObject();
            foreach(string field in new[]{"exits","edges","entry"}){before.Remove(field);after.Remove(field);}
            if(!JsonNode.DeepEquals(before,after))throw new ArgumentException("Public return edits preserve nodes, profile, IDs and data contracts");
            Element feature;
            if(externalFunction){var manifest=units.Single(u=>u.Value?["kind"]?.ToString()=="project").Value!["draft"]!.GetValue<string>();feature=BlueprintPublicReturnContract.Validate(origin["registeredFunction"]!.AsObject(),owner,manifest,implementation["draft"]!.ToString());}
            else{var function=units[owner.Function!];if(function?["kind"]?.ToString()!="function")throw new ArgumentException("Retain the owned public function contract");feature=new Parser(function["draft"]!.GetValue<string>(),"<retained-public-contract>").ParseElement();}
            var branches=BlueprintExecutionBranches.Read(feature);var allowed=new HashSet<string>(branches.Select(b=>b!["id"]!.ToString()),StringComparer.Ordinal){"none"};
            foreach(var exit in graph["exits"]!.AsObject())if(exit.Value is not JsonObject choice||choice.Count!=1||!allowed.Contains(choice["executionBranch"]?.ToString()??""))throw new ArgumentException("Choose an existing public execution branch or None");
        }
        return new JsonArray(checks.Values.Select(v=>v.DeepClone()).ToArray());
    }
}
