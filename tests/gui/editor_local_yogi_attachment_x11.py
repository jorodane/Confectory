#!/usr/bin/env python3
"""Stage a real sealed box in the ordinary local chat composer without delivery."""
import json
from pathlib import Path
import sys
import tempfile
import time

from playwright.sync_api import expect, sync_playwright

from editor_create_lay_x11 import box_drag, drag_region, hold, move, pixels, point
from editor_home_project_display_x11 import close_project, gtk
from editor_lan_chat_x11 import ui
from editor_local_ey_x11 import OBJECT, begin, box, finish, open_subject, package_files, seed
from v821_home_recent_edits import attach, editor, home, open_project

DRAFT = "Keep this unsent Alpha draft"
DESCRIPTION = "Private EY and LaY attachment preview"
CHIP = "YogiBox 로컬 미리보기"
REMOVE = "YogiBox 첨부 제거"


def source_bytes(file):
    return file.read_bytes(), file.stat().st_mtime_ns


def gtk_workflow(package, root, projects):
    with gtk(package, root, "gtk-local-yogi-attachment") as app:
        alpha = open_subject(app, 0)
        x, y = begin(app)
        ui.click(app.window, x, y)
        finish(app, 1)
        app.click(471)
        app.wait(lambda row: row["screen"] == "project", "Return to Alpha workspace")
        crop = [x, y, 36, 10]
        expected = pixels(app, crop)
        assert begin(app) == (x, y)
        drag_region(app, crop)
        finish(app, 2)
        app.fill(473, DESCRIPTION)
        app.click(474)
        box(app, lambda row: "Sealed YogiBox" in row["texts"])
        app.click(471)
        app.wait(lambda row: row["screen"] == "project", "Return from sealed box")
        app.fill(38, DRAFT)
        file, = package_files(alpha["path"])
        exact = source_bytes(file)

        def no_attachment(row):
            return row["screen"] == "project" and 447 not in row["hits"][::5]

        box_drag(app, (x, y))  # Painted workspace, outside the composer.
        app.wait(no_attachment, "Outside drop leaves the composer alone")
        start_x, start_y = point(app, 470)
        end = point(app, 38)
        move(app.window, start_x, start_y)
        hold(True)
        try:
            move(app.window, *end)
            time.sleep(.1)
            ui.key(app.window, 0xFF1B)
        finally:
            hold(False)
        app.wait(no_attachment, "Escape cancels drag before release")
        assert source_bytes(file) == exact

        box_drag(app, point(app, 38))
        row = app.wait(lambda row: 447 in row["hits"][::5], "Local composer attachment")
        assert app.field(row, 38)["text"] == DRAFT
        app.click(447)
        preview = box(app, lambda row: "YogiBox local preview" in row["texts"])
        assert DESCRIPTION in preview["texts"] and f"EY · {OBJECT} · object" in preview["texts"]
        assert "LaY 1 · 36 × 10" in preview["texts"]
        assert not {472, 473, 474, 477, 478}.intersection(preview["hits"][::5])
        app.click(476)
        left, _, _, _ = app.bounds(471)
        app.wait(lambda row: row["screen"] == "yogi" and not row["job"], "LaY preview is drawn")
        assert pixels(app, [left, 350, crop[2], crop[3]]) == expected
        app.click(471)
        app.click(448)
        row = app.wait(no_attachment, "Remove preview from Alpha draft")
        assert app.field(row, 38)["text"] == DRAFT
        assert source_bytes(file) == exact

        box_drag(app, point(app, 38))
        app.wait(lambda row: 447 in row["hits"][::5], "Attach again before changing projects")
        close_project(app)
        row = app.wait(lambda row: row["screen"] == "home", "Home after closing Alpha")
        assert 447 not in row["hits"][::5] and row["model"]["yogi"] is None
        bravo = open_subject(app, 1)
        row = app.wait(no_attachment, "Bravo composer contains no Alpha attachment")
        assert app.field(row, 38)["text"] == "" and not package_files(bravo["path"])
        assert source_bytes(file) == exact
        close_project(app)
    assert not package_files(projects[1]["path"])
    print("PASS actual GTK outside drop, Escape, local sealed attachment preview, removal, and Home/Bravo isolation")
    return file, expected, alpha["projectId"]


