using Confectory.Core;
namespace Confectory.Tests;
public sealed class UINavigationTests : TestCase
{
    public void test_optional_navigation_inventory_input_policy_and_provider_locality()
    {
        string consumer=Path.Combine(f.Root,"owned navigation consumer"),owned=Path.Combine(f.Root,"owned navigation policy");
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","ui-navigation"),consumer);Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","ui-navigation"),owned);
        string project=Path.Combine(consumer,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../",Fixture.Repo+"/",StringComparison.Ordinal).Replace(Path.Combine(Fixture.Repo,"packs","ui-navigation","pack.cpack"),Path.Combine(owned,"pack.cpack"),StringComparison.Ordinal));
        var built=new Builder(project,"linux").Build();var run=Processes.Run(Strings(built,"run"),timeoutSeconds:120);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("same-key priority/consumption/dedup",StringComparison.Ordinal));
        foreach(string key in new[]{"compiledContracts","compiledImplementations"})True(!Strings(built,"statistics",key).Any(x=>x.StartsWith("Confectory.Window::",StringComparison.Ordinal)||x.StartsWith("Confectory.EditWorkspace::",StringComparison.Ordinal)||x.StartsWith("Confectory.Stage::",StringComparison.Ordinal)));
        File.AppendAllText(Path.Combine(owned,"Route.csbody"),"\n// owning navigation policy locality probe\n");var changed=new Builder(project,"linux").Build();Sequence(new[]{"Confectory.UINavigation::RouteBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
    }
}
