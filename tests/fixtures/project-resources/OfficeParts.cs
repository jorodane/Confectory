using System.Text.Json.Nodes;
using System.Text;
using System.Security.Cryptography;
class Calls {
 public Func<string,string,string,string,string> Files=null!;
 public Func<string,string,string[]> Deletions=(m,p)=>Program.Deletions(m,p,new Calls());
 public Func<string,int,string[]> Snapshot=Program.Snapshot;
 public Func<string,string,string[]> CommitPlan=null!;
 public Func<string,string> LeasePath=Program.Lease;
 public Action<string,string> WriteAtomic=Program.Write;
}
class Program {
 public static string Legacy(string manifest,string project,string operation,string payload,Calls calls){OLD_LAYOUT}
 public static string Layout(string manifest,string project,string operation,string payload,Calls calls){LAYOUT_BODY}
 public static string Resource(string manifest,string project,string operation,string payload,Calls calls){RESOURCE_BODY}
 public static string[] Deletions(string manifest,string project,Calls calls){DELETIONS_BODY}
 public static string[] Snapshot(string path,int limit){SNAPSHOT_BODY}
 public static string[] Plan(string root,string plan,Calls calls){PLAN_BODY}
 public static void Write(string path,string text){WRITE_BODY}
 public static string Lease(string root){LEASE_BODY}
 static void Check(bool ok,string message){if(!ok)throw new Exception(message);}
 static string Hash(byte[] bytes)=>Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
 static void Main(string[] args){
  string root=args[0];Directory.CreateDirectory(Path.Combine(root,".confectory"));string manifest=Path.Combine(root,"project.cproj"),project=Guid.NewGuid().ToString("N"),id=Guid.NewGuid().ToString("N"),store=Path.Combine(root,".confectory/resources.v1.json");
  File.WriteAllText(manifest,"source");File.WriteAllText(Path.Combine(root,".confectory/project-identity.json"),new JsonObject{["version"]=1,["projectId"]=project,["manifest"]=manifest}.ToJsonString());
  var calls=new Calls();var fileCalls=new Calls();fileCalls.CommitPlan=(r,p)=>Plan(r,p,fileCalls);calls.Files=(m,o,a,i)=>Resource(m,o,a,i,fileCalls);calls.CommitPlan=(r,p)=>Plan(r,p,calls);
  JsonObject Call(string op,JsonObject? data=null)=>JsonNode.Parse(Layout(manifest,project,op,(data??new()).ToJsonString(),calls))!.AsObject();
  byte[] raw=new byte[4194304];uint random=713;for(int n=0;n<raw.Length;n++){random^=random<<13;random^=random>>17;random^=random<<5;raw[n]=(byte)random;}
  new byte[]{80,75,3,4}.CopyTo(raw,0);
  var imported=new JsonObject{["id"]=id,["name"]="large.docx",["type"]="application/vnd.openxmlformats-officedocument.wordprocessingml.document",["size"]=raw.Length,["hash"]=Hash(raw),["modifiedAt"]=0,["data"]=Convert.ToBase64String(raw).Replace('+','-').Replace('/','_')};
  void Import()=>Resource(manifest,project,"import",new JsonObject{["revision"]=JsonNode.Parse(Resource(manifest,project,"load","{}",fileCalls))!["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["item"]=imported.DeepClone()}.ToJsonString(),fileCalls);
  Import();var header=Call("read",new(){["id"]=id,["hash"]=Hash(raw)});var request=new JsonObject{["id"]=id,["hash"]=Hash(raw),["generation"]=header["item"]!["contentGeneration"]!.DeepClone(),["revision"]=header["displayRevision"]!.DeepClone(),["part"]=0};
  bool wrongLane=false;try{Call("preview-image-part",request);}catch(InvalidOperationException){wrongLane=true;}Check(wrongLane,"Office not an image-part source");
  Check(header["officePreview"]!["extension"]!.ToString()=="docx","format descriptor");
  Check(header["encoding"]!.ToString()=="unavailable"&&header["data"]is null&&header["officePreview"]!["partBytes"]!.GetValue<int>()==1048576,"bounded descriptor");
  int writes=0;calls.CommitPlan=(r,p)=>{writes++;throw new Exception("read attempted write");};byte[] before=File.ReadAllBytes(store);var combined=new byte[raw.Length];
  for(int part=0;part<4;part++){
   request["part"]=part;var reply=Call("preview-office-part",request);byte[] expected=raw[(part*1048576)..((part+1)*1048576)];string partData=reply["data"]!.ToString();
   Check(reply.ToJsonString().Length<1500000&&partData==Convert.ToBase64String(expected).Replace('+','-').Replace('/','_')&&reply["preview"]!["sha256"]!.ToString()==Hash(expected)&&reply["preview"]!["total"]!.GetValue<int>()==raw.Length&&reply["preview"]!["offset"]!.GetValue<int>()==part*1048576&&reply["preview"]!["part"]!.GetValue<int>()==part&&reply["item"]!["hash"]!.ToString()==Hash(raw),"part/full-file integrity and RPC bound");
   Check(JsonNode.DeepEquals(reply["item"],header["item"]),"header/part item differs");Convert.FromBase64String(partData.Replace('-','+').Replace('_','/')).CopyTo(combined,part*1048576);
  }
  Check(Hash(combined)==Hash(raw),"whole Office assembly");request["part"]=2;
  bool Refused(JsonObject input){try{Call("preview-office-part",input);return false;}catch{return true;}}
  foreach(string key in new[]{"id","hash","generation","revision"}){var wrong=(JsonObject)request.DeepClone();wrong[key]=key=="id"?new string('0',32):new string('0',64);Check(Refused(wrong),"accepted wrong "+key);}
  foreach(JsonNode value in new JsonNode[]{JsonValue.Create(-1)!,JsonValue.Create(4)!,JsonValue.Create(0.5)!,JsonValue.Create("0")!}){var wrong=(JsonObject)request.DeepClone();wrong["part"]=value.DeepClone();Check(Refused(wrong),"accepted invalid part "+value);}
  var extra=(JsonObject)request.DeepClone();extra["path"]="/outside";Check(Refused(extra),"accepted path");
  var legacy=JsonNode.Parse(Legacy(manifest,project,"read",new JsonObject{["id"]=id,["hash"]=Hash(raw)}.ToJsonString(),calls))!;var compatible=(JsonObject)header.DeepClone();compatible.Remove("officePreview");Check(JsonNode.DeepEquals(legacy,compatible),"legacy read changed");
  bool oldRefused=false;try{Legacy(manifest,project,"preview-office-part",request.ToJsonString(),calls);}catch(ArgumentException){oldRefused=true;}Check(oldRefused,"legacy unexpectedly supports Office parts");
  // Corrupt a byte outside the displayed prefix while keeping hash/receipt.
  var damaged=JsonNode.Parse(File.ReadAllText(store))!;string data=damaged["items"]![0]!["data"]!.ToString();int offset=data.Length-100;damaged["items"]![0]!["data"]=data[..offset]+(data[offset]=='A'?'B':'A')+data[(offset+1)..];File.WriteAllText(store,damaged.ToJsonString());Check(Refused(request),"tail corruption accepted");File.WriteAllBytes(store,before);
  Check(writes==0&&File.ReadAllBytes(store).SequenceEqual(before),"reader mutated owned copy");Console.WriteLine("PASS four bounded Office parts/full SHA/legacy/tail corruption/stale/fields");
  calls.CommitPlan=(r,p)=>Plan(r,p,calls);var current=Call("load");Call("rename-file",new(){["revision"]=current["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["id"]=id,["name"]="renamed.docx"});Check(Refused(request),"old display revision accepted");header=Call("read",new(){["id"]=id,["hash"]=Hash(raw)});request["revision"]=header["displayRevision"]!.DeepClone();Check(Call("preview-office-part",request)["item"]!["name"]!.ToString()=="renamed.docx","fresh rename observation");
  current=Call("load");Call("delete-file",new(){["revision"]=current["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["id"]=id,["hash"]=Hash(raw)});Import();header=Call("read",new(){["id"]=id,["hash"]=Hash(raw)});request["revision"]=header["displayRevision"]!.DeepClone();Check(Refused(request),"old generation accepted after same ID/hash reimport");request["generation"]=header["item"]!["contentGeneration"]!.DeepClone();Call("preview-office-part",request);Console.WriteLine("PASS rename and same-ID/hash new import generation pinning");
  calls.CommitPlan=(r,p)=>{writes++;throw new Exception("read attempted write");};string content=".confectory/resource-content/"+id+".v1.json";
  foreach(string relative in new[]{"project.cproj",".confectory/project-identity.json",".confectory/resources.v1.json",".confectory/resource-layout.v1.json",".confectory/resource-file-names.v1.json",".confectory/resource-folder-names.v1.json",".confectory/resource-descriptions.v1.json",".confectory/resource-deletions.v1.json",content}){
   string path=Path.Combine(root,relative);Directory.CreateDirectory(Path.GetDirectoryName(path)!);byte[]? saved=File.Exists(path)?File.ReadAllBytes(path):null;int seen=0;bool injected=false;string pinned=request.ToJsonString();
   calls.Snapshot=(p,l)=>{if(p==manifest&&++seen==2){File.WriteAllBytes(path,(saved??Array.Empty<byte>()).Concat(Encoding.UTF8.GetBytes(" ")).ToArray());injected=true;}return Snapshot(p,l);};
   Check(Refused(request)&&injected&&writes==0&&request.ToJsonString()==pinned,"final observation dependency "+relative);calls.Snapshot=Snapshot;
   if(saved is null)File.Delete(path);else File.WriteAllBytes(path,saved);
   Console.WriteLine("PASS controlled final-read dependency refusal "+relative);
  }
 }
}
