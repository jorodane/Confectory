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
