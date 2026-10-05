# C# migration verification against 설계 기준 2

Verified from main commit **8876cdc65f881d48fcc3269f4cf0876570c48d39** (Quick Build Batch), including migration **f1774b77b15f3f41039702214704b2d039226257**. The attached 37-page specification has SHA-256 `3c255a726d58510a3691fbec23578f2f56318575fb3697dd7770cdbf161c2769`; all 20 sections were read. The commit containing this report identifies the verified snapshot (`git log -1 --format=%H` on the verification branch).

## Executed checks and environment

Linux x86-64, kernel 6.18.44, .NET SDK **8.0.425**, runtime **8.0.31**, 2026-10-05. The solution builds with **zero warnings/errors**. The full suite passes **77 tests, 0 failures, 148.721 seconds**: original 68 plus nine verification regressions. [Test output](test-output.txt), [build output](build-output.txt), [baseline failures](verification-baseline.txt), [cache observations](cache-observations.json), and [requirement map](REQUIREMENT_TEST_MAP.md) distinguish execution from inspection. Missing tools cause failures, not skips.

```sh
export CONFECTORY_DOTNET=/workspace/toolchains/dotnet-8.0.425/dotnet
export DOTNET_CLI_HOME=/tmp/confectory-dotnet-home
export NUGET_PACKAGES=/tmp/confectory-nuget-packages
mkdir -p /tmp/confectory-no-python-path
ln -sf "$CONFECTORY_DOTNET" /tmp/confectory-no-python-path/dotnet
ln -sf /bin/sh /tmp/confectory-no-python-path/sh
ln -sf /usr/bin/dirname /tmp/confectory-no-python-path/dirname
export PATH=/tmp/confectory-no-python-path
"$CONFECTORY_DOTNET" build Confectory.sln -c Release -m:1 -p:UseSharedCompilation=false --nologo
"$CONFECTORY_DOTNET" tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll
"$CONFECTORY_DOTNET" src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/app/project.cpack portable
"$CONFECTORY_DOTNET" src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/app/project.cpack linux
"$CONFECTORY_DOTNET" src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/engine/project.cpack portable
```

PATH contains no Python. Offline restore uses the included NuGet.Config. Generated app portable output: `Hello Confectory from common`; Linux launcher: `Hello Confectory from linux`; engine sample: `Confectory.Engine built as a ProjectPack`. All ran with exit 0. Original tests also execute scope-specific providers, inherited bodies, recursive functions and UTF-8 paths. The app package excludes Example.Unused and the build-time target pack.

## Prerequisites and packaging

Inspection finds no tracked Python source or Python subprocess dependency in core, CLI, target providers, scripts or tests. All executable repository components are C# plus the Windows batch. Historical untracked Python bytecode directories were not added to Git. An old managed-host setup script outside the repository still checks Python; it is not part of the verified repository build path.

| Operation | Prerequisite |
| --- | --- |
| Build core/CLI/provider/tests | .NET 8 SDK, writable outputs, platform libraries required by .NET |
| Compile/check/validate ProjectPack with bundled provider | Built Release target tool, .NET 8 SDK with Roslyn/framework references, owned pack sources |
| Start CLI/help or generated portable app | .NET 8 Microsoft.NETCore.App runtime and dotnet host; DLLs/runtimeconfig |
| Linux launcher | Same runtime, POSIX sh and dirname; CONFECTORY_DOTNET or dotnet on PATH |
| Windows batch | Windows command shell and .NET 8 SDK; execution untested here |

An isolated `/tmp/confectory-runtime-only` contains only dotnet, host/fxr and shared/Microsoft.NETCore.App/8.0.31 copied from the SDK installation, with **no sdk or packs directories**. With DOTNET_ROOT pointing there, DOTNET_MULTILEVEL_LOOKUP=0, and the restricted PATH above, `--list-sdks` returned nothing and `--list-runtimes` listed only the private runtime. Portable app, engine sample, CLI help and the Linux launcher ran with this runtime-only host. A CLI build using CONFECTORY_DOTNET=/tmp/confectory-runtime-only/dotnet failed, exit 1, with `TARGET_FAILURE: The target pack requires an installed .NET 8 SDK, not only a runtime`.

These are **framework-dependent** packages. There is no self-contained distribution; running with no runtime installation was not established. The isolated test verifies SDK-independent execution, not self-contained packaging. Windows batch/.exe execution, native apphosts, mobile, AOT and signing remain untested or absent. Linux results do not establish Windows behavior.

