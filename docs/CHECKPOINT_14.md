# Checkpoint14 bounded shared Field milestone — local

Preserved public baseline: CP13 831fd45, Windows launcher7f38520, interim CP14 ce217cc on integration/checkpoint-14. Final implementation fixes are local commit f5fcc2a. Further publication/merge is paused. This slice extends role packs and ordinary ProjectPack consumers; no engine/editor host is added to Core.

## Bounded delivered scope

BaseUI owns CreateText/TextInput/TextSnapshot/RefreshText/SelectText/CloseText, measured Field/FieldInput, TextLines and Stack. SourceEditor public IDs stay compatible through adapters and retain authoring Apply/Labels policy. Editor forwards shared frames and owns labels/action/domain validation. Independent examples/field-game registers only BaseUI, UINavigation, RuntimeBase, RealTimeUpdate, Window, RenderInput and DotNet roles; no Editor/SourceEditor/EditWorkspace/ProjectManager/AI dependency enters its selected closure.

RenderInput adds MeasureText and clipped DrawText. Window supplies matching Linux Cairo/Pango and Win32 GDI metrics/painting, Unicode full-run geometry and scalar boundary advances. X11 capture releases on up/focus loss/resize/close; transient NotifyPointer focus transitions do not cancel a valid press. SurfaceDimensions declares its own default provider so legacy Draw/Android consumers need no new binding. Field follows measured geometry changes without recreating buffers/models, preserves horizontal/vertical viewports and maps pointer ranges from the same immutable text frame.

Formatting is consumer/domain policy: the game accepts raw text and JSON integer amount, preserves invalid text and last valid model, and changes only the intended View. No numeric-only widget, table-owned model semantics or duplicated schema validation is added.

## Commands and gate records

Use an existing .NET SDK8; in this workspace CONFECTORY_DOTNET and PATH point to `/workspace/toolchains/dotnet-8.0.425/dotnet`, DOTNET_CLI_HOME to `/tmp/confectory-dotnet`. Linux actual GUI uses an existing Xorg dummy server (:97; isolated supplementary tests :98).

```sh
dotnet build Confectory.sln -c Release
dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/editor/project.cpack linux
dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/field-game/project.cpack linux
# Run each build report's run array; native game additionally needs:
# CONFECTORY_FIELD_GAME_GUI=1 CONFECTORY_FIELD_GAME_TRACE=1
python3 tests/gui/field_game_x11.py /tmp/cp14-field-verified-build.json
python3 tests/gui/editor_x11_workflow.py /tmp/cp14-editor-corrected-build.json
dotnet tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll
dotnet tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll FieldTests test_editor_windows_and_android_managed_target_profiles_are_compile_only
# Separate output avoids rewriting an active full runner:
dotnet build tests/Confectory.Tests/Confectory.Tests.csproj -c Release -p:OutputPath=/workspace/Confectory/.confectory/cp14-affected-runner/
dotnet .confectory/cp14-affected-runner/Confectory.Tests.dll EngineTests FieldTests test_editor_native_designed_create_open_edit_save_review_confirm_run_stop_and_lifetime
```

Functional and structural/locality gates are recorded separately. Linux native Editor workflow and independent Field font/caret pixels, Korean/emoji scalar geometry, click/range replacement, keyboard selection, capture/cancel, full-run scrolling, format rules, resize/reopen and interrupt cleanup passed. Independent Field ran at font scales1 and1.5; this is not OS DPI coverage. Provider-only probes require exactly one owning implementation and zero compiled contracts; excluded authoring/AI closure is checked independently.

The complete124-case run finished123 passed/1 failed in3472.495s (exit1). Its sole failure was the pre-correction Engine cold-font auto-close/cache fixture. The repaired source and stronger no-native-cache-error assertion passed in the final affected run: Engine + actual Editor GUI + independent Field/native/locality/managed targets3 passed/0 failed in601.722s (exit0). All other123 broad cases passed; no known functional failure remains after the repaired-case rerun. This is not a single clean124/0 full-run claim. Earlier Android resolution repair passed1/0 in49.882s; initial affected Field/Editor profiles passed2/0 in522.525s. Functional and structure/locality gates are met for the bounded desktop slice; unsupported native-platform and broader editing capabilities below remain open. See CHECKPOINT_14_WORK_LOG.md for actual outside reads/edits/rebuild scopes and exact repair evidence.

## Limits and next-stage handoff

Existing Windows/Android named managed targets are compilation evidence; Linux Win32 ABI fixture is not native Windows. Native Windows spot checks remain asynchronous. Android workload exists, but JDK/javac, SDK manager and adb are absent; no APK or Android runtime/Field text bridge is claimed or tool installation authorized. Android still requires app-owned native text metrics/draw/font providers, primary-touch/pointer ownership, surface lifecycle and storage/execution strategies. Desktop two-window capabilities are distinct from Android's app surface.

Editing remains scalar-safe rather than complete grapheme/Bidi/IME text handling. Clipboard/undo, preferred-column up/down, Shift-click, multi-touch, accessibility and richer style/DPI/virtualized text remain open. Metrics are bounded to65536 UTF16 units and2048 lines; common grid/canvas/overlay/scroll/split/constraint layout remains future BaseUI work.

CP13/CP14 Editor is a functional validation consumer. Read EDITOR_SPEC_IMPLEMENTATION_MAP.md before production UI composition; the original section8 specification is authority. Typed domain projection/custom Element Views and remaining layout primitives should be implemented as coherent role-pack increments with independent consumers, rather than extending this temporary screen into production design. Existing models/Views remain reusable outside tables. No editor rewrite, optional AI or multiplayer work is included.

Full official design text is readable; original DOCX bytes/page metadata and requested Library screenshot materialization remain blocked. Own native evidence was captured/viewed privately under /tmp and is excluded from Git. No binaries/images/secrets/raw chat logs are committed. See CHECKPOINT_14_WINDOWS_CHECK.md for asynchronous user checks and CHECKPOINT_14_ANDROID_PLAN.md for the app-surface equivalent and exact keyboard/text-provider gaps.
