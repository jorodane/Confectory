"""Enter the production editor through its real first-run startup choice."""
def goto_editor(page, url):
    page.goto(url)
    page.wait_for_selector(".welcome[data-startup-ready],.home-grid,.work-body,#status", state="attached")
    later=page.locator('.welcome #later')
    if later.count():
        later.click()
