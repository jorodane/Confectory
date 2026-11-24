"""Exercise the Linux CLI's incremental build across a nominal contract change."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


APP = "Incremental.App"
PROVIDER = "Incremental.Provider"
STABLE = "Incremental.Stable"


def symbol(value):
    return "E" + hashlib.sha256(json.dumps(value).encode()).hexdigest()[:24]


def stats(report, field):
    return set(report["statistics"][field])


def artifact(report, category, owner):
    item = report[category][owner]
    assembly = Path(item["assembly"])
    return item["key"], assembly, hashlib.sha256(assembly.read_bytes()).hexdigest()


def run(report, expected):
    result = subprocess.run(report["run"], capture_output=True, text=True, timeout=30)
    assert (result.returncode, result.stdout.strip()) == (0, expected), result


def exercise(repo, root):
    app, provider, stable = (root / name for name in ("app", "provider", "stable"))
    for directory in (app, provider, stable):
        directory.mkdir()
    dotnet = os.environ["CONFECTORY_DOTNET"]
    cli = repo / "src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll"
    manifest = app / "project.cproj"
    latest = app / ".confectory/outputs/portable/latest.json"
    nominal = f"Confectory.Reference.{symbol(PROVIDER)}.{symbol(PROVIDER + '::Info')}"

    def build(error=None):
        result = subprocess.run([dotnet, str(cli), "build", str(manifest), "portable"],
                                capture_output=True, text=True, timeout=120)
        if error:
            assert result.returncode != 0 and error in result.stderr, result
            return
        assert result.returncode == 0, result.stderr
        return json.loads(result.stdout)

    def provider_contract(result_type, body):
        (provider / "Value.celem").write_text(
            f"function {PROVIDER}::Value ({nominal} input) -> {result_type} "
            f"{{ provide {PROVIDER}::Value with {PROVIDER}::ValueBody; }}")
        (provider / "ValueBody.celem").write_text(
            f"implementation {PROVIDER}::ValueBody for {PROVIDER}::Value ({nominal} input) "
            f'-> {result_type} {{ body common "Value.csbody"; }}')
        (provider / "Value.csbody").write_text(body)

    def caller_import(result_type):
        (app / "MainBody.celem").write_text(
            f"implementation {APP}::MainBody for {APP}::Main () -> int {{ "
            f"import {PROVIDER}::Value as ProviderValue ({nominal}) -> {result_type}; "
            f"import {STABLE}::Value as StableValue () -> int; "
            'body common "Main.csbody"; }')

    target = repo / "targets/dotnet/pack.cpack"
    manifest.write_text(
        f'project {APP} version "1" {{ standalone true; entry {APP}::Main; '
        'element Main function "Main.celem"; element MainBody implementation "MainBody.celem"; '
        f'registry {PROVIDER} {json.dumps(str(provider / "pack.cpack"))}; dependency {PROVIDER} version "1"; '
        f'registry {STABLE} {json.dumps(str(stable / "pack.cpack"))}; dependency {STABLE} version "1"; '
        f'registry Confectory.Build.DotNet {json.dumps(str(target))}; '
        'dependency Confectory.Build.DotNet version "0.1.0"; target portable Confectory.Build.DotNet::Portable; }')
    (app / "Main.celem").write_text(f"function {APP}::Main () -> int {{ provide {APP}::Main with {APP}::MainBody; }}")
    (app / "Main.csbody").write_text('Console.WriteLine($"{calls.ProviderValue.Invoke(default)}/{calls.StableValue.Invoke()}"); return 0;')
    (provider / "pack.cpack").write_text(
        f'pack {PROVIDER} version "1" {{ element Info schema "Info.celem"; '
        'element Value function "Value.celem"; element ValueBody implementation "ValueBody.celem"; }')
    (provider / "Info.celem").write_text(f"schema {PROVIDER}::Info {{ field Count single general long; }}")
    (stable / "pack.cpack").write_text(
        f'pack {STABLE} version "1" {{ element Value function "Value.celem"; '
        'element ValueBody implementation "ValueBody.celem"; }')
    (stable / "Value.celem").write_text(f"function {STABLE}::Value () -> int {{ provide {STABLE}::Value with {STABLE}::ValueBody; }}")
    (stable / "ValueBody.celem").write_text(
        f'implementation {STABLE}::ValueBody for {STABLE}::Value () -> int {{ body common "Value.csbody"; }}')
    (stable / "Value.csbody").write_text("return 7;")
    protected = {path: path.read_bytes() for path in (
        manifest, app / "Main.celem", app / "Main.csbody", provider / "pack.cpack", provider / "Info.celem", *stable.iterdir())}

    provider_contract("int", "return 11;")
    caller_import("int")
    initial = build()
    run(initial, "11/7")
    assert stats(initial, "compiledPacks") == {APP, PROVIDER, STABLE}

    (provider / "Value.csbody").write_text("return 22;")
    body = build()
    assert stats(body, "compiledPacks") == {PROVIDER}
    assert stats(body, "reusedPacks") == {APP, STABLE}
    assert not stats(body, "compiledContractPacks")
    assert stats(body, "reusedContractPacks") == {APP, PROVIDER, STABLE}
    for pack in (APP, STABLE):
        assert artifact(body, "implementationArtifacts", pack) == artifact(initial, "implementationArtifacts", pack)
    assert body["key"] != initial["key"] and body["statistics"]["targetInvocations"]["link"] == 1
    run(body, "22/7")
    run(initial, "11/7")
    print("PASS body edit compiles only the provider and relinks; both outputs execute", flush=True)

    provider_contract("long", "return 4294967296L;")
    published = latest.read_bytes()
    build("CONTRACT_MISMATCH")
    assert latest.read_bytes() == published
    run(body, "22/7")
    print("PASS stale caller fails validation without changing the last runnable output", flush=True)

    caller_import("long")
    updated = build()
    run(updated, "4294967296/7")
    run(body, "22/7")
    assert updated["key"] != body["key"] and updated["statistics"]["targetInvocations"]["link"] == 1
    bindings = {(binding["function"], binding["implementation"]) for binding in updated["bindings"]}
    assert {(pack + "::Value", pack + "::ValueBody") for pack in (PROVIDER, STABLE)} <= bindings, bindings
    compiled = stats(updated, "compiledPacks")
    contracts = stats(updated, "compiledContractPacks")
    assert compiled == {APP, PROVIDER} and contracts == {PROVIDER}, (compiled, contracts)
    assert stats(updated, "reusedPacks") == {STABLE}
    assert stats(updated, "reusedContractPacks") == {APP, STABLE}
    for category, owner in (("contractArtifacts", STABLE + "::Value"), ("implementationArtifacts", STABLE)):
        reused = artifact(updated, category, owner)
        assert reused == artifact(body, category, owner)
        packaged = Path(updated["output"]) / reused[1].name
        assert hashlib.sha256(packaged.read_bytes()).hexdigest() == reused[2]
    assert all(path.read_bytes() == original for path, original in protected.items())
    print("PASS contract update rebuilds the provider and caller while both linked stable assemblies are reused")


if __name__ == "__main__":
    repository = Path(sys.argv[1]).resolve()
    with tempfile.TemporaryDirectory(prefix="confectory-incremental-") as fixture:
        exercise(repository, Path(fixture))
