"""Toggle the local 3D actor appearance without changing the observed job or selection."""

import re
import uuid

from playwright.sync_api import expect, sync_playwright

from v821_helper_character_visibility_ui import close, show_characters
from v821_helper_worker_tooltip_ui import AGENT, NODE, call, card, dot, fixture, place, register


HELPER = "작업실 표시 도우미"
DRAFT = "작업실에서도 전송하지 않은 대화"


def current_job(task):
    return next(row for row in fixture.state()["assignmentWorkers"] if row["id"] == task)


def open_office(page):
    workspace = page.locator("#workspace")
    office = workspace.locator(".voxel-office")
    if not office.is_visible():
        page.get_by_role("button", name="아이소메트릭 Workspace", exact=True).click()
    expect(workspace).to_have_attribute("data-office-renderer", "ready")
    expect(office).to_be_visible()
    return office


def observe_draws(page):
    # Sample real main-pass draws for the existing pick IDs. This leaves the scene,
    # renderer and native owner state unchanged and distinguishes boxes from textures.
    page.evaluate("""async () => {
      const {Mesh, Vector3} = await import('/workspace-3d/assets/three.module-0.160.1.js');
      const before = Mesh.prototype.onBeforeRender;
      window.officeActorDraws = {};
      Mesh.prototype.onBeforeRender = function (renderer, scene, camera, geometry, material, group) {
        before.call(this, renderer, scene, camera, geometry, material, group);
        const pick = this.userData.pick;
        if (!['helper', 'worker'].includes(pick?.kind) || renderer.getRenderTarget() !== null
            || !renderer.domElement.closest('.voxel-office')) return;
        const style = material.map ? 'textured' : 'plain';
        const rect = renderer.domElement.getBoundingClientRect();
        const point = this.getWorldPosition(new Vector3()).project(camera);
        (window.officeActorDraws[pick.id] ??= {})[style] = {
          x: rect.left + (point.x + 1) * rect.width / 2,
          y: rect.top + (1 - point.y) * rect.height / 2,
        };
      };
    }""")


def assert_draws(page, ids, style):
    opposite = "plain" if style == "textured" else "textured"
    page.evaluate("() => { window.officeActorDraws = {}; }")
    page.wait_for_function(
        "([ids, style]) => ids.every(id => window.officeActorDraws[id]?.[style])",
        arg=[ids, style],
        timeout=30000,
    )
    samples = page.evaluate("() => window.officeActorDraws")
    if style == "plain":
        assert all(opposite not in samples[id] for id in ids), samples
    return samples


def select_worker(page, office, task):
    page.locator("#worker-finder-bubble").click()
    finder = page.locator("#workspace-find-panel")
    expect(finder).to_have_attribute("data-office", "true")
    field = finder.get_by_role("searchbox")
    field.fill("SlotBody")
    row = finder.locator(".workspace-find-worker")
    expect(row).to_have_count(1)
    expect(row).to_contain_text("배정 대기")
    expect(row).to_contain_text(task[:12])
    field.press("Enter")
    expect(finder).to_have_count(0)
    name = office.locator("[data-office-radial-name]")
    expect(name).to_contain_text(task[:12])
    name.press("Enter")
    inspector = office.locator(".office-inspector")
    expect(inspector).to_be_visible()
    expect(inspector.locator("[data-worker-job-state]")).to_have_text("배정 대기")
    return inspector


