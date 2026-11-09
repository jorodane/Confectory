using System.Text.Json.Nodes;

namespace Confectory.Core;

public sealed partial class Builder
{
    public Dictionary<string, JsonObject> InformationContracts { get; } = new(StringComparer.Ordinal);
    readonly Dictionary<string, InformationStructs.Definition> informationTypes = new(StringComparer.Ordinal);
    void PrepareInformation(IEnumerable<string> functions)
    {
        InformationContracts.Clear(); informationTypes.Clear();
        foreach (string function in functions)
            foreach (string type in InformationStructs.SignatureTypes(Registry.Get(function, "function").Signature!))
            {
                var definition = InformationStructs.Resolve(Registry, type, function);
                informationTypes.TryAdd(type, definition);
                if (informationTypes.Count > 256) throw new BuildError("INFORMATION_CLR_BUDGET", "At most 256 selected information value types");
            }
    }
    JsonObject InformationContract(string ns)
    {
        if (InformationContracts.TryGetValue(ns, out var prior)) return prior;
        var selected = informationTypes.Values.Where(d => PackPaths.Namespace(d.Id) == ns).OrderBy(d => d.Id, StringComparer.Ordinal).ToArray();
        if (selected.Length == 0) throw new BuildError("INFORMATION_CLR_SELECTION", "Information contract was not selected: " + ns);
        string name = "Information_" + Generation.Symbol(ns);
        string key = JsonData.Digest(new object[] { ArtifactLayout, InformationStructs.Profile, Tool.Identity, ns, selected.Select(d => new[] { d.Id, d.Source }).ToArray() });
        var artifacts = cache.Get(key) ?? cache.Produce(key, work => Tool.Invoke("compile-contract", new { output = work, name,
            sources = selected.Select(d => WriteSource(Path.Combine(work, Generation.Symbol(d.Id) + ".cs"), d.Source)).ToArray(), references = Array.Empty<string>() })["artifacts"]!.AsObject());
        if (!artifacts.ContainsKey("assembly") || !artifacts.ContainsKey("reference")) throw new BuildError("TOOL_PROTOCOL", "Information compilation must return assembly and reference");
        var result = JsonData.Object(artifacts); result["key"] = key; result["pack"] = ns; InformationContracts[ns] = result; return result;
    }
    JsonObject InformationReferences(IEnumerable<string> functions)
    {
        var result = new JsonObject();
        foreach (string ns in functions.SelectMany(id => InformationStructs.SignatureTypes(Registry.Get(id, "function").Signature!)).Select(type => PackPaths.Namespace(informationTypes[type].Id)).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal))
            result[ns] = InformationContract(ns).DeepClone();
        return result;
    }
    static IEnumerable<string> InformationFiles(IEnumerable<JsonObject> contracts, string kind) => contracts.SelectMany(contract => (contract["informationContracts"] as JsonObject ?? new()).Select(p => p.Value![kind]!.GetValue<string>())).Distinct(StringComparer.Ordinal);
    JsonArray InformationCatalog() => new(informationTypes.Values.OrderBy(d => d.Id, StringComparer.Ordinal).Select(d => { var item = InformationStructs.Document(d); item.Remove("source"); item.Remove("sourceWritten"); item.Remove("executed"); item["assembly"] = Path.GetFileName(InformationContract(PackPaths.Namespace(d.Id))["assembly"]!.GetValue<string>()); return (JsonNode)item; }).ToArray());
}
