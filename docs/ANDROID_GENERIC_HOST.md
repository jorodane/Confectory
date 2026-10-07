# Generic Android product host increment

Intended pack/contracts: Confectory.Window existing CreateSurfaces/SurfaceDimensions/Close/Reopen/Place and RenderInput Pump/Draw/MeasureText/DrawText; Confectory.NativeUI existing Request; Confectory.ProjectEntry existing Request. Public function IDs/signatures are retained. HostLoop common controller publishes object[]{Func<bool> step, Action dispose}; Activity schedules that controller on Android Choreographer. Exporter supplies separate generated PackEntry.Run invoking the actual ProjectPack entry; GenericActivity contains no product namespace, model aliases, action/menu/control definitions.

Android declares one OS Activity surface. One requested surface works; multiple desktop windows and manual Reopen fail explicitly. Android owns positioning. Activity main looper owns Canvas/native fields/events. Target bodies resolve delegates installed by that owner. Existing SurfaceBridge sample fallback remains for already generated sample integrations; it is not evidence of the actual product port.

SAF tree/file import copies granted readable bytes into private storage, bounded at 1024 entries, depth16, 64MiB, rejects unsafe names, stages before publication. Repeat URI reuses existing copy, preserving edits. Saves affect the app-owned copy only; no provider write/persistent permission is requested. SingleTask incoming intent while picker pending is refused without queue/replay. Generic ProjectEntry inbox sends paths to the same common controller policy. Android ACTION_VIEW has no synchronous caller reply channel. Device permission/cancellation/task/configuration/IME behavior remains unrun.

Actual outside implementation reads: common editor Main/Render/Action read to match Window, NativeInput and ProjectEntry signatures; they expose platform contracts but synchronous desktop loop prevented Android looper scheduling (shared runtime worker owns the explicit HostLoop extension). Exporter Program read to identify hardcoded namespace template selection (root owns universal template/entry bridge integration). NativeFieldHost edited because native clip provider was missing yet actual common Render calls Clip; EditText draw/touch now respects common visible region requests. Core Parser is consumed through public ParseManifest only; no core grammar or model edits.

Rebuild scope: affected target implementation bodies and consuming product binding closures; Android host template + native field/import adapter and Android package. No product layout/actions/views changed by this increment. Structural gate: SDK10/API36 compile of all generic host sources passes zero warnings/errors in /tmp/confectory-generic-android-compile.log; its explicit throwing Entry stub is compile-only, never executed or packaged and is not actual product evidence. Actual ProjectPack export/package gates follow root universal entry integration. Functional device and lifecycle/IME/grant checks remain separate and unrun.

Provider audit follow-up: minimal non-UI entries display an explicit no-presentation-loop diagnostic, not a fabricated product screen. Picker request codes carry a per-owner generation so stale cancellation/results cannot complete a later picker. Parent native host handles are validated before folder operations. Failed startup and OnDestroy clear global adapters in finally only for the matching Activity owner. Common HostLoop private registry is not removed by Activity: Stop/Dispose policy and pending job closure remain provider-owned. Single-pointer touch cancels on additional pointers, retaining no unintended activation on release; touch pointer IDs are not misreported as keyboard modifier flags. Placement/multiwindow/reopen capabilities are explicit. Rectangle/text request shapes and native measurement budgets are validated. Canvas metrics/rendering use the existing nominal12 text scale contract. SDK host source compile passes zero warnings/errors; real same-product package verification and device checks are separate.

## Universal exporter integration (2026-10-07)

The exporter now generates `PackEntry.Run` from the planner's actual entry binding for both valid `() -> int` and `() -> void` contracts. It copies the same generic target-owned Activity, native-field adapter and granted-document importer for every ProjectPack. There is no product namespace selector, import-alias facade or mandatory physical Window-pack file lookup. Core is referenced solely for public manifest parsing used by the generic metadata provider; Core resolution/build policy is unchanged.

