"""Verify the desktop project dock against the real Linux editor and disposable projects."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time

from playwright.sync_api import expect, sync_playwright

from editor_navigation import goto_editor


def make_project(root, repo, name, output):
    project = root / name
    project.mkdir()
    manifest = project / "project.cpack"
    manifest.write_text(
        f'project Dock.{name} version "1.0.0" {{ standalone true;\n'
        f'registry Confectory.Build.DotNet "{repo}/targets/dotnet/pack.cpack";\n'
        'dependency Confectory.Build.DotNet version "0.1.0";\n'
        'target linux Confectory.Build.DotNet::Linux;\n'
        f'entry Dock.{name}::Main; element Main function "Main.celem";\n'
        'element MainBody implementation "MainBody.celem"; }\n'
    )
    (project / "Main.celem").write_text(
        f"function Dock.{name}::Main () -> int {{ provide Dock.{name}::Main with Dock.{name}::MainBody; }}\n"
    )
    (project / "MainBody.celem").write_text(
        f'implementation Dock.{name}::MainBody for Dock.{name}::Main () -> int {{ body common "Main.csbody"; }}\n'
    )
    body = project / "Main.csbody"
    text = json.dumps(name + "\n")
    body.write_text(
        f"System.Console.Write({text});\n"
        f"System.IO.File.AppendAllText({json.dumps(str(output))}, {text});\n"
        "return 0;\n"
    )
    return manifest, body


@contextmanager
def editor(root, repo, command, manifest):
    env = dict(
        os.environ, CONFECTORY_UI="web", CONFECTORY_EDITOR_REPO=str(repo),
        CONFECTORY_HOME_STORAGE=str(root / "profile"), CONFECTORY_ENTRY_STORAGE=str(root / "profile"),
        CONFECTORY_MCP_DIRECTORY=str(root / "instances"), CONFECTORY_WEB_PROJECT=str(manifest),
    )
    log = root / f"{manifest.parent.name}.log"
    with log.open("w") as stream:
        host = subprocess.Popen(command, cwd=repo, env=env, stdout=stream,
                                stderr=subprocess.STDOUT, start_new_session=True)
        try:
            for _ in range(600):
                for line in log.read_text().splitlines():
                    if line.startswith("CONFECTORY_WEB_UI "):
                        yield line.split(" ", 1)[1]
                        return
                assert host.poll() is None, "Editor exited during startup"
                time.sleep(.05)
            raise AssertionError("Editor startup timed out")
        finally:
            if host.poll() is None:
                os.killpg(host.pid, signal.SIGTERM)
                host.wait(timeout=20)


def check(page, origin, first_output, second_output, second_body, second_title):
    requests = []
    errors = []
    external = []
    page.on("pageerror", lambda error: errors.append(str(error)))

    def route(request):
        req = request.request
        if not req.url.startswith(origin + "/"):
            external.append(req.url)
            request.abort()
            return
        if req.method == "POST" and req.url == origin + "/api/request":
            data = req.post_data_json
            if data.get("op") == "invoke" and data.get("endpoint") in ("runWindow", "runProject", "startRun"):
                requests.append((data["endpoint"], data["input"].get("operation")))
        request.continue_()

    page.route("**/*", route)

    def wait_output(path, name):
        deadline = time.monotonic() + 120
        while not path.exists() and time.monotonic() < deadline:
            page.wait_for_timeout(100)
        assert path.exists(), f"{name} did not execute"
        assert path.read_text().splitlines() == [name], path.read_text()

    def menu_only():
        before = list(requests)
        page.locator("#project-menu").click()
        menu = page.locator(".context-menu")
        expect(menu.get_by_role("button", name="프로젝트 정보", exact=True)).to_be_visible()
        page.locator(".topbar .muted").click()
        expect(menu).to_have_count(0)
        assert requests == before, requests

    run = page.get_by_role("button", name="프로젝트 실행", exact=True)
    start_requests = lambda: requests.count(("runWindow", "start"))
    title = page.locator("#title")
    expect(title).to_contain_text("First")
    expect(page.locator("#dock #run + #project-menu")).to_be_visible()
    menu_only()
    assert not first_output.exists() and not second_output.exists()
    assert page.locator(".run-window").count() == 0
    print("PASS ≡ opens the project menu without opening or starting a Run window")

    run.click()
    first = page.locator(".run-window:visible")
    expect(first).to_have_count(1)
    expect(first.locator("[data-run-project]")).to_contain_text("First")
    expect(first.locator("[data-run-frame]")).to_have_text("종료 코드 0", timeout=120000)
    wait_output(first_output, "First")
    assert not second_output.exists() and start_requests() == 1
    print("PASS one dock ▶ click launches the open project exactly once")

    page.locator(".brand").click()
    expect(page.locator(".home-grid")).to_be_visible()
    page.locator("[data-enter]").filter(
        has=page.get_by_role("heading", name=second_title, exact=True),
    ).click()
    expect(title).to_contain_text("Second")
    menu_only()
    assert not second_output.exists() and first_output.read_text().splitlines() == ["First"]
    run.click()
    second = page.locator(".run-window:visible")
    expect(second).to_have_count(1)
    expect(second.locator("[data-run-project]")).to_contain_text("Second")
    expect(second.locator("[data-run-frame]")).to_have_text("종료 코드 0", timeout=120000)
    wait_output(second_output, "Second")
    assert first_output.read_text().splitlines() == ["First"] and start_requests() == 2
    print("PASS switching projects changes which executable runs; ≡ remains independent")

    original = second_body.read_bytes()
    try:
        second_body.write_text("fixture_compile_error__\n")
        page.get_by_role("tab", name="Workspace", exact=True).click()
        run.click()
        failure = page.locator(".run-window:visible")
        expect(failure.locator(".caption strong")).to_have_text("실행 실패", timeout=120000)
        expect(failure.locator("[data-run-project]")).to_contain_text("Second")
        expect(title).to_contain_text("Second")
        assert start_requests() == 3
        assert first_output.read_text().splitlines() == ["First"]
        assert second_output.read_text().splitlines() == ["Second"]
        page.get_by_role("tab", name="Workspace", exact=True).click()
        menu_only()
        expect(title).to_contain_text("Second")
        print("PASS real compile failure keeps the current project and launches neither fixture")
    finally:
        second_body.write_bytes(original)

    # The compact menu retains its existing open-only action.
    page.set_viewport_size({"width": 390, "height": 844})
    page.locator("[data-mobile-more]").click()
    page.locator(".context-menu").get_by_role("button", name="프로젝트 실행", exact=True).click()
    compact = page.locator(".run-window:visible")
    expect(compact.locator("[data-run-play]")).to_be_enabled()
    expect(compact.locator(".caption strong")).to_have_text("실행 대기중")
    assert start_requests() == 3
    assert not errors and not external, (errors, external)
    print("PASS the compact menu still opens idle Run controls")


repo = Path(sys.argv[1]).resolve()
command = json.loads(Path(sys.argv[2]).read_text())["run"]
with tempfile.TemporaryDirectory(prefix="confectory-run-dock-") as temp, sync_playwright() as playwright:
    root = Path(temp)
    first_output, second_output = root / "first-output", root / "second-output"
    first_manifest, _ = make_project(root, repo, "First", first_output)
    second_manifest, second_body = make_project(root, repo, "Second", second_output)
    browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
    with editor(root, repo, command, second_manifest) as url:
        # Enter B once through regular startup so the application's own listing records it.
        warmup = browser.new_page()
        origin = url.split("/#")[0]
        warmup.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin + "/") else route.abort())
        goto_editor(warmup, url)
        title = warmup.locator("#title")
        expect(title).to_contain_text("Second")
        second_title = title.inner_text().removesuffix(" ▾")
        warmup.close()
    with editor(root, repo, command, first_manifest) as url:
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.set_default_timeout(30000)
        origin = url.split("/#")[0]
        # The check installs its route after first-run navigation.
        page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin + "/") else route.abort())
        goto_editor(page, url)
        check(page, origin, first_output, second_output, second_body, second_title)
        page.close()
    browser.close()
