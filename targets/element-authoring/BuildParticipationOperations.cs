using Confectory.Core;
using System.Text.Json.Nodes;

internal static class BuildParticipationOperations
{
    internal static JsonNode Execute(string operation,JsonObject request)
    {
        string root=Path.GetFullPath(request["root"]!.GetValue<string>());var plan=JsonNode.Parse(request["plan"]!.GetValue<string>())!.AsObject();if(plan["version"]!.GetValue<int>()!=1)throw new ArgumentException("Build plan version 1 required.");
        var outputs=plan["outputs"]!.AsArray().Select(x=>x!.AsObject()).OrderBy(x=>x["priority"]?.GetValue<int>()??0).ThenBy(x=>x["id"]!.GetValue<string>(),StringComparer.Ordinal).ToArray();
        if(outputs.Length==0||outputs.Select(x=>x["id"]!.GetValue<string>()).Distinct(StringComparer.Ordinal).Count()!=outputs.Length)throw new ArgumentException("Nonempty unique output IDs required.");
        string receipt=Path.Combine(root,".confectory","build-participation",JsonData.Digest(plan),"last-success.json");
        if(operation=="outputsLast")return File.Exists(receipt)?JsonNode.Parse(File.ReadAllText(receipt))!:new JsonObject{["state"]="none"};
        var described=new JsonArray();
        foreach(var output in outputs)
        {
            string id=output["id"]!.GetValue<string>();if(string.IsNullOrWhiteSpace(id))throw new ArgumentException("Output ID required.");
            string project=Path.GetFullPath(Path.Combine(root,output["project"]!.GetValue<string>())),entry=output["entry"]!.GetValue<string>(),target=output["target"]!.GetValue<string>();
            if(string.IsNullOrWhiteSpace(entry)||string.IsNullOrWhiteSpace(target))throw new ArgumentException("Every output declares explicit entry and target.");
            var usage=PackOperations.Usage(project,entry,target);usage["id"]=id;described.Add(usage);
        }
        if(operation=="outputsDescribe"||operation=="outputsValidate")return new JsonObject{["state"]="planned",["outputs"]=described,["executedProjectOrTargetCode"]=false};
        if(operation!="outputsBuild")throw new ArgumentException("Unknown output operation.");
        var results=new JsonArray();
        try
        {
            foreach(var output in described)
            {
                var builder=new Builder(output!["project"]!.GetValue<string>(),output["target"]!.GetValue<string>());builder.Registry.Project.Entry=output["entry"]!.GetValue<string>();var built=builder.Build();built["id"]=output["id"]!.GetValue<string>();results.Add(built);
            }
            var success=new JsonObject{["state"]="built",["outputs"]=results};JsonData.AtomicWrite(receipt,success);return success;
        }
        catch(Exception error)
        {
            return new JsonObject{["state"]="failed",["error"]=error.Message,["partialArtifacts"]=results,["lastSuccessfulPlanRetained"]=File.Exists(receipt)};
        }
    }
}