Outside reads: exporter planner/binding and `Generation.MainSource` entry normalization establish the existing public entry contract; generic Activity was inspected to verify it calls the generated entry and contains no sample/model aliases. No product controller/model implementation was edited. Rebuild scope: exporter and each newly generated Android project; pack contracts and managed binding closure are unchanged.

Functional source gate: SDK10 exporter and test project builds have zero warnings/errors. `/tmp/confectory-api36-minimal-input/project.cpack`, a valid one-implementation ProjectPack with no Window/NativeUI/model registry, exported successfully to `/tmp/confectory-universal-minimal-20261007` (1 implementation/1 contract). Its generated entry invokes the real binding. This is source-export proof, not Android execution. Actual product source-export regression and API36 native archive gates are recorded separately once complete. Generic bootstrap uses Android app-private process working directory instead of product-specific environment keys.

Root integration replay: `CONFECTORY_DOTNET=/workspace/toolchains/dotnet-10.0.401/dotnet DOTNET_CLI_HOME=/tmp/confectory-dotnet10 /workspace/toolchains/dotnet-10.0.401/dotnet tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll test_android_home_export_selects` passes1/0/0SKIP in237.979s. It checks actual common controller selection and generated entry source, target-owned import/native adapters, unsigned source-only reporting and metadata references. An earlier concurrent source-change run failed (old import plan/new Close body); the stable-source replay passed. Neither run constitutes device execution.
## Actual same-product API36 package gates

Source snapshot: root owner/dispatch integration3a0c002 and official zipalign pipeline6596120, after HostLoop startup/release audit fixes. Both product exports completed before the later browser registry/target integration; common product body bytes were frozen throughout source generation. APK used actual `examples/editor-home/project.cpack`. AAB used a consumer-local exact copy of the same element/body files with registry paths rebased and only its owned `packageFormat` set to aab; `/tmp/confectory-same-editor-source-identity.json` records SHA256 identity. This is the actual common Main/Render/Action entry, not an Android Home UI/model replacement. Both source reports select `Confectory.EditorHome::MainBody` common and generated `PackEntry.Run` invokes its actual ID binding.

A separate arbitrary `Example.MinimalAndroid` ProjectPack int entry, registered only with Build.DotNet and Android export settings, also exported and built both formats. It has no Window/NativeUI/model registry or sample aliases. Generic host contains an explicit no-presentation-loop diagnostic for non-UI entries; package compilation alone is not proof of Android entry execution. Durable tests cover renamed no-Window int and void entries and actual Android-selected Request owner failure/retry/proven-close/unknown-owner rejection: root result2 passed,0 failed,0 skipped,8.700s. Root actual Home source gate passed1/0/0 skipped,237.979s under concurrent compilation.

Exact package command environment (no keys or signing):

```sh
export DOTNET_CLI_HOME=/tmp/confectory-dotnet10
export CONFECTORY_DOTNET=/workspace/toolchains/dotnet-10.0.401/dotnet
export CONFECTORY_ANDROID_DOTNET=$CONFECTORY_DOTNET
export JAVA_HOME=/workspace/toolchains/jdk-21
export ANDROID_HOME=/workspace/toolchains/android-sdk
export AndroidSdkDirectory=$ANDROID_HOME
export JavaSdkDirectory=$JAVA_HOME
$CONFECTORY_DOTNET targets/android-export/bin/Release/net10.0/Confectory.AndroidExport.dll examples/editor-home/project.cpack /tmp/confectory-actual-editor-api36-apk-final --package
```

Full exact script and inputs for the AAB/minimal variants are preserved locally at `/tmp/confectory-current-android-package.sh`, `/tmp/confectory-same-editor-home-aab-input`, `/tmp/confectory-api36-minimal-input` and `/tmp/confectory-api36-minimal-aab-input`. No fixture or generated binary is committed. SDK10.0.401/Android workload36.1.2, API36 rev2/build-tools36.0.0, full JDK21.0.12.1 were used. Previous SDK8/JDK17 tools remain present.

