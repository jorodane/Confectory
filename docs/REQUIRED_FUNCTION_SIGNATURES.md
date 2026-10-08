# Required-function signature query

The baseline's module contract requires public function IDs/signatures independently of implementation selection. Core already parses ordinary function declarations and module require statements into the same public FunctionSignature type. Inspect already serializes function `signature`; the prior declared-relation reply omitted a require statement's parsed signature. This increment reuses that exact serializer/shape rather than creating a second contract model or a new query function.

## Additive contract

Existing `Confectory.SchemaEditing::Inspect(text)` signature and old JSON fields remain unchanged. Only relation edges whose role is require gain `signature`:

```
{"role":"require","target":"Missing::Function","function":null,
 "signature":{"Args":[{"Type":"string","Name":"arg0"},
                       {"Type":"int[]","Name":"arg1"}],"return":"bool"}}
```

Preserve the existing case of Args/Type/Name and `return`; it is the same shape as ordinary function Inspect. Require declarations do not author parameter names, so the existing Parser supplies arg0/arg1 in declaration order. No-argument/void signatures return Args:[] and return:"void". Types and array suffixes are those already accepted by the Parser. No coercion, signature match verdict, inherited requirement merge, default selection or implementation conflict resolution is performed.

Owner/target remain qualified IDs and relations.scope remains declared. Unregistered targets can be inspected without target opening, compilation or function invocation. Parent/module/include/default/provide edges retain their previous fields without a new signature field.

Use the existing actual product route:

```
EditorHome.Model::Command(session,"workspace",
 {context: activeContext,action:"select",id:"Shell.Contracts::Rules"})
EditorHome.Model::Command(session,"workspace",
 {context: activeContext,action:"inspect"})
```

Read workspace.inspection.relations.edges where role==require. workspace.inspectionRevision belongs to the selected current draft; request again after editing. No new layout or permission surface.

## Increment ledger and verification

Intended existing contract: SchemaEditing Inspect's additive declared relation payload. Implementation edits: desktop target-owned DeclaredRelations and identical Android/browser MetadataAuthoring templates. Outside reads: public Core FunctionSignature/Parameter and Parser.Signature establish existing field shape and synthetic parameter names; earlier direct-relation helper and selected draft command establish reuse. No core/pack signature, workspace operation, EditorHome command, resolver, rendering, input or layout edits. Existing actual VerifyShell gains a real selected module test through the same product provider, not a new page. Rebuild scope: desktop authoring tool; Android/browser app regeneration for modified templates. Pack consumers keep the same function contracts; test-only VerifyShell changes rebuild its owning product implementation pack. Existing physical PackWorkspace SnapshotBody/CommandBody and actual model CommandBody locality probes stay separate from functional checks.

Commands with existing SDK10.0.401, DOTNET_CLI_HOME=/tmp/confectory-dotnet10, CONFECTORY_DOTNET=/workspace/toolchains/dotnet-10.0.401/dotnet:

```
$CONFECTORY_DOTNET build Confectory.sln -c Release --no-restore
$CONFECTORY_DOTNET run --project tests/Confectory.Tests -c Release --no-build -- --require-runtime PackWorkspaceTests SchemaEditingTests test_project_shell_domain_isolated_execution_no_null_chat_open_and_context_cleanup test_project_shell_windows_and_android_managed_compile
```

Coverage: empty args/void, ordered scalar/array/multiple parameters and array returns compared against existing ordinary function signature serialization; desktop-versus-compiled metadata adapter relation JSON parity; Android/browser template byte equality; actual EditorHome module selection, missing-target require inspection, draft return-type edit/reinspection at revision1 with unchanged final source. Existing relation roles, stable-ID filters/pages, draft/View isolation, Save/review/cancel/cleanup and locality gates retained. Windows/Android actual common product managed compilation is distinct from OS/device execution. No new tools, installations, native packages, arbitrary calls or AI authority changes.

## Remaining functional gaps — report only

1. Explicit registered owning-pack target availability: determine whether a direct relationship's target ID has a locator and expose kind without recursive graph loading. Existing Core Registry locators exist; an editor read-only public projection is still missing.
2. Lazy owned semantic navigation: EditWorkspace currently describes the owned root eagerly. A selected-pack/element incremental index and invalidation contract need a separate coherent increment; filtering already cached units is not that index.
3. Effective inheritance/module contract explanation: Core resolves these during builds, while editor queries now expose declarations only. A read-only public explanation must preserve provenance, target-specific provider choices and existing conflict semantics; do not invent a second resolver.
4. Typed property/schema/reference presentation: scalar metadata editing exists, but complete schema-driven fields, reference target queries and migration workflows are incomplete. Cross-pack rename/move requires explicit reference migration, not inferred ID changes.
5. Relation editing and transitive graph navigation: deferred; requires deliberate ownership/read/mutation bounds. Asset indexing and broader editor tooling also remain outside these bounded queries.

No larger follow-up is started automatically. Layout integration belongs to the user's separately produced layout. These items distinguish existing low-level parser/resolver capabilities from missing editor-facing contracts.

Recorded result (2026-10-08): full solution build passes with zero warnings/errors (3.06s). Initial combined selection reports4 passed/1 failed/0 skipped (118.261s): the SchemaEditing test consumer had a C# local-name collision in its newly added fixture loop. Renaming that fixture variable required no product change; the affected SchemaEditing functional/locality gate then passes1/0/0 (15.109s). The four other current gates include target JSON parity, workspace functional/locality, actual EditorHome signature/revision flow and Windows/Android managed compilation. Thus all five relevant gates have passing current results, across these runs; a clean single combined five-pass run is not claimed. Private logs: /tmp/confectory-required-signatures-build.log, /tmp/confectory-required-signatures-tests.log, /tmp/confectory-required-signatures-schema.log. Existing navigation/relation commits4e9ff89/372d686 remain in this stacked work branch relative to main f215a70.
