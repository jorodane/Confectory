# Owned element navigation, without layout

## Selection and existing capabilities

Design baseline section 3 separates namespace/element identity from physical paths and keeps owned meanings local; section 6 covers concept/schema/object editing. The locally preserved extracted baseline was read for these requirements; original DOCX bytes remain unverified as previously recorded. No AGENTS.md or applicable .agents/skills files were present in the inspected repository/workspace paths.

EditWorkspace already owns stable unit IDs, revisioned drafts, scalar metadata editing, creation and subscriptions. SchemaEditing already exposes Describe/Inspect/Create/Register/SetValue. PackWorkspace already coordinates selection, 32-unit pages, source snapshots, Save and desktop review/Confirm. The actual EditorHome.Model already routes these operations with active-project context checks. They are reused, not duplicated. The missing small connection was an owned-unit navigation query with view-local query state; this increment supplies it without a new page, layout or source model.

## Connect a future layout

Existing public contracts remain:

- `Confectory.PackWorkspace::Open(project, participant, context) -> handle`
- `Confectory.PackWorkspace::Command(handle, operation, payload) -> JSON`
- `Confectory.PackWorkspace::Snapshot(handle) -> JSON`
- `Confectory.PackWorkspace::Close(handle)`

New operation: `filter {query,kind}`. Missing fields reset to empty. `query` is an ordinal case-insensitive substring of the qualified stable unit ID, at most 256 UTF-16 characters. `kind` is an exact, case-sensitive declaration kind (e.g. concept, module, object, function, body), at most 64 characters; unknown kinds yield an empty result. No wildcard or source-content search. Filtering resets page to zero and leaves selected unit, draft and current review unchanged. Invalid filter lengths fail before mutation. Each opaque View handle owns its own filter even when it shares the same draft identity with another View.

Snapshot adds `query`, `kind`, `ownedTotal`. `total` means the filtered count; without filters it retains the prior count. `units` is a stable ordinal-ID-sorted page, at most 32 items. `unit` remains the selected unit even if filtered out: an empty list does not erase an editor's selection or draft. Existing `select {id}`, `page {page}`, revisioned edit, Save and review/Confirm are unchanged. `sources` remains the complete owned source export, unaffected by filters.

Actual product route (no direct private-state access):

```
Confectory.EditorHome.Model::Command(session, "workspace",
  {context: activeProjectContext, action:"filter", query:"::Player", kind:"object"})
```

Read returned `workspace.units` for navigation and `workspace.unit` for the existing editor. Clear via `action:"filter"` with omitted query/kind; select by exact ID using `action:"select", id:...`. The existing active-context guard rejects stale project commands. No coordinates, window dimensions, table-owned models or rendering contracts are involved.

## Locality and limits

This is a navigation projection over the existing **owned draft snapshot**, not the complete design's lazy per-pack semantic graph/index. EditWorkspace Open still eagerly describes owned root files; List returns all owned IDs. Imported registry packs are neither traversed nor editable. ID matching restricts candidates before kind Read calls; kind-only queries inspect owned in-memory unit records, and page output remains bounded. This does not claim constant-time Open, property-schema discovery, inheritance/module graph browsing, namespace relocation, reference migration or asset indexing. Those need their own subsequent increments.

Intended modified elements: `Confectory.PackWorkspace::{CommandBody,SnapshotBody}` and actual consumer `Confectory.EditorHome.Model::CommandBody`. Public function signatures/IDs unchanged; operation/JSON additions are explicitly consumer-tested. Outside implementation reads: EditWorkspace List/Read and README establish stable unit data and eager scope; EditorHome.Model Command and actual VerifyShell establish active-context routing and genuine product integration. Outside edit: EditorHome.Model Command must forward the new query fields because its existing public workspace route only forwarded known action payloads. No Core or platform provider edits. Physical rebuild scope: selected PackWorkspace implementation assembly and EditorHome.Model consumer implementation assembly, followed by final link; contract DLLs are unaffected. Functional and locality checks are separate.

## Verification

Use existing SDK10.0.401 with `DOTNET_CLI_HOME=/tmp/confectory-dotnet10` and `CONFECTORY_DOTNET=/workspace/toolchains/dotnet-10.0.401/dotnet`:

```
$CONFECTORY_DOTNET build Confectory.sln -c Release --no-restore
$CONFECTORY_DOTNET run --project tests/Confectory.Tests -c Release --no-build -- --require-runtime PackWorkspaceTests test_project_shell_domain_isolated_execution_no_null_chat_open_and_context_cleanup test_project_shell_windows_and_android_managed_compile
```

PackWorkspace regressions exercise exact-ID/case/kind matching, empty/reset filters, selected-unit retention, per-view isolation, empty-page clamping and bound rejection alongside existing stale-revision, Save/reopen/review/cancel/cleanup checks. Existing provider-locality gate mutates SnapshotBody and expects only the owning PackWorkspace assembly, with zero contract compilations. Actual EditorHome VerifyShell exercises filter and stale-context refusal through the same EditorHome.Model provider used by Main; its existing consumer-locality gate verifies CommandBody ownership. This is product domain execution, not a new test page or OS visual/device acceptance. Windows/Android gates compile the actual common EditorHome controller; no device/signing/APK claim is made for this layout-free increment.

Recorded results: full solution build passes, zero warnings/errors (6.61s). Four selected regression/integration/target checks pass, zero failed/skipped (108.366s). After extending the owned fixture to 40 objects, the revised PackWorkspace functional/locality check passes again (1/0/0,13.995s), including pages32+8, stable ordering, same-draft different-view filter isolation and unchanged review token/text. Final test-runner build also passes zero warnings/errors. Private logs: /tmp/confectory-owned-navigation-build.log, /tmp/confectory-owned-navigation-tests.log, /tmp/confectory-owned-navigation-pages.log. No tools installed, signatures, native packages, external servers or device runs.
