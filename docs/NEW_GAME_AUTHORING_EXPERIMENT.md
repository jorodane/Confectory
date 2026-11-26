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
