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


def workflow_opening_view(report, root):
    from editor_local_multilay_x11 import LocalEditor, repo

    app = LocalEditor(root)
    (alpha, bravo), originals, proof = seed(report, root, checkout=repo)
    view = Path(alpha["path"]).with_name("StockDesk.celem")
    initial = view.read_text().replace(" }", ' value editorWindow = "element-view-card"; }', 1)
    view.write_text(initial)
    invalid = Path(bravo["path"])
    invalid.write_text(invalid.read_text().rstrip()[:-1] + 'element Invalid view "Invalid.celem";\n}\n')
    invalid_view = invalid.with_name("Invalid.celem")
    invalid_view.write_text('view Recent.Alpha::Invalid { use object Recent.Alpha::Missing; '
                            'value editorName = "Invalid"; value editorMain = "element-view-table"; }')
    originals[invalid] = invalid.read_bytes()
    originals[invalid_view] = invalid_view.read_bytes()

    def opening_state(project, expected):
        open_project(app, project)
        row = app.wait(lambda row: not row["job"] and row["operation"] == "native-project-main-view"
                       and 55 in row["hits"][::5], "GTK opening View lookup finished")
        assert bool(app.field(row, 496).get("visible")) is expected
        assert 36 in row["hits"][::5] and 33 in row["hits"][::5] and app.field(row, 38).get("visible")
        if expected:
            assert WINDOW_TITLE in row["texts"] and "Read-only table" in row["texts"]
            assert app.field(row, 496)["readonly"] and app.field(row, 496)["text"] == "Local Alpha only"

    def stage(button, prior, draft):
        app.click(492)
        app.wait(lambda row: not row["job"] and "✓ " + prior in row["texts"], "Read opening View setting")
        app.click(button)
        app.wait(lambda row: not row["job"] and app.field(row, 54).get("text") == draft,
                 "Stage opening View and retain other input")

    def confirm(expected):
        review(app)
        app.click(65)
        app.wait(lambda row: not row["job"] and view.read_text() == expected,
                 "Confirm the opening View through GTK", timeout=150)

    build = json.loads(report.read_text())
    assert build["target"] == "linux" and build["tool"]["ok"]
    try:
        app.launch(build["run"])
        ui.resize(ui.display, app.window, 1080, 760)
        ui.flush(ui.display)
        app.wait(lambda row: (row["width"], row["height"]) == (1080, 760), "Resize isolated GTK")
        opening_state(alpha, False)
        pending = source_view(app) + "// Keep the unsaved source comment.\n"
        app.fill(54, pending)
        proposed = pending.replace(" }", ' value editorMain = "element-view-table"; }', 1)
        stage(495, "Default workspace", proposed)
        review(app)
        app.click(66)
        row = app.wait(lambda row: not row["job"] and row["model"]["workspace"]["review"] is None,
                       "Cancel opening View Review")
        assert view.read_text() == initial and app.field(row, 54)["text"] == proposed
        close_project(app)
        opening_state(alpha, False)

        assert source_view(app) == proposed
        confirm(proposed)
        close_project(app)
        opening_state(bravo, False)
        close_project(app)
        opening_state(alpha, True)
        open_window(app, "card")
        app.click(33)
        app.wait(lambda row: app.field(row, 496).get("visible") and not app.field(row, 487).get("visible"),
                 "Independent menu card closes, leaving the opening table")
        assert not proof.exists()
        app.click(36)
        run = app.wait(lambda row: (row["model"].get("execution") or {}).get("state") in ("exited", "failed"),
                       "Run Alpha from its opening workspace", timeout=150)
        assert run["model"]["execution"]["state"] == "exited" and str(run["model"]["execution"]["exit"]) == "0"
        assert proof.read_bytes() == b"Alpha\n"

        assert source_view(app) == proposed
        assert not app.field(app.state(), 496).get("visible")
        cleared = proposed.replace('value editorMain = "element-view-table";', "", 1)
        stage(493, "Read-only table", cleared)
        confirm(cleared)
        close_project(app)
        assert not app.field(app.state(), 496).get("visible")
        opening_state(alpha, False)
        app.close()
    finally:
        if hasattr(app, "child") and app.child.poll() is None:
            app.child.terminate()
            app.child.wait(timeout=15)
        if hasattr(app, "stream") and not app.stream.closed:
            app.stream.close()
    originals[view] = cleared.encode()
    assert all(path.read_bytes() == data for path, data in originals.items())
    print("PASS GTK opening View: cancel, confirm, read-only table, menu card, Alpha Run, sources, reset and Bravo isolation")


