# Local Windows compiler transport fix

The reported Windows launcher reached `TARGET_FAILURE` inside the executed dotnet target tool. Its inner Roslyn launch passed every framework and project reference on the command line. A short executable and working-directory path do not prevent the Windows command-line length limit from being exceeded. Provider JSON already used stdin; changing that transport or enabling long filesystem paths would not address this launch.

The target now writes compiler arguments to a uniquely named UTF-8 response file in its existing output workspace. The launch contains only the compiler path, `-noconfig`, and the response-file path. Response files are removed in `finally` on success and handled failure; concurrent invocations use different names. Compiler stdout/stderr are drained concurrently and the existing 90-second compiler timeout is unchanged. Embedded quotes, line breaks, NULs and trailing backslashes are rejected before response-file execution. Abrupt termination of the entire target process is outside this cleanup guarantee.

CLI `run` now invokes the ordinary CLI `build` process and reports its PID, elapsed time, bounded cache observations, completion and runtime exit. Both build pipes are drained concurrently. The runtime exit code and structured build failure remain observable. This adds progress diagnostics without adding a build timeout.

## Validation

Using `/workspace/toolchains/dotnet-8.0.425/dotnet`:

```
dotnet build targets/dotnet/Confectory.Build.DotNet.csproj -c Release
dotnet build src/Confectory.Cli/Confectory.Cli.csproj -c Release
dotnet build tests/Confectory.Tests/Confectory.Tests.csproj -c Release
dotnet tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll CompilerTransport
CONFECTORY_BUILD_HEARTBEAT_SECONDS=1 dotnet tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll cli_run
```

The compiler regression passed: one test, zero failures, 2.322 seconds. It actually compiled with 600 project references plus 163 framework references, Unicode/space-containing source and output paths, and a copied native dotnet host at a space-containing path. Estimated expanded arguments measured 124,509 characters; the response-file launch measured 365. Concurrent successful compilations and a malformed-source failure left no response files. The CLI regression passed: one test, zero failures, 3.701 seconds, covering spaced paths, visible output, build failure and runtime exit-code propagation.

These are actual Linux process/compiler checks, including a command far above the Windows command-line limit. Native Windows acceptance remains pending; no Windows runtime or APK execution is claimed. To spot-check on Windows, build Release and run `run-engine-windows.bat`; retain the new PID/progress/completion lines and any target diagnostic. Development does not wait for this asynchronous check.

## Stress arguments versus real selected references

The preliminary 103,734-character probe deliberately supplied the same `System.Runtime.dll` reference 600 times. Those repeated references were unnecessary to that tiny test function. This was a transport stress test, not a measurement of normal engine compilation. The later registered regression uses the same construction at different temporary path lengths and measures 124,509 characters. These counts use the target's explicit expanded-command estimate, not captured Windows process command lines.

For comparison, the new target actually relinked the retained Checkpoint 6 engine and Checkpoint 8 Augment artifact sets, using their original contract/implementation paths and generated binding sources copied into temporary output workspaces:

| Selected composition | Contract references | Implementation references | Unique project paths | Framework references | Expanded estimate | Response launch estimate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Confectory.Engine, Checkpoint 6 | 116 | 116 | 232 of 232 | 163 | 66,500 | 216 |
| Example.Augment, Checkpoint 8 | 82 | 82 | 164 of 164 | 163 | 53,472 | 216 |

Both real relinks succeeded and removed their response files. Engine project-reference arguments contributed 45,008 estimated characters and framework-reference arguments 21,131; the copied source argument contributed 47. Augment project references contributed 31,980 with the same framework/source counts. Remaining characters are options/output and launch overhead. Measurements are Linux paths for retained compositions, not the user's current Windows build. No raw body text is passed on compiler argv.

The public planner starts from the entry and explicit `always` roots, selects implementations through binding/import and declared dependency edges, and compiles selected implementations. `CompilePack` deduplicates each implementation's own contract and declared imported contracts by ID. Final linking supplies the selected contract assemblies and selected implementation assemblies, rather than every registered pack. The target adds the entire .NET 8 reference pack as a broad compile-time framework set. A referenced assembly is not thereby proven runtime-used or necessary to the smallest possible compiler set. No project-reference duplicates appeared in either measured composition. Exact duplicate-path elimination is a possible separate optimization; framework pruning or removal of declared dependencies requires analysis and consumer testing. Response files solve transport limits without claiming a minimal dependency set.

## Locality and rebuild scope

Public target-tool compile/link contracts are unchanged; result diagnostics are additive. The dotnet target implementation and CLI launcher own these changes. The regression reads the existing test Fixture and public target request/result protocol. No Core, platform-window, UI pack or application behavior was edited for this fix. Changing the target tool rebuilds managed artifacts selected for Linux, Windows and Android; platform capability/acceptance gates remain separate. This is a local coherent increment on `integration/checkpoint-9`, ahead of the unfinished projection increment, and is not a completed Checkpoint 9 marker. No publication is authorized.
