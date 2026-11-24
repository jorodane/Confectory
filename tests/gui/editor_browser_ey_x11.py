#!/usr/bin/env python3
"""Local semantic browser EY and LaY in the installed Linux GTK package."""

import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

from editor_create_lay_x11 import double_box, drag_region, pixels
from editor_home_project_display_x11 import close_project, gtk
from editor_lan_chat_x11 import ui
from editor_local_ey_x11 import OBJECT, box, finish, package_files, seed
from editor_local_multilay_x11 import check_image, saved
from editor_project_browser_scope_x11 import gtk_open_project_browser

NS = "Recent.Alpha"
MODULE = f"{NS}::Twin"
FOREIGN = "Library::Twin"
FUNCTION = f"{NS}::LocalAction"
CONCEPT = f"{NS}::LocalConcept"
CATEGORY = f"{NS}::LocalFolder"
UNREGISTERED = f"{NS}::PendingObject"


def projects_with_semantics(package, root):
    projects, originals = seed(package, root)
    library = root / "library"
    library.mkdir()
    registry = library / "pack.cpack"
    registry.write_text('pack Library version "1" { element Twin module "entry.celem"; }')
    (library / "entry.celem").write_text(f'module {FOREIGN} {{ description "Registered elsewhere"; }}')
    for project in projects:
        title = project["title"]
        manifest = Path(project["path"])
        declarations = ""
        for kind, identifier, source in (
            ("module", MODULE, f'module {MODULE} {{ description "{title} owned Twin"; }}'),
            ("function", FUNCTION, f'function {FUNCTION} () -> int {{ description "{title} function"; }}'),
            ("concept", CONCEPT, f'concept {CONCEPT} {{ description "{title} concept"; }}'),
            ("category", CATEGORY, f'category {CATEGORY} {{ }}'),
        ):
            name = identifier.split("::")[-1]
            filename = f"declaration-{name}.celem"
            path = manifest.with_name(filename)
            path.write_text(source)
            originals[path] = path.read_bytes()
            declarations += f'element {name} {kind} "{filename}"; '
        if title == "Alpha":
            declarations += f'registry Library {json.dumps(str(registry))}; dependency Library version "1";'
        manifest.write_text(manifest.read_text().rstrip()[:-1] + declarations + "}")
        originals[manifest] = manifest.read_bytes()
    originals.update({path: path.read_bytes() for path in library.iterdir()})
    return projects, originals


def search(app, group, label):
    app.click(group)
    app.fill(77, label)
    app.click(78)
    return app.wait(lambda row: (row.get("nativeTreeState") or {}).get("query") == label
                    and not row["job"], f"GTK results for {label}")


def bounds_for(state, key):
    rows = state["nativeTree"]["rows"]
    index = next(i for i, node in enumerate(rows) if node["key"] == key)
    offset = min(state["nativeTreeState"]["offset"], len(rows) - 1)
    hit = state["hits"][::5].index(210 + index - offset) * 5
    return state["hits"][hit + 1:hit + 5]


def begin_browser_capture(app):
    ui.key(app.window, "y", (0xFFE3,))
    app.wait(lambda state: state["laySelecting"], "GTK browser Ctrl+Y")