Four final SDK Package builds passed zero warnings/errors: actual product APK64.60s/AAB69.29s; minimal APK83.35s/AAB86.00s. Root pipeline invokes official zipalign on unsigned APK before reporting success; independent `zipalign -c -P16 -v4` passes both final APKs. Actual archive manifests show compileSDK36 and targetSDK36/minSDK23. Both AABs declare PAGE_ALIGNMENT_16K in bundletool dump config and bundletool validate succeeds. All archives contain classes.dex and their manifest; apksigner expected unsigned rejection, jarsigner unsigned, no certificate entries or debug-keystore paths.

| Final source | Format | Bytes | SHA256 |
| --- | --- | ---: | --- |
| actual-editor | apk | 42,313,569 | `1f64dbc366669db76c345498fd5da2720585b62835e9b59d652ec4ee9108edb2` |
| actual-editor | aab | 42,249,140 | `21b8f04e18013d92284b7110c1b7ec96dffda9d5cea22b7e0b8badc9d7baef91` |
| minimal | apk | 41,781,161 | `75fc7d6362584fba692144d520341b9ec75c894769cbdca9432fd785dd0050ab` |
| minimal | aab | 41,721,687 | `ccfd068aeff7bd3be2c23346fb1e9a67e8436ccf0e2f5cc262c9df5da13effe5` |

Final artifacts are `/tmp/confectory-{actual-editor,minimal}-api36-{apk,aab}-final/bin/Release/net10.0-android/org.confectory.checkpoint.{apk,aab}`. Exact logs share the output basename plus `.log`; actual SDK archive/manifest/ZIP/bundle/signature evidence uses `-verified-*`. `/tmp/confectory-current-android-final-verification.json` records every native library, artifact hash and archive gate.

Pre-fix versions remain distinct evidence, not final artifacts. Their APKs compiled but resources.arsc was offset1037, failing ZIP alignment; unsigned public Package did not automatically run signing-associated alignment. This prompted root pipeline6596120. Pre-fix hashes:

- actual-editor apk: `7006ed0dc7e0ff9ea548fc6f1780ef100b7c1feb760a48dea4ed3766a6b99da0` (zipalign-failed-pre-fix).
- actual-editor aab: `fc7a9eae90ad7e4cc1cbf26e3149768053816178dc7376132614cac322939e9c` (bundle-config-PAGE_ALIGNMENT_16K).
- minimal apk: `14ea985a1c4154f030cd00ca721f88784bfcf0c7b94a4045dd4552198cf9e535` (zipalign-failed-pre-fix).
- minimal aab: `b82b24c23f9cfae0896b9d6f07733f9bdf2799972ed63c1b6fae43cd94f15e78` (bundle-config-PAGE_ALIGNMENT_16K).

Native compatibility bounds: all20 ELF64 arm64/x86_64 libraries in every final archive have PT_LOAD alignment16384 and offset/address congruence. Strict raw GNU_RELRO-end alignment still reports18 warnings (2 strict passes); rounded-up16KiB tails do not overlap any writable PT_LOAD memory. Strict public inspection stays false and has not been relaxed to a blanket pass. Bundle alignment configuration and APK ZIP alignment are different from on-device16KiB execution and Play acceptance. No signing keys, signed artifacts, device/emulator installation/execution, or Play/upload acceptance test was performed. Native IME/composition/clip/touch/density, Activity task/picker/configuration and injected native Java detach failures remain device checks.

Owner policy: failed native release delegates remain bound to their original owner until verified native detach+dispose succeeds, independently of replacement Activity globals. Already-successful close is idempotent only for the latest4096 lightweight process-owned success records; unknown/expired owner close fails explicitly. Closed records retain no Activity. Surface IDs are unique; closed surface sentinel requires the corresponding success record. Worker-thread cleanup marshals to the main looper with a20s timeout, while the main looper never waits on itself. Pending failures retain callable handles and are not reported fully closed. Functional Java release behavior is unrun; managed dispatch and SDK compilation are separate gates.

