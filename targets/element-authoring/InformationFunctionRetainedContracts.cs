using Confectory.Core;
using System.Text.Json.Nodes;

// A retained caller's own value-input names and its native callee's names/text
// are explicit choices. Prove each original closure; the existing internal
// overlay composes those typed rewrites, never arbitrary graph/source fields.
internal static class InformationFunctionRetainedContracts
{
 static bool Scalar(string type)=>type is "bool" or "int" or "long" or "float" or "double" or "string";
 internal static bool Typed(JsonNode? row)
 {
  if(row?["type"]?.ToString()!="function-edit"||row["mapping"] is not JsonObject map||map["before"] is not JsonObject before||row["signature"] is not JsonObject after||map["args"] is not JsonObject args||map["callers"] is not JsonObject callers||callers.Count is <1 or >64||map["implementations"] is not JsonObject uses||uses.Count is <1 or >64||map.Any(p=>p.Key is not ("before" or "args" or "bodies" or "callers" or "implementations"))||(map["bodies"] is not null&&map["bodies"] is not JsonObject))return false;
  var a=InformationFunctionBodies.Signature(before);var b=InformationFunctionBodies.Signature(after);
  return a.Return==b.Return&&Scalar(a.Return)&&a.Args.Count is >=1 and <=8&&a.Args.Count==b.Args.Count&&args.Count==a.Args.Count&&a.Args.Where((pin,i)=>pin.Type!=b.Args[i].Type).Count()==1&&a.Args.Select((pin,i)=>pin.Name==b.Args[i].Name&&pin.Mode is null&&b.Args[i].Mode is null&&Scalar(pin.Type)&&Scalar(b.Args[i].Type)&&args.ContainsKey(pin.Name)&&(pin.Type==b.Args[i].Type?args[pin.Name]?.ToString()==pin.Name:args[pin.Name] is null)).All(ok=>ok);
 }
 static bool Names(JsonNode? row)
 {
  if(row?["type"]?.ToString()!="function-edit"||row["mapping"] is not JsonObject map||map["before"] is not JsonObject before||row["signature"] is not JsonObject after||map["args"] is not JsonObject args||map.Any(p=>p.Key is not ("before" or "args" or "bodies" or "callers"))||map["bodies"] is not null&&map["bodies"] is not JsonObject||map["callers"] is not null&&(map["callers"] is not JsonObject callers||callers.Count!=0))return false;
  var a=InformationFunctionBodies.Signature(before);var b=InformationFunctionBodies.Signature(after);
  return a.Matches(b)&&Scalar(a.Return)&&a.Args.Count is >=1 and <=8&&!a.Args.Any(p=>p.Mode is not null||!Scalar(p.Type))&&InformationFunctionBodyBatch.ValueNames(a,b,args)&&a.Args.Where((pin,i)=>pin.Name!=b.Args[i].Name).Count()==1;
 }
 internal static JsonNode?[]? Edits(JsonArray changes)
 {
  var rows=changes.Where(row=>!InformationFunctionBodyBatch.Presentation(row)).ToArray();if(rows.Length!=2||rows.Any(row=>row?["nativeTypes"] is not null||!Names(row)&&!Typed(row)))return null;
  if(rows.Count(row=>(row!["mapping"]!["bodies"] as JsonObject)?.Count is null or 0)!=1||rows.Count(row=>(row!["mapping"]!["bodies"] as JsonObject)?.Count==1)!=1||rows.Any(row=>Typed(row)&&(row!["mapping"]!["bodies"] as JsonObject)?.Count>0))return null;
  var normalized=rows.Select(row=>row!.DeepClone()).ToArray();foreach(var row in normalized)row["mapping"]!["bodies"]??=new JsonObject();return normalized;
 }
 // Original typed selections name original graph hashes. Prove both closures
 // first, then apply the caller's explicit detach/replacement before the callee
 // rename. Only the preparation order changes; no live hash or choice is rebased.
 internal static IEnumerable<JsonNode?> Order(JsonArray changes)
 {
  var typed=Edits(changes)?.SingleOrDefault(Typed);return typed is null?changes:changes.OrderBy(row=>row?["id"]?.ToString()==typed["id"]!.ToString()?0:1);
 }
 internal static HashSet<string>? Prepare(JsonObject request,JsonArray changes,JsonObject units,Func<Element,string> format)
 {
  if(Edits(changes) is not {} rows)return null;
  string owner=request["id"]!.ToString(),ns=PackPaths.Namespace(owner);if(units.Count>240||units[owner]?["kind"]?.ToString()!="schema")throw new InvalidOperationException("Retain the complete original retained caller source scope");
  Element Read(string id){var unit=units[id];if(!id.StartsWith(ns+"::",StringComparison.Ordinal)||unit?["draft"] is not JsonValue text)throw new InvalidOperationException("Read each original owned retained declaration");var value=new Parser(text.ToString(),"<retained-contract-group>").ParseElement();if(value.Id!=id)throw new InvalidOperationException("Direct original retained declarations required");return value;}
  var information=Read(owner);var functions=new HashSet<string>(StringComparer.Ordinal);
  foreach(var row in rows){string id=row!["id"]!.ToString();var before=Read(id);if(!functions.Add(id)||!id.StartsWith(owner+"_Function_",StringComparison.Ordinal)||!information.Contains.Any(child=>child.Id==id&&child.Kind=="function")||before.Kind!="function"||before.Parent is not null||row["hash"]?.ToString()!=JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(units[id]!["draft"]!.ToString()))||!JsonNode.DeepEquals(row["mapping"]!["before"],FeatureBlueprint.SignatureDocument(before.Signature!))||BlueprintAsync.Has(before)||BlueprintExecutionBranches.Has(before))throw new InvalidOperationException("Retain each original owned synchronous function and exact input map");}
  var caller=rows.Single(row=>row!["mapping"]!["bodies"]!.AsObject().Count==0)!;var callee=rows.Single(row=>row!["mapping"]!["bodies"]!.AsObject().Count==1)!;string callerId=caller["id"]!.ToString(),calleeId=callee["id"]!.ToString();
  var implementations=units.Where(p=>p.Value?["kind"]?.ToString()=="implementation").Select(p=>Read(p.Key)).ToArray();
  var a=implementations.SingleOrDefault(d=>d.Function==callerId)??throw new InvalidOperationException("One directly owned retained caller implementation required");var b=implementations.SingleOrDefault(d=>d.Function==calleeId)??throw new InvalidOperationException("One directly owned native callee implementation required");
  if(a.Parent is not null||b.Parent is not null||a.Bodies.Count!=1||a.Bodies.Values.Single().SourceKind!="blueprint"||a.Imports.Count!=1||!a.Imports.TryGetValue(FeatureBlueprint.ImportAlias(calleeId),out var import)||import.Id!=calleeId||!import.Signature.Matches(Read(calleeId).Signature)||b.Imports.Count!=0||!InformationFunctionBodyBatch.NativeTargets(b)||b.Bodies.Count!=1)throw new InvalidOperationException("Retain the exact ordinary caller and its directly owned native callee; other source dependencies need separate plans");
  string graphId=a.Id+"/body:"+a.Bodies.Keys.Single();if(units[graphId]?["kind"]?.ToString()!="blueprint"||JsonNode.Parse(units[graphId]!["draft"]!.ToString()) is not JsonObject graph||graph["copySource"] is not null||graph["nodes"] is not JsonArray nodes||!nodes.Any(n=>n?["kind"]?.ToString()=="code")||!nodes.Any(n=>n?["kind"]?.ToString()=="call"&&n["feature"]?.ToString()==calleeId)||nodes.Any(n=>n is not JsonObject||n["graph"] is not null||n["implementationContext"] is not null||n["forwardCallerStorage"] is not null||n["postCall"] is not null||n["kind"]?.ToString() is not ("call" or "code" or "export")||n["control"]?.ToString()!="next"||n["kind"]?.ToString()=="call"&&n["feature"]?.ToString()!=calleeId))throw new InvalidOperationException("Retain the original ordinary CSharp caller, locals and routes; private/opaque/copy contexts need their explicit plans");
  var body=callee["mapping"]!["bodies"]!.AsObject().Single();var plan=body.Value as JsonObject??throw new InvalidOperationException("Explicit native callee text required");
  if(body.Key!=b.Id+"/body:"+b.Bodies.Keys.Single()||units[body.Key]?["kind"]?.ToString()!="body"||plan.Count!=6||plan.Any(p=>p.Key is not ("hash" or "path" or "beforeSignature" or "signature" or "contract" or "text"))||!JsonNode.DeepEquals(plan["beforeSignature"],FeatureBlueprint.SignatureDocument(b.Signature!))||!JsonNode.DeepEquals(plan["signature"],plan["beforeSignature"])||!JsonNode.DeepEquals(plan["contract"],callee["signature"]))throw new InvalidOperationException("Explicitly retain original native aliases, types, roles and text boundaries");
  foreach(var row in rows){var original=Read(row!["id"]!.ToString());var selected=Read(original.Id);DeclarationAuthoring.Apply(selected,new JsonObject{["action"]="signature",["value"]=row["signature"]!.DeepClone()});InformationFunctionContracts.Prepare(request,original,selected,row["mapping"]!.AsObject(),format);}
  return functions;
 }
 internal static bool RequiresCapture(JsonObject receipt)
 {
  if(receipt["declaration"]?["changes"] is JsonArray changes&&Edits(changes) is not null)return true;
  if(receipt["sources"] is not JsonObject proof)return false;int functions=proof.Count(p=>p.Value?["kind"]?.ToString()=="function"),bodies=proof.Count(p=>p.Value?["kind"]?.ToString()=="body");
  return functions>=2&&bodies>0&&bodies<functions&&proof.Any(p=>p.Value?["kind"]?.ToString()=="blueprint")&&proof.Any(p=>p.Value?["kind"]?.ToString()=="implementation");
 }
}
