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
  var row=new JsonObject{["id"]=function,["available"]=false,["reason"]="직접 소유 동기 기능과 일반 C# 구현·호출자만 전환할 수 있어요. 상속·참조·Blueprint·요구 계약은 유지됩니다."};
  string ns=PackPaths.Namespace(owner);var pack=registry.Packs[ns];
  var definition=registry.Get(owner,"schema");if(!definition.Contains.Any(c=>c.Kind=="function"&&c.Id==function)||!function.StartsWith(owner+"_Function_",StringComparison.Ordinal)||!pack.Elements.TryGetValue(function[(ns.Length+2)..],out var locator)||locator.Kind!="function"||locator.Path!="elements/"+function[(ns.Length+2)..]+".celem")return row;
  var method=registry.Get(function,"function",owner);if(method.Parent is not null||BlueprintAsync.Has(method)||BlueprintExecutionBranches.Has(method))return row;
  var queue=new Queue<(string Id,string Source)>();var seen=new HashSet<string>(StringComparer.Ordinal);var proofs=new JsonObject();var headers=new List<Element>();var native=new HashSet<string>(StringComparer.Ordinal);
  foreach(var entry in registry.Packs.Where(p=>p.Key==ns||pack.Dependencies.ContainsKey(p.Key)))foreach(var declaration in entry.Value.Elements.Where(e=>e.Value.Kind is "category" or "concept" or "object" or "schema" or "function" or "implementation" or "module" or "enum"))queue.Enqueue((entry.Key+"::"+declaration.Key,owner));
  while(queue.TryDequeue(out var next)){
   if(!seen.Add(next.Id))continue;if(seen.Count>200){row["reason"]="사용처 읽기 범위를 넘었어요. 원본과 입력은 유지됩니다.";return row;}
   var element=registry.Get(next.Id,source:next.Source);
   headers.Add(element);
   if(element.Parent==function||element.Requires.ContainsKey(function)||element.Defaults.ContainsKey(function)||element.Provides.ContainsKey(function)&&element.Id!=function&&element.Id!=owner||element.Fields.Values.Any(f=>f.Kind=="function"&&f.Type==function)||element.Id!=owner&&element.Contains.Any(c=>c.Kind=="function"&&c.Id==function))return row;
   if(element.Function==function||element.Imports.Values.Any(i=>i.Id==function)){
    if(element.Kind!="implementation"||PackPaths.Namespace(element.Id)!=ns||element.Parent is not null||element.Bodies.Count is <1 or >8||element.Bodies.Values.Any(b=>b.SourceKind!="csharp")||element.Function is null)return row;
    var feature=registry.Get(element.Function,"function",element.Id);if(feature.Parent is not null||BlueprintAsync.Has(feature)||BlueprintExecutionBranches.Has(feature))return row;
    native.Add(element.Id);
   }
   proofs[element.Id]=new JsonObject{["source"]=JsonData.HashBytes(Encoding.UTF8.GetBytes(read(element.Loc.File))),["path"]=Path.GetFullPath(element.Loc.File)};
   void Follow(string? id){if(id is not null)queue.Enqueue((id,element.Id));}
   Follow(element.Parent);Follow(element.Function);foreach(var item in element.Imports.Values)Follow(item.Id);foreach(var item in element.Includes)Follow(item.Id);foreach(string id in element.Requires.Keys)Follow(id);foreach(var item in element.Defaults.Values)Follow(item.Id);foreach(var item in element.Provides.Values)Follow(item.Id);foreach(var item in element.Uses)Follow(item.Id);foreach(var item in element.Contains)Follow(item.Id);foreach(var item in element.Fields.Values.Where(f=>f.Kind!="general"))Follow(item.Type);
  }
  if(headers.Any(e=>e.Parent is not null&&native.Contains(e.Parent)))return row;
  foreach(string packId in seen.Select(PackPaths.Namespace).Append(ns).Distinct(StringComparer.Ordinal)){string path=Path.GetFullPath(registry.Paths[packId]);proofs["$manifest:"+packId]=new JsonObject{["path"]=path,["source"]=JsonData.HashBytes(Encoding.UTF8.GetBytes(read(path)))};}
  row["adaptation"]=native.Count>0?"native-bodies":"declaration";row["shapeHash"]=native.Count==0?JsonData.Digest(new{profile="unused-information-function-v1",owner,function}):JsonData.Digest(new{profile="native-information-function-abi-v1",owner,function,implementations=native.Order(StringComparer.Ordinal).ToArray()});row["sources"]=proofs;row["proof"]=new JsonObject{["shapeHash"]=row["shapeHash"]!.DeepClone(),["sources"]=proofs.DeepClone()};row["available"]=true;return row;
 }
 internal static void Validate(string function,FunctionSignature signature,JsonNode proof,JsonArray choices,JsonObject scope)
 {
  if(scope["id"]?.ToString()!=function||scope["available"]?.GetValue<bool>()!=true||proof is not JsonObject selected||!JsonNode.DeepEquals(selected[Prefix+function],scope["proof"]))throw new InvalidOperationException("The owned native function source scope changed or is unsupported; retain all input");
  var types=selected.DeepClone().AsObject();types.Remove(Prefix+function);FunctionNativeTypes.Validate(signature,types,choices);
 }
}
