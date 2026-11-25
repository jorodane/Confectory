"""Reopen an owned property view with saved and unsaved input at the three-view limit."""
from playwright.sync_api import expect, sync_playwright

import v821_property_window_floating_ui as floating
from v821_project_browser_search_labels import browser_window, choose_tree_location, search

fixture = floating.fixture
fallback = floating.fallback
owner = f"{fallback.NS}::{fallback.TARGET}"
peer = f"{fallback.NS}::{fallback.PEER}"


def seed():
    source = fallback.seed()
    for manifest, title in zip(fixture.projects, (fallback.FIRST, fallback.SECOND)):
        registrations = []
        for number in (1, 2):
            name, folder = f"Extra{number}", f"ExtraFolder{number}"
            folder_path = manifest.parent / f"private-source-{folder}.celem"
            folder_path.write_text(f"category {fallback.NS}::{folder} {{}}\n")
            object_path = manifest.parent / f"private-source-{name}.celem"
            object_path.write_text(f"""object {fallback.NS}::{name} {{
                use schema {fallback.NS}::StockInfo;
                value editorName = "{fallback.LABEL}";
                value editorFolder = "{fallback.NS}::{folder}";
                data Count = 73;
                data Note = "{title} {name}";
            }}\n""")
            registrations += [f'element {folder} category "{folder_path.name}";',
                              f'element {name} object "{object_path.name}";']
            for file in (folder_path, object_path):
                fixture.before[str(file)] = file.read_bytes()
        manifest.write_text(manifest.read_text().rstrip()[:-1] + "\n" +
                            "\n".join(registrations) + "\n}\n")
        fixture.before[str(manifest)] = manifest.read_bytes()
    return source


def close(window):
    window.get_by_role("button", name="창 닫기", exact=True).click()
    expect(window).to_be_hidden()


def binding(identifier):
    return next(item for item in fixture.state()["editorViews"] if item["id"] == identifier)


def drag(page, name, folder):
    browser = browser_window(page)
    choose_tree_location(browser, f'[data-tree-id="{fallback.NS}::{folder}"]')
    search(browser, fallback.LABEL, name)
    item = browser.locator(f'[data-object="{fallback.NS}::{name}"]')
    canvas = page.locator("#workspace")
    bounds = canvas.bounding_box()
    item.drag_to(canvas, target_position={"x": bounds["width"] * .82, "y": bounds["height"] * .70})
def place(page):
    drag(page, fallback.TARGET, "StockFolder")
    visible = page.locator('.window[data-key^="editor-"]:visible')
    expect(visible).to_have_count(1)
    window = page.locator(f'.window[data-key="editor-{binding(owner)["view"]}"]')
    expect(window).to_be_visible()
    return window


def reopen_without_host_read(page, window):
    """A retained, bound view must be interactive while real status reads wait."""
    browser = browser_window(page)
    choose_tree_location(browser, f'[data-tree-id="{fallback.NS}::StockFolder"]')
    search(browser, fallback.LABEL, fallback.TARGET)
    item = browser.locator(f'[data-object="{owner}"]')
    canvas = page.locator("#workspace")
    bounds = canvas.bounding_box()
    held = []

    def hold_status(route):
        body = route.request.post_data_json
        if isinstance(body, dict) and body.get("op") == "update":
            held.append(route)
        else:
            route.fallback()

    page.route("**/api/request", hold_status)
    try:
        item.drag_to(canvas, target_position={"x": bounds["width"] * .82,
                                              "y": bounds["height"] * .70})
        expect(window).to_be_visible(timeout=3000)
        note = floating.property_value(window, "Note")
        expect(note).to_be_editable(timeout=3000)
        expect(note).to_have_value("unapplied target input")
        note.fill("local input while reads wait")
        expect(note).to_have_value("local input while reads wait")
        note.fill("unapplied target input")
    finally:
        page.unroute("**/api/request", hold_status)
        for route in held:
            route.fallback()
    expect(page.locator("#project-menu")).to_be_enabled()
    print("PASS retained property view reopens and accepts input without a host status response", flush=True)


def click_during_read(page):
    browser = browser_window(page)
    choose_tree_location(browser, f'[data-tree-id="{fallback.NS}::StockFolder"]')
    search(browser, fallback.LABEL, fallback.TARGET)
    item = browser.locator(f'[data-object="{owner}"]')
    handle = item.element_handle()
    box = item.bounding_box()
    page.mouse.move(box['x'] + 12, box['y'] + 12)
    page.mouse.down()
    try:
        fixture.call('browserDrafts', {'action': 'status', 'ids': [owner]})
        assert handle.evaluate('row => row.isConnected'), 'Unchanged browser row replaced during real pointer press'
    finally:
        page.mouse.up()
    window = page.locator(f'.window[data-key="editor-{binding(owner)["view"]}"]')
    expect(window).to_be_visible()
    return window


