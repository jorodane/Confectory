# Checkpoint 10: optional reusable Stage foundation

Locally completed optional Stage milestone on integration/checkpoint-10, preserving Checkpoint9 9d1c85bbd562d1ab494b6f2e924c37ba7c202de8. Pack increment 8651b683a641fd9b0370eaa2cc741c4f8a9b25b4; consumer/test increment 408d180e584e9573727cdde9d952281ff329d357. No push, publication, merge, external file transfer, provider calls, tool installation or license acceptance.

## Scope and policies

Confectory.Stage is optional, with RuntimeBase/RealTimeUpdate/ProjectExecution dependencies. Create/Enter/Transition/Stop/Close own per-instance composition token, diagnostic scalar Owner, schedule/clock, scoped subscriptions and explicitly launched execution handles. Snapshot/Epoch/Read/Write/Register/Unregister/Advance/Dispatch/Post/Drain/Subscribe/Poll/Unsubscribe/Launch/Observe are the public operations. Consumer-selectable PrepareResources/StopResources/ReleaseResources/CheckTransition/Event hooks supply concrete worlds/scenes/views. No special engine host, hidden current Stage, forced render/physics/editor dependency or table-owned model.

Transitions choose keep-prior or stop-prior explicitly. Preparation/veto failures leave the active source state valid; mutation from preflight hooks is fenced. Irreversible cleanup failure after target entry reports committed:true rather than falsely claiming rollback. Return policy preserve keeps local resource/model/camera/window identity with a new epoch; forbid prevents return. Stopped owned external workers do not implicitly restart. Stop invalidates callbacks/backlog and retains local resources; Close disposes resources/session/Owner/subscriptions, with closing-state cleanup retry. View unsubscribe does not destroy Stage. Owner-thread mutations, bounded background Post and live-token/epoch dispatch prevent stale callbacks from operating on returned/released state.

RealTimeUpdate defines function/phase/priority/ties and fixed catch-up/drop policy. Stage orders fixed update, variable update, camera, presentation, render. Interpolation does not add physics ticks. Two consumer scenes each own camera queues, projectile context and persistent surface; the same scenes have a Stage-free preview entry. Ballistic2D remains a bounded projectile/fuse demonstration, not acceptance of general 2D/3D physics.

## Functional evidence

Focused Stage regression: **2 passed, 0 failed, 118.885s**. Covers simultaneous model/camera isolation, explicit transitions/preserved and forbidden return, preparation/veto/preflight-mutation failure, wrong-scope View subscription, queued background intent, callback Stop skipping later callbacks, phase fault identity, explicit owned worker stop without harming the other Stage, release failure/retry, repeated close and Owner cleanup. Full frozen-source regression: **111 passed, 0 failed, 1973.653s**, from the retained ignored .confectory/verification-checkpoint10 runner. Source stayed frozen at 408d180e584e9573727cdde9d952281ff329d357 throughout. Exact result/log: /tmp/checkpoint10-full-tests.log. No product source changed after this run.

Actual X11 check on Xorg dummy DISPLAY=:97 (1024x768) passed two persistent 480x280 windows: arrow A only, stop A/B continues, preserved return, stop-prior transition, coexisting reentry, close A/B survives, native close B, fresh run reopen and SIGINT cleanup. Screenshot /tmp/checkpoint10-stage-live.png was visually inspected: both labels/counters/camera identities and differently positioned yellow/blue projectiles visible. Screenshot/logs are outside Git. Initial UI probe found incorrect six-field event offsets/types in the new consumer; corrected and final native probe passed.

## Locality and structure evidence

Provider-only Stage Command.csbody edit compiles **Confectory.Stage::CommandBody only, zero contracts** in a private copied pack/consumer test. This is an explicit shared Stage policy boundary, not semantic isolation of all Stage APIs. No Core, external pack or shared public contract changed. Preview selected packs are exactly Ballistic2D, RealTimeUpdate, RenderInput, Window and Example.StageLab: Stage, RuntimeBase and ProjectExecution are not selected. Stage lab adds Stage/RuntimeBase/ProjectExecution and ProjectExecution's FileStream dependency. Registered dormant packs do not force selected dependencies. Outside reads and reasons are in CHECKPOINT_10_WORK_LOG.md; no external implementation edit.

## Commands and target limits

