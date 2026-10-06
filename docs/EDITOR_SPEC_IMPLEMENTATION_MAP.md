# Editor specification mapping before production composition

Authority: full readable design baseline v1, section8 “시작 화면과 프로젝트 화면”, 설계 기준2. The parsed baseline has39 pages; the requested37-page metadata and original DOCX byte materialization remain unresolved. CP13/CP14 Editor is a functional validation consumer. Its current layout is not production design authority. Future production work must compose verified role packs from the specification below; do not expand the temporary screen into an implicit new product design.

| Agreed behavior | Current functional evidence | Remaining production composition |
|---|---|---|
| Logo/title/subtitle sequence, optional Agent connect/later, logo moves top left | Offline functional startup only | Missing intro/transition/connection presentation; optional AI is not a CP14 dependency |
| Left management sidebar and two-column project cards; first card splits New/Open | Basic split New/Open via BaseUI Stack; create/open functional workflow | Temporary geometry; complete card collection, sidebar, icons and responsive constraints |
| Folder selection and valid-project registration | Functional folder browse/open/validation | Production folder presentation and empty/error states |
| Card name/icon/delete/open-folder | Name and selection | Missing icon/delete/open-folder actions |
| Required name focuses error; multiline intent description; no required Main Helper/Agent | Functional create/required focus/description; shared Field and Button | Production content/styling, complete placeholder/focus visual acceptance |
| Collapsible Agent/Helper/Player sidebar and counts/profile overflow | Offline labels/functional consumer context | Missing collapse/count/profile/overflow composition |
| Bottom project chat/log tabs, visible input and meaningful latest log | Execution output log exists | Missing chat/log tab and input composition; do not substitute permanent IDE console |
| Top-left project menu: information/settings/folder/leave | Project/home transitions and metadata | Missing production menu/settings/folder composition |
| Bottom-right circular grievance, run and rounded upward navigation with edge-aware expansion | Functional Run/Stop and screen navigation | Missing grievance/count/urgency and agreed round/expansion geometry |
| No default permanently exposed full IDE panels | Element/source/property tools used to exercise contracts | Temporary integration tooling must remain a test consumer; future Views compose by specification |

Functional workflow and UX fidelity are separate gates. BaseUI Field/Stack and renderer metrics are generic mechanisms; labels/actions/domain validation remain in consumers. No production Editor composition is included in CP14.

## CP15 separate entry/home composition

`examples/editor-home` now composes a fresh `Confectory.EditorHome` ProjectPack from the section8 behavior above. It registers no temporary `Confectory.Editor` or SourceEditor/AI roles. The old consumer remains unchanged. Entry/Home implements offline optional connect/Later presentation, wordmark transition, left management sidebar, two-column project list with split New/Open first card, folder browse/validation, required name focus and multiline intent, create-to-project landing, persistent card metadata/reopen, OS folder action and explicit listing removal. BaseUI adds only a generic Grid; its editor-free consumer is `examples/grid-game`.

Functional acceptance and original visual acceptance remain separate: original logo/subtitle/palette/font/timing assets are absent, so the available text wordmark/action hint are documented functional fallbacks, not approved visual reproduction. Already-connected skip awaits an actual connection-state contract; no provider/account is invented. Listing deletion retains files; destructive project deletion semantics are unresolved. The section8 full project workspace/sidebar/chat/log/grievance/run/upward navigation remains the next slice, not the CP15 landing.

## CP16 bounded project shell

Production EditorHome preserves CP15 entry/home and now composes `Confectory.ProjectShell` for the selected validated project: center workspace, collapsible actual-zero Agent/Helper/Player sidebar, top-left project information/read-only settings/folder/leave menu, bottom chat/log tabs/input/latest meaningful line, and bottom-right current-project Run/Stop. No permanent full IDE panels. New role is usable without EditorHome/ProjectManager/FileStream/AI and cannot open/create/load a project; project identity flows into panel state, exact context is required for every command. No null ProjectContext or chat-driven project opening. Private standalone Helper chat remains its separate optional role per section9, not an emulated live-provider panel.

