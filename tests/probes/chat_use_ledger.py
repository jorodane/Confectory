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
  public Func<string,string> Schema=Describe;
  public Func<string,string> Permission=_=>new JsonObject{["requirements"]=new JsonArray(new[]{"contentApproved","usageApproved","processApproved","managedCredentialApproved","managedConfigurationApproved","managedStorageApproved"}.Select(id=>(JsonNode)new JsonObject{["id"]=id}).ToArray())}.ToJsonString();
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
  public Func<string,string,string,string> Verification=(_,_,_)=>new JsonObject{["supported"]=true,["verificationFingerprint"]=new string('d',64),["accountIdentity"]=new JsonObject{["fingerprint"]=new string('a',64)}}.ToJsonString();
  public Func<string,string> Definitions=_=>"[{\"name\":\"workspace_read\",\"description\":\"owned\",\"parameters\":{\"projectId\":\"owned\"}}]";
 }
 static string Hash(string value)=>Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(value))).ToLowerInvariant();
 static string Invoke(Calls calls,string session,string operation,string payload){BODY}
 static string Describe(string scope){SCHEMASOURCE}
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
  const string agentInput="{\"agent\":\"Confectory.Agent.Codex::Connection\"}";
  void AcceptAgent(){var pending=Call("agent-status",agentInput);if(pending["state"]!.ToString()=="granted")return;Assert(pending["state"]!.ToString()=="consent-required"&&pending["level"]!.ToString()=="agent");Assert(Call("agent-accept",new JsonObject{["agent"]="Confectory.Agent.Codex::Connection",["challenge"]=pending["challenge"]!.DeepClone()}.ToJsonString())["state"]!.ToString()=="granted");}
  string Accept(){AcceptAgent();var pending=Call("status");Assert(pending["state"]!.ToString()=="consent-required");string payload=new JsonObject{["kind"]="project",["helper"]="helper-a",["challenge"]=pending["challenge"]!.DeepClone()}.ToJsonString();Assert(Call("accept",payload)["state"]!.ToString()=="granted");return payload;}
  Denied("authorize");Assert(!File.Exists(Path.Combine(root,"chat-use-grants.json")));Denied("accept","{\"kind\":\"project\",\"challenge\":\"forged\"}");Denied("accept","{\"kind\":\"project\",\"approved\":true}");
  // A readiness/registered binding does not mint common consent or context consent.
  Assert(Call("status")["state"]!.ToString()=="agent-consent-required");
  Denied("agent-accept","{\"agent\":\"Confectory.Agent.Codex::Connection\",\"challenge\":\"forged\"}");
  var commonPending=Call("agent-status",agentInput);Assert(commonPending["level"]!.ToString()=="agent"&&!File.Exists(Path.Combine(root,"chat-use-grants.json")));
  // Preserve an exact old combined receipt as historical evidence, never promote it.
  JsonNode? Stable(JsonNode? n){if(n is JsonObject o){var sorted=new JsonObject();foreach(var item in o.OrderBy(p=>p.Key,StringComparer.Ordinal))sorted[item.Key]=Stable(item.Value);return sorted;}if(n is JsonArray a)return new JsonArray(a.Select(Stable).ToArray());return n?.DeepClone();}
  string Digest(JsonNode n)=>Hash(Stable(n)!.ToJsonString());
  var oldBasis=new JsonObject{["version"]=1,["policy"]="codex-chat-use-v1",["agent"]="Confectory.Agent.Codex::Connection",["context"]=new JsonObject{["kind"]="project",["helper"]="old-helper"}};
  var old=new JsonObject{["id"]=Guid.NewGuid().ToString("N"),["basis"]=oldBasis,["scope"]=Digest(oldBasis),["audience"]=Digest(oldBasis["context"]!),["acceptedAt"]=DateTimeOffset.UtcNow.ToString("O"),["revision"]=1L,["state"]="active"};old["checksum"]=Digest(old);string oldId=old["id"]!.ToString();
  File.WriteAllText(Path.Combine(root,"chat-use-grants.json"),new JsonObject{["version"]=1,["revision"]=1L,["grants"]=new JsonArray(old)}.ToJsonString());
  Denied("agent-accept",new JsonObject{["agent"]="Confectory.Agent.Codex::Connection",["challenge"]=commonPending["challenge"]!.DeepClone()}.ToJsonString());
  Assert(Call("agent-status",agentInput)["state"]!.ToString()=="consent-required");Assert(Call("status")["state"]!.ToString()=="agent-consent-required");
  AcceptAgent();Assert(Call("status")["state"]!.ToString()=="consent-required");Denied("authorize");
  var stored=JsonNode.Parse(File.ReadAllText(Path.Combine(root,"chat-use-grants.json")))!;Assert(stored["version"]!.GetValue<int>()==2&&stored["grants"]!.AsArray().Any(r=>r!["id"]!.ToString()==oldId&&r["state"]!.ToString()=="active"));
  Accept();Assert(Call("status")["state"]!.ToString()=="granted");var issued=Call("authorize");var guard=(Action<Action>)((object[])AppDomain.CurrentDomain.GetData("Confectory.ChatUse.Guard."+issued["token"]!.ToString())!)[0];int performed=0;guard(()=>performed++);Assert(performed==1);
  // A second Helper shares only the Agent common receipt; its context must be explicit.
  registry["assignments"]!["helper-b"]="Confectory.Agent.Codex::Connection";model["helperSelections"]!["project-a"]!["helpers"]!.AsArray().Add("helper-b");helperContext["helper"]="helper-b";
  Assert(Call("agent-status",agentInput)["state"]!.ToString()=="granted");Assert(Call("status","{\"kind\":\"project\",\"helper\":\"helper-b\"}")["state"]!.ToString()=="consent-required");
  var bp=Call("status","{\"kind\":\"project\",\"helper\":\"helper-b\"}");Assert(Call("accept",new JsonObject{["kind"]="project",["helper"]="helper-b",["challenge"]=bp["challenge"]!.DeepClone()}.ToJsonString())["state"]!.ToString()=="granted");
  helperContext["helper"]="helper-a";Assert(Call("status")["state"]!.ToString()=="granted");
  // Context and common challenges cannot substitute for each other.
  Denied("agent-accept",new JsonObject{["agent"]="Confectory.Agent.Codex::Connection",["challenge"]=bp["challenge"]!.DeepClone()}.ToJsonString());Denied("agent-status","{\"agent\":\"Confectory.Agent.Responses::Connection\"}");
  var proof=calls.Verification;calls.Verification=(_,_,_)=>new JsonObject{["supported"]=true,["verificationId"]=Guid.NewGuid().ToString("N"),["expires"]=DateTime.UtcNow.AddMinutes(10),["verificationFingerprint"]=new string('d',64),["accountIdentity"]=new JsonObject{["fingerprint"]=new string('a',64)}}.ToJsonString();Assert(Call("agent-status",agentInput)["state"]!.ToString()=="granted");Assert(Call("status")["state"]!.ToString()=="granted");calls.Verification=proof;

  if(OperatingSystem.Windows){string path=model["selected"]!["path"]!.ToString();model["selected"]!["path"]=path.ToUpperInvariant();Assert(Call("status")["state"]!.ToString()=="granted");model["helperSelections"]!["project-a"]!["manifest"]=path.ToUpperInvariant();Assert(Call("status")["state"]!.ToString()=="granted");model["selected"]!["path"]=path;model["helperSelections"]!["project-a"]!["manifest"]=path;}
  var readiness=calls.Verification;string savedReceipts=File.ReadAllText(Path.Combine(root,"chat-use-grants.json"));calls.Verification=(_,_,_)=>"{\"supported\":false,\"state\":\"stale\"}";Assert(Call("status")["state"]!.ToString()=="blocked");calls.Verification=readiness;Assert(Call("status")["state"]!.ToString()=="granted");Assert(savedReceipts==File.ReadAllText(Path.Combine(root,"chat-use-grants.json")));
  helperContext["memory"]!.AsArray().Add(new JsonObject{["scope"]="project",["text"]="new selected category content"});preview["message"]="different message";Assert(Call("status")["state"]!.ToString()=="granted");
  Session("restart");session="restart";Assert(Call("status")["state"]!.ToString()=="granted");
  model["helperSelections"]!["project-a"]!["allowCommon"]=true;Assert(Call("status")["state"]!.ToString()=="consent-required");model["helperSelections"]!["project-a"]!["allowCommon"]=false;Assert(Call("status")["state"]!.ToString()=="consent-required");Accept();
  var token=Call("authorize");var runtime=(object[])AppDomain.CurrentDomain.GetData("Confectory.ChatUse.Guard."+token["token"]!.ToString())!;guard=(Action<Action>)runtime[0];var entered=new ManualResetEventSlim();var release=new ManualResetEventSlim();var cancelled=new ManualResetEventSlim();((Action<Action>)runtime[1])(()=>cancelled.Set());
  string toolCapability="owned-tools";var toolModel=new JsonObject{["projectId"]="project-a",["namespace"]="Owned",["rights"]=new JsonArray("workspace_list"),["calls"]=new JsonObject(),["log"]=new JsonArray()};AppDomain.CurrentDomain.SetData("Confectory.DevelopmentTools."+toolCapability,new object[]{new object(),"", "owned-draft",toolModel,false});AppDomain.CurrentDomain.SetData("Confectory.DevelopmentTools.ChatUse."+toolCapability,guard);string toolArgs="{\"projectId\":\"project-a\"}";string visible=InvokeTools(calls,toolCapability,"before-revoke","workspace_list",toolArgs);Assert(visible.Contains("Owned::One")&&!visible.Contains("Other::Secret")&&calls.ToolCalls==1);
  var active=Task.Run(()=>guard(()=>{entered.Set();release.Wait();performed++;}));Assert(entered.Wait(5000));var revoke=Task.Run(()=>Call("revoke-context"));Assert(cancelled.Wait(5000));bool queuedDenied=false;var queued=Task.Run(()=>{try{InvokeTools(calls,toolCapability,"queued-after-revoke","workspace_list",toolArgs);}catch(UnauthorizedAccessException){queuedDenied=true;}});release.Set();Task.WaitAll(active,revoke,queued);Assert(queuedDenied&&performed==2&&calls.ToolCalls==1);bool futureDenied=false;try{InvokeTools(calls,toolCapability,"future-after-revoke","workspace_list",toolArgs);}catch(UnauthorizedAccessException){futureDenied=true;}Assert(futureDenied&&calls.ToolCalls==1);Denied("authorize");
  Accept();var beforeFailure=Call("authorize");var failureGuard=(Action<Action>)((object[])AppDomain.CurrentDomain.GetData("Confectory.ChatUse.Guard."+beforeFailure["token"]!.ToString())!)[0];var commit=calls.Commit;calls.Commit=(_,_,_,_)=>new[]{"conflict"};Denied("revoke-context");Denied("authorize");bool stoppedAfterFailure=false;try{failureGuard(()=>performed+=1000);}catch(UnauthorizedAccessException){stoppedAfterFailure=true;}Assert(stoppedAfterFailure&&performed==2);calls.Commit=commit;Assert(Call("status")["state"]!.ToString()=="consent-required");Accept();Assert(Call("status")["state"]!.ToString()=="granted");
  config["model"]="changed-model";Assert(Call("status")["state"]!.ToString()=="agent-consent-required");config["model"]="owned-model";Assert(Call("status")["state"]!.ToString()=="agent-consent-required");Accept();
  binding["identity"]!["fingerprint"]=new string('b',64);Assert(Call("status")["state"]!.ToString()=="blocked");binding["identity"]!["fingerprint"]=new string('a',64);
  preview["permissionPolicy"]!["requirements"]!.AsArray().Add(new JsonObject{["id"]="unknownRight"});Assert(Call("status")["state"]!.ToString()=="blocked");preview["permissionPolicy"]!["requirements"]!.AsArray().RemoveAt(6);
  ((Action)runtime[2])();Assert(AppDomain.CurrentDomain.GetData("Confectory.ChatUse.Guard."+token["token"]!.ToString()) is null);
  // A different project with the same display name/path suffix has no matching receipt.
  Accept();var selected=(JsonObject)model["selected"]!.DeepClone();model["selected"]!["projectId"]="project-b";model["selected"]!["path"]=Path.Combine(root,"second","SameName","project.cproj");helperContext["projectId"]="project-b";model["helperSelections"]!["project-b"]=new JsonObject{["helper"]="helper-a",["helpers"]=new JsonArray("helper-a"),["manifest"]=model["selected"]!["path"]!.DeepClone(),["allowCommon"]=false};Assert(Call("status")["state"]!.ToString()=="consent-required");model["selected"]=selected;helperContext["projectId"]="project-a";Assert(Call("status")["state"]!.ToString()=="granted");
  // Global conversations cannot reuse a project's scope and never include its tools.
  model["globalHelperPreview"]=new JsonObject{["helper"]="helper-a",["canStart"]=true,["context"]=new JsonObject{["helper"]="helper-a",["projectId"]="",["membership"]=new JsonObject{["kind"]="global"},["conversationId"]=new string('c',32)},["policy"]=preview["permissionPolicy"]!.DeepClone()};var hs=(object[])AppDomain.CurrentDomain.GetData("Confectory.EditorHome.HelperAgents."+session)!;((Dictionary<string,object[]>)hs[3])["helper-a"]=new object[]{new JsonObject{["includeCommon"]=false}};string globalInput="{\"kind\":\"global\",\"helper\":\"helper-a\"}";
  string beforeGlobal=File.ReadAllText(Path.Combine(root,"chat-use-grants.json"));var globalReady=Call("status",globalInput);Assert(globalReady["state"]!.ToString()=="granted");Assert(Call("authorize",globalInput)["state"]!.ToString()=="granted");Assert(beforeGlobal==File.ReadAllText(Path.Combine(root,"chat-use-grants.json")));Denied("accept",globalInput);Assert(Call("status")["state"]!.ToString()=="granted");
  // A new owned Helper outside a project uses the same Agent grant immediately.
  registry["assignments"]!["helper-fff"]="Confectory.Agent.Codex::Connection";model["globalHelperPreview"]!["helper"]="helper-fff";model["globalHelperPreview"]!["context"]!["helper"]="helper-fff";((Dictionary<string,object[]>)hs[3])["helper-fff"]=new object[]{new JsonObject{["includeCommon"]=false}};string fff="{\"kind\":\"global\",\"helper\":\"helper-fff\"}";Assert(Call("status",fff)["state"]!.ToString()=="granted");Assert(Call("authorize",fff)["state"]!.ToString()=="granted");Assert(beforeGlobal==File.ReadAllText(Path.Combine(root,"chat-use-grants.json")));model["globalHelperPreview"]!["helper"]="helper-a";model["globalHelperPreview"]!["context"]!["helper"]="helper-a";
  // Context removal and unexpected final-write/exec tools fail closed, never acquire rights.
  var choice=model["helperSelections"]!["project-a"]!.DeepClone();model["helperSelections"]!.AsObject().Remove("project-a");Denied("status");model["helperSelections"]!["project-a"]=choice;
  var definitions=calls.Definitions;calls.Definitions=_=>"[{\"name\":\"workspace_confirm\"}]";Assert(Call("status")["code"]!.ToString()=="chat-use-new-tool-scope");Assert(Call("authorize")["state"]!.ToString()=="blocked");Assert(Call("agent-status",agentInput)["state"]!.ToString()=="granted");calls.Definitions=definitions;Accept();
  var globalContext=model["globalHelperPreview"]!["context"]!;globalContext["projectId"]="project-a";Denied("status",globalInput);globalContext["projectId"]="";
  // Agent revoke stops every outstanding context ticket, without changing account or files.
  var projectTicket=Call("authorize");var globalTicket=Call("authorize",globalInput);var projectGuard=(object[])AppDomain.CurrentDomain.GetData("Confectory.ChatUse.Guard."+projectTicket["token"]!.ToString())!;var globalGuard=(object[])AppDomain.CurrentDomain.GetData("Confectory.ChatUse.Guard."+globalTicket["token"]!.ToString())!;int cancelledContexts=0;((Action<Action>)projectGuard[1])(()=>Interlocked.Increment(ref cancelledContexts));((Action<Action>)globalGuard[1])(()=>Interlocked.Increment(ref cancelledContexts));
  calls.Commit=(_,_,_,_)=>new[]{"conflict"};Denied("revoke-agent",agentInput);Assert(cancelledContexts==2);Denied("authorize");foreach(var g in new[]{projectGuard,globalGuard}){bool denied=false;try{((Action<Action>)g[0])(()=>throw new Exception("must not execute"));}catch(UnauthorizedAccessException){denied=true;}Assert(denied);}calls.Commit=commit;Assert(Call("status")["state"]!.ToString()=="agent-consent-required");Accept();
  // Material effective configuration change invalidates common use, benign lease IDs do not.
  calls.Verification=(_,_,_)=>new JsonObject{["supported"]=true,["verificationFingerprint"]=new string('e',64),["accountIdentity"]=new JsonObject{["fingerprint"]=new string('a',64)}}.ToJsonString();Assert(Call("agent-status",agentInput)["state"]!.ToString()=="consent-required");calls.Verification=proof;Assert(Call("agent-status",agentInput)["state"]!.ToString()=="consent-required");Accept();
  string file=Path.Combine(root,"chat-use-grants.json"),original=File.ReadAllText(file);File.WriteAllText(file,original.Replace("owned-model","tampered-model"));Denied("status");File.WriteAllText(file,original);
  if(!System.OperatingSystem.IsWindows()){string ledger=Path.Combine(root,"chat-use-grants.json"),aside=ledger+".owned";File.Move(ledger,aside);File.CreateSymbolicLink(ledger,aside);Denied("status");File.Delete(ledger);File.Move(aside,ledger);}
  // Placement uses the same pure tool schema as the real chat capability, no turn required.
  Denied("placement-accept");var priorDefinitions=calls.Definitions;calls.Definitions=_=>Describe(new JsonObject{["projectId"]="project-a",["rights"]=new JsonArray("workspace_list","workspace_read","workspace_inspect","workspace_stage","workspace_create","workspace_changes")}.ToJsonString());
  model["helperPlacementApply"]=new JsonObject{["helper"]="helper-a",["context"]="context-a"};var placement=Call("placement-status");Assert(placement["state"]!.ToString()=="consent-required");Assert(Call("placement-accept",new JsonObject{["kind"]="project",["helper"]="helper-a",["challenge"]=placement["challenge"]!.DeepClone()}.ToJsonString())["state"]!.ToString()=="granted");model["helperPlacementApply"]=null;Assert(Call("status")["state"]!.ToString()=="granted");Assert(Call("authorize")["state"]!.ToString()=="granted");Denied("placement-status");calls.Definitions=priorDefinitions;Accept();
  var beforeClose=Call("authorize");var closing=(object[])AppDomain.CurrentDomain.GetData("Confectory.ChatUse.Guard."+beforeClose["token"]!.ToString())!;var stopped=new ManualResetEventSlim();((Action<Action>)closing[1])(()=>stopped.Set());Call("close");Assert(stopped.IsSet);Assert(AppDomain.CurrentDomain.GetData("Confectory.ChatUse.Guard."+beforeClose["token"]!.ToString()) is null);Assert(Call("status")["state"]!.ToString()=="granted");
  Console.WriteLine($"PASS {checks} owned two-receipt cases: legacy preserved/no promotion/Agent-only global/new fff/two Helpers/project scope/lease renewal/material change/Agent+context revoke/CAS queue race/client forgery; no real user consent");return 0;
 }
}
'''.replace('BODY',(repo/'packs/editor-home-model/ChatUse.csbody').read_text()).replace('TOOLSOURCE',(repo/'packs/development-tools/Invoke.csbody').read_text()).replace('SCHEMASOURCE',(repo/'packs/development-tools/Schema.csbody').read_text())
(root/'Program.cs').write_text(source)
for mode in ('native-policy','windows-policy'):
 r=subprocess.run([os.environ.get('CONFECTORY_DOTNET','dotnet'),'run','--project',str(root/'probe.csproj'),'-c','Release','--',str(root/mode),*(['windows'] if mode=='windows-policy' else [])],capture_output=True,text=True,timeout=90);print(mode+' '+r.stdout+r.stderr,end='')
 if r.returncode:print('ARTIFACT '+str(root));sys.exit(r.returncode)
print('ARTIFACT '+str(root))
