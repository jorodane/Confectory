#!/usr/bin/env python3
"""Exercise local EY and LaY with real GTK input in the installed Linux package."""
import json
from pathlib import Path
import sys
import tempfile
import time

from editor_create_lay_x11 import double_box, drag_region, hold, move, pixels
from editor_home_project_display_x11 import close_project, gtk, make_project
from editor_lan_chat_x11 import ui
from editor_local_multilay_x11 import check_image, saved

OBJECT = "Recent.Alpha::CaptureSubject"
DESCRIPTION = "Alpha local capture only"


def seed(package, root):
    (root / "profile").mkdir()
    projects = []
    originals = {}
    for name in ("Alpha", "Bravo"):
        manifest, _ = make_project(package, root, name)
        for path in manifest.parent.iterdir():
            path.write_text(path.read_text().replace("Recent." + name, "Recent.Alpha"))
        source = manifest.parent / "CaptureSubject.celem"
        source.write_text(f'object {OBJECT} {{ description "{name} semantic source"; }}\n')
        manifest.write_text(manifest.read_text().rstrip()[:-1] +
                            'element CaptureSubject object "CaptureSubject.celem";\n}\n')
        originals.update({path: path.read_bytes() for path in manifest.parent.iterdir()})
        projects.append({"path": str(manifest), "title": name, "description": ""})
    (root / "profile/projects.json").write_text(json.dumps(projects, separators=(",", ":")))
    return projects, originals


def open_subject(app, index):
    app.click(100 + index * 3)
    active = app.wait(lambda row: row["screen"] == "project", "Open the fixture project")
    app.click(55)
    row = app.wait(lambda row: row["model"]["workspace"] and row["model"]["workspace"]["unit"],
                   "Open owned source workspace")
    while row["model"]["workspace"]["selected"] != OBJECT:
        workspace = row["model"]["workspace"]
        ids = [unit["id"] for unit in workspace["units"]]
        current = workspace["selected"]
        app.click(57 if ids.index(current) < ids.index(OBJECT) else 56)
        row = app.wait(lambda row: row["model"]["workspace"]["selected"] != current, "Move source selection")
    return active["model"]["selected"]


