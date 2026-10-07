# Generic browser platform provider increment

The user authorizes normal target provider and common runtime development. The same editor ProjectPack/content is the acceptance consumer; tests remain intact. The old model-only browser demonstration is excluded from this gate and preserved separately, as is the loopback .NET route.

Provider IDs: existing Window Capabilities/CreateSurfaces/Close/SurfaceDimensions, RenderInput Pump/Draw/DrawText/MeasureText, NativeUI Request/Capabilities, FileStream Capabilities, ProjectEntry Request. Only browser target bodies are added; common/Windows/Linux/Android bodies remain selected for their targets. NativeInput editing contracts remain unchanged.

The browser has one document surface, Canvas rectangle/text rendering, six-integer input records using common Linux-style key values, DOM single/multiline fields with retained binding identity, UTF16 caret/selection, IME composition protection, actual field snapshot/events/frame/clip/focus operations, and selected folder/file bytes staged in virtual storage. Native OS multiwindow, process launch, native filesystem, IPC and dynamic compilation are unavailable capabilities. Folder selection uses a browser file picker rather than an OS pathname grant.

The reusable target Platform element selects generic platform assets. The target Bridge installs provider delegates and invokes ordinary generated entry. HostLoop registers a token whose captured Step/dispose callbacks are dispatched through requestAnimationFrame; no editor screen, Action or layout is copied into JS. The existing Browser target's separate demonstration assets and loopback host remain independent.

Outside implementation reads/edits: actual editor Main/MainBody to identify assumptions; NativeInput Field/Poll/Frame/Focus/Clip to preserve low-level JSON; Window metrics/surface contracts to reproduce real renderer geometry; browser build host/bootstrap edited because only this trusted target can connect JS imports and exported Step without core hardcoding. FileStream capabilities updated because common body falsely described an OS filesystem in browser. ProjectEntry browser body explicitly supplies local listen/poll/reply/close lifecycle without native IPC.

Rebuild scope: browser-selected provider assemblies plus browser target/bootstrap/asset output. Common function signatures unchanged. HostLoop is a separately owned shared-contract increment with desktop/browser consumer gates. Functional status at first provider commit: host build `dotnet build targets/browser-wasm/Confectory.Build.BrowserWasm.csproj -c Release --nologo` succeeds with zero warnings/errors on SDK10.0.401; `node --check packs/browser-platform/assets/app.js` passes. Actual same-editor Chromium acceptance is still pending shared runtime integration and must not be inferred from these checks. No deploy or push.

## Actual same-product gate outcome (WIP, not integrated architecture baseline)

Local branch `integration/browser-native-boundary` starts from root `840180b`; provider increment `8b61103`, SDK compatibility increment `daf91bf`, consumer wiring/test increment `96e7938`. Root's architecture audit freezes a separate `4e37` snapshot; this WIP must not be read as evidence that the frozen snapshot has generic portability.

Command (SDK10.0.401, official wasm-tools10.0.112):

```
dotnet src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll build examples/editor-home/project.cpack browser
python tests/web/editor_home_browser.py /tmp/confectory-same-editor-browser-build.json
```

The actual ProjectPack build succeeds, `entry = Confectory.EditorHome::Main`, `warnings = []`, static output contains actual native-linked WASM. The build report is `/tmp/confectory-same-editor-browser-build.json`. Its compiled common Main includes the `9ca75de` lifetime-release stage; the later `5043856` fix was applied while this build ran and is preserved in current source, but not claimed as its compiled code. Actual common Main, not the model-only browser demonstration, is selected.

The unchanged real Chromium gate **fails during entry startup**, before any RAF callback or editor rendering. Error: `System.PlatformNotSupportedException: Arg_PlatformNotSupported`. An exception-logging-only diagnostic rebuild of local generated Bridge confirms this exact stack:

```
System.Runtime.InteropServices.PosixSignalRegistration.Register
System.Runtime.InteropServices.PosixSignalRegistration.Create
System.Console.add_CancelKeyPress
Confectory.Implementations.[actual EditorHome MainBody].Invoke
Program.Main
Confectory.Browser.Bridge.Initialize
```

Evidence: `/tmp/confectory-same-editor-browser-smoke.log`, `/tmp/confectory-same-editor-browser-diagnostic.log`, `/tmp/confectory-same-editor-diagnostic-build.log`. The diagnostic republishes only the local generated project with managed exception logging; resource paths were adjusted after the Builder renamed its pending output directory. It is troubleshooting evidence, not an acceptance build. No common UI behavior or assertion was bypassed. No startup/render/input/open/edit/close success is claimed. No final visual screenshot exists because startup stops first.

