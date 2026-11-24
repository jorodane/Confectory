"""Exercise declared object references in the Linux project browser."""

import json

from playwright.sync_api import expect, sync_playwright

import v666_workspace_finder_fixture as fixture
from v821_project_browser_search_labels import NS, browser_window, search


FIRST, SECOND = "Reference Direction First", "Reference Direction Second"


def seed():
    for project, target in zip(fixture.projects, ("TargetB", "UnrelatedC")):
        declarations = {
            "Vitals": ("schema", "field HP single general int;"),
            "Links": ("schema", f"field Target single reference {NS}::Vitals;"),
            "SourceA": ("object", f"use schema {NS}::Links; data Target = {NS}::{target};"),
            "TargetB": ("object", f"use schema {NS}::Vitals; data HP = 2;"),
            "UnrelatedC": ("object", f"use schema {NS}::Vitals; data HP = 3;"),
            "VariantOfB": ("object", "", "TargetB"),
        }
        entries = []
        for name, (kind, body, *parent) in declarations.items():
            extends = f" extends {NS}::{parent[0]}" if parent else ""
            path = project.parent / f"private-source-{name}.celem"
            path.write_text(f"{kind} {NS}::{name}{extends} {{ {body} }}\n")
            fixture.before[str(path)] = path.read_bytes()
            entries.append(f'element {name} {kind} "{path.name}";')
        project.write_text(project.read_text().rstrip()[:-1] + "\n" + "\n".join(entries) + "\n}\n")
        fixture.before[str(project)] = project.read_bytes()
    profile = fixture.root / "profile"
    profile.mkdir()
    (profile / "projects.json").write_text(json.dumps([
        {"path": str(path), "title": title, "description": ""}
        for path, title in zip(fixture.projects, (FIRST, SECOND))
    ]))


def hover(window, row):
    search(window, row, row)
    window.locator(f'[data-object="{NS}::{row}"]').hover()
    tip = window.page.get_by_role("tooltip")
    expect(tip).to_be_visible()
    expect(tip).not_to_contain_text("private-source-")
    return tip


def scenario(page):
    window = browser_window(page)
    tip = hover(window, "SourceA")
    expect(tip).to_contain_text("직접 참조: TargetB")
    expect(tip).not_to_contain_text("UnrelatedC")
    page.keyboard.down("Shift")
    expect(tip).to_contain_text("직접 역참조 없음")
    expect(tip).not_to_contain_text("TargetB")
    page.keyboard.up("Shift")
    expect(tip).to_contain_text("직접 참조: TargetB")

    tip = hover(window, "UnrelatedC")
    expect(tip).to_contain_text("직접 참조 없음")
    page.keyboard.down("Shift")
    expect(tip).to_contain_text("직접 역참조 없음")
    page.keyboard.up("Shift")

    tip = hover(window, "VariantOfB")
    expect(tip).to_contain_text("직접 참조 없음")
    expect(tip).to_contain_text("상속 부모: TargetB")

    tip = hover(window, "TargetB")
    expect(tip).to_contain_text("직접 참조 없음")
    page.keyboard.down("Shift")
    expect(tip).to_contain_text("직접 역참조: SourceA")
    expect(tip).to_contain_text("상속 바리에이션: VariantOfB")
    fixture.checked("A to B is directional, C is unrelated, and inheritance is listed separately")

    home = page.get_by_role("button", name="Confectory 홈으로")
    home.press("Enter")
    expect(page.locator(".home-grid")).to_be_visible()
    expect(tip).to_have_count(0)
    page.keyboard.up("Shift")
    page.locator(".project-card").filter(
        has=page.get_by_role("heading", name=SECOND, exact=True)
    ).locator("[data-enter]").click()
    expect(page.locator("#title")).to_contain_text(SECOND)
    expect(tip).to_have_count(0)
    tip = hover(browser_window(page), "SourceA")
    expect(tip).to_contain_text("직접 참조: UnrelatedC")
    expect(tip).not_to_contain_text("TargetB")
    assert not any(request["endpoint"] == "select" for request in fixture.requests)
    fixture.original()
    fixture.checked("Project switch clears the hover; the same ID resolves from its own project without writes")


if __name__ == "__main__":
    seed()
    fixture.start(0)
    try:
        with sync_playwright() as playwright, playwright.chromium.launch(
                executable_path="/usr/bin/chromium", args=["--no-sandbox", "--disable-gpu"],
                ignore_default_args=["--disable-dev-shm-usage"]) as browser:
            expect.set_options(timeout=6000)
            scenario(fixture.setup(browser))
            assert not fixture.errors and not fixture.external
    finally:
        fixture.stop()
