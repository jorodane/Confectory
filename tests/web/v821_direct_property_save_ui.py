"""A local direct Save commits an exact primitive property group; other drafts remain private."""
import uuid

from playwright.sync_api import expect, sync_playwright

import v821_property_window_floating_ui as floating
from v821_project_browser_search_labels import browser_window, choose_tree_location, search

fixture = floating.fixture
fallback = floating.fallback


def value(window, name):
    return floating.property_value(window, name)


def commit(page, window):
    button = window.locator('[data-element-action="confirm"]')
    expect(button).to_have_text("저장")
    mark = len(fixture.requests)
    button.click()
    expect(page.locator("#status")).to_have_text("저장했습니다.", timeout=120000)
    expect(page.locator("#project-menu")).to_be_enabled()
    expect(window.locator("[data-element-error]")).to_have_text("")
    expect(page.locator('.window[data-key="review"]')).to_be_hidden()
    expect(page.get_by_role("dialog", name="관련 변경 검토")).to_have_count(0)
    calls = [row["endpoint"] for row in fixture.requests[mark:]]
    assert calls.count("reviewGroup") == calls.count("confirmGroup") == 1, calls


def close(window):
    window.get_by_role("button", name="창 닫기", exact=True).click()
    expect(window).to_be_hidden()


def open_detached(page, name, folder, expected):
    window = browser_window(page)
    choose_tree_location(window, f'[data-tree-id="{fallback.NS}::{folder}"]')
    search(window, fallback.LABEL, name)
    identifier = f"{fallback.NS}::{name}"
    window.locator(f'[data-object="{identifier}"]').click(button="right")
    page.locator(".context-menu").get_by_role("button", name="새 창으로 열기", exact=True).click()
    expect(page.locator("#project-menu")).to_be_enabled()
    bound = next(row for row in fixture.state()["editorViews"] if row["id"] == identifier)
    target = page.locator(f'.window[data-key="editor-{bound["view"]}"]')
    expect(target).to_be_visible()
    expect(value(target, "Note")).to_have_value(expected)
    return target


def place_unused_helper(page):
    page.locator("#add-agent").click()
    dialog = page.get_by_role("dialog", name="Agent 추가", exact=True)
    dialog.get_by_role("button", name="OpenAI Responses", exact=True).click()
    dialog.locator('[data-connection-field="model"]').fill("unused-save-fixture")
    dialog.locator('[data-connection-field="endpoint"]').fill("http://127.0.0.1:9")
    dialog.locator("[data-agent-register]").click()
    expect(dialog.locator("[data-agent-registration-state]")).to_contain_text("Agent 등록됨")
    dialog.locator("[data-connection-cancel]").click()
    helper = fixture.call("helperGlobal", {"action": "create", "creationId": uuid.uuid4().hex,
        "name": "Unused local Helper", "personality": "Fixture", "speciality": "Fixture",
        "agent": "Confectory.Agent.Responses::Connection"})["helper"]
    page.locator("#add-helper").click()
    placement = page.get_by_role("dialog", name="프로젝트 도우미 배치", exact=True)
    placement.locator(f'[data-project-helper="{helper}"]').click()
    placement.locator('button[type="submit"]').click()
    expect(placement).to_have_count(0)
    assert fixture.state()["projectHelperIds"] == [helper]


