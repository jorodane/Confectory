"""Compare existing module/provider details with the Linux compiler's binding IDs."""
import json
import os
import subprocess
from pathlib import Path

from playwright.sync_api import expect, sync_playwright
import v666_workspace_finder_fixture as f
from v821_browser_compound_roundtrip_ui import open_browser
from v821_schema_field_order_ui import restart, select_details

PREFIX = "Example.FrameLoop::"
EXT = "Origin.Library::"
SLOT = EXT + "Value"
RULES = PREFIX + "OriginRules"
BASE_MODULE = EXT + "DefaultRules"
DEFAULT = EXT + "DefaultBody"
PARENT = PREFIX + "OriginParent"
PARENT_BODY = PREFIX + "InheritedBody"
LOCAL_BODY = PREFIX + "DirectBody"
FALLBACK = PREFIX + "FallbackProbe"
INHERITED = PREFIX + "InheritedProbe"
EXPLICIT = PREFIX + "ExplicitProbe"


def seed():
    for manifest in f.projects:
        base = manifest.parent
        library = base / "registered-origin"
        library.mkdir()
        external_files = {
            "pack.cpack": """pack Origin.Library version "1" {
element Value function "Value.celem";
element DefaultBody implementation "DefaultBody.celem";
element DefaultRules module "DefaultRules.celem";}""",
            "Value.celem": f"function {SLOT} (long value) -> long {{}}",
            "DefaultBody.celem": f'implementation {DEFAULT} for {SLOT} (long value) -> long {{body common "Default.csbody";}}',
            "DefaultRules.celem": f"module {BASE_MODULE} {{require {SLOT} (long) -> long;default {SLOT} with {DEFAULT};}}",
            "Default.csbody": "return value + 10;",
        }
        for name, content in external_files.items():
            path = library / name
            path.write_text(content + "\n")
            f.before[str(path)] = path.read_bytes()
        defs = {
            "OriginRules": ("module", f"module {RULES} extends {BASE_MODULE} {{}}"),
            "OriginParent": ("object", f"object {PARENT} {{provide {SLOT} with {PARENT_BODY};}}"),
            "InheritedProbe": ("object", f"object {INHERITED} extends {PARENT} {{module {RULES};}}"),
            "ExplicitProbe": ("object", f"object {EXPLICIT} extends {PARENT} {{module {RULES};provide {SLOT} with {LOCAL_BODY};}}"),
            "FallbackProbe": ("object", f"object {FALLBACK} {{module {RULES};provide {SLOT} with {LOCAL_BODY};}}"),
        }
        for body, value in (("InheritedBody", 20), ("DirectBody", 30)):
            path = base / f"{body}.csbody"
            path.write_text(f"return value + {value};\n")
            f.before[str(path)] = path.read_bytes()
            defs[body] = ("implementation", f'implementation {PREFIX}{body} for {SLOT} (long value) -> long {{body common "{body}.csbody";}}')
        for name, (kind, content) in defs.items():
            path = base / f"{name}.celem"
            path.write_text(content + "\n")
            f.before[str(path)] = path.read_bytes()
        regs = "".join(f'element {name} {kind} "{name}.celem";' for name, (kind, _) in defs.items())
        manifest.write_text(manifest.read_text().rstrip()[:-1] +
                            f'\nregistry Origin.Library "{library / "pack.cpack"}";dependency Origin.Library version "1";\n' +
                            regs + "\n}\n")
        imports = " ".join(f"import {SLOT} as {name} (long) -> long in {owner};" for name, owner in
                           (("Fallback", FALLBACK), ("Inherited", INHERITED), ("Explicit", EXPLICIT)))
        entry = base / "MainBody.celem"
        entry.write_text(f'implementation {PREFIX}MainBody for {PREFIX}Main () -> int {{{imports}body common "Main.csbody";}}\n')
        body = base / "Main.csbody"
        body.write_text("return checked((int)(calls.Fallback.Invoke(0L) + calls.Inherited.Invoke(0L) + calls.Explicit.Invoke(0L)));\n")
        for path in (manifest, entry, body):
            f.before[str(path)] = path.read_bytes()


def compile_bindings(name, expected):
    output = subprocess.check_output([os.environ["CONFECTORY_DOTNET"],
        str(f.repo / "src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll"),
        "build", str(f.projects[0]), "linux"], text=True, timeout=180)
    data = json.loads(output)
    actual = {row["owner"]: row["implementation"] for row in data["bindings"] if row["function"] == SLOT}
    (f.root / (name + "-bindings.json")).write_text(json.dumps(actual, indent=2))
    assert actual == expected, actual


def close_panels(page):
    for key in ("schema", "declaration"):
        window = page.locator(f'.window[data-key="{key}"]')
        if window.is_visible():
            window.locator("[data-close]").click()


def browse(page, qualified, tab):
    browser = page.locator('.window[data-key="browser"]')
    if not browser.is_visible():
        browser = open_browser(page)
    group = browser.locator(f'[data-tab="{tab}"]')
    if "selected" not in (group.get_attribute("class") or ""):
        group.click()
    search = browser.get_by_role("button", name="검색 확정")
    expect(search).to_be_enabled()
    query = browser.locator('[data-browser-control="object-query"]')
    query.fill(qualified.split("::")[-1])
    query.press("Enter")
    card = browser.locator(f'[data-object="{qualified}"]')
    expect(card).to_be_visible()
    expect(search).to_be_enabled()
    return browser, card


