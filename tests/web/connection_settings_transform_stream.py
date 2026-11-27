"""Exact settings-owner transform, ordinary CLI equivalence and stream fencing."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

HOST = [os.environ["CONFECTORY_DOTNET"], os.environ["CONFECTORY_ELEMENT_AUTHORING_HOST"]]


def start():
    process = subprocess.Popen(HOST + ["--inspect-stream"], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert process.stdout.readline().strip() == "CONFECTORY_INSPECT_STREAM_12"
    return process


def send(process, request):
    process.stdin.write(json.dumps(request) + "\n")
    process.stdin.flush()
    return process.stdout.readline()


def finish(process):
    if process.poll() is None:
        process.kill()
    process.wait(timeout=5)
    for pipe in (process.stdin, process.stdout, process.stderr):
        pipe.close()


with tempfile.TemporaryDirectory(prefix="confectory-settings-transform-") as directory:
    root = Path(directory)
    def owner(connection):
        path = root / "ai-settings" / hashlib.sha256(connection.encode()).hexdigest()[:16]
        path.mkdir(parents=True)
        return path / "project.cpack"

    a, b = owner("Test.Agent::Connection"), owner("Test.Other::Connection")
    text = "object Confectory.AISettings::Settings {data model = \"initial\";}\n"
    manifest = 'project Confectory.AISettings version "1" {standalone false; element Settings object "Settings.celem";}'
    for path in (a, b):
        path.write_text(manifest)
        path.with_name("Settings.celem").write_text(text)
    original = {file: file.read_bytes() for file in root.rglob("*") if file.is_file()}

    transform = dict(operation="setDataPath", text=text, path=["model"], value="changed")
    expected = json.loads(subprocess.run(HOST, input=json.dumps(transform), text=True,
                                         capture_output=True, check=True, timeout=20).stdout)
    assert expected["ok"]
    process = start()
    try:
        assert json.loads(send(process, dict(transform, _streamProject=str(a)))) == expected
        wrong = dict(transform, text='object Test.Other::Object {}')
        assert not json.loads(send(process, dict(wrong, _streamProject=str(a))))["ok"]
        # A failed identity validation does not poison subsequent reads.
        assert json.loads(send(process, dict(transform, _streamProject=str(a)))) == expected
        assert send(process, dict(transform, _streamProject=str(b))) == ""
        assert process.wait(timeout=5) == 2
    finally:
        finish(process)

    # Unsupported generic-project or non-string scopes retain the old one-shot path.
    for denied in (dict(transform, _streamProject=str(root / "project.cpack")),
                   dict(transform, _streamProject=str(a), value=12)):
        process = start()
        try:
            assert send(process, denied) == ""
            assert process.wait(timeout=5) == 2
        finally:
            finish(process)

    assert all(file.read_bytes() == data for file, data in original.items())
print("PASS settings transform equivalence, wrong identity, owner fencing, and no writes")
