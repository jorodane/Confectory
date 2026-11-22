"""Exercise Chat/Logs and the latest log against two real isolated projects."""
import json
import time
import uuid

from playwright.sync_api import expect, sync_playwright

from project_chat_contract import OwnedChat
import v666_workspace_finder_fixture as fixture

MESSAGE = "CHAT_ONLY_Approved_Local_Message"
REPLY = "OWNED project-chat REPLY"
DRAFT_A = "FIRST_Unsent_Chat_Draft"
DRAFT_B = "SECOND_Unsent_Chat_Draft"
LABELS = ("First Log Fixture", "Second Log Fixture")
MARKERS = ("FIRST_RUN_LAST_LINE", "SECOND_RUN_LAST_LINE")


def seed():
    for manifest, marker in zip(fixture.projects, MARKERS):
        body = manifest.parent / "Main.csbody"
        body.write_text(f'System.Console.WriteLine("{marker}_previous");\n'
                        f'System.Console.WriteLine("{marker}");\nreturn 0;\n')
        fixture.before[str(body)] = body.read_bytes()
    profile = fixture.root / "profile"
    profile.mkdir()
    (profile / "projects.json").write_text(json.dumps([
        {"path": str(project), "title": title, "description": ""}
        for project, title in zip(fixture.projects, LABELS)
    ]))


def wait_state(page, predicate, timeout=25):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        state = fixture.state()
        if predicate(state):
            return state
        page.wait_for_timeout(75)
    raise AssertionError((state.get("aiState"), state.get("executionState"), state["logs"]))


def add_helper(page, owned):
    page.locator("#add-agent").click()
    dialog = page.get_by_role("dialog", name="Agent 추가", exact=True)
    dialog.get_by_role("button", name="OpenAI Responses", exact=True).click()
    for field, value in (("model", "chat-log-loopback"), ("endpoint", owned.endpoint),
                         ("credentialReference", "")):
        dialog.locator(f'[data-connection-field="{field}"]').fill(value)
    dialog.locator("[data-agent-register]").click()
    expect(dialog.locator("[data-agent-registration-state]")).to_contain_text("Agent 등록됨")
    dialog.locator("[data-connection-cancel]").click()
    helper = fixture.call("helperGlobal", {
        "action": "create", "creationId": uuid.uuid4().hex, "name": "Local test Helper",
        "personality": "Test profile", "speciality": "Test profile",
        "agent": "Confectory.Agent.Responses::Connection",
    })["helper"]
    page.locator("#add-helper").click()
    placement = page.get_by_role("dialog", name="프로젝트 도우미 배치", exact=True)
    placement.locator(f'[data-project-helper="{helper}"]').click()
    placement.locator('button[type="submit"]').click()
    expect(placement).to_have_count(0)


def send_chat(page, owned):
    page.locator("#chat-input").fill(MESSAGE)
    page.locator("#chat-prepare").click()
    approval = page.locator('.window[data-key="ai-preview"]')
    expect(approval.locator("#ai-start")).to_be_disabled()
    assert not owned.requests
    for permission in ("contentApproved", "usageApproved"):
        approval.locator(f'[data-permission="{permission}"]').check()
    approval.locator("#ai-start").click()
    expect(page.locator("#chat-output")).to_have_text(REPLY, timeout=30000)
    assert len(owned.requests) == 1 and not owned.errors
    assert owned.requests[0]["message"] == MESSAGE


def run_event(page, marker):
    # Use the existing ProjectPack execution endpoint feeding the ProjectShell
    # logs, while leaving the separate dock Run-window tests to their suite.
    fixture.call("runProject", {"target": "linux"})
    wait_state(page, lambda state: marker in "\n".join(state["logs"]).splitlines(), timeout=90)
    return wait_state(page, lambda state: state["executionState"] == "exited", timeout=20)


def logs_tab(page):
    page.locator("#logs-tab").click()
    expect(page.locator("#chat-inner")).to_be_hidden()
    expect(page.locator("#execution-logs")).to_be_visible()
    return page.locator("#execution-logs")


def chat_tab(page, draft):
    page.locator("#chat").click()
    expect(page.locator("#execution-logs")).to_be_hidden()
    expect(page.locator("#chat-input")).to_have_value(draft)
    expect(page.locator("#chat-input")).to_be_visible()


