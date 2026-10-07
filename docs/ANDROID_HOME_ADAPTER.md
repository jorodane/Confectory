# Android Entry/Home adapter increment

This increment keeps `Confectory.EditorHome` as the existing ProjectPack. After shared-model integration, CreateSession/Command/Snapshot/CloseSession are owned by `Confectory.EditorHome.Model`; consumer aliases remain stable. Its Android Main body dispatches to an Activity rather than running the desktop blocking window loop. CreateSession's Android body keeps the exact shared state layout, common Command/Snapshot/CloseSession, ProjectManager, and ProjectShell contracts. No special engine host is added to the minimal core.

NativeUI Request and Capabilities select Android bodies in their existing owning role pack. Request requires the owning Activity delegate and UI main looper. Native fields are retained EditText instances by semantic ID and binding; Activity buttons/text use Android touch and IME. Text snapshots preserve focused/composing text against external replacement. Arbitrary desktop clip-region and folder-path capabilities are explicitly unsupported. Android owns one Activity surface, rather than independent desktop OS windows.

`EditorHomeActivity.cs` and `NativeFieldHost.cs` are application adapter templates. The integrated exporter selects these for `Confectory.EditorHome`, copies/references `Confectory.Core.dll` for metadata-only parsing, and includes both template files plus AndroidManifest.xml. The existing engine-android sample template remains a separate two-logical-view SurfaceView sample. An exported Home must not receive that sample's PackCalls assumptions.

## File entry and work protection

The document picker and ACTION_VIEW accept only granted `content:` URIs for .cproj or legacy .cpack files. ContentResolver reads at most 1 MiB with strict UTF-8; Parser reads declarations only. There is no filesystem path guessing, persistent grant, registry traversal, compilation, launch, or original-provider write. A validated manifest is copied into app-owned imports storage under an origin identity hash.

Same document requests retain the selected context and native/source/chat drafts. Another document is refused whenever a project is selected, including a clean project. Picker cancellation retains work. Leave requires save/discard of a dirty imported manifest and uses the common Leave policy. Save validates and writes only the application-owned imported manifest copy. Registry siblings are not imported, and this is not a linked pack source editor. Run, dynamic compilation, source tooling, folder access and project creation are explicitly unavailable in this host. Packaged Android ProjectPacks remain the app execution route.

Activity recreation retains the common session and drafts. Pause writes private UI draft state atomically, allowing process recreation to restore a selected private manifest and its unsaved draft; this does not save the edited manifest or grant access to its original provider. Finishing closes the common session and disposes native fields. Source/drafts persist only in the app's own storage. No signing credential fields, key generation, passwords, or credential storage are involved.

## Increment boundary and locality

This Android provider increment kept public signatures unchanged: Home domain CreateSession/Command/Snapshot/CloseSession/Main, NativeUI Request/Capabilities, ProjectExecution DescribeProject/Capabilities. The subsequent shared-model extraction explicitly moves the domain IDs into Confectory.EditorHome.Model; consumer aliases are retained. Android Description delegates to the installed application metadata parser; desktop description still uses its existing tool. The exporter/API adapter uses the public Core Parser API to parse metadata, without new platform logic in Core.

Outside implementation reads: Home model and shell state layout were read because lifecycle adapter compatibility could not be inferred from function signatures alone; native desktop Request was read to preserve semantic field/frame/snapshot behavior. Outside implementation edits: Home platform bodies and ProjectExecution Android metadata provider are necessary consumers of native Activity lifecycle and metadata access, where existing common bodies assumed a desktop repository/process tool. Existing common Home Command and native Windows/Linux implementations are unchanged. Rebuild scope: four Android provider bodies and selected Home bodies, owning target templates, plus affected consumer links; no public contract recompilation caused by body-only locality probes.

## Verification

Managed Home target build passed using the existing CLI. Generated Activity, native field adapter, generated PackCalls/bindings and actual owned managed assemblies compiled against installed .NET 8 / Android API34 references. This checks Android C# API compatibility, not SDK packaging, D8/AOT/linker behavior, APK/AAB production or device execution.

Reproduce API check after source export and Core build:

