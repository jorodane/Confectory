using System.Text.Json;
using System.Text.Json.Nodes;

namespace Confectory.Core;

public static partial class FeatureBlueprint
{
    static bool CompletionAdapter(Node node)=>node.Definition[BlueprintCompletionAdapter.Metadata] is not null;
    static string WrappedCapture(Node node)=>CompletionAdapter(node)||BlueprintPrivateCompletion.OwnsResults(node.Definition)?BlueprintExecutionBranches.CaptureName(node.Signature):"__fg_wrapped_return";
    static string CompletionSelector(string type,Node node,string marker)
    {
        var context=BlueprintCompletionAdapter.Context(node.Signature);var fields=context["fields"]!.AsArray();
        string parameters=string.Join(", ",fields.Select((p,i)=>p!["type"]+" value"+i));
        return "private static class "+type+" {\n"+BlueprintCompletionAdapter.EnumSource(node.Definition)+context["source"]+"public static int Select("+parameters+") => (int)After(new SourceContext("+string.Join(", ",fields.Select((_,i)=>"value"+i))+"));\nprivate static Result After(SourceContext context) {\n#line 1 "+JsonSerializer.Serialize(marker+"/completion")+"\n"+node.Definition[BlueprintCompletionAdapter.Metadata]!["source"]+"\n#line default\n}\n}\n";
    }
    static string CompletionSyncMember(string type,Node node,string imports,string importArguments,string symbol)
    {
        string declarations=string.Join(",",node.Signature.Args.Select(p=>p.Declaration()).Concat(WrappedReturn(node)?new[]{"out "+node.Signature.Return+" "+WrappedCapture(node)}:Array.Empty<string>()).Concat(imports.Length==0?Array.Empty<string>():new[]{imports}));
        string arguments=string.Join(",",node.Signature.Args.Select(p=>(p.IsOut?"out ":"")+p.Name).Concat(importArguments.Length==0?Array.Empty<string>():new[]{importArguments}));
        string values=string.Join(",",node.Signature.Args.Select(p=>p.Name).Concat(WrappedReturn(node)?new[]{WrappedCapture(node)}:Array.Empty<string>()));
        return "static int "+symbol+"("+declarations+") {\n"+(WrappedReturn(node)?WrappedCapture(node)+" = ":"")+type+".Execute("+arguments+");\nreturn "+type+"_completion.Select("+values+");\n}\n";
    }
}
