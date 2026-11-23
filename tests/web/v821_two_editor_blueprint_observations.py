"""Two local EditorHome processes sharing a project, with real Save and Review."""
import ast
from contextlib import contextmanager
import copy
import json
from pathlib import Path
import sys
import time

from playwright.sync_api import expect, sync_playwright

from editor_navigation import choose_project_tool, goto_editor

save_loss = sys.argv[3:4] == ["save-loss"]
sys.argv[3:4] = ["method-compound-order"]
fixture = Path(__file__).with_name("v821_frame_structure_ui.py")
statements = ast.parse(fixture.read_text()).body
setup = statements[:next(i for i, node in enumerate(statements) if isinstance(node, ast.Try))]
exec(compile(ast.Module(body=setup, type_ignores=[]), str(fixture), "exec"), globals())

SOURCE = f.project / "Pair.body.inner.node.json"
SOURCE_ID = t.graph + "/node:body/node:nest/node:inner"
GRAPH = f.project / t.graph_file
NOTE = "두 번째 편집기의 별도 미저장 설명"


class Editor:
    def __init__(self, number, browser):
        self.number = number
        self.browser = browser
        self.open(number)

    def open(self, index):
        profile = f.case / f"editor-{self.number}"
        profile.mkdir(exist_ok=True)
        old_env = f.env
        f.env = {**old_env, "CONFECTORY_HOME_STORAGE": str(profile),
                 "CONFECTORY_ENTRY_STORAGE": str(profile),
                 "CONFECTORY_MCP_DIRECTORY": str(profile / "instances")}
        keys = ("origin", "token", "url", "host", "log", "page")
        previous = {key: getattr(f, key, None) for key in keys}
        try:
            f.start(index)
            self.channel = {key: getattr(f, key) for key in keys[:-1]}
            self.page = self.browser.new_page(viewport={"width": 1900, "height": 1400})
            self.channel["page"] = self.page
            self.page.on("pageerror", lambda error: f.errors.append(str(error)))
            self.page.on("response", f.observe)
            self.page.route("**/*", self.route)
            goto_editor(self.page, self.channel["url"])
            expect(self.page.locator(".work-body")).to_be_visible()
            self.page.wait_for_function("() => typeof globalThis.confectoryFlushPresentation === 'function'")
        except Exception:
            f.stop()
            raise
        finally:
            f.env = old_env
            f.__dict__.update(previous)

    def route(self, route):
        if not route.request.url.startswith(self.channel["origin"] + "/"):
            f.external.append(route.request.url)
            route.abort()
        else:
            route.continue_()

    @contextmanager
    def active(self):
        previous = {key: getattr(f, key, None) for key in self.channel}
        f.__dict__.update(self.channel)
        try:
            yield
        finally:
            f.__dict__.update(previous)

    def close(self):
        with self.active():
            try:
                self.page.close()
            finally:
                f.stop()

    def restart(self, index):
        with self.active():
            f.pending()
        self.close()
        self.open(index)


def open_parent():
    f.idle()
    logic = panel().get_by_role("tab", name="논리 코드", exact=True)
    if logic.is_visible():
        logic.click()
    open_document()
    if panel().locator(".bp-breadcrumbs button").count():
        root_view()
    enter()


def prepare_independent_draft():
    f.page.locator("#workspace").click(button="right", position={"x": 1300, "y": 300})
    f.page.get_by_role("button", name="프로젝트 브라우저", exact=True).click()
    browser = f.page.locator('.window[data-key^="browser:project:"]')
    browser.get_by_role("button", name="기능", exact=True).click()
    browser.locator('[data-browser-control="object-query"]').fill("Slot")
    browser.locator('[data-browser-control="object-search"]').click()
    browser.locator(f'[data-object="{f.n}Slot"]').press("Enter")
    browser.locator("[data-close]").first.click()
    f.idle()
    f.page.locator("[data-operation=feature-author-open]").first.click()
    panel().get_by_role("tab", name="논리 코드", exact=True).click()
    doc().locator('[data-document-name="body"]').fill(NOTE)
    separate = pending()
    assert separate and any(row["text"] == NOTE for _, row in separate)
    panel().locator("[data-close]").first.click()
    return separate


