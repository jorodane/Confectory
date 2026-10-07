# Editor ownership and cleanup retry

This increment fixes audit R1/R2 at their owning roles. The actual product input remains `examples/editor-home/project.cpack`, entry `Confectory.EditorHome::Main`; its Render and Action layout/command functions were not replaced by a target shell.

## Contracts and boundaries

`Confectory.EditorHome.Model::CloseSession(string)->void` now marks the session closing, attempts each shell/workspace and the manager independently, retains failed handles, and clears the session registry only after success. Closing rejects further commands; public CloseSession remains retryable. Manager Dispose is already idempotent. The caller does not inspect its opaque internal fields.

`Confectory.HostLoop::Close(string)->bool` is the new public cleanup/retry contract. True means all owned resources closed. False means an asynchronous owned command still prevents model closure. A release exception retains the loop token and failing acquisition for retry. Run's selected provider owns desktop signals, browser RAF or Android app scheduling. Browser/Android Run install the public Close delegate for their host. The process-local callback array is Step, Dispose, requestStop, isClosed; it is a private bridge, not an engine special host.

Main installs its retryable acquisition ledger and callbacks before CreateSession, controls, Owner, surfaces, native hosts, text buffers, Snapshot, navigation and EntryListen. Every successful acquisition immediately records its releaser. Cleanup attempts all resources in reverse acquisition order, removing only successful releases. Early startup failures invoke the same cleanup. A pending command keeps the model alive until completion without blocking the app UI callback; its fault is observed and reported. Deferred cleanup failures retain their retry token and are not marked fully closed.

Reads/edits outside the intended HostLoop role: actual product Main/MainBody and the owning Model CloseSession body, because blocking desktop scheduling and disposed-first model cleanup could not be corrected solely in a host provider. No Core changes. Affected rebuild scope for this real implementation change: MainBody, Model::CloseSessionBody, HostLoop::RunBody/CloseBody and the new HostLoop::Close public contract. Actual Linux report confirmed exactly those four implementation bodies and one contract. Later tests changes do not modify target product bodies.

## Separate verification gates

Auxiliary fault checks read the exact checked-in Main, CloseSession and HostLoop.Close bodies and compile a typed provider-fault harness. They never rewrite a product body or substitute a shell for platform acceptance. The harness sweeps 16 startup fault/success points, two cleanup failure/retry cases, independently attempted shell/workspace/manager failures, retained handles, successful-release deduplication and the exact audit manager retry (two attempts, disposed, registry cleared).

```sh
CONFECTORY_DOTNET=/workspace/toolchains/dotnet-10.0.401/dotnet \
DOTNET_CLI_HOME=/tmp/confectory-dotnet10 \
python3 tests/probes/editor_lifetime_retry.py /tmp/confectory-lifetime-product-probe

CONFECTORY_DOTNET=/workspace/toolchains/dotnet-10.0.401/dotnet \
DOTNET_CLI_HOME=/tmp/confectory-dotnet10 \
/workspace/toolchains/dotnet-10.0.401/dotnet \
tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll EditorLifetimeTests
```

The registered gate passed 1/0 in 8.101 seconds. Exact audit retry probe also passed with `disposeAttempts=2`, manager disposed and registry cleared. Product Linux build passed at `/tmp/confectory-shared-runtime-r2-linux.json`. Actual unchanged GUI tests remain separate mandatory checks; auxiliary fault checks do not prove a desktop window, Android device, browser input/IME or APK execution.
