# Checkpoint15 — fresh entry/home composition

Branch `integration/checkpoint-15-entry-home`, base published CP14 `234c246586698d66f4de54c26da96e48901b07c8`. This milestone is local; no new branch push/publication/main merge is performed. `examples/editor` and its original launcher remain the CP13/14 functional validation consumer.

## Delivered slice

Fresh ordinary `Confectory.EditorHome` ProjectPack in `examples/editor-home`, built from the original readable section8 and implementation map rather than the temporary editor screen. Public role contracts compose offline entry/connect presentation/Later, left management sidebar, two-column cards with split New/Open first card, folder browser/pages/validation, required name/error focus and multiline intent, local project create/enter/leave/reopen, persistent metadata and explicit listing removal. Project landing is the bounded handoff; it does not replace the agreed next project-workspace slice with permanently exposed IDE panels.

Shared BaseUI adds only `Grid` (pure row-major viewport layout, caller scroll/columns) with editor-free `Example.GridGame`. Actual visual checks also identified and fixed shared Field unused multiline background using the existing content palette. Button/Field/Stack/navigation/contracts are reused; no UI catalog, special engine/editor core host, optional AI or multiplayer dependency is added. Existing signature/model/Owner lifetimes remain unchanged.

Main retains controls/text tokens and native surface across route/resizes, renders cached model snapshots, serializes filesystem/project commands off the UI thread, joins work and disposes every session/Owner/buffer/control/surface on close or SIGINT. No whole UI reconstruction per frame. Existing ProjectManager validation/no-overwrite and EditWorkspace/Save ProjectInfo draft semantics remain the public project boundary.

## Launch and verification

Linux: `CONFECTORY_DOTNET=/workspace/toolchains/dotnet-8.0.425/dotnet DISPLAY=:98 bash examples/editor-home/run-home.sh` in this environment. Other consumers may use their existing SDK8 with `CONFECTORY_DOTNET` or PATH. Optional `CONFECTORY_HOME_STORAGE` selects owned local settings; default ignored `.confectory/editor-home`.

Windows: double-click `run-home-windows.bat`. Existing `run-editor-windows.bat` is unchanged. See `CHECKPOINT_15_WINDOWS_CHECK.md` for asynchronous native checks. Android requirements/gaps: `CHECKPOINT_15_ANDROID_PLAN.md`.

Exact test commands/results and private Library evidence are appended after final gates. Build command: `dotnet build Confectory.sln -c Release` with SDK8 selected by global.json. Registered new gates are `EntryHomeTests`; affected shared Field consumers are existing FieldTests native/locality and existing EditorTests actual GUI. Raw logs and images remain /tmp/ignored; no binaries/images/secrets/raw chat logs in Git.

## Fidelity limits and next stage

Functional behavior/layout and original visual fidelity are distinct gates. The readable authority contains no original logo asset, exact subtitle, palette/font or animation timing. No asset files were found in the checkout. Current text wordmark/action hint and generic P marker are explicitly functional fallbacks; no pixel-faithful restoration claim. Original DOCX materialization/page-count discrepancy remains inherited (full readable text was read, not original DOCX bytes). Already-connected skip awaits real connection-state contract; no fake connected status or live provider/API/login configuration.

Card removal currently means an explicitly confirmed listing removal retaining project files. Destructive project deletion semantics are unresolved and intentionally not invented. Project workspace, collapsible Agent/Helper/Player profiles/count/overflow, bottom chat/log tabs/input, project menu/settings, grievance/count/urgency, run and rounded upward edge-aware navigation remain the next bounded composition. Keep new production composition and old validation consumer separate. Add generic layout or typed Views only with independent consumers and locality gates; do not grow the temporary test screen or require AI/multiplayer.

Windows native spot checks asynchronous, not a development gate. Android managed compile is not an APK/device/app lifecycle/touch/IME claim; JDK/javac, sdkmanager and adb are absent, no installs/licenses performed. Original artwork is a narrow fidelity blocker, not a reason to stop independent pack development.

## Completed exact gates

With `CONFECTORY_DOTNET=/workspace/toolchains/dotnet-8.0.425/dotnet`, `DOTNET_CLI_HOME=/tmp/confectory-dotnet` and that SDK directory prepended to PATH:

```bash
dotnet build Confectory.sln -c Release
DISPLAY=:98 dotnet tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll EntryHomeTests
DISPLAY=:97 dotnet tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll test_shared_field_editor_free_geometry_input_lifetime_and_provider_locality test_editor_native_designed_create_open_edit_save_review_confirm_run_stop_and_lifetime
dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/editor-home/project.cpack linux > /tmp/cp15-final-home.json
DISPLAY=:98 python tests/gui/entry_home_x11.py /tmp/cp15-final-home.json
```

Results: Release build0warnings/0errors; EntryHomeTests4/0 in410.703s; existing Field+Editor affected tests2/0 in453.344s; additional final actual X11 acceptance passes card pagination/OS folder argument and verified in-flight interrupt as well as pixel/layout checks. Native suite uses existing Xorg displays97/98 with `docs/window-xorg.conf`; no additional tools installed. Locality checks separately prove GridBody/FieldBody/EditorHome MainBody/CommandBody-only rebuilds, zero contract rebuilds for body edits. Fresh selected closure excludes the old Editor/SourceEditor and optional AI/multiplayer. The initial presentation-probe failure from a simultaneous Field edit was corrected with frozen source/owned BaseUI copy; final registered suite is clean.

Private GUI screenshots are retained in `.confectory/cp15-evidence/CP15-{intro,home-card,home-narrow,create}.png`; raw evidence source `/tmp/confectory-entry-home-gui-jcqm4su_`, logs `/tmp/cp15-final-entry-tests.log`, `/tmp/cp15-final-field-editor-tests.log`, `/tmp/cp15-inflight-gui-final.log`. Images/logs are ignored/untracked, not Git deliverables. Library upload was blocked by automatic approval review under the local-only/no-external-sharing scope; no Library saved-file claim or public share. Renewed screenshot-upload approval is needed if that private delivery is desired.

Durable next-stage handoff is `ROADMAP_HANDOFF.md` and the scope/fidelity section above. Keep native Windows/Android user spot checks asynchronous; continue the project-workspace slice independently. Source/model/locality gates passed; original visual identity and native Android provider/tooling gates remain open.
