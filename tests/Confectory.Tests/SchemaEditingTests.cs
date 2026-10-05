using Confectory.Core;
namespace Confectory.Tests;
public sealed class SchemaEditingTests : TestCase
{
 public void test_authoring_preservation_validation_and_locality()
 {
  string sample=Path.Combine(f.Root,"schema-sample"),pack=Path.Combine(f.Root,"packs","schema-editing");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","schema-editing"),sample);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","schema-editing"),pack);
  string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/",StringComparison.Ordinal).Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));
  string? host=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST"),selected=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT");
  try
  {
   Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets","element-authoring","bin","Release","net8.0","Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",f.Project);
   var built=new Builder(project,"portable").Build();var result=Processes.Run(Strings(built,"run"),timeoutSeconds:120);True(result.ExitCode==0,result.Stderr+result.Stdout);True(result.Stdout.Contains("SchemaEditing authoring/preservation/compiler PASS",StringComparison.Ordinal),result.Stderr);
   File.AppendAllText(Path.Combine(pack,"SetValue.csbody"),"\n// local authoring provider change\n");var changed=new Builder(project,"portable").Build();Sequence(new[]{"Confectory.SchemaEditing::SetValueBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
  }
  finally{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",selected);}
 }
}
