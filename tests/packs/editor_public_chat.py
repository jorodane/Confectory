"""Exercise the actual EditorHome WebUI observation using disposable native journals."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import urllib.request
import uuid

from playwright.sync_api import sync_playwright

repo = Path(__file__).resolve().parents[2]
tools = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else repo
dotnet = os.environ.get("CONFECTORY_DOTNET") or shutil.which("dotnet")
cli = tools / "src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll"
endpoint = "readPublicChatHistory"
assert dotnet and cli.is_file(), "Build the Release CLI and targets or pass their checkout"
env = dict(os.environ, CONFECTORY_DOTNET=dotnet,
           PATH=str(Path(dotnet).resolve().parent) + os.pathsep + os.environ["PATH"])


def build(manifest):
    built = subprocess.run([dotnet, str(cli), "build", str(manifest), "linux"], env=env,
                           capture_output=True, text=True, timeout=240)
    assert built.returncode == 0, built.stdout[-5000:] + built.stderr[-5000:]
    return json.loads(built.stdout)["run"]


class Editor:
    def __init__(self, url):
        self.url = url
        self.origin, self.token = url.split("/#")

    def request(self, body):
        req = urllib.request.Request(self.origin + "/api/request", data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json", "X-Confectory-Session": self.token})
        with urllib.request.urlopen(req, timeout=30) as reply:
            return json.load(reply)

    def mount(self):
        for _ in range(300):
            mounted = self.request({"op": "mount"})
            if mounted["ok"]:
                return mounted
            assert mounted["error"]["code"] == "busy", mounted
            time.sleep(.01)
        raise AssertionError("Editor could not mount")

    def observe(self, mounted, payload=None):
        return self.request({"op": "observe", "view": mounted["view"], "scope": mounted["scope"],
                             "endpoint": endpoint, "input": payload or {}})

    def change(self, action, payload, project):
        for _ in range(8):
            view = self.mount()
            rid = uuid.uuid4().hex
            frame = {"view": view["view"], "scope": view["scope"]}
            try:
                begun = self.request({"op": "invoke", **frame, "endpoint": action, "input": payload,
                                      "requestId": rid, "expectedRevision": view["revision"]})
                assert begun["ok"], begun
                for _ in range(600):
                    reply = self.request({"op": "update", **frame})
                    if reply.get("error", {}).get("code") == "scope_changed":
                        opened = self.mount()
                        assert opened["state"]["projectId"] == project
                        return opened
                    row = next((r for r in reply.get("results", []) if r["requestId"] == rid), None)
                    if row is not None:
                        assert row.get("error", {}).get("code") == "stale_revision", row
                        break
                    time.sleep(.01)
                else:
                    raise AssertionError("Transition did not finish")
            finally:
                self.request({"op": "dispose", "view": view["view"]})
        raise AssertionError("Repeated editor transition conflicts")


@contextmanager
def host(command, checkout, profile, manifest):
    with tempfile.TemporaryFile(mode="w+t") as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
                                   cwd=checkout, env=dict(env, CONFECTORY_UI="web",
                                   CONFECTORY_EDITOR_REPO=str(checkout), CONFECTORY_WEB_PROJECT=str(manifest),
                                   CONFECTORY_HOME_STORAGE=str(profile), CONFECTORY_ENTRY_STORAGE=str(profile),
                                   CONFECTORY_MCP_DIRECTORY=str(profile / "instances")))
        try:
            for _ in range(600):
                log.seek(0)
                text = log.read()
                urls = [line.split(" ", 1)[1] for line in text.splitlines() if line.startswith("CONFECTORY_WEB_UI ")]
                if urls:
                    yield Editor(urls[-1])
                    return
                assert process.poll() is None, text[-3000:]
                time.sleep(.05)
            raise AssertionError("Editor startup timeout")
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=20)


def assert_message(reply, mounted, title, attachment=False):
    assert reply["ok"], reply
    result = reply["result"]
    assert result["status"] == "available" and result["projectActivation"] == mounted["scope"]["projectActivation"], result
    row, = result["messages"]
    assert set(row) == ({"id", "sender", "text", "attachmentId"} if attachment else {"id", "sender", "text"}), row
    assert row["text"] == title + " public message" and row["sender"] == "local-user", row
    if attachment:
        assert row["attachmentId"] == row["id"]


def delayed_observation(page, url):
    # Hold a real, completed server reply before delivering it to the shipped WebView.
    page.goto(url)
    arrived = page.evaluate("""async () => {
        const {connectLocal, WebView} = await import('/web-ui.js');
        const send = connectLocal();
        let reportReply;
        const arrived = new Promise(resolve => { reportReply = resolve; });
        const gate = new Promise(resolve => { window.releaseChatReply = resolve; });
        window.chatView = new WebView(async (request, options) => {
            const reply = await send(request, options);
            if (request.endpoint === 'readPublicChatHistory' && !window.chatReplyHeld && reply.ok) {
                window.chatReplyHeld = true;
                reportReply(reply.result);
                await gate;
            }
            return reply;
        });
        window.mountChatView = async () => {
            for (let attempt = 0;; attempt++) {
                try { return await chatView.mount(); }
                catch (error) {
                    if (error.message !== 'busy' || attempt === 15) throw error;
                    await new Promise(resolve => setTimeout(resolve, 25));
                }
            }
        };
        await mountChatView();
        window.chatResult = chatView.observe('readPublicChatHistory').then(
            value => ({ value }), error => ({ error: error.message }));
        return await Promise.race([arrived, chatResult]);
    }""")
    assert arrived["messages"][0]["text"] == "AuthorA public message", arrived


with tempfile.TemporaryDirectory(prefix="confectory-editor-public-chat-") as directory:
    root = Path(directory)
    checkout = root / "checkout"
    home = checkout / "examples/editor-home"
    shutil.copytree(repo / "packs", checkout / "packs", ignore=shutil.ignore_patterns(".confectory"))
    shutil.copytree(repo / "examples/editor-home", home, ignore=shutil.ignore_patterns(".confectory"))
    (checkout / "targets").symlink_to(tools / "targets", target_is_directory=True)
    manifest = home / "project.cpack"
    original = manifest.read_text()
    manifest.write_text(original.replace("entry Confectory.EditorHome::Main;", "entry Confectory.EditorHome::VerifyShell;"))
    body = home / "VerifyShellBody.celem"
    body.write_text(body.read_text().replace('body common "VerifyShell.csbody";', '''\
import Confectory.ProjectChat::OpenHostWithAttachments as OpenHost (string,string,string,string) -> object;
import Confectory.EditWorkspace::Open as OpenWorkspace (string,string,string) -> string;
import Confectory.YogiBox::Open as OpenBox (string,string,string,string) -> string;
import Confectory.YogiBox::Text as Text (string,string) -> void;
import Confectory.YogiBox::Seal as Seal (string,bool) -> void;
body common "PublicChatFixture.csbody";'''))
    shutil.copyfile(repo / "tests/fixtures/editor-public-chat/Main.csbody", home / "PublicChatFixture.csbody")
    seed = subprocess.run(build(manifest), capture_output=True, text=True, timeout=90,
                          env=dict(env, CONFECTORY_EDITOR_REPO=str(checkout), CONFECTORY_CHAT_TEST_ROOT=str(root)))
    assert seed.returncode == 0, seed.stdout + seed.stderr
    manifest.write_text(original)
    command = build(manifest)
    fixtures = json.loads((root / "fixtures.json").read_text())
    a, b, empty = [fixtures[name] for name in ("AuthorA", "AuthorB", "Empty")]
    profile, copy_profile, empty_profile = [root / name for name in ("profile", "copy-profile", "empty-profile")]

    # Same OS display name, same journal and copied receipt, but a separate profile and a fresh editor session.
    shutil.copytree(profile, copy_profile)
    replica = root / "replica"
    shutil.copytree(Path(a["manifest"]).parent, replica)
    replica_manifest = replica / "project.cproj"
    identity = replica / ".confectory/project-identity.json"
    proof = json.loads(identity.read_text())
    identity.write_text(json.dumps(dict(proof, manifest=str(replica_manifest), role="host")))
    catalog = profile / "projects.json"
    catalog.write_text(json.dumps(json.loads(catalog.read_text()) +
                                 [{"path": str(replica_manifest), "title": "AuthorA", "description": ""}]))

    private = profile / "helper-conversations/fixture.json"
    private.parent.mkdir(exist_ok=True)
    private.write_text('{"unchanged":"personal Helper data"}\n')
    protected = {path: path.read_bytes() for path in [private, *profile.glob("project-chat/*.json")]}
    unavailable = {"status": "unavailable"}

    with host(command, checkout, empty_profile, empty["manifest"]) as editor:
        view = editor.mount()
        assert editor.observe(view)["result"]["messages"] == []
        assert not (empty_profile / "project-chat").exists()
        home_view = editor.change("leaveProject", {}, "")
        assert editor.observe(home_view)["result"] == unavailable
    with host(command, checkout, copy_profile, a["manifest"]) as editor:
        assert editor.observe(editor.mount())["result"] == unavailable
    print("PASS no journal on read, Home denied, and exact copies of a journal/receipt denied in another profile", flush=True)

    with host(command, checkout, profile, a["manifest"]) as editor:
        first = editor.mount()
        assert_message(editor.observe(first), first, "AuthorA", attachment=True)
        for key in ("role", "projectId", "path", "user"):
            assert not editor.observe(first, {key: "forged"})["ok"]

        def open_project(path, project_id):
            listing = hashlib.sha256(str(path).encode()).hexdigest()[:32].upper()
            return editor.change("openProject", {"id": listing}, project_id)

        editor.change("leaveProject", {}, "")
        copied = open_project(replica_manifest, a["id"])
        assert editor.observe(copied)["result"] == unavailable
        assert editor.observe(first)["error"]["code"] == "scope_changed"
        editor.change("leaveProject", {}, "")
        again = open_project(a["manifest"], a["id"])
        assert editor.observe(first)["error"]["code"] == "scope_changed"
        assert_message(editor.observe(again), again, "AuthorA", attachment=True)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
            page = browser.new_page()
            page.route("**/*", lambda route: route.continue_()
                       if route.request.url.startswith(editor.origin + "/") else route.abort())
            delayed_observation(page, editor.url)
            editor.change("leaveProject", {}, "")
            second = open_project(b["manifest"], b["id"])
            result = page.evaluate("""async () => {
                const update = await chatView.update().then(() => 'still_active', error => error.message);
                await chatView.dispose();
                await mountChatView();
                releaseChatReply();
                return { update, held: await chatResult, current: await chatView.observe('readPublicChatHistory') };
            }""")
            assert result["update"] == "scope_changed" and result["held"] == {"error": "view_closed"}, result
            assert_message({"ok": True, "result": result["current"]}, second, "AuthorB")
            browser.close()
        assert_message(editor.observe(second), second, "AuthorB")
        assert editor.observe(again)["error"]["code"] == "scope_changed"
        receipt = profile / "project-creators" / (b["id"] + ".json")
        receipt.rename(receipt.with_suffix(".withheld"))
        assert editor.observe(second)["result"] == unavailable

    assert all(path.read_bytes() == original for path, original in protected.items())
    print("PASS cold read/v1/v2, stale A→copy→A, delayed Chromium reply on A→B, live proof withdrawal, private/journal bytes unchanged")
