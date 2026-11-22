"""Actual Linux editor: append to the same local sealed YogiBox."""
import re

from playwright.sync_api import expect, sync_playwright
import v666_workspace_finder_fixture as fixture


NS = "Example.FrameLoop"
NOTE = "  이미 봉인해 둔 설명\n원래 내용 유지  "
CAPTURING = re.compile(r"\byogi-capturing\b")
project = fixture.projects[0]
for name in ("Before", "Next"):
    (project.parent / f"{name}.celem").write_text(f"object {NS}::{name} {{}}\n")
project.write_text(project.read_text().rstrip()[:-1] +
    '\n element Before object "Before.celem";\n element Next object "Next.celem";\n}\n')
sources = {path:path.read_bytes() for path in project.parent.rglob("*") if path.is_file()}


def requests(mark):
    return [req["input"]["action"] for req in fixture.requests[mark:] if req["endpoint"] == "yogi"]


def files():
    directory = project.parent / ".confectory" / "yogi"
    return {path:path.read_bytes() for path in directory.glob("package-*.json") if path.is_file()}


def box(page):
    return page.get_by_role("dialog", name="YogiBox", exact=True)


def package_state(sealed, retained=()):
    package = fixture.state()["yogi"]
    assert package["sealed"] == sealed and package["text"] == NOTE, package
    items = package["items"]
    for previous, current in zip(retained, items):
        assert previous == current, (previous,current)
    assert len(items) >= len(retained)
    return items


def tiles(page):
    panel = page.locator('.window[data-key="browser"]')
    if not panel.is_visible():
        page.locator("#title").click()
        page.get_by_role("button", name="프로젝트 브라우저", exact=True).click()
    toggle = panel.locator("[data-browser-detail]")
    if toggle.get_attribute("aria-pressed") == "false":
        toggle.click()
    panel.locator(f'[data-tree-select="ns:{NS}"]').click()
    # Fixture setup can finish the Browser layout write before capture starts.
    page.evaluate("() => confectoryFlushPresentation()")
    return [panel.locator(f'[data-object="{NS}::{name}"]') for name in ("Before","Next")]


def seal(page):
    box(page).locator("#yogi-seal").click()
    expect(box(page).locator(".yogi-package")).to_be_visible()


def begin(page):
    page.keyboard.press("Control+y")
    expect(page.locator("body")).to_have_class(CAPTURING)


def seed(page):
    before, next_tile = tiles(page)
    page.locator("#yogi").click()
    expect(page.locator("body")).to_have_class(CAPTURING)
    before.click()
    box(page).locator("#yogi-text").fill(NOTE)
    seal(page)
    items = package_state(True)
    assert len(items) == 1 and items[0]["id"] == f"{NS}::Before"
    return items,next_tile


def blank(page):
    point = page.evaluate("""() => {
      const space = document.querySelector('#workspace').getBoundingClientRect();
      for (let y = Math.floor(space.top)+40; y < space.bottom-40; y += 25)
        for (let x = Math.floor(space.left)+40; x < space.right-40; x += 25) {
          const el = document.elementFromPoint(x,y);
          if(el?.id === 'workspace' || el?.closest('#workspace') &&
             !el.closest('.window,[data-object],button,.yogi-clipboard')) return [x,y];
        }
    }""")
    assert point
    page.mouse.click(*point)


def drag_region(page):
    panel = page.locator('.window[data-key="schema"]')
    bounds = panel.bounding_box()
    assert bounds, bounds
    x, y = int(bounds["x"]) + 38, int(bounds["y"]) + 32
    assert page.evaluate("""([x,y]) => !!document.elementFromPoint(x,y)
                         ?.closest('.window[data-key="schema"]')""",[x,y]), bounds
    page.mouse.move(x,y)
    page.mouse.down()
    page.mouse.move(x+37,y+28,steps=7)
    page.mouse.up()


def append_image(page, old):
    mark = len(fixture.requests)
    begin(page)
    drag_region(page)
    expect(box(page).locator("#yogi-text")).to_have_value(NOTE)
    items = package_state(False, old)
    assert len(items) == len(old)+1 and items[-1]["kind"] == "image"
    assert requests(mark) == ["show","capture"], requests(mark)
    return items


def run(page):
    initial, next_tile = seed(page)
    original_store = files()
    assert len(original_store)==1
    mark = len(fixture.requests)
    begin(page)
    expect(box(page).locator(".yogi-package")).to_be_visible()
    page.keyboard.press("Escape")
    expect(page.locator("body")).not_to_have_class(CAPTURING)
    assert requests(mark)==["show"] and package_state(True)==initial and files()==original_store
    print("PASS Escape leaves the same sealed item, description and persisted bytes", flush=True)

    mark = len(fixture.requests)
    begin(page)
    blank(page)
    expect(page.locator("#status")).to_contain_text("실제 의미 객체나 소유한 편집창")
    assert requests(mark)==["show"] and package_state(True)==initial and files()==original_store
    print("PASS rejecting an area without an owned item leaves the sealed package unchanged", flush=True)

    mark = len(fixture.requests)
    begin(page)
    next_tile.click()
    expect(box(page).locator("#yogi-text")).to_have_value(NOTE)
    after_ey = package_state(False,initial)
    assert len(after_ey)==2 and after_ey[-1]["id"]==f"{NS}::Next"
    assert requests(mark)==["show","exactly"], requests(mark)
    assert set(files())==set(original_store)
    print("PASS a real EY appends to the same local package and opens it once", flush=True)

    next_tile.click()
    expect(page.locator('.window[data-key="schema"]')).to_be_visible()
    page.evaluate("() => confectoryFlushPresentation()")
    seal(page)
    after_lay = append_image(page, after_ey)
    seal(page)
    at_limit = append_image(page, after_lay)
    seal(page)
    sealed_store = files()
    mark = len(fixture.requests)
    begin(page)
    drag_region(page)
    expect(page.locator("#status")).to_contain_text("작업 사본과 입력은 유지됩니다.")
    assert requests(mark)==["show","capture"], requests(mark)
    assert package_state(True,at_limit)==at_limit
    assert files()==sealed_store and set(files())==set(original_store)
    assert all(path.read_bytes()==before for path,before in sources.items())
    assert not fixture.external and not fixture.errors, (fixture.external,fixture.errors)
    print("PASS a real LaY appends to the same package; capacity rejection keeps its seal and saved contents", flush=True)


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
