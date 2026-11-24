#!/usr/bin/env python3
"""Installed Linux host-only send from a staged mixed YogiBox in GTK and Chromium."""
import base64
import json
import os
from pathlib import Path
import re
import sys
import tempfile

from playwright.sync_api import expect, sync_playwright

from editor_create_lay_x11 import box_drag, drag_region, pixels, point
from editor_home_project_display_x11 import close_project, gtk
from editor_lan_chat_x11 import ui
from editor_local_ey_x11 import box, finish, package_files
from v821_home_recent_edits import attach, editor, make_project, open_project

TITLE = "PublicYogi"
DESCRIPTION = "Synthetic attachment description"
NATIVE_BODY = "Synthetic local host GTK submission"
WEB_BODY = "Synthetic local host Chromium submission"
LIVE_BODY = "New mixed box during the guest session"
AFTER_REJOIN = "New mixed box after a different invitation"


def source_capture(app, identity):
    def begin():
        ui.key(app.window, "y", (0xFFE3,))
        row = app.wait(lambda row: row["laySelecting"] and row["eyBounds"], "Capture in the owned object")
        x, y, width, height = row["eyBounds"][:4]
        return x + min(12, width // 2), y + height // 2

    app.click(55)
    row = app.wait(lambda row: row["model"]["workspace"] and row["model"]["workspace"]["unit"], "Owned workspace")
    while row["model"]["workspace"]["selected"] != identity:
        workspace = row["model"]["workspace"]
        ids = [unit["id"] for unit in workspace["units"]]
        current = workspace["selected"]
        app.click(57 if ids.index(current) < ids.index(identity) else 56)
        row = app.wait(lambda row: row["model"]["workspace"]["selected"] != current, "Select the capture object")
    x, y = begin()
    ui.click(app.window, x, y)
    finish(app, 1)
    app.click(471)
    app.wait(lambda row: row["screen"] == "project", "Return to the workspace")
    crop = [x, y, 36, 10]
    expected = pixels(app, crop)
    assert begin() == (x, y)
    drag_region(app, crop)
    finish(app, 2)
    app.fill(473, DESCRIPTION)
    app.click(474)
    box(app, lambda row: "Sealed YogiBox" in row["texts"])
    app.click(471)
    return expected


def tcp_listeners(pid):
    proc = Path("/proc") / str(pid)
    sockets = set()
    for fd in (proc / "fd").iterdir():
        try:
            link = os.readlink(fd)
        except FileNotFoundError:  # The owned process may close a descriptor during enumeration.
            continue
        if link.startswith("socket:["):
            sockets.add(link[len("socket:["):-1])
    for name in ("tcp", "tcp6"):
        rows = (proc / "net" / name).read_text().splitlines()[1:]
        if rows and any(cells[3] == "0A" and cells[9] in sockets for cells in map(str.split, rows)):
            return True
    return False


def native(package, root):
    (root / "profile").mkdir()
    (root / "projects").mkdir()
    with gtk(package, root, "create", with_listings=False) as app:
        project = app.create(TITLE, "")
        close_project(app)
    manifest = Path(project["path"])
    source = manifest.read_text()
    namespace = re.search(r"^project\s+(\S+)", source, re.M)[1]
    identity = namespace + "::YogiCaptureFixture"
    (manifest.parent / "YogiCaptureFixture.celem").write_text(
        f'object {identity} {{ description "Synthetic EY"; }}\n')
    manifest.write_text(source.rstrip()[:-1] + 'element YogiCaptureFixture object "YogiCaptureFixture.celem";\n}\n')
    sources = {path: path.read_bytes() for path in manifest.parent.iterdir() if path.is_file()}
    journal = root / "profile/project-chat" / (project["projectId"] + ".json")
    with gtk(package, root, "send-gtk") as app:
        app.click(100)
        app.wait(lambda row: row["screen"] == "project", "Open the original creator project")
        assert not tcp_listeners(app.child.pid)
        expected = source_capture(app, identity)
        sealed, = package_files(manifest)
        exact = sealed.read_bytes()
        app.fill(38, NATIVE_BODY)
        box_drag(app, point(app, 38))
        app.wait(lambda row: 440 in row["hits"][::5], "Explicit public Send is available to the creator")
        assert not journal.exists()
        # Only this disposable profile is touched. Exercise the host's real storage failure.
        journal.parent.mkdir()
        journal.write_text("{}")
        app.click(440)
        state = app.wait(lambda row: "Public send could not be confirmed" in row["message"], "Journal rejects the send")
        assert app.field(state, 38)["text"] == NATIVE_BODY and 447 in state["hits"][::5]
        assert journal.read_text() == "{}" and sealed.read_bytes() == exact
        journal.unlink()
        app.click(440)
        state = app.wait(lambda row: "Public message and YogiBox saved" in row["message"], "Commit retry")
        assert app.field(state, 38)["text"] == "" and 447 not in state["hits"][::5]
        assert sealed.read_bytes() == exact and not tcp_listeners(app.child.pid)
        close_project(app)

    with gtk(package, root, "read-gtk") as app:
        app.click(100)
        app.wait(lambda row: row["screen"] == "project", "Cold reopen the original project")
        app.click(55)
        app.wait(lambda row: row["model"]["workspace"] and row["model"]["workspace"]["unit"], "Owned workspace available")
        app.click(450)
        app.click(479)
        app.wait(lambda row: NATIVE_BODY in app.field(row, 461).get("text", ""), "Read saved public history")
        app.click(465)
        viewed = app.wait(lambda row: DESCRIPTION in row["texts"], "Read the saved mixed attachment")
        assert any("EY · " + identity in line for line in viewed["texts"])
        left, _, _, _ = app.bounds(468)
        assert pixels(app, [left, 294, 36, 10]) == expected
        assert not tcp_listeners(app.child.pid)
    return identity, journal, sealed, exact, sources


def chromium(package, root, identity, journal, sealed, exact):
    attempts = []
    with (sync_playwright() as playwright,
          playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"],
                                     ignore_default_args=["--disable-dev-shm-usage"]) as browser,
          editor(package, root, "send-chromium") as address):
        page, errors = attach(browser, address)
        endpoints = []

        def transport(route):
            request = route.request.post_data_json
            endpoint = request.get("endpoint")
            endpoints.append(endpoint)
            if endpoint == "sendLocalYogiPreview":
                response = route.fetch()
                if (response.json().get("result") or {}).get("status") == "committed":
                    attempts.append(request["input"])
                    if len(attempts) == 1:
                        route.abort()
                        return
                route.fulfill(response=response)
                return
            route.continue_()

        page.route("**/api/request", transport)
        open_project(page, TITLE)
        draft = page.locator("#chat-input")
        expect(draft).to_have_value("")
        page.locator("#yogi").click()
        sealed_icon = page.locator(".yogi-package")
        expect(sealed_icon).to_be_visible()
        draft.fill(WEB_BODY)
        sealed_icon.drag_to(draft)
        send = page.locator("[data-local-yogi-preview]").get_by_role("button", name="공용으로 보내기", exact=True)
        expect(send).to_be_visible()
        assert len(json.loads(journal.read_text())["messages"]) == 1
        send.click()
        expect(page.get_by_text("공용 전송을 확인하지 못했어요.", exact=False)).to_be_visible()
        expect(draft).to_have_value(WEB_BODY)
        expect(send).to_be_visible()
        send.click()
        expect(draft).to_have_value("")
        expect(send).to_have_count(0)
        row = page.locator("[data-public-chat-rows] .message").filter(has_text=WEB_BODY)
        row.get_by_role("button", name="YogiBox 보기").click()
        viewer = page.locator("[data-public-yogi]")
        expect(viewer).to_contain_text(DESCRIPTION)
        expect(viewer.get_by_role("button", name=identity, exact=True)).to_be_visible()
        viewer.get_by_role("button", name="이미지 보기").click()
        expect(viewer.locator("canvas")).to_be_visible()
        assert len(attempts) == 2 and attempts[0] == attempts[1]
        assert not errors and not {"startAI", "prepareAI", "selectHelperConversation", "localProjectChat", "localChatDevelopment"}.intersection(endpoints)
        assert sealed.read_bytes() == exact
        page.close()