def prepare_source(before, after):
    open_parent()
    doc().locator('[data-document-internal="nest"]').click()
    f.idle()
    panel().get_by_role("tab", name="논리 코드", exact=True).click()
    doc().locator('[data-document-code="inner"]').click()
    dialog = f.page.locator(".bp-script-dialog")
    field = dialog.locator("[data-code-source]")
    field.evaluate("""(element, text) => {
        const at = element.value.indexOf(text);
        if (at < 0) throw Error('Source marker missing');
        element.focus();
        element.setSelectionRange(at, at + text.length);
    }""", before)
    f.page.keyboard.insert_text(after)
    dialog.locator("[data-code-save]").click()
    expect(dialog).to_be_hidden()
    assert any(after in row["text"] for _, row in pending() if row.get("type") == "source")


def approve(window):
    advanced = window.locator("[data-review-advanced]")
    if advanced.get_attribute("aria-expanded") != "true":
        advanced.click()
    agreement = window.locator("[data-advanced-reviewed]")
    if agreement.count():
        agreement.check()
    expect(window.locator("#confirm")).to_be_enabled()


def publish_source():
    window = review()
    reviewed = f.state()["review"]
    changed = {row["id"] for row in reviewed["units"] if row["before"] != row["after"]}
    assert changed == {SOURCE_ID}, changed
    approve(window)
    window.locator("#confirm").click()
    expect(window).to_be_hidden(timeout=120000)
    f.idle()


def undo_shared_move():
    # Both editors use the same local checkpoint. The draft with the move and
    # its observed C# cannot be partially confirmed. Undo the fixture's move
    # explicitly in the publishing editor while the other Review stays open.
    choose_project_tool(f.page, "의미 편집 이력")
    history = f.page.locator('.window[data-key="history"]')
    expect(history.locator('[data-history-tip="undo"]')).to_contain_text(t.graph)
    history.locator('[data-history-move="undo"]').click()
    f.idle()
    assert read()["entry"] == "nest"
    history.locator("[data-close]").first.click()


def hold_preview():
    view = panel().locator(".function-native-preview")
    requests = set()
    held = {}

    def intercept(route):
        body = route.request.post_data_json
        if body.get("op") == "invoke" and body.get("endpoint") == "blueprint" and body["input"].get("action") == "nativePreview":
            requests.add(body["requestId"])
        response = route.fetch()
        for row in response.json().get("results", []):
            if not held and row.get("requestId") in requests:
                assert row["ok"] and '"body"' in row["result"]["diagnostics"]["members"], row.get("error")
                held.update(route=route, response=response)
                return
        route.fulfill(response=response)

    f.page.route("**/api/request", intercept)
    panel().get_by_role("tab", name="네이티브 미리보기", exact=True).click()
    deadline = time.monotonic() + 60
    while not held and time.monotonic() < deadline:
        f.page.wait_for_timeout(25)
        assert view.locator("[role=status]").text_content() == "생성 중…" or held, view.locator("[role=status]").text_content()
    assert held, "The successful original C# preview did not reach the transport"
    return view, held, intercept