def enter(page, title):
    page.locator(".brand").click()
    expect(page.locator(".home-grid")).to_be_visible()
    page.locator(".project-card").filter(has=page.get_by_role("heading", name=title, exact=True)).locator("[data-enter]").click()
    expect(page.locator("#title")).to_contain_text(title)


def assert_log_excludes(logs, *strings):
    for text in strings:
        expect(logs).not_to_contain_text(text)


def latest_line(logs):
    return next(line.strip() for row in reversed(logs) for line in reversed(row.splitlines()) if line.strip())


def assert_latest(page, state):
    line = page.locator("#chat-form + #chat-latest-log")
    expect(line).to_be_visible()
    expect(line).to_have_text(latest_line(state["logs"]))
    assert len(line.text_content().splitlines()) == 1
    assert line.evaluate("node => getComputedStyle(node).whiteSpace") == "nowrap"
    composer = page.locator("#chat-input").bounding_box()
    assert line.bounding_box()["y"] >= composer["y"] + composer["height"]


def exercise(page, owned):
    add_helper(page, owned)
    send_chat(page, owned)
    page.locator("#chat-input").fill(DRAFT_A)
    logs = logs_tab(page)
    assert_log_excludes(logs, DRAFT_A, MESSAGE, REPLY)
    chat_tab(page, DRAFT_A)
    expect(page.locator("#chat-output")).to_have_text(REPLY)
    fixture.checked("Chat·Logs 전환이 보낸 대화와 미전송 초안을 로그로 섞지 않으며 초안을 보존한다")

    previous = fixture.state()
    assert_latest(page, previous)
    a = run_event(page, MARKERS[0])
    assert latest_line(a["logs"]) != latest_line(previous["logs"])
    assert_latest(page, a)
    logs = logs_tab(page)
    expect(logs).to_contain_text(MARKERS[0])
    assert_log_excludes(logs, MARKERS[1], DRAFT_A, MESSAGE, REPLY)
    chat_tab(page, DRAFT_A)
    fixture.checked("첫 프로젝트의 실제 실행 이벤트가 로그에 들어오며 채팅 내용은 제외된다")
    assert_latest(page, a)

    enter(page, LABELS[1])
    chat_tab(page, "")
    assert_latest(page, fixture.state())
    assert_log_excludes(page.locator("#chat-latest-log"), MARKERS[0], DRAFT_A, MESSAGE, REPLY)
    page.locator("#chat-input").fill(DRAFT_B)
    logs = logs_tab(page)
    assert_log_excludes(logs, MARKERS[0], DRAFT_A, MESSAGE, REPLY)
    b = run_event(page, MARKERS[1])
    assert b["projectId"] != a["projectId"]
    expect(logs).to_contain_text(MARKERS[1])
    assert_log_excludes(logs, MARKERS[0], DRAFT_A, DRAFT_B, MESSAGE, REPLY)
    chat_tab(page, DRAFT_B)
    assert_latest(page, b)
    fixture.checked("로그 탭을 보고 있을 때 새 실행 이벤트가 와도 현재 프로젝트의 최신 한 줄만 채팅 아래에 표시된다")

    enter(page, LABELS[0])
    chat_tab(page, DRAFT_A)
    a_again = fixture.state()
    assert a_again["projectId"] == a["projectId"]
    assert_latest(page, a_again)
    logs = logs_tab(page)
    expect(logs).to_contain_text(MARKERS[0])
    assert_log_excludes(logs, MARKERS[1], DRAFT_B, MESSAGE, REPLY)
    assert len(owned.requests) == 1 and not owned.errors
    assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
    fixture.original()
    fixture.checked("두 프로젝트를 왕복해도 초안·대화·실행 로그의 기존 범위가 유지된다")


if __name__ == "__main__":
    seed()
    owner = OwnedChat()
    try:
        fixture.start(0)
        with sync_playwright() as playwright:
            with playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
                page = fixture.setup(browser)
                exercise(page, owner)
    finally:
        fixture.stop()
        owner.close()
        fixture.save_evidence()
        print("evidence:", fixture.root)
