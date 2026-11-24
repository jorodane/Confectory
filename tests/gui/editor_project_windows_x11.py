#!/usr/bin/env python3
"""Exercise the confirmed project-window menu and existing GTK source review."""
import json
import os
from pathlib import Path
import sys
from tempfile import mkdtemp

from editor_home_project_display_x11 import close_project, gtk
from editor_lan_chat_x11 import ui
from project_owned_window_boundary import UNSUPPORTED, WINDOW, WINDOW_TITLE, seed


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


def source_view(app, target=WINDOW):
    if app.state()["model"]["workspace"] is None:
        app.click(55)
    row = app.wait(lambda row: app.field(row, 54).get("visible") and not row["job"],
                   "Open the existing source editor")
    while row["model"]["workspace"]["selected"] != target:
        workspace = row["model"]["workspace"]
        ids = [unit["id"] for unit in workspace["units"]]
        current = workspace["selected"]
        app.click(57 if ids.index(current) < ids.index(target) else 56)
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


def choose_menu_setting(app, current, button, expected):
    app.click(488)
    app.wait(lambda row: not row["job"] and "✓ " + current in row["texts"],
             "Read the current View menu setting")
    app.click(button)
    row = app.wait(lambda row: not row["job"]
                   and row["model"]["status"].startswith("Project window setting staged.")
                   and row["model"]["workspace"]["unit"]["text"] == expected
                   and app.field(row, 54)["text"] == expected,
                   "Stage one setting in the existing View draft and refresh its GTK field")
    assert row["model"]["workspace"]["review"] is None


def workflow_menu_setting(package, root):
    (alpha, bravo), originals, proof = seed(package, root)
    source = Path(alpha["path"]).with_name("StockDesk.celem")
    original = originals[source]
    with gtk(package, root, "gtk-menu-setting") as app:
        ui.resize(ui.display, app.window, 1080, 760)
        ui.flush(ui.display)
        app.wait(lambda row: row["width"] == 1080 and row["height"] == 760, "Resize the isolated GTK window")
        open_project(app, alpha)
        unsupported = source_view(app, UNSUPPORTED)
        app.click(488)
        blocked = app.wait(lambda row: not row["job"] and "does not support" in row["message"],
                           "Reject the unsupported View")
        assert not {489, 490, 491}.intersection(blocked["hits"][::5])
        assert app.field(blocked, 54)["text"] == unsupported

        prior_input = source_view(app).replace("{ ", '{ description "Kept across menu editing"; ', 1)
        prior_input += '// A trailing comment with } and value editorWindow = "ignored";\n'
        app.fill(54, prior_input)
        card = prior_input.replace(" }", ' value editorWindow = "element-view-card"; }', 1)
        choose_menu_setting(app, "Hidden", 490, card)
        assert source.read_bytes() == original
        review(app)
        app.click(66)
        row = app.wait(lambda row: not row["job"] and row["model"]["workspace"]["review"] is None,
                       "Cancel the existing Review")
        assert app.field(row, 54)["text"] == card and source.read_bytes() == original
        menu(app, False)
        app.click(42)
        review(app)
        app.click(65)
        app.wait(lambda row: not row["job"] and source.read_text() == card, "Confirm the selected card")
        open_window(app, "card")
        app.click(33)

        table = card.replace('editorWindow = "element-view-card"', 'editorWindow = "element-view-table"', 1)
        choose_menu_setting(app, "Read-only card", 491, table)
        assert source.read_text() == card
        review(app)
        app.click(65)
        app.wait(lambda row: not row["job"] and source.read_text() == table, "Confirm the selected table")
        open_window(app, "table")
        app.click(33)

        hidden = table.replace('value editorWindow = "element-view-table";', "", 1)
        choose_menu_setting(app, "Read-only table", 489, hidden)
        assert source.read_text() == table
        review(app)
        app.click(65)
        app.wait(lambda row: not row["job"] and source.read_text() == hidden, "Confirm removal from the menu")
        menu(app, False)
        app.click(42)
        close_project(app)
        open_project(app, bravo)
        app.click(55)
        row = app.wait(lambda row: not row["job"] and row["model"]["workspace"] is not None,
                       "Open the separate project's owned sources")
        assert WINDOW not in {unit["id"] for unit in row["model"]["workspace"]["units"]}
        assert 488 not in row["hits"][::5]
    originals[source] = hidden.encode()
    assert not proof.exists()
    assert all(path.read_bytes() == data for path, data in originals.items())
    print("PASS GTK View menu settings: draft preservation, cancel, confirm card and table, hide, and project scope")


