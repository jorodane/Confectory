# Checkpoint 3 pack work ledger

Base: preserved published 07ab2d7. Remote fetched, no newer main work; integration/checkpoint-3 dedicated branch. Full baseline version-1 text already verified/read (18 bounded Library chunks); relevant schema/View/lifetime/Save/Confirm/table sections reread locally. Original DOCX bytes remain proxy-blocked. Latest requirements supplement this baseline. Google explicit SDK license acceptance remains pending; no APK/app-launch/JDK claims.

## Increment design: FileStream

Intended IDs Confectory.FileStream::{Snapshot,WriteAtomic,LeasePath,Commit,CopySources,Capabilities}. IO only: exact byte hash/readable text, atomic local writes, root-constrained compare-and-swap batch with rollback, explicit shared source lease, source-copy preparation. Android uses same IDs/common app-private IO with an explicit capability variant, not forced connector pairs. No schema/edit/model policy in this pack. Functional gates: missing/read/write, rollback/conflict/no overwrite, symlink/root escape/read-only, source copy isolation. Structure gate: provider-only Snapshot rebuild; IO separate from Save semantics.

## Planned coherent increments

1. FileStream reusable IO and tested shared lease contract.
2. SchemaEditing owned declarations/typed scalar authoring and validation using existing public parser/compiler APIs; no core edit. Preserve category/concept/function/module/object signatures, inheritance/default/binding/module rules through real candidate validation.
3. EditWorkspace shared participant/project/work-context drafts with element identity and narrow revisions/subscriptions. Multiple Views borrow the same session; different users remain independent. Opening/closing a View does not change source or acquire a data lock.
4. Save versioned local-diff state/restore, ChangeSet selected review/conflict/Confirm. Save never changes final files. Confirm validates selected candidate, compares true selected baselines and preserves drafts on conflict/failure; unrelated files/metadata do not invalidate an independent body edit.
5. ElementView reusable outside tables, card/table/aggregate bindings to shared element IDs/session; persistent View state and local redraw. Composed engine UI create/edit, preview build/run, Save/restore, selective Confirm/conflict demonstration. Preserve A/B controls.

Every increment records actual outside implementation reads/edits, why existing contracts were insufficient, affected rebuild scope and separate functional/structure outcomes. This delegated run permits local commits only; no push, publication or merge. No generated binaries/images/secrets/raw documents in Git. RenderMeshGeneration remains far later.

### FileStream implementation evidence

Read outside this pack: existing public pack syntax and test fixture/build/result helpers to create an ordinary consumer; existing public compiler APIs were inspected for the next SchemaEditing increment, with no compiler edits. Edited outside this pack: test runner registration and the new example/test/documents only. Existing packs do not expose local source snapshots, owned-file conditional commit or candidate source-copy contracts, so this is a separate IO pack rather than added core policy. No existing provider implementation was changed.

Affected rebuild scope: new FileStream public contracts/providers plus its new consumer. A Snapshot-only body change must recompile SnapshotBody alone, with zero contract compiles; Android Capabilities selects its target-specific body. Functional IO checks and rebuild-locality checks are separate assertions in FileStreamTests.

Commit's cooperative lease coordinates participating consumers; it does not lock arbitrary external editors. Selected hashes compare exact bytes; each rollback image and its compared hash come from one read. Single-file replacement is atomic. Batch rollback can fail and reports all errors; this is not a crash-proof multi-file filesystem transaction. ProjectExecution does not yet participate in this lease. Save, EditWorkspace, ChangeSet and UI integration remain future increments, so this commit does not mark Checkpoint 3 complete.

Final increment verification: `DOTNET_CLI_HOME=/tmp/confectory-dotnet CONFECTORY_DOTNET=/workspace/toolchains/dotnet-8.0.425/dotnet /workspace/toolchains/dotnet-8.0.425/dotnet build Confectory.sln -c Release --no-restore` succeeded with zero warnings/errors. The same environment running `dotnet tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll FileStreamTests` passed 1/1 in 20.761 seconds on final sources, including lease symlink rejection, actual rollback, provider locality and managed Android selection. Existing full Windows-correction regression evidence remains 87/87; this new isolated increment did not edit existing provider bodies. `git diff --check` passed. No push or external sharing performed during this delegated run.
