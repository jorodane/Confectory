# Checkpoint 4 — independent editor self-edit and pack management

Dedicated local branch `integration/checkpoint-4`, preserving Checkpoint 3 `4dbb7d7`. Final native self-edit and the complete relevant suite pass. Existing Checkpoint 1 remains `73d793fdd9784a447780cc1e01bd7155a3a15370`.

## Runnable workflows

- PackManager consumer: explicit local pin update; version mismatch warning; hooks by public function ID, priority then ordinal tie order; failed hook retains working selection; journal restore/retry skips successful hooks. Optional registration and usage differ. Removal preserves old sources and user saves. SDK artifact source-only pinning explicitly unsupported.
- BuildParticipation consumer: generic plan with distinct entries and `linux`/`portable` outputs. Reachable UI exists only in the client output. Discovery/validation work with the target executable removed; explicit Build invokes compiler. Failed output retains the previous whole-plan receipt and immutable artifacts.
- SourceEditor consumer: arbitrary caller-supplied multiline C# body actually builds/runs; arbitrary function contract is parser/link checked; Save/reopen recovers drafts; Confirm acknowledgement prevents stale draft resurrection. Revision conflict preserves the buffer.
- Engine: F2 opens selected source/declaration, F3 applies a draft, Escape cancels, F4 selects all. D Save, W Save/close/restore, F Confirm selected, G Confirm all, V draft preview. E remains explicitly a preset demonstration. H opens the explicitly configured self ProjectPack; Y independently launches the confirmed engine source through ProjectExecution. A retains its loaded implementation. Native close/reopen retains text buffers; owner shutdown releases buffers/workspaces/children.

## Reproduction

Use installed .NET SDK; do not download tools or accept Android licenses implicitly.

```bash
export CONFECTORY_DOTNET=/workspace/toolchains/dotnet-8.0.425/dotnet
export DOTNET_CLI_HOME=/tmp/confectory-dotnet
export CONFECTORY_ELEMENT_AUTHORING_HOST="$PWD/targets/element-authoring/bin/Release/net8.0/Confectory.ElementAuthoring.dll"
export CONFECTORY_PROJECT_EXECUTION_HOST="$PWD/targets/project-execution-host/bin/Release/net8.0/Confectory.ProjectExecutionHost.dll"
"$CONFECTORY_DOTNET" build Confectory.sln -c Release --no-restore
DISPLAY=:97 "$CONFECTORY_DOTNET" tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll
python3 tests/gui/self_edit_prepare.py /tmp/confectory-self-edit-check
DISPLAY=:97 python3 tests/gui/self_edit_x11_spotcheck.py /tmp/confectory-self-edit-check/editor-A.json /tmp/confectory-self-edit-check
```

`:97` requires a live X11 server. Setup refuses to replace existing source and creates a consumer-local copy. It pins ElementView through public PackManager, retaining the bootstrap target externally. Cold engine validation explicitly permits at most fifteen minutes; engine jobs remain asynchronous and owner-cancellable. Optional screenshot argument stays outside Git.

## Separate acceptance gates

Functional tests and exact provider/zero-contract locality assertions are separate. New public contract/tool changes legitimately revalidate shared consumer closures; body-only edits must not cause wholesale provider recreation. See `CHECKPOINT_4_WORK_LOG.md` for exact outcomes and outside reads/edits.

Windows native acceptance of the earlier STATIC-class correction and new text input remains pending; Linux ABI shim is not Windows OS coverage. Android workload exists but Google SDK/license, adb/full JDK are unavailable. Managed selection/capability tests do not prove APK/device/native authoring. Android touch, surface and app lifetime remain explicit existing contracts; desktop multiwindow and app-owned surface behavior are distinct. No compiler self-hosting or full editor claim.

## Final evidence

Final complete suite on Checkpoint 4 code: **95 passed, 0 failed; 915.010 seconds**. Command: the installed SDK running `tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll` with DISPLAY=:97. This includes the corrected Android provider assertion and final workspace-switch fix. Earlier 94/1 plus focused evidence is superseded by this complete pass. Final Engine consumer separately passed 1/1 (172.817s), including three actual X11 scripted repeats.

Actual X11 self-edit passes arbitrary native text input, project-local pin ownership, Save/restore/selected Confirm, unchanged loaded A versus user-authored A-prime, separate immutable loaded artifact paths, A-prime opening a different project then its own engine source, failed draft/source/artifact retention, unapplied-buffer close/reopen and owner/child cleanup. Screenshot was visually inspected locally; it shows the changed ElementView applied to an ordinary function, not a table-owned model. Screenshots/logs/binaries remain outside Git. Prior actual mixed camera/input, control, resize, repeat, close/reopen and SIGINT checks pass.

Final Linux and Windows engine targets compile. The workspace-switch fix rebuilt exactly Confectory.Engine::MainBody and zero contracts in both the self engine and Windows target. A project switch closes/recreates only the affected ElementView projection because Bind can change an element ID within its existing workspace, not replace its workspace. Stable windows/runtime models/controls survive; actual X11 checks verify it.

Outstanding gates: corrected native Windows acceptance and native text/IME UX; Android Google SDK/full JDK/license prerequisites, APK/device run and native authoring/app execution; source-plus-artifact pin packaging for SDK packs. The complete specification was already verified: all twenty sections via eighteen official bounded reads. Original binary transfer is not an outstanding specification-reading gap. Existing explicit authorization permits ordinary public source/docs/tests publication and safe main integration; the earlier local-only restriction is superseded. Binaries/images/secrets/raw chat/original documents remain excluded.

Windows spot check stays asynchronous: run `run-authoring-windows.bat`, use O/A to attach a project, J to select a declaration/body, F2/F3 for user text, D/W for recovery and F for selected Confirm. Check both native windows, button isolation, shifted typing, close/reopen, mixed camera sources and final shutdown. Record launcher output and exact environment if it fails; Linux compilation/shim does not replace this gate.
