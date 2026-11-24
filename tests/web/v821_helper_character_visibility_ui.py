"""Verify the personal character presentation preference in the real local editor."""

import json
import uuid

from playwright.sync_api import expect, sync_playwright

from v821_helper_blank_description_ui import NAME, PERSONALITY, SPECIALITY, state_metadata
from v821_helper_worker_tooltip_ui import AGENT, NODE, call, card, fixture, hover, place, register


PREFERENCE = "도우미 캐릭터 표현 표시"
DRAFT = "전송하지 않은 고정 도우미 대화"


def settings(page):
    page.get_by_role("button", name="설정 열기", exact=True).click()
    dialog = page.get_by_role("dialog", name="설정", exact=True)
    return dialog, dialog.get_by_role("checkbox", name=PREFERENCE, exact=True)


def close(dialog):
    dialog.get_by_role("button", name="닫기", exact=True).click()


def show_characters(page, show):
    dialog, checkbox = settings(page)
    checkbox.set_checked(show)
    expect(checkbox).to_be_enabled()
    if show:
        expect(checkbox).to_be_checked()
    else:
        expect(checkbox).not_to_be_checked()
    expect(dialog.locator("[data-helper-character-status]")).to_be_hidden()
    close(dialog)


def check_profile(page, helper, *, show, task, live):
    helper_button = page.locator(f'.home-side [data-helper="{helper}"]')
    expect(page.locator(".home-side .is-project-main")).to_have_attribute("data-helper", helper)
    expect(page.locator(f'#participant-agent [data-agent="{AGENT}"]')).to_be_visible()
    helper_button.hover()
    tooltip = page.locator(".coworker-hover-card.helper-profile-card")
    expect(tooltip).to_be_visible()
    expect(tooltip.locator(".helper-profile-identity")).to_contain_text(SPECIALITY)
    check_decorations(tooltip, show)
    profile = card(page, helper)
    expect(profile.locator(".helper-profile-identity")).to_contain_text(NAME)
    expect(profile.locator(".helper-profile-identity")).to_contain_text(SPECIALITY)
    check_decorations(profile, show)
    expect(profile.get_by_role("button", name="도우미 설정", exact=True)).to_be_enabled()
    expect(profile.get_by_role("button", name="고정", exact=True)).to_be_enabled()
    expect(profile.locator("#global-chat textarea")).to_be_enabled()
    expect(profile.locator("#global-chat [data-helper-send]")).to_be_enabled()
    expect(page.locator("#run")).to_be_enabled()
    worker = profile.locator('.helper-profile-workers [data-worker]')
    expect(worker).to_have_count(1)
    expect(hover(worker, "ready", NODE)).to_contain_text(NODE)
    page.mouse.move(1200, 40)
    if not live:
        assert worker.evaluate("(element) => element.tagName") == "SPAN"
        return None
    worker.click()
    window = page.locator('.window[data-key="worker"]')
    expect(window.locator("h2")).to_have_text(task)
    expect(window.locator("#worker-cancel-ready")).to_be_enabled()
    controls = window.locator("button[data-operation]").evaluate_all(
        "(buttons) => buttons.map(button => [button.id, button.textContent, button.disabled])")
    expect(window.locator("#worker-prepare")).to_be_visible()
    window.get_by_role("button", name="창 닫기", exact=True).click()
    return controls


def check_decorations(pane, show):
    portrait = pane.locator(".helper-profile-bust")
    description = pane.locator(".helper-profile-status")
    if show:
        expect(portrait).to_be_visible()
        expect(description).to_have_text(PERSONALITY)
        expect(description).to_be_visible()
    else:
        expect(portrait).to_be_hidden()
        expect(description).to_be_hidden()


