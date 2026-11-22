"""Project Browser Enter through Chromium and the real local EditorHome transport."""
import json
import sys

from playwright.sync_api import expect, sync_playwright

import v666_workspace_finder_fixture as fixture

NAMESPACE = "Example.FrameLoop::"
FIRST = "EarlierResult"
SECOND = "LaterResult"
KOREAN = "한글 검색"
DRAFT = "개인 입력을 보존하는 동안 Enter"
NO_RESULT = "MissingResult"
results = {}


def seed():
    titles = ["Search First", "Search Second"]
    for manifest, title in zip(fixture.projects, titles):
        for name in (FIRST, SECOND):
            source = manifest.parent / (name + ".celem")
            source.write_text(
                f'function {NAMESPACE}{name} () -> int {{description "{title}";'
                f'value editorName = "{KOREAN if name == SECOND else name}";}}'
            )
            fixture.before[str(source)] = source.read_bytes()
            manifest.write_text(manifest.read_text().rstrip()[:-1] +
                                f'element {name} function "{source.name}";}}')
        fixture.before[str(manifest)] = manifest.read_bytes()
    profile = fixture.root / "profile"
    profile.mkdir()
    (profile / "projects.json").write_text(json.dumps([
        {"path": str(project), "title": title, "description": ""}
        for project, title in zip(fixture.projects, titles)
    ]))


def search_page(page):
    page.locator("#title").click()
    page.locator(".context-menu").get_by_role("button", name="프로젝트 브라우저", exact=True).click()
    window = page.locator('.window[data-key="browser"]')
    feature = window.get_by_role("button", name="기능", exact=True)
    feature.click()
    expect(feature).to_have_class("selected")
    expect(window.get_by_role("button", name="검색 확정")).to_be_enabled()
    return window


def matches(window, name):
    return window.locator(f'[data-object="{NAMESPACE}{name}"]')


def submit(query, value):
    query.fill(value)
    query.press("Enter")


def inputs(endpoint, since=0):
    return [row["input"] for row in fixture.requests[since:] if row["endpoint"] == endpoint]


def observe(response):
    if response.url != fixture.origin + "/api/request":
        return
    request = response.request.post_data_json
    if request["op"] not in ("invoke", "update"):
        return
    reply = response.json()
    if request["op"] == "invoke" and not reply["ok"]:
        results[request["requestId"]] = reply["error"]["code"]
    if request["op"] == "update":
        for result in reply.get("results", []):
            results[result["requestId"]] = "applied" if result["ok"] else result["error"]["code"]


def expect_one_selection(since, identifier):
    selection = [row for row in fixture.requests[since:] if row["endpoint"] == "select"]
    assert {row["input"]["id"] for row in selection} == {identifier}, selection
    outcomes = [results.get(row["requestId"]) for row in selection]
    # The existing view retries only when admission refused a stale revision.
    assert outcomes.count("applied") == 1 and set(outcomes) <= {"applied", "stale_revision"}, outcomes


class Gate:
    def __init__(self, page, predicate):
        self.page = page
        self.endpoint = fixture.origin + "/api/request"
        self.predicate = predicate
        self.route = None
        self.used = False

    def intercept(self, route):
        body = route.request.post_data_json
        if not self.used and isinstance(body, dict) and body.get("op") == "invoke" and self.predicate(body):
            self.used = True
            self.route = route
        else:
            route.fallback()

    def __enter__(self):
        self.page.route(self.endpoint, self.intercept)
        return self

    def release(self):
        assert self.route is not None, "No held request"
        self.route.fallback()
        self.route = None

    def __exit__(self, *error):
        if self.route:
            self.release()
        self.page.unroute(self.endpoint, self.intercept)

    def wait(self):
        for _ in range(200):
            if self.route:
                return
            self.page.wait_for_timeout(25)
        raise AssertionError("Expected to hold an actual transport request")


def search_for(request, query):
    return request["endpoint"] == "objects" and request["input"].get("query") == query


def test_latest_submission(page, window, query):
    search_button = window.get_by_role("button", name="검색 확정")
    submit(query, "Main")
    expect(window.locator("[data-object]")).to_have_count(1)
    expect(search_button).to_be_enabled()
    old_card = matches(window, "Main")
    moment = len(fixture.requests)
    with Gate(page, lambda request: search_for(request, FIRST)) as old, \
            Gate(page, lambda request: search_for(request, SECOND)) as latest:
        submit(query, FIRST)
        old.wait()
        old_card.press("Enter")
        submit(query, SECOND)
        assert not inputs("select", moment) and not latest.used
        old.release()
        latest.wait()
        expect(old_card).to_be_visible()
        expect(matches(window, FIRST)).to_have_count(0)
        old_card.press("Enter")
        latest.release()
        expect(matches(window, SECOND)).to_be_visible()
        expect(matches(window, FIRST)).to_have_count(0)
        expect(search_button).to_be_enabled()
        expect(query).to_have_value(SECOND)
        assert [row["query"] for row in inputs("objects", moment)] == [FIRST, SECOND]
        assert not inputs("select", moment)
    fixture.checked("The latest explicit search waits for the first real reply, keeps superseded rows out and never opens an unconfirmed card")


