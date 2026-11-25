"""A real pointer press must survive registered context-action discovery."""
import time
import v821_property_window_reopen_ui as r
from playwright.sync_api import sync_playwright, expect

f = r.fixture
d = r.fallback
r.seed()
expect.set_options(timeout=60000)
try:
    with sync_playwright() as p, p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-gpu']) as b:
        f.start(0)
        page = f.setup(b)
        page.set_viewport_size({'width': 2000, 'height': 1200})
        browser = r.browser_window(page)
        r.choose_tree_location(browser, f'[data-tree-id="{d.NS}::StockFolder"]')
        r.search(browser, d.LABEL, d.TARGET)
        expect(page.locator('#project-menu')).to_be_enabled()
        held = []
        def intercept(route):
            payload = route.request.post_data_json if route.request.method == 'POST' else {}
            if payload.get('op') == 'invoke' and payload.get('endpoint') == 'contextActions' and not held:
                held.append(route)
                return
            route.fallback()
        page.route('**/api/request', intercept)
        browser.locator(f'[data-object="{r.owner}"]').click(button='right')
        deadline = time.monotonic() + 10
        while not held and time.monotonic() < deadline:
            page.wait_for_timeout(20)
        assert len(held) == 1
        menu = page.locator('.context-menu')
        item = menu.get_by_role('button', name='새 창으로 열기', exact=True)
        handle = item.element_handle()
        box = item.bounding_box()
        page.mouse.move(box['x'] + 20, box['y'] + box['height'] / 2)
        page.mouse.down()
        try:
            held[0].continue_()
            expect(menu.get_by_role('button', name='등록 기능 조회 중…', exact=True)).to_have_count(0)
            assert handle.evaluate('element => element.isConnected')
        finally:
            page.mouse.up()
        target = page.locator('.window[data-key="editor-1"]')
        expect(r.floating.property_value(target, 'Note')).to_be_editable()
        rows = f.state()['editorViews']
        assert len(rows) == 1 and rows[0]['id'] == r.owner, rows
        f.original()
        print('PASS actual pointer click survives registered-action menu update', flush=True)
finally:
    f.stop()
    print('evidence', f.root, flush=True)
