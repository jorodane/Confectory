"""Keep the same qualified concept selected across the Project Browser densities."""

from playwright.sync_api import expect, sync_playwright

import v666_workspace_finder_fixture as fixture
from v821_browser_compound_roundtrip_ui import PEER, UNIT, card, close_details, detail_value, open_browser, seed


LABEL = "같은 표시 이름"


def seed_twins():
    seed()
    for identifier in (UNIT, PEER):
        path = fixture.projects[0].parent / (identifier.split("::")[-1] + ".celem")
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("use schema", f'value editorName = "{LABEL}"; use schema', 1),
                        encoding="utf-8")
        fixture.before[str(path)] = path.read_bytes()


def density(window, step, card_class):
    window.locator(f'[data-density="{step}"]').click()
    for identifier in (UNIT, PEER):
        expect(card(window, identifier).and_(window.locator(card_class))).to_be_visible()


def selected(window, identifier):
    expect(window.locator("[data-object].selected")).to_have_attribute("data-object", identifier)
    assert fixture.state()["draft"]["id"] == identifier


def expect_editor(window, speed):
    expect(window).to_be_visible()
    expect(window.locator(".object-title-name")).to_have_text(LABEL)
    expect(detail_value(window, "Speed")).to_have_value(speed)


def check_density_selection(page):
    window = open_browser(page)
    query = window.locator('[data-browser-control="object-query"]')
    query.fill(LABEL)
    query.press("Enter")
    expect(window.locator("[data-object]")).to_have_count(2)

    density(window, 0, ".object-row")
    primary = page.locator('.window[data-key="schema"]')
    card(window, UNIT).locator(".obj-icon").click()
    expect_editor(primary, "2")
    close_details(primary)
    selected(window, UNIT)

    density(window, 40, ".object-card")
    selected(window, UNIT)
    card(window, UNIT).locator(".obj-icon").click()
    expect_editor(primary, "2")
    close_details(primary)
    fixture.checked("Compact and Preview select the same qualified concept despite identical names")

    density(window, 100, ".browser-data-row")
    for identifier, speed in ((UNIT, "2"), (PEER, "3")):
        expect(card(window, identifier).get_by_role("spinbutton", name=LABEL + " Speed", exact=True)).to_have_value(speed)

    mark = len(fixture.requests)
    card(window, UNIT).get_by_role("button", name=LABEL + " 편집", exact=True).click()
    editor = page.locator('.window[data-key^="editor-"]:visible')
    expect_editor(editor, "2")
    opened = [row["input"]["id"] for row in fixture.requests[mark:] if row.get("endpoint") == "openEditorView"]
    assert opened and set(opened) == {UNIT}, opened
    detail_value(editor, "Speed").fill("19")
    editor.locator('[data-element-action="discard"]').click()
    expect(detail_value(editor, "Speed")).to_have_value("2")
    close_details(editor)
    fixture.original()
    fixture.checked("The Data edit opens the exact Preview ID and discarding preserves both sources")

    selected(window, UNIT)
    card(window, PEER).locator(".obj-icon").click()
    expect_editor(primary, "3")
    close_details(primary)
    selected(window, PEER)
    density(window, 40, ".object-card")
    selected(window, PEER)
    density(window, 0, ".object-row")
    selected(window, PEER)
    fixture.checked("Data follows the current selection and carries the new ID back to Preview and Compact")


def run():
    seed_twins()
    try:
        fixture.start(0)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
            page = fixture.setup(browser)
            page.set_viewport_size({"width": 1850, "height": 1180})
            try:
                check_density_selection(page)
                assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
            except Exception:
                page.screenshot(path=str(fixture.root / "failure.png"))
                raise
            finally:
                browser.close()
    finally:
        print("BROWSER_DENSITY_FIXTURE", fixture.root)
        fixture.save_evidence()
        fixture.stop()


if __name__ == "__main__":
    run()
