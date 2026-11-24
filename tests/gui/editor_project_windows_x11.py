#!/usr/bin/env python3
"""Exercise the confirmed project-window menu and existing GTK source review."""
import os
from pathlib import Path
import sys
from tempfile import mkdtemp

from editor_home_project_display_x11 import close_project, gtk
from editor_lan_chat_x11 import ui
from project_owned_window_boundary import WINDOW, WINDOW_TITLE, seed


def open_project(app, project):
    cards = app.state()["model"]["cards"]
    index = next(n for n, row in enumerate(cards) if row["path"] == project["path"])
    app.click(100 + index * 3)
    app.wait(lambda row: row["screen"] == "project" and not row["job"]
             and row["model"]["selected"]["path"] == project["path"], "Open fixture project")


def menu(app, available):
    app.click(33)
    row = app.wait(lambda row: row["operation"] == "native-project-windows-list" and not row["job"]
                   and 317 in row["hits"][::5], "Read the confirmed project menu")
    assert (480 in row["hits"][::5]) is available
    assert 36 in row["hits"][::5] and "Close menu" in row["texts"]
    return row


def source_view(app):
    if app.state()["model"]["workspace"] is None:
        app.click(55)
    row = app.wait(lambda row: app.field(row, 54).get("visible") and not row["job"],
                   "Open the existing source editor")
    while row["model"]["workspace"]["selected"] != WINDOW:
        workspace = row["model"]["workspace"]
        ids = [unit["id"] for unit in workspace["units"]]
        current = workspace["selected"]
        app.click(57 if ids.index(current) < ids.index(WINDOW) else 56)
        row = app.wait(lambda row: not row["job"] and row["model"]["workspace"]["selected"] != current,
                       "Select the registered View in the ordinary source editor")
    return app.field(row, 54)["text"]


def review(app):
    app.click(64)
    return app.wait(lambda row: row["model"]["workspace"].get("review") is not None and not row["job"],
                    "Existing View source Review")


def change_renderer(app, file, renderer, *, cancel=False):
    before = file.read_bytes()
    text = source_view(app)
    old = 'value editorWindow = "element-view-card";'
    new = f'value editorWindow = "{renderer}";'
    edited = text.replace(old, new) if old in text else text.rstrip()[:-1] + new + " }\n"
    app.fill(54, edited)
    app.click(58)
    app.wait(lambda row: not row["job"] and row["model"]["workspace"]["unit"]["text"] == edited,
             "Save the working copy only")
    assert file.read_bytes() == before
    if cancel:
        menu(app, False)
        app.click(42)
        review(app)
        app.click(66)
        app.wait(lambda row: not row["job"] and not row["model"]["workspace"].get("review"), "Cancel Review")
        assert file.read_bytes() == before
        menu(app, False)
        app.click(42)
    review(app)
    app.click(65)
    app.wait(lambda row: not row["job"] and file.read_text() == edited, "Confirm the explicit View setting")
    return edited.encode()


def open_window(app, renderer):
    menu(app, True)
    app.click(480)
    app.wait(lambda row: WINDOW_TITLE in row["texts"] and 484 in row["hits"][::5], "The only approved window")
    assert "Unsupported renderer" not in app.state()["texts"] and 485 not in app.state()["hits"][::5]
    app.click(484)
    row = app.wait(lambda row: not row["job"] and app.field(row, 487).get("visible"), "Open the confirmed projection")
    assert f"Read-only {renderer}" in row["texts"] and "Note" in row["texts"]
    assert app.field(row, 487)["readonly"] is True
    assert app.field(row, 487)["text"] == "Local Alpha only"
    app.click(487)
    app.key(487, "x")
    app.wait(lambda row: row["focus"] == 487 and app.field(row, 487)["text"] == "Local Alpha only",
             "The native field accepts focus and preserves the read-only value")


def workflow(package, root):
    (alpha, bravo), originals, run_proof = seed(package, root)
    source = Path(alpha["path"]).with_name("StockDesk.celem")
    starting = originals[source]
    with gtk(package, root, "gtk-project-windows") as app:
        ui.resize(ui.display, app.window, 1080, 760)
        ui.flush(ui.display)
        app.wait(lambda row: row["width"] == 1080 and row["height"] == 760, "Resize the isolated GTK window")
        open_project(app, alpha)
        menu(app, False)
        app.click(42)
        originals[source] = change_renderer(app, source, "element-view-card", cancel=True)
        open_window(app, "card")
        app.click(42)
        originals[source] = change_renderer(app, source, "element-view-table")
        open_window(app, "table")
        app.click(481)
        app.wait(lambda row: 484 in row["hits"][::5] and not app.field(row, 487).get("visible"),
                 "Close the opened value and retain the project menu")
        # Change only the disposable confirmed fixture between listing and activation.
        source.write_bytes(starting)
        app.click(484)
        denied = app.wait(lambda row: "This project window is no longer available." in row["message"]
                          and not row["job"], "A cached entry cannot open a revoked source")
        assert not app.field(denied, 487).get("visible")
        source.write_bytes(originals[source])
        app.click(42)
        open_window(app, "table")
        app.click(33)
        app.wait(lambda row: not app.field(row, 487).get("visible") and 480 not in row["hits"][::5],
                 "The primary project menu closes the read-only projection")
        close_project(app)
        assert not {480, 484, 487}.intersection(app.state()["hits"][::5])
        open_project(app, bravo)
        denied = menu(app, False)
        assert not app.field(denied, 487).get("visible")
    assert not run_proof.exists()
    assert all(path.read_bytes() == data for path, data in originals.items())
    print("PASS GTK card, table, source Review/Cancel/Confirm, stale menu rejection, A/B/Home and read-only field")


if __name__ == "__main__":
    root = Path(mkdtemp(prefix="gtk-project-windows-", dir=os.environ.get("TMPDIR")))
    workflow(Path(sys.argv[1]).resolve(), root)
