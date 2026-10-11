# WASM publish timing investigation after 6d7a601

The current ordinary EditorHome ProjectPack WASM build still does not pass the unchanged 120-second target-tool limit. No production fix was made. Frozen inputs from the earlier successful e3d55ea-era SDK publish also reproduce a timeout in the current workspace. Therefore the UI restoration changes are not necessary to reproduce this failure; the evidence does not establish a new UI/native-code regression. The precise source of the execution-time variation remains unresolved.

## Input comparison

The browser target source and project settings are unchanged since e3d55ea. SDK is 10.0.401, wasm workload 10.0.12. app.js and consumer.css are the only changed declared resources: aggregate bytes increase from 16,737,704 to 16,773,759 (+36,055). They are not additional SDK native code.

The frozen successful SDK snapshot contains the e3 app manifest pin; the current captured snapshot contains the current pin. Both have 74 immutable references. 73 DLLs are byte identical; one 209,408-byte EditorHome implementation DLL differs. Generated Bindings (184,873 bytes) and public-linkage (536,861 bytes) are byte identical. Rebuilding each diagnostic input produces **the same 3,004,710-byte native WASM**, also identical to the earlier successful native artifact. This supports an unchanged native-code workload, not an inference that every managed byte is unchanged.

The original successful output's last framework compression file was written about 90.735 seconds after its SDK project was created. Its CoreLib Brotli file was written at 82.087 seconds; these are file timestamps, not a measured end-to-end CLI duration.

## Measured phases

Logging-only MSBuild BeforeTargets/AfterTargets hooks were placed in the ignored generated output parent. They changed no build properties, production sources, optimization or compression settings. The hooks were removed after measurement. Diagnostic SDK copies preserve source/reference bytes and rewrite only relocated paths. They are comparisons, not acceptance builds or special ProjectPacks.

| Run | Completed phases | Result |
| --- | --- | --- |
| Current ordinary ProjectPack, managed CPU=2 | C# compile 15.374s; native link 26.644s; publish compression begins around 69.607s after first Restore event | Normal target invocation exceeds 120s during publish compression. |
| Frozen successful input, cold SDK copy on tmpfs, CPU=2 | C# compile 7.724s; native link 16.133s; publish compression 72.531s | SDK diagnostic publish passes: 111.465s from first Restore event to final Publish event. Not current ProjectPack acceptance. |
| Current input, cold SDK copy on tmpfs, CPU=2 | C# compile 4.987s; native link 25.559s; compression begins around 51.032s | External 120s diagnostic bound reached during compression. |
| Current ordinary ProjectPack, managed CPU auto, EMCC=4/Binaryen=4 | C# compile 4.184s; native link about 25s; compression begins around 49.241s | Normal target invocation exceeds 120s during compression. |
| Frozen successful input, cold SDK copy in workspace, same quota-aligned settings | Compression begins around 43.857s | **Earlier successful input also reaches the 120s bound during compression.** |
| Current ordinary ProjectPack, managed CPU auto, EMCC=2/Binaryen=1 | Native link approximately 36s | Single native thread is slower; normal target again reaches 120s during compression. Not a viable recovery. |

[Machine-readable byte/phase comparison](evidence/wasm-publish-investigation/comparison.json) and six stage traces record exact events. Native output identity is stronger evidence than comparing only pack names. The SDK's compression mode remains its default SmallestSize; neither compression nor boot SRI verification was bypassed. The normal target's existing VerifyBundle was retained, but current publication never reaches successful acceptance.

## Environment and boundary

The container exposes five affinity CPUs but a cgroup quota of four (`400000/100000`). `/workspace` is overlay; `/tmp` is tmpfs. Removing the previous two-CPU managed override and aligning native degrees with the quota did not recover the normal build. One native thread worsened it. Root/workspace versus tmpfs and identical native workloads show substantial timing variation, but these measurements do not isolate one definitive filesystem, CPU-scheduling or SDK-compression cause.

No SDK cache substitution, older UI, hidden fixture, disabled target, lower optimization/compression level, timeout increase or EditorHome-specific path was introduced. Reusing cached older success was not presented as current success. No current standalone WASM runtime validation is claimed. The HTML transport, native Linux, managed platform and CRLF results already recorded remain valid and separate.

A successful normal current ProjectPack WASM publish remains required. A faster/more stable execution environment or a separately designed and integrity-preserving general SDK caching improvement could be investigated; neither is implemented or represented as validated here. Temporary SDK timing imports were removed; existing files/settings, UI restoration, CRLF behavior, main, Android versions and paused work are preserved.
