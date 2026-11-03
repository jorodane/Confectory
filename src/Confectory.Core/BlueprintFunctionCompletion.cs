using System.Text.Json;
using System.Text.Json.Nodes;
namespace Confectory.Core;

// The former public completion remains a nominal public result, independently
// of the original C# return/out data. Calls retain their literal completion wire.
public static class BlueprintFunctionCompletion
{
    public const string Metadata="blueprintFunctionCompletion";
    public static JsonObject? Read(Element fn)
    {
        if(!fn.Values.TryGetValue(Metadata,out var value))return null;
        if(fn.Kind!="function"||fn.Parent is not null||value.Value.ValueKind!=JsonValueKind.String||JsonNode.Parse(value.Value.GetString()!) is not JsonObject marker||marker.Count!=3||marker.Any(p=>p.Key is not ("id" or "name" or "value")))throw new ArgumentException("Exact owned public completion identity required");
        var copy=JsonData.Clone(fn);copy.Values.Remove(BlueprintAsync.Metadata);BlueprintExecutionBranches.Set(copy,new JsonArray(marker.DeepClone()));
        var row=BlueprintExecutionBranches.Read(fn).SingleOrDefault(r=>r!["id"]!.ToString()==marker["id"]!.ToString());
        if(BlueprintAsync.Has(fn)?BlueprintExecutionBranches.Read(fn).Any(r=>r!["id"]!.ToString()==marker["id"]!.ToString()||r["name"]!.ToString()==marker["name"]!.ToString()||r["value"]!.GetValue<int>()==marker["value"]!.GetValue<int>()):row is null||!JsonNode.DeepEquals(row,marker))throw new ArgumentException("Retain the public completion member and its reserved identity");
        return marker.DeepClone().AsObject();
    }
    static void Store(Element fn,JsonObject marker)=>fn.Values[Metadata]=new(JsonSerializer.SerializeToElement(marker.ToJsonString()),fn.Id,new());
    public static JsonObject Preview(Element fn)
    {
        if(Read(fn) is JsonObject prior)return prior;
        string id=BlueprintAsync.Read(fn)?["completion"]?.ToString()??"async_complete_"+JsonData.Digest(fn.Id)[..16];var rows=BlueprintExecutionBranches.Read(fn);if(rows.Count>=31)throw new ArgumentException("Room for the retained public completion required");
        int value=1;while(rows.Any(r=>r!["value"]!.GetValue<int>()==value))value++;
        return new(){["id"]=id,["name"]="완료 시",["value"]=value};
    }
    public static void Demote(Element fn)
    {
        var marker=Preview(fn);var rows=BlueprintExecutionBranches.Read(fn);fn.Values.Remove(BlueprintAsync.Metadata);if(!rows.Any(r=>r!["id"]!.ToString()==marker["id"]!.ToString()))rows.Insert(0,marker.DeepClone());BlueprintExecutionBranches.Set(fn,rows);Store(fn,marker);_=Read(fn);
    }
    public static string? Promote(Element fn)
    {
        var marker=Read(fn);if(marker is null)return null;if(BlueprintAsync.Has(fn))return marker["id"]!.ToString();
        var rows=BlueprintExecutionBranches.Read(fn);rows.Remove(rows.Single(r=>r!["id"]!.ToString()==marker["id"]!.ToString()));BlueprintExecutionBranches.Set(fn,rows);return marker["id"]!.ToString();
    }
    public static JsonObject NodeMarker(Element fn)
    {
        var marker=Read(fn)??throw new ArgumentException("Observed public completion required");return new(){["id"]=marker["id"]!.DeepClone(),["name"]=BlueprintExecutionBranches.Member(marker["id"]!.ToString()),["value"]=marker["value"]!.DeepClone(),["label"]=marker["name"]!.DeepClone()};
    }
    // M12 edits may rename/remove this ordinary public branch only through its
    // existing explicit caller/return transaction. Reconcile its retained ID.
    public static void Reconcile(Element fn)
    {
        if(!fn.Values.TryGetValue(Metadata,out var value)||BlueprintAsync.Has(fn))return;
        var marker=JsonNode.Parse(value.Value.GetString()!)!;var row=BlueprintExecutionBranches.Read(fn).SingleOrDefault(r=>r!["id"]!.ToString()==marker["id"]!.ToString());
        if(row is null)fn.Values.Remove(Metadata);else Store(fn,row.DeepClone().AsObject());
    }
    public static bool SameBranches(Element before,Element after)
    {
        var marker=Read(after);if(marker is null)return Read(before) is null&&JsonNode.DeepEquals(BlueprintExecutionBranches.Read(before),BlueprintExecutionBranches.Read(after));
        var old=Read(before);var expected=old??Preview(before);if(!JsonNode.DeepEquals(marker,expected))return false;
        JsonArray Other(Element fn){var rows=BlueprintExecutionBranches.Read(fn);return new JsonArray(rows.Where(r=>r!["id"]!.ToString()!=marker["id"]!.ToString()).Select(r=>r!.DeepClone()).ToArray());}
        return JsonNode.DeepEquals(Other(before),Other(after));
    }
}
