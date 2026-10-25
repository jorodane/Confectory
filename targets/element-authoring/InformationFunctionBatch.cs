using Confectory.Core;
using System.Text.Json.Nodes;

// Compose existing pure closures over an internal overlay. This is not a new
// save operation: the caller publishes the complete result with its one CAS.
internal sealed class InformationFunctionBatch
{
 public JsonObject Request { get; }
 readonly JsonObject originalUnits;
 readonly HashSet<string> functions;
 readonly bool composeCallers;
 readonly Dictionary<string,JsonObject> outputPlans;
 readonly HashSet<string> completed=new(StringComparer.Ordinal);
 InformationFunctionBatch(JsonObject request,HashSet<string> functions,bool composeCallers,Dictionary<string,JsonObject> outputPlans){Request=request.DeepClone().AsObject();originalUnits=request["units"]!.AsObject();this.functions=functions;this.composeCallers=composeCallers;this.outputPlans=outputPlans;}
 public static InformationFunctionBatch? Begin(JsonObject request,JsonArray changes,Func<Element,string> format)
 {
  bool ContractEdit(JsonNode? row){
   if(row?["type"]?.ToString()!="function-edit"||row["mapping"] is not JsonObject mapping)return false;
   if((mapping["bodies"] as JsonObject)?.Count>0)return true;
   // Metadata-only edits keep the existing path, including native/ref bodies.
   if(mapping["before"] is null)return true;
   return !JsonNode.DeepEquals(FeatureBlueprint.SignatureDocument(InformationFunctionBodies.Signature(mapping["before"]!)),FeatureBlueprint.SignatureDocument(InformationFunctionBodies.Signature(row["signature"]!)));
  }
  var edits=changes.Where(ContractEdit).ToArray();
  if(edits.Length<2)return null;
  if(edits.Length>8||changes.Count!=edits.Length)throw new InvalidOperationException("Save up to eight direct function input contracts together; other input is retained");
  var units=request["units"]?.AsObject()??throw new InvalidOperationException("Read every shared caller before saving the function group");if(units.Count>2048)throw new ArgumentException("Shared contract source budget");
  var functions=new HashSet<string>(StringComparer.Ordinal);bool typed=false,hasOutputs=false,outputTyped=false;
  bool Scalar(string type)=>type is "bool" or "int" or "long" or "float" or "double" or "string";
  foreach(var row in edits){
   string id=row!["id"]!.ToString();if(!functions.Add(id))throw new ArgumentException("One explicit edit per function identity required");
   var mapping=row["mapping"]!.AsObject();if(mapping.Any(p=>p.Key is not ("before" or "args" or "callers" or "implementations" or "outputs"))||mapping["before"] is not JsonObject||mapping["args"] is not JsonObject)throw new InvalidOperationException("Shared caller batching currently preserves body, output structure and copy contracts; retain all input");
   var original=new Parser(units[id]?["draft"]?.ToString()??throw new InvalidOperationException("Original function snapshot missing"),"<function-group>").ParseElement();
   var before=original.Signature??throw new ArgumentException("Function signature required");var next=InformationFunctionBodies.Signature(row["signature"]!);var remap=mapping["args"]!.AsObject();
   if(original.Kind!="function"||original.Parent is not null||!JsonNode.DeepEquals(mapping["before"],FeatureBlueprint.SignatureDocument(before))||before.Return!=next.Return||before.Args.Count!=next.Args.Count||before.Args.Count!=remap.Count||before.Args.Any(a=>a.Mode is not (null or "out")))throw new InvalidOperationException("Shared caller batching requires same-position value/out identities and an unchanged return; retain all input");
   for(int i=0;i<before.Args.Count;i++){var a=before.Args[i];var b=next.Args[i];if(a.Mode!=b.Mode)throw new InvalidOperationException("Retain the original input/output roles explicitly");hasOutputs|=a.IsOut;if(a.Type==b.Type){if(remap[a.Name]?.ToString()!=b.Name)throw new InvalidOperationException("Retain each unchanged pin identity explicitly");}else if(a.IsOut){outputTyped=true;if(a.Name!=b.Name||!Scalar(a.Type)||!Scalar(b.Type)||remap[a.Name]?.ToString()!=a.Name)throw new InvalidOperationException("Changed scalar outputs retain their explicit original pin identity");}else{typed=true;if(a.Mode is not null||a.Name!=b.Name||!Scalar(a.Type)||!Scalar(b.Type)||!remap.ContainsKey(a.Name)||remap[a.Name] is not null)throw new InvalidOperationException("Changed scalar inputs need explicit replacement at the same position and name");}}
  }
  var projections=new Dictionary<string,JsonObject>(StringComparer.Ordinal);
  if(outputTyped){
   if(typed)throw new InvalidOperationException("Keep input and output type batches separate; all input retained");
   foreach(var row in edits){var mapping=row!["mapping"]!.AsObject();var before=InformationFunctionBodies.Signature(mapping["before"]!);var next=InformationFunctionBodies.Signature(row["signature"]!);
    if(mapping.Count!=4||mapping["callers"] is not JsonObject callers||mapping["outputs"] is not JsonObject||mapping.ContainsKey("implementations")||before.Args.Select((a,i)=>a.Name!=next.Args[i].Name||!a.IsOut&&a.Type!=next.Args[i].Type).Any(v=>v))throw new InvalidOperationException("Shared scalar output types retain all input and output names and require original writer/caller selections");
    foreach(var plan in callers.Select(p=>p.Value!.AsObject()))if(plan["inputs"] is not JsonObject inputs||inputs.Count!=before.Args.Count(a=>!a.IsOut)||before.Args.Where(a=>!a.IsOut).Any(a=>inputs[a.Name]?.ToString()!=a.Name)||plan["disconnect"] is not JsonObject disconnect||disconnect.Count!=0||plan["outputs"] is not JsonObject)throw new InvalidOperationException("Retain the original caller inputs while selecting exact compatible outputs");
    projections.Add(row["id"]!.ToString(),callers.DeepClone().AsObject());
   }
  }else if((hasOutputs&&(typed||edits.Any(row=>row!["mapping"]!.AsObject().Count!=2)))||edits.Any(row=>row!["mapping"]?["outputs"] is not null))throw new InvalidOperationException("Shared output names retain exact types and automatic identity-preserving bindings; other selected input is retained");
  // Out names propagate the explicit old-pin identity through existing semantic
  // bindings. They never select a different output, rewrite C# or replan values.
  bool independent=typed||hasOutputs;
  foreach(var row in units.Where(p=>p.Value?["kind"]?.ToString()=="implementation")){
   var d=new Parser(row.Value!["draft"]!.ToString(),"<shared-caller-group>").ParseElement();if(!functions.Contains(d.Function!)&&!d.Imports.Values.Any(i=>functions.Contains(i.Id)))continue;
   bool callee=functions.Contains(d.Function!);
   if(independent&&(callee&&d.Imports.Count!=0||!callee&&d.Imports.Values.Any(i=>!functions.Contains(i.Id))))throw new InvalidOperationException("Shared type/output edits require independent leaf implementations and callers of only the selected functions");
   if(d.Parent is not null||d.Bodies.Count is <1 or >8||d.Bodies.Any(b=>b.Value.SourceKind!="blueprint"))throw new InvalidOperationException("Shared caller batching currently requires direct Blueprint targets; original sources retained");
   foreach(var body in d.Bodies){var graph=JsonNode.Parse(units[d.Id+"/body:"+body.Key]?["draft"]?.ToString()??throw new InvalidOperationException("Complete shared caller graph required"))!.AsObject();
    if(graph["copySource"] is not null||graph["nodes"] is not JsonArray nodes||nodes.Any(n=>n is not JsonObject||n["graph"] is not null||n["implementationContext"] is not null||n["forwardCallerStorage"] is not null||n["postCall"] is not null||n["kind"]?.ToString() is not ("code" or "call" or "export")||n["kind"]?.ToString()!="export"&&n["control"]?.ToString()!="next"))throw new InvalidOperationException("Shared caller batching preserves copy, private, native and wrapper contexts; save those contracts separately");
    if(independent&&(graph["locals"] is JsonArray locals&&locals.Count>0||graph["aliases"] is JsonObject aliases&&aliases.Count>0||nodes.Any(n=>n!["kind"]?.ToString()!=(callee?"code":"call")&&n["kind"]?.ToString()!="export")))throw new InvalidOperationException("Shared type/output edits preserve code-free caller and leaf callee contexts; retain all input");
   }
  }
  // Prove every original selection before composing anything. No user consent
  // is rebased onto a changed live source, and no intermediate result is saved.
  if(independent)foreach(var row in edits){var original=new Parser(units[row!["id"]!.ToString()]!["draft"]!.ToString(),"<original-group-contract>").ParseElement();var next=new Parser(units[original.Id]!["draft"]!.ToString(),"<group-contract>").ParseElement();DeclarationAuthoring.Apply(next,new JsonObject{["action"]="signature",["value"]=row["signature"]!.DeepClone()});InformationFunctionContracts.Prepare(request,original,next,row["mapping"]!.AsObject(),format);}
  return new(request,functions,typed||outputTyped,projections);
 }
 public JsonObject MappingFor(string function,JsonObject mapping)
 {
  if(!composeCallers)return mapping;
  var prepared=mapping.DeepClone().AsObject();
  foreach(var entry in prepared["callers"] as JsonObject??new JsonObject()){
   var plan=entry.Value!.AsObject();string id=plan["graph"]!.ToString();string initial=originalUnits[id]!["draft"]!.ToString(),current=Request["units"]![id]!["draft"]!.ToString();
   if(plan["hash"]?.ToString()!=Hash(initial))throw new InvalidOperationException("Original shared caller selection changed; retain all input");
   if(initial==current)continue;
   var before=JsonNode.Parse(initial)!.AsObject();var after=JsonNode.Parse(current)!.AsObject();ProjectOutputs(id,before);string nodeId=plan["node"]!.ToString();
   JsonNode? Selected(JsonObject graph)=>graph["nodes"]!.AsArray().SingleOrDefault(n=>n!["id"]?.ToString()==nodeId&&n["feature"]?.ToString()==function);
   if(Selected(before) is null||!JsonNode.DeepEquals(Selected(before),Selected(after)))throw new InvalidOperationException("Selected shared call changed; repeat the explicit selection");
   void MaskOtherCalls(JsonObject graph){foreach(var node in graph["nodes"]!.AsArray().OfType<JsonObject>())if(node["kind"]?.ToString()=="call"&&node["feature"]?.ToString() is string target&&target!=function&&functions.Contains(target)){node.Remove("signature");node.Remove("arguments");}}
   MaskOtherCalls(before);MaskOtherCalls(after);
   if(!JsonNode.DeepEquals(before,after))throw new InvalidOperationException("Shared graph changed outside the prepared independent calls; retain every input");
   // This hash names only our verified internal overlay. Final updates and CAS
   // still carry the original request's source identity and checkpoint version.
   plan["hash"]=Hash(current);
  }
  completed.Add(function);return prepared;
 }
 void ProjectOutputs(string id,JsonObject graph)
 {
  // Apply only earlier, independently proved producer choices to a clone of
  // the ORIGINAL graph. This is not consent to a changed live caller/source.
  foreach(string function in completed){if(!outputPlans.TryGetValue(function,out var plans))continue;
   foreach(var plan in plans.Select(p=>p.Value!.AsObject()).Where(p=>p["graph"]?.ToString()==id)){
    string nodeId=plan["node"]!.ToString();if(!graph["nodes"]!.AsArray().Any(n=>n!["id"]?.ToString()==nodeId&&n["feature"]?.ToString()==function))throw new InvalidOperationException("Original producer identity changed; retain every input");
    var outputs=plan["outputs"]!.AsObject();void Rebind(JsonNode? value){if(value is JsonObject o){if(o["node"]?.ToString()==nodeId){string name=o["output"]?.ToString()??"return",to=outputs[name]?.GetValue<string>()??throw new InvalidOperationException("An explicitly disconnected output is still consumed");if(to=="return")o.Remove("output");else o["output"]=to;return;}foreach(var p in o.ToArray())if(p.Key!="constant")Rebind(p.Value);}else if(value is JsonArray array)foreach(var v in array)Rebind(v);}
    InformationFunctionGraphs.Bindings(graph,Rebind);
   }
  }
 }
 public void Stage(string id,string text){var unit=Request["units"]![id]??throw new InvalidOperationException("Observed shared contract source missing");unit["draft"]=text;}
 public void Merge(JsonArray updates,JsonObject update)
 {
  string id=update["id"]!.ToString();var initial=originalUnits[id]??throw new InvalidOperationException("Original shared source missing");var current=Request["units"]![id]??throw new InvalidOperationException("Current shared source missing");
  if(update["kind"]?.ToString()!=initial["kind"]?.ToString()||update["path"]?.ToString()!=initial["path"]?.ToString()||update["hash"]?.ToString()!=Hash(current["draft"]!.ToString()))throw new InvalidOperationException("Shared source identity or preparation basis changed; no candidate applied");
  var prior=updates.SingleOrDefault(row=>row!["id"]?.ToString()==id);var merged=update.DeepClone().AsObject();merged["hash"]=Hash(initial["draft"]!.ToString());
  if(prior is null)updates.Add(merged);else updates[updates.IndexOf(prior)]=merged;
  if(updates.Count>64)throw new ArgumentException("Combined function usage closure budget");
  Stage(id,update["text"]!.ToString());
 }
 static string Hash(string text)=>JsonData.HashBytes(System.Text.Encoding.UTF8.GetBytes(text));
}
