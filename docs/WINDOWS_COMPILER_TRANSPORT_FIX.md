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

## Locality and rebuild scope

Public target-tool compile/link contracts are unchanged; result diagnostics are additive. The dotnet target implementation and CLI launcher own these changes. The regression reads the existing test Fixture and public target request/result protocol. No Core, platform-window, UI pack or application behavior was edited for this fix. Changing the target tool rebuilds managed artifacts selected for Linux, Windows and Android; platform capability/acceptance gates remain separate. This is a local coherent increment on `integration/checkpoint-9`, ahead of the unfinished projection increment, and is not a completed Checkpoint 9 marker. No publication is authorized.
