# Independent browser/WASM milestone

`examples/editor-home-browser/project.cproj` is a separate engine ProjectPack targeting `browser`. Its generated entry, shared Entry/Home model, metadata parsing and browser role providers execute inside an actual .NET WebAssembly runtime. The output is a static website; it requires **no .NET application backend or `/api` service**. Local static serving is enough. This does not replace the separately retained local .NET loopback route (`examples/editor-home-web`, target `web`), which remains useful groundwork for a separately authorized future server IDE. No remote IDE, server compilation/AI, multiplayer, authentication, external bind/deployment or upload was added.

## Composition and capabilities

- ProjectPack/entry: `Confectory.EditorHome.Browser::Main` → `Confectory.BrowserRuntime::Initialize`.
- Public renderer: `Confectory.BrowserRuntime::Render(snapshot:string)->void`. Its browser provider invokes the target-owned JavaScript interop adapter. `dom.js` provides reusable keyed DOM rendering, native browser text-input binding and explicitly chosen file reading. Existing controls and card nodes are preserved during state updates.
- Actual shared model: `Confectory.EditorHome.Model::{CreateSession,Command,Snapshot,CloseSession}`. A new `CreateSession.browser.csbody` initializes owner-scoped virtual memory storage without a desktop execution host. Android and common bodies remain selected on their own targets.
- Metadata: `Confectory.ProjectExecution::DescribeProject` browser provider delegates to platform-neutral Core Parser through the owned WASM adapter. It reads only staged selected bytes beneath the browser owner root, without registry resolution, Builder invocation, scripts or imported entry execution.
- File storage: ordinary reusable FileStream contracts operate on Emscripten's in-memory virtual filesystem. It is **not the machine's filesystem**, and nothing is mounted or persisted to IndexedDB/OS storage. Explicitly chosen filename/content imports have a one-MiB budget, no arbitrary host paths. Owner close removes its virtual tree and model subscriptions/state; page reload starts empty. BFCache suspension preserves its frozen document owner; actual page disposal closes it.
- Browser capability JSON reports `backendRequired:false`, `dynamicCompilation:false`, `projectPlay:false`, `nativeFilesystem:false`, `nativeMultiwindow:false`, `ai:false`. Build/Play, OS paths, arbitrary commands and AI are absent and identified in UI. ProjectExecution's browser launch provider explicitly refuses external compilation/process execution even outside the UI controller allowlist.

The runtime uses the regular generated public provider bindings. Core source was not edited. Namespace migration to the shared model remains documented in ENTRY_HOME_MODEL_PACK.md. Platform-specific metadata/storage/render adapters belong to role and target packs, rather than a special engine host in core.

## Open/edit policy

`.cproj` must declare a ProjectPack; legacy `.cpack` and library packs can import. Standalone declaration is visible independently from browser execution readiness. Imported files are metadata and editable manifest drafts, not executable code.

Same filename+contents preserve the selected model and both draft buffers. Different contents or another file remain refused while a project is selected, even if clean. Explicit Leave confirms dirty drafts, Cancel preserves everything, and reimporting the same file after Leave restores session-local drafts. Picker cancellation is harmless. Native browser keyboard/text controls retain focus/buffers; the renderer does not replace them. Download exports a local draft; dirty state remains because browser download completion/cancellation cannot be proven. Browser unload protection is advisory, not durable save. Reload intentionally discards virtual files/model after its guard; use download for a durable copy.

## Build and serve

Prerequisites: .NET8 SDK with `wasm-tools`, trusted target tools, and a Chromium/Playwright installation for the recorded gate. The user explicitly approved WASM development-tool installation; no store credentials or signing keys were requested/created.

