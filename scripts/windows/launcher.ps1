param([ValidateSet('menu','editor','web','build','android','association')][string]$Action = 'editor')
$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
function Read-Choice([string]$Prompt) {
    if ([Console]::IsInputRedirected) { Write-Host ($Prompt + ': ') -NoNewline; return [Console]::ReadLine() }
    return Read-Host $Prompt
}
if ($Action -eq 'menu') {
    # Every selected action runs in a child process. Mode flags cannot leak between selections.
    while ($true) {
        Write-Host "`nConfectory"
        Write-Host '1  Editor - current EditorHome (build tools, then run/open selected file)'
        Write-Host '2  Embedded v196 HTML editor - NOT AVAILABLE (information only)'
        Write-Host '3  Build tools only - no project execution'
        Write-Host '4  Export unsigned Android package - existing Android SDK/JDK required'
        Write-Host '5  Generate file association .reg - review/import manually, no registry changes'
        Write-Host '6  Developer diagnostics (external browser, not the embedded editor)'
        Write-Host '0  Exit'
        $selection = Read-Choice 'Choose'
        if ($null -eq $selection) { exit 0 }
        $chosen = switch ($selection) { '1' {'editor'} '2' {'unavailable'} '3' {'build'} '4' {'android'} '5' {'association'} '6' {'diagnostics'} '0' {'exit'} default {''} }
        if ($chosen -eq 'exit') { exit 0 }
        if (!$chosen) { Write-Host 'Choose 0 through 6. Nothing was started.'; continue }
        if ($chosen -eq 'unavailable') {
            Write-Host 'The generic Windows rendering host exists, but the v196 source port and editor workflows are not available yet.'
            Write-Host 'Not implemented as the default editor. No browser/server/build/install was started.'
            [void](Read-Choice 'Press Enter to return to the menu'); continue
        }
        if ($chosen -eq 'diagnostics') {
            Write-Host '1  External browser WebUI contract probe: object browsing and draft Save only.'
            Write-Host '   Starts a local HTTP host, NOT the embedded HTML editor or full Sites UI.'
            Write-Host '0  Back (no work)'
            if ((Read-Choice 'Diagnostic choice') -ne '1') { continue }
            $chosen = 'web'
        }
        $savedPreference = $ErrorActionPreference
        try {
            $ErrorActionPreference = 'Continue'
            $global:LASTEXITCODE = -1
            & (Join-Path $PSHOME 'powershell.exe') -NoProfile -STA -ExecutionPolicy Bypass -File $PSCommandPath -Action $chosen
            $code = $LASTEXITCODE
        } finally { $ErrorActionPreference = $savedPreference }
        if ($code -eq 2) { Write-Host 'Cancelled. No further action.' }
        elseif ($code -ne 0) { Write-Host "Action failed (exit $code). Diagnostics and log location are above." }
        else { Write-Host 'Action finished.' }
        [void](Read-Choice 'Press Enter to return to the menu')
    }
}
# Child-only environment, including inherited legacy presentation switches.
foreach ($name in @('CONFECTORY_UI','CONFECTORY_WEB_PROJECT','CONFECTORY_BROWSER_PROJECT','CONFECTORY_WINDOWLESS_EDIT','CONFECTORY_ELEMENT_UI')) {
    [Environment]::SetEnvironmentVariable($name, $null, 'Process')
}
$env:CONFECTORY_EDITOR_REPO = $repo
$env:CONFECTORY_ELEMENT_AUTHORING_HOST = Join-Path $repo 'targets\element-authoring\bin\Release\net10.0\Confectory.ElementAuthoring.dll'
$env:CONFECTORY_PROJECT_EXECUTION_HOST = Join-Path $repo 'targets\project-execution-host\bin\Release\net10.0\Confectory.ProjectExecutionHost.dll'
$dotnet = 'dotnet'
if ($env:CONFECTORY_DOTNET) { $dotnet = $env:CONFECTORY_DOTNET }
$log = $null
$failureCode = 1
. (Join-Path $PSScriptRoot 'internal\native-tool.ps1')
function Run-Tool {
    param([string[]]$ToolArguments, [string]$Executable = $dotnet)
    if (!(Get-Command $Executable -CommandType Application -ErrorAction SilentlyContinue)) { throw "Executable not found: $Executable" }
    $toolExit = Invoke-ConfectoryNativeTool -Executable $Executable -ToolArguments $ToolArguments -LogPath $log
    if ($toolExit -ne 0) { $script:failureCode = $toolExit; throw "Tool failed with exit $toolExit. Log: $log" }
}
function Choose-Project {
    if ($env:CONFECTORY_LAUNCH_PROJECT) {
        $path = [IO.Path]::GetFullPath($env:CONFECTORY_LAUNCH_PROJECT)
        if (!(Test-Path -LiteralPath $path -PathType Leaf)) { throw 'The supplied project file does not exist.' }
        return $path
    }
    Add-Type -AssemblyName System.Windows.Forms
    $picker = New-Object System.Windows.Forms.OpenFileDialog
    $picker.Title = 'Select an existing Confectory project to edit (not execute)'
    $picker.Filter = 'Confectory (*.cproj;*.cpack)|*.cproj;*.cpack'
    $picker.InitialDirectory = Join-Path $repo 'examples'
    try { if ($picker.ShowDialog() -ne 'OK') { return $null }; return $picker.FileName } finally { $picker.Dispose() }
}
try {
    Set-Location -LiteralPath $repo
    $project = $null
    if ($Action -eq 'web') { $project = Choose-Project; if (!$project) { exit 2 } }
    $folder = Join-Path $repo '.confectory\launcher-logs'
    [void][IO.Directory]::CreateDirectory($folder)
    $log = Join-Path $folder ($Action + '-' + [DateTime]::Now.ToString('yyyyMMdd-HHmmss-fff') + '-' + $PID + '.log')
    [IO.File]::WriteAllText($log, "Action: $Action`r`n")
    Write-Host "Diagnostics: $log"
    if ($Action -eq 'android') {
        Write-Host 'The exporter reports its phase and export folder; launcher log contains no credentials.'
        Write-Host 'Unsigned export only. No SDK install, signing, key creation or registry modification.'
        Run-Tool -Executable (Join-Path $PSHOME 'powershell.exe') -ToolArguments @('-NoProfile', '-STA', '-ExecutionPolicy', 'Bypass', '-File', (Join-Path $PSScriptRoot 'internal\export-android-windows.ps1'), '-Unsigned')
        exit 0
    }
    if (!(Get-Command $dotnet -ErrorAction SilentlyContinue)) { throw 'Existing dotnet SDK host not found. Set CONFECTORY_DOTNET or PATH; no SDK was installed.' }
    Run-Tool -ToolArguments @('--version')
    Run-Tool -ToolArguments @('build', (Join-Path $repo 'Confectory.sln'), '--configuration', 'Release', '--nologo')
    foreach ($stem in @('targets\desktop-entry\bin\Release\net10.0\Confectory.DesktopEntry', 'src\Confectory.Cli\bin\Release\net10.0\Confectory.Cli', 'targets\dotnet\bin\Release\net10.0\Confectory.Build.DotNet', 'targets\element-authoring\bin\Release\net10.0\Confectory.ElementAuthoring', 'targets\project-execution-host\bin\Release\net10.0\Confectory.ProjectExecutionHost')) {
        foreach ($suffix in @('.dll', '.deps.json', '.runtimeconfig.json')) {
            $required = Join-Path $repo ($stem + $suffix)
            if (!(Test-Path -LiteralPath $required -PathType Leaf)) { throw "Build did not produce expected tool output: $required" }
        }
        if (!$stem.EndsWith('Confectory.Build.DotNet')) {
            $core = Join-Path (Split-Path (Join-Path $repo $stem)) 'Confectory.Core.dll'
            if (!(Test-Path -LiteralPath $core -PathType Leaf)) { throw "Missing tool dependency: $core" }
        }
    }
    foreach ($assembly in @('Microsoft.CodeAnalysis.dll', 'Microsoft.CodeAnalysis.CSharp.dll')) {
        $required = Join-Path $repo ('targets\element-authoring\bin\Release\net10.0\' + $assembly)
        if (!(Test-Path -LiteralPath $required -PathType Leaf)) { throw "Missing authoring dependency: $required" }
    }
    if ($Action -eq 'build') { exit 0 }
    $cli = Join-Path $repo 'src\Confectory.Cli\bin\Release\net10.0\Confectory.Cli.dll'
    $entry = Join-Path $repo 'targets\desktop-entry\bin\Release\net10.0\Confectory.DesktopEntry.dll'
    $confectoryEditorProject = Join-Path $repo 'examples\editor-home\project.cpack'
    if ($Action -eq 'association') {
        $registration = Join-Path $repo '.confectory\Confectory.cproj.reg'
        Run-Tool -ToolArguments @($entry, 'registration-file', $registration, '--repository', $repo)
        Write-Host "Created only: $registration. Review it before manually importing. Existing old associations need this explicit migration."
    } elseif ($Action -eq 'editor') {
        if ($env:CONFECTORY_LAUNCH_PROJECT) { Run-Tool -ToolArguments @($entry, 'open', $env:CONFECTORY_LAUNCH_PROJECT, '--repository', $repo) }
        else { Run-Tool -ToolArguments @($cli, 'run', $confectoryEditorProject, 'windows') }
    } elseif ($Action -eq 'web') {
        $env:CONFECTORY_UI = 'web'
        $env:CONFECTORY_WEB_PROJECT = $project
        Write-Host 'Open the printed http://127.0.0.1 URL in your browser. Keep this host window open.'
        Write-Host 'Close the host with Ctrl+C. If the menu exits too, reopen scripts/windows/developer-tools.bat.'
        Run-Tool -ToolArguments @($cli, 'run', $confectoryEditorProject, 'windows')
    }
    exit 0
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    if ($log) {
        try { [IO.File]::AppendAllText($log, $_.Exception.Message + [Environment]::NewLine) } catch {}
        [Console]::Error.WriteLine("Diagnostics: $log")
    }
    exit $failureCode
}
