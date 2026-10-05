using System.Diagnostics;
using Confectory.Core;

namespace Confectory.Tests;

public sealed class EngineTests : TestCase
{
    public void test_role_composition_two_windows_and_cleanup()
    {
        string sample=Path.Combine(f.Root,"engine-sample");
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","engine"),sample);
        foreach(string pack in new[]{"runtime-base","realtime-update","render-input","base-ui","window"})
            Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",pack),Path.Combine(f.Root,"packs",pack));
        string project=Path.Combine(sample,"project.cpack");
        File.WriteAllText(project,File.ReadAllText(project)
            .Replace("../../packs/","../packs/",StringComparison.Ordinal)
            .Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack",StringComparison.Ordinal));
        var report=new Builder(project,"portable").Build();
        Equal("Confectory.Engine::Main",Text(report,"entry"));
        Sequence(new[]{"Confectory.BaseUI","Confectory.Engine","Confectory.RealTimeUpdate","Confectory.RenderInput","Confectory.RuntimeBase","Confectory.Window"},Strings(report,"includedPacks"));
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
            start.Environment["CONFECTORY_BASEUI_CLOSE_AFTER_MS"]="400";
            start.Environment["CONFECTORY_BASEUI_SCRIPTED"]="1";
            bool gui=OperatingSystem.IsWindows()||(OperatingSystem.IsLinux()&&!string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISPLAY")));
            using var process=Process.Start(start)!;
            if(!process.WaitForExit(10000)){process.Kill(true);throw new Exception("Engine did not stop");}
            var stdout=process.StandardOutput.ReadToEnd();var stderr=process.StandardError.ReadToEnd();
            if(gui){Equal(0,process.ExitCode);True(stdout.Contains("two-window isolation/reopen PASS",StringComparison.Ordinal),stdout+stderr);}
            else {Equal(1,process.ExitCode);True(stderr.Contains("Cannot open X11 display",StringComparison.Ordinal),stderr);}
        }
    }
}
