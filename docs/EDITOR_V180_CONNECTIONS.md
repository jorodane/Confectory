# v180 consumer connections

## Source and ownership

The 2026-10-10 continuation starts at `work/current` 5c3a4ce. Remote main a4418ec has the same tree. The initial local b5ea38c was not used as the implementation baseline. No AGENTS.md or .agents/skills exists in this checkout.

The official Library skill resolved `Confectory_UI_설계서_v180.pdf` (25 pages) and its Word original. Consumer-local materialization of both returned `download failed`; the transfer host was refused by the environment proxy with HTTP 403. Library page text was readable and pages 5–16 and 23–25 supplied the behavior requirements below. The returned image references were not locally renderable. **No PDF screenshots were inspected; visual fidelity to v180 remains unverified.** No guessed download route, Sites source change or deployment was used.

This increment changes the production `Confectory.EditorHome::MainBody` consumer. Public Model Command, PackWorkspace, SchemaEditing, Helper, ProjectAI, UIOrder, WindowPlacement, platform adapters and Core are unchanged. Outside implementation reads: PackWorkspace Command/Snapshot and SchemaEditing DescribeView for schema-origin/revision/scope shapes; ProjectAI Open and WorkerTasks Command to verify projected Helper/project identities; Window DrawText/MeasureText to diagnose a transient capture between rectangle/text drawing. These reads introduce no private calls.

## Implemented behavior

- On wide project screens, the bottom-right controls now include Augment and Object browser beside report, Run/Stop and Navigate. Narrow screens retain these two tools in the sidebar. Both routes use the same control IDs and existing Model commands; navigation anchoring uses the displayed Dock geometry.
- Agent presentation distinguishes an unbound connection from configured/running/error state instead of treating running requests as the connection count. No configuration is presented as authenticated/live verification.
- The selected Helper window has an independent message draft keyed by live project context, Helper ID and membership. Its Review button uses existing ai-prepare and all subsequent content, configuration, token and permission guards. The project-chat draft is not reused. A global Helper's message here is still scoped to the current explicit project; this does not introduce a global conversation service.
- Helper output and Worker goal/progress/status are selectable read-only text. An unavailable Worker projection is labeled unavailable rather than shown as a zero count. Workers are filtered by exact ownerHelper and durable project ID. Previous/Next selects existing task IDs without dispatch; the status dot is paired with the actual status text. Error, cancelled, interrupted, running and completed remain distinct. No Worker chat is added.
- Proposal direction has its own retained floating window (UIOrder ID 20) and text buffer keyed by original project context and target ID. Back returns to existing cards without preparing or starting a request. Reopen retains the input/binding. Review refuses a changed selected target and uses the existing proposals preview. It never borrows project-chat text, creates mock cards, charges, dispatches a Worker or changes reroll policy.
- Properties can open the selected field's actual `schemaOrigin` ID through ordinary owned selection/schema-view, and return to the object. Shared schema draft changes are reflected by the next schema-view. Source buffers retain their original binding, all edits retain CAS, and Save/Review/Confirm remain separate. Missing/out-of-scope schema resolution is not replaced by a hardcoded schema. This opens the field's defining schema; it is not an invented primary-schema rule for multi-schema objects.
- Native source and form inputs remain interactive during readonly Model polling, matching existing button availability. Mutating commands still serialize and retain scope/CAS checks. This fixes the lost-focus failure exposed by the extended AI UI regression.
- Browser Search preserves the selected kind filter. Object browser opens the existing draft workspace instead of a second explorer or source model.
- Complete close retires the new buffers/navigation state through existing project UI cleanup. Hide preserves the original owner. Only controls used by the project surface are registered, retaining the shared 128-control budget without a core exception.

## Remaining scope

The v180 visual port is not complete. Neutral/gold styling, Helper artwork, exact title-bar layout, arbitrary simultaneous object/compound editors and three side-by-side proposal cards remain unimplemented. Full responsive panel scrolling/workarea sizing and long-label fit are still incomplete; the current tall Helper panel can overlap the chat/Dock. These are not claimed as v180 visual acceptance. The existing central workspace/menu windows and input bindings remain retained. The new schema navigation uses the existing single workspace; it does not claim simultaneous parent/child editing windows.

Helper profile mutation, global conversation lifetime, reroll costs/hold policy, reporting recipients, YogiBox delivery, automatic data migration/merge and new persistent layout policy remain undecided and unchanged. Real accounts/models, user PC changes, native Windows/Android device execution and Sites edits/deployment remain deferred.

## Verification

Use .NET SDK 10.0.401 and its normal wasm-tools workload, with `CONFECTORY_DOTNET=/workspace/toolchains/dotnet-10.0.401/dotnet` and private writable DOTNET_CLI_HOME/entry/XDG storage. Tests use the repository's custom runner; `dotnet test` is not execution evidence.

New acceptance scripts consume a normal build report for `examples/editor-home/project.cpack`:

```sh
DISPLAY=:96 python3 tests/gui/editor_home_v180_connections_x11.py /tmp/confectory-ui-linux-final.json
python3 tests/web/editor_home_v180_connections.py /tmp/confectory-ui-browser-final.json
```

Both create ordinary projects/schema/object drafts using real controls. They check actual schema ID navigation, shared schema draft updates, original source binding retention, separate target direction input, two Helper drafts and hide/reopen retention. No product command injection, special success-only pack or provider invocation is used. The native test is also registered as `test_actual_editor_home_v180_scoped_inputs_and_schema_navigation`.

Final gate results are recorded in [AI_DEVELOPMENT_STATUS.md](AI_DEVELOPMENT_STATUS.md), under the 2026-10-10 entry. Initial control-budget refusal, incorrect test schema inheritance syntax and first cold browser publish timeout were real failures; they are not counted as passing gates. The shared control limit, schema grammar and normal build timeout were not relaxed.
