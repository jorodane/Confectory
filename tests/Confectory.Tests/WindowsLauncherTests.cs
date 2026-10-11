using System.Diagnostics;
namespace Confectory.Tests;
public sealed class WindowsLauncherTests : TestCase
{
    public void test_actual_cmd_menu_spaces_repeat_unsupported_error_and_environment_scope()
    {
        if(!OperatingSystem.IsWindows())Skip("CMD/Windows PowerShell unavailable; static layout tests are not Windows execution evidence");
        string root=Path.Combine(f.Root,"launcher 한글 spaces & bang!"),scripts=Path.Combine(root,"scripts");Directory.CreateDirectory(root);
        File.Copy(Path.Combine(Fixture.Repo,"Confectory.bat"),Path.Combine(root,"Confectory.bat"));Fixture.CopyTree(Path.Combine(Fixture.Repo,"scripts"),scripts);
        string wrapper=Path.Combine(root,"probe.cmd");File.WriteAllText(wrapper,"@echo off\r\nsetlocal DisableDelayedExpansion\r\nset \"CONFECTORY_UI=parent-sentinel\"\r\ncall \"%~dp0Confectory.bat\"\r\necho PARENT_SCOPE=%CONFECTORY_UI%\r\nexit /b 0\r\n",System.Text.Encoding.ASCII);
        var start=new ProcessStartInfo(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.System),"cmd.exe")){UseShellExecute=false,RedirectStandardInput=true,RedirectStandardOutput=true,RedirectStandardError=true,WorkingDirectory=f.Root,Arguments="/d /v:off /s /c \"\""+wrapper+"\"\""};
        start.Environment["CONFECTORY_DOTNET"]=Path.Combine(root,"missing-sdk.exe");start.Environment["CONFECTORY_NO_PAUSE"]="1";
        using var process=Process.Start(start)!;var output=process.StandardOutput.ReadToEndAsync();var error=process.StandardError.ReadToEndAsync();
        process.StandardInput.Write("invalid\n2\n\n6\n0\n3\n\n0\n");process.StandardInput.Close();
        if(!process.WaitForExit(45000)){process.Kill(true);throw new TimeoutException("Windows menu repeat/exit");}
        string text=output.GetAwaiter().GetResult()+error.GetAwaiter().GetResult();Equal(0,process.ExitCode);
        True(text.Contains("Nothing was started")&&text.Contains("Not implemented")&&text.Contains("Action failed (exit 1)"),text);
        True(text.Contains("PARENT_SCOPE=parent-sentinel"),text);True(!Directory.Exists(Path.Combine(root,"targets")),"Unsupported/missing SDK did not build or install anything");
        var logs=Directory.GetFiles(Path.Combine(root,".confectory","launcher-logs"));Equal(1,logs.Length);True(File.ReadAllText(logs[0]).Contains("not found"));
    }
}
