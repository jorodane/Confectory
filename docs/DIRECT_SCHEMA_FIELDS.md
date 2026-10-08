# Direct schema declarations and actual editor authoring

The user selected formal `.celem` field/type/reference declarations on 2026-10-08. This supersedes the pending representation question in SCHEMA_CONTRACT_DECISION_AND_EDITOR_STATUS.md. Generic schema contracts are direct source declarations; existing Rig/Render JSON domain payloads and primitive `value` metadata remain compatible. This increment does not complete the entire editor.

## Grammar and public model

```text
schema Example::Shape {
  field title single general string;
  field levels multiple general int;
  field child single compound Example::Leaf;
  field peer single reference Example::Shape;
  field callback single function Example::Compute;
}
object Example::Item {
  use schema Example::Shape;
  data title = "";
  data levels = [0, 2];
  data child = { enabled = false; };
  data peer = Example::OtherItem;
  data callback = Example::ComputeBody;
}
```

Each field has name, cardinality (`single`/`multiple`), kind, type/qualified target and source provenance. `general` supports the existing function-contract primitive types bool/int/long/float/double/string, excluding void and array suffixes. `reference` is the explicit general-reference case: a schema-constrained object identity, rather than a quoted string that looks like an ID. `compound` is a nested field group constrained by a schema. `function` points to an independent public function contract; its data is the ID of an implementation with matching function identity/signature. It records an implementation association, without calling the function or implicitly selecting an execution provider. Function-valued field invocation/presentation remains a subsequent pack policy.

Lists implement multiple cardinality for all four representations. Nested compounds/lists are direct syntax, with a 64-level input limit. `$ref` appears only in API transport, never as a stored JSON string. Existing element kinds, signatures, `use`/`contain`, primitive `value`, target-specific bodies and old source files continue to parse. No schema-specific engine host, new platform connector or table-owned object model is introduced.

## Validation and inheritance

Public Core `SchemaContracts.Fields` and `Validate` resolve applied schemas and validate present data. Planner validates reachable typed metadata and records its referenced IDs without binding data function associations. Builder.Validate validates all registered declarations, including unreferenced newly authored objects, so desktop Confirm cannot accept invalid typed data merely because it is not reachable from Main. Qualified targets use the existing direct-dependency and element-kind checks; function associations use the existing implementation/contract checks.

Single-parent schema inheritance preserves omitted fields and their origin. A same-name explicit field must retain cardinality/kind/type; incompatible contracts diagnose SCHEMA_INHERITANCE. Object data inherits by top-level field name; an explicit datum replaces that entire datum, including a compound/list. There is no nested semantic merge, reference rewriting or deletion syntax. Multiple applied schemas with different origins for the same field diagnose SCHEMA_AMBIGUITY; no implicit merge is invented. Missing fields remain unset: required/default/null policies are not inferred. Ordinary object reference cycles remain valid; compound schema/parent structural cycles fail through the existing structural gate. Number bounds and finite floating values are checked. Unknown fields, mismatched cardinality/type, invalid target kinds and absent/dependency-invalid references fail with source locations.

## Same actual EditorHome path

`examples/editor-home/project.cpack` still selects `Confectory.EditorHome::Main`. Existing Model Command workspace routing accepts:

- `field`: selected owned schema; `{field, value:{cardinality,kind,type}, expectedRevision}`.
- `data`: selected owned object; `{field,value,expectedRevision}`. Primitives retain false/0/empty; arrays are multiple data; plain objects are compounds; `{"$ref":"Namespace::ID"}` is an explicit reference.
- Existing `inspect` projects declared fields/data; `effective` projects schema-derived fields/data from current root-owned drafts and confirmed registered files. Declared field/data references are included in explicit relation navigation.

Both edits use the existing revision check and SetTextIfRevision; successful edits invalidate Review, malformed requests preserve existing drafts/reviews, stale edits return the current View conflict. Shared SchemaEditing::Call operations `setField`/`setData` format direct source and reparse it. The existing scalar formatter also preserves fields/data. Actual product verification creates schema declarations, edits all representations, reads the owned draft descriptor, fails invalid grouped Confirm without writes, retries valid grouped compiler-backed Confirm, and preserves null failures. Save/export and explicit pinned Review/Confirm retain their established behavior.

