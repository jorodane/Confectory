using Confectory.Core;
namespace Confectory.Tests;

public sealed class StageTests : TestCase
{
    public void test_optional_stage_lifecycle_isolation_and_owned_policy_locality()
    {
        string consumer=Path.Combine(f.Root,"stage consumer"), owned=Path.Combine(f.Root,"stage pack"), child=Path.Combine(f.Root,"private child");
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","stage-lab"),consumer);
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","stage"),owned);
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","projects","authoring"),child);
        string project=Path.Combine(consumer,"project.cpack"), childProject=Path.Combine(child,"project.cpack");
        File.WriteAllText(project,File.ReadAllText(project).Replace("../../",Fixture.Repo+"/",StringComparison.Ordinal).Replace(Path.Combine(Fixture.Repo,"packs","stage","pack.cpack"),Path.Combine(owned,"pack.cpack"),StringComparison.Ordinal));
        File.WriteAllText(childProject,File.ReadAllText(childProject).Replace("../../../targets/",Fixture.Repo+"/targets/",StringComparison.Ordinal));
        string[] keys={"CONFECTORY_STAGE_CHILD_PROJECT","CONFECTORY_PROJECT_EXECUTION_HOST","CONFECTORY_STAGE_MODE"};
        var saved=keys.Select(Environment.GetEnvironmentVariable).ToArray();
        try
        {
            Environment.SetEnvironmentVariable(keys[0],childProject);
            Environment.SetEnvironmentVariable(keys[1],Path.Combine(Fixture.Repo,"targets","project-execution-host","bin","Release","net10.0","Confectory.ProjectExecutionHost.dll"));
            Environment.SetEnvironmentVariable(keys[2],null);
            var built=new Builder(project,"linux").Build();
            var run=Processes.Run(Strings(built,"run"),timeoutSeconds:120);
            True(run.ExitCode==0,run.Stdout+run.Stderr);
            True(run.Stdout.Contains("prior-state failure",StringComparison.Ordinal));
            True(run.Stdout.Contains("Stage owner cleanup complete",StringComparison.Ordinal));
            File.AppendAllText(Path.Combine(owned,"Command.csbody"),"\n// explicit owned Stage policy locality probe\n");
            var changed=new Builder(project,"linux").Build();
            Sequence(new[]{"Confectory.Stage::CommandBody"},Strings(changed,"statistics","compiledImplementations"));
            Equal(0,Strings(changed,"statistics","compiledContracts").Length);
        }
        finally { for(int i=0;i<keys.Length;i++)Environment.SetEnvironmentVariable(keys[i],saved[i]); }
    }

    public void test_stage_free_preview_has_no_stage_or_execution_dependency()
    {
        string consumer=Path.Combine(f.Root,"stage free preview");
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","stage-lab"),consumer);
        string project=Path.Combine(consumer,"preview.cpack");
        File.WriteAllText(project,File.ReadAllText(project).Replace("../../",Fixture.Repo+"/",StringComparison.Ordinal));
        var built=new Builder(project,"linux").Build();
        string report=built.ToJsonString();
        // Inspect selected IDs rather than manifest registry strings.
        foreach(string key in new[]{"compiledContracts","compiledImplementations"})
            True(!Strings(built,"statistics",key).Any(x=>x.StartsWith("Confectory.Stage::",StringComparison.Ordinal)||x.StartsWith("Confectory.ProjectExecution::",StringComparison.Ordinal)));
        string? prior=Environment.GetEnvironmentVariable("CONFECTORY_STAGE_MODE");
        try { Environment.SetEnvironmentVariable("CONFECTORY_STAGE_MODE",null); var run=Processes.Run(Strings(built,"run"),timeoutSeconds:30);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Stage-free render/camera/bounded ballistic preview PASS",StringComparison.Ordinal)); }
        finally {Environment.SetEnvironmentVariable("CONFECTORY_STAGE_MODE",prior);}
    }
}
