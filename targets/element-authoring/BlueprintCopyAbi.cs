using Confectory.Core;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json.Nodes;

// A saved copy is an independent owned body, not authority over its donor. This
// receipt binds one directly assigned object and exact target. No file I/O.
internal static class BlueprintCopyAbi
{
 public static JsonObject Bind(JsonObject request)
 {
  string id=request["id"]!.ToString(),ownerId=request["owner"]!.ToString(),graphId=request["graphId"]!.ToString();
  var caller=new Parser(request["text"]!.GetValue<string>(),"<copy-abi>").ParseElement();
  var fn=new Parser(request["functionText"]!.GetValue<string>(),"<copy-function>").ParseElement();
  var owner=new Parser(request["ownerText"]!.GetValue<string>(),"<copy-owner>").ParseElement();
  var graph=request["graph"]!.AsObject();string ns=PackPaths.Namespace(id);
  if(caller.Id!=id||caller.Kind!="implementation"||caller.Parent is not null||caller.Bodies.Count!=1||owner.Id!=ownerId||owner.Kind!="object"||PackPaths.Namespace(ownerId)!=ns||fn.Kind!="function"||PackPaths.Namespace(fn.Id)!=ns||caller.Function!=fn.Id||!fn.Signature!.Matches(caller.Signature)||graph["feature"]?.ToString()!=fn.Id)throw new ArgumentException("One owned saved copy and its direct object/function required");
  var body=caller.Bodies.Single();if(body.Value.SourceKind!="blueprint"||graphId!=id+"/body:"+body.Key||body.Value.Path!=request["graphPath"]!.ToString())throw new ArgumentException("One exact saved copy target/locator required");
  if(graph["copySource"] is not JsonObject provenance||provenance.Count!=4||provenance.Any(p=>p.Key is not ("implementation" or "target" or "bodyOrigin" or "sourceKind"))||provenance["target"]?.ToString()!=body.Key||provenance["sourceKind"]?.ToString() is not ("blueprint" or "csharp")||provenance["implementation"] is not JsonValue||provenance["bodyOrigin"] is not JsonValue||!provenance["implementation"]!.ToString().Contains("::",StringComparison.Ordinal)||!provenance["bodyOrigin"]!.ToString().Contains("::",StringComparison.Ordinal)||provenance["implementation"]!.ToString()==id||request["unitProvenance"] is not null&&!JsonNode.DeepEquals(request["unitProvenance"],provenance))throw new ArgumentException("Exact unchanged copy provenance required");
  if(!owner.Provides.TryGetValue(fn.Id,out var direct)||direct.Id!=id)throw new ArgumentException("Direct copied slot assignment required");
  var requirements=request["requirements"]!.AsArray();var providers=request["providers"]!.AsArray();
  var requirement=requirements.SingleOrDefault(r=>r!["function"]?.ToString()==fn.Id)??throw new ArgumentException("Current required slot contract needed");
  var provider=providers.SingleOrDefault(r=>r!["function"]?.ToString()==fn.Id&&r["implementation"]?.ToString()==id&&r["origin"]?.ToString()==ownerId)??throw new ArgumentException("Current direct copy provider required");
  FunctionSignature Signature(JsonNode row)=>new(row["Args"]!.AsArray().Select(a=>new Parameter(a!["Type"]!.ToString(),a["Name"]!.ToString(),a["Mode"]?.GetValue<string>())).ToList(),row["return"]!.ToString());
  if(!fn.Signature.Matches(Signature(requirement["signature"]!))||!fn.Signature.Matches(Signature(requirement["moduleSignature"]!)))throw new ArgumentException("Public slot/module signature must remain valid");
  // A stale import is precisely what explicit ABI repair addresses. It is not a
  // successful provider: the staged result must pass the complete provider check.
  if(provider["contract"]?["status"]?.ToString()!="valid"&&(request["requireValid"]?.GetValue<bool>()==true||provider["contract"]?["status"]?.ToString()!="invalid"||provider["contract"]?["code"]?.ToString()!="CONTRACT_MISMATCH"))throw new ArgumentException("Copied provider contract must be valid after explicit repair");
  var objects=request["objects"]!.AsArray();if(objects.Count is <1 or >255)throw new ArgumentException("Bounded owned object closure required");
  var snapshots=new JsonArray();var seen=new HashSet<string>(StringComparer.Ordinal);int assignments=0,bytes=0;
  foreach(var row in objects.OrderBy(r=>r!["id"]!.ToString(),StringComparer.Ordinal)){
   string text=row!["text"]!.GetValue<string>(),objectId=row["id"]!.ToString();bytes=checked(bytes+Encoding.UTF8.GetByteCount(text));if(bytes>2097152||!seen.Add(objectId))throw new ArgumentException("Unique bounded object closure required");
   var obj=new Parser(text,"<copy-object>").ParseElement();if(obj.Kind!="object"||obj.Id!=objectId||PackPaths.Namespace(objectId)!=ns)throw new ArgumentException("Owned object closure required");
   foreach(var slot in obj.Provides.Where(p=>p.Value.Id==id)){if(objectId!=ownerId||slot.Key!=fn.Id)throw new ArgumentException("A shared copy requires an all-owner candidate");assignments++;}
   snapshots.Add(new JsonObject{["id"]=objectId,["path"]=row["path"]!.DeepClone(),["hash"]=Hash(text)});
  }
  if(assignments!=1||!seen.Contains(ownerId))throw new ArgumentException("One exclusively assigned saved copy required");
  var assignment=new JsonObject{["function"]=fn.Id,["implementation"]=id,["origin"]=ownerId};
  return new JsonObject{["schema"]=1,["owner"]=ownerId,["ownerHash"]=Hash(request["ownerText"]!.GetValue<string>()),["implementation"]=id,["implementationPath"]=request["implementationPath"]!.DeepClone(),["graph"]=graphId,["graphPath"]=request["graphPath"]!.DeepClone(),["target"]=body.Key,["function"]=fn.Id,["provenance"]=provenance.DeepClone(),["objectsHash"]=Hash(snapshots.ToJsonString()),["slotHash"]=Hash(new JsonArray(requirement.DeepClone(),assignment).ToJsonString())};
 }
 static string Hash(string text)=>Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(text))).ToLowerInvariant();
}