```
CONFECTORY_DOTNET=/path/to/dotnet python3 tests/android/verify_home_api.py /path/to/repo /path/to/home-export
```

Managed domain test: `test_android_home_activity_dispatch_requires_adapter_and_preserves_public_domain` passed: 1 passed, 0 failed, 136.095s. It checks absent adapter rejection, installed adapter dispatch, common pack context reuse/draft preservation, different-pack refusal, explicit Leave/next-open, and body-only compilation scope. It does not test the Android document provider, actual IME/touch, Activity rotation, process kill, or OS file associations.

During the initial API-only verification Android SDK platforms were unavailable and no installation or license acceptance had yet been authorized. Subsequent approved installation and actual unsigned packaging are recorded below. Device lifecycle/content-provider checks, signing and store delivery remain unrun.

## Unsigned package target inspection

The installed Android workload 34.0.43 appends `_CopyPackage`, `_Sign`, and `_CreateUniversalApkFromBundle` to ordinary `BuildDependsOn` outside IDEs. `AndroidBuildApplicationPackage=false` does not remove that signing path in this SDK. `_ResolveAndroidSigningKey` depends on `_CreateAndroidDebugSigningKey`, whose condition is a missing debug keystore and `AndroidKeyStore != True`; ordinary Build can therefore create a key even when no user release credentials were supplied.

The installed public `Package` target depends on `Build;_CopyPackage`. The unsigned route is `-t:Package -p:BuildingInsideVisualStudio=true -p:AndroidKeyStore=true`, with `AndroidPackageFormats=apk` or `aab`. The IDE property removes signing from Build; Package still creates/copies the chosen unsigned package. `AndroidKeyStore=true` independently prevents automatic debug-key generation. No signing target, installation target, keystore path, or password should be supplied for this route. Because this relies on inspected workload target composition, the exporter should additionally guard signing/debug-key targets and revalidate after SDK updates.

Read-only MSBuild property evaluation confirmed ordinary Build includes `_Sign`; the guarded properties remove `_Sign`, preserve `AndroidKeyStore=true`, and select `AndroidPackageFormat=aab` for `AndroidPackageFormats=aab`. This was property evaluation only, not a successful package build. At that initial inspection SDK platforms and a complete JDK were absent; installation was subsequently authorized and completed as recorded below. No key generation occurred.

Exporter selection regression: `test_android_home_export_selects_activity_and_metadata_parser_without_engine_surface_sample` checks actual exported Activity, native field template, Parser DLL reference, Android Main selection and truthful source-only report. It must be run after exporter wiring is integrated. AndroidPreparationTests also copies the new export-settings role when isolating the engine sample.


## Final approved tools and actual unsigned packages

