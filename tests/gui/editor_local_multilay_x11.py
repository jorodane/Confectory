#!/usr/bin/env python3
"""Write one local two-image YogiBox through the native GTK editor.

Pass a Linux EditorHome build report. Use a dedicated Xorg DISPLAY with
XAUTHORITY and CONFECTORY_DOTNET, as in editor_lan_chat_x11.py.
"""
import base64
import json
import os
from pathlib import Path
import sys
import tempfile
import time

from editor_create_lay_x11 import double_box, drag_region, hold, move, packages, pixels, start_drag
from editor_lan_chat_x11 import NativeEditor, eventually, repo, ui


TITLE = "Local GTK two regions"
CHAT_DRAFT = "Unsent local Helper draft"
PRELIMINARY = "Description while choosing another region"
DESCRIPTION = "Keep only the second region"


class LocalEditor(NativeEditor):
    def __init__(self, root):
        super().__init__(None, root / "profile", repo)
        self.profile.mkdir()
        self.env = os.environ.copy()
        for key in ("CONFECTORY_WEB_PROJECT", "CONFECTORY_DEV_PUBLIC_CHAT_LOOPBACK",
                    "CONFECTORY_TEST_PUBLIC_CHAT_RELAY"):
            self.env.pop(key, None)
        self.env.update(
            CONFECTORY_UI="native", CONFECTORY_HOME_TRACE="1",
            CONFECTORY_EDITOR_REPO=str(repo), CONFECTORY_HOME_STORAGE=str(self.profile),
            CONFECTORY_ENTRY_STORAGE=str(root / "entry"), CONFECTORY_ENTRY_SCOPE=str(root / "bridge"),
            CONFECTORY_MCP_DIRECTORY=str(root / "instances"),
            GSETTINGS_BACKEND="memory", HOME=str(root / "home"),
            XDG_CACHE_HOME=str(root / "cache"), XDG_CONFIG_HOME=str(root / "config"),
            XDG_DATA_HOME=str(root / "data"),
        )
        (root / "home").mkdir()

    def command(self, command, setup=False, **variables):
        assert not setup
        return ["env", *[f"{key}={value}" for key, value in dict(self.env, **variables).items()], *command]


def saved(file):
    return json.loads(file.read_bytes())["package"]


def check_image(item, area, expected):
    assert item["kind"] == "image"
    capture = item["capture"]
    assert (capture["width"], capture["height"]) == tuple(area[2:])
    assert base64.b64decode(capture["pixels"]) == b"".join(pixel.to_bytes(3, "big") for pixel in expected)


def cancel_drag(editor, area):
    ui.key(editor.window, "y", (0xFFE3,))
    editor.wait(lambda row: row["laySelecting"], "Ctrl+Y starts the second capture")
    x, y, width, height = area
    before_drag = pixels(editor, area)
    move(editor.window, x, y)
    hold(True)
    try:
        time.sleep(.04)
        move(editor.window, x + width, y + height)
        eventually(lambda: pixels(editor, area) != before_drag, "Active LaY outline before Escape", timeout=5)
        ui.key(editor.window, 0xFF1B)
        editor.wait(lambda row: row["screen"] == "project" and not row["laySelecting"],
                    "Escape cancels the drag before pointer release")
    finally:
        hold(False)
    editor.click(470)
    return editor.wait(lambda row: row["screen"] == "yogi" and editor.field(row, 473).get("visible"),
                       "Read the original unsealed draft after releasing the mouse")


