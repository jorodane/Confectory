# v318 baseline and behavior-preserving refactor

The user supplied v318 as the new reference and then requested internal refactoring before engine integration. Main 32994e7 contains only the additional ZIP and already includes work/current 2001d96. It was fast-forwarded into work/current; main was not written. Existing Review/description/Save/Confirm/restart implementation remains intact.

The ZIP is 15,930,003 bytes, blob `1b7026b34e47379e98a1968d14c04102491c33de`, SHA-256 `0a614fe2bf1ad3d8e10dfa8905bb6b61ea9f21b87b2492b2b87ca8566e9e6908`. It contains 16 files. Relative to frozen v196, app.js, style.css and the README changed; index, icon and all eleven asset files have identical contents. No live Site changes or Library retransfers are included. No applicable AGENTS.md or .agents/skills were present in this checkout.

## Findings and boundary

v318 already uses common nodes for windows, notes, groups and child Workspace portals. Refactoring retains that implementation rather than adding separate selection/focus/drag state. It moves 78 functions and 14 state fields into one presentation runtime, with 35 explicit host dependencies; semantic selection and execution closing are explicit domain callbacks rather than writes to external scalar state. The state record/index is used directly by the application; wrappers do not copy or synchronize state. The stylesheet and UI markup/actions are retained.

The reference's Home adds project search/favorites and project/pack tabs. Workspace adds pan/zoom, multiple selection, notes/groups/portals, child navigation/drag targets and main-window positioning. Browsers add instances, namespace/hierarchy/detail views, sorting and scoped Save/Confirm. Run now has a viewport, pause/step controls and separate build affordances. These changes were inspected in the actual original HTML on local Chromium.

The prototype still has simulated accounts/AI, marketplace/install/export/build/run behavior, field-level in-memory Confirm, mutable display-name identity and a hardcoded Monster schema. These are reference behavior only. The workbench is not linked into the actual consumer and never replaces real domain results. Actual terminal object editing and the issue inbox are excluded from this migration; existing compiler-backed Review and object-ID schema lookup must remain authoritative.

## Characterization

Original and refactored workbench: eight matching screenshot pairs, matching state snapshots and zero page errors. Actions cover Home filtering/favorites/pack tab, real browser opening, note/group shared multi-selection and drag/pointer cancellation, child navigation and delete cancellation, fold/close/reopen and fresh page restoration. A refresh deliberately retains the reference's welcome → later → Home sequence. Gesture points use the handle background; clicking a selected name has the original separate rename behavior and was not changed by refactoring.

[Recorded states/comparisons](evidence/v318-refactor/characterization.json), [state/host boundary](evidence/v318-refactor/runtime-boundary.json), [resource identities](evidence/v318-refactor/resource-comparison.json), [original nodes](evidence/v318-refactor/original-nodes.png), [refactored nodes](evidence/v318-refactor/refactor-nodes.png).

## Engine integration sequence

1. Port the Home/frame and wire project search/favorites/open/create/remove to actual cards and existing host/domain actions. Keep v318 pack-tab structure; populate only real known packs and expose unavailable remote/install actions explicitly.
2. Use this same common runtime for actual windows, notes/groups/child Workspaces, pan/zoom and search. Add explicit domain-view lifecycle adapters so hiding/moving/reopening windows retains owned inputs and shared drafts; note/layout persistence must not implicitly Save or Confirm source edits.
3. Attach v318 browser/participant/Helper/augmentation presentation to actual IDs, domain scopes, Worker status and existing commands. Preserve leaf editors, exact source-unit Review, mandatory creation registration and fresh subset tokens. Reference field-level acceptance is not a new source transaction policy.
4. Bind build/run presentation only to actual compiler/execution contracts. Pause/frame stepping, external marketplace, account connection, upload/export format and paid AI actions require an existing supported contract or a surfaced decision; no simulated completion is acceptable.

Each actual increment requires reference-screen comparison and the ordinary ProjectPack's action/cancel/close/repeat/restart checks; actual Linux/browser and cross-target managed builds are distinct from unavailable Windows/Android device acceptance. Identity migration, semantic deletion/conflict merging, billing and external publishing policies are not decided by this refactor.

Screenshot measurement disables CSS animation/transition/caret equally in both versions to avoid phase-dependent portrait/news effects. Gesture/state checks remain real browser events. Animation timing is not claimed as characterized. Repeated registered runs found time-label and portrait/font raster phase differences; this measurement correction does not change application code.

The comparison fixes the reference-only Date clock equally, waits for image decode, and checks visible text, geometry and behavior exactly. Screenshot checks record every difference and allow only at most 768 nonzero color channels (at most 256 pixels) with channel delta ≤8 on a 1440×900 frame. CSS must remain byte-identical. This is a visual measurement boundary, not an engine/compiler exception or a claim of universal pixel identity.

Registered final characterization: 1 passed, 0 failed, 0 skipped (31.883s). Test assembly build: zero warnings/errors (26.12s). Shipping consumer app.js and style.css are byte-identical to verified 2001d96; the new runtime is not yet registered in WebBundle or loaded by the engine. This checkpoint establishes reference refactoring only, not completed v318 engine migration.
