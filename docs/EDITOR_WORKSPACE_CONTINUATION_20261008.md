# Actual editor source workspace continuation

Product: `examples/editor-home/project.cpack`, entry `Confectory.EditorHome::Main`. The common product controller remains the selected controller on Linux, Windows, Android and browser. PackWorkspace is a normal role dependency; no core engine/editor host or alternate success demo was added. Original `[Checkpoint 1]` remains in history.

The initially simple workspace now offers **Edit sources** explicitly. Selected owned element/body Views use stable BaseUI text buffers, Prev/Next and bounded source pages. Save draft writes the existing identity-local Save record; final source bytes are unchanged. Reload source explicitly adopts a conflicting current revision. Working-copy export overlays the public owned source texts into ZIP, including newly created metadata and the edited manifest, without applying or executing them. Browser download `offered` is distinct from Android/desktop document `saved`.

Every source edit carries the View's expected revision. A conflict keeps its input buffer and reports the conflict; it does not silently replace the user's text. Source buffers are owned by the product controller and keyed by selected context plus element ID. Separate project contexts retain independent inputs. PackWorkspace owner handles are retained until session cleanup, and failed individual cleanup remains retryable. No implicit Confirm or dynamic compiler capability was introduced. Creation on Android/browser uses owned standalone source templates with honest missing desktop compiler provisioning instructions.

Browser-owned files restore from bounded IndexedDB before the actual entry starts. Save requests the existing generic NativeUI storage-flush/poll contract and reports acknowledged save only after the provider completes. Browser acknowledgement means a completed origin-storage transaction; local desktop/Android acknowledgement follows the completed local filesystem write. Abrupt tab closure cannot guarantee unfinished transactions complete. The existing chat draft remains runtime-only.

## Increment and locality ledger

Intended packs/public IDs: `Confectory.PackWorkspace::{Open,Snapshot,Command,Close}`; `Confectory.ProjectManager::CreationTemplate`; `Confectory.FileStream::{ArchiveSources,ArchiveSourceTexts}`; existing `Confectory.NativeUI::Request` operations archive-begin/poll/cancel and storage-flush/poll; existing `Confectory.EditorHome.Model::{CreateSession,Command,CloseSession}` and `Confectory.EditorHome::Main` consumers. Public function signatures of existing consumers remain unchanged.

Actual outside implementation reads: EditWorkspace Read/Open/Create and Save/Restore ownership and draft boundaries; SchemaEditing formatting/metadata target transport; product model session dictionaries and commands; Main stable native fields, UIOrder clipping and lifetime; platform Request providers and existing GTK/Win32/document import infrastructure. These reads established existing public return shapes and missing target providers; private editing state is never accessed by the new consumer at runtime. Source paths are taken from public PackWorkspace sources and duplicate identical paths are coalesced; divergent texts sharing one physical path are rejected. Archive scope is the selected pack's declared owned units and local draft manifest. Registry packs, compiler tools and undeclared assets require separate explicit provisioning/export; the ZIP alone is not a fully provisioned build distribution.

Outside edits: actual product manifest/declarations, model session/command/cleanup and common Main; existing auxiliary Home consumers' provider declarations/role registries because model's new role dependencies must resolve in every consumer scope. Target metadata formatters and browser bootstrap changes are generic providers, described in their owning increment records. Core unchanged. No namespace-specific import, fixed editor alias, generated-output patch, binary/image or private log enters Git.

Affected rebuild: the new role contracts/providers and their explicit consumers on first build; subsequent Main/Command body edits rebuild those individual implementations. SchemaEditing target selection and platform transport/template changes rebuild selected provider/output, requiring actual WASM/Android regeneration. Auxiliary role locality and functional tests are separate from actual product GUI acceptance. Current EditWorkspace Open eagerly snapshots selected owned units; page-limited Views do not claim lazy source indexing.

## Verification and remaining coverage

Results and exact commands will be appended after the actual frozen product gates finish. Initial integration exposed missing explicit Save Restore provider selection; consumer declarations were corrected rather than hiding the build failure. Existing GTK chooser 10-second intermittent failure remains recorded in SOURCE_EXCHANGE_INCREMENT and is not resolved by replacing its input, timeout or temporary-directory conditions.

