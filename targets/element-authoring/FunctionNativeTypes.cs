using Confectory.Core;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

// Public native value types only. No object lookup, provider choice or grants.
internal static class FunctionNativeTypes
{
 internal static JsonArray Project(Registry registry,string owner,Func<string,string> source,Func<string,string> read)
 {
  string ns=PackPaths.Namespace(owner);var result=new JsonArray();
  var declarations=registry.Packs.Where(p=>p.Key==ns||registry.Packs[ns].Dependencies.ContainsKey(p.Key)).SelectMany(p=>p.Value.Elements.Where(e=>e.Value.Kind is "schema" or "enum" or "module").Select(e=>p.Key+"::"+e.Key)).Order(StringComparer.Ordinal).ToArray();
  foreach(string id in declarations){
   if(result.Count>=256)throw new ArgumentException("Native function type catalogue budget");
   var declared=registry.Get(id,source:owner);if(declared.Kind=="schema"&&OwnedInformationDefinitions.PrivateSchema(declared))continue;
   var row=new JsonObject{["id"]=id,["kind"]=declared.Kind,["clrType"]=InformationStructs.Type(id),["available"]=false};result.Add(row);
   try{
    var definition=registry.Effective(id);row["name"]=definition.Values.TryGetValue("editorName",out var label)&&label.Value.ValueKind==JsonValueKind.String?label.Value.GetString():id.Split("::")[1];
    var closure=InformationStructs.Closure(registry,id,owner);var selected=closure.Single(d=>d.Id==id);var proofs=new JsonObject();var seen=new HashSet<string>(StringComparer.Ordinal);
    void Observe(string current){
     if(!seen.Add(current))return;if(seen.Count>256)throw new ArgumentException("Native function type proof budget");
     var element=registry.Get(current);proofs[current]=new JsonObject{["draft"]=JsonData.HashBytes(Encoding.UTF8.GetBytes(source(current))),["source"]=JsonData.HashBytes(Encoding.UTF8.GetBytes(read(element.Loc.File))),["path"]=Path.GetFullPath(element.Loc.File)};
     if(element.Parent is not null)Observe(element.Parent);
     foreach(var include in element.Includes)Observe(include.Id);
     foreach(string required in element.Requires.Keys)Observe(required);
     foreach(var choice in element.Defaults.Values)Observe(choice.Id);
    }
    foreach(var item in closure)Observe(item.Id);
    foreach(string pack in seen.Select(PackPaths.Namespace).Append(ns).Distinct(StringComparer.Ordinal)){
     string path=Path.GetFullPath(registry.Paths[pack]);string hash=JsonData.HashBytes(Encoding.UTF8.GetBytes(read(path)));proofs["$manifest:"+pack]=new JsonObject{["source"]=hash,["path"]=path};
    }
    row["proof"]=new JsonObject{["shapeHash"]=selected.ShapeHash,["sources"]=proofs.DeepClone()};
    row["profile"]=selected.NativeProfile;row["shapeHash"]=selected.ShapeHash;row["sources"]=proofs;row["available"]=true;
   }catch(BuildError error){row["code"]=error.Diagnostic.Code;row["reason"]="이 정의는 현재 C# 값 타입으로 사용할 수 없어요. 원본은 유지됩니다.";}
  }
  return result;
 }
 internal static JsonObject Labels(Registry registry,FunctionSignature signature,string source)
 {
  var labels=new JsonObject();foreach(string type in InformationStructs.SignatureTypes(signature))try{
   var ids=registry.Packs.SelectMany(p=>p.Value.Elements.Where(e=>e.Value.Kind is "schema" or "enum" or "module").Select(e=>p.Key+"::"+e.Key)).Where(id=>InformationStructs.Type(id)==type).Take(2).ToArray();if(ids.Length!=1)continue;var element=registry.Effective(registry.Get(ids[0],source:source).Id);labels[type]=element.Values.TryGetValue("editorName",out var name)&&name.Value.ValueKind==JsonValueKind.String?name.Value.GetString():ids[0].Split("::")[1];
  }catch(BuildError){/* A label never weakens the existing contract validation. */}return labels;
 }
 internal static void Validate(FunctionSignature signature,JsonNode? proof,JsonArray choices)
 {
  var selected=InformationStructs.SignatureTypes(signature).ToArray();
  if(selected.Length>0&&proof is null)throw new InvalidOperationException("Read and select exact native function type proofs before creation; input retained");
  if(proof is not null&&(proof is not JsonObject map||map.Count!=selected.Length||map.Any(p=>!selected.Contains(p.Key,StringComparer.Ordinal))))throw new ArgumentException("Exact selected native type proofs required");
  foreach(string type in selected){
   var choice=choices.SingleOrDefault(c=>c?["clrType"]?.ToString()==type);
   if(choice?["available"]?.GetValue<bool>()!=true||proof is not null&&!JsonNode.DeepEquals(choice["proof"],proof[type]))throw new InvalidOperationException("Selected native function type changed or is unavailable; all input retained");
  }
 }

