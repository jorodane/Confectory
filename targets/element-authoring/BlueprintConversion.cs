using Confectory.Core;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

// Explicit preparation and pending-conversion verification only. Never writes sources.
internal static class BlueprintConversion
{
 public static JsonObject Query(JsonObject request)
 {
  bool verify=request["action"]?.ToString()=="verify";
  var origin=verify?request["origin"]!.AsObject():null;
  string project=Path.GetFullPath(request["project"]!.GetValue<string>()),root=Path.GetDirectoryName(project)!;
  string id=(origin??request)["id"]!.GetValue<string>(),target=(origin??request)["target"]!.GetValue<string>();
  string graphPath=(origin??request)["graphPath"]!.GetValue<string>(),nodePath=(origin??request)["nodePath"]!.GetValue<string>();
  if(target.Length>128||!Regex.IsMatch(target,@"\A[A-Za-z_][A-Za-z_0-9.-]*\z"))throw new ArgumentException("Explicit body target required");
  string graphFull=PackPaths.Owned(root,graphPath),nodeFull=PackPaths.Owned(Path.GetDirectoryName(graphFull)!,nodePath);
  PackPaths.Owned(root,Path.GetRelativePath(root,nodeFull));
  if(graphFull==nodeFull)throw new ArgumentException("Separate graph and node destinations required");
  int bytes=0;var observations=new SortedDictionary<string,string>(StringComparer.Ordinal);
  string Read(string path)
  {
   path=Path.GetFullPath(path);var file=new FileInfo(path);if(!file.Exists||file.Length>1048576)throw new IOException("Conversion source unavailable or over one MiB: "+path);
   for(FileSystemInfo? current=file;current is not null;current=current is FileInfo f?f.Directory:((DirectoryInfo)current).Parent)if(current.LinkTarget is not null)throw new IOException("Conversion sources cannot traverse links");
   byte[] raw=File.ReadAllBytes(path);string hash=JsonData.HashBytes(raw);
   if(observations.TryGetValue(path,out string? before)){if(before!=hash)throw new IOException("Conversion source changed during read");}
   else{bytes=checked(bytes+raw.Length);if(bytes>2097152||observations.Count>=64)throw new IOException("Conversion observation budget exceeded");observations[path]=hash;}
   // Match Documents.Body exactly, including CRLF and any UTF-8 BOM character.
   string value=new UTF8Encoding(false,true).GetString(raw);if(JsonData.HashBytes(File.ReadAllBytes(path))!=hash)throw new IOException("Conversion source changed during decode");return value;
  }
  Read(project);
  var registry=new Registry(project,new Documents(Path.Combine(root,".confectory","conversion-cache"),new BuildStatistics()),new BuildStatistics());
  if(PackPaths.Namespace(id)!=registry.Project.Namespace)throw new ArgumentException("Select an implementation owned by the current ProjectPack");
  var physical=registry.Get(id,"implementation");string implementationText=Read(physical.Loc.File);
  string expected=verify?origin!["originalImplementation"]!.GetValue<string>():request["text"]!.GetValue<string>();
  if(JsonData.Digest(new Parser(implementationText,physical.Loc.File).ParseElement())!=JsonData.Digest(physical))throw new InvalidOperationException("Implementation changed while loading its conversion context");
  if(expected!=implementationText)throw new InvalidOperationException("Confirm existing declaration edits before converting this body's current published version");
  foreach(string path in registry.Paths.Values)Read(path);
  for(Element? current=physical;current is not null;current=current.Parent is null?null:registry.Get(current.Parent,"implementation",current.Id))Read(current.Loc.File);
  var effective=registry.Effective(id);
  if(!effective.Bodies.TryGetValue(target,out var body)||body.SourceKind!="csharp")throw new ArgumentException("Select an existing C# body target; graph conversion is explicit and target-specific");
  string oldPath=PackPaths.Owned(Path.GetDirectoryName(registry.Paths[PackPaths.Namespace(body.Origin)])!,body.Path);
  if(graphFull==oldPath||nodeFull==oldPath||graphFull==physical.Loc.File||nodeFull==physical.Loc.File)throw new ArgumentException("Preserve the original body and declaration destinations");
  string source=Read(oldPath);
  var function=registry.Get(effective.Function!,"function",id);string featureText=Read(function.Loc.File);
  var contracts=new JsonObject();foreach(string feature in effective.Imports.Values.Select(i=>i.Id).Distinct(StringComparer.Ordinal)){var fn=registry.Get(feature,"function",id);contracts[feature]=Read(fn.Loc.File);}
  var context=FeatureBlueprint.ImplementationContext(effective);
  var signature=context["signature"]!.DeepClone();var arguments=new JsonObject();
  for(int i=0;i<effective.Signature!.Args.Count;i++)arguments[effective.Signature.Args[i].Name]=new JsonObject{["input"]=function.Signature!.Args[i].Name};
  var nodes=new JsonArray(new JsonObject{["id"]="body",["kind"]="code",["intent"]="Whole existing body of "+id+" / "+target,["control"]="next",["signature"]=signature,["arguments"]=arguments,["implementation"]=nodePath,["implementationContext"]=context.DeepClone(),["sourceIdentity"]=oldPath});
  var edges=new JsonArray();
  if(effective.Signature.Return!="void"){
   nodes.Add(new JsonObject{["id"]="return",["kind"]="export",["intent"]="Assign the existing body's return",["control"]="next",["output"]="return",["signature"]=new JsonObject{["args"]=new JsonArray(new JsonObject{["name"]="value",["type"]=effective.Signature.Return}),["return"]="void"},["arguments"]=new JsonObject{["value"]=new JsonObject{["node"]="body"}}});
   edges.Add(new JsonObject{["from"]="body",["port"]="next",["to"]="return"});
  }
  var graph=new JsonObject{["schema"]=1,["profile"]=FeatureBlueprint.ImplicitProfile,["feature"]=function.Id,["contractHash"]=FeatureBlueprint.ContractHash(function),["entry"]="body",["nodes"]=nodes,["edges"]=edges,["exits"]=new JsonObject()};
  var definitions=FeatureBlueprint.Execute(new JsonObject{["operation"]="featureBlueprintNodes",["featureSource"]=featureText,["featureContracts"]=contracts,["implementationContext"]=context.DeepClone(),["graph"]=graph.DeepClone()});
  if(definitions["state"]?.ToString()!="node-definitions")throw new ArgumentException(definitions.ToJsonString());
  var record=new JsonObject{["schema"]=1,["node"]="body",["definitionHash"]=definitions["nodes"]!.AsArray().Single(n=>n!["id"]!.ToString()=="body")!["definitionHash"]!.DeepClone(),["source"]=source};
  var receipt=new JsonObject{["schema"]=1,["id"]=id,["target"]=target,["graphPath"]=graphPath,["nodePath"]=nodePath,["originalImplementation"]=implementationText,["originalBodyPath"]=oldPath,["originalBodyHash"]=observations[oldPath],["bodyOrigin"]=body.Origin,["observations"]=new JsonArray(observations.Select(p=>(JsonNode)new JsonObject{["path"]=p.Key,["sha256"]=p.Value}).ToArray())};
  foreach(var pair in observations)if(JsonData.HashBytes(File.ReadAllBytes(pair.Key))!=pair.Value)throw new IOException("Conversion source changed during preparation");
  if(verify&& !JsonNode.DeepEquals(origin,receipt))throw new InvalidOperationException("Pending conversion origin changed; preserve the original body and review a new conversion");
  string declaration=ReplaceBody(implementationText,target,graphPath);
  return new JsonObject{["id"]=id+"/body:"+target,["implementation"]=declaration,["graph"]=graph,["node"]=record,["origin"]=receipt,["context"]=context,["signature"]=context["signature"]!.DeepClone(),["observedBytes"]=bytes,["sourceWritten"]=false,["compiled"]=false};
 }

