"""Shipped ledger body with fake verified account/owner contexts and real private files.
No installed CLI, credential, real account, model or user permission is touched.
"""
import os,pathlib,subprocess,sys,tempfile
repo=pathlib.Path(sys.argv[1]).resolve();root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-use-ledger-'))
(root/'probe.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>')
source=r'''
using System.Text.Json.Nodes;
class Probe {
 static class OperatingSystem {public static bool Windows;public static bool IsWindows()=>Windows;}
 class Calls {
  public int ToolCalls;
  public Func<string,string[]> Identity=_=>new[]{"","","","/tmp"};
  public Func<string,string[]> List;
  public Calls(){List=_=>{Interlocked.Increment(ref ToolCalls);return new[]{"Owned::One","Other::Secret"};};}
  public Func<string,string,string[]> Status=(_,id)=>new[]{id,"object","owned.celem","","1","","clean"};
  public Func<string,string,string[]> Read=(_,_)=>new[]{"","object","1","object Owned::One {}"};
  public Func<string,string,string,long,bool> Stage=(_,_,_,_)=>true;
  public Action<string,string,string> Create=(_,_,_)=>{};
  public Func<string,string[],string[]> Changes=(_,_)=>Array.Empty<string>();
  public Func<string,string> Inspect=_=>"{}";
  public Func<string,string[]> Snapshot=path=>File.Exists(path)?new[]{"exists",File.ReadAllText(path),Hash(File.ReadAllText(path))}:new[]{"missing","","missing"};
  public Func<string,string[],string[],string[],string[]> Commit=(root,paths,hashes,texts)=>{for(int n=0;n<paths.Length;n++){string path=Path.Combine(root,paths[n]);if((File.Exists(path)?Hash(File.ReadAllText(path)):"missing")!=hashes[n])return new[]{"conflict"};File.WriteAllText(path,texts[n]);}return new[]{"applied"};};
  public Func<string,string,string,string> Verification=(_,_,_)=>new JsonObject{["supported"]=true,["accountIdentity"]=new JsonObject{["fingerprint"]=new string('a',64)}}.ToJsonString();
  public Func<string,string> Definitions=_=>"[{\"name\":\"workspace_read\",\"description\":\"owned\",\"parameters\":{\"projectId\":\"owned\"}}]";
 }
 static string Hash(string value)=>Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(value))).ToLowerInvariant();
 static string Invoke(Calls calls,string session,string operation,string payload){BODY}
 static string InvokeTools(Calls calls,string capability,string callId,string operation,string arguments){TOOLSOURCE}
 static int Main(string[] args){
  OperatingSystem.Windows=args.Length>1&&args[1]=="windows";string root=args[0];Directory.CreateDirectory(root);var calls=new Calls();int checks=0;
  void Assert(bool ok){if(!ok)throw new Exception("ledger assertion "+checks);checks++;}
  string[] rights={"contentApproved","usageApproved","processApproved","managedCredentialApproved","managedConfigurationApproved","managedStorageApproved"};
  var config=new JsonObject{["connectionMethod"]="local-cli",["executable"]=Path.Combine(root,"owned-cli"),["managedHome"]=Path.Combine(root,"owned-home"),["credentialReference"]="codex:managed",["model"]="owned-model"};
  var binding=new JsonObject{["connection"]="Confectory.Agent.Codex::Connection",["config"]=config,["identity"]=new JsonObject{["fingerprint"]=new string('a',64)}};
  var registry=new JsonObject{["agents"]=new JsonObject{["Confectory.Agent.Codex::Connection"]=binding},["assignments"]=new JsonObject{["helper-a"]="Confectory.Agent.Codex::Connection"}};
  var helperContext=new JsonObject{["helper"]="helper-a",["projectId"]="project-a",["profile"]=new JsonObject{["personality"]="toy"},["memory"]=new JsonArray()};
  var preview=new JsonObject{["canStart"]=true,["kind"]="chat",["context"]="context-a",["helperContext"]=helperContext,["permissionPolicy"]=new JsonObject{["requirements"]=new JsonArray(rights.Select(id=>(JsonNode)new JsonObject{["id"]=id}).ToArray())}};
  var model=new JsonObject{["selected"]=new JsonObject{["context"]="context-a",["projectId"]="project-a",["path"]=Path.Combine(root,"first","SameName","project.cproj"),["namespace"]="Owned"},["aiPreview"]=preview,["helperSelections"]=new JsonObject{["project-a"]=new JsonObject{["helper"]="helper-a",["helpers"]=new JsonArray("helper-a"),["manifest"]=Path.Combine(root,"first","SameName","project.cproj"),["allowCommon"]=false}}};
  object[] Session(string id){var owner=new object[14];owner[2]=Path.Combine(root,"projects.json");owner[3]=model;owner[6]=false;owner[11]=new Dictionary<string,string>{{"context-a","owned-ai"}};AppDomain.CurrentDomain.SetData("Confectory.EditorHome."+id,owner);AppDomain.CurrentDomain.SetData("Confectory.EditorHome.HelperAgents."+id,new object[]{registry,null!,null!,new Dictionary<string,object[]>()});return owner;}
  Session("first");AppDomain.CurrentDomain.SetData("Confectory.ProjectAI.owned-ai",new object[]{new object(),null!,null!,null!,"owned-tools"});string session="first",input="{\"kind\":\"project\",\"helper\":\"helper-a\"}";
  JsonNode Call(string op,string? body=null)=>JsonNode.Parse(Invoke(calls,session,op,body??input))!;
  void Denied(string op,string? body=null){bool denied=false;try{Call(op,body);}catch(Exception e)when(e is UnauthorizedAccessException or ArgumentException or InvalidOperationException){denied=true;}Assert(denied);}
  string Accept(){var pending=Call("status");Assert(pending["state"]!.ToString()=="consent-required");string payload=new JsonObject{["kind"]="project",["helper"]="helper-a",["challenge"]=pending["challenge"]!.DeepClone()}.ToJsonString();Assert(Call("accept",payload)["state"]!.ToString()=="granted");return payload;}
  Denied("authorize");Assert(!File.Exists(Path.Combine(root,"chat-use-grants.json")));Denied("accept","{\"kind\":\"project\",\"challenge\":\"forged\"}");Denied("accept","{\"kind\":\"project\",\"approved\":true}");
  Accept();Assert(Call("status")["state"]!.ToString()=="granted");var issued=Call("authorize");var guard=(Action<Action>)((object[])AppDomain.CurrentDomain.GetData("Confectory.ChatUse.Guard."+issued["token"]!.ToString())!)[0];int performed=0;guard(()=>performed++);Assert(performed==1);
  if(OperatingSystem.Windows){string path=model["selected"]!["path"]!.ToString();model["selected"]!["path"]=path.ToUpperInvariant();model["helperSelections"]!["project-a"]!["manifest"]=path.ToUpperInvariant();Assert(Call("status")["state"]!.ToString()=="granted");model["selected"]!["path"]=path;model["helperSelections"]!["project-a"]!["manifest"]=path;}
  var readiness=calls.Verification;string savedReceipts=File.ReadAllText(Path.Combine(root,"chat-use-grants.json"));calls.Verification=(_,_,_)=>"{\"supported\":false,\"state\":\"stale\"}";Assert(Call("status")["state"]!.ToString()=="blocked");calls.Verification=readiness;Assert(Call("status")["state"]!.ToString()=="granted");Assert(savedReceipts==File.ReadAllText(Path.Combine(root,"chat-use-grants.json")));
  helperContext["memory"]!.AsArray().Add(new JsonObject{["scope"]="project",["text"]="new selected category content"});preview["message"]="different message";Assert(Call("status")["state"]!.ToString()=="granted");
  Session("restart");session="restart";Assert(Call("status")["state"]!.ToString()=="granted");
  model["helperSelections"]!["project-a"]!["allowCommon"]=true;Assert(Call("status")["state"]!.ToString()=="consent-required");model["helperSelections"]!["project-a"]!["allowCommon"]=false;Assert(Call("status")["state"]!.ToString()=="consent-required");Accept();
  var token=Call("authorize");var runtime=(object[])AppDomain.CurrentDomain.GetData("Confectory.ChatUse.Guard."+token["token"]!.ToString())!;guard=(Action<Action>)runtime[0];var entered=new ManualResetEventSlim();var release=new ManualResetEventSlim();var cancelled=new ManualResetEventSlim();((Action<Action>)runtime[1])(()=>cancelled.Set());
  string toolCapability="owned-tools";var toolModel=new JsonObject{["projectId"]="project-a",["namespace"]="Owned",["rights"]=new JsonArray("workspace_list"),["calls"]=new JsonObject(),["log"]=new JsonArray()};AppDomain.CurrentDomain.SetData("Confectory.DevelopmentTools."+toolCapability,new object[]{new object(),"", "owned-draft",toolModel,false});AppDomain.CurrentDomain.SetData("Confectory.DevelopmentTools.ChatUse."+toolCapability,guard);string toolArgs="{\"projectId\":\"project-a\"}";string visible=InvokeTools(calls,toolCapability,"before-revoke","workspace_list",toolArgs);Assert(visible.Contains("Owned::One")&&!visible.Contains("Other::Secret")&&calls.ToolCalls==1);
  var active=Task.Run(()=>guard(()=>{entered.Set();release.Wait();performed++;}));Assert(entered.Wait(5000));var revoke=Task.Run(()=>Call("revoke-context"));Assert(cancelled.Wait(5000));bool queuedDenied=false;var queued=Task.Run(()=>{try{InvokeTools(calls,toolCapability,"queued-after-revoke","workspace_list",toolArgs);}catch(UnauthorizedAccessException){queuedDenied=true;}});release.Set();Task.WaitAll(active,revoke,queued);Assert(queuedDenied&&performed==2&&calls.ToolCalls==1);bool futureDenied=false;try{InvokeTools(calls,toolCapability,"future-after-revoke","workspace_list",toolArgs);}catch(UnauthorizedAccessException){futureDenied=true;}Assert(futureDenied&&calls.ToolCalls==1);Denied("authorize");
  Accept();var beforeFailure=Call("authorize");var failureGuard=(Action<Action>)((object[])AppDomain.CurrentDomain.GetData("Confectory.ChatUse.Guard."+beforeFailure["token"]!.ToString())!)[0];var commit=calls.Commit;calls.Commit=(_,_,_,_)=>new[]{"conflict"};Denied("revoke-context");Denied("authorize");bool stoppedAfterFailure=false;try{failureGuard(()=>performed+=1000);}catch(UnauthorizedAccessException){stoppedAfterFailure=true;}Assert(stoppedAfterFailure&&performed==2);calls.Commit=commit;Assert(Call("status")["state"]!.ToString()=="consent-required");Accept();Assert(Call("status")["state"]!.ToString()=="granted");
  config["model"]="changed-model";Assert(Call("status")["state"]!.ToString()=="consent-required");config["model"]="owned-model";Assert(Call("status")["state"]!.ToString()=="consent-required");Accept();
  binding["identity"]!["fingerprint"]=new string('b',64);Assert(Call("status")["state"]!.ToString()=="blocked");binding["identity"]!["fingerprint"]=new string('a',64);
  preview["permissionPolicy"]!["requirements"]!.AsArray().Add(new JsonObject{["id"]="unknownRight"});Assert(Call("status")["state"]!.ToString()=="blocked");preview["permissionPolicy"]!["requirements"]!.AsArray().RemoveAt(6);
  ((Action)runtime[2])();Assert(AppDomain.CurrentDomain.GetData("Confectory.ChatUse.Guard."+token["token"]!.ToString()) is null);
  // A different project with the same display name/path suffix has no matching receipt.
  Accept();var selected=(JsonObject)model["selected"]!.DeepClone();model["selected"]!["projectId"]="project-b";model["selected"]!["path"]=Path.Combine(root,"second","SameName","project.cproj");helperContext["projectId"]="project-b";model["helperSelections"]!["project-b"]=new JsonObject{["helper"]="helper-a",["helpers"]=new JsonArray("helper-a"),["manifest"]=model["selected"]!["path"]!.DeepClone(),["allowCommon"]=false};Assert(Call("status")["state"]!.ToString()=="consent-required");model["selected"]=selected;helperContext["projectId"]="project-a";Assert(Call("status")["state"]!.ToString()=="granted");
  // Global conversations cannot reuse a project's scope and never include its tools.
  model["globalHelperPreview"]=new JsonObject{["helper"]="helper-a",["canStart"]=true,["context"]=new JsonObject{["helper"]="helper-a",["projectId"]="",["membership"]=new JsonObject{["kind"]="global"},["conversationId"]=new string('c',32)},["policy"]=preview["permissionPolicy"]!.DeepClone()};var hs=(object[])AppDomain.CurrentDomain.GetData("Confectory.EditorHome.HelperAgents."+session)!;((Dictionary<string,object[]>)hs[3])["helper-a"]=new object[]{new JsonObject{["includeCommon"]=false}};string globalInput="{\"kind\":\"global\",\"helper\":\"helper-a\"}";
  var globalPending=Call("status",globalInput);Assert(globalPending["state"]!.ToString()=="consent-required");Assert(globalPending["draftTools"]!.GetValue<bool>()==false);Assert(Call("accept",new JsonObject{["kind"]="global",["helper"]="helper-a",["challenge"]=globalPending["challenge"]!.DeepClone()}.ToJsonString())["state"]!.ToString()=="granted");Assert(Call("status",globalInput)["state"]!.ToString()=="granted");Assert(Call("status")["state"]!.ToString()=="granted");
  string file=Path.Combine(root,"chat-use-grants.json"),original=File.ReadAllText(file);File.WriteAllText(file,original.Replace("owned-model","tampered-model"));Denied("status");File.WriteAllText(file,original);
  if(!System.OperatingSystem.IsWindows()){string ledger=Path.Combine(root,"chat-use-grants.json"),aside=ledger+".owned";File.Move(ledger,aside);File.CreateSymbolicLink(ledger,aside);Denied("status");File.Delete(ledger);File.Move(aside,ledger);}
  var beforeClose=Call("authorize");var closing=(object[])AppDomain.CurrentDomain.GetData("Confectory.ChatUse.Guard."+beforeClose["token"]!.ToString())!;var stopped=new ManualResetEventSlim();((Action<Action>)closing[1])(()=>stopped.Set());Call("close");Assert(stopped.IsSet);Assert(AppDomain.CurrentDomain.GetData("Confectory.ChatUse.Guard."+beforeClose["token"]!.ToString()) is null);Assert(Call("status")["state"]!.ToString()=="granted");
  Console.WriteLine($"PASS {checks} owned ledger cases: first/next/restart/categories/material model change/revoke queue race/client forgery/corruption; no real user consent");return 0;
 }
}
'''.replace('BODY',(repo/'packs/editor-home-model/ChatUse.csbody').read_text()).replace('TOOLSOURCE',(repo/'packs/development-tools/Invoke.csbody').read_text())
(root/'Program.cs').write_text(source)
for mode in ('native-policy','windows-policy'):
 r=subprocess.run([os.environ.get('CONFECTORY_DOTNET','dotnet'),'run','--project',str(root/'probe.csproj'),'-c','Release','--',str(root/mode),*(['windows'] if mode=='windows-policy' else [])],capture_output=True,text=True,timeout=90);print(mode+' '+r.stdout+r.stderr,end='')
 if r.returncode:print('ARTIFACT '+str(root));sys.exit(r.returncode)
print('ARTIFACT '+str(root))
