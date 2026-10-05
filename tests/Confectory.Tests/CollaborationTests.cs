using Confectory.Core;
namespace Confectory.Tests;
public sealed class CollaborationTests : TestCase
{
 public void test_two_client_loopback_conflicts_confirm_reconnect_cleanup_and_locality()
 {
  string sample=Path.Combine(f.Root,"collaboration-sample");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","collaboration"),sample);
  foreach(string name in new[]{"file-stream","schema-editing","edit-workspace","save","change-set","multiplay","collaboration-editing"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",name),Path.Combine(f.Root,"packs",name));
  string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/",StringComparison.Ordinal).Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));
  string authored=Path.Combine(f.Root,"authored");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","projects","authoring"),authored);File.WriteAllText(Path.Combine(authored,"project.cpack"),File.ReadAllText(Path.Combine(authored,"project.cpack")).Replace("../../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));
  string? host=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST"),selected=Environment.GetEnvironmentVariable("CONFECTORY_COLLAB_PROJECT");
  try
  {
   Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets","element-authoring","bin","Release","net8.0","Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable("CONFECTORY_COLLAB_PROJECT",Path.Combine(authored,"project.cpack"));var first=new Builder(project,"portable").Build();var output=Processes.Run(Strings(first,"run"),timeoutSeconds:300);True(output.ExitCode==0,output.Stderr+output.Stdout);True(output.Stdout.Contains("Collaboration two-client loopback drafts/conflicts/CAS/reconnect/cleanup PASS",StringComparison.Ordinal),output.Stderr);
   File.AppendAllText(Path.Combine(f.Root,"packs","multiplay","Policy.csbody"),"\n// body-only configurable local transport policy\n");var changed=new Builder(project,"portable").Build();Sequence(new[]{"Confectory.MultiPlay::PolicyBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
   File.AppendAllText(Path.Combine(f.Root,"packs","collaboration-editing","Authorize.csbody"),"\n// body-only authority policy\n");var authority=new Builder(project,"portable").Build();Equal(0,Strings(authority,"statistics","compiledImplementations").Length);File.AppendAllText(Path.Combine(sample,"authority.csbody"),"\n// selected public authority policy only\n");authority=new Builder(project,"portable").Build();Sequence(new[]{"Example.Collaboration::Authority"},Strings(authority,"statistics","compiledImplementations"));Equal(0,Strings(authority,"statistics","compiledContracts").Length);
   var android=new Builder(project,"android").Build();True(Strings(android,"includedPacks").Contains("Confectory.MultiPlay")); // managed compilation only; no Android app/permission/runtime claim
   var windows=new Builder(project,"windows").Build();True(Strings(windows,"includedPacks").Contains("Confectory.CollaborationEditing"));
  }
  finally{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_COLLAB_PROJECT",selected);}
 }
 public void test_offline_build_excludes_registered_optional_multiplay()
 {
  Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","multiplay"),Path.Combine(f.Root,"OptionalMultiPlay"));string manifest=File.ReadAllText(f.Project).Replace("\n}","\nregistry Confectory.MultiPlay \"../OptionalMultiPlay/pack.cpack\";\ndependency Confectory.MultiPlay version \"0.1.0\";\n}",StringComparison.Ordinal);File.WriteAllText(f.Project,manifest);File.WriteAllText(Path.Combine(f.Root,"OptionalMultiPlay","OpenServer.csbody"),"this is deliberately unreachable invalid C#;");var built=new Builder(f.Project,"portable").Build();True(!Strings(built,"includedPacks").Contains("Confectory.MultiPlay"));Output(built,"5");
 }
}
