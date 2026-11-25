"""Search the project browser's own metadata through the Linux editor."""

import json

from playwright.sync_api import expect, sync_playwright

import v666_workspace_finder_fixture as fixture


NS = "Example.FrameLoop"
FIRST, SECOND = "Label Search First", "Label Search Second"
SAME = "안내 표식"
CATEGORY = "작업 분류"
MODULE = "조작 규격"


def seed():
    for manifest, title in zip(fixture.projects, (FIRST, SECOND)):
        declarations = {
            "LookupObject": ("object", f'value editorName = "{SAME}";'),
            "LookupFunction": ("function", f'value editorName = "{SAME}";'),
            "LookupModule": ("module", f'value editorName = "{SAME}";'),
        }
        if title == FIRST:
            declarations.update({
                "Folder": ("category", f'value editorName = "{CATEGORY}";'),
                "LookupObject": ("object", f'value editorName = "{SAME}"; value editorFolder = "{NS}::Folder";'),
                "ContractModule": ("module", f'value editorName = "{MODULE}"; require {NS}::LookupFunction () -> int;'),
                "Unbound": ("function", ""),
            })
        else:
            declarations["LookupObject"] = ("object", 'value editorName = "대조 표식";')
            declarations["PeerOnly"] = ("object", f'value editorName = "{SAME}";')
        entries = []
        for name, (kind, details) in declarations.items():
            file = manifest.parent / f"private-source-{name}.celem"
            signature = " () -> int" if kind == "function" else ""
            file.write_text(f"{kind} {NS}::{name}{signature} {{ {details} }}\n", encoding="utf-8")
            fixture.before[str(file)] = file.read_bytes()
            entries.append(f'element {name} {kind} "{file.name}";')
        manifest.write_text(manifest.read_text().rstrip()[:-1] + "\n" + "\n".join(entries) + "\n}\n")
        fixture.before[str(manifest)] = manifest.read_bytes()
    profile = fixture.root / "profile"
    profile.mkdir(exist_ok=True)
    (profile / "projects.json").write_text(json.dumps([
        {"path": str(path), "title": title, "description": ""}
        for path, title in zip(fixture.projects, (FIRST, SECOND))
    ]))


def browser_window(page):
    page.locator("#project-menu").click()
    page.locator(".context-menu").get_by_role("button", name="프로젝트 브라우저", exact=True).click()
    window = page.get_by_role("region", name="프로젝트 브라우저", exact=True)
    expect(window).to_be_visible()
    return window


def search(window, value, *wanted):
    start = len(fixture.requests)
    window.get_by_role("textbox", name="의미 객체 검색", exact=True).fill(value)
    submit = window.get_by_role("button", name="검색 확정", exact=True)
    submit.click()
    expect(submit).to_be_enabled()
    rows = window.locator("[data-object]")
    expect(rows).to_have_count(len(wanted))
    for name in wanted:
        expect(window.locator(f'[data-object="{NS}::{name}"]')).to_be_visible()
    expect(window.locator(".browser-file-pane")).not_to_contain_text("private-source-")
    expect(window.locator('.browser-file-pane [title*=".celem"]')).to_have_count(0)
    for request in fixture.requests[start:]:
        endpoint = request["endpoint"]
        assert endpoint in {"objects", "localInventory", "relationsMap", "savePresentation", "browserDrafts",
                            "schema", "inspectDeclaration", "preparePropertyModels"}, endpoint
        if endpoint == "preparePropertyModels":
            ids = request["input"]["ids"]
            assert 1 <= len(ids) <= 12 and len(set(ids)) == len(ids), ids
        if endpoint == "browserDrafts":
            assert request["input"]["action"] == "status"


def tab(window, name, key):
    window.get_by_role("button", name=name, exact=True).click()
    expect(window.locator("[data-tab].selected")).to_have_attribute("data-tab", key)


def choose_tree_location(window, selector):
    tree = window.locator(".browser-folder-tree")
    if not tree.is_visible():
        window.get_by_role("button", name="폴더 계층 펼치기", exact=True).click()
    node = tree.locator(selector)
    node.click()
    expect(node).to_have_attribute("aria-current", "location")


def choose(window, name, editor_key):
    page = window.page
    start = len(fixture.requests)
    window.locator(f'[data-object="{NS}::{name}"]').press("Enter")
    editor = page.locator(f'.window[data-key="{editor_key}"]')
    expect(editor).to_be_visible()
    selected = [request["input"]["id"] for request in fixture.requests[start:] if request["endpoint"] == "select"]
    assert selected and set(selected) == {f"{NS}::{name}"}, selected
    expect(page.locator("#status")).to_have_text("Ready")
    assert fixture.state()["draft"]["id"] == f"{NS}::{name}"
    editor.get_by_role("button", name="창 닫기", exact=True).click()


def scenario(page):
    window = browser_window(page)
    search(window, "LookupObject", "LookupObject")
    search(window, SAME, "LookupObject")
    choose(window, "LookupObject", "schema")
    search(window, CATEGORY, "LookupObject")
    search(window, "private-source-LookupObject.celem")
    search(window, "PeerOnly")
    tab(window, "기능", "feature")
    search(window, "FrameLoop", "LookupFunction", "Main", "Tick", "Unbound")
    search(window, SAME, "LookupFunction")
    choose(window, "LookupFunction", "declaration")
    search(window, MODULE, "LookupFunction")
    tab(window, "모듈", "module")
    search(window, SAME, "LookupModule")
    choose(window, "LookupModule", "declaration")
    search(window, MODULE, "ContractModule")
    fixture.checked("Same display labels open their exact qualified declarations by tab; category and direct module requirements filter their members")

    tab(window, "기능", "feature")
    choose_tree_location(window, f'[data-namespace="{NS}"]')
    search(window, MODULE, "LookupFunction")
    tab(window, "개념", "concept")
    choose_tree_location(window, f'[data-namespace="{NS}"]')
    search(window, CATEGORY, "Folder", "LookupObject")
    choose_tree_location(window, f'[data-tree-id="{NS}::Folder"]')
    search(window, CATEGORY, "LookupObject")
    fixture.checked("The same searches respect the selected namespace and category in catalogue view")

    page.get_by_role("button", name="Confectory 홈으로").click()
    expect(page.locator(".home-grid")).to_be_visible()
    page.locator(".project-card").filter(has=page.get_by_role("heading", name=SECOND, exact=True)).locator("[data-enter]").click()
    expect(page.locator("#title")).to_contain_text(SECOND)
    window = browser_window(page)
    search(window, CATEGORY)
    search(window, SAME, "PeerOnly")
    choose(window, "PeerOnly", "schema")
    tab(window, "기능", "feature")
    search(window, MODULE)
    search(window, SAME, "LookupFunction")
    fixture.original()
    fixture.checked("A second project with the same namespace has its own results and no first-project classification; searches preserve all original files")


if __name__ == "__main__":
    seed()
    fixture.start(0)
    try:
        with sync_playwright() as playwright, playwright.chromium.launch(
                executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
            expect.set_options(timeout=10000)
            page = fixture.setup(browser)
            scenario(page)
            assert not fixture.errors and not fixture.external
    finally:
        fixture.stop()
