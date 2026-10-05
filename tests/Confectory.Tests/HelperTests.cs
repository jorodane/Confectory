using Confectory.Core;
namespace Confectory.Tests;
public sealed class HelperTests : TestCase
{
 public void test_persistent_memory_templates_owner_refs_conflict_and_optional_agent_locality()
 {
  string sample=Path.Combine(f.Root,"helper-sample");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","helper"),sample);foreach(string pack in new[]{"helper","agent","file-stream"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",pack),Path.Combine(f.Root,"packs",pack));string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/",StringComparison.Ordinal).Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));File.WriteAllText(Path.Combine(f.Root,"packs","agent","Start.csbody"),"unselected invalid Agent implementation");var built=new Builder(project,"portable").Build();True(!Strings(built,"includedPacks").Contains("Confectory.Agent"));Output(built,"Helper persistent private memory/immutable template/owner refs/storage conflict PASS");
  File.AppendAllText(Path.Combine(f.Root,"packs","helper","Remember.csbody"),"\n// selected memory wrapper locality\n");var changed=new Builder(project,"portable").Build();Sequence(new[]{"Confectory.Helper::RememberBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);File.AppendAllText(Path.Combine(f.Root,"packs","helper","Talk.csbody"),"\n// unselected Helper conversation boundary\n");var excluded=new Builder(project,"portable").Build();Equal(0,Strings(excluded,"statistics","compiledImplementations").Length);
 }
}
