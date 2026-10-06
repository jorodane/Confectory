using Confectory.Core;
using System.Text.Json.Nodes;
namespace Confectory.Tests;
public sealed class ProjectShellTests : TestCase
{
    string Consumer(string name)
    {
        string path=Path.Combine(f.Root,"owned "+name);Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples",name),path);
        string shell=Path.Combine(path,"owned project-shell");Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs","project-shell"),shell);
        foreach(string file in Directory.GetFiles(path,"*.cpack"))File.WriteAllText(file,File.ReadAllText(file).Replace("../../",Fixture.Repo+"/",StringComparison.Ordinal).Replace(Path.Combine(Fixture.Repo,"packs","project-shell","pack.cpack"),Path.Combine(shell,"pack.cpack"),StringComparison.Ordinal));return path;
    }
    void OptionalExcluded(JsonObject built)
    {
        foreach(string key in new[]{"registeredPacks","includedPacks"})True(!Strings(built,key).Any(x=>new[]{"Confectory.Editor","Confectory.SourceEditor","Confectory.Agent","Confectory.Helper","Confectory.MultiPlay"}.Contains(x)),"project shell acquired temporary editor or optional AI");
    }
    public void test_project_shell_standalone_context_direction_and_provider_locality()
    {
        string consumer=Consumer("project-shell-model"),project=Path.Combine(consumer,"project.cpack");var built=new Builder(project,"linux").Build();var run=Processes.Run(Strings(built,"run"),timeoutSeconds:120);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("ProjectShell context model:"));
        foreach(string key in new[]{"registeredPacks","includedPacks"})True(!Strings(built,key).Any(x=>new[]{"Confectory.EditorHome","Confectory.ProjectManager","Confectory.FileStream","Confectory.Agent","Confectory.Helper"}.Contains(x)),"model consumer cannot load a project/provider");
        foreach(string body in new[]{"Create","Command","Snapshot","Close"}){File.AppendAllText(Path.Combine(consumer,"owned project-shell",body+".csbody"),"\n// ProjectShell owning provider locality probe\n");var changed=new Builder(project,"linux").Build();Sequence(new[]{"Confectory.ProjectShell::"+body+"Body"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);}
    }
    public void test_project_shell_domain_isolated_execution_no_null_chat_open_and_context_cleanup()
    {
        string consumer=Consumer("editor-home"),project=Path.Combine(consumer,"verify-shell.cpack");var built=new Builder(project,"linux").Build();OptionalExcluded(built);string? previous=Environment.GetEnvironmentVariable("CONFECTORY_EDITOR_REPO");try{Environment.SetEnvironmentVariable("CONFECTORY_EDITOR_REPO",Fixture.Repo);var run=Processes.Run(Strings(built,"run"),timeoutSeconds:300);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Project shell domain:"));}finally{Environment.SetEnvironmentVariable("CONFECTORY_EDITOR_REPO",previous);}
        File.AppendAllText(Path.Combine(consumer,"Command.csbody"),"\n// project execution/context consumer locality probe\n");var changed=new Builder(project,"linux").Build();Sequence(new[]{"Confectory.EditorHome::CommandBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
    }
    public void test_project_shell_actual_linux_menu_tabs_run_logs_resize_context_and_lifetime()
    {
        if(string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISPLAY"))){Console.WriteLine("SKIP native project shell: no actual DISPLAY");return;}
        string consumer=Consumer("editor-home"),project=Path.Combine(consumer,"project.cpack");var built=new Builder(project,"linux").Build();OptionalExcluded(built);string report=Path.Combine(f.Root,"shell native report.json");File.WriteAllText(report,built.ToJsonString());var run=Processes.Run(new[]{"python",Path.Combine(Fixture.Repo,"tests","gui","project_shell_x11.py"),report},timeoutSeconds:240);True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("Project shell actual X11"));
        File.AppendAllText(Path.Combine(consumer,"Main.csbody"),"\n// project shell presentation locality probe\n");var changed=new Builder(project,"linux").Build();Sequence(new[]{"Confectory.EditorHome::MainBody"},Strings(changed,"statistics","compiledImplementations"));Equal(0,Strings(changed,"statistics","compiledContracts").Length);
    }
    public void test_project_shell_windows_android_managed_profiles_compile_only()
    {
        string consumer=Consumer("editor-home");foreach(string target in new[]{"windows","android"}){var built=new Builder(Path.Combine(consumer,"project.cpack"),target).Build();True(built["tool"]!["ok"]!.GetValue<bool>());OptionalExcluded(built);}
    }
}
