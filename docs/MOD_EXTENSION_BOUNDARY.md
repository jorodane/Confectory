# Mod build extension requirement

Recorded from the user's additional instruction on 2026-10-05, after the baseline technical design. This is an extension boundary for later work, not authorization to build a full mod loader in this stage.

## Required behavior

- A project supports both mod-enabled and mod-disabled builds. A mod-enabled build can accept additional mod packs that add content and change existing behavior. Mod-disabled output must not expose an active external-mod path.
- Each individual object has an explicit `externalModInheritanceAllowed` checkbox/flag. This governs inheritance by **external mod packs** and is distinct from public visibility, ordinary project inheritance and whether the object's public contract can be referenced. The exact serialized syntax and default must be chosen when implementing this policy; an absent value must not be interpreted as an implicit grant.
- The main game DLL may be supplied as an authoring reference. It is optional; mod connections still use namespace-qualified element IDs and public contracts. An assembly reference must not become a replacement identity scheme or permission to couple to private implementation classes.
- Preserve a versioned public element/contract catalog and the correspondence between IDs, generated interface types, selected providers and generated linkage. A future loader pack must be able to consume this metadata without inferring identities from file names or implementation class names.
- Object policy must remain visible as object-specific policy metadata even when its public contract is visible. A generic exported/private bit does not satisfy the requirement.

## Responsibility boundary

The minimum core resolves declarations and contracts and can describe final linkage. The build-target pack owns reference/export/package mechanics. A future **loader pack** owns discovering, loading and activating extra runtime mod packs, integrating their content and behavior, and enforcing external inheritance policy. The core must not silently accept duplicate namespace/ID declarations as a patch operation.

Windows and Linux are the initial intended runtime targets, conditional on the actual loader/runtime capabilities. Compilation or portable CLR packaging in this stage does not demonstrate runtime mod loading, and it does not promise support on Android, iOS, AOT or every target. Compiled mod code is not sandboxed by pack boundaries, metadata or load contexts.

**Explicitly undecided:** patch mechanics and how behavior changes are expressed, conflict/override ordering, security/trust/permission policy, loader ABI, DLL sharing strategy and per-target runtime capability negotiation. None is resolved by registry order, last-writer-wins, unrestricted reflection, or automatic execution of discovered code.

## This stage

Retain the namespace/ID → contract → actual-provider correspondence in a versioned final public linkage catalog. Record build mode and object policy as future format requirements, but do not add a mod CLI, runtime loader, patch engine, mod discovery or security framework. The current generated function implementation DLL is a function artifact, not a claim that a complete main-game authoring SDK already exists.

## Verified current boundary

On `work/current` at `22eee624523946be2e6adc005b4bd6c9c278c940`, the element parser supports generic Boolean `value` metadata. The ordinary resolver matches the qualified parent ID and kind, requires a direct dependency across packs, and merges parent metadata with local overrides. The proposed checkbox has no dedicated declaration, validation or authoring contract at this revision. [Element and manifest parser](../src/Confectory.Core/Declarations.cs) · [Ordinary dependency and inheritance resolver](../src/Confectory.Core/Resolution.cs)

An isolated Linux project registered an ordinary library pack containing two object parents. The parents carried opposite Boolean values under the proposal's name as generic metadata probes. The Chromium object editor opened both owned children and displayed their respective parents. Each editor snapshot recorded the qualified parent and identified the inherited value as Boolean metadata with its original source. The object editor had no dedicated external-inheritance checkbox. All project and library source bytes were preserved.

The same fixture passed ordinary `validate` and `build` for `linux`. Both child relationships appeared in `public-linkage.json`, with the Boolean values under `metadataValues` and their original parents as their origins. An unreferenced owned object was absent from the catalog. Removing the library dependency while leaving its registry entry produced `UNDECLARED_DEPENDENCY` in a separate probe manifest. Those results describe ordinary pack resolution and the `linked-elements` surface. [Public linkage generation](../src/Confectory.Core/Generation.cs) · [Format and catalog semantics](FORMAT.md#public-linkage-catalog)

The catalog reported `coreProvidesRuntimeModLoader: false` in the ordinary Linux build. The CLI treated `mod-enabled` and `mod-disabled` as target names and reported `MISSING_TARGET` for both on this fixture. MOD01 and MOD03 still require a defined build-mode and object-policy contract, including how the owner identifies an external mod link and where that link is checked. [Target lookup](../src/Confectory.Core/Build.cs)

## Future acceptance tests

| ID | Required future evidence |
| --- | --- |
| MOD01 | Build the same project with mods enabled and disabled; verify only enabled output activates a loader pack. |
| MOD02 | An additional mod pack adds content and changes behavior through the eventual approved patch/link contract. |
| MOD03 | Two equally public objects differ in external inheritance permission; only the opted-in object accepts external mod inheritance. Ordinary project inheritance and contract references retain their separately specified policy. |
| MOD04 | Mod authoring against the optional main-game DLL plus public metadata resolves namespace-qualified IDs without private implementation references. |
| MOD05 | Runtime tests on supported Windows/Linux configurations; unsupported runtime/target capabilities fail explicitly. |
| MOD06 | Duplicate identities, conflicts and untrusted-code policy follow the later approved mechanics, ordering and security specification. No sandbox claim without an actual enforced boundary. |

These tests are pending loader-stage acceptance criteria and must not be counted among current build-core passes.