def workflow_worker_opening_review(report, root):
    from editor_local_multilay_x11 import LocalEditor, repo
    from project_owned_window_boundary import stage_worker_opening_fixture

    app = LocalEditor(root)
    (alpha, _), originals, proof = seed(report, root, checkout=repo)
    source = Path(alpha["path"]).with_name("StockDesk.celem")
    initial = source.read_text()
    build = json.loads(report.read_text())
    assert build["target"] == "linux" and build["tool"]["ok"]

    def launch():
        app.launch(build["run"])
        ui.resize(ui.display, app.window, 1080, 760)
        ui.flush(ui.display)
        app.wait(lambda row: (row["width"], row["height"]) == (1080, 760), "Resize isolated GTK")

    def opening(expected):
        open_project(app, alpha)
        row = app.wait(lambda row: row["operation"] == "native-project-main-view" and not row["job"],
                       "GTK read the confirmed opening View")
        assert bool(app.field(row, 496).get("visible")) is expected
        if expected:
            assert app.field(row, 496)["readonly"] and app.field(row, 496)["text"] == "Local Alpha only"

    def verify_review(row, summary, *, worker):
        assert summary in row["texts"], row["texts"]
        attribution = [text for text in row["texts"] if "작업자 제안" in text]
        assert attribution == (["작업자 제안 · synthetic-worker · 작업 task-opening-view"] if worker else [])
        assert app.field(row, 67).get("visible") and app.field(row, 68).get("visible")

    try:
        launch()
        opening(False)
        app.close()
        stage_worker_opening_fixture(repo, alpha)
        assert source.read_text() == initial
        launch()
        opening(False)
        draft = source_view(app)
        assert draft != initial and 'editorMain = "element-view-card"' in draft
        summary = "프로젝트 시작 화면 · 기본 화면 → 읽기 전용 카드"
        verify_review(review(app), summary, worker=True)
        app.click(66)
        app.wait(lambda row: not row["job"] and row["model"]["workspace"]["review"] is None, "Cancel Review")
        assert source.read_text() == initial
        close_project(app)
        opening(False)
        assert source_view(app) == draft
        verify_review(review(app), summary, worker=True)
        app.click(65)
        app.wait(lambda row: not row["job"] and source.read_text() == draft, "Confirm Worker proposal", timeout=150)
        close_project(app)
        opening(True)

        assert source_view(app) == draft
        direct = draft.replace('"element-view-card"', '"element-view-table"', 1)
        app.fill(54, direct)
        verify_review(review(app), "프로젝트 시작 화면 · 읽기 전용 카드 → 읽기 전용 표", worker=False)
        app.click(66)
        app.wait(lambda row: not row["job"] and row["model"]["workspace"]["review"] is None,
                 "Cancel direct edit Review")
        assert source.read_text() == draft
        app.close()
    finally:
        if hasattr(app, "child") and app.child.poll() is None:
            app.child.terminate()
            app.child.wait(timeout=15)
        if hasattr(app, "stream") and not app.stream.closed:
            app.stream.close()
    assert not proof.exists()
    originals[source] = draft.encode()
    assert all(path.read_bytes() == data for path, data in originals.items())
    print("PASS GTK opening View Review shows exact Worker origin, cancels, confirms and reopens; direct edit has no attribution")


