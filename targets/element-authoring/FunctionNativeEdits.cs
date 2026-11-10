using Confectory.Core;
using System.Text;
using System.Text.Json.Nodes;

// Native transitions retain the observed header closure. Existing direct native
// bodies/callers still require the established explicit source adaptation plans.
internal static class FunctionNativeEdits
{
 internal const string Prefix="$function:";
 internal static JsonObject Project(Registry registry,string owner,string function,Func<string,string> read)
 {
  var row=new JsonObject{["id"]=function,["available"]=false,["reason"]="직접 소유 동기 기능의 일반 C#/Blueprint 구현과 직접 호출자를 전환할 수 있어요. 상속·참조·내부 복사본·요구 계약은 유지됩니다."};
  string ns=PackPaths.Namespace(owner);var pack=registry.Packs[ns];
  var definition=registry.Get(owner,"schema");if(!definition.Contains.Any(c=>c.Kind=="function"&&c.Id==function)||!function.StartsWith(owner+"_Function_",StringComparison.Ordinal)||!pack.Elements.TryGetValue(function[(ns.Length+2)..],out var locator)||locator.Kind!="function"||locator.Path!="elements/"+function[(ns.Length+2)..]+".celem")return row;
  var method=registry.Get(function,"function",owner);if(method.Parent is not null||BlueprintAsync.Has(method)||BlueprintExecutionBranches.Has(method))return row;
  var queue=new Queue<(string Id,string Source)>();var seen=new HashSet<string>(StringComparer.Ordinal);var proofs=new JsonObject();var headers=new List<Element>();var native=new HashSet<string>(StringComparer.Ordinal);var graphs=new SortedSet<string>(StringComparer.Ordinal);var entries=new SortedSet<string>(StringComparer.Ordinal);var codes=new SortedSet<string>(StringComparer.Ordinal);var lifts=new SortedSet<string>(StringComparer.Ordinal);var retained=new SortedSet<string>(StringComparer.Ordinal);
  foreach(var entry in registry.Packs.Where(p=>p.Key==ns||pack.Dependencies.ContainsKey(p.Key)))foreach(var declaration in entry.Value.Elements.Where(e=>e.Value.Kind is "category" or "concept" or "object" or "schema" or "function" or "implementation" or "module" or "enum"))queue.Enqueue((entry.Key+"::"+declaration.Key,owner));
  while(queue.TryDequeue(out var next)){
   if(!seen.Add(next.Id))continue;if(seen.Count>200){row["reason"]="사용처 읽기 범위를 넘었어요. 원본과 입력은 유지됩니다.";return row;}
   var element=registry.Get(next.Id,source:next.Source);
   headers.Add(element);
   if(element.Parent==function||element.Requires.ContainsKey(function)||element.Defaults.ContainsKey(function)||element.Provides.ContainsKey(function)&&element.Id!=function&&element.Id!=owner||element.Fields.Values.Any(f=>f.Kind=="function"&&f.Type==function)||element.Id!=owner&&element.Contains.Any(c=>c.Kind=="function"&&c.Id==function))return row;
   if(element.Function==function||element.Imports.Values.Any(i=>i.Id==function)){
    if(element.Kind!="implementation"||PackPaths.Namespace(element.Id)!=ns||element.Parent is not null||element.Bodies.Count is <1 or >8||element.Function is null)return row;
    var feature=registry.Get(element.Function,"function",element.Id);if(feature.Parent is not null||BlueprintAsync.Has(feature)||BlueprintExecutionBranches.Has(feature))return row;
    foreach(var body in element.Bodies){
     if(body.Value.SourceKind=="csharp")continue;
     // One owned root context may explicitly adapt its ABI while independent
     // code records, routes and locals retain their original contracts.
     if(body.Value.SourceKind!="blueprint")return row;
     string path=PackPaths.Owned(Path.GetDirectoryName(registry.Paths[PackPaths.Namespace(body.Value.Origin)])!,body.Value.Path,body.Value.Loc),text=read(path);
     if(JsonNode.Parse(text) is not JsonObject graph||graph["feature"]?.ToString()!=element.Function||graph["copySource"] is not null||graph["profile"]?.ToString()==BlueprintAsync.Profile||graph["nodes"] is not JsonArray nodes)return row;
     bool contextRoot=element.Function==function&&nodes.Count(n=>n?["implementationContext"] is not null)==1;bool lift=contextRoot&&InformationFunctionRetained.IsLift(graph);
     if(nodes.Any(n=>!(n?["kind"]?.ToString()=="call"||element.Function==function&&n?["kind"]?.ToString() is "export" or "code")||n["control"]?.ToString()!="next"||n["postCall"] is not null||(n["implementationContext"] is not null||n["forwardCallerStorage"] is not null)&&!(contextRoot&&n["implementationContext"] is not null)))return row;
     if(contextRoot){
      // A saved candidate overlays its new header while this receipt proves the
      // original physical graph/context. Keep that observation separate from
      // the compiler's later validation of the complete candidate.
      var observed=new Parser(read(element.Loc.File),element.Loc.File).ParseElement();var context=nodes.Single(n=>n?["implementationContext"] is not null)!;
      if(observed.Id!=element.Id||observed.Kind!="implementation"||observed.Function!=function||observed.Parent is not null||context["kind"]?.ToString()!="code"||!JsonNode.DeepEquals(context["implementationContext"],FeatureBlueprint.ImplementationContext(observed))||!JsonNode.DeepEquals(context["signature"],FeatureBlueprint.SignatureDocument(observed.Signature!)))return row;
     }
     string bodyId=element.Id+"/body:"+body.Key;if(lift)lifts.Add(bodyId);else if(contextRoot)retained.Add(bodyId);
     foreach(var node in nodes.OfType<JsonObject>().Where(n=>n["kind"]?.ToString()=="code")){
      if(node["imports"] is JsonArray imports&&imports.Any(i=>i?.ToString()==function)||node["async"]?.GetValue<bool>()==true||node["implementation"] is not JsonValue file||!file.TryGetValue<string>(out var relative))return row;
      string recordId=BlueprintTree.SourceId(bodyId,node["id"]!.GetValue<string>()),recordPath=PackPaths.Owned(Path.GetDirectoryName(path)!,relative),recordText=read(recordPath);
      BlueprintDocuments.Validate(recordId,"blueprint-node",recordText);codes.Add(recordId);proofs["$code:"+recordId]=new JsonObject{["source"]=JsonData.HashBytes(Encoding.UTF8.GetBytes(recordText)),["path"]=Path.GetFullPath(recordPath)};
     }
     string key=bodyId;graphs.Add(key);if(element.Function==function)entries.Add(key);proofs["$graph:"+key]=new JsonObject{["source"]=JsonData.HashBytes(Encoding.UTF8.GetBytes(text)),["path"]=Path.GetFullPath(path)};
    }
    native.Add(element.Id);
   }
   proofs[element.Id]=new JsonObject{["source"]=JsonData.HashBytes(Encoding.UTF8.GetBytes(read(element.Loc.File))),["path"]=Path.GetFullPath(element.Loc.File)};
   void Follow(string? id){if(id is not null)queue.Enqueue((id,element.Id));}
   Follow(element.Parent);Follow(element.Function);foreach(var item in element.Imports.Values)Follow(item.Id);foreach(var item in element.Includes)Follow(item.Id);foreach(string id in element.Requires.Keys)Follow(id);foreach(var item in element.Defaults.Values)Follow(item.Id);foreach(var item in element.Provides.Values)Follow(item.Id);foreach(var item in element.Uses)Follow(item.Id);foreach(var item in element.Contains)Follow(item.Id);foreach(var item in element.Fields.Values.Where(f=>f.Kind!="general"))Follow(item.Type);
  }
  if(headers.Any(e=>e.Parent is not null&&native.Contains(e.Parent)))return row;
  foreach(string packId in seen.Select(PackPaths.Namespace).Append(ns).Distinct(StringComparer.Ordinal)){string path=Path.GetFullPath(registry.Paths[packId]);proofs["$manifest:"+packId]=new JsonObject{["path"]=path,["source"]=JsonData.HashBytes(Encoding.UTF8.GetBytes(read(path)))};}
  row["blueprintImplementation"]=entries.Count>0;row["adaptation"]=native.Count>0?"native-bodies":"declaration";row["shapeHash"]=native.Count==0?JsonData.Digest(new{profile="unused-information-function-v1",owner,function}):graphs.Count==0?JsonData.Digest(new{profile="native-information-function-abi-v1",owner,function,implementations=native.Order(StringComparer.Ordinal).ToArray()}):retained.Count>0?JsonData.Digest(new{profile="native-information-function-retained-whole-v1",owner,function,implementations=native.Order(StringComparer.Ordinal).ToArray(),graphs=graphs.ToArray(),entries=entries.ToArray(),codes=codes.ToArray(),lifts=lifts.ToArray(),retained=retained.ToArray()}):lifts.Count>0?JsonData.Digest(new{profile="native-information-function-whole-lift-v1",owner,function,implementations=native.Order(StringComparer.Ordinal).ToArray(),graphs=graphs.ToArray(),entries=entries.ToArray(),codes=codes.ToArray(),lifts=lifts.ToArray()}):codes.Count>0?JsonData.Digest(new{profile="native-information-function-retained-code-v1",owner,function,implementations=native.Order(StringComparer.Ordinal).ToArray(),graphs=graphs.ToArray(),entries=entries.ToArray(),codes=codes.ToArray()}):entries.Count>0?JsonData.Digest(new{profile="native-information-function-blueprint-entry-v1",owner,function,implementations=native.Order(StringComparer.Ordinal).ToArray(),graphs=graphs.ToArray(),entries=entries.ToArray()}):JsonData.Digest(new{profile="native-information-function-blueprint-call-v1",owner,function,implementations=native.Order(StringComparer.Ordinal).ToArray(),graphs=graphs.ToArray()});row["sources"]=proofs;row["proof"]=new JsonObject{["shapeHash"]=row["shapeHash"]!.DeepClone(),["sources"]=proofs.DeepClone()};row["available"]=true;return row;
 }
 internal static void Validate(string function,FunctionSignature signature,JsonNode proof,JsonArray choices,JsonObject scope)
 {
  if(scope["id"]?.ToString()!=function||scope["available"]?.GetValue<bool>()!=true||proof is not JsonObject selected||!JsonNode.DeepEquals(selected[Prefix+function],scope["proof"]))throw new InvalidOperationException("The owned native function source scope changed or is unsupported; retain all input");
  var types=selected.DeepClone().AsObject();types.Remove(Prefix+function);FunctionNativeTypes.Validate(signature,types,choices);
 }
}
