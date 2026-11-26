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
  if(definition.Any(p=>p.Key is not ("id" or "feature" or "intent" or "control" or "branchInsertion" or "privateInsertion" or "arguments"))||id.Length>128||!System.Text.RegularExpressions.Regex.IsMatch(id,@"\A[A-Za-z_][A-Za-z_0-9.-]*\z")||string.IsNullOrWhiteSpace(intent)||intent.Length>16384||control is not ("next" or "branch")||control=="branch"&&target.Signature.Return!="bool")throw new ArgumentException("Explicit call node identity, intent and compatible execution port required");
  var graph=request["graph"]!.DeepClone().AsObject();if(graph["feature"]?.ToString()!=implementation.Function||graph["nodes"]!.AsArray().Any(n=>n!["id"]!.ToString()==id))throw new ArgumentException("Current caller graph and a new node identity required");
  string alias=FeatureBlueprint.ImportAlias(feature);
  if(implementation.Imports.TryGetValue(alias,out var existing)){
   if(existing.Id!=feature||!existing.Signature.Matches(target.Signature))throw new ArgumentException("Existing import identity or signature differs from the selected contract; preserve and repair it explicitly");
  }else{
   foreach(var pair in implementation.Imports)if(pair.Value.Id==feature)throw new ArgumentException("The function already has another import alias; preserve it and review the implementation's typed imports explicitly");
   implementation.Imports.Add(alias,new Import(feature,target.Signature,null,new(),implementation.Id));
  }
  var signature=FeatureBlueprint.SignatureDocument(target.Signature);
  var node=new JsonObject{["id"]=id,["kind"]="call",["feature"]=feature,["intent"]=intent,["control"]=control,["signature"]=signature.DeepClone(),["arguments"]=new JsonObject()};
  if(definition["privateInsertion"] is JsonObject privateGap){
   if(definition["branchInsertion"] is not null||control!="next"||implementation.Parent is not null||BlueprintAsync.Has(target)||
      target.Signature.Args.Any(a=>a.Mode is not null)||BlueprintExecutionBranches.Has(target))
    throw new ArgumentException("Ordinary synchronous private reference required");
   var arguments=definition["arguments"] as JsonObject??new JsonObject();
   if(arguments.Count>target.Signature.Args.Count||arguments.Any(p=>!target.Signature.Args.Any(a=>a.Name==p.Key)))
    throw new ArgumentException("Declared private value inputs required");
   node["arguments"]=arguments.DeepClone();
   BlueprintCellRegion.InsertPrivateReference(graph,node,privateGap);
  }else if(definition["privateInsertion"] is not null||definition["arguments"] is not null)
   throw new ArgumentException("Private insertion arguments require an exact frame");
  else if(definition["branchInsertion"] is JsonNode placement){
   if(control!="next"||placement is not JsonObject gap||implementation.Parent is not null||BlueprintAsync.Has(target))throw new ArgumentException("Synchronous direct branch reference required");
   BlueprintCellRegion.InsertReference(graph,node,gap);
  }
  if(definition["privateInsertion"] is null)graph["nodes"]!.AsArray().Add(node);
  return new JsonObject{["implementation"]=format(implementation),["graph"]=graph,["feature"]=feature,["alias"]=alias,["scope"]=implementation.Imports[alias].Scope,["signature"]=signature,["description"]=target.Description,["contractHash"]=FeatureBlueprint.ContractHash(target),["sourceWritten"]=false,["compiled"]=false};
 }
}
