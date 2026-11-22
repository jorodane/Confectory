"""Confirm a Category move through the Browser and reopen the saved sources."""

import os
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

import v821_category_move_identity_ui as category


fixture = category.fixture


def source_files():
    sources = {}
    for manifest in fixture.projects:
        for root, directories, names in os.walk(manifest.parent):
            directories[:] = [name for name in directories if name not in (".confectory", ".build")]
            for name in names:
                path = Path(root) / name
                sources[path] = path.read_bytes()
    return sources


def assert_only_classification_changed(original, moved):
    current = source_files()
    assert current.keys() == original.keys(), current.keys() ^ original.keys()
    changed = {path for path in current if current[path] != original[path]}
    assert changed == {moved}, changed
    expected = original[moved].decode("utf-8").replace(f'"{category.ORIGIN}"', f'"{category.DESTINATION}"')
    assert category.flat_declaration(current[moved].decode("utf-8")) == category.flat_declaration(expected)
    return current


def open_review(window, original):
    page = window.page
    window.locator("[data-browser-confirm]").click()
    review = page.locator('.window[data-key="review"]')
    expect(review).to_be_visible()
    units = review.locator("[data-review-unit]")
    expected_ids = {category.MOVING, category.ORIGIN, category.DESTINATION}
    assert set(units.evaluate_all("rows => rows.map(row => row.dataset.reviewUnit)")) == expected_ids
    changes = review.locator("[data-semantic-change]")
    expect(changes).to_have_count(1)
    change = review.locator(f'[data-review-unit="{category.MOVING}"]').get_by_role("group", name="분류 위치", exact=True)
    expect(change.locator("[data-semantic-before]")).to_have_text("StartFolder")
    expect(change.locator("[data-semantic-after]")).to_have_text("DestinationFolder")
    expect(review.locator('input[data-review-group]')).to_have_count(1)
    expect(review.locator('input[data-review-group]')).to_be_checked()
    review.locator("[data-review-advanced]").click()
    sources = review.locator("[data-review-source] details")
    expect(sources).to_have_count(len(expected_ids))
    for identifier in expected_ids:
        source = sources.filter(has=page.get_by_text(identifier + " · 소스 변경", exact=True))
        path = fixture.projects[0].parent / (identifier.split("::")[1] + ".celem")
        before = original[path].decode("utf-8")
        expect(source.locator("[data-source-before]")).to_be_visible()
        assert source.locator("[data-source-before]").text_content() == before
        after = source.locator("[data-source-after]").text_content()
        if identifier == category.MOVING:
            expected = before.replace(f'"{category.ORIGIN}"', f'"{category.DESTINATION}"')
            assert category.flat_declaration(after) == category.flat_declaration(expected)
        else:
            assert after == before
    return review


def stage_and_confirm(page, original):
    window = category.open_browser(page)
    category.tree_id(window, category.ORIGIN).click()
    expect(category.tree_id(window, category.ORIGIN)).to_have_attribute("aria-current", "location")
    mover = category.object_card(window)
    destination = category.tree_id(window, category.DESTINATION)
    expect(mover).to_have_attribute("draggable", "true")
    mover.locator(".obj-icon").hover()
    start = mover.locator(".obj-icon").bounding_box()
    target = destination.bounding_box()
    assert start and target
    mouse = page.mouse
    mouse.down()
    mouse.move(target["x"] + target["width"] / 2, target["y"] + target["height"] / 2, steps=14)
    mouse.move(target["x"] + target["width"] / 2 + 2, target["y"] + target["height"] / 2)
    mouse.up()
    expect(page.locator("#status")).to_contain_text("분류 위치를 변경했어요")
    assert source_files() == original

    window.locator("[data-browser-save]").click()
    expect(page.locator("#status")).to_contain_text("작업 사본을 저장했습니다")
    assert source_files() == original
    fixture.checked("Browser drag and explicit Save retain the original bytes in both projects")

    review = open_review(window, original)
    assert source_files() == original
    before_cancel = sum(row["endpoint"] == "confirmGroup" for row in fixture.requests)
    review.locator("[data-reject]").click()
    expect(review).to_be_hidden()
    assert sum(row["endpoint"] == "confirmGroup" for row in fixture.requests) == before_cancel
    assert source_files() == original
    fixture.checked("Review shows the folder change and both unchanged categories; cancel issues no Confirm")

    review = open_review(window, original)
    acknowledge = review.locator("[data-advanced-reviewed]")
    if acknowledge.count():
        expect(review.locator("#confirm")).to_be_disabled()
        acknowledge.check()
    assert source_files() == original
    review.locator("#confirm").click()
    expect(page.locator("#status")).to_have_text("검토한 변경을 최종 소스에 반영했습니다.", timeout=120000)
    expect(review).to_be_hidden()
    moved = fixture.projects[0].parent / "Mover.celem"
    confirmed = assert_only_classification_changed(original, moved)
    fixture.checked("Explicit compiler Confirm changes only Mover.celem and only its folder value")
    return confirmed


