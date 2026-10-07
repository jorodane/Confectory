# Repeatable local Windows APK/AAB export

Entry point: double-click `export-android-windows.bat`, select an engine ProjectPack, and follow the local prompts. There is currently no Android export menu in Home. The script builds the trusted exporter, creates a new timestamped output under `%LOCALAPPDATA%\Confectory\exports`, and packages the format in the selected project's AndroidExport object. It does not install development tools, create keys, install the app, or contact Play. The wrapper permits its own PowerShell script for that process only; it does not persist an execution-policy change.

For current Home use `examples\editor-home\project.cpack`. For the packaged two-logical-View Surface sample use `examples\engine-android\project.cpack`. Home supports app-owned imported manifest metadata/editing/drafts/Leave; arbitrary imported projects cannot Build/Play in it. This is not full desktop editor parity. The Activity templates currently cover these consumer contracts; arbitrary unrelated ProjectPacks are not automatically Android apps.

Project settings are **nonsecret** and live in `examples/editor-home/AndroidExport.celem` (or the selected consumer's own registered AndroidExport object). For a modern AAB candidate:

```text
object Confectory.EditorHome::AndroidExport extends Confectory.AndroidExport.Settings::Defaults {
value applicationId = "org.yourcompany.yourapp";
value applicationTitle = "Your App";
value versionName = "0.1.0";
value versionCode = 1;
value packageFormat = "aab";
value androidTargetFramework = "net10.0-android";
value keyAlias = "your-existing-upload-key-alias";
}
```

Use your real application ID and existing upload-key alias. Keep the application ID stable for updates and advance versionCode for each upload. Select `apk` for a locally installable signed APK instead. There is no keystore/password/path settings field. Existing projects retain `net8.0-android` for compatibility; this legacy default is **not a current general Play-submission configuration**. Framework selection must match the selected SDK major and installed Android workload; the exporter rejects mismatches before provider compilation and pins the selected SDK version in the generated project.

Prerequisites on Windows: .NET8 runtime for the Confectory tools; selected .NET10 SDK/Android workload for the modern candidate; its compatible full JDK (current Microsoft guidance recommends JDK21); Android SDK API36 and the workload's required build-tools. Set `JAVA_HOME`, `ANDROID_HOME`, and optionally `CONFECTORY_DOTNET` to your installed host. Tools installed in a cloud workspace are not installed on your PC. Dependency/license installation is a separate explicit local action, not performed by this script. Microsoft documents how its `InstallAndroidDependencies` target resolves the selected project's exact dependencies: https://learn.microsoft.com/en-us/dotnet/android/getting-started/installation/dependencies . Do not merely change a manifest number on the old runtime.

Optional CLI-style wrapper usage from `C:\Confectory`:

```bat
export-android-windows.bat -Project "C:\Confectory\examples\editor-home\project.cpack"
```

`-Output "C:\YourNewExport"` chooses a new output directory; existing exports are never overwritten. `-Unsigned` skips all signing prompts. The completed unsigned path is shown by the exporter and recorded in `package-report.json`, normally `bin\Release\<selected-framework>\<applicationId>.aab` (or `.apk`). Failures do not produce a successful package report. A source-only export is still available through the existing two-argument exporter command.

After packaging, signing is optional and entirely user-local: explicitly choose SIGN, select an **existing** keystore in the file picker, confirm SIGN in the owned console, and enter masked store/key passwords. Enter at the key-password prompt means the same password. Escape cancels password entry. The alias comes from project settings. For Play App Signing use the existing registered **upload key**, not an arbitrary replacement key. No actual key has been created/used by our tests.

The signing helper invokes JDK jarsigner for AAB and Java/apksigner plus prior zipalign for APK. Passwords travel only in the individual signing child's transient environment via the tools' official environment-password options; they are absent from argv, the parent environment, reports, files and tool logs. Signer output is consumed without logging. These are normal local process credentials, not a guarantee of erased managed-memory copies or protection from privileged local process inspection. No credential is requested through chat. Unsigned input remains preserved; signed output uses `-signed.aab`/`-signed.apk`. Only after certificate-block presence and SDK signature verification does `signing-report.json` record success. Existing signed files are refused and preserved. Signature verification does not certify Google Play acceptance.

To retry signing an existing current export without rebuilding (local console only):

```bat
dotnet targets\android-export\bin\Release\net8.0\Confectory.AndroidExport.dll --sign-export "C:\YourExport" "C:\YourExistingKey.jks"
```

The selected key path is not persisted. No passwords are accepted as arguments or redirected input. This command has not been executed with a real key in development.

## Play and native compatibility gates

As checked on 2026-10-07, Google's live ordinary mobile new-app/update policy requires API36 from 2026-08-31, with an extension mechanism until November1: https://support.google.com/googleplay/android-developer/answer/11926878 . No internal-testing exemption is assumed. The prior actual net8/API34 APK/AAB proof verifies packaging only, not submission readiness.

The live page-size guidance also requires 16KB support for 64-bit native libraries on API35+ and states noncompliant-update blocking from 2027-02-01: https://developer.android.com/guide/practices/page-sizes . This project embeds a native .NET runtime. Framework support alone does not validate every native dependency or archive alignment. Read-only inspection is available without Python/NDK:

```bat
dotnet targets\android-export\bin\Release\net8.0\Confectory.AndroidExport.dll --inspect-package "C:\YourExport\bin\Release\net10.0-android\org.yourcompany.yourapp.aab"
```

It lists actual arm64/x86_64 `.so` ELF LOAD alignment and RELRO-end checks; exit1 means failed/absent coverage. It explicitly does **not** claim APK ZIP alignment, 16KB device runtime, or Play acceptance. Follow Google's separate ZIP/bundletool/device checks. Actual SDK manifest target, native libraries, current upload-key registration and Play Console validation remain necessary. Upload the verified signed AAB yourself to your selected Play testing track; the workflow does not access your account or upload anything.

## Verification and ownership ledger

Public settings addition: `Confectory.AndroidExport.Settings::Defaults.androidTargetFramework`; existing IDs/role signatures unchanged. Target-owned exporter, unsigned report, optional signer/native inspector and Windows entry scripts changed. Outside reads: existing Home/engine settings and exporter SDK Package policy; Oracle/Android signing tool manuals and Play requirements. No Core, runtime model, browser renderer or editor UI implementation changed. Rebuild scope: exporter/tests and the selected Android export; settings alter generated app metadata/framework, not managed function signatures. Signing is a separate local operation and never changes pack sources.

Functional/security gates: solution builds with zero warnings/errors; test fixtures cover password-free arguments, child-only environment, no shell, alias injection refusal, and 4KB/RELRO/truncated ELF rejection. Settings tests cover format/framework export and hostile XML/MSBuild values plus credential rejection before compilation. No test generates a key or performs real signing. Windows file picker/console execution and actual signing remain unrun here. API36 SDK/package/device verification is pending separate approved tool installation; no modern candidate is labelled Play-ready.

Official signing references: https://docs.oracle.com/en/java/javase/17/docs/specs/man/jarsigner.html , https://developer.android.com/tools/apksigner , https://developer.android.com/studio/publish/app-signing .
