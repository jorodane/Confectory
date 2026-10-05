using System.Diagnostics;
using Confectory.Core;
namespace Confectory.Tests;
public sealed class ProjectExecutionTests : TestCase
{
 public void test_execution_handles_and_provider_locality()
 {
  string sample=Path.Combine(f.Root,"execution-sample"),pack=Path.Combine(f.Root,"packs","project-execution");
  Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","project-execution"),sample);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","project-execution"),pack);
  string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/project-execution/pack.cpack","../packs/project-execution/pack.cpack",StringComparison.Ordinal).Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));
  var first=new Builder(project,"portable").Build();
  string? host=Environment.GetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST"),repo=Environment.GetEnvironmentVariable("CONFECTORY_TEST_REPO");
  try
  {
   Environment.SetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST",Path.Combine(Fixture.Repo,"targets","project-execution-host","bin","Release","net8.0","Confectory.ProjectExecutionHost.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_REPO",Fixture.Repo);
   var result=Processes.Run(Strings(first,"run"),timeoutSeconds:120);Equal(0,result.ExitCode);True(result.Stdout.Contains("ProjectExecution lifecycle PASS",StringComparison.Ordinal),result.Stderr);var cached=new Builder(project,"portable").Build();Equal(0,Strings(cached,"statistics","compiledImplementations").Length);
   File.AppendAllText(Path.Combine(pack,"Observe.csbody"),"\n// provider-only locality check\n");var changed=new Builder(project,"portable").Build();Sequence(new[]{"Confectory.ProjectExecution::ObserveBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
   var android=new Builder(project,"android").Build();var catalog=System.Text.Json.Nodes.JsonNode.Parse(File.ReadAllText(Text(android,"publicCatalog")))!;
   foreach(string id in new[]{"Confectory.ProjectExecution::LaunchBody","Confectory.ProjectExecution::CapabilitiesBody"})Equal("android",catalog["implementations"]!.AsArray().Single(x=>x!["id"]!.GetValue<string>()==id)!["bodySelection"]!.GetValue<string>());
  }
  finally{Environment.SetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_REPO",repo);}
 }
}
