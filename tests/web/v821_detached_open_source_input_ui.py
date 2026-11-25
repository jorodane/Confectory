"""Keep an unrelated local body input usable while a detached property view opens."""
from playwright.sync_api import expect, sync_playwright

import v821_object_fallback_roundtrip_ui as fallback
from editor_navigation import goto_editor
from v821_project_browser_search_labels import browser_window, choose_tree_location, search

fixture = fallback.fixture


def exercise(browser):
    page = browser.new_page(viewport={"width": 2000, "height": 1200})
    errors, held, calls = [], [], []
    page.on("pageerror", lambda error: errors.append(str(error)))

    def intercept(route):
        if not route.request.url.startswith(fixture.origin + "/"):
            fixture.external.append(route.request.url)
            route.abort()
            return
        if route.request.method == "POST":
            body = route.request.post_data_json
            if isinstance(body, dict) and body.get("op") == "invoke":
                calls.append(body["endpoint"])
                if body["endpoint"] == "openEditorView":
                    held.append(route)
                    return
        route.continue_()

    page.route("**/*", intercept)
    goto_editor(page, fixture.url)
    window = browser_window(page)
    choose_tree_location(window, f'[data-tree-id="{fallback.NS}::StockFolder"]')
    search(window, fallback.LABEL, fallback.TARGET)
    page.get_by_role("button", name="검색", exact=True).click()
    finder = page.get_by_role("dialog", name="검색", exact=True)
    finder.locator('[data-find-mode="text"]').click()
    finder.get_by_role("searchbox").fill("LOCAL_FRAME")
    finder.get_by_role("button", name="MainBody · C# · common", exact=False).click(timeout=30000)
    source = page.locator("#source")
    expect(source).to_be_visible()
    expect(page.locator("#project-menu")).to_be_enabled()
    original = source.input_value()
    identity = page.locator("#selection").inner_text()
    assert identity == f"{fallback.NS}::MainBody/body:common"
    target = window.locator(f'[data-object="{fallback.NS}::{fallback.TARGET}"]')
    target.click(button="right")
    with page.expect_request(lambda request: request.method == "POST" and
                             request.url.endswith("/api/request") and
                             request.post_data_json.get("endpoint") == "openEditorView"):
        page.locator(".context-menu").get_by_role("button", name="새 창으로 열기", exact=True).click()
    # Hold the real local request at transport admission until the independent
    # input is exercised. No fabricated host response or timing threshold.
    try:
        expect(page.locator("#project-menu")).to_be_disabled()
        page.wait_for_function("() => !document.querySelector('#source').disabled")
        expect(source).to_be_enabled()
        expect(page.locator("#save")).to_be_disabled()
        expect(page.locator("#apply")).to_be_disabled()
        expect(page.locator("#review")).to_be_disabled()
        expect(page.locator(".brand")).to_be_disabled()
        expect(target).to_have_attribute("aria-disabled", "true")
        local = original + "\n// Local unsaved body input during detached open\n"
        source.fill(local)
        expect(source).to_have_value(local)
        expect(source).to_be_focused()
        assert calls.count("openEditorView") == 1
        assert len(held) == 1
    finally:
        for route in held:
            route.continue_()
    expect(page.locator("#project-menu")).to_be_enabled()
    expect(page.locator('.window[data-key^="editor-"]:visible')).to_have_count(1)
    expect(source).to_have_value(local)
    expect(page.locator("#selection")).to_have_text(identity)
    state = fixture.state()
    assert state["draft"]["id"] == identity and state["draft"]["text"] == original
    assert [row["id"] for row in state["editorViews"]] == [f"{fallback.NS}::{fallback.TARGET}"]
    assert not set(calls) & {"editDraft", "saveDraft", "editViewField", "confirmGroup", "leaveProject"}
    assert calls.count("openEditorView") == 1
    fixture.original()
    assert not errors and not fixture.external, (errors, fixture.external)
    page.close()
    print("PASS independent body input survives detached open; shared mutations and project switch stay blocked")


if __name__ == "__main__":
    fallback.seed()
    fixture.start(0)
    try:
        with sync_playwright() as playwright, playwright.chromium.launch(
            executable_path="/usr/bin/chromium", args=["--no-sandbox", "--disable-gpu"]
        ) as browser:
            expect.set_options(timeout=30000)
            exercise(browser)
    finally:
        fixture.stop()
