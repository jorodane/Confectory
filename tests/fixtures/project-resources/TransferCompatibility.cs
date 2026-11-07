using System.Text.Json.Nodes;
using System.Text;
using System.Security.Cryptography;
class Calls {
 public Func<string,string,string[]> Deletions=(m,p)=>Program.Deletions(m,p,new Calls());
 public Func<string,int,string[]> Snapshot=Program.Snapshot;
 public Func<string,string,string[]> CommitPlan=null!;
 public Func<string,string> LeasePath=Program.Lease;
 public Action<string,string> WriteAtomic=Program.Write;
}
class Program {
 public static string Resource(string manifest,string project,string operation,string payload,Calls calls){RESOURCE_BODY}
 public static string[] Deletions(string manifest,string project,Calls calls){DELETIONS_BODY}
 public static string[] Snapshot(string path,int limit){SNAPSHOT_BODY}
 public static string[] Plan(string root,string plan,Calls calls){PLAN_BODY}
 public static void Write(string path,string text){WRITE_BODY}
 public static string Lease(string root){LEASE_BODY}
 static void Check(bool ok,string message){if(!ok)throw new Exception(message);}
 static string Hash(string value)=>Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(value))).ToLowerInvariant();
 static JsonObject Item(string name)=>new(){["id"]=Guid.NewGuid().ToString("N"),["name"]=name,["type"]="text/plain",["size"]=3,["hash"]=Hash("abc"),["modifiedAt"]=0,["data"]="YWJj"};
 public static string OldResource(string manifest,string project,string operation,string payload,Calls calls){OLD_RESOURCE_BODY}
 static void Main(string[] args){
  string root=args[0];Directory.CreateDirectory(Path.Combine(root,".confectory"));string manifest=Path.Combine(root,"project.cproj"),project=Guid.NewGuid().ToString("N"),store=Path.Combine(root,".confectory/resources.v1.json");File.WriteAllText(manifest,"original owned manifest");File.WriteAllText(Path.Combine(root,".confectory/project-identity.json"),new JsonObject{["version"]=1,["manifest"]=manifest,["projectId"]=project,["namespace"]="Owned"}.ToJsonString());
  var calls=new Calls();calls.CommitPlan=(r,p)=>Plan(r,p,calls);var entries=new JsonArray();
  for(int i=0;i<4;i++){var bytes=new byte[1048576];Array.Fill(bytes,(byte)(151+i));entries.Add(new JsonObject{["command"]=Guid.NewGuid().ToString("N"),["item"]=new JsonObject{["id"]=Guid.NewGuid().ToString("N"),["name"]="owned "+i+" 🧪.bin",["type"]="application/octet-stream",["size"]=bytes.Length,["hash"]=Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant(),["data"]=Convert.ToBase64String(bytes).Replace('+','-').Replace('/','_'),["modifiedAt"]=0}});}
  string payload=new JsonObject{["revision"]="missing",["imports"]=entries.DeepClone()}.ToJsonString();var result=JsonNode.Parse(Resource(manifest,project,"import-many",payload,calls))!;Check(result["items"]!.AsArray().Count==4,"maximum atomic group missing");string saved=File.ReadAllText(store);Check(JsonNode.Parse(saved)!["version"]!.GetValue<int>()==1,"stored grammar changed");var old=JsonNode.Parse(OldResource(manifest,project,"load","{}",calls))!;Check(old["items"]!.AsArray().Count==4&&old["limits"]!["importBytes"]!.GetValue<int>()==1048576,"old reader could not load full existing store");
  foreach(var entry in entries){var item=entry!["item"]!;var read=JsonNode.Parse(OldResource(manifest,project,"read",new JsonObject{["id"]=item["id"]!.DeepClone(),["hash"]=item["hash"]!.DeepClone()}.ToJsonString(),calls))!;Check(read["data"]!.ToString()==item["data"]!.ToString(),"old reader changed bytes");}
  Check(JsonNode.Parse(Resource(manifest,project,"import-many",payload,calls))!["replayed"]!.GetValue<bool>()&&File.ReadAllText(store)==saved,"new group replay changed source");Check(File.ReadAllText(manifest)=="original owned manifest","manifest rewritten");Console.WriteLine("PASS exact4MiB group; actual v1 rollback production reader returns all four exact files; current replay preserves IDs, receipts and manifest");
 }
}
