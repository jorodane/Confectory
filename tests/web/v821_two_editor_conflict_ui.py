"""Use two actual EditorHome processes and the existing conflict controls."""
from contextlib import contextmanager
import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

from editor_navigation import choose_project_tool, goto_editor
import v821_browser_compound_roundtrip_ui as data

fixture = data.fixture
SOURCE_ID = data.UNIT
LOCAL = "data Speed = 11"
CURRENT = "data Speed = 31"


class Editor:
    def __init__(self, browser, number):
        profile = str(fixture.root / f"profile-{number}")
        old_env = fixture.env
        fixture.env = {**fixture.env, "CONFECTORY_HOME_STORAGE": profile,
                       "CONFECTORY_ENTRY_STORAGE": profile,
                       "CONFECTORY_MCP_DIRECTORY": str(fixture.root / f"instances-{number}")}
        try:
            fixture.start(number)
        finally:
            fixture.env = old_env
        self.channel = {key: getattr(fixture, key) for key in ("origin", "token", "host", "stream", "url")}
        self.page = browser.new_page(viewport={"width": 1850, "height": 1180})
        self.page.on("pageerror", lambda error: fixture.errors.append(str(error)))
        self.requests = []
        self.page.route("**/*", self.route)
        goto_editor(self.page, self.channel["url"])
        expect(self.page.locator(".work-body")).to_be_visible()

    def route(self, route):
        if not route.request.url.startswith(self.channel["origin"] + "/"):
            fixture.external.append(route.request.url)
            route.abort()
            return
        if route.request.method == "POST":
            body = route.request.post_data_json
            if isinstance(body, dict) and body.get("op") == "invoke":
                self.requests.append(body)
        route.continue_()

    @contextmanager
    def active(self):
        previous = {key: getattr(fixture, key) for key in self.channel}
        fixture.__dict__.update(self.channel)
        try:
            yield
        finally:
            fixture.__dict__.update(previous)

    def state(self):
        with self.active():
            return fixture.state()

    def call(self, endpoint, **values):
        with self.active():
            return fixture.call(endpoint, values)

    def close(self):
        self.page.close()
        with self.active():
            fixture.stop()

    def tool(self, name):
        choose_project_tool(self.page, name)
        expect(self.page.locator(".brand")).to_be_enabled(timeout=60000)


def review(editor):
    editor.tool("변경 검토")
    panel = editor.page.locator('.window[data-key="review"]')
    expect(panel).to_be_visible()
    return panel


def confirm(editor, panel):
    panel.locator("[data-review-advanced]").click()
    ack = panel.locator("[data-advanced-reviewed]")
    if ack.count():
        ack.check()
    expect(panel.locator("#confirm")).to_be_enabled()
    panel.locator("#confirm").click()
    expect(panel).to_be_hidden(timeout=150000)
    expect(editor.page.locator("#status")).to_have_text("검토한 변경을 최종 소스에 반영했습니다.")


def open_compare(editor):
    editor.tool("소스 충돌 비교")
    panel = editor.page.locator('.window[data-key="conflict"]')
    expect(panel).to_be_visible()
    expect(panel.locator("[data-conflict-id]")).to_have_text(SOURCE_ID)
    return panel


def set_draft(editor, expected, new):
    editor.call("select", id=SOURCE_ID)
    original = editor.state()["draft"]
    assert original["text"] == expected
    editor.call("editDraft", id=SOURCE_ID, text=new, revision=original["revision"])
    assert editor.state()["draft"]["text"] == new


def run_pair(publisher, late):
    source = fixture.projects[0].parent / "ProbeUnit.celem"
    original = source.read_text()
    local = original.replace("data Speed = 2", LOCAL)
    current = original.replace("data Speed = 2", CURRENT)
    assert local != original and current != original
    set_draft(late, original, local)
    set_draft(publisher, original, current)
    late_original_review = review(late)
    expect(late_original_review.locator("#confirm")).to_be_enabled()
    initial_token = late.state()["review"]["token"]
    late_original_review.locator("[data-reject]").click()
    expect(late_original_review).to_be_hidden()
    fixture.original()

    publisher.call("saveDraft")
    confirm(publisher, review(publisher))
    assert source.read_text() == current
    assert late.state()["draft"]["text"] == local
    fixture.checked("두 실제 편집기의 독립 초안에서 같은 값 하나를 달리 편집하고 앞선 편집기만 확정한다")

    panel = open_compare(late)
    for version, text in {"baseText": original, "fileText": current, "draftText": local}.items():
        expect(panel.locator(f'[data-conflict-version="{version}"]')).to_have_value(text)
    assert late.state()["review"]["token"] == initial_token
    checkpoints = {path: path.read_bytes() for path in source.parent.rglob("draft.json")}
    assert checkpoints
    panel.locator('[data-close]').first.click()
    expect(panel).to_be_hidden()
    assert late.state()["draft"]["text"] == local
    assert publisher.state()["draft"]["text"] == current
    assert source.read_text() == current
    assert all(path.read_bytes() == saved for path, saved in checkpoints.items())
    assert not any(row["endpoint"] == "resolveSourceConflict" for row in late.requests)
    fixture.checked("실제 기준·현재·로컬 값을 함께 표시하며 닫기는 원본과 두 작업 사본을 보존한다")

    stale = review(late)
    expect(stale.locator("[data-review-conflict-notice]")).to_be_visible()
    expect(stale.locator("#confirm")).to_be_disabled()
    stale_token = late.state()["review"]["token"]
    stale.locator(f'[data-review-conflict="{SOURCE_ID}"]').click()
    expect(panel).to_be_visible()
    panel.locator('[data-conflict-use="draftText"]').click()
    expect(stale).to_be_hidden()
    assert late.state()["review"]["token"] == stale_token
    proof = json.loads(panel.locator("[data-conflict-proof]").text_content())
    panel.locator("[data-conflict-apply]").click()
    expect(late.page.locator("#status")).to_contain_text("공유 초안에 합쳤습니다")
    resolution, = [row["input"] for row in late.requests if row["endpoint"] == "resolveSourceConflict"]
    assert resolution == {"id": SOURCE_ID, "text": local,
                          **{key: proof[key] for key in ("revision", "draftHash", "fileHash")}}
    assert late.state()["draft"]["text"] == local
    assert late.state()["review"] is None
    assert source.read_text() == current
    panel.locator("[data-conflict-save]").click()
    expect(late.page.locator("#status")).to_have_text("Draft saved; final sources unchanged")
    assert source.read_text() == current
    panel.locator("[data-conflict-review]").click()
    fresh = late.page.locator('.window[data-key="review"]')
    expect(fresh.locator("#confirm")).to_be_enabled()
    fresh_state = late.state()["review"]
    assert fresh_state["token"] not in (initial_token, stale_token)
    assert fresh_state["before"] == current and fresh_state["after"] == local
    assert source.read_text() == current
    fixture.checked("명시 선택은 공유 초안만 합치며 저장해도 원본은 이전 값이다. 새 Review가 정확한 차이를 고정한다")

    confirm(late, fresh)
    assert source.read_text() == local
    for path, expected in fixture.before.items():
        if Path(path) != source:
            assert Path(path).read_bytes() == expected, path
    assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
    fixture.checked("새로 검토하고 확정한 단일 소스만 수정된다")


def main():
    data.seed()
    with sync_playwright() as playwright:
        with playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
            publisher = Editor(browser, 0)
            try:
                late = Editor(browser, 1)
                try:
                    run_pair(publisher, late)
                finally:
                    late.close()
            finally:
                publisher.close()
    print("evidence:", fixture.root)


if __name__ == "__main__":
    main()
