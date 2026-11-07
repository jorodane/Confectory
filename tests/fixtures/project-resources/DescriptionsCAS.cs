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
 foreach(string mode in new[]{"success","manifest-race","identity-race","store-race","layout-race","names-race","description-race","write-failure"}){
  string root=Path.Combine(args[0],mode);Directory.CreateDirectory(Path.Combine(root,".confectory"));string manifest=Path.Combine(root,"project.cproj"),project=Guid.NewGuid().ToString("N");File.WriteAllText(manifest,"original manifest");string identityPath=Path.Combine(root,".confectory/project-identity.json");File.WriteAllText(identityPath,new JsonObject{["version"]=1,["projectId"]=project,["manifest"]=manifest,["namespace"]="Owned"}.ToJsonString());
  var calls=new Calls();calls.Files=(m,p,a,i)=>Resource(m,p,a,i,calls);calls.CommitPlan=(r,p)=>Plan(r,p,calls);
  var item=Item("notes.txt");string id=item["id"]!.ToString();Resource(manifest,project,"import",new JsonObject{["revision"]="missing",["command"]=Guid.NewGuid().ToString("N"),["item"]=item.DeepClone()}.ToJsonString(),calls);
  JsonNode Load()=>JsonNode.Parse(Layout(manifest,project,"load","{}",calls))!;
  Check(Load()["revision"]!.ToString()==JsonNode.Parse(Legacy(manifest,project,"load","{}",calls))!["revision"]!.ToString(),"missing metadata changed existing revision");
  JsonObject Input(string target,string value)=>new(){["revision"]=Load()["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["id"]=target,["generation"]=Load()["items"]!.AsArray().Single(row=>row!["id"]!.ToString()==target)!["descriptionGeneration"]!.DeepClone(),["value"]=value};
  var input=Input(id,"  설명\n\t<literal>😀  ");string submitted=input.ToJsonString(),store=Path.Combine(root,".confectory/resources.v1.json"),originalStore=File.ReadAllText(store),description=Path.Combine(root,".confectory/resource-descriptions.v1.json");int writes=0;
  calls.CommitPlan=(r,p)=>{var plan=JsonNode.Parse(p)!;var checks=plan["checks"]!.AsArray().Select(row=>row!["path"]!.ToString()).ToHashSet();Check(checks.IsSupersetOf(new[]{"project.cproj",".confectory/project-identity.json",".confectory/resources.v1.json",".confectory/resource-layout.v1.json",".confectory/resource-folder-names.v1.json",".confectory/resource-file-names.v1.json",".confectory/resource-deletions.v1.json"}),"missing final dependency");
   if(mode=="manifest-race")File.AppendAllText(manifest," ");if(mode=="identity-race")File.AppendAllText(identityPath," ");if(mode=="store-race")File.AppendAllText(store," ");if(mode=="layout-race")File.WriteAllText(Path.Combine(root,".confectory/resource-layout.v1.json"),"peer");if(mode=="names-race")File.WriteAllText(Path.Combine(root,".confectory/resource-folder-names.v1.json"),"peer");if(mode=="description-race")File.WriteAllText(description,"peer");return Plan(r,p,calls);};
  calls.WriteAtomic=(p,t)=>{writes++;if(mode=="write-failure")throw new IOException("owned fixture write failure");Write(p,t);};bool rejected=false;try{Layout(manifest,project,"describe",submitted,calls);}catch{rejected=true;}
  Check(input.ToJsonString()==submitted,"caller input mutated");if(mode!="success"){Check(rejected,"late dependency/failure accepted");Check(writes==(mode=="write-failure"?1:0),"wrote before final CAS");Check(mode=="description-race"?File.ReadAllText(description)=="peer":!File.Exists(description),"failed save lost peer or partially committed");Console.WriteLine("PASS description final CAS "+mode);continue;}
  calls.CommitPlan=(r,p)=>Plan(r,p,calls);calls.WriteAtomic=Write;Check(!rejected&&writes==1,"description save failed");var saved=Load();Check(saved["items"]![0]!["description"]!.ToString()==input["value"]!.ToString(),"description whitespace/unicode lost");Check(File.ReadAllText(store)==originalStore,"description rewrote file bytes");Check(JsonNode.Parse(Layout(manifest,project,"describe",submitted,calls))!["replayed"]!.GetValue<bool>(),"exact retry not replayed");
  void Reject(JsonObject value,string why){bool no=false;try{Layout(manifest,project,"describe",value.ToJsonString(),calls);}catch{no=true;}Check(no,why);}
  var reused=input.DeepClone().AsObject();reused["value"]="different";Reject(reused,"command reused");var stale=Input(id,"stale");stale["revision"]=input["revision"]!.DeepClone();Reject(stale,"stale revision accepted");var generation=Input(id,"wrong generation");generation["generation"]=new string('a',64);Reject(generation,"wrong generation accepted");Reject(Input(id,new string('한',1001)),"maxlength bypass");Reject(Input(id,"NUL\0"),"NUL accepted");
  var read=JsonNode.Parse(Layout(manifest,project,"read",new JsonObject{["id"]=id,["hash"]=item["hash"]!.DeepClone()}.ToJsonString(),calls))!;Check(read["item"]!["description"]!.ToString()==input["value"]!.ToString()&&read["data"]!.ToString()=="YWJj","immutable read lost metadata/bytes");
  string folder=Guid.NewGuid().ToString("N");Layout(manifest,project,"create-folder",new JsonObject{["revision"]=Load()["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["id"]=folder,["name"]="folder",["parent"]=null}.ToJsonString(),calls);Layout(manifest,project,"describe",Input(folder,"folder description").ToJsonString(),calls);Check(Load()["items"]!.AsArray().Single(row=>row!["id"]!.ToString()==folder)!["description"]!.ToString()=="folder description","folder description missing");
  var preserved=Directory.GetFiles(Path.Combine(root,".confectory")).ToDictionary(p=>p,File.ReadAllBytes);calls.WriteAtomic=(p,t)=>{Write(p,t);if(p==description)throw new IOException("owned deletion after-description-write failure");};
  var failedTargets=new JsonArray();foreach(var row in Load()["items"]!.AsArray())failedTargets.Add(new JsonObject{["id"]=row!["id"]!.DeepClone(),["hash"]=row["hash"]!.DeepClone()});bool deletionFailed=false;try{Layout(manifest,project,"delete-selected",new JsonObject{["revision"]=Load()["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["targets"]=failedTargets}.ToJsonString(),calls);}catch{deletionFailed=true;}Check(deletionFailed&&preserved.All(p=>File.ReadAllBytes(p.Key).SequenceEqual(p.Value)),"failed deletion did not restore metadata/bytes/topology/receipts together");calls.WriteAtomic=Write;
  var targets=new JsonArray();foreach(var row in Load()["items"]!.AsArray())targets.Add(new JsonObject{["id"]=row!["id"]!.DeepClone(),["hash"]=row["hash"]!.DeepClone()});Layout(manifest,project,"delete-selected",new JsonObject{["revision"]=Load()["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["targets"]=targets}.ToJsonString(),calls);Check(JsonNode.Parse(File.ReadAllText(description))!["items"]!.AsArray().Count==0,"delete retained descriptions/receipts");Check(!File.ReadAllText(description).Contains("literal"),"deleted content retained");
  Resource(manifest,project,"import",new JsonObject{["revision"]=Load()["resourceRevision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["item"]=item.DeepClone()}.ToJsonString(),calls);Check(Load()["items"]![0]!["description"]is null,"reused ID inherited description");Reject(input,"retired description replay accepted");
  var fresh=Input(id,"");Layout(manifest,project,"describe",fresh.ToJsonString(),calls);Check(Load()["items"]![0]!["description"]!.ToString()=="","explicit clear failed");string prior=File.ReadAllText(description);var tampered=JsonNode.Parse(prior)!;tampered["items"]![0]!["value"]="tampered";File.WriteAllText(description,tampered.ToJsonString());bool invalid=false;try{Load();}catch{invalid=true;}Check(invalid,"tampered receipt accepted");File.WriteAllText(description,prior);
  Console.WriteLine("PASS description file/folder save/read/replay/clear/generation/limits/legacy/deletion/tamper, original file bytes preserved");
 }
 }
}