def workflow_window_revocation(package, root, reader_package):
    (alpha, bravo), originals, proof = seed(package, root)
    source = Path(alpha["path"]).with_name("StockDesk.celem")
    reader_root = root / "reader"
    (reader_root / "profile").mkdir(parents=True)
    (reader_root / "profile" / "projects.json").write_text(json.dumps([alpha, bravo]))

    def prepare(app):
        ui.resize(ui.display, app.window, 1080, 760)
        ui.flush(ui.display)
        app.wait(lambda row: (row["width"], row["height"]) == (1080, 760), "Resize the test window")
        open_project(app, alpha)
        return source_view(app)

    def confirm_setting(app, expected):
        review(app)
        app.click(65)
        row = app.wait(lambda row: not row["job"] and row["model"]["status"].startswith("Confirm "),
                       "Confirm the View from the other window", timeout=180)
        assert source.read_text() == expected, row["model"]["status"]

    def reload_window(app, retained):
        assert "487" in app.state()["fields"]
        app.click(61)
        message = ("Current source revision loaded explicitly" if retained
                   else "This project window is no longer available.")
        row = app.wait(lambda row: not row["job"] and row["operation"] == "native-project-windows-list"
                       and row["message"] == message, "Reload source with the panel already open")
        # Clicking the source toolbar may put it in front of the menu. The panel
        # still owns its field while behind it, so test existence as well as data.
        assert ("487" in row["fields"]) is retained
        assert row["model"]["selected"]["path"] == alpha["path"]
        if retained:
            assert app.field(row, 487)["text"] == "Local Alpha only"
        else:
            assert not {480, 481, 484, 487}.intersection(row["hits"][::5])
        return row

    with gtk(package, root, "author") as author:
        text = prepare(author)
        card = text.replace(" }", ' value editorWindow = "element-view-card"; }', 1)
        choose_menu_setting(author, "Hidden", 490, card)
        confirm_setting(author, card)
        with gtk(reader_package, reader_root, "reader") as reader:
            prepare(reader)
            open_window(reader, "card")
            # Hide each project through the normal menu and retain its workspace.
            reader.click(33)
            menu(reader, True)
            reader.click(15)
            reader.wait(lambda row: row["screen"] == "home", "Hide Alpha")
            open_project(reader, bravo)
            assert "487" not in menu(reader, False)["fields"]
            reader.click(15)
            reader.wait(lambda row: row["screen"] == "home", "Hide Bravo")
            open_project(reader, alpha)
            assert "487" not in reader.state()["fields"]
            source_view(reader)
            open_window(reader, "card")
            print("PASS A → B → A cleared the old panel and required a fresh explicit open", flush=True)

            hidden = card.replace('value editorWindow = "element-view-card";', "", 1)
            choose_menu_setting(author, "Read-only card", 489, hidden)
            assert source.read_text() == card
            reload_window(reader, True)

            review(author)
            author.click(66)
            author.wait(lambda row: not row["job"] and row["model"]["workspace"]["review"] is None,
                        "Cancel the author's Review")
            assert source.read_text() == card
            reload_window(reader, True)
            print("PASS unconfirmed Hide and canceled Review preserve the reader's card", flush=True)

            confirm_setting(author, hidden)
            row = reload_window(reader, False)
            if row["model"]["shell"]["menu"] == "project":
                reader.click(33)
            assert "487" not in menu(reader, False)["fields"]
            assert not proof.exists()
            print("PASS confirmed Hide retired the held panel on Reload source and the entry could not reopen", flush=True)
    originals[source] = hidden.encode()
    assert all(path.read_bytes() == value for path, value in originals.items())


if __name__ == "__main__":
    root = Path(mkdtemp(prefix="gtk-project-windows-", dir=os.environ.get("TMPDIR")))
    package = Path(sys.argv[1]).resolve()
    if len(sys.argv) > 2 and sys.argv[2] == "--revocation":
        reader_package = Path(sys.argv[3]).resolve() if len(sys.argv) > 3 else package
        workflow_window_revocation(package, root, reader_package)
    else:
        scenario = workflow_menu_setting if "--menu-setting" in sys.argv[2:] else workflow
        scenario(package, root)
