"""Actual Browser preparation and local first property windows for owned objects."""
import json
import time

from playwright.sync_api import expect, sync_playwright

import v821_property_window_reopen_ui as reopen
import v821_direct_property_save_ui as direct

fixture = reopen.fixture
fallback = reopen.fallback
names = (fallback.TARGET, fallback.PEER, "Extra1", "Extra2")
identifiers = {fallback.NS + "::" + name for name in names}


def wait_model(page, open_browser=False):
    def ready(response):
        try:
            state = response.json().get("state")
            return state and {row["id"] for row in state.get("preparedPropertyModels", [])} == identifiers
        except Exception:
            return False

    started = time.perf_counter()
    if open_browser:
        with page.expect_response(ready, timeout=60000):
            reopen.browser_window(page)
    elif {row["id"] for row in fixture.state().get("preparedPropertyModels", [])} != identifiers:
        with page.expect_response(ready, timeout=60000):
            page.locator("#title").hover()
    models = fixture.state()["preparedPropertyModels"]
    assert {row["id"] for row in models} == identifiers
    print("model-ready-ms", round((time.perf_counter()-started)*1000, 1),
          "model-json-bytes", len(json.dumps(models).encode()), flush=True)


def open_local(page, name, folder, expected, hold=True):
    browser = reopen.browser_window(page)
    reopen.choose_tree_location(browser, f'[data-tree-id="{fallback.NS}::{folder}"]')
    reopen.search(browser, fallback.LABEL, name)
    item = browser.locator(f'[data-object="{fallback.NS}::{name}"]')
    window = page.locator('.window[data-key="schema"]')
    expect(page.locator("#project-menu")).to_be_enabled()
    page.evaluate("""expected=>{globalThis.localFirstMs=null;document.addEventListener('keydown',e=>{
      if(!e.isTrusted||e.key!=='Enter')return;const start=performance.now();const observe=()=>{
      const w=document.querySelector('.window[data-key="schema"]');
      const fields=[...w?.querySelectorAll('[data-property-value]')||[]];
      if(w&&!w.hidden&&fields.some(f=>f.value===expected&&!f.disabled&&!f.readOnly&&!f.closest('[inert]')&&f.getClientRects().length)){globalThis.localFirstMs=performance.now()-start;return;}
      if(performance.now()-start<10000)requestAnimationFrame(observe);};requestAnimationFrame(observe);},{capture:true,once:true})}""", expected)
    held = []

    def hold_updates(route):
        body = route.request.post_data_json
        if isinstance(body, dict) and body.get("op") == "update":
            held.append(route)
        else:
            route.fallback()

    if hold:
        page.route("**/api/request", hold_updates)
    mark = len(fixture.requests)
    try:
        item.press("Enter")
        expect(window).to_be_visible(timeout=3000)
        note = direct.value(window, "Note")
        expect(note).to_be_editable(timeout=3000)
        expect(note).to_have_value(expected)
        page.wait_for_function("()=>localFirstMs!==null", timeout=3000)
        print("local-editable-ms", name, page.evaluate("localFirstMs"), flush=True)
        if hold:
            assert not any(row["endpoint"] in ("select", "schema", "openEditorView")
                           for row in fixture.requests[mark:])
    finally:
        if hold:
            page.unroute("**/api/request", hold_updates)
            for route in held:
                route.fallback()
    return window, note


def exercise(browser, source):
    fixture.start(0)
    page = fixture.setup(browser)
    page.set_viewport_size({"width": 2000, "height": 1200})
    wait_model(page, open_browser=True)
    assert page.locator('.window[data-key="schema"]').count() == 0
    window, note = open_local(page, fallback.TARGET, "StockFolder",
                              fallback.FIRST + " " + fallback.TARGET)
    note.fill("local first unsaved")
    expect(page.locator("#project-menu")).to_be_enabled()
    window, note = open_local(page, "Extra2", "ExtraFolder2", fallback.FIRST + " Extra2")
    note.fill("local extra saved")
    direct.commit(page, window)
    extra = source.parent / "private-source-Extra2.celem"
    assert 'data Note = "local extra saved"' in extra.read_text()
    assert source.read_bytes() == fixture.before[str(source)]
    print("PASS first two arbitrary owned objects opened locally; exact second owner saved", flush=True)
    window, note = open_local(page, fallback.TARGET, "StockFolder",
                              "local first unsaved", hold=False)
    direct.commit(page, window)
    assert 'data Note = "local first unsaved"' in source.read_text()
    print("PASS other local input retained through the first save", flush=True)

    wait_model(page)
    window, note = open_local(page, fallback.PEER, "PeerFolder",
                              fallback.FIRST + " " + fallback.PEER)
    note.fill("preserve conflict input")
    dependency = source.parent / "private-source-StockInfo.celem"
    dependency.write_text(dependency.read_text() + "\n// external model dependency change\n")
    assert not fixture.state()["preparedPropertyModels"]
    peer = source.parent / "private-source-PeerRecord.celem"
    external = peer.read_text().replace(fallback.FIRST + " " + fallback.PEER,
                                        "external peer value")
    peer.write_text(external)
    window.locator('[data-element-action="confirm"]').click()
    expect(page.locator("#project-menu")).to_be_enabled(timeout=120000)
    expect(window.locator("[data-element-error]")).not_to_have_text("")
    expect(note).to_have_value("preserve conflict input")
    assert peer.read_text() == external
    print("PASS dependency invalidation and external conflict preserve the local input", flush=True)

    fallback.enter_from_home(page, fallback.SECOND)
    wait_model(page, open_browser=True)
    window, note = open_local(page, fallback.TARGET, "StockFolder",
                              fallback.SECOND + " " + fallback.TARGET)
    note.fill("second unbound input survives restart")
    page.evaluate("()=>confectoryFlushPresentation()")
    page.close()
    fixture.stop()
    fixture.env["CONFECTORY_WEB_PROJECT"] = str(fixture.projects[1])
    fixture.start(1)
    page = fixture.setup(browser)
    expect(page.locator("#title")).to_contain_text(fallback.SECOND)
    window = page.locator('.window[data-key="schema"]')
    expect(window).to_be_visible()
    expect(direct.value(window, "Note")).to_have_value("second unbound input survives restart")
    assert 'data Note = "local first unsaved"' in source.read_text()
    assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
    print("PASS same-ID project isolation and first local selection/input restored after restart", flush=True)


if __name__ == "__main__":
    expect.set_options(timeout=60000)
    source = reopen.seed()
    try:
        with sync_playwright() as playwright, playwright.chromium.launch(
                executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
            exercise(browser, source)
    finally:
        fixture.stop()
        print("evidence:", fixture.root)
