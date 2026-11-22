"""Keep explicit generated-card selection bound to its current proposal batch."""
import json
import time

from playwright.sync_api import expect, sync_playwright

import v821_worker_review_binding_ui as flow

fixture = flow.fixture
TARGET = fixture.n + "Unit"


def overlay(page):
    return page.locator(".augment-overlay")


def wait_state(page, predicate):
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        state = fixture.state()
        if predicate(state):
            return state
        page.wait_for_timeout(40)
    raise AssertionError((state["aiState"], state["augment"]))


def generate(page, owned, previous=None):
    requests_before = len(owned.requests)
    if not overlay(page).is_visible():
        page.locator("#augment").click()
    overlay(page).locator("[data-propose]").click()
    dialog = page.get_by_role("dialog", name="증강 제안하기")
    dialog.locator("textarea").fill(f"Local fixture direction {requests_before + 1}")
    dialog.locator('button[type="submit"]').click()
    approval = page.locator('.window[data-key="ai-preview"]')
    expect(approval.locator("#ai-start")).to_be_disabled()
    assert len(owned.requests) == requests_before
    for permission in ("contentApproved", "usageApproved"):
        approval.locator(f'[data-permission="{permission}"]').check()
    approval.locator("#ai-start").click()
    state = wait_state(page, lambda state: len(state["augment"]["cards"]) == 3
                       and state["augment"]["batch"] != previous)
    assert len(owned.requests) == requests_before + 1 and not owned.errors, owned.errors
    return state["augment"]


def select(page, card):
    overlay(page).locator(f'[data-card="{card}"]').click()
    expect(page.locator("#status")).to_contain_text("Worker 작업 선택됨")
    fixture.idle()
    state = fixture.state()
    return state["selectedWorkerId"], state


def journal(name):
    path, = fixture.project.glob(f".confectory/ai-development/**/{name}.json")
    return path


def exercise(owned):
    fixture.start(0)
    page = fixture.page = fixture.setup()
    page.set_viewport_size({"width": 1600, "height": 1150})
    helper = flow.setup_helper(page, owned)
    flow.call("select", id=TARGET)
    first = generate(page, owned)
    first_card, unselected = first["cards"][:2]
    assert not fixture.state()["workers"]
    augment_path = journal("augment")
    history_before_close = augment_path.read_bytes()

    overlay(page).locator("[data-close]").click()
    expect(overlay(page)).to_have_count(0)
    assert augment_path.read_bytes() == history_before_close
    assert not fixture.state()["workers"]
    page.locator("#augment").click()
    expect(overlay(page).locator("[data-card]")).to_have_count(3)
    assert fixture.state()["augment"]["batch"] == first["batch"]
    fixture.checked("승인한 로컬 생성은 카드 3개만 만들고 닫기와 재열기는 어떤 Task도 만들지 않는다")

    first_task, selected = select(page, first_card["id"])
    assert len(selected["workers"]) == 1 and selected["workers"][0]["status"] == "ready"
    assert first_task == select(page, first_card["id"])[0]
    assert len(fixture.state()["workers"]) == 1
    fixture.checked("같은 현재 카드의 반복 선택이 하나의 준비 Task만 유지한다")

    second = generate(page, owned, first["batch"])
    second_card = second["cards"][0]
    assert {card["id"] for card in first["cards"]}.isdisjoint({card["id"] for card in second["cards"]})
    expect(overlay(page).locator(f'[data-card="{first_card["id"]}"]')).to_have_count(0)
    second_task, selected = select(page, second_card["id"])
    assert second_task != first_task
    tasks = journal("tasks")
    recorded = json.loads(tasks.read_text())
    assert recorded["project"] == selected["projectId"] and recorded["chief"] == helper
    assert set(recorded["tasks"]) == {first_task, second_task}
    selections = {row["card"]: row["task"] for row in json.loads(augment_path.read_text())["selections"].values()}
    assert selections == {first_card["id"]: first_task, second_card["id"]: second_task}
    for card, task in ((first_card, first_task), (second_card, second_task)):
        row = recorded["tasks"][task]
        assert row["ownerHelper"] == helper and row["status"] == "ready"
        assert row["specification"]["goal"] == card["summary"]
        assert [target["id"] for target in row["specification"]["semanticTargets"]] == [TARGET]
    assert len(owned.requests) == 2 and not owned.errors
    fixture.originals()
    fixture.checked("각 명시 선택이 해당 카드·선언·프로젝트에 묶인 준비 Task만 등록한다")

    before = augment_path.read_bytes(), tasks.read_bytes()
    # A new ordinary selection from an out-of-date view carries the old card
    # ID with valid current transport identity; it is not a replayed command.
    for card in (unselected, first_card):
        fixture.invoke("selectCard", {"card": card["id"]}, False)
        assert (augment_path.read_bytes(), tasks.read_bytes()) == before
        assert fixture.state()["selectedWorkerId"] == second_task
    fixture.checked("이전 묶음의 미선택 카드와 이미 선택한 카드는 새 Task나 선택 변경을 만들지 않는다")

    overlay(page).locator("[data-skip-proposals]").click()
    skip = page.get_by_role("dialog", name="현재 생성 제안 비우기")
    skip.locator("[data-close]").click()
    expect(skip).to_be_hidden()
    assert (augment_path.read_bytes(), tasks.read_bytes()) == before
    assert fixture.state()["augment"]["batch"] == second["batch"]
    overlay(page).locator("[data-skip-proposals]").click()
    skip.locator("[data-confirm-skip]").click()
    expect(skip).to_be_hidden()
    expect(overlay(page).locator("[data-card]")).to_have_count(0)
    state = fixture.state()
    assert not state["augment"]["batch"] and not state["augment"]["cards"]
    assert state["selectedWorkerId"] == second_task and tasks.read_bytes() == before[1]
    after = json.loads(augment_path.read_text())
    assert after["current"] is None and after["history"][-1]["kind"] == "skipped"
    assert {row["card"]: row["task"] for row in after["selections"].values()} == selections
    assert {row["id"] for row in after["batches"]} == {first["batch"], second["batch"]}
    skipped_history = augment_path.read_bytes()
    fixture.invoke("selectCard", {"card": second_card["id"]}, False)
    assert augment_path.read_bytes() == skipped_history and tasks.read_bytes() == before[1]
    assert fixture.state()["selectedWorkerId"] == second_task
    assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
    assert len(owned.requests) == 2 and not owned.errors
    fixture.originals()
    fixture.checked("Skip 취소는 묶음을 유지하고 확정 Skip은 묶음만 비우며 기존 Task와 원본을 보존한다")


if __name__ == "__main__":
    owned = flow.OwnedResponses(TARGET)
    try:
        with sync_playwright() as playwright:
            with playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
                fixture.browser = browser
                exercise(owned)
    finally:
        fixture.stop()
        owned.close()
        print("evidence:", fixture.case)
