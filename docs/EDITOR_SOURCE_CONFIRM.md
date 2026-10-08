# Desktop source review, Confirm and Run — 2026-10-08

The actual editor-home ProjectPack now supports explicit confirmation of one selected existing owned source file. Save remains a local draft operation. Review persists the draft and shows file path, element identity, target, current final text and exact reviewed text. Confirm validates a copied candidate before conditionally committing that revision. Run builds confirmed sources and opens a separate child editor; the parent is not hot-reloaded.

## User checkpoint

Desktop: open an owned project, Edit sources, edit, optionally Save, then Review. Compare both panes and the file/target header. Cancel review retains the draft. Confirm selected validates and applies that exact revision; failures appear in review/status and Logs. Run after successful confirmation; Stop an existing child before running again. Use a private editor-home copy with valid registry paths for self-editing.

External changes, stale tokens, subsequent draft edits and compiler failures prevent confirmation and preserve drafts. Saved drafts survive leave/reopen/restart. Once validation starts controls are busy; cancellation is available before Confirm, not during compilation. Owned close waits for the command worker. Scope is one selected existing owned file, not multi-file/new-declaration authoring.

## Pack and locality ledger

Intended elements: Confectory.PackWorkspace::{Command,CommandBody,SnapshotBody}, Confectory.EditorHome.Model::{Command,CommandBody}, Confectory.EditorHome::{Main,MainBody}. Public function signatures remain unchanged. Command adds review/cancel-review/confirm; Snapshot adds review metadata and confirmation results. Explicit ChangeSet dependencies/provider bindings migrate native/web/browser and verification consumers.

Outside implementation reads: ChangeSet Review/Confirm; FileStream Snapshot/conditional Commit; EditWorkspace Identity/Changes/Accept; Save Write/Acknowledge; SchemaEditing Prepare/Validate; ProjectManager Context/Executions/Launch; ProjectExecution LaunchConfigured/Host; native input/field/owner/UIOrder. These establish baseline hashes, revisions, atomic guards, candidate validation and cleanup. Those implementations and Core were not edited; runtime composition uses public contracts.

Manager Launch lacks per-launch environment settings. Product model therefore composes public Context, Executions and LaunchConfigured with unique CONFECTORY_ENTRY_SCOPE and CONFECTORY_HOME_STORAGE under each selected project's .confectory directory. This generic runnable-pack policy isolates child entry transport/catalog from its parent, with no editor-home identity condition in Core or execution host.

Initial dependency selection compiled 130 contracts/implementations, no full rebuild. Final MainBody/model CommandBody adjustments on Linux/Windows/browser compiled two bodies, linked once and compiled zero contracts. Separate locality assertions require SnapshotBody-only and model CommandBody-only rebuilds with zero contracts; functional gates are independent.

## Verification

SDK /workspace/toolchains/dotnet-10.0.401/dotnet; set CONFECTORY_DOTNET to it and DOTNET_CLI_HOME=/tmp/confectory-dotnet10. Exact commands from repository (dotnet denotes that SDK):

```sh
dotnet build tests/Confectory.Tests/Confectory.Tests.csproj -c Release --nologo
dotnet tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll --require-runtime PackWorkspaceTests project_shell_domain
dotnet src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll build examples/editor-home/project.cpack linux
# Repeat actual-entry build for windows, android, browser.
DISPLAY=:96 CONFECTORY_TEST_EVIDENCE_ROOT=/workspace/confectory-validation-archives CONFECTORY_ENTRY_STORAGE=/tmp/confectory-confirm-entry XDG_CACHE_HOME=/tmp/confectory-confirm-cache python3 tests/gui/editor_confirm_x11.py /tmp/confectory-confirm-linux-final-build.json
python3 tests/web/editor_home_workspace.py /tmp/confectory-confirm-browser-final-build.json
python3 tests/web/editor_home_browser.py /tmp/confectory-confirm-browser-final-build.json
```

Final runtime/locality tests: 3 passed, 0 failed, 0 skipped, 158.016s. Tests-project build: zero warnings/errors. Four actual-entry target builds succeed; Android here is managed compilation, not AAB/device acceptance. Actual Chromium source workflow and input/import/cleanup pass, including acknowledged persistence, reload, 480px layout and ZIP. Browser/Android dynamic Confirm/Run remain capability-disabled.

Actual X11 test passes Save without final writes, exact review panes, cancel/reopen, external-change rejection, invalid compiler retention, interrupted-process restart restoration, successful Confirm, confirmed-source marker in child execution logs, two distinct native editor windows, parent model isolation, Stop and owner cleanup. It edits actual copied 48KB Main through native keyboard input and seeds a controlled owned catalog; it does not test the unresolved GTK chooser. Review screenshot was visually inspected. Post-Run screenshot was black and is not child visual evidence; native window IDs, public model state and execution logs establish the child assertion.

Private evidence: /workspace/confectory-validation-archives/confirm-recovered-gui.log and its named fixture; /tmp/confectory-confirm-recovered-frozen-tests.log; /tmp/confectory-confirm-tests-recovered-build.log; /tmp/confectory-confirm-{linux,windows,browser}-final-build.json; /tmp/confectory-confirm-android-build.json; /tmp/confectory-confirm-browser-recovered-ui.log; /tmp/confectory-confirm-browser-regression.log. No generated sources/binaries/images/raw logs are committed.

## Preserved failures and handoff

Initial missing Review provider/ChangeSet dependency failures were fixed explicitly in consumers. An exact-output test failed on an extra print; new behavioral assertions were retained and the print removed. Concurrent tool rebuild invalidated shell tool-identity locality; isolated frozen-output recheck passed.

First GUI observation limit 180s expired during cold candidate validation. New test observes for 340s against the unchanged 300s authoring limit; native input timing is unchanged. Original fixture is preserved under /workspace/confectory-validation-archives/confirm-first and original failure log /tmp/confectory-confirm-linux-gui.log. Later /tmp quota exhaustion caused sandbox startup failure, compiler bus error and Chromium crash. Completed owned artifacts were moved intact to workspace archives, including Android intermediate obj directories. Failed fixtures remain under confirm-quota-failure. Isolated frozen retries passed without weakening input/failure assertions.

Actual Windows GUI and Android device/IME acceptance remain asynchronous. GTK chooser delivery and original Library DOCX materialization remain unresolved. Next work should address those authorized pack gaps independently; no mobile/browser dynamic compiler, remote development, gamepad, mobile layout, Play upload or signing changes were added. Ordinary integration-branch push is authorized; main merge/deployment are outside scope.
