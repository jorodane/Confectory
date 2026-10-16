using System.Text.Json;
using Confectory.Core;
namespace Confectory.Tests;

public sealed class BuildJobTests : TestCase
{
 public void test_build_only_real_compiler_owned_cancel_artifacts_failure_history_and_no_run()
 {
  string consumer=Path.Combine(f.Root,"build-job-consumer"),packs=Path.Combine(f.Root,"job-packs");Directory.CreateDirectory(consumer);
  foreach(string name in new[]{"project-execution","file-stream"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",name),Path.Combine(packs,name));
  string project=Path.Combine(consumer,"project.cpack");
  File.WriteAllText(project,"project Job.Consumer version \"1\" {entry Job.Consumer::Main;standalone true;registry Confectory.ProjectExecution "+JsonSerializer.Serialize(Path.Combine(packs,"project-execution/pack.cpack"))+";dependency Confectory.ProjectExecution version \"0.1.0\";registry Confectory.FileStream "+JsonSerializer.Serialize(Path.Combine(packs,"file-stream/pack.cpack"))+";dependency Confectory.FileStream version \"0.1.0\";registry Confectory.Build.DotNet "+JsonSerializer.Serialize(Path.Combine(f.Root,"target/pack.cpack"))+";dependency Confectory.Build.DotNet version \"0.1.0\";target portable Confectory.Build.DotNet::Portable;element Main function \"Main.celem\";element MainBody implementation \"MainBody.celem\";}");
  string[] roles={"CreateSession","Build","BuildQuery","Observe","Output","Stop","Poll","Dispose","Capabilities"};
  File.WriteAllText(Path.Combine(consumer,"Main.celem"),"function Job.Consumer::Main () -> int {provide Job.Consumer::Main with Job.Consumer::MainBody;"+string.Join("",roles.Select(role=>"provide Confectory.ProjectExecution::"+role+" with Confectory.ProjectExecution::"+role+"Body;"))+"provide Confectory.FileStream::LeasePath with Confectory.FileStream::LeasePathBody;}");
  File.WriteAllText(Path.Combine(consumer,"MainBody.celem"),"""
  implementation Job.Consumer::MainBody for Job.Consumer::Main () -> int {
  import Confectory.ProjectExecution::CreateSession as Session () -> string[];
  import Confectory.ProjectExecution::Build as Build (string[],string,string,string) -> string;
  import Confectory.ProjectExecution::BuildQuery as Query (string[],string,string,string) -> string;
  import Confectory.ProjectExecution::Observe as Observe (string[],string) -> string[];
  import Confectory.ProjectExecution::Stop as Stop (string[],string) -> void;
  import Confectory.ProjectExecution::Poll as Poll (string[]) -> string[];
  import Confectory.ProjectExecution::Dispose as Dispose (string[]) -> void;
  import Confectory.FileStream::LeasePath as Lease (string) -> string;
  body common "Main.csbody";}
  """);
  f.Body("App","main.csbody","System.IO.File.WriteAllText(Environment.GetEnvironmentVariable(\"CONFECTORY_BUILD_SENTINEL\")!,\"executed\");return 0;");f.Sync();
  File.WriteAllText(Path.Combine(consumer,"Main.csbody"),"""
  void Check(bool ok,string why){if(!ok)throw new Exception(why);}
  void Reject(Action action){bool rejected=false;try{action();}catch(ArgumentException){rejected=true;}catch(InvalidOperationException){rejected=true;}Check(rejected,"Foreign or disposed build operation accepted");}
  string project=Environment.GetEnvironmentVariable("CONFECTORY_BUILD_TEST_PROJECT")!,root=System.IO.Path.GetDirectoryName(project)!,sentinel=Environment.GetEnvironmentVariable("CONFECTORY_BUILD_SENTINEL")!;
  var originals=System.Linq.Enumerable.ToDictionary(System.IO.Directory.EnumerateFiles(root),path=>path,path=>System.IO.File.ReadAllBytes(path));
  var session=calls.Session.Invoke();var foreign=calls.Session.Invoke();
  System.Text.Json.Nodes.JsonNode Info(string[] owner,string job,bool verify=false)=>System.Text.Json.Nodes.JsonNode.Parse(calls.Query.Invoke(owner,project,"info",System.Text.Json.JsonSerializer.Serialize(new{job,verify})))!;
  System.Text.Json.Nodes.JsonNode History(string[] owner)=>System.Text.Json.Nodes.JsonNode.Parse(calls.Query.Invoke(owner,project,"history","{\"page\":0}"))!;
  string[] Finish(string job){var clock=System.Diagnostics.Stopwatch.StartNew();while(clock.Elapsed.TotalSeconds<120){var status=calls.Observe.Invoke(session,job);if(status[1] is "built" or "failed" or "stopped")return status;System.Threading.Thread.Sleep(20);}throw new Exception("Actual build timed out");}
  try{
   string lease=calls.Lease.Invoke(root);System.IO.Directory.CreateDirectory(System.IO.Path.GetDirectoryName(lease)!);
   using(var held=new System.IO.FileStream(lease,System.IO.FileMode.OpenOrCreate,System.IO.FileAccess.ReadWrite,System.IO.FileShare.None)){
    string waiting=calls.Build.Invoke(session,project,"App::Main","portable");Check(calls.Observe.Invoke(session,waiting)[1]=="building","Asynchronous owned build while actual source lease is held");
    var own=Info(session,waiting);Check(own["canStop"]!.GetValue<bool>()&&own["ownerAvailable"]!.GetValue<bool>(),"Owned cancellation available");
    var other=Info(foreign,waiting);Check(other["state"]!.ToString()=="owner-unavailable"&&!other["canStop"]!.GetValue<bool>(),"Foreign session cannot revive ownership");Reject(()=>calls.Stop.Invoke(foreign,waiting));
    calls.Stop.Invoke(session,waiting);calls.Stop.Invoke(session,waiting);Check(calls.Observe.Invoke(session,waiting)[1]=="stopped"&&Info(session,waiting)["state"]!.ToString()=="stopped","Actual waiting worker retired and durable cancellation");
    Check(calls.Poll.Invoke(session).Length==4&&calls.Poll.Invoke(session).Length==0,"Terminal build notification once");Check(!System.IO.Directory.Exists(System.IO.Path.Combine(root,".confectory","outputs")),"Cancelled source-lease wait never compiled");
   }
   string success=calls.Build.Invoke(session,project,"App::Main","portable");var done=Finish(success);Check(done[1]=="built",string.Join(" | ",done));Check(!System.IO.File.Exists(sentinel),"Compiler success must never run linked application");
   var info=Info(session,success,true);Check(info["artifactState"]!.ToString()=="verified"&&info["files"]!.AsArray().Count>0&&info["key"]!.ToString().Length==64,"Actual artifact files and content hashes");Check(!info.ToJsonString().Contains(root,StringComparison.Ordinal)&&!info.ToJsonString().Contains("owner\"",StringComparison.Ordinal),"No host paths or owner nonce in public receipt");
   Check(calls.Poll.Invoke(session).Length==4&&calls.Poll.Invoke(session).Length==0,"Built is a terminal notification");
   var report=System.Text.Json.Nodes.JsonNode.Parse(System.IO.File.ReadAllText(System.IO.Path.Combine(root,".confectory","outputs","portable","latest.json")))!;string output=report["output"]!.ToString(),artifact=System.IO.Path.Combine(output,"build-report.json");byte[] saved=System.IO.File.ReadAllBytes(artifact);
   System.IO.File.AppendAllText(artifact," ");Check(Info(session,success,true)["artifactState"]!.ToString()=="changed","Artifact content tamper detected");System.IO.File.WriteAllBytes(artifact,saved);System.IO.File.Move(artifact,artifact+".removed");Check(Info(session,success,true)["artifactState"]!.ToString()=="missing","Deleted artifact explicit");System.IO.File.Move(artifact+".removed",artifact);Check(Info(session,success,true)["artifactState"]!.ToString()=="verified","Restored exact artifact");
   string source=System.IO.Path.Combine(root,"main.csbody");System.IO.File.AppendAllText(source,"\nthis is deliberately invalid C#;\n");string failed=calls.Build.Invoke(session,project,"App::Main","portable");Check(Finish(failed)[1]=="failed","Actual compiler failure");var failure=Info(session,failed);Check(failure["state"]!.ToString()=="failed"&&failure["key"] is null&&failure["job"]!.ToString()!=success,"New failure never borrows prior success artifacts");Check(Info(session,success,true)["artifactState"]!.ToString()=="verified","Prior successful result retained independently");System.IO.File.WriteAllBytes(source,originals[source]);
   Check(calls.Poll.Invoke(session).Length==4&&calls.Poll.Invoke(session).Length==0,"Failed notification once");var history=History(foreign);Check(history["total"]!.GetValue<int>()==3&&System.Linq.Enumerable.Any(history["rows"]!.AsArray(),row=>row!["state"]!.ToString()=="built")&&System.Linq.Enumerable.Any(history["rows"]!.AsArray(),row=>row!["state"]!.ToString()=="failed"),"Durable distinct outcomes readable by fresh session without replay");
   Check(!System.IO.File.Exists(sentinel),"No build executes user application");foreach(var pair in originals)Check(System.Linq.Enumerable.SequenceEqual(System.IO.File.ReadAllBytes(pair.Key),pair.Value),"Final source bytes changed: "+System.IO.Path.GetFileName(pair.Key));
   calls.Dispose.Invoke(session);Reject(()=>Info(session,success));Check(Info(foreign,success,true)["artifactState"]!.ToString()=="verified"&&!Info(foreign,success)["ownerAvailable"]!.GetValue<bool>(),"Receipt survives disposed runtime owner");
   Console.WriteLine("Build-only real compiler/owned cancel/artifacts/failure/history/no program execution PASS");return 0;
  }finally{calls.Dispose.Invoke(session);calls.Dispose.Invoke(foreign);}
  """);
  var names=new[]{"CONFECTORY_PROJECT_EXECUTION_HOST","CONFECTORY_BUILD_TEST_PROJECT","CONFECTORY_BUILD_SENTINEL"};var previous=names.Select(Environment.GetEnvironmentVariable).ToArray();
  try{Environment.SetEnvironmentVariable(names[0],Path.Combine(Fixture.Repo,"targets/project-execution-host/bin/Release/net10.0/Confectory.ProjectExecutionHost.dll"));Environment.SetEnvironmentVariable(names[1],f.Project);Environment.SetEnvironmentVariable(names[2],Path.Combine(f.Root,"must-not-run.txt"));Output(new Builder(project,"portable").Build(),"Build-only real compiler/owned cancel/artifacts/failure/history/no program execution PASS");}
  finally{for(int i=0;i<names.Length;i++)Environment.SetEnvironmentVariable(names[i],previous[i]);}
 }
 public void test_unavailable_build_profiles_never_invoke_desktop_provider()
 {
  string folder=Path.Combine(f.Root,"unavailable-builds"),packs=Path.Combine(f.Root,"native-job-packs");Directory.CreateDirectory(folder);
  foreach(string name in new[]{"project-execution","file-stream"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",name),Path.Combine(packs,name));
  string project=Path.Combine(folder,"project.cpack");
  File.WriteAllText(project,$$"""
  project Job.Unavailable version "1" {
  entry Job.Unavailable::Main;
  registry Confectory.ProjectExecution {{JsonSerializer.Serialize(Path.Combine(packs,"project-execution/pack.cpack"))}};
  dependency Confectory.ProjectExecution version "0.1.0";
  registry Confectory.FileStream {{JsonSerializer.Serialize(Path.Combine(packs,"file-stream/pack.cpack"))}};
  dependency Confectory.FileStream version "0.1.0";
  registry Confectory.Build.DotNet {{JsonSerializer.Serialize(Path.Combine(f.Root,"target/pack.cpack"))}};
  dependency Confectory.Build.DotNet version "0.1.0";
  target android Confectory.Build.DotNet::Portable;target browser Confectory.Build.DotNet::Portable;
  element Main function "Main.celem";element Body implementation "Body.celem";
  }
  """);
  string[] roles={"CreateSession","Build","BuildQuery","StopBuilds","Stop","Observe","Poll","Dispose","Capabilities"};
  File.WriteAllText(Path.Combine(folder,"Main.celem"),"function Job.Unavailable::Main () -> int {provide Job.Unavailable::Main with Job.Unavailable::Body;"+string.Join("",roles.Select(role=>"provide Confectory.ProjectExecution::"+role+" with Confectory.ProjectExecution::"+role+"Body;"))+"provide Confectory.FileStream::LeasePath with Confectory.FileStream::LeasePathBody;}");
  File.WriteAllText(Path.Combine(folder,"Body.celem"),"""
  implementation Job.Unavailable::Body for Job.Unavailable::Main () -> int {
  import Confectory.ProjectExecution::CreateSession as Session () -> string[];
  import Confectory.ProjectExecution::Build as Build (string[],string,string,string) -> string;
  import Confectory.ProjectExecution::BuildQuery as Query (string[],string,string,string) -> string;
  import Confectory.ProjectExecution::Observe as Observe (string[],string) -> string[];
  import Confectory.ProjectExecution::Capabilities as Capabilities () -> string[];
  import Confectory.ProjectExecution::StopBuilds as StopBuilds (string[]) -> void;
  import Confectory.ProjectExecution::Poll as Poll (string[]) -> string[];
  import Confectory.ProjectExecution::Dispose as Dispose (string[]) -> void;
  body common "Body.csbody";}
  """);
  File.WriteAllText(Path.Combine(folder,"Body.csbody"),"""
  void Check(bool value,string why){if(!value)throw new Exception(why);}
  var session=calls.Session.Invoke();try{
   Check(!System.Linq.Enumerable.Contains(calls.Capabilities.Invoke(),"build-only"),"Unavailable runtime falsely advertised dynamic build");
   string job=calls.Build.Invoke(session,"explicit-never-read.cpack","App::Main","explicit-target");Check(calls.Observe.Invoke(session,job)[1]=="failed","Explicit failed unavailable handle");
   var info=System.Text.Json.Nodes.JsonNode.Parse(calls.Query.Invoke(session,"explicit-never-read.cpack","info",System.Text.Json.JsonSerializer.Serialize(new{job})))!;Check(info["state"]!.ToString()=="failed"&&!info["providerAvailable"]!.GetValue<bool>()&&!info["canStop"]!.GetValue<bool>(),"No desktop provider invocation");
   var history=System.Text.Json.Nodes.JsonNode.Parse(calls.Query.Invoke(session,"explicit-never-read.cpack","history","{}"))!;Check(history["state"]!.ToString()=="unavailable"&&!history["providerAvailable"]!.GetValue<bool>(),"Unavailable is distinct from empty history");
   calls.StopBuilds.Invoke(session);Check(calls.Poll.Invoke(session).Length==4&&calls.Poll.Invoke(session).Length==0,"Unavailable terminal notification once");
  }finally{calls.Dispose.Invoke(session);}
  Console.WriteLine("Unavailable build provider managed probe PASS");return 0;
  """);
  string? previous=Environment.GetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST");
  try{
   Environment.SetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST",Path.Combine(f.Root,"must-not-run.dll"));
   foreach(string target in new[]{"android","browser"}){
    var built=new Builder(project,target).Build();Output(built,"Unavailable build provider managed probe PASS");
    var catalog=System.Text.Json.Nodes.JsonNode.Parse(File.ReadAllText(Text(built,"publicCatalog")))!;
    foreach(string id in new[]{"Confectory.ProjectExecution::BuildBody","Confectory.ProjectExecution::BuildQueryBody"})Equal(target,catalog["implementations"]!.AsArray().Single(row=>row!["id"]!.ToString()==id)!["bodySelection"]!.ToString());
   }
  }finally{Environment.SetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST",previous);}
 }
}
