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
  byte[] sample=Convert.FromBase64String("AVIF_SAMPLE");sample.CopyTo(raw,0);int free=raw.Length-sample.Length;System.Buffers.Binary.BinaryPrimitives.WriteUInt32BigEndian(raw.AsSpan(sample.Length,4),(uint)free);Encoding.ASCII.GetBytes("free").CopyTo(raw,sample.Length+4);
  var imported=new JsonObject{["id"]=id,["name"]="large.avif",["type"]="image/avif",["size"]=raw.Length,["hash"]=Hash(raw),["modifiedAt"]=0,["data"]=Convert.ToBase64String(raw).Replace('+','-').Replace('/','_')};
  void Import()=>Resource(manifest,project,"import",new JsonObject{["revision"]=JsonNode.Parse(Resource(manifest,project,"load","{}",fileCalls))!["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["item"]=imported.DeepClone()}.ToJsonString(),fileCalls);
  Import();var header=Call("read",new(){["id"]=id,["hash"]=Hash(raw)});var request=new JsonObject{["id"]=id,["hash"]=Hash(raw),["generation"]=header["item"]!["contentGeneration"]!.DeepClone(),["revision"]=header["displayRevision"]!.DeepClone(),["part"]=0};
  Check(header["encoding"]!.ToString()=="unavailable"&&header["data"]is null&&header["imagePreview"]!["partBytes"]!.GetValue<int>()==1048576,"bounded descriptor");
  int writes=0;calls.CommitPlan=(r,p)=>{writes++;throw new Exception("read attempted write");};byte[] before=File.ReadAllBytes(store);var combined=new byte[raw.Length];
  for(int part=0;part<4;part++){
   request["part"]=part;var reply=Call("preview-image-part",request);byte[] expected=raw[(part*1048576)..((part+1)*1048576)];string partData=reply["data"]!.ToString();
   Check(reply.ToJsonString().Length<1500000&&partData==Convert.ToBase64String(expected).Replace('+','-').Replace('/','_')&&reply["preview"]!["sha256"]!.ToString()==Hash(expected)&&reply["preview"]!["total"]!.GetValue<int>()==raw.Length&&reply["preview"]!["offset"]!.GetValue<int>()==part*1048576&&reply["preview"]!["part"]!.GetValue<int>()==part&&reply["item"]!["hash"]!.ToString()==Hash(raw),"part/full-file integrity and RPC bound");
   Check(JsonNode.DeepEquals(reply["item"],header["item"]),"header/part item differs");Convert.FromBase64String(partData.Replace('-','+').Replace('_','/')).CopyTo(combined,part*1048576);
  }
  Check(Hash(combined)==Hash(raw),"whole image assembly");request["part"]=2;
  bool Refused(JsonObject input){try{Call("preview-image-part",input);return false;}catch{return true;}}
  foreach(string key in new[]{"id","hash","generation","revision"}){var wrong=(JsonObject)request.DeepClone();wrong[key]=key=="id"?new string('0',32):new string('0',64);Check(Refused(wrong),"accepted wrong "+key);}
  foreach(JsonNode value in new JsonNode[]{JsonValue.Create(-1)!,JsonValue.Create(4)!,JsonValue.Create(0.5)!,JsonValue.Create("0")!}){var wrong=(JsonObject)request.DeepClone();wrong["part"]=value.DeepClone();Check(Refused(wrong),"accepted invalid part "+value);}
  var extra=(JsonObject)request.DeepClone();extra["path"]="/outside";Check(Refused(extra),"accepted path");
  var legacy=JsonNode.Parse(Legacy(manifest,project,"read",new JsonObject{["id"]=id,["hash"]=Hash(raw)}.ToJsonString(),calls))!;var compatible=(JsonObject)header.DeepClone();compatible.Remove("imagePreview");Check(JsonNode.DeepEquals(legacy,compatible),"legacy read changed");
  bool oldRefused=false;try{Legacy(manifest,project,"preview-image-part",request.ToJsonString(),calls);}catch(InvalidOperationException e)when(e.Message=="resource_image_preview_budget"){oldRefused=true;}Check(oldRefused,"legacy unexpectedly supports AVIF parts");
  // Corrupt a byte outside the displayed prefix while keeping hash/receipt.
  var damaged=JsonNode.Parse(File.ReadAllText(store))!;string data=damaged["items"]![0]!["data"]!.ToString();int offset=data.Length-100;damaged["items"]![0]!["data"]=data[..offset]+(data[offset]=='A'?'B':'A')+data[(offset+1)..];File.WriteAllText(store,damaged.ToJsonString());Check(Refused(request),"tail corruption accepted");File.WriteAllBytes(store,before);
  Check(writes==0&&File.ReadAllBytes(store).SequenceEqual(before),"reader mutated owned copy");Console.WriteLine("PASS four bounded image parts/full SHA/legacy/tail corruption/stale/fields");
  calls.CommitPlan=(r,p)=>Plan(r,p,calls);var current=Call("load");Call("rename-file",new(){["revision"]=current["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["id"]=id,["name"]="renamed.avif"});Check(Refused(request),"old display revision accepted");header=Call("read",new(){["id"]=id,["hash"]=Hash(raw)});request["revision"]=header["displayRevision"]!.DeepClone();Check(Call("preview-image-part",request)["item"]!["name"]!.ToString()=="renamed.avif","fresh rename observation");
  current=Call("load");Call("delete-file",new(){["revision"]=current["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["id"]=id,["hash"]=Hash(raw)});Import();header=Call("read",new(){["id"]=id,["hash"]=Hash(raw)});request["revision"]=header["displayRevision"]!.DeepClone();Check(Refused(request),"old generation accepted after same ID/hash reimport");request["generation"]=header["item"]!["contentGeneration"]!.DeepClone();Call("preview-image-part",request);Console.WriteLine("PASS rename and same-ID/hash new import generation pinning");
  calls.CommitPlan=(r,p)=>{writes++;throw new Exception("read attempted write");};string content=".confectory/resource-content/"+id+".v1.json";
  foreach(string relative in new[]{"project.cproj",".confectory/project-identity.json",".confectory/resources.v1.json",".confectory/resource-layout.v1.json",".confectory/resource-file-names.v1.json",".confectory/resource-folder-names.v1.json",".confectory/resource-descriptions.v1.json",".confectory/resource-deletions.v1.json",content}){
   string path=Path.Combine(root,relative);Directory.CreateDirectory(Path.GetDirectoryName(path)!);byte[]? saved=File.Exists(path)?File.ReadAllBytes(path):null;int seen=0;bool injected=false;string pinned=request.ToJsonString();
   calls.Snapshot=(p,l)=>{if(p==manifest&&++seen==2){File.WriteAllBytes(path,(saved??Array.Empty<byte>()).Concat(Encoding.UTF8.GetBytes(" ")).ToArray());injected=true;}return Snapshot(p,l);};
   Check(Refused(request)&&injected&&writes==0&&request.ToJsonString()==pinned,"final observation dependency "+relative);calls.Snapshot=Snapshot;
   if(saved is null)File.Delete(path);else File.WriteAllBytes(path,saved);
   Console.WriteLine("PASS controlled final-read dependency refusal "+relative);
  }

  void Signature(string label,Action<byte[]> change,bool advertised){
   string folder=Path.Combine(root,"prefix-"+label);Directory.CreateDirectory(Path.Combine(folder,".confectory"));string ownManifest=Path.Combine(folder,"project.cproj"),ownProject=Guid.NewGuid().ToString("N"),ownId=Guid.NewGuid().ToString("N");File.WriteAllText(ownManifest,"generated source");File.WriteAllText(Path.Combine(folder,".confectory/project-identity.json"),new JsonObject{["version"]=1,["projectId"]=ownProject,["manifest"]=ownManifest}.ToJsonString());
   var ownFile=new Calls();ownFile.CommitPlan=(r,p)=>Plan(r,p,ownFile);var own=new Calls();own.Files=(m,o,a,i)=>Resource(m,o,a,i,ownFile);
   byte[] variant=raw.ToArray();Array.Clear(variant,sample.Length+8,variant.Length-sample.Length-8);change(variant);var item=new JsonObject{["id"]=ownId,["name"]="prefix.avif",["type"]="image/avif",["size"]=variant.Length,["hash"]=Hash(variant),["modifiedAt"]=0,["data"]=Convert.ToBase64String(variant).Replace('+','-').Replace('/','_')};
   Resource(ownManifest,ownProject,"import",new JsonObject{["revision"]=JsonNode.Parse(Resource(ownManifest,ownProject,"load","{}",ownFile))!["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["item"]=item}.ToJsonString(),ownFile);
   var header=JsonNode.Parse(Layout(ownManifest,ownProject,"read",new JsonObject{["id"]=ownId,["hash"]=Hash(variant)}.ToJsonString(),own))!;Check((header["imagePreview"]is not null)==advertised,"native ftyp signature "+label);
   var input=new JsonObject{["id"]=ownId,["hash"]=Hash(variant),["generation"]=header["item"]!["contentGeneration"]!.DeepClone(),["revision"]=header["displayRevision"]!.DeepClone(),["part"]=0};
   if(advertised){var part=JsonNode.Parse(Layout(ownManifest,ownProject,"preview-image-part",input.ToJsonString(),own))!;Check(part["preview"]!["bytes"]!.GetValue<int>()==1048576,"native compatible-brand part");}
   else {bool denied=false;try{Layout(ownManifest,ownProject,"preview-image-part",input.ToJsonString(),own);}catch(InvalidOperationException e)when(e.Message=="resource_image_preview_budget"){denied=true;}Check(denied,"native unsupported prefix lane "+label);}
   Console.WriteLine("PASS native bounded ftyp/brand "+label);
  }
  Signature("compatible-only",b=>Encoding.ASCII.GetBytes("mif1").CopyTo(b,8),true);
  Signature("no-avif",b=>{Encoding.ASCII.GetBytes("heic").CopyTo(b,8);Encoding.ASCII.GetBytes("heic").CopyTo(b,16);},false);
  foreach(uint length in new uint[]{0,1,12,17,80,4294967295})Signature("length-"+length,b=>System.Buffers.Binary.BinaryPrimitives.WriteUInt32BigEndian(b.AsSpan(0,4),length),false);
 }
}
