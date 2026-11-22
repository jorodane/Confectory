"""Review and Confirm a saved compound edit from a filtered Project Browser."""

import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

import v821_browser_compound_roundtrip_ui as data


fixture = data.fixture
MANIFEST = "Example.FrameLoop::ProjectManifest"


def filtered_browser(page, identifier):
    window = data.open_browser(page)
    tree = window.locator(".browser-folder-tree")
    if not tree.is_visible():
        window.locator("[data-browser-detail]").click()
    namespace = tree.locator('[data-namespace="Example.FrameLoop"]')
    expect(namespace).to_be_visible()
    if namespace.get_attribute("aria-current") != "location":
        namespace.click()
    expect(namespace).to_have_attribute("aria-current", "location")
    query = window.locator('[data-browser-control="object-query"]')
    query.fill(identifier.split("::")[-1])
    query.press("Enter")
    density = window.locator('[data-density="100"]')
    if density.get_attribute("aria-pressed") != "true":
        density.click()
    expect(window.locator("[data-object]")).to_have_count(1)
    expect(data.scalar(window, identifier)).to_be_visible()
    expect(page.locator(".brand")).to_be_enabled()
    return window


def save_scalar(window, identifier, value):
    field = data.scalar(window, identifier)
    field.fill(value)
    field.press("Enter")
    window.locator("[data-browser-save]").click()
    expect(window.page.locator("#status")).to_contain_text("작업 사본을 저장했습니다")
    expect(field).to_have_value(value)


def checkpoint_changes():
    checkpoint, = fixture.projects[0].parent.glob(".confectory/edit-workspaces/*/draft.json")
    return {row["id"]: row for row in json.loads(checkpoint.read_text())["changes"]}


def prepare_review(window):
    page = window.page
    start = len(fixture.requests)
    window.locator("[data-browser-confirm]").click()
    review = page.locator('.window[data-key="review"]')
    page.wait_for_function("""() => !!document.querySelector('.window[data-key="review"]:not([hidden])') ||
        !!document.querySelector('#status')?.textContent?.includes('소스 작업을 완료하지 못했습니다')""")
    attempts = [row["input"]["ids"] for row in fixture.requests[start:] if row["endpoint"] == "reviewGroup"]
    assert attempts and set(attempts[-1]) == {data.UNIT, MANIFEST}, attempts
    expect(review).to_be_visible()
    assert set(review.locator("[data-review-unit]").evaluate_all(
        "rows => rows.map(row => row.dataset.reviewUnit)"
    )) == {data.UNIT, MANIFEST}
    review.locator("[data-review-advanced]").click()
    static_manifest = review.locator("[data-review-source] details").filter(
        has=page.get_by_text(MANIFEST + " · 소스 변경", exact=True)
    )
    original = fixture.before[str(fixture.projects[0])].decode("utf-8")
    assert static_manifest.locator("[data-source-before]").text_content() == original
    assert static_manifest.locator("[data-source-after]").text_content() == original
    return review


def edit_and_confirm(page):
    window = filtered_browser(page, data.PEER)
    save_scalar(window, data.PEER, "9")
    window = filtered_browser(page, data.UNIT)
    save_scalar(window, data.UNIT, "7")
    editor = data.open_details(window)
    expect(data.detail_value(editor, "Combat", "Power")).to_have_value(data.INITIAL_POWER)
    data.detail_value(editor, "Combat", "Power").fill(data.SAVED_POWER)
    editor.locator('[data-element-action="save"]').click()
    expect(page.locator(".brand")).to_be_enabled(timeout=60000)
    expect(editor.locator("[data-element-error]")).to_have_text("")
    expect(editor.locator('[data-element-action="discard"]')).to_be_disabled()
    data.close_details(editor)
    expect(data.compound_leaf(window, "Power")).to_have_value(data.SAVED_POWER)
    expect(data.scalar(window)).to_have_value("7")

    checkpoint = checkpoint_changes()
    assert set(checkpoint[data.UNIT]["atomicEditGroup"]) == {data.UNIT, MANIFEST}
    assert checkpoint[MANIFEST]["draft"] == checkpoint[MANIFEST]["original"]
    fixture.original()
    fixture.checked("The saved compound and scalar have an unchanged required manifest and an unrelated saved draft")

    review = prepare_review(window)
    fixture.original()
    before_cancel = sum(row["endpoint"] == "confirmGroup" for row in fixture.requests)
    review.locator("[data-reject]").click()
    expect(review).to_be_hidden()
    assert sum(row["endpoint"] == "confirmGroup" for row in fixture.requests) == before_cancel
    fixture.original()
    assert checkpoint_changes()[data.PEER]["draft"] == checkpoint[data.PEER]["draft"]
    fixture.checked("Review includes the exact required group and cancel preserves every file and draft")

    review = prepare_review(window)
    acknowledge = review.locator("[data-advanced-reviewed]")
    if acknowledge.count():
        acknowledge.check()
    fixture.original()
    review.locator("#confirm").click()
    expect(page.locator("#status")).to_have_text("검토한 변경을 최종 소스에 반영했습니다.", timeout=120000)
    expect(review).to_be_hidden()
    moved = fixture.projects[0].parent / "ProbeUnit.celem"
    for path, expected in fixture.before.items():
        if Path(path) == moved:
            assert moved.read_text() == checkpoint[data.UNIT]["draft"]
        else:
            assert Path(path).read_bytes() == expected, path
    assert checkpoint_changes()[data.PEER]["draft"] == checkpoint[data.PEER]["draft"]
    fixture.checked("Explicit compiler Confirm writes only the chosen object and keeps the peer checkpoint")


def run():
    data.seed()
    try:
        fixture.start(0)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
            page = fixture.setup(browser)
            page.set_viewport_size({"width": 1850, "height": 1180})
            try:
                edit_and_confirm(page)
                page.locator(".brand").click()
                expect(page.locator(".home-grid")).to_be_visible()
                page.close()
                fixture.stop()
                fixture.start(1)
                page = fixture.setup(browser)
                page.set_viewport_size({"width": 1850, "height": 1180})
                window = filtered_browser(page, data.UNIT)
                expect(data.scalar(window)).to_have_value("7")
                expect(data.compound_leaf(window, "Power")).to_have_value(data.SAVED_POWER)
                expect(data.compound_leaf(window, "Label")).to_have_value("원래 복합 값")
                window = filtered_browser(page, data.PEER)
                expect(data.scalar(window, data.PEER)).to_have_value("9")
                peer_file = fixture.projects[0].parent / "ProbePeer.celem"
                assert peer_file.read_bytes() == fixture.before[str(peer_file)]
                assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
                fixture.checked("Fresh host shows the confirmed values and the peer remains a working copy")
            except Exception:
                if not page.is_closed():
                    page.screenshot(path=str(fixture.root / "failure.png"))
                print("COMPOUND_REVIEW_FIXTURE", fixture.root)
                raise
            finally:
                browser.close()
    finally:
        fixture.save_evidence()
        fixture.stop()


if __name__ == "__main__":
    run()