def save(page, window):
    window.locator('[data-element-action="save"]').click()
    expect(page.locator("#project-menu")).to_be_enabled()
    expect(window.locator("[data-element-error]")).to_have_text("")


def exercise(browser, source):
    fixture.start(0)
    page = fixture.setup(browser)
    page.set_viewport_size({"width": 2000, "height": 1200})
    peer_window, peer_key = floating.open_properties(page, fallback.PEER, "PeerFolder")
    floating.property_value(peer_window, "Note").fill("unapplied peer input")
    close(peer_window)
    for number in (1, 2):
        window, _ = floating.open_properties(page, f"Extra{number}", f"ExtraFolder{number}")
        close(window)
    assert len(fixture.state()["editorViews"]) == 3

    primary, _ = fallback.open_from_search(page, fallback.FIRST, fallback.TARGET, fallback.BEFORE)
    floating.property_value(primary, "Note").fill("saved primary draft")
    save(page, primary)
    expect(primary.locator('[data-element-action="save"]')).to_be_disabled()
    close(primary)
    target = place(page)
    expect(floating.property_value(target, "Note")).to_have_value("saved primary draft")
    assert binding(peer)["view"] == peer_key.removeprefix("editor-")
    assert len(fixture.state()["editorViews"]) == 3
    fixture.original()
    print("PASS drag reclaims a clean hidden view and preserves the unrelated pending input", flush=True)

    # The two hidden pending-input views and saved target draft must not be
    # displaced just to create a fourth independent property view.
    close(target)
    extra, _ = floating.open_properties(page, "Extra2", "ExtraFolder2")
    floating.property_value(extra, "Note").fill("keep extra input")
    close(extra)
    owners = {row["id"] for row in fixture.state()["editorViews"]}
    drag(page, "Extra1", "ExtraFolder1")
    expect(page.locator("#status")).to_contain_text("독립 창 수를 확인해 주세요")
    assert {row["id"] for row in fixture.state()["editorViews"]} == owners
    expect(page.locator('.window[data-key^="editor-"]:visible')).to_have_count(0)
    target = place(page)
    expect(floating.property_value(target, "Note")).to_have_value("saved primary draft")
    print("PASS a fourth view is denied while a retained dirty target can reopen", flush=True)

    floating.property_value(target, "Note").fill("unapplied target input")
    close(target)
    target = place(page)
    expect(floating.property_value(target, "Note")).to_have_value("unapplied target input")
    save(page, target)
    expect(page.locator("#project-menu")).to_be_enabled()
    close(target)
    target = place(page)
    expect(floating.property_value(target, "Note")).to_have_value("unapplied target input")
    fixture.original()
    print("PASS same-session reopen preserves both local input and saved draft", flush=True)
    close(target)
    reopen_without_host_read(page, target)
    close(target)
    page.locator('#workspace [data-workspace-zoom]').click()
    page.locator('[data-zoom-value]').fill('62.5')
    page.locator('[data-zoom-value]').press('Enter')
    page.locator('[data-zoom-value]').press('Escape')
    expect(page.locator('#workspace [data-workspace-zoom]')).to_have_text('62.5%')
    target = click_during_read(page)
    expect(floating.property_value(target, "Note")).to_have_value("unapplied target input")
    assert len(fixture.state()["editorViews"]) == 3
    print("PASS real pointer press survives a status refresh at 62.5% and reopens the retained view", flush=True)


    close(target)
    page.evaluate("()=>confectoryFlushPresentation()")
    page.close()
    fixture.stop()
    fixture.start(1)
    page = fixture.setup(browser)
    page.set_viewport_size({"width": 2000, "height": 1200})
    target = place(page)
    expect(floating.property_value(target, "Note")).to_have_value("unapplied target input")
    close(target)
    drag(page, fallback.PEER, "PeerFolder")
    other = page.locator(f'.window[data-key="editor-{binding(peer)["view"]}"]')
    expect(other).to_be_visible()
    expect(floating.property_value(other, "Note")).to_have_value("unapplied peer input")
    fixture.original()
    print("PASS cold reopen preserves the saved draft and unrelated local input", flush=True)
    assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)


if __name__ == "__main__":
    expect.set_options(timeout=30000)
    source = seed()
    try:
        with sync_playwright() as playwright, playwright.chromium.launch(
                executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
            exercise(browser, source)
    finally:
        fixture.stop()
        print("evidence:", fixture.root)
