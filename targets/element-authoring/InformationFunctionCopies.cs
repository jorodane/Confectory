using Confectory.Core;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

// A verified editing view for a saved, directly assigned copy. Provenance is
// detached only inside this view and restored before a candidate can leave it.
// Donor declarations/bodies are never used as writable source identities.
internal sealed class InformationFunctionCopies(JsonObject request,Action<string>? observe=null)
{
 readonly JsonObject units=request["units"]!.AsObject();
 readonly Dictionary<string,View> views=new(StringComparer.Ordinal);
 readonly Dictionary<string,string> reads=new(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);
 readonly SortedDictionary<string,string> context=new(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);
 Registry? registry;
 int bytes,files;
 static string Hash(string text)=>JsonData.HashBytes(Encoding.UTF8.GetBytes(text));
 public sealed class View
 {
  readonly string id,text;
  readonly JsonObject? provenance;
  internal View(string id,string text,JsonObject? provenance,JsonObject proof){this.id=id;this.text=text;this.provenance=provenance?.DeepClone().AsObject();Proof=proof;}
  public JsonObject Proof{get;}
  public JsonObject EditingGraph(){var graph=JsonNode.Parse(text)!.AsObject();if(provenance is not null)graph.Remove("copySource");return graph;}
  public bool Matches(string graph,string source)=>provenance is not null&&id==graph&&text==source;
  public void Restore(JsonObject graph){if(provenance is null)return;if(graph["copySource"] is not null)throw new InvalidOperationException("Do not replace original copy provenance");graph["copySource"]=provenance.DeepClone();}
 }
 Registry Registry()
 {
  if(registry is not null)return registry;
  string project=PackPaths.Resolve(request["project"]!.ToString()),manifest=request["manifest"]!.ToString(),root=Path.GetDirectoryName(project)!;
  var selected=new Parser(manifest,project).ParseManifest();var owned=new Dictionary<string,string>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);
  foreach(var row in selected.Elements){string id=selected.Namespace+"::"+row.Key;var unit=units[id]??throw new InvalidOperationException("Complete owned copy context required");if(unit["kind"]?.ToString()!=row.Value.Kind||unit["path"]?.ToString()!=row.Value.Path)throw new InvalidOperationException("Copy declaration locator changed");owned.Add(PackPaths.Owned(root,row.Value.Path),unit["draft"]!.ToString());}
  byte[] Read(string path){path=PackPaths.Resolve(path);for(FileSystemInfo? current=new FileInfo(path);current is not null;current=current is FileInfo file?file.Directory:((DirectoryInfo)current).Parent)if(current.LinkTarget is not null)throw new ArgumentException("Copy context cannot traverse links");string text;
   if(path==project){var info=new FileInfo(path);if(!info.Exists||info.Length>1048576)throw new ArgumentException("Bounded copy project required");text=File.ReadAllText(path,new UTF8Encoding(false,true));var physical=new Parser(text,path).ParseManifest();if(physical.Namespace!=selected.Namespace||physical.Registry.Count!=selected.Registry.Count||physical.Registry.Any(p=>!selected.Registry.TryGetValue(p.Key,out var row)||row.Path!=p.Value.Path)||physical.Dependencies.Count!=selected.Dependencies.Count||physical.Dependencies.Any(p=>!selected.Dependencies.TryGetValue(p.Key,out var row)||row.Version!=p.Value.Version))throw new InvalidOperationException("Confirm changed copy registration separately");observe?.Invoke(path);text=manifest;}
   else if(owned.TryGetValue(path,out var draft))text=draft;
   else{var info=new FileInfo(path);if(!info.Exists||info.Length>1048576)throw new ArgumentException("Bounded copy declaration required");text=File.ReadAllText(path,new UTF8Encoding(false,true));observe?.Invoke(path);}
   var raw=Encoding.UTF8.GetBytes(text);string hash=JsonData.HashBytes(raw);if(reads.TryGetValue(path,out var prior)){if(prior!=hash)throw new InvalidOperationException("Copy context changed while reading");}else{reads.Add(path,hash);bytes=checked(bytes+raw.Length);files++;}if(raw.Length>1048576||bytes>16777216||files>2048)throw new ArgumentException("Copy context budget");context[path]=hash;return raw;
  }
  var statistics=new BuildStatistics();registry=new Registry(project,new Documents("",statistics,Read),statistics);return registry;
 }
 public View For(string id)
 {
  if(views.TryGetValue(id,out var existing))return existing;var unit=units[id]??throw new InvalidOperationException("Original copy graph required");string text=unit["draft"]!.ToString();if(unit["kind"]?.ToString()!="blueprint"||Encoding.UTF8.GetByteCount(text)>1048576)throw new ArgumentException("Bounded original copy graph required");var graph=JsonNode.Parse(text)!.AsObject();
  if(graph["copySource"] is not null&&graph["copySource"] is not JsonObject)throw new InvalidOperationException("Exact saved copy provenance required");
  if(graph["copySource"] is not JsonObject provenance){int at=id.LastIndexOf("/body:",StringComparison.Ordinal);if(at>=0&&units[id[..at]]?["copySource"] is not null)throw new InvalidOperationException("Retain the saved copy provenance on its graph");return new View(id,text,null,new());}
  if(unit["baseline"]?.ToString() is null or "missing")throw new InvalidOperationException("Confirm a new copy before editing its saved function contract; retain input");
  int slash=id.LastIndexOf("/body:",StringComparison.Ordinal);if(slash<0)throw new ArgumentException("Exact saved copy root required");string implementation=id[..slash];var implUnit=units[implementation]??throw new InvalidOperationException("Copy implementation required");
  var d=new Parser(implUnit["draft"]!.ToString(),"<owned-information-copy>").ParseElement();
  var objects=new JsonArray(units.Where(p=>p.Value?["kind"]?.ToString() is "object" or "schema").OrderBy(p=>p.Key,StringComparer.Ordinal).Select(p=>(JsonNode)new JsonObject{["id"]=p.Key,["path"]=p.Value!["path"]!.DeepClone(),["text"]=p.Value["draft"]!.DeepClone()}).ToArray());
  var owners=objects.Where(p=>new Parser(p!["text"]!.ToString(),"<copy-assignment>").ParseElement().Provides.GetValueOrDefault(d.Function!)?.Id==implementation).ToArray();if(owners.Length!=1)throw new InvalidOperationException("Select one directly owned copy assignment; shared copies retain every source");
  registry=null;context.Clear();string owner=owners[0]!["id"]!.ToString();var r=Registry();var effective=r.Effective(owner);var fn=r.Effective(d.Function!);var requirements=new JsonArray();var module=new Planner(r,"metadata").ModulesFor(owner);
  if(module.Required.TryGetValue(fn.Id,out var required))requirements.Add(new JsonObject{["function"]=fn.Id,["signature"]=JsonSerializer.SerializeToNode(fn.Signature),["moduleSignature"]=JsonSerializer.SerializeToNode(required.Signature)});
  else if(effective.Kind=="schema"&&effective.Contains.Any(c=>c.Kind=="function"&&c.Id==fn.Id&&c.Origin==owner))requirements.Add(new JsonObject{["function"]=fn.Id,["signature"]=JsonSerializer.SerializeToNode(fn.Signature),["moduleSignature"]=JsonSerializer.SerializeToNode(fn.Signature)});
  else throw new InvalidOperationException("Existing module or directly contained information function required");
  var provider=r.Implementation(fn.Id,implementation,owner,d.Loc);var providers=new JsonArray(new JsonObject{["function"]=fn.Id,["implementation"]=implementation,["origin"]=owner,["contract"]=new JsonObject{["status"]="valid"}});
  var proof=BlueprintCopyAbi.Bind(new JsonObject{["id"]=implementation,["text"]=implUnit["draft"]!.DeepClone(),["implementationPath"]=implUnit["path"]!.DeepClone(),["functionText"]=units[fn.Id]?["draft"]?.DeepClone()??throw new InvalidOperationException("Owned copy function required"),["owner"]=owner,["ownerText"]=units[owner]!["draft"]!.DeepClone(),["graphId"]=id,["graphPath"]=unit["path"]!.DeepClone(),["graph"]=graph.DeepClone(),["unitProvenance"]=implUnit["copySource"]?.DeepClone(),["objects"]=objects,["requirements"]=requirements,["providers"]=providers,["requireValid"]=true});
  proof["graphHash"]=Hash(text);proof["implementationHash"]=Hash(implUnit["draft"]!.ToString());
  proof["context"]=new JsonArray(context.Select(p=>(JsonNode)new JsonObject{["path"]=p.Key,["hash"]=p.Value}).ToArray());
  var view=new View(id,text,provenance,proof);views.Add(id,view);return view;
 }
 public JsonObject Read(string function)
 {
  if(units.Count>2048)throw new ArgumentException("Owned copy context budget");var proofs=new JsonObject();foreach(var row in units.Where(p=>p.Value?["kind"]?.ToString()=="implementation")){var impl=new Parser(row.Value!["draft"]!.ToString(),"<copy-closure>").ParseElement();if(impl.Function!=function&&!impl.Imports.Values.Any(i=>i.Id==function))continue;foreach(var body in impl.Bodies.Where(p=>p.Value.SourceKind=="blueprint")){string id=impl.Id+"/body:"+body.Key;var view=For(id);if(view.Proof.Count>0)proofs[id]=view.Proof.DeepClone();}}if(proofs.Count>32)throw new ArgumentException("Saved copy selection budget");return proofs;
 }
 public void ValidateAfter(string function,string functionText,JsonArray updates)
 {
  if(views.Count==0)return;var candidate=request.DeepClone().AsObject();var afterUnits=candidate["units"]!.AsObject();afterUnits[function]!["draft"]=functionText;
  foreach(var row in updates)afterUnits[row!["id"]!.ToString()]!["draft"]=row["text"]!.DeepClone();
  var after=new InformationFunctionCopies(candidate,observe).Read(function);
  if(after.Count!=views.Count)throw new InvalidOperationException("Copy assignments changed during candidate preparation");
  foreach(var row in views)foreach(string field in new[]{"owner","ownerHash","objectsHash","implementation","implementationPath","graph","graphPath","target","function","provenance"})if(!JsonNode.DeepEquals(row.Value.Proof[field],after[row.Key]?[field]))throw new InvalidOperationException("Preserve the copy owner, target and original provenance");
 }
 public static JsonObject Query(JsonObject request)
 {
  string owner=request["id"]!.ToString(),function=request["function"]!.ToString();var schema=new Parser(request["units"]![owner]!["draft"]!.ToString(),"<information-copy-owner>").ParseElement();if(schema.Id!=owner||schema.Kind!="schema"||!function.StartsWith(owner+"_Function_",StringComparison.Ordinal)||!schema.Contains.Any(c=>c.Kind=="function"&&c.Id==function))throw new InvalidOperationException("Direct owned information function required");return new InformationFunctionCopies(request).Read(function);
 }
}
