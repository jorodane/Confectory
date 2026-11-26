using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

namespace Confectory.Core;

// Authored JSON documents, never generated C#. Final acceptance remains compiler-backed Confirm.
public static class BlueprintDocuments
{
    private static void Require(bool condition, string message)
    { if (!condition) throw new ArgumentException(message); }

    public static JsonObject Validate(string id, string kind, string text)
    {
        var document = JsonNode.Parse(text)?.AsObject() ?? throw new ArgumentException("Blueprint source object required");
        Require(document["schema"]?.GetValue<int>() == 1 || kind == "blueprint" && document["schema"]?.GetValue<int>() == 2 && document["executionExitMode"]?.GetValue<bool>() == true && document["profile"]?.ToString() is FeatureBlueprint.SwitchProfile or BlueprintAsync.Profile, "Blueprint source schema required");
        if (kind == "blueprint-node")
        {
            int marker = id.LastIndexOf("/node:", StringComparison.Ordinal);
            Require(marker > 0 && document["node"]?.ToString() == id[(marker + 6)..], "Stable node identity required");
            Require(Regex.IsMatch(document["definitionHash"]?.ToString() ?? "", "\\A[0-9a-f]{64}\\z", RegexOptions.CultureInvariant), "Node definition hash required");
            Require(document["source"] is JsonValue value && value.TryGetValue<string>(out _), "Node source string required");
            if(document.ContainsKey("helpers")) Require(document["helpers"] is JsonValue helper && helper.TryGetValue<string>(out _), "Static helper method source string required");
            Require(document.All(p => p.Key is "schema" or "node" or "definitionHash" or "source" or "helpers"), "Only node source, static helper methods and its definition receipt belong in a node file");
        }
        else if (kind == "blueprint")
        {
            Require(id.Contains("/body:", StringComparison.Ordinal), "Explicit implementation target source required");
            Require(document["profile"]?.ToString() is FeatureBlueprint.Profile or FeatureBlueprint.ImplicitProfile or FeatureBlueprint.MultiOutputProfile or FeatureBlueprint.LocalsProfile or FeatureBlueprint.RefNodesProfile or FeatureBlueprint.ExternalRefsProfile or FeatureBlueprint.AliasLocalsProfile or FeatureBlueprint.NestedProfile or FeatureBlueprint.PropertyProfile or FeatureBlueprint.MethodsProfile or FeatureBlueprint.SwitchProfile or FeatureBlueprint.PropertySetProfile or FeatureBlueprint.PropertyRefProfile or BlueprintAsync.Profile, "Supported Blueprint profile required");
            Require(Regex.IsMatch(document["feature"]?.ToString() ?? "", @"\A[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*::[A-Za-z_][A-Za-z_0-9]*\z", RegexOptions.CultureInvariant), "Qualified feature identity required");
            Require(document["nodes"] is JsonArray && document["edges"] is JsonArray && document["exits"] is JsonObject, "Graph source collections required");
            if(FeatureBlueprint.SupportsPrivateGraphs(document["profile"]?.ToString()))BlueprintTree.Nodes(document).ToArray();
            var ids = new HashSet<string>(StringComparer.Ordinal);
            foreach (var node in document["nodes"]!.AsArray())
            {
                string nodeId = node?["id"]?.GetValue<string>() ?? "";
                Require(nodeId.Length <= 128 && Regex.IsMatch(nodeId, @"\A[A-Za-z_][A-Za-z_0-9.-]*\z", RegexOptions.CultureInvariant) && ids.Add(nodeId), "Unique stable node ID required");
            }
        }
        else throw new ArgumentException("Blueprint document kind required");
        return new JsonObject { ["id"] = id, ["kind"] = kind, ["validSourceDocument"] = true, ["compiled"] = false };
    }

    // One projection already owns a bounded, exact source snapshot. Validate
    // each original document by the same validator, without a process per leaf.
    public static JsonObject ValidateBatch(JsonArray documents)
    {
        Require(documents.Count is >0 and <=64, "Bounded Blueprint source batch required");
        var seen = new HashSet<string>(StringComparer.Ordinal);
        int bytes=0;
        foreach (var value in documents)
        {
            Require(value is JsonObject {Count:3} && value["id"] is JsonValue &&
                value["kind"] is JsonValue && value["text"] is JsonValue, "Exact Blueprint source required");
            string id=value!["id"]!.GetValue<string>(), kind=value["kind"]!.GetValue<string>(), text=value["text"]!.GetValue<string>();
            bytes=checked(bytes+System.Text.Encoding.UTF8.GetByteCount(text));
            Require(seen.Add(id)&&bytes<=2097152,"Unique bounded Blueprint source snapshot required");
            Validate(id,kind,text);
        }
        return new JsonObject{["validated"]=documents.Count};
    }

