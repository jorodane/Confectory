using System.Text.Json.Nodes;

namespace Confectory.Core;

// The legacy v508 adapter keeps native completion mapped ONLY to NoBranch.
// A separate explicit receipt binds the public execution result; never infer it.
// Native data returns use a separate explicit output storage mapping, never a cast.
public static class BlueprintCallWrapper
{
    public const string NativeReturnMapping = "native-return-out-v1";
    public static JsonObject Enum(JsonObject value)
    {
        if (value.Any(p => p.Key is not ("primary" or "members"))) throw new ArgumentException("Execution contract fields required");
        var checkedValue = BlueprintEnumContract.Validate(new JsonObject { ["schema"] = 1, ["kind"] = "execution-enum-proposal", ["sourceId"] = "wrapper-enum", ["definitionHash"] = new string('0', 64), ["sourceHash"] = new string('0', 64), ["primary"] = value["primary"]?.DeepClone(), ["members"] = value["members"]?.DeepClone() });
        return new JsonObject { ["primary"] = checkedValue["primary"]!.DeepClone(), ["members"] = checkedValue["members"]!.DeepClone() };
    }
    public static JsonObject Prepare(Element feature, JsonObject executionEnum, string? expected = null, string? source = null, string helpers = "", string? returnMapping = null, string? originalExecution = null)
    {
        if (feature.Signature is null || (feature.Signature.Return == "void" ? returnMapping is not null : returnMapping != NativeReturnMapping)) throw new ArgumentException("Exact native-return output mapping required; execution outcome is separate");
        var contract = Enum(executionEnum); var snapshot = BlueprintOutputSnapshot.Prepare(feature);
        string hash = ContractHash(feature, originalExecution is not null);
        if (expected is not null && expected != hash || originalExecution is not null && originalExecution != FeatureBlueprint.ContractHash(feature)) throw new InvalidOperationException("The original execution/output contract changed; retain and explicitly review wrapper input");
        string primary = contract["primary"]!.ToString(), name = contract["members"]!.AsArray().Single(m => m!["id"]!.ToString() == primary)!["name"]!.ToString();
        string body = source ?? (originalExecution is null ? "return Result." + name + ";" : DefaultBody(feature,snapshot,contract));
        if (body.Length > 65536 || helpers.Length > 65536) throw new ArgumentException("Wrapper source budget");
        return new JsonObject { ["mode"] = "execution-enum", ["contractHash"] = hash, ["executionEnum"] = contract, ["source"] = body, ["helpers"] = helpers, ["snapshot"] = snapshot, ["originalExecution"] = originalExecution, ["originalOutcome"] = originalExecution is not null ? "public-execution-branches" : feature.Signature.Return == "void" ? "native-void-completion-only" : "native-data-completion-only", ["returnMapping"] = returnMapping, ["outputBindings"] = new JsonArray(FeatureBlueprint.FeatureOutputs(feature.Signature).Select(p => (JsonNode)new JsonObject { ["port"] = p.Name, ["type"] = p.Type, ["storage"] = p.Name == "return" ? "native-return" : "native-out" }).ToArray()), ["parts"] = Parts(feature, snapshot, contract, body, helpers, "Function", "IOriginal", true, originalExecution is not null), ["sourceWritten"] = false, ["executed"] = false };
    }
    public static string ContractHash(Element feature,bool publicExecution=false) {
        string snapshot=BlueprintOutputSnapshot.Prepare(feature)["contractHash"]!.ToString();
        if(!publicExecution)return snapshot;
        if(!BlueprintExecutionBranches.Has(feature))throw new ArgumentException("Existing public execution contract required");
        _=BlueprintExecutionBranches.Read(feature);
        return JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(new JsonObject{["schema"]=1,["snapshot"]=snapshot,["execution"]=FeatureBlueprint.ContractHash(feature)}.ToJsonString()));
    }
    public static JsonObject Default(Element feature) => Prepare(feature,BlueprintExecutionBranches.Has(feature)?DefaultEnum(feature):new JsonObject{["primary"]="next",["members"]=new JsonArray(new JsonObject{["id"]="next",["name"]="NoBranch",["value"]=0})},returnMapping:feature.Signature!.Return=="void"?null:NativeReturnMapping,originalExecution:BlueprintExecutionBranches.Has(feature)?FeatureBlueprint.ContractHash(feature):null);
    static JsonObject DefaultEnum(Element feature) {
        var result=BlueprintExecutionBranches.Enum(feature);
        foreach(var branch in BlueprintExecutionBranches.Read(feature)){
            var row=result["members"]!.AsArray().Single(m=>m!["id"]!.ToString()==branch!["id"]!.ToString())!;string fallback=row["name"]!.ToString();
            foreach(string name in new[]{branch!["name"]!.ToString(),"@"+branch["name"]}){row["name"]=name;try{_=Enum(result);break;}catch(ArgumentException){row["name"]=fallback;}}
        }
        return result;
    }
    public static JsonObject Editor(Element feature,JsonObject executionEnum,JsonObject? post,bool inspect=false) => Prepare(feature,executionEnum,inspect?null:post?["contractHash"]?.ToString(),post?["source"]?.GetValue<string>(),post?["helpers"]?.GetValue<string>()??"",inspect?(feature.Signature!.Return=="void"?null:NativeReturnMapping):post?["returnMapping"]?.GetValue<string>(),post?["originalExecution"] is null?null:inspect?FeatureBlueprint.ContractHash(feature):post["originalExecution"]!.GetValue<string>());
    static string DefaultBody(Element feature,JsonObject snapshot,JsonObject contract) {
        var used=feature.Signature!.Args.Select(p=>p.Name).Concat(new[]{snapshot["sourceParameter"]!.ToString(),snapshot["contextVariable"]!.ToString()}).ToHashSet(StringComparer.Ordinal);string branch="originalBranch";while(!used.Add(branch))branch="_"+branch;
        var rows=new List<string>{"switch (@"+branch+")","{"};
        foreach(var source in BlueprintExecutionBranches.Enum(feature)["members"]!.AsArray()){var target=contract["members"]!.AsArray().SingleOrDefault(m=>m!["id"]!.ToString()==source!["id"]!.ToString());if(target is not null)rows.Add("    case OriginalResult."+source!["name"]+": return Result."+target["name"]+";");}
        rows.Add("}");rows.Add("return Result."+contract["members"]!.AsArray().Single(m=>m!["id"]!.ToString()==contract["primary"]!.ToString())!["name"]+";");return string.Join("\n",rows);
    }
    static JsonArray Parts(Element feature, JsonObject snapshot, JsonObject contract, string body, string helpers, string type, string originalInterface, bool preview, bool publicExecution)
    {
        var signature=feature.Signature!;
        string original = snapshot["sourceParameter"]!.ToString(), context = snapshot["contextVariable"]!.ToString(), branch = "originalBranch";
        var used = signature.Args.Select(p => p.Name).Concat(new[] { original, context }).ToHashSet(StringComparer.Ordinal);
        while (!used.Add(branch)) branch = "_" + branch;
        used.Add(snapshot["returnVariable"]!.ToString()); string storage = "nativeReturn"; while (!used.Add(storage)) storage = "_" + storage;
        string outputParameter = signature.Return == "void" ? "" : ", out " + signature.Return + " @" + storage, capture = signature.Return == "void" ? "" : "@" + storage + " = @" + snapshot["returnVariable"] + ";\n";
        string Args(bool declarations, bool inputsOnly = false) => string.Join(", ", signature.Args.Where(p => !inputsOnly || !p.IsOut).Select(p => (p.Mode is "out" or "ref" ? p.Mode + " " : "") + (declarations ? p.Type + " " : "") + "@" + p.Name));
        string inputTail = signature.Args.Any(p => !p.IsOut) ? ", " + Args(false, true) : "", declarations = signature.Args.Any(p => !p.IsOut) ? ", " + Args(true, true) : "";
        string members = string.Join("\n", contract["members"]!.AsArray().Select(m => "    " + m!["name"] + " = " + m["value"] + ","));
        string sourceMembers=publicExecution?string.Join("\n",BlueprintExecutionBranches.Enum(feature)["members"]!.AsArray().Select(m=>"    "+m!["name"]+" = "+m["value"]+",")):"    NoBranch = 0,";
        string sourceInterface=snapshot["originalInterface"]!.ToString();
        if(publicExecution&&preview)sourceInterface=sourceInterface.Replace(" }", " "+type+".OriginalResult InvokeExecution("+Args(true)+(signature.Return=="void"?"":(signature.Args.Count>0?", ":"")+BlueprintExecutionBranches.CaptureParameter(signature))+"); }");
        string fixedPrefix = (preview ? sourceInterface : "") + (preview ? "public" : "private") + " static class " + type + "\n{\npublic enum OriginalResult\n{\n"+sourceMembers+"\n}\n\n" + snapshot["contextSource"] + "\npublic enum Result\n{\n";
        string originalCall=snapshot["originalCall"]!.ToString();
        if(publicExecution){
            string outcome="__fg_original_execution";while(!used.Add(outcome))outcome="_"+outcome;
            string receiver=preview?"@"+original:"(("+BlueprintExecutionBranches.Interface(feature.Id)+")@"+original+")";
            originalCall="var "+outcome+" = "+receiver+".InvokeExecution("+Args(false)+(signature.Return=="void"?"":(signature.Args.Count>0?", ":"")+"out "+signature.Return+" @"+snapshot["returnVariable"])+");\nvar @"+context+" = new SourceContext("+string.Join(", ",snapshot["fields"]!.AsArray().Select(f=>"@"+(f!["name"]!.ToString()=="return"?snapshot["returnVariable"]!.ToString():f["name"]!.ToString())))+");\n";
            originalCall+="var @"+branch+" = (int)"+outcome+" switch { "+string.Join(", ",BlueprintExecutionBranches.Enum(feature)["members"]!.AsArray().Select(m=>m!["value"]+" => OriginalResult."+m["name"]))+", _ => throw new global::System.InvalidOperationException(\"Unknown original execution branch\") };\n";
        }
        string fixedCall = "\n}\npublic static Result Execute(" + originalInterface + " @" + original + (signature.Args.Count > 0 ? ", " + Args(true) : "") + outputParameter + ")\n{\n" + originalCall + capture + (publicExecution?"":"var @" + branch + " = OriginalResult.NoBranch;\n")+"return After(@" + branch + ", @" + context + inputTail + ");\n}\nprivate static Result After(OriginalResult @" + branch + ", SourceContext @" + context + declarations + ")\n{\n";
        return new JsonArray(new JsonObject { ["text"] = fixedPrefix }, new JsonObject { ["id"] = "enum", ["text"] = members }, new JsonObject { ["text"] = fixedCall }, new JsonObject { ["id"] = "body", ["text"] = body }, new JsonObject { ["text"] = "\n}\n" }, new JsonObject { ["id"] = "helpers", ["text"] = helpers }, new JsonObject { ["text"] = "\n}\n" });
    }
    public static string Member(Element feature, JsonObject postCall, JsonObject executionEnum, string type, string originalInterface, string marker)
    {
        var prepared = Prepare(feature, executionEnum, postCall["contractHash"]!.GetValue<string>(), postCall["source"]!.GetValue<string>(), postCall["helpers"]?.GetValue<string>() ?? "", postCall["returnMapping"]?.GetValue<string>(),postCall["originalExecution"]?.GetValue<string>());
        var parts = Parts(feature, prepared["snapshot"]!.AsObject(), prepared["executionEnum"]!.AsObject(), prepared["source"]!.ToString(), prepared["helpers"]!.ToString(), type, originalInterface, false, postCall["originalExecution"] is not null);
        return string.Concat(parts.Select(p => p!["id"]?.ToString() is "enum" or "body" or "helpers" ? "#line 1 " + System.Text.Json.JsonSerializer.Serialize(marker + "/" + p["id"]) + "\n" + p["text"] + "\n#line default\n" : p["text"]!.ToString()));
    }
}
