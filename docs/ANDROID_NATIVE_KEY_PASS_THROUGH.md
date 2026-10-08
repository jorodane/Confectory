# Android native field key pass-through

The installed Mono.Android 36.1.2 binding initializes View.KeyPress event arguments with Handled=true. NativeFieldHost previously returned for unregistered/editing keys without clearing that value, consuming the event before EditText's default handling. The handler now starts with Handled=false and sets it true only after queuing a registered, non-composing Enter/Tab/Escape command.

## Scope and locality

Intended provider: Android export NativeFieldHost, reached through Confectory.NativeUI::Request and Confectory.BaseUI.NativeInput Field/Poll. Public element IDs, request/event payloads and contracts are unchanged. Outside implementation reads: GenericActivity and export generation establish the actual editor-home adapter path; BaseUI NativeInput Field/Poll establish snapshot ownership; installed Mono.Android binding IL establishes the event default that the old doubles missed. These facts are internal event semantics, not exposed by the public contract. No shared implementation edits were required. Rebuild scope: Android exporter/template and regenerated Android applications; Core, common editor-home entry and desktop packs are unchanged.

## Functional verification

The doubles now match the binding's Handled=true initial value. Against the old exported editor-home adapter, the new regression fails at Del/Down/0. Against the corrected template and newly exported editor-home adapter it checks DEL, forward delete, left/right, ordinary A/Space, Enter/Tab/Escape, Down/Up and repeats 0/1/7. Unregistered and composing events pass through without application queue entries; registered non-composing commands consume and preserve their six-value event payload. Existing snapshot, retained-field, focus, external-update deferral, readonly and contrast checks remain.

Commands (run from repository root; SDK=/workspace/toolchains/dotnet-10.0.401/dotnet, DOTNET_CLI_HOME=/tmp/confectory-dotnet10):

```
$SDK build Confectory.sln -c Release --no-restore
$SDK run --project tests/android/native_field_harness/NativeFieldHarness.csproj -c Release
$SDK run --project tests/Confectory.Tests -c Release --no-build -- --require-runtime AndroidPreparationTests android_home_export native_public_projection_target_selection_and_provider_locality
bash /tmp/confectory-current-android-package.sh /workspace/Confectory/examples/editor-home/project.cpack /workspace/confectory-android-key-fix-evidence/editor-home-aab
$SDK run --project tests/android/native_field_harness/NativeFieldHarness.csproj -c Release -p:NativeFieldSource=/workspace/confectory-android-key-fix-evidence/editor-home-aab/NativeFieldHost.cs
```

The package helper uses the existing .NET Android workload, JDK21 and Android SDK, and invokes AndroidExport with --package. The current editor-home AndroidExport element selects AAB and minimum SDK24. Packaging is unsigned; no signing keys or device installation are involved. Logs and binaries remain outside Git under /workspace/confectory-android-key-fix-evidence.

## Device acceptance still required

These are adapter dispatch/protocol checks, not an Android keyboard session. A soft keyboard can instead use InputConnection deletion/selection APIs; the user's actual keyboard transport has not been established. No emulator/system image is installed and no attached-device session was available. Do not claim actual text deletion or spacebar slide is fixed based only on these checks.

On the newly built application, check short and held delete at `under th|e sea` and `unde|r the sea`; forward delete if available; spacebar hold-slide left/right; touch caret, mid-text insertion, Select All/Cut; Korean composition; registered command keys. Verify no later replay of deleted text and no swallowed composing commands. Record application version, Android version and keyboard/version with the result. Continue development independently of this asynchronous acceptance check.

## Recorded result (2026-10-08)

Solution build: zero warnings/errors. Corrected-template and actual exported-adapter harnesses pass. Current editor-home unsigned AAB build passes (62.44s, zero warnings/errors). An initial broad NativeUITests selection reported 3 passed, 0 failed, 2 skipped and strict exit 1 because there is no actual DISPLAY for unrelated GTK GUI tests; the narrowed Android/provider selection passes with 3 passed, 0 failed, 0 skipped (63.995s, strict exit 0). The optional --inspect-package check exits 1: it reports ELF16KiBAligned=false for most packaged native libraries, zipAlignmentVerified=false, device16KiBTested=false and playAcceptanceVerified=false. This build is not a 16KiB/Play acceptance certification; that packaging/toolchain finding is outside this minimal input-handler change. No new tools were installed.
