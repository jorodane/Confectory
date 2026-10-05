# Build core verification evidence

The new core passed **61 tests: 37 declaration/graph tests and 24 real compilation/integration tests**, with zero failures and zero skips. The full suite completed in 100.156 seconds on 2026-10-05. Two final catalog/provider-class boundary checks also passed after refining the catalog capability label and making the negative class-reference test name the actual generated provider type. See [the captured test output](test-output.txt) and [requirement map](REQUIREMENT_TEST_MAP.md).

## Specification and environment

All 20 sections of the attached 37-page “설계 기준 2” document were read from its complete DOCX body before code. The extraction contained 618 paragraphs/table rows and 41,571 characters. The original attachment's SHA-256 was rechecked and remained `3c255a726d58510a3691fbec23578f2f56318575fb3697dd7770cdbf161c2769`. No old repository was read, resumed or modified.

The Linux x86-64 environment was responsive: filesystem/Python operations, actual C# compilation and generated application execution all completed. The .NET 8.0.414 SDK and 8.0.20 runtime were used outside the repository. SDK `dotnet --info` encountered an environment-specific process-information exception; invoking SDK `csc.dll` and produced application DLLs directly worked. The target pack uses that direct path and requires no NuGet restore.

The requested 6.1 sol model could not be selected through a model-switching capability in this session. The implementation was completed in the current session; this report does not claim that 6.1 sol ran it.

## Reproduction

Install a .NET 8 SDK and Python 3.11+, then run from the repository root:

```sh
python -m unittest discover -v
```

Use `CONFECTORY_DOTNET` when `dotnet` is not on PATH. Integration tests explicitly skip without the SDK; those skips are not compilation evidence. The full output linked above records the actual SDK-enabled run.

## Runnable outputs

| Project and target | Actual stdout | Exit status |
| --- | --- | --- |
| `examples/app/project.cpack`, portable | `Hello Confectory from common` | 0 |
| `examples/app/project.cpack`, linux | `Hello Confectory from linux` | 0 |
| `examples/engine/project.cpack`, portable | `Confectory.Engine built as a ProjectPack` | 0 |
| Independent inherited/default consumer scopes | `5/102` | 0 |
| Recursive function implementation | `3` | 0 |

The example app included only `Example.App`, `Example.Api`, `Example.Provider`; `Example.Unused` and the build-time target tool pack were excluded from its executable graph/package. Each successful example contained its public linkage catalog. Reference-only compiler images were excluded from runtime packaging.

The engine example uses the same entry/target path as any other ProjectPack. It is a composition proof, not the complete engine or a self-hosted rewrite of the Python bootstrap.

## Incremental scope measurements

Controlled fixture: an app, a provider, a separately included unchanged `Stable` implementation, plus an API contract and target pack. Source changes were made between builds; every successful result was executed.

| Scenario | Implementation packs compiled | Packs reused | Contract artifacts compiled | Source documents read / parsed | Stdout |
| --- | --- | --- | --- | --- | --- |
| Cold initial build | App, Provider, Stable | — | 3 | 16 / 13 | 5 |
| No source change | — | App, Provider, Stable | 0 | 0 / 0 | 5 |
| Provider C# body only | Provider | App, Stable | 0 | 1 / 0 | 11 |
| API contract and consumer updated after rejected old consumer | App, Provider | Stable | 1 | 2 / 2 | 11 |

The old consumer failed with `CONTRACT_MISMATCH` when the API return type changed from `int` to `long`. After updating it, only the changed contract and the two affected packs rebuilt. The prior rejected check warmed declaration caches before the last measurement. Provider-only changes preserved the caller DLL's content hash and modification time; an old completed package continued producing its old output. Final bindings/package creation still runs for each successful build; the local implementation results above are reused.

Additional cold local checks compared 5 versus 45 registered packs. Both read **5 element/body documents**, with **0 unrelated element reads**. Initial small-manifest registration read 5 versus 45 manifests, respectively; this is not a claim that all startup reads are constant. An unrelated function-contract edit in the same API pack left consumer/provider DLLs unchanged. Contract source relocation kept its qualified identity and reused its artifact.

## Contract-only and failure boundaries

- A real consumer DLL compiled with no implementation provider registered; final build failed until the provider was added. The identical consumer DLL was then reused in the runnable final result.
- A separate experiment removed the registered provider's actual implementation declaration and C# file. Local compilation still succeeded without reading that implementation. Final build reported `MISSING_FILE`; restoring the provider rebuilt only Provider and reused App. It produced stdout `5`.
- Missing/duplicate namespace or element, wrong element kind, undeclared direct dependency, incompatible signature/function identity, distinct module defaults and structural cycles failed. Valid explicit/inherited bindings won over defaults; repeated paths to the same implementation deduplicated.
- Broken selected target C# failed compilation without falling back to common. C# with a bad argument type failed against the generated contract with `CS1503`. Direct typed references to a private provider class were not available to local compilation.
- Corrupt cached DLLs rebuilt; the repaired DLL was byte-identical to its original deterministic output. Tool revisions invalidated local results. Failed candidates preserved the previous `latest.json` and runnable output. Temporary incomplete artifacts were removed.
- Namespace-qualified IDs, public signatures, generated interface mappings, provider mappings, inherited metadata and per-scope links were retained in the versioned public catalog; absolute source paths were omitted.

## Remaining boundaries

The bootstrap supports synchronous primitive/array contracts and metadata/graph declarations. Full product schemas, asset pipelines, runtime owners/state/hot reload, UI/MVC, physics, input, editor, AI and collaboration remain later packs. Local compiled implementations are per pack; contracts are per function. Generated bindings are rebuilt at final link rather than cached as a completed package.

Only the portable .NET profile and Linux launcher were executed. Windows runtime execution, mobile, AOT, native apphosts and signing are unverified. Selected version directories are explicit registry choices; imported-pack copying/update management is not implemented. Declaration caches assume normal local filesystem changes, and concurrent writers to one ProjectPack are not yet a supported workflow.

The public catalog covers linked elements, not all unlinked authoring exports. Mod-enabled/disabled project builds, object-specific external-mod inheritance permission, optional main-game DLL authoring references and loader-pack runtime work are recorded in [the extension requirement](MOD_EXTENSION_BOUNDARY.md). MOD01–MOD06 are pending and not counted as passed tests. Patch mechanics, conflict ordering and security policy remain undecided; compiled code is not sandboxed.

Source, docs, examples and tests are the publication candidates. The original document, extracted specification, SDK, credentials, generated caches and binaries are excluded. Publication to the currently public new repository remains pending the user's requested first-push scope confirmation.
