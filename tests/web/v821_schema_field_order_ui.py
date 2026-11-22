"""Reorder owned schema definitions by native field identity in Linux EditorHome."""
import json
import re
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

import v666_workspace_finder_fixture as fixture
from v821_browser_compound_roundtrip_ui import open_browser

NS = "Example.FrameLoop::"
BASE = NS + "OrderBase"
ORDER = NS + "OrderProbe"
OBJECT = NS + "OrderRecord"
PEER = NS + "OrderPeer"
PEER_DRAFT = "untouched peer draft"
FIELDS = ["AFirst", "BSecond", "CReference"]
FIELD_SOURCES = {
    "AFirst": "field AFirst  single general long;",
    "BSecond": "field BSecond single general long;",
    "CReference": f"field CReference single reference {NS}OrderTargetInfo;",
}


def seed():
    for manifest in fixture.projects:
        parent = manifest.parent
        metadata = {
            "AFirst": "9223372036854775804",
            "BSecond": "21",
            "CReference": json.dumps({"$ref": NS + "OrderTarget"}, separators=(",", ":")),
        }
        defaults = "\n".join(f"  value editorFieldDefault_{key}={json.dumps(value)};" for key, value in metadata.items())
        sources = {
            "OrderBase": ("schema", f"""schema {BASE} {{
              field FromParent single general long;
              value editorInformationDefaults="typed-json-v1";
              value editorFieldDefault_FromParent="11";
            }}"""),
            "OrderProbe": ("schema", f"""// keep description and field syntax
schema {ORDER} extends {BASE} {{
  description "Keep this description";
  {FIELD_SOURCES["AFirst"]}
  // keep this standalone annotation
  {FIELD_SOURCES["BSecond"]}
  {FIELD_SOURCES["CReference"]}
  value editorInformationDefaults="typed-json-v1";
{defaults}
}}
"""),
            "OrderTargetInfo": ("schema", f"schema {NS}OrderTargetInfo {{ field Number single general int; }}"),
            "OrderTarget": ("object", f"object {NS}OrderTarget {{use schema {NS}OrderTargetInfo;data Number=7;}}"),
            "OrderRecord": ("object", f"""object {OBJECT} {{
              use schema {ORDER};
              data AFirst=33;data BSecond=44;data CReference={NS}OrderTarget;data FromParent=55;
            }}"""),
            "OrderPeer": ("object", f'object {PEER} {{description "original peer";}}'),
        }
        registrations = []
        for name, (kind, text) in sources.items():
            path = parent / f"{name}.celem"
            path.write_text(text)
            fixture.before[str(path)] = path.read_bytes()
            registrations.append(f'element {name} {kind} "{path.name}";')
        manifest.write_text(manifest.read_text().rstrip()[:-1] + "\n" + "\n".join(registrations) + "\n}\n")
        fixture.before[str(manifest)] = manifest.read_bytes()
    return fixture.projects[0].parent / "OrderProbe.celem"


def select_details(page, identifier, tab):
    panel = page.locator('.window[data-key="schema"]')
    browser = page.locator('.window[data-key="browser"]')
    if panel.is_visible() and panel.locator(".object-title-name").inner_text() == identifier.split("::")[-1]:
        return panel
    if not browser.is_visible():
        browser = open_browser(page)
    group = browser.locator(f'[data-tab="{tab}"]')
    if "selected" not in (group.get_attribute("class") or ""):
        group.click()
    search = browser.get_by_role("button", name="검색 확정")
    expect(search).to_be_enabled()
    query = browser.locator('[data-browser-control="object-query"]')
    query.fill(identifier.split("::")[-1])
    query.press("Enter")
    card = browser.locator(f'[data-object="{identifier}"]')
    expect(card).to_be_visible()
    expect(search).to_be_enabled()
    card.click(button="right")
    page.locator(".context-menu").get_by_role("button", name="상세 편집", exact=True).click()
    expect(panel.locator(".object-title-name")).to_have_text(identifier.split("::")[-1])
    browser.locator("[data-close]").click()
    return panel


def rows(panel):
    return panel.locator(".own-property-body > .property-fields > [data-property-id]")


def field(panel, name):
    return panel.locator(f'[data-property-path=\'["{name}"]\']')


def order(panel, wanted):
    expect(rows(panel)).to_have_count(len(wanted))
    for index, name in enumerate(wanted):
        expect(rows(panel).nth(index)).to_have_attribute("data-property-id", name, timeout=7000)


def values(panel, record=False):
    for name, value in zip(("AFirst", "BSecond", "FromParent"),
                           ("33", "44", "55") if record else ("9223372036854775804", "21", "11")):
        expect(field(panel, name).get_by_label(name + " 기본값", exact=True)).to_have_value(value)
    expect(field(panel, "CReference").locator(".property-reference-value")).to_have_text("OrderTarget")


def changes(source):
    checkpoint, = source.parent.glob(".confectory/edit-workspaces/*/draft.json")
    return {row["id"]: row["draft"] for row in json.loads(checkpoint.read_text())["changes"]}


def save_peer():
    # A separate, valid, previously saved draft must survive the order edit.
    fixture.call("select", {"id": PEER})
    draft = fixture.state()["draft"]
    fixture.call("editDraft", {"id": PEER, "revision": draft["revision"],
                              "text": draft["text"].replace("original peer", PEER_DRAFT)})
    fixture.call("saveDraft", {})


