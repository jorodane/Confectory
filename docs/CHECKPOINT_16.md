# Checkpoint16 — bounded project shell

Local branch `integration/checkpoint-16-project-shell` from published CP15 `1f9343fd097c0038d6f664097734166094304b58`. Publication is separately coordinated; no push/merge in this increment. Existing CP15 start/home and independent/legacy validation consumers are retained. `examples/editor` and `run-editor-windows.bat` remain untouched.

## Delivered specification slice

Read original readable baseline v1 section8 project layout and section9/UI02 context rules plus `EDITOR_SPEC_IMPLEMENTATION_MAP.md`. Production EditorHome now shows a center workspace without permanent IDE tooling, a collapsible Agent/Helper/Player sidebar, project-name menu/info/read-only settings/folder/leave, bottom project chat/log tabs with input/latest meaningful line, and bottom-right Run/Stop for the currently selected project's default ProjectPack entry.

`Confectory.ProjectShell` is a new reusable role, not a Core editor host. Its explicit public Create/Command/Snapshot/Close contracts borrow an already-validated project identity and own panel state. It cannot create/open/load projects, access filesystem, execute code or connect a provider. Its standalone model consumer has no EditorHome/ProjectManager/FileStream/AI dependency and validates null/missing/cross-context rejection, isolated drafts/tab/menu/logs and independent lifetime. Existing BaseUI Button/Field/Stack/navigation and render/input/window contracts are sufficient; no generic UI catalog or shared widget body changes.

Project→project-chat direction is enforced. Home constructor/restart has `selected=null,shell=null`; project create/open supplies the active exact context. Stale or null chat intents reject without opening anything. Helper private chat without a project is allowed by the original specification but belongs to its actual optional service; no fake session is created here. Current chat text is an explicitly offline local runtime draft, not a sent message or fake response. No provider/login/account/API selection or connection is attempted.

Model and text are app-owned per context; control surfaces and buffers persist across tab/menu/resize/explicit reopen. Project menu makes covered controls ineligible and suppresses covered workspace text. Serialized filesystem/project jobs stay off the render thread, which draws coherent cached snapshots. Run builds/executes the current final ProjectPack entry, not editor code or implicitly Confirmed metadata drafts. Public Observe/Output drain bounded meaningful logs. Stop/leave target only selected execution; app close joins pending work and disposes all owned shell/text/control/project execution resources. Other explicitly open context models remain isolated.

## Launch and current-source checks

Linux existing SDK8/X11: `bash examples/editor-home/run-home.sh`; this environment can set `CONFECTORY_DOTNET=/workspace/toolchains/dotnet-8.0.425/dotnet`, `DOTNET_CLI_HOME=/tmp/confectory-dotnet`, prepend that SDK directory to PATH and use `DISPLAY=:97` or`:98`. Windows double-click unchanged production launcher `run-home-windows.bat`; asynchronous native checklist below. Settings remain ignored `.confectory/editor-home` or `CONFECTORY_HOME_STORAGE`.

Exact scoped test commands/results and local evidence are appended after final gates. Functional and locality/structure assertions are separate; body-only probes must compile precisely the edited Shell or EditorHome provider and zero contracts. Managed Windows/Android profile compilation is compile-only.

## Remaining bounds and handoff

Read-only settings is a bounded actual information surface; mutable settings need a real public contract. No live Agent/Helper participant binding exists, so counts are genuinely zero; profile/overflow needs real participant data before presentation. Round grievance/count/urgency and upward rounded edge-aware internal navigation are the next coherent original-section8 slice, followed by substantive reusable workspace Element Views. Keep production composition separate from temporary examples/editor; add generic missing behavior only with independent consumers.

Functional layout acceptance is not original visual identity approval. Original logo/subtitle/palette/font/timing assets remain absent; available text/style fallbacks do not claim pixel-faithful restoration. Actual native screenshot inspection identified and fixed text showing through an opaque information menu; final visual gate reruns the current source. No new Library upload is attempted while exact prior CP15 screenshot approval is pending. Screenshots/logs stay /tmp/ignored, not Git.

Android equivalent keeps ProjectShell and context rules but must borrow one app-owned surface with logical regions, granted folder/storage/authoring providers, actual text/IME and touch pointer identity/cancel, pause/resume/surface-replacement cleanup. Existing Android workload is present; javac/JDK, sdkmanager and adb are absent, no installs/licenses performed. No APK/device/lifecycle/touch/IME run claim. Native Windows tools are also absent; retest is asynchronous, not a development gate.

## Completed exact gates and evidence

With existing SDK8 selected (`CONFECTORY_DOTNET=/workspace/toolchains/dotnet-8.0.425/dotnet`, `DOTNET_CLI_HOME=/tmp/confectory-dotnet`, SDK directory on PATH):

```bash
dotnet build Confectory.sln -c Release
DISPLAY=:98 dotnet tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll ProjectShellTests
DISPLAY=:97 dotnet tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll EntryHomeTests
DISPLAY=:98 dotnet tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll test_project_shell_actual_linux_menu_tabs_run_logs_resize_context_and_lifetime
```

Solution0warnings/0errors. New shell4/0 in489.938s, preserved entry/home4/0 in471.918s, final actual GUI/presentation-locality1/0 in154.887s after the visually identified menu text suppression fix. Native Windows and Android managed profiles compile. These are scoped relevant gates, not a claim of a newly rerun full132-case repository suite. No native Windows or APK/device/runtime coverage is inferred.

Functional direction/ownership gate also runs two real final ProjectPack children with distinct contexts: stale/null chat does not select/open/load; draft/Stop/leave stays scoped; explicit reopen restores the correct borrowed context; app restart has no selected project/chat/children. Shared role and consumer body-only rebuild scopes are separately asserted with zero contracts; generic widget/native/Core bodies are unchanged. Native screen inspection verifies the final information overlay and readable960×700/640×520 shell; original artwork/style fidelity remains open.

Logs `/tmp/cp16-{final-shell-tests,home-regression,final-native-visual-tests}.log`; inspected private screenshots `.confectory/cp16-evidence/CP16-project-{chat,info,running,narrow}.png`, original native evidence `/tmp/confectory-project-shell-gui-de23x8yt`. These artifacts are excluded from Git. Prior exact CP15 Library-upload approval remains pending; no retry/new upload. New shell images are a separate local evidence set, not silently added to that approval scope.

Durable next-stage handoff: implement original circular grievance/count/urgency and upward rounded edge-aware internal navigation as one bounded increment with real public domain/context contracts and generic independent consumers only where new shared behavior is necessary. Then bind participant profiles/overflow and substantive reusable Element Views/settings. Keep offline/live-provider status honest and project→chat direction intact. Windows user checks and Android tooling/provider preparation stay asynchronous to independent pack work; publication separately coordinated.