def check_reopened_projects(page, confirmed):
    expect(page.locator("#title")).to_contain_text("Category First")
    window = category.open_browser(page)
    category.tree_id(window, category.ORIGIN).click()
    expect(category.object_card(window)).to_have_count(0)
    category.tree_id(window, category.DESTINATION).click()
    expect(window.locator(".browser-title-path")).to_contain_text("DestinationFolder")
    expect(category.object_card(window)).to_be_visible()
    expect(category.tree_id(window, category.DESTINATION)).to_have_attribute("aria-current", "location")

    category.tree_id(window, category.LINKS).dblclick()
    references = page.locator('.window[data-key="declaration"]')
    expect(references.locator("[data-declaration-id]")).to_have_text(category.LINKS)
    references.locator("[data-declaration-references] summary").click()
    references.locator(f'[data-reference-target="{category.MOVING}"]').click()
    editor = page.locator('.window[data-key="schema"]')
    expect(editor.locator(".object-title-name")).to_have_text("Mover")
    expect(editor.locator(".object-parent-reference [data-parent] strong")).to_have_text("BaseUnit")
    expect(editor.get_by_label("HP 기본값", exact=True)).to_have_value("41")
    assert source_files() == confirmed
    fixture.checked("A new editor process shows the confirmed folder and the old reference opens the same inherited concept")

    page.locator(".brand").click()
    expect(page.locator(".home-grid")).to_be_visible()
    page.locator(".project-card").filter(
        has=page.get_by_role("heading", name="Category Second", exact=True)
    ).locator("[data-enter]").click()
    expect(page.locator("#title")).to_contain_text("Category Second")
    window = category.open_browser(page)
    category.tree_id(window, category.ORIGIN).click()
    expect(category.object_card(window)).to_be_visible()
    category.object_card(window).click()
    expect(page.locator('.window[data-key="schema"]').get_by_label("HP 기본값", exact=True)).to_have_value("84")
    assert source_files() == confirmed
    fixture.checked("The second project retains its own category and field for the same qualified ID")


def run():
    category.seed_projects()
    original = source_files()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
            fixture.start(0)
            page = fixture.setup(browser)
            page.set_viewport_size({"width": 1850, "height": 1180})
            try:
                confirmed = stage_and_confirm(page, original)
                old_host = fixture.host
                page.close()
                fixture.stop()
                assert old_host.poll() is not None
                fixture.start(1)
                assert fixture.host.pid != old_host.pid
                page = fixture.setup(browser)
                page.set_viewport_size({"width": 1850, "height": 1180})
                check_reopened_projects(page, confirmed)
                assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
            except Exception:
                if not page.is_closed():
                    page.screenshot(path=str(fixture.root / "failure.png"))
                print("CATEGORY_CONFIRM_FIXTURE", fixture.root)
                raise
            finally:
                browser.close()
    finally:
        fixture.save_evidence()
        fixture.stop()


if __name__ == "__main__":
    run()
