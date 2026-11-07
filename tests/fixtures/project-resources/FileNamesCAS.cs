using System.Text.Json.Nodes;
using System.Text;
using System.Security.Cryptography;
class Calls {
 public Func<string,string,string,string,string> Files=null!;
 public Func<string,int,string[]> Snapshot=Program.Snapshot;
 public Func<string,string,string[]> CommitPlan=null!;
 public Func<string,string> LeasePath=Program.Lease;
 public Action<string,string> WriteAtomic=Program.Write;
}
class Program {
 public static string Legacy(string manifest,string project,string operation,string payload,Calls calls){OLD_LAYOUT}
 public static string Layout(string manifest,string project,string operation,string payload,Calls calls){LAYOUT_BODY}
 public static string Resource(string manifest,string project,string operation,string payload,Calls calls){RESOURCE_BODY}
 public static string[] Snapshot(string path,int limit){SNAPSHOT_BODY}
 public static string[] Plan(string root,string plan,Calls calls){PLAN_BODY}
 public static void Write(string path,string text){WRITE_BODY}
 public static string Lease(string root){LEASE_BODY}
 static void Check(bool ok,string message){if(!ok)throw new Exception(message);}
 static string Hash(string value)=>Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(value))).ToLowerInvariant();
 static JsonObject Item(string name)=>new(){["id"]=Guid.NewGuid().ToString("N"),["name"]=name,["type"]="text/plain",["size"]=3,["hash"]=Hash("abc"),["modifiedAt"]=0,["data"]="YWJj"};
 static void Main(string[] args){
  foreach(string mode in new[]{"success","manifest-race","identity-race","store-race","layout-race","names-race","folder-names-race","write-failure"}){
   string root=Path.Combine(args[0],mode);Directory.CreateDirectory(Path.Combine(root,".confectory"));string manifest=Path.Combine(root,"project.cproj"),identityPath=Path.Combine(root,".confectory/project-identity.json"),store=Path.Combine(root,".confectory/resources.v1.json"),project=Guid.NewGuid().ToString("N");
   File.WriteAllText(manifest,"original manifest");var identity=new JsonObject{["version"]=1,["projectId"]=project,["manifest"]=manifest,["namespace"]="Owned"};File.WriteAllText(identityPath,identity.ToJsonString());string originalManifest=File.ReadAllText(manifest),originalIdentity=File.ReadAllText(identityPath);
   var calls=new Calls();calls.Files=(m,o,a,i)=>Resource(m,o,a,i,calls);calls.CommitPlan=(r,p)=>Plan(r,p,calls);
   var first=JsonNode.Parse(Resource(manifest,project,"import",new JsonObject{["revision"]="missing",["command"]=Guid.NewGuid().ToString("N"),["item"]=Item("already stored.txt")}.ToJsonString(),calls))!;
   string layout=Path.Combine(root,".confectory/resource-layout.v1.json"),folderNames=Path.Combine(root,".confectory/resource-folder-names.v1.json"),names=Path.Combine(root,".confectory/resource-file-names.v1.json"),id=first["selected"]!.ToString();JsonObject Input(string name)=>new(){["revision"]=JsonNode.Parse(Layout(manifest,project,"load","{}",calls))!["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["id"]=id,["name"]=name};
   var create=Input("folder");create["id"]=Guid.NewGuid().ToString("N");create["parent"]=null;Layout(manifest,project,"create-folder",create.ToJsonString(),calls);Layout(manifest,project,"rename-folder",new JsonObject{["revision"]=JsonNode.Parse(Layout(manifest,project,"load","{}",calls))!["revision"]!.DeepClone(),["command"]=Guid.NewGuid().ToString("N"),["id"]=create["id"]!.DeepClone(),["name"]="folder renamed"}.ToJsonString(),calls);Layout(manifest,project,"rename-file",Input("already renamed").ToJsonString(),calls);string before=File.ReadAllText(names),layoutBefore=File.ReadAllText(layout),storeBefore=File.ReadAllText(store),folderBefore=File.ReadAllText(folderNames),peer=before+" ";var input=Input("pending");string submitted=input.ToJsonString();int commits=0,writes=0;
   Check(JsonNode.Parse(Legacy(manifest,project,"load","{}",calls))!["items"]!.AsArray().Any(row=>row!["id"]!.ToString()==id&&row["name"]!.ToString()=="already stored.txt"),"previous exact v1 reader cannot read original topology");Check(File.ReadAllText(folderNames)==folderBefore,"legacy read rewrote folder names");Check(File.ReadAllText(layout)==layoutBefore,"legacy read rewrote original topology");
   calls.CommitPlan=(r,p)=>{
    commits++;var plan=JsonNode.Parse(p)!;Check(plan["writes"]!.AsArray().Count==1&&plan["writes"]![0]!["path"]!.ToString()==".confectory/resource-file-names.v1.json","source became an asset write");
    Check(plan["checks"]!.AsArray().Select(row=>row!["path"]!.ToString()).ToHashSet().SetEquals(new[]{"project.cproj",".confectory/project-identity.json",".confectory/resources.v1.json",".confectory/resource-layout.v1.json",".confectory/resource-folder-names.v1.json"}),"final owner/manifest check was omitted");
    if(mode=="manifest-race")File.WriteAllText(manifest,"peer manifest");if(mode=="identity-race"){identity["projectId"]=Guid.NewGuid().ToString("N");File.WriteAllText(identityPath,identity.ToJsonString());}if(mode=="store-race")File.WriteAllText(store,storeBefore+" ");if(mode=="layout-race")File.WriteAllText(layout,layoutBefore+" ");if(mode=="names-race")File.WriteAllText(names,peer);if(mode=="folder-names-race")File.WriteAllText(folderNames,folderBefore+" ");
    return Plan(r,p,calls);
   };
   calls.WriteAtomic=(p,t)=>{writes++;if(mode=="write-failure")throw new IOException("owned fixture exact write boundary");Write(p,t);};
   bool rejected=false;try{Layout(manifest,project,"rename-file",submitted,calls);}catch{rejected=true;}
   Check(commits==1,"case never reached actual final CommitPlan");Check(input.ToJsonString()==submitted,"pending caller input changed");
   if(mode=="success")Check(!rejected&&writes==1&&JsonNode.Parse(File.ReadAllText(names))!["items"]![0]!["name"]!.ToString()=="pending","successful atomic append failed");
   else{Check(rejected,"late change/failure was accepted");Check(File.ReadAllText(names)==(mode=="names-race"?peer:before),"partial append or peer data loss");Check(writes==(mode=="write-failure"?1:0),"writes occurred before final checks");}
   Check(File.ReadAllText(folderNames)==(mode=="folder-names-race"?folderBefore+" ":folderBefore),"folder names rewritten");Check(File.ReadAllText(layout)==(mode=="layout-race"?layoutBefore+" ":layoutBefore),"original topology rewritten");Check(File.ReadAllText(store)==(mode=="store-race"?storeBefore+" ":storeBefore),"file bytes were rewritten");Check(File.ReadAllText(manifest)==(mode=="manifest-race"?"peer manifest":originalManifest),"manifest was rewritten or peer lost");Check(File.ReadAllText(identityPath)==(mode=="identity-race"?identity.ToJsonString():originalIdentity),"identity was rewritten or peer lost");Console.WriteLine("PASS production resource/final CAS bodies "+mode);
   if(mode=="success"){
    var readInput=new JsonObject{["id"]=id,["hash"]=first["items"]![0]!["hash"]!.DeepClone()};int readWrites=0,readCommits=0;calls.CommitPlan=(r,p)=>{readCommits++;throw new Exception("read attempted CommitPlan");};calls.WriteAtomic=(p,t)=>{readWrites++;throw new Exception("read attempted write");};
    var observed=JsonNode.Parse(Layout(manifest,project,"read",readInput.ToJsonString(),calls))!;Check(observed["item"]!["name"]!.ToString()=="pending"&&observed["data"]!.ToString()=="YWJj","current display read lost original bytes");
    foreach(string dependency in new[]{manifest,identityPath,store,layout,folderNames,names}){
     string baseline=File.ReadAllText(dependency);calls.Files=(m,o,a,i)=>{string result=Resource(m,o,a,i,calls);if(a=="read")File.WriteAllText(dependency,baseline+" ");return result;};bool stale=false;try{Layout(manifest,project,"read",readInput.ToJsonString(),calls);}catch{stale=true;}Check(stale&&readWrites==0&&readCommits==0,"post-read dependency race leaked or wrote data");Check(File.ReadAllText(dependency)==baseline+" ","read repaired peer data");File.WriteAllText(dependency,baseline);Console.WriteLine("PASS read final dependency race "+Path.GetFileName(dependency));
    }
   }

  }
 }
}
