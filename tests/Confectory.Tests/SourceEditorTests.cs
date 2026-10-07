using Confectory.Core;
namespace Confectory.Tests;
public sealed class SourceEditorTests : TestCase
{
 public void test_arbitrary_user_body_contract_edit_recovery_and_locality()
 {
  string sample=Path.Combine(f.Root,"source-sample");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","source-editor"),sample);foreach(string name in new[]{"base-ui","runtime-base","file-stream","schema-editing","edit-workspace","save","change-set","source-editor"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",name),Path.Combine(f.Root,"packs",name));
  string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/",StringComparison.Ordinal).Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));
  string user=Path.Combine(f.Root,"user.csbody");File.WriteAllText(user,"Console.WriteLine(\"user entered \" + (17 * 3)); return 0;");string[] names={"CONFECTORY_ELEMENT_AUTHORING_HOST","CONFECTORY_TEST_AUTHOR_PROJECT","CONFECTORY_USER_SOURCE_FILE"};var old=names.Select(Environment.GetEnvironmentVariable).ToArray();
  try
  {
   Environment.SetEnvironmentVariable(names[0],Path.Combine(Fixture.Repo,"targets","element-authoring","bin","Release","net10.0","Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable(names[1],f.Project);Environment.SetEnvironmentVariable(names[2],user);
   var built=new Builder(project,"portable").Build();var result=Processes.Run(Strings(built,"run"),timeoutSeconds:240);True(result.ExitCode==0,result.Stderr+result.Stdout);True(result.Stdout.Contains("SourceEditor arbitrary user body/contract execution/recovery/stale PASS",StringComparison.Ordinal),result.Stderr);
   File.AppendAllText(Path.Combine(f.Root,"packs","source-editor","Labels.csbody"),"\n// body-only source projection edit\n");var changed=new Builder(project,"portable").Build();Sequence(new[]{"Confectory.SourceEditor::LabelsBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
  }
  finally{for(int i=0;i<names.Length;i++)Environment.SetEnvironmentVariable(names[i],old[i]);}
 }
}
