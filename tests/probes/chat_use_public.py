"""Shipped public ChatUse admission block; no real model/permission operation."""
import os,pathlib,subprocess,sys,tempfile
repo=pathlib.Path(sys.argv[1]).resolve();root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-public-use-'));text=(repo/'examples/editor-home/WebInvoke.csbody').read_text();a=text.index('if(endpoint=="chatUse")');b=text.index('if(endpoint=="helperGlobal")',a)
(root/'probe.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings></PropertyGroup></Project>')
code=r'''
using System.Text.Json.Nodes;
class Probe{
 class Call{public Func<string,string,string,string> Invoke;}
 class Calls{public Call ChatUse;}
 static string Invoke(Calls calls,Func<string,JsonObject,JsonNode> Command,JsonObject args){string endpoint="chatUse",context="owned";var before=new JsonObject();BLOCK throw new Exception("unhandled");}
 static void Main(){int called=0,commands=0,checks=0;var calls=new Calls{ChatUse=new(){Invoke=(_,_,_)=>{called++;return "{\"state\":\"fixture-only\"}";}}};JsonNode Command(string action,JsonObject request){commands++;return new JsonObject();}
 void Denied(string payload){bool denied=false;try{Invoke(calls,Command,JsonNode.Parse(payload)!.AsObject());}catch(UnauthorizedAccessException){denied=true;}if(!denied||called!=0||commands!=0)throw new Exception("Forbidden public route reached a grant handler");checks++;}
 foreach(string action in new[]{"accept","revoke-helper","authorize","placement-accept","placement-status"})Denied(new JsonObject{["action"]=action,["kind"]="project",["helper"]="owned-helper",["challenge"]="caller-challenge"}.ToJsonString());
 Denied("{\"action\":\"agent-accept\",\"agent\":\"Confectory.Agent.Responses::Connection\",\"challenge\":\"caller\"}");Denied("{\"action\":\"agent-accept\",\"agent\":\"Confectory.Agent.Codex::Connection\",\"approvals\":{\"contentApproved\":true}}");Denied("{\"action\":\"agent-accept\",\"agent\":\"Confectory.Agent.Codex::Connection\",\"configuration\":{}}");
 foreach(string action in new[]{"agent-accept","revoke-agent"}){Invoke(calls,Command,new JsonObject{["action"]=action,["agent"]="Confectory.Agent.Codex::Connection",["challenge"]="fixture"});if(commands==0||called!=0)throw new Exception("Agent command route lost");checks++;}
 Console.WriteLine($"PASS {checks} public legacy/internal/forged route barriers and Agent command dispatch; no actual grant");}
}
'''.replace('BLOCK',text[a:b]);(root/'Program.cs').write_text(code)
r=subprocess.run([os.environ.get('CONFECTORY_DOTNET','dotnet'),'run','--project',str(root/'probe.csproj'),'-c','Release'],capture_output=True,text=True,timeout=90);print(r.stdout+r.stderr,end='');print('ARTIFACT '+str(root));sys.exit(r.returncode)
