using Confectory.Core;
using System.Text.Json.Nodes;

// Compose two existing explicit operations. Each is proved against the complete
// original observation before the caller stages any internal overlay.
internal static class InformationFunctionMixedBodies
{
 static bool NameEdit(JsonNode? row)=>row?["mapping"] is JsonObject map&&map.Count==2&&map["before"] is JsonObject&&map["args"] is JsonObject args&&!JsonNode.DeepEquals(map["before"],row["signature"])&&InformationFunctionBodyBatch.ValueNames(InformationFunctionBodies.Signature(map["before"]!),InformationFunctionBodies.Signature(row["signature"]!),args);
 public static HashSet<string>? Prepare(JsonObject request,JsonNode?[] edits,JsonObject units,Func<Element,string> format)
 {
  var native=edits.Where(InformationFunctionBodyBatch.BodyEdit).ToArray();var names=edits.Where(row=>!InformationFunctionBodyBatch.BodyEdit(row)).ToArray();
  if(native.Length==0||names.Length==0||!names.All(NameEdit))return null;
  string owner=request["id"]!.ToString(),ns=PackPaths.Namespace(owner);var functions=new HashSet<string>(StringComparer.Ordinal);var nativeFunctions=native.Select(row=>row!["id"]!.ToString()).ToHashSet(StringComparer.Ordinal);
  bool Scalar(string type)=>type is "bool" or "int" or "long" or "float" or "double" or "string";
  Element Read(string id)=>new Parser(units[id]?["draft"]?.ToString()??throw new InvalidOperationException("Complete original mixed function source required"),"<mixed-function-group>").ParseElement();
  foreach(var row in edits){
   string id=row!["id"]!.ToString();var original=Read(id);var before=original.Signature;var selected=InformationFunctionBodies.Signature(row["signature"]!);var map=row["mapping"]!.AsObject();
   if(!functions.Add(id)||!id.StartsWith(owner+"_Function_",StringComparison.Ordinal)||units[id]?["kind"]?.ToString()!="function"||original.Id!=id||original.Kind!="function"||original.Parent is not null||before is null||BlueprintAsync.Has(original)||BlueprintExecutionBranches.Has(original)||before.Args.Any(a=>a.Mode is not null||!Scalar(a.Type))||before.Return!="void"&&!Scalar(before.Return)||!JsonNode.DeepEquals(map["before"],FeatureBlueprint.SignatureDocument(before))||map["args"] is not JsonObject args||!InformationFunctionBodyBatch.ValueNames(before,selected,args)||map.Count!=(nativeFunctions.Contains(id)?3:2))throw new InvalidOperationException("Mixed native body and Blueprint name edits retain direct synchronous scalar contracts and exact positional input maps; all input retained");
  }
  var implementations=functions.ToDictionary(id=>id,_=>0,StringComparer.Ordinal);
  foreach(var unit in units.Where(pair=>pair.Value?["kind"]?.ToString()=="implementation")){
   var d=Read(unit.Key);bool callee=functions.Contains(d.Function!),consumer=d.Imports.Values.Any(import=>functions.Contains(import.Id));if(!callee&&!consumer)continue;
   if(d.Id!=unit.Key||PackPaths.Namespace(d.Id)!=ns||d.Parent is not null||d.Bodies.Count is <1 or >8||callee&&(d.Bodies.Count!=1||d.Imports.Count!=0))throw new InvalidOperationException("Mixed edits keep import-free single callee targets and ordinary owned callers; other closures retained");
   if(callee)implementations[d.Function!]++;
   foreach(var body in d.Bodies){
    string id=d.Id+"/body:"+body.Key;
    if(callee&&nativeFunctions.Contains(d.Function!)){
     if(body.Value.SourceKind!="csharp"||units[id]?["kind"]?.ToString()!="body")throw new InvalidOperationException("Explicit unchanged-contract native body source required");
     continue;
    }
    if(body.Value.SourceKind!="blueprint"||units[id]?["kind"]?.ToString()!="blueprint")throw new InvalidOperationException("A value input name edit requires its ordinary Blueprint source; no native caller source is inferred");
    var graph=JsonNode.Parse(units[id]!["draft"]!.ToString())!.AsObject();
    if(graph["copySource"] is not null||graph["profile"]?.ToString().StartsWith("sync-",StringComparison.Ordinal)!=true||graph["locals"] is JsonArray locals&&locals.Count>0||graph["aliases"] is JsonObject aliases&&aliases.Count>0||graph["nodes"] is not JsonArray nodes||nodes.Any(node=>node?["kind"]?.ToString()!=(callee?"code":"call")&&node?["kind"]?.ToString()!="export"||node?["control"]?.ToString()!="next"||node?["graph"] is not null||node?["implementationContext"] is not null||node?["forwardCallerStorage"] is not null||node?["postCall"] is not null||node?["async"]?.GetValue<bool>()==true||node?["imports"] is JsonArray imports&&imports.Count>0))throw new InvalidOperationException("Mixed name/body edits retain ordinary leaf and caller graphs; private, whole, wrapper and copy source plans keep their existing boundaries");
   }
  }
  if(implementations.Any(pair=>pair.Value!=1))throw new InvalidOperationException("One exact original implementation per selected mixed function required");
  if(InformationFunctionBodyBatch.Prepare(request,native,units,format) is null)throw new InvalidOperationException("Original native body closure required before mixed composition");
  foreach(var row in names){var original=Read(row!["id"]!.ToString());var selected=Read(original.Id);DeclarationAuthoring.Apply(selected,new JsonObject{["action"]="signature",["value"]=row["signature"]!.DeepClone()});InformationFunctionContracts.Prepare(request,original,selected,row["mapping"]!.AsObject(),format);}
  return functions;
 }
}