Runtime-only reproduction (replace the last DLL path with the generated report's application):

```sh
# Create this tree before restricting PATH, or use absolute mkdir/cp paths.
mkdir -p /tmp/confectory-runtime-only/host /tmp/confectory-runtime-only/shared
cp /workspace/toolchains/dotnet-8.0.425/dotnet /tmp/confectory-runtime-only/dotnet
cp -a /workspace/toolchains/dotnet-8.0.425/host/fxr /tmp/confectory-runtime-only/host/
cp -a /workspace/toolchains/dotnet-8.0.425/shared/Microsoft.NETCore.App /tmp/confectory-runtime-only/shared/
export DOTNET_ROOT=/tmp/confectory-runtime-only
export DOTNET_MULTILEVEL_LOOKUP=0
/tmp/confectory-runtime-only/dotnet --list-sdks
/tmp/confectory-runtime-only/dotnet --list-runtimes
/tmp/confectory-runtime-only/dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll --help
/tmp/confectory-runtime-only/dotnet <generated-output>/Confectory.App.dll
CONFECTORY_DOTNET=/tmp/confectory-runtime-only/dotnet <linux-output>/run
CONFECTORY_DOTNET=/tmp/confectory-runtime-only/dotnet /tmp/confectory-runtime-only/dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/app/project.cpack portable
# Last command must fail with the SDK-required diagnostic.
```

## Engine pack and core/provider boundary

| Component | Actual pack supply |
| --- | --- |
| Confectory.Engine ProjectPack | Boot function contract, entry ID Confectory.Engine::Boot, and BootBody print-and-return body only |
| Confectory.Build.DotNet | Portable/Linux target declarations and owned C# tool; compiler selection/flags/references, runtimeconfig, DLL copies and launcher packaging |
| Example API/provider/app packs | Demonstration contracts, bodies and bindings; no engine runtime subsystems |
| Core, CLI and provider binary bootstrap | Ordinary csproj/solution compilation; no complete corresponding ProjectPack declarations |

App and engine-labelled sample use the same ProjectPack + target + entry-ID pipeline. **This does not demonstrate engine self-hosting.** No test builds Confectory.Core, CLI or an actual engine runtime through packs. The specification's engine-as-a-ProjectPack requirement remains incomplete. Runtime owners/state/hot reload, UI/MVC, input, physics, editor, AI, collaboration, pack/update management and runtime mod loading remain deferred. No old Golemancer implementation or complete editor was added.

Source inspection confirms target compilation/packaging live in the provider. The bootstrap core resolves IDs/contracts/direct dependencies, inheritance/scopes and build plans, generates interface/binding glue, caches artifacts and delegates target operations. Its C# glue generator remains a bootstrap detail; it does not establish a fully pack-supplied engine.

## Reproduced defects and fixes

Seven new regressions against unchanged baseline failed: **0 passed, 7 failed, 25.771 s**. Direct implementation traversal could mark a pack included without selecting its implementation: no DLL, selected-body validation or import dependency closure. Bad bodies, missing target bodies, incompatible contracts and unscoped root imports were silently omitted. Local Check(App) also compiled MainBody + UnusedBody into one DLL, while final selection of MainBody produced a different DLL and unnecessarily rebuilt App.

Planner traversal now selects/validates implementations reached through always, use, containment and module edges; includes their contracts and declared import closure; and retains consumer context. An always-root import without explicit `in Namespace::Consumer` fails IMPLEMENTATION_SCOPE with a source diagnostic. Success and invalid C# bodies are tested for all three direct paths; module inclusion is separately exercised. Unused invalid bodies remain pruned in final builds but fail local whole-pack checking. Existing inheritance, ownership, recursion, cycle and failure-preservation tests still pass.

Local artifacts now compile/cache **per implementation within its owning pack**, against public contracts/framework references only. Local full-pack checking and final selected subsets use identical keys. Linking/catalog generation use every selected DLL. `assemblies` and ID-keyed `implementationArtifacts` enumerate all DLLs; legacy `assembly`/`reference` identify the first only. This increases cold compiler calls/file counts for multi-implementation packs but preserves dependency boundaries and prevents unused implementations from invalidating unchanged consumers.

## Observed compilation and invalidation

App owns MainBody and UnusedBody. MainBody imports Api::Value; Provider::ValueBody supplies it. JSON evidence records artifact names/keys; regression assertions compare caller DLL hash and mtime before/after unused-body local rechecking.

| Scenario | Contract compilations | Implementation compilations | Final bindings compilation |
| --- | --- | --- | --- |
| Cold local Check(App) | Main, Value, Spare | MainBody, UnusedBody | none |
| Final after check | none | ValueBody; MainBody reused | 1 |
| No changes | none | none | 1 |
| Unused body change, final | none | none; unused body not read | 1 |
| Local recheck after unused change | none | UnusedBody only; MainBody reused | none |
| Final after recheck | none | none | 1 |
| Used main body change | none | MainBody only; Provider reused | 1 |
| Value contract int to long | Value only | MainBody and ValueBody after declarations updated | 1 |

The old incompatible import first fails CONTRACT_MISMATCH. Contract keys invalidate observing implementations; provider body changes never enter caller keys. Existing tests check provider-only and unrelated-contract changes preserve unaffected DLLs.

No-change/unused-body final builds read/parse zero requested source documents on this Linux filesystem, but still perform target fingerprinting and **one real final compiler/link operation**. Fingerprinting hashes SDK/compiler/framework files; cache validation hashes artifacts; packaging copies DLLs. Zero source reads or zero local compilation do not imply zero compilation, negligible I/O or cheap incremental builds. Final link output is not cached. Windows cache fallback and timing were not executed.
