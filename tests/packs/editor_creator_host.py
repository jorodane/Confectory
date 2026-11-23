"""Run real EditorHome create/open commands with separate Linux processes and profiles."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

repo = Path(__file__).resolve().parents[2]
tool_repo = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else repo
dotnet = os.environ.get("CONFECTORY_DOTNET") or shutil.which("dotnet")
cli = tool_repo / "src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll"
assert sys.platform == "linux", "This test requires the Linux creator provider"
assert dotnet and cli.is_file(), "Build the Release CLI and targets or pass their checkout"
env = dict(os.environ, CONFECTORY_DOTNET=dotnet,
           PATH=str(Path(dotnet).resolve().parent) + os.pathsep + os.environ["PATH"])


def run(command, **variables):
    return subprocess.run(command, env={**env, **variables}, capture_output=True, text=True, timeout=240)


with tempfile.TemporaryDirectory(prefix="confectory-creator-host-") as directory:
    root = Path(directory)
    checkout = root / "checkout"
    shutil.copytree(repo / "packs", checkout / "packs", ignore=shutil.ignore_patterns(".confectory"))
    home = checkout / "examples/editor-home"
    shutil.copytree(repo / "examples/editor-home", home, ignore=shutil.ignore_patterns(".confectory"))
    (checkout / "targets").symlink_to(tool_repo / "targets", target_is_directory=True)
    manifest = home / "project.cpack"
    manifest.write_text(manifest.read_text().replace(
        "entry Confectory.EditorHome::Main;", "entry Confectory.EditorHome::VerifyShell;"))
    body = home / "VerifyShellBody.celem"
    body.write_text(body.read_text().replace('body common "VerifyShell.csbody";', '''import Confectory.EditorHome.Model::CreatorHost as CreatorHost (string) -> bool;
import Confectory.ProjectManager::PlanCreation as PlanCreation (string,string) -> string[];
body common "CreatorHostFixture.csbody";'''))
    shutil.copyfile(repo / "tests/fixtures/editor-creator-host/Main.csbody", home / "CreatorHostFixture.csbody")
    built = run([dotnet, str(cli), "build", str(manifest), "linux"])
    assert built.returncode == 0, built.stdout[-8000:] + built.stderr[-5000:]
    report = json.loads(built.stdout)
    assert "Confectory.ProjectChat" not in report["includedPacks"]
    for phase in ("create", "restart"):
        result = run(report["run"], CONFECTORY_EDITOR_REPO=str(checkout),
                     CONFECTORY_CREATOR_TEST_ROOT=str(root), CONFECTORY_CREATOR_TEST_PHASE=phase)
        print(result.stdout, end="", flush=True)
        assert result.returncode == 0, result.stderr
    for data in ("creator-profile", "guest-profile", "projects"):
        assert not list((root / data).rglob("project-chat"))
    print("PASS creator proof remains local; no public chat journal or network adapter")
