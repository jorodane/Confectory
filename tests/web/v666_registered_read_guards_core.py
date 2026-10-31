"""Execute production Confirm/CommitPlan and inject a race after receipt verification.
Registry authority and real compilation are covered by the separate API/UI suite;
only that metadata response and compiler are controlled in this source-lease probe.
"""
import hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
repo=Path(sys.argv[1]).resolve();case=Path(tempfile.mkdtemp(prefix='confectory-registered-read-guards-'))
(case/'probe.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Exe</OutputType><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>')
paths={'CONFIRM':'packs/change-set/ConfirmReviewed.csbody','PLAN':'packs/file-stream/CommitPlan.csbody'};bodies={k:(repo/p).read_text() for k,p in paths.items()}
source=r'''using System.Text.Json.Nodes;using System.Text;using System.Security.Cryptography;
class Calls{
 public Func<string,string[],string[]> Changes=null!;public Action<string,string[]> ValidateSelection=null!,Accept=null!,Acknowledge=(h,ids)=>{};
 public Func<string,string[]> Identity=null!;public Action<string,string> CopySources=(a,b)=>Directory.CreateDirectory(b),WriteAtomic=null!;
 public Func<string,string,string> Prepare=(a,b)=>"project",Validate=(a,b)=>"valid",Metadata=null!;
 public Func<string,string,string[]> Activity=(a,b)=>new[]{"activity.json","missing","activity"},CommitPlan=null!;
 public Func<string,string[],string[],string[],string[]> Commit=(a,b,c,d)=>throw new Exception("Typed CAS required");
 public Func<string,string> LeasePath=root=>Path.Combine(root,".confectory/source-transaction.lock");
}
class Program{
 static string[] Confirm(string handle,string[] selected,string target,string[] reviewed,Calls calls){CONFIRM}
 static string[] Plan(string root,string plan,Calls calls){PLAN}
 static string Hash(string text)=>Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(text))).ToLowerInvariant();
 static void Check(bool ok,string message){if(!ok)throw new Exception(message);}
 static void Main(){foreach(string mode in new[]{"success","after-metadata-race","missing-parent","tampered-hash","write-failure"}){
  string dir=Path.Combine(Path.GetTempPath(),"registered-cas-"+Guid.NewGuid().ToString("N")),root=Path.Combine(dir,"owned"),parent=Path.Combine(dir,"parent.celem"),handle=Guid.NewGuid().ToString("N"),owner="Owned::Body/body:common";Directory.CreateDirectory(root);File.WriteAllText(parent,"original parent");File.WriteAllText(Path.Combine(root,"Owner.celem"),"old child");
  var unit=new JsonObject{["kind"]="blueprint",["path"]="Owner.celem",["baseline"]=Hash("old child"),["original"]="old child",["draft"]="new child",["atomicEditGroup"]=new JsonArray(owner),["nodeFlowOrigin"]=new JsonObject()};var state=new JsonObject{["units"]=new JsonObject{[owner]=unit}};var before=state.DeepClone();AppDomain.CurrentDomain.SetData("Confectory.EditWorkspace."+handle,state);int accepted=0;
  try{
   var changes=new[]{owner,"Owner.celem",Hash("old child"),"new child"};var calls=new Calls{Changes=(h,ids)=>changes,Identity=h=>new[]{Path.Combine(root,"project.cproj"),"actor","context",root},ValidateSelection=(h,ids)=>{},Accept=(h,ids)=>accepted++,WriteAtomic=(path,text)=>{if(mode=="write-failure"&&path==Path.Combine(root,"activity.json"))throw new IOException("injected write failure");Directory.CreateDirectory(Path.GetDirectoryName(path)!);File.WriteAllText(path,text);}};
   calls.Metadata=(op,input)=>new JsonObject{["reads"]=new JsonArray(new JsonObject{["path"]=parent,["hash"]=mode=="tampered-hash"?new string('0',64):Hash("original parent")})}.ToJsonString();
   calls.CommitPlan=(r,input)=>{var plan=JsonNode.Parse(input)!;Check(plan["reads"]!.AsArray().Single()!["path"]!.ToString()==parent,"External observation lost");Check(!plan["writes"]!.AsArray().Any(p=>Path.IsPathRooted(p!["path"]!.ToString())),"External source became a write");if(mode=="after-metadata-race")File.WriteAllText(parent,"peer after metadata");if(mode=="missing-parent")File.Move(parent,parent+".retained");return Plan(r,input,calls);};
   var result=Confirm(handle,new[]{owner},"fixture",changes,calls);
   if(mode=="success")Check(result[0]=="confirmed"&&accepted==1&&File.ReadAllText(Path.Combine(root,"Owner.celem"))=="new child"&&File.ReadAllText(parent)=="original parent","Positive checkpoint failed");
   else{Check(result[0] is "conflict" or "invalid"&&accepted==0,"CAS refusal required");Check(File.ReadAllText(Path.Combine(root,"Owner.celem"))=="old child"&&!File.Exists(Path.Combine(root,"activity.json"))&&JsonNode.DeepEquals(state,before),"Partial write or lost input");if(mode=="after-metadata-race")Check(File.ReadAllText(parent)=="peer after metadata","Peer overwritten");}
   // The optional read-only channel never permits an absolute/escaping write,
   // or a text payload disguised as a read observation.
   foreach(bool absolute in new[]{true,false}){string sentinel=Path.Combine(dir,"sentinel");File.WriteAllText(sentinel,"retained");var plan=new JsonObject{["writes"]=new JsonArray(new JsonObject{["path"]=absolute?sentinel:"Owner.celem",["hash"]=Hash(absolute?"retained":"old child"),["text"]="forbidden"}),["checks"]=new JsonArray(),["reads"]=absolute?new JsonArray():new JsonArray(new JsonObject{["path"]=sentinel,["hash"]=Hash("retained"),["text"]="forbidden"})};bool refused=false;try{Plan(root,plan.ToJsonString(),calls);}catch(ArgumentException){refused=true;}Check(refused&&File.ReadAllText(sentinel)=="retained","Read-only boundary weakened");}
   Console.WriteLine("PASS production registered read CAS "+mode);
  }finally{AppDomain.CurrentDomain.SetData("Confectory.EditWorkspace."+handle,null);Directory.Delete(dir,true);}
 }}
}'''
for token,body in bodies.items():source=source.replace(token,body)
(case/'Program.cs').write_text(source);print('CASE '+str(case),flush=True)
result=subprocess.run([os.environ.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'),'run','--project',str(case/'probe.csproj'),'-c','Release','-p:UseSharedCompilation=false'],cwd=repo)
if result.returncode==0:(case/'evidence.json').write_text(json.dumps({'actualProductionBodies':{paths[k]:hashlib.sha256(v.encode()).hexdigest() for k,v in bodies.items()},'controlledMetadataAndCompiler':True,'nativeWindows':False,'checks':5},indent=2))
raise SystemExit(result.returncode)
