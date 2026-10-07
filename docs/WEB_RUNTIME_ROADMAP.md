# Independent browser runtime: next-stage handoff

The shipped first phase is a **local .NET loopback host displayed in Chromium**, not an independent browser/WASM engine. The compiled public-link application runs on the machine, while HTML/CSS/JavaScript render and collect input in the browser. The website cannot run without that process and the trusted repository metadata hosts. Browser file imports transfer only the explicitly chosen file to that same machine's loopback process. No Internet service or deployment is involved.

An independent browser target remains required to fulfill the complete requested web runtime. This cannot be reported as finished merely because the local browser UI passes.

## Tooling observed

Read-only `/workspace/toolchains/dotnet-8.0.425/dotnet workload list` lists `android` only. SDK workload manifests describe `wasm-tools`, but installed runtime packs do not contain `Microsoft.NETCore.App.Runtime.Mono.net8.browser-wasm` or the browser cross-AOT pack. Chromium and Python Playwright are installed and usable; neither browser nor Python packages needed installation. No WASM workload was installed by this worker. User approval for Android SDK/JDK tooling does not automatically settle new WASM development-tool scope.

## Concrete independent-runtime route

1. After tool scope is authorized, use the supported .NET 8 `wasm-tools` workload and a pack-owned WebAssembly build-target executable. Produce the WebAssembly runtime, managed public-contract/provider assemblies, generated bindings, and static bootstrap assets. Preserve public linkage catalog and report output files; core still only exchanges its existing build tool protocol.
2. Keep `Confectory.EditorHome.Model` contracts as the shared model. Add browser-specific model initialization and providers for metadata description and file storage. Browser file selection/content bytes go into session-owned virtual storage; no direct OS paths, Process invocation, build tool execution or registry code execution. Imported dependencies need explicit multi-file/directory import or a declared absent capability.
3. Implement a browser provider with DOM/JavaScript interop rather than `HttpListener`. Bind the model's public CreateSession/Command/Snapshot/CloseSession operations through generated linkage and interop entrypoints. DOM text inputs own IME/composition; browser surface and document lifetime are explicit capabilities, not simulated native multiwindow.
4. Metadata parsing can reuse platform-neutral declaration parsing behind a reusable metadata contract, with no new platform logic in core. A metadata provider must not call the desktop external process. Dynamic C# compilation, SDK invocation, native dialogs and file associations remain absent unless independent providers are implemented. Plain import/edit/download is a valid restricted capability, but browser engine code actually has to run in WASM to count as that target.
5. Run Chromium against locally served static output with the .NET backend stopped. Verify initial runtime startup, render/input/IME where supported, file import/repeat/cancel/dirty protection, Leave/reopen, no unexpected network or external service, browser reload/lifetime cleanup, honest missing build/run/native capabilities, and output integrity. Re-run native/Android consumers after shared contract changes.

This route requires implementation and real runtime artifacts/tests, not just adding a `web` target name or copying HTML. The current local-host build target is described explicitly as local and must remain distinguishable from the independent runtime target.
