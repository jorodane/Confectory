using System.Text.Json.Nodes;
using Confectory.Core;

// No source writes. Legacy3/4 validation is pure; multi-target groups may
// explicitly recheck registered receipts at Save, Review and Confirm.
static class BlueprintRootGroup
{
 public static JsonObject Validate(JsonObject request)
 {
  if(request["group"]!.AsArray().Count>4)return BlueprintCallAbiGroup.ValidateGroup(request);
  var group=request["group"]!.AsArray();var units=request["units"]!.AsObject();string ns=request["namespace"]!.GetValue<string>();var ids=group.Select(p=>p!.GetValue<string>()).ToArray();
  if(ids.Length is not (3 or 4)||ids.Distinct(StringComparer.Ordinal).Count()!=ids.Length||ids.Any(id=>!id.StartsWith(ns+"::",StringComparison.Ordinal)||units[id] is null||!JsonNode.DeepEquals(units[id]!["rootContractGroup"],group)))throw new ArgumentException("Exact root group membership required");
  if(units[ids[0]]!["kind"]?.ToString()!="function"||units[ids[1]]!["kind"]?.ToString()!="implementation"||units[ids[2]]!["kind"]?.ToString()!="blueprint"||!ids[2].StartsWith(ids[1]+"/body:",StringComparison.Ordinal))throw new ArgumentException("Root group kinds required");
  if(ids.Length==4){
   var fn=new Parser(units[ids[0]]!["draft"]!.GetValue<string>(),"<group-function>").ParseElement();var impl=new Parser(units[ids[1]]!["draft"]!.GetValue<string>(),"<group-implementation>").ParseElement();var graph=JsonNode.Parse(units[ids[2]]!["draft"]!.GetValue<string>())!.AsObject();string target=ids[2][(ids[1].Length+6)..];
   if(fn.Id!=ids[0]||impl.Id!=ids[1]||impl.Function!=fn.Id||impl.Parent is not null||impl.Bodies.Count!=1||!impl.Bodies.TryGetValue(target,out var body)||body.SourceKind!="blueprint"||body.Path!=units[ids[2]]!["path"]!.ToString()||!fn.Signature!.Matches(impl.Signature)||graph["feature"]?.ToString()!=fn.Id||graph["contractHash"]?.ToString()!=FeatureBlueprint.ContractHash(fn))throw new ArgumentException("Exact root/body declaration group required");
   if(units[ids[3]]!["kind"]?.ToString()!="blueprint-node"||!ids[3].StartsWith(ids[2]+"/node:",StringComparison.Ordinal))throw new ArgumentException("Fourth member is the root's own body node");
   string nodeId=ids[3][(ids[2].Length+6)..];var node=graph["nodes"]!.AsArray().SingleOrDefault(n=>n!["id"]?.ToString()==nodeId);
   if(node?["kind"]?.ToString()!="code"||node["control"]?.ToString()!="next"||!JsonNode.DeepEquals(node["implementationContext"],FeatureBlueprint.ImplementationContext(impl))||!JsonNode.DeepEquals(node["signature"],FeatureBlueprint.SignatureDocument(impl.Signature!))||graph["entry"]?.ToString()!=nodeId||graph["nodes"]!.AsArray().Count(n=>n!["implementationContext"] is not null)!=1)throw new ArgumentException("Fourth member requires the exact whole-body context");
   string root=Path.GetFullPath(Path.Combine(Path.GetTempPath(),"confectory-pure-root-group"))+Path.DirectorySeparatorChar;string graphPath=Path.GetFullPath(Path.Combine(root,units[ids[2]]!["path"]!.ToString())),nodePath=Path.GetFullPath(Path.Combine(Path.GetDirectoryName(graphPath)!,node["implementation"]!.GetValue<string>())),memberPath=Path.GetFullPath(Path.Combine(root,units[ids[3]]!["path"]!.ToString()));var comparison=OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal;
   if(!graphPath.StartsWith(root,comparison)||!nodePath.StartsWith(root,comparison)||!nodePath.Equals(memberPath,comparison))throw new ArgumentException("Owned root body locator required");BlueprintDocuments.Validate(ids[3],"blueprint-node",units[ids[3]]!["draft"]!.GetValue<string>());
   if(impl.Imports.Count>0)throw new ArgumentException("Imported whole-body root groups require explicit complete contracts");
   var definitions=FeatureBlueprint.Execute(new JsonObject{["operation"]="featureBlueprintNodes",["featureSource"]=units[ids[0]]!["draft"]!.DeepClone(),["graph"]=graph.DeepClone(),["implementationContext"]=FeatureBlueprint.ImplementationContext(impl),["featureContracts"]=new JsonObject()});
   var record=JsonNode.Parse(units[ids[3]]!["draft"]!.GetValue<string>())!;if(definitions["state"]?.ToString()!="node-definitions"||record["definitionHash"]?.ToString()!=definitions["nodes"]!.AsArray().Single(n=>n!["id"]!.ToString()==nodeId)!["definitionHash"]!.ToString())throw new ArgumentException("Fourth member's current context receipt required");
  }
  return new JsonObject{["valid"]=true,["ids"]=group.DeepClone(),["sourceWritten"]=false,["executed"]=false};
 }
}
