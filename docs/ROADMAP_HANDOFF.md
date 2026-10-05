# Confectory pack roadmap and handoff

## Local delegated-run handoff (2026-10-05)

Current branch is `integration/checkpoint-3`; fetched origin main has no commits beyond the current local ancestry. Preserve `[Checkpoint 1]` at `73d793fdd9784a447780cc1e01bd7155a3a15370` and `[Checkpoint 2]` at `07ab2d735bf2387f7b3592d36082b08afb50b4f2`. Windows correction is `2a81f43`, evidence `e242ef1`; see WINDOWS_NATIVE_FIX.md. The user's original native Windows failure is not erased by Linux shim coverage: corrected actual Windows acceptance remains pending. Full correction regression suite: 87 passed, zero failed; both real Linux GUI probes and Windows target compilation passed.

FileStream is the first independent Checkpoint 3 foundation. Read CHECKPOINT_3_WORK_LOG.md and packs/file-stream/README.md before extending it. Continue with SchemaEditing, shared participant/project/work-context EditWorkspace, versioned Save/restore, selected ChangeSet validation/Confirm, then reusable ElementView card/table consumers. No editing milestone is complete yet; no source lease participation by ProjectExecution is claimed. Keep UI ownership and data storage independent, and leave drafts intact on conflict.

The user's later explicit authorization permits public source/test/specification pushes and safe main integration, overriding the initial local-only restriction. Never publish binaries/images/secrets/raw chat or original documents. Android APK/runtime remains blocked by missing Google SDK/full JDK and pending explicit SDK license acceptance; original DOCX byte materialization remains proxy-blocked, although the complete official extracted version-1 design text was read.

Start with CHECKPOINT_2.md for project/context/execution workflow and CHECKPOINT_1.md for the runnable engine and exact commands, and PACK_WORK_LOG.md for pack IDs, public contracts, observed outside reads/edits and rebuild scope. Do not resume Golemancer work or revert to the saved Python baseline.

## Current durable state

Checkpoint 1 is preserved at `73d793f`; Checkpoint 2 development follows it on `integration/checkpoint-2`. Reusable ProjectExecution increment `6ca29c7` and ProjectManager increment `285da33` are published with launcher convenience `ff94e25`; the runnable project panel milestone is recorded as [Checkpoint 2]. General CLI run is pack-neutral. Project context, execution handle and native View have separate lifetimes; managers stop their owned workers on final caller disposal.


Integration base: completed Window commit `4a7b07df510449c7ec49dc1e657ec94b67dcb752`, based on independently verified C# core `b750d0d2b06acb738ffca5b442a8d78d4b58aa42`. Local branch is `integration/checkpoint-1`. RuntimeBase increment `ef0d428` and RealTimeUpdate increment `ff9d396` were separately committed and published. Later integration commits add the runnable BaseUI engine, public state accessors and Android preparation. Preserve unrelated local/remote branches and re-fetch before integrating main.

Role ownership: ProjectExecution owns execution capability/session handles and replaceable platform strategy; ProjectManager owns data contexts/active selection; RuntimeBase owns instances/lifetime/subscriptions; RealTimeUpdate owns scheduling/cadence/camera policies; RenderInput owns public requests/events; Window owns native windows/app-surface adapters; BaseUI owns model-to-control behavior/layout/persistent element Views; the engine ProjectPack selects their concrete providers and frame loop. The core resolves/builds these contracts and has no special engine/runtime host.

Full design content was read through 18 bounded official version-1 text reads and reconciled. Consumer-local extraction/evidence are under `/workspace/confectory-design/` outside Git. Original DOCX byte transfer remains blocked by proxy HTTP 403. Do not claim it was verified or bypass access restrictions.

## Next pack-sized work

Next UI/editing stage: typed project data inspection and property editing, local work-copy Save/reopen/Confirm, reusable element/property Views and explicit ownership; no mandatory Helper/multiplayer or fixed engine/editor host. Native Android app execution is an unavailable strategy capability distinct from the Google SDK/JDK setup gaps. Preserve it as an open target gate.


1. Finish Android native target verification once SDK license acceptance is explicitly authorized (development-tool installation is already authorized). Existing source export preserves separate managed artifacts and genuine bindings. Build the SDK project, correct native callback/compiler issues, produce a local debug APK, verify pause/resume, surface/configuration recreation, pointer identity/cancel, pinch/drag and independent logical Views. Implement/verify fixed-step consumer callback coverage and phase failure diagnostics in the native app. Distinguish managed Linux probes, SDK compilation, emulator, device and UX evidence. A source export is not an APK target provider; migrate to a protocol-1 native packaging provider when its build contract is ready.
2. Expand the BaseUI slice into general reusable element Views/typed widgets: text/finite-number/boolean/color/resource/vector properties, explicit Set/Bind/On/Contribute, range/default/slot validation, property-level subscriptions and inheritance provenance. Keep consumer-owned models independent of tables. Add text/IME/edit/focus/scroll state and native font/accessibility/safe-area/DPI adapters with measured local updates. Preserve existing controls and token APIs; make necessary shared-contract additions explicit and consumer-tested.
3. Add runtime Owner hierarchy/transfer, work cancellation and safe-point provider replacement only as explicit pack policies. Preserve old state/version on failure; surface restart-needed cases instead of silently resetting. Model/schema migration is separate from View refresh and DLL loading.
4. Project execution/management are now present; add edit-session/work-copy packs with local Save/reopen and explicit Confirm semantics, then schema/object editing and universal fallback Views. No full editor is included in Checkpoint 1. Keep local drafts, shared originals and View lifetimes separate.
5. Add selected 2D/3D render/scene/input/physics validation packs as actual consumers of RealTimeUpdate and RuntimeBase. Do not hardcode existing 2D defaults as universal 3D contracts. Multiplayer and AI are optional future packs, not prerequisites for UI/timing.
6. Proceed to conceptual navigation, Helper/Task/collaboration, Yogi, augmentation, render authoring and algorithm projection according to the full baseline, as separate coherent increments. Do not add all future editor/AI requirements to the minimal build core.

## Working rules and known limits

For every increment, write intended namespace/element IDs/public contracts first, record actual outside implementation reads/edits and why contracts were insufficient, then record affected rebuild scope. Keep functional and structure/locality gates separate. Provider-only edits must reuse unrelated consumers; shared-contract changes must revalidate/compile affected consumers. Do not equate file splitting or one shared DLL with locality.

All model/control operations are serialized on the UI thread. Current models are scalar, state tokens are opaque, Views use fixed stable render slots, and the current renderer draws rectangles/text. Full widget schemas, general edit sessions, live reload, high-DPI/accessibility completeness, native Wayland and 3D are not claimed. Windows execution and native Android compilation/runtime remain asynchronous/not-run gates until actually exercised.

Public source/specification/test pushes and safe main integration are explicitly authorized. No binaries/images/secrets/raw chat or original documents in Git; no force push/credential changes. User Windows/Android spot checks must not pause independent development. Record failures with exact environment/command/target evidence, fix the owning pack, and continue.
