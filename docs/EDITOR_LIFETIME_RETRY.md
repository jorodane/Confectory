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


## Actual product verification and GTK limitation

The post-R1/R2 actual product Windows profile compiled successfully as net10.0 (`/tmp/confectory-shared-runtime-r2-windows.json`); this is compile-only, not Windows OS execution. The actual ProjectShell X11 gate passed unchanged, including menu/tabs, native fields, Run/Stop/logs, resize, leave/reopen and active execution interruption/cleanup (`/tmp/confectory-shared-runtime-r2-shell-x11.log`). The current Home card and narrow-window screenshots were actually viewed. Images and logs remain private and are not in Git.

The **original dense `/tmp` per-character folder typing gate failed**, first at parent selection and later at invalid-folder selection. A stock GTK chooser with the unchanged helper reproduced the failure without EditorHome; key events continued arriving after the helper's unchanged ten-second close deadline. `/tmp` had 6,228 immediate entries during the experiment. Writable XDG cache/config and memory settings alone did not resolve it. A sparse owned temporary directory let the same stock GTK helper close two dialogs, and the actual unchanged Home gate pass. This isolates an environment/directory-completion limitation; it does **not** resolve large-directory per-character typing or justify replacing the original failure with a general pass.

The first sparse directory `/workspace/confectory-gui-tmp` was too long for the ProjectEntry Unix named-pipe socket (108-byte OS limit). The actual product startup then failed at EntryListen and completed the new acquisition cleanup before propagating the original exception. A shorter `/workspace/g` yields a 105-character socket path. No temporary files were mass-deleted, no HOME variable was changed, and no timeout or expected outcome was relaxed.

**Required original Home gate: latest replay PASS; earlier failures remain unresolved/intermittent.** After all Android native package jobs finished, the original dense `/tmp`, per-character input order and ten-second deadline ran again with no TMPDIR/XDG/GSETTINGS overrides and passed. This is the original required scenario, not a substituted input path. It does not establish a product performance fix or resolve the earlier time-sensitive failures. Sparse directory and clipboard results below remain diagnostic experiments only; neither is used to satisfy the required gate. Existing helper, original input sequence and assertions are unchanged.

Diagnostic sparse-directory command that returned PASS (not a completion gate):

```sh
mkdir -p /workspace/g /tmp/confectory-gtk-probe-cache /tmp/confectory-gtk-probe-config
DISPLAY=:97 TMPDIR=/workspace/g XDG_CACHE_HOME=/tmp/confectory-gtk-probe-cache XDG_CONFIG_HOME=/tmp/confectory-gtk-probe-config GSETTINGS_BACKEND=memory PATH=/workspace/toolchains/dotnet-10.0.401:$PATH DOTNET_CLI_HOME=/tmp/confectory-dotnet10 CONFECTORY_DOTNET=/workspace/toolchains/dotnet-10.0.401/dotnet CONFECTORY_ENTRY_STORAGE=/workspace/g/entry-scope python3 tests/gui/entry_home_x11.py /tmp/confectory-shared-runtime-r2-linux.json
```

Report `/tmp/confectory-shared-runtime-r2-home-isolated-short-x11.log`, evidence `/workspace/g/confectory-entry-home-gui-77cm66kg`. This diagnostic run kept all original intro/create/focus/multiline/native picker validation/cancel/cards/paging/OS folder request/stable buffers/resize/repeated-open/restart/close/in-flight cleanup assertions.

A distinct actual product alternative was also verified against dense `/tmp`: Ctrl+L followed by native clipboard paste of the entire path. The private diagnostic driver `/tmp/confectory-home-clipboard-flow.py` uses the installed GTK clipboard service only for folder path entry; all original product assertions and close deadline remain, and ordinary field typing still runs. It runs the same actual product report, not another ProjectPack or UI. This diagnostic input path returned PASS; it is not the unchanged per-character gate, is not registered in the test runner, and does not erase or satisfy that failure. The alternative input driver is kept privately under /tmp and is not published in the repository.

```sh
DISPLAY=:97 XDG_CACHE_HOME=/tmp/confectory-gtk-probe-cache XDG_CONFIG_HOME=/tmp/confectory-gtk-probe-config GSETTINGS_BACKEND=memory PATH=/workspace/toolchains/dotnet-10.0.401:$PATH DOTNET_CLI_HOME=/tmp/confectory-dotnet10 CONFECTORY_DOTNET=/workspace/toolchains/dotnet-10.0.401/dotnet CONFECTORY_ENTRY_STORAGE=/tmp/confectory-shared-clipboard-entry python3 /tmp/confectory-home-clipboard-flow.py /tmp/confectory-shared-runtime-r2-linux.json
```