## Entry listener owner-routing follow-up

ProjectEntry listener tokens now route through their original Activity-bound provider rather than the current global Activity delegate. Failed close retains the listener handle and callback; proven successful close adds the same bounded lightweight closed record used by native/window resources. Unknown/expired listener close is an error. Retire attempts each listener close and retains failures instead of clearing all handles. Worker-thread cleanup marshals to the main looper; no main-looper self-wait. No implicit ACTION_VIEW intent filter or OS file association is installed: only explicitly delivered user-granted content intents and the SAF picker are supported.

Other owned global delegates were inspected: Window requests route by unique surface owner; NativeUI by host owner; HostLoop.Close uses explicit private token policy and its delegate captures no Activity; DescribeProject is a static parser adapter with no owner release resource; HostLoop.Schedule owns job tokens directly. Global creation/bootstrap delegates may select the current Activity, but release does not cross into a replacement Activity. Device callback/failure behavior remains unrun and is separate from managed routing regression and SDK compile/package gates.

### Final rebuild after ProjectEntry owner routing

The latest product snapshot includes the browser registry/target additions and root56d7b37 listener owner fix; selected Android/common product source was frozen during these exports. After the original unchanged-condition Linux GUI replays settled, four fresh `-entry-final` outputs were built through the same actual exporter `--package` pipeline. No prior artifact was overwritten. APK used current actual `examples/editor-home/project.cpack`; AAB used `/tmp/confectory-current-editor-aab-entry-input`, an exact current source copy with registry paths rebased and only its owned package format changed. SHA identity is recorded in `/tmp/confectory-current-editor-source-entry-identity.json`.

SDK builds: actual product APK70.29s/AAB80.12s; minimal no-Window APK91.44s/AAB101.26s, each0 warnings/errors. Independent actual manifest target/compile36, APK official ZIP alignment, AAB PAGE_ALIGNMENT_16K configuration+bundle validation, unsigned signatures/no certificate entries and no debug-keystore checks all pass. All20 ELF64 LOAD entries align/congrue16KiB; strict18 raw RELRO warnings remain, with no rounded-tail writable LOAD overlap. Prior `-final` builds above remain valid baseline proof before the listener-routing change.

| Latest source | Format | Bytes | SHA256 |
| --- | --- | ---: | --- |
| actual-editor | apk | 42,314,637 | `815d58474f2568d18accf931f83d46c64c2fcbbc2db18497e005eba2258e053b` |
| actual-editor | aab | 42,249,789 | `20a6b69aa839e1c785dc5ea6b186901b5296d55a664e25de46b1181fe710594d` |
| minimal | apk | 41,781,608 | `273ca3069e5c5a9978171ebe48897bb1291462f4f32c1ca73b80fdf0911c44e9` |
| minimal | aab | 41,722,505 | `ae2f962bf111488e31f620e58273ecd21c855297146ff2742aaec238a1d882c3` |

Latest outputs: `/tmp/confectory-{actual-editor,minimal}-api36-{apk,aab}-entry-final`; detailed verification `/tmp/confectory-current-android-entry-final-verification.json` and summary with `-summary.json`, raw archive evidence `-entry-final-verified-*`. The exact commands still use `/tmp/confectory-current-android-package.sh`. Root durable actual Android ProjectEntry dispatch failure/retry/unknown-close regression passed1/0/0 skipped in3.601s; native-owner+lifetime protocol gates passed2/0/0 skipped in6.432s. Managed protocol tests do not execute Android Java/native controls.

No further source changes were made during verification. No OS file association, native task/IME/configuration/grant failure execution, signing/key creation, device/emulator installation, upload or Play readiness is claimed. No worker push was performed.
