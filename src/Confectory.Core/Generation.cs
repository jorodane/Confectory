using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

namespace Confectory.Core;

public static class Generation
{
    public const string Abi = "confectory-csharp-interface-v2-pack-assemblies";
    public static string Symbol(string id) => "E" + JsonData.Digest(id)[..24];
    public static string Interface(string id) => $"global::Confectory.Contracts.{Symbol(id)}.IInvoke";
    public static string Implementation(string id) => $"global::Confectory.Implementations.{Symbol(PackPaths.Namespace(id))}.{Symbol(id)}";
    private static string Parameters(FunctionSignature signature) => string.Join(", ", signature.Args.Select(a => a.Declaration()));
    private static string Arguments(FunctionSignature signature) => string.Join(", ", signature.Args.Select(a => (a.Mode is "out" or "ref" ? a.Mode+" " : "") + a.Name));
    public static string ContractSource(Element fn) => $$"""
        // Generated public function contract for {{fn.Id}}; {{Abi}}
        namespace Confectory.Contracts.{{Symbol(fn.Id)}}
        {
            {{ExecutionContract(fn)}}
            public interface IInvoke
            {
                {{fn.Signature!.Return}} Invoke({{Parameters(fn.Signature)}});
            }
        }
        """ + "\n";

    private static string ExecutionContract(Element fn)
    {
        var branches = BlueprintExecutionBranches.Read(fn);
        return !BlueprintExecutionBranches.Has(fn) ? "" : "public enum ExecutionResult : int { None = 0, " + string.Join(", ", branches.Select(b => BlueprintExecutionBranches.Member(b!["id"]!.GetValue<string>()) + " = " + b["value"])) + " }\npublic interface IExecutionInvoke : IInvoke { ExecutionResult InvokeExecution(" + Parameters(fn.Signature!) + "); }";
    }

    public static string ImplementationSource(Element e, string body, string path, string members = "", FunctionSignature? entry = null, Element? feature = null)
    {
        bool execution = feature is not null && BlueprintExecutionBranches.Has(feature);
        string executionAdapter = execution ? "public void Invoke(" + Parameters(e.Signature!) + ") { _ = ((" + BlueprintExecutionBranches.Interface(e.Function!) + ")this).InvokeExecution(" + Arguments(e.Signature!) + "); }\n" + BlueprintExecutionBranches.Result(e.Function!) + " " + BlueprintExecutionBranches.Interface(e.Function!) + ".InvokeExecution(" + Parameters(e.Signature!) + ") { return (" + BlueprintExecutionBranches.Result(e.Function!) + ")this.ExecuteBranches(" + Arguments(e.Signature!) + "); }" : "";
        string imports = string.Join("\n", e.Imports.OrderBy(x => x.Key, StringComparer.Ordinal).Select(x => $"        {Interface(x.Value.Id)} {x.Key} {{ get; }}"));
        string quotedPath = JsonSerializer.Serialize(path, JsonData.Options);
        return $$"""
            // Generated implementation boundary for {{e.Id}}; {{Abi}}
            using System;
            namespace Confectory.Implementations.{{Symbol(PackPaths.Namespace(e.Id))}}
            {
                public sealed class {{Symbol(e.Id)}} : {{(execution ? BlueprintExecutionBranches.Interface(e.Function!) : Interface(e.Function!))}}
                {
                    public interface IImports
                    {
            {{imports}}
                    }
                    private readonly IImports calls;
                    public {{Symbol(e.Id)}}(IImports calls) { this.calls = calls; }
                    {{executionAdapter}}
                    {{(execution ? "private int ExecuteBranches" : (entry is null ? "public " : "") + e.Signature!.Return + " " + (entry is null ? "" : Interface(e.Function!) + ".") + "Invoke")}}({{Parameters(entry ?? e.Signature!)}})
                    {
            #line 1 {{quotedPath}}
            {{body}}
            #line default
                    }
            {{members}}
                }
            }
            """ + "\n";
    }
    public static string BindingSymbol(BindingKey key) => "B" + JsonData.Digest(new[] { key.Owner, key.Function })[..24];
    public static string FinalSource(Planner plan)
    {
        var lines = new StringBuilder($"// Generated actual provider connections; {Abi}\n");
        foreach (var (key, node) in plan.Bindings.OrderBy(x => x.Key.Owner, StringComparer.Ordinal).ThenBy(x => x.Key.Function, StringComparer.Ordinal))
        {
            var fn = plan.Registry.Get(node.Function, "function"); var sig = fn.Signature!;
            string name = BindingSymbol(key), impl = Implementation(node.Implementation), prefix = sig.Return == "void" ? "" : "return ";
            bool execution = BlueprintExecutionBranches.Has(fn);
            lines.AppendLine($"internal sealed class {name} : {(execution ? BlueprintExecutionBranches.Interface(fn.Id) : Interface(fn.Id))}"); lines.AppendLine("{");
            lines.AppendLine($"    public {sig.Return} Invoke({Parameters(sig)})"); lines.AppendLine("    {");
            lines.AppendLine($"        {prefix}(({Interface(fn.Id)})new {impl}(new {name}Imports())).Invoke({Arguments(sig)});");
            lines.AppendLine("    }");
            if (execution) lines.AppendLine($"    public {BlueprintExecutionBranches.Result(fn.Id)} InvokeExecution({Parameters(sig)}) => (({BlueprintExecutionBranches.Interface(fn.Id)})new {impl}(new {name}Imports())).InvokeExecution({Arguments(sig)});");
            lines.AppendLine("}");
            lines.AppendLine($"internal sealed class {name}Imports : {impl}.IImports"); lines.AppendLine("{");
            foreach (var (alias, imported) in node.Imports.OrderBy(x => x.Key, StringComparer.Ordinal))
                lines.AppendLine($"    public {Interface(imported[1])} {alias} => new {BindingSymbol(new(imported[0], imported[1]))}();");
            lines.AppendLine("}");
        }
        string entry = plan.Registry.Project.Entry!;
        string invocation = $"new {BindingSymbol(new(entry, entry))}().Invoke()";
        lines.AppendLine("internal static class Program"); lines.AppendLine("{"); lines.AppendLine("    public static int Main()"); lines.AppendLine("    {");
        lines.AppendLine(plan.Registry.Get(entry).Signature!.Return == "int" ? $"        return {invocation};" : $"        {invocation}; return 0;");
        lines.AppendLine("    }"); lines.AppendLine("}");
        return lines.ToString().Replace("\r\n", "\n", StringComparison.Ordinal);
    }
    private static object PublicDatum(SchemaDatum datum) => new
    {
        kind = datum.Kind, scalar = datum.Scalar, reference = datum.Reference, origin = datum.Origin,
        items = datum.Items?.Select(PublicDatum).ToArray(),
        members = datum.Members?.ToDictionary(p => p.Key, p => PublicDatum(p.Value), StringComparer.Ordinal)
    };

