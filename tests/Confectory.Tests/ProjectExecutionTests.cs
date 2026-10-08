using System.Diagnostics;
using Confectory.Core;
namespace Confectory.Tests;
public sealed class ProjectExecutionTests : TestCase
{
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