def loopback(package, root, identity, journal, expected):
    guest_root = root / "guest"
    (guest_root / "profile").mkdir(parents=True)
    manifest, _ = make_project(package, guest_root, "LocalGuest")
    (guest_root / "profile/projects.json").write_text(json.dumps(
        [{"path": str(manifest), "title": "LocalGuest", "description": ""}]))

    with (sync_playwright() as playwright,
          playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"],
                                     ignore_default_args=["--disable-dev-shm-usage"]) as browser,
          editor(package, root, "loopback-host", loopback=True) as host_address,
          editor(package, guest_root, "loopback-guest", loopback=True) as guest_address):
        host, host_errors = attach(browser, host_address)
        guest, guest_errors = attach(browser, guest_address)
        open_project(host, TITLE)
        open_project(guest, "LocalGuest")

        def menu(page, label):
            page.locator("#title").click()
            page.locator(".context-menu").get_by_role("button", name=label, exact=True).click()
            return page.get_by_role("dialog", name=label, exact=True)

        def issue():
            panel = menu(host, "로컬 채팅 초대")
            panel.get_by_role("button", name="일회용 초대 발급", exact=True).click()
            expect(panel.get_by_role("button", name="초대 텍스트 선택")).to_be_visible()
            card = panel.get_by_label("일회용 초대").input_value()
            assert isinstance(json.loads(card)["port"], int)
            return panel, card

        def join(panel, card):
            panel.get_by_label("일회용 초대").fill(card)
            panel.get_by_label("참가 이름").fill("Synthetic local guest")
            panel.get_by_role("button", name="참가", exact=True).click()

        def join_empty(panel, card):
            join(panel, card)
            expect(panel.locator("[data-local-chat-status]")).to_have_text("새 메시지가 없습니다.")
            expect(panel.locator("[data-local-chat-messages]")).to_be_empty()

        def send_from_draft(text):
            sealed = host.locator(".yogi-package")
            if not sealed.is_visible():
                host.locator("#yogi").click()
            expect(sealed).to_be_visible()
            draft = host.locator("#chat-input")
            draft.fill(text)
            sealed.drag_to(draft)
            send = host.locator("[data-local-yogi-preview]").get_by_role("button", name="공용으로 보내기", exact=True)
            expect(send).to_be_visible()
            assert all(row["text"] != text for row in json.loads(journal.read_text())["messages"])
            send.click()
            expect(draft).to_have_value("")

        host_panel, first = issue()
        guest_panel = menu(guest, "로컬 초대 참가")
        join_empty(guest_panel, first)
        send_from_draft(LIVE_BODY)
        messages = guest_panel.locator("[data-local-chat-messages]")
        expect(messages).to_contain_text(LIVE_BODY)
        messages.get_by_role("button", name="YogiBox 보기", exact=True).click()
        viewer = guest_panel.get_by_role("region", name="YogiBox 보기", exact=True)
        expect(viewer).to_contain_text(DESCRIPTION)
        expect(viewer).to_contain_text("현재 열 수 없는 EY")
        expect(viewer).not_to_contain_text(identity)
        viewer.get_by_role("button", name="이미지 보기", exact=True).click()
        canvas = viewer.locator("canvas")
        expect(canvas).to_be_visible()
        rgb = canvas.evaluate("""canvas => Array.from(
            canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height).data)
            .filter((_,i)=>i%4!==3)""")
        assert bytes(rgb) == expected

        guest_panel.get_by_role("button", name="닫기", exact=True).click()
        guest_panel = menu(guest, "로컬 초대 참가")
        join(guest_panel, first)
        expect(guest_panel.locator("[data-local-chat-status]")).to_contain_text("연결할 수 없습니다")
        host_panel.get_by_role("button", name="닫기", exact=True).click()
        host_panel, second = issue()
        join_empty(guest_panel, second)
        send_from_draft(AFTER_REJOIN)
        expect(messages).to_contain_text(AFTER_REJOIN)
        expect(messages).not_to_contain_text(LIVE_BODY)
        expect(messages.get_by_role("button", name="YogiBox 보기", exact=True)).to_have_count(1)
        host_panel.get_by_role("button", name="닫기", exact=True).click()
        expect(messages).to_be_empty()
        assert not host_errors and not guest_errors, (host_errors, guest_errors)
        assert not (guest_root / "profile/project-chat").exists()
        assert not (guest_root / "profile/helper-conversations").exists()
        host.close()
        guest.close()


