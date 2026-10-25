using Confectory.Core;
using System.Text.Json.Nodes;

// Existing After/enum C# regions: explicit text only, immutable execution ports,
// original graph/wrapper receipt and the actual candidate's current contract.
internal static class InformationFunctionPostCalls
{
 static string Hash(string text)=>JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(text));
 static JsonObject Receipt(string id,string text,JsonObject call)=>new(){["graph"]=id,["hash"]=Hash(text),["node"]=call["id"]!.DeepClone(),["postCall"]=call["postCall"]!.DeepClone(),["executionEnum"]=call["executionEnum"]?.DeepClone()};
 static JsonObject Editor(Element feature,JsonObject call,string source,string helpers)
 {
  var post=call["postCall"]!.AsObject();if(post["mode"]?.ToString()=="execution-enum")return BlueprintCallWrapper.Prepare(feature,call["executionEnum"]!.AsObject(),source:source,helpers:helpers,returnMapping:feature.Signature!.Return=="void"?null:BlueprintCallWrapper.NativeReturnMapping);
  if(post["mode"] is not null)throw new InvalidOperationException("Known existing post-call mode required");return BlueprintCallAfter.Prepare(feature,source:source,helpers:helpers);
 }
 internal static int Read(JsonObject result,string id,string text,JsonObject graph,Element implementation,Element original,Element current,string label,string target,string path)
 {
  if(graph["copySource"] is not null)return 0;
  int bytes=0;foreach(var call in graph["nodes"]!.AsArray().OfType<JsonObject>().Where(n=>n["kind"]?.ToString()=="call"&&n["feature"]?.ToString()==original.Id&&n["postCall"] is JsonObject)){
   var post=call["postCall"]!.AsObject();if(!JsonNode.DeepEquals(call["signature"],FeatureBlueprint.SignatureDocument(original.Signature!))||post["contractHash"]?.ToString()!=BlueprintOutputSnapshot.Prepare(original)["contractHash"]!.ToString())throw new InvalidOperationException("Original post-call contract is stale; retain source");
   string source=post["source"]!.GetValue<string>(),helpers=post["helpers"]?.GetValue<string>()??"";bytes=checked(bytes+System.Text.Encoding.UTF8.GetByteCount(source+helpers));var editor=Editor(current,call,source,helpers);
   result.Add(id+"/postCall:"+call["id"]!.ToString(),new JsonObject{["sourceKind"]="post-call-csharp",["name"]=label+" · 후처리 "+call["id"],["caller"]=true,["implementation"]=implementation.Id,["function"]=original.Id,["target"]=target,["path"]=path,["hash"]=Hash(text),["graph"]=id,["node"]=call["id"]!.DeepClone(),["text"]=source,["helpers"]=helpers,["wrapper"]=Receipt(id,text,call),["postEditor"]=editor});
   if(result.Count>32)throw new ArgumentException("Explicit body/wrapper selection budget");
  }return bytes;
 }
 internal static JsonObject Prepare(string id,string text,JsonObject originalCall,Element original,Element current,JsonObject plan)
 {
  if(JsonNode.Parse(text)?["copySource"] is not null)throw new InvalidOperationException("Copy wrapper provenance requires its separate source receipt");
  if(plan.Count!=4||plan.Any(p=>p.Key is not ("wrapper" or "contract" or "text" or "helpers"))||!JsonNode.DeepEquals(plan["wrapper"],Receipt(id,text,originalCall))||!JsonNode.DeepEquals(plan["contract"],FeatureBlueprint.SignatureDocument(current.Signature!))||plan["text"] is not JsonValue body||!body.TryGetValue<string>(out string? source)||plan["helpers"] is not JsonValue members||!members.TryGetValue<string>(out string? helpers))throw new InvalidOperationException("Exact original wrapper and explicit current C# regions required; source retained");
  var before=originalCall["postCall"]!.AsObject();if(before["contractHash"]?.ToString()!=BlueprintOutputSnapshot.Prepare(original)["contractHash"]!.ToString())throw new InvalidOperationException("Original wrapper publication changed; source retained");
  var prepared=Editor(current,originalCall,source,helpers);var post=new JsonObject{["contractHash"]=prepared["contractHash"]!.DeepClone(),["source"]=source,["helpers"]=helpers};if(prepared["mode"] is not null){post["mode"]=prepared["mode"]!.DeepClone();if(prepared["returnMapping"] is not null)post["returnMapping"]=prepared["returnMapping"]!.DeepClone();}return post;
 }
}
