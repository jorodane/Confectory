using Confectory.Core;
namespace Confectory.Tests;
public sealed class EntryHomeNativeDetailsTests : TestCase
{
 public void test_linux_native_home_information_profile_cas_cancel_and_project_input_lifetimes()
 {
  if(string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISPLAY")))Skip("native details need a live X11 display");
  var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"linux").Build();string report=Path.Combine(f.Root,"native-details.json");File.WriteAllText(report,built.ToJsonString());
  var run=Processes.Run(new[]{"python3",Path.Combine(Fixture.Repo,"tests/gui/entry_home_details_x11.py"),report},timeoutSeconds:360);Console.WriteLine(run.Stdout.Trim());True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS native Home information/profile"),run.Stdout+run.Stderr);
 }
 public void test_windows_native_information_and_profile_composition_builds()
 {
  var built=new Builder(Path.Combine(Fixture.Repo,"examples/editor-home/project.cpack"),"windows").Build();True(built["tool"]!["ok"]!.GetValue<bool>());Console.WriteLine("PASS Windows managed native composition compile only; no Windows device run");
 }
}
