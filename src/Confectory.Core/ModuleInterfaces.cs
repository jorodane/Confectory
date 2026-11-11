using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

namespace Confectory.Core;

// A module's required function slots form an interface. Defaults stay
// provider-selection metadata; generating a type never selects or invokes one.
public static class ModuleInterfaces
{
    public const string Profile = "module-interface-basic-v1";
    public const string NominalProfile = "module-interface-nominal-v1";
    public const string FlowProfile = "module-interface-flow-v1";
    static readonly HashSet<string> Primitives = ["void", "bool", "int", "long", "float", "double", "string", "object"];
    public static string Member(string function) => "Call_" + Generation.Symbol(function);
    public static string AsyncMember(string function) => Member(function) + "Async";
    public static string ExecutionMember(string function) => Member(function) + "Execution";
    public static InformationStructs.Definition Generate(string id, Func<string, Element> effective)
        => Generate(id, effective, (type, source) => throw new BuildError("MODULE_CLR_SOURCE", "Observe the exact nominal module method type before generation: " + type, effective(source).Loc));
    internal static InformationStructs.Definition Generate(string id, Func<string, Element> effective, Func<string, string, InformationStructs.Definition> resolve)
    {
        var methods = new SortedDictionary<string, Element>(StringComparer.Ordinal); var visiting = new HashSet<string>(StringComparer.Ordinal); var done = new Dictionary<string, HashSet<string>>(StringComparer.Ordinal);
        HashSet<string> Read(string current) {
            if (done.TryGetValue(current, out var prior)) return prior;
            if (!visiting.Add(current)) throw new BuildError("MODULE_CYCLE", "Acyclic module inclusion required");
            var module = effective(current); if (module.Kind != "module") throw new BuildError("MODULE_CLR_KIND", "Module definition required", module.Loc);
            var selected = new HashSet<string>(StringComparer.Ordinal);
            foreach (var include in module.Includes) selected.UnionWith(Read(include.Id));
            foreach (var requirement in module.Requires) {
                var function = effective(requirement.Key);
                if (function.Kind != "function" || !requirement.Value.Signature.Matches(function.Signature)) throw new BuildError("CONTRACT_MISMATCH", "Module must preserve its required public function contract", requirement.Value.Loc);
                _ = BlueprintAsync.Read(function); _ = BlueprintExecutionBranches.Read(function);
                if (function.Signature!.Args.Select(a => a.Type).Append(function.Signature.Return).Any(type => !Primitives.Contains(InformationStructs.BaseType(type)) && !InformationStructs.IsType(type)))
                    throw new BuildError("MODULE_CLR_PROFILE", "A generated module method must retain a supported native contract type", function.Loc);
                methods[function.Id] = function; selected.Add(function.Id); if (methods.Count > 256) throw new BuildError("MODULE_CLR_BUDGET", "Module interface member budget", module.Loc);
            }
            foreach (var choice in module.Defaults) {
                if (!selected.Contains(choice.Key)) throw new BuildError("MODULE_CONTRACT", "A default must retain its module requirement", choice.Value.Loc);
                var implementation = effective(choice.Value.Id);
                if (implementation.Kind != "implementation" || implementation.Function != choice.Key || !methods[choice.Key].Signature!.Matches(implementation.Signature)) throw new BuildError("IMPLEMENTATION_ID", "A module default must implement the original required contract", choice.Value.Loc);
            }
            visiting.Remove(current); done[current] = selected; return selected;
        }
        Read(id);
        var dependencies = new SortedDictionary<string, InformationStructs.Dependency>(StringComparer.Ordinal);
        foreach (var method in methods.Values)
            foreach (string signatureType in InformationStructs.SignatureTypes(method.Signature!)) {
                var definition = resolve(signatureType, method.Id); dependencies[definition.ClrType] = new(definition.Id, definition.ClrType, definition.ShapeHash);
            }
        var publicContracts = methods.Values.Where(fn => BlueprintAsync.Has(fn) || BlueprintExecutionBranches.Has(fn)).Select(fn => fn.Id).ToArray();
        var inputs = dependencies.Values.OrderBy(d => d.Id, StringComparer.Ordinal).ThenBy(d => d.ClrType, StringComparer.Ordinal).ToArray(); string profile = publicContracts.Length > 0 ? FlowProfile : inputs.Length == 0 ? Profile : NominalProfile;
        var rows = new JsonArray(methods.Values.Select(fn => (JsonNode)new JsonObject { ["id"] = fn.Id, ["clrMember"] = Member(fn.Id), ["signature"] = FeatureBlueprint.SignatureDocument(fn.Signature!) }).ToArray());
        foreach (var row in rows.OfType<JsonObject>()) {
            var fn = methods[row["id"]!.ToString()];
            if (BlueprintAsync.Has(fn)) { row["asyncMember"] = AsyncMember(fn.Id); row["async"] = BlueprintAsync.Read(fn); }
            if (BlueprintExecutionBranches.Has(fn)) row["executionMember"] = ExecutionMember(fn.Id);
            if (publicContracts.Contains(fn.Id, StringComparer.Ordinal)) row["publicContractHash"] = JsonData.Digest(Generation.ContractSource(fn));
        }
        string hash = inputs.Length == 0 && publicContracts.Length == 0 ? JsonData.Digest(new { profile = Profile, id, methods = rows }) : JsonData.Digest(new { profile, id, methods = rows, dependencies = inputs });
        var code = new StringBuilder("// Generated module interface " + id + "; " + profile + "; " + hash + "\n#nullable disable\n");
        code.AppendLine("namespace Confectory.Information." + Generation.Symbol(PackPaths.Namespace(id)) + " {");
        code.AppendLine("public interface " + Generation.Symbol(id) + " {");
        foreach (var fn in methods.Values) {
            const string asyncError = "[global::System.Obsolete(\"Async function: explicitly convert the caller before invoking this contract\", true)]";
            if (BlueprintAsync.Has(fn)) code.AppendLine(asyncError);
            code.AppendLine(fn.Signature!.Return + " " + Member(fn.Id) + "(" + string.Join(", ", fn.Signature.Args.Select(a => a.Declaration())) + ");");
            if (BlueprintExecutionBranches.Has(fn)) {
                if (BlueprintAsync.Has(fn)) code.AppendLine(asyncError);
                var parameters = fn.Signature.Args.Select(a => a.Declaration()).ToList();
                if (fn.Signature.Return != "void") parameters.Add(BlueprintExecutionBranches.CaptureParameter(fn.Signature));
                code.AppendLine(BlueprintExecutionBranches.Result(fn.Id) + " " + ExecutionMember(fn.Id) + "(" + string.Join(", ", parameters) + ");");
            }
            if (BlueprintAsync.Has(fn)) code.AppendLine("global::System.Threading.Tasks.Task<" + BlueprintAsync.Result(fn) + "> " + AsyncMember(fn.Id) + "(" + BlueprintAsync.InputParameters(fn.Signature) + ");");
        }
        code.AppendLine("}\n}");
        return new(id, InformationStructs.Type(id), hash, [], code.ToString().Replace("\r\n", "\n", StringComparison.Ordinal), inputs, "module", profile, rows, publicContracts);
    }
}
