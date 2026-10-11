# Restore the original v196 screen before connecting actions

The user's Windows Home screenshot matches the separate `drawHome` renderer at 52bd307. It is not evidence of a stylesheet load failure. Git history introduces this renderer in 9e5b282; subsequent changes extend it. The history does not establish a direct copy of an older test layout. That implementation replaced the original `showHome`/`enterProject` presentation with a function-oriented consumer and reused the original stylesheet. This did not satisfy the requested screen-first integration.

This increment restores the frozen ZIP's Home and project frame, then attaches existing engine actions at their original locations. Reference: `reference/site-ui/Confectory-Editor-Prototype-v196.zip`, SHA-256 `02d4824e92ed0edbb43113659982b37a99a614117652bde4d8ac92367e334e34`. No current live Site was consulted or changed.

| Original presentation | Restoration / actual connection |
| --- | --- |
| `showHome`, heading/count, `home-grid` | Original DOM template with actual persisted project IDs/title/description. No inline development toolbar, Reconnect or base-page Ready label. |
| Two creation/open tiles and project card icon/menu/stats | Original card structure. Enter goes through `openProject`; card menu uses the original context-menu structure. Unavailable statistics show a dash rather than demo counts. |
| `createProject` modal | Original form, location preview, Helper/Agent fields and pack details. Existing creation action remains engine-owned. Unsupported initial membership/pack recommendation controls remain disabled in their original positions. |
| Original folder-selection flow | Windows selects the existing project folder. New-project parent selection returns an opaque token plus display label; only the host retains the selected path. Creation uses the existing native `create-project` contract. Old combined picker/create calls still work. Cancel creates nothing; unknown tokens are rejected. |
| `participantSidebarMarkup` / section icons / resize / settings | Shared Home/project sidebar, original section/drawer DOM, original resize and settings functions, actual public Helper/connection identities and counts. Startup reads existing Helper metadata; the original Agent action reads the available connection catalog. No demo people, account dispatch or fabricated Agent ownership. |
| `enterProject`, workspace, Dock, chat bar | Original project frame and Dock SVG/buttons, original main-column placement, chat resize and single Send form. Blur/hide saves the existing project chat draft; Send opens the existing permission review. Browser/Yogi/augmentation/build/run route to existing functions. No automatically opened development browser/schema on entering the frame. |
| Project hide and close | Existing `leaveProject` keeps work running. Windows full-close confirmation and engine cleanup are unchanged. |

The ordinary browser host now permits inline **styles**, matching the embedded Windows host, because the original DOM uses them. Inline scripts remain disallowed. No compiler acceptance, ProjectPack-specific build exception, model ownership, draft, Save/Review/Confirm, CRLF policy, launcher configuration, main or Android version change is introduced.

## Acceptance boundaries

`tests/web/editor_home_original_layout.py` renders the frozen reference and the ordinary actual EditorHome ProjectPack at 1440×1000. It captures both Home/project/create screens, compares major Home DOM structures, checks the two original tiles/card regions and inline styling, then opens a real regular ButtonGame object, views its actual schema, saves a chat draft, hides the project and reopens it. It uses the normal transport; no fake successful engine or UI-only fixture pack is supplied. It also enters the actual AI settings schema through the original Agent dialog, covering the polling/disposal scope transition. It is registered as `test_actual_editor_original_v196_home_project_and_create_flow`.

The Windows Git-checkout gate distinguishes intentional new UI content from retained, unchanged assets; after pull it still checks all original bytes remain unchanged by serving and rejects every prior encoding/content/binary/budget case.

The existing full WebUI regression is adjusted to navigate the original participant/Dock/menu locations instead of removed development buttons. It retains domain draft, independent view, semantic/schema authoring, Review/Confirm, scope/private-data, Yogi, Helper and approval assertions. The generic ButtonGame Reconnect test remains; an editor reconnect assertion uses independent transport mounting/domain draft inspection instead of exposing a diagnostic button in product Home.

This is the first restoration increment, not complete original-screen acceptance. The semantic browser/schema/Review/augmentation/Yogi and Helper management content still contains the earlier consumer forms; their original inner DOM and complete popup flows require a subsequent port. Original Helper expanded/pinned card interactions and complete grouping/portrait metadata are not fully restored. Global Helper Talk, coworker operations and unavailable initial pack/membership actions are not represented as successful. Last-edit/pack/object card metadata and original offline font assets remain incomplete. Linux native UI is a separate existing renderer, preserved and regression-tested; it is not claimed to visually match the v196 HTML. Actual Windows `Confectory.bat`/WebView runtime and Android device execution cannot be performed from this Linux environment.

## Evidence from the restored frame

Reference/consumer pairs at the same 1440×1000 viewport:

- [Original Home](evidence/v196-restoration/original-home.png) / [actual Home](evidence/v196-restoration/consumer-home.png)
- [Original project](evidence/v196-restoration/original-project.png) / [actual project](evidence/v196-restoration/consumer-project.png)
- [Original create modal](evidence/v196-restoration/original-create.png) / [actual create modal](evidence/v196-restoration/consumer-create.png)
- [Actual settings schema opened from Agent](evidence/v196-restoration/consumer-settings.png)

The Home heading, two action tiles, project-card shell, project workspace/Dock and single chat compose form preserve the original presentation. Actual names, missing metadata dashes, available participant identities and disabled unsupported actions differ intentionally from the reference's demo data. This visual comparison is separate from domain/function regression acceptance. In particular the captured settings schema still demonstrates the unported inner consumer form; it is not presented as an original schema-window port.

## Validation of this increment

The registered original-frame gate passed (1/0/0, 47.189s), the full actual editor Chromium regression passed, and generic ButtonGame Chromium and native Linux Entry/Home X11 regressions passed. Final ordinary EditorHome ProjectPack Linux/browser WASM/Windows/Android builds all returned `tool.ok=true`; the Windows WebView host compiled with zero warnings/errors. These are function/build results, separate from the capture comparison above. Real Windows and Android runtime remains unverified.

The actual Windows Git CRLF checkout/resource startup gate passed after committing the restored UI: 1 passed, 0 failed, 0 skipped (13.077s). Unchanged retained assets, changed UI resource identities, canonical served bytes and prior encoding/content/binary/budget rejection cases were verified. The paused workspace's 18 recorded files and HEAD were rechecked unchanged; main and Android version configuration were preserved.
