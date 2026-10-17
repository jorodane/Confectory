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
        Require(document["schema"]?.GetValue<int>() == 1, "Blueprint source schema required");
        if (kind == "blueprint-node")
        {
            int marker = id.LastIndexOf("/node:", StringComparison.Ordinal);
            Require(marker > 0 && document["node"]?.ToString() == id[(marker + 6)..], "Stable node identity required");
            Require(Regex.IsMatch(document["definitionHash"]?.ToString() ?? "", "\\A[0-9a-f]{64}\\z", RegexOptions.CultureInvariant), "Node definition hash required");
            Require(document["source"] is JsonValue value && value.TryGetValue<string>(out _), "Node source string required");
            Require(document.All(p => p.Key is "schema" or "node" or "definitionHash" or "source"), "Only node source and its definition receipt belong in a node file");
        }
        else if (kind == "blueprint")
        {
            Require(id.Contains("/body:", StringComparison.Ordinal), "Explicit implementation target source required");
            Require(document["profile"]?.ToString() is FeatureBlueprint.Profile or FeatureBlueprint.ImplicitProfile, "Supported Blueprint profile required");
            Require(Regex.IsMatch(document["feature"]?.ToString() ?? "", @"\A[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*::[A-Za-z_][A-Za-z_0-9]*\z", RegexOptions.CultureInvariant), "Qualified feature identity required");
            Require(document["nodes"] is JsonArray && document["edges"] is JsonArray && document["exits"] is JsonObject, "Graph source collections required");
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

    public static JsonObject DescribeOwned(JsonObject request)
    {
        string project = Path.GetFullPath(request["project"]!.GetValue<string>());
        var registry = new Registry(project, new Documents(Path.Combine(Path.GetDirectoryName(project)!, ".confectory", "document-cache"), new BuildStatistics()), new BuildStatistics());
        var implementation = new Parser(request["text"]!.GetValue<string>(), "<assigned-implementation>").ParseElement();
        Require(implementation.Id == request["id"]!.ToString() && implementation.Kind == "implementation" && PackPaths.Namespace(implementation.Id) == registry.Project.Namespace, "Assigned project implementation required");
        if (implementation.Parent is not null)
        {
            registry.Elements[implementation.Id] = implementation;
            implementation = registry.Effective(implementation.Id);
        }
        string ReadContract(string id)
        {
            string? draft = request["draftContracts"]?[id]?.GetValue<string>();
            // A new owned function is not in the physical manifest until reviewed Confirm.
            // Foreign contracts still require the registry's ordinary dependency checks.
            string source;
            if (draft is not null && PackPaths.Namespace(id) == registry.Project.Namespace) source = draft;
            else
            {
                var declaration = registry.Get(id, "function", implementation.Id);
                source = draft ?? File.ReadAllText(declaration.Loc.File);
            }
            var parsed = new Parser(source, "<owned-contract>").ParseElement();
            Require(parsed.Kind == "function" && parsed.Id == id, "Assigned contract identity required");
            return source;
        }
        var contracts = new JsonObject();
        foreach (string id in implementation.Imports.Values.Select(i => i.Id).Distinct(StringComparer.Ordinal)) contracts[id] = ReadContract(id);
        return FeatureBlueprint.Execute(new JsonObject
        {
            ["operation"] = request["definitionsOnly"]?.GetValue<bool>() == true ? "featureBlueprintNodes" : "featureBlueprintDescribe", ["featureSource"] = ReadContract(implementation.Function!),
            ["implementationContext"] = FeatureBlueprint.ImplementationContext(implementation), ["featureContracts"] = contracts, ["graph"] = request["graph"]!.DeepClone(),
            ["implementations"] = request["implementations"]?.DeepClone()
        });
    }

    public static JsonArray NodeUnits(string root, string graphPath, string bodyId, string? draft = null)
    {
        var units = new JsonArray();
        if (draft is null && !File.Exists(graphPath)) return units;
        var graph = JsonNode.Parse(draft ?? File.ReadAllText(graphPath))?.AsObject() ?? throw new ArgumentException("Graph source object required");
        Validate(bodyId, "blueprint", graph.ToJsonString());
        var paths = new HashSet<string>(OperatingSystem.IsWindows() ? StringComparer.OrdinalIgnoreCase : StringComparer.Ordinal);
        foreach (var node in graph["nodes"]!.AsArray())
        {
            if (node!["kind"]?.ToString() != "code" || node["implementation"] is null) continue;
            string path = PackPaths.Owned(Path.GetDirectoryName(graphPath)!, node["implementation"]!.GetValue<string>());
            path = PackPaths.Owned(root, Path.GetRelativePath(root, path));
            Require(paths.Add(path), "Each node needs its own source file");
            units.Add(new JsonObject
            {
                ["id"] = bodyId + "/node:" + node["id"]!.GetValue<string>(), ["kind"] = "blueprint-node", ["path"] = Path.GetRelativePath(root, path)
            });
        }
        return units;
    }
}