Offline text is an explicitly local runtime draft, never a sent message or manufactured Helper response. Explicit project reopen restores its own draft/model; switching context uses another borrowed buffer. App restart lists projects without opening any project/chat. Settings are read-only because no editable settings surface is part of this slice. Execution uses current ProjectPack default entry/final source, with no automatic Confirm. New native checks and public-domain tests cover independent context/Run/Stop, menu/tab/capture eligibility, resize, explicit leave/reopen and worker cleanup.

Still separate: actual participant/profile/overflow binding, circular grievance/count/urgency, upward rounded edge-aware internal navigation, editable settings, substantive reusable Element Views in the workspace, original visual identity and native Android storage/text/surface providers. These are not replaced by the temporary editor or invented catalog.

## CP17 original-source audit, separate from functional evidence

The current screenshot can still feel like a test screen. Separate files/pack identity and passing functional tests are not visual/product fidelity evidence. Sections8/12 were re-read during this audit. No wholesale redesign is performed while the minimize fix/native-input migration take priority.

| Current visible item/workflow | Source requirement vs provisional presentation |
|---|---|
| Confectory text wordmark, English subtitle/action hint, fixed intro timings | Logo/subtitle transition required; exact assets/text/timing/color/font are absent. Present wordmark and hint are provisional, not approved reproduction. |
| Agent connection/Later and optional offline use | Explicit source behavior; unavailable-connection panel and repeated Offline/AI-is-optional explanatory copy are provisional status presentation, not a finished connection UX. |
| Collapsible left sidebar, separate Agent/Helper/Player counts | Required. Current plain text counts and Agent button are placeholders; no real profile collection, two-line participant region or overflow View exists. |
| Two-column cards, split New/Open, project title/icon/folder/delete | Required. `P` icon, flat palette/geometry and Previous/Next paging buttons are implementation choices. Delete removes listing only; destructive semantics are unresolved. |
| Required project name and multiline intent with focus/hint | Required. Current custom drawn Field is explicitly rejected by the user's new native-input requirement. Per-screen fields must migrate through shared BaseUI; caret-only tests were insufficient for normal editing/IME acceptance. |
| Internal folder chooser Up/Use folder/Previous/Next/Cancel | Folder selection required; this handcrafted picker layout is provisional and still not native picker presentation. No claim that source specified these buttons. |
| Project title/menu information/settings/folder/leave | Explicit source actions. Current text-only modal, read-only settings and Close menu button are bounded implementation presentation; editable settings surface is missing. |
| Central Workspace title plus project-description text | Source requires working space, not this placeholder. Substantive reusable Element Views/edit spaces are still missing. Description in the canvas is provisional. |
| Bottom Project chat/Logs, recent meaningful line, draft input | Source placement/function required. Keep local draft button, no-Helper explanatory copy and runtime-only draft policy are bounded offline behaviors, not a designed real chat/provider workflow. No actual Helper/Player transport. |
| Run/Stop | Run-current-project required. User identified separate rectangular Run/Stop as test-page carryover; CP17 replaces them with one rounded bubble in the bottom-right, idle Run / active Stop over unchanged execution contracts. Source does not define a detailed stop transition or icon; this state projection is explicit and bounded, not a second permanent control. |
| Circular `?` grievance and unavailable-report explanation | Circle/count/urgency required; `?` glyph, explanatory modal and unavailable state are provisional. Actual report/count/urgency/recipient/Yogi attachment workflow missing; no fabricated values or sends. |
| Navigate launcher and rounded upward bar, edge-aware Project submenu | Shape/upward/edge response required. Workspace/Project chat/Logs/Information/Settings grouping reuses available routes; the complete original editor-space taxonomy is not specified or implemented. Button labels, dimensions, colors and submenu hierarchy are provisional. |
| Footer Working/status text and fixed-pixel page dimensions | Operational feedback/layout implementation, not original visual authority. Native font/DPI/accessibility/theme/safe-area completeness remains absent. |

No full permanent inspector/explorer/console is introduced; this meets a negative requirement but does not establish that the current limited screen faithfully restores the positive design. Shared mechanisms (Button, Stack/Grid, runtime Owner, exact project identity and cancellation) remain reusable functionality; they must not dictate product-specific arrangement. Next changes should use concrete original requirements and user-identified mismatches, preserving functional ownership while replacing provisional presentation deliberately.