def begin(app, from_box=False):
    if from_box:
        app.click(472)
    else:
        ui.key(app.window, "y", (0xFFE3,))
    row = app.wait(lambda row: row["laySelecting"] and row["eyBounds"], "Ctrl+Y shows the owned EY target")
    x, y, width, height = row["eyBounds"][:4]
    return x + min(12, width // 2), y + height // 2


def box(app, condition=lambda row: True):
    return app.wait(lambda row: row["screen"] == "yogi" and not row["job"] and condition(row),
                    "Private YogiBox shows the expected result")


def package_files(manifest):
    return list(Path(manifest).parent.glob(".confectory/yogi/package-*.json"))


def finish(app, count):
    return box(app, lambda row: len(row["model"]["yogi"]["items"]) == count)


def workflow(package, root):
    projects, originals = seed(package, root)
    with gtk(package, root, "installed-gtk-ey") as app:
        alpha = open_subject(app, 0)
        initial = app.state()
        unit = initial["model"]["workspace"]["unit"]
        start_operation = initial["operation"]

        begin(app)
        ui.key(app.window, 0xFF1B)
        app.wait(lambda row: not row["laySelecting"], "Escape cancels an empty EY selection")
        begin(app)
        app.click(61)  # Reload Source inside the painted workspace is not the semantic target.
        row = app.wait(lambda row: not row["laySelecting"] and "painted workspace" in row["message"],
                       "Non-semantic action is consumed during capture")
        assert row["operation"] == start_operation and row["model"]["workspace"]["unit"] == unit
        assert not package_files(alpha["path"])

        x, y = begin(app)
        move(app.window, x, y)
        hold(True)
        try:
            move(app.window, x + 32, y + 14)
            time.sleep(.09)
            move(app.window, x, y)
        finally:
            hold(False)
        app.wait(lambda row: not row["laySelecting"] and "512" in row["message"], "A drag back to its origin is not an EY")
        assert not package_files(alpha["path"])

        x, y = begin(app)
        ui.click(app.window, x, y)
        row = finish(app, 1)
        file, = package_files(alpha["path"])
        original_ey, = saved(file)["items"]
        assert row["model"]["workspace"]["unit"] == unit
        assert f"EY · {OBJECT} · current" in row["texts"]
        assert original_ey["id"] == OBJECT and original_ey["kind"] == "semantic"
        assert original_ey["elementKind"] == "object" and original_ey["metadata"]["description"] == "Alpha semantic source"
        assert not any(key in original_ey for key in ("capture", "path", "file"))
        app.fill(473, DESCRIPTION)

        # Sample the ordinary workspace before its capture outlines are drawn.
        app.click(471)
        app.wait(lambda row: row["screen"] == "project", "Return to the same workspace")
        crop = [x, y, 47, 8]
        original_pixels = pixels(app, crop)
        assert begin(app) == (x, y)
        drag_region(app, crop)  # Start over the real EY target, then move past the threshold.
        row = finish(app, 2)
        ey, image = saved(file)["items"]
        assert ey == original_ey and app.field(row, 473)["text"] == DESCRIPTION
        check_image(image, crop, original_pixels)

        begin(app, from_box=True)
        drag_region(app, [x + 3, y + 2, 34, 8])
        finish(app, 3)
        app.click(442)
        row = box(app, lambda row: "2 / 2" in row["texts"])
        assert "LaY 2 · 34 × 8" in row["texts"]
        app.click(477)
        finish(app, 2)
        assert saved(file)["items"] == [ey, image]

        app.click(474)
        box(app, lambda row: "Sealed YogiBox" in row["texts"] and DESCRIPTION in row["texts"])
        app.click(471)
        app.wait(lambda row: row["screen"] == "project", "Return from mixed sealed box")
        double_box(app)
        row = finish(app, 2)
        assert f"EY · {OBJECT} · current" in row["texts"] and "LaY 1 · 47 × 8" in row["texts"]
        assert saved(file)["items"] == [ey, image] and saved(file)["text"] == DESCRIPTION

        app.click(474)
        box(app, lambda row: app.field(row, 473).get("visible"))
        app.click(477)
        finish(app, 1)
        assert saved(file)["items"] == [image]  # Remove the EY only.
        x, y = begin(app, from_box=True)
        ui.click(app.window, x, y)
        finish(app, 2)
        _, remaining_ey = saved(file)["items"]
        app.click(477)
        finish(app, 1)
        assert saved(file)["items"] == [remaining_ey] and remaining_ey["id"] == OBJECT
        app.click(474)
        box(app, lambda row: "Sealed YogiBox" in row["texts"])
        a_bytes = file.read_bytes()

        app.click(471)
        close_project(app)
        home = app.wait(lambda row: row["screen"] == "home", "Project closed")
        assert home["model"]["yogi"] is None and 470 not in home["hits"][::5]
        ui.key(app.window, "y", (0xFFE3,))
        assert not app.state()["laySelecting"]

        bravo = open_subject(app, 1)
        assert bravo["projectId"] != alpha["projectId"] and not package_files(bravo["path"])
        row = app.wait(lambda row: row["screen"] == "project", "Other project has no Alpha box")
        assert row["model"]["yogi"] is None
        x, y = begin(app)
        ui.click(app.window, x, y)
        row = finish(app, 1)
        b_file, = package_files(bravo["path"])
        assert saved(b_file)["items"][0]["metadata"]["description"] == "Bravo semantic source"
        assert not app.field(row, 473)["text"]
        assert file.read_bytes() == a_bytes

    assert all(path.read_bytes() == data for path, data in originals.items())
    assert not (root / "profile/project-chat").exists() and not (root / "profile/helper-conversations").exists()
    print("PASS installed GTK click EY, drag LaY, cancellation, mixed removal and seal, and same-ID project isolation")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="local-native-ey-") as path:
        workflow(Path(sys.argv[1]).resolve(), Path(path))