def workflow_recipe_view(report, root):
    from editor_local_multilay_x11 import LocalEditor, repo
    from project_owned_window_boundary import NS, seed_recipe

    app = LocalEditor(root)
    alpha, bravo, originals, proof, title, identifier = seed_recipe(report, root, repo)
    source = Path(alpha["path"]).with_name("RecipeDesk.celem")
    initial = source.read_text()
    draft = initial.replace(" }", ' value editorWindow = "element-view-recipe"; }', 1)
    build = json.loads(report.read_text())
    assert build["target"] == "linux" and build["tool"]["ok"]

    try:
        app.launch(build["run"])
        ui.resize(ui.display, app.window, 1080, 760)
        ui.flush(ui.display)
        app.wait(lambda row: (row["width"], row["height"]) == (1080, 760), "Resize isolated GTK")
        open_project(app, alpha)
        assert source_view(app, identifier) == initial
        app.click(488)
        choices = app.wait(lambda row: not row["job"] and 497 in row["hits"][::5], "Read-only recipe setting")
        assert not {490, 491}.intersection(choices["hits"][::5])
        app.click(497)
        app.wait(lambda row: not row["job"] and app.field(row, 54).get("text") == draft, "Stage recipe View")
        review(app)
        app.click(66)
        app.wait(lambda row: not row["job"] and row["model"]["workspace"]["review"] is None, "Cancel recipe Review")
        assert source.read_text() == initial
        menu(app, False)
        app.click(42)
        review(app)
        app.click(65)
        app.wait(lambda row: not row["job"] and source.read_text() == draft, "Confirm recipe View", timeout=150)
        menu(app, True)
        app.click(480)
        app.wait(lambda row: title in row["texts"] and 484 in row["hits"][::5], "Confirmed recipe menu entry")
        app.click(484)
        row = app.wait(lambda row: not row["job"] and app.field(row, 487).get("visible"), "Open recipe projection")
        value = f"Ingredients\n{NS}::Fiber × 2\n{NS}::Tile × 3\n\nResult\n{NS}::Panel × 4"
        assert title in row["texts"] and "Read-only recipe" in row["texts"]
        assert app.field(row, 487)["readonly"] and app.field(row, 487)["text"] == value
        app.click(487)
        app.key(487, "x")
        app.wait(lambda row: row["focus"] == 487 and app.field(row, 487)["text"] == value, "Recipe text remains read-only")
        app.click(33)
        app.wait(lambda row: not app.field(row, 487).get("visible"), "Close recipe projection")
        close_project(app)
        open_project(app, alpha)
        app.wait(lambda row: row["operation"] == "native-project-main-view" and not row["job"],
                 "Read the independent opening View")
        assert not app.field(app.state(), 496).get("visible")
        close_project(app)
        open_project(app, bravo)
        menu(app, False)
        assert not app.field(app.state(), 487).get("visible")
        app.close()
    finally:
        if hasattr(app, "child") and app.child.poll() is None:
            app.child.terminate()
            app.child.wait(timeout=15)
        if hasattr(app, "stream") and not app.stream.closed:
            app.stream.close()

    originals[source] = draft.encode()
    assert not proof.exists()
    assert all(path.read_bytes() == data for path, data in originals.items())
    print("PASS GTK recipe: cancel keeps it hidden; Confirm displays exact ingredients and result; Bravo and opening Workspace remain isolated")


