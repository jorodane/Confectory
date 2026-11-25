#!/usr/bin/env python3
"""Local EditorHome build report + isolated X11: source draft, Review, Run, harvest."""
import json
import os
from pathlib import Path
import shutil
import sys
import time
from tempfile import TemporaryDirectory

from editor_lan_chat_x11 import eventually, native_windows, ui
from editor_local_multilay_x11 import LocalEditor, repo
from editor_project_windows_x11 import open_project, review, source_view
from editor_home_project_display_x11 import close_project

PLANT = "Example.HarvestGame::PowderPlant"
GAME_WINDOW = b"Confectory Harvest single"


def run_game(app, fixture, expected_count):
    assert app.state()["model"]["selected"]["path"] == fixture["path"]
    assert not native_windows(GAME_WINDOW), "Use a dedicated display without another harvest game"
    app.click(36)
    app.wait(lambda row: row["model"].get("execution", {}).get("state") in ("building", "running"),
             "Run starts for selected project")
    window, = eventually(lambda: native_windows(GAME_WINDOW), "The selected project Run mapped the game", timeout=150)

    def wait_log(event, feedback, count=1):
        def observed(row):
            logs = row["model"]["shell"]["logs"]
            start = max((index for index, line in enumerate(logs) if "Run requested" in line), default=None)
            if start is None:
                return False
            return sum(event in line and feedback in line for line in logs[start:]) >= count

        return app.wait(observed, f"Game reports {feedback}", timeout=15)

    ui.key(window, "h")
    wait_log("harvest-applied", "Harvested Powder.")
    ui.key(window, "c")
    if expected_count == 1:
        wait_log("craft-rejected", "Missing: Powder 1")
        eventually(lambda: native_windows(GAME_WINDOW), "Game remains available")
        # The declared growth period is observed through the ordinary game loop.
        time.sleep(.4)
        ui.key(window, "h")
        wait_log("harvest-applied", "Harvested Powder.", count=2)
        ui.key(window, "c")
    wait_log("craft-applied", "Crafted Bomb.")
    ui.key(window, 0xFF1B)
    closed = app.wait(lambda row: (row["model"].get("execution") or {}).get("state") == "exited",
                      "Game exits through its normal close path", timeout=30)
    assert closed["model"]["selected"]["path"] == fixture["path"]
    assert str(closed["model"]["execution"]["exit"]) == "0"
    assert not native_windows(GAME_WINDOW)
    print(f'PASS {fixture["title"]}: craft requires {2 if expected_count == 1 else 1} harvest(s)', flush=True)


def workflow(report, root):
    assert not native_windows(GAME_WINDOW), "Dedicated display required"
    app = LocalEditor(root)
    fixtures = []
    for name in ("Alpha", "Bravo"):
        project = root / name
        shutil.copytree(repo / "examples/projects/harvest-game", project,
                        ignore=shutil.ignore_patterns(".confectory", ".build"))
        manifest = project / "project.cpack"
        manifest.write_text(manifest.read_text().replace("../../../packs/", str(repo / "packs") + "/")
                            .replace("../../../targets/", str(repo / "targets") + "/"))
        fixtures.append({"path": str(manifest), "title": f"Local harvest {name}", "description": ""})
    alpha, bravo = fixtures
    (app.profile / "projects.json").write_text(json.dumps(fixtures))
    bravo_root = Path(bravo["path"]).parent
    bravo_sources = {path: path.read_bytes() for path in bravo_root.iterdir() if path.is_file()}
    # The ordinary Run must derive the sample path from its working directory.
    # LocalEditor uses env key=value and otherwise inherits the parent environment.
    assert "CONFECTORY_GAME_PROJECT" not in os.environ, "Unset CONFECTORY_GAME_PROJECT before this test"
    assert "CONFECTORY_GAME_PROJECT" not in app.env
    app.env.pop("CONFECTORY_GAME_MODE", None)
    app.env.pop("CONFECTORY_COMPARISON_INPUT", None)
    app.env.pop("CONFECTORY_GAME_CLOSE_MS", None)
    plant = Path(alpha["path"]).with_name("PowderPlant.celem")
    before = plant.read_bytes()
    build = json.loads(report.read_text())
    try:
        app.launch(build["run"])
        open_project(app, alpha)
        source = source_view(app, PLANT)
        proposed = source.replace("value yield = 2;", "value yield = 1;")
        assert proposed != source
        app.fill(54, proposed)
        app.click(58)
        app.wait(lambda row: not row["job"] and row["model"]["workspace"]["unit"]["text"] == proposed,
                 "Save only the draft")
        review(app)
        app.click(66)
        app.wait(lambda row: not row["job"] and row["model"]["workspace"]["review"] is None,
                 "Cancel Review")
        assert plant.read_bytes() == before
        run_game(app, alpha, 2)
        review(app)
        app.click(65)
        app.wait(lambda row: not row["job"] and plant.read_text() == proposed,
                 "Confirm the selected plant source", timeout=150)
        run_game(app, alpha, 1)
        assert all(path.read_bytes() == value for path, value in bravo_sources.items())
        close_project(app)
        open_project(app, bravo)
        assert source_view(app, PLANT) == before.decode()
        run_game(app, bravo, 2)
        close_project(app)
        app.close()

        app.launch(build["run"])
        open_project(app, alpha)
        assert source_view(app, PLANT) == proposed
        run_game(app, alpha, 1)
        assert plant.read_text() == proposed
        assert all(path.read_bytes() == value for path, value in bravo_sources.items())
        app.close()
    finally:
        for window in native_windows(GAME_WINDOW):
            ui.key(window, 0xFF1B)
        if hasattr(app, "child") and app.child.poll() is None:
            app.child.terminate()
            app.child.wait(timeout=15)
        if hasattr(app, "stream") and not app.stream.closed:
            app.stream.close()


if __name__ == "__main__":
    with TemporaryDirectory(prefix="harvest-editor-roundtrip-") as directory:
        workflow(Path(sys.argv[1]).resolve(), Path(directory))
    print("PASS native editor draft/cancel, isolated Confirm, project switches and restart Run")
