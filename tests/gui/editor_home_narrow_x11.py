#!/usr/bin/env python3
"""Run the narrow Home keyboard and project-menu regression on a dedicated X11 display."""

import hashlib
import json
from pathlib import Path
import sys
import tempfile

from editor_create_lay_x11 import pixels
from editor_lan_chat_x11 import display, repo, ui
from editor_local_multilay_x11 import LocalEditor


def fixture(root, profile):
    cards = []
    target = repo / "targets/dotnet/pack.cpack"
    for title in ("Alpha", "Bravo"):
        project = root / title
        project.mkdir()
        manifest = project / "project.cproj"
        namespace = f"NarrowHome.{title}"
        (project / "Main.celem").write_text(
            f"function {namespace}::Main () -> int {{ provide {namespace}::Main with {namespace}::MainBody; }}",
            encoding="utf-8",
        )
        (project / "MainBody.celem").write_text(
            f'implementation {namespace}::MainBody for {namespace}::Main () -> int {{ body common "Main.csbody"; }}',
            encoding="utf-8",
        )
        (project / "Main.csbody").write_text("return 0;\n", encoding="utf-8")
        manifest.write_text(
            f"""project {namespace} version "1.0.0" {{
standalone true;
registry Confectory.Build.DotNet {json.dumps(str(target))};
dependency Confectory.Build.DotNet version "0.1.0";
target linux Confectory.Build.DotNet::Linux;
entry {namespace}::Main;
element Main function "Main.celem";
element MainBody implementation "MainBody.celem";
}}
""",
            encoding="utf-8",
        )
        cards.append({"path": str(manifest), "title": title, "description": f"{title} fixture"})
    (profile / "projects.json").write_text(json.dumps(cards), encoding="utf-8")

    # A persisted edit makes Bravo render before Alpha while keeping Bravo at catalog index 1.
    bravo = cards[1]["path"]
    key = hashlib.sha256(bravo.encode()).hexdigest()
    activity = Path(bravo).parent / ".confectory/project-activity"
    activity.mkdir(parents=True)
    (activity / f"{key}.json").write_text(json.dumps({
        "version": 1, "manifest": bravo, "projectId": "", "sequence": 1, "kind": "save",
        "at": "2025-01-01T00:00:00.0000000+00:00", "scope": "persisted-source-edit",
    }), encoding="utf-8")
    return bravo


def narrow_workflow(editor, bravo):
    def bounds(row, control):
        first = row["hits"][::5].index(control) * 5 + 1
        return row["hits"][first:first + 4]

    ui.resize(display, editor.window, 440, 920)
    ui.flush(display)
    home = editor.wait(
        lambda row: row["screen"] == "home" and row["width"] == 440 and row["height"] == 920
        and not row["job"] and len(row["model"].get("homeActivity", {})) == 2
        and {2, 500, 501, 103}.issubset(row["hits"][::5]),
        "Narrow GTK Home with both synthetic project cards",
    )
    assert [card["title"] for card in home["model"]["cards"]] == ["Alpha", "Bravo"]
    assert bounds(home, 2)[1] < bounds(home, 501)[1] < bounds(home, 500)[1]
    assert bounds(home, 501)[0] == bounds(home, 500)[0]
    assert home["focus"] != 103
    x, y, _, _ = bounds(home, 103)
    unfocused = pixels(editor, (x + 2, y + 2, 1, 1))

    state = home
    for _ in range(len(home["hits"][::5])):
        previous = state["focus"]
        ui.key(editor.window, 0xFF09)
        state = editor.wait(lambda row: row["focus"] != previous, "Tab advances Home focus", timeout=5)
        if state["focus"] == 103:
            break
    assert state["focus"] == 103, "Tab must reach Bravo's Open button"
    assert pixels(editor, (x + 2, y + 2, 1, 1)) != unfocused, "Bravo's Open button must visibly highlight"
    ui.key(editor.window, 0xFF09, (0xFFE1,))
    editor.wait(lambda row: row["focus"] == 501, "Shift+Tab returns to Bravo's Info button", timeout=5)
    ui.key(editor.window, 0xFF09)
    editor.wait(lambda row: row["focus"] == 103, "Tab returns to Bravo's Open button", timeout=5)
    ui.key(editor.window, 0xFF0D)
    opened = editor.wait(
        lambda row: row["screen"] == "project" and not row["job"] and 33 in row["hits"][::5],
        "Keyboard opens the selected project",
    )
    assert opened["model"]["selected"]["path"] == bravo
    print("PASS visible Tab focus, reverse Tab and Enter open the highlighted project", flush=True)

    editor.click(33)
    editor.wait(
        lambda row: row["screen"] == "project" and row["width"] == 440
        and row["model"]["shell"]["menu"] == "project" and 52 in row["hits"][::5],
        "Project menu opens with a Close project action at narrow width",
    )
    editor.click(52)
    closed = editor.wait(
        lambda row: row["screen"] == "home" or row["model"].get("closeRequest"),
        "Closing from the narrow project menu leaves the editor alive",
    )
    if closed["screen"] != "home":
        editor.click(65)
    editor.wait(lambda row: row["screen"] == "home" and not row["job"], "Editor returns to Home")
    print("PASS narrow project menu opens and closes the project without terminating the editor", flush=True)


def main(report_path):
    report = json.loads(Path(report_path).read_text(encoding="utf-8"))
    assert report["target"] == "linux" and report["tool"]["ok"], "Successful Linux EditorHome build required"
    with tempfile.TemporaryDirectory(prefix="cf-native-narrow-home-") as directory:
        root = Path(directory)
        editor = LocalEditor(root)
        bravo = fixture(root, editor.profile)
        try:
            editor.launch(report["run"])
            narrow_workflow(editor, bravo)
            editor.close()
        except Exception:
            if editor.log.exists():
                log = editor.log.read_text(encoding="utf-8").splitlines()
                print("\n".join(line for line in log if not line.startswith("HOME_UI ")), file=sys.stderr)
            raise
        finally:
            if hasattr(editor, "child") and editor.child.poll() is None:
                editor.child.terminate()
                editor.child.wait(timeout=15)
            if hasattr(editor, "stream") and not editor.stream.closed:
                editor.stream.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 tests/gui/editor_home_narrow_x11.py LINUX_BUILD_REPORT")
    main(sys.argv[1])
