using Confectory.Core;
using System.Text.Json.Nodes;

// Explicit whole-body text joins the owner's existing candidate/CAS. This
// adapter never infers a C# edit, a new cell, an alias or a caller binding.
internal static class InformationFunctionWholeBody
{
 internal static JsonObject Prepare(string id, JsonObject graph, Element original, Element requested, Element implementation, string target, JsonObject units, JsonObject plans, JsonObject remap, Func<Element,string> format)
 {
  if(graph["copySource"] is not null)throw new InvalidOperationException("Copy provenance requires its separate explicit source receipt; original copy retained");
  var node=graph["nodes"]!.AsArray().SingleOrDefault(n=>n!["implementationContext"] is not null)??throw new InvalidOperationException("One explicit whole-body context required");
  string recordId=id+"/node:"+node["id"]!.ToString();var unit=units[recordId]?.AsObject()??throw new InvalidOperationException("Original whole-body source missing");
  var plan=plans[recordId]?.AsObject()??throw new InvalidOperationException("Explicitly review the whole C# body and caller storage before changing its contract");
  var before=implementation.Signature!;var selected=InformationFunctionBodies.Signature(plan["signature"]!);
  var expected=new FunctionSignature(before.Args.Select((p,i)=>new Parameter(p.Type,p.Name,requested.Signature!.Args.ElementAtOrDefault(i)?.Mode)).ToList(),before.Return);
  if(!JsonNode.DeepEquals(FeatureBlueprint.SignatureDocument(selected),FeatureBlueprint.SignatureDocument(expected)))throw new InvalidOperationException("Keep exact native names, types, order and out roles; select value/ref explicitly");
  string text=InformationFunctionBodies.Text(recordId,unit["path"]!.ToString(),unit,before,selected,requested.Signature!,plan);
  var modes=new JsonObject(original.Signature!.Args.Where(a=>!a.IsOut).Select(a=>KeyValuePair.Create<string,JsonNode?>(a.Name,JsonValue.Create(requested.Signature!.Args.Single(p=>p.Name==a.Name).IsRef?"ref":"value"))));
  var one=new Parser(format(implementation),"<whole-body-target>").ParseElement();one.Bodies=new(){[target]=implementation.Bodies[target]};
  return BlueprintRootContract.Prepare(new JsonObject{["functionText"]=format(original),["text"]=format(one),["bodyTarget"]=target,["graph"]=graph.DeepClone(),["plan"]=new JsonObject{["args"]=FeatureBlueprint.SignatureDocument(requested.Signature!)["args"]!.DeepClone(),["returnType"]=requested.Signature!.Return,["remap"]=remap.DeepClone(),["inputModes"]=modes,["rootBody"]=new JsonObject{["node"]=node["id"]!.DeepClone(),["source"]=text}}},format);
 }
}