def run_pair(publisher, late):
    with late.active():
        f.invoke("select", {"id": t.feature})
        f.invoke("saveDraft", {})
        checkpoint, = f.project.glob(".confectory/edit-workspaces/*/draft.json")
        separate = prepare_independent_draft()
        open_parent()

    publisher.restart(6)
    with publisher.active():
        prepare_source('"body"', '"publisher-one"')
    with late.active():
        view, held, intercept = hold_preview()
    try:
        with publisher.active():
            publish_source()
            assert '"publisher-one"' in json.loads(SOURCE.read_text())["source"]
    finally:
        with late.active():
            held["route"].fulfill(response=held["response"])
            f.page.unroute("**/api/request", intercept)
    saved_after_publish = checkpoint.read_bytes()
    with late.active():
        f.idle()
        expect(view.locator("[role=status]")).not_to_have_text("생성 중…")
        stale_displayed = '"body"' in view.locator("[data-native-members]").text_content()
        print("delayed old code displayed:", stale_displayed, flush=True)
        if not stale_displayed:
            expect(view.locator("[role=status]")).to_contain_text("원본 또는 저장된 초안이 바뀌었습니다")
            assert not view.locator("[data-native-body]").text_content()
        view.locator("[data-native-refresh]").click()
        expect(view.locator("[role=status]")).to_contain_text("실패")
        assert not view.locator("[data-native-body]").text_content()
        assert not view.locator("[data-native-members]").text_content()
        assert f.pending()["blueprint"] == separate
        assert checkpoint.read_bytes() == saved_after_publish
        assert all(path.read_bytes() == raw for path, raw in x.physical.items() if path != SOURCE)
    f.checked("A real previously successful preview is completed after the other editor publishes; a new stale observation is refused and private input is preserved.")

    late.restart(2)
    with late.active():
        assert f.pending()["blueprint"] == separate
        open_parent()
        doc().locator('[data-document-down="nest"]').click()
        f.idle()
        assert order() == moved_order, (order(), panel().locator(".bp-status").text_content())
        save()
        old_review = review()
        approve(old_review)
        previous_token = f.state()["review"]["token"]
        assert f.state()["review"]["status"] == "ready"

    publisher.restart(3)
    with publisher.active():
        undo_shared_move()
        prepare_source('"publisher-one"', '"publisher-two"')
        publish_source()
        assert '"publisher-two"' in json.loads(SOURCE.read_text())["source"]
    after_second_publish = checkpoint.read_bytes()
    saved = json.loads(after_second_publish)
    assert saved["version"] == 1
    clean_graph = next(row for row in saved["changes"] if row["id"] == t.graph)
    assert clean_graph["draft"] == clean_graph["original"] and not clean_graph.get("propertyObservations")
    assert clean_graph["authorSaveReceipt"]["ownedRoute"] is True
    assert GRAPH.read_bytes() == x.physical[GRAPH]
    with late.active():
        old_review.locator("#confirm").click()
        f.idle()
        assert (f.state()["review"] or {}).get("status") != "confirmed"
        assert checkpoint.read_bytes() == after_second_publish
        assert GRAPH.read_bytes() == x.physical[GRAPH]
        assert f.pending()["blueprint"] == separate
        if old_review.is_visible():
            old_review.locator("[data-reject]").click()
    f.checked("An existing move Review cannot write after the second source-only Confirm in the other editor.")

    late.restart(4)
    with late.active():
        assert f.pending()["blueprint"] == separate
        open_parent()
        assert order() == original_order
        doc().locator('[data-document-down="nest"]').click()
        f.idle()
        assert order() == moved_order
        fresh = review()
        current = f.state()["review"]
        print("fresh movement review:", current["status"], flush=True)
        assert current["status"] == "ready" and current["token"] != previous_token
        approve(fresh)
        fresh.locator("#confirm").click()
        expect(fresh).to_be_hidden(timeout=120000)
        f.idle()
        assert f.pending()["blueprint"] == separate
    late.restart(5)
    with late.active():
        open_parent()
        assert order() == moved_order and f.pending()["blueprint"] == separate
        panel().get_by_role("tab", name="네이티브 미리보기", exact=True).click()
        view = panel().locator(".function-native-preview")
        expect(view.locator("[data-native-members]")).to_contain_text('"publisher-two"')
        assert '"body"' not in view.locator("[data-native-members]").text_content()
        assert '"peer-inner"' not in view.locator("[data-native-members]").text_content()
    expected = copy.deepcopy(base)
    chosen(expected).update(entry="finish", edges=[edge("finish", "nest"), edge("nest", "exit:return")])
    assert json.loads(GRAPH.read_text()) == expected
    assert all(path.read_bytes() == raw for path, raw in x.physical.items() if path not in (GRAPH, SOURCE))
    x.build("two-editor-child-run", 10, "parent-tail\npublisher-two\ninside\npeer-inner\npeer-tail\nafter\n10")
    assert not f.errors and not f.external, (f.errors, f.external)
    assert not stale_displayed, "The late completed preview published superseded C# in the still-selected parent"


