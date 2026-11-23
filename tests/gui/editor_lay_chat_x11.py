#!/usr/bin/env python3
"""Two actual GTK clients send previously sealed LaY via LAN or the isolated relay.

Run on an isolated Xorg display with the fixture image from editor_relay_chat_x11.
The existing project and YogiBox owners install deterministic synthetic packages
in a separate process. All attachment and viewing controls are actual UI.
"""
import ctypes as c
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from editor_create_lay_x11 import box_drag, point
from editor_lan_chat_x11 import GUEST, HOST, P, U, bind, display, dotnet, internal_network, peer, repo, x11
from editor_relay_chat_x11 import fixture_build, identity, issue as relay_issue, reservations, review as relay_review


def seed_build(checkout):
    home = checkout / "examples/editor-home"
    manifest = home / "project.cpack"
    original = manifest.read_text()
    manifest.write_text(original.replace("entry Confectory.EditorHome::Main;", "entry Confectory.EditorHome::VerifyShell;"))
    try:
        (home / "VerifyShell.csbody").write_text((repo / "tests/fixtures/isolated-relay-editor/SeedGtkLay.csbody").read_text())
        cli = repo / "src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll"
        build = subprocess.run([dotnet, cli, "build", manifest, "linux"], text=True, capture_output=True, timeout=240)
        assert build.returncode == 0, build.stderr[-3000:] + build.stdout[-3000:]
        return json.loads(build.stdout)["run"]
    finally:
        manifest.write_text(original)


def seed(editor, command, role):
    with (editor.profile / "seed.log").open("w") as log:
        result = subprocess.run(editor.command(command, CONFECTORY_TEST_GTK_LAY=role),
                                stdout=log, stderr=subprocess.STDOUT, timeout=60)
    assert result.returncode == 0, "Could not prepare synthetic YogiBox; see seed.log"


def open_project(editor, title, draft=None):
    home = editor.wait(lambda row: row["screen"] == "home" and len(row["model"]["cards"]) > 0, "Fixture project listing")
    index = next(i for i, item in enumerate(home["model"]["cards"]) if item["title"] == title)
    editor.click(100 + 3 * index)
    state = editor.wait(lambda row: row["screen"] == "project" and row["model"]["selected"]["title"] == title,
                        "Open the matching local project card")
    if draft is not None:
        editor.fill(38, draft)
    return state["model"]["selected"]


def pixels(editor, tone):
    bounds = editor.wait(lambda row: row["lanImageBounds"] and row["lanImageBounds"][2:] == [24,18],
                         "Native image painted at 1:1")["lanImageBounds"]
    x, y, w, h = bounds
    get_image = bind(x11, "XGetImage", P, P, U, c.c_int, c.c_int, c.c_uint, c.c_uint, U, c.c_int)
    get_pixel = bind(x11, "XGetPixel", U, P, c.c_int, c.c_int)
    destroy = bind(x11, "XDestroyImage", c.c_int, P)
    capture = get_image(display, editor.window, x, y, w, h, U(-1).value, 2)
    assert capture, "Native X11 pixels unavailable"
    try:
        for dy in range(h):
            for dx in range(w):
                expected = (tone << 16) | (dx * 7 << 8) | (dy * 11)
                assert get_pixel(capture, dx, dy) & 0xffffff == expected, "Painted LaY differs from sealed pixels"
    finally:
        destroy(capture)


