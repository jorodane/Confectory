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
    for name in ("yogi-box", "edit-workspace", "schema-editing"):
        shutil.copytree(repo / "packs" / name, root / name, ignore=shutil.ignore_patterns(".confectory"))
    shutil.copy(repo / "tests/fixtures/project-chat/Main.csbody", root / "Main.csbody")
    manifest = root / "project.cpack"
    manifest.write_text(f'''project Test.ProjectChat version "0.1.0" {{
standalone true;
entry Test.ProjectChat::Main;
registry Confectory.ProjectChat "chat/pack.cpack";
dependency Confectory.ProjectChat version "0.1.0";
registry Confectory.FileStream "files/pack.cpack";
dependency Confectory.FileStream version "0.1.0";
registry Confectory.YogiBox "yogi-box/pack.cpack";
dependency Confectory.YogiBox version "0.1.0";
registry Confectory.EditWorkspace "edit-workspace/pack.cpack";
dependency Confectory.EditWorkspace version "0.1.0";
registry Confectory.SchemaEditing "schema-editing/pack.cpack";
dependency Confectory.SchemaEditing version "0.1.0";
registry Confectory.Build.DotNet "{(tool_repo / 'targets/dotnet/pack.cpack').as_posix()}";
dependency Confectory.Build.DotNet version "0.1.0";
target portable Confectory.Build.DotNet::Portable;
element Main function "Main.celem";
element MainBody implementation "MainBody.celem";
}}
''')
    (root / "Main.celem").write_text('''function Test.ProjectChat::Main () -> int {
provide Test.ProjectChat::Main with Test.ProjectChat::MainBody;
description "synthetic metadata for the reference test";
provide Confectory.YogiBox::Open with Confectory.YogiBox::OpenBody;
provide Confectory.YogiBox::Save with Confectory.YogiBox::SaveBody;
provide Confectory.YogiBox::ValidateStorage with Confectory.YogiBox::ValidateStorageBody;
provide Confectory.YogiBox::Revalidate with Confectory.YogiBox::RevalidateBody;
provide Confectory.EditWorkspace::Open with Confectory.EditWorkspace::OpenBody;
provide Confectory.EditWorkspace::Identity with Confectory.EditWorkspace::IdentityBody;
provide Confectory.EditWorkspace::List with Confectory.EditWorkspace::ListBody;
provide Confectory.EditWorkspace::Read with Confectory.EditWorkspace::ReadBody;
provide Confectory.SchemaEditing::Call with Confectory.SchemaEditing::CallBody;
provide Confectory.SchemaEditing::Inspect with Confectory.SchemaEditing::InspectBody;
provide Confectory.FileStream::Snapshot with Confectory.FileStream::SnapshotBody;
provide Confectory.FileStream::BoundedSnapshot with Confectory.FileStream::BoundedSnapshotBody;
provide Confectory.FileStream::Commit with Confectory.FileStream::CommitBody;
provide Confectory.FileStream::LeasePath with Confectory.FileStream::LeasePathBody;
provide Confectory.FileStream::WriteAtomic with Confectory.FileStream::WriteAtomicBody;
}
''')
    (root / "MainBody.celem").write_text('''implementation Test.ProjectChat::MainBody for Test.ProjectChat::Main () -> int {
import Confectory.ProjectChat::OpenHostWithAttachments as Open (string,string,string,string) -> object;
import Confectory.ProjectChat::OpenHost as OpenText (string,string,string) -> object;
import Confectory.YogiBox::Create as CreateBox () -> string;
import Confectory.YogiBox::Open as OpenBox (string,string,string,string) -> string;
import Confectory.YogiBox::Snapshot as BoxSnapshot (string) -> string;
import Confectory.YogiBox::Save as SaveBox (string) -> void;
import Confectory.YogiBox::Exactly as Exactly (string,string,string[],string[]) -> void;
import Confectory.YogiBox::Text as SetDescription (string,string) -> void;
import Confectory.YogiBox::Seal as Seal (string,bool) -> void;
import Confectory.YogiBox::Handoff as LegacyHandoff (string,string) -> string;
import Confectory.YogiBox::ReserveCapture as Reserve (string,string,int,int,int,int,int) -> string;
import Confectory.YogiBox::CompleteCapture as Complete (string,string,string) -> bool;
import Confectory.EditWorkspace::Open as OpenWorkspace (string,string,string) -> string;
body common "Main.csbody";
}
''')
    mirror = root / "mirror"
    mirror.mkdir()
    (mirror / "project.cpack").write_text("""project Test.ProjectChat version "0.1.0" {
standalone false;
element Mirror function "Mirror.celem";
}
""")
    (mirror / "Mirror.celem").write_text("function Test.ProjectChat::Mirror () -> int {}\n")
    (root / "host-home").mkdir()
    (root / "other-home").mkdir()
    personal = root / "host-home/helper-conversations/fixture.json"
    personal.parent.mkdir()
    private_bytes = b'{"private":"existing local fixture"}\n'
    personal.write_bytes(private_bytes)
    authoring = tool_repo / "targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll"
    assert authoring.is_file(), "Build the Release element-authoring tool"
    origins = {path: path.read_bytes() for path in (manifest, root / "Main.celem", root / "MainBody.celem", root / "Main.csbody")}

    built = run([dotnet, str(cli), "build", str(manifest), "portable"])
    assert built.returncode == 0, built.stdout[-6000:] + built.stderr[-3000:]
    report = json.loads(built.stdout)
    assert "Confectory.ProjectChat" in report["includedPacks"]
    assert "Confectory.MultiPlay" not in report["includedPacks"]
    for phase in ("first", "restart"):
        result = run(report["run"], CONFECTORY_CHAT_FIXTURE=str(root), CONFECTORY_CHAT_PHASE=phase,
                     CONFECTORY_ELEMENT_AUTHORING_HOST=str(authoring), CONFECTORY_DOTNET=dotnet)
        assert all(path.read_bytes() == data for path, data in origins.items())
        assert personal.read_bytes() == private_bytes
        print(result.stdout, end="", flush=True)
        assert result.returncode == 0, result.stderr
    assert list((root / "other-home").iterdir()) == []
    journals = list(root.glob("**/project-chat/*.json"))
    assert len(journals) == 2
    assert {path.parent.parent for path in journals} == {root / "host-home"}
    public = json.loads((root / "host-home/project-chat" / f"{100:032x}.json").read_text(encoding="utf-8"))
    assert public["version"] == 2
    assert [row["sender"] for row in public["messages"]] == ["host", "alice", "host", "alice", "host", "bob"]
    assert public["messages"][1]["text"] == "첫 번째 메시지\nwith a second line 🐉"
    assert list(personal.parent.iterdir()) == [personal]
    assert [row["id"] for row in public["messages"] if "attachment" in row] == [f"{2:032x}", f"{4:032x}"]
    assert "synthetic metadata for the reference test" not in json.dumps(public)
    print("PASS only host-local messages own attachments; private Helper bytes and source unchanged; no network pack")
