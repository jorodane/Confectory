# New local game experiment — timing puzzle (v821 continuation)

Baseline: cb283939befa0c91bc376acb0356e595a7623763. The v821 Logic
Code document editor supports creating a new function, authoring a C# cell,
saving its shared draft and reviewing/confirming its owned registration.
The actual new-project experiment uses these existing surfaces, not a
pre-authored game pack or a test-only editor command.

## First missing general authoring capability

The ordinary new project template has a confirmed Main entry. The user can
create and confirm another entry-compatible function, but the old target
picker only selected a target and was not itself a normal visible way to
assign a different project entry. A generic source edit deliberately rejects
ProjectManifest registration changes. A project manager context also stores
its entry at initial open, so merely changing the source would not guarantee
that an already-open project's next default Run selected it.

The visible project menu now has **실행 설정** for runnable local projects.
It connects the existing target selector to an explicit project-entry
choice. A confirmed directly owned, non-inherited function with no inputs
and return int or void can be chosen. This is the existing compiler's
entry-signature contract, not a new game-specific convention. The owning
EditWorkspace operation stages only the entry declaration. It checks
registered identity, source scope, original hash and revision; an unrelated
manifest draft cannot be overwritten. An earlier entry-only draft can be
superseded by another explicit choice. Existing Review shows old/new entry,
and the normal compiler-backed Confirm and source CAS are required before
it changes execution. There is no direct final-source write in the new
selection endpoint.

ProjectManager refreshes the opened context's execution metadata after
successful manifest confirmation and before default Run/Build commands,
checking manifest identity and bytes. The exact manifest hash avoids
repeated description processes when the file has not changed. The explicit
entry argument to the existing manager Launch remains supported. Run uses
the confirmed entry, not a currently selected function or unconfirmed
candidate. No ownership or execution permission is expanded.

## Actual experiment and repeatable regression

`tests/gui/editor_new_game_workflow.py <Linux EditorHome report> [build repository]`
uses the existing Xorg/native file-picker and Chromium transport fixtures,
with a fresh temporary local profile and an empty parent folder:

1. Native GTK Home → new local project **Timing Puzzle** → genuine folder
   picker → first Main Run.
2. Browser editor opens the created project from Recent. ProjectInfo is
   confirmed; an ordinary owned concept object **TimingRules** is created
   and confirmed through the project browser's creation UI.
3. A new **PlayTimingPuzzle** function is created in the function browser.
   Its first v821 logic-code cell is edited in the existing protected C#
   editor, saved and confirmed. The original Main remains the declared
   entry. No project source is written by the test itself.
4. The experimental function evaluates three deterministic sample taps
   (50, 495, 850 ms) against a 500 ms target with 50 ms tolerance. It
   returns success and writes the score (1/3) to an owned fixture result
   file so actual child execution is observable.
5. Project menu → 실행 설정 → new entry → Review cancel:
   confirmed manifest bytes remain identical and actual Run still
   executes Main (no score). Re-Review and Confirm: only the exact
   entry clause changes, the settings display reflects it, and the same
   editor's ordinary Run executes the new game-rule function.
6. Completely new Chromium editor process and native GTK Recent reopen
   both execute the same final entry and produce score 1/3.

`tests/packs/project_entry_authoring.py <ElementAuthoring.dll>` additionally
checks exact byte-preserving entry replacement, int/void eligibility,
wrong return type or input count, wrong kind, foreign/unregistered IDs,
superseding a prior entry-only draft, and refusal to overwrite a separate
manifest edit. This is a parser boundary test, not an alternate editor UI.
The ordinary ProjectManager lifecycle/locality and offline template
integration tests remain relevant regression coverage.

## Scope and next experiment

This is a first engine-authoring vertical slice, **not a playable mouse
timing game yet**. TimingRules is a real created concept object, but its
values are not yet connected to the scoring function. The concrete
remaining work is to author runtime input and presentation through existing
window/frame/input contracts in the local project, configure any required
pack dependencies through a normal visible editor flow, bind rule values
rather than hardcode sample taps, and verify actual player click timing,
score display and replay/reset. The runtime game rules must remain in the
game pack, not Core/EditorHome. Existing inventory/recipe contracts are
unrelated and unchanged. Windows actual runtime and interactive input
were not validated here.

Performance follow-up remains separate: previous confirmed-candidate final
link reuse removes the duplicate link, but path-sensitive implementation
compiles, compiler/tool fingerprints and the first project description
still cost real time. The first default Run in a context may need one
description refresh; later unchanged manifest bytes reuse the already
described entry. No new performance speedup is claimed in this increment.

## Installed runtime pack connection

The fixed Pack Manager tab now offers **설치된 팩 연결** (Connect installed
pack). Select an installed pack by its namespace and use the ordinary
manifest Review/Confirm. This adds a direct dependency and registrations
for its required installed closure, without downloading anything or
silently adding unrelated direct dependencies. Existing conflicting
registrations and unrelated manifest drafts are refused.

