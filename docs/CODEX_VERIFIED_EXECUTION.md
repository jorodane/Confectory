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

## Home installation discovery and model selection

Home → AI Agent → Codex → local CLI now offers **설치 후보 자동 찾기 · 이 호스트**.
It inspects absolute local entries in the host's normal PATH, bounded standard
installation prefixes, the explicit npm prefix, CODEX_HOME and the user profile's
`.codex` directory. This identifies candidates on the host running Confectory,
which can differ from the machine displaying a browser. It never traverses the
disk recursively, opens credential or Codex configuration contents, executes a candidate,
installs Codex, copies account files or changes settings during discovery.
Bounded legacy executable path hints are the named exception described below.
Discovery has limits of 64 PATH entries, 512 executable probes, 64 executable
candidates and 16 directory candidates. Relative, UNC/device and malformed
locations are excluded. Browser and Android runtimes report the unsupported host.

Candidates show their paths and discovery sources, with a separate explicit
selection action. Version and account status remain unverified at this stage.
Executable links are resolved using metadata. The official npm platform package's
`vendor/<target>/bin/codex` and older `vendor/<target>/codex/codex` layouts are
checked at known adjacent locations, including a resolved `codex.js` launcher.
JS/CMD/PowerShell launchers are displayed as disabled wrappers rather than executed.
Linked/root managed directories are diagnosed consistently with the provider's
existing storage restriction. Missing candidates retain manual entry. Rediscovery
does not replace saved or pending inputs, and a previously selected missing path
stays visible for an explicit correction.

**버전·공식 모델 목록 확인 준비** accepts an empty model name. After the same four
explicit preflight consents, the selected CLI performs the existing restricted
startup, version/account metadata/configuration checks and paged official
`model/list` request. Unsupported versions report the observed version and stop
before account lookup. Catalogue responses are bounded to eight pages of at most
100 unique entries. Empty/unavailable catalogues produce a diagnostic. The picker
contains only returned model identifiers; it chooses no guessed/default model and
preserves an existing selection when that identifier is returned.

Catalogue lookup stops before thread/start or turn/start and creates no execution
receipt. Applying a returned model saves through the ordinary settings path and
invalidates previous evidence. The model-bound preflight and separate Helper
request approvals are still required. Cancellation/settings changes fence late
results using the existing per-configuration gate; host restart retains saved
settings but retains neither verification evidence nor a model catalogue.
Closing the form drops pending consent and catalogue selections. A late start
requires the currently open form and its current token; replaying a cancelled
form's token cannot start the CLI even with all former consent flags supplied.

The actual Home test uses owned empty directories and labelled Python protocol
fixtures exclusively. It exercises multiple native candidates, an official npm
layout and disabled JS wrapper, a linked directory diagnostic, empty-model paged
lookup, consent refusal, unsupported-version refusal before account/read,
cancellation, disappearance/rediscovery, modal reentry and cold saved-settings
restart, including rejection of a cancelled form's consent-token replay. Fixture
request capture requires zero thread/start or turn/start during
catalogue discovery, and all owned credential directories remain empty. It does
not validate a real user account, paid request or native Windows runtime.