Windows OS execution and Android device execution remain asynchronous user spot checks. Windows JAVA_HOME diagnosis waits for the user's actual message; no user PC settings or installations were changed. Existing Android runtime RELRO issue and official workload-download blocker remain separate toolchain limitations; source-provider managed/native compile is not evidence of Play or device coverage.

### Verified stage and preserved failures

Source workflow at commit `3c8f06f`: actual Linux X11 full flow PASS against `/tmp/confectory-workspace-linux-final-build.json`; actual Chromium full flow and unchanged browser input/import/owner regression PASS against `/tmp/confectory-workspace-browser-final-build.json`. Both use the actual common Main and ordinary compiled ProjectPack. Linux assertions include stable native source field, 760×620 and 1000×760 resize, repeated Save, leave/reopen, process restart, saved source restoration, a real GTK ZIP save, ZIP edited body plus ProjectInfo/manifest, unchanged final body and two Owner cleanup completions. Browser additionally verifies origin-storage Save acknowledgement and page reload before export; a download offer is not durable external-file acknowledgement. Root inspected the private normal and narrow Linux screenshots; no images were committed. The narrow layout follow-up read existing BaseUI Stack clipping behavior because its public extent contract did not specify how exhausted fixed-width slots disappear; its implementation was not edited.

Latest source `c58a5f0` adds a two-row source toolbar below 460 pixels of workspace width. Linux partial flow verifies 480×620 source buffer/control/native field retention, confined visible hit regions, Save and process restart restoration. Its final GTK export gate failed the unchanged 10-second chooser condition; two further unchanged runs failed the parent chooser. Those are preserved, not relabeled as a current whole-flow PASS. Screenshot `/tmp/confectory-workspace-responsive-replay-chooser-failure.png` shows only `/tmp/co` in the location entry despite the driver sending the complete path. No provider exception is logged. This supports an input/GTK response symptom, but does not establish the underlying cause. No input, timeout, TMPDIR or settings substitution was used to manufacture a pass.

Sandbox default Linux startup also failed at the existing read-only `/home/agent/.local/share/Confectory` listener storage. The configured path below is an existing supported public setting; the default failure remains separate. Actual current Windows/Android managed builds pass with warnings `[]`; source-only Android export and API36/JDK21 SDK Compile pass with zero warnings/errors. No latest APK/AAB, signing/key generation, device install or native OS/device runtime follows from Compile. Installed Android emulator and system-images are absent; read-only adb enumeration was blocked before device presence could be established. No writable adb home was substituted, because it could generate unauthorized keys.

Commands from the repository root (SDK10.0.401):

```
export DOTNET_CLI_HOME=/tmp/confectory-dotnet10
export CONFECTORY_DOTNET=/workspace/toolchains/dotnet-10.0.401/dotnet
$CONFECTORY_DOTNET build Confectory.sln -c Release --nologo
$CONFECTORY_DOTNET tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll --require-runtime PackWorkspaceTests fresh_entry_home_project_contracts project_shell_domain
$CONFECTORY_DOTNET src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll build examples/editor-home/project.cpack linux
$CONFECTORY_DOTNET src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll build examples/editor-home/project.cpack windows
$CONFECTORY_DOTNET src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll build examples/editor-home/project.cpack android
$CONFECTORY_DOTNET src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll build examples/editor-home/project.cpack browser
DISPLAY=:96 CONFECTORY_GUI_REPO=/workspace/Confectory CONFECTORY_ENTRY_STORAGE=/tmp/confectory-workspace-gui-entry XDG_CACHE_HOME=/tmp/confectory-workspace-gui-font-cache python3 tests/gui/editor_workspace_x11.py /tmp/confectory-workspace-linux-responsive-build.json
```

The integrated auxiliary suite passed **4/0/0, 196.482s**, covering PackWorkspace target metadata/owned sources and revision/Save/restore/locality, actual Home model contracts/locality and ProjectShell isolation/cleanup. Latest solution build passed zero warnings/errors. The responsive body-only increment on all four targets compiled **only MainBody, zero contracts, zero full rebuilds**. Earlier final Linux guard change compiled exactly MainBody and Model CommandBody, zero contracts. These build statistics are structure/locality evidence, separate from the functional gates.

Latest Android compile commands use the existing exporter and tools; no package or signing target is invoked:

