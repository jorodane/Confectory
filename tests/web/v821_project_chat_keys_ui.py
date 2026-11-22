"""Chat keyboard regression in the real Linux editor with a loopback provider."""
from playwright.sync_api import expect, sync_playwright

from v821_project_chat_latest_log_ui import OwnedChat, add_helper, fixture

FIRST_LINE = "한글 조합을 마쳤습니다"
SECOND_LINE = "다음 줄도 빠짐없이 보냅니다"
MESSAGE = FIRST_LINE + "\n" + SECOND_LINE


def enter_event(composer, **options):
    composer.evaluate("""(input, options) => {
      const {keyCode, ...flags} = options;
      const event = new KeyboardEvent("keydown", {
        key: "Enter", code: "Enter", bubbles: true, cancelable: true, ...flags,
      });
      if (keyCode !== undefined) Object.defineProperty(event, "keyCode", {value: keyCode});
      input.dispatchEvent(event);
    }""", options)


def history(endpoint):
    return [request["input"] for request in fixture.requests if request["endpoint"] == endpoint]


def exercise(page, owned):
    add_helper(page, owned)
    composer = page.locator("#chat-input")
    form = page.locator("#chat-form")
    approval = page.locator('.window[data-key="ai-preview"]')
    # Count native form submit events without substituting any handler or response.
    form.evaluate("""form => {
      form.dataset.fixtureSubmissions = '0';
      form.addEventListener('submit', () => form.dataset.fixtureSubmissions++);
    }""")

    composer.fill(FIRST_LINE)
    composer.dispatch_event("compositionstart")
    composer.dispatch_event("compositionupdate", {"data": FIRST_LINE})
    enter_event(composer)
    expect(form).to_have_attribute("data-fixture-submissions", "0")
    composer.dispatch_event("compositionend", {"data": FIRST_LINE})
    enter_event(composer, isComposing=True)
    expect(form).to_have_attribute("data-fixture-submissions", "0")
    enter_event(composer, keyCode=229)
    expect(form).to_have_attribute("data-fixture-submissions", "0")
    expect(approval).to_have_count(0)
    assert not owned.requests and not history("prepareAI")
    fixture.checked("합성 국문 조합과 이벤트 플래그가 붙은 Enter는 원래 전송 폼을 제출하지 않는다")

    # A keyboard may keep reporting Enter after it has committed composition.
    enter_event(composer, repeat=True)
    expect(form).to_have_attribute("data-fixture-submissions", "0")
    expect(composer).to_have_value(FIRST_LINE)
    expect(approval).to_have_count(0)
    fixture.checked("조합 확정 키를 계속 누르고 있어도 뒤따르는 반복 Enter는 전송 검토를 열지 않는다")

    composer.press("End")
    composer.press("Shift+Enter")
    page.keyboard.insert_text(SECOND_LINE)
    expect(composer).to_have_value(MESSAGE)
    expect(form).to_have_attribute("data-fixture-submissions", "0")
    fixture.checked("Shift+Enter가 실제 줄바꿈을 만들고 완성된 한글을 그대로 유지한다")

    composer.press("Enter")
    expect(form).to_have_attribute("data-fixture-submissions", "1")
    expect(approval.locator("#ai-start")).to_be_disabled()
    fixture_state = fixture.state()
    token = fixture_state["aiPreview"]["token"]
    assert fixture_state["aiPreview"]["message"] == MESSAGE
    assert len(history("prepareAI")) == 1 and not owned.requests
    # A held key must not replace the completed preparation or its permission choices.
    approval.locator('[data-permission="contentApproved"]').check()
    enter_event(composer, repeat=True)
    expect(form).to_have_attribute("data-fixture-submissions", "1")
    assert fixture.state()["aiPreview"]["token"] == token
    expect(approval.locator('[data-permission="contentApproved"]')).to_be_checked()
    approval.locator('[data-permission="usageApproved"]').check()
    approval.locator("#ai-start").click()
    expect(page.locator("#chat-output")).to_have_text("OWNED project-chat REPLY", timeout=30000)
    assert len(owned.requests) == 1 and owned.requests[0]["message"] == MESSAGE
    assert len(history("prepareAI")) == len(history("startAI")) == 1
    assert not fixture.errors and not fixture.external and not owned.errors
    fixture.original()
    fixture.checked("명시적인 단일 Enter가 검토 한 건을 만들고 승인 뒤 동일한 한글·줄바꿈을 한 번만 전송한다")


if __name__ == "__main__":
    owned = OwnedChat()
    try:
        fixture.start(0)
        with sync_playwright() as playwright:
            with playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
                exercise(fixture.setup(browser), owned)
    finally:
        fixture.stop()
        owned.close()
        fixture.save_evidence()
        print("evidence:", fixture.root)
