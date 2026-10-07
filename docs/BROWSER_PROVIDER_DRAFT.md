# Local browser Entry/Home milestone

**This is a runnable local .NET host with browser UI. It is not the requested independent browser/WASM runtime.** The earlier unlinked provider draft is superseded by the shared-model extraction and tested consumer described here. The remaining independent-runtime implementation is in [WEB_RUNTIME_ROADMAP.md](WEB_RUNTIME_ROADMAP.md).

The ProjectPack `Confectory.EditorHome.Web` composes `Confectory.EditorHome.Model`, `Confectory.BrowserHost`, project/file/domain packs and the target pack `Confectory.Build.Web::Browser`. Target name `web` currently means this explicitly local host. No native Window/NativeUI or AI providers are reached. The engine entry is an ordinary linked ProjectPack function; core has no browser-specific host logic.

## Run locally

With .NET 8 SDK and existing trusted repository hosts built:

```sh
dotnet build Confectory.sln -c Release
dotnet build targets/web/Confectory.Build.Web.csproj -c Release
CONFECTORY_EDITOR_REPO="$PWD" dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll run examples/editor-home-web/project.cproj web
```

On Windows, run `run-web-home-windows.bat`. Windows script execution is not verified in this Linux environment. Open the printed `http://127.0.0.1:<port>/#<session>` URL in a browser. Keep the local host running; Ctrl+C ends its owner and removes staged imported files. `CONFECTORY_WEB_PORT` optionally selects an unprivileged local port. The final build output includes `browser-assets/index.html`, `app.js`, `style.css`, linked managed application/provider assemblies and public linkage catalog; no external website was deployed.

## Current capabilities and UX

DOM rendering, responsive layout, browser keyboard/touch-native controls and text inputs, explicitly selected `.cproj`/legacy `.cpack` imports, a manifest draft area and draft download work. Existing Entry/Home CreateSession/Command/Snapshot/CloseSession public operations are used through generated bindings. Declaration metadata is interpreted without executing imported pack code or reading/building its untrusted registry dependencies. Library packs can open with standalone false. `.cproj` requires a ProjectPack.

Same imported filename and contents map to the same staged path and return the existing project without replacing manifest/chat drafts. A different selected file is refused until explicit Leave, even when the current project is clean. Leave asks for confirmation if drafts are dirty; Cancel preserves selection and buffers. Confirmed Leave retains drafts only in this browser session, and reopening the same import restores them. Picker cancellation preserves buffers. Browser unload protection is advisory UX, not durable save. Download initiation leaves the dirty marker intact because cancellation/save completion cannot be acknowledged by this provider.

Build/Play, arbitrary commands, native OS filesystem browsing, file associations, desktop multiwindow and AI connections are absent from the browser HTTP surface and visibly identified in UI. The local host requires .NET and trusted repository metadata-description hosts; this capability does not establish browser-native C# execution. Import transfers the chosen bytes to the same machine's loopback process only. Session metadata/staged files are temporary, not an external upload or account-backed persistence.

## Security/lifetime boundary

The provider binds only `127.0.0.1`, requires a random per-process session header on APIs, rejects foreign Origin/Host, exposes a fixed static asset allowlist, sets a restrictive CSP, limits imported manifest size to one MiB, and allows only snapshot/import/leave operations. Imports accept filenames rather than caller-selected filesystem paths. Plain pack metadata validation is delegated to the reusable existing DescribeProject contract. No keystore/password/schema/signing input was added by this worker. Abrupt process termination can leave the private temporary session folder; no automatic global temp deletion is performed.

## Functional and structure gates

Actual Chromium against the real linked ProjectPack passed startup/render/input, Unicode/spaces import, invalid manifest rejection, same-file repeat buffer retention, different-file refusal, file picker cancellation, dirty Leave cancel, clean-active guard, explicit Leave/reopen, manifest draft download, responsive 390px view, forbidden/unauthorized APIs and orderly owner exit. Final packaged asset build was rerun through this same browser gate. A private screenshot was inspected at `/tmp/confectory-browser-verified.png`; no images or binaries are in Git.

Exact commands used (SDK selected through `CONFECTORY_DOTNET`, .NET home under `/tmp`):

```sh
dotnet build targets/web/Confectory.Build.Web.csproj -c Release
dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/editor-home-web/project.cproj web > /tmp/confectory-web-build2.json
python3 tests/web/browser_entry.py /workspace/Confectory-web-platform /tmp/confectory-web-build2.json
node --check packs/browser-host/assets/app.js
git diff --check
```

The linked consumer build had zero warnings and reached the shared model without native providers. The automated BrowserTests runner separately exercises a consumer-local BrowserHost provider change and asserts exactly `Confectory.BrowserHost::ServeBody` compiled with zero contracts; this gate remains separate from browser functionality. Native model/shell-domain and Android managed adapter regression commands/results are recorded in the final worker handoff, and root owns actual Linux native GUI checks after integration. No independent WASM build, static-site runtime, Windows browser execution, browser IME composition, Android browser execution, deployment or main merge is claimed.

## Locality/ownership ledger

Intended public elements: BrowserHost Serve(repository, assets)->int / ServeBody; EditorHome.Web Main/MainBody; Build.Web Browser target; shared Model four domain operations (see ENTRY_HOME_MODEL_PACK.md).

Outside implementation reads: existing native Home Main declarations and model sources/providers were inspected to discover domain ownership, operations and provider reachability; dotnet target/tool and core build protocol were read to implement delegation and preserve linkage artifacts. Model extraction was explicitly coordinated with root after Android worker completion. Native consumers' declarations/manifests and two locality fixtures were edited because a ProjectPack cannot be a library dependency; no platform logic was put in core. Root owns Android packaging/settings. Browser target delegates compilation to the existing trusted DotNet tool, owns its target identity, fingerprints browser assets and compiler, and packages those assets in its link output. Main reads only selected pack asset paths; HTTP routes never expose arbitrary asset paths.

Affected rebuild scope: first shared model namespace change rebuilds model contracts/providers and native/browser consumer bindings; thereafter BrowserHost body-only changes compile its provider only. A browser asset or target-tool change affects the target identity and therefore its target-specific compiled artifacts; current tool protocol does not have a separate link-only asset fingerprint. This broader target rebuild is explicit. Runtime assets are copied into final output, rather than silently reading changed source assets from the repository.

Independent browser/WASM follow-up is now available as a **separate** `browser` target and `examples/editor-home-browser/project.cproj`; see INDEPENDENT_BROWSER_WASM.md. This loopback `web` route is preserved, not replaced, and remains a basis for future separately authorized server IDE work. Its capabilities remain as recorded above.
