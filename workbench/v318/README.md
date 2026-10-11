# Frozen v318 behavior workbench

This is a **reference-only prototype**, not the EditorHome engine or an alternate ProjectPack entry. Its original mock objects, accounts, build/run and AI results deliberately remain reference behavior; none establishes real engine success. The shipping consumer is `examples/editor-home/ui/app.js`.

Source: `reference/site-ui/Confectory-Editor-Prototype-v318.zip`, uploaded by the user on main 32994e7. Git blob `1b7026b34e47379e98a1968d14c04102491c33de`; ZIP SHA-256 `0a614fe2bf1ad3d8e10dfa8905bb6b61ea9f21b87b2492b2b87ca8566e9e6908`. Original ZIP/Site are unchanged. No later live Site state is mixed in.

78 existing workspace functions and 14 previously global fields now have one owner in `examples/editor-home/ui/workspace.js`. Windows and decorations retain the original shared node index, selection, focus and drag/cancellation path. The browser/app use that same state directly; there is no second state synchronized with it. Explicit host getters/callbacks preserve current project/domain ownership. Style is byte-identical to v318; unchanged icon/portrait/html2canvas assets are reused from the consumer without duplicating them.

For local reference inspection, serve the repository root and open `/workbench/v318/`. The index base only resolves the same unchanged assets. This is not a deployment instruction.

Registered characterization extracts the original ZIP, serves both versions locally, and compares actual UI gestures, states and eight screenshot pairs with recorded rendering noise. Font requests are disabled equally to measure the documented offline fallback. It does not claim coverage of every prototype interaction, actual AI calls, domain authoring, billing or device runtimes. See `docs/EDITOR_V318_REFACTOR.md`.

Screenshot measurement disables CSS animation/transition/caret equally in both versions to avoid phase-dependent portrait/news effects. Gesture/state checks remain real browser events. Animation timing is not claimed as characterized. Repeated registered runs found time-label and portrait/font raster phase differences; this measurement correction does not change application code.

The comparison fixes the reference-only Date clock equally, waits for image decode, and checks visible text, geometry and behavior exactly. Screenshot checks record every difference and allow only at most 768 nonzero color channels (at most 256 pixels) with channel delta ≤8 on a 1440×900 frame. CSS must remain byte-identical. This is a visual measurement boundary, not an engine/compiler exception or a claim of universal pixel identity.

Additional original-v318 regression coverage passed in both versions: mixed window/note/group/child-Workspace selection Delete; cancel retains all selected nodes and child space; confirming removes all selected presentation nodes and the child tab while semantic browser objects remain; Delete in a focused note textarea removes the character without deleting any selected node. Registered result: 1 passed, 0 failed, 0 skipped (29.052s). This adds characterization only, not a new deletion rule.
