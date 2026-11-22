"""Cancel a real Roslyn invocation through the Linux editor's Build Jobs window."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import NamedTuple

from playwright.sync_api import expect, sync_playwright

import v666_workspace_finder_fixture as fixture
from v821_build_jobs_ui import MARKERS, open_builds, receipt, seed, wait_state


class Process(NamedTuple):
    pid: int
    state: str
    parent: int
    start: str
    cpu_ticks: int
    arguments: list[bytes]


def process(pid):
    directory = Path("/proc") / str(pid)
    try:
        fields = (directory / "stat").read_text().rsplit(")", 1)[1].split()
        arguments = (directory / "cmdline").read_bytes().split(b"\0")
    except (FileNotFoundError, ProcessLookupError, PermissionError):
        return None
    return Process(pid, fields[0], int(fields[1]), fields[19], int(fields[11]) + int(fields[12]), arguments)


def active_compile(project, assembly):
    build_root = project.parent / ".confectory"
    for entry in Path("/proc").iterdir():
        if not entry.name.isdecimal():
            continue
        compiler = process(int(entry.name))
        if not compiler or compiler.state == "Z" or not compiler.cpu_ticks or len(compiler.arguments) < 4:
            continue
        if not compiler.arguments[1].endswith(b"/csc.dll") or not compiler.arguments[3].startswith(b"@"):
            continue
        response_file = Path(compiler.arguments[3][1:].decode())
        if not response_file.is_relative_to(build_root):
            continue
        try:
            if not any(line.startswith('"-out:') and line.endswith(f'/{assembly}"')
                       for line in response_file.read_text().splitlines()):
                continue
        except FileNotFoundError:
            continue

        target = process(compiler.parent)
        worker = process(target.parent) if target else None
        if worker and b"build-job" in worker.arguments:
            return compiler, target, worker
    return None


def retired(observed):
    current = process(observed.pid)
    return current is None or current.start != observed.start or current.state == "Z"


def check_compile_cancellation(page):
    project = fixture.projects[0]
    marker = MARKERS[0]
    page.locator("#run").click()
    run = page.locator(".run-window:visible")
    expect(run.locator(".caption strong")).to_have_text("실행 중", timeout=60000)
    run_key = run.get_attribute("data-key")
    owner = fixture.run("read", fixture.data(run_key))
    assert owner["handle"] and owner["state"] == "running"
    wait_state(page, lambda _: marker.exists())
    page.get_by_role("tab", name="Workspace", exact=True).click()

    outputs = project.parent / ".confectory" / "outputs" / owner["target"]
    latest = outputs / "latest.json"
    previous_report = latest.read_bytes()
    pack = json.loads(previous_report)["implementationArtifacts"]["Example.FrameLoop"]
    assembly = Path(pack["assembly"]).name
    previous_packages = {entry.name for entry in outputs.iterdir()}
    panel = open_builds(page)
    start = panel.get_by_role("button", name="빌드만", exact=True)
    stop = panel.get_by_role("button", name="이 빌드 중지", exact=True)
    status = panel.locator("[data-build-result-state]")
    body = project.parent / "Main.csbody"
    original = body.read_bytes()

    # This valid, uncached initializer keeps Roslyn busy without changing the
    # compiler/OS or injecting a result. It is never executed by the fixture.
    entries = ",\n".join(f'("fixture-{i:05}", {i})' for i in range(70000))
    slow_source = ('if (System.Environment.TickCount == 0) {\n'
                   f'var entries = new (string, int)[] {{\n{entries}\n}};\n'
                   'System.Console.WriteLine(entries.Length);\n}\n')
    body.write_bytes(slow_source.encode() + original)
    try:
        start.click()
        expect(status).to_have_text("컴파일 중", timeout=30000)
        active = wait_state(page, lambda state: any(row.get("phase") == "compiling" for row in state["buildJobs"]))
        job = next(row["job"] for row in active["buildJobs"] if row.get("phase") == "compiling")
        observed = None
        for _ in range(600):
            observed = active_compile(project, assembly)
            if observed:
                break
            page.wait_for_timeout(25)
        assert observed, "No real csc process for the fixture's implementation pack was observed"
        assert all(not retired(item) for item in observed)
        fixture.checked("Real csc has used CPU and its target tool and owned build worker are live before Stop")

        stop.click()
        expect(status).to_have_text("중지됨", timeout=15000)
        assert all(retired(item) for item in observed), observed
        stopped = receipt(project, job)
        assert stopped["state"] == stopped["phase"] == "stopped" and stopped["finishedUtc"]
        assert not any(field in stopped for field in ("key", "files", "output"))
        expect(panel.locator("[data-build-artifacts]")).to_have_text("")
        expect(panel.locator("[data-build-error]")).to_have_text("")
        expect(panel.get_by_role("button", name="기록된 파일 검증", exact=True)).to_be_disabled()
        assert latest.read_bytes() == previous_report
        assert {entry.name for entry in outputs.iterdir()} == previous_packages
        assert [row["input"]["job"] for row in fixture.requests if row["endpoint"] == "stopBuild"] == [job]
        fixture.checked("The compiler and worker have exited when the UI reports stopped, with no published package or success receipt")
    finally:
        body.write_bytes(original)

    current = fixture.run("read", owner)
    assert current["state"] == "running" and current["handle"] == owner["handle"]
    assert marker.read_text() == "run\n" and not MARKERS[1].exists()
    expect(start).to_be_enabled()
    start.click()
    expect(status).to_have_text("빌드 완료", timeout=60000)
    assert receipt(project, job) == stopped
    assert marker.read_text() == "run\n"
    page.locator(f'[data-window-tab="{run_key}"]').click()
    run.get_by_role("button", name="중단", exact=True).click()
    expect(run.get_by_role("button", name="재생", exact=True)).to_be_enabled()
    assert fixture.run("read", owner)["state"] == "stopped"
    fixture.original()
    assert not fixture.errors and not fixture.external
    fixture.checked("The separate Run survives cancellation and a subsequent Build succeeds without launching the project again")


def main():
    seed()
    # The separate Run must also work when the inherited TMPDIR would make
    # FrameControl's legacy relative pipe name exceed the Linux socket limit.
    with TemporaryDirectory(prefix="cf-cc-", dir="/tmp") as runtime_tmp:
        long_tmp = Path(runtime_tmp) / "editor-runtime-under-a-longer-temporary-directory"
        long_tmp.mkdir()
        fixture.env["TMPDIR"] = str(long_tmp)
        try:
            fixture.start(0)
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
                page = fixture.setup(browser)
                page.set_viewport_size({"width": 1850, "height": 1180})
                try:
                    check_compile_cancellation(page)
                except Exception:
                    page.screenshot(path=str(fixture.root / "failure.png"))
                    raise
                finally:
                    browser.close()
        finally:
            print("BUILD_COMPILING_CANCEL_FIXTURE", fixture.root)
            fixture.save_evidence()
            fixture.stop()


if __name__ == "__main__":
    main()
