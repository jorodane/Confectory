# Selected draft: direct inheritance and module relations

This follows owned-element-navigation without any layout work. Baseline sections 2–3 define single-parent inheritance, module registration/inclusion, required functions, default and explicit providers as qualified identities. Core already parses these declarations. Existing SchemaEditing Inspect returned parent and scalar metadata but omitted the module/provider relationships. The missing function is a read-only projection, not a second resolver or source model.

## Public replies and usage

`Confectory.SchemaEditing::Inspect(string text) -> string` keeps its signature and existing fields. Its additive `relations` object is:

```
{"scope":"declared","owner":"App::Rules","edges":[
 {"role":"default","target":"Provider::Body","function":"Api::Function"},
 {"role":"include","target":"App::Child","function":null},
 {"role":"module","target":"App::Role","function":null},
 {"role":"parent","target":"App::Parent","function":null},
 {"role":"provide","target":"Provider::Explicit","function":"Api::Function"},
 {"role":"require","target":"Api::Function","function":null}
]}
```

Only actually declared edges are returned, sorted ordinally by role/target/function; empty declarations return empty edges. Defaults/provides relate a function ID to an implementation ID. Parent/module/include/require target IDs remain qualified. Direct declarations can reference missing/unloaded targets: inspection never resolves those targets or compiles/runs their code. It does not describe inherited effective values, chosen implementations, signature satisfaction, conflicts or transitive graphs. Existing parent/signature/values fields remain unchanged. Desktop's existing extra editor metadata is retained; relation responses themselves match Android/browser exactly.

`Confectory.PackWorkspace::Command(handle,"inspect","{}")` returns the ordinary selected workspace snapshot plus `inspection` (the Inspect reply) and `inspectionRevision` (selected draft revision). It reads current draft text using public Read under the workspace operation lock. It does not edit, Save, Confirm, change selection, filter or review. No selection, project/pack manifest and implementation body units are rejected with an explicit declaration-required error. Malformed draft declarations propagate the existing parser diagnostic; there is no cached old inspection. Inspection is request-specific: callers request it again after an edit; ordinary Snapshot/filter responses do not retain stale inspection fields.

Actual product entry:

```
Confectory.EditorHome.Model::Command(session,"workspace",
  {context: activeProjectContext,action:"select",id:"App::Rules"})
Confectory.EditorHome.Model::Command(session,"workspace",
  {context: activeProjectContext,action:"inspect"})
```

Consume `workspace.inspection.relations` independently of any table or layout. Existing stale-context guard and model error reporting apply. Future layout can bind this data without coordinates, native window structure or renderer changes.

## Increment ledger

Modified elements: PackWorkspace CommandBody (new public SchemaEditing Inspect import); SchemaEditing Inspect's target-owned Call replies; actual EditorHome VerifyShell consumer exercise. Function signatures and core are unchanged. PackWorkspace manifest already declares SchemaEditing dependency, and actual EditorHome bindings already provide InspectBody. No new pack or duplicated edit/review/Confirm/Run flow.

Outside implementation reads: Core public Element declarations/Parser fields establish exact direct-declaration representation; desktop element-authoring Inspect and Android/browser MetadataAuthoring establish protocol/parity; EditorHome workspace routing establishes how to consume the new operation. Existing EditWorkspace Read gives revision and selected owned source. Public Inspect previously omitted these direct relation fields, so extending its target providers was necessary. Outside edits: desktop Inspect response and both platform metadata templates, using only public Parser/Element APIs. Small deterministic projection code is target-owned; templates stay byte-identical and replies are independently compared in regression. No build-core policy/resolver, OS input, signing, layout or dependency traversal edits.

Rebuild scope: PackWorkspace owning implementation assembly and final bindings because CommandBody imports Inspect; no public signature/contract DLL changes. Desktop authoring tool must rebuild; Android/browser export apps must regenerate/recompile metadata templates. Physical PackWorkspace SnapshotBody/CommandBody and actual EditorHome.Model CommandBody locality gates are checked separately from functional replies. No full-project semantic index is claimed; existing owned snapshot/eager Open limitations are unchanged.

## Verification commands and limits

Existing SDK10.0.401; set DOTNET_CLI_HOME=/tmp/confectory-dotnet10 and CONFECTORY_DOTNET=/workspace/toolchains/dotnet-10.0.401/dotnet:

```
$CONFECTORY_DOTNET build Confectory.sln -c Release --no-restore
$CONFECTORY_DOTNET run --project tests/Confectory.Tests -c Release --no-build -- --require-runtime PackWorkspaceTests SchemaEditingTests test_project_shell_domain_isolated_execution_no_null_chat_open_and_context_cleanup test_project_shell_windows_and_android_managed_compile
```

Functional: all six roles, empty relation set, missing targets without loading/resolution, unchanged scalar/signature inspection, Android/browser identical templates and compiled adapter compared with desktop JSON, selected draft edits/revision, body rejection, actual EditorHome selected-object inspection/edit/reinspect/restore, prior stable-ID filters/pages/same-draft View isolation/Save/review/cleanup. Locality: existing SnapshotBody, added CommandBody and existing actual model CommandBody provider-body probes expect only their selected physical owning implementation pack and zero contracts. Actual common EditorHome builds for Windows/Android; no alternate page. OS UI, Android device/native package and browser OS runtime are not asserted by compiled metadata protocol tests. No new tools or installations.

Next missing bounded candidates: selected required-function signature presentation using existing parsed metadata; read-only direct relation target availability in an explicitly selected registered owning pack. Lazy semantic indexing, effective inheritance/module resolution and cross-pack relationship editing remain larger subsequent increments; do not infer new graph/migration policy from this direct query.

Recorded result (2026-10-08): final full solution/test runner build passes with zero warnings/errors (2.88s). Five selected functional/product/provider/target gates pass, 0 failed,0 skipped (120.721s), including the added CommandBody locality probe. Logs remain private at /tmp/confectory-declared-relations-build.log and /tmp/confectory-declared-relations-tests.log. This branch stacks on owned-element-navigation commit4e9ff89; both functional increments are preserved relative to main f215a70. Work-branch publication only; no main merge.

## Existing typed references and named imports

The schema decision audit adds already-defined `use`/`contain` declarations as edges with their declared target `kind`. Implementation `import` edges preserve function target, alias, optional qualified `scope`, and existing `signature`; multiple aliases for one function remain separate edges. Deterministic ties include kind/alias. Inspect remains declared-only and reads no targets or body code. Locate includes an explicitly declared import scope's manifest locator, without a validity/binding verdict. See [decision audit and status](SCHEMA_CONTRACT_DECISION_AND_EDITOR_STATUS.md) for evidence, scope and remaining decisions.
