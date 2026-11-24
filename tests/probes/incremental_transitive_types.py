"""Check invalidation and type checking across a public nominal type dependency."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from incremental_nominal_contracts import artifact, run, stats, symbol


MODEL = "Transitive.Model"
API = "Transitive.Api"
APP = "Transitive.App"
STABLE = "Transitive.Stable"
SHAPE = MODEL + "::Shape"
ENVELOPE = API + "::Envelope"


def nominal(identity, kind="Information"):
    namespace = identity.split("::")[0]
    return f"Confectory.{kind}.{symbol(namespace)}.{symbol(identity)}"


def elements(*declarations):
    return "".join(f'element {name} {kind} "{name}.celem"; ' for name, kind in declarations)


def exercise(repo, root):
    model, api, app, stable = (root / name for name in ("model", "api", "app", "stable"))
    for directory in (model, api, app, stable):
        directory.mkdir()
    dotnet = os.environ["CONFECTORY_DOTNET"]
    cli = repo / "src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll"
    manifest = app / "project.cproj"
    latest = app / ".confectory/outputs/portable/latest.json"
    shape = model / "Shape.celem"

    def build():
        return subprocess.run([dotnet, str(cli), "build", str(manifest), "portable"],
                              capture_output=True, text=True, timeout=120)

    def successful_build():
        result = build()
        assert result.returncode == 0, result.stderr + result.stdout
        return json.loads(result.stdout)

    def set_field_type(field_type):
        shape.write_text(f"schema {SHAPE} {{ field Count single general {field_type}; }}")

    def function(directory, namespace, name, return_type, body, imports=""):
        identity = f"{namespace}::{name}"
        (directory / f"{name}.celem").write_text(
            f"function {identity} () -> {return_type} {{ provide {identity} with {identity}Body; }}")
        (directory / f"{name}Body.celem").write_text(
            f"implementation {identity}Body for {identity} () -> {return_type} "
            f'{{ {imports} body common "{name}.csbody"; }}')
        (directory / f"{name}.csbody").write_text(body)

    set_field_type("int")
    (model / "pack.cpack").write_text(
        f'pack {MODEL} version "1" {{ ' + elements(("Shape", "schema"), ("Make", "function"), ("MakeBody", "implementation")) + "}")
    function(model, MODEL, "Make", nominal(SHAPE), "return new() { Count = 23 };")

    (api / "pack.cpack").write_text(
        f'pack {API} version "1" {{ dependency {MODEL} version "1"; '
        + elements(("Envelope", "schema"), ("Read", "function"), ("ReadBody", "implementation")) + "}")
    (api / "Envelope.celem").write_text(f"schema {ENVELOPE} {{ field Value single compound {SHAPE}; field Live single reference {SHAPE}; }}")
    function(api, API, "Read", nominal(ENVELOPE), "return new() { Value = calls.Make.Invoke() };",
             f"import {MODEL}::Make as Make () -> {nominal(SHAPE)};")

    (stable / "pack.cpack").write_text(f'pack {STABLE} version "1" {{ ' + elements(("Read", "function"), ("ReadBody", "implementation")) + "}")
    function(stable, STABLE, "Read", "int", "return 7;")

    target = repo / "targets/dotnet/pack.cpack"
    manifest.write_text(
        f'project {APP} version "1" {{ standalone true; entry {APP}::Main; '
        + elements(("Main", "function"), ("MainBody", "implementation"))
        + "".join(f"registry {name} {json.dumps(str(directory / 'pack.cpack'))}; "
                  for name, directory in ((MODEL, model), (API, api), (STABLE, stable)))
        + f'dependency {API} version "1"; dependency {STABLE} version "1"; '
        + f'registry Confectory.Build.DotNet {json.dumps(str(target))}; '
        + 'dependency Confectory.Build.DotNet version "0.1.0"; target portable Confectory.Build.DotNet::Portable; }')
    # The caller names only API and Stable. It actually uses the transitive value
    # and reference types through the returned envelope, with no Model dependency.
    function(app, APP, "Main", "int", '''
var result = calls.Read.Invoke();
long count = result.Value.Count;
if (result.Live.IsBound || result.Live.GetType().Assembly != result.Value.GetType().Assembly) return 1;
Console.WriteLine($"{result.Value.Count.GetType().Name}:{count}/{calls.StableRead.Invoke()}");
return 0;
''', f"import {API}::Read as Read () -> {nominal(ENVELOPE)}; import {STABLE}::Read as StableRead () -> int;")
    protected = {path: path.read_bytes() for directory in (model, api, app, stable)
                 for path in directory.iterdir() if path != shape}

    first = successful_build()
    run(first, "Int32:23/7")
    warm = successful_build()
    assert not stats(warm, "compiledPacks") and not stats(warm, "compiledContractPacks")
    assert warm["key"] == first["key"]

    set_field_type("long")
    updated = successful_build()
    assert stats(updated, "compiledPacks") == {MODEL, API, APP}, updated["statistics"]
    assert stats(updated, "compiledContractPacks") == {MODEL, API}
    assert stats(updated, "reusedPacks") == {STABLE}
    assert stats(updated, "reusedContractPacks") == {APP, STABLE}
    assert updated["key"] != first["key"] and updated["statistics"]["targetInvocations"]["link"] == 1
    for category, owner in (("contractArtifacts", STABLE + "::Read"), ("implementationArtifacts", STABLE)):
        assert artifact(updated, category, owner) == artifact(first, category, owner)
    for pack in (MODEL, API, APP):
        assert artifact(updated, "implementationArtifacts", pack)[0] != artifact(first, "implementationArtifacts", pack)[0]

    def public_types(report):
        catalog = json.loads(Path(report["publicCatalog"]).read_text())
        return {item["clrType"]: item for item in catalog["informationTypes"]}

    before_types, after_types = public_types(first), public_types(updated)
    assert before_types.keys() == after_types.keys() == {nominal(SHAPE), nominal(SHAPE, "Reference"), nominal(ENVELOPE)}
    for clr_type, before in before_types.items():
        after = after_types[clr_type]
        assert (before["id"], before["assembly"]) == (after["id"], after["assembly"])
        assert before["shapeHash"] != after["shapeHash"], clr_type
    envelope = after_types[nominal(ENVELOPE)]
    assert {item["clrType"]: item["shapeHash"] for item in envelope["dependencies"]} == {
        clr_type: after_types[clr_type]["shapeHash"] for clr_type in (nominal(SHAPE), nominal(SHAPE, "Reference"))}
    assert updated["bindings"] == first["bindings"]
    run(updated, "Int64:23/7")
    run(first, "Int32:23/7")
    print("PASS a model-only change rebuilds the transitive caller and reuses the linked independent pack", flush=True)

    set_field_type("double")
    published = latest.read_bytes()
    rejected = build()
    assert rejected.returncode != 0 and "CS0266" in rejected.stderr and "Main.csbody" in rejected.stderr, rejected
    assert latest.read_bytes() == published
    run(updated, "Int64:23/7")
    print("PASS a model-only incompatible change fails in the caller and preserves the last runnable build", flush=True)

    set_field_type("long")
    restored = successful_build()
    assert restored["key"] == updated["key"]
    assert not stats(restored, "compiledPacks") and not stats(restored, "compiledContractPacks")
    assert all(path.read_bytes() == original for path, original in protected.items())
    run(restored, "Int64:23/7")
    print("PASS restoring the exact model contract reuses the validated output inputs", flush=True)


if __name__ == "__main__":
    repository = Path(sys.argv[1]).resolve()
    with tempfile.TemporaryDirectory(prefix="confectory-transitive-") as fixture:
        exercise(repository, Path(fixture))
