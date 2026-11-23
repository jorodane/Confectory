#!/usr/bin/env python3
"""Capture, seal and share LaY through the real GTK editor on a private Xorg display.

Use the local fixture image described by editor_relay_chat_x11.py. LAN uses the
ordinary Linux build report. Relay adds only the existing stdin transport setup.
Every private YogiBox is made in the GTK UI of a fresh project.
"""
import base64
import ctypes as c
import json
import os
import select
import subprocess
from pathlib import Path
import sys
import tempfile
import time

from editor_lan_chat_x11 import GUEST, HOST, P, U, bind, display, eventually, internal_network, native_windows, peer, ui, x11
from editor_relay_chat_x11 import fixture_build, identity, issue as relay_issue, reservations, review as relay_review


def pixels(editor, bounds):
    x, y, width, height = bounds
    get_image = bind(x11, "XGetImage", P, P, U, c.c_int, c.c_int, c.c_uint, c.c_uint, U, c.c_int)
    get_pixel = bind(x11, "XGetPixel", U, P, c.c_int, c.c_int)
    destroy = bind(x11, "XDestroyImage", c.c_int, P)
    image = get_image(display, editor.window, x, y, width, height, U(-1).value, 2)
    assert image, "Cannot inspect the synthetic editor surface"
    try:
        return [get_pixel(image, dx, dy) & 0xffffff for dy in range(height) for dx in range(width)]
    finally:
        destroy(image)


def packages(editor):
    return list((editor.profile.parent / "projects").rglob("package-*.json"))


def root_point(window, x, y):
    rx, ry, child = c.c_int(), c.c_int(), U()
    assert ui.translate(display, window, ui.root, x, y, c.byref(rx), c.byref(ry), c.byref(child))
    return rx.value, ry.value


def move(window, x, y):
    ui.motion(display, -1, *root_point(window, x, y), 0)
    ui.flush(display)


def hold(down):
    ui.button(display, 1, int(down), 0)
    ui.flush(display)


def drag_region(editor, crop):
    x, y, width, height = crop
    ui.raise_window(display, editor.window)
    move(editor.window, x, y)
    hold(True)
    time.sleep(.04)
    move(editor.window, x + width, y + height)
    time.sleep(.04)
    hold(False)


def point(editor, control):
    row = editor.wait(lambda row: control in row["hits"][::5], f"Visible control {control}")
    i = 5 * row["hits"][::5].index(control)
    x, y, w, h = row["hits"][i+1:i+5]
    return x+w//2, y+h//2


def box_drag(editor, target):
    x, y = point(editor, 470)
    dest_x, dest_y = target
    drag_region(editor, [x, y, dest_x-x, dest_y-y])


def double_box(editor):
    x, y = point(editor, 470)
    ui.raise_window(display, editor.window)
    move(editor.window, x, y)
    for _ in range(2):
        hold(True)
        time.sleep(.035)
        hold(False)
        time.sleep(.075)
    editor.wait(lambda row: row["screen"] == "yogi" and "Sealed YogiBox" in row["texts"], "Double-click opened sealed YogiBox")


def keyboard_attach(editor):
    for _ in range(20):
        focus = editor.state()["focus"]
        if focus == 464:
            ui.key(editor.window, 0xFF0D)
            return
        if editor.field(editor.state(), focus).get("visible"):
            editor.key(focus, 0xFF09)
        else:
            ui.key(editor.window, 0xFF09)
        editor.wait(lambda row: row["focus"] != focus, "Tab navigates public chat")
    raise AssertionError("Attachment button unavailable through keyboard navigation")


EXTERNAL_DROP = """
import gi
import sys
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk
window = Gtk.Window(title="GTK External Drop Fixture")
window.move(4, 4)
window.set_default_size(132, 66)
button = Gtk.Button(label="Drag fixture")
window.add(button)
button.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [Gtk.TargetEntry.new(sys.argv[1], 0, 0)], Gdk.DragAction.COPY)
button.connect("drag-begin", lambda *_: print("drag-begin", flush=True))
def data(widget, context, selection, info, time):
    selection.set(selection.get_target(), 8, sys.argv[2].encode())
button.connect("drag-data-get", data)
window.show_all()
Gtk.main()
"""


