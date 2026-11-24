"""Category navigation and concept inheritance through the actual Linux editor."""

import json

from playwright.sync_api import expect, sync_playwright

import v666_workspace_finder_fixture as fixture
from v821_project_browser_search_labels import browser_window, choose_tree_location


NS = "Example.FrameLoop"
FIRST, SECOND = "Concept Routes First", "Concept Routes Second"
FOLDER_LABELS = {"Arrival": "시작 분류", "Departure": "도착 분류"}
BASE, VARIANT, LOCAL = "AnchorConcept", "CrossFolderVariant", "LocalVariant"
SAME_LABEL = "같은 개념"


def qualified(name):
    return f"{NS}::{name}"


def seed():
    for manifest, title in zip(fixture.projects, (FIRST, SECOND)):
        def concept(name, folder=None, parent=None):
            extends = f" extends {qualified(parent)}" if parent else ""
            where = f'value editorFolder = "{qualified(folder)}";' if folder else ""
            label = "같은 분류의 변형" if name == LOCAL else SAME_LABEL
            return "object", f'''object {qualified(name)}{extends} {{
                value editorName = "{label}"; description "{title} {name}"; {where}
            }}'''

        folders = FOLDER_LABELS if title == FIRST else {"Arrival": "두 번째 프로젝트 분류"}
        elements = {name: ("category", f'category {qualified(name)} {{ value editorName = "{label}"; }}')
                    for name, label in folders.items()}
        elements[BASE] = concept(BASE, "Arrival")
        elements[VARIANT] = concept(VARIANT, "Departure" if title == FIRST else "Arrival", BASE)
        if title == FIRST:
            elements[LOCAL] = concept(LOCAL, parent=BASE)
        registrations = []
        for name, (kind, source) in elements.items():
            path = manifest.parent / f"local-concept-source-{name}.celem"
            path.write_text(source + "\n", encoding="utf-8")
            fixture.before[str(path)] = path.read_bytes()
            registrations.append(f'element {name} {kind} "{path.name}";')
        manifest.write_text(manifest.read_text().rstrip()[:-1] + "\n" + "\n".join(registrations) + "\n}\n",
                            encoding="utf-8")
        fixture.before[str(manifest)] = manifest.read_bytes()
    (fixture.root / "profile").mkdir(exist_ok=True)
    (fixture.root / "profile" / "projects.json").write_text(json.dumps([
        {"path": str(project), "title": title, "description": ""}
        for project, title in zip(fixture.projects, (FIRST, SECOND))
    ]), encoding="utf-8")


def card(window, name):
    return window.locator(f'[data-object="{qualified(name)}"]')


def folder_button(window, name):
    return card(window, name).locator("[data-browser-enter]")


def assert_editor(page, title, name):
    editor = page.locator('.window[data-key="schema"]')
    expect(editor.get_by_role("heading", name=SAME_LABEL, exact=True)).to_be_visible()
    expect(editor.get_by_role("textbox", name="객체 설명", exact=True)).to_have_value(f"{title} {name}")
    expect(page.locator("#project-menu")).to_be_enabled()
    assert fixture.state()["draft"]["id"] == qualified(name)
    return editor


def assert_semantic_navigation(window):
    for part in (window.locator(".browser-title-path"), window.locator(".browser-file-pane")):
        expect(part).not_to_contain_text("local-concept-source-")
        for project in fixture.projects:
            expect(part).not_to_contain_text(str(project.parent))
        expect(part.locator('[title*=".celem"], [aria-label*=".celem"]')).to_have_count(0)


