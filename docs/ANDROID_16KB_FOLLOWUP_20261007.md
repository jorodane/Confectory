# Android 16KB submission-risk follow-up

Environment reconnected successfully on 2026-10-07; repository shell and artifact reads work. This is non-destructive inspection of the exact final unsigned EditorHome artifacts, not a new build, signing or device test. No checker or assertion was relaxed.

**Current package cannot be declared fully 16KB compliant or Play-ready.** The official [Android page-size guide](https://developer.android.com/guide/practices/page-sizes#check-relro-security-flag) separately checks LOAD alignment, APK ZIP alignment and `(GNU_RELRO.VirtAddr + MemSiz) % 0x4000 == 0`. It warns of runtime faults when RELRO rounding protects data that should remain writable. AAB `PAGE_ALIGNMENT_16K` requests ZIP alignment; it does not change ELF contents. Device testing remains required even after static alignment checks pass.

## Fresh exact-artifact results

AAB SHA256 `20a6b69aa839e1c785dc5ea6b186901b5296d55a664e25de46b1181fe710594d`; APK SHA256 `815d58474f2568d18accf931f83d46c64c2fcbbc2db18497e005eba2258e053b`.

- All20 arm64/x86_64 ELF files: LOAD alignment16384 and address/file-offset congruence pass.
- Official build-tools36 `zipalign -c -P 16 -v 4` on exact APK: Verification successful.
- Installed SDK bundletool dump of exact AAB: PAGE_ALIGNMENT_16K. Earlier independent bundletool validation passed.
- Independent Python ELF-header decode:18 RELRO-end failures,2 passes. GNU readelf independently confirms representative failures. No writable LOAD bytes intersect the rounded-up RELRO tail in these files. This reduces evidence for the specific overlap crash described by the guide; it does not satisfy the published raw-boundary rule or establish runtime safety/Play acceptance.
- Twelve packaged libraries byte-match installed Mono10.0.12 runtime prebuilts; ten of those twelve fail RELRO. The remaining generated/SDK-native libraries also include failures. This is not an EditorHome model/entry C# layout issue.

Representative arm64 `libmonosgen-2.0.so`: RELRO address0x2f3970 + memory0x6690 =0x2fa000, remainder0x2000. It exactly matches `Microsoft.NETCore.App.Runtime.Mono.android-arm64/10.0.12/runtimes/android-arm64/native/libmonosgen-2.0.so`. Generated arm64 `libxamarin-app.so`:0xf1bb0+0x11450=0x103000, remainder0x3000. Both LOAD alignments are0x4000. These are distinct properties, not contradictory reports.

Private reproducible ledger: `/tmp/confectory-relro-followup.json`; independent representative readelf files `/tmp/confectory-relro-followup-*.so.readelf.txt`; exact ZIP/config outputs `/tmp/confectory-relro-followup-{zipalign,bundle-config}.txt`. No binary or raw diagnostic artifact added to Git.

```sh
/workspace/toolchains/android-sdk/build-tools/36.0.0/zipalign -c -P 16 -v 4 /tmp/confectory-actual-editor-api36-apk-entry-final/bin/Release/net10.0-android/org.confectory.checkpoint.apk
/workspace/toolchains/jdk-21/bin/java -jar /workspace/toolchains/dotnet-10.0.401/packs/Microsoft.Android.Sdk.Linux/36.1.2/tools/bundletool.jar dump config --bundle=/tmp/confectory-actual-editor-api36-aab-entry-final/bin/Release/net10.0-android/org.confectory.checkpoint.aab
```

## Blocking boundary and next action

No app-only build property or ZIP realignment can repair the already linked runtime prebuilts. A generally correct fix needs compatible upstream runtime/Android SDK native binaries, or an independently validated native-runtime rebuild with suitable linker settings; changing only app-generated linking is insufficient. No native toolchain/source rebuild or new installation was performed. Binary-header patching, disabling RELRO, changing the inspector, suppression and compression workarounds were not used.

The official static RELRO criterion is currently unmet: retain this as an external native-toolchain compatibility blocker. Actual crash on a particular 16KB Android release and the exact Play Console decision cannot be proven here. No emulator/system image is installed and no device run is authorized/performed. Once an upstream compatible toolchain is selected, rerun all native-library checks on the same product AAB/APK, then authorized 16KB runtime acceptance with `adb shell getconf PAGE_SIZE` returning16384. Play validation is a separate later authorized action. Windows wrapper remains unexecuted on Windows; default project format remains APK.

Increment ledger: intended owner is Android submission evidence, no elementID/public contract change. Reads outside exporter: exact installed Mono runtime files and Android official linker/guidance, needed because app contracts cannot describe native ELF layout. Edits only documentation. Rebuild scope none; functional product results unchanged, compatibility gate remains failed.
