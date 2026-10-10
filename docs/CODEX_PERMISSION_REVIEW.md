# Ordinary connection permission review

EditorHome now prepares an inert review from the selected connection's public permission function. It shows the exact message, project/Helper scope, model, endpoint or managed executable/home, authentication mechanism, limits and verification status in a selectable read-only field. Each declared right needs an explicit per-turn choice. Cancellation retires the token and choices. Starting rechecks the current policy, configuration, context and Helper selection. A checked box never overrides an unsupported or unverified provider.

## Pack contracts and locality

- `Confectory.Agent.Responses::Permission(config)->string` and `Confectory.Agent.Codex::Permission(config)->string` own their disclosures, requirements, pinned values and support gate; each Connection declares `permissionFunction`.
- `Confectory.ProjectAI::Permission(connection,config)->string` composes the existing qualified provider roles, following Configuration's dispatcher pattern.
- `Confectory.AIConnection::Authorize(policy,projectId,approvals)->string` validates all declared rights, rejects unknown choices/preapproved pins, checks support, and creates the pinned grant without I/O. This shared contract was necessary because the old content/usage-only UI could not represent process, account, configuration and storage rights without a provider-specific frontend bypass.
- EditorHome Model owns temporary choices/token lifetime and calls those contracts. The production Main uses ordinary BaseUI buttons, native read-only text and navigation; permission buttons have unique shell IDs; five home-only IDs are excluded from the shell registration to preserve the public 128-control budget.
- Outside implementation reads: existing provider Validate/Start, ProjectAI Configuration/Open, AIConnection grant handling, EditorHome model/controller and existing GUI/consumer harnesses, to preserve the actual authorization and lifetime boundaries. Edits outside permission providers are explicit consumer composition, model/UI wiring and acceptance tests. No core, BaseUI implementation, target, main branch or version changes.
- Affected rebuild scope: new permission/authorization implementation owners and directly consuming model/Main bindings; unchanged provider execution bodies and unrelated packs retain their contracts. The existing presentation-owner locality test is a separate structural gate from functional approval tests.

## Account and model boundaries

This change performs no login, account authorization, model request or account modification. Secrets are neither imported nor saved in packs or review logs. Runner authentication is never interpreted as user authentication.

For a future Codex test the user would choose the ordinary Codex Connection and set model, official executable, their own managedHome, and `credentialReference=codex:managed`. The supported intended account mechanism is a user-performed official CLI ChatGPT sign-in in that selected CODEX_HOME, outside this UI. No in-app OAuth/token-import or Codex API-key path was implemented. An existing login alone will not enable execution: chosen-model tool filtering, actual account/service verification, file-read isolation remain unresolved. Installed unauthenticated startup evidence is documented in [the offline gate](CODEX_NO_ENVIRONMENT_OFFLINE_GATE.md).

Codex's current stdio contract bounds one turn to 90 seconds and 32 dynamic tool calls, with 65,536 input characters and 32,768 displayed output bytes. It cannot enforce a hard number of internal model requests/retries or a currency cap; the review explicitly reports `maxModelRequests:null` and `hardModelRequestCapEnforced:false`. Permission remains unsupported because the account/service/tool/read-isolation checks are unresolved. Internal request count and cost are disclosures, not new mandatory execution gates. If the user later requires a hard application request count, choose a transport that can enforce that requirement, such as Responses. Responses bounds requests to maxRounds (1–8, default 4), zero application retries, 4,096 output tokens and 25 seconds per request; it does not enforce a currency cap. Browser/Android direct credentials remain blocked pending an approved relay.

A future smallest connectivity check should ask only for a fixed acknowledgement, with no tools and Responses maxRounds=1. A subsequent proposed draft can use `examples/projects/authoring/project.cpack`, `Example.Authoring::Counter`, count 0 to 1, followed by separate human Review/Confirm. Existing tool rights cover the owned namespace, not a hard one-element allowlist. The reviewed message, selected Helper context and later tool results are transmitted; a whole checkout is not automatically attached. No live check is authorized or executed by this task.

## Verification commands

SDK: `/workspace/toolchains/dotnet-10.0.401/dotnet`; `DOTNET_CLI_HOME=/tmp/confectory-dotnet10`, `CONFECTORY_DOTNET` set to that SDK.

```
dotnet build tests/Confectory.Tests -c Release --no-restore
dotnet run --project tests/Confectory.Tests -c Release --no-build -- test_actual_editor_home_ai_scope
DISPLAY=:96 CONFECTORY_AI_PRODUCT_GUI=1 dotnet run --project tests/Confectory.Tests -c Release --no-build -- test_actual_editor_home_ai_scope
dotnet run --project tests/Confectory.Tests -c Release --no-build -- test_project_shell_windows_and_android_managed_compile test_editor_home_semantic_presentation_rebuilds_only_own_provider
```

The actual model consumer passed the approval/stale scope/helper/Worker/close flows plus all six Codex choices, undeclared-right rejection, blocked dispatch, cancellation and fresh empty choices. The test provider is owned and simulated. Native UI and target outcomes are recorded below after execution. Windows/Android managed compilation does not establish native runtime or APK/device coverage. Screenshots and generated build artifacts remain outside Git.

Final results (2026-10-09):

- Tests build: 0 warnings, 0 errors. Headless actual model approval consumer: 1 passed (41.888s).
- Final Linux actual Main GUI + model consumer: 1 passed, 0 failed (181.264s), `/tmp/confectory-permission-ui-native-final.log`. This includes chat/proposals/Worker/draft review/close and the six-right Codex review, paging, blocked start after every choice, cancellation and fresh empty review. The initial registration/budget/ID-collision failures were corrected; they are not reported as successful runs.
- Final managed Windows/Android compile and presentation owner locality: 2 passed, 0 failed (239.764s), `/tmp/confectory-permission-ui-final-targets.log`.
- Connection regression guards and owned Codex stdio fixture: 2 passed, 0 failed (123.182s), `/tmp/confectory-permission-connection-tests.log`; no real model/account or external service.
- Final actual EditorHome WASM build succeeded. Chromium production UI passed settings, Helper scope, unsupported relay permission review/cancel and native binding close/reopen: `/tmp/confectory-permission-browser-accepted-ui.log`. Build: `dotnet src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll build /tmp/confectory-project-ai-browser-consumer-7r0rx5bd/project.cpack browser > /tmp/confectory-permission-browser-accepted-build.json`; UI: `python3 tests/web/editor_home_connections.py /tmp/confectory-permission-browser-accepted-build.json`. Consumer files are verbatim production EditorHome, with absolute manifest registry paths only. Its own generated outputs were regenerated to stay within storage quota.
- Actual Linux approval and Codex screenshots were visually inspected at `/tmp/confectory-project-shell-gui-ld4y_dzc/ai-chat-approval.png` and `codex-permission-review.png`. The latter shows checked rights while the start action remains blocked. No images/binaries/raw chat logs are committed.
- Execution tools remained responsive during the reported connection warnings; final commands, GUI and browser checks completed. No native Windows test, Android APK/device runtime, authentication or live model test was performed.

Next handoff: ordinary approval wiring is complete. Resolve the documented model/account/service/read-isolation checks before enabling a live Codex turn. Do not remove the provider-owned `supported:false` gate merely because the UI choices are checked. Existing main/version values remain unchanged; publish only the authorized work/current source branch.
