# Pack-owned compilation and DLL boundaries — 2026-10-08

Work branch `pack-dll-boundaries` starts from fetched `origin/main` 8fab4abc9c5d56a9c9443c334e769f45247a4bd3. Earlier integration commits and the user's main merge are preserved. This branch may be pushed; main merge/direct push, deployment and signing are not part of this change.

## Physical unit and preserved logical contracts

A selected owning namespace now produces at most one `Contracts_<namespace-symbol>.dll` and one `Pack_<namespace-symbol>.dll`. A pack with only one selected role produces only that role. Each compile also emits a build-only `.ref.dll`; references are not deployed. Final bindings remain a separate `Confectory.App.dll`. Packs are never merged across manifests to reduce this count.

Independent namespace/element IDs, generated interface/type names, signature validation, scoped providers, dependency analysis, target-first/common fallback, recursive calls and public linkage catalog mappings remain. Element artifact maps now alias their physical owner pack file; `assembly` is the actual pack assembly and `assemblies` contains one path. Compile/reference/link inputs are deduplicated. Protocol 1 already accepts source arrays, so each contract/implementation pack is compiled with one multi-source request and one compiler invocation. No persistent compiler server or extra target installation is introduced.

Contracts remain separate from implementations to allow cyclic function calls and local checks without implementation providers. Implementation packs still reference contracts/framework only, never another pack's implementation assembly. Pack boundaries do not provide a security sandbox. Same-pack sources share their physical compilation ownership; public imports remain the supported authoring route. No runtime mod loader or private cross-pack reference permission was added.

Current physical declarations are distinct: `packs/base-ui/pack.cpack` owns Confectory.BaseUI controls/layout; `packs/window/pack.cpack` owns Confectory.Window platform window/render-input providers. BaseUI has no Window element in its current manifest; editor-home explicitly registers both, and Window declares RenderInput dependency. The user subsequently accepted keeping this split where it benefits reuse: controls/layout and platform window providers remain independently consumable. This compiler change does not combine/reclassify them. In actual Linux editor-home, Window's 19 selected implementations share one implementation DLL.

## Selection, invalidation and ABI migration

Final compilation still prunes unselected bodies and contracts, even inside a reached pack. A local Check includes all owned implementation declarations and only their required contracts; a pruned final build can therefore have a different artifact key. Whole-check/final reuse requires matching selected sources and observed contract-pack keys. A body change recompiles all selected implementations of its owner pack once, while other packs reuse. A selected contract change replaces its physical owner contract DLL and invalidates every implementation pack referencing it, including references to other selected functions in that same contract DLL. Unselected contract changes remain unopened and do not invalidate final builds.

Sorted IDs/source content, target-tool fingerprint, generated ABI and observed contract-pack keys determine content-addressed artifacts. `pack-assemblies-v2` partitions all compile/link keys from the old element layout. Old artifact entries and successful runnable outputs are preserved, not deleted. Hash verification, atomic artifact/output writes and failed-build preservation remain. Declaration/body caches keep their existing schema.

Public ABI is `confectory-csharp-interface-v2-pack-assemblies`: interface type identities remain logically mapped but their assembly identities changed. Existing externally compiled DLLs referencing old per-function assemblies require rebuilding against the new catalog and contract DLLs. No binary compatibility/type forwarding or dynamic mod-loading promise is made. Catalog formatVersion 1 remains valid because its shape is unchanged and already carries explicit ABI and per-element assembly mappings. The future mod-loader boundary remains in MOD_EXTENSION_BOUNDARY.md.

Builder selection is refreshed for each Check/Build operation. This matters to the real SchemaEditing candidate validator, which calls Validate, Check and Build on the same Builder. A larger checked contract assembly must not leak aliases into the subsequent pruned final link.

`compiledContractPacks`/`reusedContractPacks`, `compiledPacks`/`reusedPacks` and target invocation counts describe physical work. Existing `compiledContracts`/`compiledImplementations` lists describe every logical element included in a rebuilt artifact; they are not compiler-process counts. Warm builds still perform one final link/package operation.

## Verification ledger

