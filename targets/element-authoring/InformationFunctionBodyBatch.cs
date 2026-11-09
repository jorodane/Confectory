using Confectory.Core;
using System.Text.Json.Nodes;

// The existing body editor can hold several texts without changing any ABI.
// Prove each original closure; publish their disjoint bodies through one CAS.
internal static class InformationFunctionBodyBatch
{
 public static bool NativeTargets(Element implementation)=>implementation.Kind=="implementation"&&implementation.Parent is null&&implementation.Bodies.Count is >=1 and <=8&&implementation.Bodies.Values.All(body=>body.SourceKind=="csharp");
 // Retain already authored ordinary callers and their owned private frames.
 // Qualified code, contracts and routes still pass the full source checks.
 static bool RetainedCallerNode(JsonNode? node)
 {
  if(node is not JsonObject||node["implementationContext"] is not null||node["forwardCallerStorage"] is not null)return false;
  string? kind=node["kind"]?.ToString(),control=node["control"]?.ToString();
  if(kind=="graph")return node["postCall"] is null&&control=="next"&&node["graph"] is JsonObject child&&child["copySource"] is null;
  if(node["graph"] is not null)return false;
  if(kind=="code")return node["postCall"] is null&&control is "next" or "branch" or "switch";
  if(kind=="export")return node["postCall"] is null&&control=="next";
  if(kind!="call")return false;
  if(node["postCall"] is null)return control=="next";
  // Existing After/enum source and receipts still pass complete typed graph,
  // original publication and assembled C# checks. No wrapper text is inferred.
  return node["postCall"] is JsonObject post&&(post["mode"] is null?control=="next":post["mode"]?.ToString()=="execution-enum"&&control=="switch");
 }
 // Presentation stays under InformationDefinitions' existing exact-key,
 // duplicate, text and image validation. It cannot add another source closure.
 public static bool Presentation(JsonNode? row)=>row is JsonObject value&&value.Count==2&&value["type"]?.ToString() is "description" or "icon"&&value["text"] is JsonValue text&&text.TryGetValue<string>(out _);
 public static bool BodyEdit(JsonNode? row)=>row?["type"]?.ToString()=="function-edit"&&row["mapping"] is JsonObject map&&map["before"] is JsonObject&&JsonNode.DeepEquals(map["before"],row["signature"])&&map["bodies"] is JsonObject bodies&&bodies.Count>0&&bodies.All(p=>p.Value is JsonObject plan&&!plan.ContainsKey("whole")&&!plan.ContainsKey("wrapper"));
 public static JsonNode?[]? Edits(JsonArray changes)
 {
  if(changes.Count is <2 or >10)return null;
  var edits=changes.Where(row=>!Presentation(row)).ToArray();
  return edits.Length is >=2 and <=8&&edits.All(BodyEdit)?edits:null;
 }
 // Earlier members may have staged their explicit presentation while all
 // public/native contracts stay unchanged. Project only those proved owned
 // declaration hashes onto the internal overlay, never a changed live source.
 public static JsonObject ProjectCopies(JsonObject request,JsonObject originals,HashSet<string> functions,string function,JsonObject mapping)
 {
  if(mapping["copies"] is null)return mapping;
  var initial=request.DeepClone().AsObject();initial["units"]=originals.DeepClone();
  var before=new InformationFunctionCopies(initial).Read(function);
  if(!JsonNode.DeepEquals(before,mapping["copies"]))throw new InvalidOperationException("Retain the exact original copy proof before composing native bodies");
  var after=new InformationFunctionCopies(request).Read(function);var allowed=new Dictionary<string,string>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);string root=Path.GetDirectoryName(Path.GetFullPath(request["project"]!.ToString()))!;
  foreach(string id in functions){
   var original=originals[id]!.AsObject();var current=request["units"]![id]!.AsObject();var old=new Parser(original["draft"]!.ToString(),"<original-native-member>").ParseElement();var next=new Parser(current["draft"]!.ToString(),"<staged-native-member>").ParseElement();
   if(old.Id!=id||next.Id!=id||old.Kind!="function"||next.Kind!="function"||old.Parent is not null||next.Parent is not null||!JsonNode.DeepEquals(FeatureBlueprint.SignatureDocument(old.Signature!),FeatureBlueprint.SignatureDocument(next.Signature!)))throw new InvalidOperationException("Retained copy projection preserves every original native contract");
   allowed[PackPaths.Owned(root,original["path"]!.ToString())]=JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(current["draft"]!.ToString()));
  }
  if(before.Count!=after.Count)throw new InvalidOperationException("Retained copy assignments changed within the native group");
  foreach(var row in before){
   var original=row.Value!.DeepClone().AsObject();var current=after[row.Key]?.DeepClone().AsObject()??throw new InvalidOperationException("Retain every original copy identity");var oldContext=original["context"]!.AsArray();var newContext=current["context"]!.AsArray();original.Remove("context");current.Remove("context");
   if(!JsonNode.DeepEquals(original,current)||oldContext.Count!=newContext.Count)throw new InvalidOperationException("Keep copy owner, provenance, graph, contract and source scope unchanged");
   for(int i=0;i<oldContext.Count;i++){var prior=oldContext[i]!.AsObject();var projected=newContext[i]!.AsObject();if(JsonNode.DeepEquals(prior,projected))continue;string path=prior["path"]!.ToString();if(projected.Count!=2||projected["path"]?.ToString()!=path||!allowed.TryGetValue(path,out string? hash)||projected["hash"]?.ToString()!=hash)throw new InvalidOperationException("Only explicitly staged native declarations may project their copy context hash");}
  }
  var result=mapping.DeepClone().AsObject();result["copies"]=after;return result;
 }
 public static HashSet<string>? Prepare(JsonObject request,JsonNode?[] edits,JsonObject units,Func<Element,string> format)
 {
  if(!edits.All(BodyEdit))return null;
  var functions=new HashSet<string>(StringComparer.Ordinal);var bodyIds=new HashSet<string>(StringComparer.Ordinal);string ns=PackPaths.Namespace(request["id"]!.ToString());
  Element Declaration(string id)=>new Parser(units[id]?["draft"]?.ToString()??throw new InvalidOperationException("Complete original body declaration required"),"<body-group>").ParseElement();
  foreach(var row in edits){
   string id=row!["id"]!.ToString();var original=Declaration(id);var mapping=row["mapping"]!.AsObject();var signature=original.Signature;
   if(!functions.Add(id)||original.Id!=id||original.Kind!="function"||original.Parent is not null||signature is null||!JsonNode.DeepEquals(mapping["before"],FeatureBlueprint.SignatureDocument(signature))||mapping.Count!=3+(mapping["copies"] is null?0:1)||mapping.Any(p=>p.Key is not ("before" or "args" or "bodies" or "copies"))||mapping["args"] is not JsonObject args||args.Count!=signature.Args.Count||signature.Args.Any(a=>args[a.Name]?.GetValue<string>()!=a.Name))throw new InvalidOperationException("Body-only groups retain exact original contracts and pin identities");
   foreach(var body in mapping["bodies"]!.AsObject()){
    int at=body.Key.LastIndexOf("/body:",StringComparison.Ordinal);if(at<0)throw new InvalidOperationException("Direct native body target required");var implementation=Declaration(body.Key[..at]);string target=body.Key[(at+6)..];
    if(!bodyIds.Add(body.Key)||units[body.Key]?["kind"]?.ToString()!="body"||!NativeTargets(implementation)||implementation.Function!=id||!implementation.Bodies.ContainsKey(target)||body.Key!=implementation.Id+"/body:"+target||!JsonNode.DeepEquals(body.Value?["beforeSignature"],body.Value?["signature"])||!JsonNode.DeepEquals(body.Value?["contract"],mapping["before"]))throw new InvalidOperationException("Review the unchanged declaration of every directly owned native target");
   }
  }
  if(2+functions.Count+bodyIds.Count>64)throw new InvalidOperationException("Keep the complete native body group within the existing 64-member Review budget; all input retained");
  foreach(var unit in units.Where(p=>p.Value?["kind"]?.ToString()=="implementation")){
   var d=Declaration(unit.Key);bool callee=functions.Contains(d.Function!),consumer=d.Imports.Values.Any(i=>functions.Contains(i.Id));if(!callee&&!consumer)continue;
   if(!d.Id.StartsWith(ns+"::",StringComparison.Ordinal)||d.Parent is not null||d.Bodies.Count is <1 or >8)throw new InvalidOperationException("Body-only groups preserve direct source ownership");
   if(callee&&!NativeTargets(d))throw new InvalidOperationException("Body-only groups retain all native targets and their original imports");
   foreach(var import in d.Imports.Values){var dependency=Declaration(import.Id);if(!import.Id.StartsWith(ns+"::",StringComparison.Ordinal)||dependency.Kind!="function"||dependency.Parent is not null||!import.Signature.Matches(dependency.Signature))throw new InvalidOperationException(callee?"Keep the exact owned native imports; no external contract is edited":"Keep the exact owned caller imports; no external contract is edited");}
   if(callee)continue;
   foreach(var body in d.Bodies){
    if(body.Value.SourceKind=="csharp"){
     if(units[d.Id+"/body:"+body.Key]?["kind"]?.ToString()!="body"||units[d.Id+"/body:"+body.Key]?["draft"] is null)throw new InvalidOperationException("Read every retained native caller body; no C# source is inferred");
     continue;
    }
    if(body.Value.SourceKind!="blueprint")throw new InvalidOperationException("Retain the ordinary caller while editing native leaf bodies");
    var graph=JsonNode.Parse(units[d.Id+"/body:"+body.Key]?["draft"]?.ToString()??throw new InvalidOperationException("Complete original caller required"))!.AsObject();
    // A retained root copy still passes InformationFunctionCopies' exact
    // assignment/provenance proof in every function's complete preparation.
    // Neither its donor nor the local copy becomes an editable body target.
    if(graph["copySource"] is not null&&(graph["copySource"] is not JsonObject||units[d.Id+"/body:"+body.Key]?["baseline"]?.ToString()=="missing")||graph["nodes"] is not JsonArray||BlueprintTree.Nodes(graph).Any(entry=>!RetainedCallerNode(entry.Node)))throw new InvalidOperationException("Body-only groups retain forwarding and native context caller boundaries");
   }
  }
  foreach(var row in edits){var original=Declaration(row!["id"]!.ToString());InformationFunctionContracts.Prepare(request,original,Declaration(original.Id),row["mapping"]!.AsObject(),format);}
  return functions;
 }
}
