# WebUI: resources, views and bounded consumer calls

The JavaScript `WebView` class is a state/request client, not an OS WebView control. Windows EditorHome now defaults to the generic embedded host. The v196 integration uses the original stylesheet, images and presentation functions with real project/draft endpoints; feature completeness and OS verification are separate. See [the support matrix](../../docs/EMBEDDED_WEB_UI.md).

WebUI is presentation infrastructure. It imports only RuntimeBase and its two
explicit consumer interfaces, `State` and `Invoke`. It has no editor, project
manager, Helper, file, shell, compiler, credential or arbitrary function dispatcher.
The final ProjectPack binds those interfaces using ordinary typed `provide` / `import`.

## Consumer contract

- `State(context) -> string`: JSON `{scope, revision, state}`. `scope` is a
  host-derived public scope object; an editor supplies durable project ID, selected
  Helper ID and common-memory permission. `revision` is a nonnegative monotonic
  revision within that scope. `state` is an explicitly safe public projection,
  never the whole model, opaque owner/capability, credential configuration or secret.
- `Invoke(context, endpoint, input, cancellation) -> string`: an explicit endpoint
  switch calling typed pack functions. Validate endpoint arguments and retain the
  domain pack's revision, authorization, approval and commit rules. The opaque
  context is supplied by the compiled consumer, not the browser. Cooperative work
  checks `Cancelled(cancellation)` and stops when true.
- `Open(context, descriptor) -> owner`: the descriptor has `id`, `version`, `entry`,
  `endpoints`, and `resources: {resourceID: {mime, base64}}`. Only declared relative
  resource IDs are served. The HTML entry differs from `ProjectPack.entry`.
  Resource replies include MIME, bytes encoded as base64, and SHA-256.

Bundles are ordinary compiled consumer data. Inline `{mime,base64}` resources remain supported. Larger applications may supply a trusted `resourceDirectory` and `{file:resourceID,mime,size,sha256}` rows. `Open` verifies finite file size and pinned SHA-256, rejects relative traversal and reparse-point paths, and snapshots bytes before serving. This is not a renderer folder mapping: a page receives only declared IDs and can never choose the trusted directory. JSON, PNG/JPEG/WebP, HTML, CSS, JS and SVG are supported. Consumer resource identities are pinned in its body fingerprint; changing assets requires updating its manifest.

An optional compiled `hostActions` allowlist (32 distinct names, 64 characters per name) exposes `NativeRequest(owner,action,input)` to a platform adapter, separately from browser envelopes. Native file selection is private host IPC; the renderer supplies no path. Actions use the same serialized consumer execution and cooperative cancellation binding. They are neither shell operations nor arbitrary function dispatch. A consumer's ordinary `Invoke` switch explicitly handles `host.<action>`; it must not declare those names as browser endpoints.

## Transport-neutral protocol

`Request(owner, envelope)` is independent of HTTP/WASM:

| Operation | Input / result |
| --- | --- |
| `mount` | Returns opaque view ID, host scope, revision and projected state. |
| `update` | View + scope; returns current state, revision, subscription `changed` and completed request records. While a consumer call owns execution, returns `busy` without blocking cancellation or leaking intermediate state. |
| `invoke` | View + scope + requestId + declared endpoint + input + expectedRevision; returns pending acknowledgement. Result/error is collected through update. |
| `cancel` | View + scope + requestId; acknowledges `cancellation_requested`, `already_completed`, or an unknown-request error. |
| `dispose` | Retires only the view, idempotently; unsubscribes and requests cancellation of its pending calls. |

The owner serializes consumer execution. The JS client ignores older out-of-order state revisions within its mounted scope. It compares the bound scope against
current host state before execution and again before exposing a result. Expected
revision is checked immediately before calling the consumer; domain CAS still
runs independently. Reusing a request ID with changed view/endpoint/input/revision
is refused. Completed identical requests are replayed only under the current host
scope; they are not executed again. Completed records remain in the owner's bounded
ledger. There is no automatic mutation retry or exactly-once network guarantee.