Alternative-flow report `/tmp/confectory-shared-runtime-r2-home-clipboard-x11.log`, evidence `/tmp/confectory-entry-home-gui-9y0usu81`. Stock-GTK negative controls remain local at `/tmp/confectory-gtk-folder-probe*.log`. The earlier typing-delay issue remains open/intermittent; native path paste is only a diagnostic workaround, not a product performance fix. The required original replay succeeded after native jobs settled, so directory density alone was not established as the cause. Stock-GTK delayed events and concurrent build load remain observations, not a proven root cause.


Required original replay command (after Android native jobs finished):

```sh
DISPLAY=:97 PATH=/workspace/toolchains/dotnet-10.0.401:$PATH DOTNET_CLI_HOME=/tmp/confectory-dotnet10 CONFECTORY_DOTNET=/workspace/toolchains/dotnet-10.0.401/dotnet CONFECTORY_ENTRY_STORAGE=/tmp/confectory-shared-r2-original-replay-entry CONFECTORY_DIALOG_FAILURE_SCREENSHOT=/tmp/confectory-shared-r2-original-replay-dialog.png python3 tests/gui/entry_home_x11.py /tmp/confectory-shared-runtime-r2-linux.json
```

Actual full PASS report `/tmp/confectory-shared-runtime-r2-original-replay-home-x11.log`, evidence `/tmp/confectory-entry-home-gui-7u_i9p9x`. No product, helper, input order, timeout or assertion changed between the failed original scenario and this replay. Native package build completion was the sequencing change. Earlier FAIL reports and negative controls remain evidence of the intermittent issue; they are not omitted from the outcome.

### Original-scenario replay series and stable input identity

After Android native package jobs settled, two further sequential runs used the same original command, DISPLAY :97, dense default `/tmp`, original per-character NativeControls input, original ten-second close condition and unchanged product source. Both passed:

| Original scenario run | Result | Private report | Private GUI evidence |
| --- | --- | --- | --- |
| Initial post-R1/R2 original run | FAIL at invalid-folder chooser close | `/tmp/confectory-shared-runtime-r2-home-x11.log` | Failure image `/tmp/confectory-shared-r2-dialog.png` |
| Original replay 1 after native jobs settled | PASS | `/tmp/confectory-shared-runtime-r2-original-replay-home-x11.log` | `/tmp/confectory-entry-home-gui-7u_i9p9x` |
| Original replay 2 | PASS | `/tmp/confectory-shared-runtime-r2-original-replay2-home-x11.log` | `/tmp/confectory-entry-home-gui-vza0ot1m` |
| Original replay 3 | PASS | `/tmp/confectory-shared-runtime-r2-original-replay3-home-x11.log` | `/tmp/confectory-entry-home-gui-0038uov6` |

Replay 2 and 3 reused the replay-1 command and entry scope; only private report/failure-image filenames changed. No files were deleted, no artificial stressor was introduced, and no product/helper/input/timeout/assertion was patched. A fresh base-environment check showed TMPDIR, XDG_CACHE_HOME, XDG_CONFIG_HOME and GSETTINGS_BACKEND all unset; `tempfile.gettempdir()` was `/tmp`, with 6,301 immediate entries then. Android native jobs remained inactive during these replays and resumed afterward. These three original-scenario passes establish the observed normal-workload result; they do not erase prior failures or prove a GTK performance fix. The earlier delayed-input failure remains unresolved/intermittent.

SHA256 identities of the actual tested worktree inputs, unchanged through these three runs:

| Input | SHA256 |
| --- | --- |
| `examples/editor-home/project.cpack` | `30fc997c50211707f40e1ba4c75d96dc71fbd3a97039cd1473d73cf103ab24ab` |
| `examples/editor-home/Main.csbody` | `ea2c4102d69eb52cd7654d8ff3a5cf9ef744e579daef84d3a2a2beb8d77b39f5` |
| `examples/editor-home/MainBody.celem` | `791837dc76f8ac1a1f5996ea3ea42e0dcc32c13914c7167c23eeab096d97b74a` |
| `packs/editor-home-model/CloseSession.csbody` | `642b0f24513eb7f3447d895b61909107fc4e71903dd373aeceb51a6dcd87f156` |
| `packs/host-loop/Run.csbody` | `ce76ea9fd15b82a381ef883e12cb840d88d9dccf0281de490a85ccdc497ed51e` |
| `packs/host-loop/Close.csbody` | `1853ab10a8c9fdb7a1d0942fcafa4d41943c05c8234fb9842576388ee154f6e2` |

The existing explicit private HostLoop bridge ABI remains documented for this increment. Relocating its Step lookup behind an additional provider delegate is deferred to a separate increment; no Core or product source was changed for these checks. The clipboard input experiment remains private, unregistered and unpublished.
