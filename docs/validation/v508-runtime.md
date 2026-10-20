# v508 runtime presentation and Agent-owned Helpers

The previous `744463b` runtime still loaded the older consumer presentation despite retaining the v508 ZIP. This change replaces the runtime entry and the startup, Home, participant sidebar, Helper form and project-creation presentation with source-derived v508 views. Real engine controllers continue to own editing, drafts, Review/Confirm, Blueprint, tasks, Workspace and execution.

## Source and entry

- Reference: `reference/site-ui/Confectory-Editor-Prototype-v508.zip`, SHA-256 `b306ce4deff9616c4107ae224443d864f8fce0f52cf3c3e158de8745c17c659f`.
- Full `ui/style.css`: 325,710 bytes, byte-identical to the original v508 stylesheet; SHA-256 `f5b0be01e7daccef55d3aabcf2d33f9b887caee7b6f40c8d49cd46e7347a2700`.
- Normal Windows entry remains `Confectory.bat -> scripts/windows/launcher.ps1 -Action editor -> examples/editor-home/project.cpack -> Main.csbody -> WebStart.csbody -> WebBundle.csbody`.
- The bundle now loads `ui/index.html -> app.js -> v508-runtime.js -> v508-views.js`, plus the full v508 stylesheet and separate `runtime.css` integration rules. All 50 resources are pinned by the bundle.
- The prototype's demo database, fake installs, account states, generated portraits and mock provider replies do not supply production state. Actual controllers replace prototype mutations. The original ZIP is unchanged.

## Resulting behavior

The sidebar lists registered Agent configurations and their owned Helpers. Registration does not imply authentication or live connection. Offline state is separate, retains configuration and Helpers, and blocks new requests. New creation, import and legacy recruitment require a registered Agent. Existing unassigned Helper data stays on disk and is offered through explicit import.

The Helper form retains the source artwork slots, Agent picker, identity fields and modal geometry. Unsupported image/random generation is disabled. Closing the form preserves input. Import and real creation use the existing Helper store; no placeholder Codex owner or assign-later option is inserted.

Agent registration uses the actual provider schema and existing setup/preflight actions. External ChatGPT/MCP connection has its own settings entry. Registration has no project scope grant. An explicit project Helper roster defines internal access, and session conversation selection is separate from durable Main Helper delegation. Dispatch rechecks current registration, configuration and offline state. A newly created Main Helper can own local proposals; its task storage is separated by Helper identity while legacy main-helper storage remains intact.

Responses opens successfully in the fresh Linux host. An owned moved-checkout fixture reproduces stale generated registry paths causing settings/schema failure. Matching generated manifests with a consistent missing old checkout root can be repaired using current authoritative paths; the previous manifest is backed up and `Settings.celem` bytes are preserved. Existing custom/valid registry paths and structurally different manifests are not rewritten. This reproduced case does not establish the cause of the user's Windows error.

Routine Home-save messages are hidden. Errors and explicit action results remain. Global transmission review preserves the conversation/input, and history is scrollable within the viewport. Engine windows emit the source stylesheet's placed-state class. The actual authoring toolbar scrolls horizontally within its row so controls cannot overlap the Blueprint overview. Project tools remain accessible from the project title menu.

## Verification

| Check | Result |
| --- | --- |
| Affected aggregate: embedded/relay boundaries, engine-only creation, global Helper model/UI, setup diagnostics/retry, Workspace invariants and WebUI lifetime/scope | 19 passed, 0 failed, 0 skipped |
| Blueprint edit/Review/Confirm/cold input; v508 overview camera/scope/cancel/cold; v508 rename/IME/CAS/cold | 3 passed, 0 failed, 0 skipped after the placement/toolbar fixes |
| Enhanced global model regression including a newly created Main Helper owning real local proposals | Passed; owned HTTP/stdio fixtures only |
| Final global Chromium flow after the last sidebar change | Passed; 4 owned HTTP requests, 0 external calls, 0 page errors; cancellation/history CAS and cold drafts preserved |
| Existing WorkerTasks supervision/recovery and Augment chief/draft/verification/locality | Passed |
| Project shell domain isolation, execution, no null chat/open and context cleanup | Passed |
| Final Linux and Windows target compilation | `tool.ok=true`, no diagnostics |
| Source/runtime rendered comparison | 7 screens at 1440×1000, 900×760 and 600×800; 44 PNGs including narrow project footers; no horizontal overflow or page errors |
| JavaScript/Python syntax and `git diff --check` | Passed |
| Ordinary Git checkout/resource startup | Passed: 50 resources, retained CRLF after pull, fresh LF, content/encoding/BOM/binary/budget rejection; original bytes retained |

The rendered comparison captures the original prototype in an isolated browser and the ordinary production host with owned temporary storage. Both use fallback fonts: the original Google Fonts request is blocked by the fixture and the production host retains its existing resource security policy. Dialog widths are compared and the narrow footer is reached by scrolling. Screenshots were visually inspected; these checks do not assert pixel equivalence across data or functionality that differs.

Expected visible differences are registered configurations instead of seeded Agents/users/news; two real adapters instead of prototype mock adapters/versions; disabled generation without a real contract; explicit Helper import; and actual native folder tickets/available starter pack instead of fake paths and recommendations. The web fixture cannot show a native folder picker.

No real account login, new credential, paid inference request, external connector scope grant or user project was created. Native Windows CMD/WebView execution and the exact user-PC Responses error remain unverified on this Linux executor. The entire repository test suite was not run; the table identifies the affected checks actually executed. Main, original ZIPs and Android settings were not edited.

Implementation commit: `60d573b904525855eea082fd015df0ded581f806`. The separate receipt records final resource keys and checkout results. The local deliverables are `Confectory-v508-runtime-comparison.html` and `Confectory-v508-runtime-screenshots.zip`. Library delivery failed at the supported upload helper's connection step before any upload result; no new screenshot Library IDs are claimed.
