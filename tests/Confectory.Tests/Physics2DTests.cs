using Confectory.Core;
namespace Confectory.Tests;
public sealed class Physics2DTests : TestCase
{
    public void test_bounded_physics_analytic_worlds_queries_events_changes_timing_and_locality()
    {
        string consumer=Path.Combine(f.Root,"physics verification"),owned=Path.Combine(f.Root,"owned physics");
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","physics-lab"),consumer);
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","physics-2d"),owned);
        string project=Path.Combine(consumer,"verify.cpack");
        File.WriteAllText(project,File.ReadAllText(project).Replace("../../",Fixture.Repo+"/",StringComparison.Ordinal).Replace(Path.Combine(Fixture.Repo,"packs","physics-2d","pack.cpack"),Path.Combine(owned,"pack.cpack"),StringComparison.Ordinal));
        var built=new Builder(project,"linux").Build();
        var run=Processes.Run(Strings(built,"run"),timeoutSeconds:120);
        True(run.ExitCode==0,run.Stdout+run.Stderr);
        True(run.Stdout.Contains("momentum/energy",StringComparison.Ordinal));
        True(run.Stdout.Contains("Physics owner cleanup complete",StringComparison.Ordinal));
        foreach(string key in new[]{"compiledContracts","compiledImplementations"})
            True(!Strings(built,"statistics",key).Any(x=>x.StartsWith("Confectory.Stage::",StringComparison.Ordinal)||x.StartsWith("Confectory.Ballistic2D::",StringComparison.Ordinal)||x.StartsWith("Confectory.Window::",StringComparison.Ordinal)||x.StartsWith("Confectory.Agent::",StringComparison.Ordinal)));
        File.AppendAllText(Path.Combine(owned,"Command.csbody"),"\n// explicit owned Physics policy locality probe\n");
        var changed=new Builder(project,"linux").Build();
        PackRebuilt(changed, new[]{"Confectory.Physics2D::CommandBody"});
        Equal(0,Strings(changed,"statistics","compiledContracts").Length);
    }
    public void test_same_physics_contracts_stage_free_preview_and_two_stage_owned_worlds()
    {
        string consumer=Path.Combine(f.Root,"physics consumers");
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","physics-lab"),consumer);
        string? mode=Environment.GetEnvironmentVariable("CONFECTORY_PHYSICS_MODE");
        try
        {
            Environment.SetEnvironmentVariable("CONFECTORY_PHYSICS_MODE",null);
            foreach(string name in new[]{"project","stages"})
            {
                string project=Path.Combine(consumer,name+".cpack");
                File.WriteAllText(project,File.ReadAllText(project).Replace("../../",Fixture.Repo+"/",StringComparison.Ordinal));
                var built=new Builder(project,"linux").Build();var run=Processes.Run(Strings(built,"run"),timeoutSeconds:120);
                True(run.ExitCode==0,run.Stdout+run.Stderr);
                True(run.Stdout.Contains(name=="project"?"Stage-free Physics preview motion/collision PASS":"Two-stage same Physics contracts collision/isolation/stop/return/close PASS",StringComparison.Ordinal));
                if(name=="project")foreach(string key in new[]{"compiledContracts","compiledImplementations"})
                    True(!Strings(built,"statistics",key).Any(x=>x.StartsWith("Confectory.Stage::",StringComparison.Ordinal)||x.StartsWith("Confectory.ProjectExecution::",StringComparison.Ordinal)||x.StartsWith("Confectory.Ballistic2D::",StringComparison.Ordinal)));
            }
        }
        finally {Environment.SetEnvironmentVariable("CONFECTORY_PHYSICS_MODE",mode);}
    }
}