Set CONFECTORY_DOTNET=/workspace/toolchains/dotnet-8.0.425/dotnet and DOTNET_CLI_HOME=/tmp/confectory-dotnet. Existing SDK and hosts only; no new tools.

```sh
$CONFECTORY_DOTNET build tests/Confectory.Tests -c Release -o .confectory/verification-checkpoint10
$CONFECTORY_DOTNET .confectory/verification-checkpoint10/Confectory.Tests.dll StageTests
$CONFECTORY_DOTNET .confectory/verification-checkpoint10/Confectory.Tests.dll
$CONFECTORY_DOTNET src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/stage-lab/project.cpack linux > /tmp/checkpoint10-stage-build.json
DISPLAY=:97 python3 tests/gui/stage_x11_spotcheck.py /tmp/checkpoint10-stage-build.json
$CONFECTORY_DOTNET src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/stage-lab/preview.cpack linux
```

The same build command passed with project.cpack and preview.cpack for both windows/android named profiles: Stage lab selects 74 contracts and 74 implementations; preview selects 27 and 27 (one newly compiled pair and 26 reused per target). All four report tool.ok=true. These are managed net8.0 Portable compilation, not native Windows execution or APK/runtime coverage. The existing .NET Android workload 34.0.43/8.0.100 is installed. adb/sdkmanager/javac are absent, the selected full JDK directory is empty, and Google SDK/license prerequisites remain unresolved; no install/acceptance attempted. The desktop lab explicitly requires native multiwindow capability. Android needs an app-owned surface consumer, touch/cancel routing and Activity/surface lifecycle policies, with independent logical scene state; no pretend equivalence between desktop windows and Android surfaces.

User desktop spot check: run UI mode, use arrows/S/E/T/B/Q; inspect independent camera/counter, stable return, selected close and Ctrl+C cleanup. Windows/Android asynchronous user checks do not block subsequent independent development. Actual native platform acceptance remains separate.

## Projection timing provenance and next handoff

Checkpoint9's historical 81.6998ms is one SDK-host syntax/projection generation sample for 49455 UTF-8 bytes/characters, 900 conditional branches, 9909 selected-body syntax nodes including wrapper block, and 3603 projected outline nodes. Source-node count was independently collected with existing SDK Roslyn, not remeasurement of historical latency. Each Generate used a new OS process (process/parser/JIT state cold; OS filesystem pages unflushed/already exercised). Timer begins after host startup/request decode and ends before result serialization/persistence. The current full-run sample is 86.5208ms for the same fixture (578852/1283/1880 full/root/delta UTF-8 bytes). These are separate uncontrolled runs, not a controlled warmed-process comparison, cache-flush/variance benchmark or universal-speed claim.

Preserve this optional Stage boundary for the next consumer experiment. General 2D physics/world/contact/layers and 3D/render APIs require explicit domain contracts and independent Stage-free consumers. Render authoring, mod-loader packaging/trust/selection, general typed UI/IME/accessibility, Android native packaging/runtime and eventual Mesh remain open. Do not expand the scalar diagnostic or bounded Ballistic2D example into an unreviewed universal schema. Live providers and external publication remain separately gated. See ROADMAP_HANDOFF.md and REMAINING_GATES_AND_LOCAL_CHAIN.md.

Windows asynchronous UI checkpoint from a local checkout with its already installed .NET SDK:

```powershell
$env:CONFECTORY_STAGE_MODE = 'ui'
$report = dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/stage-lab/project.cpack windows | ConvertFrom-Json
$command = $report.run[0]
$runArgs = @($report.run | Select-Object -Skip 1)
& $command @runArgs
```

Use the generated report's exact run argv. Build the CLI/target first if absent using the repository's normal Release build. Report native window/input/close behavior independently of the managed compile result. Android has no equivalent APK command at this checkpoint because the app-owned surface consumer/SDK packaging prerequisites remain open; do not run a desktop launcher and label it Android acceptance.

## Durable local handoff

All intended local functional/locality/structure and available target gates above passed. The [Checkpoint 10] documentation marker follows the two coherent source/test increments; use `git log integration/checkpoint-10` for its exact hash. Preserved C9 is an ancestor. Only Stage, its consumer examples/tests and documentation changed; existing product packs/Core/target implementations did not. Further broad physics/render/mod-loader policy decisions and unavailable native platform/document-byte gates remain open, not failures concealed by this local checkpoint. No external write was attempted.