def test_enter_after_reply(page, window, query):
    submit(query, FIRST)
    expect(matches(window, FIRST)).to_be_visible()
    expect(window.get_by_role("button", name="검색 확정")).to_be_enabled()
    moment = len(fixture.requests)
    save_chat = lambda request: (request["endpoint"] == "savePresentation" and
                                request["input"]["presentation"]["inputs"]["chat"] == DRAFT)
    with Gate(page, lambda request: search_for(request, SECOND)) as search, Gate(page, save_chat) as save:
        submit(query, SECOND)
        search.wait()
        page.locator("#chat-input").fill(DRAFT)
        search.release()
        save.wait()
        card = matches(window, SECOND)
        expect(card).to_be_visible()
        expect(matches(window, FIRST)).to_have_count(0)
        expect(window.get_by_role("button", name="검색 확정")).to_be_disabled()
        card.press("Enter")
        assert not inputs("select", moment)
        save.release()
        expect(window.get_by_role("button", name="검색 확정")).to_be_enabled()
        expect(page.locator(f'.window[data-key="declaration"] [data-obj="{NAMESPACE}{SECOND}"]')).to_be_visible()
        expect_one_selection(moment, NAMESPACE + SECOND)
        expect(page.locator("#chat-input")).to_have_value(DRAFT)
    fixture.checked("Enter on the confirmed result during the presentation flush opens that qualified function once")


def test_composition_and_empty(page, window, query):
    declaration = page.locator('.window[data-key="declaration"]')
    if declaration.is_visible():
        declaration.locator("[data-close]").click()
    moment = len(fixture.requests)
    query.fill(KOREAN)
    query.dispatch_event("compositionstart")
    query.press("Enter")
    query.dispatch_event("compositionend", {"data": KOREAN})
    ime_keys = query.evaluate("""input => [true, false].map(isComposing => {
      const event = new KeyboardEvent("keydown", {key:"Enter",bubbles:true,cancelable:true,isComposing});
      if (!isComposing) Object.defineProperty(event, "keyCode", {value:229});
      return input.dispatchEvent(event);
    })""")
    assert ime_keys == [True, True]
    query.dispatch_event("keydown", {"key": "Enter", "repeat": True})
    assert not inputs("objects", moment)
    expect(query).to_have_value(KOREAN)
    query.press("Enter")
    expect(matches(window, SECOND)).to_be_visible()
    expect(window.locator("[data-object]")).to_have_count(1)
    expect(window.get_by_role("button", name="검색 확정")).to_be_enabled()
    assert [row["query"] for row in inputs("objects", moment)] == [KOREAN]
    expect(declaration).not_to_be_visible()
    fixture.checked("Composition, legacy IME Enter and repeats do not search; a fresh Enter searches the complete Korean text once")

    submit(query, NO_RESULT)
    expect(window.get_by_text("검색 결과가 없습니다.", exact=True)).to_be_visible()
    page.keyboard.press("Enter")
    expect(window.get_by_role("button", name="검색 확정")).to_be_enabled()
    expect(declaration).not_to_be_visible()
    assert not inputs("select", moment)
    fixture.checked("An empty result does not open a previous row or a default target")


def test_retired_browser(page, window, query):
    moment = len(fixture.requests)
    with Gate(page, lambda request: search_for(request, FIRST)) as old:
        submit(query, FIRST)
        old.wait()
        submit(query, SECOND)
        window.locator("[data-close]").click()
        expect(window).not_to_be_visible()
        old.release()
        expect(page.locator("#title")).to_be_enabled()
    assert [row["query"] for row in inputs("objects", moment)] == [FIRST]
    assert not inputs("select", moment)
    page.locator(".brand").click()
    expect(page.locator(".home-grid")).to_be_visible()
    page.locator(".project-card").filter(has=page.get_by_role("heading", name="Search Second", exact=True)).locator("[data-enter]").click()
    expect(page.locator("#title")).to_contain_text("Search Second")
    second = search_page(page)
    second_query = second.locator('[data-browser-control="object-query"]')
    expect(second_query).to_have_value("")
    submit(second_query, FIRST)
    expect(second.get_by_role("button", name="검색 확정")).to_be_enabled()
    expect(matches(second, FIRST)).to_be_visible()
    moment = len(fixture.requests)
    matches(second, FIRST).press("Enter")
    expect(page.locator(f'.window[data-key="declaration"] [data-obj="{NAMESPACE}{FIRST}"]')).to_have_value("Search Second")
    expect_one_selection(moment, NAMESPACE + FIRST)
    fixture.checked("Closing the old browser retires its queued key action; Enter in the other project opens its own same-ID function")


def run():
    seed()
    fixture.start(0)
    try:
        with sync_playwright() as playwright:
            with playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
                expect.set_options(timeout=8000)
                page = fixture.setup(browser)
                page.on("response", observe)
                page.set_viewport_size({"width": 1600, "height": 1180})
                try:
                    window = search_page(page)
                    query = window.locator('[data-browser-control="object-query"]')
                    mode = sys.argv[3] if len(sys.argv) > 3 else "all"
                    if mode in ("latest", "all"):
                        test_latest_submission(page, window, query)
                    if mode in ("settling", "all"):
                        test_enter_after_reply(page, window, query)
                    if mode == "all":
                        test_composition_and_empty(page, window, query)
                        test_retired_browser(page, window, query)
                    fixture.original()
                    assert not fixture.errors and not fixture.external
                except Exception:
                    page.screenshot(path=str(fixture.root / "failure.png"))
                    raise
    finally:
        fixture.save_evidence()
        fixture.stop()
        print("BROWSER_SEARCH_FIXTURE", fixture.root)


if __name__ == "__main__":
    run()
