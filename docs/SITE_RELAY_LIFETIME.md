# Site relay lifetime and browser handoff review

The user's earlier workflow is a regression question, not evidence that a visible
relay window is a necessary product constraint. No persistence, background lifetime
or external-browser credential handoff was implemented during this review.

## Previous implementation at 1c16fe8

The reviewed repository is `jorodane/The-Golemancer-s-Factory`, commit
`1c16fe84444d342d1277c7dd72aef1b505dfe830`.

- On connection, the application hid `sharedBrowser` and resumed its normal browser
  surface while a three-second timer kept relay calls running. It did not dispose
  the shared WebView. See [SharedWeb lines 209–216](https://github.com/jorodane/The-Golemancer-s-Factory/blob/1c16fe84444d342d1277c7dd72aef1b505dfe830/editor/PackEngine.Editor/EditorWindow.SharedWeb.cs#L209).
- Browser controls shared the fixed `%LocalAppData%/PackEngine/WebProfile` environment;
  login popups used it too. See [Browser lines 144–153](https://github.com/jorodane/The-Golemancer-s-Factory/blob/1c16fe84444d342d1277c7dd72aef1b505dfe830/editor/PackEngine.Editor/EditorWindow.Browser.cs#L144)
  and [popup setup](https://github.com/jorodane/The-Golemancer-s-Factory/blob/1c16fe84444d342d1277c7dd72aef1b505dfe830/editor/PackEngine.Editor/EditorWindow.Browser.cs#L178).
  WebView2 user-data folders store cookies and browser data ([Microsoft documentation](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/user-data-folder)).
- `web-bridge.json` saved the request ID, session ID, expiry and permissions. A later
  explicit connection reused the request ID only for the same pack and permissions
  before expiry. See [reuse checks](https://github.com/jorodane/The-Golemancer-s-Factory/blob/1c16fe84444d342d1277c7dd72aef1b505dfe830/editor/PackEngine.Editor/EditorWindow.SharedWeb.cs#L181)
  and [saved receipt](https://github.com/jorodane/The-Golemancer-s-Factory/blob/1c16fe84444d342d1277c7dd72aef1b505dfe830/editor/PackEngine.Editor/EditorWindow.SharedWeb.cs#L214).
- Closing the entire editor stopped the timer and disposed that WebView. The
  explicit stop action also deleted its binding. `ScheduleAutoConnect` connects
  the local AI provider, not the Site relay. All 27 `EditorWindow*.cs` files at this
  commit were checked: no automatic startup invocation of `BeginSharedEditor` was
  found. See [editor close](https://github.com/jorodane/The-Golemancer-s-Factory/blob/1c16fe84444d342d1277c7dd72aef1b505dfe830/editor/PackEngine.Editor/EditorWindow.SharedWeb.cs#L89),
  [explicit stop](https://github.com/jorodane/The-Golemancer-s-Factory/blob/1c16fe84444d342d1277c7dd72aef1b505dfe830/editor/PackEngine.Editor/EditorWindow.SharedWeb.cs#L366)
  and [provider auto-connect](https://github.com/jorodane/The-Golemancer-s-Factory/blob/1c16fe84444d342d1277c7dd72aef1b505dfe830/editor/PackEngine.Editor/EditorWindow.History.cs#L105).

This supports the remembered hidden-window experience and reusable login state.
It does not identify whether “close the internet / open it again” meant a login
popup, embedded browser surface, external browser or complete engine restart.
The old external-browser fallback opened conversation AI; these files do not
establish an external-browser authentication handoff into the editor relay.

## Current behavior and smallest restoration options

The current connection uses a temporary InPrivate profile. X retires the local
nonce/grant and disposes the WebView. The page's close action retires both the local
connection and the hosted session. After X, the hosted engine listing can remain
until its existing 15-second heartbeat lease expires; local dispatch is revoked
immediately. Engine shutdown still revokes the connection. Sessions remain limited
to 30 minutes and project/node grants remain explicit.

The smallest candidate is to separate visible authentication UI from the retained
relay WebView, add explicit reopen/disconnect controls, and verify polling while
hidden. That can retain the existing running-session lifetime without restoring
project grants. It is proposed only: X was not changed to hide, and hidden-view
heartbeat behavior still needs actual Windows validation.

Restoring login across engine restarts would additionally need an approved browser
profile retention policy. It must not copy browser cookies/tokens, revive old node
capabilities, replay interrupted edits, import the old eight-hour session rule or
restore the old automatic initial project snapshot upload.

## External-browser authentication

Available Sites identity instructions describe top-level sign-in followed by a
same-Site relative return path and server-supplied Site-scoped identity headers.
They do not establish a native handoff/refresh contract. The parent separately
verified that OpenAI native PKCE for the API resource is not a Sites token flow.
Neither browser-cookie extraction nor a service bypass token is an acceptable
substitute for owner identity and consent.

A single-use pairing code plus native polling would be a new application protocol,
not an existing Sites feature. Before promising it, the native client needs a
documented way through the owner-private gateway or a separately reviewed broker
and scoped authentication contract. A child anonymous GET probe obtained no HTTP
status (`URLError`), so it did not verify that route's native reachability. No
gateway bypass, new grant, permanent credential or authentication server was made.

## Verification limits

The parent confirmed actual Windows login and one engine-only relay (`scope: null`)
on v2. Real project operations remain unverified. New loading-state transitions,
retry/close races and page late replies use owned fixtures; the Windows host is
cross-built. No user-PC login delay or updated Windows rendering time was measured.
