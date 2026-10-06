# Platform and backend substitution conformance gate

Pause unrelated product feature expansion. Current gate combines shared native text/folder boundaries with a bounded language/backend stress test. Compiler is C#/.NET on the PC; firmware must have no CLR or engine. No Arduino flashing or C# transpiler. No installs/licenses/accounts without explicit approval. Apple gets architecture review first, not silently added full implementation.

| Target | Current build backend | Native service boundary | Artifact/package/runtime evidence and blockers |
|---|---|---|---|
| Windows | Build.DotNet Portable | NativeUI desktop role pack target body: Rich Edit child HWND; native Shell folder dialog on owned STA; common BaseUI bridge | Managed compile is possible; real Windows/IME/candidate anchoring and dialog runtime require Windows. No Wine/cmd/PowerShell here. |
| Linux | Build.DotNet Linux | Installed GTK3/GtkSourceView4 native controls; explicit X11 foreign-parent/lifecycle; GTK native folder dialog | Actual native prototype Ctrl+A/edit/isolation/close passed. Full editor/picker/cancellation/selection gates still pending. This is X11, not verified native Wayland. |
| Android | Portable currently only managed profile | Required app-owned EditText, Activity lifecycle/UI-thread, system document-tree picker/granted URI | Native provider pack absent; contract binding fails before compilation. Java runtime21 present; javac/adb/sdkmanager absent. Managed profile is not APK/device input/IME coverage. |
| Web | No actual browser build backend yet | Required DOM input/textarea, browser IME, user-activation/permission-bound file APIs | Native provider and browser backend packs absent; binding/build cannot succeed. The diagnostic test checks missing implementation resolution; no fake browser provider is declared. |
| MEGA2560 | No current AVR/C++ backend | No UI; target GPIO/delay and target-owned setup/loop | g++ host exists; arduino-cli and avr-g++ absent. Real AVR firmware build blocked unless toolchain is authorized/provided. No emitted ELF/HEX or flashing claim. |
| Apple | Architecture compatibility review only | Would require AppKit/UIKit text/dialogs and signed app/lifecycle/permissions | No current backend/native/signing/device gate promised. |

`NativeUI::Capabilities` in the installed desktop role pack records implemented service/prerequisites and selected target, not successful runtime evidence. Tests/report records supply evidence separately. Core namespace+ID binding and target-specific body choice already enable native provider substitution without putting OS branches in each UI consumer. Compilation backend and runtime capability ownership remain distinct.

Filesystem locators are a discovered desktop-provider assumption: current desktop consumers/ProjectManager use fully-qualified paths. Browser handles and Android granted URIs are not equivalent. A future provider must return a tagged locator/permission context, and the consuming storage/project role must support that kind or reject it. Do not fake a desktop path or grant broader access. Native Create borrows an explicit surface identity/View; only target provider interprets that identity as HWND/XID. Other targets need app/DOM surface registries, not raw pointer assumptions in BaseUI.

## Bounded compiler extraction plan, before implementation

Actual `Core/Build.cs` calls `Generation.ContractSource`, `ImplementationSource` and `FinalSource`, chooses `.cs`, fingerprints `confectory-csharp-interface-v1`, requires assembly/reference artifacts and mandatory run command. `Core/Generation.cs` embeds CLR implementation types and catalog details. Thus adding an Arduino buildtarget alone cannot currently produce firmware correctly.

Minimal generic change: preserve parser/dependency/binding/cache/locality orchestration, pass normalized public signatures/import bindings/effective target bodies/object metadata to backend tooling. Move C# emission/CLR-specific catalog to a C# backend/tool. Fingerprint backend ABI/options/tool dependencies and normalized source input. Replace mandatory DLL/run assumptions with typed public/implementation/final artifact roles and executable-vs-build-only output. Preserve existing C# report aliases/catalog/commands and consumer behavior through compatibility tests; no Arduino-specific conditional in core. Source-language bodies are explicitly authored per language; no translation of arbitrary C#.

Then create a minimal shared C++ backend supporting only void/bool/int32 contracts, an authored Blink graph and GPIO/delay contracts. MEGA target owns Arduino setup/loop/FQBN `arduino:avr:mega:cpu=atmega2560`; another host g++ profile uses the same C++ backend to prove extension rather than board-specific core code. Compiler driver stays managed on PC. Check real artifact architecture/type and no CLR dependency. AVR compilation remains blocked by missing toolchain; intermediate source generation is separate evidence, not firmware success.

Core files needing bounded edits: Build's normalized requests/cache/artifact/run validation and language-neutral catalog projection; a small protocol/DTO boundary; existing C# emitter extraction and target tool adaptation. Parser/dependency resolver/engine-host semantics need no Arduino rewrite. Before changing these files, keep the native draft independently reviewable and establish old C# baseline/public compatibility tests. Do not silently weaken tests because the first backend was tightly coupled.

## Reusable substitution method (later Agent providers)

1. Record public contracts, target/provider selection and actual runtime capabilities independently of build success.
2. Construct a second independent consumer/provider to expose first-provider assumptions (CLR artifacts, desktop paths, native pointers, UI-thread/message pump, provider-specific error/state shapes).
3. Separate functional, lifecycle/permission, locality and packaging/runtime gates; preserve deterministic failure and explicit unsupported modes.
4. Fingerprint ABI/options/dependencies, test provider-only replacement and bounded rebuild, and preserve owner/state on cancel/failure.
5. Keep provider data behind the contract; do not let Helper/Worker consume Agent vendor IDs, session internals, transport errors or credential setup directly.

The Agent use is future validation pattern only. No Agent implementation/live API/credentials/provider calls are in this gate.
