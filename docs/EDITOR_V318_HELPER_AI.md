# v318 Helper connection and turn ownership

The ordinary EditorHome uses its existing AIConnection discovery, provider-owned settings schema, ProjectAI approval/Agent run, Helper scope and Worker/Augment contracts. This increment connects the existing v318 Helper presentation to those owners. It does not replace the object/Properties editor or import a newer Site.

## Connection and conversation flow

Responses declares desktop HTTP support. Codex settings remain available, with execution unsupported according to its existing capability declaration. Connection rows show current-host support and the actual locally selected pack. Selecting settings is not authentication, account verification or permission to send a message.

From a project, connection settings reuse the existing ordinary settings object and Properties View. The current project is hidden through the normal leave contract; its AI/Worker owners remain attached to the original durable project. Existing source and presentation/input drafts are preserved. No provider fields are enumerated by this UI.

Helper Add now explicitly opens recruitment, even when another Helper is already selected. The existing immutable global/project recruitment and explicit project selection are retained; arbitrary profile, image and Agent ownership edits remain unsupported.

Each Helper composer retains its own unsubmitted input, keyed by durable project and actual Helper ID. It does not copy another Helper's message from the project chat draft. Send opens the existing exact-content/curated-memory/permission review. Missing connection selection opens the connection picker without preparing or sending a turn. Cancelling review preserves the input.

The public projection adds the actual ProjectAI Helper ID, request ID and sanitized error code. Replies are attributed to the request owner, rather than whichever Helper is currently selected. Empty/new/error output clears a prior reply; no persistent conversation history is invented. Completed means the actual Agent response completed, not that a Worker task or source adoption succeeded. Existing Worker IDs/statuses remain authoritative.

All Helper Worker controls use one owner/project-checked presentation route. Opening a Worker dismisses an unpinned profile so it cannot cover the Worker controls; pinned presentations retain their existing behavior. Updating the status no longer installs a different click path.

While an actual permission review is open, Helper presentations are temporarily hidden and kept alive so they cannot cover approval controls. Cancel/start restores the same presentation and input. The common controls refresh owns form enablement; cancelled idle turns do not need another model revision to re-enable Send.

Project hiding retains work. Navigation retries are bounded to three attempts and only cover an explicit transport `stale_revision` rejection before the leave operation executed, under the same project ID. Message/source/AI/approval commands are not replayed. Complete project close uses the existing close contract. Active AI/Worker/project execution shows a confirmation; Keep working sends no close request.

## Ownership ledger and preserved boundaries

Owned changes are EditorHome WebState/WebBundle and Helper/connection/navigation portions of its shared app.js. Public pack signatures and provider/Agent/Helper/ProjectAI/WorkerTasks/Augment implementations are unchanged. Outside implementation reads were needed to establish ProjectAI's actual `helper`/`requestID`/`errorCode` snapshot shape, current-host connection capabilities, and existing bind/prepare/leave/close ownership behavior.

Only app.js's declared canonical identity changes in the ordinary 19-file resource manifest. Object/Properties/Review implementation regions, Workspace resources, inbox, original reference ZIPs, Android configuration and main are preserved. Global chat ownership, rich profiles/history, arbitrary Agent ownership, credentials, billing and actual Codex execution remain separate unsupported/gated work. Three-card generation, reroll, per-request approval, Worker dispatch/adoption and memory inclusion rules are unchanged.

## Verification

The focused ordinary EditorHome/ordinary ButtonGame test passed **1 passed, 0 failed, 0 skipped, exit 0, 23.789s** before the final affected regression. It uses the production Responses adapter against an explicitly owned HTTP fixture; the service output is simulated and labelled `OWNED LOOPBACK FIXTURE`. There is no substituted editor, provider role or special product branch.

The gate verifies settings navigation, zero requests before approval/cancel, exact current-project memory with common memory excluded, the actual request owner/output, a different project Helper with an empty independent input, background work and close cancellation, sanitized HTTP failure with old output cleared, complete-close cleanup and unchanged project source bytes. Exactly three owned HTTP requests occur. No real model/account, credential read/write, Codex process or paid service is involved. Chromium execution is on Linux; Windows device execution is a separate user check.

Initial failures remain in consumer-local logs, separately from the final pass: fixture completion waits around repeated memory notifications/recruitment; the actual Helper panel covering review; hidden-panel dismissal and disabled Send after cancellation; Add reopening the selected profile; and transport revision rejection during active-work navigation. No source, ownership, permission, memory or request-count assertion was waived.

The first frozen affected batch was **3 passed, 1 failed, 0 skipped, 196.203s**: the new Helper gate, cold recovery and checkout/startup passed; the broad gate exposed a refreshed Worker click handler leaving the unpinned profile over its controls. Its common route was corrected before the next frozen regression. This mixed batch is not reported as all-pass.

Reproduce with SDK 10.0.401 and Release tools:

```sh
dotnet build tests/Confectory.Tests/Confectory.Tests.csproj -c Release --nologo
dotnet tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll --require-runtime \
  WebUITests.test_actual_editor_v318_helper_connection_chat_state_and_ownership \
  WebUITests.test_actual_editor_v318_helper_inputs_and_panels_cold_restart \
  WebUITests.test_actual_editor_and_button_game_common_web_transport_chromium \
  WebUITests.test_editor_web_resources_windows_git_checkout_and_actual_startup
```

Runtime logs and fixture state remain outside Git. The final report distinguishes the focused result from the subsequent affected regression and identifies its full tested SHA.
