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
 public static string Layout(string manifest,string project,string operation,string payload,Calls calls){LAYOUT_BODY}
 public static string Resource(string manifest,string project,string operation,string payload,Calls calls){RESOURCE_BODY}
 public static string OldResource(string manifest,string project,string operation,string payload,Calls calls){OLD_RESOURCE_BODY}
 public static string OldLayout(string manifest,string project,string operation,string payload,Calls calls){OLD_LAYOUT_BODY}
 public static string[] Deletions(string manifest,string project,Calls calls){DELETIONS_BODY}
 public static string[] Snapshot(string path,int limit){SNAPSHOT_BODY}
 public static string[] Plan(string root,string plan,Calls calls){PLAN_BODY}
 public static void Write(string path,string text){WRITE_BODY}
 public static string Lease(string root){LEASE_BODY}
 static void Check(bool ok,string message){if(!ok)throw new Exception(message);}
 static string Hash(string value)=>Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(value))).ToLowerInvariant();
 static JsonObject Item(string name)=>new(){["id"]=Guid.NewGuid().ToString("N"),["name"]=name,["type"]="text/plain",["size"]=3,["hash"]=Hash("abc"),["modifiedAt"]=0,["data"]="YWJj"};
 static void Main(string[] args){
  foreach(bool existing in new[]{false,true})foreach(string mode in new[]{"success","manifest-race","identity-race","store-race","layout-race","folder-names-race","file-names-race","deletion-race","new-content-race","existing-content-race","write-first","write-second","after-second","tampered-plan"}){
   if(!existing&&mode=="existing-content-race")continue;
   string root=Path.Combine(args[0],(existing?"existing-":"first-")+mode);Directory.CreateDirectory(Path.Combine(root,".confectory"));string manifest=Path.Combine(root,"project.cproj"),identityPath=Path.Combine(root,".confectory/project-identity.json"),store=Path.Combine(root,".confectory/resources.v1.json"),layout=Path.Combine(root,".confectory/resource-layout.v1.json"),project=Guid.NewGuid().ToString("N");File.WriteAllText(manifest,"original manifest");File.WriteAllText(identityPath,new JsonObject{["version"]=1,["projectId"]=project,["manifest"]=manifest,["namespace"]="Owned"}.ToJsonString());var calls=new Calls();calls.Files=(m,p,a,i)=>Resource(m,p,a,i,calls);calls.CommitPlan=(r,p)=>Plan(r,p,calls);
   var oldItem=Item("existing.txt");if(existing)Resource(manifest,project,"import",new JsonObject{["revision"]="missing",["command"]=Guid.NewGuid().ToString("N"),["item"]=oldItem.DeepClone()}.ToJsonString(),calls);
   string folder=Guid.NewGuid().ToString("N");Layout(manifest,project,"create-folder",new JsonObject{["revision"]=JsonNode.Parse(Layout(manifest,project,"load","{}",calls))!["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["id"]=folder,["name"]="target",["parent"]=null}.ToJsonString(),calls);
   var loaded=JsonNode.Parse(Layout(manifest,project,"load","{}",calls))!;var entry1=new JsonObject{["command"]=Guid.NewGuid().ToString("N"),["item"]=Item("new one.txt")};var entry2=new JsonObject{["command"]=Guid.NewGuid().ToString("N"),["item"]=Item("new two.txt")};var input=new JsonObject{["revision"]=loaded["revision"]!.DeepClone(),["resourceRevision"]=loaded["resourceRevision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["parent"]=folder,["imports"]=new JsonArray(entry1,entry2)};string submitted=input.ToJsonString();
   var originals=new Dictionary<string,byte[]?>(StringComparer.Ordinal);foreach(string path in new[]{manifest,identityPath,store,layout})originals[path]=File.Exists(path)?File.ReadAllBytes(path):null;
   int commits=0,writes=0;string? peerPath=null;
   calls.CommitPlan=(r,p)=>{commits++;var plan=JsonNode.Parse(p)!;Check(plan["writes"]!.AsArray().Select(x=>x!["path"]!.ToString()).SequenceEqual(new[]{".confectory/resources.v1.json",".confectory/resource-layout.v1.json"}),"not exactly one atomic resource and placement group");
    var checks=plan["checks"]!.AsArray().Select(x=>x!["path"]!.ToString()).ToHashSet();Check(checks.IsSupersetOf(new[]{"project.cproj",".confectory/project-identity.json",".confectory/resource-deletions.v1.json",".confectory/resource-folder-names.v1.json",".confectory/resource-file-names.v1.json",".confectory/resource-content/"+entry1["item"]!["id"]+".v1.json",".confectory/resource-content/"+entry2["item"]!["id"]+".v1.json"}),"missing observation boundary");
    peerPath=mode switch{"manifest-race"=>manifest,"identity-race"=>identityPath,"store-race"=>store,"layout-race"=>layout,"folder-names-race"=>Path.Combine(root,".confectory/resource-folder-names.v1.json"),"file-names-race"=>Path.Combine(root,".confectory/resource-file-names.v1.json"),"deletion-race"=>Path.Combine(root,".confectory/resource-deletions.v1.json"),"new-content-race"=>Path.Combine(root,".confectory/resource-content/"+entry1["item"]!["id"]+".v1.json"),"existing-content-race"=>Path.Combine(root,".confectory/resource-content/"+oldItem["id"]+".v1.json"),_=>null};if(peerPath is not null){Directory.CreateDirectory(Path.GetDirectoryName(peerPath)!);File.WriteAllText(peerPath,"peer-owned change");}return Plan(r,p,calls);};
   calls.WriteAtomic=(p,t)=>{writes++;if(mode=="write-first"&&writes==1||mode=="write-second"&&writes==2)throw new IOException("owned injected write failure");Write(p,t);if(mode=="after-second"&&writes==2)throw new IOException("owned post-second-write failure");};
   if(mode=="tampered-plan")calls.Files=(m,p,a,i)=>{var text=Resource(m,p,a,i,calls);if(a=="prepare-import-many"){var broken=JsonNode.Parse(text)!;broken["plan"]!["writes"]![0]!["path"]="../not-authorized";return broken.ToJsonString();}return text;};
   // Preparation must not reach CommitPlan, including for a missing first store.
   var preparation=Resource(manifest,project,"prepare-import-many",new JsonObject{["revision"]=loaded["resourceRevision"]!.DeepClone(),["imports"]=input["imports"]!.DeepClone()}.ToJsonString(),calls);Check(commits==0&&writes==0&&JsonNode.Parse(preparation)!["plan"]is not null,"preparation wrote state");foreach(var pair in originals)Check(pair.Value is null?!File.Exists(pair.Key):File.ReadAllBytes(pair.Key).SequenceEqual(pair.Value),"preparation changed original");
   bool rejected=false;try{Layout(manifest,project,"import-files",submitted,calls);}catch{rejected=true;}Check(input.ToJsonString()==submitted,"caller input mutated");
   if(mode=="success"){Check(!rejected&&commits==1&&writes==2,"successful group not atomic");var value=JsonNode.Parse(Layout(manifest,project,"load","{}",calls))!;foreach(var entry in input["imports"]!.AsArray())Check(value["items"]!.AsArray().Single(x=>x!["id"]!.ToString()==entry!["item"]!["id"]!.ToString())!["parent"]!.ToString()==folder,"wrong initial parent");var replay=JsonNode.Parse(Layout(manifest,project,"import-files",submitted,calls))!;Check(replay["replayed"]!.GetValue<bool>()&&commits==1&&writes==2,"exact retry rewrote placement or bytes");
    Check(JsonNode.Parse(OldResource(manifest,project,"load","{}",calls))!["items"]!.AsArray().Count==(existing?3:2),"old v1 resource reader rejected grouped bytes");calls.Files=(m,p,a,i)=>OldResource(m,p,a,i,calls);var oldView=JsonNode.Parse(OldLayout(manifest,project,"load","{}",calls))!;Check(oldView["items"]!.AsArray().Single(x=>x!["id"]!.ToString()==entry1["item"]!["id"]!.ToString())!["parent"]!.ToString()==folder,"old v1 layout reader rejected placement");calls.CommitPlan=(r,p)=>Plan(r,p,calls);OldLayout(manifest,project,"move",new JsonObject{["revision"]=oldView["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["ids"]=new JsonArray(entry1["item"]!["id"]!.DeepClone()),["parent"]=null}.ToJsonString(),calls);calls.Files=(m,p,a,i)=>Resource(m,p,a,i,calls);int beforeReplay=writes;var later=JsonNode.Parse(Layout(manifest,project,"import-files",submitted,calls))!;Check(later["replayed"]!.GetValue<bool>()&&writes==beforeReplay&&later["items"]!.AsArray().Single(x=>x!["id"]!.ToString()==entry1["item"]!["id"]!.ToString())!["parent"]is null,"replay reset a later explicit old-writer move");}
   else{Check(rejected&&commits==(mode=="tampered-plan"?0:1),"failure accepted or boundary bypassed");Check(writes==(mode=="write-first"?1:mode is "write-second" or "after-second"?2:0),"unexpected partial write count");foreach(var pair in originals)Check(pair.Key==peerPath?File.ReadAllText(pair.Key)=="peer-owned change":pair.Value is null?!File.Exists(pair.Key):File.ReadAllBytes(pair.Key).SequenceEqual(pair.Value),"rollback lost original or peer");if(peerPath is not null)Check(File.ReadAllText(peerPath)=="peer-owned change","peer data overwritten");}
   Console.WriteLine("PASS destination atomic CAS "+(existing?"existing ":"first ")+mode);
  }
 }
}