def click_row(app, bounds):
    x, y, _, height = bounds
    ui.click(app.window, x + 14, y + height // 2)


def return_to_browser(app):
    app.click(471)
    return app.wait(lambda state: state["screen"] == "project" and state.get("nativeTree"), "Back in browser")


def open_project(app, project):
    cards = app.state()["model"]["cards"]
    index = next(i for i, card in enumerate(cards) if card["path"] == project["path"])
    app.click(100 + 3 * index)
    app.wait(lambda state: state["screen"] == "project"
             and state["model"]["selected"]["path"] == project["path"] and not state["job"],
             "Open project from Home")
    gtk_open_project_browser(app)


def workflow(package, root):
    (alpha, bravo), originals = projects_with_semantics(package, root)
    with gtk(package, root, "installed-browser-ey") as app:
        ui.resize(ui.display, app.window, 1500, 1120)
        ui.flush(ui.display)
        app.wait(lambda row: row["width"] == 1500 and row["height"] == 1120, "GTK browser rows fit")
        open_project(app, alpha)
        state = search(app, 203, "Twin")
        owner = bounds_for(state, "decl:" + MODULE)
        twins = {row["key"]: row for row in state["nativeTree"]["rows"] if row["label"] == "Twin"}
        assert set(twins) == {"decl:" + MODULE, "decl:" + FOREIGN}
        assert not twins["decl:" + FOREIGN]["row"]["owned"]

        # Without capture mode a real row click changes the normal browser selection.
        click_row(app, owner)
        state = app.wait(lambda row: row["nativeTreeState"]["selection"] == "decl:" + MODULE,
                         "Normal row selection")
        assert not package_files(alpha["path"])
        unit = state["model"]["workspace"]["selected"]
        foreign = bounds_for(state, "decl:" + FOREIGN)
        begin_browser_capture(app)
        click_row(app, foreign)
        state = app.wait(lambda row: not row["laySelecting"], "Registered foreign row ignored")
        assert state["nativeTreeState"]["selection"] == "decl:" + MODULE
        assert not package_files(alpha["path"])

        begin_browser_capture(app)
        click_row(app, owner)
        state = finish(app, 1)
        assert state["model"]["workspace"]["selected"] == unit
        file, = package_files(alpha["path"])
        item, = saved(file)["items"]
        assert (item["id"], item["elementKind"], item["metadata"]["description"]) == (MODULE, "module", "Alpha owned Twin")
        assert return_to_browser(app)["nativeTreeState"]["selection"] == "decl:" + MODULE

        for count, (group, identifier, kind) in enumerate(
                ((202, FUNCTION, "function"), (201, CONCEPT, "concept"), (201, OBJECT, "object")), 2):
            state = search(app, group, identifier.split("::")[-1])
            bounds = bounds_for(state, "decl:" + identifier)
            before_selection = app.state()["nativeTreeState"]["selection"]
            begin_browser_capture(app)
            click_row(app, bounds)
            state = finish(app, count)
            assert state["model"]["workspace"]["selected"] == unit
            item = saved(file)["items"][-1]
            assert item["kind"] == "semantic" and (item["id"], item["elementKind"]) == (identifier, kind)
            assert return_to_browser(app)["nativeTreeState"]["selection"] == before_selection

        state = search(app, 76, "LocalFolder")
        category = bounds_for(state, "decl:" + CATEGORY)
        before = file.read_bytes()
        selection = state["nativeTreeState"]["selection"]
        for target in (category, bounds_for(state, "root")):
            begin_browser_capture(app)
            click_row(app, target)
            state = app.wait(lambda row: not row["laySelecting"], "Non-semantic container ignored")
            assert state["nativeTreeState"]["selection"] == selection
        x, y, _, height = category
        begin_browser_capture(app)
        ui.click(app.window, x + 14, y + height + 1)
        app.wait(lambda row: not row["laySelecting"], "Empty browser space ignored")
        assert file.read_bytes() == before

        state = search(app, 203, "Twin")
        x, y, _, _ = bounds_for(state, "decl:" + MODULE)
        crop = [x + 10, y + 5, 41, 12]
        original_pixels = pixels(app, crop)
        begin_browser_capture(app)
        drag_region(app, crop)
        finish(app, 5)
        check_image(saved(file)["items"][-1], crop, original_pixels)
        app.fill(473, "Browser selections stay local")
        app.click(474)
        box(app, lambda row: row["model"]["yogi"]["sealed"])
        return_to_browser(app)
        sealed = file.read_bytes()
        double_box(app)
        row = finish(app, 5)
        assert row["model"]["yogi"]["sealed"] and row["model"]["yogi"]["text"] == "Browser selections stay local"
        assert [item.get("id") for item in row["model"]["yogi"]["items"]] == [MODULE, FUNCTION, CONCEPT, OBJECT, None]
        assert file.read_bytes() == sealed
        return_to_browser(app)
        close_project(app)

        open_project(app, bravo)
        assert not package_files(bravo["path"])
        app.fill(84, UNREGISTERED)
        app.click(86)
        app.wait(lambda row: row["model"]["workspace"]["selected"] == UNREGISTERED and not row["job"],
                 "Unconfirmed browser declaration")
        app.click(87)
        app.wait(lambda row: row["operation"] == "native-tree" and not row["job"], "Read tree containing the draft")
        state = search(app, 201, "PendingObject")
        pending = bounds_for(state, "decl:" + UNREGISTERED)
        begin_browser_capture(app)
        click_row(app, pending)
        app.wait(lambda row: not row["laySelecting"], "Unregistered row ignored")
        assert not package_files(bravo["path"])

        state = search(app, 203, "Twin")
        begin_browser_capture(app)
        click_row(app, bounds_for(state, "decl:" + MODULE))
        finish(app, 1)
        other, = package_files(bravo["path"])
        item, = saved(other)["items"]
        assert item["id"] == MODULE and item["metadata"]["description"] == "Bravo owned Twin"
        assert file.read_bytes() == sealed
    assert all(path.read_bytes() == data for path, data in originals.items())
    for project in (alpha, bravo):
        directory = Path(project["path"]).parent
        assert {path for path in directory.iterdir() if path.is_file()} == {
            path for path in originals if path.parent == directory
        }
    assert all(not (root / "profile" / name).exists() for name in ("project-chat", "helper-conversations"))
    print("PASS packaged GTK browser row EY for four kinds, foreign/category/draft rejection, LaY, sealed reopen and exact project isolation")


if __name__ == "__main__":
    with TemporaryDirectory(prefix="browser-native-ey-") as path:
        workflow(Path(sys.argv[1]).resolve(), Path(path))
