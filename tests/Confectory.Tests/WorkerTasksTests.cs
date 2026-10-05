using System.Diagnostics;
using System.Text.Json.Nodes;
using Confectory.Core;
namespace Confectory.Tests;
public sealed class WorkerTasksTests : TestCase
{
 public void test_durable_supervision_recovery_live_worker_and_process_restart_without_replay()
 {
  string sample=Path.Combine(f.Root,"supervision-sample");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","supervision"),sample);foreach(string pack in new[]{"helper","agent","worker-tasks","file-stream"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",pack),Path.Combine(f.Root,"packs",pack));string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/",StringComparison.Ordinal).Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));var built=new Builder(project,"portable").Build();Output(built,"Supervision Helper memory/Worker lineage/chief authority/epoch recovery/no duplicates/cleanup PASS");
  File.AppendAllText(Path.Combine(f.Root,"packs","worker-tasks","Command.csbody"),"\n// owning lifecycle implementation locality\n");var changed=new Builder(project,"portable").Build();Sequence(new[]{"Confectory.WorkerTasks::CommandBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
  File.AppendAllText(Path.Combine(sample,"Provider.csbody"),"\n// configured provider remains replaceable\n");var provider=new Builder(project,"portable").Build();Sequence(new[]{"Example.Supervision::Provider"},Strings(provider,"statistics","compiledImplementations"));Equal(0,Strings(provider,"statistics","compiledContracts").Length);
  string storage=Path.Combine(f.Root,"durable-crash");var command=Strings(provider,"run");using var crash=Start(command,"crash",storage);try{string? ready=crash.StandardOutput.ReadLineAsync().WaitAsync(TimeSpan.FromSeconds(15)).GetAwaiter().GetResult();Equal("CRASH_READY",ready);crash.Kill(entireProcessTree:true);True(crash.WaitForExit(5000),"private fixture process did not exit");}finally{if(!crash.HasExited)crash.Kill(entireProcessTree:true);}
  string file=Path.Combine(storage,"project-a","tasks.json");var before=JsonNode.Parse(File.ReadAllText(file))!;string worker=before["tasks"]!["crash"]!["worker"]!.GetValue<string>();Equal("running",before["tasks"]!["crash"]!["status"]!.GetValue<string>());
  using var recovered=Start(command,"inspect-crash",storage);var stdout=recovered.StandardOutput.ReadToEndAsync();var stderr=recovered.StandardError.ReadToEndAsync();try{System.Threading.Tasks.Task.WhenAll(stdout,stderr).WaitAsync(TimeSpan.FromSeconds(15)).GetAwaiter().GetResult();}catch{if(!recovered.HasExited)recovered.Kill(entireProcessTree:true);throw;}string output=stdout.Result;string error=stderr.Result;True(recovered.WaitForExit(15000)&&recovered.ExitCode==0,error+output);True(output.Contains("process restart retains lineage without replay PASS",StringComparison.Ordinal));var after=JsonNode.Parse(File.ReadAllText(file))!;Equal(worker,after["tasks"]!["crash"]!["worker"]!.GetValue<string>());Equal("interrupted",after["tasks"]!["crash"]!["status"]!.GetValue<string>());
  var windows=new Builder(project,"windows").Build();True(Strings(windows,"includedPacks").Contains("Confectory.WorkerTasks"));var android=new Builder(project,"android").Build();True(Strings(android,"includedPacks").Contains("Confectory.Agent")); // managed compilation only
 }
 private static Process Start(string[] command,string mode,string storage)
 {
  var info=new ProcessStartInfo(command[0]){UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true};foreach(string arg in command.Skip(1))info.ArgumentList.Add(arg);info.Environment["CONFECTORY_SUPERVISION_MODE"]=mode;info.Environment["CONFECTORY_SUPERVISION_DIR"]=storage;return Process.Start(info)??throw new Exception("Failed to start private fixture");
 }
}
