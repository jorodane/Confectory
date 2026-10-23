"""Compile the actual SlotBatch body with controlled dependencies; deterministic commit races.
Not an account/provider test. Actual creator/path semantics are covered by engine tests.
"""
import pathlib,sys,tempfile,os,subprocess,json,hashlib
repo=pathlib.Path(sys.argv[1]).resolve();case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-slot-batch-core-'))
(case/'probe.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Exe</OutputType><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>')
body=(repo/'packs/edit-workspace/SlotBatch.csbody').read_text()
source=r'''using System.Text.Json.Nodes;
using System.Security.Cryptography;
using System.Text;
class Calls {
 public Func<string,string,string> Context=null!;
 public Func<string,string,string,string,string,string[],long[],string[],string> Create=null!;
 public Func<string,string,string> Metadata=null!;
 public Func<string,string,string> Copy=(h,p)=>throw new Exception("Unexpected copy branch in ordinary slot transaction regression");
}
class Program {
 static string Batch(string handle,string plans,Calls calls){ BODY }
 static string Hash(string value)=>Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(value))).ToLowerInvariant();
 static void Check(bool condition,string message){if(!condition)throw new Exception(message);}
 static int Main(){
  int passed=0;
  foreach(string mode in new[]{"second-failure","peer-race","owner-race","manifest-race","close-race","destination-race","stale-hash","success-preserves-checkpoint"}){
   string handle=Guid.NewGuid().ToString("N"),key="Confectory.EditWorkspace."+handle,root=Path.Combine(Path.GetTempPath(),"slot-batch-core-"+handle);Directory.CreateDirectory(root);
   var units=new JsonObject();foreach(string id in new[]{"Owner","Slot","Slot2","Donor","ProjectManifest","Peer"})units["Owned::"+id]=new JsonObject{["id"]="Owned::"+id,["kind"]=id=="Owner"||id=="Peer"?"object":id=="ProjectManifest"?"project":"function",["path"]=id+".celem",["draft"]=id,["original"]=id,["baseline"]="fixture-hash",["revision"]=1L};
   var state=new JsonObject{["root"]=root,["project"]=Path.Combine(root,"ProjectManifest.celem"),["namespace"]="Owned",["units"]=units,["checkpoint"]="keep",["history"]=new JsonObject{["revision"]=0L}};AppDomain.CurrentDomain.SetData(key,state);var before=state.DeepClone();
   var context=new JsonObject{["owner"]="Owned::Owner",["guards"]=new JsonObject(),["requirements"]=new JsonArray(new JsonObject{["function"]="Owned::Slot"},new JsonObject{["function"]="Owned::Slot2"})};var plans=new JsonArray();int count=0;string? stagedKey=null;using var staged=new ManualResetEventSlim();using var resume=new ManualResetEventSlim();
   foreach(string fn in new[]{"Slot","Slot2"}){var ids=new[]{"Owned::Owner","Owned::"+fn,"Owned::Donor","Owned::ProjectManifest"};plans.Add(new JsonObject{["id"]="Owned::Owner",["function"]="Owned::"+fn,["implementation"]="Owned::Impl_"+fn,["context"]=context.DeepClone(),["ids"]=System.Text.Json.JsonSerializer.SerializeToNode(ids),["revisions"]=System.Text.Json.JsonSerializer.SerializeToNode(new long[]{1,1,1,1}),["hashes"]=System.Text.Json.JsonSerializer.SerializeToNode(ids.Select(id=>Hash(units[id]!["draft"]!.ToString())).ToArray())});}
   if(mode=="stale-hash")plans[1]!["hashes"]![1]=new string('0',64);
   var calls=new Calls{Context=(h,o)=>context.ToJsonString(),Metadata=(op,input)=>throw new Exception("Unexpected metadata operation")};
   calls.Create=(h,o,f,impl,c,ids,revs,hashes)=>{stagedKey="Confectory.EditWorkspace."+h;var candidate=(JsonObject)AppDomain.CurrentDomain.GetData(stagedKey)!;int index=Interlocked.Increment(ref count);candidate["units"]![o]!["draft"]="staged-"+index;candidate["units"]![o]!["revision"]=1L+index;candidate["units"]!["Owned::ProjectManifest"]!["draft"]="staged-registration-"+index;candidate["units"]!["Owned::ProjectManifest"]!["revision"]=1L+index;candidate["units"]![impl]=new JsonObject{["kind"]="implementation",["path"]=impl.Split("::")[1]+".celem",["draft"]="fixture",["revision"]=1L,["baseline"]="missing"};
    if(index==1&&mode is "peer-race" or "owner-race" or "manifest-race" or "close-race" or "destination-race" or "success-preserves-checkpoint"){staged.Set();Check(resume.Wait(TimeSpan.FromSeconds(10)),"Race release timeout");}
    if(index==2&&mode=="second-failure")throw new InvalidOperationException("second staged plan fails");return new JsonObject{["id"]=impl}.ToJsonString();};
   Exception? failure=null;string? result=null;var task=Task.Run(()=>{try{result=Batch(handle,plans.ToJsonString(),calls);}catch(Exception e){failure=e;}});
   if(mode is "peer-race" or "owner-race" or "manifest-race" or "close-race" or "destination-race" or "success-preserves-checkpoint"){
    Check(staged.Wait(TimeSpan.FromSeconds(10)),"Race entry timeout");lock(state){if(mode is "peer-race" or "owner-race" or "manifest-race"){string affected=mode=="owner-race"?"Owned::Owner":mode=="manifest-race"?"Owned::ProjectManifest":"Owned::Peer";state["units"]![affected]!["draft"]="concurrent peer";state["units"]![affected]!["revision"]=2L;}if(mode=="close-race")AppDomain.CurrentDomain.SetData(key,null);if(mode=="destination-race")File.WriteAllText(Path.Combine(root,"Impl_Slot2.celem"),"preserve collision");if(mode=="success-preserves-checkpoint")state["checkpoint"]="new independent checkpoint";}resume.Set();
   }
   Check(task.Wait(TimeSpan.FromSeconds(10)),"Transaction timeout");Check(stagedKey is null||AppDomain.CurrentDomain.GetData(stagedKey) is null,"Staged state leaked");
   if(mode=="success-preserves-checkpoint"){Check(failure is null&&JsonNode.Parse(result!)!["atomic"]!.GetValue<bool>(),failure?.ToString()??"No result");Check(state["units"]!["Owned::Impl_Slot"] is not null&&state["units"]!["Owned::Impl_Slot2"] is not null,"Only one result committed");Check(state["checkpoint"]!.ToString()=="new independent checkpoint","Checkpoint overwritten");}
   else {Check(failure is InvalidOperationException,"Expected refusal: "+failure);var expected=before!["units"]!.DeepClone();if(mode is "peer-race" or "owner-race" or "manifest-race"){string affected=mode=="owner-race"?"Owned::Owner":mode=="manifest-race"?"Owned::ProjectManifest":"Owned::Peer";expected[affected]!["draft"]="concurrent peer";expected[affected]!["revision"]=2L;}Check(JsonNode.DeepEquals(expected,state["units"]),"Partial transaction or peer update lost");Check(state["checkpoint"]!.ToString()=="keep","Existing checkpoint lost");if(mode=="destination-race")Check(File.ReadAllText(Path.Combine(root,"Impl_Slot2.celem"))=="preserve collision","Collision file lost");}
   AppDomain.CurrentDomain.SetData(key,null);Directory.Delete(root,true);Console.WriteLine("PASS "+mode);passed++;
  }
  Console.WriteLine(passed+" actual SlotBatch-body controlled-dependency race checks; not native Windows/account testing");return 0;
 }
}
'''.replace('BODY',body)
(case/'Program.cs').write_text(source)
env=os.environ.copy();env.update(DOTNET_CLI_HOME='/tmp/confectory-dotnet10-final',NUGET_PACKAGES='/tmp/confectory-site-nuget')
print('CASE '+str(case),flush=True);result=subprocess.run(['/workspace/toolchains/dotnet-10.0.401/dotnet','run','--project',str(case/'probe.csproj'),'-c','Release'],env=env)
if result.returncode==0:(case/'evidence.json').write_text(json.dumps({'checks':['second-failure','peer-race','owner-race','manifest-race','close-race','destination-race','stale-hash','success-preserves-checkpoint'],'actualProductBody':True,'controlledDependencies':True,'actualEngine':False,'nativeWindows':False,'sourceSha256':hashlib.sha256(body.encode()).hexdigest(),'evidence':str(case)},indent=2))
raise SystemExit(result.returncode)