def workflow_recipe_editor(report, root):
    from editor_local_multilay_x11 import LocalEditor, repo
    from project_owned_window_boundary import NS, seed_recipe

    app = LocalEditor(root)
    alpha, bravo, originals, proof, title, identifier = seed_recipe(report, root, repo, both=True)
    for project in (alpha, bravo):
        path = Path(project["path"]).with_name("RecipeDesk.celem")
        path.write_text(path.read_text().replace(" }", ' value editorWindow = "element-view-recipe"; }', 1))
        originals[path] = path.read_bytes()
    build = json.loads(report.read_text())
    assert build["target"] == "linux" and build["tool"]["ok"]

    def snapshots(project):
        folders = Path(project["path"]).parent.glob(".confectory/edit-workspaces/*/draft.json")
        return {path: path.read_bytes() for path in folders}

    def recipe(count):
        menu(app, True)
        app.click(480)
        app.wait(lambda row: title in row["texts"] and 484 in row["hits"][::5],
                 "Return to the confirmed Project windows list")
        app.click(484)
        row = app.wait(lambda row: not row["job"] and row["focus"] == 481 and 498 in row["hits"][::5],
                       "GTK focuses Back on opening the recipe")
        value = app.field(row, 487)
        assert value["readonly"] and f"{NS}::Fiber × {count}" in value["text"]

    def focus_link():
        for _ in range(4):
            focus = app.state()["focus"]
            if focus == 498:
                return
            if focus == 487:
                app.key(487, 0xFF09)
            else:
                ui.key(app.window, 0xFF09)
            app.wait(lambda row: row["focus"] != focus, "Advance focus in the recipe window", timeout=5)
        assert app.state()["focus"] == 498

    try:
        app.launch(build["run"])
        ui.resize(ui.display, app.window, 1080, 760)
        ui.flush(ui.display)
        app.wait(lambda row: (row["width"], row["height"]) == (1080, 760), "Resize isolated GTK")
        open_project(app, alpha)
        saved = source_view(app, identifier) + "// Existing independent draft for the View.\n"
        app.fill(54, saved)
        app.click(58)
        app.wait(lambda row: not row["job"] and bool(snapshots(alpha)), "Save an independent draft")
        target = NS + "::Assembly"

        for project, count in ((alpha, 2), (bravo, 7)):
            before = snapshots(project)
            recipe(count)
            focus_link()
            ui.key(app.window, 0xFF0D)
            row = app.wait(
                lambda row: not row["job"] and row["focus"] == 74 and not row["model"]["shell"]["menu"]
                and row["model"]["workspace"]["selected"] == target and row["model"]["workspace"].get("schemaView"),
                "Enter opens the existing properties editor and restores project focus",
            )
            selected = row["model"]["workspace"]["unit"]
            assert row["model"]["selected"]["path"] == project["path"]
            assert selected["text"] == Path(project["path"]).with_name("Assembly.celem").read_text()
            assert not app.field(row, 487).get("visible") and snapshots(project) == before
            assert all(path.read_bytes() == data for path, data in originals.items())
            if project == alpha:
                close_project(app)
                open_project(app, bravo)

        recipe(7)
        focus_link()
        before = snapshots(bravo)
        manifest = Path(bravo["path"])
        # Simulate an external registration change to the disposable Bravo fixture.
        manifest.write_text(manifest.read_text().replace('element Assembly object "Assembly.celem";\n', ""))
        originals[manifest] = manifest.read_bytes()
        ui.key(app.window, 0xFF0D)
        denied = app.wait(lambda row: not row["job"] and row["message"] == "This project window is no longer available."
                          and row["focus"] == 498, "Revoked target does not open the editor")
        assert denied["model"]["shell"]["menu"] == "project" and app.field(denied, 487)["readonly"]
        assert snapshots(bravo) == before
        app.click(481)
        app.wait(lambda row: row["focus"] == 484 and not app.field(row, 487).get("visible"),
                 "Back returns to the original Project windows row")
        app.close()
    finally:
        if hasattr(app, "child") and app.child.poll() is None:
            app.child.terminate()
            app.child.wait(timeout=15)
        if hasattr(app, "stream") and not app.stream.closed:
            app.stream.close()

    assert not proof.exists()
    assert all(path.read_bytes() == data for path, data in originals.items())
    print("PASS GTK recipe editor link: same-ID isolation, Tab/Enter focus, unchanged source/drafts, stale target and Back")


if __name__ == "__main__":
    prefix = "project-owned-view-" if "--worker-opening-review" in sys.argv[2:] else "gtk-project-windows-"
    root = Path(mkdtemp(prefix=prefix, dir=os.environ.get("TMPDIR")))
    package = Path(sys.argv[1]).resolve()
    if "--worker-opening-review" in sys.argv[2:]:
        workflow_worker_opening_review(package, root)
    elif "--recipe-editor" in sys.argv[2:]:
        workflow_recipe_editor(package, root)
    elif "--recipe-view" in sys.argv[2:]:
        workflow_recipe_view(package, root)
    elif "--opening-view" in sys.argv[2:]:
        workflow_opening_view(package, root)
    elif len(sys.argv) > 2 and sys.argv[2] == "--revocation":
        reader_package = Path(sys.argv[3]).resolve() if len(sys.argv) > 3 else package
        workflow_window_revocation(package, root, reader_package)
    else:
        scenario = workflow_menu_setting if "--menu-setting" in sys.argv[2:] else workflow
        scenario(package, root)
