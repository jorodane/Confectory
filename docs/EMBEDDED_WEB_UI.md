# Embedded v196 EditorHome integration — 2026-10-11

Windows `Confectory.bat` now defaults to the embedded HTML EditorHome, using the ordinary `examples/editor-home/project.cpack`. The former external-browser page is not the default. This is a partial functional integration; it is not full v196 acceptance.

## Source and presentation

User commit `1ded375` supplied `reference/site-ui/Confectory-Editor-Prototype-v196.zip`; main merge `f64e329` was fast-forwarded on work/current. The archive is exactly 15,892,643 bytes, SHA-256 `02d4824e92ed0edbb43113659982b37a99a614117652bde4d8ac92367e334e34`. This resolves the earlier Library transfer blocker. No more Library retries or URL guesses were used.

The archive was extracted locally and its welcome/home/project screens inspected in Chromium. The consumer reuses the original stylesheet, SVG icon, nine PNG portraits and floating-window presentation functions. External Google Fonts import is removed in the consumer; system fallback fonts are used. Original demo objects, connected-account claims, Worker states and generated chat replies are not executed as application state. The unchanged ZIP retains the full original JS reference.

The working layout retains the sidebar, central floating browser/source/schema/review windows, bottom area and lower-right dock. Moving, resizing, snapping, folding and presentation placement persistence use the source JS behavior. Unapplied input is retained in memory per project when a panel is hidden; applied drafts remain owned by PackWorkspace. A second view changing the selected object keeps typed source pinned to its original ID until the user selects that object again. Calls read current state before invocation; out-of-order older state responses cannot rewind the client revision. Placement is local presentation state, keyed by durable project ID. It is not a new domain model or replacement for the existing UIOrder contracts in native consumers.

## Functional boundary

| Feature | Connected behavior |
| --- | --- |
| Windows entry | Root launcher builds the normal solution and selects the generic embedded host; no browser URL or legacy menu is the default. OS association/open arguments retain the existing DesktopEntry inbox. |
| Home / existing project | Safe catalog IDs open existing trusted model cards. Windows native file dialog selects a file through private host IPC; HTML receives no filesystem path. New project creation is visibly disabled. |
| Hide and return | Existing Model `leave` hides the panel while work and drafts stay owned. Unapplied HTML input is retained per project and is not silently saved or confirmed. |
| Object browser | Actual owned IDs, kinds and pagination through existing Model/PackWorkspace. Imported/unowned selections are rejected. |
| Source draft | Actual shared draft, consumer CAS, Apply and Save. Save leaves final source files unchanged. |
| Review / Confirm | Real Review token and before/after source preview. Explicit Confirm calls existing compiler-backed contract; stale selection/revision/token remains rejected. |
| Schema | Current object ID queries the effective schema. Scalar/reference fields use existing `data-path` CAS with the inspected source revision into the shared draft. Pending field input survives schema redisplay; it is not silently rebased. Compound/function/list editing is disabled pending consumer binding. No fixed Monster lookup. |
| Complete close | Native window asks for confirmation, then consumer saves and closes selected/background projects through existing commands; runtime owners retire before the session. Unsaved HTML input requires Apply/Save before close and is explicitly mentioned by the confirmation. Actual Windows dialog behavior remains unverified. |
| Run / Stop / Logs | Existing Model run/stop commands and actual execution polling/logs, with project/repository roots redacted. Start/stop of an ordinary ButtonGame project is tested; this is not a claim of a full successful game run. Hidden active projects keep polling. |
| Helper / Worker / chat / augmentation / directions / YogiBox / build target selection | Consumer bindings remain unfinished and controls are disabled. Portraits are marked as reference artwork; no fake account, Worker, proposal or chat success. No per-Worker chat was added. |
| Multiple independent object edit windows | Existing native model/view contracts preserved, but this HTML consumer currently has one source view plus schema/review windows. |

Live AI accounts/model calls, user-PC installation, signing, registry imports and Sites edits are deferred. No new conflict/payment/transmission policy is introduced. Linux keeps the existing native UI; browser diagnostics use the same HTML consumer and common transport. Android managed compilation retains its existing UI and version settings.

## Common resources and host

The common WebUI accepts a compiled trusted resource manifest with file ID, MIME, exact size and SHA-256. Each file is read into a size-bounded buffer and snapshotted before exposure; path traversal and reparse-point components are refused. Budgets are 4 MiB per resource, 32 MiB aggregate, 256 resources and 4 Mi characters for the descriptor. Inline bundles continue to work. All nine original PNGs fit this ordinary contract; no EditorHome exception or unbounded file serving is used. Consumer identities are pinned in `WebBundle.csbody` and must be updated when assets change.

Windows host renders declared resources beneath a private synthetic HTTPS origin using WebResourceRequested. There is no HTTP listener, arbitrary folder mapping, file URL or JS host object. PackChannel replies are bounded to 6 Mi characters so a 4 MiB base64 resource fits. Request/revision/scope/cancellation checks remain in WebUI. Native actions have a separate compiled allowlist, 16 Ki-character payload bound and private parent IPC. Browser endpoints cannot invoke `host.open-file` or `host.close`.

The host needs existing .NET 10 Desktop and WebView2 runtimes. Missing WebView2 is diagnosed with exit 2; nothing is installed. Popups, downloads, permissions, host objects and external navigation are disabled. Its temporary profile is not deleted while the browser may still own it; profile reclamation is unfinished.

## Validation

Final outcomes are recorded in [AI_DEVELOPMENT_STATUS.md](AI_DEVELOPMENT_STATUS.md). The final browser/Windows/Android managed run passed both gates (312.651s). Common boundaries, embedded channel and actual Linux Xorg UI also passed. See [original](evidence/v196/original-project.png), [consumer](evidence/v196/consumer-project.png) and [home](evidence/v196/consumer-home.png) captures. Solution managed compilation, ordinary EditorHome Windows/Android profiles, generic transport/channel boundaries, actual Chromium images/drafts/Review/Confirm/hide-return/schema and actual Linux native UI are distinct checks. Managed cross-builds do not prove Windows OS execution. Windows CMD/PowerShell/file-dialog/WebView2 close/IME/resize and Android device/APK execution remain unverified.
