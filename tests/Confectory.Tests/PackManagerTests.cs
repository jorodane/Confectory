using Confectory.Core;
namespace Confectory.Tests;
public sealed class PackManagerTests : TestCase
{
 public void test_local_pins_hooks_retry_updates_and_provider_locality()
 {
  string sample=Path.Combine(f.Root,"pack-management-sample");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","pack-manager"),sample);foreach(string name in new[]{"file-stream","schema-editing","pack-manager"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",name),Path.Combine(f.Root,"packs",name));
  string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/",StringComparison.Ordinal).Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));
  var names=new[]{"CONFECTORY_ELEMENT_AUTHORING_HOST","CONFECTORY_TEST_AUTHOR_PROJECT","CONFECTORY_TEST_PACK_SOURCE","CONFECTORY_TEST_UNUSED_SOURCE"};var old=names.Select(Environment.GetEnvironmentVariable).ToArray();
  try
  {
   Environment.SetEnvironmentVariable(names[0],Path.Combine(Fixture.Repo,"targets","element-authoring","bin","Release","net10.0","Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable(names[1],f.Project);Environment.SetEnvironmentVariable(names[2],Path.Combine(f.Packs["Api"].Root,"pack.cpack"));Environment.SetEnvironmentVariable(names[3],Path.Combine(f.Packs["Unused"].Root,"pack.cpack"));
   var built=new Builder(project,"portable").Build();var result=Processes.Run(Strings(built,"run"),timeoutSeconds:300);True(result.ExitCode==0,result.Stderr+result.Stdout);True(result.Stdout.Contains("PackManager local pin/update/usage/hooks/retry/preservation PASS",StringComparison.Ordinal),result.Stderr);
   File.AppendAllText(Path.Combine(f.Root,"packs","pack-manager","Inspect.csbody"),"\n// provider-only management edit\n");var changed=new Builder(project,"portable").Build();PackRebuilt(changed, new[]{"Confectory.PackManager::InspectBody"});Equal(0,Strings(changed,"statistics","compiledContracts").Length);
  }
  finally{for(int i=0;i<names.Length;i++)Environment.SetEnvironmentVariable(names[i],old[i]);}
 }
}
