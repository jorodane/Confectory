"""Compile the actual SlotBatch body; verify the exact snapshot/hash gate.
Controlled dependencies only; the Chromium test supplies the real engine path.
"""
import os,sys,subprocess,tempfile
from pathlib import Path
repo=Path(sys.argv[1]).resolve()
with tempfile.TemporaryDirectory(prefix='cf-slot-context-proof-') as folder:
    root=Path(folder)
    (root/'probe.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Exe</OutputType><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>')
    body=(repo/'packs/edit-workspace/SlotBatch.csbody').read_text()
    source=r'''
using System.Text.Json.Nodes;
using System.Text;
using System.Security.Cryptography;
class Calls {
 public Func<string,string,string> Context=null!,Capture=null!,Metadata=null!;
 public Func<string,string,string,string,string,string[],long[],string[],string> Create=(a,b,c,d,e,f,g,h)=>throw new Exception("unexpected slot");
 public Func<string,string,string> Copy=(h,p)=>throw new Exception("unexpected copy");
}
class Program {
 static string Batch(string handle,string plans,Calls calls){ BODY }
 static string Hash(string text)=>Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(text))).ToLowerInvariant();
 static void Check(bool value,string message){if(!value)throw new Exception(message);}
 static int Main(){
  foreach(bool compact in new[]{false,true})foreach(var mode in new[]{"success","staged-resource","original-peer","checkpoint","external-hash","ordinary-fallback","retained-reference","detached-compact","string-fallback","string-proof","string-external","string-detached","string-detached-external","string-dirty","non-direct"}){
   if((mode is "retained-reference" or "detached-compact" or "string-detached" or "string-detached-external")&&!compact||mode=="non-direct"&&compact)continue;
   string handle=Guid.NewGuid().ToString("N"),key="Confectory.EditWorkspace."+handle,root=Path.Combine(Path.GetTempPath(),"cf-context-"+handle);
   Directory.CreateDirectory(root);string project=Path.Combine(root,"project.cpack"),dep=Path.Combine(root,"dependency.cpack"),owner="Owned::Owner",manifest="Owned::ProjectManifest";
   File.WriteAllText(dep,"registered context");
   var units=new JsonObject();
   foreach(var id in new[]{owner,manifest,"Owned::Schema","Owned::Peer"})units[id]=new JsonObject{["kind"]=id==manifest?"project":id.EndsWith("Schema")?"schema":"object",["path"]=id.Split("::")[1]+".celem",["draft"]=id,["original"]=id,["revision"]=1L,["baseline"]=Hash(id)};
   if(mode is "retained-reference" or "string-dirty")units["Owned::Peer"]!["draft"]="retained prior draft";
   var state=new JsonObject{["root"]=root,["project"]=project,["namespace"]="Owned",["units"]=units};AppDomain.CurrentDomain.SetData(key,state);
   var original=units.DeepClone();
   var observations=new JsonArray(new JsonObject{["path"]=dep,["hash"]=Hash("registered context")});
   var context=new JsonObject{["compactClean"]=compact,["owner"]=owner,["guards"]=units.DeepClone(),["checkpointHash"]="checkpoint",["observations"]=observations.DeepClone(),["requirements"]=new JsonArray(),["providers"]=new JsonArray(),["ownFunctions"]=new JsonArray()};
   var declaration=new JsonObject{["id"]=owner,["hash"]=Hash(owner),["changes"]=new JsonArray(new JsonObject{["type"]="data",["path"]=new JsonArray("Phase"),["contract"]=new JsonObject{["kind"]="general",["cardinality"]="single",["type"]="long"},["valueJson"]="6000"})};
   var plans=new JsonArray(new JsonObject{["kind"]="owner-edit",["id"]=owner,["function"]=owner,["context"]=context.DeepClone(),["declaration"]=declaration,["directPropertySave"]=true});
   if(mode is "detached-compact" or "string-detached" or "string-detached-external")plans[0]!["uiSurface"]="view:1";
   if(mode is "string-fallback" or "string-proof" or "string-external" or "string-detached" or "string-detached-external" or "string-dirty"){declaration["changes"]![0]!["contract"]!["type"]="string";declaration["changes"]![0]!["valueJson"]="\"hello\"";}
   if(mode=="non-direct")plans[0]!["directPropertySave"]=false;
   int callsContext=0,captures=0,mixed=0,effective=0,inspect=0;
   var calls=new Calls {
    Context=(h,o)=>{callsContext++;return context.ToJsonString();},
    Capture=(h,o)=>{
     captures++;var captured=((JsonObject)AppDomain.CurrentDomain.GetData("Confectory.EditWorkspace."+h)!)["units"]!.DeepClone();
     if(mode=="staged-resource"&&h!=handle)captured["Owned::Owner/body:linux"]=new JsonObject{["kind"]="body",["path"]="new-resource.csbody",["draft"]="changed"};
     if(mode=="original-peer"&&h==handle)captured["Owned::Peer"]!["draft"]="changed";
     if(mode is ("external-hash" or "string-external" or "string-detached-external")&&h==handle)File.WriteAllText(dep,"changed reference");
     return new JsonObject{["units"]=captured,["project"]=project,["namespace"]="Owned",["manifest"]=manifest,["checkpointHash"]=mode=="checkpoint"?"changed":"checkpoint"}.ToJsonString();
    },
    Metadata=(op,input)=>{
     if(op is "effective" or "inspectEffective"){
      var req=JsonNode.Parse(input)!;Check(req["project"]?.ToString()==project&&req["id"]?.ToString()==owner&&req["text"]?.ToString()=="new owner"&&req["schemaView"]?.GetValue<bool>()==true&&req["validateObjects"]?.GetValue<bool>()==true&&req["observeSources"]?.GetValue<bool>()==true,"complete final validation flags");
      var model=new JsonObject{["status"]="available",["schemaModel"]=new JsonObject{["validation"]=new JsonObject{["status"]="valid"}}};
      if(op=="inspectEffective"){inspect++;Check(req["kind"]?.ToString()=="object","exact object identity");return new JsonObject{["effective"]=model}.ToJsonString();}
      effective++;return model.ToJsonString();
     }
     Check(op=="mixedOwnerCopyEdits","unexpected metadata "+op);mixed++;
     if(mode is "string-fallback" or "string-proof" or "string-external" or "string-detached" or "string-detached-external")Check(JsonNode.Parse(input)?["reuseStringPreparation"]?.GetValue<bool>()==true,"missing exact string proof request");
     var result=new JsonObject{["text"]="new owner",["manifest"]=manifest,["additions"]=new JsonArray(),["updates"]=new JsonArray()};
     if(mode=="string-dirty")Check(JsonNode.Parse(input)?["reuseStringPreparation"] is null,"dirty peer must not ask for proof");
     if(mode is not ("ordinary-fallback" or "string-fallback" or "string-dirty" or "non-direct"))result["repeatProof"]=new JsonObject{["observations"]=observations.DeepClone(),["ownershipPaths"]=new JsonArray(dep)};
     return result.ToJsonString();
    }
   };
   try{
    Exception? failure=null;try{Batch(handle,plans.ToJsonString(),calls);}catch(Exception ex){failure=ex;}
    bool success=mode is "string-proof" or "string-detached" or "string-dirty" or "success" or "ordinary-fallback" or "retained-reference" or "detached-compact" or "string-fallback" or "non-direct";
    Check(success?failure is null:failure is InvalidOperationException,mode+": "+failure);
    if(success)Check(state["units"]![owner]!["draft"]!.ToString()=="new owner","missing candidate");
    else Check(JsonNode.DeepEquals(original,state["units"]),"partial mutation");
    if(mode is "ordinary-fallback" or "string-fallback" or "string-dirty")Check(callsContext==3&&effective==1&&inspect==0&&mixed==2&&captures==0,"ordinary fallback checks lost");
    else if(mode=="non-direct")Check(callsContext==3&&effective==1&&inspect==0&&mixed==2&&captures==0,"non-direct exact path changed");
    else if(mode=="retained-reference")Check(callsContext==3&&effective==1&&inspect==0&&mixed==1&&captures==0,"retained draft must keep existing full context validation");
    else if(mode is "string-detached" or "string-detached-external")Check(callsContext==1&&effective==0&&inspect==0&&mixed==1&&captures>=1,"compact detached string must verify exact captured candidate and sources");
    else if(mode=="detached-compact")Check(callsContext==3&&effective==0&&inspect==1&&mixed==1&&captures==0,"compact detached proof must keep all semantic checks on the warm route");
    else Check(callsContext==1&&effective==0&&inspect==0&&mixed==1&&captures>=1,"expected one semantic context");
    Console.WriteLine("PASS "+mode+(compact?" compact":" ordinary"));
   }finally{AppDomain.CurrentDomain.SetData(key,null);Directory.Delete(root,true);}
  }
  return 0;
 }
}
'''.replace('BODY',body)
    (root/'Program.cs').write_text(source)
    env=dict(os.environ,DOTNET_CLI_HOME='/tmp/confectory-context-test-dotnet')
    subprocess.run([os.environ['CONFECTORY_DOTNET'],'run','--project',str(root/'probe.csproj'),'-c','Release'],env=env,check=True)
