# Project creation responsiveness and Helper chat space

Baseline: `a99925c4b06988590fba45ab33b4333664fda7df`. This patch fixes the reproduced post-creation input lock and applies the user's narrow exception to the v508 chat layout: remove the persistent response-status strip and enlarge the floating chat surface to approximately 1.25 times its previous width and height. Settings and the broader v508 restoration remain outside this change.

## Reproduced creation defect

The isolated native-contract fixture created the real project files and assigned an Agent-owned Main Helper, but the new screen retained `#app.inert=true` with no modal left in `#overlays`. Native creation itself returned in 1,130 ms in that run. This was a permanent browser-input lock after completed work, not evidence of continuing model inference or a game build. The user's actual Windows execution has not been reproduced.

The shared modal function set `inert` on opening and restored it only in its close callback. The project transition cleared the modal DOM directly. Helper assignment then changed the view's Helper scope; the correct transport scope guard rejected the old view, so the original creation callback never reached its final close operation. The browser and outer native window have separate input handling, so the reported ability to close the window does not prove the native UI thread was unblocked.

Modal ownership now has an idempotent disposal callback. A replacement or project/Home transition disposes the old modal before removing its DOM. A stale close callback cannot remove a newer modal or release its input lock. Closing also restores the prior `inert` value rather than indiscriminately setting it to false; an independently owned pre-existing lock remains intact. The existing layouts, focus handling and conditional permission dialogs are retained.

Native creation returns the already-public opaque project ID with its acceptance receipt. The UI binds subsequent work to that project. After Helper assignment changes scope, it remounts and verifies the exact project, Main Helper and Helper order before completing. It does not replay creation or an uncertain assignment, remove the created project, or disable the scope guard. Missing or unexpected receipts remain failures.

Creation performs folder/name validation, writes an atomic staged project template, describes/opens its project and workspace metadata, saves the local ProjectInfo draft, registers its listing, opens the semantic workspace and assigns a registered Agent-owned Helper. This path does not request a model answer, install/login an Agent or build/run the game.

## Requested chat change

The `data-helper-ai-status` paragraph and its updater are removed from the floating chat. Success, idle and sending status no longer reserve a header row. Streamed messages, safe inline errors, retry, cancel/stop and draft/history behavior remain in their existing controls. The freed row and the additional window height go to the scrollable message area.

Measured at 1440 × 1000 with the same owned fixture and single-line description:

| Measurement | Before | After |
|---|---:|---:|
| Floating width | 450 px | 562.5 px |
| Floating height | 351.58 px | 439.5 px |
| Message height | 108 px | 230.31 px |
| Description-to-body gap | 50.39 px | 16 px |
| Send button | 70.17 × 42 px | 70.17 × 42 px |
| Input/button font size | 16 px | 16 px |

The full chat is capped to the available viewport with a 12 px inset, including resize and restored positions. At very short viewport heights the message area shrinks while the input and Send controls stay inside the window. Compact pinned characters retain their existing dimensions. No font/control scaling or settings redesign is introduced.

Actual rendered screenshots: [before](chat-space-create/chat-before.png), [after](chat-space-create/chat-after.png), [375 × 667](chat-space-create/chat-375x667.png), [667 × 375](chat-space-create/chat-667x375.png), [320 × 240](chat-space-create/chat-320x240.png), [error/retry](chat-space-create/chat-error-retry.png), [created project](chat-space-create/create-after.png), and [both retained projects](chat-space-create/created-projects-home.png). The [blocked-before screenshot](chat-space-create/create-blocked-before.png) accompanies the instrumented `inert` assertion; the visual image alone cannot prove input blocking.

## Validation and boundaries

The [JSON record](chat-space-create.json) retains exact source hashes, measurements and fixture results. Completed checks include:

- Actual production native creation contract, with only the parent-selection boundary supplied by an isolated loopback fixture: automatic Main Helper, explicitly selected existing Helper without duplication, post-create hover/click navigation, duplicate destination failure, native cancellation, visible usable failure modal, project/Home cleanup, nested/replaced modals, stale close callbacks and preservation of independently owned `inert` state. Two projects were created under a private temporary directory; a duplicate and cancelled creation produced no additional project or Helper.
- Final native creation requests returned in 1,126 and 1,092 ms in the isolated environment. These timings are not Windows performance guarantees. The fixture-specific native HTTP route is not added to the product's browser host or public endpoint allowlist.
- Focused actual chat layout/responsive tests at 1440 × 1000, 900 × 760, 600 × 800, 375 × 667, 667 × 375 and 320 × 240; unchanged button/font dimensions, absent status DOM/space, real owned HTTP reply/error/retry and reopen draft/history preservation. Transient toast capture uses the unchanged CSP and waits for its normal dismissal.
- Existing actual global Helper regression: Korean IME, Enter/Shift+Enter, accepted input clearing, sending/cancel/retry, two-Helper isolation, draft conflicts, history and cold restart. Existing project/pinned/worker approval and unsent-input cold recovery passed with the larger chat surface; their original behavioral assertions remain.
- Three backend project-manager/engine-creation checks passed, including atomic creation, desktop-buildable offline template, context/provider locality and explicit local confirmation/scope retirement.
- Release solution build: zero warnings/errors. Windows x64 distribution cross-published; composition, 50 resources, unrelated-working-directory runtime-only startup, owned profile preservation, tamper/missing dependency rejection and exact byte comparison of all five changed runtime source files passed.

Original v508 ZIP, Android, main and real user data/accounts are preserved. No real login, credential access or paid model request was performed. All provider/project fixtures are isolated. Native Windows FolderBrowserDialog, WebView2 input/rendering and actual double-click responsiveness remain untested; passing the shared production UI/native contract on Linux does not prove the user's Windows symptom is fully resolved. No whole-suite or broad v508 restoration claim is made.

Windows output: `Builds/Windows-x64/Confectory.exe`. Keep the entire output folder together. Microsoft .NET Desktop Runtime 10 x64 and WebView2 Runtime are prerequisites; this work does not install them on the user's computer.
