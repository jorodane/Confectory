# Codex verification and ordinary Helper execution

The previous Home flow could inspect and save settings but could not create the
verification grant required by the provider. That was an implementation gap. The
ordinary dialog now has a separately approved preflight step, session evidence and
a normal Helper request path through the existing provider. Declared desktop/tool
availability describes the adapter; Permission computes execution support from
that evidence. Users cannot set `protocolVerified` in settings or a checkbox.

Choose the official CLI executable, the existing user-owned login directory and
model in Home's AI Agent dialog. Check connection conditions, then approve the
four displayed preflight permissions. This starts the selected installation to
inspect public account metadata with `account/read(refreshToken:false)`, effective
configuration and the official model catalogue, and creates a temporary empty
thread. It sends no project context and starts no model turn. Missing login gets a
specific result and a separate official CLI login step for that selected directory.
The product never imports tokens, runs login or writes persistent account settings.

The check reports existing login metadata separately from untested live service authentication; it cannot observe all network activity inside the CLI.

A successful check records an opaque session receipt for ten minutes. Its evidence
pins normalized configuration, executable bytes/size/mtime, protocol version,
account metadata hash, effective configuration hash and the selected model entry.
JSON object ordering is canonicalized before hashing. Editing settings, cancelling
a check, a changed installation or expiry invalidates support. A fresh check gets
a new identity, so earlier request approvals cannot authorize the new receipt.
Evidence is held in process memory, does not survive host restart, and publishes no
account email, tokens, raw configuration or private Helper memory.

After selecting that configuration for a project and selecting a Helper, sending a
message opens the existing per-request content, usage, process, account,
configuration and storage review. Authorize pins the current receipt into the grant.
Provider checks that private receipt and rechecks installation, account, selected
model and effective configuration before `turn/start`. Changed evidence causes
`provider-verification-stale` before project content is sent. Human Review/Confirm,
Worker completion evidence, Helper memory and request ownership stay separate.

## Supported scope and genuine interface limits

The current supported profile is the installed 0.159.0-alpha.3 v2 app-server
contract. `initialize` reports the executable version in the requested client name's
user-agent prefix. Startup requests strict configuration, disabled hosted search,
25 disabled external/native feature groups and an empty notification command list.
The effective configuration and paged experimentalFeature/list runtime state must confirm every required control. Managed configRequirements/read evidence is pinned too. Raw override requests alone are insufficient. Enabled MCP or
plugin entries, configured telemetry exporters, custom service providers/endpoints, custom instruction sources,
unsupported versions/models or missing controls fail with a precise code/detail.
These are runtime decisions, not a global unverified-account constant.

Both `thread/start` and `turn/start` explicitly select `environments: []` before
inference. The returned fresh thread must confirm no environments or instruction
sources and the exact requested model/provider. In the supported official tool
builder, no environments removes shell, apply-patch and native image/file access.
Hosted/extension tools need their independent startup restrictions. Read-only only
limits writes; it is not read isolation. Instructions and rejection of unexpected
`item/started` events are additional diagnostics, not the scope guarantee. Internal
clock/planning/UI utilities can remain; they have no project file, process,
connector or external-recipient authority. Confectory dynamic tools retain the
existing owned namespace/draft scope, call budgets and separate Confirm contract.

A shared Desktop/IDE socket is blocked with `shared_policy_unpinned`: the inspected
public API cannot identify and freeze its installation/startup tool policy against
other clients. A sampled configuration is insufficient. The offered alternative is
a dedicated owned CLI app-server using the same existing login directory. Public
Unix socket framing remains implemented, but a forged flag cannot invoke it through
the product. Supporting more versions or a future immutable socket-policy API needs
another explicit compatibility implementation. Ordinary private app IPC is not an
alternative. Workspace Agent API receipt/status also cannot supply Helper replies
or remote cancellation and remains a separate contract.

A turn can contain multiple model requests/retries; this interface supplies no hard
monetary or inference-count cap. Existing account metadata is not proof that a live
service request will succeed. The user still has to run the preflight against their
own installation/account and approve any actual model request. No real account,
login, personal token read, paid model call or new persistent access was used during
this implementation. Native Windows execution is not claimed by Chromium on Linux.

Sources: [official app-server contract](https://learn.chatgpt.com/docs/app-server),
[configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference),
[official tool-plan source](https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/spec_plan.rs).
The local installed probe used an owned empty directory and only initialize,
initialized and config/read. It confirmed the version-response format and effective
startup controls without account/read, model/list, thread/start or inference.

The ordinary Home/Helper browser test uses a clearly labelled owned Python protocol
fixture. It covers grant creation, separate request approval, missing login,
unsupported tools/version/model, changed effective configuration, check cancellation
and Escape/reentry, stale approvals and a normal Helper-owner request-stop button. The stdio fixture also
checks foreign/deduplicated tools, separate Helper owners, cancellation, installation
changes, stale receipts and unchanged final source until ordinary Review/Confirm.

Validation at this increment: Home/Helper verification plus project scope/background/
close passed 2/0/0 in 153.156s. The frozen Editor/ButtonGame editing gate, existing
Responses Helper ownership gate and shared-socket refusal/Workspace receipt gate
passed. A corrected pre-turn scope error classification then passed the owned stdio
suite 1/0/0 in 69.295s, including generated Windows/Android compilation. Connection
settings/declaration, numeric/subset review and fresh/saved Home entry gates also
passed in their focused runs. Release test build had zero warnings/errors. All 18
protected tracked hashes and all seven object editing function bodies match the
baseline. The earlier broad restart failure was caused by editing the resource while
its test host was running; the frozen run passed. No original ZIP, Android setting,
Core, inbox or main change is included in this increment.


## Receipt invalidation before first request dispatch

Open-time approval is not a reservation that survives a revoked receipt. The
provider rechecks the currently registered receipt after serializing each fresh
thread/turn start and immediately before handing the message to its transport.
The check and handoff use the same per-configuration gate as cancellation,
settings invalidation and receipt replacement. That gate survives replacement;
lookup under it reads the current record rather than the open-time copy. An
expired, cancelled, changed or replaced receipt causes
`provider-verification-stale` before the first `turn/start` context is sent.

The handoff is the dispatch commit point. Invalidation confirmed before that point
blocks the pending request. Invalidation after handoff prevents future starts;
it does not retroactively stop an already approved dispatched turn. The ordinary
Helper request-stop action remains the explicit way to stop that owned turn.
No gate is held while waiting for an RPC response, and receipt invalidation closes
only its owned check process, leaving other active Helper owners running.

The owned fixture holds account/read and thread/start responses, then applies
cancellation, the ordinary settings-invalidation operation, receipt replacement
or a deterministic expiry on its own emitted in-memory receipt. All eight cases
require zero additional turn/start messages and no output from the blocked
request. A separate already-dispatched Helper must continue and complete, and a
blocked old generation must retain the newer valid receipt.

Boundary validation: the owned stdio suite passed 1/0/0 in 108.762s with all eight
pre-request invalidation cases and an unaffected continuing Helper. The actual
Home/Helper grant flow, Responses Helper ownership flow and project scope/
background/close regressions passed together 3/0/0 in 229.007s. Release test build
had zero warnings/errors. app.js and all 18 protected tracked hashes remained
unchanged at this follow-up; no UI, Core or unrelated editing behavior was changed.
