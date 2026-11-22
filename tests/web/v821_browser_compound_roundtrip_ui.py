"""Exercise real single-compound values from the Project Browser Data view."""

import json

from playwright.sync_api import expect, sync_playwright

import v666_workspace_finder_fixture as fixture


UNIT = "Example.FrameLoop::ProbeUnit"
PEER = "Example.FrameLoop::ProbePeer"
INITIAL_POWER = "9223372036854775804"
SAVED_POWER = "9223372036854775805"
SAVED_LABEL = '복합 "저장" 값'
PEER_INPUT = "2147483648"


def seed():
    manifest = fixture.projects[0]
    sources = {
        "Details": ("schema", """schema Example.FrameLoop::Details {
            field Power single general long; field Label single general string;
        }"""),
        "Stats": ("schema", """schema Example.FrameLoop::Stats {
            field Speed single general int;
            field Combat single compound Example.FrameLoop::Details;
        }"""),
        "ProbeUnit": ("object", f"""object {UNIT} {{
            use schema Example.FrameLoop::Stats;
            data Speed = 2; data Combat = {{Power = {INITIAL_POWER}; Label = "원래 복합 값";}};
        }}"""),
        "ProbePeer": ("object", f"""object {PEER} {{
            use schema Example.FrameLoop::Stats;
            data Speed = 3; data Combat = {{Power = 34; Label = "별도 개념";}};
        }}"""),
    }
    registrations = []
    for name, (kind, source) in sources.items():
        path = manifest.parent / f"{name}.celem"
        path.write_text(source, encoding="utf-8")
        fixture.before[str(path)] = path.read_bytes()
        registrations.append(f'element {name} {kind} "{path.name}";')
    manifest.write_text(manifest.read_text().rstrip()[:-1] + "\n" + "\n".join(registrations) + "\n}\n",
                        encoding="utf-8")
    fixture.before[str(manifest)] = manifest.read_bytes()


def open_browser(page):
    page.locator("#title").click()
    page.locator(".context-menu").get_by_role("button", name="프로젝트 브라우저", exact=True).click()
    window = page.locator('.window[data-key="browser"]')
    expect(window).to_be_visible()
    return window


def card(window, identifier=UNIT):
    return window.locator(f'[data-object="{identifier}"]')


def scalar(window, identifier=UNIT):
    return card(window, identifier).get_by_role("spinbutton", name=identifier.split("::")[-1] + " Speed", exact=True)


def compound_leaf(window, leaf):
    return card(window).get_by_label("ProbeUnit Combat." + leaf, exact=True)


def open_details(window):
    card(window).get_by_role("button", name="ProbeUnit 편집", exact=True).click()
    page = window.page
    editor = page.locator('.window[data-key^="editor-"]:visible').filter(
        has=page.locator(".object-title-name").filter(has_text="ProbeUnit")
    )
    expect(editor).to_be_visible()
    expect(editor.locator('[data-property-path=\'["Combat"]\'] .property-complex-body')).to_be_visible()
    return editor


def detail_value(editor, *path):
    key = json.dumps(path, separators=(",", ":"))
    return editor.locator(f"[data-property-path='{key}'] [data-property-value]")


def close_details(editor):
    editor.locator(":scope > .object-header [data-close]").click()
    expect(editor).to_be_hidden()


def check_values(window):
    expect(scalar(window)).to_have_value("7")
    expect(compound_leaf(window, "Power")).to_have_value(SAVED_POWER)
    expect(compound_leaf(window, "Label")).to_have_value(SAVED_LABEL)
    expect(scalar(window, PEER)).to_have_value(PEER_INPUT)


def check_roundtrip(page):
    window = open_browser(page)
    query = window.locator('[data-browser-control="object-query"]')
    query.fill("Probe")
    query.press("Enter")
    window.locator('[data-density="100"]').click()

    speed = scalar(window)
    expect(speed).to_have_value("2")
    speed.fill("99")
    speed.press("Escape")
    expect(speed).to_have_value("2")
    speed.fill("7")
    speed.press("Enter")
    window.locator("[data-browser-save]").click()
    expect(page.locator("#status")).to_contain_text("작업 사본을 저장했습니다")
    expect(speed).to_have_value("7")
    fixture.original()
    fixture.checked("Inline scalar Escape cancels the input and explicit Save retains the accepted value")

    peer = scalar(window, PEER)
    peer.fill(PEER_INPUT)
    peer.press("Enter")
    expect(peer).to_have_attribute("aria-invalid", "true")
    expect(compound_leaf(window, "Power")).to_have_value(INITIAL_POWER)
    editor = open_details(window)
    power = detail_value(editor, "Combat", "Power")
    label = detail_value(editor, "Combat", "Label")
    expect(power).to_have_value(INITIAL_POWER)
    expect(label).to_have_value("원래 복합 값")
    power.fill("123")
    label.fill("취소할 입력")
    editor.locator('[data-element-action="discard"]').click()
    expect(power).to_have_value(INITIAL_POWER)
    expect(label).to_have_value("원래 복합 값")
    close_details(editor)
    editor = open_details(window)
    power = detail_value(editor, "Combat", "Power")
    label = detail_value(editor, "Combat", "Label")
    expect(power).to_have_value(INITIAL_POWER)
    expect(label).to_have_value("원래 복합 값")
    fixture.checked("Cancel and reopen keep the saved compound without touching the scalar or the peer")

    power.fill(SAVED_POWER)
    label.fill(SAVED_LABEL)
    editor.locator('[data-element-action="save"]').click()
    expect(page.locator(".brand")).to_be_enabled(timeout=60000)
    expect(editor.locator("[data-element-error]")).to_have_text("")
    expect(editor.locator('[data-element-action="discard"]')).to_be_disabled()
    close_details(editor)
    editor = open_details(window)
    expect(detail_value(editor, "Combat", "Power")).to_have_value(SAVED_POWER)
    expect(detail_value(editor, "Combat", "Label")).to_have_value(SAVED_LABEL)
    expect(detail_value(editor, "Speed")).to_have_value("7")
    close_details(editor)
    fixture.original()
    fixture.checked("The detail Save persists exact compound fields and retains the sibling scalar")
    check_values(window)
    expect(peer).to_have_attribute("aria-invalid", "true")
    fixture.checked("The original Data rows show the saved compound while retaining the other record's unsubmitted input")


def run():
    seed()
    try:
        fixture.start(0)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
            page = fixture.setup(browser)
            page.set_viewport_size({"width": 1850, "height": 1180})
            try:
                check_roundtrip(page)
                page.locator(".brand").click()
                expect(page.locator(".home-grid")).to_be_visible()
                page.close()
                fixture.stop()
                fixture.start(1)
                page = fixture.setup(browser)
                page.set_viewport_size({"width": 1850, "height": 1180})
                window = open_browser(page)
                check_values(window)
                scalar(window, PEER).press("Escape")
                expect(scalar(window, PEER)).to_have_value("3")
                expect(compound_leaf(window, "Power")).to_have_value(SAVED_POWER)
                expect(compound_leaf(window, "Label")).to_have_value(SAVED_LABEL)
                fixture.original()
                assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
                fixture.checked("Cold restart keeps the saved compound and the separately cancellable peer input")
            except Exception:
                if not page.is_closed():
                    page.screenshot(path=str(fixture.root / "failure.png"))
                print("COMPOUND_BROWSER_FIXTURE", fixture.root)
                raise
            finally:
                browser.close()
    finally:
        fixture.save_evidence()
        fixture.stop()


if __name__ == "__main__":
    run()
