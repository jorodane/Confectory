"""Actual EditorHome with synthetic loopback messages. Global history is personal."""
import hashlib
import http.server
import json
import shutil
import threading
import uuid

from playwright.sync_api import expect, sync_playwright
import v666_workspace_finder_fixture as fixture


AGENT = "Confectory.Agent.Responses::Connection"
TITLE = "Same name chat project"
HELPER_LABEL = "Local boundary fixture"
PERSONAL = "independent synthetic private message"
PROJECT_MESSAGE = "synthetic project conversation, not private"
CANCELLED = "cancel this preparation without sending"
CREATION = uuid.uuid4().hex
HELPER = "helper-" + CREATION


class Provider:
    def __init__(self):
        self.requests = []
        self.errors = []
        self.release = threading.Event()
        owner = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                try:
                    assert self.path == "/responses" and self.headers.get("Authorization") is None
                    request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                    assert request["store"] is False
                    payload = json.loads(request["input"][0]["content"])
                    assert payload["projectId"] == payload["context"]["projectId"]
                    assert payload["context"]["helper"] == HELPER
                    owner.requests.append(payload)
                    if payload["kind"] == "helper-global-chat":
                        assert payload["message"] == PERSONAL
                        assert payload["projectId"] == "" and payload["context"]["membership"]["kind"] == "global"
                        assert owner.release.wait(25), "fixture did not release the response"
                    else:
                        assert payload["kind"] == "project-chat" and payload["projectId"]
                        assert payload["message"] == PROJECT_MESSAGE
                        if sum(row["kind"] == "project-chat" for row in owner.requests) == 1:
                            self.send_error(422, "synthetic rejection before completion")
                            return
                    body = json.dumps({
                        "status": "completed", "output": [{"type": "message", "role": "assistant", "content": [
                            {"type": "output_text", "text": "LOCAL FIXTURE: " + payload["message"]}
                        ]}]
                    }).encode()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                except Exception as error:
                    owner.errors.append(str(error))
                    self.send_error(500)

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.endpoint = f"http://127.0.0.1:{self.server.server_port}/responses"

    def close(self):
        self.release.set()
        self.server.shutdown()
        self.server.server_close()


class ChromiumProfile:
    """Keep the same Chromium profile across process restarts and origins."""
    def __init__(self, chromium):
        self.chromium = chromium

    def new_page(self, **options):
        self.context = self.chromium.launch_persistent_context(
            str(fixture.root / "chromium"), executable_path="/usr/bin/chromium",
            args=["--no-sandbox", "--disable-gpu", "--renderer-process-limit=2"],
            ignore_default_args=["--disable-dev-shm-usage"], **options,
        )
        return self.context.pages[0]

    def close(self):
        self.context.close()


def catalog(profile, project):
    profile.mkdir()
    (profile / "projects.json").write_text(json.dumps([
        {"path": str(project), "title": TITLE, "description": ""}
    ]))


def register(page, endpoint):
    page.locator("#add-agent").click()
    dialog = page.get_by_role("dialog", name="Agent 추가", exact=True)
    dialog.get_by_role("button", name="OpenAI Responses", exact=True).click()
    for field, value in (("model", "owned-chat-boundary"), ("endpoint", endpoint), ("credentialReference", "")):
        dialog.locator(f'[data-connection-field="{field}"]').fill(value)
    dialog.locator("[data-agent-register]").click()
    expect(dialog.locator("[data-agent-registration-state]")).to_contain_text("Agent 등록됨")
    dialog.locator("[data-connection-cancel]").click()
    expect(dialog).to_have_count(0)
    added = fixture.call("helperGlobal", {
        "action": "create", "creationId": CREATION, "name": HELPER_LABEL,
        "personality": "fixture", "speciality": "fixture", "agent": AGENT,
    })
    assert added["helper"] == HELPER


def home(page):
    if not page.locator(".home-grid").is_visible():
        page.locator(".brand").click()
    expect(page.locator(".home-grid")).to_be_visible(timeout=30000)


def enter_project(page):
    card = page.locator(".project-card").filter(has=page.get_by_role("heading", name=TITLE, exact=True))
    card.locator("[data-enter]").click()
    expect(page.locator("#title")).to_contain_text(TITLE, timeout=30000)


def global_chat(page):
    page.locator(f'.home-side [data-helper="{HELPER}"]').first.click()
    chat = page.locator(f'[data-global-helper="{HELPER}"]')
    expect(chat.locator("form")).to_be_visible()
    return chat


def project_review(page, text):
    page.locator("#chat-input").fill(text)
    page.locator("#chat-prepare").click()
    expect(page.locator("#ai-start")).to_be_disabled()
    for right in ("contentApproved", "usageApproved"):
        page.locator(f'[data-permission="{right}"]').check()
    expect(page.locator("#ai-start")).to_be_enabled()


def personal_journal(profile):
    name = hashlib.sha256(HELPER.encode()).hexdigest()
    return profile / "helper-conversations" / f"{name}.json"


profile = fixture.root / "profile"
catalog(profile, fixture.projects[0])
other_home = fixture.root / "second-profile"
catalog(other_home, fixture.projects[1])
journal = personal_journal(profile)
provider = Provider()

