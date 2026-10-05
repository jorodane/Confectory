# Requirements and executable tests

The initial requirement/verification table was written before implementation. Named tests below remain searchable after the C# rewrite. `C` means `CoreTests` in `tests/Confectory.Tests/CoreTests.cs`; `I` means `IntegrationTests` in `tests/Confectory.Tests/IntegrationTests.cs`. The dependency-free console runner executes the tests against the C# library and real .NET target tool. Current results are in `VERIFICATION.md`.

| ID | Specification requirement | Verification |
| --- | --- | --- |
| CORE01 | §§1,2,4 ProjectPack + target; engine is a ProjectPack | App/sample pipeline and role-composed two-View engine pass. Core/CLI/tool remain ordinary csproj bootstraps; compiler self-hosting is not claimed. |
| DECL01 | §2 Dedicated structure language, C# bodies, explanations | Parse owned manifests/elements with locations; unknown syntax, wrong locator/header, duplicate fields and escaped paths fail. |
| ID01 | §2 Namespace-qualified identity | Same local ID in different namespaces succeeds; duplicate namespace/element fails; moving source location preserves identity. |
| LINK01 | §§2,20 Missing/wrong-kind/incompatible links | Missing namespace/element/dependency, mismatched kind/signature/function identity and invalid entry fail with source diagnostics. |
| CONTRACT01 | §2 Contract-only local compilation | Compile actual consumer DLL without provider implementation; execute final build only after provider arrives; final missing provider fails. |
| CONTRACT02 | §§2,4 One contract across target implementations | Target/common bodies share one generated interface; incompatible imports/providers and invalid C# fail. |
| INHERIT01 | §§2,20 Single parent then explicit overrides | Values/provenance and bindings inherit; false/zero/empty-string override; sibling/parent unchanged; wrong kind, missing parent, multiple parents fail. |
| MODULE01 | §2 Independent functions and composed modules | Direct use without module, shared function across modules, nested defaults, required functions and independent consumer scopes. |
| MODULE02 | §2 Exact declaration/default selection table | Explicit/inherited binding beats defaults, one default works, distinct defaults conflict, zero providers fails, repeated identical provider deduplicates. |
| CYCLE01 | §2 Structural cycles vs references/recursion | Inheritance, containment, module cycles fail; ordinary reference cycles and recursive actual function calls succeed. |
| TARGET01 | §4 Target-specific → common → missing | Execute target body and common fallback; missing both fails; broken selected body does not fall back. |
| TOOL01 | §2 Delegate compiler/packaging to target pack | Exercise protocol, missing/broken tool/invalid reply errors, tool fingerprint invalidation; portable and Linux launcher outputs. |
| GRAPH01 | §§2,3 Entry usage graph and always-include | Transitive stage/view/module/inheritance/import links are included; unused pack excluded without body reads; always-include is validated. |
| VERSION01 | §3 Project-selected versions remain pinned | Mismatch warning still produces runnable app; selected version/path does not change; incompatible contract still fails. |
| LOCAL01 | §§3,5 Reuse unchanged local artifacts | Second build compiles zero local DLLs; hashes/mtimes of reused artifacts remain unchanged. |
| LOCAL02 | §§3,5 Implementation vs contract invalidation | Provider body change rebuilds only provider; caller DLL reused and new app output observed. Contract change rechecks affected callers; compatible updated consumer rebuilds; unrelated artifacts reused. |
| LOCAL03 | §3 Local reads and per-element contract granularity | Add many unrelated packs; local check reads no unrelated documents; change unused contract in same pack without rebuilding callers. |
| CACHE01 | §§2,5 Inputs/tools ↔ outputs; failure preserves old result | Corrupt cache artifact forces rebuild, tool changes invalidate, failed candidate preserves last successful runnable output. |
| SCOPE01 | §§1,2,5 Runtime/editor remain external | Source review: core contains no runtime/UI/physics/editor implementation; no old-repository access or modification. |
| META01 | Additional mod extension boundary | Final public catalog preserves qualified IDs, contracts and actual linkage without bundling a runtime loader; MOD01–MOD06 are explicitly deferred in `MOD_EXTENSION_BOUNDARY.md`. |

Exact version expectations and `*`, primitive C# contract types, synchronous function bodies, and selected target profiles are the initial supported syntax. Unsupported syntax fails explicitly; later language features must extend this map rather than silently reinterpret declarations.

## Concrete test references

