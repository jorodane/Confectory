"""Linux editor: compare a real Ctrl+Y drag with an independent known raster."""
import base64
import hashlib
from io import BytesIO
import re

from PIL import Image
from playwright.sync_api import expect, sync_playwright

import v666_workspace_finder_fixture as fixture


TARGET = "Example.FrameLoop::RasterBeacon"
project = fixture.projects[0]
(project.parent / "RasterBeacon.celem").write_text(f"object {TARGET} {{}}\n")
project.write_text(project.read_text().rstrip()[:-1] + '\n  element RasterBeacon object "RasterBeacon.celem";\n}\n')
sources = {path: path.read_bytes() for manifest in fixture.projects
           for path in manifest.parent.rglob("*") if path.is_file()}


class BrowserAtScale:
    def __init__(self, browser, scale):
        self.browser = browser
        self.scale = scale

    def new_page(self, **options):
        return self.browser.new_page(**options, device_scale_factor=self.scale, reduced_motion="reduce")


def own_editor(page):
    page.locator("#title").click()
    page.locator(".context-menu").get_by_role("button", name="프로젝트 브라우저", exact=True).click()
    browser = page.locator('.window[data-key="browser"]')
    toggle = browser.locator("[data-browser-detail]")
    if toggle.get_attribute("aria-pressed") == "false":
        toggle.click()
    browser.locator('[data-tree-select="ns:Example.FrameLoop"]').click()
    browser.locator(f'[data-object="{TARGET}"]').click()
    panel = page.locator('.window[data-key="schema"]')
    expect(panel).to_be_visible()
    return panel


def set_zoom(page, percent):
    button = page.locator("[data-workspace-zoom]")
    if button.inner_text() != f"{percent}%":
        button.click()
        value = page.get_by_label("화면 배율 직접 입력")
        value.fill(str(percent))
        value.press("Enter")
        button.click()
    expect(button).to_have_text(f"{percent}%")


def colors(alternate=False):
    return [(219 - x * 17 if alternate else 23 + x * 17, 37 + y * 29, 67 + (x + y) * 9)
            for y in range(6) for x in range(8)]


def render_fixture(panel, palette):
    # Paint only the disposable editor's visual fixture. Capture, storage and preview are real.
    return panel.evaluate("""(panel, palette) => {
      panel.querySelector('[data-raster-fixture]')?.remove();
      const raster = document.createElement('div');
      raster.dataset.rasterFixture = '';
      raster.style.cssText = 'position:absolute;left:25px;top:68px;width:160px;height:120px;'
        + 'display:grid;grid-template-columns:repeat(8,20px);grid-template-rows:repeat(6,20px);z-index:5';
      for (const color of palette) {
        const cell = document.createElement('div');
        cell.style.backgroundColor = 'rgb(' + color.join(',') + ')';
        raster.append(cell);
      }
      panel.append(raster);
      return raster.getBoundingClientRect().toJSON();
    }""", palette)


def screenshot(page, clip):
    return Image.open(BytesIO(page.screenshot(clip=clip, scale="css", animations="disabled"))).convert("RGB")


def read_image(box):
    tab = box.get_by_role("button", name="Look at Yogi", exact=True)
    if tab.get_attribute("aria-expanded") != "true":
        tab.click()
    row = box.locator('#yogi-items [data-kind="image"]')
    expect(row).to_have_count(1)
    row.get_by_role("button", name="이미지 보기", exact=True).click()
    canvas = row.locator("canvas[data-yogi-image]")
    expect(canvas).to_be_visible(timeout=30000)
    png = canvas.evaluate("canvas => canvas.toDataURL().split(',')[1]")
    return canvas.get_attribute("data-yogi-image"), Image.open(BytesIO(base64.b64decode(png))).convert("RGB")


