using System.Text.Json.Nodes;

namespace Confectory.Core;

// Describes a caller-provided function handle. No provider selection, body
// loading, instance creation, invocation or conversion from declaration IDs.
internal static class RuntimeFunctionContracts
{
    public const string Profile = "function-interface-live-v1";
    internal static (JsonObject Contract, IReadOnlyList<string> Dependencies) Describe(Registry registry, SchemaField field)
    {
        var function = registry.Effective(registry.Get(field.Type, "function", field.Origin, field.Loc).Id);
        _ = BlueprintAsync.Read(function); _ = BlueprintExecutionBranches.Read(function);
        var types = new SortedDictionary<string, InformationStructs.Definition>(StringComparer.Ordinal);
        foreach (string type in InformationStructs.SignatureTypes(function.Signature!))
            foreach (var definition in InformationStructs.ResolveAll(registry, type, function.Id)) types[definition.ClrType] = definition;
        var dependencies = new SortedSet<string>(StringComparer.Ordinal);
        void Observe(string id) {
            if (!dependencies.Add(id)) return;
            var declaration = registry.Get(id);
            if (declaration.Parent is not null) Observe(declaration.Parent);
            foreach (var include in declaration.Includes) Observe(include.Id);
            foreach (string required in declaration.Requires.Keys) Observe(required);
            foreach (var choice in declaration.Defaults.Values) Observe(choice.Id);
            foreach (var member in declaration.Fields.Values.Where(p => p.Kind is "compound" or "reference" or "enum" or "function")) Observe(member.Type);
        }
        Observe(function.Id); foreach (var definition in types.Values) Observe(definition.Id);
        var contract = new JsonObject {
            ["profile"] = Profile, ["id"] = function.Id,
            ["clrType"] = Generation.ImportInterface(function)["global::".Length..],
            ["nativeType"] = Generation.Interface(function.Id)["global::".Length..],
            ["assembly"] = "Contracts_" + Generation.Symbol(PackPaths.Namespace(function.Id)),
            ["signature"] = FeatureBlueprint.SignatureDocument(function.Signature!),
            ["contractHash"] = JsonData.Digest(Generation.ContractSource(function)),
            ["types"] = new JsonArray(types.Values.Select(d => (JsonNode)new JsonObject {
                ["id"] = d.Id, ["clrType"] = d.ClrType, ["kind"] = d.Kind,
                ["assembly"] = "Information_" + Generation.Symbol(PackPaths.Namespace(d.Id)), ["shapeHash"] = d.ShapeHash
            }).ToArray())
        };
        if (BlueprintAsync.Has(function)) {
            var signature = function.Signature!;
            string execution = BlueprintExecutionBranches.Result(function.Id)["global::".Length..];
            var properties = new JsonArray(new JsonObject { ["name"] = BlueprintAsync.BranchName(signature), ["type"] = execution });
            if (signature.Return != "void") properties.Add(new JsonObject { ["name"] = BlueprintAsync.ReturnName(signature), ["type"] = signature.Return });
            foreach (var parameter in signature.Args.Where(p => p.IsOut)) properties.Add(new JsonObject { ["name"] = parameter.Name, ["type"] = parameter.Type });
            contract["asyncResult"] = new JsonObject {
                ["clrType"] = BlueprintAsync.Result(function)["global::".Length..], ["properties"] = properties,
                ["executionType"] = execution, ["members"] = BlueprintExecutionBranches.Enum(function)["members"]!.DeepClone(),
                ["async"] = BlueprintAsync.Read(function)
            };
        }
        return (contract, dependencies.ToArray());
    }
}
