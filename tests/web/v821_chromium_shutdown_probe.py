"""One real Linux Chromium launch/close; run through run_isolated_browser_test.py."""
from playwright.sync_api import expect, sync_playwright

with sync_playwright() as playwright:
    with playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
        with browser.new_context() as context:
            page = context.new_page()
            page.set_content("<p>Disposable Chromium shutdown probe</p>")
            expect(page.locator("p")).to_have_text("Disposable Chromium shutdown probe")
        # Browser and Playwright context managers close normally before exit.
print("PASS real Chromium page and normal teardown")
