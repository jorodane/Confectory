using Confectory.Core;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

internal static class ConnectionSettingsRepair
{
 // Read-only proposal. The caller backs up and commits using the observed file
 // revisions. Nothing here writes a profile, changes Settings, or grants access.
 public static JsonObject Propose(Manifest fresh,Registry installed,string connection,JsonObject request,Func<Manifest,string> format)
 {
  JsonObject Preserve(string reason)=>new(){["state"]="preserved",["reason"]=reason};
  string text=request["manifest"]!.GetValue<string>(),source=request["text"]!.GetValue<string>();
  if(text.Length>1048576||source.Length>1048576)return Preserve("copy-budget");
  try{
   var old=new Parser(text,"<settings-copy>").ParseManifest();var settings=new Parser(source,"<settings-source>").ParseElement();
   string Compact(string value)=>Regex.Replace(value,@"""(?:\\.|[^""\\])*""|\s+",m=>m.Value[0]=='"'?m.Value:"");
   if(old.Kind!="project"||old.Namespace!=fresh.Namespace||old.Version!=fresh.Version||old.Description!=fresh.Description||old.Standalone!=false||old.Entry is not null||old.Targets.Count!=0||old.Always.Count!=0||old.Elements.Count!=1||!old.Elements.TryGetValue("Settings",out var locator)||locator.Kind!="object"||locator.Path!="Settings.celem"||Compact(text)!=Compact(format(old)))return Preserve("custom-manifest");
   if(settings.Kind!="object"||settings.Id!=fresh.Namespace+"::Settings"||settings.Parent!=connection)return Preserve("settings-identity");
   foreach(var pair in old.Dependencies)if(!fresh.Dependencies.TryGetValue(pair.Key,out var expected)||pair.Value.Version!=expected.Version)return Preserve("custom-dependency");
   string repository=System.IO.Path.GetFullPath(request["repository"]!.GetValue<string>()),settingsRoot=System.IO.Path.GetDirectoryName(System.IO.Path.GetFullPath(request["settingsProject"]!.GetValue<string>()))!;
   var comparison=OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal;
   string? oldRoot=null;bool relocated=false,missingOldPath=false;
   foreach(var pair in old.Registry.ToArray()){
    if(!fresh.Registry.TryGetValue(pair.Key,out var current))return Preserve("registration-not-installed");
    string from=System.IO.Path.GetFullPath(System.IO.Path.Combine(settingsRoot,pair.Value.Path)),to=current.Path;
    if(string.Equals(from,to,comparison))continue;
    string relative=System.IO.Path.GetRelativePath(repository,to).Replace('\\','/'),normalized=from.Replace('\\','/');
    if(relative.StartsWith("../",StringComparison.Ordinal)||System.IO.Path.IsPathRooted(relative)||!normalized.EndsWith("/"+relative,comparison)||!System.IO.File.Exists(to))return Preserve("custom-registration-path");
    string prefix=normalized[..^(relative.Length+1)];if(oldRoot is not null&&!string.Equals(oldRoot,prefix,comparison))return Preserve("inconsistent-old-root");oldRoot=prefix;relocated=true;missingOldPath|=!System.IO.File.Exists(from);old.Registry[pair.Key]=current;
   }
   if(relocated&&!missingOldPath)return Preserve("old-checkout-still-present");
   string selected=connection.Split("::")[0];bool dependencyAdded=old.Dependencies.TryAdd(selected,fresh.Dependencies[selected]);
   var pending=new Queue<string>(old.Registry.Keys.Concat(old.Dependencies.Keys));var visited=new HashSet<string>(StringComparer.Ordinal);var added=new JsonArray();
   while(pending.TryDequeue(out string? ns)){
    if(!visited.Add(ns))continue;
    if(!old.Registry.ContainsKey(ns)){
     if(!fresh.Registry.TryGetValue(ns,out var registration))return Preserve("dependency-not-installed");
     old.Registry.Add(ns,registration);added.Add(ns);
    }
    if(!installed.Packs.TryGetValue(ns,out var pack))return Preserve("dependency-not-installed");
    foreach(string dependency in pack.Dependencies.Keys)pending.Enqueue(dependency);
   }
   if(!relocated&&!dependencyAdded&&added.Count==0)return new(){["state"]="unchanged"};
   return new(){["state"]="repair",["manifest"]=format(old),["addedNamespaces"]=added,["selectedDependencyAdded"]=dependencyAdded,["relocated"]=relocated};
  }catch(Exception error) when(error is BuildError or ArgumentException){return Preserve("unrecognized-copy");}
 }
}
