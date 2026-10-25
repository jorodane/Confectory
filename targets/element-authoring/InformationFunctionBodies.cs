using Confectory.Core;
using System.Text.Json.Nodes;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;

// Explicit user text in the existing owned-function transaction. No rewrites,
// assembly loading, emit, execution, registration or source-file writes.
internal static class InformationFunctionBodies
{
 static string Hash(string text)=>JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(text));
 public static JsonObject Read(JsonObject request)
 {
  string owner=request["id"]!.ToString(),function=request["function"]!.ToString();var units=request["units"]!.AsObject();var schema=new Parser(units[owner]!["draft"]!.ToString(),"<body-owner>").ParseElement();
  if(units.Count>2048||schema.Kind!="schema"||!schema.Contains.Any(c=>c.Id==function&&c.Kind=="function")||!function.StartsWith(owner+"_Function_",StringComparison.Ordinal))throw new InvalidOperationException("Direct owned information function required");
  int bytes=0;var result=new JsonObject();foreach(var entry in units){if(entry.Value?["kind"]?.ToString()!="implementation")continue;var d=new Parser(entry.Value["draft"]!.ToString(),"<body-implementation>").ParseElement();if(d.Function!=function&&!d.Imports.Values.Any(i=>i.Id==function))continue;
   if(d.Parent is not null||d.Bodies.Count==0)continue;if(!d.Id.StartsWith(PackPaths.Namespace(owner)+"::",StringComparison.Ordinal)||d.Bodies.Count>8)throw new InvalidOperationException("Direct owned implementation and all targets required");
   var feature=new Parser(units[d.Function!]!["draft"]!.ToString(),"<body-function>").ParseElement();string name=feature.Values.TryGetValue("editorName",out var label)&&label.Value.ValueKind==System.Text.Json.JsonValueKind.String?label.Value.GetString()??d.Function!:d.Function!;
   foreach(var body in d.Bodies){
    bool graph=body.Value.SourceKind=="blueprint";
    if(body.Value.SourceKind!="csharp"&&!(graph&&request["includeBlueprintTargets"]?.GetValue<bool>()==true&&d.Function==function))continue;
    string id=d.Id+"/body:"+body.Key;var unit=units[id]??throw new InvalidOperationException("Original target source missing");string text=unit["draft"]!.ToString();
    if(unit["kind"]?.ToString()!=(graph?"blueprint":"body")||text.Length>(graph?1048576:262144))throw new ArgumentException("Bounded original target body required");
    var row=new JsonObject{["name"]=name,["sourceKind"]=body.Value.SourceKind,["implementation"]=d.Id,["target"]=body.Key,["function"]=d.Function,["caller"]=d.Function!=function,["path"]=unit["path"]!.DeepClone(),["hash"]=Hash(text),["signature"]=FeatureBlueprint.SignatureDocument(d.Signature!),["contractSignature"]=FeatureBlueprint.SignatureDocument(feature.Signature!)};
    if(graph){
     var g=JsonNode.Parse(text)!.AsObject();var node=g["nodes"]!.AsArray().SingleOrDefault(n=>n!["implementationContext"] is not null);
     if(node is null){if(!d.Bodies.Any(p=>p.Value.SourceKind=="csharp"))continue;row["graph"]=id;}
     else{
      if(d.Imports.Count>0||g["copySource"] is not null)continue;
      string recordId=id+"/node:"+node["id"]!.ToString();var recordUnit=units[recordId]??throw new InvalidOperationException("Original whole-body record missing");
      BlueprintDocuments.Validate(recordId,"blueprint-node",recordUnit["draft"]!.ToString());
      var record=JsonNode.Parse(recordUnit["draft"]!.ToString())!;
      row["sourceKind"]="whole-csharp";row["graph"]=id;row["node"]=node["id"]!.DeepClone();row["path"]=recordUnit["path"]!.DeepClone();row["hash"]=Hash(recordUnit["draft"]!.ToString());row["signature"]=node["signature"]!.DeepClone();row["text"]=record["source"]!.DeepClone();id=recordId;
     }
    }else row["text"]=text;
    if(row["text"] is not null)bytes=checked(bytes+System.Text.Encoding.UTF8.GetByteCount(row["text"]!.GetValue<string>()));
    if(bytes>1048576||result.Count>=32)throw new ArgumentException("Body selection budget");result.Add(id,row);
   }

  }return result;
 }
 internal static FunctionSignature Signature(JsonNode value)=>new Parser("function Body.Validation::Selected ("+string.Join(",",value["args"]!.AsArray().Select(a=>(a!["mode"] is null?"":a["mode"]+" ")+a!["type"]+" "+a["name"]))+") -> "+value["return"]+" {}","<selected-C#-signature>").ParseElement().Signature!;
 internal static string Text(string id,string path,JsonObject unit,FunctionSignature before,FunctionSignature selected,FunctionSignature contract,JsonObject plan)
 {
  if(plan.Count!=6||plan.Any(p=>p.Key is not ("hash" or "path" or "beforeSignature" or "signature" or "contract" or "text"))||plan["path"]?.ToString()!=path||plan["hash"]?.ToString()!=Hash(unit["draft"]!.ToString())||!JsonNode.DeepEquals(plan["beforeSignature"],FeatureBlueprint.SignatureDocument(before))||!JsonNode.DeepEquals(plan["signature"],FeatureBlueprint.SignatureDocument(selected))||!JsonNode.DeepEquals(plan["contract"],FeatureBlueprint.SignatureDocument(contract))||plan["text"] is not JsonValue value||!value.TryGetValue<string>(out string? text)||text.Length>262144)throw new InvalidOperationException("Exact original C# body and explicitly selected current declaration required; all input retained");
  return text;
 }
 internal static void Validate(Element implementation,Element feature,string body,string path,IReadOnlyDictionary<string,Element> declarations,Element requested,string members="",FunctionSignature? entry=null)
 {
  // Check the real generator's boundary and import interfaces, not a fake method
  // with inferred argument names. Runtime platform references are read only.
  string prefix="class BodyContent { "+implementation.Signature!.Return+" Invoke("+string.Join(",",(entry??implementation.Signature).Args.Select(a=>a.Declaration()))+") {\n";
  var options=new CSharpParseOptions(LanguageVersion.CSharp14);var content=CSharpSyntaxTree.ParseText(prefix+body+"\n} }",options);var cls=content.GetRoot().DescendantNodes().OfType<ClassDeclarationSyntax>().SingleOrDefault();var method=cls?.Members.OfType<MethodDeclarationSyntax>().SingleOrDefault();
  if(content.GetDiagnostics().Any(d=>d.Severity==DiagnosticSeverity.Error)||cls?.Members.Count!=1||method?.Body?.CloseBraceToken.SpanStart!=prefix.Length+body.Length+1)throw new InvalidOperationException("C# 본문 구문과 보호된 함수 경계를 확인해 주세요. 원문과 입력은 유지됩니다.");
  var contracts=new Dictionary<string,Element>(StringComparer.Ordinal){{feature.Id,feature}};
  foreach(var import in implementation.Imports.Values){var target=import.Id==requested.Id?requested:declarations.GetValueOrDefault(import.Id)??throw new InvalidOperationException("Registered C# imports require their read-only contract receipt");if(target.Kind!="function"||!import.Signature.Matches(target.Signature!))throw new InvalidOperationException("Explicit C# import contract is stale");contracts[target.Id]=target;}
  var trees=contracts.Values.Select(d=>CSharpSyntaxTree.ParseText(Generation.ContractSource(d),options)).Append(CSharpSyntaxTree.ParseText(Generation.ImplementationSource(implementation,body,path,members,entry),options)).ToArray();
  var platform=(AppContext.GetData("TRUSTED_PLATFORM_ASSEMBLIES") as string??"").Split(Path.PathSeparator,StringSplitOptions.RemoveEmptyEntries);if(platform.Length is <1 or >512)throw new InvalidOperationException("Trusted runtime references unavailable; C# text retained");
  var compilation=CSharpCompilation.Create("OwnedBodyCandidate",trees,platform.Distinct(StringComparer.Ordinal).Select(p=>MetadataReference.CreateFromFile(p)),new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary,optimizationLevel:OptimizationLevel.Release));
  var errors=compilation.GetDiagnostics().Where(d=>d.Severity==DiagnosticSeverity.Error).Take(8).Select(d=>d.Id).Distinct().ToArray();if(errors.Length>0)throw new InvalidOperationException("직접 편집한 C# 본문과 현재 계약을 확인해 주세요. 입력은 유지됩니다. ["+string.Join(",",errors)+"]");
 }
}
