"""Exercise ordinary PackWorkspace Save with independent local editor processes."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
from selectors import DefaultSelector, EVENT_READ
import shutil
import subprocess
import sys
import tempfile


ENTRY = r'''
string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_SAVE_PROJECT")!;
string owner=calls.Open.Invoke(project,"save-probe","editor");
try{
    while(Console.ReadLine() is string input){
        var request=System.Text.Json.Nodes.JsonNode.Parse(input)!;
        try{
            Console.WriteLine(calls.Command.Invoke(owner,request["operation"]!.ToString(),
                request["input"]?.ToJsonString()??"{}"));
        }catch(InvalidOperationException error){
            Console.WriteLine(System.Text.Json.JsonSerializer.Serialize(new{error=error.Message}));
        }
    }
    return 0;
}finally{calls.Close.Invoke(owner);}
'''


def build_probe(repo, root, dotnet, env):
    probe = root / "probe"
    probe.mkdir()
    example = repo / "examples/edit-workspace"
    for name in ("project.cpack", "main.celem"):
        shutil.copyfile(example / name, probe / name)
    manifest = probe / "project.cpack"
    text = manifest.read_text()
    text = text.replace("../../packs/", (repo / "packs").as_posix() + "/")
    text = text.replace("../../targets/dotnet/pack.cpack", (repo / "targets/dotnet/pack.cpack").as_posix())
    manifest.write_text(text.replace("element Main function", f"""
registry Confectory.PackWorkspace {json.dumps(str(repo / "packs/pack-workspace/pack.cpack"))};
dependency Confectory.PackWorkspace version "0.1.0";
element Main function"""))
    (probe / "main_body.celem").write_text("""
implementation Example.EditWorkspace::MainBody for Example.EditWorkspace::Main () -> int {
 import Confectory.PackWorkspace::Open as Open (string,string,string) -> string;
 import Confectory.PackWorkspace::Command as Command (string,string,string) -> string;
 import Confectory.PackWorkspace::Close as Close (string) -> void;
 body common "main.csbody";
}
""")
    (probe / "main.csbody").write_text(ENTRY)
    result = subprocess.run([dotnet, str(repo / "src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll"),
                             "build", str(manifest), "portable"], cwd=probe, env=env,
                            capture_output=True, text=True, timeout=250)
    assert result.returncode == 0, result.stdout[-6000:] + result.stderr[-6000:]
    return json.loads(result.stdout)["run"]


@contextmanager
def editor(command, root, env, name):
    log_path = root / (name + ".log")
    with (log_path.open("w") as log,
          subprocess.Popen(command, cwd=root, env=env, stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, stderr=log, text=True) as process,
          DefaultSelector() as output):
        output.register(process.stdout, EVENT_READ)

        def call(operation, **payload):
            process.stdin.write(json.dumps({"operation": operation, "input": payload}) + "\n")
            process.stdin.flush()
            assert output.select(timeout=45), (operation, log_path.read_text())
            line = process.stdout.readline()
            assert line, (operation, log_path.read_text())
            return json.loads(line)

        try:
            yield call
        finally:
            process.stdin.close()
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def exercise(repo, root, dotnet):
    project = root / "owned"
    project.mkdir()
    manifest = project / "project.cproj"
    manifest.write_text('project SaveProbe version "1" { standalone true; element Alpha object "Alpha.celem"; element Bravo object "Bravo.celem"; }\n')
    originals = {}
    for name in ("Alpha", "Bravo"):
        path = project / (name + ".celem")
        path.write_text(f'object SaveProbe::{name} {{ description "original {name}"; }}\n')
        originals[path] = path.read_bytes()
    originals[manifest] = manifest.read_bytes()
    env = dict(os.environ, CONFECTORY_DOTNET=dotnet, CONFECTORY_TEST_SAVE_PROJECT=str(manifest),
               CONFECTORY_ELEMENT_AUTHORING_HOST=str(
                   repo / "targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll"))
    command = build_probe(repo, root, dotnet, env)

    def read(call, name):
        return call("select", id="SaveProbe::" + name)["unit"]

    def edit(call, name, text):
        selected = read(call, name)
        next_text = f'object SaveProbe::{name} {{ description "{text}"; }}'
        result = call("edit", expectedRevision=selected["revision"], text=next_text)
        assert not result["conflict"] and result["unit"]["text"] == next_text
        return next_text

    def save(call):
        result = call("save")
        assert "error" not in result, result

    def reject(call, selected, staged, checkpoint):
        before = checkpoint.read_bytes()
        result = call("save")
        assert "Checkpoint changed before Save" in result.get("error", ""), (
            "A stale window overwrote or accepted another editor's checkpoint",
            result.get("error", "Save succeeded"), checkpoint.read_bytes() == before)
        assert checkpoint.read_bytes() == before
        assert read(call, selected)["text"] == staged

    with editor(command, root, env, "first") as first, editor(command, root, env, "second") as second:
        draft = edit(first, "Alpha", "first unsaved input")
        edit(second, "Bravo", "second first save")
        save(second)
        checkpoint, = project.glob(".confectory/edit-workspaces/*/draft.json")
        assert json.loads(checkpoint.read_bytes())["changes"][0]["id"] == "SaveProbe::Bravo"
        reject(first, "Alpha", draft, checkpoint)
        reject(first, "Alpha", draft, checkpoint)
        saved = edit(second, "Bravo", "second consecutive save")
        save(second)
        save(second)

        with editor(command, root, env, "reopened") as reopened:
            assert read(reopened, "Bravo")["text"] == saved
            assert read(reopened, "Alpha")["text"] == originals[project / "Alpha.celem"].decode()
            other = edit(reopened, "Alpha", "fresh but pending local input")
            latest = edit(second, "Bravo", "second saved while reopened")
            save(second)
            reject(reopened, "Alpha", other, checkpoint)
            review = reopened("review", target="portable")
            assert "Checkpoint changed before Save" in review.get("error", ""), review
            assert read(reopened, "Alpha")["text"] == other

        with editor(command, root, env, "review-saved") as reopened:
            assert read(reopened, "Bravo")["text"] == latest
            assert read(reopened, "Alpha")["text"] == originals[project / "Alpha.celem"].decode()
        assert all(path.read_bytes() == contents for path, contents in originals.items())

    print("PASS ordinary Save prevents cross-process checkpoint overwrite and preserves both drafts")


if __name__ == "__main__":
    checkout = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
    dotnet = os.environ.get("CONFECTORY_DOTNET") or shutil.which("dotnet")
    assert dotnet, "A local .NET 10 SDK is required"
    with tempfile.TemporaryDirectory(prefix="cf-draft-save-probe-") as scratch:
        exercise(checkout, Path(scratch), dotnet)
