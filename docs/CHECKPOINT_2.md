# [Checkpoint 2] Project data and execution handles

`examples/engine/project.cpack` remains an ordinary composed engine ProjectPack. ProjectExecution and ProjectManager are reusable packs, not core/editor-only engine policies. Any ProjectPack can use them, including an engine that is itself edited or produces another editor. Games require only their own declared gameplay entry; opening project data does not run it. Editing/Save/Confirm UI is subsequent work.

## Runnable desktop workflow

On Windows, double-click `run-engine-windows.bat` or run it from CMD. `build-windows.bat` remains build-only. No manual PowerShell commands, JSON parsing, Python or policy change is required. The launcher honors CONFECTORY_DOTNET, quotes paths with spaces, propagates exact build/child failures and keeps failure diagnostics visible (CONFECTORY_NO_PAUSE=1 disables pause).

On Linux, from the repository root with .NET 8 on PATH:

```
export DOTNET_CLI_HOME=/tmp/confectory-dotnet
export CONFECTORY_DOTNET=/workspace/toolchains/dotnet-8.0.425/dotnet
export CONFECTORY_PROJECT_EXECUTION_HOST="$PWD/targets/project-execution-host/bin/Release/net8.0/Confectory.ProjectExecutionHost.dll"
export CONFECTORY_PROJECT_ROOT="$PWD"
"$CONFECTORY_DOTNET" build Confectory.sln -c Release
"$CONFECTORY_DOTNET" src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll run examples/engine/project.cpack linux
```

Each native View has project/status rows and four controls: **Open [O]**, **Start [S]**, **Stop [T]**, **Close [C]**. The bundled Project A and B have independent gameplay entries, not editor entries. Optional CONFECTORY_PROJECT_A/B select explicit ProjectPack paths. No project is automatically loaded when none is configured/opened. Sample gameplay lasts 60 seconds by default; CONFECTORY_PROJECT_DURATION_MS controls a bounded sample duration. Start is idempotent in this UI while its current handle is building/running; the reusable execution API permits multiple independent instances.

Open both projects, then start them. Building happens in owned worker processes while the UI continues pumping/rendering. Status shows building/running/terminal state and stable instance handle prefix. Stop A while B continues. Closing project context A must leave A's execution running; reopening gets a fresh data context. Closing native View A must leave its context/worker alone; press R in B to reopen the View. Close both Views or Ctrl+C to dispose engine-owned managers and stop all remaining owned execution trees. Start without Open reports a visible error. Existing counter/toggle and camera controls remain.

## Lifetimes and capability boundary

ProjectExecution caller-owned session and stable handles abstract desktop process strategy; public capabilities identify available strategy and future inspection/call support. Observe reads a fresh snapshot. Poll delivers each termination once, and Observe retains terminal state. Stop is idempotent and affects only the selected worker tree. Invalid/cross-session handles fail. Session Dispose stops every owned worker; if a stop fails, other stops are attempted and the session is retained for retry. No operation silently edits source.

ProjectManager owns explicit data contexts and an execution session. Open describes metadata without compiling/running code. Select changes active context only. Close only closes data; View close and execution Stop are independent. Manager Dispose has documented stop-on-dispose policy. CreateProject is an explicit local source write into a new directory, staged then atomically moved; existing projects are never overwritten. Engine roles are symmetric: no fixed host/game-guest assumption, no mandatory Helper/multiplayer dependency.

DescribeProject is read-only metadata capability. Runtime inspection and calls are explicitly unavailable future capabilities; AI access will need separate contracts. Runtime calls must not imply source-file modification. Execution of trusted local pack code uses caller permissions; this milestone does not add a sandbox.

## Separate verification gates

Full regression run: **85 passed, 0 failed** in 441.822 seconds, followed by the added general CLI launch check (1 pass) and expanded managed Android capability check (1 pass). Solution build zero warnings/errors. Exact results and measured commands are recorded in CHECKPOINT_2_WORK_LOG.md. Coverage includes independent repeated sessions/context lifetimes, explicit entry/target selection, build errors, stop during build, owner disposal, no implicit project, new project creation/no overwrite, source unchanged, one-time terminal notifications and provider-local rebuilds. Actual Linux X11 controls check A/B, context close while running, native View close/reopen, independent Stop and cleanup. Windows named target and common Win32 code compile; Windows runtime/batch UX checks remain asynchronous and unrun here.

Android uses the same IDs/common manager contracts with an explicit Android Launch/Capabilities override. Managed body selection/compilation is verified. Native app-launch provider is unavailable; it returns a failed stable handle rather than trying desktop process behavior. Native data picker/creation, project-execution strategy, APK/device coverage remain open. Existing Android Activity/bridge API preparation is preserved; it does not imply this project UI has native Android coverage.

Android tools: installed .NET android workload manifest 34.0.43, runtime packs 8.0.31. Google SDK absent; terms approval pending at https://developer.android.com/studio#terms-and-conditions, acceptance via sdkmanager --licenses or AcceptAndroidSDKLicenses=True. Full JDK absent; both official Microsoft download and Eclipse Adoptium API returned HTTP 403. No bypass, credential/security changes or new license acceptance occurred. These setup gaps do not block unrelated pack work.

Reproduce focused actual GUI verification (private capture optional):

```
"$CONFECTORY_DOTNET" src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/engine/project.cpack linux > /tmp/checkpoint2-engine.json
DISPLAY=:97 python3 tests/gui/project_manager_x11_spotcheck.py /tmp/checkpoint2-engine.json /tmp/checkpoint2-ui.png
DISPLAY=:97 "$CONFECTORY_DOTNET" tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll
```

Use an existing X11 session instead of :97 where appropriate. GUI test tooling uses Python locally; Windows application launch does not. Do not add temporary captures/build outputs to Git. User platform spot checks remain asynchronous and do not gate further pack work.

## Windows acceptance correction

Native Windows user acceptance **failed**, including pointer/focus/non-client/paint behavior and the published launcher. A scoped Window-class/backbuffer/launcher correction is documented in [WINDOWS_NATIVE_FIX.md](WINDOWS_NATIVE_FIX.md). Compilation and Linux ABI/shim tests do not establish Windows acceptance; corrected Windows runtime remains pending a focused asynchronous recheck.
