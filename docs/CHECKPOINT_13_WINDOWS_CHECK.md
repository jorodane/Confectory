# Checkpoint13 Windows spot check

For the user-confirmed batch/.NET environment, double-click **run-editor-windows.bat** in the repository root. No terminal, manual cd or PowerShell is needed. Keep its console open during initial pack compilation; the Editor opens when it completes. On failure read the retained window and `.confectory/editor-launch.log`, preferably the first error and last stage. The log remains local/ignored. See [launcher evidence](WINDOWS_EDITOR_LAUNCH_FIX.md). No execution-policy bypass/change or installation is performed.

Optional existing environment settings `CONFECTORY_DOTNET` (full SDK8 dotnet.exe path) and `CONFECTORY_EDITOR_STORAGE` (owned settings folder) are honored; their use is not required in the normal PATH-based double-click flow. The launcher installs nothing. Native Windows is not accepted merely from the successful managed target builds; these user checks are asynchronous and do not block development.

1. Create with name, multiline description and real parent-folder picker. Verify a distinct local ProjectPack and starter Main.
2. Create/select a scalar element, edit source/property, Save, close/relaunch and Open it. Verify restored drafts and unchanged final source until Confirm.
3. Review selected IDs, Confirm valid edits and Run/Stop with output. Invalid C# must preserve final bytes/drafts and report errors while UI responds.
4. Share to the second View; verify independent selection/text input, stable caret/selection, resize, close during Confirm and reopen. Dirty sibling CAS and external-final conflict must retain drafts; explicit recovery must work.
5. Check Tab/Shift+Tab, Enter/Space, pointer pressed/release/cancel, folder/element/Review pages and interruption/child cleanup.

Optional developer check for the same shared BaseUI Button without an editor (CMD, where manual commands are convenient):

```bat
dotnet build Confectory.sln -c Release
set "CONFECTORY_BUTTON_GAME_GUI=1"
dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll run examples/button-game/project.cpack windows
```

Increase/Reset share BaseUI Button presentation/input in two game windows. A changes only A; Tab/Enter/Space activate once; F6 hides Increase; focus loss cancels held activation; closing A leaves B running. Clear it afterward with `set "CONFECTORY_BUTTON_GAME_GUI="`. Record exact OS/SDK/branch SHA, action and visible failure if any. No screenshot/binary upload is required.

Android managed profile compilation is separate evidence. Current environment lacks JDK/javac, SDK manager and adb; native app surface/touch/lifecycle/granted picker/authoring/execution providers and APK/device checks remain open. No tool installation or license acceptance follows from this spot check.