def exercise(browser, source):
    fixture.start(0)
    page = fixture.setup(browser)
    page.set_viewport_size({"width": 2000, "height": 1200})
    primary, _ = fallback.open_from_search(page, fallback.FIRST, fallback.TARGET, fallback.BEFORE)
    value(primary, "Note").fill("primary direct value")
    commit(page, primary)
    assert 'data Note = "primary direct value"' in source.read_text()
    close(primary)
    place_unused_helper(page)
    peer = open_detached(page, fallback.PEER, "PeerFolder", f"{fallback.FIRST} {fallback.PEER}")
    value(peer, "Note").fill("unrelated local input")
    target = open_detached(page, fallback.TARGET, "StockFolder", "primary direct value")
    value(target, "Note").fill("direct value")
    commit(page, target)
    assert 'data Note = "direct value"' in source.read_text()
    expect(value(peer, "Note")).to_have_value("unrelated local input")
    peer_path = source.with_name("private-source-PeerRecord.celem")
    assert peer_path.read_bytes() == fixture.before[str(peer_path)]
    print("PASS primary and detached direct values, unrelated input retained", flush=True)

    target.locator("[data-schema-add]").click()
    definition = target.locator("[data-definition-key]").last
    definition.locator("[data-property-name]").fill("Bonus")
    definition.get_by_label("새 속성 기본값", exact=True).fill("new last focus")
    commit(page, target)
    expect(value(target, "Bonus")).to_have_value("new last focus")
    manifest = source.parent / "project.cpack"
    assert "StockRecord_Properties_" in manifest.read_text()
    generated = list(source.parent.glob("elements/StockRecord_Properties_*.celem"))
    assert len(generated) == 1 and "field Bonus" in generated[0].read_text()
    assert 'data Bonus = "new last focus"' in source.read_text()
    close(target)
    # The retained detached binding reopens the final source.
    target = open_detached(page, fallback.TARGET, "StockFolder", "direct value")
    expect(value(target, "Bonus")).to_have_value("new last focus")
    print("PASS manifest, object and generated schema saved in one explicit action", flush=True)

    # Simulate the browser composition event boundary; there is no native IME.
    field = value(target, "Note")
    field.fill("composing value")
    field.evaluate("el => el.dispatchEvent(new CompositionEvent('compositionstart', {bubbles:true,data:'조합'}))")
    button = target.locator('[data-element-action="confirm"]')
    before = source.read_bytes()
    mark = len(fixture.requests)
    button.click()
    expect(target.locator("[data-element-error]")).to_contain_text("문자 조합")
    assert source.read_bytes() == before
    assert not any(row["endpoint"] in ("blueprint", "confirmGroup") for row in fixture.requests[mark:])
    field.evaluate("el => el.dispatchEvent(new CompositionEvent('compositionend', {bubbles:true,data:'조합'}))")
    expect(field).to_have_value("composing value")
    print("PASS composition guard", flush=True)

    changed = source.read_text().replace('data Note = "direct value"', 'data Note = "external value"')
    source.write_text(changed)
    button.click()
    expect(page.locator("#project-menu")).to_be_enabled(timeout=120000)
    expect(target.locator("[data-element-error]")).not_to_have_text("")
    expect(field).to_have_value("composing value")
    assert source.read_text() == changed
    print("PASS external conflict preserves input and physical edit", flush=True)

    # An already staged peer group is not silently published by another Save.
    fallback.enter_from_home(page, fallback.SECOND)
    second_source = fixture.projects[1].parent / source.name
    second_peer = open_detached(page, fallback.PEER, "PeerFolder", f"{fallback.SECOND} {fallback.PEER}")
    value(second_peer, "Note").fill("existing peer draft")
    second_peer.locator('[data-element-action="save"]').click()
    expect(second_peer.locator('[data-element-action="save"]')).to_be_disabled()
    close(second_peer)
    second_target = open_detached(page, fallback.TARGET, "StockFolder", f"{fallback.SECOND} {fallback.TARGET}")
    value(second_target, "Note").fill("new direct intent")
    mark = len(fixture.requests)
    second_target.locator('[data-element-action="confirm"]').click()
    expect(page.get_by_role("dialog", name="관련 변경 검토")).to_be_visible(timeout=120000)
    assert not any(row["endpoint"] == "confirmGroup" for row in fixture.requests[mark:])
    assert second_source.read_bytes() == fixture.before[str(second_source)]
    second_peer_source = second_source.with_name("private-source-PeerRecord.celem")
    assert second_peer_source.read_bytes() == fixture.before[str(second_peer_source)]
    print("PASS pre-existing draft group remains subject to Review", flush=True)
    assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
    assert not any(row["endpoint"] in ("startAI", "prepareAI", "prepareWorker", "startLogin") for row in fixture.requests)


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
