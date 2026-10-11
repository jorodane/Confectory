# Stable declaration identity and display names — proposed stages

Status: design proposal, not a migration or a new reference contract. The user's direction is to separate an immutable reference identity from the editable name. No existing declarations, references, names, namespaces or caches are rewritten by this change. The independently completed [description form](DECLARATION_DESCRIPTION_FORM.md) uses existing declaration drafts and Save/Review/Confirm.

## Separate the roles

| Role | Proposed meaning | Current compatibility |
| --- | --- | --- |
| Stable declaration ID | Opaque identifier issued once and persisted, such as a random UUID; independent of name, description, contents and location | Additive first; existing packs have no such member |
| Display name | User-facing, editable text | Fall back to the current local declaration name when absent; duplicate-name rules need a product decision |
| Qualified symbol / legacy alias | `Namespace::Name`, used by published source contracts and name lookup | Keep existing names and external imports working; changing the display name does not rename this symbol |
| Owner / package namespace | Pack selection, dependency scope and ownership | Preserve current namespace checks; a UUID must not grant access across packages |
| Locator | Owned declaration file and implementation target/body path | Remains storage and discovery information, separate from identity |
| Content hash | Baseline conflict checks and artifact freshness | Changes with content; never use it as immutable reference identity |

Calling the reference identity a hash is possible as a representation, but hashing an editable name, source text or path would change the identity on edits. A generated persistent opaque ID avoids that dependency. Existing generated CLR symbol hashes are not already immutable declaration IDs.

## What the current code requires

- [Element and manifest declarations](../src/Confectory.Core/Declarations.cs#L26) store references, parents, function imports, bindings and schema data as string IDs; Element has no general display-name or stable-ID property.
- [Registry.Get](../src/Confectory.Core/Resolution.cs#L45) requires exactly `namespace::local`, checks direct dependencies, selects the manifest locator and verifies that the loaded declaration ID matches it. Namespace is an ownership and dependency boundary, not just a display prefix. Duplicate namespaces currently fail.
- [Effective inheritance](../src/Confectory.Core/Resolution.cs#L74) and [schema contracts](../src/Confectory.Core/SchemaContracts.cs#L8) resolve parent/type/object/function references through that registry. Origins remain important for dependency checks and inherited-field conflicts. `$ref` transport currently requires a namespace-qualified string; a bare UUID is not valid input.
- [Generation.Symbol](../src/Confectory.Core/Generation.cs#L10) hashes the current textual ID. Contract/implementation/binding names therefore change when that ID changes. [Build artifact keys](../src/Confectory.Core/Build.cs#L157) include IDs and generated sources, and linking also hashes the catalog. Separating display metadata will require checking catalog/link invalidation; it does not automatically make name changes free of rebuilds.
- [EditWorkspace revision editing](../packs/edit-workspace/SetTextIfRevision.csbody) explicitly rejects changed IDs/kinds. [Export](../packs/edit-workspace/Export.csbody) and [Restore](../packs/edit-workspace/Restore.csbody) use version-1 identity/path/baseline records keyed by the current textual ID. Saved drafts must not be silently rebound to another object.
- Existing authoring `prepare` relocates copied manifest registry paths; it does not issue new declaration identities. An identity for an edit-workspace session is a hash of project/participant/context, not a declaration identity.

## Proposed implementation order

1. **Specify and add optional persisted identity/display metadata.** Define the versioned parser/formatter, manifest/catalog and transport fields before wiring the name input. Newly authored declarations can receive an ID once; existing declarations continue to load unchanged with their qualified symbols. Assigning an ID to an existing declaration must be an explicit draft change reviewed and confirmed, not a side effect of reading an imported pack. Persist identity in a domain-owned format, not UI localStorage or a conventionally named scalar `value`.
2. **Enable display-name editing through the shared draft.** Keep `Namespace::Name`, registrations, paths, imports and `$ref` strings unchanged. Browser, title and data form read the new display member with the legacy fallback. Save/Review/Confirm and expected revision apply to the actual persisted member. This is the first useful name-editing increment and does not require rewriting every reference. It depends on approval of the additive metadata contract.
3. **Introduce identity-aware resolution with compatibility lookup.** Build a validated owner/qualified-symbol/stable-ID index; legacy names resolve to the same canonical identity, while a versioned identity reference form resolves within the selected, declared package dependencies. Reject duplicate IDs, ambiguous aliases, wrong kinds and missing owners. Inheritance, schema origins, imports, function/provider bindings and implementation body identity must all use the same resolution result. Keep old packs and published namespace contracts usable; do not guess missing external identities.
4. **Version serialization and compilation boundaries.** Add versioned schema/reference/catalog and draft serialization, preserving version-1 reads and source baselines. Decide canonical identity keys for code generation and caches only after resolution is complete; bump the affected ABI/artifact format rather than reusing incompatible artifacts. Test display changes, content changes, file relocation and symbol-alias changes separately. Display metadata should invalidate its consumers; promises about avoiding relinks require measured dependency separation.
5. **Offer explicit, reviewable migration for selected owned packs.** Inventory the complete owned declaration/reference graph and unresolved external consumers first. Produce stable-ID assignment and alias maps with collision diagnostics, source baselines and rollback data. Review all changed sources and registrations, then compiler-backed Confirm. Existing external contracts/aliases remain until their consumers are deliberately migrated. Arbitrary C# body strings and external packs cannot be rewritten by a blanket text substitution.

## Copy, restore and fork

Restoring or moving the same logical pack should retain stable identities while updating locators through existing owned-path checks. Making an independent fork needs an explicit choice: retain identities as another copy/version of the same logical objects, or issue new identities with a complete owned reference map. External references cannot be silently redirected to a new fork. How two copies with the same IDs are selected or rejected in one project must be specified; current duplicate-namespace rejection is not replaced by an arbitrary winner.

## Decisions still needed before name implementation

- Confirm that the first increment edits **display names only**, retaining current published qualified symbols.
- Choose the versioned domain format and ownership of persisted stable ID/display metadata; define collision and duplicate display-name behavior.
- Define copy/fork semantics and cross-version/package selection before exposing identity reassignment.

The user's direction supports this staged separation; it does not authorize bulk migration or immediate removal of namespace contracts. No name-editing or migration code is included in the description-form fix.

## Required acceptance gates

Use the same ordinary ProjectPack across targets. Verify display-name change without changed identity/references; Save/Review/cancel/failure/Confirm/process reopen; inherited schema and function/provider bindings; legacy imported packs and missing/ambiguous IDs; version-1 draft/reference roundtrips; moved locators; preserved-copy and explicit-fork cases; and measured cache/provider rebuild locality. Linux actual UI/browser and Windows/Android managed builds are required; actual Windows/Android device results must be separately established. No fake catalog, synthetic success, special test pack or EditorHome-only build exception substitutes for these gates.
