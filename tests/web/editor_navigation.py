"""Enter the production editor through its real first-run startup choice."""
def goto_editor(page, url):
    page.goto(url)
    page.wait_for_selector(".welcome[data-startup-ready],.home-grid,.work-body,#status", state="attached")
    later=page.locator('.welcome #later')
    if later.count():
        later.click()


def open_project_tools(page):
    """Open the real project menu; the v508 toolbar has no legacy browse button."""
    page.locator('#title').click()
    page.locator('.context-menu').get_by_role('button', name='프로젝트 도구', exact=True).click()
