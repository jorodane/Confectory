# [Checkpoint 1] Runnable pack engine

The runnable desktop engine is `examples/engine/project.cpack`, entry `Confectory.Engine::Main`. It is built through the ordinary ProjectPack graph, generated public contracts, independently compiled providers and actual bindings. Composed packs are RuntimeBase, RealTimeUpdate, RenderInput, Window and BaseUI. The core/CLI/compiler tool remain ordinary .NET bootstrap projects; compiler self-hosting is not claimed. No full editor, AI, multiplayer or physics dependency is included.

Two persistent desktop Views have independent counters/toggles, subscriptions, focus/press state and cameras. A button updates the intended model/View. Value changes redraw without recreating View/native-window instances. Resize recomputes layout. Close one View and press R in the other to reopen only that surface, retaining the model and the other window. Model lifetime, subscription lifetime, native surface lifetime and compiled-code lifetime are separate. Owner/subscription disposal is idempotent and late updates are ignored. Ctrl+C performs cleanup.

Keyboard arrows, drag, wheel and P (programmatic move) queue camera intents. State update precedes camera commit and presentation/render. Picking uses the last actually displayed snapshot. Fixed-step catch-up is accumulated and capped at four steps per engine pump; excess whole steps are dropped/reported, fractional time retained. Display interpolation alpha is a separate output, never an extra simulation update. The UI sample has no interpolated physics scene; its fixed callback is a timing probe. 2D camera semantics are explicit and do not fix future 3D contracts.

## Verification gates

| Gate | Evidence | Limit |
| --- | --- | --- |
| Full C# regressions | 83 passed, 0 failed, 278.288 seconds on final current implementation | Platform-specific runtime limits listed separately |
| New public accessor consumers | EngineTests, BaseUITests, RealTimeUpdateTests, AndroidPreparationTests pass | SDK packaging/native execution remain unverified |
| Runtime owners/subscriptions | 30 repeated isolated-owner/release/reopen cycles; shared-model peer subscriptions | Scalar models and serialized UI thread; no ownership transfer/hot reload |
| Cadence/order/camera | Independent cadence, priority ties, mutation tokens, bounded overflow, fixed boundary, coherent mixed intents/picking | 2D orthographic translation/zoom only |
| Linux real GUI | Actual X11 native windows and pixels; click/outside release/autorepeat/resize/close/reopen/SIGINT probe | X.Org dummy display, Linux x64, ASCII milestone font path; no Wayland |
| Provider locality | RuntimeBase Write, RealTimeUpdate Advance, BaseUI UpdateView/Labels, Android Window Draw edits rebuild only that provider body | Full core graph/cache suite separately validates shared-contract impact |
| Windows named target | Managed common Win32 code compiles in framework-dependent Windows profile | No actual Windows runtime/visual check here |
| Android managed target | Android-specific Pump/Draw/Capabilities bodies and common lifecycle/controls compile; export copies separate artifacts | Linux CLR probes are not native Android execution |
| Android native C# API | Activity, bridge and genuine generated bindings compile against installed Android refs | CS1701 Java.Interop runtime-version warning; no SDK packaging/runtime validation |
| Android SDK app | Source project candidate exported | After workload installation, native build stops XA5300 (Google SDK absent); no APK/emulator/device coverage |

Temporary GUI captures were inspected locally and are not in Git. Actual X11 probe displayed A count 2/camera `(30,25,1.10)` while B stayed count 0/camera `(0,0,1)`; B's native window identity survived A close/reopen. Both normal WM_DELETE_WINDOW close and SIGINT exited successfully with no remaining milestone windows. The final probe command can also generate a private temporary capture; never add it to Git.

## Commands

Run from repository root with .NET 8 SDK on PATH. In the supplied Linux environment:

```
export PATH="/workspace/toolchains/dotnet-8.0.425:$PATH"
export DOTNET_CLI_HOME=/tmp/confectory-dotnet
export CONFECTORY_DOTNET=/workspace/toolchains/dotnet-8.0.425/dotnet
dotnet build Confectory.sln -c Release
DISPLAY=:97 dotnet tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll
dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/engine/project.cpack linux > /tmp/engine-build.json
DISPLAY=:97 python3 tests/gui/engine_x11_spotcheck.py /tmp/engine-build.json
```

An existing X11 session can replace `:97`. This environment's private test display was started with:

```
Xorg :97 -noreset -nolisten tcp -config /workspace/Confectory/docs/window-xorg.conf -logfile /tmp/confectory-xorg.log
```

For Windows spot checks, double-click `run-engine-windows.bat` or run it from CMD:

```
run-engine-windows.bat
```

It builds the solution and runs the engine ProjectPack through the general CLI `run` command. No manual PowerShell command, JSON parsing, Python installation or execution-policy change is needed. Paths with spaces are quoted; `CONFECTORY_DOTNET` selects a specific dotnet executable. Build/runtime failures retain their exit code and pause to keep diagnostics visible. Set `CONFECTORY_NO_PAUSE=1` for unattended use. Existing `build-windows.bat` still only builds.

Check independent increment/toggle in A/B, outside-release cancellation, Enter/Space repeat and Tab focus, resize, combined camera inputs, A close followed by R in B, both-window close and Ctrl+C. Windows/Android user spot checks are asynchronous; record defects and keep independent pack development moving.

Android source preparation:

```
dotnet targets/android-export/bin/Release/net8.0/Confectory.AndroidExport.dll examples/engine-android/project.cpack /absolute/new/android-export
python3 tests/android/compile_api.py /absolute/new/android-export /workspace/toolchains/dotnet-8.0.425
dotnet build /absolute/new/android-export/Confectory.Android.csproj -c Debug
```

The .NET android workload was installed with authorized official-source tooling: manifest `34.0.43/8.0.100`, Mono runtime packs `8.0.31` using SDK `8.0.425`. A normal SDK-project build now fails XA5300 because the Google SDK is absent. Java 21 is only a runtime (no `jar`/`javac`); the official Microsoft JDK 17.0.20.1 download was blocked by HTTP 403. Google SDK download/use requires explicit [SDK license agreement](https://developer.android.com/studio#terms-and-conditions) approval; `sdkmanager --licenses` and `AcceptAndroidSDKLicenses=True` remain pending. No APK/native execution is claimed. See the preparation README for the next setup/build gates.

## Baseline and publication

Complete design baseline version 1 was read in 18 bounded Library text chunks: all 20 sections, lines 1–1029, 44,761 characters. The current extraction renders 39 pages for the same source version reported as 37 pages originally. Readable extraction/per-chunk evidence are private local files outside Git. Original DOCX byte materialization failed at the network proxy; no original-byte hash/verification is claimed.

Source/specifications/tests publication is authorized, superseding the initial local-only restriction. Commits are coherent and remote commits are verified; no force pushes or credential changes. Source history retains the completed window baseline and original compiler bootstrap. Generated binaries/images, original documents, credentials and raw chat logs are excluded. Exact checkpoint commit and remote integration status are reported at completion rather than guessed in this document.
