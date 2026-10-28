using Confectory.Core;
using System.Text;
using System.Text.Json.Nodes;

// Registered declarations are read-only evidence, never workspace write units.
// Restore validates the saved snapshot without consulting mutable external files;
// Save, Review and Confirm separately recheck the current registry receipt.
internal static class BlueprintAbiContracts
{
 public static JsonObject Validate(JsonObject? snapshot,Element caller,string path)
 {
  var foreign=caller.Imports.Values.Select(i=>i.Id).Where(id=>PackPaths.Namespace(id)!=PackPaths.Namespace(caller.Id)).ToHashSet(StringComparer.Ordinal);
  if(snapshot is null){if(foreign.Count!=0)throw new ArgumentException("Registered target contracts require their read-only snapshot");return new();}
  if(snapshot.Count!=5||snapshot.Any(p=>p.Key is not ("schema" or "manifest" or "path" or "text" or "contracts"))||snapshot["schema"]?.GetValue<int>()!=1||Encoding.UTF8.GetByteCount(snapshot.ToJsonString())>2097152)throw new ArgumentException("Bounded exact registered target snapshot required");
  string ns=PackPaths.Namespace(caller.Id),manifestText=snapshot["text"]!.GetValue<string>();var manifest=new Parser(manifestText,"<abi-owner-manifest>").ParseManifest();
  if(manifest.Kind!="project"||manifest.Namespace!=ns||PackPaths.Namespace(snapshot["manifest"]!.ToString())!=ns||!manifest.Elements.TryGetValue(caller.Id[(ns.Length+2)..],out var locator)||locator.Kind!="implementation"||locator.Path!=path)throw new ArgumentException("Exact owned caller/manifest locator required");
  string root=Path.Combine(Path.GetTempPath(),"confectory-pure-abi-contracts");PackPaths.Owned(root,path);PackPaths.Owned(root,snapshot["path"]!.ToString());
  var rows=snapshot["contracts"]!.AsObject();if(foreign.Count==0||!foreign.SetEquals(rows.Select(p=>p.Key)))throw new ArgumentException("Exactly the imported registered contracts required");var contracts=new JsonObject();
  foreach(var row in rows){
   var proof=row.Value!.AsObject();var receipt=proof["receipt"]!.AsObject();string text=proof["text"]!.GetValue<string>(),dependency=PackPaths.Namespace(row.Key);var fn=new Parser(text,"<abi-registered-function>").ParseElement();
   if(proof.Count!=2||proof.Any(p=>p.Key is not ("text" or "receipt"))||fn.Kind!="function"||fn.Id!=row.Key||!manifest.Dependencies.ContainsKey(dependency)||!manifest.Registry.ContainsKey(dependency)||receipt.Count!=4||receipt.Any(p=>p.Key is not ("id" or "ownerManifestHash" or "manifestHash" or "textHash"))||receipt["id"]?.ToString()!=row.Key||receipt["ownerManifestHash"]?.ToString()!=JsonData.HashBytes(Encoding.UTF8.GetBytes(manifestText))||receipt["textHash"]?.ToString()!=JsonData.HashBytes(Encoding.UTF8.GetBytes(text))||!System.Text.RegularExpressions.Regex.IsMatch(receipt["manifestHash"]?.ToString()??"",@"\A[a-f0-9]{64}\z"))throw new ArgumentException("Exact read-only registered function receipt required");
   contracts[row.Key]=text;
  }
  return contracts;
 }
 public static void Verify(string project,JsonObject snapshot,string callerText)
 {
  if(Path.GetFileName(project)!=snapshot["path"]!.ToString())throw new ArgumentException("Current project manifest required");
  var caller=new Parser(callerText,"<abi-registered-caller>").ParseElement();Validate(snapshot,caller,new Parser(snapshot["text"]!.ToString(),"<abi-owner>").ParseManifest().Elements[caller.Id[(PackPaths.Namespace(caller.Id).Length+2)..]].Path);
  int bytes=0;foreach(var contract in snapshot["contracts"]!.AsObject()){
   var current=BlueprintCallableContracts.Query(new JsonObject{["action"]="read",["project"]=project,["manifest"]=snapshot["text"]!.DeepClone(),["sourceId"]=caller.Id,["text"]=callerText,["id"]=contract.Key});
   bytes=checked(bytes+current["registeredBytes"]!.GetValue<int>());if(bytes>2097152||current["bodyReads"]?.GetValue<int>()!=0||!JsonNode.DeepEquals(current["receipt"],contract.Value!["receipt"])||current["text"]?.ToString()!=contract.Value["text"]?.ToString())throw new InvalidOperationException("Registered target contract changed; preserve all input and explicitly refresh");
  }
 }
}
