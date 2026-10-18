# Non-authorizing Run history and cold status

This increment stores the last facts observed from an existing ProjectExecution launch. It supplies history for the Run viewport after a new host opens the same manifest. It never imports history into the execution registry, reconnects an old frame pipe, reads an old process environment, scans/adopts PIDs, restores Stop authority or replays a command. Frame control and current-process state remain the existing live session contracts.

## Stored facts and ownership

`ProjectExecution::RunHistory(session,project,operation,payload)` supports read-only `history`/`info` and an owning-provider `checkpoint`. Checkpoint accepts only an execution ID currently present in that session and exact manifest scope; it derives the fields from the existing owned status and validated frame receipt. Callers cannot submit replacement state, frame/ack, exit or credentials. Lifecycle checkpoints run at launch, actual running/terminal observation, verified frame observation and explicit owned Stop. Observe retains its seven-string process snapshot.

One version-1 file lives at `.confectory/run-history/<normalized-manifest-SHA256>.json`. Its five fixed fields are `version`, `scope`, `manifest`, `sequence`, `rows`. Each row has exactly nine fields:

| Field | Meaning |
|---|---|
| execution | The existing launch ID; it is not a saved execution-session or frame capability |
| recordedState | Last observed building/running/exited/failed/stopped process state |
| frame / ack / frameState | Last validated completed frame and acknowledged command with running/paused mode; all null before a supported frame observation |
| exitCode | Observed integer result for exited/failed, otherwise null; Stop invents no exit code |
| revision | Monotonic observation version for this launch |
| order | First successful record's project-local order, independent of filesystem mtime |
| observedUtc | UTC time when these facts changed; read/no-op observations do not refresh it |

No pipe name, secret, execution-session ID, runtime epoch, control capability, token, PID, environment, arbitrary payload, raw output or diagnostic/error string is stored. Frame/ack values are recorded data and cannot authenticate a client. No durable credential, security setting or permission was created. Current owner flags are computed from the live in-memory registry and are never saved.

A new session receives `state: owner-unavailable`, `ownerAvailable: false`, `canControl: false`, `canStop: false` for every historical row, including recorded terminal outcomes. The separate `recordedState` preserves the last fact; it does not establish whether any prior process currently lives. History is read-only even for an owned row: the ordinary Run controls retain their own current-handle and session checks. An explicit Stop with a historical ID and no matching live view owner is rejected instead of reporting a false successful stop.

## Atomicity, monotonicity and limits

The journal follows the existing build-history pattern: a dedicated per-manifest `FileShare.None` lease, validated bounded read, same-directory temporary file, data flush and atomic replacement. It does not take the source/build lease, so checkpointing can complete while compilation is waiting on that lease. A busy journal lease returns within about 200ms. A failed history write does not change the actual Run/Stop outcome.

Per-launch private serialization captures current facts, gives changed facts a monotonic revision and remembers the last persisted row digest. Before replacement the previous row digest and complete file snapshot must still match. Lower/equal conflicting versions, terminal rewrites, running-to-building regression and decreasing frame/ack are refused. Old executions retain their original order and cannot replace a newer launch row. The stored file contains none of the private CAS bookkeeping. A retry writes current confirmed facts; it never resends a frame or process command.

The fixed schema is at most 256 rows / 262144 strict UTF-8 bytes, with 32 rows/page and eight pages. Capacity returns an explicit recording warning and never silently deletes existing records. Query is separate from execution authority and does not start a compiler, execution worker or control-channel connection. Unknown schema/fields, malformed bytes, oversized files, scope mismatch and symlinks produce unavailable status. Checkpoint preserves corrupt/conflicting/read-only existing bytes; it does not reset or migrate them. There is no claim that ordinary project metadata is an authenticated or tamper-proof ownership record.

## Run UI and platforms

The Run window adds a read-only history section, paging/refresh, saved-state/frame/ack/exit/time display, and explicit `owner-unavailable` cold labels. Failed recording is distinguished from an empty history and from current execution state. Reading old rows does not select them as the active execution. Current live controls remain independent when a history file is corrupt or full. Project/context guards and the existing WebView revision protocol apply to history refresh. Row identity is retained while facts update.

Desktop .NET providers support recording/query with existing filesystem permissions. Android and independent browser/WASM providers return explicit unavailable, advertise no history capability and perform no history filesystem access. Managed profile checks are not device execution. Main, original ZIPs and Android settings remain protected. Property set/ref, extended ABI, general overflow, durable host ownership transfer and embedded render/input remain separate scopes. No real account, paid call or new remote service is used.

## Validation

Exact source hashes, diagnostic phases, final distinct methods, real cold-host observations, managed compilation, ordinary checkout/resource/Home startup and implementation identity are recorded in `validation/v480-recorded-run-history.json`. Earlier focused attempts are excluded from final totals. The actual UI gate crashes only its owned host, reads its saved facts in a fresh host with no execution children, rejects historical Step/Stop, preserves corrupt bytes and verifies a separate explicit Run/Stop remains available.

Command-admission regression: background `WebState` previously could poll the execution while validating a queued user request, advance the model revision itself, and reject that single request as stale. A real protocol gate reproduces this after an interval with no client state reads. WebStart now registers its serving thread in memory; only that thread publishes background observations. Worker admission/scope checks read the published snapshot without polling. No revision/CAS/frame guard is waived and no command is automatically resubmitted. A real intervening revision still rejects stale Step without running it. The thread marker is ephemeral bookkeeping and is removed during cleanup; it is never a stored credential or execution authority.

Final frozen validation: **14/0/0 execution/model methods**, **5/0/0 actual UI/transport methods**, **1/0/0 Windows/Android Home managed-profile compile method**, and **1/0/0 ordinary checkout/resource/Home startup method**: 21 distinct methods. Release solution build has zero warnings/errors. All final gates use the same 28-source manifest `e81087f3c978ff029d05c604f33fc9e747ac9ff89632655c3a9d798eb2ae326f`; ordinary checkout fixes implementation commit `a89b13cf1a6f810a42c0fd7ee014dd62d5f5401e` and 41 canonical/exact resources. Initial UI failures, fixture corrections and the admission RED/GREEN reproduction are preserved separately and excluded from these totals.
