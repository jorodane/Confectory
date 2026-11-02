using Confectory.Core;
using System.Text;
using System.Text.Json.Nodes;

// Existing owned copy bodies may return the published IDs; they never edit
// the public contract. Keep every observed original in the final file lease.
static class BlueprintPublicCopyReturns
{
    public static JsonObject Guards(JsonObject request)
    {
        var units=request["units"]!.AsObject();var checks=new JsonArray();string ns=request["namespace"]!.ToString();
        var selected=request["selected"]?.AsArray().Select(n=>n!.ToString()).ToHashSet(StringComparer.Ordinal);
        var paths=new Dictionary<string,string>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);
        foreach(var pair in units) {
            var unit=pair.Value;
            if(unit?["kind"]?.ToString()!="blueprint"||unit["baseline"]?.ToString()=="missing"||unit["draft"] is null)continue;
            if(selected is not null&&!selected.Contains(pair.Key)&&!(unit["atomicEditGroup"] is JsonArray chosen&&chosen.Any(n=>selected.Contains(n!.ToString()))))continue;
            var graph=JsonNode.Parse(unit["draft"]!.GetValue<string>())!.AsObject();
            if(graph["copySource"] is null||graph["executionExitMode"]?.GetValue<bool>()!=true)continue;
            var originalGraph=JsonNode.Parse(unit["original"]!.GetValue<string>())!.AsObject();
            if(unit["authorSaveReceipt"]?["publicCopyReturns"]?.GetValue<bool>()!=true&&new[]{"entry","edges","exits"}.All(key=>JsonNode.DeepEquals(graph[key],originalGraph[key])))continue;
            if(unit["atomicEditGroup"] is not JsonArray group)throw new ArgumentException("Complete public copy return review group required");
            var ids=group.Select(n=>n!.ToString()).ToArray();
            if(selected is not null&&!ids.Any(selected.Contains))continue;
            if(ids.Length is <4 or >64||ids.Distinct(StringComparer.Ordinal).Count()!=ids.Length||!ids.Contains(pair.Key,StringComparer.Ordinal)||ids.Any(id=>PackPaths.Namespace(id)!=ns||units[id] is null||!JsonNode.DeepEquals(units[id]!["atomicEditGroup"],group)))throw new ArgumentException("Complete owned public copy return group required");
            if(!ids.Any(id=>units[id]!["draft"]?.ToString()!=units[id]!["original"]?.ToString()||units[id]!["baseline"]?.ToString()=="missing"))continue;
            int marker=pair.Key.IndexOf("/body:",StringComparison.Ordinal);if(marker<0||pair.Key.Contains("/graph:",StringComparison.Ordinal))throw new ArgumentException("Saved root copy return required");
            string implementationId=pair.Key[..marker],target=pair.Key[(marker+6)..],feature=graph["feature"]!.ToString();
            var implementation=units[implementationId]??throw new ArgumentException("Owned copy declaration required");var function=units[feature]??throw new ArgumentException("Owned published contract required; external declarations remain protected");
            var impl=new Parser(implementation["draft"]!.GetValue<string>(),"<copy-return>").ParseElement();var fn=new Parser(function["draft"]!.GetValue<string>(),"<copy-return-contract>").ParseElement();
            if(implementation["kind"]?.ToString()!="implementation"||function["kind"]?.ToString()!="function"||impl.Id!=implementationId||fn.Id!=feature||impl.Parent is not null||fn.Parent is not null||impl.Function!=feature||!impl.Signature!.Matches(fn.Signature)||!BlueprintExecutionBranches.Has(fn)||!impl.Bodies.TryGetValue(target,out var body)||body.SourceKind!="blueprint"||body.Path!=unit["path"]?.ToString()||graph["contractHash"]?.ToString()!=FeatureBlueprint.ContractHash(fn)||function["draft"]?.ToString()!=function["original"]?.ToString()||implementation["draft"]?.ToString()!=implementation["original"]?.ToString()||!JsonNode.DeepEquals(graph["copySource"],JsonNode.Parse(unit["original"]!.GetValue<string>())!["copySource"]))throw new ArgumentException("Preserve the saved copy, original public contract and provenance");
            _=BlueprintExecutionBranches.Read(fn);
            var receipt=unit["authorSaveReceipt"]??throw new ArgumentException("Saved copy return observation receipt required");string owner=receipt["slotRequest"]?["owner"]?.ToString()??"";
            if(receipt["version"]?.GetValue<int>()!=1||receipt["graph"]?.ToString()!=pair.Key||!ids.Contains(owner,StringComparer.Ordinal)||units[owner]?["kind"]?.ToString() is not ("schema" or "object")||!ids.Contains(feature,StringComparer.Ordinal)||!ids.Contains(implementationId,StringComparer.Ordinal)||receipt["sources"] is not JsonObject sources||sources.Count is <4 or >64||!sources.ContainsKey(owner)||!sources.ContainsKey(feature)||!sources.ContainsKey(implementationId)||!sources.ContainsKey(pair.Key))throw new ArgumentException("Exact copy owner and complete observed source receipt required");
            var ownerText=units[owner]!["draft"]!.GetValue<string>();var ownerDefinition=new Parser(ownerText,"<copy-return-owner>").ParseElement();
            if(ownerDefinition.Id!=owner||ownerDefinition.Kind!=units[owner]!["kind"]!.ToString()||!ownerDefinition.Provides.TryGetValue(feature,out var assignment)||assignment.Id!=implementationId||receipt["slotRequest"]?["ownerHash"]?.ToString()!=JsonData.HashBytes(Encoding.UTF8.GetBytes(ownerText)))throw new ArgumentException("Preserve the explicit copy assignment and observed owner source");
            foreach(var observed in sources) {
                var source=units[observed.Key];
                if(!ids.Contains(observed.Key,StringComparer.Ordinal)||source is null||source["path"]?.ToString()!=observed.Value?["path"]?.ToString()||source["kind"]?.ToString()!=observed.Value?["kind"]?.ToString()||source["draft"] is null||JsonData.HashBytes(Encoding.UTF8.GetBytes(source["draft"]!.GetValue<string>()))!=observed.Value?["hash"]?.ToString())throw new ArgumentException("Observed copy return sources changed; preserve input and refresh explicitly");
            }
            foreach(string id in ids) {
                var source=units[id]!;string path=source["path"]!.ToString(),hash=source["baseline"]!.ToString();
                _=PackPaths.Owned(Path.Combine(Path.GetTempPath(),"confectory-public-copy-return"),path);
                if(!System.Text.RegularExpressions.Regex.IsMatch(hash,@"\A[a-f0-9]{64}\z"))throw new ArgumentException("Confirm existing copy sources before editing published returns");
                if(paths.TryGetValue(path,out var prior)){if(prior!=hash)throw new ArgumentException("Conflicting owned source observations");continue;}
                paths[path]=hash;checks.Add(new JsonObject{["path"]=path,["hash"]=hash});
            }
        }
        return new JsonObject{["checks"]=checks,["sourceWritten"]=false,["executed"]=false};
    }
}