| Requirement | Named test evidence |
| --- | --- |
| CORE01 | I `test_bootstrap_projectpack_uses_identical_build_path`; EngineTests `test_role_composition_two_windows_and_cleanup`; C `test_project_input_cannot_be_a_regular_pack`, `test_entry_is_required_and_typed` |
| DECL01 | C `test_wrong_locator_and_source_locations`, `test_duplicate_target_body_and_unknown_syntax`, `test_owned_source_path_cannot_escape_pack` |
| ID01 | C `test_namespace_qualified_same_local_id`, `test_duplicate_namespace`, `test_duplicate_element`; I `test_contract_location_move_keeps_identity_and_local_dlls` |
| LINK01 | C `test_missing_namespace`, `test_missing_element`, `test_wrong_element_kind`, `test_undeclared_cross_pack_dependency`, `test_provider_signature_mismatch`, `test_import_signature_mismatch`, `test_provider_wrong_function_identity`, `test_missing_final_provider` |
| CONTRACT01 | I `test_contract_only_compile_without_provider_and_reuse_at_final_link`, `test_private_implementation_class_cannot_be_an_authoring_reference` |
| CONTRACT02 | I `test_csharp_body_is_type_checked_against_generated_contract`, `test_broken_selected_target_body_does_not_fall_back`; C `test_provider_signature_mismatch` |
| INHERIT01 | C `test_inherited_values_and_provenance_without_parent_mutation`, `test_explicit_empty_description_overrides_parent`, `test_inherited_binding_beats_defaults`, `test_parent_missing_wrong_kind_and_multiple_parent_syntax`; I `test_inherited_cross_pack_references_keep_original_owner_dependencies`, `test_implementation_inherits_target_body_from_owning_pack` |
| MODULE01 | C `test_single_module_default`, `test_same_default_deduplicates_through_nested_modules`, `test_module_contract_signature`, `test_default_not_in_module_contract`; I `test_independent_scopes_and_inherited_bindings_execute` |
| MODULE02 | C `test_explicit_binding_beats_multiple_defaults`, `test_different_defaults_conflict`, `test_module_missing_default`, `test_same_default_deduplicates_through_nested_modules`, `test_invalid_default_cannot_hide_behind_explicit_binding` |
| CYCLE01 | C `test_inheritance_cycle`, `test_containment_cycle`, `test_module_inclusion_cycle`, `test_reference_cycle_is_allowed`; I `test_recursive_function_calls_execute` |
| TARGET01 | I `test_target_specific_common_fallback_and_linux_launcher`, `test_distinct_module_defaults_and_missing_target_fail_before_execution`, `test_broken_selected_target_body_does_not_fall_back` |
| TOOL01 | I `test_missing_target_and_tool_protocol_errors`, `test_tool_binary_change_invalidates_local_artifacts`, `test_inherited_build_target_uses_parent_owned_tool` |
| GRAPH01 | C `test_transitive_stage_view_inheritance_and_always`, `test_unused_documents_are_not_read`; I `test_actual_linked_output_and_public_catalog` |
| VERSION01 | I `test_selected_versions_warn_without_breaking_executable`, `test_addition_of_a_newer_pack_does_not_change_project_selected_version` |
| LOCAL01 | I `test_unchanged_build_and_provider_only_change` |
| LOCAL02 | I `test_unchanged_build_and_provider_only_change`, `test_contract_change_rechecks_consumers_and_rebuilds_only_affected_packs` |
| LOCAL03 | I `test_local_compilation_reads_do_not_grow_with_unrelated_element_documents`, `test_unrelated_contract_in_same_pack_does_not_invalidate_consumers` |
| CACHE01 | I `test_corrupted_local_artifact_is_rebuilt`, `test_tool_binary_change_invalidates_local_artifacts`, `test_failure_preserves_latest_successful_runnable_output`; C `test_changed_text_with_restored_mtime_is_not_a_stale_document_hit`, `test_corrupted_document_cache_is_reparsed` |
| META01 | I `test_actual_linked_output_and_public_catalog`; pending loader requirements MOD01–MOD06 are documented separately |
| SCOPE01 | Manual source/diff review; tests compile through the independent target pack and never use the old repository |
| C# migration | I `test_cli_preserves_json_reports_and_exit_codes`, `test_validate_checks_unreached_declarations_without_compiling`, `test_utf8_pack_and_body_paths_with_spaces_execute`, `test_compiler_artifacts_cannot_escape_requested_output`; C `test_non_utf8_source_reports_owned_location`, `test_owned_source_symlink_cannot_escape_pack` |

## Migration verification regressions

`VerificationTests` adds nine executed tests: successful and invalid-body direct inclusion for always/use/contain; missing target body; incompatible contract; missing root import scope; import dependency closure for all three paths; module implementation edges; pruning an unused invalid body while local checking rejects it; and multi-implementation local/final cache reuse across unused-body, used-body and contract changes. See `VERIFICATION.md` and the captured observations for exact compilation counts. Core/compiler self-hosting, self-contained packaging and Windows execution remain incomplete/unverified; the later runnable engine ProjectPack milestone is recorded in CHECKPOINT_1.md.


Runtime pack gates: RuntimeBaseTests (isolated/shared lifetime, release/reopen and provider locality), RealTimeUpdateTests (cadence/catch-up/order/token replacement/camera/picking snapshots), BaseUITests (intended controls/repeat/cancel/resize/locality), EngineTests (real composed provider graph, two-window isolation/reopen and labels-only rebuild), AndroidPreparationTests (managed Android overrides/lifecycle/export and provider locality). Actual X11 click/autorepeat/resize/camera/close/reopen/SIGINT checks are in `tests/gui/engine_x11_spotcheck.py`. Android native SDK template/APK/runtime and Windows execution are separate not-run gates.

Checkpoint 2: ProjectExecutionTests validates stable independent handles, selected entry/target, build errors, stop/caller disposal, one-time notifications, provider locality and explicit managed Android unavailable capability. ProjectManagerTests validates create/open/select/close/reopen, no implicit project, independent data/execution lifetime, no overwrite and Context-only locality. BaseUITests validates reusable project panel activation/cancel/repeat/resize/error labels. Actual X11 project_manager_x11_spotcheck.py validates composed UI A/B controls and independent context/View/worker lifetime. IntegrationTests CLI run validates stream/exit/spaced paths. Windows compile/native runtime and Android managed/native SDK/APK/device gates remain distinct.