    public static JsonObject PublicCatalog(Planner plan, Dictionary<string, JsonObject> packs, Dictionary<string, JsonObject> contracts, string target)
    {
        List<JsonObject> elements = [];
        foreach (string id in plan.Reached.Order(StringComparer.Ordinal))
        {
            var e = plan.Registry.Effective(id);
            var item = JsonData.Object(new { id, kind = e.Kind, parent = e.Parent, description = e.Description });
            if (e.Signature is not null) item["contract"] = JsonSerializer.SerializeToNode(e.Signature, JsonData.Options);
            if (e.Values.Count > 0) item["metadataValues"] = JsonSerializer.SerializeToNode(e.Values.ToDictionary(x => x.Key, x => new { value = x.Value.Value, origin = x.Value.Origin }), JsonData.Options);
            if (e.Fields.Count > 0) item["schemaFields"] = JsonSerializer.SerializeToNode(e.Fields.ToDictionary(p => p.Key, p => new { cardinality = p.Value.Cardinality, kind = p.Value.Kind, type = p.Value.Type, origin = p.Value.Origin }), JsonData.Options);
            if (e.Data.Count > 0) item["typedData"] = JsonSerializer.SerializeToNode(e.Data.ToDictionary(p => p.Key, p => PublicDatum(p.Value)), JsonData.Options);
            elements.Add(item);
        }
        return JsonData.Object(new
        {
            formatVersion = 1, abi = Abi, surface = "linked-elements", project = plan.Registry.Project.Namespace, entry = plan.Registry.Project.Entry, target,
            packs = plan.Reached.Select(PackPaths.Namespace).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal).Select(ns => new { @namespace = ns, version = plan.Registry.Packs[ns].Version }).ToArray(),
            elements,
            functions = contracts.Keys.Order(StringComparer.Ordinal).Select(id => new { id, contract = plan.Registry.Get(id).Signature, interfaceType = Interface(id)["global::".Length..], executionBranches = BlueprintExecutionBranches.Read(plan.Registry.Get(id)), executionInterfaceType = BlueprintExecutionBranches.Has(plan.Registry.Get(id)) ? BlueprintExecutionBranches.Interface(id)["global::".Length..] : null, assembly = Path.GetFileName(contracts[id]["assembly"]!.GetValue<string>()) }).ToArray(),
            implementations = plan.Implementations.OrderBy(x => x.Key, StringComparer.Ordinal).Select(x => new { id = x.Key, function = x.Value.Function, implementationType = Implementation(x.Key)["global::".Length..], assembly = Path.GetFileName(packs[PackPaths.Namespace(x.Key)]["implementationArtifacts"]![x.Key]!["assembly"]!.GetValue<string>()), bodySelection = x.Value.Bodies.ContainsKey(target) ? target : "common", sourceKind = (x.Value.Bodies.GetValueOrDefault(target) ?? x.Value.Bodies.GetValueOrDefault("common"))?.SourceKind }).ToArray(),
            bindings = plan.Bindings.Values.ToArray(), coreProvidesRuntimeModLoader = false
        });
    }
}
