# Android Entry/Home adapter increment

This increment keeps `Confectory.EditorHome` as the existing ProjectPack. Its Android Main body dispatches to an Activity rather than running the desktop blocking window loop. CreateSession's Android body keeps the exact shared state layout, common Command/Snapshot/CloseSession, ProjectManager, and ProjectShell contracts. No special engine host is added to the minimal core.

NativeUI Request and Capabilities select Android bodies in their existing owning role pack. Request requires the owning Activity delegate and UI main looper. Native fields are retained EditText instances by semantic ID and binding; Activity buttons/text use Android touch and IME. Text snapshots preserve focused/composing text against external replacement. Arbitrary desktop clip-region and folder-path capabilities are explicitly unsupported. Android owns one Activity surface, rather than independent desktop OS windows.

`EditorHomeActivity.cs` and `NativeFieldHost.cs` are application adapter templates. Exporter integration must select these for `Confectory.EditorHome`, copy/reference `Confectory.Core.dll` for metadata-only parsing, and include both template files. The existing engine-android sample template remains a separate two-logical-view SurfaceView sample. An exported Home must not receive that sample's PackCalls assumptions.

## File entry and work protection

The document picker and ACTION_VIEW accept only granted `content:` URIs for .cproj or legacy .cpack files. ContentResolver reads at most 1 MiB with strict UTF-8; Parser reads declarations only. There is no filesystem path guessing, persistent grant, registry traversal, compilation, launch, or original-provider write. A validated manifest is copied into app-owned imports storage under an origin identity hash.

Same document requests retain the selected context and native/source/chat drafts. Another document is refused whenever a project is selected, including a clean project. Picker cancellation retains work. Leave requires save/discard of a dirty imported manifest and uses the common Leave policy. Save validates and writes only the application-owned imported manifest copy. Registry siblings are not imported, and this is not a linked pack source editor. Run, dynamic compilation, source tooling, folder access and project creation are explicitly unavailable in this host. Packaged Android ProjectPacks remain the app execution route.

Activity recreation retains the common session and drafts. Pause writes private UI draft state atomically, allowing process recreation to restore a selected private manifest and its unsaved draft; this does not save the edited manifest or grant access to its original provider. Finishing closes the common session and disposes native fields. Source/drafts persist only in the app's own storage. No signing credential fields, key generation, passwords, or credential storage are involved.

## Increment boundary and locality

Public contracts are unchanged: EditorHome CreateSession/Command/Snapshot/CloseSession/Main, NativeUI Request/Capabilities, ProjectExecution DescribeProject/Capabilities. Android Description delegates to the installed application metadata parser; desktop description still uses its existing tool. The exporter/API adapter uses the public Core Parser API to parse metadata, without new platform logic in Core.

Outside implementation reads: Home model and shell state layout were read because lifecycle adapter compatibility could not be inferred from function signatures alone; native desktop Request was read to preserve semantic field/frame/snapshot behavior. Outside implementation edits: Home platform bodies and ProjectExecution Android metadata provider are necessary consumers of native Activity lifecycle and metadata access, where existing common bodies assumed a desktop repository/process tool. Existing common Home Command and native Windows/Linux implementations are unchanged. Rebuild scope: four Android provider bodies and selected Home bodies, owning target templates, plus affected consumer links; no public contract recompilation caused by body-only locality probes.

## Verification

Managed Home target build passed using the existing CLI. Generated Activity, native field adapter, generated PackCalls/bindings and actual owned managed assemblies compiled against installed .NET 8 / Android API34 references. This checks Android C# API compatibility, not SDK packaging, D8/AOT/linker behavior, APK/AAB production or device execution.

Reproduce API check after source export and Core build:

```
CONFECTORY_DOTNET=/path/to/dotnet python3 tests/android/verify_home_api.py /path/to/repo /path/to/home-export
```

Managed domain test: `test_android_home_activity_dispatch_requires_adapter_and_preserves_public_domain` passed: 1 passed, 0 failed, 136.095s. It checks absent adapter rejection, installed adapter dispatch, common pack context reuse/draft preservation, different-pack refusal, explicit Leave/next-open, and body-only compilation scope. It does not test the Android document provider, actual IME/touch, Activity rotation, process kill, or OS file associations.

Android SDK platforms were not found in this worker's available paths. No tool installation, SDK license acceptance, app signing key creation, package signing, device/emulator launch or store upload was performed. Packaging/exporter integration and actual device lifecycle/content-provider checks remain required.
