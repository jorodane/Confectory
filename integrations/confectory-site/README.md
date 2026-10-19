# Confectory Connect

New owner-private Sites MCP server and authenticated engine relay. It is independent
of PackEngine Links and the local STDIO development plugin. Neither is modified.

- Site: `appgprj_6ad620d14cf4819191aef4a4d0a18b43`
- Published private URL: `https://confectory-connect.jorodane.chatgpt.site`
- Engine source: this directory in `jorodane/Confectory`, `work/current`.
- Separate deployment source: `/workspace/sites/confectory-connect`.
- Status: private v2 deployment succeeded with `has_mcp: true`.
- Plugin ID: `plugin_asdk_app_sites_c997ef642378819187e0c2511c98a119`.
- Live private-plugin smoke test: `confectory_engines` succeeded and returned
  `{"engines":[]}`; no live PC engine was connected during that check.
- Subsequent parent verification confirmed actual Windows login and one live
  engine-only relay with `scope: null`. Real project-scope operations remain
  unverified. A plugin installation URL was not supplied; do not infer one.

## Connection and permissions

In the Windows editor launched by `Confectory.bat`, choose **Agent 연결 → Codex →
엔진 연결 준비 → 2. ChatGPT 로그인 · 엔진 연결**. The second button is beside engine
preparation, above project settings. Complete login in the dedicated window;
preparation alone starts local IPC and does not register an engine with the Site.
An empty `confectory_engines` result is therefore expected before Site pairing.
The panel distinguishes local preparation from ChatGPT connection and explains
when the running host cannot open the login window. No project is required for
these connection steps.

The native window distinguishes runtime preparation, navigation, login wait,
engine handshake, connected, disconnected and reported failure. Loading does not
fail merely because time passes. After pairing, a host-wake-capable connection
hides its window and keeps the relay alive in the running engine. **X / 창 숨기기**
only hides an active supported connection. **연결 창 다시 열기** reopens that same
window without preparing a new connection or resetting its grant. Before pairing,
X cancels. **개인 플러그인 연결 해제** in the main panel and **연결 해제** in the
connection window stop the relay explicitly. Engine exit always stops it.

A failed navigation keeps the browser's login/error document visible. Authentication
waits are not terminal failures; an already rendered successful HTTP document that
reports `ConnectionAborted` is also retained. Actual network, HTTP and certificate
failures still require inspection/retry and cannot complete pairing. The selectable
diagnostic field shows the stage, navigation result and HTTP status, or exception
type/HRESULT for initialization and native transport. It excludes URLs, query
strings, exception messages, local paths and credentials. If a paired hidden relay
fails, its window is shown again. Do not begin diagnosis by clearing the profile:
the diagnostic field is the minimum useful report.

The Site page and native host negotiate `hostWake` only in their paired handshake.
An older Site that does not acknowledge it stays visible, with an explanation;
an older native host receives the original paired envelope. Polling and retry
backoff use native wake messages when negotiated, rather than hidden JavaScript
timers. A Windows Forms timer emits wakes every two seconds and independently
checks the received session expiry. No unsupported browser flags or suspension
settings are used. OS sleep, process loss and prolonged request failure can still
expire the existing lease; no session is silently extended.

## Saved login on this PC

The user approved a fixed, dedicated, non-InPrivate WebView2 profile at:

`%LOCALAPPDATA%/Confectory/SiteRelay/confectory-connect.jorodane.chatgpt.site`

Its profile name is `ConfectoryRelay`. WebView2 keeps its own login cookies and
browser storage there, independently of normal Edge/Chrome profiles. Password
autosave and general autofill remain disabled. No browser cookie/token is read,
copied or exported by Confectory code. A later engine run reuses whatever login
state the service still considers valid when the user opens a new connection.
It never restores a remote session, project/node grant, queued job or scope from
the profile. The fresh connection starts with `scope: null`.

To sign out and forget this local login, reopen the connection window, choose
**로그인 정보 지우기**, and confirm. The app disconnects first, clears that
WebView2 profile through `ClearBrowsingDataAsync`, then closes the window. A clear
failure is reported rather than claimed as success. Other Confectory Connect
windows using the same Windows user's profile may be signed out too. This does
not delete ordinary browser profiles or uninstall/revoke the ChatGPT plugin.

