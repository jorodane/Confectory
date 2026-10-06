# Checkpoint 12: bounded Rig authoring and optional Navigation

Integration branch preserves CP11 a0f77a4 and the SDK8 compatibility fix b017085. RigMotion/RenderAuthoring source increment 0cfc96c; reusable preview/workspace consumers 95c6e44. Navigation source increment 6ada6ab, engine regression fixture correction cebdc82. Navigation has an isolated branch based on b017085, preserving separation from optional Rig work. Checkpoint marker and final regression evidence will be added only after the frozen run succeeds.

## Delivered behavior

Dependency-free RigMotion validates/evaluates complete 3D joint hierarchy and quaternion/translation/scale KeyPoses with duration/Bezier AnimationDeltas; one common Motion pose supports coherent front/side/top preview output. RenderAuthoring preserves Category inheritance/style/rules/base Action meaning/common Rig, Object expression/reference, optional Concept directional/structural harness, Phenotype and grouped layer order/visibility. Geometric fixtures are deliberately bounded; no production generation/skinning/Mesh claim.

Ordinary preview ProjectPack works independently of Stage/Physics/Helper. The authoring consumer borrows workspace-owned documents and keeps two independent RuntimeBase View Owners/time/projection states. Hierarchy, KeyPose, duration and layer changes are validated through composition; Save persists draft without changing final source; reload retains windows; Confirm performs actual source/build acceptance. A scoped background job keeps coherent cached presentation responsive and cancels/joins on interruption. Closing one View unsubscribes its token and releases its whole native session; another View continues. Models do not belong to a table.

Optional UINavigation has no BaseUI/OS dependency. Consumer-configured bindings/groups own traversal, priority/consumption, release activation and focus restoration through public requests. BaseUI adds only Focus/Activate primitives and removes unconditional Tab traversal; engine explicitly composes demo Tab traversal. Inventory demonstration binds higher-priority Tab toggle and independent F6 traversal, including Win32/X11 key codes. Same-event dedup/repeat cannot toggle twice. Source-editor text routing precedes demo navigation; text/modifier permission is explicit. This is not semantic element search or a full widget/IME framework.

## Gates and limits

Actual Linux X11: standalone motion pixels/pause/scrub/persistent window/close; two independent front/side Views, H/P/D/L/O authored changes, layer visibility, Save/reload with stable XIDs, actual Confirm with continuing frames, selected close, reopen, SIGINT during scoped Confirm and Owner/session cleanup. Captures were inspected locally under /tmp and are not in Git. Navigation actual Tab open/close/F6, independent two-window groups, text gating and cleanup pass. Existing engine native click/outside-release/autorepeat/resize/mixed camera/close/reopen/SIGINT flow passes after Navigation composition.

Functional tests are distinct from locality: analytic hierarchy/quaternion/duration/Bezier/projection/inheritance/invalid-domain; actual workspace persistence/Confirm/independent drafts and subscriptions. Private policy edits compile only RigMotion::CommandBody, RenderAuthoring::CommandBody or UINavigation::RouteBody respectively, with zero contracts. They are declared owning policy boundaries, not claims that wrapper APIs have independent semantics.

Windows/android-named verify/preview/workbench and Navigation manifests compile through installed SDK8/net8 Portable providers. These are managed contract checks, not native Windows acceptance or an Android APK. User-reported prior Windows window/button/focus acceptance is recorded separately; new Rig/Navigation native Windows is unrun here. Android workload 34.0.43/8.0.100 exists, but adb/sdkmanager/javac are absent and selected JDK directory is empty. No prerequisite installation or license acceptance occurred. Desktop consumers explicitly require native windows; Android still needs app-owned surface/touch/lifecycle integration, logical Views and packaging/runtime checks.

Original full Library text is readable and was read, including render design section15. Original DOCX materialization remains blocked by proxy403; original bytes/page count are not claimed verified. Refer to the increment ledger for actual outside reads and reasons.

## Reproduce locally

```sh
export CONFECTORY_DOTNET=/workspace/toolchains/dotnet-8.0.425/dotnet
export DOTNET_CLI_HOME=/tmp/confectory-dotnet
export CONFECTORY_ELEMENT_AUTHORING_HOST=/workspace/Confectory/targets/element-authoring/bin/Release/net8.0/Confectory.ElementAuthoring.dll
"$CONFECTORY_DOTNET" build Confectory.sln -c Release --no-restore
"$CONFECTORY_DOTNET" tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll
"$CONFECTORY_DOTNET" src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/rig-lab/preview.cpack linux > /tmp/rig-preview.json
"$CONFECTORY_DOTNET" src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/rig-lab/workbench.cpack linux > /tmp/rig-workbench.json
DISPLAY=:97 python tests/gui/rig_x11_spotcheck.py /tmp/rig-preview.json /tmp/rig-workbench.json
python tests/packs/rig_render_locality.py
"$CONFECTORY_DOTNET" src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/ui-navigation/gui.cpack linux > /tmp/navigation.json
DISPLAY=:97 python tests/gui/navigation_x11_spotcheck.py /tmp/navigation.json
```

The GUI harness creates an explicitly owned temporary asset project. Interactive Rig use requires an owned project copy and the host environment; see [consumer instructions](../examples/rig-lab/README.md). Navigation GUI uses Tab/F6/Enter/T/Q. Windows can use target windows and the returned launcher with installed SDK8; no downgrade/removal of existing SDK10 is required. Existing global.json selects SDK8 locally. Exact asynchronous PowerShell actions are in [Windows checks](CHECKPOINT_12_WINDOWS_CHECK.md).

## Next stage

Prioritize the [usable Editor ProjectPack composition](NEXT_EDITOR_COMPOSITION.md): explicit open/create project → element/property/source edit → save draft/reload → review selected changes/Confirm → run/stop/status. Reuse the intended specification and current public capabilities; remove environment-only/shortcut-only entry gaps through visible scoped actions. This is the smallest next integrated milestone, not restoration of the whole designed editor. Do not stack further optional feature packs ahead of this real-device integration gate. Windows spot checks remain asynchronous, with native unknowns explicit; Android remains an open required target rather than a blocker to a useful desktop editor. Semantic entry-point discovery is a later separate roadmap item. No main merge, force push, binaries, images, secrets or raw chats.
