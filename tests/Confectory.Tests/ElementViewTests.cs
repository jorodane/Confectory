using Confectory.Core;
namespace Confectory.Tests;
public sealed class ElementViewTests : TestCase
{
 public void test_reusable_shared_card_table_view_lifetimes_and_locality()
 {
  f.Add("App","object","Counter","object App::Counter { value count = 0; }");f.Sync();string sample=Path.Combine(f.Root,"view-sample");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","element-view"),sample);
  foreach(string name in new[]{"file-stream","schema-editing","edit-workspace","element-view"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",name),Path.Combine(f.Root,"packs",name));
  string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/",StringComparison.Ordinal).Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));
  string? host=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST"),selected=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT");
  try
  {
   Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets","element-authoring","bin","Release","net10.0","Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",f.Project);
   var built=new Builder(project,"portable").Build();var result=Processes.Run(Strings(built,"run"),timeoutSeconds:120);True(result.ExitCode==0,result.Stderr+result.Stdout);True(result.Stdout.Contains("ElementView shared card/table persistent lifetime/selection PASS",StringComparison.Ordinal),result.Stderr);
   File.AppendAllText(Path.Combine(f.Root,"packs","element-view","Labels.csbody"),"\n// projection provider locality\n");var changed=new Builder(project,"portable").Build();Sequence(new[]{"Confectory.ElementView::LabelsBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
  }
  finally{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",selected);}
 }
}