def reject_external_drop(editor):
    cache = editor.profile / "external-drag-cache"
    cache.mkdir(exist_ok=True)
    environment = dict(os.environ, XDG_CACHE_HOME=str(cache))
    for mime, marker in (("UTF8_STRING", "Unauthenticated text https://invalid.example/"),
                         ("text/uri-list", "file:///tmp/confectory-no-file.txt\r\n")):
        with subprocess.Popen(["/usr/bin/python3", "-u", "-c", EXTERNAL_DROP, mime, marker],
                              stdout=subprocess.PIPE, text=True, env=environment) as source:
            try:
                window = eventually(lambda: next(iter(native_windows(b"GTK External Drop Fixture")), None), "Actual GTK drag source")
                move(window, 45, 45)
                hold(True)
                time.sleep(.1)
                move(window, 96, 53)
                assert select.select([source.stdout], [], [], 5)[0] and source.stdout.readline().strip() == "drag-begin"
                move(editor.window, *point(editor, 459))
                time.sleep(.25)
                hold(False)
                time.sleep(.25)
                assert editor.field(editor.state(),459).get("text") == "Keep this public draft"
                assert "attached to this draft" not in editor.state()["lanStatus"]
            finally:
                hold(False)
                source.terminate()
                source.wait(timeout=5)


def start_drag(editor, crop):
    # Leave the GTK text widget through the actual painted workspace before
    # pressing the application shortcut. Its own Ctrl+Y remains widget-owned.
    left, top, _, _ = editor.state()["layBounds"]
    ui.click(editor.window, left + 1, top + 1)
    ui.key(editor.window, "y", (0xFFE3,))
    editor.wait(lambda row: row["laySelecting"], "Ctrl+Y activated the LaY selector")
    drag_region(editor, crop)


def make_box(editor, title, description, cancel_and_remove=False):
    owner = editor.create(title, title + " private draft")
    editor.click(55)
    selected = editor.wait(lambda row: row["model"]["workspace"] and row["model"]["workspace"]["unit"],
                           "Selected the existing editor workspace")
    x, y, _, _ = selected["layBounds"]
    crop = [x + 10, y + 11, 112, 31]
    if cancel_and_remove:
        editor.click(470)
        editor.wait(lambda row: row["screen"] == "yogi" and "No captured regions" in row["texts"], "Open empty local box")
        assert not packages(editor)
        ui.key(editor.window, 0xFF1B)
        editor.wait(lambda row: row["screen"] == "project", "Escape returned to the selected workspace")

        ui.key(editor.window, "y", (0xFFE3,))
        editor.wait(lambda row: row["laySelecting"], "Keyboard selection activated")
        ui.key(editor.window, 0xFF1B)
        editor.wait(lambda row: not row["laySelecting"] and row["screen"] == "project", "Escape canceled selection")
        assert not packages(editor)
        draft = title + " private draft after cancel"
        editor.fill(38, draft)
        # A drag beginning outside the workspace must neither capture nor click the underlying shell.
        start_drag(editor, [22, y + 115, 31, 18])
        editor.wait(lambda row: not row["laySelecting"] and row["screen"] == "project" and "inside the selected workspace" in row["message"],
                    "Outside workspace selection refused")
        assert not packages(editor)
    else:
        draft = title + " private draft"

    expected = pixels(editor, crop)
    assert len(set(expected)) > 2, "Use actual painted text and controls for the pixel check"
    start_drag(editor, crop)
    editor.wait(lambda row: row["screen"] == "yogi" and 475 in row["hits"][::5], "Dragged image added to the actual YogiBox")
    if cancel_and_remove:
        editor.fill(473, description)
        editor.click(477)
        editor.wait(lambda row: "No captured regions" in row["texts"] and editor.field(row,473).get("text") == description,
                    "Only the capture was removed; description draft persisted")
        editor.click(472)
        editor.wait(lambda row: row["laySelecting"] and row["screen"] == "project", "Use box control to select again")
        expected = pixels(editor, crop)
        drag_region(editor, crop)
        editor.wait(lambda row: row["screen"] == "yogi" and 475 in row["hits"][::5] and editor.field(row,473).get("text") == description,
                    "Replacement capture and existing description draft")
    else:
        editor.fill(473, description)
    editor.click(474)
    editor.wait(lambda row: "Sealed YogiBox" in row["texts"] and description in row["texts"], "Sealed the frozen capture and description")
    package, = packages(editor)
    stored = package.read_bytes()
    document = json.loads(stored)
    capture, = document["package"]["items"]
    actual = base64.b64decode(capture["capture"]["pixels"])
    expected_rgb = b"".join(pixel.to_bytes(3, "big") for pixel in expected)
    assert actual == expected_rgb, "Sealed pixels differ from the actual selected workspace"
    assert document["package"]["text"] == description and document["package"]["sealed"]
    assert capture["capture"]["pixels"].encode() not in editor.log.read_bytes(), "Private pixels reached native diagnostics"
    editor.click(471)
    editor.wait(lambda row: row["screen"] == "project" and any("▣ YogiBox" in text for text in row["texts"]),
                "Small sealed box in the same workspace")
    editor.wait(lambda row: editor.field(row,38).get("text") == draft, "Private Helper draft retained")
    return owner, crop, expected, package, stored