def exercise():
    fixture.start(0)
    page = fixture.page = fixture.setup()
    register(page)
    helper = call("helperGlobal", action="create", creationId=uuid.uuid4().hex, name=HELPER,
                  personality="오프라인 표시 시험", speciality="실제 작업 위치 확인", agent=AGENT)["helper"]
    place(page, helper)
    plan = call("nodeTask", action="inspect", node=NODE)
    task = call("nodeTask", action="assign", node=NODE, assignmentHash=plan["assignmentHash"],
                commandID=uuid.uuid4().hex, rationale="Existing local Worker observation")["task"]
    office = open_office(page)
    observe_draws(page)
    label = office.locator(".office-worker-label[data-native-task]")
    expect(label).to_have_count(1)
    expect(label).to_have_attribute("data-native-status", "ready")
    native_task = label.get_attribute("data-native-task")
    assert native_task and native_task != task
    job = current_job(native_task)
    assert job["ownerHelper"] == helper and job["assignedNode"] == NODE and job["status"] == "ready"
    worker = label.get_attribute("data-office-id")
    assert worker
    assert_draws(page, [helper, worker], "textured")
    inspector = select_worker(page, office, native_task)
    expect(inspector.locator(".office-character-activity")).to_be_visible()
    original_inspector = inspector.element_handle()
    expect(office).to_have_class(re.compile(r"\bis-following\b"))

    show_characters(page, False)
    expect(office).to_have_class(re.compile(r"\bis-neutral-actors\b"))
    expect(office).to_have_class(re.compile(r"\bis-following\b"))
    expect(inspector.locator(".office-character-activity")).to_be_hidden()
    expect(inspector.locator("[data-worker-job-state]")).to_have_text("배정 대기")
    assert original_inspector.evaluate("(element) => element.isConnected && !element.hidden")
    assert_draws(page, [helper, worker], "plain")
    expect(label).to_have_attribute("aria-label", f"{HELPER} · Worker {native_task[:12]} · 배정 대기 · SlotBody")
    assert current_job(native_task) == job
    fixture.checked("The actual 3D draw switches from a voxel to a neutral marker without resetting the selected and followed Worker")

    office.locator("[data-office-radial-name]").press("Escape")
    draws = assert_draws(page, [worker], "plain")
    marker = draws[worker]["plain"]
    page.mouse.click(marker["x"], marker["y"])
    expect(office.locator("[data-office-radial-name]")).to_contain_text(native_task[:12])
    office.locator("[data-office-radial-name]").press("Escape")
    select_worker(page, office, native_task)
    office.locator("[data-office-radial-name]").press("Escape")
    expect(page.locator(".home-side .is-project-main")).to_have_attribute("data-helper", helper)
    expect(page.locator(f'#participant-agent [data-agent="{AGENT}"]')).to_be_visible()
    profile = card(page, helper)
    compose = profile.get_by_role("textbox", name="Helper 대화 입력", exact=True)
    expect(compose).to_be_enabled()
    compose.fill(DRAFT)
    expect(profile.locator("[data-helper-send]")).to_be_enabled()
    close(profile)
    expect(card(page, helper).get_by_role("textbox", name="Helper 대화 입력", exact=True)).to_have_value(DRAFT)
    dot(card(page, helper), task).click()
    task_window = page.locator('.window[data-key="worker"]')
    expect(task_window.locator("h2")).to_have_text(task)
    expect(task_window).to_contain_text(NODE)
    page.get_by_role("button", name="패널 Workspace", exact=True).click()
    expect(task_window.get_by_role("button", name="작업 전 검토", exact=True)).to_be_visible()
    task_window.get_by_role("button", name="창 닫기", exact=True).click()
    office = open_office(page)
    expect(office).to_have_class(re.compile(r"\bis-neutral-actors\b"))
    assert current_job(native_task) == job
    fixture.checked("The neutral Worker remains selectable on the canvas and in search; the existing task window and Helper chat work")

    fixture.pending()
    page.close()
    fixture.stop()
    fixture.start(1)
    page = fixture.page = fixture.setup()
    office = open_office(page)
    expect(office).to_have_class(re.compile(r"\bis-neutral-actors\b"))
    observe_draws(page)
    inspector = select_worker(page, office, native_task)
    expect(inspector.locator(".office-character-activity")).to_be_hidden()
    assert_draws(page, [worker], "plain")
    show_characters(page, True)
    expect(office).not_to_have_class(re.compile(r"\bis-neutral-actors\b"))
    expect(inspector.locator(".office-character-activity")).to_be_visible()
    assert_draws(page, [worker], "textured")
    assert current_job(native_task)["assignedNode"] == NODE
    fixture.checked("Cold reopen retains neutral appearance, real job lookup, and the original textured actor when re-enabled")

    fixture.originals()
    assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
    forbidden = {"prepareAI", "startAI", "prepareWorker", "runProject", "editDraft", "confirmDraft"}
    assert not forbidden.intersection(row["invoke"]["endpoint"] for row in fixture.traffic if "invoke" in row)


if __name__ == "__main__":
    try:
        with sync_playwright() as playwright, playwright.chromium.launch(
            executable_path="/usr/bin/chromium",
            args=["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
            ignore_default_args=["--disable-dev-shm-usage"],
        ) as browser:
            fixture.browser = browser
            expect.set_options(timeout=30000)
            exercise()
    finally:
        fixture.stop()