No presentation layout has changed. Existing source View edits these declarations; schema-derived metadata and structured editing are now public product commands. Automatic schema-generated control/table Views, function-call controls and customized ObjectEditors remain next-stage work, separate from this declaration/authoring increment. Browser/Android support direct metadata/draft editing; their existing capability gates still require a compiler provider for Confirm/dynamic project execution.

## Pack boundary and rebuild ledger

Intended owners: Confectory.SchemaEditing::Call/Inspect/SetValue; Confectory.PackWorkspace::CommandBody; Confectory.EditorHome.Model::CommandBody. Their function IDs/signatures are unchanged; Call gains explicit typed transport operations and projections, PackWorkspace/Model gain typed command actions. No caller may reach private EditWorkspace state.

Necessary shared-contract edits: Core Element adds Fields/Data, typed records, parser grammar, effective inheritance and public validation. Existing scalar-only contracts could neither declare schema field types nor distinguish qualified object/function references from opaque strings, so these are explicit shared language changes. Documents cache version changes to avoid loading pre-schema AST records. Public linkage catalogue carries schemaFields/typedData without local build paths; final link key includes catalogue digest so metadata-only changes are reflected while unchanged provider/contract DLLs remain reusable. Core edits require rebuilding the Core/CLI/authoring/target assemblies; they are not claimed as a pack-only locality change.

Outside implementation reads: baseline extracted text sections 2–3/6; Core declarations/resolution/planner/Builder/catalogue; SchemaEditing desktop/native adapters; PackWorkspace revision/Review/Confirm; actual Model routing and VerifyShell; existing schema packs and roadmap. Readable extracted baseline bytes were inspected; original Library DOCX byte materialization remains unverified and no claim of newly reading the original DOCX is made.

Outside edits and reasons: desktop authoring host and identical Android/browser MetadataAuthoring templates preserve/project/format the new public AST, which their old scalar formatters would discard. EffectiveMetadata and declared relations expose the new contracts without body execution. Actual VerifyShell, Core tests, metadata-only relink integration tests and native metadata consumer tests validate these required consumers. The Android API probe was also corrected to include its real exported metadata and SDK-generated Resource inputs after the stale harness failed. No main/layout/domain Rig/Render edits.

Structure gates remain separate: existing runtime locality probes require only their owning implementation pack rebuilt and zero compiledContracts after an owning body edit. Language/compiler rebuild scope is separately acknowledged above. Test logs, binaries, browser outputs and recovery artifacts remain outside Git.

## Verification and next stage

Exact commands and final results are recorded below. Continue on `work/current`, normal authorized push; no main merge or new feature branch. Reconcile the historical stage-18 numbering before assigning a new numbered checkpoint. Future work must resolve separately any required/default/removal policy, conflicting multiple-schema combination or function invocation semantics, rather than treating the representation approval as authorization to invent them.

### Completed gates (2026-10-08)

All builds use SDK `/workspace/toolchains/dotnet-10.0.401/dotnet`, `DOTNET_CLI_HOME=/tmp/confectory-dotnet10`, and `CONFECTORY_DOTNET` set to that executable. No tools were installed.

