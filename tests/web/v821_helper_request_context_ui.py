"""Check request preparation independently of the local character display setting."""

import json
import select
import shutil
import socket
import uuid

from playwright.sync_api import expect, sync_playwright

from v821_helper_blank_description_ui import save_description
from v821_helper_character_visibility_ui import show_characters
from v821_helper_worker_tooltip_ui import AGENT, call, card, fixture, place, register


MESSAGE = "반환값과 호출자 연결을 검토해 주세요."
PERSONALITY = "작업 지시: 변경 전에 현재 연결을 확인합니다."
SPECIALITY = "함수 계약 검토"
DISPLAY_TEXT = "표시 전용 한 줄"
PROJECT_NOTE = "프로젝트 A 반환 계약: 기존 호출자와 이름을 유지."
OTHER_NOTE = "프로젝트 B의 독립적인 입력 계약."
COMMON_NOTE = "공통 기억: 결과에 근거와 확인 범위를 적습니다."


def remember(helper, scope, text):
    call("helperRemember", helper=helper, scope=scope, text=text)


def project_preview(page, helper):
    profile = card(page, helper)
    profile.locator("#global-chat textarea").fill(MESSAGE)
    profile.locator("#global-chat [data-helper-send]").click()
    review = page.locator('.window[data-key="ai-preview"]')
    expect(review).to_be_visible()
    expect(review.locator("#ai-start")).to_be_disabled()
    preview = fixture.state()["aiPreview"]
    assert preview["kind"] == "chat" and preview["connection"] == AGENT
    assert preview["canStart"] is True and preview["approvals"] == {}
    assert {entry["id"] for entry in preview["requirements"]} >= {"contentApproved", "usageApproved"}
    review.locator("#cancel-preview").click()
    expect(review).to_have_count(0)
    assert fixture.state()["aiPreview"] is None
    return preview


def global_preview(helper, include_common):
    preview = call("helperGlobal", action="prepare", helper=helper, message=MESSAGE,
                   includeCommon=include_common)
    call("helperGlobal", action="cancel-preview", helper=helper)
    assert preview["connection"] == AGENT
    assert preview["context"]["history"] == []
    assert preview["policy"]["contentScope"] == {
        "kind": "helper-global",
        "helperId": helper,
        "conversationId": preview["context"]["conversationId"],
    }
    return preview


def assert_context(preview, key, helper, project, memory):
    assert preview["message"] == MESSAGE
    context = preview[key]
    assert context["projectId"] == project
    assert context["profile"] == {
        "helper": helper, "personality": PERSONALITY, "speciality": SPECIALITY,
    }
    assert context["membership"]["kind"] == "global"
    assert {(entry["scope"], entry["projectId"], entry["text"]) for entry in context["memory"]} == memory
    assert DISPLAY_TEXT not in json.dumps(context, ensure_ascii=False)
    assert "showHelperCharacters" not in context and "relationship" not in context


def equal_preparation(first, second):
    assert first["token"] != second["token"]
    assert {k: v for k, v in first.items() if k != "token"} == {
        k: v for k, v in second.items() if k != "token"
    }


def exercise(provider):
    other = fixture.case / "other project"
    shutil.copytree(fixture.project, other, ignore=shutil.ignore_patterns(".confectory"))
    other_sources = {p: p.read_bytes() for p in other.rglob("*") if p.is_file()}

    fixture.start(0)
    page = fixture.page = fixture.setup()
    project = fixture.state()["projectId"]
    register(page, endpoint=f"http://127.0.0.1:{provider.getsockname()[1]}")
    helper = call("helperGlobal", action="create", creationId=uuid.uuid4().hex,
                  name="요청 문맥 검증 도우미", personality=PERSONALITY, speciality=SPECIALITY,
                  agent=AGENT)["helper"]
    place(page, helper)
    save_description(page, helper, DISPLAY_TEXT)
    remember(helper, "project", PROJECT_NOTE)
    remember(helper, "common", COMMON_NOTE)
    assert fixture.state()["homePreferences"]["showHelperCharacters"] is True
    project_on = project_preview(page, helper)
    global_on = global_preview(helper, include_common=True)

    show_characters(page, False)
    project_off = project_preview(page, helper)
    global_off = global_preview(helper, include_common=True)
    assert_context(project_off, "helperContext", helper, project,
                   {("project", project, PROJECT_NOTE)})
    assert_context(global_off, "context", helper, "", {("common", "", COMMON_NOTE)})
    assert_context(global_preview(helper, include_common=False), "context", helper, "", set())
    equal_preparation(project_on, project_off)
    equal_preparation(global_on, global_off)
    fixture.checked("Display on/off leaves project and global preparation, work context and approval requirements identical")

    fixture.pending()
    page.close()
    fixture.stop()
    fixture.env["CONFECTORY_WEB_PROJECT"] = str(other / "project.cproj")
    fixture.start(1)
    page = fixture.page = fixture.setup()
    other_project = fixture.state()["projectId"]
    assert other_project and other_project != project
    assert fixture.state()["homePreferences"]["showHelperCharacters"] is False
    place(page, helper)
    remember(helper, "project", OTHER_NOTE)
    assert_context(project_preview(page, helper), "helperContext", helper, other_project,
                   {("project", other_project, OTHER_NOTE)})
    fixture.checked("A second active project excludes the original project memory and leaves common memory opt-in")

    fixture.originals()
    assert all(path.read_bytes() == content for path, content in other_sources.items())
    assert not list((fixture.storage / "helper-conversations").glob("*.json"))
    assert not list((fixture.storage / "project-chat").glob("*.json"))
    assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
    assert not select.select([provider], [], [], 0)[0], "Unexpected provider connection"
    invoked = [row["invoke"] for row in fixture.traffic if "invoke" in row]
    assert not any(row["endpoint"] == "startAI"
                   or (row["endpoint"] == "helperGlobal" and row["input"]["action"] == "start")
                   for row in invoked)


if __name__ == "__main__":
    try:
        with socket.socket() as provider, sync_playwright() as playwright, playwright.chromium.launch(
                executable_path="/usr/bin/chromium", args=["--no-sandbox", "--disable-gpu"],
                ignore_default_args=["--disable-dev-shm-usage"]) as browser:
            provider.bind(("127.0.0.1", 0))
            provider.listen(1)
            fixture.browser = browser
            expect.set_options(timeout=12000)
            exercise(provider)
    finally:
        fixture.stop()