def exercise(host, guest, invite, review):
    owner = open_project(host, "GTK LaY Host", "Private host draft")
    local = open_project(guest, "GTK LaY Guest", "Private guest draft")
    files = {file: file.read_bytes() for editor in (host, guest)
             for file in (editor.profile.parent / "projects").rglob("package-*.json")}
    assert len(files) == 3
    originals = {Path(row["path"]): Path(row["path"]).read_bytes() for row in (owner, local)}

    invite()
    review(owner)
    guest.click(458)
    guest.wait(lambda row: guest.field(row,461).get("text") == "No messages yet.", "Fresh attachment inbox")
    host.click(464)
    host.wait(lambda row: row["lanStatus"].startswith("Sealed YogiBox attached"), "Host prepared YogiBox")
    assert not (host.profile / "project-chat").exists(), "Preparing alone wrote public history"
    host.click(464)
    host.wait(lambda row: row["lanStatus"].startswith("Attachment removed"), "Detach unsent YogiBox")
    assert not (host.profile / "project-chat").exists(), "Detaching wrote public history"

    host.click(464)
    host.wait(lambda row: row["lanStatus"].startswith("Sealed YogiBox attached"), "Host prepared existing YogiBox again")
    host.send("Host frozen LaY")
    guest.wait(lambda row: "Host frozen LaY  [YogiBox 1]" in guest.field(row,461).get("text",""), "Attached to the host message")
    guest.click(465)
    guest.wait(lambda row: "GTK LaY Host frozen description" in row["texts"], "Original description")
    pixels(guest,91)
    assert any("EY unavailable" in text for text in guest.state()["texts"])
    guest.click(469)
    guest.wait(lambda row: any("Image 2 / 2" in text for text in row["texts"]), "Second capture selected")
    pixels(guest,110)
    guest.click(468)

    guest.click(464)
    guest.wait(lambda row: row["lanStatus"].startswith("Sealed YogiBox attached"), "Guest prepared YogiBox")
    guest.send("Guest frozen LaY")
    host.wait(lambda row: "Guest frozen LaY  [YogiBox 2]" in host.field(row,461).get("text",""), "Attached to the guest message")
    host.click(467)
    host.wait(lambda row: "View YogiBox 2" in row["texts"], "Select the matching guest message")
    host.click(465)
    host.wait(lambda row: "GTK LaY Guest frozen description" in row["texts"], "Guest description")
    pixels(host,153)
    journal, = (host.profile / "project-chat").glob("*.json")
    committed = journal.read_bytes()
    assert [row["text"] for row in json.loads(committed)["messages"]] == ["Host frozen LaY","Guest frozen LaY"]
    assert not (guest.profile / "project-chat").exists()

    # Ending the host session also clears an open viewer on the guest.
    guest.click(465)
    guest.wait(lambda row: row["lanImageBounds"], "Guest viewer open at revocation")
    host.click(451)
    guest.wait(lambda row: row["lanMode"]=="closed" and not row["lanImageBounds"], "Viewer retired with the room")
    guest.click(451)
    guest.wait(lambda row: guest.field(row,38).get("text") == "Private guest draft", "Guest draft after leaving the room")
    guest.click(33)
    guest.click(15)
    guest.wait(lambda row: row["screen"] == "home", "Return to local Home")
    open_project(guest,"GTK Mixed Guest")
    invite()
    review(owner)
    guest.click(458)
    guest.wait(lambda row: guest.field(row,461).get("text") == "No messages yet.", "New session has no old attachments")
    box_drag(guest, point(guest,459))
    guest.wait(lambda row: "with EY cannot be shared" in row["lanStatus"], "Mixed guest package refused on drop")
    assert journal.read_bytes() == committed
    host.click(464)
    host.wait(lambda row: row["lanStatus"].startswith("Sealed YogiBox attached"), "Prepare an attachment before closing")
    host.close()
    guest.wait(lambda row: row["lanMode"]=="closed", "Host shutdown disconnected the guest")
    guest.close()
    assert journal.read_bytes() == committed
    assert not (guest.profile / "project-chat").exists()
    assert not (host.profile / "helper-conversations").exists() and not (guest.profile / "helper-conversations").exists()
    assert all(file.read_bytes() == data for file,data in (files | originals).items())
    print("PASS both directions, native exact pixels and descriptions, detach/close without sending, EY refusal, revoke and empty re-entry", flush=True)


def lan(root, image, checkout, command, seed_command):
    with internal_network(image) as (network, image_id), \
         peer(root,network,image_id,HOST,checkout) as host, peer(root,network,image_id,GUEST,checkout) as guest:
        seed(host,seed_command,"host"); seed(guest,seed_command,"guest")
        host.launch(command); guest.launch(command)
        def invite():
            host.issue()
            host.copy_invite()
        def review(owner):
            guest.review(host,next(iter(host.listeners()))[1],owner["title"])
        exercise(host,guest,invite,review)


def relayed(root, image, checkout, command, seed_command):
    left, right, left_relay, right_relay = "192.0.2.27","198.51.100.27","192.0.2.26","198.51.100.26"
    relay_key, relay_pin, _ = identity("relay.confectory.invalid")
    host_key, host_pin, fingerprint = identity("chat-host.confectory.invalid")
    with internal_network(image,"192.0.2.24/29") as (a,image_id), internal_network(image,"198.51.100.24/29") as (b,_), \
         peer(root,a,image_id,left,checkout) as host, peer(root,b,image_id,right,checkout) as guest, \
         peer(root,a,image_id,left_relay,checkout,other_network=(b,right_relay)) as relay, reservations(relay,command,relay_key) as reserve:
        seed(host,seed_command,"host"); seed(guest,seed_command,"guest")
        pairs = [reserve(240) for _ in range(2)]
        host.launch(command,dict(role="host",identity=host_key,relayPin=relay_pin,address=left_relay,reservations=[p[0] for p in pairs]))
        guest.launch(command,dict(role="guest",identity=host_pin,relayPin=relay_pin,address=right_relay,reservations=[p[1] for p in pairs]))
        pending = iter(pairs)
        def review(owner):
            _, reservation = next(pending)
            relay_review(guest,f"{right_relay}:{reservation['port']}",fingerprint,owner)
        exercise(host,guest,lambda:relay_issue(host),review)


if __name__ == "__main__":
    root = Path(tempfile.mkdtemp(prefix="cf-native-lay-test-"))
    print("Native LaY fixture logs at",root,flush=True)
    checkout, command = fixture_build(root)
    {"lan":lan,"relay":relayed}[sys.argv[2]](root,sys.argv[1],checkout,command,seed_build(checkout))
