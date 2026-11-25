"""Actual Codex setup in isolated profiles, including readable missing-namespace errors."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

from playwright.sync_api import expect, sync_playwright
from editor_navigation import goto_editor

repo = Path(sys.argv[1]).resolve()
report = json.loads(Path(sys.argv[2]).read_text())
root = Path(tempfile.mkdtemp(prefix="confectory-codex-error-ui-"))
codex = "Confectory.Agent.Codex::Connection"
expect.set_options(timeout=30000)


def exercise(browser, scenario):
    case = root / scenario
    case.mkdir()
    storage = case / "profile"
    settings = storage / "ai-settings" / hashlib.sha256(codex.encode()).hexdigest()[:16]
    source_repo = repo
    authoring = repo / "targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll"
    if scenario == "fallback":
        source_repo = case / "content"
        shutil.copytree(repo / "examples/editor-home/ui", source_repo / "examples/editor-home/ui")
        (source_repo / "targets/dotnet").mkdir(parents=True)
        shutil.copy2(repo / "targets/dotnet/pack.cpack", source_repo / "targets/dotnet/pack.cpack")
        assert not (source_repo / "examples/editor-home/project.cpack").exists()
    env = os.environ.copy()
    env.update(CONFECTORY_UI="web", CONFECTORY_EDITOR_REPO=str(source_repo),
               CONFECTORY_HOME_STORAGE=str(storage), CONFECTORY_ENTRY_STORAGE=str(storage),
               CONFECTORY_MCP_DIRECTORY=str(case / "instances"),
               CONFECTORY_ELEMENT_AUTHORING_HOST=str(authoring))
    env.pop("CONFECTORY_WEB_PROJECT", None)
    if scenario == "missing-namespace":
        request = {"operation": "connectionSettings",
                   "project": str(repo / "examples/editor-home/project.cpack"), "id": codex}
        result = subprocess.run([env["CONFECTORY_DOTNET"], str(authoring)],
                                input=json.dumps(request), text=True, capture_output=True,
                                check=True, env=env)
        generated = json.loads(result.stdout)
        assert generated["ok"], generated
        manifest = generated["result"]["manifest"]
        source = generated["result"]["source"]
        invalid, count = re.subn(r'registry\s+Confectory\.InstantTable\s+"[^"\n]*"\s*;\s*', "", manifest)
        assert count == 1
        invalid = re.sub(r'dependency\s+Confectory\.InstantTable\s+version\s+"[^"\n]*"\s*;\s*', "", invalid)
        invalid += "// custom settings manifest must be retained\n"
        settings.mkdir(parents=True)
        (settings / "project.cpack").write_text(invalid)
        (settings / "Settings.celem").write_text(source)
    log_path = case / "host.log"
    with log_path.open("w") as log:
        host = subprocess.Popen(report["run"], cwd=source_repo, env=env, stdout=log,
                                stderr=subprocess.STDOUT, start_new_session=True)
        page = browser.new_page(viewport={"width": 1360, "height": 900})
        errors = []
        external = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        try:
            for _ in range(600):
                urls = [line.split(" ", 1)[1] for line in log_path.read_text().splitlines()
                        if line.startswith("CONFECTORY_WEB_UI ")]
                if urls:
                    break
                assert host.poll() is None, log_path.read_text()
                time.sleep(.05)
            else:
                raise AssertionError("Editor startup deadline")
            url = urls[-1]
            origin = url.split("/#")[0]

            def route(request):
                if request.request.url.startswith(origin + "/"):
                    request.continue_()
                else:
                    external.append(request.request.url)
                    request.abort()

            page.route("**/*", route)
            goto_editor(page, url)
            page.locator("#add-agent").click()
            dialog = page.get_by_role("dialog", name="Agent 추가", exact=True)
            dialog.get_by_role("button", name="Codex", exact=True).click()
            if scenario == "missing-namespace":
                diagnostic = dialog.locator("[data-connection-error]")
                expect(diagnostic).to_have_attribute("data-code", "connection_settings_invalid")
                expect(diagnostic).to_contain_text("settings-schema / MISSING_NAMESPACE")
                expect(diagnostic).to_contain_text("누락된 네임스페이스: Confectory.InstantTable")
                expect(diagnostic).to_contain_text("설정 사본의 선언·스키마")
                assert (settings / "project.cpack").read_text() == invalid
                assert (settings / "Settings.celem").read_text() == source
                toast = page.locator("#toast")
                expect(toast).to_have_class(re.compile(r"\bshow\b"))
                page.wait_for_function("""() => {
                    const toast = document.querySelector('#toast');
                    const shade = document.querySelector('.participant-create-shade');
                    return Number(getComputedStyle(toast).opacity) > .95 &&
                        Number(getComputedStyle(toast).zIndex) > Number(getComputedStyle(shade).zIndex);
                }""")
                retry = diagnostic.get_by_role("button", name="연결 화면 다시 열기")
                expect(retry).to_be_enabled()
                assert retry.evaluate("""button => {
                    const r = button.getBoundingClientRect();
                    return button.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2));
                }""")
                page.screenshot(path=str(case / "readable-error.png"))
                # Restore the known valid fixture manifest and retry without deleting Settings.
                (settings / "project.cpack").write_text(manifest)
                retry.click()
            expect(dialog.locator("[data-cli-login]")).to_be_enabled()
            expect(dialog.locator("[data-connection-error]")).to_be_hidden()
            assert "dependency Confectory.Agent.Codex version " in (settings / "project.cpack").read_text()
            if scenario == "fallback":
                assert "connection-metadata" in (settings / "project.cpack").read_text()
            dialog.locator("[data-connection-cancel]").click()
            expect(dialog).to_have_count(0)
            assert not errors and not external, (errors, external)
            print("PASS", scenario, flush=True)
        finally:
            page.close()
            if host.poll() is None:
                os.killpg(host.pid, signal.SIGTERM)
            host.wait(timeout=15)


if __name__ == "__main__":
    with sync_playwright() as playwright, playwright.chromium.launch(
            executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
        for scenario in ("fresh", "missing-namespace", "fallback"):
            exercise(browser, scenario)
    print("evidence:", root)
