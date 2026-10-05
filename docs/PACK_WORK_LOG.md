# Pack implementation record

Integration branch: `integration/checkpoint-1`, based on remote main/window-pack `4a7b07df510449c7ec49dc1e657ec94b67dcb752`. Saved Python baseline was clean and preserved on its existing branches. Fetch succeeded. Publication of source/specifications/tests is explicitly authorized; no binaries, images, credentials or original design document are publication candidates.

## Baseline access and environment

Library baseline: `libfile_d19357dd1dc4819188ec627f5187c81d`, `Confectory_엔진_통합_설계_명세_20261005.docx`, version 1, reported 74,257 bytes. Library text extraction reports 39 pages (request described 37). Text excerpts of sections 4–7 and preserved UI/timing/lifetime contracts were read. Full initial read output was truncated: no full-document reading or local byte verification is claimed. Required current materialization helper was obtained; local transfer is blocked by proxy tunnel HTTP 403. This blocker remains to resolve before declaring design-baseline verification complete.

.NET SDK 8.0.425/runtime 8.0.31 installed under `/workspace/toolchains/dotnet-8.0.425`. Set `DOTNET_CLI_HOME` to a writable local directory. X.Org and dummy driver are installed. Android SDK path, adb, sdkmanager and .NET workloads absent; Java 21 present. No tool installation performed. Android compile/APK/runtime coverage is not claimed.

No AGENTS.md or repository .agents/skills found during scoped search. Relevant repository design docs: FORMAT, TECHNICAL_DESIGN, window README. No Golemancer implementation inspected.

## Increment 1: RuntimeBase

Intended/public IDs: `Confectory.RuntimeBase::{CreateOwner,CreateInstance,Read,Write,Subscribe,Poll,Unsubscribe,DisposeOwner}`; independent contracts, matching Body implementation IDs. Scalar consumer-owned model, opaque owner state, owner-scoped instance handles, exact element subscriptions and coherent revision snapshots. Model semantics have no dependency on tables. API and limits documented in pack README.

Outside implementation reads: `src/Confectory.Core/Generation.cs` to verify generated bodies are method-local and providers are reconstructed per call; public FORMAT did not establish where persistent fields could live. `tests/Confectory.Tests/{Program,Support,WindowTests}.cs` for test registration, fixture isolation and native-test conventions; no existing test-framework public contract exists. `src/Confectory.Cli/Program.cs` for executable CLI invocation. Existing window native body read to assess extraction of reusable native capability ownership; its old Open contract does not expose surfaces or events. No outside implementation edits in RuntimeBase itself. Test-runner registration is the required outside test edit.

Rebuild scope: eight new contracts, eight RuntimeBase bodies and test consumer. Core and existing window pack unchanged. Functional gate: generated consumer executable passed 30 lifecycle cycles, independent models, intended subscription updates, equal writes, cross-owner rejection, idempotent release, late events and reopen. Structure/locality gate: declarations use only ID imports, no implementation assembly references; incremental provider-rebuild assertion recorded in regression test.

Commands (from repository root, with DOTNET_CLI_HOME and CONFECTORY_DOTNET set):

```
dotnet build Confectory.sln -c Release
dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/runtime-base/project.cpack portable
```

Use the returned `run` array to execute. Output: `RuntimeBase lifecycle PASS`.

This increment is not [Checkpoint 1]. Remaining milestone: RealTimeUpdate, coherent mixed-input camera snapshots, reusable window/render/input capabilities, BaseUI, composed engine ProjectPack, two-window GUI checks, Android surface/lifecycle counterpart and target verification, checkpoint handoff.
