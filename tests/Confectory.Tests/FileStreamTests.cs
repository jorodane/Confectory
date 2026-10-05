using Confectory.Core;
namespace Confectory.Tests;
public sealed class FileStreamTests : TestCase
{
 public void test_local_io_transactions_and_provider_locality()
 {
  string sample=Path.Combine(f.Root,"io-sample"),pack=Path.Combine(f.Root,"packs","file-stream");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","file-stream"),sample);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","file-stream"),pack);
  string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/",StringComparison.Ordinal).Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));
  var first=new Builder(project,"portable").Build();Output(first,"FileStream local IO/rollback PASS");File.AppendAllText(Path.Combine(pack,"Snapshot.csbody"),"\n// provider-only snapshot edit\n");var changed=new Builder(project,"portable").Build();Sequence(new[]{"Confectory.FileStream::SnapshotBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
  var android=new Builder(project,"android").Build();var catalog=System.Text.Json.Nodes.JsonNode.Parse(File.ReadAllText(Text(android,"publicCatalog")))!;Equal("android",catalog["implementations"]!.AsArray().Single(x=>x!["id"]!.GetValue<string>()=="Confectory.FileStream::CapabilitiesBody")!["bodySelection"]!.GetValue<string>());
 }
}
