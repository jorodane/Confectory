"""Restore three owned windows using the initial status already read by the host."""
import sys,time
import v821_property_window_reopen_ui as r
from playwright.sync_api import sync_playwright, expect
from editor_navigation import goto_editor

f, d = r.fixture, r.fallback
r.seed()
mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
expect.set_options(timeout=60000)
try:
    with sync_playwright() as p, p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-gpu']) as b:
        f.start(0)
        page = f.setup(b)
        page.set_viewport_size({'width': 2000, 'height': 1200})
        if mode=='primary':
            # The primary and detached owners are distinct. Open the primary
            # before filling all three detached slots, avoiding a duplicate UI target.
            browser=r.browser_window(page)
            r.choose_tree_location(browser,f'[data-tree-id="{d.NS}::ExtraFolder2"]')
            r.search(browser,d.LABEL,'Extra2')
            browser.locator(f'[data-object="{d.NS}::Extra2"]').click(button='right')
            page.locator(".context-menu").get_by_role("button", name="스키마 열기", exact=True).click()
            primary=page.locator('.window[data-key="schema"]')
            expect(r.floating.property_value(primary,'Note')).to_have_value(d.FIRST+' Extra2')
        notes = {}
        for name, folder in [(d.TARGET, 'StockFolder'), (d.PEER, 'PeerFolder'), ('Extra1', 'ExtraFolder1')]:
            window, key = r.floating.open_properties(page, name, folder)
            value = 'Retained local ' + name
            r.floating.property_value(window, 'Note').fill(value)
            notes[key] = (f'{d.NS}::{name}', value)
        if mode=='stale':
            # A retained dirty working copy deliberately exercises the ordinary
            # host admission fallback instead of the clean local read model.
            window.locator('[data-element-action="save"]').click()
            expect(page.locator('#project-menu')).to_be_enabled()
        saved_id=f.state()['draft']['id']
        if mode=='primary':assert saved_id==d.NS+'::Extra2',saved_id
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
        held=[]
        def intercept(route):
            if not route.request.url.startswith(f.origin + '/'):
                route.abort()
                return
            if route.request.method == 'POST':
                req = route.request.post_data_json
                if req.get('op') == 'invoke':
                    invokes.append(req)
                    if mode=='stale' and req.get('endpoint')=='openEditorView' and req.get('input',{}).get('view')=='2' and not held:
                        held.append(route);return
            route.continue_()
        page.route('**/*', intercept)
        goto_editor(page, f.url)
        page.locator('.project-card').filter(has=page.get_by_role('heading', name=d.FIRST, exact=True)).locator('[data-enter]').click()
        if mode=='stale':
            deadline=time.monotonic()+30
            while not held and time.monotonic()<deadline:page.wait_for_timeout(20)
            assert len(held)==1
            # Advance the actual shared revision without changing the cursor or source.
            try:f.call('browserDrafts',{'action':'status','ids':[saved_id]})
            finally:held[0].continue_()
        expect(page.locator('.window[data-key^="editor-"]:visible')).to_have_count(3)
        expect(page.locator('#project-menu')).to_be_enabled()
        for key, (identifier, value) in notes.items():
            window = page.locator(f'.window[data-key="{key}"]')
            expect(r.floating.property_value(window, 'Note')).to_have_value(value)
            expect(d.field(window, 'RestartFlag')).to_be_visible()
            assert window.get_attribute('data-element-owner') == identifier
        opens = [req for req in invokes if req.get('endpoint') == 'openEditorView']
        status = [req for req in invokes if req.get('endpoint') == 'browserDrafts' and req.get('input',{}).get('view')]
        if mode=='stale':
            assert len(opens)>=4, opens
        else:
            # Clean restoration can use one shared preparation rather than a
            # separate host view admission for every visible window.
            assert len(opens) in (0,3), opens
            if not opens:assert any(req.get('endpoint')=='preparePropertyModels' for req in invokes)
        if mode=='stale':
            attempts=[req['expectedRevision'] for req in opens if req['input']['view']=='2']
            assert len(attempts)>=2 and attempts[0]!=attempts[-1],attempts
            print('actual stale restore admission revisions',attempts,flush=True)
        snapshot=f.state()
        assert snapshot['draft']['id']==saved_id and len(snapshot['editorViews']) in (0,3)
        if mode=='primary':
            assert snapshot['schema']['id']==saved_id
            expect(d.field(page.locator('.window[data-key="schema"]'),'RestartFlag')).to_be_visible()
        elif mode!='baseline':assert snapshot['schema'] is None, snapshot['schema']

        print('restored detached status reads',len(status),flush=True)
        if mode != 'baseline':
            assert not status, status
        # The initial proof is one-shot, not a session cache. A later real
        # dependency change must still be visible on an ordinary status read.
        schema.write_text(schema.read_text().rstrip()[:-1] + ' field AfterRestoreFlag single general string;\n}\n')
        f.before[str(schema)] = schema.read_bytes()
        rows = f.state()['editorViews']
        if rows:
            row = rows[0]
            f.call('browserDrafts', {'action':'status', 'view':row['view'], 'id':row['id'], 'ids':[row['id']]})
        else:
            for name,folder in [(d.TARGET,'StockFolder'),(d.PEER,'PeerFolder'),('Extra1','ExtraFolder1')]:
                r.drag(page,name,folder)
                expect(page.locator('#project-menu')).to_be_enabled()
        for key, (_, value) in notes.items():
            window = page.locator(f'.window[data-key="{key}"]')
            expect(d.field(window, 'AfterRestoreFlag')).to_be_visible()
            expect(r.floating.property_value(window, 'Note')).to_have_value(value)
        f.original()
        print('PASS cold restore ('+mode+'): exact three owners, retained input and external schema refresh', flush=True)
finally:
    f.stop()
    print('evidence', f.root, flush=True)
