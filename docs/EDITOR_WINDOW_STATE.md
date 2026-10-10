# Retained EditorHome window state

The later [multiple-view connection](EDITOR_MULTIPLE_VIEWS.md) extends this foundation with three additional owned source/selected-field windows. The single-workspace limitation below describes the original increment.

This increment connects the existing actual `examples/editor-home` Main to the public UIOrder/WindowPlacement contracts. It does not implement the Sites visual layout. The reference URL failed through the environment proxy (403 / Chromium ERR_TUNNEL_CONNECTION_FAILED). Official Library materialization to the consumer-local destination also failed (`download failed`); no screenshot bytes were obtained or inspected. No archive/download bypass was attempted.

## Behavior

- Each live project context owns a serialized UIOrder scene and a set of folded window IDs, separate from its model, draft buffers, jobs and permissions. Home screens have separate presentation scenes.
- The existing workspace is window 6. Project menu, information, settings, reports, Helper selection, selected Helper, Augment, connection selection and approval each have stable IDs 10–18. These identities do not reuse the old single menu slot. The workspace and displayed menu share a render order; activation determines their front-to-back order. Existing navigation overlays and modal source/close reviews retain their higher orders.
- Drag the existing eight-pixel top inset of the workspace or menu. Double-click it to fold or unfold; a folded window has a 26-pixel handle. Folding omits its body controls/native fields from the frame, retaining the existing buffers and native binding lifetimes. The current product still displays one selected workspace and one selected menu, not arbitrary concurrent element editors.
- Geometry, viewport reachability, snapping, relative relationships and recovery use UIOrder's existing public operations. The available placement area excludes the sidebar and bottom chat. Oversized panels retain the common minimum-visible-handle policy; this increment does not invent responsive content layouts for them.
- Drawing rectangles/text, native field clipping and hit testing use the same composed regions. Pointer/native field activation occurs before presentation composition. All final bounds are read after placement updates, including dependent-window movement.
- Closing/hiding a menu and returning to that same menu keeps its placement and folded state. Hiding a project keeps its scene under the same live context. The existing model still requires **Edit sources** to show its source workspace again after returning; the retained draft/native binding is reused. A different project cannot inherit it. Complete project close retires its presentation state with the existing UI resources; reopening a completely closed project gets a fresh scene. No cross-process layout persistence policy was added.
- Resize, focus/capture cancellation, scene change and surface suspension cancel an active drag. The platform's existing pointer capture remains responsible for physical capture.

## Boundary and locality

Only the existing `Confectory.EditorHome::MainBody` production implementation changes. No new public contract, core rule, platform adapter, model command, Helper policy, source Confirm policy or provider permission is introduced. Existing public `UIOrder::{Create,Update,Compose,Hit}` calls carry retained state. The ordinary ProjectPack and common Main remain selected for Linux, Windows, Android and browser.

Outside implementation reads: UIOrder Update/Compose and WindowPlacement README for state/placement semantics, Window Pump for capture cancellation, NativeInput interaction through the existing Main. Tests reuse the existing real X11 harness and ordinary UI actions. The navigation test's report-window lookup changes from transient ID 2 to stable ID 13; its behavior assertions remain intact. No alternate entry, injected product command or success-only execution path was added.

## Validation

See the dated entry in `AI_DEVELOPMENT_STATUS.md` for final results and commands. New acceptance: `tests/gui/editor_home_windows_x11.py` and `tests/web/editor_home_windows.py`. The X11 gate is registered as `test_actual_editor_home_retained_window_state_and_project_isolation`.

Visual porting, additional simultaneous object views, Helper settings policy, YogiBox recipient wiring and Sites screenshots remain outside this behavior-only increment. Live providers/accounts, user-PC changes, native Windows and Android device execution remain untested/deferred. Main and Android version settings remain unchanged.
