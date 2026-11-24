"""Exercise the actual Helper-card dots for a scoped local task journal."""
import json
import re
import shutil
import uuid

from playwright.sync_api import expect, sync_playwright

import v536_wide_mixed as fixture


AGENT = "Confectory.Agent.Responses::Connection"
NODE = fixture.n + "SlotBody/body:common/node:body"
DECLARATION = fixture.n + "SlotBody"


def call(endpoint, **body):
    return fixture.invoke(endpoint, body)["result"]["result"]


def register(page):
    page.locator("#add-agent").click()
    dialog = page.get_by_role("dialog", name="Agent 추가", exact=True)
    dialog.get_by_role("button", name="OpenAI Responses", exact=True).click()
    for field, value in (("model", "worker-tooltip-no-inference"), ("endpoint", "http://127.0.0.1:9"),
                         ("credentialReference", "")):
        dialog.locator(f'[data-connection-field="{field}"]').fill(value)
    dialog.locator("[data-agent-register]").click()
    expect(dialog.locator("[data-agent-registration-state]")).to_contain_text("Agent 등록됨")
    dialog.locator("[data-connection-cancel]").click()


def create_helper(name):
    return call("helperGlobal", action="create", creationId=uuid.uuid4().hex, name=name,
                personality="Fixture", speciality="Fixture", agent=AGENT)["helper"]


def place(page, *helpers):
    page.locator("#add-helper").click()
    dialog = page.get_by_role("dialog", name="프로젝트 도우미 배치", exact=True)
    for helper in helpers:
        dialog.locator(f'[data-project-helper="{helper}"]').click()
    dialog.locator('button[type="submit"]').click()
    expect(dialog).to_have_count(0)
    assert fixture.state()["projectHelperIds"] == list(helpers)


def card(page, helper):
    page.locator(f'.home-side [data-helper="{helper}"]').click()
    profile = page.locator(f'.participant-expanded-card[data-helper-id="{helper}"]')
    expect(profile).to_be_visible()
    return profile


def dots(profile):
    return profile.locator(".helper-profile-workers [data-worker]")


def dot(profile, task):
    return profile.locator(f'.helper-profile-workers [data-worker="{task}"]')


def hover(profile_dot, status, goal):
    profile_dot.hover()
    tooltip = profile_dot.get_by_role("tooltip")
    expect(tooltip).to_be_visible()
    expect(tooltip.locator("strong")).to_have_text(status)
    expect(tooltip).to_contain_text(goal)
    return tooltip


def exercise():
    fixture.start(0)
    page = fixture.page = fixture.setup()
    fixture.idle()
    register(page)
    helper = create_helper("작업 담당 도우미")
    neighbor = create_helper("다른 도우미")
    place(page, helper, neighbor)
    plan = call("nodeTask", action="inspect", node=NODE)
    node_task = call("nodeTask", action="assign", node=NODE, assignmentHash=plan["assignmentHash"],
                     commandID=uuid.uuid4().hex, rationale="실제 Blueprint 위치가 있는 검증 작업")["task"]
    ordinary_goal = "일반 작업의 검증용 고유 설명"
    call("customProposal", target=DECLARATION, commandID=uuid.uuid4().hex, text=ordinary_goal)
    proposal = fixture.state()["augment"]["customCards"][-1]
    call("selectCard", card=proposal["id"])
    state = fixture.state()
    rows = {w["id"]: w for w in state["workers"]}
    assert len(rows) == 2 and rows[node_task]["assignedNode"] == NODE
    ordinary_task = next(task for task in rows if task != node_task)
    assert not rows[ordinary_task]["assignedNode"]
    assert all(w["ownerHelper"] == helper and w["status"] == "ready" for w in rows.values())
    assert not state["aiOwnerAvailable"] and state["aiPreview"] is None
    node_goal = rows[node_task]["goal"]
    assert node_goal and ordinary_goal in rows[ordinary_task]["goal"]

    other_profile = card(page, neighbor)
    expect(dots(other_profile)).to_have_count(0)
    profile = card(page, helper)
    expect(dots(profile)).to_have_count(2)
    node_dot = dot(profile, node_task)
    ordinary_dot = dot(profile, ordinary_task)
    expect(hover(ordinary_dot, "ready", ordinary_goal)).not_to_contain_text(NODE)
    target = hover(node_dot, "ready", node_goal)
    fixture.checked("두 실제 로컬 Worker의 설명과 상태가 소유 도우미의 개별 점에만 나타난다")
    expect(target).to_contain_text(NODE)
    page.mouse.move(1200, 40)
    profile.locator(".helper-window-pin").press("Tab")
    expect(node_dot).to_be_focused()
    expect(target).to_be_visible()
    expect(target).to_contain_text(NODE)
    fixture.checked("Blueprint 배정 위치가 해당 점의 호버와 키보드 포커스에서 정확한 ID로 표시된다")

    second_view = fixture.setup()
    dot(card(second_view, helper), node_task).click()
    panel = second_view.locator('.window[data-key="worker"]')
    expect(panel.locator("h2")).to_have_text(node_task)
    panel.get_by_role("button", name="준비 작업 취소", exact=True).click()
    expect(panel.locator(".window-content > p").first).to_contain_text("cancelled")
    second_view.close()
    expect(node_dot).to_have_class(re.compile(r"\bproblem\b"))
    expect(hover(node_dot, "cancelled", node_goal)).to_contain_text(NODE)
    ordinary_dot = dot(profile, ordinary_task)
    expect(ordinary_dot).to_have_class(re.compile(r"\bwaiting\b"))
    expect(hover(ordinary_dot, "ready", ordinary_goal)).not_to_contain_text(NODE)
    verified = fixture.state()
    assert {w["id"]: w["status"] for w in verified["workers"]} == {
        node_task: "cancelled", ordinary_task: "ready",
    }
    fixture.checked("기존 취소 동작이 선택 일감의 상태 점만 갱신하며 두 번째 설명과 상태를 유지한다")

    fixture.pending()
    fixture.originals()
    journals = {p: p.read_bytes() for p in fixture.project.rglob("tasks.json")}
    assert journals
    second = fixture.case / "second-project"
    shutil.copytree(fixture.project, second, ignore=shutil.ignore_patterns(".confectory", ".build"))
    page.close()
    fixture.stop()
    fixture.env["CONFECTORY_WEB_PROJECT"] = str(second / "project.cproj")
    fixture.start(1)
    page = fixture.page = fixture.setup()
    fixture.idle()
    assert fixture.state()["projectId"] != state["projectId"]
    place(page, helper, neighbor)
    expect(dots(card(page, helper))).to_have_count(0)
    assert fixture.state()["workers"] == []
    assert all(path.read_bytes() == content for path, content in journals.items())
    fixture.originals()
    fixture.checked("같은 선언을 가진 별도 프로젝트에서 같은 도우미를 배치해도 이전 점이나 위치가 나오지 않는다")

    assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
    assert not [row for row in fixture.traffic if row.get("invoke", {}).get("endpoint") in (
        "startAI", "prepareWorker", "executeProject",
    )]


if __name__ == "__main__":
    try:
        with sync_playwright() as playwright:
            with playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
                fixture.browser = browser
                exercise()
    finally:
        fixture.stop()
        (fixture.case / "worker-tooltip-evidence.json").write_text(json.dumps({
            "checks": fixture.checks, "errors": fixture.errors, "external": fixture.external,
        }, ensure_ascii=False, indent=2))
        print("evidence:", fixture.case)
