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
 public static JsonNode Execute(JsonNode request)
 {
 string contract=request["contract"]!.GetValue<string>(),implementation=request["implementation"]!.GetValue<string>(),body=request["body"]!.GetValue<string>();
 if(contract.Length>65536||implementation.Length>65536||body.Length>262144)throw new ArgumentException("Bounded selected function/implementation/body required");
 var function=new Parser(contract,"<contract>").ParseElement();var provider=new Parser(implementation,"<implementation>").ParseElement();
 if(function.Kind!="function"||provider.Kind!="implementation"||provider.Function!=function.Id||!function.Signature!.Matches(provider.Signature))throw new ArgumentException("Selected implementation must match its public function contract");
 const string prefix="class ProjectionContainer { void Body() {\n";var tree=CSharpSyntaxTree.ParseText(prefix+body+"\n}}",new CSharpParseOptions(LanguageVersion.Latest));
 var errors=new JsonArray();foreach(var diagnostic in tree.GetDiagnostics().Where(x=>x.Severity==DiagnosticSeverity.Error))errors.Add(new JsonObject{["code"]=diagnostic.Id,["line"]=Math.Max(1,diagnostic.Location.GetLineSpan().StartLinePosition.Line),["message"]=diagnostic.GetMessage()});
 var method=tree.GetRoot().DescendantNodes().OfType<MethodDeclarationSyntax>().FirstOrDefault(m=>m.Identifier.ValueText=="Body");
 var imports=new JsonArray();foreach(var (alias,import) in provider.Imports)imports.Add(new JsonObject{["alias"]=alias,["id"]=import.Id});
 string Label(SyntaxNode node){string text=node.ToString().Replace("\r","").Replace("\n"," ");return text.Length>160?text[..160]+"…":text;}
 bool Essential(SyntaxNode n)=>n is StatementSyntax or ElseClauseSyntax or CatchClauseSyntax or FinallyClauseSyntax or SwitchSectionSyntax or LambdaExpressionSyntax or AwaitExpressionSyntax or InvocationExpressionSyntax or AssignmentExpressionSyntax;
 JsonObject Project(SyntaxNode node)
 {
  string kind=node switch{IfStatementSyntax=>"branch",ElseClauseSyntax=>"else",FinallyClauseSyntax=>"finally",SwitchStatementSyntax=>"switch",SwitchSectionSyntax=>"case",LambdaExpressionSyntax=>"lambda",LocalFunctionStatementSyntax=>"local-function",ForStatementSyntax or ForEachStatementSyntax or WhileStatementSyntax or DoStatementSyntax=>"loop",TryStatementSyntax=>"try",CatchClauseSyntax=>"catch",ThrowStatementSyntax=>"throw",ReturnStatementSyntax=>"return",AwaitExpressionSyntax=>"await",InvocationExpressionSyntax=>"call",AssignmentExpressionSyntax=>"assignment",LocalDeclarationStatementSyntax=>"declaration",BlockSyntax=>"block",_=>"statement"};
  var children=new JsonArray();IEnumerable<SyntaxNode> selected=node is BlockSyntax block?block.Statements:node.ChildNodes();foreach(var child in selected){if(Essential(child))children.Add(Project(child));else foreach(var nested in child.DescendantNodesAndSelf().Where(Essential).Where(n=>!n.Ancestors().TakeWhile(a=>a!=child).Any(Essential)))children.Add(Project(nested));}
  return new JsonObject{["kind"]=kind,["label"]=Label(node),["line"]=Math.Max(1,node.GetLocation().GetLineSpan().StartLinePosition.Line),["children"]=children};
 }
 var result=new JsonObject{["schema"]=1,["function"]=function.Id,["provider"]=provider.Id,["description"]=function.Description,["signature"]=JsonSerializer.SerializeToNode(function.Signature),["imports"]=imports,["bodyHash"]=Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(body))).ToLowerInvariant(),["contractHash"]=Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(contract))).ToLowerInvariant(),["status"]=errors.Count==0?"syntax-projected":"invalid-syntax",["validation"]="syntax only; not semantic proof or code generation",["diagnostics"]=errors,["tree"]=method?.Body is null?new JsonObject{["kind"]="unavailable",["label"]="Malformed selected body",["line"]=1,["children"]=new JsonArray()}:Project(method.Body)};
 return result;
 }
}
