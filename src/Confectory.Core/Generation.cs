using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

namespace Confectory.Core;

public static partial class Generation
{
    public const string Abi = "confectory-csharp-interface-v2-pack-assemblies";
    public static string Symbol(string id) => "E" + JsonData.Digest(id)[..24];
    public static string Interface(string id) => $"global::Confectory.Contracts.{Symbol(id)}.IInvoke";
    public static string Implementation(string id) => $"global::Confectory.Implementations.{Symbol(PackPaths.Namespace(id))}.{Symbol(id)}";
    private static string Parameters(FunctionSignature signature) => string.Join(", ", signature.Args.Select(a => a.Declaration()));
    private static string Arguments(FunctionSignature signature) => string.Join(", ", signature.Args.Select(a => (a.Mode is "out" or "ref" ? a.Mode+" " : "") + a.Name));
    public static string ContractSource(Element fn) {
        _ = BlueprintAsync.Read(fn);
        return $$"""
        // Generated public function contract for {{fn.Id}}; {{Abi}}
        namespace Confectory.Contracts.{{Symbol(fn.Id)}}
        {
            {{ExecutionContract(fn)}}{{(BlueprintAsync.Has(fn) ? "\n" + BlueprintAsync.Contract(fn) : "")}}
            public interface IInvoke
            {
                {{(BlueprintAsync.Has(fn) ? "[global::System.Obsolete(\"Async function: explicitly convert the caller and await InvokeAsync.\", true)]\n                " : "")}}{{fn.Signature!.Return}} Invoke({{Parameters(fn.Signature)}});
            }
        }
        """ + "\n";
    }

    private static string ExecutionParameters(FunctionSignature signature) => string.Join(", ",new[]{Parameters(signature),BlueprintExecutionBranches.CaptureParameter(signature)}.Where(s=>s.Length>0));
    private static string ExecutionArguments(FunctionSignature signature, string? capture=null) => string.Join(", ",new[]{Arguments(signature),signature.Return=="void"?"":"out "+(capture??BlueprintExecutionBranches.CaptureName(signature))}.Where(s=>s.Length>0));
    private static string ExecutionContract(Element fn)
    {
        var branches = BlueprintExecutionBranches.Read(fn);
        if (!BlueprintExecutionBranches.Has(fn) && !BlueprintAsync.Has(fn)) return "";
        string result = "public enum ExecutionResult : int { None = 0, " + string.Join(", ", branches.Select(b => BlueprintExecutionBranches.Member(b!["id"]!.GetValue<string>()) + " = " + b["value"])) + " }\n";
        if (BlueprintExecutionBranches.Has(fn)) result += "public interface IExecutionInvoke : IInvoke { " + (BlueprintAsync.Has(fn) ? "[global::System.Obsolete(\"Async function: explicitly convert the caller and await InvokeAsync.\", true)] " : "") + "ExecutionResult InvokeExecution(" + ExecutionParameters(fn.Signature!) + "); }";
        return result;
    }

    public static string ImplementationSource(Element e, string body, string path, string members = "", FunctionSignature? entry = null, Element? feature = null, IReadOnlySet<string>? asyncImports = null)
    {
        if (feature is not null && BlueprintAsync.Has(feature)) return AsyncImplementationSource(e, feature, body, path, members, asyncImports);
        bool execution = feature is not null && BlueprintExecutionBranches.Has(feature);
        string captured=BlueprintExecutionBranches.CaptureName(e.Signature!);
        // A lifted whole-body retains its public native Invoke for this/recursion.
        // The graph entry uses the same explicit IInvoke boundary as sync M11.
        string ordinary=execution?(entry is null?"public ":"")+e.Signature!.Return+" "+(entry is null?"":Interface(e.Function!)+".")+"Invoke("+Parameters(e.Signature)+") { _ = (("+BlueprintExecutionBranches.Interface(e.Function!)+")this).InvokeExecution("+ExecutionArguments(e.Signature,e.Signature.Return=="void"?null:e.Signature.Return+" "+captured)+"); "+(e.Signature.Return=="void"?"":"return "+captured+";")+" }\n":"";
        string executionAdapter = execution ? ordinary+BlueprintExecutionBranches.Result(e.Function!)+" "+BlueprintExecutionBranches.Interface(e.Function!)+".InvokeExecution("+ExecutionParameters(e.Signature!)+") { return ("+BlueprintExecutionBranches.Result(e.Function!)+")this.ExecuteBranches("+ExecutionArguments(e.Signature!)+"); }" : "";
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
                    {{(execution ? "private int ExecuteBranches" : (entry is null ? "public " : "") + e.Signature!.Return + " " + (entry is null ? "" : Interface(e.Function!) + ".") + "Invoke")}}({{(execution ? ExecutionParameters(entry ?? e.Signature!) : Parameters(entry ?? e.Signature!))}})
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
            if (BlueprintAsync.Has(fn)) AsyncBinding(lines, fn, name, impl);
            else {
            lines.AppendLine($"internal sealed class {name} : {(execution ? BlueprintExecutionBranches.Interface(fn.Id) : Interface(fn.Id))}"); lines.AppendLine("{");
            lines.AppendLine($"    public {sig.Return} Invoke({Parameters(sig)})"); lines.AppendLine("    {");
            lines.AppendLine($"        {prefix}(({Interface(fn.Id)})new {impl}(new {name}Imports())).Invoke({Arguments(sig)});");
            lines.AppendLine("    }");
            if (execution) lines.AppendLine($"    public {BlueprintExecutionBranches.Result(fn.Id)} InvokeExecution({ExecutionParameters(sig)}) => (({BlueprintExecutionBranches.Interface(fn.Id)})new {impl}(new {name}Imports())).InvokeExecution({ExecutionArguments(sig)});");
            lines.AppendLine("}");
            }
            lines.AppendLine($"internal sealed class {name}Imports : {impl}.IImports"); lines.AppendLine("{");
            foreach (var (alias, imported) in node.Imports.OrderBy(x => x.Key, StringComparer.Ordinal))
                lines.AppendLine($"    public {(BlueprintAsync.Has(fn) ? ImportInterface(plan.Registry.Get(imported[1], "function")) : Interface(imported[1]))} {alias} => new {BindingSymbol(new(imported[0], imported[1]))}();");
            lines.AppendLine("}");
        }
        string entry = plan.Registry.Project.Entry!;
        string invocation = $"new {BindingSymbol(new(entry, entry))}().Invoke()";
        lines.AppendLine("internal static class Program"); lines.AppendLine("{"); var entryFunction = plan.Registry.Get(entry);
        if (BlueprintAsync.Has(entryFunction)) {
            lines.AppendLine("    public static async global::System.Threading.Tasks.Task<int> Main()"); lines.AppendLine("    {");
            lines.AppendLine("        var result = await new " + BindingSymbol(new(entry, entry)) + "().InvokeAsync();");
            lines.AppendLine(entryFunction.Signature!.Return == "int" ? "        return result." + BlueprintAsync.ReturnName(entryFunction.Signature) + ";" : "        return 0;");
        } else {
            lines.AppendLine("    public static int Main()"); lines.AppendLine("    {");
            lines.AppendLine(entryFunction.Signature!.Return == "int" ? $"        return {invocation};" : $"        {invocation}; return 0;");
        }
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
