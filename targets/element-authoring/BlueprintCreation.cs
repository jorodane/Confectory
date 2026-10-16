using Confectory.Core;
using System.Text.Json.Nodes;

internal static class BlueprintCreation
{
 public static JsonObject PrepareForOwner(JsonObject request, Func<Element,string> format)
 {
  var function=new Parser(request["text"]!.GetValue<string>(),"<existing-function>").ParseElement();
  var owner=new Parser(request["ownerText"]!.GetValue<string>(),"<implementation-owner>").ParseElement();
  if(owner.Kind!="object"||owner.Id!=request["owner"]!.GetValue<string>()||function.Kind!="function"||function.Id!=request["id"]!.GetValue<string>()||function.Signature is null||function.Parent is not null)
   throw new ArgumentException("An owned object and the existing function's explicit contract are required");
  // Reuse only the contract generator. Its temporary default never replaces the real function.
  function.Provides.Clear();if(string.IsNullOrWhiteSpace(function.Description)){function.Description="Implement "+function.Id+" for "+owner.Id;function.DescriptionPresent=true;}var input=(JsonObject)request.DeepClone();input["text"]=format(function);
  var result=Prepare(input,format);result.Remove("function");
  string implementation=request["implementation"]!.GetValue<string>();
  owner.Provides[function.Id]=new ElementReference(implementation,new(),function.Id);
  result["owner"]=format(owner);result["feature"]=function.Id;
  result["signature"]=result["graph"]!["nodes"]![0]!["signature"]!.DeepClone();
  return result;
 }
 public static JsonObject Prepare(JsonObject request, Func<Element,string> format)
 {
  var function=new Parser(request["text"]!.GetValue<string>(),"<new-function>").ParseElement();
  string implementationId=request["implementation"]!.GetValue<string>(),graphPath=request["graphPath"]!.GetValue<string>(),nodePath=request["nodePath"]!.GetValue<string>();
  if(function.Kind!="function"||function.Id!=request["id"]!.GetValue<string>()||function.Signature is null||function.Parent is not null||function.Provides.ContainsKey(function.Id)||PackPaths.Namespace(function.Id)!=PackPaths.Namespace(implementationId))throw new ArgumentException("An owned new function with its exact identity, an explicit signature and no existing implementation is required");
  string signature="("+string.Join(", ",function.Signature.Args.Select(a=>a.Type+" "+a.Name))+") -> "+function.Signature.Return;
  string implementation=$"implementation {implementationId} for {function.Id} {signature} {{blueprint common {System.Text.Json.JsonSerializer.Serialize(graphPath)};}}\n";
  new Parser(implementation,"<new-implementation>").ParseElement();
  function.Provides.Add(function.Id,new ElementReference(implementationId,new(),function.Id));
  var args=new JsonArray();var arguments=new JsonObject();foreach(var arg in function.Signature.Args){args.Add(new JsonObject{["type"]=arg.Type,["name"]=arg.Name});arguments[arg.Name]=new JsonObject{["input"]=arg.Name};}
  var graph=new JsonObject{
   ["schema"]=1,["profile"]=FeatureBlueprint.Profile,["feature"]=function.Id,["contractHash"]=FeatureBlueprint.ContractHash(function),["entry"]="body",
   ["nodes"]=new JsonArray(new JsonObject{["id"]="body",["kind"]="code",["control"]="next",["intent"]=function.Description,["signature"]=new JsonObject{["args"]=args,["return"]=function.Signature.Return},["arguments"]=arguments,["implementation"]=nodePath}),
   ["edges"]=new JsonArray(new JsonObject{["from"]="body",["port"]="next",["to"]="exit:return"}),
   ["exits"]=new JsonObject{["return"]=function.Signature.Return=="void"?null:new JsonObject{["node"]="body"}}
  };
  string text=format(function);var checkedGraph=FeatureBlueprint.Execute(new JsonObject{["operation"]="featureBlueprintNodes",["featureSource"]=text,["graph"]=graph.DeepClone()});
  if(checkedGraph["state"]?.ToString()!="node-definitions")throw new ArgumentException(checkedGraph.ToJsonString());
  return new JsonObject{["function"]=text,["implementation"]=implementation,["graph"]=graph,["node"]=new JsonObject{["schema"]=1,["node"]="body",["definitionHash"]=new string('0',64),["source"]=""}};
 }
}
