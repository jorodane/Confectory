using System.Diagnostics;
using Confectory.Core;

namespace Confectory.Tests;

public sealed class EngineTests : TestCase
{
    public void test_role_composition_two_windows_and_cleanup()
    {
        string sample=Path.Combine(f.Root,"engine-sample");
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","engine"),sample);
        foreach(string pack in new[]{"project-entry","runtime-base","realtime-update","render-input","base-ui","ui-navigation","window","project-manager","project-execution","file-stream","schema-editing","edit-workspace","save","change-set","element-view","source-editor","agent","helper","worker-tasks"})
            Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",pack),Path.Combine(f.Root,"packs",pack));
        string project=Path.Combine(sample,"project.cpack");
        File.WriteAllText(project,File.ReadAllText(project)
            .Replace("../../packs/","../packs/",StringComparison.Ordinal)
            .Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));
        File.WriteAllText(Path.Combine(f.Root,"packs","agent","Provider.csbody"),"unselected invalid provider");
        var report=new Builder(project,"portable").Build();
        True(!Strings(report,"includedPacks").Contains("Confectory.Agent")&&!Strings(report,"includedPacks").Contains("Confectory.Helper")&&!Strings(report,"includedPacks").Contains("Confectory.WorkerTasks"),"Optional AI packs cannot become engine prerequisites");
        Equal("Confectory.Engine::Main",Text(report,"entry"));
        Sequence(new[]{"Confectory.BaseUI","Confectory.ChangeSet","Confectory.EditWorkspace","Confectory.ElementView","Confectory.Engine","Confectory.FileStream","Confectory.ProjectEntry","Confectory.ProjectExecution","Confectory.ProjectManager","Confectory.RealTimeUpdate","Confectory.RenderInput","Confectory.RuntimeBase","Confectory.Save","Confectory.SchemaEditing","Confectory.SourceEditor","Confectory.UINavigation","Confectory.Window"},Strings(report,"includedPacks"));
        var cached=new Builder(project,"portable").Build();
        Equal(0,Strings(cached,"statistics","compiledImplementations").Length);
        File.AppendAllText(Path.Combine(f.Root,"packs","base-ui","Labels.csbody"),"\n// provider-only locality probe\n");
        var changed=new Builder(project,"portable").Build();
        Sequence(new[]{"Confectory.BaseUI::LabelsBody"},Strings(changed,"statistics","compiledImplementations"));
        Equal(0,Strings(changed,"statistics","compiledContracts").Length);
        var command=Strings(changed,"run");
        for(int repeat=0;repeat<3;repeat++)
        {
            var start=new ProcessStartInfo(command[0]){RedirectStandardOutput=true,RedirectStandardError=true,UseShellExecute=false};
            foreach(var arg in command.Skip(1))start.ArgumentList.Add(arg);
            // Native font/shaping cold start is outside the scripted interaction latency assertion.
            start.Environment["CONFECTORY_BASEUI_CLOSE_AFTER_MS"]="1500";
            start.Environment["CONFECTORY_BASEUI_SCRIPTED"]="1";
            bool gui=OperatingSystem.IsWindows()||(OperatingSystem.IsLinux()&&!string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISPLAY")));
            using var process=Process.Start(start)!;
            if(!process.WaitForExit(10000)){process.Kill(true);throw new Exception("Engine did not stop");}
            var stdout=process.StandardOutput.ReadToEnd();var stderr=process.StandardError.ReadToEnd();
            if(gui){True(!stderr.Contains("Fontconfig error: No writable cache directories",StringComparison.Ordinal),stderr);Equal(0,process.ExitCode);True(stdout.Contains("two-window isolation/reopen PASS",StringComparison.Ordinal),stdout+stderr);}
            else {Equal(1,process.ExitCode);True(stderr.Contains("Cannot open X11 display",StringComparison.Ordinal),stderr);}
        }
        if(!OperatingSystem.IsWindows() && !(OperatingSystem.IsLinux() && !string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISPLAY")))) Skip("Native runtime requires Windows or Linux DISPLAY; managed/negative assertions ran only");
    }
}