The independently prepared shared HostLoop signal ownership fix `9a07c4a` moves OS signal subscription to the desktop provider; it remains outside this tested WIP and needs root audit disposition/integration and a fresh same-consumer build/Chromium gate. Root requested stopping larger implementation during architecture audit; provider WIP is preserved. Remaining browser provider behaviors are unvalidated until entry starts. New project scaffolding requires a legitimate virtual-storage/project-provider treatment; dynamic compilation and native OS folder opening stay unavailable. Loopback and earlier separate demonstration remain available independently and do not substitute for this failed gate.


## Superseding final resource/provider acceptance — 2026-10-07

The earlier startup failure above is superseded by the desktop-only signal provider and retryable shared HostLoop.Close implementation. Product source is frozen at `03aed0d`; this follow-up changes only test cancellation annotation and documentation. The actual same EditorHome ProjectPack now passes a fresh native-linked .NET10 WASM build and Chromium acceptance, with no generated-output edits, no .NET backend, and GET-only local static serving. Auxiliary demo and loopback routes remain separate and are not portability evidence.

Target resource contract: existing public Tool.Options declare `compiler` (installed `compiler/Confectory.Build.DotNet.dll`) and `assetRoot` (`assets/platform` or auxiliary `assets/demo`). Paths resolve relative to the installed target host, using symlink-aware `PackPaths.Owned` for directories and each copied file. MSBuild packages owned compiler/assets/templates. No repository-root discovery, EditorHome namespace/path/schema selection, or Core changes remain. A copied target in `/tmp/Confectory target 이름` and unrelated renamed consumer `Unrelated.Renamed` passed actual Chromium entry startup without Home owner/snapshot assumptions. Escaping asset symlinks reject with `Path escapes its owning pack`.

Provider public IDs are the existing Window, NativeUI, RenderInput, FileStream and ProjectEntry roles listed above; signatures are unchanged. NativeUI.commands now retains declared handled keys and prevents native insertion only for routed keys, with actual Enter registration/unregistration and emoji keyboard selection gates. Wheel uses ±120 records; Unicode input emits scalar records. Successfully released NativeUI owners have bounded 4096-token tombstones, retaining no DOM; unknown and expired tokens reject. Surface release does not erase unreleased NativeUI handles. Actual DOM release fault injection proves first close failure retains ownership and subsequent public Close succeeds.

Shared-contract change: HostLoop.Close is supplied by the separately owned runtime increment and consumed through its browser-installed delegate. The private Step callback registry is still read by trusted SDK interop because public Run does not export a browser frame callback. This outside implementation dependency is explicit and deferred to a separate public HostLoop ABI increment; it is not a Core special case. Outside reads included NativeInput payload contracts, actual common Main, platform metrics and SDK native-link properties. No editor UI/screen/layout implementation was copied into HTML or JS.

Exact final commands (SDK10.0.401, official wasm-tools10.0.112):

```sh
dotnet build Confectory.sln -c Release --nologo
dotnet src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll build examples/editor-home/project.cpack browser > /tmp/confectory-same-editor-browser-frozen-final-build.json
python -u tests/web/editor_home_browser.py /tmp/confectory-same-editor-browser-frozen-final-build.json
python -u tests/web/browser_bootstrap.py /tmp/confectory-browser-renamed-relocated-build.json
```

Solution: zero warnings/errors. Build: 110 contract and 110 implementation target invocations, one link, zero fullRebuilds; the changed target compiler fingerprint causes selected artifact recompilation. Functional acceptance and locality are distinct: this proves consumer correctness, not absence of target-fingerprint cache coupling. The common Main is selected and its current source is byte-exact inside its generated implementation: SHA256 `ea2c4102d69eb52cd7654d8ff3a5cf9ef744e579daef84d3a2a2beb8d77b39f5`. Installed/output app.js equals source SHA256 `cb840ec0f1b8c1a17a1e2065ef5f0bc0c848e2ebb229fd17a96ee51e49c50546`.

Evidence remains private under /tmp: final build report, `confectory-same-editor-browser-frozen-final-chromium.log`, renamed/copied-target Chromium log, and first/create/project screenshots. Gate covers actual common entry/render, Latin/Unicode inputs, focus/commands, wheel, file import, metadata-only untrusted registry, repeated leave/reopen, retained controls and cleanup retry. Cancellation invokes the actual public NativeUI.folder-cancel operation after a real chooser opens; physical OS chooser Cancel is not exercised because Playwright cannot clear a webkitdirectory chooser.

Remaining capabilities: one browser document surface; virtual process-memory storage, not native filesystem grants; no dynamic compilation/process execution/AI/native IPC or native folder launch. New-project input UI is verified, but successful project scaffolding/build is not claimed. No deployment, external upload, push, binaries, screenshots or raw logs were added to Git.
