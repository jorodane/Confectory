using Confectory.Core;
namespace Confectory.Tests;
public sealed class AIConnectionTests : TestCase
{
 public void test_codex_owned_stdio_protocol_fixture_without_installed_codex_authentication_or_external_network()
 {
 if(!OperatingSystem.IsLinux())Skip("Owned stdio fixture requires Linux /usr/bin/python3; installed Codex is never used");
 string sample=Path.Combine(f.Root,"connections");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","edit-workspace"),sample);
 string project=Path.Combine(sample,"project.cpack"),manifest=File.ReadAllText(project).Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack").Replace("../../packs/","../packs/");
 foreach(string name in new[]{"agent","ai-connection","agent-responses","agent-codex","development-tools","pack-workspace","file-stream","schema-editing","edit-workspace","save","change-set"}){Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",name),Path.Combine(f.Root,"packs",name));string pack=File.ReadAllText(Path.Combine(f.Root,"packs",name,"pack.cpack")).Split(" version ")[0].Replace("pack ","");if(!manifest.Contains("registry "+pack+" "))manifest=manifest.Replace("element Main function","registry "+pack+" \"../packs/"+name+"/pack.cpack\"; dependency "+pack+" version \"0.1.0\";\nelement Main function");}
 File.WriteAllText(Path.Combine(sample,"Counter.celem"),"object Example.EditWorkspace::Counter {value count = 0;}");manifest=manifest.Replace("element Main function","element Counter object \"Counter.celem\"; element Main function");File.WriteAllText(project,manifest);string main=Path.Combine(sample,"main.celem");File.WriteAllText(main,File.ReadAllText(main).Replace(" -> int {"," -> int {use object Confectory.Agent.Responses::Connection; use object Confectory.Agent.Codex::Connection;"));
 File.WriteAllText(Path.Combine(sample,"main_body.celem"),"""
 implementation Example.EditWorkspace::MainBody for Example.EditWorkspace::Main () -> int {
 import Confectory.Agent.Codex::ValidateConfig as Validate (string) -> string;
 import Confectory.Agent.Codex::Provider as Provider (string,string,string,string) -> string;
 import Confectory.DevelopmentTools::Open as ToolsOpen (string,string,string,string,string) -> string;
 import Confectory.DevelopmentTools::Snapshot as ToolsSnapshot (string) -> string;
 import Confectory.DevelopmentTools::Close as ToolsClose (string) -> void;
 import Confectory.PackWorkspace::Open as ViewOpen (string,string,string) -> string;
 import Confectory.PackWorkspace::Command as ViewCommand (string,string,string) -> string;
 import Confectory.PackWorkspace::Close as ViewClose (string) -> void;
 body common "main.csbody";}
 """);
 File.WriteAllText(Path.Combine(sample,"main.csbody"),"""""
 string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_CONNECTION_PROJECT")!,root=System.IO.Path.GetDirectoryName(project)!,fixture=System.IO.Path.Combine(root,"owned-codex-protocol.py");
 System.IO.File.WriteAllText(fixture,""""
#!/usr/bin/python3
import json,sys,time,os
assert sys.argv[1:]==['app-server']
assert os.environ.get("CODEX_HOME") and "OPENAI_API_KEY" not in os.environ and "HOME" not in os.environ
def read():
 x=json.loads(sys.stdin.readline())
 with open(os.path.join(os.path.dirname(__file__),'owned-requests.jsonl'),'a') as f:f.write(json.dumps(x)+'\n')
 return x
def send(x):print(json.dumps(x),flush=True)
a=read();assert a['method']=='initialize' and a['params']['capabilities']['experimentalApi'];send({'id':a['id'],'result':{'userAgent':'owned-fixture'}})
assert read()['method']=='initialized'
a=read();assert a['method']=='thread/start' and a['params']['ephemeral'] and a['params']['sandbox']=='read-only' and a['params']['approvalPolicy']=='never'
assert all(t['type']=='function' and 'inputSchema' in t for t in a['params']['dynamicTools'])
assert os.getcwd()==a['params']['cwd'];send({'id':a['id'],'result':{'thread':{'id':'owned-thread'}}})
a=read();assert a['method']=='turn/start' and a['params']['sandboxPolicy']=={'type':'readOnly','networkAccess':False}
text=a['params']['input'][0]['text'];assert 'authorization' not in text and 'toolCapability' not in text and 'credentialReference' not in text
mode=json.loads(text)['message'];send({'id':a['id'],'result':{'turn':{'id':'owned-turn','status':'inProgress'}}})
if mode=='cancel':
 b=read();assert b['method']=='turn/interrupt';open(os.path.join(os.path.dirname(__file__),'owned-interrupt-marker'),'w').write('owned-turn');sys.exit(0)
if mode=='foreign':
 send({'id':'foreign-request','method':'item/tool/call','params':{'threadId':'another-project','turnId':'owned-turn','callId':'foreign','tool':'workspace_stage','arguments':{}}});time.sleep(1);sys.exit(0)
if mode=='approval':
 send({'id':'native-request','method':'item/fileChange/requestApproval','params':{'threadId':'owned-thread','turnId':'owned-turn'}});b=read();assert b['id']=='native-request' and 'error' in b;sys.exit(0)
for n in range(2):
 send({'id':'rpc-'+str(n),'method':'item/tool/call','params':{'threadId':'owned-thread','turnId':'owned-turn','callId':'same-call','tool':'workspace_stage','arguments':{'projectId':'A','id':'Example.EditWorkspace::Counter','expectedRevision':0,'text':'object Example.EditWorkspace::Counter {value count = 3;}'}}})
 b=read();assert b['id']=='rpc-'+str(n) and b['result']['success'] and b['result']['contentItems'][0]['type']=='inputText'
 if n==0:first=b['result']
 else:assert b['result']==first
send({'method':'item/completed','params':{'threadId':'owned-thread','turnId':'owned-turn','item':{'id':'answer','type':'agentMessage','text':'Owned fixture staged draft; review required.'}}})
send({'method':'turn/completed','params':{'threadId':'owned-thread','turn':{'id':'owned-turn','status':'completed'}}})
read()
"""");
 System.IO.File.SetUnixFileMode(fixture,System.IO.UnixFileMode.UserRead|System.IO.UnixFileMode.UserWrite|System.IO.UnixFileMode.UserExecute);
 string managedHome=System.IO.Path.Combine(root,"owned-managed-home");System.IO.Directory.CreateDirectory(managedHome);string config=new System.Text.Json.Nodes.JsonObject{["managedHome"]=managedHome,["provider"]="codex",["protocol"]="app-server-stdio",["executable"]=fixture,["model"]="owned-protocol-fixture",["credentialReference"]="codex:managed"}.ToJsonString();
 var checkedConfig=System.Text.Json.Nodes.JsonNode.Parse(calls.Validate.Invoke(config))!;if(checkedConfig["processStarted"]!.GetValue<bool>()||checkedConfig["credentialRead"]!.GetValue<bool>())throw new Exception("Validation started process or read credentials");
 string rejected=Guid.NewGuid().ToString("N");try{bool denied=false;try{calls.Provider.Invoke(config,rejected,"open","{}");}catch(UnauthorizedAccessException){denied=true;}if(!denied)throw new Exception("Missing grant accepted");}finally{calls.Provider.Invoke(config,rejected,"close","");}
 string capability=calls.ToolsOpen.Invoke(project,"A","Example.EditWorkspace","alice","editor"),original=System.IO.File.ReadAllText(System.IO.Path.Combine(root,"Counter.celem"));
 string Request(string mode)=>new System.Text.Json.Nodes.JsonObject{["message"]=mode,["toolCapability"]=capability,["context"]=new System.Text.Json.Nodes.JsonObject{["projectId"]="A"},["authorization"]=new System.Text.Json.Nodes.JsonObject{["projectId"]="A",["executable"]=fixture,["model"]="owned-protocol-fixture",["contentApproved"]=true,["usageApproved"]=true,["processApproved"]=true,["managedCredentialApproved"]=true,["managedConfigurationApproved"]=true,["managedStorageApproved"]=true,["managedHome"]=managedHome,["protocolVerified"]=true}}.ToJsonString();
 try{
 foreach(string mode in new[]{"normal","foreign","approval","cancel"}){
 string execution=Guid.NewGuid().ToString("N");try{calls.Provider.Invoke(config,execution,"open",Request(mode));if(mode=="cancel"){System.Threading.Thread.Sleep(150);calls.Provider.Invoke(config,execution,"cancel","");}string terminal="",text="";for(int n=0;n<1000;n++){var item=System.Text.Json.Nodes.JsonNode.Parse(calls.Provider.Invoke(config,execution,"next",""))!;string kind=item["kind"]!.ToString();if(kind=="delta")text+=item["text"]!.ToString();if(kind is "error" or "completed"){terminal=kind;break;}System.Threading.Thread.Sleep(5);}if(terminal!=(mode=="normal"?"completed":"error")||mode=="normal"&&!text.Contains("review required"))throw new Exception("Unexpected protocol outcome "+mode+" "+terminal);}finally{calls.Provider.Invoke(config,execution,"close","");calls.Provider.Invoke(config,execution,"close","");}if(mode=="cancel"&&!System.IO.File.Exists(System.IO.Path.Combine(root,"owned-interrupt-marker")))throw new Exception("Cancellation did not send scoped turn interrupt");}
 if(System.IO.File.ReadAllText(System.IO.Path.Combine(root,"Counter.celem"))!=original||System.Text.Json.Nodes.JsonNode.Parse(calls.ToolsSnapshot.Invoke(capability))!["staged"]!["Example.EditWorkspace::Counter"] is null)throw new Exception("Codex fixture bypassed draft boundary");
 string view=calls.ViewOpen.Invoke(project,"alice","editor");try{calls.ViewCommand.Invoke(view,"select","{\"id\":\"Example.EditWorkspace::Counter\"}");var reviewed=System.Text.Json.Nodes.JsonNode.Parse(calls.ViewCommand.Invoke(view,"review","{\"target\":\"portable\"}"))!["review"]!;if(reviewed["status"]!.ToString()!="ready"||System.IO.File.ReadAllText(System.IO.Path.Combine(root,"Counter.celem"))!=original)throw new Exception("Review changed final source");var applied=System.Text.Json.Nodes.JsonNode.Parse(calls.ViewCommand.Invoke(view,"confirm",new System.Text.Json.Nodes.JsonObject{["token"]=reviewed["token"]!.DeepClone()}.ToJsonString()))!;if(applied["confirmation"]![0]!.ToString()!="confirmed"||!System.IO.File.ReadAllText(System.IO.Path.Combine(root,"Counter.celem")).Contains("count = 3"))throw new Exception("Explicit consumer Confirm/build feedback failed");}finally{calls.ViewClose.Invoke(view);}
 }finally{calls.ToolsClose.Invoke(capability);}
 Console.WriteLine("Owned Codex stdio handshake / tool dedup / foreign scope / native approval refusal / cancellation PASS");return 0;
""""");
 string? oldProject=Environment.GetEnvironmentVariable("CONFECTORY_TEST_CONNECTION_PROJECT"),oldHost=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST");try{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets","element-authoring","bin","Release","net10.0","Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_CONNECTION_PROJECT",project);var first=new Builder(project,"portable").Build();var actual=Processes.Run(Strings(first,"run"),timeoutSeconds:120);Equal(0,actual.ExitCode);True(actual.Stdout.Contains("Owned Codex stdio handshake / tool dedup / foreign scope / native approval refusal / cancellation PASS"),actual.Stderr);if(Environment.GetEnvironmentVariable("CONFECTORY_CODEX_SCHEMA_DIRECTORY") is string schemaDirectory){var schemaCheck=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests","protocol","codex_installed_schema.py"),schemaDirectory,Path.Combine(sample,"owned-requests.jsonl")},timeoutSeconds:30);Equal(0,schemaCheck.ExitCode);True(schemaCheck.Stdout.Contains("Installed schema actual request capture PASS"),schemaCheck.Stdout+schemaCheck.Stderr);}new Builder(project,"windows").Build();new Builder(project,"android").Build();File.AppendAllText(Path.Combine(f.Root,"packs","agent-codex","Provider.csbody"),"\n// owning Codex transport locality\n");var changed=new Builder(project,"portable").Build();PackRebuilt(changed,new[]{"Confectory.Agent.Codex::AdapterBody"});Equal(0,Strings(changed,"statistics","compiledContracts").Length);}finally{Environment.SetEnvironmentVariable("CONFECTORY_TEST_CONNECTION_PROJECT",oldProject);Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",oldHost);}
 }
 public void test_declared_connection_settings_and_responses_approval_guards_without_external_network_or_credentials()
 {
 string sample=Path.Combine(f.Root,"connections");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","edit-workspace"),sample);
 string project=Path.Combine(sample,"project.cpack"),manifest=File.ReadAllText(project).Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack").Replace("../../packs/","../packs/");
 foreach(string name in new[]{"agent","ai-connection","agent-responses","agent-codex","development-tools","pack-workspace","file-stream","schema-editing","edit-workspace","save","change-set"}){Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",name),Path.Combine(f.Root,"packs",name));string pack=File.ReadAllText(Path.Combine(f.Root,"packs",name,"pack.cpack")).Split(" version ")[0].Replace("pack ","");if(!manifest.Contains("registry "+pack+" "))manifest=manifest.Replace("element Main function","registry "+pack+" \"../packs/"+name+"/pack.cpack\"; dependency "+pack+" version \"0.1.0\";\nelement Main function");}
 File.WriteAllText(Path.Combine(sample,"Counter.celem"),"object Example.EditWorkspace::Counter {value count = 0;}");manifest=manifest.Replace("element Main function","element Counter object \"Counter.celem\"; element Main function");File.WriteAllText(project,manifest);string main=Path.Combine(sample,"main.celem");File.WriteAllText(main,File.ReadAllText(main).Replace(" -> int {"," -> int {use object Confectory.Agent.Responses::Connection; use object Confectory.Agent.Codex::Connection;"));
 File.WriteAllText(Path.Combine(sample,"main_body.celem"),"""
 implementation Example.EditWorkspace::MainBody for Example.EditWorkspace::Main () -> int {
 import Confectory.AIConnection::ValidateReference as Reference (string) -> void;
 import Confectory.AIConnection::ValidateSettings as SettingsCheck (string) -> void;
 import Confectory.AIConnection::MaterializeMetadata as Materialize (string) -> string;
 import Confectory.AIConnection::Discover as Discover (string) -> string;
 import Confectory.AIConnection::SettingsSource as SettingsSource (string,string) -> string;
 import Confectory.Agent.Responses::ValidateConfig as Validate (string) -> string;
 import Confectory.Agent.Responses::Provider as Provider (string,string,string,string) -> string;
 import Confectory.DevelopmentTools::Open as ToolsOpen (string,string,string,string,string) -> string;
 import Confectory.DevelopmentTools::Snapshot as ToolsSnapshot (string) -> string;
 import Confectory.DevelopmentTools::Close as ToolsClose (string) -> void;
 import Confectory.PackWorkspace::Open as ViewOpen (string,string,string) -> string;
 import Confectory.PackWorkspace::Command as ViewCommand (string,string,string) -> string;
 import Confectory.PackWorkspace::Close as ViewClose (string) -> void;
 body common "main.csbody";}
 """);
 File.WriteAllText(Path.Combine(sample,"main.csbody"),"""
 string config="{\"provider\":\"responses\",\"protocol\":\"responses\",\"endpoint\":\"https://api.openai.com/v1/responses\",\"model\":\"explicit-model\",\"keyEnvironment\":\"CONFECTORY_AI_NOT_CONFIGURED\"}";
 var checkedConfig=System.Text.Json.Nodes.JsonNode.Parse(calls.Validate.Invoke(config))!;
 if(checkedConfig["networkContacted"]!.GetValue<bool>()||checkedConfig["credentialRead"]!.GetValue<bool>())throw new Exception("configuration performed IO");
 void Denied(Action action){try{action();}catch(ArgumentException){return;}catch(UnauthorizedAccessException){return;}throw new Exception("unsafe operation was accepted");}
 calls.Reference.Invoke("env:CONFECTORY_AI_NOT_CONFIGURED");calls.Reference.Invoke("codex:managed");calls.SettingsCheck.Invoke("object Example.EditWorkspace::Settings {data credentialReference = \"env:CONFECTORY_AI_NOT_CONFIGURED\";}");Denied(()=>calls.Reference.Invoke("literal-credential-must-be-denied"));Denied(()=>calls.SettingsCheck.Invoke("object Example.EditWorkspace::Settings {data credentialReference = \"literal-credential-must-be-denied\";}"));
 Denied(()=>calls.Validate.Invoke(config.Replace("https://api.openai.com/v1/responses","http://example.com/v1/responses")));
 Denied(()=>calls.Validate.Invoke(config.Replace("https://api.openai.com/v1/responses","https://user:secret@example.com/v1/responses")));
 Denied(()=>calls.Validate.Invoke(config.Replace("\"protocol\":","\"apiKey\":\"must-not-be-a-secret-field\",\"protocol\":")));
 string execution=Guid.NewGuid().ToString("N");try{Denied(()=>calls.Provider.Invoke(config,execution,"open","{}"));}finally{calls.Provider.Invoke(config,execution,"close","{}");}
 execution=Guid.NewGuid().ToString("N");try{Denied(()=>calls.Provider.Invoke(config,execution,"open","{\"authorization\":{\"projectId\":\"A\",\"contentApproved\":false}}"));}finally{calls.Provider.Invoke(config,execution,"close","{}");}
 // A local HTTP protocol fixture is not a model or live-provider validation.
 string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_CONNECTION_PROJECT")!;string projection=calls.Materialize.Invoke(System.IO.Path.Combine(System.IO.Path.GetDirectoryName(project)!,"owned-metadata"));var portableCatalogue=System.Text.Json.Nodes.JsonNode.Parse(calls.Discover.Invoke(projection))!;if(portableCatalogue["connections"]!.AsArray().Count!=2||!System.IO.File.ReadAllText(projection).Contains("standalone false")||System.IO.Directory.GetFiles(System.IO.Path.GetDirectoryName(projection)!,"*.csbody",System.IO.SearchOption.AllDirectories).Length!=0)throw new Exception("portable projection is metadata-only");var catalogue=System.Text.Json.Nodes.JsonNode.Parse(calls.Discover.Invoke(project))!;if(catalogue["connections"]!.AsArray().Count!=2||catalogue["bodyReads"]!.GetValue<int>()!=0)throw new Exception("declared catalogue must not read provider bodies");var declaredSettings=System.Text.Json.Nodes.JsonNode.Parse(calls.SettingsSource.Invoke(project,"Confectory.Agent.Codex::Connection"))!;if(!declaredSettings["source"]!.ToString().Contains("extends Confectory.Agent.Codex::Connection")||declaredSettings["credentialRead"]!.GetValue<bool>())throw new Exception("settings are declarations only");string capability=calls.ToolsOpen.Invoke(project,"A","Example.EditWorkspace","alice","editor");
 var listener=new System.Net.Sockets.TcpListener(System.Net.IPAddress.Loopback,0);listener.Start();int port=((System.Net.IPEndPoint)listener.LocalEndpoint).Port;var sent=new System.Collections.Generic.List<string>();
 var server=System.Threading.Tasks.Task.Run(()=>{for(int round=0;round<2;round++){using var client=listener.AcceptTcpClient();using var stream=client.GetStream();var header=new System.Text.StringBuilder();int c;while((c=stream.ReadByte())>=0){header.Append((char)c);if(header.ToString().EndsWith("\r\n\r\n",StringComparison.Ordinal))break;if(header.Length>16384)throw new Exception("header bound");}int length=int.Parse(System.Text.RegularExpressions.Regex.Match(header.ToString(),"Content-Length: ([0-9]+)",System.Text.RegularExpressions.RegexOptions.IgnoreCase).Groups[1].Value);var body=new byte[length];int offset=0;while(offset<length){int read=stream.Read(body,offset,length-offset);if(read==0)throw new Exception("short body");offset+=read;}sent.Add(System.Text.Encoding.UTF8.GetString(body));string response=round==0?new System.Text.Json.Nodes.JsonObject{["status"]="completed",["output"]=new System.Text.Json.Nodes.JsonArray(new System.Text.Json.Nodes.JsonObject{["type"]="function_call",["call_id"]="fixture-call",["name"]="workspace_stage",["arguments"]=new System.Text.Json.Nodes.JsonObject{["projectId"]="A",["id"]="Example.EditWorkspace::Counter",["expectedRevision"]=0,["text"]="object Example.EditWorkspace::Counter {value count = 2;}"}.ToJsonString()})}.ToJsonString():"{\"status\":\"completed\",\"output\":[{\"type\":\"message\",\"role\":\"assistant\",\"content\":[{\"type\":\"output_text\",\"text\":\"Fixture staged draft; user review required.\"}]}]}";byte[] bytes=System.Text.Encoding.UTF8.GetBytes(response),headers=System.Text.Encoding.ASCII.GetBytes("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: "+bytes.Length+"\r\nConnection: close\r\n\r\n");stream.Write(headers);stream.Write(bytes);}});
 string endpoint="http://127.0.0.1:"+port+"/v1/responses",localConfig=new System.Text.Json.Nodes.JsonObject{["provider"]="responses",["protocol"]="responses",["endpoint"]=endpoint,["model"]="protocol-fixture",["maxRounds"]=2}.ToJsonString();
 var input=new System.Text.Json.Nodes.JsonObject{["message"]="Owned protocol fixture only",["toolCapability"]=capability,["context"]=new System.Text.Json.Nodes.JsonObject{["projectId"]="A"},["authorization"]=new System.Text.Json.Nodes.JsonObject{["projectId"]="A",["contentApproved"]=true,["endpoint"]=endpoint,["model"]="protocol-fixture"}};
 execution=Guid.NewGuid().ToString("N");try{string original=System.IO.File.ReadAllText(System.IO.Path.Combine(System.IO.Path.GetDirectoryName(project)!,"Counter.celem"));calls.Provider.Invoke(localConfig,execution,"open",new System.Text.Json.Nodes.JsonObject{["kind"]="worker-task",["project"]="A",["ownerHelper"]="chief",["input"]=input}.ToJsonString());bool completed=false;string output="";for(int n=0;n<600;n++){var item=System.Text.Json.Nodes.JsonNode.Parse(calls.Provider.Invoke(localConfig,execution,"next","{}"))!;if(item["kind"]!.ToString()=="error")throw new Exception("protocol fixture failed");if(item["kind"]!.ToString()=="delta")output+=item["text"]!.ToString();if(item["kind"]!.ToString()=="completed"){completed=true;break;}System.Threading.Thread.Sleep(10);}if(!completed||!output.Contains("review required")||!server.Wait(3000))throw new Exception("transport rounds did not finish");if(sent.Count!=2||System.Linq.Enumerable.Any(sent,text=>text.Contains(capability)||text.Contains("authorization")||text.Contains("credentialReference")))throw new Exception("local capability or auth leaked");if(!sent[1].Contains("function_call_output")||System.IO.File.ReadAllText(System.IO.Path.Combine(System.IO.Path.GetDirectoryName(project)!,"Counter.celem"))!=original||System.Text.Json.Nodes.JsonNode.Parse(calls.ToolsSnapshot.Invoke(capability))!["staged"]!["Example.EditWorkspace::Counter"] is null)throw new Exception("tool roundtrip bypassed draft boundary");}finally{calls.Provider.Invoke(localConfig,execution,"close","{}");calls.ToolsClose.Invoke(capability);listener.Stop();}
 Console.WriteLine("Connection declarations / approval guards / local HTTP fixture / draft-only tool roundtrip PASS");return 0;
 """);
 string? oldProject=Environment.GetEnvironmentVariable("CONFECTORY_TEST_CONNECTION_PROJECT"),oldHost=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST");try{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets","element-authoring","bin","Release","net10.0","Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_CONNECTION_PROJECT",project);var built=new Builder(project,"portable").Build();Output(built,"Connection declarations / approval guards / local HTTP fixture / draft-only tool roundtrip PASS");File.AppendAllText(Path.Combine(f.Root,"packs","agent-responses","ValidateConfig.csbody"),"\n// connection configuration locality\n");var changed=new Builder(project,"portable").Build();PackRebuilt(changed,new[]{"Confectory.Agent.Responses::ValidateConfigBody"});Equal(0,Strings(changed,"statistics","compiledContracts").Length);File.AppendAllText(Path.Combine(f.Root,"packs","ai-connection","Discover.csbody"),"\n// owning connection discovery locality\n");var discovered=new Builder(project,"portable").Build();PackRebuilt(discovered,new[]{"Confectory.AIConnection::DiscoverBody"});Equal(0,Strings(discovered,"statistics","compiledContracts").Length);}finally{Environment.SetEnvironmentVariable("CONFECTORY_TEST_CONNECTION_PROJECT",oldProject);Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",oldHost);}
 }
}
