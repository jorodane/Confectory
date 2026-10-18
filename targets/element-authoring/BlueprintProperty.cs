using Confectory.Core;
using System.Text.Json.Nodes;

internal static class BlueprintProperty
{
    static Registry Registry(JsonObject request)
    {
        string project=Path.GetFullPath(request["project"]!.GetValue<string>());
        var registry=new Registry(project,new Documents(Path.Combine(Path.GetDirectoryName(project)!,".confectory","document-cache"),new BuildStatistics()),new BuildStatistics());
        RuntimeObjectContracts.ApplyOwnedDrafts(registry,request["draftPropertySources"] as JsonObject);
        return registry;
    }
    public static JsonObject Query(JsonObject request)
    {
        var registry=Registry(request);
        string source=request["sourceId"]!.GetValue<string>();
        if(request["action"]?.ToString()=="list")
        {
            string query=request["query"]?.ToString()??"";int page=request["page"]?.GetValue<int>()??0;
            if(query.Length>256||page<0||page>1000000)throw new ArgumentException("Bounded explicit property owner page required");
            var rows=registry.Project.Elements.Where(p=>p.Value.Kind is "object" or "concept").Select(p=>registry.Project.Namespace+"::"+p.Key).Where(id=>id.Contains(query,StringComparison.OrdinalIgnoreCase)).Order(StringComparer.Ordinal).ToArray();
            return new JsonObject{["rows"]=new JsonArray(rows.Skip(checked(page*32)).Take(32).Select(id=>(JsonNode)new JsonObject{["id"]=id}).ToArray()),["total"]=rows.Length,["page"]=page,["pageSize"]=32,["runtimeValuesRead"]=false};
        }
        string owner=request["owner"]!.GetValue<string>();
        var descriptor=RuntimeObjectContracts.Describe(registry,owner,source);
        var observations=new JsonArray();foreach(var id in descriptor["dependencies"]!.AsArray()){
            var declaration=registry.Get(id!.ToString());string path=declaration.Loc.File;
            observations.Add(new JsonObject{["id"]=declaration.Id,["path"]=path,["sha256"]=JsonData.HashBytes(File.ReadAllBytes(path))});
        }
        return new JsonObject{["descriptor"]=descriptor,["observations"]=observations,["runtimeValuesRead"]=false,["sourceWritten"]=false};
    }

    public static JsonObject Prepare(JsonObject request,Func<Element,string> format)
    {
        var registry=Registry(request);
        var implementation=new Parser(request["text"]!.GetValue<string>(),"<property-owner>").ParseElement();
        if(implementation.Kind!="implementation"||implementation.Id!=request["id"]!.ToString()||PackPaths.Namespace(implementation.Id)!=registry.Project.Namespace)throw new ArgumentException("Owned implementation required");
        string owner=request["owner"]!.GetValue<string>(),name=request["field"]!.GetValue<string>(),id=request["node"]!.GetValue<string>();
        if(id.Length>128||!System.Text.RegularExpressions.Regex.IsMatch(id,@"\A[A-Za-z_][A-Za-z_0-9.-]*\z"))throw new ArgumentException("Stable property node identity required");
        var descriptor=RuntimeObjectContracts.Describe(registry,owner,implementation.Id);
        var field=descriptor["fields"]!.AsArray().Single(f=>f!["name"]!.ToString()==name)!;
        if(field["supported"]?.GetValue<bool>()!=true)throw new ArgumentException("This field kind has no live property value contract");
        var graph=request["graph"]!.DeepClone().AsObject();string path=request["privatePath"]?.ToString()??"";
        if(!FeatureBlueprint.SupportsProperties(graph["profile"]?.ToString()))throw new ArgumentException("Explicitly upgrade to the node-time property profile first");
        var selected=BlueprintTree.Select(graph,path);if(!FeatureBlueprint.SupportsProperties(selected["profile"]?.ToString()))throw new ArgumentException("Private property profile required");
        string access=request["access"]?.GetValue<string>()??"read";if(access is not ("read" or "set"))throw new ArgumentException("Explicit read or set property access required");
        bool writing=access=="set";if(writing&&(graph["profile"]?.ToString()!=FeatureBlueprint.PropertySetProfile||selected["profile"]?.ToString()!=FeatureBlueprint.PropertySetProfile))throw new ArgumentException("Explicitly upgrade to the property Set profile first");
        string kind=writing?"property-set":"property";
        bool rebind=request["rebind"]?.GetValue<bool>()==true;
        var prior=selected["nodes"]!.AsArray().SingleOrDefault(n=>n!["id"]!.ToString()==id);
        if(rebind?prior?["kind"]?.ToString()!=kind:prior is not null)throw new ArgumentException("Explicit new property or existing property rebind required");
        var reader=registry.Get(writing?FeatureBlueprint.PropertySetter:FeatureBlueprint.PropertyReader,"function",implementation.Id);
        var parameters=new List<Parameter>{new("object","target")};if(writing)parameters.Add(new(field["clrType"]!.ToString(),"value"));
        var signature=new FunctionSignature(parameters,writing?"void":field["clrType"]!.ToString());
        string alias=FeatureBlueprint.ImportAlias(reader.Id);
        if(implementation.Imports.TryGetValue(alias,out var existing)){
            if(existing.Id!=reader.Id||!existing.Signature.Matches(reader.Signature))throw new ArgumentException("Existing property reader import differs; preserve and review it explicitly");
        }else{
            if(implementation.Imports.Values.Any(i=>i.Id==reader.Id))throw new ArgumentException("Property reader has another alias; review the existing typed import explicitly");
            implementation.Imports.Add(alias,new Import(reader.Id,reader.Signature!,null,new(),implementation.Id));
        }
        var node=new JsonObject{["id"]=id,["kind"]=kind,["control"]=prior?["control"]?.DeepClone()??JsonValue.Create("next"),["intent"]=prior?["intent"]?.DeepClone()??JsonValue.Create((writing?"Set ":"Read ")+owner+" / "+name+" at this node"),["propertyOwner"]=owner,["field"]=name,["fieldContractHash"]=field["hash"]!.DeepClone(),["signature"]=FeatureBlueprint.SignatureDocument(signature),["arguments"]=new JsonObject{["target"]=request["target"]?.DeepClone()??prior?["arguments"]?["target"]?.DeepClone()}};
        if(writing)node["arguments"]!["value"]=request["value"]?.DeepClone()??prior?["arguments"]?["value"]?.DeepClone();
        if(prior?["branchOwner"] is JsonNode branchOwner)node["branchOwner"]=branchOwner.DeepClone();
        if(prior is null)selected["nodes"]!.AsArray().Add(node);else selected["nodes"]!.AsArray()[selected["nodes"]!.AsArray().IndexOf(prior)]=node;
        return new JsonObject{["implementation"]=format(implementation),["graph"]=graph,["node"]=node.DeepClone(),["descriptor"]=descriptor,[writing?"setterSource":"readerSource"]=File.ReadAllText(reader.Loc.File),[writing?"writeTiming":"readTiming"]="execution-node",["sourceWritten"]=false,["executed"]=false};
    }
}
