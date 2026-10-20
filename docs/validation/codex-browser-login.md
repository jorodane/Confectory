# Browser-first Codex login

The initial Codex screen still has one Login action. New login uses the official app-server browser flow by default; the Windows host asks the operating system to open its default browser once for each current login attempt. The official CLI owns localhost callback handling, OAuth, completion and credential storage. Confectory does not create an OAuth client, exchange authorization codes, accept tokens or read auth.json.

The browser API is `account/login/start` with `{ "type": "chatgpt" }`. The engine validates the returned `loginId` and official `authUrl`, then waits for the matching completion notification and reads account metadata with `refreshToken:false`. Existing successful login, account verification, readiness and automatic Agent registration continue through the prior coordinator. This follows the [official app-server authentication contract](https://learn.chatgpt.com/docs/app-server) and [normal Codex browser-login guidance](https://learn.chatgpt.com/docs/auth).

The installed `0.159.0-alpha.3` CLI's generated schema confirms this request and response. Schema extraction used a fresh owned home and child network denial, without starting any real OAuth/login/account operation. The [exact release-tag callback source](https://github.com/openai/codex/blob/rust-v0.159.0-alpha.3/codex-rs/login/src/server.rs) confirms the default issuer, authorize path, PKCE and loopback callback. This is protocol/source evidence, not a live account result.

## Explicit alternative and failures

Device login is secondary: the browser waiting screen offers a contextual “브라우저 로그인이 어려운가요?” disclosure, and suitable login failures offer the same explicit alternative. Choosing it cancels the owned browser-login process, waits for cleanup and requires new device-specific consent before sending `chatgptDeviceCode`. The security-setting caveat appears only after selecting this alternative. Account security settings are never changed. Returning to browser login also requires explicit choice and consent. Retry retains a deliberately selected method.

The native browser bridge accepts only the current waiting attempt's opaque handle and obtains its URL from the engine. The caller cannot supply a destination. The host validates the official HTTPS authorize origin/path, bounded PKCE/query shape and HTTP loopback callback before handing a canonical URI to the OS. The device alternative uses the fixed official device page. Browser opening failures remain visible and permit an explicit retry. In browser diagnostic mode, the link is user-opened; native browser success is not inferred from `window.open` returning null with `noopener`.

Cancellation retires only the owned CLI and incomplete new account directory, clears the displayed URL/code and ignores late completion. Matching official completion and an account metadata check are required before the existing readiness/Agent registration pipeline. Startup failure, callback unavailability, invalid URL, expired/failed login and cleanup failure retain fixed, secret-free diagnostic codes. Raw server messages, URLs, OAuth state, local paths and credentials are not copied into failure diagnostics.

Before browser login, a read-only listener check detects an occupied default callback port 1455. This avoids deliberately asking the pinned CLI to cancel a pre-existing login server. Port unavailability is shown with retry/device choice; it is not silently converted to device login. This precheck cannot remove races with other processes after the check. No custom callback server or account-security workaround is implemented.

The new `switching-login` phase is polled until cancellation cleanup completes. An initial test caught its omission from the WebState active-job predicate; that omission was fixed before the final regression runs.

## Validation and limits

Validation uses isolated CLI/account/model replies and a simulated OS browser opener. The normal coordinator, storage, cancellation, installer, verification and registration run as production code. The native URL/open helper is also compiled and exercised directly with injected success/failure; no real browser or user OAuth runs.

Final executed groups, Windows package and Git checkout results are recorded below and in the companion JSON. Failed compilation and test-fixture attempts are not counted as passing coverage. Actual Windows default-browser association, WebView2, callback/OAuth success with a real account and paid inference remain unverified.

## Executed results

- **36 distinct actual UI scenarios passed across recorded groups**: the original 27 connection scenarios, eight browser/device cases, and an additional cleanup-failure guard. Browser default, explicit browser → device → browser consent, once-per-attempt automatic open requests, failed browser open/retry, service-reported expiry, callback RPC error, owned port occupancy, invalid URLs, device cancel/late completion, method-preserving retry and automatic Agent registration were exercised. Page errors and external browser requests were empty for passing groups.
- The occupied-port case binds a fixture-owned listener at 1455 before login consent. The engine refuses before `account/login/start`, and no cancellation connection reaches that listener. Releasing the listener allows an explicit browser retry. This is a Linux fixture, not Windows networking evidence.
- The cleanup-failure case removes traversal permissions from an owned fake account directory, then explicitly requests a method change. Failure to retire it blocks fresh consent, retry and another-account bypass; no additional login RPC or Agent appears. Test permissions are restored afterward. No real account directory is used.
- Three backend regressions passed (global Helper ownership/approval/cancel/history/restart, production native URL/open helper, owned stdio). Two actual UI/internal safety regressions passed (presentation/settings retention/late close and installer/login safety with nine archive rejections and zero pre-consent side effects).
- The installed pinned schema validates the browser/device requests actually captured from the owned fixture. The production URL helper rejects foreign origins, non-loopback callbacks, wrong schemes, malformed/duplicate parameters and unsafe destinations before its injected OS opener. Browser launch failure/retry and canonical URI dispatch also pass. These checks establish protocol and boundary behavior, not live OAuth success.
- Windows host, Home Windows target and Release solution compilation passed. The final Windows package has **2,222 files**. The actual packaged engine renders minimal login and serves all **50** pinned resources from an unrelated directory, including an isolated runtime-only copy with no SDK. Hash/tamper/missing-component rejection and existing checkout profile reuse with explicit overrides pass.
- Original v508 stylesheet/reference ZIP hashes and all current resource pins match. Final Git checkout startup is recorded after the implementation commit.

No real ten-minute timer wait was run; expiry uses an isolated provider completion indicating expiration. Browser launch success/failure is simulated at the OS boundary. Actual Windows apphost double-click, default-browser association, WebView2 and real account callback completion remain unverified. Existing explicit storage overrides and the prior exe build procedure are preserved; the old local archive from the device-default implementation is not this delivery.

## Output and use

Run the existing Windows developer menu **3** or `scripts/windows/internal/build-windows.bat` to build the exe package. Alternatively, after a Release solution build:

```text
dotnet targets/editor-desktop/bin/Release/net10.0/Confectory.dll package . Builds/Windows-x64
```

Open `Builds/Windows-x64/Confectory.exe` with its entire output folder. The framework-dependent Windows x64 build requires .NET **Desktop Runtime 10.0 x64** and Microsoft Edge WebView2 Runtime, prepared separately; package/project compilation additionally needs the .NET 10 SDK. No runtime or account security setting is installed or changed automatically. A source-checkout result reuses its existing editor profile when present, and explicit storage variables retain precedence.

## Actual rendered fixture screens

All accounts and codes shown here are synthetic; no real OAuth page is captured.

- [Browser consent](codex-browser-login/01-Browser-Consent.png)
- [Browser waiting, without a device code](codex-browser-login/02-Browser-Login.png)
- [OS browser-open failure and retry](codex-browser-login/03-Browser-Open-Failed.png)
- [Explicit device-method consent](codex-browser-login/04-Device-Consent.png)
- [Secondary device-code login](codex-browser-login/05-Device-Login.png)
- [Verified metadata and automatic Agent registration](codex-browser-login/06-Agent-Ready.png)
- [Callback unavailable](codex-browser-login/07-Callback-Unavailable.png)
- [Cleanup failure blocks another login](codex-browser-login/08-Cleanup-Blocked.png)

[Structured evidence](codex-browser-login.json) records group boundaries, method counts, actual schema hashes, package results, artifact digest and the limits above. The first partial group stopped at a misconfigured port fixture; only its four explicitly passing cases count. The corrected port group, original 27-case group and cleanup group completed successfully.

The final Release solution build passed with zero warnings/errors (11.29s). The local delivery ZIP is `Confectory-Windows-x64-Browser-Login.zip`, 59,816,882 bytes, 2,223 entries including the package manifest, SHA-256 `eb59f000d9e29be7bda8f82fd243a673843b85b285d7403c9f94f4b232507e91`. Extract the complete folder and open `Confectory-Windows-x64/Confectory.exe` with the stated runtimes.
