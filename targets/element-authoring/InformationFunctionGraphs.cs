using Confectory.Core;
using System.Text.Json.Nodes;

// A private graph's parameters and storage belong to its parent graph node.
// Qualified node IDs are identities, never physical paths or new write rights.
internal static class InformationFunctionGraphs
{
 internal sealed record Scope(string Path,JsonObject Graph,FunctionSignature Signature);
 internal static IEnumerable<Scope> Scopes(JsonObject root,FunctionSignature signature)
 {
  var entries=BlueprintTree.Nodes(root).ToArray();if(root["copySource"] is not null||entries.Any(e=>e.Node["graph"]?["copySource"] is not null))throw new InvalidOperationException("Copy/private provenance requires its separate receipt");yield return new("",root,signature);
  foreach(var entry in entries.Where(e=>e.Node["kind"]?.ToString()=="graph"))yield return new(entry.Key,entry.Node["graph"]!.AsObject(),InformationFunctionBodies.Signature(entry.Node["signature"]!));
 }
 internal static string Label(JsonObject root,string path)
 {
  var names=new List<string>();var graph=root;if(path.Length==0)return "";foreach(string id in path.Split('/')){var node=graph["nodes"]!.AsArray().Single(n=>n!["id"]!.ToString()==id)!;names.Add(node["displayName"]?.ToString()??node["intent"]?.ToString()??id);graph=node["graph"]!.AsObject();}return string.Join(" › ",names);
 }
 internal static string Key(string path,string node)=>path.Length==0?node:path+"/"+node;
 internal static IEnumerable<JsonNode> Definitions(JsonObject result)=>result["nodes"]!.AsArray().Concat(result["nestedNodes"] as JsonArray??new()).Select(n=>n!);
 internal static void Bindings(JsonObject graph,Action<JsonNode?> apply)
 {
  foreach(var node in graph["nodes"]!.AsArray())apply(node!["arguments"]);
  foreach(var local in graph["locals"] as JsonArray??new())apply(local!["source"]);
  foreach(var value in graph["exits"]!.AsObject())apply(value.Value);
 }
 internal static void CodeText(string body,string helpers,FunctionSignature signature,JsonObject node)
 {
  string declaration=node["control"]?.ToString()=="switch"?"public enum Result : int {"+string.Join(",",node["executionEnum"]!["members"]!.AsArray().Select(m=>m!["name"]+"="+m["value"]))+"}\n":"";
  string prefix="class PrivateCode {\n"+declaration+"static "+(node["control"]?.ToString()=="switch"?"Result":signature.Return)+" Invoke("+string.Join(",",signature.Args.Select(a=>a.Declaration()))+") {\n";
  var tree=Microsoft.CodeAnalysis.CSharp.CSharpSyntaxTree.ParseText(prefix+body+"\n}\n"+helpers+"\n}",new Microsoft.CodeAnalysis.CSharp.CSharpParseOptions(Microsoft.CodeAnalysis.CSharp.LanguageVersion.CSharp14));var unit=(Microsoft.CodeAnalysis.CSharp.Syntax.CompilationUnitSyntax)tree.GetRoot();var cls=unit.Members.OfType<Microsoft.CodeAnalysis.CSharp.Syntax.ClassDeclarationSyntax>().SingleOrDefault();var method=cls?.Members.OfType<Microsoft.CodeAnalysis.CSharp.Syntax.MethodDeclarationSyntax>().SingleOrDefault(m=>m.Identifier.ValueText=="Invoke");if(tree.GetDiagnostics().Any(d=>d.Severity==Microsoft.CodeAnalysis.DiagnosticSeverity.Error)||unit.Members.Count!=1||cls?.CloseBraceToken.SpanStart!=prefix.Length+body.Length+3+helpers.Length+1||method?.Body?.CloseBraceToken.SpanStart!=prefix.Length+body.Length+1)throw new InvalidOperationException("Private C# text/helpers must retain their protected native boundary");
 }
 internal static int ReadCode(JsonObject result,string id,string text,JsonObject root,Element implementation,string label,string target,JsonObject units)
 {
  if(root["copySource"] is not null)return 0;int bytes=0;
  foreach(var entry in BlueprintTree.Nodes(root).Where(e=>e.Key.Contains('/')&&e.Node["kind"]?.ToString()=="code"&&e.Node["control"]?.ToString() is "next" or "branch" or "switch"&&e.Node["implementationContext"] is null)){
   string recordId=BlueprintTree.SourceId(id,entry.Key);var unit=units[recordId]??throw new InvalidOperationException("Original qualified private source missing");BlueprintDocuments.Validate(recordId,"blueprint-node",unit["draft"]!.ToString());var record=JsonNode.Parse(unit["draft"]!.ToString())!;string helpers=record["helpers"]?.GetValue<string>()??"";bytes=checked(bytes+System.Text.Encoding.UTF8.GetByteCount(record["source"]!.GetValue<string>()+helpers));
   result.Add(recordId,new JsonObject{["sourceKind"]="scoped-code-csharp",["name"]=label+" · 내부 "+Label(root,entry.Key[..entry.Key.LastIndexOf('/')])+" · "+(entry.Node["displayName"]?.ToString()??entry.Node["intent"]?.ToString()??entry.Node["id"]!.ToString()),["control"]=entry.Node["control"]!.DeepClone(),["executionEnum"]=entry.Node["executionEnum"]?.DeepClone(),["helperEditor"]=(entry.Node["control"]?.ToString() is "branch" or "switch"||helpers.Length>0)&&FeatureBlueprint.SupportsMethods(BlueprintTree.Select(root,entry.Key[..entry.Key.LastIndexOf('/')])["profile"]?.ToString()),["helpers"]=helpers,["caller"]=true,["implementation"]=implementation.Id,["target"]=target,["function"]=implementation.Function,["graph"]=id,["node"]=entry.Key,["path"]=unit["path"]!.DeepClone(),["hash"]=JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(unit["draft"]!.ToString())),["signature"]=entry.Node["signature"]!.DeepClone(),["contractSignature"]=entry.Node["signature"]!.DeepClone(),["text"]=record["source"]!.DeepClone(),["whole"]=InformationFunctionWholeBody.Receipt(id,text,root,entry.Node,entry.Key)});if(result.Count>32)throw new ArgumentException("Explicit private C# selection budget");
  }return bytes;
 }
 internal static string Text(string id,string graphText,JsonObject root,string key,JsonObject before,JsonObject unit,Element current,JsonObject plan)
 {
  if(root["copySource"] is not null||plan.Count!=7+(plan.ContainsKey("helpers")?1:0)||!JsonNode.DeepEquals(plan["whole"],InformationFunctionWholeBody.Receipt(id,graphText,root,before,key))||before["kind"]?.ToString()!="code"||before["control"]?.ToString() is not ("next" or "branch" or "switch")||before["implementationContext"] is not null)throw new InvalidOperationException("Exact original private code/context and explicit text required");
  var native=InformationFunctionBodies.Signature(before["signature"]!);var explicitPlan=plan.DeepClone().AsObject();explicitPlan.Remove("whole");explicitPlan.Remove("helpers");string helpers=plan["helpers"]?.GetValue<string>()??JsonNode.Parse(unit["draft"]!.ToString())!["helpers"]?.GetValue<string>()??"";if(helpers.Length>65536)throw new ArgumentException("Private helper byte budget");string value=InformationFunctionBodies.Text(BlueprintTree.SourceId(id,key),unit["path"]!.ToString(),unit,native,native,current.Signature!,explicitPlan);CodeText(value,helpers,native,before);return value;
 }
}
