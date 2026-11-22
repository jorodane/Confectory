"""An owned object's scalar reset previews the parent value before touching the draft."""
import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

import v666_workspace_finder_fixture as fixture
from v821_schema_field_order_ui import changes, field, restart, select_details

NS = "Example.FrameLoop::"
CHILD = NS + "ResetChild"
PARENT = NS + "ResetParent"
PEER = NS + "ResetPeer"
MANIFEST = NS + "ProjectManifest"
PARENT_LONG = "9223372036854775805"
PEER_EDIT = "Independent peer draft"


def seed():
    for index, manifest in enumerate(fixture.projects):
        revealed = json.dumps("Parent note" if index == 0 else "Second project's note")
        sources = {
            "ResetFields": ("schema", f"""schema {NS}ResetFields {{
  field Note single general string;
  field Empty single general string;
  field Missing single general string;
  field Score single general long;
}}
"""),
            "ResetParent": ("object", f"""object {PARENT} {{
  use schema {NS}ResetFields;
  data Note = {revealed};
  data Empty = "";
  data Score = {PARENT_LONG};
}}
"""),
            "ResetChild": ("object", f"""object {CHILD} extends {PARENT} {{
  data Note = "";
  data Empty = "Child text";
  data Missing = "Only on the child";
  data Score = 23;
}}
"""),
            "ResetPeer": ("object", f'object {PEER} extends {PARENT} {{description "Peer original";}}\n'),
        }
        registrations = []
        for name, (kind, content) in sources.items():
            source = manifest.parent / f"{name}.celem"
            source.write_text(content)
            fixture.before[str(source)] = source.read_bytes()
            registrations.append(f'element {name} {kind} "{source.name}";')
        manifest.write_text(manifest.read_text().rstrip()[:-1] + "\n" + "\n".join(registrations) + "\n}\n")
        fixture.before[str(manifest)] = manifest.read_bytes()
    return fixture.projects[0].parent / "ResetChild.celem"


def input_for(panel, name):
    return field(panel, name).get_by_label(name + " 기본값", exact=True)


def reset_for(panel, name):
    return field(panel, name).locator(".property-reset")


def review(page, panel):
    panel.locator('[data-element-action="confirm"]').click()
    window = page.locator('.window[data-key="review"]')
    related = page.locator("#review-creation")
    expect(window.or_(related)).to_be_visible(timeout=60000)
    if related.is_visible():
        related.click()
    expect(window).to_be_visible(timeout=60000)
    assert set(window.locator("[data-review-unit]").evaluate_all(
        "rows => rows.map(row => row.dataset.reviewUnit)"
    )) == {CHILD, MANIFEST}
    return window


def exercise(browser, page, child, initial):
    panel = select_details(page, CHILD, "concept")
    save = panel.locator('[data-element-action="save"]')
    discard = panel.locator('[data-element-action="discard"]')
    expect(save).to_be_disabled()
    for name, local, expected in (("Note", "", "Parent note"),
                                  ("Empty", "Child text", ""),
                                  ("Score", "23", PARENT_LONG)):
        expect(input_for(panel, name)).to_have_value(local)
        reset_for(panel, name).click()
        expect(input_for(panel, name)).to_have_value(expected)
        expect(reset_for(panel, name)).to_be_hidden()
        assert not field(panel, name).evaluate("row => row.classList.contains('is-overridden')")
    reset_for(panel, "Missing").click()
    expect(input_for(panel, "Missing")).to_have_value("Only on the child")
    expect(reset_for(panel, "Missing")).to_be_visible()
    expect(save).to_be_enabled()
    assert changes(child) == initial
    fixture.original()
    fixture.checked("Before Save: parent text, explicit empty string, and exact long previews; absent parent value is not guessed")

    discard.click()
    expect(page.locator("#title")).to_be_enabled()
    expect(save).to_be_disabled()
    expect(input_for(panel, "Note")).to_have_value("")
    expect(reset_for(panel, "Note")).to_be_visible()
    expect(input_for(panel, "Empty")).to_have_value("Child text")
    expect(input_for(panel, "Score")).to_have_value("23")
    assert changes(child) == initial
    fixture.original()
    fixture.checked("Discard restores the local display and keeps both disk and the independent saved draft unchanged")

    reset_for(panel, "Note").click()
    expect(input_for(panel, "Note")).to_have_value("Parent note")
    save.click()
    expect(page.locator("#title")).to_be_enabled(timeout=60000)
    expect(save).to_be_disabled(timeout=60000)
    fixture.original()
    original = fixture.before[str(child)].decode()
    expected = original.replace('data Note = "";', "", 1)
    saved = changes(child)
    assert saved[CHILD] == expected and saved[PEER] == initial[PEER]
    window = review(page, panel)
    window.locator("[data-reject]").click()
    expect(window).to_be_hidden()
    assert changes(child) == saved
    fixture.original()
    window = review(page, panel)
    window.locator("[data-review-advanced]").click()
    acknowledgement = window.locator("[data-advanced-reviewed]")
    if acknowledgement.is_visible():
        acknowledgement.check()
    window.locator("#confirm").click()
    expect(page.locator("#status")).to_contain_text("최종 소스에 반영", timeout=120000)
    assert child.read_text() == expected
    assert all(Path(path).read_bytes() == raw for path, raw in fixture.before.items() if Path(path) != child)

    page = restart(browser, page, 1)
    panel = select_details(page, CHILD, "concept")
    expect(input_for(panel, "Note")).to_have_value("Parent note")
    expect(reset_for(panel, "Note")).to_be_hidden()
    expect(input_for(panel, "Empty")).to_have_value("Child text")
    assert changes(child)[PEER] == initial[PEER]
    assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
    fixture.checked("Save, Review cancel, Confirm and cold reopen preserve the exact intended removal, all other sources and the separate draft")


def run():
    child = seed()
    try:
        fixture.start(0)
        # Seed an ordinary independent draft, then exercise all child changes through visible UI.
        fixture.call("select", {"id": PEER})
        peer = fixture.state()["draft"]
        fixture.call("editDraft", {"id": PEER, "revision": peer["revision"],
                                   "text": peer["text"].replace("Peer original", PEER_EDIT)})
        fixture.call("saveDraft", {})
        initial = changes(child)
        assert PEER_EDIT in initial[PEER]
        with sync_playwright() as tools:
            with tools.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox", "--disable-gpu"]) as browser:
                page = fixture.setup(browser)
                page.set_viewport_size({"width": 1500, "height": 1050})
                expect.set_options(timeout=23000)
                exercise(browser, page, child, initial)
    finally:
        fixture.save_evidence()
        fixture.stop()
        print("INHERITED_VALUE_RESET_FIXTURE", fixture.root)


if __name__ == "__main__":
    run()
