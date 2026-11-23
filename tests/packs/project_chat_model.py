"""Build and run the optional project-chat pack in two separate local .NET processes."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

repo = Path(__file__).resolve().parents[2]
tool_repo = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else repo
cli = tool_repo / "src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll"
dotnet = os.environ.get("CONFECTORY_DOTNET") or shutil.which("dotnet")
assert dotnet and cli.is_file(), "Build the Release CLI and .NET target or pass their checkout"
env = os.environ.copy()
env["PATH"] = str(Path(dotnet).resolve().parent) + os.pathsep + env["PATH"]

def run(command, **variables):
    return subprocess.run(command, env={**env, **variables}, capture_output=True, text=True, timeout=120)

with tempfile.TemporaryDirectory(prefix="confectory-project-chat-") as directory:
    root = Path(directory)
    # Stage optional packs separately so builds cannot alter the source checkout.
    shutil.copytree(repo / "packs/project-chat", root / "chat")
    shutil.copytree(repo / "packs/file-stream", root / "files")
    shutil.copy(repo / "tests/fixtures/project-chat/Main.csbody", root / "Main.csbody")
    manifest = root / "project.cpack"
    manifest.write_text(f'''project Test.ProjectChat version "0.1.0" {{
standalone true;
entry Test.ProjectChat::Main;
registry Confectory.ProjectChat "chat/pack.cpack";
dependency Confectory.ProjectChat version "0.1.0";
registry Confectory.FileStream "files/pack.cpack";
dependency Confectory.FileStream version "0.1.0";
registry Confectory.Build.DotNet "{(tool_repo / 'targets/dotnet/pack.cpack').as_posix()}";
dependency Confectory.Build.DotNet version "0.1.0";
target portable Confectory.Build.DotNet::Portable;
element Main function "Main.celem";
element MainBody implementation "MainBody.celem";
}}
''')
    (root / "Main.celem").write_text('''function Test.ProjectChat::Main () -> int {
provide Test.ProjectChat::Main with Test.ProjectChat::MainBody;
}
''')
    (root / "MainBody.celem").write_text('''implementation Test.ProjectChat::MainBody for Test.ProjectChat::Main () -> int {
import Confectory.ProjectChat::OpenHost as Open (string,string,string) -> object;
body common "Main.csbody";
}
''')
    (root / "host-home").mkdir()
    (root / "other-home").mkdir()

    built = run([dotnet, str(cli), "build", str(manifest), "portable"])
    assert built.returncode == 0, built.stdout[-6000:] + built.stderr[-3000:]
    report = json.loads(built.stdout)
    assert "Confectory.ProjectChat" in report["includedPacks"]
    assert "Confectory.MultiPlay" not in report["includedPacks"]
    for phase in ("first", "restart"):
        result = run(report["run"], CONFECTORY_CHAT_FIXTURE=str(root), CONFECTORY_CHAT_PHASE=phase)
        print(result.stdout, end="", flush=True)
        assert result.returncode == 0, result.stderr
    assert list((root / "other-home").iterdir()) == []
    journals = list(root.glob("**/project-chat/*.json"))
    assert len(journals) == 2
    assert {path.parent.parent for path in journals} == {root / "host-home"}
    public = json.loads((root / "host-home/project-chat" / f"{100:032x}.json").read_text(encoding="utf-8"))
    assert [row["sender"] for row in public["messages"]] == ["host", "alice", "host", "alice", "host", "bob"]
    assert public["messages"][1]["text"] == "첫 번째 메시지\nwith a second line 🐉"
    assert not list(root.rglob("helper-conversations"))
    print("PASS only host-local project journals were written; no private Helper store or network pack")