def browse_first(page):
    window = browser_window(page)
    namespace = f'[data-namespace="{NS}"]'
    choose_tree_location(window, namespace)
    names = {}
    for folder, visible in FOLDER_LABELS.items():
        button = folder_button(window, folder)
        expect(button).to_be_visible()
        names[visible] = (button.get_attribute("aria-label"), button.get_attribute("title"))

    start = len(fixture.requests)
    folder_button(window, "Arrival").click()
    expect(window.locator(".browser-title-path")).to_contain_text(FOLDER_LABELS["Arrival"])
    expect(card(window, BASE).locator(".name")).to_have_text(SAME_LABEL)
    expect(card(window, VARIANT)).to_have_count(0)
    within = card(window, BASE).get_by_role("button", name=SAME_LABEL + " 바리에이션으로 이동", exact=True)
    within.click()
    expect(card(window, LOCAL)).to_be_visible()
    expect(card(window, VARIANT)).to_have_count(0)
    assert_semantic_navigation(window)

    choose_tree_location(window, namespace)
    folder_button(window, "Departure").click()
    expect(window.locator(".browser-title-path")).to_contain_text(FOLDER_LABELS["Departure"])
    expect(card(window, VARIANT).locator(".name")).to_have_text(SAME_LABEL)
    expect(card(window, BASE)).to_have_count(0)
    assert_semantic_navigation(window)
    assert not [row for row in fixture.requests[start:] if row["endpoint"] == "select"]
    fixture.checked("The two categories navigate distinct locations without selecting a concept, and same-folder variation browsing still works")

    card(window, VARIANT).click()
    editor = assert_editor(page, FIRST, VARIANT)
    parent = editor.locator("[data-parent].object-parent-open")
    expect(parent).to_have_accessible_name(SAME_LABEL)
    parent.click()
    editor = assert_editor(page, FIRST, BASE)
    variations = editor.locator(".object-variations")
    descendant = card(variations, VARIANT)
    expect(descendant).to_be_visible()
    start = len(fixture.requests)
    descendant.press("Enter")
    detached = page.locator('.window[data-key^="editor-"]:visible')
    expect(detached.get_by_role("heading", name=SAME_LABEL, exact=True)).to_be_visible()
    expect(detached.get_by_role("textbox", name="객체 설명", exact=True)).to_have_value(f"{FIRST} {VARIANT}")
    openings = [row["input"] for row in fixture.requests[start:] if row["endpoint"] == "openEditorView"]
    assert openings and {row["id"] for row in openings} == {qualified(VARIANT)}, openings
    assert_semantic_navigation(window)
    fixture.checked("The parent link and the base concept's variation list open the exact same-name definitions across categories")
    return names


def browse_second(page):
    page.get_by_role("button", name="Confectory 홈으로").click()
    expect(page.locator(".home-grid")).to_be_visible()
    page.locator(".project-card").filter(has=page.get_by_role("heading", name=SECOND, exact=True)).locator("[data-enter]").click()
    expect(page.locator("#title")).to_contain_text(SECOND)
    window = browser_window(page)
    choose_tree_location(window, f'[data-namespace="{NS}"]')
    expect(window.locator(f'[data-tree-id="{qualified("Departure")}"]')).to_have_count(0)
    folder_button(window, "Arrival").click()
    expect(window.locator(".browser-title-path")).to_contain_text("두 번째 프로젝트 분류")
    expect(card(window, LOCAL)).to_have_count(0)
    card(window, VARIANT).click()
    editor = assert_editor(page, SECOND, VARIANT)
    editor.locator("[data-parent].object-parent-open").click()
    assert_editor(page, SECOND, BASE)
    assert_semantic_navigation(window)
    fixture.checked("Another project with the same IDs retains its own category and inheritance targets")


if __name__ == "__main__":
    seed()
    fixture.start(0)
    try:
        with sync_playwright() as playwright, playwright.chromium.launch(
                executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
            expect.set_options(timeout=10000)
            page = fixture.setup(browser)
            names = browse_first(page)
            browse_second(page)
            fixture.original()
            assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
            assert not {row["endpoint"] for row in fixture.requests} & {
                "moveBrowserFolders", "moveBrowserObjects", "editObjectStructure", "saveDraft", "confirmGroup",
            }
            expected = {name: (f"카테고리 {name} 열기", f"카테고리 {name} 열기") for name in names}
            assert names == expected, names
            fixture.checked("Category buttons have a category name and tooltip distinct from variation navigation")
    finally:
        fixture.stop()
