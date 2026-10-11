using System.Diagnostics;
namespace Confectory.Tests;
public sealed class WindowsLauncherTests : TestCase
{
    public void test_actual_cmd_menu_spaces_repeat_unsupported_error_and_environment_scope()
    {
        if(!OperatingSystem.IsWindows())Skip("CMD/Windows PowerShell unavailable; static layout tests are not Windows execution evidence");
        string root=Path.Combine(f.Root,"launcher 한글 spaces & bang!"),scripts=Path.Combine(root,"scripts");Directory.CreateDirectory(root);
        File.Copy(Path.Combine(Fixture.Repo,"Confectory.bat"),Path.Combine(root,"Confectory.bat"));Fixture.CopyTree(Path.Combine(Fixture.Repo,"scripts"),scripts);
        string wrapper=Path.Combine(root,"probe.cmd");File.WriteAllText(wrapper,"@echo off\r\nsetlocal DisableDelayedExpansion\r\nset \"CONFECTORY_UI=parent-sentinel\"\r\ncall \"%~dp0scripts\\windows\\developer-tools.bat\"\r\necho PARENT_SCOPE=%CONFECTORY_UI%\r\nexit /b 0\r\n",System.Text.Encoding.ASCII);
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
    public void test_actual_cmd_default_entry_failure_without_menu()
    {
        if(!OperatingSystem.IsWindows())Skip("CMD/Windows PowerShell unavailable; direct entry requires Windows");
        string root=Path.Combine(f.Root,"direct 한글 spaces & bang!");Directory.CreateDirectory(root);
        File.Copy(Path.Combine(Fixture.Repo,"Confectory.bat"),Path.Combine(root,"Confectory.bat"));
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"scripts"),Path.Combine(root,"scripts"));
        var start=new ProcessStartInfo(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.System),"cmd.exe"))
        {
            UseShellExecute=false,RedirectStandardInput=true,RedirectStandardOutput=true,RedirectStandardError=true,
            WorkingDirectory=f.Root,Arguments="/d /v:off /s /c \"\""+Path.Combine(root,"Confectory.bat")+"\"\""
        };
        start.Environment["CONFECTORY_DOTNET"]=Path.Combine(root,"missing-sdk.exe");start.Environment["CONFECTORY_NO_PAUSE"]="1";
        using var process=Process.Start(start)!;var output=process.StandardOutput.ReadToEndAsync();var error=process.StandardError.ReadToEndAsync();
        process.StandardInput.Close();
        if(!process.WaitForExit(45000)){process.Kill(true);throw new TimeoutException("Direct Windows entry");}
        string text=output.GetAwaiter().GetResult()+error.GetAwaiter().GetResult();Equal(1,process.ExitCode);
        True(!text.Contains("Choose")&&!text.Contains("Not implemented"),text);
        var logs=Directory.GetFiles(Path.Combine(root,".confectory","launcher-logs"));Equal(1,logs.Length);
        string log=File.ReadAllText(logs[0]);True(log.Contains("Action: editor")&&log.Contains("not found"),log);
    }
    public void test_windows_powershell_parser_and_reserved_assignments()
    {
        if(!OperatingSystem.IsWindows())Skip("Windows PowerShell parser unavailable");
        string probe=Path.Combine(f.Root,"parse-launchers.ps1");
        File.WriteAllText(probe,"""
            param([string]$Scripts)
            $ErrorActionPreference = 'Stop'
            $reserved = @('HOME','Host','PID','PSHOME','PSScriptRoot','PSCommandPath','PSVersionTable','PSEdition','ShellId','ExecutionContext','true','false','null','Error','input','args','PSBoundParameters','PSCmdlet','MyInvocation')
            foreach ($file in Get-ChildItem -LiteralPath $Scripts -Filter *.ps1 -Recurse) {
                $tokens = $null; $parseErrors = $null
                $tree = [System.Management.Automation.Language.Parser]::ParseFile($file.FullName, [ref]$tokens, [ref]$parseErrors)
                if ($parseErrors.Count) { throw ($parseErrors | Out-String) }
                $writes = $tree.FindAll({ param($node)
                    $node -is [System.Management.Automation.Language.AssignmentStatementAst] -or
                    $node -is [System.Management.Automation.Language.ForEachStatementAst] -or
                    $node -is [System.Management.Automation.Language.ParameterAst]
                }, $true)
                foreach ($write in $writes) {
                    $target = if ($write -is [System.Management.Automation.Language.AssignmentStatementAst]) { $write.Left }
                        elseif ($write -is [System.Management.Automation.Language.ForEachStatementAst]) { $write.Variable }
                        else { $write.Name }
                    foreach ($variable in $target.FindAll({ param($node) $node -is [System.Management.Automation.Language.VariableExpressionAst] }, $true)) {
                        $variableName = ($variable.VariablePath.UserPath -split ':')[-1]
                        if ($reserved -contains $variableName) { throw "Reserved variable assignment: $($file.FullName): $variableName" }
                    }
                }
            }
            """);
        var start=new ProcessStartInfo("powershell.exe"){UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true};
        foreach(string arg in new[]{"-NoProfile","-ExecutionPolicy","Bypass","-File",probe,"-Scripts",Path.Combine(Fixture.Repo,"scripts","windows")})start.ArgumentList.Add(arg);
        using var process=Process.Start(start)!;var output=process.StandardOutput.ReadToEndAsync();var error=process.StandardError.ReadToEndAsync();
        if(!process.WaitForExit(45000)){process.Kill(true);throw new TimeoutException("PowerShell AST checks");}
        string text=output.GetAwaiter().GetResult()+error.GetAwaiter().GetResult();True(process.ExitCode==0,text);
    }

}