def open_declaration(page, qualified, tab="concept"):
    close_panels(page)
    browser, card = browse(page, qualified, tab)
    assert card.get_attribute("data-readonly") != "true"
    card.press("F2")
    panel = page.locator('.window[data-key="declaration"]')
    expect(panel.locator("[data-declaration-id]")).to_have_text(qualified)
    if browser.is_visible():
        browser.locator("[data-close]").click()
    return panel


def applied(page, owner):
    panel = open_declaration(page, owner)
    panel.locator("[data-object-modules-read]").click()
    p = panel.locator(f'[data-object-provider="{SLOT}"]')
    expect(p).to_be_visible()
    return panel, p


def assert_detail(p, implementation=None, origin=None):
    expected = f"{implementation} ← {origin}" if implementation else "읽은 객체 제공 지정 없음"
    expect(p.locator("[data-object-provider-origin]")).to_contain_text(expected)
    expect(p.locator("[data-object-provider-defaults]")).to_contain_text(f"{DEFAULT} ← {BASE_MODULE}")


def confirm(page, panel, owner):
    panel.locator("[data-declaration-review]").click()
    review = page.locator('.window[data-key="review"]')
    expect(review).to_be_visible(timeout=60000)
    assert review.locator("[data-review-unit]").evaluate_all("rows => rows.map(row => row.dataset.reviewUnit)") == [owner]
    review.locator("[data-review-advanced]").click()
    ack = review.locator("[data-advanced-reviewed]")
    if ack.is_visible():
        ack.check()
    review.locator("#confirm").click()
    expect(review).to_be_hidden(timeout=120000)


def remove_and_confirm(page, owner, parent_provides):
    panel, p = applied(page, owner)
    assert_detail(p, LOCAL_BODY, owner)
    path = f.projects[0].parent / (owner.split("::")[-1] + ".celem")
    before = path.read_bytes()
    p.locator("[data-object-provider-remove]").click()
    assert_detail(p, PARENT_BODY if parent_provides else None, PARENT if parent_provides else None)
    expect(p.locator("[data-object-provider-value]")).to_have_value("")
    assert path.read_bytes() == before
    confirm(page, panel, owner)
    expected = before.decode().replace(f"provide {SLOT} with {LOCAL_BODY};", "", 1)
    assert "".join(path.read_text().split()) == "".join(expected.split())


def view_status(page, owner, status, title=None):
    close_panels(page)
    panel = select_details(page, owner, "concept")
    card = panel.locator(f'[data-behavior-source="{RULES}"] [data-module-method="{SLOT}"]')
    expect(card).to_have_count(1)
    badge = card.locator(".function-implementation-status")
    expect(badge).to_have_text(status)
    if title:
        expect(badge).to_have_attribute("title", title)


def run():
    seed()
    try:
        compile_bindings("before", {EXPLICIT: LOCAL_BODY, FALLBACK: LOCAL_BODY, INHERITED: PARENT_BODY})
        f.start(0)
        with sync_playwright() as tools:
            with tools.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox", "--disable-gpu"]) as browser:
                expect.set_options(timeout=18000)
                page = f.setup(browser)
                page.set_viewport_size({"width": 1500, "height": 1050})
                module = open_declaration(page, RULES, "module")
                module.locator("[data-module-read]").click()
                expect(module.locator(f'[data-module-function="{SLOT}"]')).to_contain_text(f"{DEFAULT} ← {BASE_MODULE}")
                expect(page.locator("#title")).to_be_enabled()
                refs = module.locator("[data-declaration-references]")
                refs.locator("summary").click()
                refs.locator(f'[data-reference-target="{BASE_MODULE}"]').click()
                foreign = page.locator('.window[data-key^="definition"]')
                expect(foreign).to_contain_text("읽기 전용")
                expect(foreign).to_contain_text(BASE_MODULE)
                expect(foreign.locator("[data-reference-text]")).not_to_be_editable()
                foreign.locator("[data-close]").click()
                _, row = applied(page, INHERITED)
                assert_detail(row, PARENT_BODY, PARENT)
                expect(row.locator("[data-object-provider-value]")).to_have_value("")
                view_status(page, EXPLICIT, "구현 연결")
                view_status(page, INHERITED, "구현 상속됨", "구현: OriginParent")
                f.original()
                f.checked("Module and object views attribute defaults to the read-only pack and display the inherited requirement with the correct implementation provenance")
                remove_and_confirm(page, EXPLICIT, parent_provides=True)
                remove_and_confirm(page, FALLBACK, parent_provides=False)
                page = restart(browser, page, 1)
                for owner, impl, origin in ((EXPLICIT, PARENT_BODY, PARENT), (FALLBACK, None, None)):
                    _, row = applied(page, owner)
                    assert_detail(row, impl, origin)
                    expect(row.locator("[data-object-provider-value]")).to_have_value("")
                view_status(page, EXPLICIT, "구현 상속됨", "구현: OriginParent")
                view_status(page, FALLBACK, "기본 구현 후보")
                changed = {f.projects[0].parent / "ExplicitProbe.celem", f.projects[0].parent / "FallbackProbe.celem"}
                assert all(Path(p).read_bytes() == raw for p, raw in f.before.items() if Path(p) not in changed)
                assert not f.errors and not f.external, (f.errors, f.external)
                f.checked("Existing removal restores inherited and default declaration origins after Confirm and restart; external and unrelated sources are byte-identical")
        compile_bindings("after", {EXPLICIT: PARENT_BODY, FALLBACK: DEFAULT, INHERITED: PARENT_BODY})
        f.checked("Linux compiler bindings agree with the declaration origins without executing the fixture")
    finally:
        f.save_evidence()
        f.stop()
        print("PROVIDER_ORIGIN_FIXTURE", f.root)


if __name__ == "__main__":
    run()
