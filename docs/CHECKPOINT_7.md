# Checkpoint 7: local scoped tools and declared gameplay

Runnable local desktop milestone on integration/checkpoint-7. Ordinary ProjectPacks compose InstantTable, YogiBox, AlgorithmProjection, ExecutionComparison and independent Inventory/Harvest/Recipe/Ballistic2D runtime packs. Core is unchanged. This is a bounded authoring/game workflow, not a full editor, live AI service or complete cross-platform product.

The actual workflow creates a registered resource draft, points a reusable declared plant and ingredient recipe at its ID, confirms through existing ChangeSet validation, then launches two independent game models/windows. Harvest/craft/throw produces actual intermediate 2D motion, landing, a delayed fuse effect and finite expiry. Existing running models are independent snapshots; general live replacement/migration remains separate. Tables borrow EditWorkspace and store definitions only. Closing a table retains drafts; closing the workbench cancels/joins jobs and closes child executions. Element/model semantics remain reusable outside tables.

YogiBox captures explicit IDs/selected metadata and only a bounded owned client region. Ctrl+Y, LookAtYogi, per-item removal, seal/unseal, sealed drag to the explicit local inspector, draft discard and immutable delivered receipts are exercised. No clipboard/arbitrary-file disclosure or external message/model/image service is part of the consumer. Composer text is a local preset; general text/IME widgets and durable recipient retention are unfinished.

AlgorithmProjection explains actual selected C# syntax read-only, binds the function/provider/body revisions and reports stale/invalid syntax. Human functional changes coalesce into completed batches; metadata does not request automatic maintenance; AI-origin callers update their own projection locally. No per-keystroke AI, code generation or semantic-proof claim. Current declaration descriptions/signatures remain the language format.

Comparison owns stable child handles and independent models. Isolated mode clears inherited input; sharing requires an explicit local source. The live shared-input gate proves both games consume each intent ID once in different file snapshots, retain different world IDs, reach their fuse effects and close cleanly. The harness waits for observed simulation phases with a timeout, not a wall-time assumption. Bounded fixed catch-up and display interpolation remain distinct policies.

## Verified gates

- Original complete suite retained across executor recovery: **104 passed, 0 failed, 1697.458s**.
- Strengthened three consumer/locality cases: **3 passed, 0 failed, 310.865s**. Each new pack's selected body rebuilt alone with zero contracts; selected local receiver likewise, unselected default receiver rebuilt nothing.
- Actual Linux game: two close/reopen rounds, intermediate/landing/effect pixels, fuse delay, effect expiry, active-flight SIGINT and owner cleanup.
- Actual Linux workbench: scoped composer actions, shared draft/reopen, new resource/plant/recipe Confirm, read-only source projection, UI response during Confirm, two isolated game surfaces, motion/effect, child cleanup, workbench reopen and projection-job SIGINT cancellation/join.
- Separate live X11 isolated/shared-input execution consumer passes; malformed selected C# reports invalid-syntax without a host crash.
- Win32 callback/paint/lifetime ABI shim: 1 passed, 0 failed. Harvest-game and workbench linux/windows/android-named profiles compile; Windows/Android are **net8.0 managed compilation**, not native acceptance/APK evidence.

Production shared changes are additive Window.Capture/Place, modifier bits in RenderInput.Pump, and existing SchemaEditing inspector metadata/local projection host operation. The work log records actual outside implementation reads, why those reads happened, fixture-only locality edits and rebuild scope; no zero-read claim. No binaries/images/secrets/raw chat logs are tracked.

## Reproduce

Use the already installed SDK and built hosts, with a live X11 DISPLAY for native gates:

```sh
export CONFECTORY_DOTNET=/workspace/toolchains/dotnet-8.0.425/dotnet
export DOTNET_CLI_HOME=/tmp/confectory-dotnet
export CONFECTORY_ELEMENT_AUTHORING_HOST=/workspace/Confectory/targets/element-authoring/bin/Release/net8.0/Confectory.ElementAuthoring.dll
export CONFECTORY_PROJECT_EXECUTION_HOST=/workspace/Confectory/targets/project-execution-host/bin/Release/net8.0/Confectory.ProjectExecutionHost.dll
"$CONFECTORY_DOTNET" build tests/Confectory.Tests/Confectory.Tests.csproj -c Release --no-dependencies --no-restore
"$CONFECTORY_DOTNET" tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll
"$CONFECTORY_DOTNET" tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll Checkpoint7
"$CONFECTORY_DOTNET" src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/projects/harvest-game/project.cpack linux > /tmp/game-build.json
CONFECTORY_GAME_PROJECT=/workspace/Confectory/examples/projects/harvest-game/project.cpack python3 tests/gui/harvest_game_x11_spotcheck.py /tmp/game-build.json
"$CONFECTORY_DOTNET" src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/authoring-workbench/project.cpack linux > /tmp/workbench-build.json
python3 tests/gui/authoring_workbench_x11_spotcheck.py /tmp/workbench-build.json
"$CONFECTORY_DOTNET" src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/execution-comparison/project.cpack portable > /tmp/comparison-build.json
CONFECTORY_COMPARISON_PROJECT=/workspace/Confectory/examples/projects/harvest-game/project.cpack CONFECTORY_COMPARISON_TEST_INPUT=/tmp/owned-shared-input.json python3 -c 'import json,subprocess; subprocess.run(json.load(open("/tmp/comparison-build.json"))["run"],check=True)'
```

The workbench native gate clones the game before authoring. For interactive use, see [workbench instructions](../examples/authoring-workbench/README.md); select rows, edit yield/new resource, Confirm, Run A/B, then H/C/T in either game. Windows spot checks use the windows build profile and locally configured SDK/host paths; verify Ctrl+Y, bounded capture, independent windows, closing and interruption on the actual OS. They remain asynchronous and unrun here.

Android is a required open target gate. No adb/sdkmanager/javac on PATH, the saved JDK directory is empty, SDK/license prerequisites remain absent/pending. No installation or terms acceptance occurred. The appropriate equivalent is one app-owned surface with logical tool/game panels, distinct models/owners, touch/pointer cancellation and pause/resume/surface recreation; desktop process/multiwindow authoring is explicitly unavailable. Its gameplay/authoring app adapter and native packaging/runtime remain unfinished. Named-profile compilation is not an APK.

## Durable next stage

Keep all [earlier incomplete gates and exact local chain](REMAINING_GATES_AND_LOCAL_CHAIN.md). Prioritize general typed/text widgets and inheritance/provenance, app-owned Android provider/export once prerequisites are authorized, safe replacement/migration, broader scene/collision/3D/Mesh, and optional live AI/Helper UI only with applicable service authorization. Preserve source leases, stable instances, explicit sharing and separate functional/locality gates. Do not convert these remaining gates into claimed acceptance.

Local-only scope remains authoritative. No push, publish, merge or external file sharing is authorized by this handoff; denied publication has not been retried. Recovery used the same executor and retained its original test process. Final milestone is identified by its local [Checkpoint 7] commit; read the branch log for its exact hash.