Recorded supported installation (official NuGet source was required because this environment's configured sources were disabled):

```sh
DOTNET_CLI_HOME=/tmp/confectory-dotnet NUGET_PACKAGES=/workspace/toolchains/nuget-packages \
 /workspace/toolchains/dotnet-8.0.425/dotnet workload install wasm-tools --skip-manifest-update --disable-parallel --source https://api.nuget.org/v3/index.json
```

Workload list verified `wasm-tools 8.0.31/8.0.100` plus the already installed Android workload. Installed SDK files and the official .NET runtime browser bootstrap example informed the target: https://github.com/dotnet/runtime/blob/release/8.0/src/mono/sample/wasm/browser/main.js . No new browser/Python packages were installed.

```sh
dotnet build Confectory.sln -c Release
dotnet build targets/browser-wasm/Confectory.Build.BrowserWasm.csproj -c Release
dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/editor-home-browser/project.cproj browser
```

The JSON report gives `output`. Serve `<output>/site` with any local static server; for the available Linux Python:

```sh
python3 -m http.server 8000 --bind 127.0.0.1 --directory '<output>/site'
```

Then open `http://127.0.0.1:8000`. CLI `run ... browser` uses the same optional local Python static-serving command (requires Python or `CONFECTORY_PYTHON`); static output itself has no Python/.NET backend dependency and may be served by another static server. On Windows, install the approved `wasm-tools` prerequisite using the selected SDK, build with equivalent commands, then use an installed static server. Windows SDK/browser execution has not been tested here. Nothing was externally hosted.

## Artifacts and verification

Final private report: `/tmp/confectory-wasm-build-final.json`. Actual output includes `site/index.html`, app/DOM/style assets, `_framework/dotnet.js`, **actual `dotnet.native.wasm`**, managed contract/provider/Core metadata assemblies, boot metadata and a preserved `public-linkage.json`. The first milestone intentionally disables trimming/AOT and totals 45,923,517 bytes; optimize separately after correctness. Exported working SDK sources are not the claim: actual runtime output was required and used.

Actual installed Chromium was driven against a Python GET-only static server in `tests/web/browser_wasm.py`; there was no .NET backend process. Requests were recorded and asserted to contain a fetched WASM file, **no POST and no `/api/` calls**. C# capability response and the provider's `OperatingSystem.IsBrowser()` guard independently distinguish the actual runtime from a desktop simulation.

Passed: startup/render, keyboard/native text input, Unicode+spaces import, invalid declarations, hostile registry bytes without loading code, same-file repeat buffer retention, different-file refusal, picker cancellation, dirty Leave cancel, clean-active protection, explicit Leave/reopen, draft download/dirty retention, 390px responsiveness, unsupported command refusal, idempotent owner close, and fresh empty reload. Screenshot inspected privately: `/tmp/confectory-browser-wasm-verified.png`. Commands:

```sh
python3 tests/web/browser_wasm.py /workspace/Confectory-web-platform /tmp/confectory-wasm-build-final.json
dotnet tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll BrowserWasmTests
```

The automated second gate builds a consumer-owned browser provider, runs actual Chromium, then appends a comment to that owned Initialize browser body and requires exactly `Confectory.BrowserRuntime::InitializeBody` compiled with zero contracts and stable target identity. Its final result is recorded in the worker handoff. Browser-only additions also retain Android body declarations/common desktop fallback; root owns final native/Android integration builds. Browser IME composition/mobile Safari/Android Chrome, external network hosting and AOT/release trimming are not claimed.

## Ownership and rebuild ledger

New pack public IDs: BrowserRuntime Initialize/InitializeBody and Render/RenderBody; Build.BrowserWasm Browser target; EditorHome.Browser Main/MainBody. Existing public model/metadata/launch signatures were unchanged; only browser target bodies were added.

Outside implementation reads/edits: read shared model initialization/Command and ProjectExecution metadata/launch contracts to identify desktop process dependencies. Added browser initialization and metadata/launch bodies to their existing owners because the contracts remain reusable while platform capabilities differ. Android/common bodies were preserved and no Android exporter/Activity changes were made. Read existing core Generation/Build protocol to preserve generated bindings/catalog and exchange existing compile/link requests; core was not modified. The new target delegates per-contract/provider compilation to the existing trusted DotNet target and performs its own supported WASM SDK link/publish with owned bridge assets. That adapter calls the existing neutral Parser, not Registry/Builder for imported files. No full editor, transport or remote backend was introduced.

Affected scope: browser-only provider code/entry bindings and browser target output; adding target-body declarations does not change existing function signatures. Native/Android selected code remains its own body. Asset/template/compiler/workload changes intentionally affect the browser target fingerprint and can rebuild all target-specific artifacts; the current tool protocol has no separate link-only asset fingerprint. Body-only provider changes remain element-local, tested separately. No binaries/images/secrets/raw user chats are committed.

Final gate result: `BrowserWasmTests.test_independent_browser_wasm_actual_chromium_and_owner_provider_locality` **1 passed, 0 failed; 211.891s**. This includes real static-only Chromium and strict stable-target, InitializeBody-only/zero-contract locality. Final standalone package build recorded zero warnings. Strengthened independent Chromium rerun also passed all same-origin GET-only networking and preserved DOM/card/input identity assertions; `/tmp/confectory-wasm-chromium-final.log`. SDK tool/test assembly builds recorded zero warnings/errors. Existing native/Android functional gates are separate; their selected target-body declarations were preserved and Android Planner selection checked by the WASM gate.
