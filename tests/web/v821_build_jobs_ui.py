"""Check the visible Build Jobs tool against independently owned Linux builds and Run."""

from contextlib import contextmanager
import fcntl
import json
import time

from playwright.sync_api import expect, sync_playwright

from editor_navigation import choose_project_tool
import v666_workspace_finder_fixture as fixture


TITLES = ("Build fixture One", "Build fixture Two")
MARKERS = [path.parent / "run-marker" for path in fixture.projects]


def seed():
    for project, marker in zip(fixture.projects, MARKERS):
        body = project.parent / "Main.csbody"
        text = body.read_text(encoding="utf-8")
        body.write_text(f'System.IO.File.AppendAllText({json.dumps(str(marker))},"run\\n");\n' + text,
                        encoding="utf-8")
        fixture.before[str(body)] = body.read_bytes()
    profile = fixture.root / "profile"
    profile.mkdir()
    (profile / "projects.json").write_text(json.dumps([
        {"path": str(project), "title": title, "description": ""}
        for project, title in zip(fixture.projects, TITLES)
    ]), encoding="utf-8")


@contextmanager
def hold_source_lease(project):
    # The existing Linux test lease is the same FileStream lock used by the real build worker.
    path = project.parent / ".confectory" / "source-transaction.lock"
    path.parent.mkdir(exist_ok=True)
    with path.open("a+b") as lease:
        fcntl.flock(lease, fcntl.LOCK_EX)
        yield


def wait_state(page, condition):
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        state = fixture.state()
        if condition(state):
            return state
        page.wait_for_timeout(100)
    raise AssertionError((state.get("executionState"), state.get("buildJobs")))


def open_builds(page):
    choose_project_tool(page, "빌드 작업")
    window = page.locator('.window[data-key="builds"]')
    expect(window).to_be_visible()
    return window


def enter_project(page, title):
    page.locator(".brand").click()
    expect(page.locator(".home-grid")).to_be_visible()
    page.locator(".project-card").filter(
        has=page.get_by_role("heading", name=title, exact=True)
    ).locator("[data-enter]").click()
    expect(page.locator("#title")).to_contain_text(title)


def receipt(project, job):
    path = project.parent / ".confectory" / "build-jobs" / job / "job.json"
    return json.loads(path.read_bytes())