def view_capture(editor, description, expected, crop, newer=False):
    if newer:
        editor.click(467)
        editor.wait(lambda row: "View YogiBox 2" in row["texts"], "Selected the later attached message")
    editor.click(465)
    bounds = editor.wait(lambda row: row["lanImageBounds"] and description in row["texts"],
                         "Opened the read-only public attachment")["lanImageBounds"]
    assert bounds[2:] == crop[2:], "Original-size preview"
    eventually(lambda: pixels(editor, bounds) == expected,
               "The receiver rendered different pixels from the selected workspace", timeout=3)


def exercise(host, guest, invite, review):
    host_box = make_box(host, "GTK Sender", "Host selected this workspace region", cancel_and_remove=True)
    guest_box = make_box(guest, "GTK Receiver", "Guest selected this workspace region")
    host.click(470)
    time.sleep(.45)
    assert host.state()["screen"] == "project", "Single click must not reopen the sealed box"
    double_box(host)
    host.click(471)
    host.wait(lambda row: row["screen"] == "project", "Back from the sealed workspace box")

    invite()
    review(host_box[0])
    guest.click(458)
    guest.wait(lambda row: guest.field(row,461).get("text") == "No messages yet.", "First admission is empty")

    host.fill(459, "Keep this public draft")
    reject_external_drop(host)
    assert not (host.profile / "project-chat").exists()
    box_drag(host, point(host,461))
    assert host.field(host.state(),459).get("text") == "Keep this public draft"
    assert "attached to this draft" not in host.state()["lanStatus"]
    assert not (host.profile / "project-chat").exists(), "Drop outside the composer wrote public history"

    box_drag(host, point(host,459))
    host.wait(lambda row: "attached to this draft" in row["lanStatus"], "Internal drop prepares the actual sealed box")
    assert host.field(host.state(),459).get("text") == "Keep this public draft"
    assert guest.field(guest.state(),461).get("text") == "No messages yet."
    assert not (host.profile / "project-chat").exists(), "Drop alone wrote public history"
    host.click(464)
    host.wait(lambda row: "removed from the public draft" in row["lanStatus"], "Remove the staged YogiBox")
    assert not (host.profile / "project-chat").exists()

    double_box(host)
    assert 474 not in host.state()["hits"][::5], "The private preview in chat permits changes to the staged source"
    ui.key(host.window,0xFF1B)
    host.wait(lambda row: row["screen"] == "lan-chat" and row["lanMode"] == "hosting" and row["focus"] == 470,
              "Return to the same chat and restore focus")
    assert host.field(host.state(),459).get("text") == "Keep this public draft"
    keyboard_attach(host)
    host.wait(lambda row: "attached to this draft" in row["lanStatus"], "Keyboard attachment uses the same preparation")
    assert not (host.profile / "project-chat").exists()
    host.click(464)
    host.wait(lambda row: "removed from the public draft" in row["lanStatus"], "Clear keyboard-selected attachment")

    box_drag(host, point(host,459))
    host.wait(lambda row: "attached to this draft" in row["lanStatus"], "Restore attachment via drag")
    host.send("GTK host captured this region")
    guest.wait(lambda row: "[YogiBox 1]" in guest.field(row,461).get("text",""), "Host attachment appeared on its public message")
    view_capture(guest, "Host selected this workspace region", host_box[2], host_box[1])
    guest.click(468)

    box_drag(guest, point(guest,459))
    guest.wait(lambda row: "attached to this draft" in row["lanStatus"], "Guest drag prepares the private sealed box")
    guest.send("GTK guest captured this region")
    host.wait(lambda row: "[YogiBox 2]" in host.field(row,461).get("text",""), "Guest attachment appeared on its public message")
    view_capture(host, "Guest selected this workspace region", guest_box[2], guest_box[1], newer=True)
    assert host_box[3].read_bytes() == host_box[4] and guest_box[3].read_bytes() == guest_box[4]

    guest.click(465)
    guest.wait(lambda row: row["lanImageBounds"], "A guest attachment was open before revocation")
    host.click(451)
    guest.wait(lambda row: row["lanMode"] == "closed" and not row["lanImageBounds"], "Revocation cleared the visible attachment")
    guest.click(451)

    double_box(host)
    host.click(474)
    host.wait(lambda row: host.field(row,473).get("visible"), "Explicitly unseal the local original")
    host.click(477)
    host.wait(lambda row: "No captured regions" in row["texts"], "Remove the previous private capture")
    host.fill(473,"Changed private description")
    host.click(472)
    host.wait(lambda row: row["laySelecting"], "Start a new capture for the private version")
    alternate = host_box[1].copy()
    alternate[0] += 150
    replacement = pixels(host, alternate)
    assert replacement != host_box[2]
    drag_region(host, alternate)
    host.wait(lambda row: row["screen"] == "yogi" and 475 in row["hits"][::5], "Added different private pixels")
    host.click(474)
    host.wait(lambda row: "Sealed YogiBox" in row["texts"] and "Changed private description" in row["texts"], "Resealed local original")
    revised_package = host_box[3].read_bytes()
    changed_image, = json.loads(revised_package)["package"]["items"]
    assert base64.b64decode(changed_image["capture"]["pixels"]) == b"".join(pixel.to_bytes(3,"big") for pixel in replacement)
    assert revised_package != host_box[4]
    host.click(471)
    invite()
    review(host_box[0])
    guest.click(458)
    guest.wait(lambda row: guest.field(row,461).get("text") == "No messages yet." and 465 not in row["hits"][::5],
               "Fresh invitation gave no old attachments")

    host.wait(lambda row: "View YogiBox 2" in row["texts"], "Host retained history")
    host.click(466)
    host.wait(lambda row: "View YogiBox 1" in row["texts"], "Select the original public attachment")
    view_capture(host, "Host selected this workspace region", host_box[2], host_box[1])
    host.click(468)

    box_drag(host, point(host,459))
    host.wait(lambda row: "attached to this draft" in row["lanStatus"], "New private version staged explicitly")
    double_box(host)
    host.wait(lambda row: "Changed private description" in row["texts"], "The reopened private box has the new version")
    host.close()
    guest.wait(lambda row: row["lanMode"] == "closed", "Host shutdown ended the fresh admission")
    guest.close()
    journal, = (host.profile / "project-chat").glob("*.json")
    assert [row["text"] for row in json.loads(journal.read_bytes())["messages"]] == [
        "GTK host captured this region", "GTK guest captured this region"]
    assert not (guest.profile / "project-chat").exists()
    assert not (host.profile / "helper-conversations").exists() and not (guest.profile / "helper-conversations").exists()
    assert host_box[3].read_bytes() == revised_package and guest_box[3].read_bytes() == guest_box[4]
    print("PASS actual GTK drag, outside/external drop rejection, double-click, keyboard attach, removal and close without sending",flush=True)
    print("PASS bidirectional exact pixels, original snapshot after private reseal, host-only history, revocation and empty re-entry",flush=True)


