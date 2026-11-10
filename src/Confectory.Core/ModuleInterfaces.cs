using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

namespace Confectory.Core;

// A module's required ordinary function slots form an interface. Defaults stay
// provider-selection metadata; generating a type never selects or invokes one.
public static class ModuleInterfaces
{
    public const string Profile = "module-interface-basic-v1";
    public const string NominalProfile = "module-interface-nominal-v1";
    static readonly HashSet<string> Primitives = ["void", "bool", "int", "long", "float", "double", "string", "object"];
    public static string Member(string function) => "Call_" + Generation.Symbol(function);
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
                if (BlueprintAsync.Has(function) || BlueprintExecutionBranches.Has(function) || function.Signature!.Args.Select(a => a.Type).Append(function.Signature.Return).Any(type => !Primitives.Contains(InformationStructs.BaseType(type)) && !InformationStructs.IsType(type)))
                    throw new BuildError("MODULE_CLR_PROFILE", "This module interface profile requires ordinary synchronous native contracts; original async/execution contracts retained", function.Loc);
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
                var definition = resolve(signatureType, method.Id); dependencies[definition.Id] = new(definition.Id, definition.ClrType, definition.ShapeHash);
            }
        var inputs = dependencies.Values.ToArray(); string profile = inputs.Length == 0 ? Profile : NominalProfile;
        var rows = new JsonArray(methods.Values.Select(fn => (JsonNode)new JsonObject { ["id"] = fn.Id, ["clrMember"] = Member(fn.Id), ["signature"] = FeatureBlueprint.SignatureDocument(fn.Signature!) }).ToArray());
        string hash = inputs.Length == 0 ? JsonData.Digest(new { profile = Profile, id, methods = rows }) : JsonData.Digest(new { profile, id, methods = rows, dependencies = inputs });
        var code = new StringBuilder("// Generated module interface " + id + "; " + profile + "; " + hash + "\n#nullable disable\n");
        code.AppendLine("namespace Confectory.Information." + Generation.Symbol(PackPaths.Namespace(id)) + " {");
        code.AppendLine("public interface " + Generation.Symbol(id) + " {");
        foreach (var fn in methods.Values) code.AppendLine(fn.Signature!.Return + " " + Member(fn.Id) + "(" + string.Join(", ", fn.Signature.Args.Select(a => a.Declaration())) + ");");
        code.AppendLine("}\n}");
        return new(id, InformationStructs.Type(id), hash, [], code.ToString().Replace("\r\n", "\n", StringComparison.Ordinal), inputs, "module", profile, rows);
    }
}
