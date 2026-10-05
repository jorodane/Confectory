# C# build core verification

The C# replacement passes **68 tests: 40 declaration/graph tests and 28 compilation/integration tests**, with zero failures on Linux. The full run completed in **108.774 seconds**. The original 61 cases were ported to C#; seven additional cases cover CLI JSON/exit codes, full validation, UTF-8 and spaced paths, invalid source encoding, symlink ownership, corrupt declaration caches and out-of-root compiler artifacts. See [captured output](test-output.txt) and [requirement map](REQUIREMENT_TEST_MAP.md).

The solution builds with **zero warnings and zero errors**. The core, CLI, target compiler/packager and test runner are C# projects. The former Python sources and tests have been removed; neither Python nor third-party NuGet packages are needed to build or execute them.

## Environment and reproduction

Verified on 2026-10-05 with Linux x86-64, .NET SDK **8.0.425** and runtime **8.0.31**. The SDK resides outside the repository. The checkout's `NuGet.Config` clears external feeds, and all projects restore from the installed framework without downloading packages.

```sh
dotnet build Confectory.sln -c Release
dotnet tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll
```

The bundled target declarations locate the Release tool DLL, so build the solution before using the CLI. Set `CONFECTORY_DOTNET` if `dotnet` is not on PATH. In the managed verification environment, a read-only home required a writable `DOTNET_CLI_HOME`; restricted MSBuild workers required `-m:1 -p:UseSharedCompilation=false`. These settings do not change core or pack semantics.

The tests use a dependency-free console runner. A missing compiler/tool is a failure, not an integration skip. An optional name substring limits a run, for example appending `CoreTests`. The captured full run executes every case on Linux.

## Actual sample executions

Each sample was built through the C# CLI and its returned command was executed.

| Project and target | Stdout | Exit status |
| --- | --- | --- |
| `examples/app/project.cpack`, portable | `Hello Confectory from common` | 0 |
| `examples/app/project.cpack`, linux | `Hello Confectory from linux` | 0 |
| `examples/engine/project.cpack`, portable | `Confectory.Engine built as a ProjectPack` | 0 |
| Independent inherited/default consumer scopes | `5/102` | 0 |
| Recursive function implementation | `3` | 0 |
| UTF-8 project path containing spaces | `안녕하세요`, then `5` | 0 |

The example app includes only `Example.Api`, `Example.App` and `Example.Provider`; `Example.Unused` and the build-time target pack are excluded. Its cold portable build reads 12 documents, parses 10, and compiles two contracts and two implementation packs. The public linkage catalog preserves qualified identities/contracts/providers without absolute source paths, and reference-only images are excluded from runtime packaging.

The engine sample uses the identical ProjectPack/target path. The core itself is now a C# library; building that library through its own pack declarations remains separate work.

## Preserved behavior

| Change or operation | Verified result |
| --- | --- |
| No source changes | Zero contract/pack recompilations; zero source reads/parses on the verified Linux filesystem |
| Provider body only | Only Provider recompiles; App DLL hash and modification time stay unchanged; new output is `11`, old package still produces `5` |
| API contract changes | Old consumer fails `CONTRACT_MISMATCH`; updated App and Provider rebuild; Stable is reused; only the changed contract recompiles |
| Unrelated contract or 40 unrelated packs | No unrelated element/body reads or unnecessary consumer recompilation |
| Contract document relocation | Qualified identity and local DLLs are retained |
| Contract-only local check | A real consumer DLL compiles without provider implementation; that DLL is reused after final linkage becomes complete |
| Invalid selected target body | Compilation fails against its real source location; no silent common fallback |
| Cache/tool revision | Corrupt DLLs are rebuilt; a changed owned tool binary invalidates local artifacts |
| Failed compilation | Previous `latest.json` and runnable output remain intact; pending directories are cleaned |
| Inheritance/defaults | Child overrides, provenance, scope bindings and deduplicated defaults retain their previous behavior |
| Graph errors | Missing/wrong-kind references, undeclared dependencies and structural cycles fail; ordinary reference cycles and function recursion execute |
| Cache/source/CLI boundaries | Restored mtime does not return stale data; invalid caches are reparsed; malformed UTF-8 and escaped paths report errors; CLI emits JSON and expected exit codes |

Linux declaration-cache reuse includes `statx` change time and file identity. Where reliable change stamps are unavailable, the core rereads only requested documents instead of trusting mtime/size. C# cache keys are separate from the prior implementation, so existing pack sources need no conversion.

## Remaining scope

Windows execution, mobile platforms, signing, AOT and native application packaging have not been verified. The existing synchronous primitive/array contract language and graph/metadata semantics remain the supported surface. Runtime owners/state/hot reload, UI/MVC, physics, input, editor, AI, collaboration and imported-pack update management remain later packs. Concurrent writers to one ProjectPack remain unsupported.

The public catalog covers linked elements. Mod build modes, external-mod inheritance permission and runtime loading remain pending requirements in [the mod extension boundary](MOD_EXTENSION_BOUNDARY.md). They are not counted as current passes. Source changes are local to this checkout; repository publication is a separate action.
