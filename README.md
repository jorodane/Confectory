# Confectory build core

A specification-derived build bootstrap for **ProjectPack + target**. It resolves namespace-qualified pack elements, generates C# contracts, compiles owned implementations locally, and links actual providers through a build-target pack. Runtime, UI, physics, editor and mod loading are later packs.

Read [technical design](docs/TECHNICAL_DESIGN.md), [requirement-to-test map](docs/REQUIREMENT_TEST_MAP.md), [declaration format and tool protocol](docs/FORMAT.md), [verification evidence](docs/VERIFICATION.md), and [mod extension boundary](docs/MOD_EXTENSION_BOUNDARY.md).

## Run from the repository root

Requirements: Python 3.11+ and the .NET 8 **SDK**. No third-party Python packages, NuGet restore, old repository, game assets or implicit game paths are needed. The target pack discovers `dotnet` on PATH; alternatively set `CONFECTORY_DOTNET` to the actual executable (`dotnet.exe` on Windows).

```sh
python -m unittest discover -v
python -m confectory build examples/app/project.cpack portable
python -m confectory check examples/app/project.cpack portable Example.App
python -m confectory validate examples/app/project.cpack portable
python -m confectory build examples/engine/project.cpack portable
```

Linux can also use the `linux` target, which selects Linux bodies before common bodies and produces a shell launcher. Use `python3` if that is your Python executable. Tests explicitly report integration skips when the SDK is absent; those skips do not verify compilation.

The CLI prints JSON including a `run` command, included/excluded packs, source-read statistics and compiled/reused artifacts. To compile and execute directly:

```python
import subprocess
from confectory.build import Builder

report = Builder("examples/app/project.cpack", "portable").build()
subprocess.run(report["run"], check=True)
```

The app prints `Hello Confectory from common` for portable, or `Hello Confectory from linux` for Linux. The engine composition sample prints `Confectory.Engine built as a ProjectPack`; it proves the common build path, not a complete engine or a self-hosted bootstrap.

Generated state is isolated beneath the selected ProjectPack's `.confectory/`: per-document caches, content-addressed local artifacts and unique final output directories. A failed candidate leaves the previous successful output and `latest.json` intact. Source packs are not modified by builds. No push occurs until publication scope is confirmed.

## Current limits

Contracts support synchronous primitive C# types (`void`, `bool`, `int`, `long`, `float`, `double`, `string`) and one-dimensional arrays. Exact dependency version expectations and `*` are supported; a mismatch warns. The registry chooses a concrete manifest path and never searches for a newer version or rewrites that choice. Versioned imported-pack installation/update management is later pack work.

The initial target pack produces framework-dependent .NET 8 assemblies, portable packaging and a Linux launcher. Windows execution, Android/iOS, native apphosts, signing, AOT and runtime DLL replacement are not verified here. Filesystem change stamps assume normal local-source edits; builds are currently intended for one writer per ProjectPack. Generated bindings compose functions per consumer scope; persistent runtime instance state belongs in runtime packs.

Generic schema/object/view declarations carry owned metadata and graph relationships only; this core does not claim complete product schema/UI semantics. The public catalog describes the linked surface. Whole-project authoring exports, mod build-mode controls and the object-specific external-mod inheritance flag are recorded requirements for their next stage. Compiled C# and target tools are trusted executable code; this bootstrap provides no security sandbox.
