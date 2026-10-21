"""Shipped browser checkpoint contract with private fixture sources and CAS adapters."""
import os,pathlib,subprocess,sys,tempfile
repo=pathlib.Path(sys.argv[1]).resolve();root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-browser-drafts-'))
(root/'probe.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>disable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>')
code=r'''
using System;
using System.IO;
using System.Text.Json.Nodes;
class Calls{
 public Func<string,string[]> Identity=null!,List=null!;public Func<string,string,string[]> Read=null!;public Func<string,string> Saved=null!,Save=null!;public Func<string,string[]> FileSnapshot=null!;public Func<string,string[],string[],long[],string[],bool> EditBatch=null!;
}
class Probe{
 static string Hash(string text)=>Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(text))).ToLowerInvariant();
 static string Run(Calls calls,string draft,string input){BODY}
 static void Main(string[] args){string folder=args[0];Directory.CreateDirectory(folder);string original="object Owned::Unit { }",text=original,saved="";long revision=1;int writes=0,batches=0,reads=0,checks=0;bool rejectBatch=false;string baseline=Hash(original);File.WriteAllText(Path.Combine(folder,"Unit.celem"),original);
 var identity=new[]{"owned-project","owned-participant","owned-context",folder};var calls=new Calls{Identity=_=>identity,List=_=>new[]{"Owned::ProjectManifest","Owned::Unit"},Read=(_,id)=>id=="Owned::Unit"?new[]{id,"object","Unit.celem",text,revision.ToString(),baseline,text==original?"clean":"dirty"}:id=="Owned::ProjectManifest"?new[]{id,"project","project.cproj","project", "1","baseline","clean"}:throw new ArgumentException("unknown owned unit"),Saved=_=>saved,FileSnapshot=path=>{reads++;return File.Exists(path)?new[]{"exists",File.ReadAllText(path),Hash(File.ReadAllText(path))}:new[]{"missing","","missing"};}};
 string Checkpoint()=>new JsonObject{["version"]=1,["project"]=identity[0],["participant"]=identity[1],["context"]=identity[2],["changes"]=new JsonArray(new JsonObject{["id"]="Owned::Unit",["kind"]="object",["path"]="Unit.celem",["baseline"]=baseline,["draft"]=text})}.ToJsonString();
 calls.Save=_=>{writes++;saved=Checkpoint();return "private-checkpoint";};calls.EditBatch=(_,ids,texts,revisions,hashes)=>{batches++;if(rejectBatch||revisions[0]!=revision||hashes[0]!=Hash(text))return false;text=texts[0];revision++;return true;};
 void Check(bool value){if(!value)throw new Exception("browser draft check "+checks);checks++;}
 JsonNode Status()=>JsonNode.Parse(Run(calls,"owned",new JsonObject{["action"]="status",["ids"]=new JsonArray("Owned::Unit")}.ToJsonString()))!;
 JsonObject Action(JsonNode status,string action)=>new(){["action"]=action,["ownerHash"]=status["ownerHash"]!.DeepClone(),["ids"]=status["ids"]!.DeepClone(),["revisions"]=new JsonArray(status["rows"]![0]!["revision"]!.DeepClone()),["hashes"]=new JsonArray(status["rows"]![0]!["hash"]!.DeepClone()),["checkpointHash"]=status["checkpointHash"]!.DeepClone()};
 void Denied(JsonObject request){bool denied=false;try{Run(calls,"owned",request.ToJsonString());}catch(Exception e)when(e is ArgumentException or UnauthorizedAccessException or InvalidOperationException){denied=true;}Check(denied);}
 var initial=Status();Check(initial["unsaved"]!.GetValue<bool>()==false&&initial["dirty"]!.GetValue<bool>()==false&&writes==0);
 text="object Owned::Unit { description \"saved\"; }";revision++;var before=Status();Check(before["unsaved"]!.GetValue<bool>()&&before["canDiscard"]!.GetValue<bool>());Run(calls,"owned",Action(before,"save").ToJsonString());Check(writes==1&&File.ReadAllText(Path.Combine(folder,"Unit.celem"))==original);Check(!Status()["unsaved"]!.GetValue<bool>()&&Status()["dirty"]!.GetValue<bool>());
 string checkpointText=text;text="object Owned::Unit { description \"unsaved\"; }";revision++;var edited=Status();Run(calls,"owned",Action(edited,"discard").ToJsonString());Check(text==checkpointText&&batches==1&&writes==1&&File.ReadAllText(Path.Combine(folder,"Unit.celem"))==original);
 var stale=Status();revision++;Denied(Action(stale,"discard"));Check(batches==1);var forged=Action(Status(),"discard");forged["checkpointHash"]=new string('0',64);Denied(forged);
 var foreign=Action(Status(),"discard");foreign["ownerHash"]=new string('f',64);Denied(foreign);rejectBatch=true;Denied(Action(Status(),"discard"));Check(text==checkpointText);rejectBatch=false;
 Denied(new(){["action"]="exec",["ids"]=new JsonArray("Owned::Unit")});Denied(new(){["action"]="status",["ids"]=new JsonArray("Other::Unit")});Denied(new(){["action"]="status",["ids"]=new JsonArray("Owned::Unit","Owned::Unit")});Denied(new(){["action"]="status",["ids"]=new JsonArray("Owned::ProjectManifest")});Denied(new(){["action"]="status",["ids"]=new JsonArray("Owned::Unit"),["path"]="elsewhere"});
 string valid=saved;saved=valid.Replace("owned-project","other-project");Denied(new(){["action"]="status",["ids"]=new JsonArray("Owned::Unit")});saved=valid.Replace("Unit.celem","Elsewhere.celem");Denied(new(){["action"]="status",["ids"]=new JsonArray("Owned::Unit")});
 saved="";File.WriteAllText(Path.Combine(folder,"Unit.celem"),"changed on disk");var conflict=Status();Check(!conflict["canDiscard"]!.GetValue<bool>());Denied(Action(conflict,"discard"));File.WriteAllText(Path.Combine(folder,"Unit.celem"),original);
 if(!OperatingSystem.IsWindows()){string path=Path.Combine(folder,"Unit.celem"),aside=path+".owned";File.Move(path,aside);File.CreateSymbolicLink(path,aside);int count=reads;Denied(new(){["action"]="status",["ids"]=new JsonArray("Owned::Unit")});Check(reads==count);File.Delete(path);File.Move(aside,path);}
 Check(writes==1&&File.ReadAllText(Path.Combine(folder,"Unit.celem"))==original);Console.WriteLine($"PASS {checks} browser checkpoint scope/revision/CAS/save/discard/source-preservation cases; no final Confirm or account action");}
}
'''.replace('BODY',(repo/'packs/pack-workspace/BrowserDrafts.csbody').read_text())
(root/'Program.cs').write_text(code);env=os.environ.copy();dotnet=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet');run=subprocess.run([dotnet,'run','--project',str(root/'probe.csproj'),'-c','Release','--',str(root/'owned')],capture_output=True,text=True,env=env,timeout=120);print(run.stdout+run.stderr);print('ARTIFACT '+str(root));raise SystemExit(run.returncode)
