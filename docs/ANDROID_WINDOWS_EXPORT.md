# Repeatable local Windows APK/AAB export

Entry point: double-click `export-android-windows.bat`, select an engine ProjectPack, and follow the local prompts. There is currently no Android export menu in Home. The script builds the trusted exporter, creates a new timestamped output under `%LOCALAPPDATA%\Confectory\exports`, and packages the format in the selected project's AndroidExport object. It does not install development tools, create keys, install the app, or contact Play. The wrapper permits its own PowerShell script for that process only; it does not persist an execution-policy change.

For the actual shared editor product use `examples\editor-home\project.cpack`. The exporter calls its generated real ProjectPack entry through the same generic Android Activity used for other valid entries; product UI remains in the common controller. Android supplies one Activity surface, native fields and app-private imported document copies. Multiple independent OS windows, desktop file-manager launching and arbitrary imported Build/Play are unsupported capabilities. Native APK/AAB compilation is separate from Android device/lifecycle/IME acceptance.

Project settings are **nonsecret** and live in `examples/editor-home/AndroidExport.celem` (or the selected consumer's own registered AndroidExport object). For a modern AAB candidate:

```text
object Confectory.EditorHome::AndroidExport extends Confectory.AndroidExport.Settings::Defaults {
value applicationId = "org.yourcompany.yourapp";
value applicationTitle = "Your App";
value versionName = "0.1.0";
value versionCode = 1;
value packageFormat = "aab";
value androidTargetFramework = "net10.0-android";
value androidTargetSdkVersion = 36;
value keyAlias = "your-existing-upload-key-alias";
}
```

Use your real application ID and existing upload-key alias. Keep the application ID stable for updates and advance versionCode for each upload. Select `apk` for a locally installable signed APK instead. There is no keystore/password/path settings field. The default is now `net10.0-android` after the authorized whole-project migration. Previous net8/API34 artifacts are historical packaging evidence only. Framework selection must match the selected SDK major and installed Android workload; the exporter rejects mismatches before provider compilation and pins the selected SDK version in the generated project.

Prerequisites on Windows: .NET10 runtime/SDK for the Confectory tools; its Android workload for the modern candidate; its compatible full JDK (current Microsoft guidance recommends JDK21); Android SDK API36 and the workload's required build-tools. Set `JAVA_HOME`, `ANDROID_HOME`, and optionally `CONFECTORY_DOTNET` to your installed .NET10 host. `CONFECTORY_ANDROID_DOTNET` can select a separate native-packaging host; the generated global.json pins a matching installed SDK. Tools installed in a cloud workspace are not installed on your PC. Dependency/license installation is a separate explicit local action, not performed by this script. Microsoft documents how its `InstallAndroidDependencies` target resolves the selected project's exact dependencies: https://learn.microsoft.com/en-us/dotnet/android/getting-started/installation/dependencies . Do not merely change a manifest number on the old runtime.

Optional CLI-style wrapper usage from `C:\Confectory`:

```bat
export-android-windows.bat -Project "C:\Confectory\examples\editor-home\project.cpack"
```

`-Output "C:\YourNewExport"` chooses a new output directory; existing exports are never overwritten. `-Unsigned` skips all signing prompts. The completed unsigned path is shown by the exporter and recorded in `package-report.json`, normally `bin\Release\<selected-framework>\<applicationId>.aab` (or `.apk`). For APK, the unsigned Package output is explicitly aligned with the installed official build-tools `zipalign -P 16 -f 4` and verified with `zipalign -c -P 16 -v 4` before success. The report records `apkZipAlignmentVerified`; AAB bundle alignment is a separate archive/device gate. Failures do not produce a successful package report. A source-only export is still available through the existing two-argument exporter command.

After packaging, signing is optional and entirely user-local: explicitly choose SIGN, select an **existing** keystore in the file picker, confirm SIGN in the owned console, and enter masked store/key passwords. Enter at the key-password prompt means the same password. Escape cancels password entry. The alias comes from project settings. For Play App Signing use the existing registered **upload key**, not an arbitrary replacement key. No actual key has been created/used by our tests.

The signing helper invokes JDK jarsigner for AAB and Java/apksigner plus prior zipalign for APK. Passwords travel only in the individual signing child's transient environment via the tools' official environment-password options; they are absent from argv, the parent environment, reports, files and tool logs. Signer output is consumed without logging. These are normal local process credentials, not a guarantee of erased managed-memory copies or protection from privileged local process inspection. No credential is requested through chat. Unsigned input remains preserved; signed output uses `-signed.aab`/`-signed.apk`. Only after certificate-block presence and SDK signature verification does `signing-report.json` record success. Existing signed files are refused and preserved. Signature verification does not certify Google Play acceptance.

To retry signing an existing current export without rebuilding (local console only):

```bat
dotnet targets\android-export\bin\Release\net10.0\Confectory.AndroidExport.dll --sign-export "C:\YourExport" "C:\YourExistingKey.jks"
```

The selected key path is not persisted. No passwords are accepted as arguments or redirected input. This command has not been executed with a real key in development.

## Play and native compatibility gates

As checked on 2026-10-07, Google's live ordinary mobile new-app/update policy requires API36 from 2026-08-31, with an extension mechanism until November1: https://support.google.com/googleplay/android-developer/answer/11926878 . No internal-testing exemption is assumed. The prior actual net8/API34 APK/AAB proof verifies packaging only, not submission readiness.

The live page-size guidance also requires 16KB support for 64-bit native libraries on API35+ and states noncompliant-update blocking from 2027-02-01: https://developer.android.com/guide/practices/page-sizes . This project embeds a native .NET runtime. Framework support alone does not validate every native dependency or archive alignment. Read-only inspection is available without Python/NDK:

```bat
dotnet targets\android-export\bin\Release\net10.0\Confectory.AndroidExport.dll --inspect-package "C:\YourExport\bin\Release\net10.0-android\org.yourcompany.yourapp.aab"
```

It lists actual arm64/x86_64 `.so` ELF LOAD alignment and RELRO-end checks; exit1 means failed/absent coverage. It explicitly does **not** claim APK ZIP alignment, 16KB device runtime, or Play acceptance. Follow Google's separate ZIP/bundletool/device checks. Actual SDK manifest target, native libraries, current upload-key registration and Play Console validation remain necessary. Upload the verified signed AAB yourself to your selected Play testing track; the workflow does not access your account or upload anything.

## Verification and ownership ledger

Public settings addition: `Confectory.AndroidExport.Settings::Defaults.androidTargetFramework`; existing IDs/role signatures unchanged. Target-owned exporter, unsigned report, optional signer/native inspector and Windows entry scripts changed. Outside reads: existing Home/engine settings and exporter SDK Package policy; Oracle/Android signing tool manuals and Play requirements. No Core, runtime model, browser renderer or editor UI implementation changed. Rebuild scope: exporter/tests and the selected Android export; settings alter generated app metadata/framework, not managed function signatures. Signing is a separate local operation and never changes pack sources.

Functional/security gates: solution builds with zero warnings/errors; test fixtures cover password-free arguments, child-only environment, no shell, alias injection refusal, and 4KB/RELRO/truncated ELF rejection. Settings tests cover format/framework export and hostile XML/MSBuild values plus credential rejection before compilation. No test generates a key or performs real signing. Windows file picker/console execution and actual signing remain unrun here. API36 tools are installed with approval; actual package/archive checks are recorded separately. No modern candidate is labelled Play-ready solely by generation or signing.

Official signing references: https://docs.oracle.com/en/java/javase/17/docs/specs/man/jarsigner.html , https://developer.android.com/tools/apksigner , https://developer.android.com/studio/publish/app-signing .


Unsigned alignment correction: actual API36 SDK `Package` output had an unaligned `resources.arsc` entry even with AndroidZipAlignment16 because the usual signing targets were deliberately bypassed. The exporter now resolves installed stable build-tools before APK packaging, aligns only its newly generated unsigned artifact through an owned temporary path, verifies it, then records success. No signing target/key is involved. Outside reads were UnsignedPackage, SDK-generated archive and the official zipalign command used already by the local signer. Rebuild scope is exporter and newly packaged APKs; pack contracts, common UI and AAB generation are unchanged. Actual fresh pipeline replay is documented in the current Android archive gate ledger.


## Failure visibility repair (2026-10-08)

Double-click/no-argument BAT entry now pauses after success, failure or cancellation, preserving the child exit code before `pause`. Runs with explicit CLI arguments return immediately with that code; run from an existing CMD window to retain diagnostics:

```bat
cd /d "C:\Confectory"
export-android-windows.bat -Project "C:\Confectory\examples\editor-home\project.cpack" -Unsigned
```

The actual example entry is `examples/editor-home/project.cpack`. The user's remembered “Verify” error has not been captured: no wrong-selection, SDK or product failure cause is asserted. Read the complete first error, phase and selected ProjectPack/output paths before pressing a key; report those diagnostics. The wrapper prints a planned output path before building; on failure it may contain partial output, and package/export reports only exist if their respective stages wrote them. No new log/transcript is recorded, especially across signing. `-Unsigned` never prompts for signing; otherwise signing still requires explicit `SIGN` and an existing selected key.

JDK javac/jar, Android SDK directory, dotnet executable and expected exporter output are checked. Native package SDK/API/build-tools compatibility remains diagnosed by the actual SDK invocation; nothing is automatically installed. PowerShell catch uses non-terminating Console error output followed by exit1 instead of Write-Error under ErrorActionPreference=Stop. Build/package failures identify the stage and preserve child nonzero exit codes. Missing PowerShell itself is shown by CMD and also held by the no-argument BAT pause.

Scope/ledger: Windows Android-export entry scripts only, no pack/elementID/public contract or exporter implementation changes. Existing docs and scripts were read to trace exit and explicit signing boundaries; contracts do not govern console lifetime. Source review checks exit capture before pause, argument-based no-pause branch, diagnostic catch and explicit SIGN guard. Windows CMD/PowerShell/double-click execution is NOT RUN (Linux host has neither); no user PC was operated, no credentials/keys/device/upload action occurred. Rebuild scope none. Windows spot check: missing prerequisite and invalid ProjectPack must show a readable message and wait in no-argument flow; explicit `-Project` invocation must return nonzero without waiting; a valid unsigned AAB must retain output path and avoid signing.
