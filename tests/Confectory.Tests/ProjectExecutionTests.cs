using System.Diagnostics;
using Confectory.Core;
namespace Confectory.Tests;
public sealed class ProjectExecutionTests : TestCase
{
 public void test_actual_native_button_game_pause_single_draw_step_and_stop()
 {
  if(!OperatingSystem.IsWindows()&&string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISPLAY")))Skip("Actual native game requires an existing local display");
  string sample=Path.Combine(f.Root,"button-frame-driver");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples/project-execution"),sample);string manifest=Path.Combine(sample,"frame-verify.cpack");File.WriteAllText(manifest,File.ReadAllText(manifest).Replace("../../",Fixture.Repo+"/",StringComparison.Ordinal));
  File.WriteAllText(Path.Combine(sample,"frame-verify.csbody"),"""
  var session=calls.CreateSession.Invoke();string root=Environment.GetEnvironmentVariable("CONFECTORY_TEST_REPO")!;try{string h=calls.LaunchConfigured.Invoke(session,System.IO.Path.Combine(root,"examples/button-game/project.cpack"),"Example.ButtonGame::Main","linux",new[]{"CONFECTORY_BUTTON_GAME_GUI","CONFECTORY_BUTTON_GAME_TRACE_FRAME","CONFECTORY_UI"},new[]{"1","1","native"});System.Text.Json.Nodes.JsonNode Read()=>System.Text.Json.Nodes.JsonNode.Parse(calls.Control.Invoke(session,h,"observe"))!;System.Text.Json.Nodes.JsonNode Wait(Func<System.Text.Json.Nodes.JsonNode,bool> condition){var timer=System.Diagnostics.Stopwatch.StartNew();while(timer.ElapsedMilliseconds<90000){var node=Read();if(condition(node))return node;if(calls.Observe.Invoke(session,h)[1]=="failed")throw new Exception(string.Join(" | ",calls.Observe.Invoke(session,h)));System.Threading.Thread.Sleep(15);}throw new Exception("Native game frame timeout");}
  Wait(n=>n["available"]?.GetValue<bool>()==true&&long.Parse(n["frame"]!.ToString())>1);calls.Control.Invoke(session,h,"pause");var paused=Wait(n=>n["mode"]?.ToString()=="paused"&&n["ack"]?.GetValue<int>()==1);long frame=long.Parse(paused["frame"]!.ToString());System.Threading.Thread.Sleep(100);if(long.Parse(Read()["frame"]!.ToString())!=frame)throw new Exception("Native draw continued while paused");calls.Output.Invoke(session,h);calls.Control.Invoke(session,h,"step");var step=Wait(n=>n["ack"]?.GetValue<int>()==2);if(long.Parse(step["frame"]!.ToString())!=frame+1)throw new Exception("Native Step frame count");bool drawn=false;var watch=System.Diagnostics.Stopwatch.StartNew();while(!drawn&&watch.ElapsedMilliseconds<3000){foreach(string line in calls.Output.Invoke(session,h))if(line.StartsWith("BUTTON_GAME_FRAME ",StringComparison.Ordinal)){var actual=System.Text.Json.Nodes.JsonNode.Parse(line[18..])!;if(actual["frame"]!.ToString()==step["frame"]!.ToString()&&actual["drawnViews"]?.GetValue<int>()==2)drawn=true;}System.Threading.Thread.Sleep(10);}if(!drawn)throw new Exception("Step ack has no actual two-view Draw trace");calls.Stop.Invoke(session,h);if(Read()["connected"]?.GetValue<bool>()!=false)throw new Exception("Stopped game frame owner");Console.WriteLine("Actual native ButtonGame frame PASS: paused two views, one Step/draw completion, owned Stop");}finally{calls.Dispose.Invoke(session);}return 0;
  """);
  string? host=Environment.GetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST"),repo=Environment.GetEnvironmentVariable("CONFECTORY_TEST_REPO");try{Environment.SetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST",Path.Combine(Fixture.Repo,"targets/project-execution-host/bin/Release/net10.0/Confectory.ProjectExecutionHost.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_REPO",Fixture.Repo);var built=new Builder(manifest,"portable").Build();var run=Processes.Run(Strings(built,"run"),timeoutSeconds:180);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Actual native ButtonGame frame PASS",StringComparison.Ordinal),run.Stdout+run.Stderr);}finally{Environment.SetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_REPO",repo);}
 }
 public void test_actual_native_engine_cooperative_frame_callbacks()
 {
  if(!OperatingSystem.IsWindows()&&string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISPLAY")))Skip("Actual native engine requires an existing local display");
  string sample=Path.Combine(f.Root,"native-frame-driver"),engine=Path.Combine(f.Root,"native-engine");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples/project-execution"),sample);Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples/engine"),engine);
  foreach(string folder in new[]{sample,engine})foreach(string file in Directory.GetFiles(folder,"*.cpack"))File.WriteAllText(file,File.ReadAllText(file).Replace("../../",Fixture.Repo+"/",StringComparison.Ordinal));
  string body=Path.Combine(sample,"frame-verify.csbody"),text=File.ReadAllText(body).Replace("System.IO.Path.Combine(root,\"examples\",\"frame-loop\",\"project.cpack\")",System.Text.Json.JsonSerializer.Serialize(Path.Combine(engine,"project.cpack")),StringComparison.Ordinal).Replace("entry=\"Example.FrameLoop::Main\",outputPrefix=\"LOCAL_FRAME \"","entry=\"Confectory.Engine::Main\",outputPrefix=\"ENGINE_FRAME \"",StringComparison.Ordinal);File.WriteAllText(body,text);
  string? host=Environment.GetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST"),repo=Environment.GetEnvironmentVariable("CONFECTORY_TEST_REPO");try{Environment.SetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST",Path.Combine(Fixture.Repo,"targets/project-execution-host/bin/Release/net10.0/Confectory.ProjectExecutionHost.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_REPO",Fixture.Repo);var built=new Builder(Path.Combine(sample,"frame-verify.cpack"),"portable").Build();var run=Processes.Run(Strings(built,"run"),timeoutSeconds:240);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Actual owned frame control PASS",StringComparison.Ordinal),run.Stdout+run.Stderr);}finally{Environment.SetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_REPO",repo);}
 }
 public void test_frame_ack_foreign_stale_future_replies_cannot_overwrite_owner()
 {
  string child=Path.Combine(f.Root,"fault-child");Directory.CreateDirectory(child);
  File.WriteAllText(Path.Combine(child,"project.cpack"),"project Example.FrameFault version \"0.1.0\" {standalone true;registry Confectory.Build.DotNet \""+Path.Combine(Fixture.Repo,"targets/dotnet/pack.cpack")+"\";dependency Confectory.Build.DotNet version \"0.1.0\";target portable Confectory.Build.DotNet::Portable;entry Example.FrameFault::Main;element Main function \"Main.celem\";element MainBody implementation \"MainBody.celem\";}");
  File.WriteAllText(Path.Combine(child,"Main.celem"),"function Example.FrameFault::Main () -> int {provide Example.FrameFault::Main with Example.FrameFault::MainBody;}");
  File.WriteAllText(Path.Combine(child,"MainBody.celem"),"implementation Example.FrameFault::MainBody for Example.FrameFault::Main () -> int {body common \"Main.csbody\";}");
  File.WriteAllText(Path.Combine(child,"Main.csbody"),"""
  string pipe=Environment.GetEnvironmentVariable("CONFECTORY_FRAME_PIPE")!,handle=Environment.GetEnvironmentVariable("CONFECTORY_FRAME_HANDLE")!,secret=Environment.GetEnvironmentVariable("CONFECTORY_FRAME_SECRET")!,epoch=Guid.NewGuid().ToString("N");int ack=0,fault=0;
  using var server=new System.IO.Pipes.NamedPipeServerStream(pipe,System.IO.Pipes.PipeDirection.InOut,1,System.IO.Pipes.PipeTransmissionMode.Byte,System.IO.Pipes.PipeOptions.CurrentUserOnly);
  while(true){server.WaitForConnection();try{byte[] header=new byte[4];server.ReadExactly(header);int length=System.Buffers.Binary.BinaryPrimitives.ReadInt32LittleEndian(header);if(length<1||length>4096)throw new Exception("bound");byte[] bytes=new byte[length];server.ReadExactly(bytes);var q=System.Text.Json.Nodes.JsonNode.Parse(bytes)!;if(q["secret"]!.ToString()!=secret||q["handle"]!.ToString()!=handle)throw new Exception("owner");string op=q["operation"]!.ToString();
  var reply=new System.Text.Json.Nodes.JsonObject{["version"]=1,["handle"]=handle,["runtime"]=epoch,["request"]=q["request"]!.ToString(),["connected"]=true,["mode"]="paused",["frame"]=ack==0?"10":"11",["ack"]=ack,["pending"]=0,["action"]="pause",["outcome"]="applied"};
  int injected=-1;if(op=="pause"){ack=1;reply["ack"]=1;reply["frame"]="11";}else if(ack==1){switch(injected=fault++){case 0:reply["ack"]=0;break;case 1:reply["runtime"]=new string('0',32);break;case 2:reply["request"]=new string('0',32);break;case 3:reply["handle"]=new string('0',32);break;case 4:reply["frame"]="9";break;case 5:reply["ack"]=20;break;case 6:reply.Clear();break;case 7:reply.Clear();break;case 8:reply["ack"]=long.MaxValue;break;case 9:reply["frame"]=new string('9',100);break;default:reply["frame"]="12";break;}}
  bytes=System.Text.Encoding.UTF8.GetBytes(injected==7?"null":reply.ToJsonString());System.Buffers.Binary.BinaryPrimitives.WriteInt32LittleEndian(header,bytes.Length);server.Write(header);server.Write(bytes);server.Flush();}finally{server.Disconnect();}}
  """);
  string caller=Path.Combine(f.Root,"fault-caller");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples/project-execution"),caller);
  string manifest=Path.Combine(caller,"frame-verify.cpack");File.WriteAllText(manifest,File.ReadAllText(manifest).Replace("../../",Fixture.Repo+"/",StringComparison.Ordinal));
  File.WriteAllText(Path.Combine(caller,"frame-verify.csbody"),"""
  var session=calls.CreateSession.Invoke();try{string handle=calls.Launch.Invoke(session,CHILD,"Example.FrameFault::Main","portable");System.Text.Json.Nodes.JsonNode Control(string op)=>System.Text.Json.Nodes.JsonNode.Parse(calls.Control.Invoke(session,handle,op))!;var watch=System.Diagnostics.Stopwatch.StartNew();System.Text.Json.Nodes.JsonNode first;do{first=Control("observe");if(first["available"]?.GetValue<bool>()==true)break;System.Threading.Thread.Sleep(20);}while(watch.ElapsedMilliseconds<60000);if(first["available"]?.GetValue<bool>()!=true)throw new Exception("Fault channel startup "+string.Join(" | ",calls.Observe.Invoke(session,handle)));var accepted=Control("pause");if(accepted["ack"]?.GetValue<int>()!=1)throw new Exception("Fault baseline");for(int i=0;i<10;i++){var refused=Control("observe");if(refused["connected"]?.GetValue<bool>()!=false||refused["ack"]?.GetValue<int>()!=1||refused["frame"]?.ToString()!="11")throw new Exception("Foreign/stale reply overwrote receipt "+i+" "+refused);}var fresh=Control("observe");if(fresh["connected"]?.GetValue<bool>()!=true||fresh["ack"]?.GetValue<int>()!=1||fresh["frame"]?.ToString()!="12")throw new Exception("Fresh observation did not recover");Console.WriteLine("Frame ack fault injection PASS: stale ack/frame, foreign runtime/request/handle and future ack rejected without overwriting receipt");}finally{calls.Dispose.Invoke(session);}return 0;
  """.Replace("CHILD",System.Text.Json.JsonSerializer.Serialize(Path.Combine(child,"project.cpack")),StringComparison.Ordinal));
  string? host=Environment.GetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST");try{Environment.SetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST",Path.Combine(Fixture.Repo,"targets/project-execution-host/bin/Release/net10.0/Confectory.ProjectExecutionHost.dll"));var built=new Builder(manifest,"portable").Build();var run=Processes.Run(Strings(built,"run"),timeoutSeconds:180);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Frame ack fault injection PASS",StringComparison.Ordinal),run.Stdout+run.Stderr);}finally{Environment.SetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST",host);}
 }
 public void test_frame_control_actual_boundary_order_repeat_thread_and_close()
 {
  var built=new Builder(Path.Combine(Fixture.Repo,"examples/frame-loop/protocol-verify.cpack"),"portable").Build();var run=Processes.Run(Strings(built,"run"),timeoutSeconds:90);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Actual frame protocol boundary PASS",StringComparison.Ordinal),run.Stdout+run.Stderr);
 }
 public void test_actual_owned_cooperative_frames_pause_step_reconnect_and_stop()
 {
  string sample=Path.Combine(f.Root,"frame-execution");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples/project-execution"),sample);
  foreach(string file in Directory.GetFiles(sample,"*.cpack"))File.WriteAllText(file,File.ReadAllText(file).Replace("../../",Fixture.Repo+"/",StringComparison.Ordinal));
  string? host=Environment.GetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST"),repo=Environment.GetEnvironmentVariable("CONFECTORY_TEST_REPO");
  try{Environment.SetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST",Path.Combine(Fixture.Repo,"targets/project-execution-host/bin/Release/net10.0/Confectory.ProjectExecutionHost.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_REPO",Fixture.Repo);var built=new Builder(Path.Combine(sample,"frame-verify.cpack"),"portable").Build();var result=Processes.Run(Strings(built,"run"),timeoutSeconds:240);True(result.ExitCode==0,result.Stdout+result.Stderr);True(result.Stdout.Contains("Actual owned frame control PASS",StringComparison.Ordinal),result.Stdout+result.Stderr);}
  finally{Environment.SetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_REPO",repo);}
 }
 public void test_execution_handles_and_provider_locality()
 {
  string sample=Path.Combine(f.Root,"execution-sample"),pack=Path.Combine(f.Root,"packs","project-execution");
  Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","project-execution"),sample);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","project-execution"),pack);
  Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","file-stream"),Path.Combine(f.Root,"packs","file-stream"));
  string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/",StringComparison.Ordinal).Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));
  var first=new Builder(project,"portable").Build();
  string? host=Environment.GetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST"),repo=Environment.GetEnvironmentVariable("CONFECTORY_TEST_REPO");
  try
  {
   Environment.SetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST",Path.Combine(Fixture.Repo,"targets","project-execution-host","bin","Release","net10.0","Confectory.ProjectExecutionHost.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_REPO",Fixture.Repo);
   var result=Processes.Run(Strings(first,"run"),timeoutSeconds:120);Equal(0,result.ExitCode);True(result.Stdout.Contains("ProjectExecution lifecycle PASS",StringComparison.Ordinal),result.Stderr);var cached=new Builder(project,"portable").Build();Equal(0,Strings(cached,"statistics","compiledImplementations").Length);
   File.AppendAllText(Path.Combine(pack,"Observe.csbody"),"\n// provider-only locality check\n");var changed=new Builder(project,"portable").Build();PackRebuilt(changed, new[]{"Confectory.ProjectExecution::ObserveBody"});Equal(0,Strings(changed,"statistics","compiledContracts").Length);
   File.WriteAllText(Path.Combine(sample,"main.csbody"),"""
   var session=calls.CreateSession.Invoke();
   try
   {
    if(calls.Capabilities.Invoke()[0]!="android-app-surface")throw new Exception("Android capability selection");
    string handle=calls.Launch.Invoke(session,"explicit.cpack","Project::Main","android");
    var state=calls.Observe.Invoke(session,handle);
    if(state[1]!="failed"||!state[6].Contains("not yet available"))throw new Exception("Unsupported native app launch must be explicit");
    calls.Stop.Invoke(session,handle);
    if(calls.Poll.Invoke(session).Length!=4||calls.Poll.Invoke(session).Length!=0)throw new Exception("Android terminal handle policy");
   }
   finally{calls.Dispose.Invoke(session);}
   Console.WriteLine("Android execution capability managed probe PASS; native app launch unavailable");return 0;
   """);
   var android=new Builder(project,"android").Build();Output(android,"Android execution capability managed probe PASS; native app launch unavailable");var catalog=System.Text.Json.Nodes.JsonNode.Parse(File.ReadAllText(Text(android,"publicCatalog")))!;
   foreach(string id in new[]{"Confectory.ProjectExecution::LaunchConfiguredBody","Confectory.ProjectExecution::CapabilitiesBody"})Equal("android",catalog["implementations"]!.AsArray().Single(x=>x!["id"]!.GetValue<string>()==id)!["bodySelection"]!.GetValue<string>());
  }
  finally{Environment.SetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_REPO",repo);}
 }
}
