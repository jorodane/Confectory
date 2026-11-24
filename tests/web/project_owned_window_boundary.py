"""A packaged project can link an owned view without granting it an EditorHome renderer."""

import json
from pathlib import Path
import sys
import tempfile
import time
from urllib.request import Request, urlopen

from playwright.sync_api import expect, sync_playwright

from v821_home_recent_edits import attach, editor, home, make_project, open_project
from editor_logic_workflow import find_project_item
from editor_navigation import open_project_tools

NS = "Recent.Alpha"
WINDOW = NS + "::StockDesk"
WINDOW_TITLE = "Project-owned Stock Desk"


def seed(package, root):
    (root / "profile").mkdir()
    catalog = []
    proof = root / "run-proof.txt"
    originals = {}

    for name in ("Alpha", "Bravo"):
        project, body = make_project(package, root, name)
        directory = project.parent
        title = "Local " + name
        source = project.read_text().replace("Recent." + name, NS).rstrip()[:-1]
        source += 'element Stock object "Stock.celem";\nelement StockSchema schema "StockSchema.celem";\n'
        (directory / "StockSchema.celem").write_text(
            f'schema {NS}::StockSchema {{ field Note single general string; }}\n')
        (directory / "Stock.celem").write_text(
            f'object {NS}::Stock {{ use schema {NS}::StockSchema; data Note = "{title} only"; }}\n')
        entry = directory / "Main.celem"
        entry_text = entry.read_text().replace("Recent." + name, NS)
        (directory / "MainBody.celem").write_text(
            (directory / "MainBody.celem").read_text().replace("Recent." + name, NS))
        # The same declaration bytes exist in both fixtures. Only A registers and reaches the view.
        (directory / "StockDesk.celem").write_text(
            f'view {WINDOW} {{ use object {NS}::Stock; value editorName = "{WINDOW_TITLE}"; '
            'value nodeIDs = "stock"; }\n')
        if name == "Alpha":
            source += 'element StockDesk view "StockDesk.celem";\n'
            entry_text = entry_text.replace("{", f"{{ use view {WINDOW};", 1)
        project.write_text(source + "}\n")
        entry.write_text(entry_text)
        body.write_text(f"System.IO.File.AppendAllText({json.dumps(str(proof))}, {json.dumps(name + chr(10))});\nreturn 0;\n")
        originals.update({path: path.read_bytes() for path in directory.iterdir()})
        catalog.append({"path": str(project), "title": title, "description": ""})

    listings = root / "profile" / "projects.json"
    listings.write_text(json.dumps(catalog, separators=(",", ":")))
    originals[listings] = listings.read_bytes()
    return catalog, originals, proof


def state(address):
    origin, token = address.split("/#")

    def send(payload):
        request = Request(origin + "/api/request", data=json.dumps(payload).encode(), headers={
            "Content-Type": "application/json", "X-Confectory-Session": token,
        })
        with urlopen(request, timeout=15) as reply:
            return json.load(reply)

    for _ in range(150):
        mounted = send({"op": "mount"})
        if mounted["ok"]:
            break
        assert mounted["error"]["code"] == "busy", mounted["error"]
        time.sleep(.04)
    else:
        raise AssertionError("The packaged editor did not become idle")
    try:
        return mounted["state"]
    finally:
        assert send({"op": "dispose", "view": mounted["view"]})["ok"]


def check_project_menu(page):
    page.locator("#project-menu").click()
    menu = page.locator(".context-menu")
    expect(menu.get_by_role("button", name="프로젝트 정보", exact=True)).to_be_visible()
    expect(menu).not_to_contain_text(WINDOW_TITLE)
    expect(menu).not_to_contain_text("StockDesk")
    menu.get_by_role("button", name="프로젝트 도구", exact=True).click()
    tools = page.get_by_role("navigation", name="프로젝트 작업 공간")
    expect(tools).to_be_visible()
    for label in ("개념", "기능"):
        expect(tools.get_by_role("button", name=label, exact=True)).to_be_enabled()
    expect(tools).not_to_contain_text(WINDOW_TITLE)
    expect(tools).not_to_contain_text("StockDesk")
    open_project_tools(page)
    expect(tools).to_be_hidden()


def check_builtins(page, title):
    find_project_item(page, NS + "::Stock", "개념")
    concept = page.locator('.window[data-key="schema"]')
    expect(concept.get_by_role("heading", name="Stock", exact=True)).to_be_visible()
    expect(concept.get_by_label("Note 기본값", exact=True)).to_have_value(title + " only")
    concept.get_by_role("button", name="창 닫기", exact=True).click()

    find_project_item(page, NS + "::Main", "기능")
    function = page.locator('.window[data-key="declaration"]')
    expect(function.locator(".object-title-name")).to_have_text("Main")
    function.get_by_role("button", name="창 닫기", exact=True).click()


def check_run(page, project, registered):
    title = project["title"]
    page.get_by_role("button", name="프로젝트 실행", exact=True).click()
    run = page.locator(".run-window:visible")
    expect(run.locator("[data-run-project]")).to_contain_text(title)
    expect(run.locator("[data-run-frame]")).to_have_text("종료 코드 0", timeout=120000)
    latest = Path(project["path"]).parent / ".confectory" / "outputs" / "linux" / "latest.json"
    report = json.loads(latest.read_text())
    linkage = json.loads(Path(report["publicCatalog"]).read_text())
    assert linkage["entry"] == NS + "::Main"
    owned = [element for element in linkage["elements"] if element["id"] == WINDOW]
    if registered:
        assert len(owned) == 1 and owned[0]["kind"] == "view"
        assert owned[0]["metadataValues"]["editorName"]["value"] == WINDOW_TITLE
    else:
        assert not owned


def workflow(package, root):
    projects, originals, proof = seed(package, root)
    ids = []
    with sync_playwright() as playwright:
        with playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"],
                                        ignore_default_args=["--disable-dev-shm-usage"]) as browser:
            with editor(package, root, "installed-view-boundary") as address:
                page, errors = attach(browser, address)
                for index, project in enumerate(projects):
                    expect(page.locator(".home-grid")).to_be_visible()
                    expect(page.locator("#project-menu, #run, .nav-menu")).to_have_count(0)
                    expect(page.locator(".home-grid")).not_to_contain_text(WINDOW_TITLE)
                    assert not any(row["id"] == WINDOW for row in state(address)["units"])

                    open_project(page, project["title"])
                    current = state(address)
                    ids.append(current["projectId"])
                    registered = index == 0
                    assert not any(row["id"] == WINDOW for row in current["editorViews"])
                    check_project_menu(page)
                    check_builtins(page, project["title"])
                    expected = ["Alpha", "Bravo"][:index]
                    assert (proof.read_text().splitlines() if proof.exists() else []) == expected
                    check_run(page, project, registered)
                    assert proof.read_text().splitlines() == ["Alpha", "Bravo"][:index + 1]
                    expect(page.locator('body')).not_to_contain_text(str(root))
                    home(page)
                assert all(ids) and len(set(ids)) == 2
                assert not errors, errors
                page.close()

    assert all(path.read_bytes() == data for path, data in originals.items())
    print("PASS packaged Chromium A/B/Home, project view registration and build linkage, project menus, built-in views and real Run")


if __name__ == "__main__":
    package = Path(sys.argv[1]).resolve()
    expect.set_options(timeout=25000)
    with tempfile.TemporaryDirectory(prefix="project-owned-view-") as directory:
        workflow(package, Path(directory))
