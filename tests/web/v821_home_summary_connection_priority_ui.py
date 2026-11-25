"""A connection choice owns the next foreground click, not a pending Home summary."""
from playwright.sync_api import expect, sync_playwright

import v821_object_fallback_roundtrip_ui as fallback
from editor_navigation import goto_editor

fixture = fallback.fixture


def exercise(browser):
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    requests, errors, held_summary = [], [], []
    hold_summary = False
    page.on("pageerror", lambda error: errors.append(str(error)))

    def intercept(route):
        if not route.request.url.startswith(fixture.origin + "/"):
            fixture.external.append(route.request.url)
            route.abort()
            return
        if route.request.method == "POST":
            body = route.request.post_data_json
            if isinstance(body, dict) and body.get("op") == "invoke":
                requests.append(body["endpoint"])
                if hold_summary and body["endpoint"] == "homeSummaries" and not held_summary:
                    held_summary.append(route)
                    return
        route.continue_()

    page.route("**/*", intercept)
    goto_editor(page, fixture.url)
    expect(page.locator(".work-body")).to_be_visible()
    # Exercise the actual Home and provider entry points. Schedule the picker
    # at the first observable Home DOM turn, before the background timer.
    page.evaluate("""() => {
        const observer = new MutationObserver(() => {
            const button = document.querySelector('#add-agent');
            if (document.querySelector('.home-grid') && button && !button.disabled) {
                observer.disconnect();
                button.click();
            }
        });
        observer.observe(document.querySelector('#app'), {subtree:true, childList:true, attributes:true});
    }""")
    page.get_by_role("button", name="Confectory 홈으로").click()
    dialog = page.get_by_role("dialog", name="Agent 추가", exact=True)
    expect(dialog).to_be_visible()
    expect(dialog.get_by_role("button", name="Codex", exact=True)).to_be_enabled()
    dialog.get_by_role("button", name="Codex", exact=True).click()
    expect(dialog.locator('[data-cli-login]')).to_be_enabled()
    assert requests.count("connectionSetup") == 1
    assert "homeSummaries" not in requests, requests
    assert not set(requests) & {"prepareLogin", "startLogin", "prepareInstallation", "startInstallation"}
    dialog.locator('[data-connection-cancel]').click()
    expect(dialog).to_have_count(0)
    # An immediate reopen must not inherit the deferred read's latency.
    page.locator('#add-agent').click()
    dialog.get_by_role("button", name="Codex", exact=True).click()
    expect(dialog.locator('[data-cli-login]')).to_be_enabled()
    assert requests.count("connectionSetup") == 2
    assert "homeSummaries" not in requests, requests
    dialog.locator('[data-connection-cancel]').click()
    expect(dialog).to_have_count(0)
    # The deferred read resumes on Home, with the same card identities and
    # actual persisted summaries. No synthetic response is inserted.
    expect(page.locator('[data-stat="lastEdit"][data-status="none"]')).to_have_count(2)
    expect(page.locator('[data-stat="packs"][data-status="pending"]')).to_have_count(0)
    assert requests.count("homeSummaries") == 1, requests
    for title in (fallback.FIRST, fallback.SECOND):
        expect(page.locator('.project-card').filter(has=page.get_by_role('heading', name=title, exact=True))).to_have_count(1)

    # If a summary has already started, the existing transport ordering still
    # applies. Hold the real request, then open the provider and release it.
    card = page.locator('.project-card').filter(has=page.get_by_role('heading', name=fallback.FIRST, exact=True))
    card.locator('[data-enter]').click()
    expect(page.locator('.work-body')).to_be_visible()
    hold_summary = True
    with page.expect_request(lambda request: request.method == "POST" and
                             request.url.endswith("/api/request") and
                             request.post_data_json.get("endpoint") == "homeSummaries"):
        page.get_by_role("button", name="Confectory 홈으로").click()
    try:
        page.locator('#add-agent').click()
        dialog.get_by_role("button", name="Codex", exact=True).click()
        expect(dialog.get_by_role("button", name="Codex", exact=True)).to_be_disabled()
        assert requests.count("connectionSetup") == 2
        assert len(held_summary) == 1
    finally:
        for route in held_summary:
            route.continue_()
    expect(dialog.locator('[data-cli-login]')).to_be_enabled()
    dialog.locator('[data-connection-cancel]').click()
    expect(dialog).to_have_count(0)
    assert requests.count("connectionSetup") == 3
    assert requests.count("homeSummaries") == 2
    assert fixture.state()["projectId"] == ""
    fixture.original()
    assert not errors and not fixture.external, (errors, fixture.external)
    page.close()
    print("PASS connection choice precedes pending Home summary; cards and summaries resume after close; reopen retains guards")


if __name__ == "__main__":
    fallback.seed()
    fixture.start(0)
    try:
        with sync_playwright() as playwright, playwright.chromium.launch(
            executable_path="/usr/bin/chromium", args=["--no-sandbox", "--disable-gpu"]
        ) as browser:
            expect.set_options(timeout=30000)
            exercise(browser)
    finally:
        fixture.stop()
