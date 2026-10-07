# Readonly windowless browser rendering proof

This Windows x64-only proof opens an explicitly selected existing ProjectPack and uses the same Concept/Feature/Module browsing and public UIOrder frame as the ordinary project-browser consumer. Several semantic declaration windows borrow retained text-services objects. The engine paints window backgrounds, borders/labels and the native service draws text/selection into its buffered canvas. No child RichEdit input HWND is created.

It is a readonly rendering proof. Native selection button sets a small range via native EM_SETSEL for visual inspection; pointer packets are forwarded for initial selection trials. Ordinary keyboard editing, OS shortcuts/copy, timers/capture/invalidation, raw IME/candidate positioning and DPI are not a completed provider. Use run-browser-windows.bat for the existing editable provider. The proof's field snapshots explicitly report interactiveReady=false. This is a step before replacing the browser's NativeUI role, not a completed Windows integration milestone.

With an existing .NET 8 SDK on Windows x64:

```bat
run-windowless-browser-proof-windows.bat "C:\\your\\existing-project\\project.cpack"
```

Select elements in the actual browser to open two windows. Check native text/selection clipping while overlapping, raising within equal Render Order, toggling Order 0/5, moving, minimizing/restoring, closing/reopening and closing the parent. The same published visible regions govern draw and hit ownership. The text service objects persist during movement/redraw and release with their View. Sources are not implicitly saved, renamed or moved. Existing Home design is untouched.

Actual Windows execution has not been performed in the Linux consumer environment. Keep any diagnostic logs/screenshots private; do not infer keyboard/IME/DPI/copy readiness from the Linux ABI fixture or managed build. A source/module rendering failure should be recorded as such before using this provider elsewhere.

Explorer double-click now prompts for the existing project.cpack when no argument/environment path is provided. Enter the path without surrounding quotes. The launcher prints build/run output and exit code and waits at completion, so early failures remain readable. Set CONFECTORY_NO_PAUSE=1 for scripted invocations. This is a direct cmd/dotnet flow; no PowerShell. cmd/Windows execution is unavailable in the Linux workspace: source inspection identifies the old no-argument immediate-exit path, but does not establish the cause of a particular Windows observation.

Opt-in editing bridge experiment: run-windowless-editor-proof-windows.bat "C:\your\project\project.cpack" sets CONFECTORY_WINDOWLESS_EDIT=1 for this consumer only. Native text services are then writable and attach raw keyboard/IME messages to their shared parent. Common UIOrder activation decides which View owns focus; root activation retires editor focus. Retained model buffers follow native snapshots outside observed composition, survive View close/reopen, and Keep local draft validates into the Workspace without writing source files. The default launcher remains readonly. This is still an unfinished host bridge (interactiveReady=false), not a verified replacement provider: rectangular caret rendering, timer/capture/cursor host services and IMM geometry are now connected; actual Windows editing/clipboard/IME/candidate placement/DPI validation and full normalized directional model integration remain next steps. Native snapshot selection offsets are UTF16/min-max, not a completed normalized directional BaseUI adapter.

The proof consumer now creates and joins its own STA UI thread, and each service owns a balanced OleInitialize/OleUninitialize lease. The native provider rejects incompatible COM apartments instead of silently promising clipboard/in-place readiness. Keyboard shortcuts are delegated to RichEdit rather than rewritten. The editable launcher remains an experimental opt-in; Home is preserved. Native caret/IMM request diagnostics appear in CONFECTORY_BROWSER_TRACE=1 snapshots; raw text logs should stay private.
