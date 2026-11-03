using System.Text;

namespace Confectory.Core;

public static partial class Generation
{
    public static string ImportInterface(Element function) => BlueprintAsync.Has(function) ? BlueprintAsync.Interface(function.Id) : Interface(function.Id);
    private static string RejectSynchronousEntry(Element function) => function.Signature!.Return + " " + Interface(function.Id) + ".Invoke(" + Parameters(function.Signature) + ") => throw new global::System.InvalidOperationException(\"Async function: explicitly convert the caller and await InvokeAsync.\");";
    private static string AsyncImplementationSource(Element e, Element feature, string body, string path, string members, IReadOnlySet<string>? asyncImports)
    {
        _ = BlueprintAsync.Read(feature);
        string imports = string.Join("\n", e.Imports.OrderBy(p => p.Key, StringComparer.Ordinal).Select(p => "        " + (asyncImports?.Contains(p.Value.Id) == true ? BlueprintAsync.Interface(p.Value.Id) : Interface(p.Value.Id)) + " " + p.Key + " { get; }"));
        string quoted = System.Text.Json.JsonSerializer.Serialize(path, JsonData.Options);
        return $$"""
            // Generated explicit async implementation boundary for {{e.Id}}; {{Abi}}
            using System;
            namespace Confectory.Implementations.{{Symbol(PackPaths.Namespace(e.Id))}}
            {
                public sealed class {{Symbol(e.Id)}} : {{BlueprintAsync.Interface(feature.Id)}}
                {
                    public interface IImports
                    {
            {{imports}}
                    }
                    private readonly IImports calls;
                    public {{Symbol(e.Id)}}(IImports calls) { this.calls = calls; }
                    {{RejectSynchronousEntry(feature)}}
                    #pragma warning disable CS1998
                    public async global::System.Threading.Tasks.Task<{{BlueprintAsync.Result(feature)}}> InvokeAsync({{BlueprintAsync.InputParameters(feature.Signature!)}})
                    {
            #line 1 {{quoted}}
            {{body}}
            #line default
                    }
                    #pragma warning restore CS1998
            {{members}}
                }
            }
            """ + "\n";
    }
    private static void AsyncBinding(StringBuilder lines, Element function, string name, string implementation)
    {
        lines.AppendLine("internal sealed class " + name + " : " + BlueprintAsync.Interface(function.Id)); lines.AppendLine("{");
        lines.AppendLine("    " + RejectSynchronousEntry(function));
        lines.AppendLine("    public global::System.Threading.Tasks.Task<" + BlueprintAsync.Result(function) + "> InvokeAsync(" + BlueprintAsync.InputParameters(function.Signature!) + ") => ((" + BlueprintAsync.Interface(function.Id) + ")new " + implementation + "(new " + name + "Imports())).InvokeAsync(" + BlueprintAsync.InputArguments(function.Signature!) + ");");
        lines.AppendLine("}");
    }
}
