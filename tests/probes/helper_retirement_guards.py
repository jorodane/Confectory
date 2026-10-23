"""Shipped HelperAgents body with fixture owner states/files; no real account/provider/API bypass."""
import os,pathlib,re,subprocess,sys,tempfile
repo=pathlib.Path(sys.argv[1]).resolve();root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-helper-guards-'));body=(repo/'packs/editor-home-model/HelperAgents.csbody').read_text();decl=(repo/'packs/editor-home-model/HelperAgentsBody.celem').read_text();fields=[]
for name,args,result in re.findall(r'import [^;]+? as (\w+) \(([^)]*)\) -> (\w+(?:\[\])?);',decl):
 types=[t.strip() for t in args.split(',') if t.strip()];kind=('Action<'+','.join(types)+'>') if result=='void' else 'Func<'+','.join(types+[result])+'>'
 fields.append('public '+kind+' '+name+'=('+','.join('_a'+str(i) for i in range(len(types)))+')=>throw new Exception("Unexpected '+name+' call");')
code=r'''
using System.Text.Json.Nodes;
class Probe{
 class Calls{FIELDS}
 static string Run(Calls calls,string session,string operation,string payload){BODY}
 static string Hash(string s)=>Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(s))).ToLowerInvariant();
 static string[] Snap(string path)=>File.Exists(path)?new[]{"exists",File.ReadAllText(path),Hash(File.ReadAllText(path))}:new[]{"missing","","missing"};
 record Fixture(Calls Calls,JsonObject Model,object[] State,object[] Owner,string Session,string Dir);
 static int Main(string[] args){
 int count=0,provider=0,revoke=0;string root=args[0];Directory.CreateDirectory(root);
 Fixture New(string name,bool project=false){
  string dir=Path.Combine(root,name),session=Guid.NewGuid().ToString("N");Directory.CreateDirectory(dir);string manifest=Path.Combine(dir,"A","project.cproj");
  var registry=JsonNode.Parse("""{"version":1,"agents":{"Confectory.Agent.Responses::Connection":{"connection":"Confectory.Agent.Responses::Connection","config":{"model":"fixture-no-provider"}}},"assignments":{"owned":"Confectory.Agent.Responses::Connection","other":"Confectory.Agent.Responses::Connection"}}""")!.AsObject();
  var selection=new JsonObject{["p-a"]=new JsonObject{["helper"]="owned",["helpers"]=new JsonArray("owned","other"),["manifest"]=manifest,["allowCommon"]=false}};
  File.WriteAllText(Path.Combine(dir,"helper-agents.json"),registry.ToJsonString());File.WriteAllText(Path.Combine(dir,"helper-selections.json"),selection.ToJsonString());
  var model=new JsonObject{["selected"]=new JsonObject{["projectId"]="p-a",["path"]=manifest},["helperSelections"]=selection,["aiRuns"]=new JsonObject(),["aiBindings"]=new JsonObject(),["revision"]=0};
  var owner=new object[14];owner[2]=Path.Combine(dir,"cards.json");owner[3]=model;owner[6]=false;AppDomain.CurrentDomain.SetData("Confectory.EditorHome."+session,owner);
  var state=new object[]{registry,Snap(Path.Combine(dir,"helper-agents.json"))[2],"fixture-store",new Dictionary<string,object[]>(StringComparer.Ordinal),new Dictionary<string,object[]>(StringComparer.Ordinal),new Dictionary<string,JsonObject>(StringComparer.Ordinal)};
  AppDomain.CurrentDomain.SetData("Confectory.EditorHome.HelperAgents."+session,state);
  var calls=new Calls();calls.HelperList=(_,_)=>new JsonArray(new JsonObject{["helper"]="owned",["personality"]="p",["speciality"]="s",["membership"]=new JsonObject{["kind"]=project?"project":"global",["projectId"]=project?"p-a":""}},new JsonObject{["helper"]="other",["personality"]="q",["speciality"]="t",["membership"]=new JsonObject{["kind"]="global",["projectId"]=""}}).ToJsonString();calls.Snapshot=Snap;
  calls.Commit=(storage,paths,hashes,texts)=>{if(paths.Where((p,i)=>Snap(Path.Combine(storage,p))[2]!=hashes[i]).Any())return new[]{"conflict"};for(int i=0;i<paths.Length;i++){string path=Path.Combine(storage,paths[i]);Directory.CreateDirectory(Path.GetDirectoryName(path)!);File.WriteAllText(path,texts[i]);}return new[]{"applied"};};
  calls.ChatUse=(_,op,input)=>{if(op!="revoke-helper"||JsonNode.Parse(input)?["helper"]?.ToString()!="owned")throw new Exception("Unexpected grant operation");Interlocked.Increment(ref revoke);return """{"state":"revoked"}""";};
  calls.Presentation=(_,helper,op,_)=>{if(op!="load")throw new Exception("Unexpected profile write");return new JsonObject{["revision"]="fixture",["value"]=new JsonObject{["version"]=1,["helper"]=helper,["name"]="fixture saved profile",["shortDescription"]="",["description"]="",["globalDraft"]="kept unsent"}}.ToJsonString();};
  calls.AgentOpen=_=>{Interlocked.Increment(ref provider);throw new Exception("Forbidden provider call");};
  return new(calls,model,state,owner,session,dir);
 }
 void Check(bool ok,string name){if(!ok)throw new Exception(name);Console.WriteLine("PASS "+name);count++;}
 string Plan(Fixture c)=>JsonNode.Parse(Run(c.Calls,c.Session,"archive-plan","""{"helper":"owned"}"""))!["token"]!.ToString();
 string Archive(Fixture c,string token)=>Run(c.Calls,c.Session,"archive",new JsonObject{["helper"]="owned",["token"]=token}.ToJsonString());
 bool Denied(Action f){try{f();return false;}catch(InvalidOperationException){return true;}catch(UnauthorizedAccessException){return true;}}
 void Unchanged(Fixture c,string registry,string selection){if(Snap(Path.Combine(c.Dir,"helper-agents.json"))[1]!=registry||Snap(Path.Combine(c.Dir,"helper-selections.json"))[1]!=selection||Directory.Exists(Path.Combine(c.Dir,"helper-archives")))throw new Exception("Partial archive");}
 var a=New("global-running");var turns=(Dictionary<string,object[]>)a.State[3];turns["owned"]=new object[]{new JsonObject{["state"]="running",["message"]="kept fixture text"},"","",null!};int before=revoke;
 Check(Denied(()=>Plan(a))&&revoke==before&&turns["owned"][0].ToString()!.Contains("kept fixture text"),"running global owner rejects deletion before revocation or provider access");
 var b=New("project-running",true);b.Model["aiRuns"]!["ctx"]=new JsonObject{["state"]="running",["helper"]="owned"};
 Check(Denied(()=>Plan(b))&&revoke==before,"running project owner rejects deletion");
 var c=New("queued-worker");c.Model["aiRuns"]!["ctx"]=new JsonObject{["state"]="idle",["workers"]=new JsonObject{["worker"]=new JsonObject{["ownerHelper"]="owned",["status"]="queued"}}};
 Check(Denied(()=>Plan(c))&&revoke==before,"queued owned worker rejects deletion");
 var d=New("started-after-plan");string token=Plan(d);((Dictionary<string,object[]>)d.State[3])["owned"]=new object[]{new JsonObject{["state"]="running"},"","",null!};string dr=Snap(Path.Combine(d.Dir,"helper-agents.json"))[1],ds=Snap(Path.Combine(d.Dir,"helper-selections.json"))[1];bool rejected=Denied(()=>Archive(d,token));Unchanged(d,dr,ds);
 Check(rejected&&revoke==before,"new work is rechecked at apply, retaining registry and every placement");
 var e=New("commit-cas");token=Plan(e);var commit=e.Calls.Commit;string external=Snap(Path.Combine(e.Dir,"helper-agents.json"))[1]+"\n",oldSelection=Snap(Path.Combine(e.Dir,"helper-selections.json"))[1];e.Calls.Commit=(storage,paths,hashes,texts)=>{File.WriteAllText(Path.Combine(storage,"helper-agents.json"),external);return commit(storage,paths,hashes,texts);};rejected=Denied(()=>Archive(e,token));Unchanged(e,external,oldSelection);
 Check(rejected&&revoke==before+1&&((JsonObject)e.State[0])["assignments"]?["owned"] is not null,"CAS failure retains external data and placements, scoped revoke fails closed");
 var f=New("queued-binding");token=Plan(f);using var entered=new ManualResetEventSlim();using var release=new ManualResetEventSlim();using var queued=new ManualResetEventSlim();var rev=f.Calls.ChatUse;
 f.Calls.ChatUse=(session,op,input)=>{entered.Set();if(!release.Wait(5000))throw new Exception("release timeout");return rev(session,op,input);};string applyToken=token;var applying=Task.Run(()=>Archive(f,applyToken));if(!entered.Wait(5000))throw new Exception("archive not entered");bool bindingDenied=false;var binding=Task.Run(()=>{queued.Set();bindingDenied=Denied(()=>Run(f.Calls,f.Session,"binding","""{"helper":"owned"}"""));});if(!queued.Wait(5000))throw new Exception("binding not queued");bool blocked=!binding.Wait(100);release.Set();Task.WaitAll(applying,binding);
 Check(blocked&&bindingDenied&&JsonNode.Parse(applying.Result)?["retained"]?.GetValue<bool>()==true,"queued binding waits for archive lock and cannot acquire removed assignment");
 Check(Denied(()=>Run(f.Calls,f.Session,"start",new JsonObject{["helper"]="owned",["token"]="retired-preview"}.ToJsonString())),"queued/future start cannot execute a deleted Helper's old preview");
 var g=New("project-manifest",true);token=Plan(g);string manifest=g.Model["selected"]!["path"]!.ToString();g.Model["selected"]!["path"]=Path.Combine(g.Dir,"B","project.cproj");
 Check(Denied(()=>Archive(g,token)),"same-id different manifest cannot reuse project deletion plan");g.Model["selected"]!["path"]=manifest;Archive(g,token);g.Model["selected"]!["path"]=Path.Combine(g.Dir,"B","project.cproj");
 Check(Denied(()=>Run(g.Calls,g.Session,"import","""{"helper":"owned","agent":"Confectory.Agent.Responses::Connection"}""")),"restore checks archived manifest and project identity");
 var h=New("other-helper-preview");h.Model["helperContext"]=new JsonObject{["helper"]="other"};h.Model["aiPreview"]=new JsonObject{["helperContext"]=new JsonObject{["helper"]="other"},["message"]="other fixture draft"};h.Model["globalHelperPreview"]=new JsonObject{["helper"]="other",["token"]="other-preview"};((Dictionary<string,object[]>)h.State[3])["other"]=new object[]{new JsonObject{["state"]="prepared"},"","",null!};Archive(h,Plan(h));
 Check(h.Model["helperContext"]?["helper"]?.ToString()=="other"&&h.Model["aiPreview"]?["message"]?.ToString()=="other fixture draft"&&h.Model["globalHelperPreview"]?["token"]?.ToString()=="other-preview"&&((JsonObject)((Dictionary<string,object[]>)h.State[3])["other"][0])["state"]?.ToString()=="prepared","unrelated Helper context, input and prepared preview survive archive");
 Check(provider==0,"no provider, account, credentials or actual grants invoked");Console.WriteLine("TOTAL "+count);return 0;
 }
}
'''.replace('FIELDS','\n'.join(fields)).replace('BODY',body)
(root/'Program.cs').write_text(code);(root/'probe.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>')
r=subprocess.run([os.environ.get('CONFECTORY_DOTNET','dotnet'),'run','--project',str(root/'probe.csproj'),'-c','Release','--',str(root/'fixture')],text=True,capture_output=True,timeout=120);print(r.stdout+r.stderr,end='');print('ARTIFACT '+str(root));sys.exit(r.returncode)
