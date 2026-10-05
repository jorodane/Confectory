# Checkpoint 6: optional Agent / Helper / Worker runtime

This is a bounded executable pack API milestone, not a complete AI editor or a live model demonstration. Optional Agent, Helper and WorkerTasks are ordinary ProjectPack contracts/providers; the core remains unchanged. Engine registers them for discovery while its normal UI entry excludes all three, even with a broken unreachable Agent implementation. Helper is optional and memory-only consumers exclude Agent entirely.

Agent config registration is distinct from verifying a live account/model connection. Open stores explicit provider/model configuration; Start returns before provider I/O. A consumer-selected Provider integrates open/next/cancel/close. Ordered streaming events, request identities, bounded queues/bytes/deadlines, sanitized errors and owned cancellation/cleanup are real runtime operations. Cleanup retains ownership on failure and supports bounded idempotent retry. Unconfigured default refuses execution. Simultaneous same-request callers create one run, and retired request IDs do not repeat execution.

Helper global identity/private memory and immutable recruitment templates persist independently of project tasks. Profile excludes private memory. Authorized Helper Talk uses a borrowed Agent with Helper identity/context, opens no project and recruits no Worker. Worker has no direct user-chat contract. Actor strings are trusted local application identities; no new authentication/account framework is claimed.

Worker task state preserves project/goal/stage/completion, stable Worker/owning Helper, execution key, checkpoints/verification/remaining work/blockers, and append-only history. Chief directions/recovery use a separate chief journal. Chief can recruit/direct across teams; ordinary current Helpers recruit their own Workers. Augmentation permission is chief-only; augmentation generation is not implemented here.

Supervisor replacement is explicit chief-only after failed/ended disposition, never inferred from slow/unreachable. Immutable recruitment configuration creates a temporary Helper. Controller/Epoch lease changes while task/Worker/run/owner lineage stays intact. Stale supervisors return as observers; explicit current handoff restores authority. Command IDs and callback sequences prevent duplicate application/execution. Agent completion enters awaiting-verification; current-controller Finish requires consumer-selected VerifyCompletion. The default refuses completion, and rejected evidence preserves task state. The simulated consumer verifies an explicitly declared diagnostic-marker goal; this is not a real renderer/code-writing goal or live AI coverage. Process-kill/restart retains durable lineage, marks lost process execution interrupted and refuses automatic replay; arbitrary live provider resumability is not claimed.

Final gates: **101 passed, zero failed (1380.991s)** in the complete no-filter suite; final actual Linux engine probe passes; final engine Windows profile builds; supervision Windows/Android-named managed profiles compile in the full suite. The separate durable policy gate proves one selected verifier body/zero contracts and default completion refusal. Live provider, native Windows and APK/device coverage remain unrun as described below.

Local source increments: Agent e90d9fb, Helper 40a1def, WorkerTasks c51e971, Agent cleanup b6e13e0, engine optional registration 90874a5, Helper close fence cbfbefe, explicit task verification 53ef325. No Core changes or outside shared-contract modifications.

## Reproduce locally

Use installed .NET 8 and set CONFECTORY_DOTNET to its executable; DOTNET_CLI_HOME must be writable. Build SDK/tests in Release first if needed.

```sh
$CONFECTORY_DOTNET build tests/Confectory.Tests/Confectory.Tests.csproj -c Release --no-dependencies --no-restore
DISPLAY=:97 $CONFECTORY_DOTNET tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll
$CONFECTORY_DOTNET src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/agent/project.cpack portable
$CONFECTORY_DOTNET src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/helper/project.cpack portable
$CONFECTORY_DOTNET src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/supervision/project.cpack portable
$CONFECTORY_DOTNET src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/engine/project.cpack linux > /tmp/engine.json
DISPLAY=:97 python3 tests/gui/engine_x11_spotcheck.py /tmp/engine.json
python3 tests/packs/verification_policy_check.py
$CONFECTORY_DOTNET src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/engine/project.cpack windows
```

Run each build report's `run` command. Agent/Helper/Supervision consumers print explicit PASS on their real functional checks; provider responses are explicitly simulated. Supervision accepts CONFECTORY_SUPERVISION_DIR for caller-owned persistent local storage; use a fresh directory for normal regression invocation. WorkerTasksTests owns its private process-kill fixture; do not kill production work to reproduce that test.

Public IDs, outside reads/edits, necessary imports, separate functional/locality gates, commit increments and full-suite evidence are in CHECKPOINT_6_WORK_LOG.md.

## Limits and next-stage handoff

A live Agent test requires a concrete approved provider implementation, chosen account/model/endpoint configuration, credentials supplied outside Git, and authorization for real external/possibly paid calls. None is supplied or invoked; this milestone does not claim a successful live account/model connection. Provider operations must be bounded/cooperative and concurrently cancellable; a blocked noncooperative provider reports retained ownership/timeout, not successful termination. No tools/accounts/credentials were installed/configured and no real external agent communications occurred.

The supervision consumer maps its Windows- and Android-named profiles to the managed Portable compiler; these verify managed contract/provider compilation, not net8.0-android SDK packaging or native OS execution. The final desktop engine Windows profile additionally selects the existing Windows Window bodies. Corrected Windows user acceptance remains asynchronous. Android SDK/licenses/adb/full JDK remain absent or pending: no APK/device/native provider/network-permission coverage or license acceptance. Existing native desktop windows do not pretend Android has identical multiwindow capability.

Next coherent stages: approved live adapter/contract conformance; reusable Helper management/status/chat projections using existing ElementViews and task identity; authority-approved chief recovery and temporary-helper permanence/return merge; explicit provider resume/retry policy, retention schemas and augmentation generation. Current Task state/journal and Helper memory are separate, and pending dispatch must never be silently replayed. No full editor, AI adjudication, internet collaboration or automatic takeover is claimed.

Publication is blocked by automatic review despite later parent approval evidence: one identical retry was denied and no alternate route used. Continue authorized local work; parent must resolve propagation of the existing approval as trusted input. Do not ask the sleeping user to repeat it or attempt further publication without resolving this blocker. No binaries/images/secrets/raw logs/original documents are tracked. All twenty baseline sections were read; original DOCX transfer is not a specification-reading gap. No quota-reading tool is exposed, so remaining quota/reset timing is unverified; parent requested retry in about an hour.
