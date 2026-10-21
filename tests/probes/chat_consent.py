"""Compile the shipped authorization body and exercise explicit six-right consent.
No accounts, processes, network provider or persistent grant is created.
"""
import os,pathlib,subprocess,sys,tempfile
repo=pathlib.Path(sys.argv[1]).resolve();root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-chat-consent-'))
(root/'probe.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>')
source=r'''
using System.Text.Json.Nodes;
class Probe {
 static string Authorize(string policy,string projectId,string approvals){BODY}
 static int Main(){
  string[] ids={"contentApproved","usageApproved","processApproved","managedCredentialApproved","managedConfigurationApproved","managedStorageApproved"};
  var policy=new JsonObject{["supported"]=true,["pins"]=new JsonObject{["model"]="owned"},["requirements"]=new JsonArray(ids.Select(id=>(JsonNode)new JsonObject{["id"]=id}).ToArray())};
  var choices=new JsonObject();foreach(string id in ids)choices[id]=true;int checks=0;
  void Denied(JsonObject p,JsonObject c,string project="owned-project"){
   bool denied=false;try{Authorize(p.ToJsonString(),project,c.ToJsonString());}catch(Exception e)when(e is ArgumentException or UnauthorizedAccessException or PlatformNotSupportedException){denied=true;}
   if(!denied)throw new Exception("Consent guard accepted a forbidden grant");checks++;
  }
  var granted=JsonNode.Parse(Authorize(policy.ToJsonString(),"owned-project",choices.ToJsonString()))!;
  if(ids.Any(id=>granted[id]?.GetValue<bool>()!=true)||granted["projectId"]?.ToString()!="owned-project")throw new Exception("Exact scope/rights lost");checks++;
  foreach(string id in ids){var missing=(JsonObject)choices.DeepClone();missing.Remove(id);Denied(policy,missing);var refused=(JsonObject)choices.DeepClone();refused[id]=false;Denied(policy,refused);}
  var unknown=(JsonObject)choices.DeepClone();unknown["unexpectedApproved"]=true;Denied(policy,unknown);
  var additional=(JsonObject)policy.DeepClone();additional["requirements"]!.AsArray().Add(new JsonObject{["id"]="additionalApproved"});Denied(additional,choices);
  var unsupported=(JsonObject)policy.DeepClone();unsupported["supported"]=false;Denied(unsupported,choices);
  var preapproved=(JsonObject)policy.DeepClone();preapproved["pins"]![ids[0]]=true;Denied(preapproved,choices);
  Denied(policy,new JsonObject());Denied(policy,choices,"");Denied(policy,choices," ");
  var global=(JsonObject)policy.DeepClone();global["contentScope"]=new JsonObject{["kind"]="helper-global",["helperId"]="owned-helper",["conversationId"]=new string('a',32)};
  Denied(global,choices);var globalGrant=JsonNode.Parse(Authorize(global.ToJsonString(),"",choices.ToJsonString()))!;if(globalGrant["projectId"]!.ToString()!=""||!JsonNode.DeepEquals(globalGrant["contentScope"],global["contentScope"]))throw new Exception("Global scope lost");checks++;
  var badScope=(JsonObject)global.DeepClone();badScope["contentScope"]!["conversationId"]="invalid";Denied(badScope,choices,"");
  if(policy["pins"]!.AsObject().ContainsKey(ids[0])||policy.ContainsKey("projectId"))throw new Exception("Policy mutated into a retained grant");checks++;
  Console.WriteLine($"PASS {checks} shipped authorization cases; all six explicit rights, unknown/unsupported/preapproval and project/global fences");return 0;
 }
}
'''.replace('BODY',(repo/'packs/ai-connection/Authorize.csbody').read_text())
(root/'Program.cs').write_text(source)
r=subprocess.run([os.environ.get('CONFECTORY_DOTNET','dotnet'),'run','--project',str(root/'probe.csproj'),'-c','Release'],capture_output=True,text=True,timeout=90);print(r.stdout+r.stderr,end='');print('ARTIFACT '+str(root));sys.exit(r.returncode)