def lan(root, image, command):
    with internal_network(image) as (network, image_id), \
         peer(root,network,image_id,HOST) as host, peer(root,network,image_id,GUEST) as guest:
        host.launch(command)
        guest.launch(command)
        def invite():
            host.issue()
            host.copy_invite()
        def review(owner):
            guest.review(host,next(iter(host.listeners()))[1],owner["title"])
        exercise(host,guest,invite,review)


def relayed(root, image):
    checkout, command = fixture_build(root)
    left, right, left_relay, right_relay = "192.0.2.35","198.51.100.35","192.0.2.34","198.51.100.34"
    relay_key, relay_pin, _ = identity("relay.confectory.invalid")
    host_key, host_pin, fingerprint = identity("chat-host.confectory.invalid")
    with internal_network(image,"192.0.2.32/29") as (a,image_id), internal_network(image,"198.51.100.32/29") as (b,_), \
         peer(root,a,image_id,left,checkout) as host, peer(root,b,image_id,right,checkout) as guest, \
         peer(root,a,image_id,left_relay,checkout,other_network=(b,right_relay)) as relay, reservations(relay,command,relay_key) as reserve:
        pairs = [reserve(240) for _ in range(2)]
        host.launch(command,dict(role="host",identity=host_key,relayPin=relay_pin,address=left_relay,reservations=[p[0] for p in pairs]))
        guest.launch(command,dict(role="guest",identity=host_pin,relayPin=relay_pin,address=right_relay,reservations=[p[1] for p in pairs]))
        pending = iter(pairs)
        def review(owner):
            _, reservation = next(pending)
            relay_review(guest,f"{right_relay}:{reservation['port']}",fingerprint,owner)
        exercise(host,guest,lambda:relay_issue(host),review)


if __name__ == "__main__":
    root = Path(tempfile.mkdtemp(prefix="cf-native-create-lay-test-"))
    print("Native capture fixture logs at",root,flush=True)
    if len(sys.argv) == 3:
        report = json.loads(Path(sys.argv[2]).read_text())
        assert report["target"] == "linux"
        lan(root,sys.argv[1],report["run"])
    else:
        relayed(root,sys.argv[1])
