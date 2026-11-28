"""Exercise the production CommitPlan body with complete paged evidence.

The real Chromium retirement tests cover DSL/provider wiring. This probe
injects a change in the last read page before the actual source lease.
"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

repo=Path(sys.argv[1]).resolve()
with tempfile.TemporaryDirectory(prefix="cf-paged-read-cas-") as folder:
    root=Path(folder)
    (root/"probe.csproj").write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>')
    source=r'''
using System.Text.Json.Nodes;
using System.Security.Cryptography;
class Calls {
 public Func<string,string> LeasePath=Program.Lease;
 public Action<string,string> WriteAtomic=Program.Write;
}
class Program {
 static string Hash(string path)=>Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path))).ToLowerInvariant();
 static void Check(bool condition,string message){if(!condition)throw new Exception(message);}
 public static string Lease(string root){LEASE_BODY}
 public static void Write(string path,string text){WRITE_BODY}
 public static string[] Plan(string root,string plan,Calls calls){PLAN_BODY}
 public static void Main(string[] args){
  string root=args[0];Directory.CreateDirectory(root);
  string manifest=Path.Combine(root,"project.cpack"), retained=Path.Combine(root,"retained.celem");
  File.WriteAllText(manifest,"before");File.WriteAllText(retained,"retained");
  JsonArray pages=new();JsonArray page=new();
  for(int i=0;i<400;i++){
   string path=Path.Combine(root,$"source-{i:0000}.celem");File.WriteAllText(path,$"source {i}");
   page.Add(new JsonObject{["path"]=path,["hash"]=Hash(path)});
   if(page.Count==64){pages.Add(page);page=new();}
  }
  if(page.Count>0)pages.Add(page);
  JsonObject Create()=>new(){["writes"]=new JsonArray(new JsonObject{["path"]="project.cpack",["hash"]=Hash(manifest),["text"]="after"}),["checks"]=new JsonArray(new JsonObject{["path"]="retained.celem",["hash"]=Hash(retained)}),["readPages"]=pages.DeepClone()};
  var calls=new Calls();int writes=0;calls.WriteAtomic=(path,text)=>{writes++;Write(path,text);};
  var plan=Create();File.WriteAllText(Path.Combine(root,"source-0399.celem"),"changed");
  Check(Plan(root,plan.ToJsonString(),calls)[0]=="conflict"&&writes==0&&File.ReadAllText(manifest)=="before","late-page mismatch allowed a write");
  File.WriteAllText(Path.Combine(root,"source-0399.celem"),"source 399");
  var duplicate=Create();duplicate["readPages"]!.AsArray()[^1]!.AsArray().Add(pages[0]!.AsArray()[0]!.DeepClone());
  bool denied=false;try{Plan(root,duplicate.ToJsonString(),calls);}catch(ArgumentException){denied=true;}
  Check(denied&&writes==0,"duplicate cross-page observation accepted");
  var tooManyWrites=Create();var write=tooManyWrites["writes"]!.AsArray()[0]!;
  tooManyWrites["writes"]!.AsArray().Add(write.DeepClone());tooManyWrites["writes"]!.AsArray().Add(write.DeepClone());
  denied=false;try{Plan(root,tooManyWrites.ToJsonString(),calls);}catch(ArgumentException){denied=true;}
  Check(denied&&writes==0,"paged write bound expanded");
  var oversized=Create();oversized["readPages"]!.AsArray()[0]!.AsArray().Add(pages[0]!.AsArray()[0]!.DeepClone());
  denied=false;try{Plan(root,oversized.ToJsonString(),calls);}catch(ArgumentException){denied=true;}
  Check(denied&&writes==0,"oversized observation page admitted");
  var legacy=Create();legacy.Remove("readPages");legacy["reads"]=new JsonArray(pages.SelectMany(p=>p!.AsArray()).Select(r=>r!.DeepClone()).ToArray());
  denied=false;try{Plan(root,legacy.ToJsonString(),calls);}catch(ArgumentException){denied=true;}
  Check(denied&&writes==0,"legacy budget expanded");
  Check(Plan(root,Create().ToJsonString(),calls)[0]=="applied"&&writes==1&&File.ReadAllText(manifest)=="after"&&File.ReadAllText(retained)=="retained","valid complete paged evidence did not commit");
  Console.WriteLine("PASS 400 exact observations, final-page conflict, duplicate guard, legacy bound, retained source");
 }
}
'''
    for name,path in (("PLAN_BODY","CommitPlan"),("LEASE_BODY","LeasePath"),("WRITE_BODY","WriteAtomic")):
        source=source.replace(name,(repo/f"packs/file-stream/{path}.csbody").read_text())
    (root/"Program.cs").write_text(source)
    subprocess.run([os.environ["CONFECTORY_DOTNET"],"run","--project",str(root/"probe.csproj"),"-c","Release","--",str(root/"owned")],check=True,cwd=repo)