```
$CONFECTORY_DOTNET targets/android-export/bin/Release/net10.0/Confectory.AndroidExport.dll examples/editor-home/project.cpack /tmp/confectory-workspace-android-native-responsive
cd /tmp/confectory-workspace-android-native-responsive
ANDROID_HOME=/workspace/toolchains/android-sdk JAVA_HOME=/workspace/toolchains/jdk-21 $CONFECTORY_DOTNET build Confectory.Android.csproj -t:Compile -c Release -p:AndroidSdkDirectory=/workspace/toolchains/android-sdk -p:JavaSdkDirectory=/workspace/toolchains/jdk-21
```

The exporter was normally rebuilt after detecting stale copied templates, then exported into a new directory; generated output was never patched. GenericActivity and MetadataAuthoring final copied bytes match source. Managed/native proofs and SHA are in private `/tmp/confectory-workspace-platform-source-evidence.json`. Current Main SHA256 is `a8b5637e9599f97358b94cd574a22e2a57dc92fa7183174d7995bf0a0b980241`.

A final concurrent full-solution build exposed a browser target output race: SDK build catalogued the old mutable external Core HintPath, publish later reread the replaced DLL, and Chromium SRI rejected the result despite SDK build success. `BROWSER_PUBLISH_INTEGRITY_FIX.md` records exact original failure and generic fix: snapshot all references into an output-owned sibling directory outside the SDK project before invoking SDK, choose the exact SDK publish bundle and verify every named boot SHA256 resource before reporting `ok`. Integrity remains enabled. Target fingerprint changes intentionally rebuild the browser-selected output; no core/product-specific logic was added. Post-fix actual product results will be appended after execution.

### Final browser output and delivery gate

The first immutable-input attempt placed DLL snapshots inside the SDK project and failed StaticWebAssets compression before publish. A controlled same-Core/same-SDK location experiment reproduced that failure inside the project and passed with a sibling snapshot directory. The final generic target keeps snapshots in `output/owned-references`, outside `wasm-project`, preserving compression and SDK-generated bytes. Original failed logs and the location A/B evidence remain in `BROWSER_PUBLISH_INTEGRITY_FIX.md`.

Final actual browser build `/tmp/confectory-workspace-browser-sibling-fixed-build.json` PASS: entry `Confectory.EditorHome::Main`, `tool.ok=true`, warnings `[]`, full SDK boot SHA256 validation completed before output success. The target fingerprint change compiled the browser-selected 120 contracts and 120 implementations and linked once; this is the explicitly affected target scope. It is separate from the earlier four-target MainBody-only locality gate.

Both current product gates PASS:

```
python3 tests/web/editor_home_workspace.py /tmp/confectory-workspace-browser-sibling-fixed-build.json
python3 tests/web/editor_home_browser.py /tmp/confectory-workspace-browser-sibling-fixed-build.json
```

The current source workflow includes actual 1200px creation/edit/acknowledged Save, leave/reopen, 480×850 resize with identical DOM source field/value and visible bounds, wrapped Save acknowledgement, return to wide layout, page reload/owned-draft restoration and actual ZIP download/content validation. Final source stays unchanged. The unchanged actual browser regression covers native input semantics, folder import/cancel, stable controls and retryable owner cleanup. Static traffic remains GET-only; no generated code/DLL/boot catalogue was patched. Evidence is private `/tmp/confectory-workspace-browser-sibling-fixed-{actual,regression}.log`.

The compiled target integrity gate separately accepts the preserved real good bundle and rejects the original broken bundle with the exact Core mismatch. Latest target build used `dotnet build targets/browser-wasm/Confectory.Build.BrowserWasm.csproj -c Release -p:BuildProjectReferences=false --nologo` after the full solution had already passed, keeping its unchanged built Core dependency stable; target build passed zero warnings/errors. This flag preserves existing compiled project dependencies and does not weaken output validation.

User checkpoint: on this integration branch, open the ordinary Home launcher, create or explicitly open a pack, choose Edit sources, edit an owned body, Save draft, leave/reopen and then Export ZIP. Save restores local differences; Run continues to use final source until an explicit compiler-backed Confirm stage exists. On browser, keep the same origin for persisted owned files and wait for Save acknowledgement before closing. Actual Windows OS/IME/DPI and Android device touch/surface/lifecycle/SAF checks remain asynchronous. The GTK original chooser gate remains unresolved and is explicitly not replaced by browser success.
