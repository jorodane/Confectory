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
 string root=args[0];Directory.CreateDirectory(Path.Combine(root,".confectory"));string manifest=Path.Combine(root,"project.cproj"),project=Guid.NewGuid().ToString("N"),file=Guid.NewGuid().ToString("N"),a=Guid.NewGuid().ToString("N"),b=Guid.NewGuid().ToString("N");File.WriteAllText(manifest,"source");File.WriteAllText(Path.Combine(root,".confectory/project-identity.json"),new JsonObject{["version"]=1,["projectId"]=project,["manifest"]=manifest}.ToJsonString());var calls=new Calls();var fileCalls=new Calls();fileCalls.CommitPlan=(r,p)=>Plan(r,p,fileCalls);calls.Files=(m,o,op,input)=>Resource(m,o,op,input,fileCalls);calls.CommitPlan=(r,p)=>Plan(r,p,calls);
 JsonObject Call(string op,JsonObject? data=null)=>JsonNode.Parse(Layout(manifest,project,op,(data??new()).ToJsonString(),calls))!.AsObject();
 var imported=new JsonObject{["id"]=file,["name"]="owned.txt",["type"]="text/plain",["size"]=3,["hash"]=Hash(Encoding.UTF8.GetBytes("abc")),["modifiedAt"]=0,["data"]="YWJj"};Resource(manifest,project,"import",new JsonObject{["revision"]="missing",["command"]=Guid.NewGuid().ToString("N"),["item"]=imported}.ToJsonString(),fileCalls);
 foreach(var entry in new[]{(a,(string?)null),(b,a)})Call("create-folder",new(){["revision"]=Call("load")["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["id"]=entry.Item1,["parent"]=entry.Item2,["name"]="category "+entry.Item1});
 Call("move",new(){["revision"]=Call("load")["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["ids"]=new JsonArray(file),["parent"]=b});
 var current=Call("load");Check(JsonNode.DeepEquals(current,JsonNode.Parse(Legacy(manifest,project,"load","{}",calls))),"ordinary metadata load changed");int writes=0;calls.CommitPlan=(r,p)=>{writes++;throw new Exception("navigation attempted a write");};
 bool Refused(JsonObject input){try{Call("locate",input);return false;}catch{return true;}}
 foreach(string target in new[]{file,b,a}){
 var item=current["items"]!.AsArray().Single(x=>x!["id"]!.ToString()==target)!;var input=new JsonObject{["id"]=target,["hash"]=item["hash"]!.DeepClone(),["revision"]=current["revision"]!.DeepClone()};var result=Call("locate",input);Check(JsonNode.DeepEquals(result["item"],item)&&JsonNode.DeepEquals(result["parent"]?["id"],item["parent"])&&result.ToJsonString().Length<16384&&result["format"]!.ToString()=="resource-location-v1","parent/root metadata");
 foreach(string key in new[]{"id","hash","revision"}){var wrong=input.DeepClone().AsObject();wrong[key]=new string('0',key=="id"?32:64);Check(Refused(wrong),"accepted stale or foreign "+key);}var extra=input.DeepClone().AsObject();extra["path"]="/outside";Check(Refused(extra),"accepted OS path");bool old=false;try{Legacy(manifest,project,"locate",input.ToJsonString(),calls);}catch{old=true;}Check(old,"old reader accepted new location operation");
 foreach(string relative in new[]{"project.cproj",".confectory/project-identity.json",".confectory/resources.v1.json",".confectory/resource-layout.v1.json",".confectory/resource-file-names.v1.json",".confectory/resource-folder-names.v1.json",".confectory/resource-descriptions.v1.json",".confectory/resource-deletions.v1.json",".confectory/resource-content/"+file+".v1.json"}){
 string path=Path.Combine(root,relative);Directory.CreateDirectory(Path.GetDirectoryName(path)!);byte[]? before=File.Exists(path)?File.ReadAllBytes(path):null;int seen=0;bool injected=false;calls.Snapshot=(p,l)=>{if(p==manifest&&++seen==2){File.WriteAllBytes(path,(before??Array.Empty<byte>()).Concat(Encoding.UTF8.GetBytes(" ")).ToArray());injected=true;}return Snapshot(p,l);};Check(Refused(input)&&injected&&writes==0,"final location read dependency "+relative);calls.Snapshot=Snapshot;if(before is null)File.Delete(path);else File.WriteAllBytes(path,before);Console.WriteLine("PASS controlled final location read "+target+" "+relative);
 }
 }
 Check(writes==0,"read changed project");bool foreign=false;try{Layout(manifest,Guid.NewGuid().ToString("N"),"locate",new JsonObject{["id"]=file,["hash"]=current["items"]![0]!["hash"]!.DeepClone(),["revision"]=current["revision"]!.DeepClone()}.ToJsonString(),calls);}catch{foreign=true;}Check(foreign,"foreign project accepted");Console.WriteLine("PASS actual production location bodies: folder/file/root/fields/old reader/current owner and no writes");
 }
}
