$ErrorActionPreference = 'Stop'
$EditorRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Set-Location $EditorRoot
$EditorDotnet = if ($env:CONFECTORY_DOTNET) { $env:CONFECTORY_DOTNET } else { 'dotnet' }
if ($env:CONFECTORY_DOTNET) { $env:PATH = (Split-Path $EditorDotnet) + [IO.Path]::PathSeparator + $env:PATH }
$env:CONFECTORY_EDITOR_REPO = $EditorRoot
& $EditorDotnet build Confectory.sln -c Release
if ($LASTEXITCODE -ne 0) { throw 'Solution build failed' }
New-Item -ItemType Directory -Force '.confectory' | Out-Null
$EditorReply = & $EditorDotnet 'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll' build 'examples/editor/project.cpack' windows
if ($LASTEXITCODE -ne 0) { throw ($EditorReply -join "`n") }
$EditorReply | Set-Content -Encoding utf8 '.confectory/editor-launch.json'
$EditorReport = ($EditorReply -join "`n") | ConvertFrom-Json
if (-not $EditorReport.tool.ok) { throw 'Editor managed target build failed' }
& $EditorDotnet (Join-Path $EditorReport.output 'Confectory.App.dll')
if ($LASTEXITCODE -ne 0) { throw "Editor exited with $LASTEXITCODE" }
