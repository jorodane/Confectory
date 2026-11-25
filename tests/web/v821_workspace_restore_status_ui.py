"""Restore three owned windows using the initial status already read by the host."""
import sys
import v821_property_window_reopen_ui as r
from playwright.sync_api import sync_playwright, expect
from editor_navigation import goto_editor

f, d = r.fixture, r.fallback
r.seed()
expect.set_options(timeout=60000)
try:
    with sync_playwright() as p, p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-gpu']) as b:
        f.start(0)
        page = f.setup(b)
        page.set_viewport_size({'width': 2000, 'height': 1200})
        notes = {}
        for name, folder in [(d.TARGET, 'StockFolder'), (d.PEER, 'PeerFolder'), ('Extra1', 'ExtraFolder1')]:
            window, key = r.floating.open_properties(page, name, folder)
            value = 'Retained local ' + name
            r.floating.property_value(window, 'Note').fill(value)
            notes[key] = (f'{d.NS}::{name}', value)
        page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"')
        page.evaluate('()=>confectoryFlushPresentation()')
        page.close()
        f.stop()
        # Real outside edit after the original session has stopped.
        schema = f.projects[0].parent / 'private-source-StockInfo.celem'
        schema.write_text(schema.read_text().rstrip()[:-1] + ' field RestartFlag single general string;\n}\n')
        f.before[str(schema)] = schema.read_bytes()
        f.env.pop('CONFECTORY_WEB_PROJECT', None)
        f.start(1)
        page = b.new_page(viewport={'width': 2000, 'height': 1200})
        invokes = []
        def intercept(route):
            if not route.request.url.startswith(f.origin + '/'):
                route.abort()
                return
            if route.request.method == 'POST':
                req = route.request.post_data_json
                if req.get('op') == 'invoke':
                    invokes.append(req)
            route.continue_()
        page.route('**/*', intercept)
        goto_editor(page, f.url)
        page.locator('.project-card').filter(has=page.get_by_role('heading', name=d.FIRST, exact=True)).locator('[data-enter]').click()
        expect(page.locator('.window[data-key^="editor-"]:visible')).to_have_count(3)
        expect(page.locator('#project-menu')).to_be_enabled()
        for key, (identifier, value) in notes.items():
            window = page.locator(f'.window[data-key="{key}"]')
            expect(r.floating.property_value(window, 'Note')).to_have_value(value)
            expect(d.field(window, 'RestartFlag')).to_be_visible()
            assert any('editor-' + row['view'] == key and row['id'] == identifier for row in f.state()['editorViews'])
        opens = [req for req in invokes if req.get('endpoint') == 'openEditorView']
        status = [req for req in invokes if req.get('endpoint') == 'browserDrafts' and req.get('input',{}).get('view')]
        assert len(opens) == 3, opens
        print('restored detached status reads',len(status),flush=True)
        if len(sys.argv) < 4 or sys.argv[3] != 'baseline':
            assert not status, status
        # The initial proof is one-shot, not a session cache. A later real
        # dependency change must still be visible on an ordinary status read.
        schema.write_text(schema.read_text().rstrip()[:-1] + ' field AfterRestoreFlag single general string;\n}\n')
        f.before[str(schema)] = schema.read_bytes()
        row = f.state()['editorViews'][0]
        f.call('browserDrafts', {'action':'status', 'view':row['view'], 'id':row['id'], 'ids':[row['id']]})
        for key, (_, value) in notes.items():
            window = page.locator(f'.window[data-key="{key}"]')
            expect(d.field(window, 'AfterRestoreFlag')).to_be_visible()
            expect(r.floating.property_value(window, 'Note')).to_have_value(value)
        f.original()
        print('PASS cold restore: exact three owners, retained input and external schema refresh', flush=True)
finally:
    f.stop()
    print('evidence', f.root, flush=True)
