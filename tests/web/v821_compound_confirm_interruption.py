"""Run compound Confirm interruption checks in a temporary instrumented Linux editor.

Requires a .NET 10 SDK, Playwright/Chromium, and the Release CLI, .NET target,
element-authoring, and project-execution outputs of the checkout. Pass an optional checkout path.
"""
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory


def run(checkout):
    dotnet = os.environ.get("CONFECTORY_DOTNET") or shutil.which("dotnet")
    assert dotnet, "A local .NET 10 SDK is required"
    env = dict(os.environ, CONFECTORY_DOTNET=dotnet, PYTHONDONTWRITEBYTECODE="1")
    with TemporaryDirectory(prefix="confectory-confirm-interruption-") as tmp:
        root = Path(tmp)
        fixture = root / "editor"
        # Copy tracked sources only. In particular, no live projects, caches or
        # user profiles from the checkout are copied into the instrumented editor.
        paths = subprocess.check_output(["git", "ls-files", "-z"], cwd=checkout).split(b"\0")
        for name in filter(None, paths):
            relative = Path(os.fsdecode(name))
            destination = fixture / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(checkout / relative, destination, follow_symlinks=False)
        for directory in ("src/Confectory.Cli", "targets/dotnet", "targets/element-authoring",
                          "targets/project-execution-host"):
            shutil.copytree(checkout / directory / "bin", fixture / directory / "bin")

        source = fixture / "packs/change-set/ConfirmReviewed.csbody"
        text = source.read_text()
        before = " var result=checks.Count>0||reads.Count>0?calls.CommitPlan"
        after = 'if(result[0]!="applied")return result;committed=true;'
        assert text.count(before) == text.count(after) == 1, "Confirm publication boundary changed"
        stop = 'if(Environment.GetEnvironmentVariable("CONFECTORY_TEST_CONFIRM_STOP")'
        text = text.replace(before, f' {stop}=="before")Environment.Exit(71);\n{before}')
        text = text.replace(after, f'{after}{stop}=="after")Environment.Exit(72);')
        source.write_text(text)

        report = root / "editor.json"
        with report.open("w") as output:
            subprocess.run([dotnet, str(fixture / "src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll"),
                            "build", "examples/editor-home/project.cpack", "linux"], cwd=fixture,
                           env=env, stdout=output, check=True)
        ui_test = Path(__file__).with_name("v821_cell_removal_history_ui.py")
        for point in ("before", "after", "after-restore", "unverified"):
            subprocess.run([sys.executable, str(ui_test), str(fixture), str(report),
                            "compound-confirm-interruption", point], env=env, check=True)


if __name__ == "__main__":
    checkout = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
    run(checkout)
