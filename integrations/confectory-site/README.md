# Confectory Connect

New owner-private Sites MCP server and authenticated engine relay. It is independent
of PackEngine Links and the local STDIO development plugin. Neither is modified.

- Site: `appgprj_6ad620d14cf4819191aef4a4d0a18b43`
- Expected origin: `https://confectory-connect.jorodane.chatgpt.site`
- Engine source: this directory in `jorodane/Confectory`, `work/current`.
- Separate deployment source: `/workspace/sites/confectory-connect`.
- Status: registered, owner-only access verified, not yet published. No plugin ID
  or installation URL has been returned. Do not infer one from the Site ID.

## Connection and permissions

The existing Codex connection panel opens a dedicated Windows Site WebView after
engine preparation. No project is needed. This separate InPrivate view signs in
through Sites' top-level ChatGPT authentication and uses same-origin HTTPS for
the persistent D1 queue. The Site-scoped authenticated user ID owns every record.
No service bypass token, separate OAuth implementation, API key, tunnel, copied
browser cookies, external port, or permanent engine credential is used.

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

Only the existing six `workspace_*` tools are exposed. They reuse DevelopmentTools,
shared drafts, source pins and hash/revision CAS. No shell, build, project opening
or automatic Confirm tool exists. Final source changes still require the user's
Review/Confirm in the engine.

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
The Windows host is cross-built; actual Windows authentication and runtime
navigation remain user-environment acceptance tests.

## Publishing handoff

Use the Sites plugin's shared `site-workflow.mjs` from an environment that has the
plugin scripts. Run it against the separate deployment directory and this exact
project ID. Send the short-lived source credential only through its hidden stdin;
never put it in a file, environment variable, URL, argument, transcript or commit.
Run the tests/build, push the exact Site source commit, and publish that commit
with `save_version_and_deploy_private`. Sites applies D1 migrations before upload.
Then call `get_site(include_mcp_connection: true)` and use the returned `plugin_id`
to obtain the actual private plugin installation link. Do not update PackEngine
Links or broaden this Site's access policy.

The current execution environment exposes the native Sites calls but has neither
`site-workflow.mjs` nor `project-setup.mjs` in its installed plugin paths. It cannot
complete the prescribed source push and private deployment. `get_site` with MCP
connection information currently returns: "Publish this Site before connecting
its MCP server to Codex." No deployment or installation success is claimed.

Real user login, App installation/authorization, engine installation/settings,
permanent credentials, security relaxation and tunnels require their separate
user approval. None was performed by the fixtures.
