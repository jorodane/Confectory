"""Edit a scalar through the default schema editor, from search to cold reopen."""

import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

import v666_workspace_finder_fixture as fixture
from v821_project_browser_search_labels import browser_window, choose_tree_location, search
from v821_schema_field_order_ui import changes, field


NS = "Example.FrameLoop"
TARGET, PEER = "StockRecord", "PeerRecord"
FIRST, SECOND = "Fallback First", "Fallback Second"
LABEL = "재고 항목"
BEFORE, AFTER = "9223372036854775804", "9223372036854775805"


def seed():
    for manifest, title, count in zip(fixture.projects, (FIRST, SECOND), (BEFORE, "19")):
        sources = {
            "StockInfo": ("schema", f"""schema {NS}::StockInfo {{
  field Count single general long;
  field Note single general string;
}}"""),
            "StockFolder": ("category", f"category {NS}::StockFolder {{}}"),
            "PeerFolder": ("category", f"category {NS}::PeerFolder {{}}"),
        }
        for item, folder, amount in ((TARGET, "StockFolder", count), (PEER, "PeerFolder", "41")):
            sources[item] = ("object", f"""object {NS}::{item} {{
  use schema {NS}::StockInfo;
  value editorName = "{LABEL}";
  value editorFolder = "{NS}::{folder}";
  data Count = {amount};
  data Note = "{title} {item}";
}}""")
        registrations = []
        for item, (kind, source) in sources.items():
            path = manifest.parent / f"private-source-{item}.celem"
            path.write_text(source + "\n", encoding="utf-8")
            fixture.before[str(path)] = path.read_bytes()
            registrations.append(f'element {item} {kind} "{path.name}";')
        manifest.write_text(manifest.read_text().rstrip()[:-1] + "\n" + "\n".join(registrations) + "\n}\n",
                            encoding="utf-8")
        fixture.before[str(manifest)] = manifest.read_bytes()
    profile = fixture.root / "profile"
    profile.mkdir(exist_ok=True)
    (profile / "projects.json").write_text(json.dumps([
        {"path": str(manifest), "title": title, "description": ""}
        for manifest, title in zip(fixture.projects, (FIRST, SECOND))
    ]), encoding="utf-8")
    return fixture.projects[0].parent / f"private-source-{TARGET}.celem"


def open_from_search(page, title, item, count, *, require_host=False):
    expect(page.locator("#title")).to_contain_text(title)
    window = browser_window(page)
    folder = "StockFolder" if item == TARGET else "PeerFolder"
    choose_tree_location(window, f'[data-tree-id="{NS}::{folder}"]')
    search(window, LABEL, item)
    address = page.url
    row = window.locator(f'[data-object="{NS}::{item}"]')
    if require_host:
        row.click(button="right")
        page.locator(".context-menu").get_by_role("button", name="스키마 열기", exact=True).click()
    else:
        row.press("Enter")
    editor = page.locator('.window[data-key="schema"]')
    expect(editor.get_by_role("heading", name=LABEL, exact=True)).to_be_visible()
    quantity = field(editor, "Count").get_by_label("Count 기본값", exact=True)
    note = field(editor, "Note").get_by_label("Note 기본값", exact=True)
    expect(quantity).to_have_value(count)
    expect(note).to_have_value(f"{title} {item}")
    expect(quantity).to_have_attribute("type", "number")
    expect(quantity).to_have_attribute("step", "1")
    expect(note).to_have_attribute("type", "text")
    expect(quantity).to_be_editable()
    expect(note).to_be_editable()
    expect(page.locator('.window[data-key="source"]')).not_to_be_visible()
    expect(editor).not_to_contain_text(str(fixture.root))
    assert page.url == address
    state = fixture.state()
    if state["draft"]["id"] != f"{NS}::{item}":
        assert not require_host
        assert any(row["id"] == f"{NS}::{item}" for row in state.get("preparedPropertyModels", []))
    else:
        assert state["draft"]["id"] == f"{NS}::{item}"
    return editor, quantity


def leave_to_home(page):
    page.get_by_role("button", name="Confectory 홈으로").click()
    expect(page.locator(".home-grid")).to_be_visible()


def enter_from_home(page, title):
    leave_to_home(page)
    card = page.locator(".project-card").filter(has=page.get_by_role("heading", name=title, exact=True))
    card.locator("[data-enter]").click()
    expect(page.locator("#title")).to_contain_text(title)


def review(page, editor):
    editor.locator('[data-element-action="confirm"]').click()
    window = page.locator('.window[data-key="review"]')
    registration = page.locator("#review-creation")
    expect(window.or_(registration)).to_be_visible(timeout=60000)
    if registration.is_visible():
        registration.click()
    expect(window).to_be_visible(timeout=60000)
    units = set(window.locator("[data-review-unit]").evaluate_all("rows => rows.map(row => row.dataset.reviewUnit)"))
    assert f"{NS}::{TARGET}" in units and units <= {f"{NS}::{TARGET}", f"{NS}::ProjectManifest"}, units
    return window


def edit_and_confirm(page, source):
    editor, quantity = open_from_search(page, FIRST, TARGET, BEFORE)
    quantity.fill(AFTER)
    save = editor.locator('[data-element-action="save"]')
    save.click()
    expect(page.locator("#project-menu")).to_be_enabled(timeout=60000)
    expect(save).to_be_disabled(timeout=60000)
    expect(editor.locator("[data-element-error]")).to_have_text("")
    expect(quantity).to_have_value(AFTER)
    fixture.original()
    expected = fixture.before[str(source)].decode().replace(f"data Count = {BEFORE};", f"data Count = {AFTER};")
    saved = changes(source)
    assert saved[f"{NS}::{TARGET}"] == expected
    fixture.checked("The search result opens typed integer and text fields; Save writes the exact integer to the selected working copy")

    window = review(page, editor)
    window.locator("[data-reject]").click()
    expect(window).to_be_hidden()
    assert changes(source) == saved
    fixture.original()
    window = review(page, editor)
    advanced = window.locator("[data-review-advanced]")
    if advanced.is_visible():
        advanced.click()
    acknowledge = window.locator("[data-advanced-reviewed]")
    if acknowledge.is_visible():
        acknowledge.check()
    window.locator("#confirm").click()
    expect(page.locator("#status")).to_have_text("검토한 변경을 최종 소스에 반영했습니다.", timeout=120000)
    expect(window).to_be_hidden()
    assert source.read_bytes() == expected.encode()
    fixture.before[str(source)] = expected.encode()
    fixture.original()
    fixture.checked("Review cancel keeps the saved draft and all originals; Confirm changes only the selected object's exact field")


def run():
    source = seed()
    with sync_playwright() as playwright:
        expect.set_options(timeout=15000)
        for start in (0, 1):
            fixture.start(start)
            try:
                with playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
                    page = fixture.setup(browser)
                    if start == 0:
                        edit_and_confirm(page, source)
                        leave_to_home(page)
                    else:
                        enter_from_home(page, FIRST)
                        editor, _ = open_from_search(page, FIRST, TARGET, AFTER)
                        editor.get_by_role("button", name="창 닫기", exact=True).click()
                        open_from_search(page, FIRST, PEER, "41")
                        enter_from_home(page, SECOND)
                        open_from_search(page, SECOND, TARGET, "19")
                        fixture.original()
                        fixture.checked("New engine and browser reopen the confirmed value, with the same-name peer and second project unchanged")
                    assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
            finally:
                fixture.stop()


if __name__ == "__main__":
    run()