def run(editor, projects):
    opened = editor.create(TITLE, CHAT_DRAFT, projects)
    manifest = Path(opened["path"])
    original = {path: path.read_bytes() for path in manifest.parent.rglob("*")
                if path.is_file() and ".confectory" not in path.parts}
    editor.click(55)
    selected = editor.wait(lambda row: row["model"]["workspace"] and row["model"]["workspace"]["unit"],
                           "Selected workspace before local capture")
    x, y, _, _ = selected["layBounds"]
    first = [x + 10, y + 11, 112, 31]
    second = [x + 160, y + 11, 96, 27]
    ui.click(editor.window, x + 1, y + 1)
    ui.key(editor.window, "y", (0xFFE3,))
    editor.wait(lambda row: row["laySelecting"], "Native shortcut enters region selection")
    ui.click(editor.window, first[0], first[1])
    editor.wait(lambda row: row["screen"] == "project" and not row["laySelecting"]
                and "painted workspace" in row["message"], "A click outside the semantic target cannot create a GTK capture")
    assert not packages(editor)
    print("PASS a click outside the native EY target leaves the package untouched", flush=True)

    first_pixels = pixels(editor, first)
    start_drag(editor, first)
    editor.wait(lambda row: row["screen"] == "yogi" and 475 in row["hits"][::5], "First LaY row")
    package, = packages(editor)
    first_item, = saved(package)["items"]
    check_image(first_item, first, first_pixels)
    editor.fill(473, PRELIMINARY)
    before_cancel = package.read_bytes()
    saved_at = package.stat().st_mtime_ns
    editor.click(471)
    editor.wait(lambda row: row["screen"] == "project", "Return to the same workspace with an unsealed draft")
    row = cancel_drag(editor, second)
    assert row["model"]["selected"]["projectId"] == opened["projectId"]
    assert editor.field(row, 473)["text"] == PRELIMINARY
    assert [item["item"] for item in row["model"]["yogi"]["items"]] == [first_item["item"]]
    assert packages(editor) == [package] and package.read_bytes() == before_cancel
    assert package.stat().st_mtime_ns == saved_at
    assert not (editor.profile / "project-chat").exists() and not (editor.profile / "helper-conversations").exists()
    assert all(path.read_bytes() == before for path, before in original.items())
    print("PASS Escape during the second drag keeps the original LaY and pending description without a storage write or send", flush=True)

    editor.click(472)
    editor.wait(lambda row: row["screen"] == "project" and row["laySelecting"], "Capture LaY adds from the same draft")
    second_pixels = pixels(editor, second)
    drag_region(editor, second)
    row = editor.wait(lambda row: row["screen"] == "yogi" and {475, 476, 477, 478} <= set(row["hits"][::5]),
                      "Two different LaY rows and two removal controls")
    assert editor.field(row, 473)["text"] == PRELIMINARY
    combined = saved(package)
    assert not combined["sealed"] and combined["items"][0] == first_item
    remaining = combined["items"][1]
    assert first_item["item"] != remaining["item"]
    check_image(remaining, second, second_pixels)
    print("PASS native Ctrl+Y and Capture LaY add two distinct workspace regions to one draft", flush=True)

    editor.click(474)
    editor.wait(lambda row: "Sealed YogiBox" in row["texts"] and PRELIMINARY in row["texts"],
                "Seal both original and retried captures")
    editor.click(471)
    editor.wait(lambda row: row["screen"] == "project", "Return to the workspace to reopen the box")
    double_box(editor)
    editor.wait(lambda row: PRELIMINARY in row["texts"] and {475, 476} <= set(row["hits"][::5]),
                "Reopened sealed box shows both captures")
    assert saved(package)["items"] == [first_item, remaining]
    assert saved(package)["text"] == PRELIMINARY
    editor.click(474)
    editor.wait(lambda row: editor.field(row, 473).get("visible"), "Explicitly reopen the draft for removal")

    editor.click(477)
    row = editor.wait(lambda row: row["screen"] == "yogi" and 475 in row["hits"][::5]
                      and 476 not in row["hits"][::5], "Only the second region remains")
    assert editor.field(row, 473)["text"] == PRELIMINARY
    assert saved(package)["items"] == [remaining]
    editor.fill(473, DESCRIPTION)
    editor.click(474)
    editor.wait(lambda row: "Sealed YogiBox" in row["texts"] and DESCRIPTION in row["texts"], "Seal exact remaining item")
    sealed = package.read_bytes()
    result = saved(package)
    assert result["sealed"] and result["items"] == [remaining] and result["text"] == DESCRIPTION

    editor.click(471)
    editor.wait(lambda row: row["screen"] == "project" and editor.field(row, 38).get("text") == CHAT_DRAFT,
                "Same project and unsent Helper draft")
    double_box(editor)
    row = editor.wait(lambda row: DESCRIPTION in row["texts"] and 475 in row["hits"][::5], "Reopened sealed local box")
    assert not ({476, 477, 478} & set(row["hits"][::5]))
    assert "LaY 1 · 96 × 27" in row["texts"]
    assert [item["item"] for item in row["model"]["yogi"]["items"]] == [remaining["item"]]
    assert package.read_bytes() == sealed and packages(editor) == [package]
    assert not (editor.profile / "project-chat").exists() and not (editor.profile / "helper-conversations").exists()
    assert all(path.read_bytes() == before for path, before in original.items())
    print("PASS native removal, description, seal and double-click restore the same LaY and keep the original files and chat draft", flush=True)


if __name__ == "__main__":
    report = json.loads(Path(sys.argv[1]).read_text())
    assert report["target"] == "linux"
    root = Path(tempfile.mkdtemp(prefix="cf-native-multilay-"))
    print("Native multi-LaY fixture logs at", root, flush=True)
    projects = root / "projects"
    projects.mkdir()
    editor = LocalEditor(root)
    try:
        editor.launch(report["run"])
        run(editor, projects)
        editor.close()
    finally:
        if getattr(editor, "child", None) is not None and editor.child.poll() is None:
            editor.child.terminate()
            editor.child.wait(timeout=15)
        if getattr(editor, "stream", None) is not None:
            editor.stream.close()