    public static JsonObject DescribeOwned(JsonObject request) => DescribeOwned(request, allowCompoundPreview: false);

    public static JsonObject DescribeOwned(JsonObject request, bool allowCompoundPreview, OwnedGraphReadModel? model = null)
    {
        string project = Path.GetFullPath(request["project"]!.GetValue<string>());
        var graph=request["graph"]!.DeepClone().AsObject();
        // Only the directly owned, property-free projection is eligible for
        // a retained contract context. Other contexts keep the original registry path.
        bool eligible=model is not null &&
            (request["draftPropertySources"] is null or JsonObject { Count: 0 }) &&
            !BlueprintTree.Nodes(graph).Any(node=>FeatureBlueprint.IsPropertyNode(node.Node["kind"]?.ToString()));
        var key=new JsonObject{["project"]=project,["id"]=request["id"]?.DeepClone(),["text"]=request["text"]?.DeepClone(),["draftContracts"]=request["draftContracts"]?.DeepClone()}.ToJsonString();
        OwnedGraphReadModel.Context? prepared=eligible?model!.Get(project,key):null;
        Registry? registry=null;
        Element implementation;
        string featureSource;
        JsonObject contracts;
        if(prepared is not null)
        {
            implementation=prepared.Implementation;
            featureSource=prepared.FeatureSource;
            contracts=prepared.Contracts.DeepClone().AsObject();
        }
        else
        {
            var observation=eligible?new OwnedGraphReadModel.Observation():null;
            var statistics=new BuildStatistics();
            registry=new Registry(project, new Documents(Path.Combine(Path.GetDirectoryName(project)!, ".confectory", "document-cache"), statistics, observation is null?null:observation.Read),statistics);
            implementation=new Parser(request["text"]!.GetValue<string>(), "<assigned-implementation>").ParseElement();
            Require(implementation.Id == request["id"]!.ToString() && implementation.Kind == "implementation" && PackPaths.Namespace(implementation.Id) == registry.Project.Namespace, "Assigned project implementation required");
            if(implementation.Parent is not null)
            {
                registry.Elements[implementation.Id]=implementation;
                implementation=registry.Effective(implementation.Id);
                observation=null;
            }
            string ReadContract(string id)
            {
                string? draft=request["draftContracts"]?[id]?.GetValue<string>();
                string source;
                if(draft is not null&&PackPaths.Namespace(id)==registry.Project.Namespace)source=draft;
                else
                {
                    var declaration=registry.Get(id,"function",implementation.Id);
                    source=draft??(observation is null?File.ReadAllText(declaration.Loc.File):observation.Text(declaration.Loc.File));
                }
                var parsed=new Parser(source,"<owned-contract>").ParseElement();
                Require(parsed.Kind=="function"&&parsed.Id==id,"Assigned contract identity required");
                return source;
            }
            contracts=new JsonObject();
            foreach(string id in implementation.Imports.Values.Select(i=>i.Id).Distinct(StringComparer.Ordinal))contracts[id]=ReadContract(id);
            featureSource=ReadContract(implementation.Function!);
            if(observation is not null)
            {
                observation.BindPaths(project,registry);
                model!.Put(project,key,new OwnedGraphReadModel.Context(implementation,featureSource,contracts.DeepClone().AsObject(),observation));
            }
        }
        string assemblyPath=request["assemblePreview"]?.GetValue<bool>()==true?request["privatePath"]?.GetValue<string>()??"":"";
        if(assemblyPath.Length>0)
        {
            Require(implementation.Parent is null&&PackPaths.Namespace(implementation.Function!)==PackPaths.Namespace(implementation.Id),"Direct owned child preview required");
            var root=request["graph"]!.AsObject();
            if(allowCompoundPreview)BlueprintCellRegion.OwnedPreviewFrame(root,assemblyPath,previewOutParameters:true);
            else BlueprintCellRegion.OwnedFrame(root,assemblyPath);
        }
        bool rebind=request["rebindContract"]?.GetValue<bool>()==true;
        if(rebind){
            var feature=new Parser(featureSource,"<current-owned-feature>").ParseElement();graph["contractHash"]=FeatureBlueprint.ContractHash(feature);
            if(feature.Signature!.Args.Any(p=>p.IsRef)&&!FeatureBlueprint.SupportsExternalRefs(graph["profile"]?.ToString()))graph["profile"]=FeatureBlueprint.ExternalRefsProfile;
            else if(feature.Signature.Args.Any(p=>p.IsOut)&&graph["profile"]?.ToString() is FeatureBlueprint.Profile or FeatureBlueprint.ImplicitProfile)graph["profile"]=FeatureBlueprint.MultiOutputProfile;
        }
        if(FeatureBlueprint.SupportsPrivateGraphs(graph["profile"]?.ToString())){
            string ownedTarget=request["bodyTarget"]?.GetValue<string>()??throw new ArgumentException("Explicit owned private graph body target required");
            Require(implementation.Bodies.TryGetValue(ownedTarget,out var ownedBody)&&ownedBody.SourceKind=="blueprint","Owned Blueprint body target required");
        }
        var propertyContracts=new JsonObject();
        if(registry is not null)
        {
            RuntimeObjectContracts.ApplyOwnedDrafts(registry,request["draftPropertySources"] as JsonObject);
            propertyContracts=RuntimeObjectContracts.ForGraph(registry,implementation.Id,graph,request["definitionsOnly"]?.GetValue<bool>()==true);
        }
        var projection=new JsonObject
        {
            ["operation"] = request["definitionsOnly"]?.GetValue<bool>() == true ? "featureBlueprintNodes" : request["assemblePreview"]?.GetValue<bool>() == true ? "featureBlueprintAssemble" : "featureBlueprintDescribe", ["featureSource"] = featureSource,
            ["inspectStalePostCalls"] = request["definitionsOnly"]?.GetValue<bool>() == true && request["inspectStalePostCalls"]?.GetValue<bool>() == true,
            ["inspectStaleAsyncCalls"] = request["definitionsOnly"]?.GetValue<bool>() == true && request["inspectStaleAsyncCalls"]?.GetValue<bool>() == true,
            ["implementationContext"] = FeatureBlueprint.ImplementationContext(implementation), ["bodyTarget"] = request["bodyTarget"]?.DeepClone(), ["featureContracts"] = contracts, ["graph"] = graph,
            ["implementations"] = request["implementations"]?.DeepClone(), ["propertyContracts"] = propertyContracts,
            ["assemblyPath"] = assemblyPath.Length>0?assemblyPath:null
        };
        var result=model is null||rebind?FeatureBlueprint.Execute(projection):model.Project(project,projection);
        if(rebind)result["reboundGraph"]=graph.DeepClone();
        if(request["privatePath"] is JsonValue privatePath && privatePath.GetValue<string>().Length>0 && result["state"]?.ToString()!="invalid")
        {
            Require(!rebind,"Private contract belongs to its parent node signature");
            BlueprintTree.Select(graph,privatePath.GetValue<string>());
            var assembled=result["selectedAssembly"]?.DeepClone();
            result=BlueprintTree.SelectDescription(result,privatePath.GetValue<string>());
            if(assemblyPath.Length>0){
                Require(result["state"]?.ToString()=="source-assembled"&&assembled?["path"]?.ToString()==assemblyPath
                    &&assembled["bodyHash"]?.ToString()==result["bodyHash"]?.ToString(),"Exact actual child assembly unavailable");
                result["body"]=assembled!["body"]!.DeepClone();result["members"]=assembled["members"]!.DeepClone();result["assembledPath"]=assemblyPath;
            }
        }
        result["propertyContracts"]=propertyContracts.DeepClone();
        return result;
    }

    public static JsonArray NodeUnits(string root, string graphPath, string bodyId, string? draft = null)
    {
        var units = new JsonArray();
        if (draft is null && !File.Exists(graphPath)) return units;
        var graph = JsonNode.Parse(draft ?? File.ReadAllText(graphPath))?.AsObject() ?? throw new ArgumentException("Graph source object required");
        Validate(bodyId, "blueprint", graph.ToJsonString());
        var paths = new HashSet<string>(OperatingSystem.IsWindows() ? StringComparer.OrdinalIgnoreCase : StringComparer.Ordinal);
        foreach (var entry in BlueprintTree.Nodes(graph))
        {
            var node = entry.Node;
            if (node!["kind"]?.ToString() != "code" || node["implementation"] is null) continue;
            string path = PackPaths.Owned(Path.GetDirectoryName(graphPath)!, node["implementation"]!.GetValue<string>());
            path = PackPaths.Owned(root, Path.GetRelativePath(root, path));
            Require(paths.Add(path), "Each node needs its own source file");
            units.Add(new JsonObject
            {
                ["id"] = BlueprintTree.SourceId(bodyId, entry.Key), ["kind"] = "blueprint-node", ["path"] = Path.GetRelativePath(root, path)
            });
        }
        return units;
    }
}
