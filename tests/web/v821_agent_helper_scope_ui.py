"""Validate the real editor's Agent registry and project-scoped Helper roster offline."""

import json
import re
import sys
from uuid import uuid4

from playwright.sync_api import expect, sync_playwright

import v666_workspace_finder_fixture as fixture

sys.path.insert(0, str(fixture.repo / "tests" / "gui"))
from project_shell_agent_fixture import AGENT, CODEX, prepare_agents


PROJECT_A, PROJECT_B = "Helper Scope Alpha", "Helper Scope Beta"
NAME_A, NAME_B = "편집 길잡이", "구조 검토 도우미"


def seed_registry():
    storage = fixture.root / "profile"
    storage.mkdir()
    (storage / "projects.json").write_text(json.dumps([
        {"path": str(path), "title": title, "description": ""}
        for path, title in zip(fixture.projects, (PROJECT_A, PROJECT_B))
    ]))
    fixture.env.pop("CONFECTORY_WEB_PROJECT")
    for option in ("CONFECTORY_DEV_PUBLIC_CHAT_LOOPBACK", "CONFECTORY_TEST_PUBLIC_CHAT_RELAY"):
        fixture.env.pop(option, None)
    command = fixture.report["run"]
    prepare_agents(command, fixture.repo, fixture.env, storage)
    prepare_agents(command, fixture.repo, fixture.env, storage, register_codex=True)
    fixture.start(0)
    return tuple(fixture.call("helperGlobal", {
        "action": "create", "creationId": uuid4().hex, "name": name,
        "personality": "Offline display fixture", "speciality": "Scoped test Helper", "agent": AGENT,
    })["helper"] for name in (NAME_A, NAME_B))


def tile(page, helper):
    return page.locator(f'#participant-helper [data-helper="{helper}"]')


def identities(page, selector, key):
    return set(page.locator(selector).evaluate_all("(rows, key) => rows.map(row => row.dataset[key])", key))


def assert_roster(page, helper_ids, main=None):
    agents = page.locator("#participant-agent")
    helpers = page.locator("#participant-helper")
    expect(page.locator('[data-participant-toggle="agent"]')).to_have_attribute("aria-label", "AGENT (2)")
    expect(page.locator('[data-participant-toggle="helper"]')).to_have_attribute(
        "aria-label", f"HELPER ({len(helper_ids)})")
    assert identities(page, "#participant-agent [data-agent]", "agent") == {AGENT, CODEX}
    assert identities(page, "#participant-helper [data-helper]", "helper") == set(helper_ids)
    expect(agents.locator("[data-helper]")).to_have_count(0)
    expect(helpers.locator("[data-agent]")).to_have_count(0)
    for connection, name in ((AGENT, "OpenAI Responses"), (CODEX, "Codex")):
        row = agents.locator(f'[data-agent="{connection}"]')
        expect(row).to_be_visible()
        expect(row.locator("strong")).to_have_text(name)
        expect(row.locator(".connection-dot")).not_to_have_class(re.compile(r"\b(ready|running|responded)\b"))

    badges = page.locator(".home-side .is-project-main")
    expect(badges).to_have_count(int(main is not None))
    if main:
        expect(badges).to_have_attribute("data-helper", main)
        assert badges.evaluate("(row) => getComputedStyle(row, '::before').content") == '"MAIN"'
        expect(badges.locator(".meta small")).to_have_text("메인 도우미")
    state = fixture.state()
    assert state["mainHelperId"] == main
    assert set(state["projectHelperIds"]) == (set(helper_ids) if state["projectId"] else set())
    assert not any(agent["accountVerified"] for agent in state["helperAgents"]["agents"])


def open_project(page, title):
    page.locator(".project-card").filter(has=page.get_by_role("heading", name=title, exact=True)).locator("[data-enter]").click()
    expect(page.locator("#title")).to_contain_text(title)
    return fixture.state()["projectId"]


def home(page):
    page.get_by_role("button", name="Confectory 홈으로", exact=True).click()
    expect(page.locator(".home-grid")).to_be_visible()