 private static string ReplaceBody(string text,string target,string graphPath)
 {
  // Token spans skip comments and quoted strings; descriptions never become body locators.
  var tokens=new List<(string Value,int Start,int End)>();
  for(int i=0;i<text.Length;){
   if(char.IsWhiteSpace(text[i])){i++;continue;}
   if(text[i]=='/'&&i+1<text.Length&&text[i+1]=='/'){while(i<text.Length&&text[i]!='\n')i++;continue;}
   int start=i;if(text[i]=='"'){i++;while(i<text.Length){if(text[i]=='\\'){i+=2;continue;}if(text[i++]=='"')break;}tokens.Add(("<string>",start,i));continue;}
   if(char.IsLetterOrDigit(text[i])||text[i]=='_'){while(i<text.Length&&(char.IsLetterOrDigit(text[i])||text[i]=='_'||text[i]=='.'))i++;}
   else i++;
   tokens.Add((text[start..i],start,i));
  }
  string next="blueprint "+target+" "+JsonSerializer.Serialize(graphPath)+";";
  for(int i=0;i+3<tokens.Count;i++)if(tokens[i].Value=="body"&&tokens[i+1].Value==target&&tokens[i+2].Value=="<string>"&&tokens[i+3].Value==";")return text[..tokens[i].Start]+next+text[tokens[i+3].End..];
  int end=tokens.Last(t=>t.Value=="}").Start;return text[..end]+"\n"+next+"\n"+text[end..];
 }
}