For manual cleanup when WebView2 cannot start, exit all Confectory engines normally
first, then delete only the dedicated folder above. Do not remove an active user
data folder. No automatic cleanup deletes the saved profile at engine shutdown.

The Site runtime changes are in `worker/bridge-page.js`, with regression coverage
in `tests/page.test.mjs`. They require the parent's separate private deployment;
this engine task does not publish a Site or change its access policy/database.

The dedicated saved-profile view signs in through Sites' top-level ChatGPT flow
and uses same-origin HTTPS for its persistent D1 queue. Site-scoped identity owns
each record. There is no separate native API key, service bypass, tunnel or browser
cookie extraction in this connection path.

The isolated view has no editor envelope transport, host objects, generic native
actions or local WebUI token. The native host pins the exact HTTPS relay document,
message protocol, nonce and navigation generation. It forwards only pairing,
heartbeat, bounded tool dispatch and close messages. The engine rechecks its
instance, remote connection, local grant, remote scope generation, lease and
project before and after dispatch. Opening connection UI does not run metadata
discovery, authentication commands or provider processes.

A new connection starts with `scope: null`. The user first chooses the existing
local project/node capability, then explicitly shares that capability with this
private plugin. Replacing the connection or leaving/replacing the local project
retires its grant. Remote revocation preserves the local grant. Reconnection never
inherits the earlier grant. The owner can have multiple identified engines;
there is no implicit selected-engine or selected-project variable.

The six `workspace_*` tools reuse DevelopmentTools,
shared drafts, source pins and hash/revision CAS. No shell, build, project opening
or automatic Confirm tool exists. Final source changes still require the user's
Review/Confirm in the engine.

Before a project exists, call `confectory_engine_tools` with the selected engine's
exact `sessionId` and `instanceId`. It returns the engine's three creation schemas:
`engine_project_options`, `engine_project_propose`, and `engine_project_status`.
These work with `scope: null` and never enable workspace access. Options come from
the existing empty ProjectPack/.NET creation contract. A proposal requires the
user's explicit request and bounded title/description/intent plus the supported
template/target IDs. It creates no files and accepts no filesystem path.

The engine user reviews the proposal from Home in the existing creation form,
chooses the parent folder with the native picker, and explicitly presses create.
They can instead reject it. No remote confirm tool exists. The final receipt has
an ID/status/projectId and `projectAccessGranted: false`, with no local path.
Project/node access remains a separate explicit step after creation. Current chat
is used for consultation; no new global chat/provider/memory service is introduced.
Unsupported game-pack recommendations and automatic Helper/Agent assignment are
reported as unsupported rather than supplied as mock options.

Engine jobs use the same owner/session/instance queue, request budget and expiry.
Only these three allowlisted names use reserved empty project/scope pins and zero
scope version; workspace names still require the exact current grant. Project grant
changes do not retire engine jobs. Cancellation discards queued/running results;
an already displayed proposal is rejected locally or retired on connection close.
Reconnection cannot read another connection's proposal. Engine shutdown/restart
does not restore pending proposals, sessions or grants. No database migration is
needed. Runtime changes in `worker/index.js` and queue tests in `tests/relay.test.mjs`
await the parent's private deployment; this task does not publish the Site.

## Queue and failure handling

MCP calls explicitly identify `sessionId`, `instanceId`, `scopeVersion`, `scopeId`,
`projectId`, `callId`, and an `arguments` object. `confectory_engines` reports the
owner's live grants. Before calling a workspace tool, call `confectory_tools` with
the exact session/instance/scope generation/scope/project pins. It returns only
that grant's permitted definitions, preserving the engine's original `parameters`
and an exact callable relay `inputSchema`. The latter keeps node enums, required
fields, types and CAS constraints, while moving the engine-injected `projectId`
and `scopeId` out of the inner `arguments` object. Static `tools/list` contains no
private schema values. Missing, stale, read-only, foreign-owner and retired grants
cannot expose definitions they do not permit.

The six workspace tools return a durable `requestId`;
`confectory_result` reads its status/result, and `confectory_cancel` cancels pending
execution or discards a running result. Cancellation does not roll back drafts.