In the actual disposable Timing Puzzle editor, canceling Window's review
left the confirmed manifest unchanged. Confirming Window registered its
required RenderInput pack; explicitly connecting RenderInput afterwards
added its direct dependency without a duplicate registration. A cold
Chromium reopen showed both packs and the existing authored entry still
produced score 1. Old entry-only manifest history from the previous
increment is recovered without granting generic manifest Undo authority;
new manifest ownership edits use the established history boundary.

Regression commands (using the lightweight built editor and author host):

- `python tests/packs/project_pack_registration.py <ElementAuthoring.dll> <installed-editor-project.cpack>`
- `python tests/gui/editor_new_game_workflow.py <editor-report.json> <repo>`
- `python tests/web/project_installed_pack_registration.py <editor-report.json> <repo> <disposable-evidence-directory>`

The last command uses the evidence directory printed by the game workflow.
This increment supplies the ordinary dependency selection path, not yet the
runtime window/provider binding, actual mouse timing, score presentation,
or binding TimingRules values to the game function. Windows execution is
not covered by these Linux tests.

## Registered runtime feature calls

The normal existing owned root Logic Code call picker previously queried
only the project itself, even after the installed runtime packs had been
connected. It now also searches directly registered dependency contracts
by the entered name or qualified ID. The registered result is labelled by
its full ID. It uses the existing `readCall` receipt and subsequent save
and compiler validation; it does not read or execute provider bodies to
populate search results. Pending private/preview continuations retain
their existing owned-contract-only boundary.

`python tests/web/project_registered_runtime_call.py <editor-report.json>
<repo> <disposable-evidence-directory>` follows the previous pack connection
test on the disposable project. Actual Chromium search found both
`Confectory.Window::Open` and `Confectory.RenderInput::Pump`. Closing the
search did not add any cells. Selecting the self-provided
`Confectory.Window::TextStyle` added a real typed call, saved, confirmed,
executed the existing score, then survived a cold editor reopen and Run.
The project manifest remained byte-identical. These are ordinary source
and execution paths, not a mock picker.

Window creation and input pumping still require the appropriate provider
binding and session/argument wiring. Neither actual mouse interaction nor
TimingRules value binding is claimed by this increment.

The older registered ABI UI regression reached its read-only receipt check,
but its subsequent hidden overview-node click timed out in both the prior
and new builds. The standalone RegisteredCallTests fixture also stopped on
an existing EditWorkspace provider assembly error. These do not establish
full external-conflict regression coverage for this increment; the same
host receipt/Save/Confirm paths were kept unchanged.

## Explicit runtime provider and first native window

The owned, published function's declaration now has **등록 팩 구현 지정**.
Enter the exact qualified function and implementation IDs. The authoring
host verifies direct registered pack ownership and version, exact matching
function/implementation declarations and signature, and the current
confirmed project and function bytes, without loading provider bodies.
The binding is staged in that function's draft; ordinary Review/Confirm
and compiler validation remain mandatory. An existing different binding
is not silently replaced. The function view shows the declared bindings.

Actual Chromium authored a new `ShowTimingWindow` function, assigned
`Confectory.Window::Open` to `Confectory.Window::Native`, then added the
registered function call and four literal arguments in Logic Code. After
Confirm and choosing the new entry via 실행 설정, the normal ▶ command
created an actual X11 window titled **Timing Puzzle Window** (640×480,
10-second automatic close), and exited successfully. No game source file
was written outside the editor. The runnable game rules from the previous
entry remain present; this is a window/session authoring milestone, not
an interactive timing game.

`tests/packs/registered_function_provider.py <ElementAuthoring.dll> <repo>`
checks exact ownership, wrong/missing providers, and stale input refusal.
`tests/web/project_runtime_window.py <editor-report.json> <repo>
<disposable-evidence-directory>` extends the pack connection experiment
with the actual UI/provider/window path and a cold restart. It requires
the isolated X11 display and xwininfo.

The earlier `v536_registered_call_abi.py` regression now selects Blueprint
view explicitly. A changed external manifest must not qualify as an
unchanged receipt; the test verifies refusal and retained input, restores
only that synthetic competing edit, then verifies cold retry, Review
cancel and Confirm with original registered files unchanged. No host
conflict policy was relaxed. Adopting an unresolved changed external
receipt is not claimed by this test.

Next: persistent surface creation and RenderInput pump/draw provider
bindings, event handling, and referencing actual TimingRules values in
the project function. Windows execution and actual mouse success/failure
are not covered in this step.

## Interactive native input and render loop

The ordinary saved root code cell now offers **기능 참조 추가** (Add function
reference). An explicitly selected existing function adds its canonical
import and contract to that cell, updates its source definition receipt
without changing its C# text, and stages the graph, implementation and
code record together. The cell lists the exact function IDs and generated
aliases that can be called from its native code. Existing source and
registered contract observations, original-file check, atomic draft edit,
and final compile/Review/Confirm remain in use. This is restricted to an
ordinary direct-owned, synchronous saved root code cell; preview, private,
slot, copied and incompatible async/ref/out/branch contracts are excluded.

