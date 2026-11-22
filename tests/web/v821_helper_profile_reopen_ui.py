"""Open the same saved Helper display profile in two actual local editor tabs."""
import uuid

from playwright.sync_api import expect, sync_playwright

import v666_workspace_finder_fixture as fixture

AGENT = "Confectory.Agent.Responses::Connection"
FIELDS = {"name": "#participant-name", "shortDescription": "#participant-short-description",
          "description": "#participant-description"}


def values(name, intro, description):
    return dict(zip(FIELDS, (name, intro, description)))


def register_agent(page):
    page.locator("#add-agent").click()
    dialog = page.get_by_role("dialog", name="Agent 추가", exact=True)
    dialog.get_by_role("button", name="OpenAI Responses", exact=True).click()
    for field, value in (("model", "helper-profile-no-inference"), ("endpoint", "http://127.0.0.1:9"),
                         ("credentialReference", "")):
        dialog.locator(f'[data-connection-field="{field}"]').fill(value)
    dialog.locator("[data-agent-register]").click()
    expect(dialog.locator("[data-agent-registration-state]")).to_contain_text("Agent 등록됨")
    dialog.locator("[data-connection-cancel]").click()


def create_profile(profile):
    return fixture.call("helperGlobal", {
        "action": "create", "creationId": uuid.uuid4().hex, "name": profile["name"],
        "personality": profile["description"], "speciality": profile["shortDescription"], "agent": AGENT,
    })["helper"]


def place(page, *helpers):
    page.locator("#add-helper").click()
    dialog = page.get_by_role("dialog", name="프로젝트 도우미 배치", exact=True)
    for helper in helpers:
        dialog.locator(f'[data-project-helper="{helper}"]').click()
    dialog.locator('button[type="submit"]').click()
    expect(dialog).to_have_count(0)


def tile(page, helper):
    return page.locator(f'.home-side [data-helper="{helper}"]')


def settings(page, helper):
    tile(page, helper).click()
    card = page.locator(f'.participant-expanded-card[data-helper-id="{helper}"]')
    card.get_by_role("button", name="도우미 설정", exact=True).click()
    dialog = page.locator("[data-v508-helper]")
    expect(dialog).to_be_visible()
    return dialog


def fields(dialog, expected):
    for key, value in expected.items():
        expect(dialog.locator(FIELDS[key])).to_have_value(value, timeout=4000)


def fill(dialog, edits):
    for key, value in edits.items():
        dialog.locator(FIELDS[key]).fill(value)


def close(dialog):
    dialog.get_by_role("button", name="닫기", exact=True).click()
    expect(dialog).to_have_count(0)


def saved(dialog):
    dialog.get_by_role("button", name="확정", exact=True).click()
    expect(dialog).to_have_count(0)


def row(state, helper):
    return next(item for item in state["helpers"] if item["id"] == helper)


def read_profile(state, helper):
    return {key: row(state, helper)["presentation"]["value"][key] for key in FIELDS}


def exercise(browser):
    fixture.start(0)
    page = fixture.setup(browser)
    register_agent(page)
    initial = values("기존 도우미", "기존 한 줄", "기존 상세 설명")
    neighbor = values("별도 도우미", "다른 한 줄", "다른 상세 설명")
    helper = create_profile(initial)
    other = create_profile(neighbor)
    place(page, helper, other)
    original = fixture.state()

    read_only = settings(page, helper)
    fields(read_only, initial)
    close(read_only)
    assert row(fixture.state(), helper)["presentation"] == row(original, helper)["presentation"]
    fixture.checked("편집하지 않고 닫은 설정은 저장되지 않는다")

    second = fixture.setup(browser)
    changed = values("새 도우미", "새 한 줄 소개", "새 상세 설명")
    edit = settings(second, helper)
    fields(edit, initial)
    fill(edit, changed)
    saved(edit)
    assert read_profile(fixture.state(), helper) == changed
    fixture.checked("두 번째 편집기가 이름·한 줄 소개·상세 설명을 실제로 저장한다")

    reopened = settings(page, helper)
    expect(tile(page, helper).locator("strong")).to_have_text(changed["name"])
    fields(reopened, changed)
    close(reopened)
    fixture.checked("앞서 취소한 첫 편집기는 다음 열기에서 최신 확정 필드를 표시한다")

    edit = settings(page, helper)
    cancelled = values("취소할 도우미", "취소할 소개", "취소할 설명")
    fill(edit, cancelled)
    close(edit)
    assert read_profile(fixture.state(), helper) == changed
    retained = settings(page, helper)
    fields(retained, cancelled)
    fixture.checked("실제 입력을 취소했을 때 저장본과 현재 페이지의 재개 입력을 분리한다")

    latest = {**changed, "description": "다른 편집기에서 저장한 상세 설명"}
    edit = settings(second, helper)
    fields(edit, changed)
    fill(edit, latest)
    saved(edit)
    retained.get_by_role("button", name="확정", exact=True).click()
    expect(page.get_by_text("Helper 설정을 저장하지 못했어요.", exact=False)).to_be_visible()
    fields(retained, cancelled)
    assert read_profile(fixture.state(), helper) == latest
    close(retained)
    fixture.checked("열려 있던 편집기의 충돌 저장은 최신 저장본과 사용자의 미적용 입력을 보존한다")

    unchanged = fixture.state()
    for identity in (helper, other):
        for key in ("membership", "personality", "speciality"):
            assert row(unchanged, identity)[key] == row(original, identity)[key]
    assert unchanged["helperAgents"]["assignments"] == original["helperAgents"]["assignments"]
    assert unchanged["projectHelperIds"] == original["projectHelperIds"]
    assert unchanged["mainHelperId"] == original["mainHelperId"]
    assert row(unchanged, other)["presentation"] == row(original, other)["presentation"]
    assert unchanged.get("allowCommon") == original.get("allowCommon")
    fixture.checked("다른 도우미, 모집 시 역할, 선택 Agent, 프로젝트 배치·기억 설정이 유지된다")

    second.close()
    page.close()
    fixture.stop()
    fixture.start(1)
    page = fixture.setup(browser)
    dialog = settings(page, helper)
    fields(dialog, latest)
    close(dialog)
    fields(settings(page, other), neighbor)
    assert read_profile(fixture.state(), helper) == latest
    fixture.original()
    assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
    assert not [req for req in fixture.requests if req["endpoint"] in ("startAI", "prepareAI") or
                (req["endpoint"] == "helperGlobal" and req["input"]["action"] in ("prepare", "start"))]
    fixture.checked("프로세스를 완전히 재시작하면 저장한 필드만 복원되며 두 프로젝트 원본은 동일하다")


try:
    with sync_playwright() as playwright:
        with playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
            exercise(browser)
finally:
    fixture.stop()
    fixture.save_evidence()
    print(f"evidence: {fixture.root}")