Every queue/claim/result is bound to its owner, engine, session and exact grant.
Call IDs are fingerprinted and duplicate edits retain the same engine call ID.
Completion retries resend the result without rerunning the tool. Claims are never
automatically executed again after a crash or expired lease. An interrupted edit
has an uncertain outcome: inspect shared changes before issuing another call.
Missing identity is rejected; a foreign owner, stale grant, revoked connection,
changed duplicate body or changed completion is refused.

Sessions last at most 30 minutes, the connection lease lasts 15 seconds, and jobs
expire after 90 seconds. Engine access revokes immediately locally; hosted state
is synchronized on the next pulse and stops accepting new work when its 15-second
heartbeat lease expires. Each session has at most 256 request records and each
owner has at most 16 active engines. Expired records are cleaned when pairing.
All authoritative queue state is in D1, not module globals or browser storage.

## Build and tests

Requires Node 24 (test fixtures use `node:sqlite`). With a writable npm cache:

```sh
npm ci --cache /tmp/confectory-site-npm
npm test
npm run build
node scripts/stage-deployment.mjs /workspace/sites/confectory-connect
```

The Drizzle schema is in `db/schema.js`; `npm run db:generate` generates immutable
SQL, snapshots and journal entries in `drizzle`. Never create tables in request
handlers. The build embeds the page into a single Worker ESM entry at
`dist/server/index.js`, copies the actual Site manifest and includes migrations.
The manifest has `capabilities: ["mcp"]`, `d1: "DB"`, and no static capability.

The server/DOM fixtures verify identity, scope, read-only denial, cancellation,
idempotency, completion retries, lease expiry, cold persistence and late replies.
`tests/web/editor_mcp_plugin.py` also exercises the real ordinary EditorHome model,
existing shared drafts, duplicate remote staging, CAS and human Confirm with an
owned Site-protocol fixture. This is not real Sites login or plugin installation.
The Windows host and its shared presentation lifecycle are cross-built/event-tested.
The earlier v2 Windows login and engine-only connection were parent-confirmed;
this updated retained-window/profile behavior has not been run or timed on that PC.

## Verified private deployment

The parent environment completed publication using the official Sites helper and
confirmed the following v2 result:

- Engine repository source: `7f78895a289d1bb1c0b0e2c8cde5543697a64993`.
- Site source commit: `4c3a80fb33bec3ee520aefa200a321c8bb39c07c`.
- Saved version: `appgprj_6ad620d14cf4819191aef4a4d0a18b43~appgver_e039beb2f978819199d4f6be09e23323`.
- Deployment: `appgdep_6ad628b71ac48191a944b8635a5a0118`.
- Deployment result: `succeeded`, `has_mcp: true`.
- Published URL: `https://confectory-connect.jorodane.chatgpt.site`.
- Private plugin: `plugin_asdk_app_sites_c997ef642378819187e0c2511c98a119`.
- Official-helper verification: tests `3/3` passed and Worker build passed again.
- Live plugin verification: `confectory_engines` returned `{"engines":[]}`.
- Subsequent parent pixel review and live plugin call confirmed Windows login and
  one connected engine with `scope: null`; no real project operation was verified.

The initial empty-list call verified private MCP availability. The later live check
also verified Windows authentication and engine-only pairing. Real project access
and PC tool execution remain unverified. The initial engine
fixture report at `4b60bca18079ae0db3f071a28a8e8ff13d20ae06` predates publication;
its unpublished status and helper blocker describe that earlier state.

## Future publishing

Use the Sites plugin's shared `site-workflow.mjs` from an environment that has the
plugin scripts. Run it against the separate deployment directory and this exact
project ID. Send the short-lived source credential only through its hidden stdin;
never put it in a file, environment variable, URL, argument, transcript or commit.
Run the tests/build, push the exact Site source commit, and publish that commit
with `save_version_and_deploy_private`. Sites applies D1 migrations before upload.
Then call `get_site(include_mcp_connection: true)` and use the returned `plugin_id`
to obtain the actual private plugin installation link. Do not update PackEngine
Links or broaden this Site's access policy.

Real user login, App installation/authorization, engine installation/settings,
permanent credentials, security relaxation and tunnels require their separate
user approval. None was performed by the fixtures.
