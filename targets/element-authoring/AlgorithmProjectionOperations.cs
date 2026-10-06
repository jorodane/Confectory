using System.Text.Json;
using System.Text.Json.Nodes;
using System.Security.Cryptography;
using System.Text;
using Confectory.Core;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
public static class AlgorithmProjectionOperations
{
 public static JsonObject Editor(Element element)
 {
  var help=new JsonObject();var tags=new JsonArray();foreach(var item in element.Values){if(item.Key.StartsWith("editorHelp",StringComparison.Ordinal)||item.Key.StartsWith("editorTag",StringComparison.Ordinal))help[item.Key]=JsonSerializer.SerializeToNode(item.Value.Value);if(item.Key=="editorTags"&&item.Value.Value.ValueKind==JsonValueKind.String)foreach(string tag in (item.Value.Value.GetString()??"").Split(',',StringSplitOptions.TrimEntries|StringSplitOptions.RemoveEmptyEntries))tags.Add(tag);}
  return new JsonObject{["element"]=element.Id,["description"]=element.Description,["tags"]=tags,["help"]=help,["format"]="current declaration description and editorHelp/editorTag value metadata"};
 }
 public static JsonNode Execute(JsonNode request)
 {
 var analysisWatch=System.Diagnostics.Stopwatch.StartNew();int projectedNodes=0;
 string contract=request["contract"]!.GetValue<string>(),implementation=request["implementation"]!.GetValue<string>(),body=request["body"]!.GetValue<string>();
 if(contract.Length>65536||implementation.Length>65536||body.Length>262144)throw new ArgumentException("Bounded selected function/implementation/body required");
 var function=new Parser(contract,"<contract>").ParseElement();var provider=new Parser(implementation,"<implementation>").ParseElement();
 if(function.Kind!="function"||provider.Kind!="implementation"||provider.Function!=function.Id||!function.Signature!.Matches(provider.Signature))throw new ArgumentException("Selected implementation must match its public function contract");
 const string prefix="class ProjectionContainer { void Body() {\n";var tree=CSharpSyntaxTree.ParseText(prefix+body+"\n}}",new CSharpParseOptions(LanguageVersion.Latest));
 var errors=new JsonArray();foreach(var diagnostic in tree.GetDiagnostics().Where(x=>x.Severity==DiagnosticSeverity.Error))errors.Add(new JsonObject{["code"]=diagnostic.Id,["line"]=Math.Max(1,diagnostic.Location.GetLineSpan().StartLinePosition.Line),["message"]="C# syntax diagnostic; source details remain local"});
 var method=tree.GetRoot().DescendantNodes().OfType<MethodDeclarationSyntax>().FirstOrDefault(m=>m.Identifier.ValueText=="Body");
 var imports=new JsonArray();foreach(var (alias,import) in provider.Imports)imports.Add(new JsonObject{["id"]=import.Id});
 string Label(SyntaxNode node)=>node switch {IfStatementSyntax=>"conditional branch",ElseClauseSyntax=>"alternative branch",BlockSyntax=>"sequence",ForStatementSyntax or ForEachStatementSyntax or WhileStatementSyntax or DoStatementSyntax=>"iteration",ReturnStatementSyntax=>"return",ThrowStatementSyntax=>"explicit exception",TryStatementSyntax=>"exception region",CatchClauseSyntax=>"exception handler",FinallyClauseSyntax=>"finalization",InvocationExpressionSyntax=>"call",AssignmentExpressionSyntax=>"assignment; destination/alias effects unverified",LocalDeclarationStatementSyntax=>"local declaration",AwaitExpressionSyntax=>"asynchronous suspension",LambdaExpressionSyntax=>"deferred callable",_=>"syntax operation"};
 bool Essential(SyntaxNode n)=>n is StatementSyntax or ElseClauseSyntax or CatchClauseSyntax or FinallyClauseSyntax or SwitchSectionSyntax or LambdaExpressionSyntax or AwaitExpressionSyntax or InvocationExpressionSyntax or AssignmentExpressionSyntax;
 JsonObject Project(SyntaxNode node)
 {
  if(++projectedNodes>8192||node.Ancestors().Count()>24)return new JsonObject{["kind"]="unavailable",["label"]="analysis limit reached",["line"]=1,["children"]=new JsonArray()};
  string kind=node switch{IfStatementSyntax=>"branch",ElseClauseSyntax=>"else",FinallyClauseSyntax=>"finally",SwitchStatementSyntax=>"switch",SwitchSectionSyntax=>"case",LambdaExpressionSyntax=>"lambda",LocalFunctionStatementSyntax=>"local-function",ForStatementSyntax or ForEachStatementSyntax or WhileStatementSyntax or DoStatementSyntax=>"loop",TryStatementSyntax=>"try",CatchClauseSyntax=>"catch",ThrowStatementSyntax=>"throw",ReturnStatementSyntax=>"return",AwaitExpressionSyntax=>"await",InvocationExpressionSyntax=>"call",AssignmentExpressionSyntax=>"assignment",LocalDeclarationStatementSyntax=>"declaration",BlockSyntax=>"block",_=>"statement"};
  var children=new JsonArray();IEnumerable<SyntaxNode> selected=node is BlockSyntax block?block.Statements:node.ChildNodes();foreach(var child in selected){if(Essential(child))children.Add(Project(child));else foreach(var nested in child.DescendantNodesAndSelf().Where(Essential).Where(n=>!n.Ancestors().TakeWhile(a=>a!=child).Any(Essential)))children.Add(Project(nested));}
  string? callee=null;if(node is InvocationExpressionSyntax invocation&&invocation.Expression is MemberAccessExpressionSyntax invoke&&invoke.Name.Identifier.ValueText=="Invoke"&&invoke.Expression is MemberAccessExpressionSyntax member&&member.Expression is IdentifierNameSyntax receiver&&receiver.Identifier.ValueText=="calls"&&provider.Imports.TryGetValue(member.Name.Identifier.ValueText,out var imported))callee=imported.Id;
  return new JsonObject{["kind"]=kind,["label"]=callee is null?Label(node):"public call "+callee,["callee"]=callee,["certainty"]="syntax-observed; behavior unverified",["line"]=Math.Max(1,node.GetLocation().GetLineSpan().StartLinePosition.Line),["children"]=children};
 }
 var result=new JsonObject{["schema"]=2,["function"]=function.Id,["provider"]=provider.Id,["description"]=function.Description,["signature"]=JsonSerializer.SerializeToNode(function.Signature),["imports"]=imports,["bodyHash"]=Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(body))).ToLowerInvariant(),["implementationHash"]=Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(implementation))).ToLowerInvariant(),["contractHash"]=Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(contract))).ToLowerInvariant(),["status"]=errors.Count==0?"syntax-projected":"invalid-syntax",["validation"]="syntax only; not semantic proof or code generation",["diagnostics"]=errors,["claims"]=new JsonObject{["level"]="syntactic-outline",["semanticReview"]="not-performed",["behaviorValidated"]=false},["unknowns"]=new JsonArray("callee effects and dynamic dispatch","alias/data flow","termination and determinism","concurrency and cancellation correctness","pre/postcondition satisfaction"),["effects"]=new JsonArray(method?.Body is null?Array.Empty<JsonNode?>():method.Body.DescendantNodes().Select(n=>n switch{InvocationExpressionSyntax=>"call-effects-unknown",AssignmentExpressionSyntax=>"write-alias-effects-unknown",ThrowStatementSyntax=>"explicit-throw",AwaitExpressionSyntax=>"await",LockStatementSyntax=>"lock",ObjectCreationExpressionSyntax=>"allocation",_=>null}).Where(x=>x is not null).Distinct().Select(x=>(JsonNode?)JsonValue.Create(x)).ToArray()),["editor"]=Editor(function),["tree"]=method?.Body is null?new JsonObject{["kind"]="unavailable",["label"]="Malformed selected body",["line"]=1,["children"]=new JsonArray()}:Project(method.Body)};
 void Identify(JsonNode node,string position){node["nodeID"]=Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(result["bodyHash"]!.ToString()+"|"+position))).ToLowerInvariant()[..24];int index=0;foreach(var child in node["children"]!.AsArray())Identify(child!,position+"/"+index++);}Identify(result["tree"]!,"root");analysisWatch.Stop();result["analysisMetrics"]=new JsonObject{["elapsedMilliseconds"]=analysisWatch.Elapsed.TotalMilliseconds,["selectedBodyUtf8Bytes"]=Encoding.UTF8.GetByteCount(body),["projectedNodes"]=projectedNodes,["strategy"]="whole selected-function syntax parse; no semantic analysis",["limits"]="262144 source characters, 8192 projected syntax nodes, 24 syntax ancestor depth; unavailable nodes mark truncation"};return result;
 }
}