def chromium_workflow(package, root, file, expected, alpha_id):
    endpoints = []

    with sync_playwright() as playwright, playwright.chromium.launch(
            executable_path="/usr/bin/chromium", args=["--no-sandbox"],
            ignore_default_args=["--disable-dev-shm-usage"]) as browser:
        with editor(package, root, "chromium-local-yogi-attachment") as address:
            page, errors = attach(browser, address)

            def record(request):
                if request.method == "POST" and request.url.endswith("/api/request"):
                    payload = request.post_data_json
                    if payload and payload.get("endpoint"):
                        endpoints.append(payload["endpoint"])

            page.on("request", record)
            open_project(page, "Alpha")
            draft = page.locator("#chat-input")
            expect(draft).to_have_value(DRAFT)
            page.locator("#yogi").click()
            sealed = page.locator(".yogi-package")
            expect(sealed).to_be_visible()
            exact = source_bytes(file)
            tray = page.locator("[data-local-yogi-preview]")
            sealed.drag_to(page.locator("#workspace"), target_position={"x": 260, "y": 130})
            expect(tray).to_be_empty()
            expect(draft).to_have_value(DRAFT)
            assert source_bytes(file) == exact

            def stage():
                sealed.drag_to(draft)
                expect(tray.get_by_role("button", name=CHIP, exact=True)).to_be_visible()
                expect(draft).to_have_value(DRAFT)
                assert source_bytes(file) == exact

            stage()
            tray.get_by_role("button", name=CHIP, exact=True).click()
            preview = page.locator("[data-draft-yogi-items]")
            expect(preview).to_be_visible()
            expect(preview).to_contain_text(DESCRIPTION)
            expect(preview).to_contain_text("EY · " + OBJECT)
            expect(preview).to_contain_text("LaY · 36 × 10")
            actual = preview.locator("canvas").evaluate(
                """canvas => {
                    const bytes=canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height).data;
                    return Array.from({length:bytes.length/4}, (_,i) =>
                        (bytes[i*4]<<16)|(bytes[i*4+1]<<8)|bytes[i*4+2]);
                }""")
            assert actual == expected
            page.keyboard.press("Escape")
            expect(preview).to_have_count(0)
            tray.get_by_role("button", name=REMOVE).click()
            expect(tray).to_be_empty()
            expect(draft).to_have_value(DRAFT)
            assert source_bytes(file) == exact

            stage()
            sealed.locator("[data-close]").click()
            expect(tray.get_by_role("button", name=CHIP, exact=True)).to_be_visible()
            home(page)
            expect(tray).to_have_count(0)
            open_project(page, "Bravo")
            expect(tray).to_be_empty()
            expect(draft).to_have_value("")
            draft.evaluate("""(input, oldProject) => {
                const payload=new DataTransfer();
                payload.setData('application/x-yogibox',oldProject);
                input.dispatchEvent(new DragEvent('drop',{bubbles:true,cancelable:true,dataTransfer:payload}));
            }""", alpha_id)
            expect(tray).to_be_empty()
            expect(draft).to_have_value("")
            home(page)
            open_project(page, "Alpha")
            expect(tray).to_be_empty()
            expect(draft).to_have_value(DRAFT)
            # The existing box show/restore path may save the same bytes on reopening A.
            # The drop and remove operations above must also preserve its timestamp.
            assert file.read_bytes() == exact[0]
            assert not errors, errors
            page.close()

    assert endpoints.count("readLocalYogiPreview") == 4  # Two drops, each with one LaY.
    assert not {"prepareAI", "startAI", "selectHelperConversation", "localProjectChat", "localChatDevelopment"}.intersection(endpoints)
    print("PASS packaged Chromium immutable local EY, LaY pixels and description without outgoing requests")


def run(package, root):
    projects, originals = seed(package, root)
    file, expected, alpha = gtk_workflow(package, root, projects)
    chromium_workflow(package, root, file, expected, alpha)
    assert not package_files(projects[1]["path"])
    assert not (root / "profile/project-chat").exists() and not (root / "profile/helper-conversations").exists()
    assert all(path.read_bytes() == data for path, data in originals.items())


if __name__ == "__main__":
    expect.set_options(timeout=25000)
    with tempfile.TemporaryDirectory(prefix="draft-yogi-preview-") as path:
        run(Path(sys.argv[1]).resolve(), Path(path))
