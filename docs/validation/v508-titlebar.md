# v508 app titlebar — stage 1

Baseline `9eecdcc5d40fb5660d7bf2588ec3c79a81ac3e3e`. This completes the implemented titlebar stage, not the entire v508 UI restoration. Workspace menus, the fixed Pack Manager tab, project participant filtering and semantic element editors remain separate next stages.

The original **내 정보 / 설정 / 최소화 / 최대화 / 닫기** order, SVGs and existing styles are restored to the Home and project topbar. The Windows WebView2 host supplies actual window commands. The prototype's CSS minimize, browser fullscreen and close-to-start callbacks are not used as native window actions. The maximize icon follows observed host state. The original topbar becomes the caption only after the native host acknowledges it; Intro/no-topbar and unsupported hosts retain the ordinary OS caption. Browser presentation does not pretend to minimize or close a native window.

`AppWindowForm` keeps the normal sizeable WinForms frame and asks Windows for its nonclient border insets before replacing the caption area. WebView2's supported draggable regions provide the drag path; buttons, inputs, links, tabs and other interactive regions are excluded. Per-monitor DPI mode is enabled. These are implementations intended to retain OS sizing and snapping, not evidence that native drag, sizing or snapping has been tested on Windows.

The custom close command calls the existing `Form.Close()` path. The original confirmation, presentation-flush acknowledgement and engine cleanup sequence is unchanged. Presentation flush also awaits an explicit profile Save already in progress. A failed Save retains input and prevents that flush from reporting success while the form remains open. Unsubmitted edits retain the original explicit Save/cancel behavior.

The original MyInfo form edits a private **display profile**, not an authenticated account. A bounded `user-profile.json` store under the owning editor storage persists its name, avatar, title, status and introduction across native sessions. Existing preferences, credentials, Agent grants, Helper data and projects are not migrated or cleared. Server-side field/image/size validation, revision compare-and-swap, unavailable-storage preservation and link rejection apply. Clients cannot select the storage path. Two renderer regressions found during this work were fixed: partial header recreation duplicated MyInfo, and a click while its initial profile read was pending was ignored. The module now reuses the button and shares the pending read.

## Visual evidence

The isolated visual oracle extracts the original window-control DOM construction/SVGs and MyInfo form from `reference/site-ui/Confectory-Editor-Prototype-v508.zip`, entry `Confectory-v508/dist/app.js`. Original and adapted controls use the same base header and frozen styles at 1280×892. Their screenshots are pixel-identical: topbar height 64px, control group 106×32px, each window button 34×32px. This comparison covers the restored fragment; it does **not** establish full-application v508 fidelity or compare a native Windows frame. No demo state is copied into the engine.

- [Original extracted titlebar oracle](v508-titlebar/v508-titlebar.png), [adapted titlebar](v508-titlebar/native-titlebar.png), [original-form MyInfo](v508-titlebar/my-info.png).
- [640px](v508-titlebar/titlebar-640.png) and [960px](v508-titlebar/titlebar-960.png) responsive captures.
- Actual packaged managed engine: [Home](v508-titlebar/engine-home-0.png), [profile after restart](v508-titlebar/engine-profile-1.png), [project](v508-titlebar/engine-home-2.png). The native bridge in these browser captures is simulated.

## Validation

[Machine-readable evidence](v508-titlebar.json) pins all 12 changed production sources and records the exact limits. Each source matches the verified package. The reference archive, frozen styles and protected AI connection/account/grant code match the baseline.

| Check | Result and boundary |
| --- | --- |
| Windows host Release cross-build | 0 warnings, 0 errors; no native execution |
| `tests/probes/app_titlebar_host.py` | 19 geometry/whitelist/state/busy/picker/unsupported cases with FakeForm; original FormClosing source unchanged |
| `tests/probes/user_profile.py` | 22 private-file persistence, revision, bounds/image, corrupt-data and pre-read symlink rejection cases; no account/grant |
| `tests/web/app_titlebar.py` | 10 grouped Chromium checks: original geometry/markup, host command/state simulation, pending/failed Save, duplicate clicks, header replacement, partial rerender, initial-read race, responsive and unsupported presentation |
| `tests/web/native_titlebar_bridge.py` | Exact injected script executes only in the trusted top document; same-origin/remote frames and remote top documents get no bridge. Native source admission/frame/CSP/host-object restrictions audited separately |
| Full generated EditorHome | New profile import/endpoint compiled successfully |
| `tests/web/editor_titlebar.py` with final packaged engine | 7 grouped checks through real profile API, disk save, page reload, process restart, owned project screen and presentation flush; fake window replies, zero page errors/external requests |
| `tests/probes/desktop_package.py` | Windows x64 PE cross-publication, 2,238 files, 51 resources, source integrity, changed-resource/missing-dependency rejection, profile reuse/override, unrelated working directory, managed-engine startup with runtime only and no installed SDK, minimal Login renderer |

The bridge admits only a fixed window-command vocabulary from the current trusted root/index document. It has no arbitrary window handle, process, account or project command. The production host blocks frame navigation, disallows host objects and keeps the existing CSP frame prohibition. The injected-script browser checks are not native WebView2 admission tests, and do not claim that an allowed same-origin iframe could not borrow a parent API. Such frames are prohibited by this host.

The committed-checkout result is recorded after the source commit in the machine-readable evidence. Previously passed connection/consent suites were not repeated: their implementation and guards are unchanged. This is not new evidence of live account or model success.

## Distribution and remaining native checks

The verified distribution is the entire `Builds/Windows-x64` folder. On Windows, open `Builds/Windows-x64/Confectory.exe` and keep the accompanying files together. The previous local package was preserved. Microsoft **.NET Desktop Runtime 10 x64** and **Microsoft Edge WebView2 Runtime** are prerequisites; Confectory does not install them automatically. The SDK is needed for building user projects, not for opening the packaged editor.

This Linux environment did not execute the Windows apphost or WebView2. Actual Windows titlebar removal, interactive drag exclusion, double-click, minimize/maximize/restore, resizing, taskbar/work-area behavior, DPI/multiple monitors, edge snap, Alt+F4 and asynchronous native close/cancel still require Windows QA. The Windows 11 maximize-hover Snap Layout is not implemented or verified here. No user login, credentials, real grants or paid inference were used.
