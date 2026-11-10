using System.Text.Json.Nodes;

namespace Confectory.Core;

public sealed partial class Builder
{
    bool HasModuleFlow => informationTypes.Values.Any(d => d.PublicContracts?.Count > 0);

    // Public function result DTOs and module interfaces can refer to one another.
    // Compile against nominal declarations first, then replace every declaration
    // assembly with the real information assembly of the same name. Bootstrap
    // artifacts are cache inputs only; no linker/catalog ever receives them.
    void CompileModuleFlowContracts()
    {
        if (Contracts.Count > 0) return;
        var definitions = informationTypes.Values.OrderBy(d => d.Id, StringComparer.Ordinal).ToArray();
        var information = definitions.GroupBy(d => PackPaths.Namespace(d.Id)).ToDictionary(g => g.Key, g => g.ToArray(), StringComparer.Ordinal);
        var order = new List<string>(); var visiting = new HashSet<string>(StringComparer.Ordinal); var done = new HashSet<string>(StringComparer.Ordinal);
        void Visit(string pack) {
            if (done.Contains(pack)) return;
            if (!visiting.Add(pack)) throw new BuildError("INFORMATION_CLR_PACK_CYCLE", "The selected inline information values require cyclic pack type assemblies: " + pack);
            foreach (var dependency in information[pack].SelectMany(d => d.Dependencies ?? []).Select(d => PackPaths.Namespace(d.Id)).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal))
                if (dependency != pack) Visit(dependency);
            visiting.Remove(pack); done.Add(pack); order.Add(pack);
        }
        foreach (string pack in information.Keys.Order(StringComparer.Ordinal)) Visit(pack);
        InformationContracts.Clear();
        var sources = contractGroups.OrderBy(g => g.Key, StringComparer.Ordinal).ToDictionary(g => g.Key,
            g => g.Value.Select(id => (Id: id, Source: Generation.ContractSource(Registry.Get(id, "function")))).ToArray(), StringComparer.Ordinal);
        string plan = JsonData.Digest(new object[] { ArtifactLayout, Generation.Abi, ModuleInterfaces.FlowProfile, Tool.Identity,
            definitions.Select(d => new[] { d.Id, d.Source }).ToArray(), sources.Select(g => new object[] { g.Key, g.Value.Select(s => new[] { s.Id, s.Source }).ToArray() }).ToArray() });
        var bootstrap = new SortedDictionary<string, JsonObject>(StringComparer.Ordinal);
        JsonObject Compile(string key, string name, (string Id, string Source)[] code, IEnumerable<string> references) {
            var artifact = cache.Get(key) ?? cache.Produce(key, work => Tool.Invoke("compile-contract", new { output = work, name,
                sources = code.Select(s => WriteSource(Path.Combine(work, Generation.Symbol(s.Id) + ".cs"), s.Source)).ToArray(),
                references = references.Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal).ToArray() })["artifacts"]!.AsObject());
            if (!artifact.ContainsKey("assembly") || !artifact.ContainsKey("reference")) throw new BuildError("TOOL_PROTOCOL", "Module contract compilation must return assembly and reference");
            var result = JsonData.Object(artifact); result["key"] = key; return result;
        }
        foreach (var pack in information.OrderBy(p => p.Key, StringComparer.Ordinal)) {
            var code = pack.Value.Select(d => (d.Id, "namespace Confectory.Information." + Generation.Symbol(pack.Key) + " { public " +
                (d.Kind == "module" ? "interface " : d.Kind == "enum" ? "enum " : "struct ") + Generation.Symbol(d.Id) + " {} }\n")).ToArray();
            bootstrap[pack.Key] = Compile(JsonData.Digest(new[] { plan, "nominal-bootstrap", pack.Key }), "Information_" + Generation.Symbol(pack.Key), code, []);
        }
        var realContracts = new SortedDictionary<string, JsonObject>(StringComparer.Ordinal);
        foreach (var pack in sources) {
            string key = JsonData.Digest(new[] { plan, "public-contracts", pack.Key }); bool reused = cache.Get(key) is not null;
            var artifact = Compile(key, "Contracts_" + Generation.Symbol(pack.Key), pack.Value, bootstrap.Values.Select(a => a["reference"]!.ToString()));
            artifact["pack"] = pack.Key; realContracts[pack.Key] = artifact;
            if (reused) { Statistics.ReusedContracts.AddRange(contractGroups[pack.Key]); Statistics.ReusedContractPacks.Add(pack.Key); }
            else { Statistics.CompiledContracts.AddRange(contractGroups[pack.Key]); Statistics.CompiledContractPacks.Add(pack.Key); }
        }
        foreach (string pack in order) {
            var references = realContracts.Values.Select(a => a["reference"]!.ToString()).Concat(bootstrap.Where(p => p.Key != pack)
                .Select(p => (InformationContracts.GetValueOrDefault(p.Key) ?? p.Value)["reference"]!.ToString()));
            var artifact = Compile(JsonData.Digest(new[] { plan, "real-information", pack }), "Information_" + Generation.Symbol(pack),
                information[pack].Select(d => (d.Id, d.Source)).ToArray(), references);
            artifact["pack"] = pack; InformationContracts[pack] = artifact;
        }
        var support = new JsonObject(realContracts.Select(p => KeyValuePair.Create<string, JsonNode?>(p.Key, p.Value.DeepClone())));
        var types = new JsonObject(InformationContracts.OrderBy(p => p.Key, StringComparer.Ordinal).Select(p => KeyValuePair.Create<string, JsonNode?>(p.Key, p.Value.DeepClone())));
        foreach (var group in contractGroups)
            foreach (string id in group.Value) {
                var item = realContracts[group.Key].DeepClone().AsObject(); item["supportingContracts"] = support.DeepClone(); item["informationContracts"] = types.DeepClone(); Contracts[id] = item;
            }
    }
}
