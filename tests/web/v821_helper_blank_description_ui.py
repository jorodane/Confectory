"""Clear the existing local profile description without changing the Helper's role."""

import json
import uuid

from playwright.sync_api import expect, sync_playwright

from v821_helper_worker_tooltip_ui import AGENT, NODE, call, card, dot, fixture, place, register


NAME = "로컬 표시 도우미"
PERSONALITY = "표시 기본값으로도 복사되는 고유 성격 문구"
SPECIALITY = "확인할 작업 역할"
DESCRIPTION = "#participant-description"


def settings(page, helper):
    card(page, helper).get_by_role("button", name="도우미 설정", exact=True).click()
    dialog = page.locator("[data-v508-helper]")
    expect(dialog).to_be_visible()
    return dialog


def save_description(page, helper, text):
    dialog = settings(page, helper)
    dialog.locator(DESCRIPTION).fill(text)
    dialog.get_by_role("button", name="확정", exact=True).click()
    expect(dialog).to_have_count(0)


def state_metadata(helper):
    state = fixture.state()
    profile = next(row for row in state["helpers"] if row["id"] == helper)
    return profile, {
        "agent": state["helperAgents"]["assignments"][helper],
        "main": state["mainHelperId"],
        "placed": state["projectHelperIds"],
        "personality": profile["personality"],
        "speciality": profile["speciality"],
        "membership": profile["membership"],
    }


def assert_profile(page, helper, *, description, task, clickable):
    expect(page.locator(f'#participant-agent [data-agent="{AGENT}"]')).to_be_visible()
    expect(page.locator(".home-side .is-project-main")).to_have_attribute("data-helper", helper)
    profile = card(page, helper)
    expect(profile.locator(".helper-profile-identity strong")).to_have_text(NAME)
    expect(profile.locator(".helper-profile-identity")).to_contain_text(SPECIALITY)
    expect(profile.locator(".helper-profile-bust")).to_be_visible()
    status = profile.locator(".helper-profile-status")
    if description:
        expect(status).to_have_text(description)
    else:
        expect(status).to_be_hidden()
        expect(profile).not_to_contain_text(PERSONALITY)
    expect(profile.locator("#global-chat textarea")).to_be_visible()
    expect(profile.get_by_role("button", name="도우미 설정", exact=True)).to_be_enabled()
    expect(profile.get_by_role("button", name="고정", exact=True)).to_be_enabled()

    worker = dot(profile, task) if clickable else profile.locator(".helper-profile-workers [data-worker]")
    expect(worker).to_have_count(1)
    worker.hover()
    expect(worker.get_by_role("tooltip").locator("strong")).to_have_text("ready")
    expect(worker.get_by_role("tooltip").locator(".worker-assigned-node")).to_have_text(NODE)
    page.mouse.move(1200, 40)
    if not clickable:
        assert worker.evaluate("(element) => element.tagName") == "SPAN"
    return worker


def exercise():
    fixture.start(0)
    page = fixture.page = fixture.setup()
    page.get_by_role("button", name="설정 열기", exact=True).click()
    app_settings = page.get_by_role("dialog", name="설정", exact=True)
    expect(app_settings.locator("#settings-sidebar-width")).to_be_visible()
    app_settings.get_by_role("button", name="닫기", exact=True).click()
    register(page)
    helper = call("helperGlobal", action="create", creationId=uuid.uuid4().hex, name=NAME,
                  personality=PERSONALITY, speciality=SPECIALITY, agent=AGENT)["helper"]
    place(page, helper)
    plan = call("nodeTask", action="inspect", node=NODE)
    task = call("nodeTask", action="assign", node=NODE, assignmentHash=plan["assignmentHash"],
                commandID=uuid.uuid4().hex, rationale="Explicit offline profile display fixture")["task"]
    profile, before = state_metadata(helper)
    assert profile["presentation"]["value"]["description"] == PERSONALITY
    assert_profile(page, helper, description=PERSONALITY, task=task, clickable=True)

    save_description(page, helper, "")
    profile, after = state_metadata(helper)
    assert profile["presentation"]["value"]["description"] == ""
    assert after == before
    worker = assert_profile(page, helper, description="", task=task, clickable=True)
    worker.click()
    task_window = page.locator('.window[data-key="worker"]')
    expect(task_window.locator("h2")).to_have_text(task)
    expect(task_window.get_by_role("button", name="준비 작업 취소", exact=True)).to_be_enabled()
    task_window.get_by_role("button", name="창 닫기", exact=True).click()
    dialog = settings(page, helper)
    expect(dialog.locator(DESCRIPTION)).to_have_value("")
    dialog.get_by_role("button", name="닫기", exact=True).click()
    fixture.checked("Clearing the display description keeps the Helper role, Agent, MAIN, chat and existing Worker controls")

    fixture.pending()
    page.close()
    fixture.stop()
    fixture.start(1)
    page = fixture.page = fixture.setup()
    assert_profile(page, helper, description="", task=task, clickable=False)
    dialog = settings(page, helper)
    expect(dialog.locator(DESCRIPTION)).to_have_value("")
    dialog.get_by_role("button", name="닫기", exact=True).click()
    save_description(page, helper, PERSONALITY)
    profile, restored = state_metadata(helper)
    assert restored == before and profile["presentation"]["value"]["description"] == PERSONALITY
    assert_profile(page, helper, description=PERSONALITY, task=task, clickable=False)
    fixture.checked("The cleared display survives restarting and the existing form restores it without changing the stored persona or task")
    fixture.originals()
    assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
    assert not {row.get("invoke", {}).get("endpoint") for row in fixture.traffic} & {
        "startAI", "prepareWorker", "executeProject", "dispatchWorker",
    }


if __name__ == "__main__":
    try:
        with sync_playwright() as playwright, playwright.chromium.launch(
                executable_path="/usr/bin/chromium", args=["--no-sandbox", "--disable-gpu"],
                ignore_default_args=["--disable-dev-shm-usage"]) as browser:
            fixture.browser = browser
            expect.set_options(timeout=8000)
            exercise()
    finally:
        fixture.stop()
