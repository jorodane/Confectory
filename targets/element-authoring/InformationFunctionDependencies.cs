using Confectory.Core;
using System.Text;
using System.Text.Json.Nodes;

// Existing direct-dependency function declarations only. No provider body or
// registration is read or changed, and a new receipt never replaces a saved one.
internal sealed class InformationFunctionDependencies(JsonObject request,Action<string>? observe=null)
{
 readonly Dictionary<string,(string Text,Element Function)> functions=new(StringComparer.Ordinal);
 readonly Dictionary<string,JsonObject> proofs=new(StringComparer.Ordinal);
 readonly Dictionary<string,string> reads=new(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);
 int bytes;
 string Project=>request["project"]?.ToString()??throw new InvalidOperationException("Registered callable project context required");
 string Manifest=>request["manifest"]?.ToString()??throw new InvalidOperationException("Registered callable manifest context required");
 static string Hash(string text)=>JsonData.HashBytes(Encoding.UTF8.GetBytes(text));
 static string Read(string path)
 {
  for(FileSystemInfo? current=new FileInfo(path);current is not null;current=current is FileInfo file?file.Directory:((DirectoryInfo)current).Parent)if(current.LinkTarget is not null)throw new ArgumentException("Callable declarations cannot traverse links");
  var info=new FileInfo(path);if(!info.Exists||info.Length>1048576)throw new ArgumentException("Bounded registered declaration required");return File.ReadAllText(path,new UTF8Encoding(false,true));
 }
 void Observe(string path,string expected)
 {
  path=PackPaths.Resolve(path);string text=Read(path);if(Hash(text)!=expected||reads.TryGetValue(path,out var previous)&&previous!=expected)throw new InvalidOperationException("Registered callable changed while preparing; retain input");
  if(!reads.ContainsKey(path)){bytes=checked(bytes+Encoding.UTF8.GetByteCount(text));if(bytes>2097152||reads.Count>=128)throw new ArgumentException("Registered callable observation budget");reads.Add(path,expected);}observe?.Invoke(path);if(Hash(Read(path))!=expected)throw new InvalidOperationException("Registered callable changed while observing; retain input");
 }
 public JsonObject For(Element implementation,string text)
 {
  if(proofs.TryGetValue(implementation.Id,out var saved))return saved.DeepClone().AsObject();string ns=PackPaths.Namespace(implementation.Id);
  var ids=implementation.Imports.Values.Select(i=>i.Id).Concat(implementation.Function is null?[]:[implementation.Function]).Where(id=>PackPaths.Namespace(id)!=ns).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal).ToArray();
  if(ids.Length==0)return new JsonObject();if(ids.Length>32)throw new ArgumentException("Registered import budget");
  string project=PackPaths.Resolve(Project),manifest=Manifest;string physicalText=Read(project);var physical=new Parser(physicalText,project).ParseManifest();var selected=new Parser(manifest,"<selected-callable-project>").ParseManifest();
  if(physical.Kind!="project"||physical.Namespace!=selected.Namespace||physical.Registry.Count!=selected.Registry.Count||physical.Registry.Any(p=>!selected.Registry.TryGetValue(p.Key,out var row)||row.Path!=p.Value.Path)||physical.Dependencies.Count!=selected.Dependencies.Count||physical.Dependencies.Any(p=>!selected.Dependencies.TryGetValue(p.Key,out var row)||row.Version!=p.Value.Version))throw new InvalidOperationException("Confirm registration changes separately before editing function contracts");
  Observe(project,Hash(physicalText));var contracts=new JsonObject();
  foreach(string id in ids){var data=BlueprintCallableContracts.Query(new JsonObject{["action"]="read",["project"]=project,["manifest"]=manifest,["sourceId"]=implementation.Id,["text"]=text,["id"]=id});string source=data["text"]!.GetValue<string>();var function=new Parser(source,"<registered-read-only-callable>").ParseElement();
   if(function.Id!=id||function.Kind!="function"||function.Signature is null||function.Parent is not null)throw new InvalidOperationException("An inherited callable needs its complete parent declaration receipt; retain input");
   foreach(var import in implementation.Imports.Values.Where(i=>i.Id==id))if(!import.Signature.Matches(function.Signature))throw new InvalidOperationException("Registered typed import changed; explicitly refresh it before this contract edit");
   if(implementation.Function==id&&!implementation.Signature!.Matches(function.Signature))throw new InvalidOperationException("The read-only implemented function contract changed; retain input");
   if(functions.TryGetValue(id,out var prior)&&prior.Text!=source)throw new InvalidOperationException("Registered function declaration changed");functions[id]=(source,function);if(functions.Count>64)throw new ArgumentException("Registered callable closure budget");
   foreach(var row in data["observations"]!.AsArray())Observe(row!["path"]!.ToString(),row["hash"]!.ToString());contracts[id]=data["receipt"]!.DeepClone();
  }
  var proof=new JsonObject{["schema"]=1,["caller"]=implementation.Id,["callerHash"]=Hash(text),["contracts"]=contracts};proofs.Add(implementation.Id,proof);return proof.DeepClone().AsObject();
 }
 public JsonObject Read(string function,JsonObject units)
 {
  var result=new JsonObject();foreach(var unit in units){if(unit.Value?["kind"]?.ToString()!="implementation")continue;string text=unit.Value["draft"]!.ToString();var d=new Parser(text,"<registered-caller>").ParseElement();if(d.Function!=function&&!d.Imports.Values.Any(i=>i.Id==function))continue;var proof=For(d,text);if(proof.Count>0)result[d.Id]=proof;}if(result.Count>64)throw new ArgumentException("Registered caller proof budget");return result;
 }
 public Dictionary<string,Element> AddTo(IReadOnlyDictionary<string,Element> owned)
 {
  var result=owned.ToDictionary(p=>p.Key,p=>p.Value,StringComparer.Ordinal);foreach(var pair in functions){if(result.ContainsKey(pair.Key))throw new InvalidOperationException("A read-only declaration cannot replace an owned source");result[pair.Key]=pair.Value.Function;}return result;
 }
 public JsonObject Sources()=>new(functions.Select(p=>KeyValuePair.Create<string,JsonNode?>(p.Key,JsonValue.Create(p.Value.Text))));
 public static JsonObject Query(JsonObject request)
 {
  string owner=request["id"]!.ToString(),function=request["function"]!.ToString();var units=request["units"]!.AsObject();var schema=new Parser(units[owner]!["draft"]!.ToString(),"<registered-owner>").ParseElement();
  if(units.Count>2048||schema.Kind!="schema"||!schema.Contains.Any(c=>c.Kind=="function"&&c.Id==function)||!function.StartsWith(owner+"_Function_",StringComparison.Ordinal))throw new InvalidOperationException("Direct owned information function required");return new InformationFunctionDependencies(request).Read(function,units);
 }
}
