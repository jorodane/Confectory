# Browser provider draft — integration boundary

This is a local review increment, **not a runnable or published browser milestone**.

Owned pack: `Confectory.BrowserHost`. Public element: `Serve(repository:string, assets:string)->int`. Provider: `ServeBody`. It imports existing `Confectory.EditorHome::{CreateSession,Command,Snapshot,CloseSession}` contracts and adds no platform code to core. Browser assets implement DOM rendering, keyboard/touch-native HTML inputs and text areas, file picker import, manifest draft downloads, repeat-open draft retention, explicit Leave confirmation/cancellation, and browser unload protection. Play/build/native filesystem operations are deliberately absent from the HTTP surface. Download initiation does not mark the draft saved: browser cancellation cannot be acknowledged by this provider.

The provider is a **local .NET loopback host with browser UI**, not a static site, WebAssembly runtime, or arbitrary C# browser execution target. It requires the .NET host and existing trusted metadata-description host. Imported file contents are staged in a temporary per-session folder, interpreted by existing metadata-only project opening, and deleted on orderly owner exit. Imported registries and scripts are not built or executed. No external website, external upload or service is used.

## Integration blocker

The current shared model contracts belong to `examples/editor-home`, which is itself a ProjectPack. Core correctly rejects registering a ProjectPack as a library dependency. A runnable browser consumer needs coordinated extraction of its four domain contracts/providers to a reusable library pack (and native/Android consumer contract updates), or an explicitly owned export that materializes their trusted sources into a browser consumer. This increment performs neither shared edit nor source duplication. Consequently there is **no browser execution target/consumer yet**, and `ServeBody` has not been compiled through the public pack linker.

Root coordination explicitly paused shared extraction to avoid conflicts with Android. The source is retained for integration review; it must not be reported as browser completion.

## Security and capability review

The provider binds only `127.0.0.1`, requires a random per-process session header on APIs, rejects foreign Origin/Host, exposes a fixed static asset allowlist, sets a restrictive CSP, limits import size to one MiB, and allows only snapshot/import/leave operations. It accepts filenames rather than arbitrary local paths. Different selected projects remain blocked by the existing `open-request` policy even if the local draft is clean. Same imported filename and contents map to one staged path and do not reload buffers. Changed contents at the same filename map to a distinct project and therefore require explicit Leave.

Signing inputs are unrelated to this provider and have not been added. Browser drafts remain in memory and are lost on tab/process exit unless downloaded; unload protection is advisory browser UX rather than durable save.

## Verification in this increment

- `node --check packs/browser-host/assets/app.js` — passed.
- `git diff --check` — passed (tracked tree before staging).
- Chromium is installed. Actual startup/render/input/import/repeat/cancel/unsaved browser verification **has not run**, because the runnable consumer/linker boundary is unresolved.
- No browser target build, source compilation, deployment, main merge, or external push was performed by this worker.

Next integration gate: wire a real ProjectPack through public contracts, compile ServeBody, run the loopback host, drive Chromium through startup/input/import/same-file repeat/different-file refusal/Leave cancel/reopen/download cancellation/unauthorized API/invalid imports/owner exit. Separate source locality and functional gates. Check final targets and affected model consumers after any shared contract extraction.

## Outside implementation reads

Read `examples/editor-home/{Main.celem,MainBody.celem,CreateSession.celem,CreateSessionBody.celem,CreateSession.csbody,Command.celem,Command.csbody,Snapshot.csbody,CloseSession.celem,CloseSessionBody.celem,project.cpack}` to discover domain ownership, existing public operations and provider reachability. The existing contracts are usable but cannot be selected as a library while owned by a ProjectPack. Read `src/Confectory.Core/Build.cs` and existing target manifests/programs to inspect existing tool protocol and public linkage constraints, without editing them. Read baseline design sections on ProjectPack/core/target ownership. No applicable repository AGENTS or skills were found in initial file searches. No outside implementation was edited.

Rebuild scope when integrated: BrowserHost ServeBody and browser consumer bindings, plus any shared model contract consumers only if extraction/namespace changes are adopted. Existing native UI/provider implementations are untouched in this increment.
