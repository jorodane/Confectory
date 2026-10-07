# Audited target and lifetime handoff — 2026-10-07

Current branch: `integration/checkpoint-18-native-ui`. Original runnable `[Checkpoint 1]` commit `73d793f` is preserved. Ordinary branch push is authorized; no merge, deployment, signing or device installation was performed. Historical checkpoint/audit records remain evidence, not current capability claims.

## Acceptance and remaining limits

| Gate | Final evidence | Limits |
|---|---|---|
| A1/A2 Android entry and host coupling | Actual unchanged `examples/editor-home/project.cpack`, `Confectory.EditorHome::Main`; generic host, public generated PackEntry; actual and no-Window minimal consumers each produce unsigned API36 APK and AAB, zero SDK warnings/errors | No device lifecycle/touch/IME run; one Activity surface |
| A3 browser ownership and paths | Same EditorHome entry in native-linked WASM; actual Chromium commands, fields, Unicode selection, imports, navigation, close failure/retry; relocated installed tool and unrelated renamed pack pass | Physical folder-dialog Cancel unrun; volatile virtual filesystem, no dynamic build/project scaffolding/native IPC |
| T1/T2 results and locality | Strict runner reports SKIP separately; 3 missing-display GUI cases produce 0 PASS/0 FAIL/3 SKIP and exit1; selected body-only rebuild checks pass | Compiler/asset changes invalidate target fingerprint; not a cache-independence claim |
| R1/R2 lifetime | All-startup ownership and retained cleanup retries; fault tests and actual DOM removal failure/retry pass; actual Linux Shell and unchanged Home flows pass | Earlier original GTK chooser close failure remains intermittent/unresolved despite three unchanged passes |
| Two-window engine | Original Engine/BaseUI/Window registered tests: 3 PASS/0 FAIL/0 SKIP, 217.291s; actual screenshot viewed: independent counts1/0 | Default sandbox storage is read-only; configured supported storage prerequisite required |
| Windows | Same EditorHome managed target compilation passes | Windows OS runtime and export/sign wrapper execution unrun |

The two-window failure was reproduced using the ordinary built `examples/engine/project.cpack`: default runtime exits1 with read-only `/home/agent/.local/share/Confectory` at ProjectEntry.Request. No product source, assertion, input or timeout was changed. The same generated executable passed three direct runs after setting the existing public `CONFECTORY_ENTRY_STORAGE` policy to a writable owned directory. This is a disclosed environment prerequisite, not a claimed product regression repair. Default failure log: `/tmp/confectory-current-engine-default-storage-run.log`; configured runs: `/tmp/confectory-current-engine-owned-storage-run-{0,1,2}.log`.

Exact unchanged registered regression command:

```sh
DISPLAY=:96 XDG_CACHE_HOME=/tmp/confectory-engine-font-cache CONFECTORY_ENTRY_STORAGE=/tmp/confectory-engine-entry DOTNET_CLI_HOME=/tmp/confectory-dotnet10 CONFECTORY_DOTNET=/workspace/toolchains/dotnet-10.0.401/dotnet /workspace/toolchains/dotnet-10.0.401/dotnet tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll --require-runtime EngineTests BaseUITests WindowTests
```

The Home GTK failure and three original-condition passes retain the original dense `/tmp`, per-character input, pack and 10-second assertion. Sparse TMPDIR/clipboard alternatives are diagnostic only. No GTK root cause or performance fix is claimed. See [lifetime evidence](EDITOR_LIFETIME_RETRY.md).

## Artifact and functional evidence

Final actual Android APK SHA256 `815d58474f2568d18accf931f83d46c64c2fcbbc2db18497e005eba2258e053b`; AAB `20a6b69aa839e1c785dc5ea6b186901b5296d55a664e25de46b1181fe710594d`. APK zipalign16 and AAB bundletool validation pass, manifests target36; no signatures. All20 ELF64 LOAD segments align16384; 18 strict raw RELRO boundary warnings remain. No strict RELRO/device/Play acceptance is claimed. Commands and final source ledger: [Android host](ANDROID_GENERIC_HOST.md). Local Windows instructions: [export/sign workflow](ANDROID_WINDOWS_EXPORT.md); signing needs explicit separate authorization and an existing key.

Frozen actual browser acceptance: `/tmp/confectory-same-editor-browser-frozen-final-build.json` and `...-chromium.log`; relocated consumer `/tmp/confectory-browser-relocated-renamed-final-chromium.log`. [Browser increment](BROWSER_PLATFORM_PROVIDER_INCREMENT.md) records exact scope and ownership boundaries. Private HostLoop callback-array bridge remains documented; a public Step/Stop ABI is deferred.

Relevant strict gates additionally passed: Runner/Core/RuntimeBase43; RealTimeUpdate1; Home Android export1; arbitrary int/void entry and native owner2; Entry owner1; native owner/lifetime2; lifetime1; signing/ELF policy2; legacy independent browser1; Android owned-settings gate1. These are separate invocations, not a single full-suite pass. Final solution build: zero warnings/errors (6.51s).

## Final preparation-test maintenance ledger

Intended owner: Android export target and AndroidPreparation auxiliary lifecycle/locality test. Generated public binding is `PackEntry`, not removed sample alias `PackCalls`. Correct the stale artifact assertion while retaining every lifecycle and locality condition. Direct SDK probes now compile actual exported generic host/fields/import and generated entry against API36, never a repository sample Activity. Removed two unused fixed sample Activity templates: no runtime consumer referenced them; retaining them invited bypassing actual entry acceptance. Outside implementation reads: exporter copy/reference rules and generated SDK layout, necessary to determine the actual public export artifact contract. Core/shared pack implementations unchanged. Rebuild scope: exporter content plus test assembly; direct API probe and AndroidPreparation regression. AndroidPreparation strict regression passes1/0/0SKIP (45.313s), `/tmp/confectory-final-android-preparation.log`. Direct API probe passes with CS1701 Java.Interop reference-version warning; actual SDK package builds independently have zero warnings.

Next stage: asynchronous Windows native and authorized Android device checks; reproduce intermittent original GTK failure under native workload before claiming resolution; consider public HostLoop stepping contract as a separate consumer-tested increment. Keep functional and locality gates separate. No binaries/images/secrets/raw chat logs in Git.

Latest [16KB submission-risk diagnosis](ANDROID_16KB_FOLLOWUP_20261007.md): official RELRO static criterion remains unmet in18 libraries, including runtime prebuilts. LOAD/ZIP/BundleConfig passes do not establish full compliance; external native-toolchain correction is blocked, device/Play behavior unverified. No checker relaxation.
