using System.Text.Json.Nodes;

namespace Confectory.Core;

public sealed partial class Builder
{
    public Dictionary<string, JsonObject> InformationContracts { get; } = new(StringComparer.Ordinal);
    readonly Dictionary<string, InformationStructs.Definition> informationTypes = new(StringComparer.Ordinal);
    readonly HashSet<string> informationCompiling = new(StringComparer.Ordinal);
    void PrepareInformation(IEnumerable<string> functions)
    {
        InformationContracts.Clear(); informationTypes.Clear(); informationCompiling.Clear();
        foreach (string function in functions)
            foreach (string type in InformationStructs.SignatureTypes(Registry.Get(function, "function").Signature!))
            {
                foreach (var definition in InformationStructs.ResolveAll(Registry, type, function)) informationTypes.TryAdd(definition.ClrType, definition);
                if (informationTypes.Count > 256) throw new BuildError("INFORMATION_CLR_BUDGET", "At most 256 selected information value types");
            }
    }
    JsonObject InformationContract(string ns)
    {
        if (InformationContracts.TryGetValue(ns, out var prior)) return prior;
        if (HasModuleFlow) { CompileModuleFlowContracts(); return InformationContracts[ns]; }
        if (!informationCompiling.Add(ns)) throw new BuildError("INFORMATION_CLR_PACK_CYCLE", "The selected inline information values require cyclic pack type assemblies: " + ns);
        try {
        var selected = informationTypes.Values.Where(d => PackPaths.Namespace(d.Id) == ns).OrderBy(d => d.Id, StringComparer.Ordinal).ThenBy(d => d.ClrType, StringComparer.Ordinal).ToArray();
        if (selected.Length == 0) throw new BuildError("INFORMATION_CLR_SELECTION", "Information contract was not selected: " + ns);
        var references = new SortedDictionary<string, JsonObject>(StringComparer.Ordinal);
        void AddReference(string pack) {
            if (pack == ns || references.ContainsKey(pack)) return;
            references[pack] = InformationContract(pack);
            foreach (var child in informationTypes.Values.Where(d => PackPaths.Namespace(d.Id) == pack).SelectMany(d => d.Dependencies ?? [])) AddReference(PackPaths.Namespace(child.Id));
        }
        foreach (string pack in selected.SelectMany(d => d.Dependencies ?? []).Select(d => PackPaths.Namespace(d.Id)).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal)) AddReference(pack);
        string name = "Information_" + Generation.Symbol(ns);
        string key = JsonData.Digest(new object[] { ArtifactLayout, InformationStructs.Profile, Tool.Identity, ns, selected.Select(d => new[] { d.Id, d.Source }).ToArray() });
        if (references.Count > 0) key = JsonData.Digest(new object[] { key, InformationStructs.CompoundProfile, references.Select(p => new[] { p.Key, p.Value["key"]!.GetValue<string>() }).ToArray() });
        var artifacts = cache.Get(key) ?? cache.Produce(key, work => Tool.Invoke("compile-contract", new { output = work, name,
            sources = selected.Select(d => WriteSource(Path.Combine(work, Generation.Symbol(InformationStructs.SourceKey(d)) + ".cs"), d.Source)).ToArray(), references = references.Values.Select(p => p["reference"]!.GetValue<string>()).ToArray() })["artifacts"]!.AsObject());
        if (!artifacts.ContainsKey("assembly") || !artifacts.ContainsKey("reference")) throw new BuildError("TOOL_PROTOCOL", "Information compilation must return assembly and reference");
        var result = JsonData.Object(artifacts); result["key"] = key; result["pack"] = ns; InformationContracts[ns] = result; return result;
        } finally { informationCompiling.Remove(ns); }
    }
    JsonObject InformationReferences(IEnumerable<string> functions)
    {
        var result = new JsonObject();
        void Add(string ns) {
            if (result.ContainsKey(ns)) return;
            result[ns] = InformationContract(ns).DeepClone();
            // Every type in the selected pack assembly shares its complete
            // reference closure, including types used by another function.
            foreach (var dependency in informationTypes.Values.Where(d => PackPaths.Namespace(d.Id) == ns).SelectMany(d => d.Dependencies ?? [])) Add(PackPaths.Namespace(dependency.Id));
        }
        foreach (string ns in functions.SelectMany(id => InformationStructs.SignatureTypes(Registry.Get(id, "function").Signature!)).Select(type => PackPaths.Namespace(informationTypes[type].Id)).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal)) Add(ns);
        return result;
    }
    static IEnumerable<string> InformationFiles(IEnumerable<JsonObject> contracts, string kind) => contracts.SelectMany(contract => new[] { "informationContracts", "supportingContracts" }.SelectMany(name => (contract[name] as JsonObject ?? new()).Select(p => p.Value![kind]!.GetValue<string>()))).Distinct(StringComparer.Ordinal);
    JsonArray InformationCatalog() => new(informationTypes.Values.OrderBy(d => d.Id, StringComparer.Ordinal).Select(d => { var item = InformationStructs.Document(d); item.Remove("source"); item.Remove("sourceWritten"); item.Remove("executed"); item["assembly"] = Path.GetFileName(InformationContract(PackPaths.Namespace(d.Id))["assembly"]!.GetValue<string>()); return (JsonNode)item; }).ToArray());
}
