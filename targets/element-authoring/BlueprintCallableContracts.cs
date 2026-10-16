using Confectory.Core;
using System.Text;
using System.Text.Json.Nodes;

// Explicit direct dependencies only. This reads manifests and the selected function,
// never implementations, provider bodies or a transitive registry.
internal static class BlueprintCallableContracts
{
 public static JsonObject Query(JsonObject request)
 {
  string project=Path.GetFullPath(request["project"]!.GetValue<string>()),manifestText=request["manifest"]!.GetValue<string>(),sourceText=request["text"]!.GetValue<string>();
  if(Encoding.UTF8.GetByteCount(manifestText)>1048576||Encoding.UTF8.GetByteCount(sourceText)>1048576||Encoding.UTF8.GetByteCount(manifestText)+Encoding.UTF8.GetByteCount(sourceText)>2097152)throw new ArgumentException("Callable source budget exceeded");
  var owner=new Parser(manifestText,"<callable-project>").ParseManifest();var source=new Parser(sourceText,"<callable-caller>").ParseElement();
  if(owner.Kind!="project"||source.Kind is not ("implementation" or "object")||source.Id!=request["sourceId"]!.ToString()||PackPaths.Namespace(source.Id)!=owner.Namespace||!owner.Elements.TryGetValue(source.Id[(owner.Namespace.Length+2)..],out var sourceLocator)||sourceLocator.Kind!=source.Kind)throw new ArgumentException("Owned ProjectPack caller context required");
  string action=request["action"]!.GetValue<string>(),query=request["query"]?.GetValue<string>()??"",exclude=request["exclude"]?.GetValue<string>()??"";int page=request["page"]?.GetValue<int>()??0;
  if(action is not ("list" or "read")||query.Length>256||exclude.Length>512||page<0||page>1000000)throw new ArgumentException("Bounded explicit callable query required");
  string Hash(string value)=>Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(Encoding.UTF8.GetBytes(value))).ToLowerInvariant();
  var reads=new Dictionary<string,string>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);int bytes=Encoding.UTF8.GetByteCount(manifestText)+Encoding.UTF8.GetByteCount(sourceText);
  string Read(string path){
   path=Path.GetFullPath(path);for(FileSystemInfo? current=new FileInfo(path);current is not null;current=current is FileInfo file?file.Directory:((DirectoryInfo)current).Parent)if(current.LinkTarget is not null)throw new ArgumentException("Callable declarations cannot traverse links");
   var info=new FileInfo(path);if(!info.Exists||info.Length>1048576)throw new ArgumentException("Bounded registered declaration required");
   string text=File.ReadAllText(path,new UTF8Encoding(false,true));if(reads.TryGetValue(path,out string? previous)){if(previous!=text)throw new InvalidOperationException("Registered contract changed while reading");return text;}
   bytes=checked(bytes+Encoding.UTF8.GetByteCount(text));if(bytes>2097152)throw new ArgumentException("Registered callable read budget exceeded");reads.Add(path,text);return text;
  }
  (Manifest Pack,string Text,string Path) Pack(string ns){
   if(ns==owner.Namespace||!owner.Dependencies.ContainsKey(ns)||!owner.Registry.TryGetValue(ns,out var registration))throw new ArgumentException("Callable must be in a registered direct dependency");
   string path=Path.GetFullPath(Path.Combine(Path.GetDirectoryName(project)!,registration.Path)),text=Read(path);var pack=new Parser(text,path).ParseManifest();
   if(pack.Kind!="pack"||pack.Namespace!=ns)throw new ArgumentException("Registered callable pack identity differs");return (pack,text,path);
  }
  JsonObject result;
  if(action=="list"){
   var dependencies=owner.Dependencies.Keys.Where(ns=>ns!=owner.Namespace&&owner.Registry.ContainsKey(ns)).Order(StringComparer.Ordinal).ToArray();if(dependencies.Length>128)throw new ArgumentException("At most128 registered direct callable packs may be listed");
   var matches=new List<(string Id,string Version)>();foreach(string ns in dependencies){var registered=Pack(ns);foreach(var pair in registered.Pack.Elements)if(pair.Value.Kind=="function"&&ns+"::"+pair.Key!=exclude&&(ns+"::"+pair.Key).Contains(query,StringComparison.OrdinalIgnoreCase))matches.Add((ns+"::"+pair.Key,registered.Pack.Version));}
   matches.Sort((a,b)=>StringComparer.Ordinal.Compare(a.Id,b.Id));var rows=new JsonArray();foreach(var row in matches.Skip(checked(page*32)).Take(32))rows.Add(new JsonObject{["id"]=row.Id,["version"]=row.Version,["readOnly"]=true,["dirty"]=false});
   result=new(){["rows"]=rows,["total"]=matches.Count,["page"]=page,["pageSize"]=32};
  }else{
   string id=request["id"]!.GetValue<string>();new Parser("function "+id+" () -> void {}","<callable-id>").ParseElement();string ns=PackPaths.Namespace(id);var registered=Pack(ns);
   if(!registered.Pack.Elements.TryGetValue(id[(ns.Length+2)..],out var locator)||locator.Kind!="function")throw new ArgumentException("Registered function declaration required");
   string lexical=Path.GetFullPath(Path.Combine(Path.GetDirectoryName(registered.Path)!,locator.Path));string owned=PackPaths.Owned(Path.GetDirectoryName(registered.Path)!,locator.Path);if(owned!=lexical)throw new ArgumentException("Owned registered function path required");string text=Read(lexical);
   var function=new Parser(text,owned).ParseElement();if(function.Kind!="function"||function.Id!=id||function.Signature is null)throw new ArgumentException("Registered function locator identity differs");
   result=new(){["id"]=id,["kind"]="function",["text"]=text,["version"]=registered.Pack.Version,["receipt"]=new JsonObject{["id"]=id,["ownerManifestHash"]=Hash(manifestText),["manifestHash"]=Hash(registered.Text),["textHash"]=Hash(text)}};
  }
  foreach(var pair in reads.ToArray())Read(pair.Key);
  result["registeredBytes"]=reads.Values.Sum(value=>Encoding.UTF8.GetByteCount(value));result["scope"]="registered-direct-dependency-functions";result["readOnly"]=true;result["bodyReads"]=0;result["compiled"]=false;result["providerSelection"]="not-performed";return result;
 }
}
