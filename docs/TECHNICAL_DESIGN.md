# Confectory minimum build core

This design is derived from the attached **설계 기준 2**, read in full before implementation. The core builds a ProjectPack for a named target; it does not contain an engine runtime. The empty `jorodane/Confectory` repository is the new destination. No Golemancer code or repository is used.

## Specification access

- Source: `Confectory_엔진_통합_설계_명세_20261005(1).docx`, dated 2026-10-05.
- Read all 20 sections, including the superseded decisions and preserved contracts; 618 paragraphs/table rows, 41,571 extracted characters.
- Original SHA-256: `3c255a726d58510a3691fbec23578f2f56318575fb3697dd7770cdbf161c2769`.
- Governing core requirements: §§1–5, 17–18, 20; especially U7–U11. The current instruction authorizes this new implementation despite the document's earlier planning-only status.
- The original attachment, conversation history, SDK, credentials and generated binaries are not publication candidates.

## Boundaries and format

Use a .NET 8 C# library (`src/Confectory.Core`) and a small CLI (`src/Confectory.Cli`). The former Python bootstrap is replaced, including the parser, lazy registry, inheritance, scope-aware planner, C# generation, artifact cache and diagnostic reports. All dependencies are in the standard library. C# bodies and the `.cpack`/`.celem` grammar retain their existing contracts.

A build-target pack supplies its own out-of-process tool using a versioned JSON request/response protocol. The initial C# tool is `targets/dotnet/Confectory.Build.DotNet.csproj` and uses an installed .NET 8 SDK. The solution builds its Release DLL before pack builds. The core can launch a target DLL through the .NET host or an ordinary executable, but compiler selection, compiler flags, framework references, runtime configuration and package layouts remain owned by the target tool. Python is not used at build or runtime.

`.cpack` is a dedicated declaration language for pack/project manifests and small element locators. `.celem` declares exactly one independently owned element. `.csbody` contains only an ordinary C# method body. The language represents functions, implementations, modules, categories, concepts, schemas, objects, stages, views, descriptions, typed references, single-parent inheritance and target body choices. Generic element values are metadata; interpreting UI/physics/schema-specific policies is outside this core.

`Namespace::Element` is identity. Manifest locators are locations, not identity. Only the ProjectPack registry maps namespaces to physical manifests. Body paths and tool paths must be local to their owning pack. A pack declares direct dependencies; cross-pack element edges require those dependencies. There are no author-supplied assembly references or implementation class names. C# consumers use named imports generated from qualified function contracts.

## Resolve and validate

Read the small registry and manifests first. Reject duplicate namespaces and locators before pruning. Load element documents only on demand and cache them separately using a file change stamp and content fingerprint. On Linux, `statx` supplies modification/change times, inode and device; where reliable change stamps are unavailable, reread requested documents. Restored modification times must not revive stale data. Cache keys are versioned separately from the Python implementation. Retain source file/line/column diagnostics and value/binding provenance. Validate referenced identity, expected kind, direct dependencies and exact function signatures. Exact version expectations or `*` are supported initially; version differences warn and never substitute for contract checks or change a selected path/version.

Resolve one parent before modules. Omitted values inherit, explicit values (including `false`, `0`, `""`) override, new values append; merge results never mutate parents. Structural inheritance, containment and module-inclusion cycles fail. Ordinary reference cycles and recursive calls are valid.

For each consumer scope and required function: an effective explicit binding wins; otherwise the function's own explicit binding applies; otherwise use the unique module default. Different defaults conflict, no default is an error, and identical implementation IDs reached through several module paths count once. Defaults and explicit providers must match the required function identity and contract. The scope may be specified for a function import so two independent elements can legally use different implementations of the same function. This is build-time binding metadata, not runtime instance management.

An implementation declares one function contract and a map of body files. Select the current target body before `common`. Missing bodies fail final linking. A present but broken target body fails compilation; it does not silently fall back. Every body is wrapped in the same generated public contract.

## Contracts, linking and reuse

Current physical boundary (supersedes the original per-element decision): generate one contract assembly per selected owning pack namespace and one implementation assembly per selected owning pack namespace. Keep independent generated interface types and qualified IDs inside those assemblies. Implementations reference only selected contract DLLs and framework references, never another pack's implementation DLL. Separate contracts preserve cyclic calls and local checking without implementation providers. Full local checking and pruned final builds have distinct artifact keys when their selected source/contract sets differ. Body edits rebuild the selected owner pack; contract changes invalidate consumers of that physical contract pack. Unselected contracts and bodies stay unopened/pruned. See PACK_DLL_BOUNDARIES.md for current ABI and evidence.

Final graph traversal starts at the ProjectPack entry and explicit always-include roots. Follow references, containment, inheritance, modules, selected providers and their declared imports. Only reached implementation packs and contracts enter the executable package. Manifest registration and final inclusion are reported separately. Build-target tools are build-time dependencies and are not bundled into the app. Generate concrete interface adapters/import factories for actual providers, including lazy references for recursion; no stub or missing implementation is packaged.

Content-addressed contract/pack keys cover generator/protocol version, target-tool fingerprint and SDK/compiler/reference configuration, selected C# content, owned declarations and observed contracts. Consumer keys exclude provider implementation content. A provider-only change rebuilds that provider and final bindings/package; callers reuse their existing DLLs. A contract change revalidates its consumers and recompiles only affected packs. Verify artifact hashes before accepting a cache hit; write completed entries atomically. Outputs are unique build directories; a failed build does not replace an earlier successful result.

## Verification and staged work

The requirement map is written before code. Run declaration/graph tests plus integration tests that invoke the actual target compiler and execute the resulting app. Record source reads/parses, checked contracts, compiled/reused contract and implementation artifacts, and included/excluded packs. Also build an engine-labelled ProjectPack through the identical path and demonstrate portable CLR and Linux launcher packaging.

This stage excludes runtime owners/state/hot reload, UI/MVC, physics, input, editor, AI, collaboration, Save/Confirm and product pack management. Preserve their specification requirements for later packs. The C# core does not build itself through pack declarations: the engine sample contains only a bootstrap function that prints a name. It demonstrates the ProjectPack pipeline but supplies no actual engine runtime components or reproducible self-hosting. Platform signing/AOT/mobile/native Windows packaging and legacy migration remain future target-pack work.

## Publication

Prepare and review all source/docs/tests first. Before the first push, ask whether this source set may be published to the currently **public** repository and which branch to use. Do not infer new-repository publication permission from historical Golemancer authorization.


## Later runtime pack milestone

The initial-stage exclusions above describe the compiler bootstrap at that stage. RuntimeBase, RealTimeUpdate, RenderInput, Window and BaseUI now supply a runnable engine ProjectPack through the existing pipeline; no core source or .NET compile/link protocol change is needed. Public contracts, actual outside implementation reads/edits, per-body rebuild scope and separate functional/structure gates are recorded in PACK_WORK_LOG.md. CHECKPOINT_1.md records target coverage and remaining limits. The complete version-1 Library baseline was read through 18 bounded text reads after original-byte materialization was blocked; complete extracted text is retained privately outside Git. The native Android app candidate is not represented as a completed APK/runtime result.

Source/specification/test publication to the public Confectory repository is now explicitly authorized. This supersedes the initial first-push approval hold. No generated binary, image, credential, raw chat log or original document is a publication candidate.
