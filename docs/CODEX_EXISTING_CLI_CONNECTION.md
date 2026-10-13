# Existing Codex CLI connection preparation

The selected integration is the official Codex app-server over owned stdio, with an
existing user-owned ChatGPT sign-in. This change prepares the transport and exposes
passive diagnosis in the ordinary Helper approval view. It does **not** enable real
Codex requests: desktop support, function-tool verification and live verification
remain false. A fixture cannot establish account ownership or the chosen model's
actual tool policy.

## Settings and diagnosis

Codex remains a concrete pack extending the common AIConnection contract. Its model,
credentialReference (`codex:managed`), absolute executable and explicit managedHome
are edited through the same inherited Properties object used by other connections.
Selecting settings neither launches a process nor authenticates. There is no implicit
home/PATH discovery, token import, shell wrapper, or API-key billing fallback.

The ordinary transmission preview now reports whether the selected executable file
and managed directory exist. It explicitly says their CLI version, account and model
tool policy have not been checked. These are filesystem metadata checks; no executable,
configuration or credential file is opened. Windows UNC/network and device-prefix paths are not
automatically probed. All six existing grants remain separate,
per turn and pinned to the exact executable/model/home/project. Checkboxes cannot
change `protocolVerified` or override the product gate.

After those grants, the low-level transport calls official `account/read` with
`refreshToken:false` before creating a thread. A missing account fails with
`provider-auth-required`; any non-ChatGPT account fails with
`provider-auth-mode-unsupported`. It discards email, plan and routing data instead of
publishing them. There is no login, explicit token refresh or credential-file access
by Confectory. CLI startup itself may contact managed services or update the approved
storage; this method is not an offline account-ownership proof. Custom model-provider
configuration and unexpected startup instruction sources are refused before
`turn/start`, pending their own verification.

## Request and ownership behavior

Each approved execution owns one process, an empty scratch cwd, a fresh ephemeral
thread and one turn. The selected project is represented by the reviewed Helper
context and the existing DevelopmentTools capability for its owned namespace. The
project directory is not supplied as native cwd. No existing CLI/Desktop/IDE thread
is automatically resumed, and reconnect does not replay an uncertain turn. The Agent
request ledger returns the original execution for a repeated identical request ID.
An explicit future resume feature would require a durable project/Helper/worker
binding and a fresh review; it is not part of this change.

Thread and turn start retain explicit empty `environments`, extension-disable
requests, read-only sandbox settings and the existing draft-only tools. Read-only is
not a read allowlist, and some utility/model/extension tools are independent of
`environments`; these settings alone are not proof that all native tools are absent.
The official version source and current schemas expose no demonstrated complete
non-inference tool-inventory method for the chosen model. Therefore the existing
live gate remains necessary.

Streamed message deltas are accumulated by item identity. A completed item contributes
only its missing suffix; repeated identical completion does not duplicate output, and
conflicting text fails. Notifications, errors, dynamic calls and completion must
belong to the owned thread/turn. Usage/authentication errors become fixed public codes,
not raw server diagnostics. An interrupted turn is a cancellation, not completion.
There is no automatic turn retry, even when a server error says `willRetry`. The CLI
may have its own internal inference retries; a hard request/monetary cap is still not
claimed. Existing running/output/terminal state flows through Agent, ProjectAI and
the owning Helper/Worker. Stop sends only the owned `turn/interrupt`, then retires the
owned process and scratch; other Helper executions remain owned independently.

## Evidence and remaining user step

The owned stdio gate runs the production Codex provider against a local executable
fixture. Its ChatGPT metadata is explicitly synthetic, not a real account. It covers
account/config/instruction fences, actual request-schema capture, partial deltas and
repeated final items, foreign scopes/errors, tool dedup and namespace refusal, native
approval refusal, safe error propagation through Agent, repeated Start, scoped stop,
concurrent Helper contexts, and retained CAS drafts followed by separate human
Review/Confirm. The installed CLI probe uses an empty owned home and irreversible
child-only network-syscall denial. It sends initialization, public account/config read
and ephemeral thread start only; never a model turn or login. It deliberately bypasses
the provider's account fence for its unauthenticated startup-only probe, not the
product's execution gate.

Actual Chromium acceptance uses ordinary EditorHome and ordinary ButtonGame sources.
It also edits/selects the Codex settings, displays passive diagnostics, checks all six
permissions, and proves a disposable executable sentinel is never launched. Existing
Helper messages/error/hidden work/close behavior uses an explicitly owned Responses
loopback fixture; this is not a live Codex Helper response claim.

Before actual Codex use, resolve whether the user's existing installation is CLI or
Desktop/IDE, and obtain its non-secret version/native executable path, explicitly
chosen managedHome and model. Confirm that the selected account/storage belongs to
the user. A login or new persistent access must be a separate official user action;
never send authentication files/tokens here. Then verify the installed chosen model's
effective tools and startup scope before changing supported metadata. Any account
check/model test needs its exact executable/home/service, transmitted test content,
managed credential/config/storage access, usage terms and approval disclosed first.
Neither this environment's account nor a successful `login status` establishes that
permission. Windows native execution and real Codex model/service behavior remain
unverified; Windows/Android managed compilation is a separate compatibility check.

## Validation record

The final owned protocol/installed no-inference and Chromium Helper batch passed
2/0/0 in 120.569s. It includes the selected-path diagnostics, missing turn identity,
conflicting final text, synthetic account fences and distinct concurrent owned turns.
The affected editor/Agent/project batch initially passed 4 and failed 1 in 384.969s:
the Git checkout cloned the committed old app.js while the current build used the
uncommitted new resource identity. Its startup rejection was expected from that
mismatch; checkout must be rerun after the resource commit. The broad editor and
ButtonGame, Helper, Agent and project scope/lifetime methods all passed in that batch.
Two earlier owned-gate builds failed on a missing explicit BrowseDirectory provider
in the test consumer and an unavailable extension method in generated source; both
were corrected before the passing final gate. Raw captures/logs are local evidence,
not project content or authentication artifacts.

Worker supervision/restart/locality and Augment three-card/draft/history/locality
also pass with owned synthetic account-error cases. The source-only change to their
safe-error filters preserves fixed authentication/configuration/usage codes without
expanding any command, proposal, draft or completion rights. Original tracked v318
ZIP, Android settings and object-workspace resources remain byte-identical; the seven
object editor function regions in app.js remain unchanged. main is not modified or
published.

## Official references

- [Codex app-server lifecycle, account methods and streamed events](https://learn.chatgpt.com/docs/app-server)
- [Official Codex authentication and CLI login](https://learn.chatgpt.com/docs/auth)
- [Installed 0.159.0-alpha.3 tool registration source](https://github.com/openai/codex/blob/rust-v0.159.0-alpha.3/codex-rs/core/src/tools/spec_plan.rs)
- [Installed version app-server README](https://github.com/openai/codex/blob/rust-v0.159.0-alpha.3/codex-rs/app-server/README.md)
- [Earlier installed startup boundary](CODEX_NO_ENVIRONMENT_OFFLINE_GATE.md)