Intended ownership: Core Builder pack grouping/cache selection and BuildStatistics; Generation ABI. Actual outside reads: Resolution/Declarations/Infrastructure for scope, signature matching, pruning and caches; DotNet target compiler protocol/response files; BrowserWasm/Web link/reference handling; Android exporter reference copying/generated bindings; SchemaEditing/ElementAuthoring validation orchestration; relevant repository format/technical/mod design and readable baseline extraction sections about ownership, local compilation and public contracts. No AGENTS.md or .agents/skills were found in the scoped workspace search. Original Library DOCX byte-transfer blocker is not represented as newly resolved.

Outside edits: tests across pack consumers migrate per-element locality assertions to physical owner-pack assertions; the helper checks exact affected pack set, all selected logical implementations, a single shared assembly and one compile request per pack. Multi-implementation tests explicitly retain unused invalid-body pruning and distinguish full-check/final subsets. New compiler tests assert contract coalescing, physical DLL counts, compatible contract metadata invalidation, same-Builder Check→Build and retained prior executable behavior. The Android export test expects the new contract filename. Entry's old Android refusal diagnostic assertion is aligned to the current exact provider message, without changing provider behavior. The old editor Verify fixture now expects the already-established project.cproj creation filename while retaining exact Unicode/title and collision-byte checks; legacy opening behavior is unchanged. Engine native tests use owned entry storage/scope and include child diagnostics; input/close timings and product defaults are unchanged. The exact-body lifetime probe was brought up to the existing PackWorkspace owner dictionary/capability imports and now injects failure/retry for PackWorkspace owners and capability acquisition as well. The old editor Android expectation now checks successful managed compilation plus explicit runtime refusal and Android provider selection, rather than incorrectly expecting a missing implementation. README/technical design/handoff describe current boundaries. Runtime packs and target/compiler implementations are unchanged.

Functional and locality gates are separate. Historical per-body locality evidence in older checkpoint documents describes the previous compiler layout and is superseded by this physical pack policy; historical files are retained.

## Reproduction and evidence

Use installed .NET 10.0.401 on Linux x86-64, `CONFECTORY_DOTNET=/workspace/toolchains/dotnet-10.0.401/dotnet`, `DOTNET_CLI_HOME=/tmp/confectory-dotnet10`. No tools installed. Private evidence root `/workspace/confectory-pack-dll-evidence`; binaries, screenshots, source copies and raw logs are outside Git.

```sh
dotnet build Confectory.sln -c Release --nologo
dotnet tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll --require-runtime
# Targeted strict rechecks and native DISPLAY gates are recorded below.
python3 tests/performance/pack_build_boundaries.py OLD_CLI_DLL NEW_BASELINE_EVIDENCE_DIR
python3 tests/performance/pack_build_boundaries.py src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll NEW_PACK_EVIDENCE_DIR
```

The measurement script copies the actual editor-home source and an owned BaseUI pack, rebases registries, uses a new Confectory cache, and measures cold, unchanged warm, selected-body comment change and selected public parameter-name change. Parameter naming is real public metadata but keeps callable argument types compatible, allowing an otherwise identical actual product to build. It records wall time, physical DLLs, compiler calls, owner rebuild/reuse and logical contract effects. Cold means cold Confectory artifacts, not flushed OS/SDK caches; timings are single samples, not Windows measurements. Windows all-cold cache behavior reported by the user has not been diagnosed, and this change is not proof that every source of Windows delay is fixed.

## Final measured results

Canonical measurements ran consecutively after other task builds/tests had ended on Linux 6.18.44 x86-64, glibc 2.41, .NET SDK 10.0.401. The container reports 5 logical CPUs with cgroup quota 400000/100000 (4 CPU equivalents). No other task compiler ran concurrently; OS/SDK caches were retained. Initial concurrent exploratory samples are preserved but are not the table below.

| Actual editor-home scenario | Element layout seconds | Pack layout seconds | Old contract/implementation/link calls | New contract/implementation/link calls |
| --- | ---: | ---: | --- | --- |
| Cold artifacts | 157.844 | 32.093 | 130 / 130 / 1 | 23 / 22 / 1 |
| Unchanged warm | 1.386 | 1.336 | 0 / 0 / 1 | 0 / 0 / 1 |
| Selected BaseUI body edit | 2.155 | 2.286 | 0 / 1 / 1 | 0 / 1 / 1 |
| Selected BaseUI public parameter rename | 4.276 | 6.785 | 1 / 2 / 1 | 1 / 4 / 1 |

