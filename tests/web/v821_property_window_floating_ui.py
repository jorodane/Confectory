"""Move a properties window with the mouse above another editor document."""

from playwright.sync_api import expect, sync_playwright

import v821_object_fallback_roundtrip_ui as fallback
from v821_category_move_identity_ui import title_point
from v821_project_browser_search_labels import browser_window, choose_tree_location, search


fixture = fallback.fixture
FIRST_NOTE = "첫 객체의 미적용 입력"
SECOND_NOTE = "둘째 객체의 미적용 입력"


def property_value(window, name):
    return fallback.field(window, name).get_by_label(name + " 기본값", exact=True)


def open_properties(page, name, folder):
    browser = browser_window(page)
    choose_tree_location(browser, f'[data-tree-id="{fallback.NS}::{folder}"]')
    search(browser, fallback.LABEL, name)
    identifier = f"{fallback.NS}::{name}"
    browser.locator(f'[data-object="{identifier}"]').click(button="right")
    page.locator(".context-menu").get_by_role("button", name="새 창으로 열기", exact=True).click()
    expect(page.locator("#project-menu")).to_be_enabled()
    window = page.locator(f'.window[data-element-owner="{identifier}"][data-element-mode="properties"]:visible')
    if not window.count():
        # Older verified host builds expose only their actual retained slot.
        bound = next((row for row in fixture.state()["editorViews"] if row["id"] == identifier), None)
        if bound:
            window = page.locator(f'.window[data-key="editor-{bound["view"]}"]')
    expect(window).to_have_count(1)
    key = window.get_attribute("data-key")
    window = page.locator(f'.window[data-key="{key}"]')
    expect(property_value(window, "Note")).to_have_value(f"{fallback.FIRST} {name}")
    return window, key


def tab(page, key):
    return page.locator(f'[data-window-tab="{key}"]')


def dock(window, key):
    page = window.page
    point = title_point(window)
    page.mouse.click(point["x"], point["y"], button="right")
    page.locator(".context-menu").get_by_role("button", name="탭으로 열기", exact=True).click()
    expect(tab(page, key)).to_have_attribute("aria-selected", "true")


def float_over_document(page, key, window):
    canvas = page.locator("#workspace")
    bounds = canvas.bounding_box()
    wrapper = page.locator(f'[data-tab-order-key="window:{key}"]')
    wrapper.drag_to(canvas, target_position={"x": bounds["width"] * 0.46, "y": bounds["height"] * 0.30})
    expect(tab(page, key)).to_have_count(0)
    expect(page.locator(f'.workspace-floating-window-layer .window[data-key="{key}"]')).to_be_visible()
    expect(window).to_be_visible()


def drag_clear_of(window, field):
    page = window.page
    area = page.locator("#workspace").bounding_box()
    before = window.bounding_box()
    point = title_point(window)
    under = field.bounding_box()
    focus_x = under["x"] + under["width"] / 2
    edges = (area["x"] + 24, area["x"] + area["width"] - before["width"] - 24)
    target = max(edges, key=lambda left: abs(left + before["width"] / 2 - focus_x))
    assert not target <= focus_x <= target + before["width"], (area, before, under)
    delta = target - before["x"]
    assert abs(delta) > 150, (area, before, target)
    page.mouse.move(point["x"], point["y"])
    page.mouse.down()
    page.mouse.move(point["x"] + delta, point["y"], steps=14)
    page.mouse.up()
    after = window.bounding_box()
    assert abs(after["x"] - target) <= 2, (before, after, target)
    return after


def check_contents(first, second):
    expect(property_value(first, "Count")).to_have_value(fallback.BEFORE)
    expect(property_value(second, "Count")).to_have_value("41")
    expect(property_value(first, "Note")).to_have_value(FIRST_NOTE)
    expect(property_value(second, "Note")).to_have_value(SECOND_NOTE)


def view_drafts(state):
    return {row["id"]: (row["mode"], row["draft"]["text"]) for row in state["editorViews"]}


def exercise(page):
    first, first_key = open_properties(page, fallback.TARGET, "StockFolder")
    property_value(first, "Note").fill(FIRST_NOTE)
    dock(first, first_key)
    page.get_by_role("tab", name="Workspace", exact=True).click()
    second, second_key = open_properties(page, fallback.PEER, "PeerFolder")
    property_value(second, "Note").fill(SECOND_NOTE)
    dock(second, second_key)
    tab(page, first_key).click()
    before = fixture.state()
    owners_before = {first_key: first.get_attribute("data-element-owner"), second_key: second.get_attribute("data-element-owner")}
    float_over_document(page, second_key, second)
    after = drag_clear_of(second, property_value(first, "Note"))
    expect(tab(page, first_key)).to_have_attribute("aria-selected", "true")
    for window in (first, second, first):
        value = property_value(window, "Note")
        value.click()
        expect(value).to_be_focused()
    check_contents(first, second)
    assert second.bounding_box() == after
    assert view_drafts(fixture.state()) == view_drafts(before)
    fixture.original()
    fixture.checked("Two UI-opened properties views retain inputs and draft owners after tab detachment and mouse movement above another document")

    fallback.enter_from_home(page, fallback.SECOND)
    expect(page.locator(".workspace-floating-window-layer .window:visible")).to_have_count(0)
    fallback.open_from_search(page, fallback.SECOND, fallback.TARGET, "19")
    peer = fixture.state()
    assert peer["projectId"] != before["projectId"] and not peer["editorViews"]
    fallback.enter_from_home(page, fallback.FIRST)
    expect(tab(page, first_key)).to_have_attribute("aria-selected", "true")
    expect(page.locator(f'.workspace-floating-window-layer .window[data-key="{second_key}"]')).to_be_visible()
    check_contents(first, second)
    restored = second.bounding_box()
    assert abs(restored["x"] - after["x"]) <= 2 and abs(restored["y"] - after["y"]) <= 2, (restored, after)
    state = fixture.state()
    assert state["projectId"] == before["projectId"]
    assert {first_key: first.get_attribute("data-element-owner"), second_key: second.get_attribute("data-element-owner")} == owners_before
    assert view_drafts(state) == view_drafts(before) or not view_drafts(before)
    fixture.original()
    assert not [row for row in fixture.requests if row["endpoint"] in {
        "editViewField", "editEditorView", "saveEditorView", "saveDraft", "confirmGroup",
    }]
    fixture.checked("A second project with the same IDs shows its own values; returning restores both pending inputs and the floating position")


if __name__ == "__main__":
    fallback.seed()
    fixture.start(0)
    try:
        with sync_playwright() as playwright, playwright.chromium.launch(
                executable_path="/usr/bin/chromium", args=["--no-sandbox", "--disable-gpu"],
                ignore_default_args=["--disable-dev-shm-usage"]) as browser:
            expect.set_options(timeout=18000)
            page = fixture.setup(browser)
            page.set_viewport_size({"width": 1700, "height": 1080})
            exercise(page)
            assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
    finally:
        fixture.stop()