def exercise():
    # An original version-1 Home preference file belongs to the same user.
    legacy = b'{"version":1,"tab":"packs","projectQuery":"keep","packGroup":"favorite","packs":{' + b','.join(
        b'"' + group + b'":{"draft":"","query":"","sort":"default","selected":null}'
        for group in (b'local', b'explore', b'favorite', b'mine')) + b'}}'
    home_path = fixture.storage / "home-preferences.json"
    home_path.write_bytes(legacy)
    preference_path = fixture.storage / "helper-character-presentation.json"

    fixture.start(0)
    page = fixture.page = fixture.setup()
    dialog, checkbox = settings(page)
    expect(checkbox).to_be_checked()
    expect(checkbox).to_be_enabled()
    close(dialog)
    assert not preference_path.exists()
    register(page)
    helper = call("helperGlobal", action="create", creationId=uuid.uuid4().hex, name=NAME,
                  personality=PERSONALITY, speciality=SPECIALITY, agent=AGENT)["helper"]
    place(page, helper)
    plan = call("nodeTask", action="inspect", node=NODE)
    task = call("nodeTask", action="assign", node=NODE, assignmentHash=plan["assignmentHash"],
                commandID=uuid.uuid4().hex, rationale="Verified local Worker display")["task"]
    before = state_metadata(helper)
    controls = check_profile(page, helper, show=True, task=task, live=True)

    profile = card(page, helper)
    profile.get_by_role("button", name="고정", exact=True).click()
    pinned = profile.get_by_role("button", name=f"{NAME} 대화 입력 열기", exact=True)
    expect(pinned.locator(".sd-portrait-empty")).to_be_visible()
    pinned.press("Enter")
    compose = profile.locator(".sd-compose textarea")
    expect(compose).to_be_focused()
    compose.fill(DRAFT)
    show_characters(page, False)
    expect(pinned.locator(".sd-portrait-empty")).to_be_hidden()
    expect(pinned.get_by_text(NAME, exact=True)).to_be_visible()
    expect(compose).to_have_value(DRAFT)
    compose.press("Escape")
    expect(pinned).to_be_focused()
    pinned.click()
    expect(compose).to_have_value(DRAFT)
    compose.press("Escape")
    pinned.press("Escape")

    assert check_profile(page, helper, show=False, task=task, live=True) == controls
    assert state_metadata(helper) == before
    assert preference_path.read_text() == "false" and home_path.read_bytes() == legacy
    fixture.checked("The unchecked preference hides profile and pinned presentations while preserving chat and the Worker controls")

    preference_path.chmod(0o444)
    try:
        dialog, checkbox = settings(page)
        checkbox.click()
        expect(dialog.locator("[data-helper-character-status]")).to_have_text(
            "캐릭터 표시 설정을 저장하지 못했습니다.")
        expect(checkbox).not_to_be_checked()
        close(dialog)
        assert preference_path.read_text() == "false"
        check_profile(page, helper, show=False, task=task, live=True)
    finally:
        preference_path.chmod(0o600)
    fixture.checked("A rejected write leaves the current presentation and saved preference intact")

    fixture.pending()
    page.close()
    fixture.stop()
    fixture.start(1)
    page = fixture.page = fixture.setup()
    dialog, checkbox = settings(page)
    expect(checkbox).not_to_be_checked()
    close(dialog)
    check_profile(page, helper, show=False, task=task, live=False)
    show_characters(page, True)
    check_profile(page, helper, show=True, task=task, live=False)
    assert state_metadata(helper) == before
    assert preference_path.read_text() == "true" and home_path.read_bytes() == legacy
    fixture.checked("A new host and browser context restore the preference; turning it back on displays the original profile")

    page.locator(".brand").click()
    page.locator("#home-tab-projects").click()
    query = page.locator("#home-project-search")
    expect(query).to_have_value("keep")
    query.fill("Saved independently")
    assert page.evaluate("async () => await confectoryFlushHomePreferences()")
    saved_home = json.loads(home_path.read_bytes())
    assert saved_home["projectQuery"] == "Saved independently"
    assert set(saved_home) == set(json.loads(legacy))
    assert preference_path.read_text() == "true"
    show_characters(page, False)
    page.close()
    fixture.stop()

    other_storage = fixture.case / "other-profile"
    other_storage.mkdir()
    fixture.env.update(CONFECTORY_HOME_STORAGE=str(other_storage), CONFECTORY_ENTRY_STORAGE=str(other_storage))
    fixture.start(2)
    page = fixture.page = fixture.setup()
    dialog, checkbox = settings(page)
    expect(checkbox).to_be_checked()
    expect(checkbox).to_be_enabled()
    close(dialog)
    assert not (other_storage / preference_path.name).exists()
    assert preference_path.read_text() == "false"
    fixture.checked("Existing Home settings still save independently, and a second local profile uses the default")

    fixture.originals()
    assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
    assert not {row.get("invoke", {}).get("endpoint") for row in fixture.traffic} & {
        "prepareAI", "startAI", "prepareWorker", "runProject", "executeProject", "dispatchWorker",
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
