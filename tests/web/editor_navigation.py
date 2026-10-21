"""Enter the production editor through its real first-run startup choice."""
def goto_editor(page, url):
    page.goto(url)
    page.wait_for_selector(".welcome .startup-actions:not([hidden]) #later:enabled,.home-grid,.work-body", state="visible")
    later=page.locator('.welcome #later')
    if later.is_visible():
        # A restored profile may enter Home while the asynchronous welcome
        # readiness callback retires this button. Accept only a real main view.
        from playwright.sync_api import TimeoutError as PlaywrightTimeout
        try:
            later.click(timeout=2000)
        except PlaywrightTimeout:
            if not page.locator('.home-grid,.work-body').first.is_visible():
                raise

    page.wait_for_function("() => !!document.querySelector('.home-grid,.work-body') && !document.querySelector('#app')?.inert")


def open_project_tools(page):
    """Open the real project menu; the v508 toolbar has no legacy browse button."""
    page.locator('#title').click()
    page.locator('.context-menu').get_by_role('button', name='프로젝트 도구', exact=True).click()
