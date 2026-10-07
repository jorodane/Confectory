# Confectory C# build core

A .NET 8 build core for **ProjectPack + target**. It resolves namespace-qualified pack elements, generates C# contracts, compiles owned implementations locally, and links actual providers through a build-target pack. The core, CLI, target tool and tests are implemented in C#; Python is not required. Runtime and UI are assembled from ordinary packs, including the current small draft-authoring slice. Full editor, physics and mod loading are later packs.

Read [technical design](docs/TECHNICAL_DESIGN.md), [requirement-to-test map](docs/REQUIREMENT_TEST_MAP.md), [declaration format and tool protocol](docs/FORMAT.md), [verification evidence](docs/VERIFICATION.md), and [mod extension boundary](docs/MOD_EXTENSION_BOUNDARY.md).

New projects use `project.cproj`; legacy `.cpack` paths remain supported. Packs declare independent execution capability separately from host readiness, and all packs can be opened/edited. [Project file entry](docs/PROJECT_FILE_ENTRY.md) documents same-instance forwarding, trusted engine startup, Windows Open With registration and platform limits. File opening does not run project code.

The first runtime sample is [Confectory.Window](packs/window/README.md): a reusable single-window contract/provider and an executable ProjectPack. It implements Windows Win32 and Linux X11/XWayland; Linux window creation and close events are executed in tests, while Windows runtime execution remains unverified.

## Run from the repository root

Requirements: the .NET 8 **SDK**. All projects use the .NET standard library and have no external NuGet dependencies; restore works offline with the included `NuGet.Config`. The target pack discovers `dotnet` on PATH; alternatively set `CONFECTORY_DOTNET` to the actual executable (`dotnet.exe` on Windows).

The repository's `global.json` selects the newest installed stable **8.0 SDK** (8.0.100 or later), even when SDK 9/10 is installed beside it. The authoring tool directly uses the selected SDK's Roslyn assemblies, so building it with SDK 10's Roslyn while targeting net8.0 causes CS1705/System.Runtime version conflicts. SDK selection and the target runtime are separate: a .NET 8 runtime/reference pack alone does not provide the SDK. Keep SDK 10 installed; this repository chooses SDK 8 locally. Run `dotnet --list-sdks`, then run `dotnet --version` from this repository and check that it reports `8.0.*`. If no 8.0 SDK appears in the list, building requires an existing/approved .NET 8 SDK installation; no scripts install one automatically. Run the Windows scripts from the updated checkout; both enter the repository before building. See [SDK compatibility fix evidence](docs/SDK8_COMPATIBILITY_FIX.md).

Building the core/CLI/tool/tests or compiling a ProjectPack requires the SDK. Running an already generated application requires only the .NET 8 `Microsoft.NETCore.App` runtime and its `dotnet` host. The CLI starts on that runtime, but build/check/validate use the SDK-dependent target tool. Generated packages are framework-dependent; there is no self-contained distribution. Linux execution with an isolated runtime-only installation is verified in the evidence report.

On Windows, run `build-windows.bat` to build the entire solution in Release. It uses the script's directory, so it can be called from another working directory. It performs only the build and returns the .NET build exit code; it does not install tools or run tests. Outputs are in each project's `bin/Release/net8.0/` directory. The .NET 8 SDK must already be installed.

```sh
dotnet build Confectory.sln -c Release
dotnet tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll
dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/app/project.cpack portable
dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll check examples/app/project.cpack portable Example.App
dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll validate examples/app/project.cpack portable
dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/engine/project.cpack portable
```

Build the solution in **Release** before invoking the CLI: the bundled target declarations locate their owned tool at `targets/dotnet/bin/Release/net8.0/Confectory.Build.DotNet.dll`. Rebuild the solution after changing that tool's C# source. Linux can also use the `linux` target, which selects Linux bodies before common bodies and produces a shell launcher. Tests invoke the actual SDK compiler and generated applications; they fail if the required target tool or SDK is missing.

The CLI prints JSON including a `run` command, included/excluded packs, source-read statistics and compiled/reused artifacts. To compile and execute directly:

```csharp
using Confectory.Core;

var report = new Builder("examples/app/project.cpack", "portable").Build();
var command = report["run"]!.AsArray().Select(x => x!.GetValue<string>()).ToArray();
var result = Processes.Run(command);
Console.Write(result.Stdout);
if (result.ExitCode != 0) throw new Exception(result.Stderr);
```

Add a project reference to `src/Confectory.Core/Confectory.Core.csproj` to use this API from a C# host. `Builder.Check(namespace)` compiles against contracts only; `Builder.Validate()` inspects all registered declarations. `BuildError.Diagnostic` exposes an error code and source location. The CLI preserves the previous JSON report structure and `build`, `check`, `validate` operations; only its invocation changes.

The app prints `Hello Confectory from common` for portable, or `Hello Confectory from linux` for Linux. The old compiler/bootstrap sample is preserved in `examples/build-bootstrap`. `examples/engine` now builds a runnable role-based engine ProjectPack with RuntimeBase, RealTimeUpdate, RenderInput, Window and BaseUI, opening two independent desktop Views. The core is an ordinary C# library but does not yet build itself from pack declarations.

