"""Select two real local Worker results through the ordinary Review/Adopt UI."""
import json
import time
import uuid

from playwright.sync_api import expect, sync_playwright

from owned_responses import OwnedResponses
import v536_wide_mixed as fixture

FIRST = fixture.n + "SlotBody/body:common/node:body"
SECOND = fixture.n + "ReviewBody/body:common/node:body"
FIRST_SOURCE = "slotCount=amount+2;slotReady=true;return amount+4;"
SECOND_SOURCE = "return amount+9;"


def add_second_source():
    feature, implementation = fixture.n + "ReviewTarget", fixture.n + "ReviewBody"
    declaration = f"function {feature} (long amount) -> long {{}}"
    candidate = fixture.metadata("blueprintPrepareFeature", id=feature, text=declaration,
                                 implementation=implementation, graphPath="Review.graph.json",
                                 nodePath="Review.node.json")
    graph = candidate["graph"]
    nodes = fixture.metadata("featureBlueprintNodes", featureSource=declaration, graph=graph)["nodes"]
    record = {"schema": 1, "node": "body", "source": "return amount+1;",
              "definitionHash": next(node for node in nodes if node["id"] == "body")["definitionHash"]}
    for file, content in {
        "ReviewTarget.celem": declaration.replace("{}", f"{{provide {feature} with {implementation};}}"),
        "ReviewBody.celem": candidate["implementation"],
        "Review.graph.json": json.dumps(graph),
        "Review.node.json": json.dumps(record),
    }.items():
        (fixture.project / file).write_text(content)
    manifest = fixture.project / "project.cproj"
    manifest.write_text(manifest.read_text().replace("registry Confectory.Build.DotNet",
        'element ReviewTarget function "ReviewTarget.celem";'
        'element ReviewBody implementation "ReviewBody.celem";registry Confectory.Build.DotNet'))
    fixture.original = {path.name: path.read_bytes() for path in fixture.project.iterdir() if path.is_file()}


def call(endpoint, **body):
    return fixture.invoke(endpoint, body)["result"]["result"]


def setup_helper(page, owned):
    page.locator("#add-agent").click()
    dialog = page.get_by_role("dialog", name="Agent 추가", exact=True)
    dialog.get_by_role("button", name="OpenAI Responses", exact=True).click()
    for field, value in (("model", "worker-review-loopback"), ("endpoint", owned.endpoint),
                         ("credentialReference", "")):
        dialog.locator(f'[data-connection-field="{field}"]').fill(value)
    dialog.locator("[data-agent-register]").click()
    expect(dialog.locator("[data-agent-registration-state]")).to_contain_text("Agent 등록됨")
    dialog.locator("[data-connection-cancel]").click()
    helper = call("helperGlobal", action="create", creationId=uuid.uuid4().hex,
                  name="검토 도우미", personality="Local fixture", speciality="Local fixture",
                  agent="Confectory.Agent.Responses::Connection")["helper"]
    page.locator("#add-helper").click()
    placement = page.get_by_role("dialog", name="프로젝트 도우미 배치", exact=True)
    placement.locator(f'[data-project-helper="{helper}"]').click()
    placement.locator('button[type="submit"]').click()
    expect(placement).to_have_count(0)
    call("bindHelperAgent", helper=helper)
    return helper


def stage_result(owned, node, source):
    owned.target, owned.node_source = node, source
    initial_requests = len(owned.requests)
    plan = call("nodeTask", action="inspect", node=node)
    task = call("nodeTask", action="assign", node=node, assignmentHash=plan["assignmentHash"],
                commandID=uuid.uuid4().hex, rationale="Explicit local Worker Review fixture")["task"]
    call("selectWorker", task=task)
    call("prepareWorker", task=task)
    preview = fixture.state()["aiPreview"]
    assert preview["requirements"] and len(owned.requests) == initial_requests
    for requirement in preview["requirements"]:
        call("permission", token=preview["token"], id=requirement["id"], approved=True)
    call("startAI", token=preview["token"])
    deadline = time.monotonic() + 50
    while time.monotonic() < deadline:
        state = fixture.state()
        worker = next(row for row in state["workers"] if row["id"] == task)
        if worker["status"] == "awaiting-verification" and worker["changedIds"] == [node]:
            assert initial_requests + 3 == len(owned.requests) and not owned.errors, owned.errors
            return task
        assert worker["status"] not in ("error", "cancelled", "interrupted"), worker
        time.sleep(.05)
    raise AssertionError((worker, owned.errors))


