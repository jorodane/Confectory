"""Project-card rename and local raster icon through the installed Linux web shell."""
import json
from pathlib import Path
import struct
import sys
import tempfile
from urllib.request import Request, urlopen
import zlib

from playwright.sync_api import expect, sync_playwright

from v821_home_recent_edits import attach, editor, home, make_project, open_project, tile


def png(red, green, blue):
    def chunk(name, payload):
        return struct.pack(">I", len(payload)) + name + payload + struct.pack(">I", zlib.crc32(name + payload))

    pixels = (b"\0" + bytes((red, green, blue)) * 16) * 16
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 16, 16, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(pixels)) + chunk(b"IEND", b""))


def selected_identity(address):
    origin, token = address.split("/#")

    def send(payload):
        request = Request(origin + "/api/request", data=json.dumps(payload).encode(), headers={
            "Content-Type": "application/json", "X-Confectory-Session": token,
        })
        with urlopen(request, timeout=15) as response:
            return json.load(response)

    mounted = send({"op": "mount"})
    assert mounted["ok"], mounted.get("error")
    try:
        state = mounted["state"]
        return state["projectId"], state["listingId"]
    finally:
        assert send({"op": "dispose", "view": mounted["view"]})["ok"]


def action(page, title, name):
    tile(page, title).locator("[data-enter]").click(button="right")
    page.locator(".context-menu").get_by_role("button", name=name, exact=True).click()


def picker(page, title):
    action(page, title, "아이콘 변경")
    dialog = page.get_by_role("dialog", name=title + " 아이콘 편집", exact=True)
    expect(dialog).to_be_visible()
    return dialog


def choose(page, dialog, files):
    with page.expect_file_chooser() as event:
        dialog.get_by_role("button", name="이미지 업로드", exact=True).click()
    event.value.set_files(files)


def workflow(package, root):
    (root / "profile").mkdir()
    names = ("Alpha", "Bravo")
    projects = {name: make_project(package, root, name)[0] for name in names}
    listing = [{"path": str(project), "title": name, "description": name + " details", "favorite": name == "Bravo"}
               for name, project in projects.items()]
    catalog = root / "profile/projects.json"
    catalog.write_text(json.dumps(listing))
    source = root / "synthetic-local.png"
    source.write_bytes(png(160, 70, 200))
    source_bytes = source.read_bytes()
    changed_title = "Alpha 새 표시 이름"

    with sync_playwright() as playwright:
        with playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"],
                                        ignore_default_args=["--disable-dev-shm-usage"]) as browser:
            with editor(package, root, "first") as url:
                page, errors = attach(browser, url)
                expect(page.locator('[data-stat="lastEdit"][data-status="none"]')).to_have_count(2)
                identities = {}
                for name in names:
                    open_project(page, name)
                    identities[name] = selected_identity(url)
                    assert all(identities[name])
                    home(page)
                assert identities["Alpha"] != identities["Bravo"]
                originals = {path: path.read_bytes() for project in projects.values()
                             for path in project.parent.rglob("*") if path.is_file()}
                untouched = catalog.read_bytes(), catalog.stat().st_mtime_ns

                action(page, "Alpha", "이름 변경")
                title = page.locator("[data-information-title]")
                expect(title).to_be_focused()
                title.fill("Cancelled input")
                page.locator("[data-information-discard]").click()
                expect(title).to_have_count(0)
                assert (catalog.read_bytes(), catalog.stat().st_mtime_ns) == untouched

                action(page, "Alpha", "이름 변경")
                expect(title).to_have_value("Alpha")
                title.fill(changed_title)
                page.locator("[data-project-information-form] [type=submit]").click()
                expect(tile(page, changed_title).locator("h2")).to_have_text(changed_title)
                listing[0]["title"] = changed_title
                assert json.loads(catalog.read_bytes()) == listing
                name_only = catalog.read_bytes(), catalog.stat().st_mtime_ns

                cancelled = picker(page, changed_title)
                choose(page, cancelled, [])
                expect(cancelled.locator(".object-icon-preview")).to_have_text("◈")
                cancelled.locator('[data-icon-choice="✦"]').click()
                page.keyboard.press("Escape")
                expect(cancelled).to_have_count(0)
                assert (catalog.read_bytes(), catalog.stat().st_mtime_ns) == name_only

                cancelled = picker(page, changed_title)
                choose(page, cancelled, str(source))
                preview = cancelled.locator(".object-icon-preview img")
                expect(preview).to_be_visible()
                captured = preview.get_attribute("src")
                assert captured.startswith("data:image/webp;base64,")
                assert preview.evaluate("async image => { await image.decode(); return image.naturalWidth; }") == 128
                assert (catalog.read_bytes(), catalog.stat().st_mtime_ns) == name_only
                cancelled.locator("[data-cancel]").click()
                assert (catalog.read_bytes(), catalog.stat().st_mtime_ns) == name_only

                applied = picker(page, changed_title)
                choose(page, applied, str(source))
                expect(applied.locator(".object-icon-preview img")).to_have_attribute("src", captured)
                applied.get_by_role("button", name="적용", exact=True).click()
                expect(tile(page, changed_title).locator(".project-icon img")).to_have_attribute("src", captured)
                expect(tile(page, "Bravo").locator(".project-icon")).to_have_text("◈")
                listing[0]["icon"] = captured
                assert json.loads(catalog.read_bytes()) == listing
                assert source.read_bytes() == source_bytes
                assert all(path.read_bytes() == before for path, before in originals.items())
                source.write_bytes(png(35, 200, 77))
                assert not errors, errors
                page.close()

            with editor(package, root, "cold") as url:
                page, errors = attach(browser, url)
                expect(tile(page, changed_title)).to_have_attribute("data-project", identities["Alpha"][1])
                expect(tile(page, changed_title).locator(".project-icon img")).to_have_attribute("src", captured)
                expect(tile(page, "Bravo")).to_have_attribute("data-project", identities["Bravo"][1])
                expect(tile(page, "Bravo").locator(".project-icon")).to_have_text("◈")
                for original_name, title in (("Alpha", changed_title), ("Bravo", "Bravo")):
                    open_project(page, title)
                    assert selected_identity(url) == identities[original_name]
                    icon = page.locator("#title .project-title-icon img")
                    if original_name == "Alpha":
                        expect(icon).to_have_attribute("src", captured)
                        assert icon.evaluate("async image => { await image.decode(); return image.naturalWidth; }") == 128
                    else:
                        expect(icon).to_have_count(0)
                    home(page)
                assert not errors, errors
                page.close()

    assert json.loads(catalog.read_bytes()) == listing
    for project in projects.values():
        for path in (project, project.with_name("Main.celem"), project.with_name("Main.csbody")):
            assert path.read_bytes() == originals[path]
    print("PASS project tile rename, local WebP, both cancellation boundaries and exact cold identities")


if __name__ == "__main__":
    expect.set_options(timeout=45000)
    bundle = Path(sys.argv[1]).resolve()
    if len(sys.argv) > 2:
        workflow(bundle, Path(sys.argv[2]).resolve())
    else:
        with tempfile.TemporaryDirectory(prefix="home-project-display-") as directory:
            workflow(bundle, Path(directory))