A new `PlayInteractiveTiming` function was authored entirely through the
normal editor. In its declared function scope, four providers were
explicitly bound: Window.CreateSurfaces, RenderInput.Pump, RenderInput.Draw,
and Window.Close. A code cell then selected those exact four references
and used their editor-displayed aliases in a C# event/render loop. The loop
shows a green **Click now** target and red **Wait** target, alternating
at 1.5 seconds, and changes a separate result panel to **Success** or
**Failure** in response to a real pointer-down event. It closes the native
surface in a `finally` block. These game rules are confined to the
synthetic game's editor-authored C#; no rule was added to the engine.

`tests/web/project_runtime_input.py <editor-report.json> <repo>
<disposable-evidence-directory>` uses the already-connected Timing Puzzle
fixture, actual editor creation and Save/Confirm, actual native X11
window and XTest mouse input. It captures the real screen and verifies
both result colors, then repeats after a cold editor restart. It requires
a dedicated X11 display, libXtst, xwininfo, ImageMagick import and Pillow.
The `--guard-only` mode on the completed disposable project verifies that
a duplicate import and an external competing graph edit are rejected
without changing the implementation or overwriting the external bytes.
The existing registered callable ABI conflict regression also passed.
The competing edit is test-only, not an authoring shortcut.

The TimingRules declaration is still not wired to the authored loop;
timing and geometry currently live as game-local literal values. Reusable
configuration-value binding remains separate. Actual Windows execution
is not covered here.

## Published configuration controls the playable game

A new **프로젝트 객체 참조** action on a confirmed directly owned function
stages an ordinary `use object` relationship to an exact confirmed directly
owned object. It keeps existing function relations and original source,
uses normal Review/Confirm, and refuses another project, an incorrect kind,
missing targets or stale owner/manifest input. The general public linkage
catalog now includes the effective schema contract for each published
object data field. `Confectory.RuntimeBase::ReadDeclaredLong` reads only a
single `long` value in the running project's explicitly linked object,
using the embedded catalog or the official entry-assembly-directory
sidecar (the actual Linux target uses the sidecar). It does not read source
files, editor drafts, an external assembly or a live object instance.
The final build key already includes the catalog content.

The actual editor created two typed fields in the existing TimingRules
object and its generated schema (`PhaseMilliseconds` and `OpenMilliseconds`,
both `long`), connected RuntimeBase through Pack Manager, linked the object
in `PlayInteractiveTiming`, and imported ReadDeclaredLong through the code
cell's normal function reference picker. The authored event/render loop
uses those fields by exact qualified object ID and field name. Two
independently UI-created disposable projects have the same namespace and
IDs; neither uses file-edit shortcuts for game authoring.

Actual Chromium ▶ and X11 observations:

| Confirmed Phase / Open (ms) | Click following first green | Rendered result |
| --- | --- | --- |
| 5000 / 3500 | ~1.77 s | Success (green) |
| 7000 / 1000 | ~1.76 s | Failure (red) |
| 7000 / 1000, cold restart | ~1.79 s | Failure (red) |
| Independent same-ID project, 5000 / 3500 | ~1.76 s | Success (green) |

The function declaration, implementation declaration, graph and node
C# record were byte-identical before and after the two setting changes.
Actual competing external edit of the disposable configuration object was
rejected, retaining the local 8000 input and the external 9000 value; the
fixture-only external edit was restored afterwards. The CLI component test
rejects string and int fields despite the same apparent numeric value,
missing fields, unlinked same-project objects and foreign-project IDs. It
also checks the value-only relink changes the final build key.

### Reproduce from an empty local profile

Use the Linux lightweight editor report and isolated X11 display documented
in the preceding stages. Create fresh disposable projects through the
normal test entry points in order (with the evidence directory emitted by
the first command):

1. `python tests/gui/editor_new_game_workflow.py <report> <repo>`
2. `python tests/web/project_installed_pack_registration.py <report> <repo> <evidence>`
3. `python tests/web/project_runtime_input.py <report> <repo> <evidence>`
4. `python tests/web/project_runtime_configuration.py <report> <repo> <evidence>`

For isolation, repeat steps 1–3 with a second independent profile; execute
step 4 with `--setup-only` before changing the first project's settings,
then with `--isolation-only` after the first project's change. The first
project may be checked with `--guard-only` after its narrow settings run.
Component tests: `tests/packs/owned_function_object_use.py <author-host>`
and `tests/packs/linked_declared_long.py <repo>`. Set CONFECTORY_DOTNET to
the SDK executable, keep X11 isolated and provide xwininfo, ImageMagick
and Pillow as for the native input test. Windows actual execution remains
unverified. This is a small authored experimental game, not a new game
engine-specific rule or a packaged external release.
