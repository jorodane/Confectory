using System.Text.Json;
using System.Text.Json.Nodes;

namespace Confectory.Core;

public static partial class FeatureBlueprint
{
    static bool AsyncNode(Node node) => node.Definition["async"]?.GetValue<bool>() == true;
    static string AsyncResultExpression(Element feature, string branch, string? native, Func<Parameter, string> output)
    {
        var signature = feature.Signature!;
        var assignments = new List<string> { BlueprintAsync.BranchName(signature) + " = (" + BlueprintExecutionBranches.Result(feature.Id) + ")(" + branch + ")" };
        if (signature.Return != "void") assignments.Add(BlueprintAsync.ReturnName(signature) + " = " + (native ?? "default(" + signature.Return + ")!"));
        assignments.AddRange(signature.Args.Where(p => p.IsOut).Select(p => p.Name + " = " + output(p)));
        return "new " + BlueprintAsync.Result(feature) + " { " + string.Join(", ", assignments) + " }";
    }
    static string AsyncMethodsMember(string type, Node node, string imports, string importArguments, string source, string helpers, string marker)
    {
        Need(!HasContext(node) && node.Control is "next" or "switch" && node.Signature.Args.All(p => p.Mode is null or "out"), "GRAPH_ASYNC_NODE_CONTRACT", node.Id);
        string storage = "__fg_async_storage_" + Hash(node.Id + source + helpers)[..24];
        string outputs = string.Join("\n", node.Signature.Args.Where(p => p.IsOut).Select(p => "public " + p.Type + " " + p.Name + " = default!;"));
        string inputs = string.Join(", ", node.Signature.Args.Where(p => !p.IsOut).Select(p => p.Declaration()));
        string args = string.Join(", ", node.Signature.Args.Where(p => !p.IsOut).Select(p => p.Name));
        string userType = node.Control == "switch" ? "Result" : node.Signature.Return;
        string task = "global::System.Threading.Tasks.Task" + (userType == "void" ? "" : "<" + userType + ">");
        string suffix = imports.Length == 0 ? "" : (inputs.Length == 0 ? "" : ", ") + imports;
        string callArgs = string.Join(", ", new[] { args, storage, importArguments }.Where(s => s.Length > 0));
        string parameters = string.Join(", ", new[] { inputs, "__fg_async_outputs " + storage, imports }.Where(s => s.Length > 0));
        string initialize = string.Join("\n", node.Signature.Args.Where(p => p.IsOut).Select(p => p.Type + " " + p.Name + " = default!;"));
        string capture = string.Join("\n", node.Signature.Args.Where(p => p.IsOut).Select(p => storage + "." + p.Name + " = " + p.Name + ";"));
        var values = node.Signature.Args.Where(p => p.IsOut).Select(p => p.Name + " = " + storage + "." + p.Name).ToList();
        values.Insert(0, BlueprintAsync.BranchName(node.Signature) + " = " + (node.Control == "switch" ? "(int)__fg_async_native" : "0"));
        if (node.Signature.Return != "void") values.Add(BlueprintAsync.ReturnName(node.Signature) + " = __fg_async_native");
        string native = userType == "void" ? "" : "var __fg_async_native = ";
        string nativeField = node.Signature.Return == "void" ? "" : "public " + node.Signature.Return + " " + BlueprintAsync.ReturnName(node.Signature) + " = default!;\n";
        return "private static class " + type + " {\n" + EnumDeclaration(node) +
            "private sealed class __fg_async_outputs {\n" + outputs + "\n}\npublic sealed class __fg_async_result { public int " + BlueprintAsync.BranchName(node.Signature) + ";\n" + nativeField + outputs + "\n}\n" +
            "#pragma warning disable CS1998\npublic static async global::System.Threading.Tasks.Task<__fg_async_result> InvokeAsync(" + inputs + suffix + ") { var " + storage + " = new __fg_async_outputs(); " + native + "await Execute(" + callArgs + "); return new __fg_async_result { " + string.Join(", ", values) + " }; }\n" +
            // Keep Execute and the original source marker for CallerMemberName
            // and CallerFilePath. No return statement in the source is rewritten.
            "private static async " + task + " Execute(" + parameters + ") {\n" + initialize + "\ntry {\n#line 1 " + JsonSerializer.Serialize(marker) + "\n" + source + "\n#line default\n} finally {\n" + capture + "\n} }\n#line 1 " + JsonSerializer.Serialize(marker + "/helpers") + "\n" + helpers + "\n#line default\n#pragma warning restore CS1998\n}\n";
    }
}
