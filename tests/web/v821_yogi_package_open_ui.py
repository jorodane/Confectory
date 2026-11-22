"""Real local sealed YogiBox activation in Linux Chromium."""
import re
from playwright.sync_api import expect, sync_playwright

import v666_workspace_finder_fixture as fixture


TARGET = "Example.FrameLoop::LocalYogi"
NOTE = "  봉인된 로컬 설명\n두 번째 줄  "
project = fixture.projects[0]
(project.parent / "LocalYogi.celem").write_text(f"object {TARGET} {{}}\n")
project.write_text(project.read_text().rstrip()[:-1] + '\n element LocalYogi object "LocalYogi.celem";\n}\n')
sources = {path: path.read_bytes() for path in project.parent.rglob("*") if path.is_file()}


def actions(mark):
    return [req["input"] for req in fixture.requests[mark:] if req["endpoint"] == "yogi"]


def expect_package(item, *, sealed):
    package = fixture.state()["yogi"]
    assert package["sealed"] == sealed and package["text"] == NOTE, package
    assert [entry["item"] for entry in package["items"]] == [item], package


def seed(page):
    page.locator("#title").click()
    page.get_by_role("button", name="프로젝트 브라우저", exact=True).click()
    browser = page.locator('.window[data-key="browser"]')
    toggle = browser.locator("[data-browser-detail]")
    if toggle.get_attribute("aria-pressed") == "false":
        toggle.click()
    browser.locator('[data-tree-select="ns:Example.FrameLoop"]').click()
    tile = browser.locator(f'[data-object="{TARGET}"]')
    expect(tile).to_be_visible()
    # Settle the fixture's Browser layout before capturing the item.
    page.evaluate("() => confectoryFlushPresentation()")
    page.locator("#yogi").click()
    expect(page.locator("body")).to_have_class(re.compile(r"\byogi-capturing\b"))
    tile.click()
    box = page.get_by_role("dialog", name="YogiBox", exact=True)
    box.locator("#yogi-text").fill(NOTE)
    item = fixture.state()["yogi"]["items"][0]
    assert item["id"] == TARGET
    box.locator("#yogi-seal").click()
    expect(box.locator(".yogi-package")).to_be_visible()
    expect_package(item["item"], sealed=True)
    return box, item["item"]


def open_checks(box, item, activation):
    mark = len(fixture.requests)
    activation()
    expect(box.locator("#yogi-text")).to_have_value(NOTE)
    expect(box.locator(".yogi-package")).to_have_count(0)
    expect_package(item, sealed=False)
    assert actions(mark) == [{"action":"seal","sealed":False}], actions(mark)


def drag_package(page, package, *, cancel):
    bounds = package.bounding_box()
    start_x, start_y = bounds["x"] + bounds["width"] / 2, bounds["y"] + bounds["height"] / 2
    mark = len(fixture.requests)
    package.evaluate("""el => {
        el.dataset.observedDragStart = 'false';
        el.addEventListener('dragstart', () => { el.dataset.observedDragStart = 'true'; }, {once:true});
    }""")
    page.mouse.move(start_x, start_y)
    page.mouse.down()
    page.mouse.move(start_x + 115, start_y - 80, steps=12)
    if cancel:
        page.keyboard.press("Escape")
    page.mouse.up()
    expect(package).to_be_visible()
    expect(package).to_have_attribute("data-observed-drag-start", "true")
    assert actions(mark) == [], actions(mark)
    if not cancel:
        assert package.bounding_box() != bounds


def run(page):
    box, item = seed(page)
    package = box.locator(".yogi-package")
    mark = len(fixture.requests)
    package.locator("small").click()
    expect_package(item, sealed=True)
    expect(package).to_be_focused()
    assert actions(mark) == [], actions(mark)
    print("PASS one pointer click focuses the package and leaves it sealed", flush=True)

    open_checks(box, item, lambda: package.locator("small").dblclick())
    print("PASS pointer double-click issues one unseal and preserves item and description", flush=True)

    box.locator("#yogi-seal").click()
    expect(package).to_be_visible()
    drag_package(page, package, cancel=True)
    drag_package(page, package, cancel=False)
    expect_package(item, sealed=True)
    print("PASS drag and drag cancellation keep the box sealed", flush=True)

    open_checks(box, item, lambda: package.press("Enter"))
    box.locator("#yogi-seal").click()
    expect(package).to_be_visible()
    open_checks(box, item, lambda: package.press("Space"))
    print("PASS Enter and Space each open the focused package once", flush=True)

    box.locator("#yogi-seal").click()
    expect(package).to_be_visible()
    mark = len(fixture.requests)
    box.get_by_role("button", name="YogiBox 닫기", exact=True).press("Enter")
    expect(box).to_have_count(0)
    expect_package(item, sealed=True)
    assert actions(mark) == []
    page.locator("#yogi").click()
    expect(package).to_be_visible()
    open_checks(box, item, lambda: package.locator("small").dblclick())
    mark = len(fixture.requests)
    box.locator(".yogi-clipboard-head [data-close]").click()
    expect(box).to_have_count(0)
    expect_package(item, sealed=False)
    assert actions(mark) == []
    page.locator("#yogi").click()
    expect(box.locator("#yogi-text")).to_have_value(NOTE)
    mark = len(fixture.requests)
    box.locator("#yogi-discard").click()
    expect(box).to_have_count(0)
    assert actions(mark) == [{"action":"discard"}], actions(mark)
    current = fixture.state()["yogi"]
    assert current is None or (current["items"] == [] and current["text"] == "")
    assert all(path.read_bytes() == data for path, data in sources.items())
    assert not fixture.external and not fixture.errors, (fixture.external, fixture.errors)
    print("PASS close preserves the content; only the separate delete discards it", flush=True)


with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path="/usr/bin/chromium",
        args=["--no-sandbox","--disable-gpu","--renderer-process-limit=2"],
        ignore_default_args=["--disable-dev-shm-usage"])
    try:
        fixture.start(0)
        page = fixture.setup(browser)
        try:
            run(page)
        finally:
            page.close()
    finally:
        fixture.stop()
        browser.close()
