using Confectory.Core;
namespace Confectory.Tests;
public sealed class AgentTests : TestCase
{
 public void test_configured_simulated_stream_cancel_errors_bounds_cleanup_and_locality()
 {
  string sample=Path.Combine(f.Root,"agent-sample");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","agent"),sample);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","agent"),Path.Combine(f.Root,"packs","agent"));string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/",StringComparison.Ordinal).Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));var first=new Builder(project,"portable").Build();var result=Processes.Run(Strings(first,"run"),timeoutSeconds:20);True(result.ExitCode==0,result.Stderr+result.Stdout);True(result.Stdout.Contains("Agent simulated async",StringComparison.Ordinal));
  File.AppendAllText(Path.Combine(sample,"Policy.csbody"),"\n// selected policy locality\n");var policy=new Builder(project,"portable").Build();PackRebuilt(policy, new[]{"Example.Agent::Policy"});Equal(0,Strings(policy,"statistics","compiledContracts").Length);
  File.AppendAllText(Path.Combine(f.Root,"packs","agent","Provider.csbody"),"\n// unselected default provider\n");var unused=new Builder(project,"portable").Build();Equal(0,Strings(unused,"statistics","compiledImplementations").Length);
  File.AppendAllText(Path.Combine(sample,"Provider.csbody"),"\n// selected provider locality\n");var provider=new Builder(project,"portable").Build();PackRebuilt(provider, new[]{"Example.Agent::Provider"});Equal(0,Strings(provider,"statistics","compiledContracts").Length);
  string main=Path.Combine(sample,"Main.celem");File.WriteAllText(main,File.ReadAllText(main).Replace("with Example.Agent::Provider;","with Confectory.Agent::ProviderBody;",StringComparison.Ordinal));File.WriteAllText(Path.Combine(sample,"MainBody.csbody"),"string agent=calls.Open.Invoke(\"{\\\"provider\\\":\\\"unconfigured\\\",\\\"model\\\":\\\"none\\\"}\");string run=calls.Start.Invoke(agent,\"missing\",\"{}\");for(int i=0;i<200;i++){var state=System.Text.Json.Nodes.JsonNode.Parse(calls.Poll.Invoke(run))!;if(state[\"state\"]!.GetValue<string>()==\"error\"){calls.Close.Invoke(agent);Console.WriteLine(\"Unconfigured provider fails explicitly PASS\");return 0;}System.Threading.Thread.Sleep(5);}return 1;");var missing=new Builder(project,"portable").Build();Output(missing,"Unconfigured provider fails explicitly PASS");
 }
 public void test_optional_agent_exclusion()
 {
  Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","agent"),Path.Combine(f.Root,"OptionalAgent"));File.WriteAllText(f.Project,File.ReadAllText(f.Project).Replace("\n}","\nregistry Confectory.Agent \"../OptionalAgent/pack.cpack\";\ndependency Confectory.Agent version \"0.1.0\";\n}",StringComparison.Ordinal));File.WriteAllText(Path.Combine(f.Root,"OptionalAgent","Start.csbody"),"unreachable invalid implementation");var built=Build();True(!Strings(built,"includedPacks").Contains("Confectory.Agent"));Output(built,"5");
 }
}