 // Re-resolve only already registered metadata. The saved proofs become read
 // checks under the existing final file lease, never additional write targets.
 internal static JsonObject Guards(JsonObject request,Func<Manifest,string> format)
 {
  var units=request["units"]!.AsObject();string ns=request["namespace"]!.ToString(),project=request["project"]!.ToString();var allReads=new SortedDictionary<string,JsonNode>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);var allProofs=new JsonObject();
  JsonObject Types(JsonNode? declaration){var types=new JsonObject();foreach(var change in declaration?["changes"] as JsonArray??new())if((change?["type"]?.ToString() is "function-add" or "function-edit")&&change["nativeTypes"] is JsonObject proof)foreach(var pair in proof){if(types[pair.Key]is not null&&!JsonNode.DeepEquals(types[pair.Key],pair.Value))throw new InvalidOperationException("Native type selections differ; retain input");types[pair.Key]=pair.Value!.DeepClone();}return types;}
  void Check(string owner,JsonObject types,JsonArray? saved=null){
   if(types.Count==0)return;if(types.Count>64||units[owner]?["kind"]?.ToString()!="schema")throw new ArgumentException("Owned bounded native type receipt required");
   var overlays=new JsonArray();foreach(var row in units)if(row.Key!=owner&&row.Key.StartsWith(ns+"::",StringComparison.Ordinal)&&row.Value?["draft"] is JsonValue&&row.Value?["kind"]?.ToString() is "object" or "schema" or "function" or "implementation" or "module" or "category" or "concept" or "enum")overlays.Add(new JsonObject{["id"]=row.Key,["text"]=row.Value!["draft"]!.DeepClone()});
   string Read(string path){if(!File.Exists(path)||new FileInfo(path).Length>1048576)throw new IOException("Native type read budget");return File.ReadAllText(path);}
   var scopes=types.Where(p=>p.Key.StartsWith(FunctionNativeEdits.Prefix,StringComparison.Ordinal)).Select(p=>p.Key[FunctionNativeEdits.Prefix.Length..]).ToArray();if(scopes.Length>1)throw new InvalidOperationException("Confirm the current native function type transition before selecting another; input retained");
   var current=EffectiveMetadata.Query(project,units[ns+"::ProjectManifest"]!["draft"]!.ToString(),owner,units[owner]!["draft"]!.ToString(),format,Read,overlays,observeSources:true,nativeTypes:true,nativeFunction:scopes.SingleOrDefault());
   if(current["status"]?.ToString()!="available")throw new InvalidOperationException("Native type receipt metadata unavailable; retain input");var reads=new SortedDictionary<string,JsonNode>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);
   foreach(var pair in types){var choice=pair.Key.StartsWith(FunctionNativeEdits.Prefix,StringComparison.Ordinal)?current["nativeFunctionEdit"]:current["nativeTypes"]!.AsArray().SingleOrDefault(c=>c?["clrType"]?.ToString()==pair.Key);var proof=pair.Value as JsonObject;
    if(choice?["available"]?.GetValue<bool>()!=true||proof?.Count!=2||proof["shapeHash"]?.ToString()!=choice["shapeHash"]?.ToString()||proof["sources"]is not JsonObject sources||sources.Count!=choice["sources"]!.AsObject().Count)throw new InvalidOperationException("Saved native type shape or proof changed; retain the candidate");
    foreach(var source in sources){var now=choice["sources"]![source.Key];if(now is null||source.Value?["path"]?.ToString()!=now["path"]?.ToString()||source.Value?["source"]?.ToString()!=now["source"]?.ToString())throw new InvalidOperationException("Saved native type source changed; retain the candidate");string path=now["path"]!.ToString();var read=new JsonObject{["path"]=path,["hash"]=now["source"]!.DeepClone()};if(reads.TryGetValue(path,out var prior)&&!JsonNode.DeepEquals(prior,read))throw new InvalidOperationException("Native type read versions differ");reads[path]=read;}
   }
   var list=new JsonArray(reads.Values.Select(v=>v.DeepClone()).ToArray());if(saved is not null&&!JsonNode.DeepEquals(saved,list))throw new InvalidOperationException("Complete saved native type read guards required");foreach(var row in reads){if(allReads.TryGetValue(row.Key,out var prior)&&!JsonNode.DeepEquals(prior,row.Value))throw new InvalidOperationException("Native type groups differ");allReads[row.Key]=row.Value.DeepClone();}if(allReads.Count>240)throw new ArgumentException("Native type read receipt budget");
  }
  if(request["action"]?.ToString()=="prepare"){
   string owner=request["declaration"]?["id"]?.ToString()??"";allProofs=Types(request["declaration"]);var prior=units[owner]?["atomicEditGroup"] is JsonArray?units[owner]?["slotSaveReceipt"]:null;
   if(prior?["nativeTypeProofs"]is JsonObject retained)foreach(var pair in retained){if(allProofs[pair.Key]is not null&&!JsonNode.DeepEquals(allProofs[pair.Key],pair.Value))throw new InvalidOperationException("Retain original native type proofs");allProofs[pair.Key]=pair.Value!.DeepClone();}
   Check(owner,allProofs);
  }else if(request["action"]?.ToString()=="validate"){
   var selected=request["selected"]!.AsArray();if(selected.Count>64)throw new ArgumentException("Native type review budget");
   foreach(var pair in units){var receipt=pair.Value?["slotSaveReceipt"];if(receipt is null||pair.Value?["atomicEditGroup"]is not JsonArray group||!selected.Any(id=>group.Any(member=>member!.ToString()==id!.ToString())))continue;var declared=Types(receipt["declaration"]);if(receipt["nativeTypeProofs"]is not JsonObject types){if(declared.Count>0)throw new InvalidOperationException("Saved native type proofs missing");continue;}foreach(var row in declared)if(!JsonNode.DeepEquals(row.Value,types[row.Key]))throw new InvalidOperationException("Retain selected native type proofs");Check(pair.Key,types,receipt["nativeTypeReads"]as JsonArray??throw new InvalidOperationException("Saved native type reads missing"));}
  }else throw new ArgumentException("Native type guard action");
  return new JsonObject{["proofs"]=allProofs,["reads"]=new JsonArray(allReads.Values.Select(v=>v.DeepClone()).ToArray())};
 }
}
