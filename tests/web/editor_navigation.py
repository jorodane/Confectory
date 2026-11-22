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


def choose_project_tool(page, name):
    """Select a tool and dismiss the menu if the tool leaves it open."""
    menu = page.get_by_role('navigation', name='프로젝트 작업 공간')
    if not menu.is_visible():
        open_project_tools(page)
    menu.get_by_role('button', name=name, exact=True).click()
    if menu.is_visible():
        open_project_tools(page)
        menu.wait_for(state='hidden')


def open_workspace_menu(page, position=None):
    """Right-click an empty part of the visible canvas."""
    workspace = page.locator('#workspace')
    position = workspace.evaluate("""(workspace, preferred) => {
        const bounds = workspace.getBoundingClientRect();
        const empty = ({x, y}) => {
            const hit = document.elementFromPoint(bounds.left + x, bounds.top + y);
            return workspace.contains(hit) &&
                !hit.closest('.window,.workspace-decoration,.bubble-dock,.workspace-tabs,.pack-manager-view');
        };
        if (preferred && empty(preferred)) return preferred;
        for (const horizontal of [.75, .45, .2, .9]) {
            for (const vertical of [.35, .65, .8, .2]) {
                const point = {x: bounds.width * horizontal, y: bounds.height * vertical};
                if (empty(point)) return point;
            }
        }
        return null;
    }""", position)
    assert position is not None, 'No empty point in the visible workspace'
    workspace.click(button='right', position=position)
    menu = page.locator('.workspace-search-menu')
    menu.wait_for(state='visible')
    return menu


def create_workspace_item(page, kind, position=None):
    """Create a workspace decoration through the visible placement menu."""
    menu = open_workspace_menu(page, position)
    menu.locator('[data-workspace-create-menu]').click()
    menu.locator(f'[data-workspace-tool-create="{kind}"]').click()
