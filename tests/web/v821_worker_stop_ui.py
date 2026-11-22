"""Stop a genuinely started local Worker without applying a project source change."""
import json
import select
import shutil
import socket
import threading
import uuid

from playwright.sync_api import expect, sync_playwright

import v821_worker_review_binding_ui as flow

fixture = flow.fixture


def owned_journal():
    file, = fixture.project.glob(".confectory/ai-development/**/tasks.json")
    return json.loads(file.read_text())


def gate_responses(owned):
    """Keep the targeted HTTP request open, with no tool call or fake owner events."""
    entered = threading.Event()
    retired = threading.Event()
    release = threading.Event()
    base = owned.server.RequestHandlerClass

    class Handler(base):
        def do_POST(self):
            if owned.target != flow.SECOND:
                return super().do_POST()
            try:
                assert self.path == "/responses" and self.headers.get("Authorization") is None
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                request = json.loads(body["input"][0]["content"])
                assert request["task"]["specification"]["blueprintNode"]["assignment"]["id"] == flow.SECOND
                assert request["kind"] == "worker-task" and body["store"] is False
                owned.requests.append(body)
                entered.set()
                while not release.is_set():
                    readable, _, _ = select.select([self.connection], [], [], .1)
                    if readable:
                        assert self.connection.recv(1, socket.MSG_PEEK) == b""
                        retired.set()
                        break
            except Exception as error:
                owned.errors.append(repr(error))
            finally:
                self.close_connection = True

    owned.server.RequestHandlerClass = Handler
    return entered, retired, release


def exercise(owned, entered, retired):
    second_project = fixture.case / "other-project"
    shutil.copytree(fixture.project, second_project)
    fixture.start(0)
    page = fixture.page = fixture.setup()
    page.set_viewport_size({"width": 1660, "height": 1280})
    helper = flow.setup_helper(page, owned)
    prior = flow.stage_result(owned, flow.FIRST, flow.FIRST_SOURCE)
    review_window, token = flow.review(page, helper, prior, flow.FIRST, flow.FIRST_SOURCE)
    note = "기존 Worker의 보존할 검토 근거"
    review_window.locator("#worker-goal-evidence").fill(note)
    before = fixture.state()
    prior_task = owned_journal()["tasks"][prior]
    assert before["review"]["token"] == token

    owned.target = flow.SECOND
    plan = flow.call("nodeTask", action="inspect", node=flow.SECOND)
    task = flow.call("nodeTask", action="assign", node=flow.SECOND, assignmentHash=plan["assignmentHash"],
                     commandID=uuid.uuid4().hex, rationale="Explicit local Worker stop fixture")["task"]
    flow.call("selectWorker", task=task)
    flow.call("prepareWorker", task=task)
    preview = fixture.state()["aiPreview"]
    for requirement in preview["requirements"]:
        flow.call("permission", token=preview["token"], id=requirement["id"], approved=True)
    flow.call("startAI", token=preview["token"])
    assert entered.wait(15) and not retired.is_set() and not owned.errors, owned.errors

    page.locator(f'.home-side [data-helper="{helper}"]').click()
    page.locator(f'.participant-expanded-card [data-worker="{task}"]').click()
    panel = page.locator('.window[data-key="worker"]')
    expect(panel.locator("h2")).to_have_text(task)
    status = panel.locator(".window-content > p").first
    expect(status).to_contain_text("running")
    live = owned_journal()
    assert live["tasks"][task]["status"] == "running"
    assert live["tasks"][task]["run"] and live["tasks"][task]["worker"]
    assert any(event["task"] == task and event["kind"] == "worker-started" for event in live["journal"])
    fixture.checked("실행 ID가 있는 Worker가 실제 로컬 HTTP 요청을 시작하고 응답을 기다린다")

    request_count = len(owned.requests)
    stop = panel.locator("#worker-stop")
    expect(stop).to_be_enabled()
    stop.click()
    expect(status).to_contain_text("cancelled")
    assert retired.wait(10), owned.errors
    journal = owned_journal()
    events = [event["kind"] for event in journal["journal"] if event["task"] == task]
    assert events.count("cancel-requested") == events.count("worker-cancelled") == 1, events
    assert events.index("worker-started") < events.index("cancel-requested") < events.index("worker-cancelled")
    after = fixture.state()
    assert after["selectedWorkerId"] == task
    assert next(row for row in after["workers"] if row["id"] == task)["status"] == "cancelled"
    assert journal["tasks"][prior] == prior_task
    assert after["review"] == before["review"]
    expect(review_window.locator("#worker-goal-evidence")).to_have_value(note)
    fixture.originals()
    assert not flow.receipts()
    fixture.checked("작업 소유자의 취소 기록과 로컬 요청 종료 뒤 화면에 취소 상태가 보인다")

    fixture.idle()
    expect(page.locator("#status")).to_contain_text("Worker 중지 확인됨")
    assert sum("Selected Worker stopped;" in message for message in after["logs"]) == 1
    expect(stop).to_be_disabled(timeout=4000)
    calls = [row["invoke"] for row in fixture.traffic if row.get("invoke", {}).get("endpoint")
             in ("stopWorker", "cancelReadyWorker", "skipProposals")]
    assert [(call["endpoint"], call["input"]["task"]) for call in calls] == [("stopWorker", task)]
    assert len(owned.requests) == request_count and not owned.errors
    assert owned_journal() == journal
    fixture.checked("종료된 작업은 다시 중지를 보낼 수 없고 다른 Worker 및 현재 검토 내용은 보존된다")

    fixture.pending()
    page.close()
    fixture.stop()
    fixture.env["CONFECTORY_WEB_PROJECT"] = str(second_project / "project.cproj")
    fixture.start(1)
    page = fixture.page = fixture.setup()
    fixture.idle()
    other = fixture.state()
    assert other["projectId"] != after["projectId"] and not other["workers"] and other["review"] is None
    assert not list(second_project.rglob("tasks.json"))
    for name, content in fixture.original.items():
        assert (second_project / name).read_bytes() == content
    fixture.originals()
    assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
    assert len(owned.requests) == request_count
    fixture.checked("같은 선언을 가진 별도 프로젝트에는 중지 기록이나 검토가 섞이지 않는다")


if __name__ == "__main__":
    flow.add_second_source()
    owned = flow.OwnedResponses(flow.FIRST, flow.FIRST_SOURCE)
    entered, retired, release = gate_responses(owned)
    try:
        with sync_playwright() as playwright:
            with playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
                fixture.browser = browser
                exercise(owned, entered, retired)
    finally:
        release.set()
        fixture.stop()
        owned.close()
        (fixture.case / "worker-stop-evidence.json").write_text(json.dumps({
            "checks": fixture.checks, "errors": fixture.errors, "ownedErrors": owned.errors,
            "transportRetired": retired.is_set(),
        }, ensure_ascii=False, indent=2))
        print("evidence:", fixture.case)