Implementation artifacts are cached per element within their owning pack. A full local check and a final selected subset reuse the same DLLs. Use each pack result's `assemblies` or `implementationArtifacts` to enumerate all DLLs; `assembly`/`reference` are aliases for the first implementation only. `compiledImplementations`, `reusedImplementations` and `targetInvocations` distinguish local compilation from source reads. Final builds still compile bindings and package a fresh output when every local DLL is reused.

Generated state is isolated beneath the selected ProjectPack's `.confectory/`: per-document caches, content-addressed local artifacts and unique final output directories. A failed candidate leaves the previous successful output and `latest.json` intact. Source packs are not modified by builds. C# declaration cache keys are separate from the old Python cache; existing sources need no conversion, and the first C# build creates fresh artifacts. Publication is a separate action.

## Current limits

Contracts support synchronous primitive C# types (`void`, `bool`, `int`, `long`, `float`, `double`, `string`) and one-dimensional arrays. Exact dependency version expectations and `*` are supported; a mismatch warns. The registry chooses a concrete manifest path and never searches for a newer version or rewrites that choice. Versioned imported-pack installation/update management is later pack work.

The initial target pack produces framework-dependent .NET 8 assemblies, portable packaging and a Linux launcher. Windows execution, Android/iOS, native apphosts, signing, AOT and runtime DLL replacement are not verified here. Linux declaration caches use `statx` modification/change times and file identity; where these are unavailable, the requested documents are reread rather than trusting modification time alone. Builds are currently intended for one writer per ProjectPack. Generated bindings compose functions per consumer scope; persistent runtime instance state belongs in runtime packs.

In a restricted environment with a read-only home directory, set `DOTNET_CLI_HOME` to a writable directory before building. If MSBuild worker processes are restricted, use `dotnet build Confectory.sln -c Release -m:1 -p:UseSharedCompilation=false`.

Generic schema/object/view declarations carry owned metadata and graph relationships only; this core does not claim complete product schema/UI semantics. The public catalog describes the linked surface. Whole-project authoring exports, mod build-mode controls and the object-specific external-mod inheritance flag are recorded requirements for their next stage. Compiled C# and target tools are trusted executable code; this bootstrap provides no security sandbox.


## Runnable pack checkpoints

Build `examples/engine/project.cpack` for `windows` (framework-dependent CLR profile), `linux` (launcher), or `portable`. The engine is composed through the same ID/contract pipeline as other projects; the core contains no engine host or UI/platform policies.

```
dotnet build Confectory.sln -c Release
dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/engine/project.cpack windows
```

On Windows, double-click `run-engine-windows.bat` (or invoke it from CMD) to build and launch directly. It keeps failure diagnostics visible; `CONFECTORY_DOTNET` supports a selected host, including paths with spaces. Existing `build-windows.bat` remains build-only. No manual PowerShell/JSON parsing or Python is required. On other platforms, use the general CLI `run <ProjectPack> <target>` command or execute the build report's `run` array. Checkpoint 2 adds per-View Open/Start/Stop/Close project controls and stable execution status. Open project data separately from running gameplay; View/context/execution lifetimes are independent. See [Checkpoint 2 commands and coverage](docs/CHECKPOINT_2.md). Each View also has an independent counter/toggle, persistent controls, resize handling, drag/arrow/wheel/programmatic camera intents, and local subscriptions. Close one View and press R in the remaining View to reopen it without losing its model or recreating the other window. Close both to exit; Ctrl+C cleans up. Linux needs X11/XWayland. Set `CONFECTORY_BASEUI_CLOSE_AFTER_MS=1000` for a bounded run and `CONFECTORY_BASEUI_SCRIPTED=1` for the isolation/reopen probe.

Checkpoint 3 adds shared EditWorkspace drafts, SchemaEditing, versioned local Save/restore, validated selective ChangeSet Confirm and reusable ElementView card/table projections. Double-click `run-authoring-windows.bat`, or set `CONFECTORY_ELEMENT_UI=1` and the explicit authoring-tool path on Linux. Open project data with O, attach with A, create/edit with N/I/E, preview with V, Save/reopen with D/W and Confirm selected/all with F/G. K cycles creation kinds; J cycles selected elements. Draft compile/run stays off the UI thread. Confirm actually writes selected final sources, so use a disposable copied project for acceptance checks. See [Checkpoint 3 commands, behavior and limits](docs/CHECKPOINT_3.md) and [pack gates/access ledger](docs/CHECKPOINT_3_WORK_LOG.md).

Android preparation uses the same common UI/model/camera contracts on one app-owned surface with two logical Views. Managed contracts/body selection and source export are verified; native Android SDK app compilation, APK, emulator and device execution remain explicitly unverified until prerequisites are authorized and installed. See [checkpoint verification](docs/CHECKPOINT_1.md), [roadmap/handoff](docs/ROADMAP_HANDOFF.md), [pack work record](docs/PACK_WORK_LOG.md), and [Android preparation](targets/android-export/README.md). Windows code is compiled but Windows runtime checks remain asynchronous.

Windows Checkpoint 1/2 user acceptance failed; the [scoped native/launcher correction](docs/WINDOWS_NATIVE_FIX.md) is a candidate pending actual Windows recheck. Linux GUI and Win32 ABI/contract tests are separate evidence.
