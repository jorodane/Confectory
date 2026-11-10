using Confectory.Core;
using System.Text;
using System.Text.Json.Nodes;

// A declaration-only transition does not invent values or rewrite a body.
// Its absence-of-consumers proof retains every observed header as a read lease.
internal static class FunctionNativeEdits
{
 internal const string Prefix="$function:";
 internal static JsonObject Project(Registry registry,string owner,string function,Func<string,string> read)
 {
  var row=new JsonObject{["id"]=function,["available"]=false,["reason"]="구현·호출·요구 계약이 없는 직접 소유 동기 기능의 타입만 전환할 수 있어요. 입력은 유지됩니다."};
  string ns=PackPaths.Namespace(owner);var pack=registry.Packs[ns];
  var definition=registry.Get(owner,"schema");if(!definition.Contains.Any(c=>c.Kind=="function"&&c.Id==function)||!function.StartsWith(owner+"_Function_",StringComparison.Ordinal)||!pack.Elements.TryGetValue(function[(ns.Length+2)..],out var locator)||locator.Kind!="function"||locator.Path!="elements/"+function[(ns.Length+2)..]+".celem")return row;
  var method=registry.Get(function,"function",owner);if(method.Parent is not null||BlueprintAsync.Has(method)||BlueprintExecutionBranches.Has(method))return row;
  var queue=new Queue<(string Id,string Source)>();var seen=new HashSet<string>(StringComparer.Ordinal);var proofs=new JsonObject();
  foreach(var entry in registry.Packs.Where(p=>p.Key==ns||pack.Dependencies.ContainsKey(p.Key)))foreach(var declaration in entry.Value.Elements.Where(e=>e.Value.Kind is "category" or "concept" or "object" or "schema" or "function" or "implementation" or "module" or "enum"))queue.Enqueue((entry.Key+"::"+declaration.Key,owner));
  while(queue.TryDequeue(out var next)){
   if(!seen.Add(next.Id))continue;if(seen.Count>200){row["reason"]="사용처 읽기 범위를 넘었어요. 원본과 입력은 유지됩니다.";return row;}
   var element=registry.Get(next.Id,source:next.Source);
   if(element.Function==function||element.Parent==function||element.Imports.Values.Any(i=>i.Id==function)||element.Requires.ContainsKey(function)||element.Defaults.ContainsKey(function)||element.Provides.ContainsKey(function)||element.Fields.Values.Any(f=>f.Kind=="function"&&f.Type==function)||element.Id!=owner&&element.Contains.Any(c=>c.Kind=="function"&&c.Id==function))return row;
   proofs[element.Id]=new JsonObject{["source"]=JsonData.HashBytes(Encoding.UTF8.GetBytes(read(element.Loc.File))),["path"]=Path.GetFullPath(element.Loc.File)};
   void Follow(string? id){if(id is not null)queue.Enqueue((id,element.Id));}
   Follow(element.Parent);Follow(element.Function);foreach(var item in element.Imports.Values)Follow(item.Id);foreach(var item in element.Includes)Follow(item.Id);foreach(string id in element.Requires.Keys)Follow(id);foreach(var item in element.Defaults.Values)Follow(item.Id);foreach(var item in element.Provides.Values)Follow(item.Id);foreach(var item in element.Uses)Follow(item.Id);foreach(var item in element.Contains)Follow(item.Id);foreach(var item in element.Fields.Values.Where(f=>f.Kind!="general"))Follow(item.Type);
  }
  foreach(string packId in seen.Select(PackPaths.Namespace).Append(ns).Distinct(StringComparer.Ordinal)){string path=Path.GetFullPath(registry.Paths[packId]);proofs["$manifest:"+packId]=new JsonObject{["path"]=path,["source"]=JsonData.HashBytes(Encoding.UTF8.GetBytes(read(path)))};}
  row["shapeHash"]=JsonData.Digest(new{profile="unused-information-function-v1",owner,function});row["sources"]=proofs;row["proof"]=new JsonObject{["shapeHash"]=row["shapeHash"]!.DeepClone(),["sources"]=proofs.DeepClone()};row["available"]=true;return row;
 }
 internal static void Validate(string function,FunctionSignature signature,JsonNode proof,JsonArray choices,JsonObject scope)
 {
  if(scope["id"]?.ToString()!=function||scope["available"]?.GetValue<bool>()!=true||proof is not JsonObject selected||!JsonNode.DeepEquals(selected[Prefix+function],scope["proof"]))throw new InvalidOperationException("The function is connected or its declaration-only scope changed; retain all input");
  var types=selected.DeepClone().AsObject();types.Remove(Prefix+function);FunctionNativeTypes.Validate(signature,types,choices);
 }
}
