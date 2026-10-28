"""Exercise copy cleanup with a retained cross-published package and real engine.

Usage: python3 tests/probes/desktop_package_lifetime.py REPO PACKAGE [RUNTIME_FIXTURE]
All outputs are new isolated fixtures. Original packages/runtimes are hash checked;
no Windows apphost, login or paid inference is executed.
"""
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import time


def worker(mode, repo, package, reuse):
    if mode == "mid-copy":
        original = shutil.copytree

        def partial(source, destination, *args, **kwargs):
            if str(destination).endswith("owned checkout/Builds/Windows-x64"):
                shutil.copy2(Path(source) / "Confectory.dll", Path(destination) / "partial.dll")
                raise OSError("isolated exception during legacy package copy")
            return original(source, destination, *args, **kwargs)
        shutil.copytree = partial
    elif mode == "ui-failure":
        from playwright.sync_api import Page
        screenshot = Page.screenshot

        def failed_screenshot(page, *args, **kwargs):
            screenshot(page, *args, **kwargs)
            raise RuntimeError("isolated UI assertion after screenshot")
        Page.screenshot = failed_screenshot
    elif mode == "tamper-check-failure":
        original = subprocess.run

        def failed_check(command, *args, **kwargs):
            result = original(command, *args, **kwargs)
            asset = package / "content/examples/editor-home/ui/index.html"
            if "--check-package" in command and asset.read_bytes().endswith(b"fixture corruption"):
                assert result.returncode != 0, "Actual package check must reject tampering"
                raise OSError("isolated exception after real tamper rejection")
            return result
        subprocess.run = failed_check
    probe = repo / "tests/probes/desktop_package.py"
    sys.path.insert(0, str(probe.parent))
    sys.argv = [str(probe), str(repo), str(package)] + ([str(reuse)] if reuse else [])
    runpy.run_path(str(probe), run_name="__main__")


def main():
    repo, package = map(lambda p: Path(p).resolve(), sys.argv[1:3])
    reuse = Path(sys.argv[3]).resolve() if len(sys.argv) > 3 else None
    root = Path(tempfile.mkdtemp(prefix="confectory-package-lifetime-"))
    # Chromium's Unix-domain socket cannot fit a deeply nested evidence path.
    # This is a new browser-only directory; keep its evidence, never reuse or
    # remove an existing browser/profile directory.
    browser = Path(tempfile.mkdtemp(prefix="cfb-", dir=repo.parent))
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    files = {p.relative_to(package): p for p in package.rglob("*") if p.is_file()}
    original = {name: (sha(path), path.stat().st_nlink) for name, path in files.items()}
    runtime_files = {p: sha(p) for p in (reuse / "runtime only").rglob("*") if p.is_file()} if reuse else {}
    results = []
    modes = ["success", "success-repeat", "mid-copy", "ui-failure", "tamper-check-failure"]
    if reuse:
        modes.append("reuse")
    for mode in modes:
        case = root / mode
        case.mkdir()
        env = dict(os.environ, TMPDIR=str(case), CONFECTORY_BROWSER_TMP=str(browser))
        before = shutil.disk_usage(root).free
        # A byte-copied runtime/package is about 214 MiB; reserve room for the
        # real browser. Do not delete old output or silently skip a case.
        assert before > 300 * 1024 * 1024, (mode, before)
        command = [sys.executable, str(Path(__file__).resolve()), "--worker", mode, str(repo), str(package)]
        if mode == "reuse":
            command.append(str(reuse))
        print("START " + mode, flush=True)
        minimum_free = before
        peak_memory = 0
        with (case / "probe.log").open("x") as log:
            process = subprocess.Popen(command, cwd=repo, env=env, stdout=log, stderr=subprocess.STDOUT)
            started = time.monotonic()
            while process.poll() is None:
                minimum_free = min(minimum_free, shutil.disk_usage(root).free)
                peak_memory = max(peak_memory, int(Path("/sys/fs/cgroup/memory.current").read_text()))
                if time.monotonic() - started > 300:
                    raise TimeoutError(f"Inspect existing worker {process.pid}; do not duplicate {mode}")
                time.sleep(.2)
        expected_error = {"mid-copy": "OSError", "ui-failure": "RuntimeError", "tamper-check-failure": "OSError"}.get(mode)
        assert (process.returncode != 0) == bool(expected_error), (mode, process.returncode)
        fixtures = list(case.glob("confectory-desktop-package-*"))
        assert len(fixtures) == 1
        fixture = fixtures[0]
        cleanup = json.loads((fixture / "copy-cleanup.json").read_text())
        assert cleanup["cleanupSucceeded"] and cleanup["operationErrorType"] == expected_error, cleanup
        assert all(c["removed"] and not Path(c["path"]).exists() for c in cleanup["copies"])
        assert (fixture / "owned-data").is_dir() and (fixture / "unrelated cwd").is_dir()
        if mode in ["success", "success-repeat", "reuse", "ui-failure"]:
            assert (fixture / "packaged-login.png").is_file()
            assert (fixture / "packaged-host.log").is_file()
            assert (fixture / "owned checkout/.confectory/editor-home/retained-settings").read_bytes() == b"fixture user profile unchanged"
        assert {p.relative_to(package) for p in package.rglob("*") if p.is_file()} == set(files)
        assert {name: (sha(path), path.stat().st_nlink) for name, path in files.items()} == original
        assert {p: sha(p) for p in runtime_files} == runtime_files
        after = shutil.disk_usage(root).free
        assert before - after < 8 * 1024 * 1024, (mode, "Unexpected residual copy-sized allocation", before - after)
        row = {"mode": mode, "exit": process.returncode, "expectedErrorType": expected_error,
               "copiesRemoved": len(cleanup["copies"]), "evidence": str(fixture), "browserEvidence": str(browser),
               "retainedBytesDelta": before - after, "minimumFreeBytesSampled": minimum_free,
               "peakCgroupMemoryBytesSampled": peak_memory,
               "originalPackageAndRuntimeUnchanged": True}
        results.append(row)
        (root / "results.json").write_text(json.dumps(results, indent=2) + "\n")
        print(json.dumps(row), flush=True)
    print("PASS package copy lifetime; evidence: " + str(root), flush=True)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--worker"]:
        worker(sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5]) if len(sys.argv) > 5 else None)
    else:
        main()
