"""Exercise the Home favorite reorder with a real host and persistent Chromium profile."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time

from playwright.sync_api import expect, sync_playwright

from editor_navigation import goto_editor


@contextmanager
def editor(command, repo, root, port, log_name):
    env = dict(os.environ, CONFECTORY_UI="web", CONFECTORY_EDITOR_REPO=str(repo),
               CONFECTORY_HOME_STORAGE=str(root / "storage"), CONFECTORY_ENTRY_STORAGE=str(root / "storage"),
               CONFECTORY_MCP_DIRECTORY=str(root / "instances"), CONFECTORY_WEB_PORT=str(port))
    env.pop("CONFECTORY_WEB_PROJECT", None)
    log = root / log_name
    with log.open("w") as output:
        host = subprocess.Popen(command, cwd=repo, env=env, stdout=output,
                                stderr=subprocess.STDOUT, start_new_session=True)
        try:
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                for line in log.read_text().splitlines():
                    if line.startswith("CONFECTORY_WEB_UI "):
                        yield line.split(" ", 1)[1]
                        return
                assert host.poll() is None, log.read_text()[-1200:]
                time.sleep(.05)
            raise AssertionError("Editor startup timed out")
        finally:
            if host.poll() is None:
                os.killpg(host.pid, signal.SIGTERM)
                host.wait(timeout=20)


def make_page(chromium, profile, url, calls, errors):
    browser = chromium.launch_persistent_context(
        str(profile), executable_path="/usr/bin/chromium",
        args=["--no-sandbox"], viewport={"width": 1440, "height": 1000},
    )
    page = browser.pages[0]
    origin = url.split("/#")[0]
    page.on("pageerror", lambda error: errors.append(str(error)))

    def route(request):
        if not request.request.url.startswith(origin + "/"):
            request.abort()
            return
        if request.request.method == "POST" and request.request.url == origin + "/api/request":
            payload = request.request.post_data_json
            if payload.get("op") == "invoke":
                calls.append(payload["endpoint"])
        request.continue_()

    page.route("**/*", route)
    goto_editor(page, url)
    return browser, page


def order(page):
    return page.locator('#favorite-project-content [data-project] h2')


def regular(page):
    return page.locator('section[aria-label="일반 프로젝트"] [data-project] h2')


def drag(page, ids, src, dest, target=None):
    source = page.locator(f'[data-project="{ids[src]}"] .project-card-main')
    card = page.locator(f'[data-project="{ids[dest]}"]')
    if target:
        card = card.locator(target)
    source.drag_to(card)


repo = Path(sys.argv[1]).resolve()
command = json.loads(Path(sys.argv[2]).read_text())["run"]
with tempfile.TemporaryDirectory(prefix="confectory-home-favorites-") as directory:
    root = Path(directory)
    storage = root / "storage"
    storage.mkdir()
    names = ["Filter Alpha", "Filter Bravo", "Other Charlie", "Regular Delta"]
    cards, ids, source_bytes = [], {}, {}
    for index, title in enumerate(names):
        project = root / str(index)
        shutil.copytree(repo / "examples/button-game", project, ignore=shutil.ignore_patterns(".confectory", ".build"))
        manifest = project / "project.cpack"
        manifest.write_text(manifest.read_text().replace("../../", str(repo) + "/"))
        cards.append({"path": str(manifest), "title": title, "description": "", "favorite": index < 2})
        ids[title] = hashlib.sha256(str(manifest).encode()).hexdigest().upper()[:32]
        source_bytes.update({path: path.read_bytes() for path in project.rglob("*") if path.is_file()})
    catalog = storage / "projects.json"
    catalog.write_text(json.dumps(cards))
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    alpha, bravo, charlie, delta = names
    calls, errors = [], []
    with sync_playwright() as playwright:
        with editor(command, repo, root, port, "first.log") as url:
            browser, page = make_page(playwright.chromium, root / "chrome", url, calls, errors)
            expect(order(page)).to_have_text([alpha, bravo])
            expect(regular(page)).to_have_text([charlie, delta])
            page.locator(f'[data-favorite="{ids[charlie]}"]').click()
            expect(order(page)).to_have_text([alpha, bravo, charlie])
            expect(regular(page)).to_have_text([delta])
            before_drag = catalog.read_bytes()

            drag(page, ids, charlie, alpha, ".project-favorite")
            expect(order(page)).to_have_text([charlie, alpha, bravo])
            expect(page.locator(".context-menu,.work-body")).to_have_count(0)
            for source, destination, target in ((charlie, delta, ".card-menu"),
                                                 (delta, alpha, ".project-card-main"),
                                                 (bravo, bravo, None)):
                drag(page, ids, source, destination, target)
                expect(order(page)).to_have_text([charlie, alpha, bravo])
                expect(regular(page)).to_have_text([delta])
                expect(page.locator(".context-menu,.work-body")).to_have_count(0)
            print("PASS Unfiltered valid and invalid mouse drags preserve membership, menu and project scope")

            search = page.locator("#home-project-search")
            page.locator(f'[data-project="{ids[charlie]}"] .project-card-main').drag_to(search)
            expect(search).to_have_value("")
            expect(order(page)).to_have_text([charlie, alpha, bravo])
            search.fill("Filter")
            expect(order(page)).to_have_text([alpha, bravo])
            drag(page, ids, bravo, alpha)
            expect(order(page)).to_have_text([bravo, alpha])
            search.clear()
            expect(order(page)).to_have_text([charlie, bravo, alpha])
            expect(regular(page)).to_have_text([delta])
            assert catalog.read_bytes() == before_drag

            toggle = page.locator(".favorite-section-toggle")
            toggle.click()
            expect(page.locator("#favorite-project-content")).to_be_hidden()
            toggle.press("Enter")
            expect(order(page)).to_have_text([charlie, bravo, alpha])
            expect(order(page).first).to_be_visible()
            assert page.evaluate("() => confectoryFlushHomePreferences()")
            browser.close()

        # A new host and browser process use the same existing origin and private profile.
        with editor(command, repo, root, port, "second.log") as url:
            browser, page = make_page(playwright.chromium, root / "chrome", url, calls, errors)
            expect(order(page)).to_have_text([charlie, bravo, alpha])
            expect(regular(page)).to_have_text([delta])
            assert catalog.read_bytes() == before_drag
            assert sum(endpoint == "favoriteProject" for endpoint in calls) == 1
            assert not set(calls) & {"openProject", "runProject", "runWindow", "removeListing"}
            assert all(path.read_bytes() == content for path, content in source_bytes.items())
            assert not errors, errors
            browser.close()
    print("PASS Filtered reorder keeps hidden favorites and survives a cold restart at the same origin")
