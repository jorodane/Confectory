"""Compare factored shipped schemas with previous production project/node schemas.
Pure private capability descriptors only; no workspace, process permission or account.
"""
import os,pathlib,subprocess,sys,tempfile
repo=pathlib.Path(sys.argv[1]).resolve();root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-tool-schema-'))
(root/'probe.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>')
old=subprocess.check_output(['git','show','a10caf7:./packs/development-tools/Definitions.csbody'],cwd=repo,text=True)
code=r'''
using System.Text.Json.Nodes;
class Probe{
 class Calls{public Func<string,string> Schema=Describe;}
 static string Describe(string scope){SCHEMA}
 static string Before(string capability){OLD}
 static string After(Calls calls,string capability){NEW}
 static void Main(){int count=0;var calls=new Calls();
 foreach(var node in new JsonNode?[]{null,new JsonObject{["id"]="Owned::One"}}){
  var model=new JsonObject{["projectId"]="owned-project",["rights"]=node is null?new JsonArray("workspace_list","workspace_read","workspace_inspect","workspace_stage","workspace_create","workspace_changes"):new JsonArray("workspace_read","workspace_inspect","workspace_stage"),["nodeScope"]=node};
  string cap=Guid.NewGuid().ToString("N");var owner=new object[]{new object(),"","",model,false};AppDomain.CurrentDomain.SetData("Confectory.DevelopmentTools."+cap,owner);
  if(!JsonNode.DeepEquals(JsonNode.Parse(Before(cap)),JsonNode.Parse(After(calls,cap))))throw new Exception("Project/node schema changed");count++;
  owner[4]=true;bool denied=false;try{After(calls,cap);}catch(ObjectDisposedException){denied=true;}if(!denied)throw new Exception("Closed schema capability accepted");count++;
 }
 foreach(string payload in new[]{"{\"projectId\":\"p\",\"rights\":[\"workspace_confirm\"]}","{\"projectId\":\"p\",\"rights\":[\"exec\"]}","{\"projectId\":\"\",\"rights\":[]}"}){bool denied=false;try{Describe(payload);}catch(Exception e)when(e is ArgumentException or UnauthorizedAccessException){denied=true;}if(!denied)throw new Exception("Unknown rights/identity accepted");count++;}
 Console.WriteLine($"PASS {count} shipped project/node schema compatibility and closed/unknown scope cases");}
}
'''.replace('SCHEMA',(repo/'packs/development-tools/Schema.csbody').read_text()).replace('OLD',old).replace('NEW',(repo/'packs/development-tools/Definitions.csbody').read_text())
(root/'Program.cs').write_text(code)
r=subprocess.run([os.environ.get('CONFECTORY_DOTNET','dotnet'),'run','--project',str(root/'probe.csproj'),'-c','Release'],text=True,capture_output=True,timeout=90);print(r.stdout+r.stderr,end='');print('ARTIFACT '+str(root));sys.exit(r.returncode)
