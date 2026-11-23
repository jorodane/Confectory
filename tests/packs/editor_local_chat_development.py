"""Exercise development invitations in two real editor processes and local Chromium contexts."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time

from playwright.sync_api import expect, sync_playwright

repo = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo / "tests/web"))
from editor_navigation import goto_editor

tool_repo = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else repo
dotnet = os.environ.get("CONFECTORY_DOTNET") or shutil.which("dotnet")
cli = tool_repo / "src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll"
assert dotnet and cli.is_file()
env = dict(os.environ, CONFECTORY_DOTNET=dotnet, PATH=str(Path(dotnet).parent) + os.pathsep + os.environ["PATH"])

seed_body = r'''
string root=Environment.GetEnvironmentVariable("CONFECTORY_DEV_TEST_ROOT")!;
string repo=Environment.GetEnvironmentVariable("CONFECTORY_EDITOR_REPO")!;
var result=new System.Text.Json.Nodes.JsonObject();
string projects=System.IO.Path.Combine(root,"projects");
System.IO.Directory.CreateDirectory(projects);
foreach(string title in new[]{"HostOwner","GuestWorkspace"}){
 string session=calls.CreateSession.Invoke(repo,System.IO.Path.Combine(root,title));
 try{
  var opened=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(session,"create",
   System.Text.Json.JsonSerializer.Serialize(new{title,directory=projects})))!;
  result[title]=opened["selected"]?["path"]?.DeepClone()??throw new InvalidOperationException("Fixture create failed");
 }finally{calls.CloseSession.Invoke(session);}
}
System.IO.File.WriteAllText(System.IO.Path.Combine(root,"fixture.json"),result.ToJsonString());
return 0;
'''


def build(manifest, target="linux"):
    result = subprocess.run([dotnet, str(cli), "build", str(manifest), target], capture_output=True,
                            text=True, timeout=240, env=env)
    assert result.returncode == 0, result.stdout[-5000:] + result.stderr[-5000:]
    return json.loads(result.stdout)


@contextmanager
def editor(command, checkout, storage, project, enabled):
    log = storage / f"editor-{Path(project).parent.name}-{'enabled' if enabled else 'disabled'}.log"
    with log.open("w") as output:
        process = subprocess.Popen(command, cwd=checkout, stdout=output, stderr=subprocess.STDOUT, start_new_session=True,
            env=dict(env, CONFECTORY_UI="web", CONFECTORY_WEB_PROJECT=project, CONFECTORY_WEB_PORT="0",
                     CONFECTORY_EDITOR_REPO=str(checkout), CONFECTORY_HOME_STORAGE=str(storage),
                     CONFECTORY_ENTRY_STORAGE=str(storage), CONFECTORY_MCP_DIRECTORY=str(storage / "instances"),
                     CONFECTORY_DEV_PUBLIC_CHAT_LOOPBACK="1" if enabled else "0"))
        try:
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                for line in log.read_text().splitlines():
                    if line.startswith("CONFECTORY_WEB_UI "):
                        yield line.split(" ", 1)[1], log
                        return
                assert process.poll() is None, "Editor startup failed"
                time.sleep(0.05)
            raise AssertionError("Editor startup timed out")
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=20)


def route_page(browser, url, calls, send_attempts, drop_ack=None):
    context = browser.new_context(viewport={"width": 1440, "height": 1000})
    page = context.new_page()
    origin = url.split("/#")[0]

    def handle(route):
        if not route.request.url.startswith(origin + "/"):
            route.abort()
            return
        if route.request.method == "POST" and route.request.url.endswith("/api/request"):
            request = route.request.post_data_json
            if request.get("endpoint") == "localChatDevelopment":
                data = request.get("input", {})
                calls.append((request.get("op"), data.get("action")))
                if data.get("action") == "send":
                    send_attempts.append((data["text"], data["id"]))
                    if drop_ack is not None and data["text"] in drop_ack:
                        reply = route.fetch()
                        if reply.json().get("result", {}).get("status") == "committed":
                            drop_ack.remove(data["text"])
                            route.abort()
                        else:
                            route.fulfill(response=reply)
                        return
        route.continue_()

    page.route("**/*", handle)
    goto_editor(page, url)
    return context, page


def menu(page, name):
    page.locator("#title").click()
    page.locator(".context-menu").get_by_role("button", name=name, exact=True).click()


def issue(page):
    menu(page, "로컬 채팅 초대")
    panel = page.get_by_role("dialog", name="로컬 채팅 초대", exact=True)
    panel.get_by_role("button", name="일회용 초대 발급", exact=True).click()
    expect(panel.get_by_role("button", name="초대 텍스트 선택")).to_be_visible(timeout=15000)
    field = panel.get_by_label("일회용 초대")
    card = field.input_value()
    assert set(json.loads(card)) == {"version", "port", "project", "certificate", "code"}
    assert json.loads(card)["code"] not in field.evaluate("element => element.outerHTML")
    return panel, card


def open_join(page, home=False):
    if home:
        page.get_by_role("button", name="로컬 초대 참가", exact=True).click()
    else:
        menu(page, "로컬 초대 참가")
    return page.get_by_role("dialog", name="로컬 초대 참가", exact=True)


def join(panel, card):
    panel.get_by_label("일회용 초대").fill(card)
    panel.get_by_label("참가 이름").fill("테스트 참가자")
    panel.get_by_role("button", name="참가", exact=True).click()


def composer(page, name):
    return page.get_by_role("form", name=name, exact=True)


def send(form, text):
    form.get_by_label("공용 메시지 입력").fill(text)
    form.get_by_role("button", name="공용으로 보내기", exact=True).click()
    expect(form.get_by_label("공용 메시지 입력")).to_have_value("")


with tempfile.TemporaryDirectory(prefix="confectory-dev-invite-") as temp:
    root = Path(temp)
    checkout = root / "checkout"
    home = checkout / "examples/editor-home"
    shutil.copytree(repo / "packs", checkout / "packs", ignore=shutil.ignore_patterns(".confectory"))
    shutil.copytree(repo / "examples/editor-home", home, ignore=shutil.ignore_patterns(".confectory"))
    (checkout / "targets").symlink_to(tool_repo / "targets", target_is_directory=True)
    manifest = home / "project.cpack"
    original = manifest.read_text()
    manifest.write_text(original.replace("entry Confectory.EditorHome::Main;", "entry Confectory.EditorHome::VerifyShell;"))
    (home / "VerifyShell.csbody").write_text(seed_body)
    seed = subprocess.run(build(manifest)["run"], capture_output=True, timeout=90,
        env=dict(env, CONFECTORY_DEV_TEST_ROOT=str(root), CONFECTORY_EDITOR_REPO=str(checkout)))
    assert seed.returncode == 0, seed.stderr.decode()
    projects = json.loads((root / "fixture.json").read_text())
    manifest.write_text(original)
    command = build(manifest)["run"]
    known_codes = []
    calls = []
    send_attempts = []
    drop_ack = set()
    host_storage, guest_storage = [root / name for name in ("HostOwner", "GuestWorkspace")]
    sentinels = {}
    for storage in (host_storage, guest_storage):
        private = storage / "helper-conversations/fixture.json"
        private.parent.mkdir(exist_ok=True)
        private.write_bytes(b'{"private":"fixture"}\n')
        sentinels[private] = private.read_bytes()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
        try:
            with editor(command, checkout, host_storage, projects["HostOwner"], True) as (host_url, host_log), \
                 editor(command, checkout, guest_storage, projects["GuestWorkspace"], True) as (guest_url, guest_log):
                hc, host_page = route_page(browser, host_url, calls, send_attempts)
                gc, guest_page = route_page(browser, guest_url, calls, send_attempts, drop_ack)
                try:
                    host_page.locator("#chat").click()
                    host_form = composer(host_page, "호스트 공용 채팅")
                    expect(host_form).to_have_count(0)
                    host_panel, first = issue(host_page)
                    known_codes.append(json.loads(first)["code"])
                    send(host_form, "이전 공용 기록")
                    host_history = host_page.locator("[data-public-chat-rows]")
                    expect(host_history).to_contain_text("이전 공용 기록")

                    guest_page.locator("#chat").click()
                    draft = guest_page.locator("#chat-input")
                    draft.fill("그대로 둘 Helper 작성 중 입력")
                    draft.press("Shift+Enter")
                    draft.press("End")
                    guest_page.keyboard.insert_text("다음 줄")
                    expect(draft).to_have_value("그대로 둘 Helper 작성 중 입력\n다음 줄")
                    guest_panel = open_join(guest_page)
                    broken = dict(json.loads(first), certificate="broken")
                    join(guest_panel, json.dumps(broken))
                    expect(guest_panel.locator("[data-local-chat-status]")).to_contain_text("연결할 수 없습니다")
                    expect(guest_panel.get_by_label("일회용 초대")).to_have_value("")
                    join(guest_panel, first)
                    expect(guest_panel.locator("[data-local-chat-status]")).to_have_text("새 메시지가 없습니다.")
                    expect(guest_panel).not_to_contain_text("이전 공용 기록")
                    guest_form = composer(guest_page, "참가 프로젝트 공용 채팅")
                    guest_history = guest_panel.locator("[data-local-chat-messages]")
                    send(host_form, "참가 후 공용 한 줄")
                    expect(guest_history).to_contain_text("참가 후 공용 한 줄")
                    send(guest_form, "게스트가 보낸 공용 글")
                    expect(host_history).to_contain_text("게스트가 보낸 공용 글")
                    expect(guest_history).to_contain_text("게스트가 보낸 공용 글")
                    expect(draft).to_have_value("그대로 둘 Helper 작성 중 입력\n다음 줄")

                    journal, = (host_storage / "project-chat").glob("*.json")
                    original = journal.read_bytes()
                    mode = journal.stat().st_mode & 0o777
                    rejected = "저장 실패 뒤 다시 보낸 글"
                    journal.chmod(0o444)
                    try:
                        guest_form.get_by_label("공용 메시지 입력").fill(rejected)
                        guest_form.get_by_role("button", name="공용으로 보내기").click()
                        expect(guest_form.locator("[data-public-send-status]")).to_contain_text("저장이 거절")
                        expect(guest_form.get_by_label("공용 메시지 입력")).to_have_value(rejected)
                        expect(guest_history).not_to_contain_text(rejected)
                        assert journal.read_bytes() == original
                    finally:
                        journal.chmod(mode)
                    guest_form.get_by_role("button", name="공용으로 보내기").click()
                    expect(guest_form.get_by_label("공용 메시지 입력")).to_have_value("")
                    expect(host_history).to_contain_text(rejected)

                    uncertain = "응답을 받기 전에 끊긴 공용 글"
                    drop_ack.add(uncertain)
                    guest_form.get_by_label("공용 메시지 입력").fill(uncertain)
                    guest_form.get_by_role("button", name="공용으로 보내기").click()
                    expect(guest_form.locator("[data-public-send-status]")).to_contain_text("전송을 확인하지 못했습니다")
                    expect(guest_form.get_by_label("공용 메시지 입력")).to_have_value(uncertain)
                    expect(guest_history).to_contain_text(uncertain)
                    guest_form.get_by_role("button", name="공용으로 보내기").click()
                    expect(guest_form.get_by_label("공용 메시지 입력")).to_have_value("")
                    for retried in (rejected, uncertain):
                        ids = [value for text, value in send_attempts if text == retried]
                        assert len(ids) == 2 and ids[0] == ids[1]
                        assert sum(row["text"] == retried for row in json.loads(journal.read_text())["messages"]) == 1

                    guest_panel.get_by_role("button", name="닫기").click()
                    guest_panel = open_join(guest_page)
                    join(guest_panel, first)
                    expect(guest_panel.locator("[data-local-chat-status]")).to_contain_text("연결할 수 없습니다")
                    expect(guest_panel.get_by_label("일회용 초대")).to_have_value("")

                    host_panel.get_by_role("button", name="닫기").click()
                    host_panel, second = issue(host_page)
                    known_codes.append(json.loads(second)["code"])
                    join(guest_panel, second)
                    expect(guest_panel.locator("[data-local-chat-status]")).to_have_text("새 메시지가 없습니다.")
                    expect(guest_panel).not_to_contain_text("게스트가 보낸 공용 글")
                    menu(guest_page, "프로젝트 나가기")
                    expect(guest_page.locator(".home-grid")).to_be_visible()
                    expect(guest_panel).to_have_count(0)
                    host_panel.get_by_role("button", name="닫기").click()

                    host_panel, third = issue(host_page)
                    known_codes.append(json.loads(third)["code"])
                    guest_panel = open_join(guest_page, home=True)
                    join(guest_panel, third)
                    expect(guest_panel.locator("[data-local-chat-status]")).to_have_text("새 메시지가 없습니다.")
                    send(host_form, "재참가 뒤 공용 글")
                    expect(guest_panel.locator("[data-local-chat-messages]")).to_contain_text("재참가 뒤 공용 글")
                    menu(host_page, "프로젝트 나가기")
                    expect(host_page.locator(".home-grid")).to_be_visible()
                    expect(host_panel).to_have_count(0)
                    expect(guest_panel.locator("[data-local-chat-status]")).to_contain_text("연결이 종료되었습니다")
                    expect(guest_panel.locator("[data-local-chat-messages]")).to_be_empty()
                    expect(guest_form.get_by_role("button", name="공용으로 보내기")).to_be_disabled()
                    expect(host_form).to_have_count(0)

                    for page in (host_page, guest_page):
                        visible = page.evaluate("""() => [location.href, document.documentElement.outerHTML,
                            JSON.stringify(localStorage), JSON.stringify(sessionStorage), JSON.stringify(history.state)].join(' ')""")
                        assert all(code not in visible for code in known_codes)
                finally:
                    hc.close()
                    gc.close()

            with editor(command, checkout, guest_storage, projects["HostOwner"], True) as (other_url, other_log):
                context, page = route_page(browser, other_url, calls, send_attempts)
                try:
                    menu(page, "로컬 채팅 초대")
                    panel = page.get_by_role("dialog", name="로컬 채팅 초대", exact=True)
                    panel.get_by_role("button", name="일회용 초대 발급", exact=True).click()
                    expect(panel.locator("[data-local-chat-status]")).to_contain_text("원본 프로젝트를 만든 호스트만")
                    expect(panel.get_by_label("일회용 초대")).to_have_value("")
                finally:
                    context.close()

            with editor(command, checkout, guest_storage, projects["GuestWorkspace"], False) as (disabled_url, disabled_log):
                context, page = route_page(browser, disabled_url, calls, send_attempts)
                try:
                    page.locator("#title").click()
                    expect(page.locator(".context-menu").get_by_role("button", name="로컬 채팅 초대")).to_have_count(0)
                    expect(page.locator(".context-menu").get_by_role("button", name="로컬 초대 참가")).to_have_count(0)
                finally:
                    context.close()

            assert calls and all(operation == "transient" for operation, _ in calls)
            assert {action for _, action in calls} == {"issue", "join", "read", "status", "send"}
            assert not (guest_storage / "project-chat").exists()
            journal, = (host_storage / "project-chat").glob("*.json")
            assert [row["text"] for row in json.loads(journal.read_text())["messages"]] == [
                "이전 공용 기록", "참가 후 공용 한 줄", "게스트가 보낸 공용 글",
                "저장 실패 뒤 다시 보낸 글", "응답을 받기 전에 끊긴 공용 글", "재참가 뒤 공용 글",
            ]
            for path in [journal, host_log, guest_log, other_log, disabled_log, *sentinels]:
                assert all(code.encode() not in path.read_bytes() for code in known_codes)
            assert all(path.read_bytes() == before for path, before in sentinels.items())
        finally:
            browser.close()
    print("PASS two Chromium editor sessions: UI text both ways, denied storage and lost acknowledgements, stable retries, cold rejoin, Helper isolation")