def check_builds(page):
    first_project, second_project = fixture.projects
    first_marker, second_marker = MARKERS
    first_scope = fixture.state()["projectId"]
    panel = open_builds(page)
    result = panel.locator("[data-build-result-state]")
    start = panel.get_by_role("button", name="빌드만", exact=True)
    stop = panel.get_by_role("button", name="이 빌드 중지", exact=True)

    start.click()
    expect(result).to_have_text("빌드 완료", timeout=60000)
    initial = fixture.state()
    success = initial["buildJobs"][-1]["job"]
    assert initial["executionState"] == "idle" and not first_marker.exists()
    assert receipt(first_project, success)["state"] == "built"
    panel.get_by_role("button", name="기록된 파일 검증", exact=True).click()
    expect(panel.locator("[data-build-artifacts]")).to_contain_text("기록된 파일 일치")
    fixture.checked("Standalone UI Build compiles and verifies its own artifacts without running the project")

    with hold_source_lease(first_project):
        start.click()
        expect(result).to_have_text("소스 잠금 대기")
        pending = fixture.state()["buildJobs"][-1]["job"]
        pending_row = panel.locator(f'[data-build-job="{pending}"]')
        earlier_row = panel.locator(f'[data-build-job="{success}"]')
        earlier_row.click()
        expect(earlier_row).to_have_class("selected")
        expect(panel.locator("[data-build-identity]")).to_contain_text(success)
        expect(start).to_be_disabled()
    wait_state(page, lambda state: any(
        row["job"] == pending and row["state"] == "built" for row in state["buildJobs"]
    ))
    assert receipt(first_project, pending)["state"] == "built"
    expect(pending_row).to_contain_text("빌드 완료")
    expect(earlier_row).to_have_class("selected")
    expect(panel.locator("[data-build-identity]")).to_contain_text(success)
    expect(start).to_be_enabled()
    pending_row.click()
    expect(panel.locator("[data-build-identity]")).to_contain_text(pending)
    expect(result).to_have_text("빌드 완료")
    expect(stop).to_be_disabled()
    fixture.checked("Compiler terminal state refreshes the non-selected job and re-enables Build without changing the inspected result")

    enter_project(page, TITLES[1])
    second_scope = fixture.state()["projectId"]
    assert second_scope != first_scope and not fixture.state()["buildJobs"]
    second_panel = open_builds(page)
    expect(second_panel.locator("[data-build-job]")).to_have_count(0)
    second_panel.get_by_role("button", name="빌드만", exact=True).click()
    expect(second_panel.locator("[data-build-result-state]")).to_have_text("빌드 완료", timeout=60000)
    second = fixture.state()["buildJobs"][-1]["job"]
    second_record = receipt(second_project, second)
    assert not second_marker.exists()

    enter_project(page, TITLES[0])
    panel = open_builds(page)
    assert fixture.state()["projectId"] == first_scope
    expect(panel.locator(f'[data-build-job="{second}"]')).to_have_count(0)

    # Start one real Run, then cancel only the separate Build worker at the actual lease.
    page.locator("#run").click()
    run = page.locator(".run-window:visible")
    expect(run.locator(".caption strong")).to_have_text("실행 중", timeout=60000)
    key = run.get_attribute("data-key")
    running = fixture.data(key)
    handle = running["handle"]

    def assert_running():
        current_run = fixture.run("read", running)
        assert current_run["handle"] == handle and current_run["state"] == "running"

    assert_running()
    wait_state(page, lambda _: first_marker.exists())
    page.get_by_role("tab", name="Workspace", exact=True).click()
    panel = open_builds(page)
    with hold_source_lease(first_project):
        start.click()
        expect(result).to_have_text("소스 잠금 대기")
        waiting = fixture.state()["buildJobs"][-1]
        assert waiting["phase"] == "waiting-for-lease"
        cancelled = waiting["job"]
        stop.click()
        expect(result).to_have_text("중지됨")
        expect(stop).to_be_disabled()
        assert_running()
        stopped_record = receipt(first_project, cancelled)
        assert stopped_record["state"] == "stopped" and not stopped_record.get("key")
    assert first_marker.read_text() == "run\n" and not second_marker.exists()
    fixture.checked("Existing Stop retires the selected build in the real compiler journal while the same Run remains alive")

    # A failed build must not report the verification from the earlier successful job.
    body = first_project.parent / "Main.csbody"
    original = body.read_bytes()
    body.write_bytes(original + b"\nthis is deliberately invalid C#;\n")
    try:
        start.click()
        expect(result).to_have_text("실패", timeout=60000)
        expect(panel.locator("[data-build-error]")).not_to_have_text("")
        expect(panel.locator("[data-build-artifacts]")).to_have_text("")
        failed = fixture.state()["buildJobs"][-1]["job"]
        failed_record = receipt(first_project, failed)
        assert failed_record["state"] == "failed" and not failed_record.get("key")
        assert receipt(second_project, second) == second_record
        assert_running()
    finally:
        body.write_bytes(original)
    fixture.checked("Actual compiler failure has its own result; another project's successful build and Run markers are preserved")

    assert first_marker.read_text() == "run\n" and not second_marker.exists()
    assert receipt(first_project, cancelled) == stopped_record
    assert receipt(second_project, second) == second_record
    assert [row["input"]["job"] for row in fixture.requests if row["endpoint"] == "stopBuild"] == [cancelled]
    page.locator(f'[data-window-tab="{key}"]').click()
    run.get_by_role("button", name="중단", exact=True).click()
    expect(run.get_by_role("button", name="재생", exact=True)).to_be_enabled()
    assert fixture.run("read", running)["state"] == "stopped"
    fixture.original()
    assert not fixture.errors and not fixture.external


def run():
    seed()
    try:
        fixture.start(0)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
            page = fixture.setup(browser)
            page.set_viewport_size({"width": 1850, "height": 1180})
            try:
                check_builds(page)
            except Exception:
                page.screenshot(path=str(fixture.root / "failure.png"))
                raise
            finally:
                browser.close()
    finally:
        print("BUILD_JOBS_FIXTURE", fixture.root)
        fixture.save_evidence()
        fixture.stop()


if __name__ == "__main__":
    run()
