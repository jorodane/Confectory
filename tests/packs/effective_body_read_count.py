"""Check metadata read accounting and body ownership without executing bodies.

Run with CONFECTORY_DOTNET, CANDIDATE_TOOL [BASELINE_TOOL].
The optional baseline compares exact public replies for the same sources.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

candidate = sys.argv[1]
baseline = sys.argv[2] if len(sys.argv) > 2 else None
dotnet = os.environ["CONFECTORY_DOTNET"]

def query(tool, request):
    return json.loads(subprocess.run([dotnet, tool], input=json.dumps(request),
                                     text=True, capture_output=True, check=True, timeout=30).stdout)

with tempfile.TemporaryDirectory(prefix="cf-body-read-count-") as tmp:
    for count in (40, 400):
        root = Path(tmp) / str(count)
        root.mkdir()
        manifest = root / "project.cpack"
        rows = ['element Info schema "Info.celem";', 'element F function "F.celem";',
                'element Body implementation "Body.celem";', 'element Other implementation "Other.celem";']
        (root / "Info.celem").write_text("schema Synthetic::Info { field Count single general long; }")
        (root / "F.celem").write_text("function Synthetic::F () -> int { provide Synthetic::F with Synthetic::Body; }")
        for i in range(count):
            name = f"Item{i:04}"
            (root / f"{name}.celem").write_text(f"object Synthetic::{name} {{ use schema Synthetic::Info; data Count = {i}; }}")
            rows.append(f'element {name} object "{name}.celem";')
        manifest.write_text('project Synthetic version "1" { standalone false; ' + " ".join(rows) + " }")
        request = dict(operation="effective", project=str(manifest), manifest=manifest.read_text(),
                       id="Synthetic::Item0000", text=(root / "Item0000.celem").read_text(),
                       drafts=[], schemaView=True, validateObjects=True, observeSources=True)
        def bodies(path):
            for name in ("Body", "Other"):
                (root / f"{name}.celem").write_text(
                    f'implementation Synthetic::{name} for Synthetic::F () -> int {{ body common "{path}"; }}')
        def check(expected):
            actual = query(candidate, request)
            if baseline:
                assert actual == query(baseline, request), "Public metadata reply changed"
            assert actual["ok"], actual
            result = actual["result"]
            if expected is None:
                assert result["status"] == "unavailable" and result["code"] == "OWNERSHIP", result
            else:
                assert result["status"] == "available" and result["bodyReads"] == expected, result
            return result
        bodies("body.csbody")
        (root / "body.csbody").write_text("return 0;")
        check(0)  # No body read simply because a locator exists.
        bodies("Item0001.celem")
        check(1)  # Two locators to one actually read document still count one read.
        bodies("../outside.csbody")
        (root.parent / "outside.csbody").write_text("return 0;")
        check(None)
        if os.name == "posix":
            (root / "outside-link.csbody").symlink_to(root.parent / "outside.csbody")
            bodies("outside-link.csbody")
            check(None)
        bodies("body.csbody")
        check(0)  # Later queries read current declarations; no persistent cache.
        print(f"PASS {count}: exact count, duplicate paths, body ownership, fresh source", flush=True)
