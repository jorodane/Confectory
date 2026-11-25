"""Large Browser slices prepare only visible owned candidates; unrelated proof survives."""
import json
import time

from playwright.sync_api import expect, sync_playwright

import v821_property_window_reopen_ui as reopen
import v821_direct_property_save_ui as direct

fixture = reopen.fixture
fallback = reopen.fallback


def seed():
    source = reopen.seed()
    for project in fixture.projects:
        registrations = []
        for i in range(36):
            name = "ModelExtra" + str(i)
            path = project.parent / (name + ".celem")
            path.write_text(f'object {fallback.NS}::{name} {{ use schema {fallback.NS}::StockInfo; '
                            f'value editorName = "Model Extra {i}"; data Count = {i}; '
                            f'data Note = "Model Extra {i}"; }}\n')
            registrations.append(f'element {name} object "{path.name}";')
            fixture.before[str(path)] = path.read_bytes()
        project.write_text(project.read_text().rstrip()[:-1] + "\n" +
                           "\n".join(registrations) + "\n}\n")
        fixture.before[str(project)] = project.read_bytes()
    return source


def prepared(page, identifier):
    def ready(response):
        try:
            return any(row["id"] == identifier for row in
                       response.json().get("state", {}).get("preparedPropertyModels", []))
        except Exception:
            return False

    # The independent fixture mount can see a model before the page does.
    # Match only request metadata inside the callback; read the body afterward
    # to avoid nested Playwright event dispatch.
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        with page.expect_response(lambda response: response.url.endswith("/api/request")
                                  and response.request.method == "POST", timeout=60000) as observed:
            page.locator("#title").hover()
        if ready(observed.value):
            page.evaluate("()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))")
            break
    else:
        raise AssertionError("Prepared model was not published to the actual page")
    return fixture.state()["preparedPropertyModels"]


def prepare_browser(page, name, folder):
    window = reopen.browser_window(page)
    reopen.choose_tree_location(window, f'[data-tree-id="{fallback.NS}::{folder}"]')
    started = time.perf_counter()
    reopen.search(window, fallback.LABEL, name)
    identifier = fallback.NS + "::" + name
    models = prepared(page, identifier)
    assert len(models) <= 32
    print("partial-ready-ms", name, round((time.perf_counter()-started)*1000, 1),
          "model-count", len(models), "model-json-bytes", len(json.dumps(models).encode()), flush=True)
    return window.locator(f'[data-object="{identifier}"]'), identifier


def open_local(page, item, identifier, slot, name, title=None):
    item.click(button="right")
    button = page.locator(".context-menu").get_by_role("button", name="새 창으로 열기", exact=True)
    page.evaluate("""slot=>{globalThis.partialFirstMs=null;document.addEventListener('click',e=>{
      if(!e.isTrusted)return;const start=performance.now();const observe=()=>{
      const w=document.querySelector('.window[data-key="editor-'+slot+'"]');
      if(w&&!w.hidden&&[...w.querySelectorAll('[data-property-value]')].some(f=>!f.disabled&&!f.readOnly&&f.getClientRects().length)){partialFirstMs=performance.now()-start;return;}
      if(performance.now()-start<10000)requestAnimationFrame(observe);};requestAnimationFrame(observe);},{capture:true,once:true})}""", slot)
    mark = len(fixture.requests)
    button.click()
    window = page.locator(f'.window[data-key="editor-{slot}"][data-element-owner="{identifier}"]')
    note = direct.value(window, "Note")
    expect(note).to_have_value((title or fallback.FIRST) + " " + name)
    expect(note).to_be_editable()
    page.wait_for_function("()=>partialFirstMs!==null")
    print("local-editable-ms", name, page.evaluate("partialFirstMs"), flush=True)
    assert not any(row["endpoint"] == "openEditorView" for row in fixture.requests[mark:])
    return window, note


def exercise(browser, source):
    fixture.start(0)
    page = fixture.setup(browser)
    page.set_viewport_size({"width": 2000, "height": 1200})
    target, target_id = prepare_browser(page, fallback.TARGET, "StockFolder")
    first, first_note = open_local(page, target, target_id, 1, fallback.TARGET)
    first_note.fill("retain first partial input")
    expect(page.locator("#project-menu")).to_be_enabled()
    peer, peer_id = prepare_browser(page, fallback.PEER, "PeerFolder")
    assert {target_id, peer_id} <= {row["id"] for row in fixture.state()["preparedPropertyModels"]}
    external = source.read_text().replace(fallback.FIRST + " " + fallback.TARGET,
                                          "external first value")
    source.write_text(external)
    after = {row["id"] for row in fixture.state()["preparedPropertyModels"]}
    assert target_id not in after and peer_id in after
    second, second_note = open_local(page, peer, peer_id, 2, fallback.PEER)
    second_note.fill("large project retained peer")
    # The existing host refuses a project save while an unrelated physical
    # source conflict is present. Reusing a read model must not weaken it.
    second.locator('[data-element-action="confirm"]').click()
    expect(page.locator("#project-menu")).to_be_enabled(timeout=120000)
    expect(second.locator("[data-element-error]")).not_to_have_text("")
    peer_source = source.parent / "private-source-PeerRecord.celem"
    assert peer_source.read_bytes() == fixture.before[str(peer_source)]
    assert source.read_text() == external
    expect(first_note).to_have_value("retain first partial input")
    expect(second_note).to_have_value("large project retained peer")
    print("PASS 40 owners: unaffected partial proof reused; existing external save conflict preserved", flush=True)

    fallback.enter_from_home(page, fallback.SECOND)
    clean_item, clean_id = prepare_browser(page, fallback.PEER, "PeerFolder")
    window, note = open_local(page, clean_item, clean_id, 1, fallback.PEER, fallback.SECOND)
    note.fill("large project peer save")
    direct.commit(page, window)
    clean_peer = fixture.projects[1].parent / peer_source.name
    assert 'data Note = "large project peer save"' in clean_peer.read_text()
    assert peer_source.read_bytes() == fixture.before[str(peer_source)]
    print("PASS clean 40-owner project saves exact prepared independent owner", flush=True)
    assert not fixture.errors and not fixture.external


if __name__ == "__main__":
    expect.set_options(timeout=60000)
    source = seed()
    try:
        with sync_playwright() as playwright, playwright.chromium.launch(
                executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
            exercise(browser, source)
    finally:
        fixture.stop()
        print("evidence", fixture.root, flush=True)
