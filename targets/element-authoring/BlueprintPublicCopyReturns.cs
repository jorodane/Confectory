using Confectory.Core;
using System.Text;
using System.Text.Json.Nodes;

// Existing owned copy bodies may return the published IDs; they never edit
// the public contract. Keep every observed original in the final file lease.
static class BlueprintPublicCopyReturns
{
    static void Creating(JsonObject units,string id,string ns,JsonArray checks,Dictionary<string,string> paths)
    {
        var unit=units[id]!;var graph=JsonNode.Parse(unit["draft"]!.GetValue<string>())!.AsObject();int marker=id.IndexOf("/body:",StringComparison.Ordinal);
        if(marker<0||id.Contains("/graph:",StringComparison.Ordinal))throw new ArgumentException("New root copy identity required");
        string implementationId=id[..marker],target=id[(marker+6)..],feature=graph["feature"]!.ToString();var implementation=units[implementationId]!;string owner=implementation["creationOwner"]?.ToString()??"";
        var function=units[feature]??throw new ArgumentException("Observe the owned public contract before first copy Save");
        var fn=new Parser(function["draft"]!.GetValue<string>(),"<new-copy-contract>").ParseElement();var impl=new Parser(implementation["draft"]!.GetValue<string>(),"<new-copy>").ParseElement();
        if(unit["original"]?.ToString()!=""||implementation["baseline"]?.ToString()!="missing"||implementation["original"]?.ToString()!=""||implementation["kind"]?.ToString()!="implementation"||impl.Id!=implementationId||impl.Parent is not null||fn.Parent is not null||function["kind"]?.ToString()!="function"||fn.Id!=feature||impl.Function!=feature||!impl.Signature!.Matches(fn.Signature)||!BlueprintExecutionBranches.Has(fn)||function["draft"]?.ToString()!=function["original"]?.ToString()||!impl.Bodies.TryGetValue(target,out var body)||body.SourceKind!="blueprint"||body.Path!=unit["path"]?.ToString()||graph["contractHash"]?.ToString()!=FeatureBlueprint.ContractHash(fn)||graph["copySource"] is not JsonObject provenance||!JsonNode.DeepEquals(provenance,implementation["copySource"]))throw new ArgumentException("Preserve the owned public contract, new copy and sealed provenance");
        _=BlueprintExecutionBranches.Read(fn);
        if(unit["atomicEditGroup"] is not JsonArray group)throw new ArgumentException("Complete new public copy review group required");var ids=group.Select(n=>n!.ToString()).ToArray();
        if(ids.Length is <4 or >64||ids.Distinct(StringComparer.Ordinal).Count()!=ids.Length||!new[]{id,implementationId,feature,owner}.All(ids.Contains)||ids.Any(key=>PackPaths.Namespace(key)!=ns||units[key] is null||!JsonNode.DeepEquals(units[key]!["atomicEditGroup"],group)))throw new ArgumentException("Exact owned copy creation closure required");
        var ownerUnit=units[owner]!;var declaration=new Parser(ownerUnit["draft"]!.GetValue<string>(),"<new-copy-owner>").ParseElement();var receipt=ownerUnit["slotSaveReceipt"]??throw new ArgumentException("First copy Save receipt required");
        if(declaration.Id!=owner||declaration.Kind is not ("schema" or "object")||ownerUnit["kind"]?.ToString()!=declaration.Kind||!declaration.Provides.TryGetValue(feature,out var assignment)||assignment.Id!=implementationId||receipt["owner"]?.ToString()!=owner||receipt["intents"] is not JsonArray intents||!intents.Any(intent=>intent?["function"]?.ToString()==feature&&intent["implementation"]?.ToString()==implementationId&&intent["copySource"]?.ToString()==provenance["implementation"]?.ToString()&&intent["copyTarget"]?.ToString()==target)||receipt["sources"] is not JsonObject sources||sources.Count is <4 or >64||receipt["readGuards"] is not JsonObject guards||guards.Count is <1 or >240)throw new ArgumentException("Exact first copy assignment and source receipt required");
        // Later explicit body saves may update the still-unconfirmed copy. Keep
        // creation/assignment and original file reads, but verify its latest
        // owner-bound author receipt for the changed body rather than rebasing.
        JsonObject? updates=null;if(unit["authorSaveReceipt"] is JsonObject author){string frame=author["graph"]?.ToString()??"";updates=author["sources"] as JsonObject;if(author["version"]?.GetValue<int>()!=1||frame!=id&&!frame.StartsWith(id+"/graph:",StringComparison.Ordinal)||author["slotRequest"]?["owner"]?.ToString()!=owner||author["slotRequest"]?["ownerHash"]?.ToString()!=JsonData.HashBytes(Encoding.UTF8.GetBytes(ownerUnit["draft"]!.GetValue<string>()))||updates is null||updates.Count is <4 or >64||!new[]{id,implementationId,feature,owner}.All(updates.ContainsKey))throw new ArgumentException("Exact subsequent copy body observation required");}
        if(!sources.Select(p=>p.Key).Concat(updates?.Select(p=>p.Key)??Enumerable.Empty<string>()).ToHashSet(StringComparer.Ordinal).SetEquals(ids))throw new ArgumentException("Complete original and latest copy observation closure required");
        foreach(string key in ids){var source=units[key]!;var observed=updates?[key]??sources[key];string path=source["path"]!.ToString(),baseline=source["baseline"]!.ToString();if(observed?["path"]?.ToString()!=path||observed["kind"]?.ToString()!=source["kind"]?.ToString()||source["draft"] is null||observed["hash"]?.ToString()!=JsonData.HashBytes(Encoding.UTF8.GetBytes(source["draft"]!.GetValue<string>()))||baseline!="missing"&&(guards[path]?["path"]?.ToString()!=path||guards[path]?["hash"]?.ToString()!=baseline))throw new ArgumentException("Preserve every original in the first copy source receipt");}
        foreach(var guard in guards){string path=guard.Value?["path"]?.ToString()??"",hash=guard.Value?["hash"]?.ToString()??"";if(guard.Key!=path||!System.Text.RegularExpressions.Regex.IsMatch(hash,@"\A[a-f0-9]{64}\z"))throw new ArgumentException("Exact original copy source check required");_=PackPaths.Owned(Path.Combine(Path.GetTempPath(),"confectory-new-public-copy"),path);if(paths.TryGetValue(path,out var prior)){if(prior!=hash)throw new ArgumentException("Conflicting copy source observations");continue;}paths[path]=hash;checks.Add(new JsonObject{["path"]=path,["hash"]=hash});}
    }
    public static JsonObject Guards(JsonObject request)
    {
        var units=request["units"]!.AsObject();var checks=new JsonArray();string ns=request["namespace"]!.ToString();
        var selected=request["selected"]?.AsArray().Select(n=>n!.ToString()).ToHashSet(StringComparer.Ordinal);
        var paths=new Dictionary<string,string>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);
        foreach(var pair in units) {
            var unit=pair.Value;
            if(unit?["kind"]?.ToString()!="blueprint"||unit["draft"] is null)continue;
            if(selected is not null&&!selected.Contains(pair.Key)&&!(unit["atomicEditGroup"] is JsonArray chosen&&chosen.Any(n=>selected.Contains(n!.ToString()))))continue;
            var graph=JsonNode.Parse(unit["draft"]!.GetValue<string>())!.AsObject();
            if(graph["executionExitMode"]?.GetValue<bool>()!=true)continue;
            if(unit["baseline"]?.ToString()=="missing"){
                int split=pair.Key.IndexOf("/body:",StringComparison.Ordinal);if(split<0||PackPaths.Namespace(graph["feature"]!.ToString())!=ns||graph["copySource"] is null&&units[pair.Key[..split]]?["copySource"] is null)continue;
                Creating(units,pair.Key,ns,checks,paths);continue;
            }
            if(graph["copySource"] is null)continue;
            var originalGraph=JsonNode.Parse(unit["original"]!.GetValue<string>())!.AsObject();
            if(unit["authorSaveReceipt"]?["publicCopyReturns"]?.GetValue<bool>()!=true&&new[]{"entry","edges","exits"}.All(key=>JsonNode.DeepEquals(graph[key],originalGraph[key])))continue;
            if(unit["atomicEditGroup"] is not JsonArray group)throw new ArgumentException("Complete public copy return review group required");
            var ids=group.Select(n=>n!.ToString()).ToArray();
            if(selected is not null&&!ids.Any(selected.Contains))continue;
            if(ids.Length is <4 or >64||ids.Distinct(StringComparer.Ordinal).Count()!=ids.Length||!ids.Contains(pair.Key,StringComparer.Ordinal)||ids.Any(id=>PackPaths.Namespace(id)!=ns||units[id] is null||!JsonNode.DeepEquals(units[id]!["atomicEditGroup"],group)))throw new ArgumentException("Complete owned public copy return group required");
            if(!ids.Any(id=>units[id]!["draft"]?.ToString()!=units[id]!["original"]?.ToString()||units[id]!["baseline"]?.ToString()=="missing"))continue;
            int marker=pair.Key.IndexOf("/body:",StringComparison.Ordinal);if(marker<0||pair.Key.Contains("/graph:",StringComparison.Ordinal))throw new ArgumentException("Saved root copy return required");
            string implementationId=pair.Key[..marker],target=pair.Key[(marker+6)..],feature=graph["feature"]!.ToString();
            var implementation=units[implementationId]??throw new ArgumentException("Owned copy declaration required");var function=units[feature];
            var impl=new Parser(implementation["draft"]!.GetValue<string>(),"<copy-return>").ParseElement();bool external=PackPaths.Namespace(feature)!=ns;Element fn;
            if(external){var snapshot=unit["authorSaveReceipt"]?["registeredFunction"]?.AsObject()??throw new ArgumentException("Observe the registered copy return contract");string manifest=units.Single(u=>u.Value?["kind"]?.ToString()=="project").Value!["draft"]!.GetValue<string>();fn=BlueprintPublicReturnContract.Validate(snapshot,impl,manifest,implementation["draft"]!.ToString());}
            else{if(function is null)throw new ArgumentException("Owned published contract required");fn=new Parser(function["draft"]!.GetValue<string>(),"<copy-return-contract>").ParseElement();}
            if(implementation["kind"]?.ToString()!="implementation"||!external&&function?["kind"]?.ToString()!="function"||impl.Id!=implementationId||fn.Id!=feature||impl.Parent is not null||fn.Parent is not null||impl.Function!=feature||!impl.Signature!.Matches(fn.Signature)||!BlueprintExecutionBranches.Has(fn)||!impl.Bodies.TryGetValue(target,out var body)||body.SourceKind!="blueprint"||body.Path!=unit["path"]?.ToString()||graph["contractHash"]?.ToString()!=FeatureBlueprint.ContractHash(fn)||!external&&function?["draft"]?.ToString()!=function?["original"]?.ToString()||implementation["draft"]?.ToString()!=implementation["original"]?.ToString()||!JsonNode.DeepEquals(graph["copySource"],JsonNode.Parse(unit["original"]!.GetValue<string>())!["copySource"]))throw new ArgumentException("Preserve the saved copy, original public contract and provenance");
            _=BlueprintExecutionBranches.Read(fn);
            var receipt=unit["authorSaveReceipt"]??throw new ArgumentException("Saved copy return observation receipt required");string owner=receipt["slotRequest"]?["owner"]?.ToString()??"";
            if(receipt["version"]?.GetValue<int>()!=1||receipt["graph"]?.ToString()!=pair.Key||!ids.Contains(owner,StringComparer.Ordinal)||units[owner]?["kind"]?.ToString() is not ("schema" or "object")||!external&&!ids.Contains(feature,StringComparer.Ordinal)||!ids.Contains(implementationId,StringComparer.Ordinal)||receipt["sources"] is not JsonObject sources||sources.Count is <4 or >64||!sources.ContainsKey(owner)||!external&&!sources.ContainsKey(feature)||!sources.ContainsKey(implementationId)||!sources.ContainsKey(pair.Key))throw new ArgumentException("Exact copy owner and complete observed source receipt required");
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
