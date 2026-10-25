using Confectory.Core;
using System.Text.Json.Nodes;

// Compose existing pure closures over an internal overlay. This is not a new
// save operation: the caller publishes the complete result with its one CAS.
internal sealed class InformationFunctionBatch
{
 public JsonObject Request { get; }
 readonly JsonObject originalUnits;
 InformationFunctionBatch(JsonObject request){Request=request.DeepClone().AsObject();originalUnits=request["units"]!.AsObject();}
 public static InformationFunctionBatch? Begin(JsonObject request,JsonArray changes)
 {
  var edits=changes.Where(row=>row?["type"]?.ToString()=="function-edit"&&row["mapping"] is JsonObject).ToArray();
  if(edits.Length<2)return null;
  if(edits.Length>8||changes.Count!=edits.Length)throw new InvalidOperationException("Save up to eight direct function input-name contracts together; other input is retained");
  var units=request["units"]?.AsObject()??throw new InvalidOperationException("Read every shared caller before saving the function group");if(units.Count>2048)throw new ArgumentException("Shared contract source budget");
  var functions=new HashSet<string>(StringComparer.Ordinal);
  foreach(var row in edits){
   string id=row!["id"]!.ToString();if(!functions.Add(id))throw new ArgumentException("One explicit edit per function identity required");
   var mapping=row["mapping"]!.AsObject();if(mapping.Count!=2||mapping["before"] is not JsonObject||mapping["args"] is not JsonObject)throw new InvalidOperationException("Shared caller batching currently preserves body, output and copy contracts; retain all input");
   var original=new Parser(units[id]?["draft"]?.ToString()??throw new InvalidOperationException("Original function snapshot missing"),"<function-group>").ParseElement();
   var before=original.Signature??throw new ArgumentException("Function signature required");var next=InformationFunctionBodies.Signature(row["signature"]!);var remap=mapping["args"]!.AsObject();
   if(original.Kind!="function"||original.Parent is not null||!JsonNode.DeepEquals(mapping["before"],FeatureBlueprint.SignatureDocument(before))||!before.Matches(next)||before.Args.Count!=remap.Count||before.Args.Any(a=>a.Mode is not null)||before.Args.Select((a,i)=>remap[a.Name]?.ToString()==next.Args[i].Name).Any(value=>!value))throw new InvalidOperationException("Shared caller batching requires exact same-position value input identities; type, role, output or order input is retained");
  }
  foreach(var row in units.Where(p=>p.Value?["kind"]?.ToString()=="implementation")){
   var d=new Parser(row.Value!["draft"]!.ToString(),"<shared-caller-group>").ParseElement();if(!functions.Contains(d.Function!)&&!d.Imports.Values.Any(i=>functions.Contains(i.Id)))continue;
   if(d.Parent is not null||d.Bodies.Count is <1 or >8||d.Bodies.Any(b=>b.Value.SourceKind!="blueprint"))throw new InvalidOperationException("Shared caller batching currently requires direct Blueprint targets; original sources retained");
   foreach(var body in d.Bodies){var graph=JsonNode.Parse(units[d.Id+"/body:"+body.Key]?["draft"]?.ToString()??throw new InvalidOperationException("Complete shared caller graph required"))!.AsObject();
    if(graph["copySource"] is not null||graph["nodes"] is not JsonArray nodes||nodes.Any(n=>n is not JsonObject||n["graph"] is not null||n["implementationContext"] is not null||n["forwardCallerStorage"] is not null||n["postCall"] is not null||n["kind"]?.ToString() is not ("code" or "call" or "export")||n["kind"]?.ToString()!="export"&&n["control"]?.ToString()!="next"))throw new InvalidOperationException("Shared caller batching preserves copy, private, native and wrapper contexts; save those contracts separately");
   }
  }
  return new(request);
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
