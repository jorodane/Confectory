using System.Diagnostics;
using Confectory.Core;
namespace Confectory.Tests;
public sealed class ProjectManagerTests : TestCase
{
 public void test_project_contexts_and_provider_locality()
 {
  string sample=Path.Combine(f.Root,"manager-sample"),pack=Path.Combine(f.Root,"packs","project-execution");
  Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","project-manager"),sample);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","project-execution"),pack);
  Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","project-manager"),Path.Combine(f.Root,"packs","project-manager"));
  Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","file-stream"),Path.Combine(f.Root,"packs","file-stream"));
  string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/",StringComparison.Ordinal).Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));
  var first=new Builder(project,"portable").Build();
  string? host=Environment.GetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST"),repo=Environment.GetEnvironmentVariable("CONFECTORY_TEST_REPO");
  try
  {
   Environment.SetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST",Path.Combine(Fixture.Repo,"targets","project-execution-host","bin","Release","net10.0","Confectory.ProjectExecutionHost.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_REPO",Fixture.Repo);
   var result=Processes.Run(Strings(first,"run"),timeoutSeconds:120);Equal(0,result.ExitCode);True(result.Stdout.Contains("ProjectManager lifecycle PASS",StringComparison.Ordinal),result.Stderr);var cached=new Builder(project,"portable").Build();Equal(0,Strings(cached,"statistics","compiledImplementations").Length);
   File.AppendAllText(Path.Combine(f.Root,"packs","project-manager","Context.csbody"),"\n// provider-only locality check\n");var changed=new Builder(project,"portable").Build();Sequence(new[]{"Confectory.ProjectManager::ContextBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
   var android=new Builder(project,"android").Build();var catalog=System.Text.Json.Nodes.JsonNode.Parse(File.ReadAllText(Text(android,"publicCatalog")))!;
   foreach(string id in new[]{"Confectory.ProjectExecution::LaunchConfiguredBody"})Equal("android",catalog["implementations"]!.AsArray().Single(x=>x!["id"]!.GetValue<string>()==id)!["bodySelection"]!.GetValue<string>());
  }
  finally{Environment.SetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_REPO",repo);}
 }
}