def run_save_loss(browser):
    checkpoint_dir = f.project / ".confectory" / "edit-workspaces"
    accepted_name = "저장 응답을 받지 못한 이름"
    later_name = "다른 창에서 확정한 이후 이름"
    private_name = "첫 창의 아직 저장하지 않은 이름"
    first = Editor(0, browser)
    try:
        with first.active():
            open_document()
            root_name = doc().locator('[data-document-name="after"]')
            root_name.fill(accepted_name)
            held = pending()
            assert len(held) == 1 and held[0][1]["text"] == accepted_name, held
            writes, queries, responses = {}, set(), {}

            def lose_save_replies(route):
                body = route.request.post_data_json
                if body.get("op") == "invoke" and body.get("endpoint") == "blueprint":
                    action = body.get("input", {}).get("action")
                    if action == "authorBatch":
                        writes[body["requestId"]] = body["input"]
                    if writes and action == "settledAuthorBatch":
                        queries.add(body["requestId"])
                response = route.fetch()
                payload = response.json()
                for row in payload.get("results", []):
                    request_id = row["requestId"]
                    if request_id in writes or request_id in queries:
                        responses[request_id] = copy.deepcopy(row)
                        row.clear()
                        row.update(requestId=request_id, ok=False, error={"code": "transport-interrupted"})
                route.fulfill(response=response, json=payload)

            f.page.route("**/api/request", lose_save_replies)
            try:
                save()
                assert len(writes) == 1 and queries.intersection(responses), (writes, queries)
                request_id, attempt = next(iter(writes.items()))
                assert responses[request_id]["ok"], responses[request_id]
                saved = next(checkpoint_dir.glob("*/draft.json"))
                accepted = json.loads(saved.read_bytes())
                unit = next(unit for unit in accepted["changes"] if unit["id"] == t.graph)
                assert unit["authorSaveReceipt"]["attempt"] == attempt["attempt"]
                assert next(node for node in json.loads(unit["draft"])["nodes"] if node["id"] == "after")["displayName"] == accepted_name
                assert all(dict(pending()).get(key) == value for key, value in held)
                x.original()
            finally:
                f.page.unroute("**/api/request", lose_save_replies)
            root_name.fill(private_name)
            private = pending()
            assert any(row.get("text") == private_name for _, row in private)
        f.checked("The real Save checkpoints exactly one attempt; only the browser's Save and settlement replies are lost.")

        second = Editor(1, browser)
        try:
            with second.active():
                open_document()
                expect(doc().locator('[data-document-name="after"]')).to_have_value(accepted_name)
                doc().locator('[data-document-name="after"]').fill(later_name)
                saved_in_second = save()
                assert any(row.get("result", {}).get("ok") for row in saved_in_second)
                assert not pending()
                window = review()
                reviewed = f.state()["review"]
                assert {row["id"] for row in reviewed["units"] if row["before"] != row["after"]} == {t.graph}
                approve(window)
                window.locator("#confirm").click()
                expect(window).to_be_hidden(timeout=120000)
                f.idle()
                published = json.loads(GRAPH.read_text())
                assert next(node for node in published["nodes"] if node["id"] == "after")["displayName"] == later_name
                checkpoint = saved.read_bytes()
                previous_undo = accepted["history"]["undo"]
                confirmed_undo = json.loads(checkpoint)["history"]["undo"]
                assert previous_undo and confirmed_undo[:-1] == previous_undo
        finally:
            second.close()

        with first.active():
            traffic = save()
            retried = [row["invoke"]["input"] for row in traffic
                       if row.get("invoke", {}).get("endpoint") == "blueprint"]
            assert any(row["action"] == "settledAuthorBatch" and row["attempt"] == attempt["attempt"]
                       for row in retried), retried
            assert not any(row["action"] == "authorBatch" for row in retried), retried
            if panel().locator(".bp-status").text_content() == "저장됨":
                raise AssertionError("The first editor reported saving its still-pending name.")
            assert pending() == private
        assert saved.read_bytes() == checkpoint and json.loads(GRAPH.read_text()) == published
        f.checked("The earlier Save retry preserves the second editor's Confirm and checkpoint bytes and the first editor's private inputs.")

        first.restart(2)
        with first.active():
            open_document()
            expect(doc().locator('[data-document-name="after"]')).to_have_value(private_name)
            assert pending() == private
        expected = json.loads(x.physical[GRAPH])
        next(node for node in expected["nodes"] if node["id"] == "after")["displayName"] = later_name
        assert published == expected and saved.read_bytes() == checkpoint
        assert all(path.read_bytes() == raw for path, raw in x.physical.items() if path != GRAPH)
        assert not f.errors and not f.external, (f.errors, f.external)
        f.checked("Cold reopen preserves the exact unconfirmed input, nested graph, sibling and C#.")
    finally:
        first.close()


try:
    with sync_playwright() as playwright:
        expect.set_options(timeout=60000)
        with playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
            if save_loss:
                run_save_loss(browser)
            else:
                late = Editor(1, browser)
                try:
                    publisher = Editor(0, browser)
                    try:
                        run_pair(publisher, late)
                    finally:
                        publisher.close()
                finally:
                    late.close()
finally:
    (f.case / "two-editor-blueprint-traffic.json").write_text(json.dumps(f.traffic, ensure_ascii=False))
    print("Evidence:", f.case)
