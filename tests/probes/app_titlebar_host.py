"""Exact host command and caption geometry with FakeForm; not native Windows QA."""
from pathlib import Path
import os,subprocess,tempfile,sys
r=Path(sys.argv[1]).resolve();root=Path(tempfile.mkdtemp(prefix='confectory-titlebar-host-'));s=(r/'targets/webview-windows/Program.cs').read_text();old=subprocess.check_output(['git','show','9eecdcc:./targets/webview-windows/Program.cs'],cwd=r,text=True)
def closing(t):return t[t.index('        form.FormClosing +='):t.index('        form.Shown +=')]
assert closing(s)==closing(old),'Existing close/flush/cleanup sequence changed'
a=s.index('if(message["native"]?.GetValue<string>()=="window"){');b=s.index('}else if(message["native"]?.GetValue<string>()=="site-connect")',a);block=s[a:b+1]
geometry=(r/'targets/webview-windows/AppWindowForm.cs').read_text().split('internal static class CaptionGeometry',1)[1]
(root/'probe.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>')
code=r'''
using System.Text.Json.Nodes;
enum FormWindowState{Normal,Minimized,Maximized}
class FakeForm{public FormWindowState WindowState;public bool CustomCaption;public int CloseCalls;public void Close()=>CloseCalls++;public void SetCustomCaption(bool value)=>CustomCaption=value;}
class Probe{
 static JsonNode? Invoke(FakeForm form,string payload,bool supported=true,bool pending=false,bool picker=false){var message=JsonNode.Parse(payload)!;bool nonClientSupported=supported,closing=false,closePending=pending,nativePickerOpen=picker;JsonNode? response=null;JsonObject WindowSnapshot()=>new(){["state"]=form.WindowState.ToString()};BLOCK return response;}
 static void Main(){int checks=0;void Check(bool value){if(!value)throw new Exception("Window contract assertion "+checks);checks++;}
 foreach(var x in new[]{(100,1000,131,992,108),(100,1000,146,988,112),(-800,200,-754,188,-788),(-8,1088,23,1080,0),(100,1000,123,1000,100)})Check(CaptionGeometry.ClientTop(x.Item1,x.Item2,x.Item3,x.Item4)==x.Item5);
 JsonNode? Call(FakeForm f,string action,bool enabled=true)=>Invoke(f,new JsonObject{["native"]="window",["envelope"]=action=="chrome"?new JsonObject{["command"]=action,["enabled"]=enabled}:new JsonObject{["command"]=action}}.ToJsonString());
 var f=new FakeForm();Call(f,"chrome");Check(f.CustomCaption);Call(f,"maximize");Check(f.WindowState==FormWindowState.Maximized);Call(f,"toggle-maximize");Check(f.WindowState==FormWindowState.Normal);Call(f,"minimize");Check(f.WindowState==FormWindowState.Minimized);Call(f,"restore");Check(f.WindowState==FormWindowState.Normal);Call(f,"close");Check(f.CloseCalls==1);Call(f,"chrome",false);Check(!f.CustomCaption);
 foreach(string command in new[]{"exec","project-run","unknown"}){bool denied=false;try{Call(f,command);}catch(UnauthorizedAccessException){denied=true;}Check(denied&&f.CloseCalls==1);}
 bool extraDenied=false;try{Invoke(f,"{\"native\":\"window\",\"envelope\":{\"command\":\"close\",\"windowId\":1}}");}catch(UnauthorizedAccessException){extraDenied=true;}Check(extraDenied&&f.CloseCalls==1);
 string close="{\"native\":\"window\",\"envelope\":{\"command\":\"close\"}}";Check(Invoke(f,close,pending:true)!["error"]!["code"]!.ToString()=="window_busy"&&f.CloseCalls==1);Check(Invoke(f,close,picker:true)!["ok"]!.GetValue<bool>()==false&&f.CloseCalls==1);Check(Invoke(f,close,supported:false)!["ok"]!.GetValue<bool>()==false&&f.CloseCalls==1);Console.WriteLine($"PASS {checks} caption geometry/owned window command cases; unchanged FormClosing source; no native Windows execution");}
}
internal static class CaptionGeometry GEOMETRY
'''.replace('BLOCK',block).replace('GEOMETRY',geometry)
(root/'Program.cs').write_text(code);run=subprocess.run([os.environ.get('CONFECTORY_DOTNET','dotnet'),'run','--project',str(root/'probe.csproj'),'-c','Release'],capture_output=True,text=True,timeout=90);print(run.stdout+run.stderr,end='');print('ARTIFACT '+str(root));raise SystemExit(run.returncode)
