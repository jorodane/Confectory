#!/usr/bin/env python3
"""Auxiliary fault sweep of exact product bodies; never a target UI acceptance gate."""
import os, re, subprocess, sys
from pathlib import Path
repo=Path(__file__).resolve().parents[2]
output=Path(sys.argv[1]);output.mkdir(parents=True,exist_ok=True)
imports=re.findall(r'import\s+\S+\s+as\s+(\w+)\s*\(([^)]*)\)\s*->\s*([^;]+);',(repo/'examples/editor-home/MainBody.celem').read_text())
fields=[]
for name,args,result in imports:
    types=[x.strip() for x in args.split(',') if x.strip()];result=result.strip()
    kind=('Action'+('<'+','.join(types)+'>' if types else '')) if result=='void' else 'Func<'+','.join(types+[result])+'>'
    fields.append('public '+kind+' '+name+' = null!;')
main=(repo/'examples/editor-home/Main.csbody').read_text()
close=(repo/'packs/editor-home-model/CloseSession.csbody').read_text()
loopclose=(repo/'packs/host-loop/Close.csbody').read_text()
program=r'''
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;
RunModel();RunStartup();Console.WriteLine("Editor lifetime exact-body fault/retry gate PASS; not platform UI acceptance");
static void Require(bool value,string message){if(!value)throw new Exception(message);}
static void RunModel(){
 var counts=new Dictionary<string,int>();bool fail=true;void Release(string key){counts[key]=counts.GetValueOrDefault(key)+1;if(fail&&key is "shell-a" or "workspace-a" or "manager")throw new IOException("injected "+key);}
 var calls=new CloseCalls();calls.ShellClose=Release;calls.WorkspaceClose=Release;calls.Dispose=manager=>{Release("manager");manager[1]="disposed";};
 string token=Guid.NewGuid().ToString("N");var shells=new Dictionary<string,string>{{"a","shell-a"},{"b","shell-b"}};var workspaces=new List<string>{"workspace-a","workspace-b"};var state=new object[]{new string[]{"manager","active","","execution",""},"repo","storage",new JsonObject(),"{}",workspaces,false,shells,new Dictionary<string,string>()};AppDomain.CurrentDomain.SetData("Confectory.EditorHome."+token,state);
 try{ProductClose(calls,token);throw new Exception("Failure swallowed");}catch(AggregateException error){Require(error.InnerExceptions.Count==3,"Not every failed resource reported");}
 Require((bool)state[6]&&AppDomain.CurrentDomain.GetData("Confectory.EditorHome."+token)!=null,"Closing session was discarded");Require(shells.Count==1&&workspaces.Count==1,"Successful releases retained or failed handles removed");Require(counts.Count==5,"A failing resource prevented other release attempts");
 fail=false;ProductClose(calls,token);Require(counts["manager"]==2&&((string[])state[0])[1]=="disposed","Manager close did not retry");Require(counts["shell-a"]==2&&counts["workspace-a"]==2&&counts["shell-b"]==1&&counts["workspace-b"]==1,"Release retry repeated successful resources");Require(AppDomain.CurrentDomain.GetData("Confectory.EditorHome."+token)==null,"Closed registry retained");ProductClose(calls,token);Require(counts["manager"]==2,"Closed call repeated release");Console.WriteLine("R1 retry: disposeAttempts=2; managerState=disposed; registryRetained=False; independent release PASS");
}
static void RunStartup(){
 foreach(string point in new[]{"session","control-1","control-2","owner","surfaces","native-1","native-2","text-1","text-2","text-3","text-4","snapshot","nav","listen","run",""})ProbeStartup(point,"");
 ProbeStartup("listen","native-1");ProbeStartup("run","session");
}
static void ProbeStartup(string failAt,string releaseFail){
 var created=new HashSet<string>();var released=new HashSet<string>();var attempts=new Dictionary<string,int>();int controls=0,native=0,text=0;
 void Fault(string key){if(key==failAt)throw new IOException("injected "+key);}
 string Create(string key){Fault(key);Require(created.Add(key),"Duplicate acquisition "+key);return key;}
 void Release(string key){attempts[key]=attempts.GetValueOrDefault(key)+1;if(key==releaseFail&&attempts[key]==1)throw new IOException("injected release "+key);Require(released.Add(key),"Successful resource released twice: "+key);}
 var calls=new MainCalls();calls.CreateSession=(repo,storage)=>Create("session");calls.CloseSession=Release;calls.CreateControls=ids=>Create("control-"+(++controls));calls.CloseControls=Release;calls.CreateOwner=capacity=>new[]{Create("owner")};calls.DisposeOwner=value=>Release(value[0]);calls.CreateSurfaces=(titles,w,h)=>{Create("surfaces");return new long[]{111,222};};calls.Close=(value,index)=>Release("surfaces");calls.NativeCreate=(surfaces,index)=>Create("native-"+(++native));calls.NativeClose=Release;calls.CreateText=(role,value)=>Create("text-"+(++text));calls.CloseText=Release;calls.Snapshot=session=>{Fault("snapshot");return "{}";};calls.NavCreate=json=>{Fault("nav");return "{}";};calls.EntryRequest=(handle,operation,payload)=>{if(operation=="listen"){Fault("listen");return Create("listener");}Require(operation=="close","Unexpected entry operation");Release(handle);return "{}";};calls.HostRun=token=>{Fault("run");((Action)((object[])AppContext.GetData("Confectory.HostLoop."+token)!)[1])();return 0;};
 var diagnostics=new StringWriter();var original=Console.Error;Console.SetError(diagnostics);bool failed=false;try{ProductMain(calls);}catch(IOException error){failed=true;Require(error.Message=="injected "+failAt,"Original startup error replaced");}finally{Console.SetError(original);}
 Require(failed==(failAt.Length>0),"Startup fault expectation failed: "+failAt);
 if(releaseFail.Length>0){Require(created.Except(released).SequenceEqual(new[]{releaseFail}),"Failed cleanup did not retain only pending resource");string token=Regex.Match(diagnostics.ToString(),@"Editor cleanup retained for retry: ([a-f0-9]+)").Groups[1].Value;Require(token.Length>0,"Failure token unavailable for retry");Require(CloseLoop(token),"Retry remained pending");Require(AppContext.GetData("Confectory.HostLoop."+token)==null,"Successful retry retained registry");Require(CloseLoop(token),"Repeated closed retry failed");Require(attempts[releaseFail]==2,"Failed release not retried exactly once");}
 Require(created.SetEquals(released),"Startup leaked acquired resources at "+failAt);Require(attempts.All(pair=>pair.Value==(pair.Key==releaseFail?2:1)),"Successful releases repeated");Console.WriteLine("R2 startup/cleanup: "+(failAt.Length>0?failAt:"success")+" / "+releaseFail+" PASS");
}
static int ProductMain(MainCalls calls){
__MAIN__
}
static void ProductClose(CloseCalls calls,string session){
__CLOSE__
}
static bool CloseLoop(string token){
__LOOPCLOSE__
}
class CloseCalls {public Action<string> ShellClose=null!, WorkspaceClose=null!;public Action<string[]> Dispose=null!;}
class MainCalls {
__FIELDS__
}
'''
program=program.replace('__MAIN__',main).replace('__CLOSE__',close).replace('__LOOPCLOSE__',loopclose).replace('__FIELDS__','\n'.join(fields))
(output/'Program.cs').write_text(program)
(output/'Probe.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>')
subprocess.run([os.environ.get('CONFECTORY_DOTNET','dotnet'),'run','--project',str(output/'Probe.csproj'),'-c','Release'],check=True)
