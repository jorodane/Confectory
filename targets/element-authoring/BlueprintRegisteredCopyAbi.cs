using Confectory.Core;
using System.Text.Json.Nodes;

// An external implemented function is evidence, never a writable group member.
// The ordinary public Bind path cannot obtain this authority from client JSON.
internal static class BlueprintRegisteredCopyAbi
{
 public static JsonObject Query(JsonObject request)
 {
  var implementation=new Parser(request["text"]!.GetValue<string>(),"<registered-copy>").ParseElement();
  var manifest=new Parser(request["manifest"]!.GetValue<string>(),"<registered-copy-project>").ParseManifest();
  if(implementation.Kind!="implementation"||implementation.Id!=request["id"]!.ToString()||PackPaths.Namespace(implementation.Id)!=manifest.Namespace||implementation.Function is null||PackPaths.Namespace(implementation.Function)==manifest.Namespace)throw new ArgumentException("Owned copy of a registered function required");
  var declaration=BlueprintCallableContracts.Query(new JsonObject{["action"]="read",["project"]=request["project"]!.DeepClone(),["manifest"]=request["manifest"]!.DeepClone(),["sourceId"]=implementation.Id,["text"]=request["text"]!.DeepClone(),["id"]=implementation.Function,["includeParents"]=true});
  if(declaration["readOnly"]?.GetValue<bool>()!=true||declaration["bodyReads"]?.GetValue<int>()!=0||declaration["id"]?.ToString()!=implementation.Function)throw new InvalidOperationException("Observed read-only registered declaration required");
  var function=new Parser(declaration["text"]!.GetValue<string>(),"<observed-copy-function>").ParseElement();
  var proof=BlueprintCopyAbi.Bind(request,function);
  proof["registeredFunction"]=new JsonObject{["receipt"]=declaration["receipt"]!.DeepClone(),["observations"]=declaration["observations"]!.DeepClone(),["registeredBytes"]=declaration["registeredBytes"]!.DeepClone(),["readOnly"]=true,["bodyReads"]=0};
  return proof;
 }
}
