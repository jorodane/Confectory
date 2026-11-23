"""Exercise the actual EditorHome WebUI observation using disposable native journals."""
from contextlib import contextmanager
import base64
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

from playwright.sync_api import expect, sync_playwright

repo = Path(__file__).resolve().parents[2]
tools = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else repo
dotnet = os.environ.get("CONFECTORY_DOTNET") or shutil.which("dotnet")
cli = tools / "src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll"
endpoint = "readPublicChatHistory"
attachment_endpoint = "readPublicChatAttachment"
description = "전송 당시 설명\nOriginal sealed description"
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

    def observe(self, mounted, payload=None, action=endpoint):
        return self.request({"op": "observe", "view": mounted["view"], "scope": mounted["scope"],
                             "endpoint": action, "input": payload or {}})

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
    return row


def delayed_observation(page, url, pair):
    # Hold a real, completed server reply before delivering it to the shipped WebView.
    page.goto(url)
    arrived = page.evaluate("""async pair => {
        const {connectLocal, WebView} = await import('/web-ui.js');
        const send = connectLocal();
        let reportReply;
        const arrived = new Promise(resolve => { reportReply = resolve; });
        const gate = new Promise(resolve => { window.releaseChatReply = resolve; });
        window.chatView = new WebView(async (request, options) => {
            const reply = await send(request, options);
            if (request.endpoint === 'readPublicChatAttachment' && !window.chatReplyHeld && reply.ok) {
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
        window.chatResult = chatView.observe('readPublicChatAttachment', pair).then(
            value => ({ value }), error => ({ error: error.message }));
        return await Promise.race([arrived, chatResult]);
    }""", pair)
    assert arrived["description"] == description, arrived


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
import Confectory.EditorHome::LocalPublicChat as LocalChat (string,string,string,string,string,string) -> string;
import Confectory.EditorHome::PublicChatHistory as ChatHistory (string,string,string,string,string) -> string;
import Confectory.EditWorkspace::Open as OpenWorkspace (string,string,string) -> string;
import Confectory.YogiBox::Open as OpenBox (string,string,string,string) -> string;
import Confectory.YogiBox::Text as Text (string,string) -> void;
import Confectory.YogiBox::Save as SaveBox (string) -> void;
import Confectory.YogiBox::Seal as Seal (string,bool) -> void;
import Confectory.YogiBox::Exactly as Exactly (string,string,string[],string[]) -> void;
import Confectory.YogiBox::ReserveCapture as Reserve (string,string,int,int,int,int,int) -> string;
import Confectory.YogiBox::CompleteCapture as Complete (string,string,string) -> bool;
body common "PublicChatFixture.csbody";'''))
    shutil.copyfile(repo / "tests/fixtures/editor-public-chat/Main.csbody", home / "PublicChatFixture.csbody")
    private = root / "profile/helper-conversations/fixture.json"
    private.parent.mkdir(parents=True)
    private_bytes = b'{"unchanged":"personal Helper data"}\n'
    private.write_bytes(private_bytes)
    private_before = set(private.parent.iterdir())
    seed = subprocess.run(build(manifest), capture_output=True, text=True, timeout=90,
                          env=dict(env, CONFECTORY_EDITOR_REPO=str(checkout), CONFECTORY_CHAT_TEST_ROOT=str(root)))
    assert seed.returncode == 0, seed.stdout + seed.stderr
    assert private.read_bytes() == private_bytes and set(private.parent.iterdir()) == private_before
    print(seed.stdout, end="", flush=True)
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

    a_journal = profile / "project-chat" / (a["id"] + ".json")
    message = json.loads(a_journal.read_text())["messages"][0]["id"]
    pair = {"messageId": message, "attachmentId": message}
    private_yogi, = Path(a["manifest"]).parent.glob(".confectory/yogi/package-*.json")
    protected = {path: path.read_bytes() for path in [private, private_yogi, *profile.glob("project-chat/*.json")]}
    unavailable = {"status": "unavailable"}

    def attachment(editor, view, query=pair):
        return editor.observe(view, query, attachment_endpoint)

    with host(command, checkout, empty_profile, empty["manifest"]) as editor:
        view = editor.mount()
        assert editor.observe(view)["result"]["messages"] == []
        assert attachment(editor, view)["result"] == unavailable
        assert not (empty_profile / "project-chat").exists()
        home_view = editor.change("leaveProject", {}, "")
        assert editor.observe(home_view)["result"] == unavailable
    with host(command, checkout, copy_profile, a["manifest"]) as editor:
        denied = editor.mount()
        assert editor.observe(denied)["result"] == unavailable
        assert attachment(editor, denied)["result"] == unavailable
    print("PASS no journal on read, Home denied, and exact copies of a journal/receipt denied in another profile", flush=True)

    with host(command, checkout, profile, a["manifest"]) as editor:
        first = editor.mount()
        assert_message(editor.observe(first), first, "AuthorA", attachment=True)
        metadata = attachment(editor, first)["result"]
        assert metadata["description"] == description and metadata["projectActivation"] == first["scope"]["projectActivation"]
        assert {row["id"] for row in metadata["items"] if row.get("availability") == "available"} == {
            "Project.AuthorA::Main", "Project.AuthorA::MainBody"}
        assert "pixels" not in json.dumps(metadata)
        for index, action in enumerate(("readPublicChatFirstImage", "readPublicChatSecondImage")):
            capture = editor.observe(first, pair, action)["result"]["capture"]
            pixels = base64.b64decode(capture["pixels"], validate=True)
            assert capture["width"] == capture["height"] == 512
            assert pixels == bytes([23 + index]) * (512 * 512 * 3)
            assert hashlib.sha256(pixels).hexdigest() == capture["hash"]

        for key in ("role", "projectId", "path", "user", "operation"):
            assert not editor.observe(first, {key: "forged"})["ok"]
            assert not attachment(editor, first, dict(pair, **{key: "forged"}))["ok"]
        assert attachment(editor, first, dict(pair, attachmentId=uuid.uuid4().hex))["result"] == unavailable
        assert attachment(editor, first, {"messageId": a["id"], "attachmentId": a["id"]})["result"] == unavailable

        # A cached workspace locator alone must not reopen an already removed declaration.
        body_path = Path(a["manifest"]).parent / "main_body.celem"
        moved_body = body_path.with_suffix(".withheld")
        body_path.rename(moved_body)
        try:
            items = attachment(editor, first)["result"]["items"]
            removed = next(row for row in items if row["item"] == metadata["items"][1]["item"])
            assert removed["availability"] == "unavailable" and "id" not in removed
        finally:
            moved_body.rename(body_path)

        def open_project(path, project_id):
            listing = hashlib.sha256(str(path).encode()).hexdigest()[:32].upper()
            return editor.change("openProject", {"id": listing}, project_id)

        editor.change("leaveProject", {}, "")
        copied = open_project(replica_manifest, a["id"])
        assert editor.observe(copied)["result"] == unavailable
        assert attachment(editor, copied)["result"] == unavailable
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
            page.goto(editor.url)
            later = page.locator('.welcome #later')
            if later.is_visible():
                later.click()
            rows = page.locator("[data-public-chat-rows]")
            expect(rows).to_contain_text("공용 · local-user", timeout=20000)
            expect(rows).to_contain_text("AuthorA public message")
            expect(page.locator("#chat-output")).not_to_contain_text("AuthorA public message")
            page.locator("#chat-input").fill("독립 Helper 작성 중")
            page.locator("#logs-tab").click()
            expect(rows).to_have_count(0)
            page.locator("#chat").click()
            expect(page.locator("#chat-input")).to_have_value("독립 Helper 작성 중")
            rows.get_by_role("button", name="YogiBox 보기").click()
            dialog = page.get_by_role("dialog", name="YogiBox 보기", exact=True)
            expect(dialog).to_contain_text("Original sealed description")
            expect(dialog.locator("textarea")).to_have_count(0)
            dialog.get_by_role("button", name="이미지 보기").first.click()
            canvas = dialog.locator("canvas")
            expect(canvas).to_be_visible()
            assert canvas.evaluate("node => Array.from(node.getContext('2d').getImageData(0, 0, 1, 1).data)") == [23, 23, 23, 255]

            # Qualifying EY uses the existing selection path, while the composer is left intact.
            dialog.get_by_role("button", name="Project.AuthorA::Main", exact=True).click()
            expect(dialog).to_have_count(0)
            for _ in range(120):
                selection = editor.mount()
                editor.request({"op": "dispose", "view": selection["view"]})
                if selection["state"]["draft"]["id"] == "Project.AuthorA::Main":
                    break
                page.wait_for_timeout(40)
            else:
                raise AssertionError(selection["state"]["draft"])
            expect(page.locator("#chat-input")).to_have_value("독립 Helper 작성 중")

            rows.get_by_role("button", name="YogiBox 보기").click()
            expect(dialog).to_contain_text("Original sealed description")
            proof_path = profile / "project-creators" / (a["id"] + ".json")
            hidden_proof = proof_path.with_suffix(".withheld")
            proof_path.rename(hidden_proof)
            try:
                expect(dialog).to_have_count(0, timeout=12000)
                expect(rows).to_have_count(0)
                assert attachment(editor, again)["result"] == unavailable
            finally:
                hidden_proof.rename(proof_path)

            delayed_observation(page, editor.url, pair)
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
            page.goto(editor.url)
            expect(rows).to_contain_text("AuthorB public message", timeout=20000)
            expect(rows).not_to_contain_text("AuthorA public message")
            expect(page.locator("#chat-output")).not_to_contain_text("AuthorB public message")
            browser.close()
        assert_message(editor.observe(second), second, "AuthorB")
        assert editor.observe(again)["error"]["code"] == "scope_changed"
        assert attachment(editor, second)["result"] == unavailable
        assert attachment(editor, again)["error"]["code"] == "scope_changed"
        receipt = profile / "project-creators" / (b["id"] + ".json")
        receipt.rename(receipt.with_suffix(".withheld"))
        assert editor.observe(second)["result"] == unavailable

    assert all(path.read_bytes() == original for path, original in protected.items())
    print("PASS cold v1/v2, exact ID pair and two maximum LaY captures, fresh EY deletion checking")
    print("PASS visible read-only YogiBox, existing EY navigation, Chat/Log and Helper draft, live revocation and stale reply retirement")
    print("PASS private YogiBox/Helper and public journal bytes unchanged")
