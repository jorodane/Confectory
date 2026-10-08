# Android minimum SDK export increment

The actual editor-home AAB previously inherited API23 from two exporter templates, even when targeting API36. Minimum API and target API describe different values. This increment adds `Confectory.AndroidExport.Settings::Defaults.androidMinSdkVersion` (integer, default23); the actual `Confectory.EditorHome::AndroidExport` object overrides it to24. Existing consumers and older settings objects without the field retain23. Minimum must be23 or higher and no greater than the selected target (currently supported up to36). Invalid values are rejected before managed pack compilation.

The target-owned exporter reads the public effective settings object. It writes its selected minimum to both generated `Confectory.Android.csproj/SupportedOSPlatformVersion` and `AndroidManifest.xml/uses-sdk/@android:minSdkVersion`. Target SDK stays separate. Unsigned package reports include `minSdkVersion` alongside `targetSdkVersion`. Templates retain compatible defaults; generated outputs receive validated settings, not manual post-export patches. No Android-specific grammar or policy is added to Core.

Pack/element scope: AndroidExport.Settings::Defaults, editor-home::AndroidExport and generic Android export settings reader/generator/package report. Outside reads: Core Registry effective-values shape, current generated-project/manifest templates, unsigned-package/signing guards and existing EntryHome settings regression. These establish the already-existing metadata extension and actual export path; no Core/provider implementation is edited. Rebuild scope is exporter/tests plus Android export-settings metadata in consumers. Product Main, runtime/input/render providers and public function signatures remain unchanged. Structure/locality gate is separate from actual package behavior.

Regression extends the existing actual editor-home settings/export test: omitted minimum inherits23 for APK source export, explicit24 for AAB source export, matching generated project/manifest, target36 unchanged, invalid22/37/minimum-above-target/text values rejected before a poisoned product body can compile. Existing application-ID/format/XML literal/credential rejection checks remain. This regression is source export; the separate actual product AAB package/manifest proof below verifies native packaging.

Actual product AAB gate uses `/tmp/confectory-editor-home-minsdk24-aab-input`, a copy of the repository's real `examples/editor-home` owned files. Registry paths are rebased; only AndroidExport app ID and package format are overridden to `com.Confectory.Engine` and `aab`, preserving min24. All other owned source bytes match; identity hashes live in `/tmp/confectory-editor-home-minsdk24-source-identity.json`. It retains real `Confectory.EditorHome::Main`, not a smaller substitute entry. The exporter writes a new `/tmp/confectory-editor-home-minsdk24-aab` with `--package`, using installed .NET10.0.401/Android36.1.2, API36 SDK and JDK21. Signing/debug-key targets remain guarded; no keys or credentials are used.

Commands (outputs and logs remain private, outside Git):

```sh
DOTNET_CLI_HOME=/tmp/confectory-dotnet10 /workspace/toolchains/dotnet-10.0.401/dotnet build tests/Confectory.Tests/Confectory.Tests.csproj -c Release --nologo
DOTNET_CLI_HOME=/tmp/confectory-dotnet10 CONFECTORY_DOTNET=/workspace/toolchains/dotnet-10.0.401/dotnet /workspace/toolchains/dotnet-10.0.401/dotnet tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll --require-runtime test_android_export_owned_settings_formats_xml_and_rejects_credentials_before_build
bash /tmp/confectory-current-android-package.sh /tmp/confectory-editor-home-minsdk24-aab-input/project.cpack /tmp/confectory-editor-home-minsdk24-aab
```

The packaging helper sets `CONFECTORY_DOTNET` and `CONFECTORY_ANDROID_DOTNET` to `/workspace/toolchains/dotnet-10.0.401/dotnet`, `DOTNET_CLI_HOME=/tmp/confectory-dotnet10`, `JAVA_HOME`/`JavaSdkDirectory=/workspace/toolchains/jdk-21`, `ANDROID_HOME`/`AndroidSdkDirectory=/workspace/toolchains/android-sdk`, and prepends that SDK/JDK bin to PATH; it then invokes `targets/android-export/bin/Release/net10.0/Confectory.AndroidExport.dll INPUT OUTPUT --package`.

User update: preserve local `com.Confectory.Engine`, AAB format and existing key alias when pulling. Commit/stash local `AndroidExport.celem` changes before `git pull --ff-only`; after reapplying, resolve this file by retaining those values and exactly one `value androidMinSdkVersion = 24;` inside the settings object. Generate a fresh AAB and sign it locally using the existing upload key; the old AAB stays API23 after re-signing. See ANDROID_WINDOWS_EXPORT.md for the ordinary wrapper. This addresses the reported minimum-SDK metadata requirement only: Play acceptance, device execution, signing and remaining16KiB runtime/alignment gates are not certified by this test. No main merge, Play upload, device install or key generation is performed.


## Completed gates

- Relevant exporter/tests project build: zero warnings/errors, final build5.99s.
- Final current regression (omitted minimum default23, explicit24, generated-file consistency and pre-build rejection): **1 passed,0 failed,0 skipped,197.901s**. `/tmp/confectory-minsdk-final-regression.log`. Earlier explicit23/24 iteration also passed1/0/0 in197.088s; it is not substituted for the final omitted-default check.
- Actual editor-home unsigned AAB native Package build: **zero warnings/errors,61.21s**, exporter exit0. `/tmp/confectory-editor-home-minsdk24-aab.log`. Source compilation selected122 contracts/122 implementations and one link, zero full rebuilds. This fresh copied consumer has no warm output cache; these counts do not claim a narrow incremental compile. Product/provider bodies are unchanged.
- Official installed bundletool inspected `bin/Release/net10.0-android/com.Confectory.Engine.aab`: package `com.Confectory.Engine`, minimum24, target36. Generated project, source manifest, packaged manifest and package-report.json agree. Product entry is `Confectory.EditorHome::Main`. Artifact42,320,551 bytes, SHA256 `80a0295f80d07edf9b436e651a41285f659b42a36f7ce35fbead449e4f3d1cca`; no JAR certificate block. Private verification `/tmp/confectory-editor-home-minsdk24-verification.json`; packaged manifest `/tmp/confectory-editor-home-minsdk24-aab-manifest.xml`.

Exact archive inspection:

```sh
/workspace/toolchains/jdk-21/bin/java -jar /workspace/toolchains/dotnet-10.0.401/packs/Microsoft.Android.Sdk.Linux/36.1.2/tools/bundletool.jar dump manifest --bundle=/tmp/confectory-editor-home-minsdk24-aab/bin/Release/net10.0-android/com.Confectory.Engine.aab --module=base
```

No new prerequisites were installed. Windows local export/signing and Android device/Play submission were not run here; the user reported successful local AAB signature verification independently. New AAB still needs the user's existing local signing workflow. This change verifies minimum-SDK metadata only and does not claim to resolve the previously recorded16KiB RELRO/toolchain issue.
