using Confectory.Core;
using System.Text.Json.Nodes;

// A private graph's parameters and storage belong to its parent graph node.
// Qualified node IDs are identities, never physical paths or new write rights.
internal static class InformationFunctionGraphs
{
 // A private code parameter owns a positional binding independently of the
 // enclosing frame. One explicit name change retains its type/value role and
 // original input expression; source text is always supplied by the user.
 internal static bool Nameable(JsonObject node)=>node["kind"]?.ToString()=="code"&&node["control"]?.ToString()=="next"&&node["implementationContext"] is null&&node["forwardCallerStorage"]?.GetValue<bool>()!=true&&node["signature"] is JsonObject signature&&signature["args"] is JsonArray args&&args.Count is >0 and <=32&&args.All(a=>a?["mode"] is null&&a?["type"]?.ToString() is "bool" or "int" or "long" or "float" or "double" or "string");
 internal static bool Names(JsonNode plan)
 {
  if(plan["whole"]?["node"]?.ToString().Contains('/')!=true||plan["beforeSignature"] is not JsonObject before||plan["signature"] is not JsonObject after)return false;
  var a=InformationFunctionBodies.Signature(before);var b=InformationFunctionBodies.Signature(after);
  return a.Return==b.Return&&a.Args.Count is >0 and <=32&&a.Args.Count==b.Args.Count&&a.Args.Where((pin,i)=>pin.Name!=b.Args[i].Name).Count()==1&&b.Args.Select(pin=>pin.Name).Distinct(StringComparer.Ordinal).Count()==b.Args.Count&&a.Args.Select((pin,i)=>(pin.Type is "bool" or "int" or "long" or "float" or "double" or "string")&&pin.Type==b.Args[i].Type&&pin.Mode is null&&b.Args[i].Mode is null&&!a.Args.Where((other,j)=>j!=i).Any(other=>other.Name==b.Args[i].Name)).All(value=>value);
 }
 // Untyped integer literals already take their declared parameter type in the
 // generator. This finite long->double edit preserves an exact int32 literal;
 // input/storage expressions and explicitly typed literals keep separate plans.
 internal static bool Types(JsonNode plan)
 {
  if(plan["whole"]?["node"]?.ToString().Contains('/')!=true||plan["beforeSignature"] is not JsonObject before||plan["signature"] is not JsonObject after)return false;
  var a=InformationFunctionBodies.Signature(before);var b=InformationFunctionBodies.Signature(after);
  return a.Return==b.Return&&a.Args.Count is >0 and <=32&&a.Args.Count==b.Args.Count&&a.Args.Where((pin,i)=>pin.Type!=b.Args[i].Type).Count()==1&&a.Args.Select((pin,i)=>pin.Name==b.Args[i].Name&&pin.Mode is null&&b.Args[i].Mode is null&&(pin.Type==b.Args[i].Type||pin.Type=="long"&&b.Args[i].Type=="double")).All(value=>value);
 }
 internal static JsonArray LiteralInputs(JsonObject node)
 {
  var names=new JsonArray();if(!Nameable(node)||node["arguments"] is not JsonObject inputs)return names;
  foreach(var pin in InformationFunctionBodies.Signature(node["signature"]!).Args)if(pin.Type=="long"&&inputs[pin.Name] is JsonObject binding&&binding.Count==1&&binding["constant"] is JsonValue value&&value.TryGetValue<int>(out _))names.Add(pin.Name);
  return names;
 }
 // The explicit last-parameter deletion owns exactly its original literal
 // binding. Parent inputs/storage and all retained positions keep separate plans.
 internal static bool Removes(JsonNode plan)
 {
  if(plan["whole"]?["node"]?.ToString().Contains('/')!=true||plan["beforeSignature"] is not JsonObject before||plan["signature"] is not JsonObject after)return false;
  var a=InformationFunctionBodies.Signature(before);var b=InformationFunctionBodies.Signature(after);
  return a.Return=="long"&&b.Return==a.Return&&a.Args.Count==2&&b.Args.Count==1&&a.Args[0].Name==b.Args[0].Name&&a.Args[0].Type==b.Args[0].Type&&a.Args[0].Mode is null&&b.Args[0].Mode is null&&a.Args[1].Mode is null;
 }
 internal static JsonArray RemovableInputs(JsonObject node)
 {
  if(!Nameable(node)||node["signature"]?["return"]?.ToString()!="long"||node["signature"]?["args"] is not JsonArray args||args.Count!=2)return new JsonArray();
  string last=args[1]!["name"]!.ToString();return LiteralInputs(node).Any(name=>name?.ToString()==last)?new JsonArray(last):new JsonArray();
 }
 // A declaration permutation retains each original name-bound value. Limit
 // this first structural flow to pure parameter reads and exact literals.
 internal static bool Reorders(JsonNode plan)
 {
  if(plan["whole"]?["node"]?.ToString().Contains('/')!=true||plan["beforeSignature"] is not JsonObject before||plan["signature"] is not JsonObject after)return false;
  var a=InformationFunctionBodies.Signature(before);var b=InformationFunctionBodies.Signature(after);
  return a.Return=="long"&&b.Return==a.Return&&a.Args.Count==2&&b.Args.Count==2&&a.Args[0].Name!=a.Args[1].Name&&a.Args.All(pin=>pin.Type=="long"&&pin.Mode is null)&&b.Args.All(pin=>pin.Type=="long"&&pin.Mode is null)&&a.Args[0].Name==b.Args[1].Name&&a.Args[1].Name==b.Args[0].Name;
 }
 internal static bool Reorderable(JsonObject node)
 {
  if(!Nameable(node)||node["signature"]?["return"]?.ToString()!="long"||node["arguments"] is not JsonObject inputs||inputs.Count!=2)return false;
  var signature=InformationFunctionBodies.Signature(node["signature"]!);
  return signature.Args.Count==2&&signature.Args.All(pin=>pin.Type=="long"&&inputs[pin.Name] is JsonObject binding&&binding.Count==1&&(binding["input"] is JsonValue input&&input.TryGetValue<string>(out var name)&&!string.IsNullOrWhiteSpace(name)||binding["constant"] is JsonValue value&&value.TryGetValue<int>(out _)));
 }
 // Changing an unused private return owns no caller remap. Scan the entire
 // original enclosing scope, including local sources and exits; never discard
 // a use or infer a new output connection as part of the source plan.
 internal static bool Returns(JsonNode plan)
 {
  if(plan["whole"]?["node"]?.ToString().Contains('/')!=true||plan["beforeSignature"] is not JsonObject before||plan["signature"] is not JsonObject after)return false;
  return before["return"]?.ToString()=="long"&&(after["return"]?.ToString() is "double" or "void")&&JsonNode.DeepEquals(before["args"],after["args"]);
 }
 internal static bool UnusedReturn(JsonObject root,string key,JsonObject node)
 {
  if(!key.Contains('/')||!Nameable(node)||node["signature"]?["return"]?.ToString()!="long")return false;
  bool used=false;string id=node["id"]!.ToString();
  void Uses(JsonNode? value){if(value is JsonObject item){if(item["node"]?.ToString()==id){used=true;return;}foreach(var part in item)if(part.Key!="constant")Uses(part.Value);}else if(value is JsonArray array)foreach(var part in array)Uses(part);}
  Bindings(BlueprintTree.Select(root,key[..key.LastIndexOf('/')]),Uses);return !used;
 }
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
 internal static bool RootCodeGraph(JsonObject root)=>root["nodes"]!.AsArray().All(node=>node?["implementationContext"] is null&&node?["forwardCallerStorage"]?.GetValue<bool>()!=true);
 // Retained native context and independent code keep separate ABIs. A root
 // source can be paired only with its explicitly reviewed original context.
 internal static bool HasRetainedContext(JsonObject root,Element implementation)
 {
  var contexts=root["nodes"]!.AsArray().Where(node=>node?["implementationContext"] is not null||node?["forwardCallerStorage"]?.GetValue<bool>()==true).ToArray();
  return root["copySource"] is null&&contexts.Length==1&&contexts[0]?["kind"]?.ToString()=="code"&&contexts[0]?["control"]?.ToString()=="next"&&JsonNode.DeepEquals(contexts[0]?["implementationContext"],FeatureBlueprint.ImplementationContext(implementation))&&JsonNode.DeepEquals(contexts[0]?["signature"],FeatureBlueprint.SignatureDocument(implementation.Signature!));
 }
 internal static bool RetainedCodePlans(string id,string graphText,JsonObject root,Element implementation,Element feature,JsonObject units,JsonObject plans)
 {
  if(!HasRetainedContext(root,implementation))return false;
  var context=root["nodes"]!.AsArray().Single(node=>node?["implementationContext"] is not null)!.AsObject();string source=BlueprintTree.SourceId(id,context["id"]!.ToString());var native=implementation.Signature!;var outputs=FeatureBlueprint.FeatureOutputs(native).ToArray();
  if(plans[source] is not JsonObject plan||plan.Count!=8||!JsonNode.DeepEquals(plan["beforeSignature"],context["signature"])||!JsonNode.DeepEquals(plan["signature"],context["signature"])||!JsonNode.DeepEquals(plan["contract"],FeatureBlueprint.SignatureDocument(feature.Signature!))||!JsonNode.DeepEquals(plan["whole"],InformationFunctionWholeBody.Receipt(id,graphText,root,context))||plan["outputs"] is not JsonObject selected||selected.Count!=outputs.Length||outputs.Any(output=>selected[output.Name]?.ToString()!=output.Name)||units[source] is not JsonObject unit||unit["kind"]?.ToString()!="blueprint-node")return false;
  var explicitPlan=plan.DeepClone().AsObject();explicitPlan.Remove("whole");explicitPlan.Remove("outputs");InformationFunctionBodies.Text(source,unit["path"]!.ToString(),unit,native,native,feature.Signature!,explicitPlan);return true;
 }
 internal static int ReadCode(JsonObject result,string id,string text,JsonObject root,Element implementation,string label,string target,JsonObject units,bool includeRoot=false)
 {
  if(root["copySource"] is not null)return 0;int bytes=0;
  foreach(var entry in BlueprintTree.Nodes(root).Where(e=>(e.Key.Contains('/')||includeRoot&&(RootCodeGraph(root)||HasRetainedContext(root,implementation)))&&e.Node["kind"]?.ToString()=="code"&&e.Node["control"]?.ToString() is "next" or "branch" or "switch"&&e.Node["implementationContext"] is null)){
   string scope=entry.Key.Contains('/')?entry.Key[..entry.Key.LastIndexOf('/')]:"";string recordId=BlueprintTree.SourceId(id,entry.Key);var unit=units[recordId]??throw new InvalidOperationException("Original qualified private source missing");BlueprintDocuments.Validate(recordId,"blueprint-node",unit["draft"]!.ToString());var record=JsonNode.Parse(unit["draft"]!.ToString())!;string helpers=record["helpers"]?.GetValue<string>()??"";bytes=checked(bytes+System.Text.Encoding.UTF8.GetByteCount(record["source"]!.GetValue<string>()+helpers));
   result.Add(recordId,new JsonObject{["sourceKind"]="scoped-code-csharp",["editableNativeNames"]=scope.Length>0&&Nameable(entry.Node),["editableNativeTypes"]=scope.Length>0?LiteralInputs(entry.Node):new JsonArray(),["editableNativeReturn"]=UnusedReturn(root,entry.Key,entry.Node),["removableNativeInputs"]=scope.Length>0?RemovableInputs(entry.Node):new JsonArray(),["editableNativeOrder"]=scope.Length>0&&Reorderable(entry.Node),["name"]=label+(scope.Length==0?" · 노드 ":" · 내부 "+Label(root,scope)+" · ")+(entry.Node["displayName"]?.ToString()??entry.Node["intent"]?.ToString()??entry.Node["id"]!.ToString()),["control"]=entry.Node["control"]!.DeepClone(),["executionEnum"]=entry.Node["executionEnum"]?.DeepClone(),["helperEditor"]=(entry.Node["control"]?.ToString() is "branch" or "switch"||helpers.Length>0)&&FeatureBlueprint.SupportsMethods(BlueprintTree.Select(root,scope)["profile"]?.ToString()),["helpers"]=helpers,["caller"]=true,["implementation"]=implementation.Id,["target"]=target,["function"]=implementation.Function,["graph"]=id,["node"]=entry.Key,["path"]=unit["path"]!.DeepClone(),["hash"]=JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(unit["draft"]!.ToString())),["signature"]=entry.Node["signature"]!.DeepClone(),["contractSignature"]=entry.Node["signature"]!.DeepClone(),["text"]=record["source"]!.DeepClone(),["whole"]=InformationFunctionWholeBody.Receipt(id,text,root,entry.Node,entry.Key)});if(result.Count>32)throw new ArgumentException("Explicit private C# selection budget");
  }return bytes;
 }
 internal static string Text(string id,string graphText,JsonObject root,string key,JsonObject before,JsonObject unit,Element current,JsonObject plan,bool retainedContext=false,JsonObject? after=null)
 {
  if(root["copySource"] is not null||!key.Contains('/')&&!RootCodeGraph(root)&&!retainedContext||plan.Count!=7+(plan.ContainsKey("helpers")?1:0)||!JsonNode.DeepEquals(plan["whole"],InformationFunctionWholeBody.Receipt(id,graphText,root,before,key))||before["kind"]?.ToString()!="code"||before["control"]?.ToString() is not ("next" or "branch" or "switch")||before["implementationContext"] is not null)throw new InvalidOperationException("Exact original private code/context and explicit text required");
  var native=InformationFunctionBodies.Signature(before["signature"]!);var selected=native;
  if(!JsonNode.DeepEquals(plan["beforeSignature"],plan["signature"])){
   if(after is null||!Nameable(before)||!Names(plan)&&!Types(plan)&&!Returns(plan)&&!Removes(plan)&&!Reorders(plan)||!JsonNode.DeepEquals(after["signature"],before["signature"])||!JsonNode.DeepEquals(after["arguments"],before["arguments"]))throw new InvalidOperationException("Select one explicit private parameter edit, an unused return edit, eligible literal parameter deletion or original two-value parameter order; retain the parent contract and every remaining binding");
   selected=InformationFunctionBodies.Signature(plan["signature"]!);var inputs=before["arguments"]!.AsObject();if(inputs.Count!=native.Args.Count||native.Args.Any(pin=>!inputs.ContainsKey(pin.Name)))throw new InvalidOperationException("Every original private input binding is required");
   if(Types(plan)){string changed=native.Args.Where((pin,i)=>pin.Type!=selected.Args[i].Type).Single().Name;if(!LiteralInputs(before).Any(name=>name?.ToString()==changed))throw new InvalidOperationException("Select an unchanged exact int32 literal for long-to-double; input/storage, typed literals and precision changes require their separate explicit binding plan");}
   if(Returns(plan)&&!UnusedReturn(root,key,before))throw new InvalidOperationException("Private return changes require an unused original output; preserve all consumers, frame and caller contracts");
   if(Removes(plan)&&!RemovableInputs(before).Any(name=>name?.ToString()==native.Args[1].Name))throw new InvalidOperationException("Select the exact original last int32 literal binding for private parameter removal; typed literals, input/storage and other declaration changes require their separate explicit plan");
   if(Reorders(plan)&&!Reorderable(before))throw new InvalidOperationException("Select two original long value parameters with simple original input or int32 literal bindings for private order; local/alias, typed/wide literals and mixed declarations require separate explicit plans");
   var bindings=new JsonObject();if(Removes(plan)||Reorders(plan)){foreach(var pin in selected.Args)bindings[pin.Name]=inputs[pin.Name]?.DeepClone();}else for(int i=0;i<native.Args.Count;i++)bindings[selected.Args[i].Name]=inputs[native.Args[i].Name]?.DeepClone();after["signature"]=plan["signature"]!.DeepClone();after["arguments"]=bindings;
  }
  var explicitPlan=plan.DeepClone().AsObject();explicitPlan.Remove("whole");explicitPlan.Remove("helpers");string helpers=plan["helpers"]?.GetValue<string>()??JsonNode.Parse(unit["draft"]!.ToString())!["helpers"]?.GetValue<string>()??"";if(helpers.Length>65536)throw new ArgumentException("Private helper byte budget");string value=InformationFunctionBodies.Text(BlueprintTree.SourceId(id,key),unit["path"]!.ToString(),unit,native,selected,current.Signature!,explicitPlan);CodeText(value,helpers,selected,before);return value;
 }
}
