using System.Text.Json.Nodes;
using Confectory.Core;

// Coalesce only the read-only guards over one exact supplied draft snapshot.
// No result survives this request: every guard still executes, and any
// intermediate physical materialization is left to the original caller.
internal static class InformationGuardBatch
{
 internal static JsonObject Execute(JsonObject request, Func<Element,string> formatElement, Func<Manifest,string> formatManifest)
 {
  string action=request["action"]!.GetValue<string>();
  if(request["units"] is not JsonObject || request["project"] is not JsonValue || request["namespace"] is not JsonValue)
   throw new ArgumentException("Exact project guard snapshot required");
  if(action=="prepare"){
   if(request["declaration"] is not JsonObject)throw new ArgumentException("Explicit declaration required");
  }else if(request["selected"] is not JsonArray)throw new ArgumentException("Exact selected guards required");
  // The same read-only request object is passed sequentially. No guard mutates
  // its input; private candidate documents are cloned by their existing code.
  request["action"]=action=="prepare"?"prepare":"validate";
  JsonObject Property()=>InformationFunctionPropertyGuards.Execute(request);
  JsonObject Type()=>FunctionNativeTypes.Guards(request,formatManifest);
  JsonObject Body()=>InformationFunctionBodyGuards.Execute(request,formatElement,formatManifest);
  switch(action){
   case "selection": Property();Type();return new(){["complete"]=true};
   case "final":{
    var reads=new JsonArray();foreach(var result in new[]{Type(),Property(),Body()})foreach(var read in result["reads"]!.AsArray())reads.Add(read!.DeepClone());
    return new(){["reads"]=reads};
   }
   case "observations":{
    // Only if there are no host-side reads between these operations may the
    // entire chain share a request. Otherwise the original path runs unchanged.
    if(BlueprintPropertyObservations.Query(request)["checks"]!.AsArray().Count!=0)return new(){["complete"]=false};
    var project=request["project"]!.DeepClone();request.Remove("project");request["action"]="headers";
    if(Body()["ids"]!.AsArray().Count!=0)return new(){["complete"]=false};
    request["action"]="graphs";
    if(Body()["ids"]!.AsArray().Count!=0)return new(){["complete"]=false};
    request["project"]=project;request["action"]="validate";Body();return new(){["complete"]=true};
   }
   case "prepare":{
    var body=Body();
    if(body["required"]?.GetValue<bool>()==true||body["contexts"] is not null||body["reads"] is JsonArray bodyReads&&bodyReads.Count!=0)return new(){["complete"]=false};
    var property=Property();if(property["reads"]!.AsArray().Count!=0)return new(){["complete"]=false};
    var types=Type();if(types["reads"]!.AsArray().Count!=0)return new(){["complete"]=false};
    return new(){["complete"]=true,["body"]=body,["property"]=property,["types"]=types};
   }
   default:throw new ArgumentException("Unknown read-only guard batch");
  }
 }
}