Cancellation is cooperative, not rollback: an operation may already have committed
a domain draft or other approved effect. Cancelled/retired calls publish no result;
subsequent state is authoritative. Disposing a view does not dispose the consumer's
project, shared draft or independent Worker. `Close(owner)` cancels views and
returns false until all calls have retired; callers must retain/retry ownership.
RuntimeBase owns revision instances and subscriptions. BrowserHost uses HostLoop's
normal asynchronous cleanup convention before the consumer releases its domain owner.

Bounds: descriptor 4 Mi characters, individual resource 4 MiB, aggregate resource bytes 32 MiB, 256 resources, native-action payload 16 Ki characters, request and consumer
state/result 2 Mi characters, 32 live views / pending calls, 1024 requests and total
view identities per owner. Exhaustion returns a structured error; records are not
evicted in a way that would silently permit mutation replay. Consumers should close
and create a new UI owner over the retained domain context when budgets are exhausted.
Errors expose stable codes, not private exception messages or filesystem paths.

## Adapters and consumers

`BrowserHost::Serve(owner)` serves the declared bundle on an unprivileged loopback
port. `/api/request` requires the ephemeral session token and validates Origin/Host;
resources use CSP, no-store and nosniff. Only the local adapter is implemented here;
it is not a remote server or authentication design. The local JS bootstrap stores
the transport token in per-origin tab session storage for reload, separately from
public state. Share neither the launch URL nor that token.

`BrowserRuntime::Initialize(owner)` adapts the same envelope/resource functions to
the existing WASM target bridge. It contains no editor imports. Target-specific
DOM mounting/HTML startup for a new independent WASM frontend is not completed by
this increment. A future remote adapter can implement the JS client's injected
`send(envelope)` function without changing domain endpoints; hosting, authentication,
reconnection authority and replay policy remain separate decisions.

The older import-only editor browser demos retain their previous behavior in
`examples/editor-home-web` and `examples/editor-home-browser`, including their
consumer-owned legacy adapters/assets. They are not generic WebUI implementations.

The actual `examples/editor-home/project.cpack` selects its web presentation when
`CONFECTORY_UI=web`. Its consumer exposes objects/page/select/editDraft/saveDraft
through existing EditorHome.Model commands. Project selection is a host-side
`CONFECTORY_WEB_PROJECT` path, not a browser-provided path. Save persists the same
draft; it never implies Review or Confirm. This first web consumer does not expose
Review/Confirm, AI, shell, global function invocation, arbitrary filesystem access,
project switching or Worker chats. Existing native domain workflows remain intact.

The actual `examples/button-game/project.cpack` uses the same web contract and
its existing RuntimeBase Score. Native and web presentations share `ChangeScore`;
there is no copied editor model or hard-coded successful result.

## Run and check

Build the solution with the installed .NET 10 SDK first. Set `CONFECTORY_DOTNET`
and include its directory in PATH. Build the ordinary ProjectPack with the normal
CLI and use the report's `run` command:

```sh
dotnet src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll build examples/editor-home/project.cpack linux
# Environment for the report's run command:
# CONFECTORY_UI=web
# CONFECTORY_EDITOR_REPO=/absolute/Confectory
# CONFECTORY_WEB_PROJECT=/absolute/user/project.cpack
# CONFECTORY_ENTRY_STORAGE=/absolute/owned/catalog
# ButtonGame requires CONFECTORY_UI=web only.
dotnet run --project tests/Confectory.Tests -c Release --no-build -- WebUITests
```

The product test runs actual Chromium with both ordinary packs, edits a copied real
ButtonGame Score through EditorHome, checks original source remains unchanged by
Save, and reconnects/reloads the same draft. Separate contract tests inject a
cancellable waiting function to exercise races deterministically; this unit fixture
does not replace either product acceptance test. See `docs/WEB_UI_FOUNDATION.md`
for the dated validation results and remaining platform limits.