if __name__ == "__main__":
    expect.set_options(timeout=25000)
    package = Path(sys.argv[1]).resolve()
    with tempfile.TemporaryDirectory(prefix="send-draft-yogi-") as directory:
        root = Path(directory)
        identity, journal, sealed, exact, sources = native(package, root)
        print("PASS GTK explicit send, real storage failure and cold readback", flush=True)
        chromium(package, root, identity, journal, sealed, exact)
        print("PASS Chromium local send acknowledgement loss and single committed retry", flush=True)
        original = json.loads(exact)["package"]
        loopback(package, root, identity, journal, base64.b64decode(original["items"][1]["capture"]["pixels"]))
        record = json.loads(journal.read_text())
        assert record["version"] == 2
        assert [row["text"] for row in record["messages"]] == [NATIVE_BODY, WEB_BODY, LIVE_BODY, AFTER_REJOIN]
        for row in record["messages"]:
            snapshot = row["attachment"]["package"]
            assert snapshot["text"] == DESCRIPTION
            assert snapshot["items"][0]["id"] == identity and snapshot["items"][0]["metadata"] == {}
            assert snapshot["items"][1] == original["items"][1]
        assert not (root / "profile/helper-conversations").exists()
        assert all(path.read_bytes() == content for path, content in sources.items())
    print("PASS local host and protected loopback delivery, durable mixed attachment, retries and empty rejoin")
