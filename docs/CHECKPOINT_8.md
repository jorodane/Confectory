# Checkpoint 8: local optional chief-only Augment

Runnable local optional Augment milestone, marked by its [Checkpoint 8] local commit. Baseline is tested local Checkpoint7 76d72c295f542512fa0000003358b65518833dfa; branch integration/checkpoint-8. Remote publication remains blocked by automatic approval review in this execution context. No push, merge, upload or alternate route occurred.

Confectory.Augment is optional: ordinary engine/game consumers do not require it. It borrows matching WorkerTasks and EditWorkspace sessions, owns bounded versioned proposal/selection history, and gates every augmentation power with existing chief-executor authorization. The additive public WorkerTasks.Context query rejects borrowed project/chief mismatch before Task side effects; it returns project/owner/chief, not private Helper memory. Core is unchanged.

A selected Provider supplies exactly three validated cards. Ordinary/directed natural-language reroll, skip, custom prose and target-scoped ExactlyYogi are supported. Two to four tags, idea-deviation rarity and relative effort/risk remain separate. This consumer selects deterministic creative fixtures; no live LLM, external model/image service or quality guarantee is claimed. The default provider explicitly refuses generation. Scoring, tag weights, effort/risk units and permanent retention remain undecided policy, with bounded fail-at-capacity history rather than silent pruning.

Selection creates an ordinary ready Task and preserves rationale; it never changes source or counts as implementation. The first draft adapter supports one existing selected scalar metadata field. Stage updates only the shared draft by revision CAS; Review issues a version-bound token; explicit Confirm uses normal ChangeSet compilation/source CAS. Narrative-only custom ideas require ordinary Task implementation. Source compiler confirmation is not Task/domain completion. The example's separate local Worker adapter reads confirmed source, checks the selected value, validates an actual Harvest instance and uses explicit completion verification. Active implemented tags require a completed linked Task and unchanged confirmed source; stale/deleted source contributes no active tag.

Pending generation/selection/staging/confirmation intent is durable before side effects. Stable command IDs prevent duplicate provider invocation; older completions cannot replace newer cards. Stale/deleted target proposals reject use. Closing cancels/joins owned jobs and preserves borrowed owner lifetimes. Reopen preserves history without reroll or Task replay; unavailable generation is marked interrupted. Staged/confirmed withdrawal requires normal draft/impact/removal work, not card deletion.

## Validation ledger

- Original retained no-filter full regression passed **106/0, 1899.067s** (/tmp/checkpoint8-full-tests.log), including old WorkerTasks supervision and all three Checkpoint7 consumers. No duplicate full run was launched.
- Initial pack and final consumer compilation passed.
- Final strengthened functional/locality run: **2 passed, 0 failed, 210.555s**. The strengthened run additionally checks default-provider refusal, delayed reroll order, pending-command deduplication, completed-tag exclusion on deletion and exact locality. Intermediate corrected run was 2/0, 277.050s before the additional refusal/order gates.
- Actual Linux GUI flow passed repeated reroll/selection-cancel, natural-language direction, skip/custom, scoped ExactlyYogi, Stage/Review/Confirm, real local domain verification, stale/deleted rejection, history reopen and idle SIGINT cleanup. Active-generation SIGINT/recovery passed; final-source compact visual/render/cleanup smoke passed and screenshot was inspected.
- Windows/android named managed net8.0 compilation passed; final-source Linux/windows/android-named profiles all report tool.ok=true and select 82 implementations. No native Windows or APK/runtime acceptance is implied.
- Earlier failed fixture reset, success-phrase assertion and pixel expectation are disclosed in CHECKPOINT_8_WORK_LOG.md; they are not counted as acceptance.

## Reproduce

Use the installed SDK and built host; test runner changes were built without changing Core binaries:

```sh
export CONFECTORY_DOTNET=/workspace/toolchains/dotnet-8.0.425/dotnet
export DOTNET_CLI_HOME=/tmp/confectory-dotnet
export CONFECTORY_ELEMENT_AUTHORING_HOST=/workspace/Confectory/targets/element-authoring/bin/Release/net8.0/Confectory.ElementAuthoring.dll
export DISPLAY=:97
"$CONFECTORY_DOTNET" build tests/Confectory.Tests/Confectory.Tests.csproj -c Release --no-dependencies --no-restore
"$CONFECTORY_DOTNET" tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll Augment
"$CONFECTORY_DOTNET" tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll
"$CONFECTORY_DOTNET" src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/augment/project.cpack linux > /tmp/augment-final-build.json
python3 tests/gui/augment_x11_spotcheck.py /tmp/augment-final-build.json
"$CONFECTORY_DOTNET" src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/augment/project.cpack windows > /tmp/augment-windows-final.json
"$CONFECTORY_DOTNET" src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/augment/project.cpack android > /tmp/augment-android-final.json
```

Native gate owns a private source/history fixture and uses ordinary local Confirm, not the production game source. Interactive instructions are in examples/augment/README.md. Existing public contracts and owning bodies are declared in pack.cpack; per-increment outside reads/edits and actual rebuild scope are in the work log. No binaries, screenshots, secrets or raw chats are tracked.

## Continuing gates

Preserve all REMAINING_GATES_AND_LOCAL_CHAIN.md entries. Windows actual corrected acceptance remains asynchronous. Android is required, but adb/sdkmanager/javac are absent, saved JDK is empty and SDK/license prerequisites remain pending; no installation or license acceptance occurred. Equivalent UI must be one app-owned surface with logical card/history panels, touch identity/cancel and app/surface lifecycle. Native adapter/build provider/APK/runtime remain incomplete.

Next optional Augment work: normal multi-field/code Task proposals and reviewed rejection/retirement/replacement/withdrawal impact history, durable UI recovery and policy retention once specified. Keep a refused default and consumer-selected domain verification; live creative provider integration requires separate authorized service configuration. General widgets/IME/accessibility, Owner transfer/migration, semantic merge, internet collaboration and broad render/physics remain earlier open gates. Mesh/general physics are far-later scope. Publication remains blocked by automatic approval propagation review; no further retry or alternate route.


Exact source/test increments before the documentation marker: cbcc0a281a53cf7fead42abe4c4708a9397ab40a (shared Context), 6406c9e1d6818753993e093447cc0ff47a204839 (Augment), 20fa0cf8600a8b097d6a90754c029967f1eb84a3 (consumer), ccb596caa28ff1da84a51b833b780d446838314b (tests). `git log integration/checkpoint-8` identifies the final [Checkpoint 8] marker. Git working tree is clean after the documentation commit. No Core/target source changes or tracked binary/image artifacts were introduced.