try:
    with sync_playwright() as playwright:
        browser = ChromiumProfile(playwright.chromium)
        fixture.start("first")
        first_origin = fixture.origin
        try:
            page = fixture.setup(browser)
            home(page)
            register(page, provider.endpoint)
            chat = global_chat(page)
            chat.locator("textarea").fill(PERSONAL)
            chat.locator("textarea").press("Enter")
            expect(chat.locator(".messages")).to_contain_text("응답을 기다리고 있어요")
            row = fixture.state()["helperAgents"]["turns"][HELPER]
            assert row["state"] == "running" and not row["answerReceived"]
            pending = json.loads(journal.read_bytes())["records"]
            assert len(pending) == 1 and pending[0]["state"] == "running"
            assert pending[0]["requestId"] == row["requestId"] and pending[0]["output"] == ""
            provider.release.set()
            expect(chat.locator(".messages")).to_contain_text("LOCAL FIXTURE: " + PERSONAL)
            expect(chat.locator("[data-global-send]")).to_have_text("보내기")
            saved = journal.read_bytes()
            records = json.loads(saved)["records"]
            assert [r["requestId"] for r in records] == [row["requestId"]]
            assert records[0]["state"] == "completed"
            fixture.checked("One personal record becomes completed only on real loopback response")

            page.locator(f'.participant-expanded-card[data-helper-id="{HELPER}"] [data-close]').click()
            enter_project(page)
            project_agents = fixture.state()["helperAgents"]
            assert not project_agents.get("turns") and project_agents.get("preview") is None, (
                "project snapshot contains a private conversation turn", list(project_agents["turns"])
            )
            assert project_agents["assignments"][HELPER] == AGENT
            fixture.checked("Default project snapshot omits private conversation turns and preserves Helper assignment")
            page.locator("#add-helper").click()
            placement = page.get_by_role("dialog", name="프로젝트 도우미 배치", exact=True)
            placement.locator(f'[data-project-helper="{HELPER}"]').click()
            placement.locator('button[type="submit"]').click()
            expect(placement).to_have_count(0)
            assert fixture.state()["mainHelperId"] == HELPER

            project_review(page, CANCELLED)
            page.locator("#cancel-preview").click()
            expect(page.locator("#ai-start")).to_have_count(0)
            assert len(provider.requests) == 1 and journal.read_bytes() == saved

            project_review(page, PROJECT_MESSAGE)
            page.locator("#ai-start").click()
            expect(page.locator("#ai-start")).to_have_count(0)
            for _ in range(300):
                if fixture.state().get("aiState") == "error":
                    break
                page.wait_for_timeout(100)
            else:
                raise AssertionError("The rejected synthetic request did not reach a terminal error")
            assert len(provider.requests) == 2 and journal.read_bytes() == saved
            project_review(page, PROJECT_MESSAGE)
            page.locator("#ai-start").click()
            messages = page.locator("#messages")
            expect(messages).to_contain_text("LOCAL FIXTURE: " + PROJECT_MESSAGE, timeout=30000)
            expect(messages).not_to_contain_text(PERSONAL)
            assert len(provider.requests) == 3 and journal.read_bytes() == saved
            fixture.checked("Project cancel, rejected send and explicit retry leave the private journal byte-identical")
        finally:
            browser.close()
            fixture.stop()

        fixture.start("cold")
        try:
            assert fixture.origin != first_origin
            page = fixture.setup(browser)
            expect(page.locator("#messages")).not_to_contain_text(PROJECT_MESSAGE)
            home(page)
            chat = global_chat(page)
            expect(chat.locator(".messages")).to_contain_text("LOCAL FIXTURE: " + PERSONAL)
            expect(chat.locator(".messages")).not_to_contain_text(PROJECT_MESSAGE)
            assert journal.read_bytes() == saved and len(provider.requests) == 3
            fixture.checked("Cold restart on another localhost port restores only personal history without replay")
        finally:
            browser.close()
            fixture.stop()

        fixture.env.update(CONFECTORY_HOME_STORAGE=str(other_home), CONFECTORY_ENTRY_STORAGE=str(other_home),
                            CONFECTORY_WEB_PROJECT=str(fixture.projects[1]))
        fixture.start("isolated")
        try:
            page = fixture.setup(browser)
            expect(page.locator("#title")).to_contain_text(TITLE)
            expect(page.locator("#messages")).not_to_contain_text(PROJECT_MESSAGE)
            home(page)
            register(page, provider.endpoint)
            chat = global_chat(page)
            expect(chat.locator(".messages")).to_contain_text("아직 대화가 없어요")
            expect(chat.locator(".messages")).not_to_contain_text(PERSONAL)
            assert not personal_journal(other_home).exists() and journal.read_bytes() == saved
            assert len(provider.requests) == 3
            fixture.checked("Separate EditorHome with same Helper ID and same project title has no copied history")
        finally:
            browser.close()
            fixture.stop()
    assert not fixture.errors and not fixture.external and not provider.errors, (fixture.errors, fixture.external, provider.errors)
    fixture.original()
finally:
    provider.close()
