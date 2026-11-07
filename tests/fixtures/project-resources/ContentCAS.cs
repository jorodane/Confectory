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
  foreach(string mode in new[]{"success","manifest-race","identity-race","store-race","layout-race","names-race","folder-names-race","deletions-race","content-race","fail-1"}){
   string root=Path.Combine(args[0],mode);Directory.CreateDirectory(Path.Combine(root,".confectory"));string manifest=Path.Combine(root,"project.cproj"),project=Guid.NewGuid().ToString("N");File.WriteAllText(manifest,"source");File.WriteAllText(Path.Combine(root,".confectory/project-identity.json"),new JsonObject{["version"]=1,["projectId"]=project,["manifest"]=manifest}.ToJsonString());var calls=new Calls();calls.Files=(m,o,a,i)=>Resource(m,o,a,i,calls);calls.CommitPlan=(r,p)=>Plan(r,p,calls);
   JsonObject Call(string op,JsonObject? data=null)=>JsonNode.Parse(Layout(manifest,project,op,(data??new()).ToJsonString(),calls))!.AsObject();
   var imported=Item("original.txt");string id=imported["id"]!.ToString(),contentPath=".confectory/resource-content/"+id+".v1.json";Resource(manifest,project,"import",new JsonObject{["revision"]="missing",["command"]=Guid.NewGuid().ToString("N"),["item"]=imported.DeepClone()}.ToJsonString(),calls);var originalStore=File.ReadAllBytes(Path.Combine(root,".confectory/resources.v1.json"));
   JsonObject Input(string action,string text="next") {var current=Call("load");var input=new JsonObject{["revision"]=current["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["id"]=id,["hash"]=current["items"]![0]!["hash"]!.DeepClone()};if(action=="save-content"){input["type"]="text/plain";input["size"]=Encoding.UTF8.GetByteCount(text);input["data"]=Convert.ToBase64String(Encoding.UTF8.GetBytes(text)).Replace('+','-').Replace('/','_');}return input;}
   JsonObject Read(){var item=Call("load")["items"]![0]!;return Call("read",new(){["id"]=id,["hash"]=item["hash"]!.DeepClone()});}
   var first=Input("save-content");var firstResult=Call("save-content",first);Check(Read()["data"]!.ToString()=="bmV4dA=="&&firstResult["items"]![0]!["hasContentBackup"]!.GetValue<bool>(),"first edit/read metadata");Check(Call("save-content",first)["replayed"]!.GetValue<bool>(),"exact save replay");Check(File.ReadAllBytes(Path.Combine(root,".confectory/resources.v1.json")).SequenceEqual(originalStore),"immutable import changed");
   var restoration=Input("restore-content");Call("restore-content",restoration);Check(Read()["data"]!.ToString()=="YWJj"&&Call("load")["items"]![0]!["contentRestoreToggled"]!.GetValue<bool>(),"restore original");Check(Call("restore-content",restoration)["replayed"]!.GetValue<bool>(),"restore lost response replay");Call("restore-content",Input("restore-content"));Check(Read()["data"]!.ToString()=="bmV4dA==","toggle restore");
   bool Refused(string op,JsonObject data){try{Call(op,data);return false;}catch{return true;}}
   Check(Refused("save-content",first),"superseded save reapplied");var wrong=Input("save-content");wrong["type"]="image/png";Check(Refused("save-content",wrong),"changed MIME accepted");wrong=Input("save-content");wrong["data"]="bad";Check(Refused("save-content",wrong),"invalid encoded content accepted");
   var request=Input("save-content","final");string[] paths={"project.cproj",".confectory/project-identity.json",".confectory/resources.v1.json",".confectory/resource-layout.v1.json",".confectory/resource-file-names.v1.json",".confectory/resource-folder-names.v1.json",".confectory/resource-deletions.v1.json",contentPath};var before=paths.ToDictionary(p=>p,p=>File.Exists(Path.Combine(root,p))?File.ReadAllBytes(Path.Combine(root,p)):null);int commits=0,writes=0;string? raced=mode switch{"manifest-race"=>paths[0],"identity-race"=>paths[1],"store-race"=>paths[2],"layout-race"=>paths[3],"names-race"=>paths[4],"folder-names-race"=>paths[5],"deletions-race"=>paths[6],"content-race"=>paths[7],_=>null};
   calls.CommitPlan=(r,p)=>{commits++;var plan=JsonNode.Parse(p)!;Check(plan["writes"]!.AsArray().Count==1&&plan["writes"]![0]!["path"]!.ToString()==contentPath,"edit writes outside content copy");Check(plan["writes"]!.AsArray().Concat(plan["checks"]!.AsArray()).Select(x=>x!["path"]!.ToString()).ToHashSet().SetEquals(paths),"missing final content dependency");if(raced is not null)File.AppendAllText(Path.Combine(root,raced)," ");return Plan(r,p,calls);};calls.WriteAtomic=(p,t)=>{writes++;Write(p,t);if(mode=="fail-1")throw new IOException("injected after write");};bool failed=Refused("save-content",request);Check(commits==1,"commit count");
   if(mode=="success"){Check(!failed&&writes==1&&Read()["data"]!.ToString()=="ZmluYWw=","final edit execution");calls.CommitPlan=(r,p)=>Plan(r,p,calls);calls.WriteAtomic=Write;
    var delete=new JsonObject{["revision"]=Call("load")["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["id"]=id,["hash"]=Call("load")["items"]![0]!["hash"]!.DeepClone()};var deleteBefore=paths.ToDictionary(p=>p,p=>File.Exists(Path.Combine(root,p))?File.ReadAllBytes(Path.Combine(root,p)):null);calls.WriteAtomic=(p,t)=>{Write(p,t);if(p==Path.Combine(root,contentPath))throw new IOException("injected content tombstone failure");};Check(Refused("delete-file",delete),"partial content deletion accepted");foreach(var pair in deleteBefore)Check(pair.Value is null?!File.Exists(Path.Combine(root,pair.Key)):File.ReadAllBytes(Path.Combine(root,pair.Key)).SequenceEqual(pair.Value),"content/current-backup deletion rollback failed");calls.WriteAtomic=Write;Call("delete-file",delete);var tombstone=JsonNode.Parse(File.ReadAllText(Path.Combine(root,contentPath)))!;Check(tombstone["deleted"]!.GetValue<bool>()&&tombstone["current"]is null&&Call("load")["items"]!.AsArray().Count==0,"delete leaked current or backup");Resource(manifest,project,"import",new JsonObject{["revision"]=JsonNode.Parse(Resource(manifest,project,"load","{}",calls))!["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["item"]=imported.DeepClone()}.ToJsonString(),calls);Check(Read()["data"]!.ToString()=="YWJj","fresh generation inherited retired edit");Call("save-content",Input("save-content","fresh"));Check(Read()["data"]!.ToString()=="ZnJlc2g=","fresh generation cannot replace tombstone");
   }else{Check(failed,"race or partial write accepted");foreach(var pair in before){string full=Path.Combine(root,pair.Key);byte[]? expected=raced==pair.Key?(pair.Value??Array.Empty<byte>()).Concat(Encoding.UTF8.GetBytes(" ")).ToArray():pair.Value;Check(expected is null?!File.Exists(full):File.ReadAllBytes(full).SequenceEqual(expected),"partial save or peer loss "+pair.Key);}Check(writes==(mode=="fail-1"?1:0),"writes before final CAS");}
   Console.WriteLine("PASS text content save/restore/receipt/final CAS "+mode);
  }
 }
}
