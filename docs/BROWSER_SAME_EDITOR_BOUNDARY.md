# Same editor browser boundary audit

Baseline: `4952a2c`. This audit reads the actual `examples/editor-home` entry; the separate `editor-home-browser` demonstration is excluded from desktop editor portability evidence. No example behavior, view, model, or core was changed.

## Proven source boundaries

| Source | Boundary | Provider-only consequence |
| --- | --- | --- |
| `examples/editor-home/Main.csbody:1` | Requires `Window.Capabilities()[0] == 1`; contract describes multiwindow. | A single browser canvas must not return a false native-multiwindow capability to bypass the guard. |
| `Main.csbody:26` | `Task.Run` executes model commands. | Single-thread WASM cannot substantiate independent background execution. |
| `Main.csbody:103,111,112` | Synchronous loop, `Thread.Sleep(2)`, final blocking task completion. | Ordinary browser main-thread entry prevents DOM event processing. A real worker/thread execution bridge needs verification. |
| `Main.csbody:33,42,50` | Calls `Process.Start(explorer.exe/xdg-open)` directly. | No Window/NativeUI provider can intercept this call. Browser folder semantics require an explicit public operation or capability-aware input-pack change before source edits. |
| `MainBody.celem` | Android selects `Main.android.csbody`; common selects desktop Main. | Android target entry override is not proof of unchanged common entry portability. |
| `Main.android.csbody` | Calls NativeUI `android-home` and returns. | Current Android facade owns a separate lifecycle entry. |

`BaseUI.NativeInput` can remain reusable: its public provider route is NativeUI Request. Field configure JSON includes id, binding, bounds, value, caret, anchor, mode, hint, visible, enabled and readonly. Snapshot rows must retain deferredExternal, focus and editing state; Poll consumes snapshot and events and updates the real BaseUI text buffer. Replacing these with an unrelated HTML model loses the actual editor boundary.

## Installed .NET 10 feasibility evidence

The installed `/workspace/toolchains/dotnet-10.0.401/packs/Microsoft.NET.Runtime.WebAssembly.Sdk/10.0.12/Sdk/BrowserWasmApp.targets` contains `WasmEnableThreads`, includes `dotnet.native.worker.mjs`, and passes IncludeThreadsWorker and IsMultiThreaded to build tasks. `WasmApp.Common.targets` adds `--apply-cop-headers` when threads are enabled. These are installed SDK capabilities, not a tested editor execution result. A threaded/worker host requires cross-origin isolation and an explicit worker-to-DOM provider bridge. The trusted build host must preserve the actual generated entry and selected public providers; no hardcoded core editor host is justified.

A worker can potentially address the loop and background-task boundaries. It cannot make a single document native multiwindow or replace direct OS process calls. No same-editor Chromium acceptance is claimed. The .NET 10 migration worker owns target Program/project/framework edits; this increment does not overlap them.

## Required decision before behavior edits

Resolve the real editor's capability requirement and direct folder-opening operation through an explicit input-pack/public-contract decision. Do not silently relax the guard, change example view behavior, or substitute the earlier demonstration. After this decision, implement reusable Window/RenderInput/NativeUI/ProjectEntry/metadata target providers and test the unchanged selected editor content on an actual worker-enabled browser runtime. Native filesystem and dynamic compilation remain unsupported browser capabilities unless separately provided.

## Scope ledger and gates

Intended identities: existing Confectory.Window, Confectory.RenderInput, Confectory.NativeUI, Confectory.BaseUI.NativeInput, Confectory.ProjectEntry and metadata providers. Actual increment: documentation only; no public contract or implementation changes. Outside reads: actual editor Main/MainBody/Android body to identify consumer assumptions; NativeInput Field/Poll/Create to recover provider JSON; Window Capabilities/CreateSurfaces/Pump contracts to distinguish native and browser capabilities; installed SDK targets to inspect worker support. Existing contracts are insufficient for the editor's direct Process.Start call.

Rebuild scope: none. Structure gate: example/provider/core source hashes remain unchanged in this increment. Functional gate: read-only audit, not runtime acceptance. Commands: `git show 4952a2c:examples/editor-home/Main.csbody`, `git show 4952a2c:examples/editor-home/MainBody.celem`, `git show 4952a2c:packs/base-ui-native-input/Poll.csbody`, and `rg -n 'WasmEnableThreads|worker' <installed WebAssembly SDK>/Sdk/BrowserWasmApp.targets`. No deployment, upload, or push was performed.
