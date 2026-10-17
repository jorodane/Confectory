using System.Text.Json.Nodes;
namespace Confectory.Core;
public static partial class FeatureBlueprint
{
    public const string AliasLocalsProfile="sync-acyclic-alias-locals-v1",AliasLocalsGenerator="feature-blueprint-source-v8";
    public static bool SupportsExternalRefs(string? profile)=>profile is ExternalRefsProfile or AliasLocalsProfile or NestedProfile or PropertyProfile or MethodsProfile or SwitchProfile;
    static void ValidateAliasLocals(Dictionary<string,JsonObject> locals,Element feature,Dictionary<string,Node> nodes)
    {
        foreach(var local in locals.Where(p=>p.Value["source"] is JsonObject)){
            var source=local.Value["source"]!.AsObject();Parameter? value;
            if(source.ContainsKey("input"))value=feature.Signature!.Args.SingleOrDefault(p=>!p.IsOut&&p.Name==S(source,"input"));
            else{Need(nodes.TryGetValue(S(source,"node"),out var node),"GRAPH_LOCAL_ALIAS_SOURCE",local.Key);value=FeatureOutputs(node!.Signature).SingleOrDefault(p=>p.Name==(source.ContainsKey("output")?S(source,"output"):"return"));}
            Need(value is not null,"GRAPH_LOCAL_ALIAS_SOURCE",local.Key);Need(value!.Type==S(local.Value,"type"),"GRAPH_LOCAL_ALIAS_TYPE",local.Key);
        }
    }
}
