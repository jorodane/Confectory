using System.Diagnostics;
using System.Text.Json.Nodes;
using Confectory.Core;
namespace Confectory.Tests;
public sealed class Checkpoint7Tests : TestCase
{
 private string CopyConsumer(string relative,string prefix)
 {
  string sample=Path.Combine(f.Root,"consumer");Fixture.CopyTree(Path.Combine(Fixture.Repo,relative),sample);
  Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs"),Path.Combine(f.Root,"packs"));
  string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace(prefix+"packs/","../packs/",StringComparison.Ordinal).Replace(prefix+"targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));return project;
 }
 private static string Run(JsonObject report,Dictionary<string,string> environment)
 {
  string[] command=Strings(report,"run");var info=new ProcessStartInfo(command[0]){UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true};foreach(string arg in command.Skip(1))info.ArgumentList.Add(arg);foreach(var pair in environment)info.Environment[pair.Key]=pair.Value;info.Environment["CONFECTORY_PROJECT_EXECUTION_HOST"]=Path.Combine(Fixture.Repo,"targets","project-execution-host","bin","Release","net10.0","Confectory.ProjectExecutionHost.dll");
  using var process=Process.Start(info)??throw new Exception("Consumer launch failed");var output=process.StandardOutput.ReadToEndAsync();var error=process.StandardError.ReadToEndAsync();try{System.Threading.Tasks.Task.WhenAll(output,error).WaitAsync(TimeSpan.FromSeconds(180)).GetAwaiter().GetResult();True(process.WaitForExit(5000)&&process.ExitCode==0,error.Result+output.Result);return output.Result;}finally{if(!process.HasExited)process.Kill(entireProcessTree:true);}
 }
 private static string Host=>Path.Combine(Fixture.Repo,"targets","element-authoring","bin","Release","net10.0","Confectory.ElementAuthoring.dll");
 public void test_context_tools_real_workspace_capture_projection_confirm_and_locality()
 {
  string project=CopyConsumer("examples/context-tools","../../");string source=Path.Combine(f.Root,"source");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","projects","authoring"),source);string sourceProject=Path.Combine(source,"project.cpack");File.WriteAllText(sourceProject,File.ReadAllText(sourceProject).Replace("../../../packs/","../packs/",StringComparison.Ordinal).Replace("../../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));
  var built=new Builder(project,"linux").Build();string output=Run(built,new(){["CONFECTORY_CONTEXT_PROJECT"]=sourceProject,["CONFECTORY_ELEMENT_AUTHORING_HOST"]=Host});True(output.Contains("Context tools shared table/semantic capture/",StringComparison.Ordinal));True(output.Contains("batched read-only projection/real Confirm PASS",StringComparison.Ordinal));if(!string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISPLAY")))True(output.Contains("actual scoped pixels",StringComparison.Ordinal));else True(output.Contains("capture not run",StringComparison.Ordinal));
  File.AppendAllText(Path.Combine(f.Root,"packs","instant-table","SetCell.csbody"),"\n// selected owner body locality gate\n");var changed=new Builder(project,"linux").Build();Sequence(new[]{"Confectory.InstantTable::SetCellBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
  foreach(var probe in new[]{("yogi-box","CompleteCapture","Confectory.YogiBox::CompleteCaptureBody"),("algorithm-projection","Provider","Confectory.AlgorithmProjection::ProviderBody")}){File.AppendAllText(Path.Combine(f.Root,"packs",probe.Item1,probe.Item2+".csbody"),"\n// owning context pack locality probe\n");var locality=new Builder(project,"linux").Build();Sequence(new[]{probe.Item3},Strings(locality,"statistics","compiledImplementations"));Equal(0,Strings(locality,"statistics","compiledContracts").Length);}
  File.AppendAllText(Path.Combine(f.Root,"packs","yogi-box","Receive.csbody"),"\n// unselected default receiver exclusion probe\n");var excluded=new Builder(project,"linux").Build();Equal(0,Strings(excluded,"statistics","compiledImplementations").Length);File.AppendAllText(Path.Combine(f.Root,"consumer","Receive.csbody"),"\n// explicitly selected local recipient provider\n");var recipient=new Builder(project,"linux").Build();Sequence(new[]{"Example.ContextTools::Receive"},Strings(recipient,"statistics","compiledImplementations"));Equal(0,Strings(recipient,"statistics","compiledContracts").Length);
 }
 public void test_declared_game_motion_fuse_isolation_repeated_flows_and_locality()
 {
  string project=CopyConsumer("examples/projects/harvest-game","../../../");var built=new Builder(project,"linux").Build();var environment=new Dictionary<string,string>{["CONFECTORY_GAME_PROJECT"]=project,["CONFECTORY_GAME_MODE"]="mechanics-test",["CONFECTORY_ELEMENT_AUTHORING_HOST"]=Host};string output=Run(built,environment);True(output.Contains("Declared harvest recipe ballistic motion fuse interpolation isolation/repeated flows PASS",StringComparison.Ordinal));True(output.Contains("game owner cleanup complete",StringComparison.Ordinal));
  File.AppendAllText(Path.Combine(f.Root,"packs","ballistic-2d","Step.csbody"),"\n// trajectory policy owner locality gate\n");var changed=new Builder(project,"linux").Build();Sequence(new[]{"Confectory.Ballistic2D::StepBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);True(Run(changed,environment).Contains("repeated flows PASS",StringComparison.Ordinal));
  foreach(var probe in new[]{("inventory","Apply","Confectory.Inventory::ApplyBody"),("harvest","Collect","Confectory.Harvest::CollectBody"),("recipe","Craft","Confectory.Recipe::CraftBody")}){File.AppendAllText(Path.Combine(f.Root,"packs",probe.Item1,probe.Item2+".csbody"),"\n// owning runtime pack locality probe\n");var locality=new Builder(project,"linux").Build();Sequence(new[]{probe.Item3},Strings(locality,"statistics","compiledImplementations"));Equal(0,Strings(locality,"statistics","compiledContracts").Length);}
 }
 public void test_execution_comparison_real_isolated_game_handles_and_locality()
 {
  string project=CopyConsumer("examples/execution-comparison","../../");string game=Path.Combine(f.Root,"game");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","projects","harvest-game"),game);string gameProject=Path.Combine(game,"project.cpack");File.WriteAllText(gameProject,File.ReadAllText(gameProject).Replace("../../../packs/","../packs/",StringComparison.Ordinal).Replace("../../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));var built=new Builder(project,"portable").Build();string output=Run(built,new(){["CONFECTORY_COMPARISON_PROJECT"]=gameProject,["CONFECTORY_ELEMENT_AUTHORING_HOST"]=Host});True(output.Contains("Execution comparison actual isolated game models stable handles repeated close/reopen PASS",StringComparison.Ordinal));
  File.AppendAllText(Path.Combine(f.Root,"packs","execution-comparison","Launch.csbody"),"\n// selected comparison routing locality\n");var changed=new Builder(project,"portable").Build();Sequence(new[]{"Confectory.ExecutionComparison::LaunchBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
 }

}
