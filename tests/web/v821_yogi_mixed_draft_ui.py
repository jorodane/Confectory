"""Use one local YogiBox for an EY and a LaY before sealing in Linux Chromium."""

import json
import re

from playwright.sync_api import expect, sync_playwright

import v666_workspace_finder_fixture as fixture
from v821_project_browser_search_labels import NS, browser_window, search


TARGET = f"{NS}::CaptureSubject"
NOTE = "  유지할 영역 설명\n한 줄 더  "
CAPTURING = re.compile(r"\byogi-capturing\b")
BOX_ROOT = fixture.projects[0].parent / ".confectory" / "yogi"


def seed():
    project = fixture.projects[0]
    source = project.parent / "CaptureSubject.celem"
    source.write_text(f'object {TARGET} {{ description "Recognizable local capture subject"; }}\n')
    project.write_text(project.read_text().rstrip()[:-1] +
                       '\n element CaptureSubject object "CaptureSubject.celem";\n}\n')
    for path in (project, source):
        fixture.before[str(path)] = path.read_bytes()


def actions(mark):
    return [row["input"] for row in fixture.requests[mark:] if row["endpoint"] == "yogi"]


def packages():
    return {path: path.read_bytes() for path in BOX_ROOT.rglob("*")
            if path.is_file() and path.name != "source-transaction.lock"}


def stored(package_files):
    assert len(package_files) == 1, list(package_files)
    return json.loads(next(iter(package_files.values())))["package"]


def capture_mode(page):
    page.keyboard.press("Control+y")
    expect(page.locator("body")).to_have_class(CAPTURING)


def type_button(box, name):
    return box.get_by_role("button", name=name, exact=True)


def count(button, number):
    expect(button.locator("b")).to_have_text(str(number))


def run(page):
    browser = browser_window(page)
    search(browser, "CaptureSubject", "CaptureSubject")
    browser.locator(f'[data-object="{TARGET}"]').click()
    editor = page.locator('.window[data-key="schema"]')
    expect(editor).to_be_visible()
    # Let the editor finish saving its existing window layout before using the shortcut.
    page.evaluate("() => confectoryFlushPresentation()")
    area = editor.bounding_box()
    x, y = int(area["x"]) + 38, int(area["y"]) + 32
    assert page.evaluate("([x,y]) => !!document.elementFromPoint(x,y)?.closest('.window[data-key=schema]')", [x, y])

    capture_mode(page)
    page.mouse.click(x, y)
    box = page.get_by_role("dialog", name="YogiBox", exact=True)
    ey, lay = (type_button(box, name) for name in ("Exactly Yogi", "Look at Yogi"))
    count(ey, 1)
    count(lay, 0)
    first_files = packages()
    first = stored(first_files)
    assert [(item["kind"], item["id"]) for item in first["items"]] == [("semantic", TARGET)]

    # The same shortcut should re-arm capture while the first item is still unsealed.
    mark = len(fixture.requests)
    capture_mode(page)
    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.move(x + 47, y + 32, steps=7)
    page.mouse.up()
    count(ey, 1)
    count(lay, 1)
    assert [action["action"] for action in actions(mark)] == ["show", "capture"]
    both = stored(packages())
    original_ey, image = both["items"]
    assert original_ey == first["items"][0] and image["kind"] == "image"
    assert image["item"] != original_ey["item"]
    assert (image["capture"]["width"], image["capture"]["height"]) == (47, 32)
    assert not both["sealed"]
    fixture.checked("Explicit Ctrl+Y and actual pointer gestures add an EY and a LaY to one unsealed local box")

    ey.click()
    row = box.locator('#yogi-items [data-kind="semantic"]')
    expect(row).to_contain_text(TARGET)
    remove = row.get_by_role("button", name="제거", exact=True)
    expect(remove).to_have_text("×")
    mark = len(fixture.requests)
    remove.click()
    count(ey, 0)
    count(lay, 1)
    assert actions(mark) == [{"action": "remove", "item": original_ey["item"]}]
    assert stored(packages())["items"] == [image]

    box.get_by_role("textbox", name="설명", exact=True).fill(NOTE)
    mark = len(fixture.requests)
    box.locator("#yogi-seal").click()
    package = box.locator(".yogi-package")
    expect(package).to_be_visible()
    sealed = packages()
    assert set(sealed) == set(first_files)
    assert stored(sealed)["items"] == [image]
    assert stored(sealed)["sealed"] and stored(sealed)["text"] == NOTE
    assert actions(mark) == [{"action": "text", "text": NOTE}, {"action": "seal", "sealed": True}]

    mark = len(fixture.requests)
    package.evaluate("el => el.addEventListener('dragstart', () => { el.dataset.dragObserved = 'true'; }, {once:true})")
    bounds = package.bounding_box()
    px, py = bounds["x"] + bounds["width"] / 2, bounds["y"] + bounds["height"] / 2
    page.mouse.move(px, py)
    page.mouse.down()
    page.mouse.move(px + 115, py - 80, steps=12)
    page.mouse.up()
    expect(package).to_have_attribute("data-drag-observed", "true")
    assert package.bounding_box() != bounds
    assert not actions(mark) and packages() == sealed

    mark = len(fixture.requests)
    package.locator("small").dblclick()
    expect(box.get_by_role("textbox", name="설명", exact=True)).to_have_value(NOTE)
    count(ey, 0)
    count(lay, 1)
    expect(box.locator("#yogi-items")).not_to_contain_text(TARGET)
    lay.click()
    expect(box.locator('#yogi-items [data-kind="image"]')).to_be_visible()
    assert actions(mark) == [{"action": "seal", "sealed": False}]
    reopened = stored(packages())
    assert reopened["items"] == [image] and reopened["text"] == NOTE and not reopened["sealed"]
    assert set(packages()) == set(first_files)
    assert not list(fixture.root.rglob("project-chat/*.json"))
    assert not any("send" in row["endpoint"].lower() or "submit" in row["endpoint"].lower()
                   for row in fixture.requests)
    fixture.original()
    fixture.checked("The per-item X removes only the EY; seal, drag and double-click retain the image and description in the original local file without delivery")


if __name__ == "__main__":
    seed()
    fixture.start(0)
    try:
        with sync_playwright() as playwright, playwright.chromium.launch(
                executable_path="/usr/bin/chromium", args=["--no-sandbox", "--disable-gpu"],
                ignore_default_args=["--disable-dev-shm-usage"]) as chromium:
            expect.set_options(timeout=6000)
            run(fixture.setup(chromium))
            assert not fixture.external and not fixture.errors, (fixture.external, fixture.errors)
    finally:
        fixture.stop()