Every old scenario deploys 130 contract DLLs + 130 implementation DLLs + App = 261. Every new scenario deploys 23 contract DLLs + 22 implementation DLLs + App = 46. Cold wall time fell about 79.7% in this single Linux sample. Warm builds reuse all 130 logical contracts and implementations. The body edit rebuilds only BaseUI and reuses 21 other implementation packs. The contract edit rebuilds the BaseUI contract DLL (19 selected logical contracts), then BaseUI, BaseUI.NativeInput, EditorHome and UIOrder implementation DLLs; 18 others reuse. Old per-element layout rebuilt only the one contract and BaseUI/EditorHome implementations. This is the deliberate broader invalidation cost of shared physical contracts, not a promise that all increments become faster. Type-changing contract incompatibility/revalidation is separately covered by compiler fixtures; the actual product timing uses a compatible metadata rename.

Canonical evidence: canonical-element/measurements.json and canonical-pack/measurements.json under the private evidence root, with all four complete reports/stderr each. Reproduce using the script above with a new output directory. Pre-change CLI is preserved privately at old-cli/Confectory.Cli.dll; source checkout was clean before branching. The cache-migration probe builds in the old element cache directory using the new compiler, observes no old contract/implementation reuse, and verifies every old artifact and output remains present (migration-build.json).

## Completed gates and retained limitations

- Solution build zero warnings/errors (selection-fix build 3.78s); final tests-project build zero warnings/errors (3.82s). Core/target outputs were frozen before canonical measurements.
- Strict final compiler/graph/cache/protocol/reference suite plus ProjectEntry refusal: **84 passed, 0 failed, 0 skipped, 211.608s** (compiler-frozen-tests.log). Includes grouped assemblies, unused exclusion, body/contract invalidation, corrupt cache repair, selected target failures, provider-only reuse, cyclic/scoped calls, private cross-pack reference refusal and same-Builder Check→Build.
- Actual common editor-home root entry builds on Linux, Windows, Android and independent browser: each selects 130 logical contracts/implementations but invokes only 23 contract and 22 implementation compilations. Local web consumer also builds (12/12/1); it is the separate supported editor-home-web project, not a nonexistent web mapping in the native manifest. Initial attempt to build native project with web correctly returned MISSING_TARGET; that was a command choice, not a product regression.
- Actual X11 self-pack source review/Save/conflict/invalid candidate/restart/explicit Confirm/confirmed child Run/parent isolation/Stop/cleanup passes (linux-gui-selection-fixed.log). Review screenshot visually inspected. Existing post-Run capture limitation is documented in EDITOR_SOURCE_CONFIRM.md; native window IDs/model/logs establish child execution.
- Actual Chromium current root-entry source workspace, 480px layout, acknowledged save/reload/ZIP and common input/import/owner cleanup pass (browser-workspace.log, browser-common.log); browser-frozen-build.json was rebuilt after the final Core change.
- Actual product unsigned Android AAB SDK Package build passes, zero warnings/errors, 75.26s (android-package-frozen.log). It contains current Core bytes and 46 Managed DLL references (45 role DLLs + metadata Core), runs the declared generated actual entry, and official bundletool manifest confirms com.Confectory.Engine min24/target36. Signing/device/runtime/Play acceptance is unrun. The older standalone compile_api.py probe failed because it omits current MetadataAuthoring and generated Resource inputs; its android-api.log is retained. The full actual SDK build includes those inputs and succeeds; the auxiliary probe is not counted as passing.
- Actual X11 file-entry forwarding and Window lifecycle gates pass (native-frozen-tests.log, first two tests). Engine three-repeat two-window/local reopen/cleanup gate passes independently with owned writable entry storage, **1/0/0, 34.202s** (engine-native-owned-storage.log). Checkpoint7 actual scoped pixels/Confirm passes (shared-native-controls.log, first test).
- Broad initial --require-runtime run: **144 passed, 4 failed, 15 skipped, 1579.909s** (full-tests.log). This is not a passing full-suite claim. Four stale checks were corrected without product changes: Android Entry diagnostic, old editor new-project filename, old editor Android missing-provider expectation, and lifetime probe missing PackWorkspace/capability state. Strict individual rechecks pass respectively through the 84-test suite, editor-workflow-recheck.log (1/0/0, 34.954s), editor-targets-recheck.log (1/0/0, 69.264s), editor-lifetime-final.log (1/0/0, 2.130s). Lifetime probe now additionally checks failed PackWorkspace releases and capability acquisition cleanup.
- Initial broad run had no DISPLAY, so 15 GUI/Windows gates were unrun. Explicit DISPLAY=:98 rechecks cover file entry, Window, Engine and scoped pixel capture above. Supplemental Button and Field native gates fail on hidden-button activation and synthetic focus-out capture respectively. The exact unchanged GUI scripts fail at the same assertions using the saved OLD element-DLL compiler (button-baseline-gui.log, field-baseline-gui.log), proving these failures are not introduced by pack DLL grouping. Input timing/assertions were not loosened; product UI was not changed. Other nine initial GUI/Windows gates were not re-run here, including existing GTK-related workflows. Actual Windows CMD/GUI and Android device remain external acceptance. Windows all-cold cache cause remains unknown.