def edit(page, source):
    panel = select_details(page, ORDER, "info")
    order(panel, FIELDS)
    values(panel)
    # Keep the inheritance boundary fixed.
    inherited = field(panel, "FromParent")
    expect(inherited).to_be_visible()
    assert not inherited.evaluate("row => row.draggable")
    baseline = changes(source)
    field(panel, "BSecond").press("ArrowUp")
    order(panel, ["BSecond", "AFirst", "CReference"])
    expect(page.locator("#title")).to_be_enabled()
    values(panel)
    fixture.original()
    assert changes(source) == baseline
    fixture.checked("ArrowUp reorders only the directly owned fields, with stable IDs and values, before Save")

    # Dropping on the parent group is outside the local permutation.
    field(panel, "CReference").drag_to(inherited, source_position={"x": 3, "y": 3})
    order(panel, ["BSecond", "AFirst", "CReference"])
    target = field(panel, "BSecond")
    field(panel, "CReference").drag_to(target, source_position={"x": 3, "y": 3},
                                       target_position={"x": 4, "y": 3})
    order(panel, ["CReference", "BSecond", "AFirst"])
    expect(page.locator("#title")).to_be_enabled()
    values(panel)
    assert changes(source) == baseline
    save = panel.locator('[data-element-action="save"]')
    expect(save).to_be_enabled(timeout=60000)
    save.click()
    expect(page.locator("#title")).to_be_enabled(timeout=60000)
    expect(save).to_be_disabled(timeout=60000)
    expect(panel.locator("[data-element-error]")).to_have_text("")
    fixture.original()
    updated = changes(source)
    assert updated[PEER] == baseline[PEER] and PEER_DRAFT in updated[PEER]
    target_text = updated[ORDER]
    original = fixture.before[str(source)].decode()
    before_order = iter(FIELD_SOURCES[name] for name in ["CReference", "BSecond", "AFirst"])
    exact = re.sub(r"field (AFirst|BSecond|CReference)[^;]*;", lambda _: next(before_order), original)
    assert target_text == exact, target_text
    fixture.checked("Desktop drop stays in the owner group and Save records only the raw field-clause permutation")
    return target_text, updated[PEER]


def restart(browser, page, index):
    page.locator(".brand").click()
    expect(page.locator(".home-grid")).to_be_visible()
    page.close()
    fixture.stop()
    fixture.start(index)
    opened = fixture.setup(browser)
    opened.set_viewport_size({"width": 1650, "height": 1220})
    return opened


def prepare_review(page, panel):
    panel.locator('[data-element-action="confirm"]').click()
    preview = page.locator('.window[data-key="review"]')
    related = page.locator("#review-creation")
    expect(preview.or_(related)).to_be_visible(timeout=60000)
    if related.is_visible():
        related.click()
    expect(preview).to_be_visible(timeout=60000)
    expect(preview.locator(f'[data-review-unit="{ORDER}"]')).to_be_visible()
    expect(preview.locator(f'[data-review-unit="{PEER}"]')).to_have_count(0)
    return preview


def confirm(page, source, wanted_text, peer):
    panel = select_details(page, ORDER, "info")
    order(panel, ["CReference", "BSecond", "AFirst"])
    values(panel)
    preview = prepare_review(page, panel)
    fixture.original()
    preview.locator("[data-reject]").click()
    expect(preview).to_be_hidden()
    assert changes(source)[ORDER] == wanted_text and changes(source)[PEER] == peer
    fixture.original()
    preview = prepare_review(page, panel)
    preview.locator("[data-review-advanced]").click()
    advanced = preview.locator("[data-advanced-reviewed]")
    if advanced.is_visible():
        advanced.check()
    preview.locator("#confirm").click()
    expect(page.locator("#status")).to_contain_text("최종 소스에 반영", timeout=120000)
    expect(preview).to_be_hidden()
    assert source.read_text() == wanted_text
    assert all(Path(path).read_bytes() == raw for path, raw in fixture.before.items() if Path(path) != source)
    assert changes(source)[PEER] == peer
    fixture.checked("Saved order survives a cold restart; cancelled Review keeps the draft and Confirm writes only the selected schema")


def run():
    source = seed()
    try:
        fixture.start(0)
        save_peer()
        with sync_playwright() as playwright:
            with playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
                page = fixture.setup(browser)
                page.set_viewport_size({"width": 1650, "height": 1220})
                expect.set_options(timeout=22000)
                try:
                    wanted_text, peer = edit(page, source)
                    page = restart(browser, page, 1)
                    confirm(page, source, wanted_text, peer)
                    page = restart(browser, page, 2)
                    panel = select_details(page, ORDER, "info")
                    order(panel, ["CReference", "BSecond", "AFirst"])
                    values(panel)
                    panel.locator("[data-close]").click()
                    values(select_details(page, OBJECT, "concept"), record=True)
                    assert changes(source)[PEER] == peer
                    assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
                    fixture.checked("Confirmed order and exact field values/references reopen; the other object and project retain their data")
                except Exception:
                    if not page.is_closed():
                        page.screenshot(path=str(fixture.root / "failure.png"))
                    raise
    finally:
        fixture.save_evidence()
        fixture.stop()
        print("E01_FIXTURE", fixture.root)


if __name__ == "__main__":
    run()
