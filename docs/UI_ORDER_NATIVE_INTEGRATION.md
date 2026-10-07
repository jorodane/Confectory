# Shared UI Order and Windows text integration

The next runnable experiment keeps the existing Home design and opens a project browser with several semantic editing windows. It is not a replacement input test screen. Concept, Feature and Module are independent browser tabs; Compact, Preview and Data show the same semantic objects at different densities. Simple values can be edited inline; complex values open an independent semantic editor. Category movement preserves identity and references. Namespace changes require explicit rename/refactor. Objects default to ProjectPack.

Source: Library `libfile_8f4f7e00f8ac81919ffc3ce78eaad789`, authoritative filename `붙여넣은 텍스트(5).txt`, 18,935 bytes, 938 lines. Library full-content read succeeded on 2026-10-07. Current Library materialization helper download failed; original local bytes have not been verified. Do not claim a materialized original or publish it in Git.

## Intended common pack boundary

`Confectory.UIOrder` is the proposed reusable role pack, consumed by both browser/editor and an independent game consumer. It owns the ordered window state and publishes the final presentation order, visible regions, pointer ownership and eligible keyboard window. It does not implement a world-depth renderer or own editor data.

Proposed public elementIDs are `Create`, `Command`, `Snapshot`, `Hit` and `Close`. They remain proposals until signatures, lifetime and consumer tests are implemented. Existing `BaseUI::ClipRegions` can provide bounded rectangle subtraction; its current 32-mask limit must be considered explicitly when defining the window budget. Native input integration should consume final visible regions rather than derive its own competing order.

Render Order determines the major ordering. Activating a window brings it forward only among windows with equal Render Order. Clicking an input activates its containing window while keeping keyboard focus on that input. Pointer hit testing traverses the same final ordering as rendering; a noninteractive opaque panel still blocks lower clicks. Keyboard activation and modal policy are distinct from pointer hit testing, but both refer to the same window state. Minimized, closed or fully covered inputs cannot receive new pointer input. Modal focus cannot escape to an underlying window. Closing or hiding a focused field is an intentional transition, not an external-focus dismissal.

Current gap at `872a169`: `BaseUI::ControlInput` traverses caller hit records in reverse; `Window::Win32Draw` traverses separate draw records forward. `UINavigation::Route` uses control IDs and caller eligibility. Home manually assembles masks and disables selected controls. These public contracts do not provide a shared ordered-window snapshot. No common window-order implementation is claimed yet.

## Windows native text proof

Use the existing GDI buffered renderer first. [Microsoft windowless Rich Edit documentation](https://learn.microsoft.com/en-us/windows/win32/controls/about-windowless-rich-edit-controls) specifies `CreateTextServices`, a host implementing `ITextHost`, and `ITextServices::TxSendMessage` for native editing. [TxDraw](https://learn.microsoft.com/en-us/windows/win32/api/textserv/nf-textserv-itextservices-txdraw) draws into a supplied DC. The proposed rendering contract must borrow a frame DC within the presentation transaction, preserve clipping/DC state, and use the same native layout for selection/caret geometry. The engine owns background, border and final composition; retaining a child-HWND overlay and changing its colors does not satisfy this proof.

Host callbacks need explicit UI-thread ownership, focus/capture routing, invalidation/timers, native caret geometry, IME context and candidate coordinates, DPI, scrolling and disposal. The renderer's private frame storage is not a public service; accessing it from NativeUI would be an implementation-boundary violation. Add a narrow public frame-composition contract with consumer tests rather than reading Window private state. Other targets retain distinct providers and capabilities.

Acceptance: browser opens two different semantic editors; repeated activation/movement/scrolling/partial occlusion shares draw and hit order; a covered native input cannot draw through or receive clicks; equal-order activation does not cross higher-order windows; focused input remains focused when its window rises; readonly Logs select/copy; Escape/outside click/external focus remain effective; minimize, close/reopen and Owner cleanup preserve unrelated state. Actual Windows runtime, IME and DPI evidence is required separately from compilation or Linux ABI fixtures.

## First corrective increment

`EditorHome::MainBody` executes bounded menu/navigation/tab/draft state changes synchronously through the existing public `EditorHome::Command` contract. Filesystem creation/opening, build and execution jobs remain asynchronous. `NativeUI::RequestBody` transfers a deliberately retired field's focus to its borrowed parent before hide/disable/forget. `Window::Win32CreateBody` distinguishes its pointer-up capture release from unexpected capture loss. No public signature or core implementation changes.

Outside implementation reads: `EditorHome::Command` and `ProjectShell::Command` were inspected to confirm shell changes are bounded in-memory operations; `NativeUI::RequestBody` to identify User32-triggered focus loss; `Win32CreateBody` and its ABI fixture to identify synchronous `WM_CAPTURECHANGED`. These reads are necessary because the current public event record does not encode transition intent. Edits are limited to the three bodies and contract regression fixtures. Rebuild scope is these three implementations plus dependent linking, with no contract recompilation or full rebuild.

Windows/Wine and Windows C++ cross-compiler are absent in this consumer environment. Do not install them or claim real Windows coverage. Backend/MEGA work stays paused until the browser/native integration gate is met.