After explicit SDK/JDK installation and Google SDK terms approval, tools were installed only under `/workspace/toolchains`. Command-line tools were downloaded from the [official Android page](https://developer.android.com/studio); published SHA256 `4e4c464f145a7512b57d088ac6c278c03c9eea610886b35a5e0804e74eedf583` matched. Because sdkmanager remote manifest access failed, exact official `repository2-3.xml` ZIP URLs/checksums were used; sdkmanager then recognized the local official metadata without parsing errors. Selected packages are base `platforms;android-34` revision 3 / extension 7 (`IsBaseSdk=true`), `build-tools;34.0.0`, and `platform-tools` 37.0.1. All three official package records reference `android-sdk-license`; only that approved acceptance remains. No preview package or unused preview agreement is retained.

JDK vendor CDN downloads returned HTTP403. Official Ubuntu jammy-updates OpenJDK 17.0.20.1+1 JDK-headless and JRE-headless packages were downloaded with their package-index SHA256 checksums, extracted locally without system apt installation, and their packaged configuration made self-contained. `java -version` and `javac -version` both work from `/workspace/toolchains/jdk-17`.

Both final outputs were produced by the real integrated `AndroidExport <private Home ProjectPack> <new-output-directory> --package` pipeline, after shared-model extraction and exporter manifest fixes. APK uses the pack's default `apk`; AAB uses a private copied pack whose AndroidExport object declares `packageFormat="aab"`. Repository project settings were not mutated, and generated projects were not manually patched to claim exporter coverage.

| Artifact | SDK result | Size | SHA256 |
| --- | --- | --- | --- |
| `/tmp/confectory-home-android-apk-final/bin/Release/net8.0-android/org.confectory.checkpoint.apk` | 0 warnings/errors, 22.27s | 35,658,937 bytes | `58d9de0d8ec91007be1a07a72179ba7c87ef286aa23d1165e6170e5c507d55c3` |
| `/tmp/confectory-home-android-aab-final/bin/Release/net8.0-android/org.confectory.checkpoint.aab` | 0 warnings/errors, 26.82s | 29,369,363 bytes | `13235176c5094f8e96f636d69294f34f7f74f80f5c6f601e6353a4189549c73a` |

Both artifacts contain classes.dex and AndroidManifest.xml; APK badging confirms application ID `org.confectory.checkpoint`, version code 1/name 0.1.0, app label Confectory, minimum API23 and compile API34. Final projects evaluate PublishTrimmed=false and JsonSerializerIsReflectionEnabledByDefault=true; generated packed runtime configuration also stores the reflection flag as `true`. This preserves dynamic JSON/model metadata rather than relying on trimming inference.

APK apksigner verify rejects the unsigned artifact; AAB jarsigner reports `jar is unsigned`. Neither archive contains JAR certificate/signature entries. Standard debug-keystore paths and task toolchain deployment-keystore files remain absent before and after packaging. AAB bundletool validate succeeds. No keystore generation, signing, emulator/device installation, device execution, or external upload occurred. Unsigned APK cannot be installed as a normal app until a separately authorized signing step; AAB is a bundle rather than a directly installable APK.

The initial actual SDK package attempt exposed missing AndroidManifest.xml (XA1018); exporter ownership now includes that manifest, and the source-export selection regression asserts its presence. Source export and APK/AAB production have separate reports. Managed source export alone remains insufficient evidence of package production. Source/export selection and settings isolation gates passed; settings gate includes actual MSBuild property evaluation proving a `$([System.Math]::Abs(-2))` title remains literal, XML characters round-trip, and invalid IDs/formats or saved credential fields are rejected before a poisoned body is compiled (1 passed/0 failed, 325.793s).

For reproduction set `CONFECTORY_DOTNET`, `DOTNET_CLI_HOME`, `JAVA_HOME`, `ANDROID_HOME`, `ANDROID_SDK_ROOT`, `AndroidSdkDirectory`, `JavaSdkDirectory` to the installed local tools and use the real exporter `--package` option with a new output directory. Build logs are `/tmp/confectory-home-android-apk-final.log` and `/tmp/confectory-home-android-aab-final.log`; truthful package-report.json resides in each export directory. Private generated binaries, SDKs, logs and signing material are not tracked in Git.


## Workload coexistence follow-up

After the separate web worker installed wasm-tools 8.0.31, read-only workload listing confirms wasm-tools 8.0.31/8.0.100 and Android 34.0.43/8.0.100 coexist. Both existing final projects were rebuilt through public `Package` with the same unsigned flags and generated signing guard: APK 0 warnings/errors, 19.63s; AAB 0 warnings/errors, 24.53s. Restore was up-to-date; no shared Mono/Android runtime pack was missing.

The rebuild regenerated APK archive bytes: its current SHA256 is `3a638c61324653a508e6137032e6bad0260430cc304f0988a2a995ce6b961336`; the table above records the original end-to-end exporter artifact hash. AAB SHA256 remains `13235176c5094f8e96f636d69294f34f7f74f80f5c6f601e6353a4189549c73a`. Both remain unsigned with no JAR certificate entries; APK apksigner verification again reports missing signature manifest. No debug-keystore or deployment key appeared.

The latest root source-export regression, including actual generated AndroidManifest.xml and PublishTrimmed=false / JsonSerializerIsReflectionEnabledByDefault=true assertions, passed: 1 passed, 0 failed, 167.090s. It used freshly built root tests and the extracted shared-model consumer fixture rather than the old worker model fixture. Logs: `/tmp/confectory-android-final-export-assertions.log`, `/tmp/confectory-android-apk-after-wasm.log`, `/tmp/confectory-android-aab-after-wasm.log`. Device execution/signing/upload remain unrun.