1. `dotnet build targets/element-authoring -c Release --nologo` and `dotnet build tests/Confectory.Tests -c Release --nologo`: zero warnings/errors. Strict suite `dotnet run --project tests/Confectory.Tests -c Release --no-build -- --require-runtime CoreTests EditWorkspaceTests PackWorkspaceTests SchemaEditingTests SourceEditorTests ElementViewTests test_project_shell_domain_isolated_execution_no_null_chat_open_and_context_cleanup test_project_shell_windows_and_android_managed_compile`: **52 passed, 0 failed, 0 skipped**, 265.180s. This includes public typed grammar/validation/reference/transport safety, native adapter parity and actual product typed Review/Confirm plus separate owning-body locality probes.
2. The final catalogue projection then removed source locations from public schema/data payloads while retaining qualified origin. `--require-runtime IntegrationTests`: **31 passed, 0 failed, 0 skipped**, 158.738s. New schema metadata integration gate verifies real execution, changed final link key/catalogue, **zero compiledPacks and zero compiledContracts** after both schema-only and data-only changes, and no private build paths in public schema metadata. Old contract/provider cache, target fallback, failure preservation and protocol tests also pass. Latest actual product/native metadata repeat: `--require-runtime test_project_shell_domain_isolated_execution_no_null_chat_open_and_context_cleanup test_target_metadata_owned_sources_no_registry_execution`: **2/0/0**, 74.624s.
3. Actual common EditorHome browser build: `dotnet src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll build examples/editor-home/project.cpack browser`. Unmodified `python tests/web/editor_home_workspace.py /tmp/confectory-direct-schema-browser-latest-build.json` and `python tests/web/editor_home_browser.py /tmp/confectory-direct-schema-browser-latest-build.json`: **both pass** actual create/input/stable controls/acknowledged draft Save/leave/reopen/480px resize/reload/ZIP/owner cleanup. Final sources remain unchanged by draft Save; static GET-only WASM and existing capability gates remain verified.
4. Windows and Android managed compilation of the same product pass in the strict suite. Actual Android SDK target compilation/unsigned packaging also passes: `dotnet targets/android-export/bin/Release/net10.0/Confectory.AndroidExport.dll examples/editor-home/project.cpack /tmp/confectory-schema-android-package-20261008-final --package`, additionally setting `CONFECTORY_ANDROID_DOTNET` to the installed SDK executable, `ANDROID_HOME=/workspace/toolchains/android-sdk`, `JAVA_HOME=/workspace/toolchains/jdk-21`. **Build succeeded, zero warnings/errors, 78.94s**; unsigned `com.Confectory.Engine.aab`, min24/target36, actual app compiled. No signing, installation or Play/device acceptance.
5. `python tests/android/compile_api.py /tmp/confectory-schema-android-package-20261008-final /workspace/toolchains/dotnet-10.0.401`: **pass**, with the existing Java.Interop System.Runtime9→10 CS1701 warning in this direct API probe; the actual SDK build above has zero warnings. The stale probe omitted MetadataAuthoring.cs, System.IO implicit using and SDK-generated Resource inputs. It now includes actual exported metadata and actual SDK-generated Resource source/assembly, and reports a clear missing-SDK-generated prerequisite if that resource has not been built. No resource implementation/doubles are fabricated by this correction.

Preserved failed attempts: initial broad suite50/1/0 hit a VerifyShell local-name collision; the first product retry incorrectly assumed Create's returned revision was0 instead of1. Both verification fixtures were corrected and the final strict suite passes. Initial browser workspace attempt timed out during leave/reopen; two passive diagnostic reruns and both subsequent unmodified final-output runs passed. No product timing/layout/timeout adjustment was made and that transient's cause is not claimed resolved. Initial raw Android API probe failed due to the stale source/resource inputs described above; final actual SDK packaging and corrected probe pass.

Private evidence remains outside Git: `/tmp/confectory-direct-schema-final-gates.log`, `-integration.log`, `-product-latest.log`, `-browser-latest-build.json`, `-browser-latest-workspace.log`, `-browser-latest-regression.log`, `-android-final-package.log`, `-android-latest-api.log`; prior failure/diagnostic logs use the same prefix. All generated outputs/AABs/images remain in local temporary/build storage.

Remaining runtime gates: DISPLAY is unset and Xvfb unavailable, so actual native Linux GUI was not run here; Windows OS runtime was not run. Installed Android SDK36/JDK21/workload support compilation, but adb cannot create `/home/agent/.android` under the read-only home policy (retry with Android user-directory environment settings also failed), so current device enumeration/runtime is unverified. Original Library DOCX bytes remain unverified, as above. These do not block the completed declaration/authoring/compiler increment.

### User spot checks and durable continuation

Update only `work/current` with ordinary fast-forward pull, retain local Android application/package settings. Rebuild Core/CLI/authoring/targets with the installed matching SDK; run the strict tests above for an automated actual EditorHome schema editing and Confirm exercise. Launch the actual `examples/editor-home/project.cpack` through the CLI `run ... linux` or `run ... windows` on a supported machine. Open/create a project, select owned schema/object source, edit the direct declarations above, Save, leave/reopen and verify that draft Save has not changed final sources. Review an explicit schema/object/manifest group before Confirm; an invalid type/reference must leave all final files untouched. Android spot checks use a locally signed copy of the unsigned export and remain asynchronous.

Next implementation stage: consume the public schema descriptor and `field`/`data` commands in reusable schema-derived element Views within the existing actual EditorHome layout. Keep object semantics independent of a table, reuse control instances/Owner lifetimes, and preserve the existing review scope. Automatic control choice, function invocation/return presentation and unset/required/default/removal policies need explicit bounded pack contracts; this increment records associations and rejects undefined edits rather than inventing those semantics. Preserve unresolved browser timing observation and native/device checks in subsequent handoff.
