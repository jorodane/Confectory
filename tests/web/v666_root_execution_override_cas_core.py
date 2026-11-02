"""Execute production Review/Confirm/CommitPlan bodies; inject a late read race.
Compiler and editor dependencies are controlled here; renderer/compiler tests
cover those real paths separately. This is not native Windows verification.
"""
import hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
repo=Path(sys.argv[1]).resolve();case=Path(tempfile.mkdtemp(prefix='confectory-public-return-cas-'))
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
  foreach(string mode in new[]{"success-local","race-local","success-external","race-external"}){
   string handle=Guid.NewGuid().ToString("N"),root=Path.Combine(Path.GetTempPath(),"public-return-case-"+handle),owner="Owned::Child/body:common";Directory.CreateDirectory(root);bool external=mode.EndsWith("external",StringComparison.Ordinal),race=mode.StartsWith("race",StringComparison.Ordinal);
   string dependency=external?Path.Combine(Path.GetTempPath(),"registered-parent-"+handle+".celem"):Path.Combine(root,"Parent.celem");
   string original="{\"executionExitMode\":false}",draft="{\"executionExitMode\":true}";
   try{
    File.WriteAllText(Path.Combine(root,"Child.graph.json"),original);File.WriteAllText(dependency,"observed parent");
    var state=new JsonObject{["namespace"]="Owned",["root"]=root,["project"]=Path.Combine(root,"project.cproj"),["units"]=new JsonObject{[owner]=new JsonObject{["id"]=owner,["kind"]="blueprint",["path"]="Child.graph.json",["baseline"]=Hash(original),["draft"]=draft,["original"]=original,["atomicEditGroup"]=new JsonArray(owner),["publicBodyOrigin"]=new JsonObject()}}};
    AppDomain.CurrentDomain.SetData("Confectory.EditWorkspace."+handle,state);var before=state.DeepClone();var changes=new[]{owner,"Child.graph.json",Hash(original),draft};int accepted=0,commits=0,verified=0;
    var calls=new Calls{Changes=(h,ids)=>changes,Identity=h=>new[]{Path.Combine(root,"project.cproj"),"actor","context",root},Snapshot=Snapshot,WriteAtomic=(path,text)=>{Directory.CreateDirectory(Path.GetDirectoryName(path)!);File.WriteAllText(path,text);},CopySources=(from,to)=>Directory.CreateDirectory(to)};
    // Semantic receipt/registry verification is exercised by the real engine API
    // tests. Here this controlled dependency isolates the production final lease.
    calls.Metadata=(op,input)=>{Check(op=="blueprintOverrideContracts","Unexpected semantic boundary");var request=JsonNode.Parse(input)!;if(request["action"]!.ToString()=="verifyGroup")verified++;var guard=new JsonObject{["path"]=external?dependency:"Parent.celem",["hash"]=Hash("observed parent")};return new JsonObject{["checks"]=external?new JsonArray():new JsonArray(guard),["reads"]=external?new JsonArray(guard):new JsonArray(),["readOnly"]=true}.ToJsonString();};
    calls.ValidateSelection=(h,ids)=>Review(h,ids,calls);calls.Accept=(h,ids)=>accepted++;calls.Acknowledge=(h,ids)=>{};
    calls.CommitPlan=(r,input)=>{commits++;var plan=JsonNode.Parse(input)!;var guards=plan[external?"reads":"checks"]!.AsArray();Check(guards.Single()!["path"]!.ToString()==(external?dependency:"Parent.celem"),"Final public return source observation omitted");Check(!plan["writes"]!.AsArray().Any(row=>row!["path"]!.ToString().Contains("Parent",StringComparison.Ordinal)),"Parent became a write");if(race)File.WriteAllText(dependency,"peer parent");return Plan(r,input,calls);};
    var result=Confirm(handle,new[]{owner},"fixture",changes,calls);Check(verified>=2&&commits==1,"Review or final verification was skipped");
    if(!race)Check(result[0]=="confirmed"&&accepted==1&&File.ReadAllText(Path.Combine(root,"Child.graph.json"))==draft&&File.ReadAllText(dependency)=="observed parent","Successful return CAS changed parent or lost body");
    else {Check(result[0]=="conflict"&&accepted==0,"Late parent race accepted");Check(File.ReadAllText(Path.Combine(root,"Child.graph.json"))==original&&!File.Exists(Path.Combine(root,".confectory/activity.json")),"Partial graph/activity write");Check(JsonNode.DeepEquals(state,before)&&File.ReadAllText(dependency)=="peer parent","Retained input or peer parent lost");}
    Console.WriteLine("PASS actual public return Review/Confirm/CommitPlan "+mode);
   }finally{AppDomain.CurrentDomain.SetData("Confectory.EditWorkspace."+handle,null);Directory.Delete(root,true);if(external)File.Delete(dependency);}
  }
 }
}'''
for token,key in [('REVIEW','Review'),('CONFIRM','Confirm'),('COMMITPLAN','CommitPlan'),('SNAPSHOT','Snapshot')]:source=source.replace(token,bodies[key])
(case/'Program.cs').write_text(source)
print('CASE '+str(case),flush=True)
result=subprocess.run([os.environ.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'),'run','--project',str(case/'probe.csproj'),'-c','Release','-p:UseSharedCompilation=false'],cwd=repo)
if result.returncode==0:(case/'evidence.json').write_text(json.dumps({'actualProductionBodies':{paths[k]:hashlib.sha256(v.encode()).hexdigest() for k,v in bodies.items()},'controlledDependencies':True,'nativeWindows':False,'checks':4,'semanticReceiptValidation':'separate real-engine override API'},indent=2))
raise SystemExit(result.returncode)
