"""Open two Helper profiles over real scoped offline Worker journal reads."""

import hashlib
import json
import re
import shutil
import time

from playwright.sync_api import expect, sync_playwright

from v821_helper_worker_tooltip_ui import NODE, card, create_helper, dots, fixture, place, register


ALPHA, BETA = "Worker Scope Alpha", "Worker Scope Beta"
OTHER_NODE = fixture.n + "SlotBody/body:common/node:native"
PROJECT_B = fixture.case / "second-project"


def prepare():
    shutil.copytree(fixture.project, PROJECT_B, ignore=shutil.ignore_patterns(".confectory", ".build"))
    (fixture.storage / "projects.json").write_text(json.dumps([
        {"path": str(project / "project.cproj"), "title": title, "description": ""}
        for project, title in ((fixture.project, ALPHA), (PROJECT_B, BETA))
    ]))
    for option in ("CONFECTORY_DEV_PUBLIC_CHAT_LOOPBACK", "CONFECTORY_TEST_PUBLIC_CHAT_RELAY"):
        fixture.env.pop(option, None)


def home(page):
    page.get_by_role("button", name="Confectory 홈으로", exact=True).click()
    expect(page.locator(".home-grid")).to_be_visible()


def open_project(page, title):
    page.locator(".project-card").filter(has=page.get_by_role("heading", name=title, exact=True)).locator("[data-enter]").click()
    expect(page.locator("#title")).to_contain_text(title)
    fixture.idle()
    return fixture.state()["projectId"]


def journal(directory, project, helper, key, status, node, goal):
    # The product reads the existing WorkerTasks envelope, as in the offline Battle Log fixture.
    worker = "worker-" + key
    path = directory / ".confectory" / "ai-development" / "helpers" / hashlib.sha256(helper.encode()).hexdigest()[:16] / "tasks.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({
        "schema": 1, "project": project, "owner": "local-user", "chief": helper,
        "tasks": {key: {
            "task": key, "worker": worker, "ownerHelper": helper, "project": project, "status": status,
            "specification": {"kind": "blueprint-node", "goal": goal,
                              "blueprintNode": {"assignment": {"id": node}}},
        }},
        "commands": {}, "leases": {}, "journal": [], "chiefJournal": [],
    }))
    expected_id = hashlib.sha256(f"{key}\n{worker}\n{helper}".encode()).hexdigest()
    return path, expected_id


def await_observation(project, *ids):
    for _ in range(150):
        state = fixture.state()
        observed = {worker["id"]: worker for worker in state["assignmentWorkers"]}
        if state["projectId"] == project and set(observed) == set(ids):
            assert state["workers"] == []
            assert not state["planningOwnerAvailable"] and not state["aiOwnerAvailable"]
            return observed
        time.sleep(.05)
    raise AssertionError(f"The actual Worker journal projection did not observe {ids!r}")


def check_dot(page, helper, observed, status, tone, other_node):
    profile = card(page, helper)
    expect(dots(profile)).to_have_count(1)
    dot = profile.locator(f'[data-worker="{observed["id"]}"]')
    expect(dot).to_have_class(re.compile(r"\b" + tone + r"\b"))
    assert dot.evaluate("(element) => element.tagName") == "SPAN"
    dot.hover()
    tip = dot.get_by_role("tooltip")
    expect(tip).to_be_visible()
    expect(tip.locator("strong")).to_have_text(status)
    expect(tip.locator(".worker-assigned-node")).to_have_text(observed["assignedNode"])
    expect(tip).not_to_contain_text(other_node)
    page.mouse.move(1200, 40)
    expect(tip).to_be_hidden()
    return dot


def exercise():
    prepare()
    beta_sources = {path: path.read_bytes() for path in PROJECT_B.iterdir() if path.is_file()}
    fixture.start(0)
    page = fixture.page = fixture.setup()
    register(page)
    first = create_helper("표시 검증 도우미 A")
    second = create_helper("표시 검증 도우미 B")
    place(page, first, second)
    alpha = fixture.state()["projectId"]
    home(page)
    beta = open_project(page, BETA)
    assert beta != alpha
    place(page, first, second)
    page.close()
    fixture.stop()

    left, left_id = journal(fixture.project, alpha, first, "alpha-ready", "ready", NODE, "첫 노드의 로컬 작업")
    right, right_id = journal(fixture.project, alpha, second, "alpha-cancelled", "cancelled", OTHER_NODE, "두 번째 노드의 로컬 작업")
    other, other_id = journal(PROJECT_B, beta, first, "beta-error", "error", OTHER_NODE, "별도 프로젝트 작업")
    files = {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in (left, right, other)}

    fixture.start(1)
    page = fixture.page = fixture.setup()
    observed = await_observation(alpha, left_id, right_id)
    assert observed[left_id]["ownerHelper"] == first and observed[left_id]["assignedNode"] == NODE
    assert observed[right_id]["ownerHelper"] == second and observed[right_id]["assignedNode"] == OTHER_NODE
    fixture.checked("Actual journal reader finds two distinct placed Helper records without a live Worker owner")
    check_dot(page, first, observed[left_id], "ready", "waiting", OTHER_NODE)
    old = check_dot(page, second, observed[right_id], "cancelled", "problem", NODE)
    old.hover()
    home(page)
    expect(page.locator(".helper-profile-workers [data-worker]")).to_have_count(0)
    assert await_observation("") == {}
    assert open_project(page, BETA) == beta
    observed_beta = await_observation(beta, other_id)
    expect(dots(card(page, second))).to_have_count(0)
    check_dot(page, first, observed_beta[other_id], "error", "problem", NODE)
    expect(old).to_have_count(0)
    home(page)
    assert open_project(page, ALPHA) == alpha
    check_dot(page, second, await_observation(alpha, left_id, right_id)[right_id], "cancelled", "problem", NODE)

    assert all(path.read_bytes() == data and path.stat().st_mtime_ns == when for path, (data, when) in files.items())
    fixture.originals()
    assert {path: path.read_bytes() for path in PROJECT_B.iterdir() if path.is_file()} == beta_sources
    assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
    assert not {row.get("invoke", {}).get("endpoint") for row in fixture.traffic} & {
        "nodeTask", "startAI", "prepareWorker", "executeProject", "selectWorker", "dispatchWorker",
    }
    fixture.checked("Hover closes and an active-project switch clears stale dots, without touching the original journals or starting work")


if __name__ == "__main__":
    try:
        with sync_playwright() as playwright, playwright.chromium.launch(
                executable_path="/usr/bin/chromium", args=["--no-sandbox", "--disable-gpu"],
                ignore_default_args=["--disable-dev-shm-usage"]) as browser:
            fixture.browser = browser
            expect.set_options(timeout=7500)
            exercise()
    finally:
        fixture.stop()
