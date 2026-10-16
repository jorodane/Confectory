using Confectory.Core;
using System.Text.Json.Nodes;

// A reference and typed import, never a copy of the callee's implementation.
internal static class BlueprintCall
{
 public static JsonObject Prepare(JsonObject request,Func<Element,string> format)
 {
  var implementation=new Parser(request["text"]!.GetValue<string>(),"<caller>").ParseElement();
  var target=new Parser(request["targetText"]!.GetValue<string>(),"<callee>").ParseElement();
  var definition=request["definition"]!.AsObject();string id=definition["id"]!.GetValue<string>(),feature=definition["feature"]!.GetValue<string>(),intent=definition["intent"]!.GetValue<string>(),control=definition["control"]!.GetValue<string>();
  if(implementation.Kind!="implementation"||implementation.Id!=request["id"]!.GetValue<string>()||target.Kind!="function"||target.Id!=feature||target.Signature is null||feature==implementation.Function)throw new ArgumentException("An existing function with its exact contract identity is required");
  if(definition.Any(p=>p.Key is not ("id" or "feature" or "intent" or "control"))||id.Length>128||!System.Text.RegularExpressions.Regex.IsMatch(id,@"\A[A-Za-z_][A-Za-z_0-9.-]*\z")||string.IsNullOrWhiteSpace(intent)||intent.Length>16384||control is not ("next" or "branch")||control=="branch"&&target.Signature.Return!="bool")throw new ArgumentException("Explicit call node identity, intent and compatible execution port required");
  var graph=request["graph"]!.DeepClone().AsObject();if(graph["feature"]?.ToString()!=implementation.Function||graph["nodes"]!.AsArray().Any(n=>n!["id"]!.ToString()==id))throw new ArgumentException("Current caller graph and a new node identity required");
  string alias=FeatureBlueprint.ImportAlias(feature);
  if(implementation.Imports.TryGetValue(alias,out var existing)){
   if(existing.Id!=feature||!existing.Signature.Matches(target.Signature))throw new ArgumentException("Existing import identity or signature differs from the selected contract; preserve and repair it explicitly");
  }else{
   foreach(var pair in implementation.Imports)if(pair.Value.Id==feature)throw new ArgumentException("The function already has another import alias; preserve it and review the implementation's typed imports explicitly");
   implementation.Imports.Add(alias,new Import(feature,target.Signature,null,new(),implementation.Id));
  }
  var args=new JsonArray();foreach(var arg in target.Signature.Args)args.Add(new JsonObject{["type"]=arg.Type,["name"]=arg.Name});
  var signature=new JsonObject{["args"]=args,["return"]=target.Signature.Return};
  graph["nodes"]!.AsArray().Add(new JsonObject{["id"]=id,["kind"]="call",["feature"]=feature,["intent"]=intent,["control"]=control,["signature"]=signature.DeepClone(),["arguments"]=new JsonObject()});
  return new JsonObject{["implementation"]=format(implementation),["graph"]=graph,["feature"]=feature,["alias"]=alias,["scope"]=implementation.Imports[alias].Scope,["signature"]=signature,["description"]=target.Description,["contractHash"]=FeatureBlueprint.ContractHash(target),["sourceWritten"]=false,["compiled"]=false};
 }
}
