"""Compilation and packaging belong to this build-target pack, not the core.

One JSON request/response; no compiler chatter on stdout. Uses SDK-provided C#
compiler and reference assemblies without running SDK CLI or NuGet restore.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def version_key(path):
    return tuple(int(x) if x.isdigit() else x for x in path.name.split("."))


def sdk():
    executable = os.environ.get("CONFECTORY_DOTNET") or shutil.which("dotnet")
    if not executable or not Path(executable).is_file():
        raise RuntimeError("Install the .NET 8 SDK or set CONFECTORY_DOTNET to its dotnet executable")
    dotnet = Path(executable).resolve()
    root = dotnet.parent
    candidates = [p for p in (root / "sdk").glob("8.*") if (p / "Roslyn/bincore/csc.dll").is_file()]
    if not candidates:
        raise RuntimeError("The target pack requires an installed .NET 8 SDK, not only a runtime")
    compiler = sorted(candidates, key=version_key)[-1] / "Roslyn/bincore/csc.dll"
    ref_roots = list((root / "packs/Microsoft.NETCore.App.Ref").glob("8.*"))
    if not ref_roots:
        raise RuntimeError("The SDK has no .NET 8 reference pack")
    references = sorted((sorted(ref_roots, key=version_key)[-1] / "ref/net8.0").glob("*.dll"))
    if not references or not list((root / "shared/Microsoft.NETCore.App").glob("8.*")):
        raise RuntimeError("The SDK has no complete .NET 8 references/runtime")
    return dotnet, compiler, references


def compile_csharp(request, dotnet, compiler, framework):
    out = Path(request["output"]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    name = request["name"]
    assembly = out / (name + ".dll")
    reference = out / (name + ".ref.dll")
    final = request["operation"] == "link"
    flags = ["-nologo", "-noconfig", "-nostdlib+", "-langversion:12", "-deterministic+",
             "-optimize+", "-nullable:enable", "-warnaserror+", "-target:exe" if final else "-target:library",
             f"-out:{assembly}"]
    if not final:
        flags.append(f"-refout:{reference}")
    flags += [f"-reference:{p}" for p in [*framework, *(Path(p) for p in request["references"])]]
    flags += request["sources"]
    env = dict(os.environ, DOTNET_CLI_TELEMETRY_OPTOUT="1", DOTNET_SKIP_FIRST_TIME_EXPERIENCE="1")
    r = subprocess.run([str(dotnet), str(compiler), *flags], text=True, capture_output=True, timeout=90, env=env)
    if r.returncode:
        raise RuntimeError(r.stdout.strip() + "\n" + r.stderr.strip())
    artifacts = {"assembly": str(assembly), "reference": str(reference)} if not final else {"application": str(assembly)}
    response = {"protocol": 1, "ok": True, "artifacts": artifacts}
    if final:
        for dependency in request["references"]:
            path = Path(dependency)
            destination = out / path.name
            if destination.exists() and sha(destination) != sha(path):
                raise RuntimeError(f"Conflicting package artifact {path.name}")
            shutil.copy2(path, destination)
        config = out / (name + ".runtimeconfig.json")
        config.write_text(json.dumps({"runtimeOptions": {"tfm": "net8.0", "framework": {
            "name": "Microsoft.NETCore.App", "version": "8.0.0"}, "rollForward": "LatestPatch"}}, indent=2) + "\n")
        artifacts["runtimeconfig"] = str(config)
        for resource in request.get("resources", []):
            source = Path(resource["path"])
            destination = out / resource["name"]
            if source != destination:
                shutil.copy2(source, destination)
            if resource["name"] == "public-linkage.json":
                artifacts["publicCatalog"] = str(destination)
        response["run"] = [str(dotnet), str(assembly)]
        mode = request.get("options", {}).get("mode", "portable")
        if mode == "linux":
            if platform.system() != "Linux":
                raise RuntimeError("The Linux launcher profile requires a Linux build host in this first tool pack")
            launcher = out / "run"
            launcher.write_text('#!/bin/sh\nexec "${CONFECTORY_DOTNET:-dotnet}" "$(dirname "$0")/Confectory.App.dll" "$@"\n')
            launcher.chmod(0o755)
            artifacts["launcher"] = str(launcher)
            response["run"] = [str(launcher)]
        elif mode != "portable":
            raise RuntimeError(f"Unsupported packaging mode {mode}")
    return response


def run(request):
    if request.get("protocol") != 1:
        raise RuntimeError("Unsupported target-tool protocol")
    dotnet, compiler, framework = sdk()
    operation = request.get("operation")
    if operation == "fingerprint":
        compiler_files = sorted(compiler.parent.glob("*.dll"))
        runtime = sorted((dotnet.parent / "shared/Microsoft.NETCore.App").glob("8.*"), key=version_key)[-1]
        identity = hashlib.sha256(json.dumps({"version": 1, "compiler": [(p.name, sha(p)) for p in compiler_files],
                                             "framework": [(p.name, sha(p)) for p in framework],
                                             "hostBinary": sha(dotnet), "runtime": [runtime.name, sha(runtime / "System.Private.CoreLib.dll")],
                                             "options": request.get("options", {}), "flags": "C#12/deterministic/nullable/warnings-as-errors",
                                             "host": platform.system() if request.get("options", {}).get("mode") == "linux" else "portable"}, sort_keys=True).encode()).hexdigest()
        return {"protocol": 1, "ok": True, "fingerprint": identity,
                "sdk": compiler.parents[2].name, "framework": "net8.0",
                "compiler": str(compiler), "mode": request.get("options", {}).get("mode", "portable")}
    if operation not in {"compile-contract", "compile-pack", "link"}:
        raise RuntimeError(f"Unknown tool operation {operation}")
    return compile_csharp(request, dotnet, compiler, framework)


if __name__ == "__main__":
    try:
        print(json.dumps(run(json.load(sys.stdin))))
    except Exception as ex:
        print(json.dumps({"protocol": 1, "ok": False, "error": str(ex)}))
        sys.exit(1)