Discovery sources: [official npm launcher layout](https://github.com/openai/codex/blob/main/codex-cli/bin/codex.js),
[official configuration locations](https://learn.chatgpt.com/docs/config-file/config-basic),
and [official app-server model/list contract](https://learn.chatgpt.com/docs/app-server).

Validation for this increment: the frozen editing, Home/Helper, discovery and
owned stdio suites passed 9/0/0 in 926.265s, including all eight receipt dispatch
fences and generated Windows/Android compilation. After tightening closed-form
consent, the actual discovery, Codex/Helper grants and fresh/saved Home suites
passed 3/0/0 in 262.069s. The Release test build had zero warnings/errors. All 18
protected file hashes and seven object editing function bodies match the baseline;
Core, inbox, original ZIPs, Android settings and local/remote main are unchanged.

## Existing managed installations and preparation guidance

The Home flow first searches existing preparation. Discovery now includes the
named LOCALAPPDATA/Confectory/Codex and LOCALAPPDATA/PackEngine/Codex npm prefixes,
CONFECTORY_CODEX/PACKENGINE_CODEX executable hints and each brand's codex-path.txt.
Only the two named non-credential path files are read, as bounded strict UTF-8
with at most 8192 bytes. Linked hint files/directories are excluded. Invalid hints
are not echoed, executed or changed. Known native npm package layouts replace the
old installer's recursive search. CODEX_HOME and the profile .codex remain separate
login-directory candidates; an install prefix is never treated as a login home.

The earlier managed installation pinned 0.159.2. Official npm metadata and GitHub
release pages confirm 0.159.2 and 0.159.0-alpha.3 exist. The two tags have identical
tool spec_plan.rs, npm launcher and v2 protocol module index bytes. This is partial
compatibility evidence, not validation of the entire runtime/API/startup policy.
The exact supported profile therefore remains 0.159.0-alpha.3. After explicit
preflight consent, an observed 0.159.2 reports provider-version-unverified before
account/read. The message says compatibility is unvalidated rather than claiming
proven incompatibility. No version gate, receipt or dispatch control is bypassed.

Home presents AI choice, existing preparation, plain readiness explanations and
the same explicit consents. Native file paths, protocol/method trials, detailed
versions/reasons and manual settings are folded into advanced controls. Friendly
status wording describes missing preparation and the next button without calling
a saved setting, model catalogue or installation guide a successful connection.
Advanced and ordinary views use the same settings, discovery, verification and
request-approval contracts; there is no second novice execution policy.

Preparation guidance links only to checked official documentation, the exact
supported release and six verified Windows/macOS/Linux x64/arm64 assets. It keeps
OS/architecture and version detail optional while choosing the host's matching
asset by default. The supported version is explicitly a prerelease in details.
Users are told to retain old installation/login/settings, prepare a separate
empty version folder, and rediscover or explicitly select their file. Named
Confectory/Codex-0.159.0-alpha.3 parallel folders are included in discovery. The
guide has no installer, login, download-execution or account-import action.

The actual Home fixture covers both legacy prefix layouts, both environment hints,
path-file reuse/deduplication, multiple observed versions, 0.159.2 rejection before
account lookup, advanced detail opt-in, missing-vs-unvalidated preparation,
official Windows asset selection, simulated preparation/rediscovery, cancellation
and cold saved-setting retention. Existing files are compared byte-for-byte and
an owned installer sentinel must never run. The user's Windows PC file presence
and native Windows runtime remain unobserved; all accounts/processes are labelled
owned protocol fixtures and no real authentication or paid model call is tested.

Sources: [previous installation resolver](https://github.com/jorodane/The-Golemancer-s-Factory/blob/7f208573b2ffe3babfcb04753d16fb4fedbf9654/ConfectoryEngine/editor/Shared/CodexInstallation.cs),
[previous preparation flow](https://github.com/jorodane/The-Golemancer-s-Factory/blob/7f208573b2ffe3babfcb04753d16fb4fedbf9654/ConfectoryEngine/editor/Shared/CodexBootstrap.cs),
[official supported release and assets](https://github.com/openai/codex/releases/tag/rust-v0.159.0-alpha.3),
[official 0.159.2 release](https://github.com/openai/codex/releases/tag/rust-v0.159.2),
and [verified npm version metadata](https://registry.npmjs.org/@openai/codex/0.159.0-alpha.3).

Validation: common Editor/ButtonGame editing, original Home, Codex/Helper grants,
Responses Helper ownership, v318 characterization and owned stdio dispatch fences
passed. A successful rediscovery initially collapsed the open preparation guide;
the dialog now retains the guide and optional target/detail choices while using
one shared preparation action for ordinary and advanced controls. After this fix,
discovery/model selection, Codex/Helper grants, fresh/saved Home and the novice
legacy-installation flow passed together 4/0/0 in 332.849s. Release build had zero
warnings/errors. All 18 protected tracked hashes and seven object editing function
bodies match the baseline. No real user account, token, paid request or installer
was used; actual Windows runtime/PC file presence is not claimed.
