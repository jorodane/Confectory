using Confectory.Core;
using System.Text.Json.Nodes;

// The existing body editor can hold several texts without changing any ABI.
// Prove each original closure; publish their disjoint bodies through one CAS.
internal static class InformationFunctionBodyBatch
{
 public static HashSet<string>? Prepare(JsonObject request,JsonNode?[] edits,JsonObject units,Func<Element,string> format)
 {
  if(!edits.All(row=>row?["mapping"] is JsonObject map&&map["before"] is JsonObject&&JsonNode.DeepEquals(map["before"],row["signature"])&&map["bodies"] is JsonObject bodies&&bodies.Count>0&&bodies.All(p=>p.Value is JsonObject plan&&!plan.ContainsKey("whole")&&!plan.ContainsKey("wrapper"))))return null;
  var functions=new HashSet<string>(StringComparer.Ordinal);string ns=PackPaths.Namespace(request["id"]!.ToString());
  Element Declaration(string id)=>new Parser(units[id]?["draft"]?.ToString()??throw new InvalidOperationException("Complete original body declaration required"),"<body-group>").ParseElement();
  foreach(var row in edits){
   string id=row!["id"]!.ToString();var original=Declaration(id);var mapping=row["mapping"]!.AsObject();var signature=original.Signature;
   if(!functions.Add(id)||original.Id!=id||original.Kind!="function"||original.Parent is not null||signature is null||!JsonNode.DeepEquals(mapping["before"],FeatureBlueprint.SignatureDocument(signature))||mapping.Count!=3||mapping.Any(p=>p.Key is not ("before" or "args" or "bodies"))||mapping["args"] is not JsonObject args||args.Count!=signature.Args.Count||signature.Args.Any(a=>args[a.Name]?.GetValue<string>()!=a.Name))throw new InvalidOperationException("Body-only groups retain exact original contracts and pin identities");
   foreach(var body in mapping["bodies"]!.AsObject()){
    int at=body.Key.LastIndexOf("/body:",StringComparison.Ordinal);if(at<0)throw new InvalidOperationException("Direct native body target required");var implementation=Declaration(body.Key[..at]);
    if(units[body.Key]?["kind"]?.ToString()!="body"||implementation.Kind!="implementation"||implementation.Parent is not null||implementation.Function!=id||implementation.Bodies.Count!=1||implementation.Bodies.Single().Value.SourceKind!="csharp"||body.Key!=implementation.Id+"/body:"+implementation.Bodies.Single().Key||!JsonNode.DeepEquals(body.Value?["beforeSignature"],body.Value?["signature"])||!JsonNode.DeepEquals(body.Value?["contract"],mapping["before"]))throw new InvalidOperationException("Review the unchanged declaration of each directly owned single native target");
   }
  }
  foreach(var unit in units.Where(p=>p.Value?["kind"]?.ToString()=="implementation")){
   var d=Declaration(unit.Key);bool callee=functions.Contains(d.Function!),consumer=d.Imports.Values.Any(i=>functions.Contains(i.Id));if(!callee&&!consumer)continue;
   if(!d.Id.StartsWith(ns+"::",StringComparison.Ordinal)||d.Parent is not null||d.Bodies.Count is <1 or >8)throw new InvalidOperationException("Body-only groups preserve direct source ownership");
   if(callee){if(d.Imports.Count!=0||d.Bodies.Count!=1||d.Bodies.Single().Value.SourceKind!="csharp")throw new InvalidOperationException("Body-only groups currently retain native leaf targets and every import");continue;}
   foreach(var import in d.Imports.Values){var dependency=Declaration(import.Id);if(!import.Id.StartsWith(ns+"::",StringComparison.Ordinal)||dependency.Kind!="function"||dependency.Parent is not null||!import.Signature.Matches(dependency.Signature))throw new InvalidOperationException("Keep the exact owned caller imports; no external contract is edited");}
   foreach(var body in d.Bodies){
    if(body.Value.SourceKind!="blueprint")throw new InvalidOperationException("Retain the ordinary caller while editing native leaf bodies");
    var graph=JsonNode.Parse(units[d.Id+"/body:"+body.Key]?["draft"]?.ToString()??throw new InvalidOperationException("Complete original caller required"))!.AsObject();
    if(graph["copySource"] is not null||graph["locals"] is JsonArray locals&&locals.Count>0||graph["aliases"] is JsonObject aliases&&aliases.Count>0||graph["nodes"] is not JsonArray nodes||nodes.Any(n=>n is not JsonObject||n["kind"]?.ToString() is not ("call" or "export")||n["control"]?.ToString()!="next"||n["graph"] is not null||n["implementationContext"] is not null||n["forwardCallerStorage"] is not null||n["postCall"] is not null))throw new InvalidOperationException("Body-only groups retain copy, private, storage and wrapper caller boundaries");
   }
  }
  foreach(var row in edits){var original=Declaration(row!["id"]!.ToString());InformationFunctionContracts.Prepare(request,original,Declaration(original.Id),row["mapping"]!.AsObject(),format);}
  return functions;
 }
}