def place(page, *ids):
    page.locator("#add-helper").click()
    dialog = page.get_by_role("dialog", name="프로젝트 도우미 배치", exact=True)
    for identity in ids:
        dialog.locator(f'[data-project-helper="{identity}"][data-selected="false"]').click()
    expect(dialog.locator('#project-helper-roster .is-main [data-project-helper]')).to_have_attribute(
        "data-project-helper", ids[0])
    dialog.get_by_role("button", name="배치 적용", exact=True).click()
    expect(dialog).to_have_count(0)


def run(page, first, second):
    expect(page.locator(".welcome")).to_have_attribute("aria-busy", "false")
    expect(page.locator("#later")).to_be_enabled()
    expect(page.locator(".home-grid, .work-body")).to_have_count(0)
    page.locator("#connect").click()
    picker = page.get_by_role("dialog", name="Agent 추가", exact=True)
    for agent in ("OpenAI Responses", "Codex"):
        expect(picker.get_by_role("button", name=agent, exact=True)).to_be_visible()
    for name in (NAME_A, NAME_B):
        expect(picker.get_by_text(name, exact=True)).to_have_count(0)
    picker.locator("[data-connection-cancel]").click()
    page.locator("#later").click()
    expect(page.locator(".home-grid")).to_be_visible()
    expect(page.locator(".startup-flight-layer")).to_have_count(0)
    global_helpers = ("main-helper", first, second)
    assert_roster(page, global_helpers)
    expect(tile(page, first).locator("strong")).to_have_text(NAME_A)
    expect(tile(page, second).locator("strong")).to_have_text(NAME_B)
    page.locator(f'#participant-agent [data-agent="{AGENT}"]').click()
    expect(picker.locator('[data-connection-field="model"]')).to_have_value("owned-not-contacted")
    expect(page.locator(".participant-expanded-card")).to_have_count(0)
    picker.locator("[data-connection-cancel]").click()
    expect(picker).to_have_count(0)
    fixture.checked("Offline startup shows Agent settings only; Home shows distinct Agent and registered Helper lists with no MAIN")

    tile(page, second).click()
    dialog = page.get_by_role("dialog", name=NAME_B + " 프로필과 대화", exact=True)
    expect(dialog.locator("#global-chat textarea")).to_be_visible()
    expect(dialog).to_have_attribute("data-helper-id", second)
    expect(dialog).to_have_attribute("data-project-id", "")
    assert not fixture.state()["projectId"]
    dialog.get_by_role("button", name="닫기", exact=True).click()
    expect(dialog).to_have_count(0)
    fixture.checked("A real registered global Helper opens on Home without selecting a project or sending anything")

    alpha = open_project(page, PROJECT_A)
    assert_roster(page, ())
    place(page, first, second)
    assert_roster(page, (first, second), first)
    home(page)
    assert_roster(page, global_helpers)
    beta = open_project(page, PROJECT_B)
    assert beta and beta != alpha
    assert_roster(page, ())
    place(page, second)
    assert_roster(page, (second,), second)
    home(page)
    assert_roster(page, global_helpers)
    assert open_project(page, PROJECT_A) == alpha
    assert_roster(page, (first, second), first)
    fixture.checked("MAIN follows each project's explicit placement through Home and reopening; the Agent registry stays separate")

    state = fixture.state()
    assert not state["helperAgents"]["turns"] and state["aiPreview"] is None
    assert not any(row["endpoint"] in {"codexOnboarding", "connectAgent", "prepareAI", "startAI", "submitProjectChat"}
                   or row["endpoint"] == "helperGlobal" and row["input"]["action"] in {"prepare", "start", "send", "probe"}
                   for row in fixture.requests)
    assert not (fixture.root / "profile" / "helper-conversations").exists()
    fixture.original()
    assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)


if __name__ == "__main__":
    try:
        first, second = seed_registry()
        with sync_playwright() as playwright, playwright.chromium.launch(
                executable_path="/usr/bin/chromium", args=["--no-sandbox", "--disable-gpu"],
                ignore_default_args=["--disable-dev-shm-usage"]) as browser:
            expect.set_options(timeout=10000)
            run(fixture.setup(browser, welcome=True), first, second)
    finally:
        fixture.stop()
