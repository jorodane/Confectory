using System.Diagnostics;
using Confectory.Core;
namespace Confectory.Tests;
public sealed class ProjectManagerTests : TestCase
{
 public void test_offline_creation_template_is_owned_and_desktop_buildable()
 {
  foreach(string role in new[]{"project-manager","project-execution","file-stream"}){string ns=role=="project-manager"?"Confectory.ProjectManager":role=="project-execution"?"Confectory.ProjectExecution":"Confectory.FileStream";string root=Path.Combine(f.Root,role);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",role),root);f.ExtraRegistry[ns]=Path.Combine(root,"pack.cpack");}
  f.Packs["App"].Dependencies["Confectory.ProjectManager"]="0.1.0";
  f.Targets["android"]="Confectory.Build.DotNet::Portable";f.Targets["browser"]="Confectory.Build.DotNet::Portable";
  f.Main("provide Confectory.ProjectManager::CreationTemplate with Confectory.ProjectManager::CreationTemplateBody;");
  f.Add("App","implementation","MainBody","implementation App::MainBody for App::Main () -> int { import Confectory.ProjectManager::CreationTemplate as Template (string, string) -> string[]; body common \"main.csbody\"; }");
  f.Body("App","main.csbody","Console.WriteLine(System.Text.Json.JsonSerializer.Serialize(calls.Template.Invoke(\"Arbitrary.Independent\",\"/absent/repository/pack.cpack\"))); return 0;");f.Sync();
  var build=new Builder(f.Project,"android").Build();var run=Processes.Run(Strings(build,"run"),timeoutSeconds:60);Equal(0,run.ExitCode);var files=System.Text.Json.JsonSerializer.Deserialize<string[]>(run.Stdout.Trim())!;
  var browser=new Builder(f.Project,"browser").Build();var browserRun=Processes.Run(Strings(browser,"run"),timeoutSeconds:60);Equal(0,browserRun.ExitCode);Equal(run.Stdout,browserRun.Stdout);
  string owned=Path.Combine(f.Root,"created-independent");Directory.CreateDirectory(owned);
  for(int i=0;i<files.Length;i+=2){string file=Path.Combine(owned,files[i]);Directory.CreateDirectory(Path.GetDirectoryName(file)!);File.WriteAllText(file,files[i+1]);}
  File.WriteAllText(Path.Combine(owned,"main.celem"),"function Arbitrary.Independent::Main () -> int { provide Arbitrary.Independent::Main with Arbitrary.Independent::MainBody; }");
  File.WriteAllText(Path.Combine(owned,"main_body.celem"),"implementation Arbitrary.Independent::MainBody for Arbitrary.Independent::Main () -> int { body common \"main.csbody\"; }");File.WriteAllText(Path.Combine(owned,"main.csbody"),"return 0;");
  True(File.ReadAllText(Path.Combine(owned,"BUILDING.txt")).Contains("cannot compile or launch"));
  string project=Path.Combine(owned,"project.cproj");bool unavailable=false;try{new Builder(project,"portable").Build();}catch(Exception error){unavailable=error.ToString().Contains("MISSING_TOOL");}True(unavailable,"Unprovisioned compiler must fail explicitly");
  Fixture.CopyTree(Path.GetDirectoryName(f.ToolPath)!,Path.Combine(owned,"build","tools"));var created=new Builder(project,"portable").Build();Equal(0,Processes.Run(Strings(created,"run"),timeoutSeconds:60).ExitCode);
  File.AppendAllText(Path.Combine(f.Root,"project-manager","CreationTemplate.offline.csbody"),"\n// body locality\n");var changed=new Builder(f.Project,"android").Build();PackRebuilt(changed, new[]{"Confectory.ProjectManager::CreationTemplateBody"});Equal(0,Strings(changed,"statistics","compiledContracts").Length);
 }
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
   File.AppendAllText(Path.Combine(f.Root,"packs","project-manager","Context.csbody"),"\n// provider-only locality check\n");var changed=new Builder(project,"portable").Build();PackRebuilt(changed, new[]{"Confectory.ProjectManager::ContextBody"});Equal(0,Strings(changed,"statistics","compiledContracts").Length);
   File.AppendAllText(Path.Combine(f.Root,"packs","project-manager","Open.csbody"),"\n// slot reuse owning-pack locality\n");var reopened=new Builder(project,"portable").Build();PackRebuilt(reopened,new[]{"Confectory.ProjectManager::OpenBody"});Equal(0,Strings(reopened,"statistics","compiledContracts").Length);
   File.AppendAllText(Path.Combine(f.Root,"packs","project-manager","Identity.csbody"),"\n// durable identity owning-pack locality\n");var stableIdentity=new Builder(project,"portable").Build();PackRebuilt(stableIdentity,new[]{"Confectory.ProjectManager::IdentityBody"});Equal(0,Strings(stableIdentity,"statistics","compiledContracts").Length);
   var android=new Builder(project,"android").Build();var catalog=System.Text.Json.Nodes.JsonNode.Parse(File.ReadAllText(Text(android,"publicCatalog")))!;
   foreach(string id in new[]{"Confectory.ProjectExecution::LaunchConfiguredBody"})Equal("android",catalog["implementations"]!.AsArray().Single(x=>x!["id"]!.GetValue<string>()==id)!["bodySelection"]!.GetValue<string>());
  }
  finally{Environment.SetEnvironmentVariable("CONFECTORY_PROJECT_EXECUTION_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_REPO",repo);}
 }
}
