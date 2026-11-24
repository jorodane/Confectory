"""Exercise cancellation and a disconnected Agent without dispatching a Helper turn."""

import select
import shutil
import socket
import uuid

from playwright.sync_api import expect, sync_playwright

from v821_helper_worker_tooltip_ui import AGENT, call, card, fixture, place, register


ORIGINAL = "함수 연결을 확인해 주세요.\n  다음 줄과 공백을 유지합니다.  "
PROJECT_A = ORIGINAL + "\n아직 보내지 않은 A의 수정"
PROJECT_B = "두 번째 프로젝트의 미전송 문장  🔷"
GLOBAL = "Home 전역 Helper의 별도 미전송 문장"


def conversation(page, helper, mode="project"):
    root = card(page, helper).locator("#global-chat")
    expect(root).to_have_attribute("data-conversation-mode", mode)
    return root


def home(page):
    page.locator(".brand").click()
    expect(page.locator(".home-grid")).to_be_visible()
    assert not fixture.state()["projectId"]


def open_project(page, listing, identity):
    profile = page.locator('.participant-expanded-card[data-project-id=""]')
    if profile.is_visible():
        profile.get_by_role("button", name="닫기", exact=True).click()
    page.locator(f'[data-enter="{listing}"]').click()
    expect(page.locator(".work-body")).to_be_visible()
    fixture.idle()
    assert fixture.state()["projectId"] == identity


def set_offline(page, offline):
    page.locator(f'.home-side [data-agent="{AGENT}"]').click()
    dialog = page.locator("[data-connection-dialog]")
    button = dialog.locator("[data-agent-offline]")
    expect(button).to_have_text("연결 해제" if offline else "다시 사용")
    button.click()
    expect(button).to_have_text("다시 사용" if offline else "연결 해제")
    dialog.locator("[data-connection-cancel]").click()
    expect(dialog).to_have_count(0)
    agent = next(row for row in fixture.state()["helperAgents"]["agents"] if row["id"] == AGENT)
    assert (agent["state"] == "offline") is offline


def cancel_review(page, root, message):
    draft = root.locator("textarea")
    expect(draft).to_have_value(message)
    root.locator("[data-helper-send]").click()
    review = page.locator('.window[data-key="ai-preview"]')
    expect(review).to_be_visible()
    expect(review.locator("#ai-start")).to_be_disabled()
    prepared = fixture.state()["aiPreview"]
    assert prepared["message"] == message and prepared["approvals"] == {}
    review.get_by_role("button", name="검토 취소", exact=True).click()
    expect(review).to_have_count(0)
    expect(draft).to_be_visible()
    expect(draft).to_have_value(message)
    assert fixture.state()["aiPreview"] is None
    expect(root.locator(".messages")).to_have_text("아직 받은 응답이 없습니다.")
    return draft


def blocked_attempt(page, helper, text):
    root = conversation(page, helper)
    field = root.locator("textarea")
    field.fill(text)
    root.locator("[data-helper-send]").click()
    expect(page.locator("#status")).to_contain_text("프로젝트 대화를 준비하거나 전송하지 못했어요.")
    expect(page.locator("#status")).to_contain_text("agent-binding")
    expect(field).to_be_visible()
    expect(field).to_be_enabled()
    expect(field).to_have_value(text)
    expect(root.locator(".messages")).to_have_text("아직 받은 응답이 없습니다.")
    expect(page.locator("#ai-start")).to_have_count(0)
    assert fixture.state()["aiPreview"] is None


def assert_draft(page, helper, text, mode="project"):
    root = conversation(page, helper, mode)
    expect(root.locator("textarea")).to_have_value(text)
    return root


def exercise(provider):
    other = fixture.case / "other project"
    shutil.copytree(fixture.project, other, ignore=shutil.ignore_patterns(".confectory"))
    other_sources = {p: p.read_bytes() for p in other.rglob("*") if p.is_file()}

    fixture.env["CONFECTORY_WEB_PROJECT"] = str(other / "project.cproj")
    fixture.start(0)
    state = fixture.state()
    project_b, listing_b = state["projectId"], state["listingId"]
    fixture.stop()
    fixture.env["CONFECTORY_WEB_PROJECT"] = str(fixture.project / "project.cproj")
    fixture.start(1)
    page = fixture.page = fixture.setup()
    state = fixture.state()
    project_a, listing_a = state["projectId"], state["listingId"]
    assert project_a and project_b and project_a != project_b
    register(page, endpoint=f"http://127.0.0.1:{provider.getsockname()[1]}")
    helper = call("helperGlobal", action="create", creationId=uuid.uuid4().hex,
                  name="미전송 복원 도우미", personality="계약 검토", speciality="로컬 시험", agent=AGENT)["helper"]
    place(page, helper)

    root = conversation(page, helper)
    root.locator("textarea").fill(ORIGINAL)
    draft = cancel_review(page, root, ORIGINAL)
    draft.press("End")
    draft.press("!")
    expect(draft).to_have_value(ORIGINAL + "!")
    set_offline(page, True)
    blocked_attempt(page, helper, PROJECT_A)
    assert fixture.state()["projectId"] == project_a
    set_offline(page, False)
    cancel_review(page, conversation(page, helper), PROJECT_A)
    set_offline(page, True)
    fixture.checked("Review cancellation and offline preparation preserve the exact draft for editing or reviewing again")

    home(page)
    global_root = assert_draft(page, helper, "", "global")
    expect(global_root.locator("[data-global-send]")).to_be_disabled()
    global_root.locator("textarea").fill(GLOBAL)
    expect(global_root.locator(".messages")).to_have_text("아직 대화가 없어요.")
    open_project(page, listing_b, project_b)
    place(page, helper)
    assert_draft(page, helper, "")
    blocked_attempt(page, helper, PROJECT_B)
    home(page)
    assert_draft(page, helper, GLOBAL, "global")
    open_project(page, listing_a, project_a)
    assert_draft(page, helper, PROJECT_A)
    home(page)
    fixture.checked("Normal project switching keeps A, B and the offline Home Helper drafts independent")

    page.close()
    fixture.stop()
    fixture.env.pop("CONFECTORY_WEB_PROJECT")
    fixture.start(2)
    page = fixture.page = fixture.setup()
    expect(page.locator(".home-grid")).to_be_visible()
    assert not fixture.state()["projectId"]
    assert_draft(page, helper, GLOBAL, "global")
    for listing, identity, text in ((listing_a, project_a, PROJECT_A), (listing_b, project_b, PROJECT_B)):
        open_project(page, listing, identity)
        assert_draft(page, helper, text)
        expect(page.locator(".window[data-key='ai-preview']")).to_have_count(0)
        assert fixture.state()["aiPreview"] is None
        home(page)
    fixture.checked("A new host and browser context reopen only the three private drafts, without replaying a review or send")

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
