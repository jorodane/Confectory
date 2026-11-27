"""Exact reference preparation over project-scoped read-only stream 12."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

host = [os.environ["CONFECTORY_DOTNET"], sys.argv[1]]
with tempfile.TemporaryDirectory(prefix="cf-reference-prepare-") as tmp:
    root = Path(tmp)
    project = root / "first"
    project.mkdir()
    manifest = project / "project.cpack"
    contents = {
        "Link": ("object", 'object Alpha::Link { use schema Alpha::LinkInfo; data Target = Alpha::One; }'),
        "LinkInfo": ("schema", 'schema Alpha::LinkInfo { field Target single reference Alpha::TargetInfo; }'),
        "TargetInfo": ("schema", 'schema Alpha::TargetInfo { field Count single general long; }'),
        "One": ("object", 'object Alpha::One { use schema Alpha::TargetInfo; data Count = 0; }'),
        "Two": ("object", 'object Alpha::Two { use schema Alpha::TargetInfo; data Count = 7; value editorName = "Two"; }'),
        "Wrong": ("object", 'object Alpha::Wrong {}'),
    }
    manifest.write_text('project Alpha version "1" { ' + " ".join(
        f'element {key} {kind} "{key}.celem";' for key, (kind, _) in contents.items()) + " }")
    for name, (_, text) in contents.items():
        (project / (name + ".celem")).write_text(text)
    peer = root / "second"
    shutil.copytree(project, peer)

    def unit(path, kind):
        text = path.read_text()
        return dict(kind=kind, path=path.name, draft=text, original=text,
                    baseline=hashlib.sha256(text.encode()).hexdigest(), revision=1)

    def requests(target="Two", folder=project):
        path = folder / "project.cpack"
        units = {"Alpha::ProjectManifest": unit(path, "project")}
        units.update({"Alpha::" + name: unit(folder / (name + ".celem"), kind)
                      for name, (kind, _) in contents.items()})
        change = dict(type="data", path=["Target"],
                      contract=dict(kind="reference", cardinality="single", type="Alpha::TargetInfo"),
                      valueJson=json.dumps({"$ref": "Alpha::" + target}))
        declaration = dict(id="Alpha::Link", hash=units["Alpha::Link"]["baseline"], changes=[change])
        yield dict(operation="mixedOwnerCopyEdits", project=str(path), manifest=path.read_text(),
                   id="Alpha::Link", text=units["Alpha::Link"]["draft"], changes=[change],
                   drafts=[], units=units, reuseLongPreparation=True)
        for operation in ("informationBodyGroupGuards", "informationPropertyGroupGuards", "informationTypeGuards"):
            yield dict(operation=operation, action="prepare", project=str(path), namespace="Alpha",
                       units=units, declaration=declaration)

    def ordinary(request):
        return json.loads(subprocess.run(host, input=json.dumps(request), text=True,
                                         capture_output=True, timeout=20, check=True).stdout)

    def start():
        process = subprocess.Popen(host + ["--inspect-stream"], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert process.stdout.readline().strip() == "CONFECTORY_INSPECT_STREAM_12"
        return process

    def send(process, request):
        process.stdin.write(json.dumps(request) + "\n")
        process.stdin.flush()
        line = process.stdout.readline()
        return None if not line else json.loads(line)

    def final_graph(process, target="Two", overlay=False):
        # The final SlotBatch query uses the same full graph/schema/reference
        # validation flags and the same current draft bytes as one-shot effective.
        after = contents["Link"][1].replace("Alpha::One", "Alpha::" + target)
        drafts = [{"id": "Alpha::" + name, "text": (project / (name + ".celem")).read_text()}
                  for name in contents if name != "Link"] if overlay else []
        payload = dict(operation="effective", project=str(manifest), manifest=manifest.read_text(),
                       id="Alpha::Link", text=after, drafts=drafts, schemaView=True,
                       validateObjects=True, observeSources=True)
        expected = ordinary(payload)
        actual = send(process, dict(payload, operation="inspectEffective", kind="object"))
        assert expected["ok"] and actual["ok"] and actual["result"]["effective"] == expected["result"], (expected, actual)
        return expected["result"]

    proc = start()
    try:
        initial = list(requests())
        for request in initial:
            expected = ordinary(request)
            assert expected["ok"], expected
            assert send(proc, request) == expected
        for overlay in (False, True):
            valid = final_graph(proc, overlay=overlay)
            assert valid["status"] == "available" and valid["schemaModel"]["validation"]["status"] == "valid", valid
            invalid = final_graph(proc, "Wrong", overlay=overlay)
            assert invalid["status"] != "available" or invalid["schemaModel"]["validation"]["status"] != "valid", invalid
        target = project / "Two.celem"
        raw = target.read_bytes()
        stamp = target.stat()
        target.write_text(raw.decode().replace('"Two"', '"Renamed"'))
        os.utime(target, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        for request in requests():
            assert send(proc, request) == ordinary(request)
        renamed = final_graph(proc)
        assert renamed["status"] == "available"
        target.write_text('object Alpha::Two { use schema Alpha::LinkInfo; }')
        invalid = final_graph(proc)
        assert invalid["status"] != "available" or invalid["schemaModel"]["validation"]["status"] != "valid", invalid
        for request in requests():
            assert send(proc, request) == ordinary(request)
        target.write_bytes(raw)
        for bad in ("Wrong", "Missing"):
            request = next(requests(bad))
            expected = ordinary(request)
            assert not expected["ok"] and send(proc, request) == expected
        for request in requests():
            assert send(proc, request) == ordinary(request)
        assert send(proc, next(requests(folder=peer))) is None
        assert proc.wait(timeout=5) == 2
    finally:
        if proc.poll() is None:
            proc.kill()
        proc.wait()

    proc = start()
    try:
        assert final_graph(proc)["status"] == "available"
        foreign_query = dict(operation="inspectEffective", project=str(peer / "project.cpack"),
                             manifest=(peer / "project.cpack").read_text(), id="Alpha::Link",
                             kind="object", text=contents["Link"][1], drafts=[],
                             schemaView=True, validateObjects=True, observeSources=True)
        assert send(proc, foreign_query) is None and proc.wait(timeout=5) == 2
    finally:
        if proc.poll() is None:
            proc.kill()
        proc.wait()

    # A multi-field or raw edit retains ordinary one-shot handling. The
    # read-only reference stream must not expand its accepted shape.
    for extra in ({"rawText": contents["Link"][1]},
                  {"changes": [initial[0]["changes"][0], dict(type="description", text="mixed")]}):
        proc = start()
        try:
            assert send(proc, dict(initial[0], **extra)) is None
            assert proc.wait(timeout=5) == 2
        finally:
            if proc.poll() is None:
                proc.kill()
            proc.wait()
    assert (project / "Link.celem").read_text() == contents["Link"][1]
    assert (peer / "Link.celem").read_text() == contents["Link"][1]
print("PASS preparation and final graph one-shot equivalence, fresh retype/rename, invalid targets, project scope and unsupported-shape refusal")
