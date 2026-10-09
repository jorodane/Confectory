# Codex no-environment offline gate (2026-10-09)

Implementation uses the official installed `0.159.0-alpha.3` environment selection
contract. Both thread/start and turn/start explicitly send `environments: []`.
Omission would select/inherit an environment. Existing public DevelopmentTools
definitions and project/namespace capability checks remain the only host tool path;
no native filesystem path is accepted from the model. CAS draft staging, human
Review/Confirm, cancellation and owned process retirement remain unchanged.

The adapter's child arguments now explicitly request stdio, strict config, disabled
web search and disabled shell/snapshot, app/browser, code-mode host, multi-agent,
hooks, plugin discovery and permission expansion features. These overrides affect
only that child; no existing config/account/system policy is edited. Environment
variables are still cleared and CODEX_HOME must still be explicitly pinned and
approved. Production credential storage is not switched to ephemeral: the separate
offline test adds that override to avoid reading/reusing account storage.

The actual compiled provider fixture captures launch arguments and outgoing RPCs.
The opt-in installed probe reuses those arguments and initialize/thread requests,
changing only the retired scratch cwd to a fresh owned empty cwd and adding an
ephemeral credential store. It never sends turn/start or a user message to the
installed server, and never logs in or calls model/list. Only initialize,
account/read with refreshToken=false, config/read and thread/start are allowed.
Raw RPCs/configuration/stderr are not printed; only bounded checks are reported.
The adapter reads approved effective configuration through config/read, builds bounded
thread-local `enabled=false` overrides for discovered plugins/MCP servers, and refuses
any nonempty/missing environment array in the returned thread before sending turn/start.
The installed probe rebinds only those extension IDs to its own discovered metadata,
because an installed host has different plugin IDs from the owned simulated server.

Before exec, the Linux child installs irreversible libseccomp EPERM rules for
socket/connect/sendto/sendmsg/sendmmsg and io_uring setup/enter/register. The same
child verifies IPv4, IPv6 and Unix socket creation is denied, then execs the CLI.
There are no inherited network descriptors. The filter is inherited by descendants;
no firewall, persistent policy or parent security setting is changed. No privileged
operation or new tool installation is used. `unshare --net true` was denied by this
host; no escalation was attempted. The seccomp fallback only removes child access.
Failure to install/verify this guard prevents launching the installed CLI.

Observed installed startup scope: account/read reports no account; effective config
reports ephemeral credentials and required features disabled. Before thread creation,
the probe rejects custom model-provider configuration and constructs extension-deny
overrides; it does not treat an empty CODEX_HOME as proof of no inherited settings.
This host exposed plugin configuration even with an empty home. The server accepts
captured initialize and thread/start requests, returns an empty thread environments
array and no loaded instruction sources. No auth.json is created in the empty home.
No real environment account/auth/config was manually read, copied or modified.
This demonstrates an unauthenticated, network-denied startup is possible here;
authentication or external communication is not mandatory for these local RPCs.

`disabledPluginIds` is explicitly documented by the installed response schema as a
saved list that does not yet filter capabilities. It is NOT used as an acknowledgement
of extension enforcement. An attempted acknowledgement assertion failed and was
removed for this reason, without marking that intermediate gate as passing.

Limits: no installed turn/start, inference, full model-facing tool inventory, native
tool attempt or inference-driven dynamic tool call is observed. Official version
source guards shell/apply_patch/view_image registration on environment presence;
that source evidence is separate from the returned empty runtime environment array.
Neither observation proves every extension or parent-process file read is isolated.
Read-only, cwd and disabled command network access still are not a read allowlist or
a global model-service network policy. Child seccomp is a test guard, not a new
production security claim. Scope rejection and real draft-tool execution are covered
by the owned simulated server, not by live inference.

The actual EditorHome settings/binding/ai-prepare path continues to refuse Codex
before provider dispatch. Desktop/browser/Android/functionTools flags remain false,
with a reason that distinguishes observed no-account startup from unverified live
tool behavior and managed authentication. No alternative product entry or fake
successful live result was added. Existing account ownership is unverified and that
account must not be used just because login status succeeds.

Pack ledger: intended own public elements Provider/AdapterBody, compatibility
ProviderBody, Connection. Public signatures unchanged. Outside reads: existing
DevelopmentTools Scope/Definitions/Invoke contracts and EditorHome capability gate;
signatures alone do not prove host refusal or namespace checks. Outside edits:
provider fixtures plus protocol/offline test helpers. No core/platform/editor/Agent/
Helper/Worker implementation changes. Fixture now tests a foreign namespace request
as well as foreign thread, native approval, tool dedup and scoped cancellation. A
nonempty returned environment is also rejected before a turn-start marker can appear.
Body locality gate expects only AdapterBody physical owner and zero public contracts;
Connection reason is a metadata change affecting capability consumers.

Opt-in command, using existing SDK and generated schema directory:

```sh
CONFECTORY_CODEX_SCHEMA_DIRECTORY=/tmp/confectory-codex-preflight-tf2caln7/schema CONFECTORY_CODEX_OFFLINE_EXECUTABLE=/opt/codex/bin/codex CONFECTORY_DOTNET=/workspace/toolchains/dotnet-10.0.401/dotnet DOTNET_CLI_HOME=/tmp/confectory-dotnet10 CONFECTORY_ENTRY_STORAGE=/tmp/confectory-codex-offline-entry XDG_CACHE_HOME=/tmp/confectory-codex-offline-cache XDG_DATA_HOME=/tmp/confectory-codex-offline-data /workspace/toolchains/dotnet-10.0.401/dotnet run --project tests/Confectory.Tests -c Release --no-build -- test_codex_owned_stdio test_declared_connection_settings test_actual_editor_home_ai_scope
```

Remaining live gates are concrete: verify the chosen model's effective tool catalog
and behavior under empty environments/disabled extensions; verify approved managed
account/config/storage and service access; wire exact process/config/storage/account
permissions into the actual EditorHome approval boundary; obtain reviewed input,
model and usage/cost approval before inference. These are not remedied by accepting
schema shape alone. Existing user version settings and main branch are unchanged.

Final verification: tests build 0 warnings/errors (2.33s); final three filtered
regressions 3 passed / 0 failed / 0 skipped (118.257s). This includes the installed
network-denied no-account probe, installed schema validation of captured real RPCs,
returned-environment refusal before turn/start, out-of-namespace refusal, public CAS
draft tools/review/confirm, cancellation/double-close, own-body locality with zero
public compiled contracts, Windows/Android managed target builds, Responses approval
regression and actual EditorHome unsupported Codex gate. No new native GUI/visual,
WASM, native Windows, Android device or live inference result is claimed.
Private logs: `/tmp/confectory-codex-no-environment-final-all-build.log` and
`/tmp/confectory-codex-no-environment-final-complete-gates.log`. Earlier diagnostic
runs with plugin inheritance/acknowledgement assertions failed and are superseded by
this final gate; they are not included as passing evidence. All generated captures,
schemas and diagnostics stay outside Git.
