# Readonly windowless browser rendering proof

This Windows x64-only proof opens an explicitly selected existing ProjectPack and uses the same Concept/Feature/Module browsing and public UIOrder frame as the ordinary project-browser consumer. Several semantic declaration windows borrow retained text-services objects. The engine paints window backgrounds, borders/labels and the native service draws text/selection into its buffered canvas. No child RichEdit input HWND is created.

It is a readonly rendering proof. Native selection button sets a small range via native EM_SETSEL for visual inspection; pointer packets are forwarded for initial selection trials. Ordinary keyboard editing, OS shortcuts/copy, timers/capture/invalidation, raw IME/candidate positioning and DPI are not a completed provider. Use run-browser-windows.bat for the existing editable provider. The proof's field snapshots explicitly report interactiveReady=false. This is a step before replacing the browser's NativeUI role, not a completed Windows integration milestone.

With an existing .NET 8 SDK on Windows x64:

```bat
run-windowless-browser-proof-windows.bat "C:\\your\\existing-project\\project.cpack"
```

Select elements in the actual browser to open two windows. Check native text/selection clipping while overlapping, raising within equal Render Order, toggling Order 0/5, moving, minimizing/restoring, closing/reopening and closing the parent. The same published visible regions govern draw and hit ownership. The text service objects persist during movement/redraw and release with their View. Sources are not implicitly saved, renamed or moved. Existing Home design is untouched.

Actual Windows execution has not been performed in the Linux consumer environment. Keep any diagnostic logs/screenshots private; do not infer keyboard/IME/DPI/copy readiness from the Linux ABI fixture or managed build. A source/module rendering failure should be recorded as such before using this provider elsewhere.
