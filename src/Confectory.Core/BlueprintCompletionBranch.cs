using System.Text.Json.Nodes;

namespace Confectory.Core;

// A demoted completion keeps its authored "completion" wire. The local enum
// member represents its ordinary result; it does not rewrite the C# body.
public static class BlueprintCompletionBranch
{
    public const string Metadata = "completionBranch";
    static string S(JsonNode node,string key) => node[key]?.GetValue<string>() ?? throw new ArgumentException("Missing completion branch " + key);
    static JsonObject Enum(JsonObject node) => node["executionEnum"]?.AsObject() ?? throw new ArgumentException("Existing Result contract required for completion demotion");
    static JsonObject Member(JsonObject marker) => new() { ["id"]=marker["id"]!.DeepClone(),["name"]=marker["name"]!.DeepClone(),["value"]=marker["value"]!.DeepClone() };
    public static JsonObject? Read(JsonObject node)
    {
        if(node[Metadata] is null)return null;
        if(node[Metadata] is not JsonObject marker||marker.Count!=4||marker.Any(p=>p.Key is not ("id" or "name" or "value" or "label")))throw new ArgumentException("Exact completion branch identity required");
        string label=S(marker,"label");if(label.Length is <1 or >128||label!=label.Trim()||label.Any(char.IsControl))throw new ArgumentException("Completion display name required");
        _=BlueprintEnumContract.Validate(new(){["schema"]=1,["kind"]="execution-enum-proposal",["sourceId"]="completion",["definitionHash"]=new string('0',64),["sourceHash"]=new string('0',64),["primary"]=S(marker,"id"),["members"]=new JsonArray(Member(marker))});
        return marker.DeepClone().AsObject();
    }
    public static JsonObject Preview(JsonObject node,string identity)
    {
        if(node["kind"]?.ToString()!="code"||node["control"]?.ToString()!="switch"||node["signature"]?["return"]?.ToString()!="void"||node["implementationContext"] is not null||node["forwardCallerStorage"]?.GetValue<bool>()==true)throw new ArgumentException("This original body needs its output-preserving completion adapter before sync conversion");
        if(Read(node) is JsonObject existing)return existing;
        var rows=Enum(node)["members"]!.AsArray();if(rows.Count>=32)throw new ArgumentException("Keep room for the retained completion branch in the Result contract");
        string prefix="completed_"+JsonData.Digest(identity)[..20],id=prefix,name="완료_시";int suffix=2;
        while(rows.Any(r=>r!["id"]?.ToString()==id))id=prefix+"_"+suffix++;
        suffix=2;while(rows.Any(r=>r!["name"]?.ToString().TrimStart('@')==name))name="완료_시_"+suffix++;
        int value=1;while(rows.Any(r=>r!["value"]!.GetValue<int>()==value))value++;
        return new(){["id"]=id,["name"]=name,["value"]=value,["label"]="완료 시"};
    }
    public static void Set(JsonObject node,bool enabled,string identity)
    {
        var marker=Read(node);
        if(enabled) {
            if(marker is not null){Validate(node,false);var rows=Enum(node)["members"]!.AsArray();rows.Remove(rows.Single(r=>r!["id"]!.ToString()==S(marker,"id")));}
            node["async"]=true;
        } else {
            if(marker is null&&node["async"]?.GetValue<bool>()!=true)return;
            marker??=Preview(node,identity);var rows=Enum(node)["members"]!.AsArray();if(!rows.Any(r=>r!["id"]?.ToString()==S(marker,"id")))rows.Insert(rows[0]?["id"]?.ToString()==Enum(node)["primary"]?.ToString()?1:0,Member(marker));
            node[Metadata]=marker;node.Remove("async");
        }
    }
    public static void Validate(JsonObject node,bool asynchronous)
    {
        var marker=Read(node);if(marker is null)return;
        if(node["kind"]?.ToString()!="code"||node["control"]?.ToString()!="switch"||node["signature"]?["return"]?.ToString()!="void"||node["implementationContext"] is not null||node["forwardCallerStorage"]?.GetValue<bool>()==true)throw new ArgumentException("Ordinary owned Result completion branch required");
        var execution=Enum(node);if(execution["primary"]?.ToString()==S(marker,"id"))throw new ArgumentException("Completion cannot replace the original primary result");
        var rows=execution["members"]!.AsArray();var member=rows.SingleOrDefault(r=>r!["id"]?.ToString()==S(marker,"id"));
        if(asynchronous ? member is not null||rows.Any(r=>r!["name"]!.ToString().TrimStart('@')==S(marker,"name").TrimStart('@')||r["value"]!.GetValue<int>()==marker["value"]!.GetValue<int>()) : member is null||!JsonNode.DeepEquals(member,Member(marker)))throw new ArgumentException("Retain the exact completion member identity and reserved Result name/value");
    }
    public static void Edit(JsonObject node,JsonArray edges,string? label=null)
    {
        var marker=Read(node);if(marker is null){if(label is not null)throw new ArgumentException("No observed completion display name");return;}
        if(node["async"]?.GetValue<bool>()==true){if(label is not null&&label!=S(marker,"label"))throw new ArgumentException("Implicit completion name is fixed");Validate(node,true);return;}
        var member=Enum(node)["members"]!.AsArray().SingleOrDefault(r=>r!["id"]?.ToString()==S(marker,"id"));
        if(member is null){if(edges.Any(e=>e!["from"]?.ToString()==node["id"]?.ToString()&&e["port"]?.ToString()=="completion"))throw new ArgumentException("Disconnect the retained completion branch explicitly before removing it");node.Remove(Metadata);return;}
        marker["label"]=label??(member["name"]!.ToString()==S(marker,"name")?S(marker,"label"):member["name"]!.ToString());marker["name"]=member["name"]!.DeepClone();marker["value"]=member["value"]!.DeepClone();node[Metadata]=marker;Validate(node,false);
    }
}
