# Asynchronous Windows spot check

Use the current integration branch and installed SDK8 (`dotnet --version` inside this repository must return 8.0.*). Keep SDK10 installed if desired. From repository root in PowerShell:

```powershell
dotnet build Confectory.sln -c Release
$cli = Join-Path (Get-Location) 'src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll'
$build = dotnet $cli build examples/ui-navigation/gui.cpack windows | ConvertFrom-Json
$arguments = @($build.run | Select-Object -Skip 1)
& $build.run[0] @arguments
```

In A, Tab opens inventory, F6 moves between basic controls, Tab closes it and restores eligible focus. B should retain its own group/focus. Enter activates once on release. T changes text mode; Tab must remain unconsumed there. Closing A leaves B responsive. Q exits. This checks routing, not inventory model editing or a full text/IME widget. Report target/version and the failing action if it differs from the Linux native gate.

Standalone motion preview:

```powershell
$env:CONFECTORY_RIG_MODE = 'ui'
$build = dotnet $cli build examples/rig-lab/preview.cpack windows | ConvertFrom-Json
$arguments = @($build.run | Select-Object -Skip 1)
& $build.run[0] @arguments
```

Verify visible moving grouped geometry, Space pause, arrows scrub, resize without recreating the window, native close and repeat launch. For authoring, select an owned copy of asset-project; never silently edit the repository sample:

```powershell
$repo = (Get-Location).Path.Replace('\','/')
$owned = Join-Path $env:TEMP ('ConfectoryRig-' + [guid]::NewGuid())
Copy-Item examples/rig-lab/asset-project $owned -Recurse
$project = Join-Path $owned 'project.cpack'
[IO.File]::WriteAllText($project, [IO.File]::ReadAllText($project).Replace('../../../', $repo + '/'))
$env:CONFECTORY_RIG_AUTHOR_PROJECT = $project
$env:CONFECTORY_ELEMENT_AUTHORING_HOST = Join-Path (Get-Location) 'targets/element-authoring/bin/Release/net8.0/Confectory.ElementAuthoring.dll'
$build = dotnet $cli build examples/rig-lab/workbench.cpack windows | ConvertFrom-Json
$arguments = @($build.run | Select-Object -Skip 1)
& $build.run[0] @arguments
```

A/front animates while B/side starts paused. Space/arrows affect only the selected View. H/P/D change parent/pose/duration; L/O change grouped visibility/order; S saves draft, R reloads without changing native window identity, C validates and writes final source/build. Close A and keep B; close/relaunch; interrupt during Confirm and check cleanup. These are user-device checks not yet executed by this Linux worker. They do not block the editor composition plan; failures should be repaired in the owning pack and cross-pack contracts recorded before further dependent expansion.
