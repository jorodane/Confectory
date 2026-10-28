"""Execute production Review/Confirm/CommitPlan bodies; inject a late read race.
Compiler and editor dependencies are controlled here; renderer/compiler tests
cover those real paths separately. This is not native Windows verification.
"""
import hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
repo=Path(sys.argv[1]).resolve();case=Path(tempfile.mkdtemp(prefix='confectory-copy-read-guards-'))
(case/'probe.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Exe</OutputType><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>')
paths={'Review':'packs/edit-workspace/ValidateReviewSelection.csbody','Confirm':'packs/change-set/ConfirmReviewed.csbody','CommitPlan':'packs/file-stream/CommitPlan.csbody','Snapshot':'packs/file-stream/Snapshot.csbody'}
bodies={k:(repo/p).read_text() for k,p in paths.items()}
source=r'''using System.Text.Json.Nodes;
using System.Text;
using System.Security.Cryptography;
class Calls {
 public Func<string,string[],string[]> Changes=null!;
 public Func<string,string,string[]> CreationGroup=(h,id)=>new[]{id},CreationOwners=(h,id)=>Array.Empty<string>(),Read=(h,id)=>throw new Exception("Unexpected lazy source read");
 public Func<string,string,string> Metadata=(op,input)=>throw new Exception("Unexpected metadata dependency"),Prepare=(original,candidate)=>"fixture";
 public Func<string,string[]> Snapshot=null!,Identity=null!;
 public Action<string,string[]> ValidateSelection=null!,Accept=null!,Acknowledge=null!;
 public Action<string,string> CopySources=null!,WriteAtomic=null!;
 public Func<string,string,string> Validate=(project,target)=>"valid";
 public Func<string,string,string[]> Activity=(project,action)=>new[]{".confectory/activity.json","missing","fixture activity"},CommitPlan=null!;
 public Func<string,string[],string[],string[],string[]> Commit=(root,paths,hashes,texts)=>throw new Exception("Read guards must participate in CommitPlan");
 public Func<string,string> LeasePath=root=>Path.Combine(root,".confectory/source-transaction.lock");
}
class Program {
 static void Review(string handle,string[] selected,Calls calls){ REVIEW }
 static string[] Confirm(string handle,string[] selected,string target,string[] reviewed,Calls calls){ CONFIRM }
 static string[] Plan(string root,string plan,Calls calls){ COMMITPLAN }
 static string[] Snapshot(string path){ SNAPSHOT }
 static string Hash(string text)=>Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(text))).ToLowerInvariant();
 static void Check(bool ok,string why){if(!ok)throw new Exception(why);}
 static void Main(){
  foreach(string mode in new[]{"success","after-review-race","missing-proof","path-escape"}){
   string handle=Guid.NewGuid().ToString("N"),root=Path.Combine(Path.GetTempPath(),"copy-read-case-"+handle),owner="Owned::Owner";Directory.CreateDirectory(root);
   try{
    File.WriteAllText(Path.Combine(root,"Owner.celem"),"old owner");File.WriteAllText(Path.Combine(root,"Host.celem"),"original assignment");
    var guards=new JsonObject{["Host.celem"]=new JsonObject{["path"]="Host.celem",["hash"]=Hash("original assignment")}};
    if(mode=="path-escape")guards=new JsonObject{["../Host.celem"]=new JsonObject{["path"]="../Host.celem",["hash"]="missing"}};
    var receipt=new JsonObject{["declaration"]=new JsonObject{["changes"]=new JsonArray(new JsonObject{["mapping"]=new JsonObject{["copies"]=new JsonObject{["selected graph"]=new JsonObject()}}})},["readGuards"]=guards};if(mode=="missing-proof")receipt.Remove("readGuards");
    var state=new JsonObject{["namespace"]="Owned",["root"]=root,["project"]=Path.Combine(root,"project.cproj"),["units"]=new JsonObject{[owner]=new JsonObject{["id"]=owner,["kind"]="schema",["path"]="Owner.celem",["baseline"]=Hash("old owner"),["draft"]="explicit new owner",["original"]="old owner",["atomicEditGroup"]=new JsonArray(owner),["slotSaveReceipt"]=receipt}}};
    AppDomain.CurrentDomain.SetData("Confectory.EditWorkspace."+handle,state);var before=state.DeepClone();var changes=new[]{owner,"Owner.celem",Hash("old owner"),"explicit new owner"};int validated=0,accepted=0,commits=0;
    var calls=new Calls{Changes=(h,ids)=>changes,Identity=h=>new[]{Path.Combine(root,"project.cproj"),"actor","context",root},Snapshot=Snapshot,WriteAtomic=(path,text)=>{Directory.CreateDirectory(Path.GetDirectoryName(path)!);File.WriteAllText(path,text);},CopySources=(from,to)=>Directory.CreateDirectory(to)};
    calls.ValidateSelection=(h,ids)=>{Review(h,ids,calls);if(++validated==2&&mode=="after-review-race")File.WriteAllText(Path.Combine(root,"Host.celem"),"peer assignment");};
    calls.Accept=(h,ids)=>accepted++;calls.Acknowledge=(h,ids)=>{};
    calls.CommitPlan=(r,input)=>{commits++;var plan=JsonNode.Parse(input)!;Check(plan["checks"]!.AsArray().Single()!["path"]!.ToString()=="Host.celem","Read guard omitted from final CAS");Check(!plan["writes"]!.AsArray().Any(row=>row!["path"]!.ToString()=="Host.celem"),"Read-only dependency became a write");return Plan(r,input,calls);};
    var result=Confirm(handle,new[]{owner},"fixture",changes,calls);
    if(mode=="success")Check(result[0]=="confirmed"&&accepted==1&&commits==1&&File.ReadAllText(Path.Combine(root,"Owner.celem"))=="explicit new owner"&&File.ReadAllText(Path.Combine(root,"Host.celem"))=="original assignment","Successful CAS lost the explicit write or altered its read dependency");
    else {Check(result[0]==(mode=="after-review-race"?"conflict":"invalid")&&accepted==0,"Refusal failed");Check(File.ReadAllText(Path.Combine(root,"Owner.celem"))=="old owner"&&!File.Exists(Path.Combine(root,".confectory/activity.json")),"Partial source/activity write");Check(JsonNode.DeepEquals(state,before),"Input/workspace changed on refusal");if(mode=="after-review-race")Check(commits==1&&result.Contains("Host.celem")&&File.ReadAllText(Path.Combine(root,"Host.celem"))=="peer assignment","Final CAS lost the peer or did not check late source race");}
    Console.WriteLine("PASS actual Review/Confirm/CommitPlan "+mode);
   }finally{AppDomain.CurrentDomain.SetData("Confectory.EditWorkspace."+handle,null);Directory.Delete(root,true);}
  }
 }
}'''
for token,key in [('REVIEW','Review'),('CONFIRM','Confirm'),('COMMITPLAN','CommitPlan'),('SNAPSHOT','Snapshot')]:source=source.replace(token,bodies[key])
(case/'Program.cs').write_text(source)
print('CASE '+str(case),flush=True)
result=subprocess.run([os.environ.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'),'run','--project',str(case/'probe.csproj'),'-c','Release','-p:UseSharedCompilation=false'],cwd=repo)
if result.returncode==0:(case/'evidence.json').write_text(json.dumps({'actualProductionBodies':{paths[k]:hashlib.sha256(v.encode()).hexdigest() for k,v in bodies.items()},'controlledDependencies':True,'nativeWindows':False,'checks':4},indent=2))
raise SystemExit(result.returncode)
