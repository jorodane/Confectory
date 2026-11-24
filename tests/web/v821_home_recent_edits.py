"""Home creation slot and persisted edit order in an installed Linux Logic Code shell."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import time

from playwright.sync_api import expect, sync_playwright

from editor_navigation import goto_editor

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gui"))
from editor_logic_workflow import review


@contextmanager
def editor(package, root, label, *, loopback=False):
    env = dict(os.environ, CONFECTORY_HOME_STORAGE=str(root / "profile"),
               CONFECTORY_ENTRY_STORAGE=str(root / "profile"),
               CONFECTORY_MCP_DIRECTORY=str(root / "instances"))
    for setting in ("CONFECTORY_WEB_PROJECT", "CONFECTORY_DEV_PUBLIC_CHAT_LOOPBACK",
                    "CONFECTORY_TEST_PUBLIC_CHAT_RELAY"):
        env.pop(setting, None)
    if loopback:
        env["CONFECTORY_DEV_PUBLIC_CHAT_LOOPBACK"] = "1"
    log = root / (label + ".log")
    with log.open("w") as stream:
        host = subprocess.Popen(["/bin/sh", str(package / "run"), "--logic-code"],
                                env=env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline:
                address = next((line.split(" ", 1)[1] for line in log.read_text().splitlines()
                                if line.startswith("CONFECTORY_WEB_UI ")), None)
                if address:
                    assert address.startswith("http://127.0.0.1:")
                    yield address
                    return
                assert host.poll() is None, "Linux package exited during startup"
                time.sleep(.05)
            raise AssertionError("Linux package startup timed out")
        finally:
            if host.poll() is None:
                os.killpg(host.pid, signal.SIGINT)
                try:
                    assert host.wait(timeout=25) == 0
                except subprocess.TimeoutExpired:
                    os.killpg(host.pid, signal.SIGTERM)
                    host.wait(timeout=10)
                    raise


def make_project(package, root, name):
    project = root / name
    project.mkdir()
    namespace = f"Recent.{name}"
    manifest = project / "project.cproj"
    target = package / "content/targets/dotnet/pack.cpack"
    manifest.write_text(f"""project {namespace} version "1.0.0" {{
standalone true;
registry Confectory.Build.DotNet {json.dumps(str(target))};
dependency Confectory.Build.DotNet version "0.1.0";
target linux Confectory.Build.DotNet::Linux;
entry {namespace}::Main;
element Main function "Main.celem";
element MainBody implementation "MainBody.celem";
}}
""")
    (project / "Main.celem").write_text(
        f"function {namespace}::Main () -> int {{ provide {namespace}::Main with {namespace}::MainBody; }}")
    (project / "MainBody.celem").write_text(
        f'implementation {namespace}::MainBody for {namespace}::Main () -> int {{ body common "Main.csbody"; }}')
    body = project / "Main.csbody"
    body.write_text(f"// {name}\nreturn 0;\n")
    return manifest, body


def attach(browser, address):
    page = browser.new_page(viewport={"width": 1600, "height": 1100})
    origin = address.split("/#")[0]
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin + "/") else route.abort())
    goto_editor(page, address)
    return page, errors


def tile(page, title):
    return page.locator("#home-projects [data-project]").filter(has=page.get_by_role("heading", name=title, exact=True))


def titles(page):
    return page.locator('section[aria-label="일반 프로젝트"] [data-project] h2')


def open_project(page, title):
    tile(page, title).locator("[data-enter]").click()
    expect(page.locator("#title")).to_contain_text(title)
    expect(page.locator(".work-body")).to_be_visible()


def main_editor(page, name):
    panel = page.locator('.window[data-key="blueprint"]:visible')
    if not panel.count():
        page.locator("#title").click()
        page.locator(".context-menu").get_by_role("button", name="프로젝트 브라우저", exact=True).click()
        browser = page.get_by_role("region", name="프로젝트 브라우저", exact=True)
        browser.get_by_role("button", name="기능", exact=True).click()
        browser.locator('[data-browser-control="object-query"]').fill("Main")
        browser.locator('[data-browser-control="object-search"]').click()
        browser.locator(f'[data-object="Recent.{name}::Main"]').click()
        page.locator('[data-operation="feature-author-open"]').first.click()
    expect(panel.locator("[data-native-source]")).to_be_visible()
    return panel


def home(page):
    page.locator(".brand").click()
    expect(page.locator(".home-grid")).to_be_visible()


def assert_facts(page, names):
    for title in names:
        expect(tile(page, title).locator(".project-icon")).to_be_visible()
        expect(tile(page, title).locator("h2")).to_have_text(title)


def first_tile(page):
    return page.locator("#home-projects .project-card:visible").first


def assert_home_columns(page):
    viewport = page.viewport_size
    try:
        for width, paired in ((1280, True), (390, False)):
            page.set_viewport_size({"width": width, "height": 850})
            expect(first_tile(page)).to_have_attribute("id", "new-project")
            first = first_tile(page).bounding_box()
            second = page.locator("#home-projects [data-project]:visible").first.bounding_box()
            assert first and second and abs(first["width"] - second["width"]) < 2
            if paired:
                assert abs(first["y"] - second["y"]) < 2 and first["x"] + first["width"] < second["x"]
            else:
                assert abs(first["x"] - second["x"]) < 2 and first["y"] + first["height"] < second["y"]
            card = page.locator("#home-projects [data-project]:visible").first
            for control in ("[data-favorite]", "[data-enter]", "[data-manage]"):
                card.locator(control).click(trial=True)
    finally:
        page.set_viewport_size(viewport)


def event(page, name, kind):
    result = tile(page, name).locator('time[data-stat="lastEdit"]')
    expect(result).to_be_visible(timeout=90000)
    expect(result).to_have_attribute("title", re.compile(kind + " 성공"))
    return result.get_attribute("datetime")


def workflow(package, root):
    root.mkdir(parents=True, exist_ok=True)
    (root / "profile").mkdir()
    names = ["Alpha", "Bravo", "Charlie"]
    projects = {name: make_project(package, root, name) for name in names}
    catalog = root / "profile/projects.json"
    catalog.write_text(json.dumps([{"path": str(path), "title": name, "description": name + " project"}
                                   for name, (path, _) in projects.items()], separators=(",", ":")))
    before_catalog = json.loads(catalog.read_bytes())
    sources = {name: body.read_bytes() for name, (_, body) in projects.items()}
    edited = {name: f"// {name} edited\nreturn {number};\n" for number, name in enumerate(names, 1)}

    with sync_playwright() as playwright:
        with playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"],
                                        ignore_default_args=["--disable-dev-shm-usage"]) as browser:
            with editor(package, root, "first") as address:
                page, errors = attach(browser, address)
                expect(titles(page)).to_have_text(names)
                assert_facts(page, names)
                assert_home_columns(page)
                new_slot = first_tile(page)
                expect(new_slot).to_have_attribute("id", "new-project")
                expect(new_slot).to_have_text("＋새 프로젝트")
                new_slot.click()
                dialog = page.get_by_role("dialog", name="새 프로젝트 만들기", exact=True)
                expect(dialog).to_be_visible()
                dialog.locator("[data-project-cancel]").click()
                expect(dialog).to_have_count(0)
                expect(page.locator('[data-stat="lastEdit"][data-status="none"]')).to_have_count(3, timeout=90000)

                open_project(page, "Charlie")
                panel = main_editor(page, "Charlie")
                expect(panel.locator("[data-native-source]")).to_have_value(sources["Charlie"].decode())
                panel.locator("[data-native-source]").fill(edited["Charlie"])
                panel.locator("[data-native-save]").click()
                expect(panel.locator(".bp-status")).to_have_text("저장됨", timeout=120000)
                assert projects["Charlie"][1].read_bytes() == sources["Charlie"]
                home(page)
                charlie = event(page, "Charlie", "초안 Save")
                expect(titles(page)).to_have_text(["Charlie", "Alpha", "Bravo"])

                open_project(page, "Alpha")
                panel = main_editor(page, "Alpha")
                expect(panel.locator("[data-native-source]")).to_have_value(sources["Alpha"].decode())
                panel.locator("[data-native-source]").fill(edited["Alpha"])
                panel.locator("[data-native-save]").click()
                expect(panel.locator(".bp-status")).to_have_text("저장됨", timeout=120000)
                source_review = review(page, panel.locator("[data-native-complete]"))
                source_review.locator("#confirm").click()
                expect(source_review).to_be_hidden(timeout=120000)
                assert projects["Alpha"][1].read_text() == edited["Alpha"]
                home(page)
                alpha = event(page, "Alpha", "원본 Confirm")
                assert alpha > charlie
                expect(titles(page)).to_have_text(["Alpha", "Charlie", "Bravo"])

                # Visiting an untouched third project does not move it ahead of either edit.
                open_project(page, "Bravo")
                panel = main_editor(page, "Bravo")
                expect(panel.locator("[data-native-source]")).to_have_value(sources["Bravo"].decode())
                home(page)
                expect(titles(page)).to_have_text(["Alpha", "Charlie", "Bravo"])
                expect(tile(page, "Bravo").locator('[data-stat="lastEdit"]')).to_have_attribute("data-status", "none")
                assert json.loads(catalog.read_bytes()) == before_catalog
                assert projects["Bravo"][1].read_bytes() == sources["Bravo"]
                assert projects["Charlie"][1].read_bytes() == sources["Charlie"]
                assert not errors, errors
                page.close()

            with editor(package, root, "cold") as address:
                page, errors = attach(browser, address)
                assert_facts(page, names)
                expect(first_tile(page)).to_have_attribute("id", "new-project")
                assert event(page, "Charlie", "초안 Save") == charlie
                assert event(page, "Alpha", "원본 Confirm") == alpha
                expect(titles(page)).to_have_text(["Alpha", "Charlie", "Bravo"])
                for name in ["Alpha", "Charlie", "Bravo"]:
                    open_project(page, name)
                    panel = main_editor(page, name)
                    expected = sources[name].decode() if name == "Bravo" else edited[name]
                    expect(panel.locator("[data-native-source]")).to_have_value(expected)
                    home(page)
                assert not errors, errors
                page.close()
    print("PASS first slot, Save/Confirm order, open-only control and exact cold reopen")


if __name__ == "__main__":
    expect.set_options(timeout=45000)
    package = Path(sys.argv[1]).resolve()
    if len(sys.argv) > 2:
        workflow(package, Path(sys.argv[2]).resolve())
    else:
        with tempfile.TemporaryDirectory(prefix="confectory-home-recent-") as directory:
            workflow(package, Path(directory))
