# NativeUI service contract

Public elements: `Create(long[] surfaces,int view)->string`, `Request(string host,string operation,string payload,long parent)->string`, `Capabilities()->string`. This contract pack intentionally has no Request/Capabilities provider. `packs/native-ui-desktop` is an interchangeable role pack with the same namespace/element IDs and matching public signatures, implementing Windows/Linux. ProjectPack registry chooses the role pack; it does not insert fake Android/web implementations. Create explicitly borrows one open Window View. Only the native provider interprets its identity as HWND/XID. All host operations run on the creating UI thread. Close native children/dialogs before buffers, controls and native parent; close is idempotent. Retained identities are `id:binding`. Native editing, selection, clipboard and IME stay in platform widgets.

Request operations:

| Operation | Payload/result |
|---|---|
| create | Internal provider creation, explicit borrowed parent identity. Returns host token. |
| configure | id, binding, bounds `[x,y,width,height]`, value, caret/anchor UTF16 indices, mode singleline/multiline/source, hint, visible/enabled/readonly. Returns native snapshot. Genuine external writes apply once, deferred during composition; ordinary frames preserve editing/undo/selection. |
| snapshot | Array of retained field snapshots: id/binding/value/caret/anchor/focus/visible/enabled/readonly/composing/deferredExternal/nativeHandle/provider. Hidden bindings are not copied into model by BaseUI. |
| frame | shown identity strings. Hides absent fields, preserves draft and native identity. |
| clip | key from the BaseUI Field snapshot, regions as parent-client `[x,y,width,height]` records (maximum256). Applies visual/input clipping to exactly that retained binding; regions must lie inside its configured bounds. Empty regions occlude completely. Unchanged regions preserve native identity/editing. |
| focus | id, zero returns focus to borrowed parent. Disabled/hidden fields do not receive native focus. |
| commands | id, keys (maximum16 target-native key IDs). Explicit application commands only. Ordinary editing remains native. Tab except source, Escape, single-line Enter already produce paired events outside Ctrl/Alt/preedit. |
| events | Drains flat six-int events `[controlID,kind,x,y,key,flags]`. Kind5/6 paired key transitions, Shift4/repeat1; kind9 outside-host focus loss. Consume once before rendering. |
| forget | binding. Retires native controls before disposing/replacing borrowed model buffer. |
| folder-begin | Existing absolute initial directory. Starts owned asynchronous OS folder chooser; reject duplicate active dialog. |
| folder-poll | idle/pending/selected/cancelled/error. Selected absolute existing path; completion consumed once. No custom browser fallback. |
| folder-cancel | Cancels dialog without discarding input models. |
| close | Cancels/retires owned dialog, children/callbacks/resources, preserves borrowed parent/model lifetimes. |

Budgets:128 retained bindings per host, bounds8..8192, hint2048, service payload8MiB, model text1MiB UTF16. Windows Rich Edit enforces its native limit. GTK Entry supports65535 scalar characters, exposed in Capabilities; external oversize configuration is rejected. GTK source/multiline native buffer insertion rejects text exceeding the shared model budget without replacing accepted text. No clipboard content logging or clipboard algorithms.

Linux uses installed GTK3/GtkSourceView4 under X11. Foreign-parent hosting must focus the GTK child on native pointer press and must not cancel canvas buttons for within-host focus changes. Window Create/Reopen synchronizes server creation before another native connection borrows the window. GTK3 Entry has no toolkit undo; this limitation is explicit (`singlelineUndo=false`), while GtkSourceBuffer owns multiline/source undo. No hand-written undo replacement is installed. Native Wayland is unverified.

Windows uses Unicode plain-text RICHEDIT50W child HWNDs. The OS owns IME/preedit/candidate UI. Shell IFileOpenDialog owns a cancellable STA, borrowed HWND owner and COM lifecycle while application UI continues pumping. Managed compilation does not establish Windows input/dialog/IME correctness. Actual Korean preedit/commit/cancel/focus/candidate anchoring remains a Windows runtime gate.

BaseUI.NativeInput adds `Clip(host,fieldKey,regions)` over this service; the public Field snapshot supplies fieldKey as `key`. This is binding-specific because hidden inputs in different project contexts may reuse a control ID with different geometry. Visible/ineligible and hidden are separate states. Engine overlay ClipRegions feeds both canvas text and native window regions. Native clipping requires X11 visual/input Shape support on GTK and Windows HRGNs on Rich Edit. Parent Win32 buffered drawing excludes child windows; focus moves inside a View do not emit outside-View cancellation. Consumers pump OS messages before synchronizing model focus and request OS focus only for focus intent. Windows modal parent enable/focus restoration happens on the creating UI thread after dialog-thread teardown. See `docs/CP18_WINDOWS_DEFECT_TRIAGE.md` for defects, implementation evidence and unverified Windows gates.

Android/web native provider packs are absent. Binding the contract-only pack fails with `MISSING_IMPLEMENTATION`; choosing the desktop role pack for those targets fails with `MISSING_TARGET_IMPLEMENTATION`. These are build-resolution diagnostics, not runtime stub rejection or platform support. Actual providers would require app/DOM host, lifecycle, UI-thread, system picker and granted URI/browser-handle permissions. Desktop filesystem paths do not imply URI/handle interoperability or broader permissions.