def check(browser, zoom, dpr):
    page = fixture.setup(BrowserAtScale(browser, dpr))
    try:
        panel = own_editor(page)
        set_zoom(page, zoom)
        palette = colors()
        raster = render_fixture(panel, palette)
        assert abs(raster["width"] - 160 * zoom / 100) < 0.05, raster
        assert page.evaluate("devicePixelRatio") == dpr
        left, top = int(raster["left"]) + 13, int(raster["top"]) + 11
        width, height = 103, 73
        clip = dict(x=left, y=top, width=width, height=height)
        reference = screenshot(page, clip)
        assert len(reference.getcolors(1000)) >= 20

        page.keyboard.press("Control+y")
        expect(page.locator("body")).to_have_class(re.compile(r"\byogi-capturing\b"))
        page.mouse.move(left + width, top + height)
        page.mouse.down()
        page.mouse.move(left, top, steps=12)
        assert page.locator(".yogi-selection").bounding_box() == clip
        page.mouse.up()
        box = page.get_by_role("dialog", name="YogiBox", exact=True)
        expect(box).to_be_visible(timeout=30000)
        item, image = read_image(box)
        assert image.size == (width, height)

        direct_mismatch = 0
        browser_mismatch = 0
        solid_mismatch = 0
        for y in range(height):
            row = int((top + y + 0.5 - raster["top"]) / (raster["height"] / 6))
            for x in range(width):
                col = int((left + x + 0.5 - raster["left"]) / (raster["width"] / 8))
                expected = palette[row * 8 + col]
                rendered = image.getpixel((x, y))
                composited = reference.getpixel((x, y))
                direct_mismatch += rendered != expected
                browser_mismatch += rendered != composited
                solid_mismatch += composited == expected and rendered != composited
        print(f"zoom={zoom}% DPR={dpr}: crop pixels={width * height}, swatch mismatches={direct_mismatch}, "
              f"Chromium composite mismatches={browser_mismatch}, solid pixel mismatches={solid_mismatch}", flush=True)
        assert direct_mismatch == solid_mismatch == 0
        # Chromium blends transformed layer edges. Default zoom has no such differences.
        if zoom == 100:
            assert browser_mismatch == 0

        box.get_by_role("button", name="Look at Yogi", exact=True).click()
        box.locator("#yogi-seal").click()
        package = box.locator(".yogi-package")
        expect(package).to_be_visible()
        box.get_by_role("button", name="YogiBox 닫기", exact=True).click()
        expect(box).to_have_count(0)
        render_fixture(panel, colors(alternate=True))
        assert reference.tobytes() != screenshot(page, clip).tobytes()

        page.locator("#yogi").click()
        expect(package).to_be_visible()
        package.click()
        reopened, historical = read_image(box)
        assert reopened == item and historical.tobytes() == image.tobytes()
        capture_requests = [req["input"]["image"] for req in fixture.requests
                            if req.get("endpoint") == "yogi" and req.get("input", {}).get("action") == "capture"]
        assert len(capture_requests) == 1
        assert capture_requests[0]["hash"] == hashlib.sha256(image.tobytes()).hexdigest()
        box.locator('#yogi-items [data-kind="image"]').get_by_role("button", name="제거", exact=True).click()
        expect(box.locator('#yogi-items [data-kind="image"]')).to_have_count(0)
        assert not fixture.external and not fixture.errors, (fixture.external, fixture.errors)
        assert all(path.read_bytes() == data for path, data in sources.items())
        print(f"PASS LaY drag/reopen: zoom={zoom}% DPR={dpr}, preserved item and RGB hash", flush=True)
    finally:
        page.close()


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(executable_path="/usr/bin/chromium",
        args=["--no-sandbox", "--disable-gpu", "--renderer-process-limit=2"],
        ignore_default_args=["--disable-dev-shm-usage"])
    try:
        for zoom, dpr in ((100, 1), (100, 2), (125, 1)):
            fixture.requests.clear()
            fixture.start(f"{zoom}-{dpr}")
            try:
                check(browser, zoom, dpr)
            finally:
                fixture.stop()
    finally:
        browser.close()
