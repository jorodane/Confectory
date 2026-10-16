using Confectory.Core;
using System.Text.Json.Nodes;

internal static class BlueprintCreation
{
 public static JsonObject PrepareForOwner(JsonObject request, Func<Element,string> format)
 {
  var function=new Parser(request["text"]!.GetValue<string>(),"<existing-function>").ParseElement();
  var owner=new Parser(request["ownerText"]!.GetValue<string>(),"<implementation-owner>").ParseElement();
  if(owner.Kind!="object"||owner.Id!=request["owner"]!.GetValue<string>()||function.Kind!="function"||function.Id!=request["id"]!.GetValue<string>()||function.Signature is null||function.Parent is not null||PackPaths.Namespace(owner.Id)!=PackPaths.Namespace(request["implementation"]!.GetValue<string>()))
   throw new ArgumentException("An owned object and the existing function's explicit contract are required");
  // Reuse only the contract generator. Its temporary default never replaces the real function.
  function.Provides.Clear();if(string.IsNullOrWhiteSpace(function.Description)){function.Description="Implement "+function.Id+" for "+owner.Id;function.DescriptionPresent=true;}var input=(JsonObject)request.DeepClone();input["text"]=format(function);
  var slotSignature=function.Signature!;
  var result=request["reference"] is null?Scaffold(function,input,format):ReferenceScaffold(function,input,format);result.Remove("function");
  string implementation=request["implementation"]!.GetValue<string>();
  owner.Provides[function.Id]=new ElementReference(implementation,new(),function.Id);
  result["owner"]=format(owner);result["feature"]=function.Id;
  result["signature"]=SignatureNode(slotSignature);
  return result;
 }
 private static JsonObject SignatureNode(FunctionSignature signature)=>new(){["args"]=new JsonArray(signature.Args.Select(arg=>(JsonNode)new JsonObject{["type"]=arg.Type,["name"]=arg.Name}).ToArray()),["return"]=signature.Return};
 private static JsonObject ReferenceScaffold(Element function,JsonObject request,Func<Element,string> format)
 {
  string reference=request["reference"]!.GetValue<string>(),referenceText=request["referenceText"]!.GetValue<string>();
  var donor=new Parser(referenceText,"<referenced-function>").ParseElement();var signature=function.Signature??throw new ArgumentException("Explicit required function signature");
  if(donor.Kind!="function"||donor.Id!=reference||donor.Id==function.Id||donor.Signature is null||!signature.Matches(donor.Signature))throw new ArgumentException("Select a different published function with identical input/output types and order");
  string implementationId=request["implementation"]!.GetValue<string>(),graphPath=request["graphPath"]!.GetValue<string>();
  string implementation=$"implementation {implementationId} for {function.Id} ("+string.Join(", ",signature.Args.Select(arg=>arg.Type+" "+arg.Name))+") -> "+signature.Return+" {blueprint common "+System.Text.Json.JsonSerializer.Serialize(graphPath)+";}\n";
  var graph=new JsonObject{["schema"]=1,["profile"]=FeatureBlueprint.Profile,["feature"]=function.Id,["contractHash"]=FeatureBlueprint.ContractHash(function),["entry"]="imported",["nodes"]=new JsonArray(),["edges"]=new JsonArray(),["exits"]=new JsonObject{["return"]=signature.Return=="void"?null:new JsonObject{["node"]="imported"}}};
  var prepared=BlueprintCall.Prepare(new JsonObject{["id"]=implementationId,["text"]=implementation,["targetText"]=referenceText,["graph"]=graph,["definition"]=new JsonObject{["id"]="imported",["feature"]=reference,["intent"]="Call "+reference+" for "+function.Id,["control"]="next"}},format);
  graph=prepared["graph"]!.AsObject();var arguments=graph["nodes"]![0]!["arguments"]!.AsObject();for(int index=0;index<signature.Args.Count;index++)arguments[donor.Signature.Args[index].Name]=new JsonObject{["input"]=signature.Args[index].Name};
  graph["edges"]!.AsArray().Add(new JsonObject{["from"]="imported",["port"]="next",["to"]="exit:return"});function.Provides.Add(function.Id,new ElementReference(implementationId,new(),function.Id));
  string text=format(function);var checkedGraph=FeatureBlueprint.Execute(new JsonObject{["operation"]="featureBlueprintNodes",["featureSource"]=text,["featureContracts"]=new JsonObject{[reference]=referenceText},["graph"]=graph.DeepClone()});if(checkedGraph["state"]?.ToString()!="node-definitions")throw new ArgumentException(checkedGraph.ToJsonString());
  return new JsonObject{["function"]=text,["implementation"]=prepared["implementation"]!.DeepClone(),["graph"]=graph.DeepClone(),["reference"]=reference,["referenceSignature"]=SignatureNode(donor.Signature),["scope"]=prepared["scope"]?.DeepClone()};
 }
 public static JsonObject Prepare(JsonObject request, Func<Element,string> format)
 {
  var function=new Parser(request["text"]!.GetValue<string>(),"<new-function>").ParseElement();
  string implementationId=request["implementation"]!.GetValue<string>();
  if(function.Kind!="function"||function.Id!=request["id"]!.GetValue<string>()||function.Signature is null||function.Parent is not null||function.Provides.ContainsKey(function.Id)||PackPaths.Namespace(function.Id)!=PackPaths.Namespace(implementationId))throw new ArgumentException("An owned new function with its exact identity, an explicit signature and no existing implementation is required");
  return Scaffold(function,request,format);
 }
 private static JsonObject Scaffold(Element function,JsonObject request,Func<Element,string> format)
 {
  string implementationId=request["implementation"]!.GetValue<string>(),graphPath=request["graphPath"]!.GetValue<string>(),nodePath=request["nodePath"]!.GetValue<string>();
  var functionSignature=function.Signature??throw new ArgumentException("Explicit function signature required");
  string signature="("+string.Join(", ",functionSignature.Args.Select(a=>a.Type+" "+a.Name))+") -> "+functionSignature.Return;
  string implementation=$"implementation {implementationId} for {function.Id} {signature} {{blueprint common {System.Text.Json.JsonSerializer.Serialize(graphPath)};}}\n";
  new Parser(implementation,"<new-implementation>").ParseElement();
  function.Provides.Add(function.Id,new ElementReference(implementationId,new(),function.Id));
  var args=new JsonArray();var arguments=new JsonObject();foreach(var arg in functionSignature.Args){args.Add(new JsonObject{["type"]=arg.Type,["name"]=arg.Name});arguments[arg.Name]=new JsonObject{["input"]=arg.Name};}
  var graph=new JsonObject{
   ["schema"]=1,["profile"]=FeatureBlueprint.Profile,["feature"]=function.Id,["contractHash"]=FeatureBlueprint.ContractHash(function),["entry"]="body",
   ["nodes"]=new JsonArray(new JsonObject{["id"]="body",["kind"]="code",["control"]="next",["intent"]=function.Description,["signature"]=new JsonObject{["args"]=args,["return"]=functionSignature.Return},["arguments"]=arguments,["implementation"]=nodePath}),
   ["edges"]=new JsonArray(new JsonObject{["from"]="body",["port"]="next",["to"]="exit:return"}),
   ["exits"]=new JsonObject{["return"]=functionSignature.Return=="void"?null:new JsonObject{["node"]="body"}}
  };
  string text=format(function);var checkedGraph=FeatureBlueprint.Execute(new JsonObject{["operation"]="featureBlueprintNodes",["featureSource"]=text,["graph"]=graph.DeepClone()});
  if(checkedGraph["state"]?.ToString()!="node-definitions")throw new ArgumentException(checkedGraph.ToJsonString());
  return new JsonObject{["function"]=text,["implementation"]=implementation,["graph"]=graph,["node"]=new JsonObject{["schema"]=1,["node"]="body",["definitionHash"]=new string('0',64),["source"]=""}};
 }
}
