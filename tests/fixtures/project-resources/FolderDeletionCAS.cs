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
 static string Hash(string value)=>Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(value))).ToLowerInvariant();
 static JsonObject Item(string name)=>new(){["id"]=Guid.NewGuid().ToString("N"),["name"]=name,["type"]="text/plain",["size"]=3,["hash"]=Hash("abc"),["modifiedAt"]=0,["data"]="YWJj"};
 static void Main(string[] args){
  foreach(string mode in new[]{"success","manifest-race","identity-race","store-race","layout-race","names-race","folder-names-race","deletions-race","descriptions-race","fail-1","fail-2","fail-3","fail-4","fail-5"}){
   string root=Path.Combine(args[0],mode);Directory.CreateDirectory(Path.Combine(root,".confectory"));string manifest=Path.Combine(root,"project.cproj"),project=Guid.NewGuid().ToString("N");File.WriteAllText(manifest,"source");File.WriteAllText(Path.Combine(root,".confectory/project-identity.json"),new JsonObject{["version"]=1,["projectId"]=project,["manifest"]=manifest}.ToJsonString());
   var calls=new Calls();calls.Files=(m,o,a,i)=>Resource(m,o,a,i,calls);calls.CommitPlan=(r,p)=>Plan(r,p,calls);
   JsonObject Call(string op,JsonObject? data=null)=>JsonNode.Parse(Layout(manifest,project,op,(data??new()).ToJsonString(),calls))!.AsObject();
   JsonObject Input(string id)=>new(){["revision"]=Call("load")["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["id"]=id,["hash"]=System.Linq.Enumerable.Single(Call("load")["items"]!.AsArray(),row=>row!["id"]!.ToString()==id)!["hash"]!.DeepClone()};
   string Import(){var item=Item("copy.txt");Resource(manifest,project,"import",new JsonObject{["revision"]=JsonNode.Parse(Resource(manifest,project,"load","{}",calls))!["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["item"]=item}.ToJsonString(),calls);return item["id"]!.ToString();}
   string discarded=Import();Call("delete-file",Input(discarded));string id=Import(),peer=Import(),folder=Guid.NewGuid().ToString("N"),nested=Guid.NewGuid().ToString("N");Call("create-folder",new(){["revision"]=Call("load")["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["id"]=folder,["name"]="folder",["parent"]=null});Call("create-folder",new(){["revision"]=Call("load")["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["id"]=nested,["name"]="nested",["parent"]=folder});Call("rename-folder",new(){["revision"]=Call("load")["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["id"]=folder,["name"]="display folder"});Call("move",new(){["revision"]=Call("load")["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["ids"]=new JsonArray(id),["parent"]=nested});Call("rename-file",new(){["revision"]=Call("load")["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["id"]=id,["name"]="display name"});
   File.WriteAllText(Path.Combine(root,".confectory/resource-descriptions.v1.json"),new JsonObject{["version"]=1,["project"]=project,["manifest"]=manifest,["items"]=new JsonArray()}.ToJsonString());
   string[] paths={"project.cproj",".confectory/project-identity.json",".confectory/resources.v1.json",".confectory/resource-layout.v1.json",".confectory/resource-file-names.v1.json",".confectory/resource-folder-names.v1.json",".confectory/resource-deletions.v1.json",".confectory/resource-descriptions.v1.json"};var before=paths.ToDictionary(p=>p,p=>File.ReadAllBytes(Path.Combine(root,p)));var request=Input(folder);string submitted=request.ToJsonString();int commits=0,writes=0;string? raced=mode switch{"manifest-race"=>paths[0],"identity-race"=>paths[1],"store-race"=>paths[2],"layout-race"=>paths[3],"names-race"=>paths[4],"folder-names-race"=>paths[5],"deletions-race"=>paths[6],"descriptions-race"=>paths[7],_=>null};
   calls.CommitPlan=(r,p)=>{commits++;var plan=JsonNode.Parse(p)!;Check(plan["writes"]!.AsArray().Count==5,"delete must atomically write copy/receipt/placement/file-name/folder-name");Check(plan["writes"]!.AsArray().Concat(plan["checks"]!.AsArray()).Where(x=>!x!["path"]!.ToString().StartsWith(".confectory/resource-content/",StringComparison.Ordinal)).Select(x=>x!["path"]!.ToString()).ToHashSet().SetEquals(paths),"all final dependencies required");if(raced is not null)File.AppendAllText(Path.Combine(root,raced)," ");return Plan(r,p,calls);};
   calls.WriteAtomic=(p,t)=>{writes++;Write(p,t);if(mode=="fail-"+writes)throw new IOException("injected after write "+writes);};bool failed=false;try{Call("delete-folder",request);}catch{failed=true;}
   Check(commits==1&&submitted==request.ToJsonString(),"exact caller intent or commit boundary lost");
   if(mode=="success"){Check(!failed&&writes==5&&Call("load")["items"]!.AsArray().Count==1,"successful copy deletion failed");calls.CommitPlan=(r,p)=>throw new Exception("replay wrote");Check(Call("delete-folder",request)["replayed"]!.GetValue<bool>(),"exact receipt replay failed");}
   else{Check(failed,"race/failed partial write accepted");foreach(var pair in before){var expected=raced==pair.Key?pair.Value.Concat(Encoding.UTF8.GetBytes(" ")).ToArray():pair.Value;Check(File.ReadAllBytes(Path.Combine(root,pair.Key)).SequenceEqual(expected),"partial write or peer loss: "+pair.Key);}Check(writes==(mode.StartsWith("fail-")?int.Parse(mode[5..]):0),"unexpected write before final CAS");}
   Console.WriteLine("PASS delete five-file atomic commit/rollback "+mode);
  }
 }
}
