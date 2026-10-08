param([string]$Project, [string]$Output, [switch]$Unsigned)
$ErrorActionPreference = 'Stop'
$phase = 'checking prerequisites'
try {
    Add-Type -AssemblyName System.Windows.Forms
    $repo = $PSScriptRoot
    if (!$Project) {
        $picker = New-Object System.Windows.Forms.OpenFileDialog
        $picker.Title = 'Select engine ProjectPack to export (Home: examples/editor-home/project.cpack)'
        $picker.Filter = 'Confectory ProjectPack (*.cproj;*.cpack)|*.cproj;*.cpack'
        $picker.InitialDirectory = Join-Path $repo 'examples'
        try { if ($picker.ShowDialog() -ne 'OK') { exit 2 }; $Project = $picker.FileName } finally { $picker.Dispose() }
    }
    $Project = (Resolve-Path -LiteralPath $Project).Path
    if (!$Output) { $Output = Join-Path $env:LOCALAPPDATA ('Confectory\exports\android-' + [DateTime]::Now.ToString('yyyyMMdd-HHmmss-fff')) }
    $Output = [IO.Path]::GetFullPath($Output)
    if (Test-Path -LiteralPath $Output) { throw 'Output must be a new folder. Previous exports are preserved.' }
    if (!$env:JAVA_HOME -or !(Test-Path -LiteralPath (Join-Path $env:JAVA_HOME 'bin\javac.exe')) -or !(Test-Path -LiteralPath (Join-Path $env:JAVA_HOME 'bin\jar.exe'))) { throw 'Set JAVA_HOME to a full JDK compatible with your Android workload (javac.exe and jar.exe required).' }
    if (!$env:ANDROID_HOME) { $env:ANDROID_HOME = $env:ANDROID_SDK_ROOT }
    if (!$env:ANDROID_HOME -or !(Test-Path -LiteralPath $env:ANDROID_HOME)) { throw 'Set ANDROID_HOME to your installed Android SDK.' }
    $dotnet = 'dotnet'; if ($env:CONFECTORY_DOTNET) { $dotnet = $env:CONFECTORY_DOTNET }
    if (!(Get-Command $dotnet -ErrorAction SilentlyContinue)) { throw 'dotnet was not found. Install the required .NET 10 SDK or set CONFECTORY_DOTNET to its executable.' }
    Write-Host "ProjectPack: $Project"
    Write-Host "Export output: $Output"
    Write-Host 'On failure, read the phase and tool diagnostics below. No credential transcript is recorded.'
    $phase = 'building trusted exporter'
    Write-Host 'Building trusted Confectory exporter. No signing key is created.'
    & $dotnet build (Join-Path $repo 'Confectory.sln') -c Release --nologo
    if ($LASTEXITCODE -ne 0) { [Console]::Error.WriteLine("Failed while ${phase} (exit $LASTEXITCODE). No package success is claimed."); exit $LASTEXITCODE }
    $exporter = Join-Path $repo 'targets\android-export\bin\Release\net10.0\Confectory.AndroidExport.dll'
    if (!(Test-Path -LiteralPath $exporter -PathType Leaf)) { throw "Build did not produce the expected exporter: $exporter" }
    $phase = 'exporting and packaging selected ProjectPack'
    & $dotnet $exporter $Project $Output --package
    if ($LASTEXITCODE -ne 0) { [Console]::Error.WriteLine("Failed while ${phase} (exit $LASTEXITCODE). Partial output may be at: $Output"); exit $LASTEXITCODE }
    Write-Host "Unsigned export: $Output"
    if ($Unsigned) { exit 0 }
    if ((Read-Host 'Sign locally using an EXISTING key? Type SIGN (Enter keeps unsigned output)') -ne 'SIGN') { exit 0 }
    $picker = New-Object System.Windows.Forms.OpenFileDialog
    $picker.Title = 'Select existing local upload/signing keystore (never saved in project settings)'
    $picker.Filter = 'Keystore (*.jks;*.keystore;*.p12;*.pfx)|*.jks;*.keystore;*.p12;*.pfx|All files (*.*)|*.*'
    try { if ($picker.ShowDialog() -ne 'OK') { Write-Host 'Signing cancelled; unsigned output retained.'; exit 2 }; $key = $picker.FileName } finally { $picker.Dispose() }
    # Only the nonsecret selected path is an argument. Passwords are masked in the owned .NET console.
    $phase = 'explicitly requested local signing'
    & $dotnet $exporter --sign-export $Output $key
    exit $LASTEXITCODE
} catch { [Console]::Error.WriteLine("Android export failed while ${phase}: " + $_.Exception.Message); exit 1 }