Preserved implementation failure: the first GUI candidate validator hit CONTRACT_SELECTION because Check and Build share a Builder but select different subsets. The fix clears/re-prepares contract aliases per operation; new same-Builder regression and real GUI then pass. linux-gui.log and its private first fixture remain. Native Engine's first diagnostic recheck failed on read-only /home/agent entry storage; test-owned storage/scope fixed configuration with unchanged scripted timing and product behavior. All failed logs remain private; no source caches, binaries or images enter Git.

Exact additional commands (same SDK environment):

```sh
dotnet tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll --require-runtime RunnerTests CoreTests IntegrationTests VerificationTests CompilerTransportTests test_project_entry_public_protocol_and_locality
DISPLAY=:98 dotnet tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll --require-runtime EngineTests
DISPLAY=:96 CONFECTORY_TEST_EVIDENCE_ROOT=/workspace/confectory-pack-dll-evidence CONFECTORY_ENTRY_STORAGE=/tmp/confectory-pack-boundary-entry XDG_CACHE_HOME=/tmp/confectory-pack-boundary-cache python3 tests/gui/editor_confirm_x11.py /workspace/confectory-pack-dll-evidence/linux-build.json
python3 tests/web/editor_home_workspace.py /workspace/confectory-pack-dll-evidence/browser-frozen-build.json
python3 tests/web/editor_home_browser.py /workspace/confectory-pack-dll-evidence/browser-frozen-build.json
```

Android packaging used installed JDK21/API36 and the existing local unsigned packaging helper, setting JAVA_HOME/JavaSdkDirectory=/workspace/toolchains/jdk-21, ANDROID_HOME/AndroidSdkDirectory=/workspace/toolchains/android-sdk, CONFECTORY_ANDROID_DOTNET to SDK10.0.401 and then `dotnet targets/android-export/bin/Release/net10.0/Confectory.AndroidExport.dll INPUT NEW_OUTPUT --package`. No new tools/licenses/keys or external publication beyond the authorized source branch push.

## User and next-stage handoff

Pull/build this work branch with the existing .NET10 workflow. Expect one initial pack-layout cache miss without deleting old caches; subsequent unchanged build should report compile-contract=0, compile-pack=0, link=1. Element counts can remain 130 because they describe logical participants; inspect targetInvocations and distinct assembly paths for physical work. Windows users should capture two consecutive same-target latest.json reports and elapsed times so the earlier all-cold cache behavior can be diagnosed independently. Existing locally customized Android settings/keys should be preserved.

Keep BaseUI/Window split as accepted. Do not add a mod loader, private cross-pack coupling, main merge or unrelated UI fixes to this increment. Follow-up UI failures and native platform acceptance above remain separately scoped. Public ABI consumers must rebuild against v2 before any future loader work.

