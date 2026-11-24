"""Hover the real declaration map through the Linux editor's project menu."""

from playwright.sync_api import expect, sync_playwright

import v666_workspace_finder_fixture as fixture
from v821_browser_reference_hover import NS, SECOND, seed


def open_map(page):
    page.locator("#project-menu").click()
    page.locator(".context-menu").get_by_role("button", name="프로젝트 도구", exact=True).click()
    page.locator(".nav-menu").get_by_role("button", name="개념 맵", exact=True).click()
    graph = page.locator('.window[data-key="map"]')
    expect(graph.locator("[data-map-scene]")).to_be_visible(timeout=30000)
    graph.get_by_role("button", name="맞춤", exact=True).click()
    return graph


def node(graph, name):
    return graph.locator(f'[data-relation-node="{NS}::{name}"]')


def edge(graph, label):
    return graph.locator("[data-relation-edge]").filter(has_text=label)


def scenario(page):
    graph = open_map(page)
    a, b, c = (node(graph, name) for name in ("SourceA", "TargetB", "UnrelatedC"))
    data, parent = edge(graph, "값 참조"), edge(graph, "상속")
    path = data.locator("path")
    marks = graph.locator("[data-reference-hover]")
    expect(a).to_have_css("position", "absolute")
    expect(graph.locator("[data-map-edges]")).to_have_css("position", "absolute")
    expect(path).to_have_attribute("marker-end", "url(#declared-map-arrow)")
    normal_stroke = path.evaluate("e => getComputedStyle(e).stroke")
    assert normal_stroke != "none"
    arrow_path = path.get_attribute("d")

    c.press("Enter")
    expect(c).to_have_class("relation-map-node selected")
    a.hover()
    expect(data).to_have_attribute("data-reference-hover", "outgoing")
    expect(path).to_have_css("stroke-width", "4px")
    assert path.evaluate("e => getComputedStyle(e).stroke") != normal_stroke
    expect(parent.locator("path")).to_have_css("stroke-width", "2px")
    expect(marks).to_have_count(1)
    page.keyboard.down("Shift")
    expect(marks).to_have_count(0)
    page.keyboard.up("Shift")
    expect(data).to_have_attribute("data-reference-hover", "outgoing")
    page.screenshot(path=str(fixture.root / "outgoing.png"))

    b.hover()
    expect(marks).to_have_count(0)
    page.keyboard.down("Shift")
    expect(data).to_have_attribute("data-reference-hover", "incoming")
    expect(path).to_have_attribute("d", arrow_path)
    page.screenshot(path=str(fixture.root / "incoming.png"))
    page.keyboard.up("Shift")
    expect(marks).to_have_count(0)
    page.keyboard.down("Shift")
    expect(data).to_have_attribute("data-reference-hover", "incoming")
    page.mouse.move(1400, 90)
    expect(marks).to_have_count(0)
    page.keyboard.up("Shift")
    c.hover()
    expect(marks).to_have_count(0)
    expect(c).to_have_class("relation-map-node selected")
    expect(graph.locator("[data-map-details]")).to_contain_text("UnrelatedC")
    fixture.checked("The same arrow highlights the declared direction, respects Shift, and preserves Enter selection and inheritance")

    tip = graph.get_by_role("tooltip")
    viewport = graph.locator("[data-map-viewport]").bounding_box()
    x, y = viewport["x"] + viewport["width"] / 2, viewport["y"] + viewport["height"] - 14
    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.move(x - 80, y, steps=5)
    page.mouse.up()
    assert b.bounding_box()["x"] < viewport["x"]
    expect(data).to_have_count(1)
    a.hover()
    expect(tip).to_have_text("직접 참조: TargetB")
    expect(marks).to_have_count(0)
    graph.get_by_role("button", name="맞춤", exact=True).click()

    query = graph.get_by_role("textbox", name="관계 맵 검색")
    query.fill("SourceA")
    expect(b).to_have_count(0)
    expect(data).to_have_count(0)
    a.hover()
    expect(tip).to_have_text("직접 참조: TargetB")
    page.keyboard.down("Shift")
    expect(tip).to_have_count(0)
    page.keyboard.up("Shift")
    expect(tip).to_have_text("직접 참조: TargetB")
    page.mouse.move(1400, 90)
    expect(tip).to_have_count(0)
    graph.get_by_role("button", name="전체 보기", exact=True).click()
    graph.locator('[data-map-role="data"]').uncheck()
    a.hover()
    expect(marks).to_have_count(0)
    expect(tip).to_have_count(0)
    graph.locator('[data-map-role="data"]').check()
    b.hover()
    page.keyboard.down("Shift")
    expect(data).to_have_attribute("data-reference-hover", "incoming")
    fixture.checked("Clipped and filtered targets use a tooltip; leaving the node clears it and the role filter remains authoritative")

    page.get_by_role("button", name="Confectory 홈으로").press("Enter")
    expect(page.locator(".home-grid")).to_be_visible()
    expect(marks).to_have_count(0)
    page.keyboard.up("Shift")
    page.locator(".project-card").filter(
        has=page.get_by_role("heading", name=SECOND, exact=True)
    ).locator("[data-enter]").click()
    expect(page.locator("#title")).to_contain_text(SECOND)
    graph = open_map(page)
    expect(graph.locator("[data-reference-hover]")).to_have_count(0)
    node(graph, "TargetB").hover()
    page.keyboard.down("Shift")
    expect(graph.locator("[data-reference-hover]")).to_have_count(0)
    node(graph, "UnrelatedC").hover()
    expect(edge(graph, "값 참조")).to_have_attribute("data-reference-hover", "incoming")
    page.keyboard.up("Shift")
    assert not any(row["endpoint"] in {"select", "readReferenceDefinition"} for row in fixture.requests)
    fixture.original()
    fixture.checked("The new project uses its own connections; hovering sends no selection or definition request and preserves the source bytes")


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
