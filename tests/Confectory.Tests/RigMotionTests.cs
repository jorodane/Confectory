using Confectory.Core;
namespace Confectory.Tests;
public sealed class RigMotionTests : TestCase
{
    string Consumer()
    {
        string path=Path.Combine(f.Root,"owned rig consumer");
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","rig-lab"),path);
        foreach(string file in Directory.GetFiles(path,"*.cpack"))
            File.WriteAllText(file,File.ReadAllText(file).Replace("../../",Fixture.Repo+"/",StringComparison.Ordinal));
        return path;
    }
    public void test_rig_transform_motion_render_inheritance_and_owned_policy_locality()
    {
        string consumer=Consumer(),owned=Path.Combine(f.Root,"owned rig policy");
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","rig-motion"),owned);
        string project=Path.Combine(consumer,"verify.cpack");
        File.WriteAllText(project,File.ReadAllText(project).Replace(Path.Combine(Fixture.Repo,"packs","rig-motion","pack.cpack"),Path.Combine(owned,"pack.cpack"),StringComparison.Ordinal));
        var built=new Builder(project,"linux").Build();var run=Processes.Run(Strings(built,"run"),timeoutSeconds:120);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("hierarchy, quaternion/duration/Bezier",StringComparison.Ordinal));
        foreach(string key in new[]{"compiledContracts","compiledImplementations"})
            True(!Strings(built,"statistics",key).Any(x=>new[]{"Confectory.Stage::","Confectory.Physics2D::","Confectory.Window::","Confectory.Helper::","Confectory.EditWorkspace::"}.Any(prefix=>x.StartsWith(prefix,StringComparison.Ordinal))));
        File.AppendAllText(Path.Combine(owned,"Command.csbody"),"\n// owned RigMotion locality probe\n");
        var changed=new Builder(project,"linux").Build();
        Sequence(new[]{"Confectory.RigMotion::CommandBody"},Strings(changed,"statistics","compiledImplementations"));
        Equal(0,Strings(changed,"statistics","compiledContracts").Length);
    }
    public void test_independent_preview_and_workspace_save_reload_confirm_owner_cleanup()
    {
        string consumer=Consumer(),asset=Path.Combine(f.Root,"owned authored rig");
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","rig-lab","asset-project"),asset);
        string assetProject=Path.Combine(asset,"project.cpack");
        File.WriteAllText(assetProject,File.ReadAllText(assetProject).Replace("../../../",Fixture.Repo+"/",StringComparison.Ordinal));
        string? host=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST"),mode=Environment.GetEnvironmentVariable("CONFECTORY_RIG_MODE"),selected=Environment.GetEnvironmentVariable("CONFECTORY_RIG_AUTHOR_PROJECT");
        try
        {
            Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets","element-authoring","bin","Release","net8.0","Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable("CONFECTORY_RIG_MODE",null);Environment.SetEnvironmentVariable("CONFECTORY_RIG_AUTHOR_PROJECT",assetProject);
            foreach(string name in new[]{"preview","workbench"})
            {
                var built=new Builder(Path.Combine(consumer,name+".cpack"),"linux").Build();var run=Processes.Run(Strings(built,"run"),timeoutSeconds:240);
                True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains(name=="preview"?"Independent Rig/Motion preview real hierarchy/frame PASS":"actual Confirm, comparison ownership/close/reopen PASS",StringComparison.Ordinal));
                True(run.Stdout.Contains("cleanup complete",StringComparison.Ordinal));
                foreach(string key in new[]{"compiledContracts","compiledImplementations"})
                    True(!Strings(built,"statistics",key).Any(x=>x.StartsWith("Confectory.Stage::",StringComparison.Ordinal)||x.StartsWith("Confectory.Physics2D::",StringComparison.Ordinal)||x.StartsWith("Confectory.Helper::",StringComparison.Ordinal)));
            }
        }
        finally {Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_RIG_MODE",mode);Environment.SetEnvironmentVariable("CONFECTORY_RIG_AUTHOR_PROJECT",selected);}
    }
}
