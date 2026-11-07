using Confectory.Core;
namespace Confectory.Tests;
public sealed class ActiveToolIOTests : TestCase
{
 public void test_active_tool_observation_never_waits_for_admitted_io_and_clears_on_every_exit()
 {
  var sample=Path.Combine(f.Root,"active-io-consumer");Directory.CreateDirectory(sample);
  Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs"),Path.Combine(f.Root,"packs"));
  f.Add("App","object","ToolObject","object App::ToolObject {value count = 0;}");f.Sync();
  var registered=new HashSet<string>(StringComparer.Ordinal);var registrations=Directory.GetFiles(Path.Combine(f.Root,"packs"),"pack.cpack",SearchOption.AllDirectories).OrderBy(p=>p.Count(c=>c==Path.DirectorySeparatorChar)).ThenBy(p=>p,StringComparer.Ordinal).Select(p=>{var text=File.ReadAllText(p);var name=System.Text.RegularExpressions.Regex.Match(text,@"pack\s+([^\s]+)\s+version").Groups[1].Value;return name.Length>0&&registered.Add(name)?"registry "+name+" \""+p.Replace('\\','/')+"\";":"";});
  File.WriteAllText(Path.Combine(sample,"project.cpack"),"project Owned.IO version \"1\" {standalone true;entry Owned.IO::Main;dependency Confectory.DevelopmentTools version \"0.1.0\";dependency Confectory.ProjectAI version \"0.1.0\";dependency Confectory.EditWorkspace version \"0.1.0\";dependency Confectory.WorkerTasks version \"0.1.0\";dependency Confectory.Augment version \"0.1.0\";dependency Confectory.FileStream version \"0.1.0\";dependency Confectory.SchemaEditing version \"0.1.0\";dependency Confectory.Save version \"0.1.0\";dependency Confectory.ChangeSet version \"0.1.0\";"+string.Join("",registrations)+"registry Confectory.Build.DotNet \"../target/pack.cpack\";dependency Confectory.Build.DotNet version \"0.1.0\";target portable Confectory.Build.DotNet::Portable;element Main function \"Main.celem\";element MainBody implementation \"MainBody.celem\";element GatedRead implementation \"GatedRead.celem\";element Inspect implementation \"Inspect.celem\";element Tasks implementation \"Tasks.celem\";element Augment implementation \"Augment.celem\";element Adoption implementation \"Adoption.celem\";}");
  File.WriteAllText(Path.Combine(sample,"Main.celem"),"""
  function Owned.IO::Main () -> int {
  provide Owned.IO::Main with Owned.IO::MainBody;
  provide Confectory.EditWorkspace::Read with Owned.IO::GatedRead;
  provide Confectory.WorkerTasks::Inspect with Owned.IO::Inspect;
  provide Confectory.WorkerTasks::List with Owned.IO::Tasks;
  provide Confectory.Augment::Snapshot with Owned.IO::Augment;
  provide Confectory.ProjectAI::AdoptionStatus with Owned.IO::Adoption;
  }
  """);
  var defaults=System.Text.RegularExpressions.Regex.Matches(File.ReadAllText(Path.Combine(Fixture.Repo,"examples/edit-workspace/main.celem")),@"provide\s+(\S+)\s+with\s+(\S+);").Cast<System.Text.RegularExpressions.Match>().Where(m=>m.Groups[1].Value.StartsWith("Confectory.",StringComparison.Ordinal)&&m.Groups[1].Value!="Confectory.EditWorkspace::Read").Select(m=>m.Value);
  var main=Path.Combine(sample,"Main.celem");var root=File.ReadAllText(main);root=root.Insert(root.LastIndexOf('}'),string.Join("\n",defaults)+"\nprovide Confectory.FileStream::BrowseDirectory with Confectory.FileStream::BrowseDirectoryBody;\nprovide Confectory.WorkerTasks::Pump with Owned.IO::Pump;\n");File.WriteAllText(main,root);
  var manifest=Path.Combine(sample,"project.cpack");var declaration=File.ReadAllText(manifest);File.WriteAllText(manifest,declaration.Insert(declaration.LastIndexOf('}'),"element Pump implementation \"Pump.celem\";"));
  File.WriteAllText(Path.Combine(sample,"Pump.celem"),"implementation Owned.IO::Pump for Confectory.WorkerTasks::Pump (string session,string task) -> string {body common \"Inspect.csbody\";}");
  File.WriteAllText(Path.Combine(sample,"MainBody.celem"),"""
  implementation Owned.IO::MainBody for Owned.IO::Main () -> int {
  import Confectory.DevelopmentTools::Open as Open (string,string,string,string,string) -> string;
  import Confectory.DevelopmentTools::BindOrigin as Bind (string,string,string,string) -> void;
  import Confectory.DevelopmentTools::Invoke as Tool (string,string,string,string) -> string;
  import Confectory.DevelopmentTools::Snapshot as Snapshot (string) -> string;
  import Confectory.DevelopmentTools::Observe as Observe (string[]) -> string;
  import Confectory.DevelopmentTools::Close as Close (string) -> void;
  import Confectory.ProjectAI::Poll as Poll (string) -> string;
  body common "Main.csbody";}
  """);
  File.WriteAllText(Path.Combine(sample,"GatedRead.celem"),File.ReadAllText(Path.Combine(Fixture.Repo,"packs/edit-workspace/ReadBody.celem")).Replace("Confectory.EditWorkspace::ReadBody","Owned.IO::GatedRead").Replace("Read.csbody","GatedRead.csbody"));
  File.WriteAllText(Path.Combine(sample,"GatedRead.csbody"),"""
  // Owned deterministic scheduling fixture around the unchanged real reader.
  var gate=AppDomain.CurrentDomain.GetData("Owned.IO.Gate") as object[];
  if(gate is not null&&System.Threading.Thread.CurrentThread.ManagedThreadId==(int)gate[2]){
   ((System.Threading.ManualResetEventSlim)gate[0]).Set();
   if(!((System.Threading.ManualResetEventSlim)gate[1]).Wait(TimeSpan.FromSeconds(20)))throw new InvalidOperationException("owned gate deadline");
   if((bool)gate[3])throw new InvalidOperationException("owned read failure");
  }
  """+"\n"+File.ReadAllText(Path.Combine(Fixture.Repo,"packs/edit-workspace/Read.csbody")));
  foreach(var row in new[]{("Inspect","Confectory.WorkerTasks::Inspect","string session,string task","return (string)AppDomain.CurrentDomain.GetData(\"Owned.IO.Worker\")!;"),("Tasks","Confectory.WorkerTasks::List","string session","return \"[\\\"task-A\\\"]\";"),("Augment","Confectory.Augment::Snapshot","string session","return \"{\\\"batches\\\":[]}\";"),("Adoption","Confectory.ProjectAI::AdoptionStatus","string session,string task","return \"{\\\"state\\\":\\\"none\\\"}\";")}){
   File.WriteAllText(Path.Combine(sample,row.Item1+".celem"),"implementation Owned.IO::"+row.Item1+" for "+row.Item2+" ("+row.Item3+") -> string {body common \""+row.Item1+".csbody\";}");File.WriteAllText(Path.Combine(sample,row.Item1+".csbody"),row.Item4);
  }
  File.WriteAllText(Path.Combine(sample,"Main.csbody"),"""
  string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT")!,before=System.IO.File.ReadAllText(project),sourcePath=System.IO.Path.Combine(System.IO.Path.GetDirectoryName(project)!,"ToolObject.celem"),sourceBefore=System.IO.File.ReadAllText(sourcePath),cap=calls.Open.Invoke(project,"project-A","App","alice","editor"),master=calls.Open.Invoke(project,"project-A","App","alice","editor");
  void Check(bool ok,string why){if(!ok)throw new Exception(why);}
  string Request(string text="",long revision=0)=>new System.Text.Json.Nodes.JsonObject{["projectId"]="project-A",["id"]="App::ToolObject",["text"]=text,["expectedRevision"]=revision}.ToJsonString();
  System.Text.Json.Nodes.JsonNode Parse(string text)=>System.Text.Json.Nodes.JsonNode.Parse(text)!;
  string Quickly(Func<string> read){var task=System.Threading.Tasks.Task.Run(read);Check(task.Wait(TimeSpan.FromSeconds(2)),"observer waited for the admitted operation");return task.GetAwaiter().GetResult();}
  string worker="{\"task\":\"task-A\",\"worker\":\"worker-A\",\"project\":\"project-A\",\"status\":\"running\",\"lastToolIO\":{\"forged\":true},\"activeToolIO\":{\"forged\":true}}";
  var model=new System.Text.Json.Nodes.JsonObject();var caps=new System.Collections.Generic.Dictionary<string,string>{{"task-A",cap}};
  var state=new object[]{new object(),"project-A",null!,null!,master,null!,"",model,false,project,new object[]{"tasks","augment"},null!,new System.Collections.Generic.Dictionary<string,string>(),null!,null!,null!,null!,null!,null!,caps};
  AppDomain.CurrentDomain.SetData("Confectory.ProjectAI.owned-io",state);AppDomain.CurrentDomain.SetData("Owned.IO.Worker",worker);
  System.Threading.ManualResetEventSlim? release=null;System.Threading.Tasks.Task<string>? running=null;
  try{
   calls.Bind.Invoke(cap,"task-A","worker-A","request-A");
   void Begin(string call,string operation,string args,bool fail=false){
    var entered=new System.Threading.ManualResetEventSlim();release=new System.Threading.ManualResetEventSlim();var gate=new object[]{entered,release,0,fail};AppDomain.CurrentDomain.SetData("Owned.IO.Gate",gate);
    running=System.Threading.Tasks.Task.Run(()=>{gate[2]=System.Threading.Thread.CurrentThread.ManagedThreadId;return calls.Tool.Invoke(cap,call,operation,args);});Check(entered.Wait(TimeSpan.FromSeconds(3)),"owned actual reader not entered");
   }
   void End(bool fail=false){release!.Set();bool failed=false;try{running!.GetAwaiter().GetResult();}catch(InvalidOperationException){failed=true;}Check(failed==fail,"operation outcome changed");AppDomain.CurrentDomain.SetData("Owned.IO.Gate",null);Check(Parse(calls.Observe.Invoke(new[]{master,cap}))["activities"]!.AsObject().Count==0,"active cache survived operation exit");}
   Begin("read-1","workspace_read",Request());
   var observed=Parse(Quickly(()=>calls.Observe.Invoke(new[]{master,cap})));var signal=observed["activities"]![cap]!["signal"]!;
   Check(observed["pending"]!.GetValue<bool>()&&observed["snapshots"]!.AsObject().Count==0&&signal["kind"]!.ToString()=="read"&&signal["phase"]!.ToString()=="in-progress"&&signal["ordinal"]!.GetValue<int>()==1,"actual admitted read signal only; no partial provenance snapshot");
   var polled=Parse(Quickly(()=>calls.Poll.Invoke("owned-io")));Check(polled["toolsObservationPending"]!.GetValue<bool>()&&polled["workers"]!["task-A"]!["activeToolIO"]?["receipt"]?.ToString()==signal["receipt"]!.ToString()&&polled["workers"]!["task-A"]!["lastToolIO"]is null,"ProjectAI returns actual phase without waiting, journal fields stripped");
   var wrong=Parse(worker);wrong["worker"]="other";AppDomain.CurrentDomain.SetData("Owned.IO.Worker",wrong.ToJsonString());Check(Parse(Quickly(()=>calls.Poll.Invoke("owned-io")))["workers"]!["task-A"]!["activeToolIO"]is null,"phase cannot transfer to another Worker");AppDomain.CurrentDomain.SetData("Owned.IO.Worker",worker);
   var oldResult=signal.ToJsonString();End();Check(signal.ToJsonString()==oldResult,"immutable observation changed after completion");
   polled=Parse(calls.Poll.Invoke("owned-io"));Check(!polled["toolsObservationPending"]!.GetValue<bool>()&&polled["workers"]!["task-A"]!["activeToolIO"]is null&&polled["workers"]!["task-A"]!["lastToolIO"]?["kind"]?.ToString()=="read","completion resumes exact full snapshots and original completed receipt");
   var bounded=Parse(calls.Observe.Invoke(new[]{master,cap}))["snapshots"]!;Check(bounded[master]!["provenance"]is not null&&bounded[cap]!.AsObject().Count==4&&bounded[cap]!["provenance"]is null&&bounded[cap]!["dirty"]is null,"secondary owners retained duplicate whole-project provenance");
   string read=calls.Tool.Invoke(cap,"read-1","workspace_read",Request());Check(Parse(calls.Observe.Invoke(new[]{cap}))["activities"]!.AsObject().Count==0,"dedup cannot emit a phase");long revision=Parse(read)["revision"]!.GetValue<long>();
   Begin("stage-failed","workspace_stage",Request("object App::ToolObject {value count = 1;}",revision),true);observed=Parse(Quickly(()=>calls.Observe.Invoke(new[]{master,cap})));Check(observed["activities"]![cap]!["signal"]!["kind"]!.ToString()=="draft-stage","stage intent is distinct from source write/completion");End(true);Check(Parse(calls.Snapshot.Invoke(cap))["lastToolIO"]?["kind"]?.ToString()=="read","exception cannot publish successful stage");
   Begin("stage-conflict","workspace_stage",Request("object App::ToolObject {value count = 1;}",revision+50));End();Check(!Parse(running!.Result)["applied"]!.GetValue<bool>(),"original CAS conflict must remain rejected");
   Begin("stage-ok","workspace_stage",Request("object App::ToolObject {value count = 2;}",revision));End();Check(Parse(running!.Result)["applied"]!.GetValue<bool>()&&Parse(calls.Snapshot.Invoke(cap))["lastToolIO"]!["outcome"]!.ToString()=="applied","original draft CAS and completed signal retained");Check(System.IO.File.ReadAllText(project)==before&&System.IO.File.ReadAllText(sourcePath)==sourceBefore,"phase observation adopted source");
   string fresh=calls.Open.Invoke(project,"project-A","App","alice","editor");try{Check(Parse(calls.Observe.Invoke(new[]{fresh}))["activities"]!.AsObject().Count==0,"fresh capability restored an active phase");}finally{calls.Close.Invoke(fresh);}
   calls.Close.Invoke(cap);bool closed=false;try{calls.Observe.Invoke(new[]{cap});}catch(ObjectDisposedException){closed=true;}Check(closed,"disposed owner yielded cached phase");
   Console.WriteLine("Active tool IO nonblocking / origin isolation / read and draft-stage / exception and CAS / dedup / cold and close PASS");return 0;
  }finally{release?.Set();try{running?.Wait(TimeSpan.FromSeconds(5));}catch{}AppDomain.CurrentDomain.SetData("Owned.IO.Gate",null);AppDomain.CurrentDomain.SetData("Confectory.ProjectAI.owned-io",null);calls.Close.Invoke(cap);calls.Close.Invoke(master);}
  """);
  string? host=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST"),selected=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT");try{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",f.Project);Output(new Builder(Path.Combine(sample,"project.cpack"),"portable").Build(),"Active tool IO nonblocking / origin isolation / read and draft-stage / exception and CAS / dedup / cold and close PASS");}finally{Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",selected);Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",host);}
 }
}
