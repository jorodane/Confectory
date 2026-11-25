"""First primary property window from an already prepared, real host model."""
from playwright.sync_api import expect, sync_playwright

import v821_direct_property_save_ui as direct

fixture = direct.fixture
fallback = direct.fallback
identifier = fallback.NS + "::" + fallback.TARGET


def prepare(page):
    browser = direct.browser_window(page)
    direct.choose_tree_location(browser, f'[data-tree-id="{fallback.NS}::StockFolder"]')
    direct.search(browser, fallback.LABEL, fallback.TARGET)
    item = browser.locator(f'[data-object="{identifier}"]')
    window = page.locator('.window[data-key="schema"]')
    expect(window).not_to_be_visible()
    # Existing host selection/schema operations, not a fabricated browser state.
    # This deliberately isolates the already-prepared model boundary.
    fixture.call("select", {"id": identifier})
    fixture.call("schema", {"id": identifier})
    fixture.call("relationsMap", {})

    def observed(response):
        try:
            if not response.url.endswith("/api/request"):
                return False
            state = response.json().get("state")
            return state and state.get("schema", {}).get("id") == identifier and state.get("relationsMap") and state.get("preparedPrimaryReady") is True
        except Exception:
            return False

    with page.expect_response(observed, timeout=60000):
        page.locator("#title").hover()
    expect(window).not_to_be_visible()
    assert fixture.state()["preparedPrimaryReady"] is True
    return item, window


def open_prepared(page, item, window, expected):
    held = []

    def hold_status(route):
        body = route.request.post_data_json
        if isinstance(body, dict) and body.get("op") == "update":
            held.append(route)
        else:
            route.fallback()

    page.evaluate("""()=>{globalThis.preparedFirstMs=null;document.addEventListener('keydown',e=>{
      if(!e.isTrusted||e.key!=='Enter')return;const start=performance.now();const observe=()=>{
      const window=document.querySelector('.window[data-key="schema"]');
      if(window&&!window.hidden&&[...window.querySelectorAll('[data-property-value]')].some(field=>!field.disabled&&!field.readOnly&&!field.closest('[inert]')&&field.getClientRects().length)){globalThis.preparedFirstMs=performance.now()-start;return;}
      if(performance.now()-start<10000)requestAnimationFrame(observe);};requestAnimationFrame(observe);},{capture:true,once:true})}""")
    page.route("**/api/request", hold_status)
    mark = len(fixture.requests)
    try:
        item.press("Enter")
        expect(window).to_be_visible(timeout=3000)
        note = direct.value(window, "Note")
        expect(note).to_be_editable(timeout=3000)
        expect(note).to_have_value(expected)
        note.fill("prepared local edit")
        expect(note).to_have_value("prepared local edit")
        page.wait_for_function("()=>preparedFirstMs!==null", timeout=3000)
        print("prepared first editable ms", page.evaluate("preparedFirstMs"), flush=True)
        assert not any(row["endpoint"] in ("select", "schema", "openEditorView")
                       for row in fixture.requests[mark:])
    finally:
        page.unroute("**/api/request", hold_status)
        for route in held:
            route.fallback()
    return note


def exercise(browser, source):
    fixture.start(0)
    page = fixture.setup(browser)
    page.set_viewport_size({"width": 2000, "height": 1200})
    item, window = prepare(page)
    assert window.count() == 0, "First renderer must not have been mounted"
    open_prepared(page, item, window, fallback.FIRST + " " + fallback.TARGET)
    direct.commit(page, window)
    assert 'data Note = "prepared local edit"' in source.read_text()
    print("PASS first real primary window opens and accepts input without a host selection/status response; normal Save commits exact value", flush=True)

    fallback.enter_from_home(page, fallback.SECOND)
    item, window = prepare(page)
    dependency = fixture.projects[1].parent / "private-source-StockInfo.celem"
    dependency.write_text(dependency.read_text() + "\n// external schema source revision\n")
    assert fixture.state()["preparedPrimaryReady"] is False
    # Normal model preparation must obtain a new proof; old proof is not reused.
    item, window = prepare(page)
    assert fixture.state()["preparedPrimaryReady"] is True
    print("PASS external dependency invalidates the prepared model before another window opens", flush=True)
    note = open_prepared(page, item, window, fallback.SECOND + " " + fallback.TARGET)
    second = fixture.projects[1].parent / source.name
    external = second.read_text().replace(fallback.SECOND + " " + fallback.TARGET,
                                          "external value")
    second.write_text(external)
    assert fixture.state()["preparedPrimaryReady"] is False
    window.locator('[data-element-action="confirm"]').click()
    expect(page.locator("#project-menu")).to_be_enabled(timeout=120000)
    expect(window.locator("[data-element-error]")).not_to_have_text("")
    expect(note).to_have_value("prepared local edit")
    assert second.read_text() == external
    assert 'data Note = "prepared local edit"' in source.read_text()
    print("PASS same-ID project isolation and external conflict retain local input and physical source", flush=True)
    assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)


if __name__ == "__main__":
    expect.set_options(timeout=60000)
    source = fallback.seed()
    try:
        with sync_playwright() as playwright, playwright.chromium.launch(
                executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
            exercise(browser, source)
    finally:
        fixture.stop()
        print("evidence:", fixture.root)
