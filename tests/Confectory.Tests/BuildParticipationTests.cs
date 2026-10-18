using Confectory.Core;
namespace Confectory.Tests;
public sealed class BuildParticipationTests : TestCase
{
 public void test_home_confirmed_inclusion_matches_build_without_registry_count_body_reads_or_execution()
 {
  System.Text.Json.Nodes.JsonNode Query(){var run=Processes.Run(new[]{Processes.DotNet(),Path.Combine(Fixture.Repo,"targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll")},System.Text.Json.JsonSerializer.Serialize(new{operation="catalog",project=f.Project,request=new{action="inclusion"}}));Equal(0,run.ExitCode);return System.Text.Json.Nodes.JsonNode.Parse(run.Stdout)!["result"]!;}
  // An unused registered pack and an unused unreadable declaration cannot be counted or loaded.
  string dormant=f.Add("Unused","object","Dormant","not parsed");File.WriteAllText(dormant,new string('x',1048577));f.Sync();
  var first=Query();Equal("project",first["kind"]!.ToString());Equal("App",first["namespace"]!.ToString());Sequence(f.Packs["App"].Dependencies.Keys.Order(StringComparer.Ordinal),first["requirements"]!.AsArray().Select(row=>row!["namespace"]!.ToString()));Equal("available",first["packsStatus"]!.ToString());Equal(3,first["packs"]!.GetValue<int>());True(!Directory.Exists(Path.Combine(f.Packs["App"].Root,".confectory")),"summary wrote project storage");
  string body=Path.Combine(f.Packs["App"].Root,"main.csbody"),bodyText=File.ReadAllText(body);File.WriteAllText(body,"invalid source is not read or executed by inclusion");Equal(3,Query()["packs"]!.GetValue<int>());File.WriteAllText(body,bodyText);
  var built=new Builder(f.Project,"portable").Build();Sequence(Strings(built,"includedPacks"),first["targets"]![1]!["included"]!.AsArray().Select(x=>x!.ToString()));
  File.WriteAllText(Path.Combine(f.Packs["Provider"].Root,"ValueBody.celem"),"invalid reached declaration");Equal("unavailable",Query()["status"]!.ToString());
  File.WriteAllText(Path.Combine(f.Packs["Provider"].Root,"ValueBody.celem"),new string('x',1048577));Equal("unavailable",Query()["status"]!.ToString());
  f.Add("Provider","implementation","ValueBody","implementation Provider::ValueBody for Api::Value (int n) -> int { body common \"value.csbody\"; }");f.Add("Unused","object","Dormant","object Unused::Dormant {}");f.Packs["App"].Dependencies["Unused"]="1";f.Main("provide Api::Value with Provider::ValueBody; use object Unused::Dormant;");f.Sync();
  Equal(4,Query()["packs"]!.GetValue<int>());f.Entry=null;f.Sync();Equal("unsupported",Query()["packsStatus"]!.ToString());
 }
 public void test_generic_outputs_pure_discovery_usage_closure_and_retention()
 {
  f.NewPack("UI");f.Add("UI","function","Paint","function UI::Paint () -> string { provide UI::Paint with UI::PaintBody; }");f.Add("UI","implementation","PaintBody","implementation UI::PaintBody for UI::Paint () -> string { body common \"paint.csbody\"; }");f.Body("UI","paint.csbody","return \"client UI\";");f.Packs["App"].Dependencies["UI"]="1";
  f.Add("App","function","Client","function App::Client () -> int { provide App::Client with App::ClientBody; }");f.Add("App","implementation","ClientBody","implementation App::ClientBody for App::Client () -> int { import UI::Paint as Paint () -> string; body common \"client.csbody\"; }");f.Body("App","client.csbody","Console.WriteLine(calls.Paint.Invoke());return 0;");f.Add("App","function","Service","function App::Service () -> int { provide App::Service with App::ServiceBody; }");f.Add("App","implementation","ServiceBody","implementation App::ServiceBody for App::Service () -> int { body common \"service.csbody\"; }");f.Body("App","service.csbody","Console.WriteLine(\"non-UI output\");return 0;");f.Sync();
  string sample=Path.Combine(f.Root,"outputs-sample");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","build-participation"),sample);foreach(string name in new[]{"schema-editing","build-participation"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",name),Path.Combine(f.Root,"packs",name));
  string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/",StringComparison.Ordinal).Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));string[] names={"CONFECTORY_ELEMENT_AUTHORING_HOST","CONFECTORY_TEST_AUTHOR_PROJECT","CONFECTORY_TEST_TOOL"};var old=names.Select(Environment.GetEnvironmentVariable).ToArray();
  try
  {
   Environment.SetEnvironmentVariable(names[0],Path.Combine(Fixture.Repo,"targets","element-authoring","bin","Release","net10.0","Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable(names[1],f.Project);Environment.SetEnvironmentVariable(names[2],f.ToolPath);
   var built=new Builder(project,"portable").Build();var result=Processes.Run(Strings(built,"run"),timeoutSeconds:180);True(result.ExitCode==0,result.Stderr+result.Stdout);True(result.Stdout.Contains("BuildParticipation pure discovery/multi-output closure/retention PASS",StringComparison.Ordinal),result.Stderr);
   File.AppendAllText(Path.Combine(f.Root,"packs","build-participation","Describe.csbody"),"\n// plan-only provider edit\n");var changed=new Builder(project,"portable").Build();PackRebuilt(changed, new[]{"Confectory.BuildParticipation::DescribeBody"});Equal(0,Strings(changed,"statistics","compiledContracts").Length);
  }
  finally{for(int i=0;i<names.Length;i++)Environment.SetEnvironmentVariable(names[i],old[i]);}
 }
}
