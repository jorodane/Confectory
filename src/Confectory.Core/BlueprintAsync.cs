using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

namespace Confectory.Core;

// Async execution is an explicit contract. Neither imports nor an animation
// infer it, and ordinary IInvoke must never synchronously wait for its Task.
public static class BlueprintAsync
{
    public const string Metadata = "blueprintAsync";
    public const string Profile = "async-acyclic-switch-v1", Generator = "feature-blueprint-source-v15-async";
    public static bool Has(Element function) => function.Values.ContainsKey(Metadata);
    public static JsonObject? Read(Element function)
    {
        if (!function.Values.TryGetValue(Metadata, out var value)) return null;
        if (function.Kind != "function" || function.Parent is not null || function.Signature is not { } signature || signature.Args.Any(p => p.Mode is not (null or "out")))
            throw new ArgumentException("Explicit direct async contracts cannot take ref inputs; retain the source and change the input explicitly");
        if (value.Value.ValueKind != JsonValueKind.String || JsonNode.Parse(value.Value.GetString()!) is not JsonObject document || document.Count != 2 || document.Any(p => p.Key is not ("schema" or "completion")) || document["schema"]?.GetValue<int>() != 1 || document["completion"] is not JsonValue id || !id.TryGetValue<string>(out var completion) || completion.Length > 128 || completion == "none" || !Regex.IsMatch(completion, @"\A[A-Za-z_][A-Za-z_0-9.-]*\z"))
            throw new ArgumentException("Versioned async contract and stable completion ID required");
        if (BlueprintExecutionBranches.Read(function).Any(row => row!["id"]?.ToString() == completion || row["name"]?.ToString() == "완료 시"))
            throw new ArgumentException("Preserve result branches and distinguish them from async completion before conversion");
        return document.DeepClone().AsObject();
    }
    public static void Set(Element function, string completion)
    {
        var value = new MetadataValue(JsonSerializer.SerializeToElement(new JsonObject { ["schema"] = 1, ["completion"] = completion }.ToJsonString()), function.Id, new());
        var copy = JsonData.Clone(function); copy.Values[Metadata] = value; _ = Read(copy);
        function.Values[Metadata] = value;
    }
    static string Unique(string candidate, IEnumerable<string> used)
    {
        var names = used.ToHashSet(StringComparer.Ordinal); string result = candidate; int suffix = 2;
        while (names.Contains(result)) result = candidate + "_" + suffix++;
        return result;
    }
    public static string ResultName(FunctionSignature signature) => Unique("FunctionResult", signature.Args.Select(p => p.Name));
    public static string BranchName(FunctionSignature signature) => Unique("Branch", signature.Args.Where(p => p.IsOut).Select(p => p.Name));
    public static string ReturnName(FunctionSignature signature) => Unique("Return", signature.Args.Where(p => p.IsOut).Select(p => p.Name).Append(BranchName(signature)));
    public static string Interface(string id) => "global::Confectory.Contracts." + Generation.Symbol(id) + ".IAsyncInvoke";
    public static string Result(Element function) => "global::Confectory.Contracts." + Generation.Symbol(function.Id) + "." + ResultName(function.Signature!);
    public static string InputParameters(FunctionSignature signature) => string.Join(", ", signature.Args.Where(p => !p.IsOut).Select(p => p.Declaration()));
    public static string InputArguments(FunctionSignature signature) => string.Join(", ", signature.Args.Where(p => !p.IsOut).Select(p => p.Name));
    public static string Contract(Element function)
    {
        _ = Read(function) ?? throw new ArgumentException("Explicit async contract required");
        var signature = function.Signature!;
        string fields = string.Join("\n", signature.Args.Where(p => p.IsOut).Select(p => "public " + p.Type + " " + p.Name + " { get; set; } = default!;"));
        string native = signature.Return == "void" ? "" : "public " + signature.Return + " " + ReturnName(signature) + " { get; set; } = default!;\n";
        return "public sealed class " + ResultName(signature) + " {\npublic " + BlueprintExecutionBranches.Result(function.Id) + " " + BranchName(signature) + " { get; set; } = default!;\n" + native + fields + "\n}\npublic interface IAsyncInvoke : IInvoke { global::System.Threading.Tasks.Task<" + ResultName(signature) + "> InvokeAsync(" + InputParameters(signature) + "); }\n";
    }
}