def review(page, helper, task, node, source):
    page.locator(f'.home-side [data-helper="{helper}"]').click()
    page.locator(f'.participant-expanded-card [data-worker="{task}"]').click()
    worker = page.locator('.window[data-key="worker"]')
    expect(worker.locator("h2")).to_have_text(task)
    worker.locator(f'[data-worker-source="{node}"]').check()
    worker.locator("#worker-review").click()
    review_window = page.locator('.window[data-key="worker-review"]')
    expect(review_window.locator("#worker-adopt")).to_be_enabled()
    expect(review_window.locator("details")).to_have_count(1)
    expect(review_window.locator("summary")).to_contain_text(node)
    review_window.locator("summary").click()
    expect(review_window.locator("pre").last).to_contain_text(source)
    observed = fixture.state()
    assert observed["selectedWorkerId"] == task
    assert [item["id"] for item in observed["review"]["units"]] == [node]
    return review_window, observed["review"]["token"]


def receipts():
    return list(fixture.project.glob(".confectory/ai-development/**/adoption-records/*.json"))


def exercise(owned):
    fixture.start(0)
    first_view = fixture.page = fixture.setup()
    first_view.set_viewport_size({"width": 1660, "height": 1280})
    helper = setup_helper(first_view, owned)
    first = stage_result(owned, FIRST, FIRST_SOURCE)
    fixture.originals()
    assert not receipts()

    abandoned, _ = review(first_view, helper, first, FIRST, FIRST_SOURCE)
    abandoned.locator('[data-close]').first.click()
    expect(abandoned).to_be_hidden()
    fixture.originals()
    assert not receipts()
    fixture.checked("Worker Review의 취소는 두 원본이나 채택 기록을 바꾸지 않는다")

    old_review, old_token = review(first_view, helper, first, FIRST, FIRST_SOURCE)
    note = "충돌해도 보존해야 할 기존 검토 근거"
    old_review.locator("#worker-goal-evidence").fill(note)
    second = stage_result(owned, SECOND, SECOND_SOURCE)
    fixture.originals()
    assert not receipts()
    requests = len(owned.requests)
    fixture.checked("첫 검토가 열린 동안 다른 Worker가 별도 소스에 실제 초안을 준비한다")

    second_view = fixture.setup()
    second_view.set_viewport_size({"width": 1660, "height": 1280})
    current_review, new_token = review(second_view, helper, second, SECOND, SECOND_SOURCE)
    assert new_token != old_token
    fixture.originals()
    assert not receipts()
    fixture.checked("다른 편집기의 새 Worker 검토는 새 토큰을 얻으며 확정 전에는 원본을 고치지 않는다")

    first_view.bring_to_front()
    expect(old_review.locator("#worker-adopt")).to_be_disabled(timeout=5000)
    expect(old_review.locator("#worker-goal-evidence")).to_have_value(note)
    assert not receipts()
    fixture.originals()
    fixture.checked("오래된 검토는 채택이 비활성화되고 근거 입력과 두 원본이 보존된다")

    second_view.bring_to_front()
    current_review.locator("#worker-goal-evidence").fill(
        "Compared the exact second node and reviewed its recorded local change. Compiler validation only.")
    current_review.locator("#worker-adopt").click()
    expect(current_review).to_be_hidden(timeout=180000)
    state = fixture.state()
    assert {row["id"]: row["status"] for row in state["workers"]} == {
        first: "awaiting-verification", second: "completed",
    }
    assert next(row for row in state["workers"] if row["id"] == first)["changedIds"] == [FIRST]
    assert json.loads((fixture.project / "Review.node.json").read_text())["source"] == SECOND_SOURCE
    for name, before in fixture.original.items():
        if name != "Review.node.json":
            assert (fixture.project / name).read_bytes() == before, name
    record, = receipts()
    entries = json.loads(record.read_text())["records"]
    assert len(entries) == 1
    assert entries[0]["task"] == second and entries[0]["sourceIDs"] == [SECOND]
    assert len(owned.requests) == requests and not owned.errors
    assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
    fixture.checked("명시적 채택은 새로 검토한 두 번째 Worker 소스와 기록만 확정한다")


add_second_source()
owned = OwnedResponses(FIRST, FIRST_SOURCE)
try:
    with sync_playwright() as playwright:
        with playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
            fixture.browser = browser
            exercise(owned)
finally:
    fixture.stop()
    owned.close()
    (fixture.case / "worker-review-evidence.json").write_text(json.dumps({
        "checks": fixture.checks, "errors": fixture.errors,
        "loopbackRequests": len(owned.requests), "loopbackErrors": owned.errors,
    }, ensure_ascii=False, indent=2))
    print("evidence:", fixture.case)
