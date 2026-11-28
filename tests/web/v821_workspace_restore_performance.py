"""Measure actual restored workspace readiness; no latency threshold.

Run on Linux with the ordinary EditorHome build report and authoring host:
  python tests/run_isolated_browser_test.py -- python tests/web/v821_workspace_restore_performance.py REPO BUILD_REPORT 8
Repeat with 0 or 1, or repeat the same command for a no-op comparison.
CONFECTORY_RESTORE_OBJECTS=400 selects the larger fixture (default: 40).
All projects, including the eight recent listings, are disposable synthetic copies.
The default waits for Home summaries to finish before timing the actual tile click.
Use --during-summary to measure contention instead. --exercise-command opens the
real project Browser and verifies a search after the last editable property.
--verify-restored-map additionally checks that the shared initial read renders
the actual map and explicit reload observes an external schema edit (8 windows).
--working-copy saves an actual Browser working-copy query before restoring.
--verify-no-speculative-model checks the 400-object Browser avoids optional
model requests while the normal restore admission remains available.
--verify-restore-completion verifies the three 400-object cold fallback
open requests use the existing bounded completion protocol.
--verify-filter-freshness checks an external schema edit through the working-copy
filter before the explicit map reload, retaining detached local input.
--repeat-map repeats the completed explicit reload and records UI latency.
--verify-relation-delta checks unchanged 400-object owned draft rows are reused.
--verify-state-reuse checks full, exact-reference and wrong-token host responses.
Resource Timing reports encoded API response bytes from the actual card click.
Optional --trace-files or CONFECTORY_RESTORE_CPU_PROFILE=1 is a separate
diagnostic run (tracing overhead makes its timings incomparable).
"""
import json
import os
import shutil
import sys

from playwright.sync_api import expect, sync_playwright
from editor_navigation import goto_editor
import v821_property_window_reopen_ui as r

f, d = r.fixture, r.fallback
count = int(sys.argv[3])
assert count in (0, 1, 8), 'Choose 0, 1, or 8 restored windows'
objects = int(os.environ.get("CONFECTORY_RESTORE_OBJECTS", "40"))
assert objects in (40, 400)
flags = set(sys.argv[4:])
assert flags <= {'--during-summary', '--trace-files', '--exercise-command', '--verify-restored-map', '--working-copy', '--verify-no-speculative-model', '--verify-filter-freshness', '--verify-restore-completion', '--repeat-map', '--verify-relation-delta', '--verify-state-reuse'}, flags
assert not ({'--verify-restored-map', '--working-copy'} & flags) or count == 8
assert '--verify-no-speculative-model' not in flags or objects == 400
assert '--verify-filter-freshness' not in flags or {'--working-copy', '--verify-restored-map'} <= flags
assert '--verify-restore-completion' not in flags or (objects == 400 and count == 8)
assert '--repeat-map' not in flags or '--verify-restored-map' in flags
assert '--verify-relation-delta' not in flags or (objects == 400 and '--repeat-map' in flags)
expect.set_options(timeout=90000)
f.env['CONFECTORY_UI_TRACE'] = '1'
r.seed()
for manifest in f.projects:
    registrations = []
    for i in range(objects - 4):
        name = f'ModelExtra{i}'
        source = manifest.parent / (name + '.celem')
        source.write_text(f'object {d.NS}::{name} {{ use schema {d.NS}::StockInfo; data Count = {i}; data Note = "Model Extra {i}"; }}\n')
        registrations.append(f'element {name} object "{source.name}";')
        f.before[str(source)] = source.read_bytes()
    manifest.write_text(manifest.read_text().rstrip()[:-1] + '\n' + '\n'.join(registrations) + '\n}\n')
    f.before[str(manifest)] = manifest.read_bytes()
listing = f.root / 'profile/projects.json'
cards = json.loads(listing.read_text())
for i in range(6):
    folder = f.root / f'recent-{i}'
    shutil.copytree(f.projects[0].parent, folder, ignore=shutil.ignore_patterns('.confectory', '.build'))
    cards.append({'path': str(folder / 'project.cpack'), 'title': f'Recent {i}', 'description': ''})
cards.append({'path': str(f.root / 'missing/project.cpack'), 'title': 'Missing Recent', 'description': ''})
listing.write_text(json.dumps(cards))
run = f.report['run']


def start(n):
    if '--trace-files' in flags:
        f.report['run'] = ['strace', '-f', '-e', 'trace=execve,openat', '-o', str(f.root / f'files-{n}.log'), *run]
    f.start(n)


def new_page(browser):
    page = browser.new_page(viewport={'width': 2000, 'height': 1200})
    page.route('**/*', lambda route: route.continue_() if route.request.url.startswith(f.origin + '/') else route.abort())
    page.add_init_script('globalThis.confectoryWebUITrace=[];')
    goto_editor(page, f.url)
    return page


def property_snapshot(page, keys):
    return page.evaluate('''keys=>Object.fromEntries([...document.querySelectorAll('.window[data-key]')]
        .filter(w=>keys.includes(w.dataset.key)&&(w.dataset.key==='schema'||w.dataset.key.startsWith('editor-')))
        .map(w=>[w.dataset.key,{owner:w.dataset.elementOwner||null,values:[...w.querySelectorAll('[data-property-value]')].map(i=>i.value)}]))''', keys)


def measure(page, label, keys, expected):
    page.wait_for_function("()=>confectoryWebUITrace.some(r=>r.stage==='call'&&r.endpoint==='homeSummaries'&&r.code==='completed')")
    if '--during-summary' not in flags:
        page.wait_for_function("()=>[...document.querySelectorAll('[data-stat=objects]')].every(e=>e.dataset.status!=='pending')")
    pending = page.locator('[data-stat=objects][data-status=pending]').count()
    tile = page.locator('.project-card').filter(has=page.get_by_role('heading', name=d.FIRST, exact=True)).locator('[data-enter]')
    tile.evaluate('''(button, keys)=>{globalThis.restoreMarks={};globalThis.confectoryWebUITrace=[];
      button.addEventListener('click',()=>{performance.setResourceTimingBufferSize(2000);performance.clearResourceTimings();const start=performance.now();globalThis.restoreClick=start;function mark(name,ok){if(ok&&!(name in restoreMarks))restoreMarks[name]=performance.now()-start;}
      const visible=e=>!!e&&e.getClientRects().length>0&&!e.closest('[hidden]');
      const editable=e=>visible(e)&&!e.disabled&&!e.readOnly&&!e.closest('[inert]');
      function frame(){mark('workspace',visible(document.querySelector('.work-body'))&&editable(document.querySelector('#chat-input')));
        mark('commands',visible(document.querySelector('#project-menu'))&&!document.querySelector('#project-menu').disabled);
        for(const w of document.querySelectorAll('.window[data-key]')){const key=w.dataset.key;if(!keys.includes(key))continue;
          if(key==='schema'||key.startsWith('editor-'))mark(key+'-editable',visible(w)&&editable(w.querySelector('[data-property-value]'))&&!w.textContent.includes('이 창의 실제 기능을 다시 연결해야 합니다'));}
        if(performance.now()-start<60000)requestAnimationFrame(frame);}
      requestAnimationFrame(frame);},{once:true,capture:true});}''', keys)
    prepared_requests, opened_requests = [], []
    def capture_prepare(request):
        if request.method == 'POST' and request.url.startswith(f.origin + '/'):
            body = request.post_data_json
            if isinstance(body, dict) and body.get('op') == 'invoke' and body.get('endpoint') == 'preparePropertyModels':
                prepared_requests.append(body['input'])
            if isinstance(body, dict) and body.get('op') == 'invoke' and body.get('endpoint') == 'openEditorView':
                opened_requests.append(body)
    if {'--verify-no-speculative-model', '--verify-restore-completion'} & flags:
        page.on('request', capture_prepare)
    cdp = None
    if os.environ.get("CONFECTORY_RESTORE_CPU_PROFILE"):
        cdp = page.context.new_cdp_session(page)
        cdp.send("Profiler.enable")
        cdp.send("Profiler.start")
    tile.click()
    expect(page.locator('.work-body')).to_be_visible()
    if '--exercise-command' not in flags:
        expect(page.locator('#project-menu')).to_be_enabled()
    if '--exercise-command' in flags:
        page.wait_for_function('keys=>["workspace",...keys.map(k=>k+"-editable")].every(k=>k in restoreMarks)', arg=list(expected))
        page.evaluate("()=>{globalThis.commandAttempt=performance.now()-restoreClick;document.querySelector('#project-menu').addEventListener('click',()=>{globalThis.commandClick=performance.now()-restoreClick},{once:true,capture:true})}")
        page.locator('#project-menu').click()
        page.locator('.context-menu').get_by_role('button', name='프로젝트 브라우저', exact=True).click()
        browser = page.get_by_role('region', name='프로젝트 브라우저', exact=True)
        expect(browser).to_be_visible()
        ready = page.evaluate('performance.now()-restoreClick')
        if '--working-copy' in flags:
            expect(browser.get_by_role('textbox', name='의미 객체 검색', exact=True)).to_have_value(d.TARGET)
            expect(browser.locator(f'[data-object="{d.NS}::{d.TARGET}"]')).to_be_visible()
            print('PASS saved working-copy query and exact result restored', flush=True)
        r.choose_tree_location(browser, f'[data-tree-id="{d.NS}::StockFolder"]')
        r.search(browser, d.LABEL, d.TARGET)
        print('actual-command', json.dumps({'attemptMs': page.evaluate('commandAttempt'),
              'clickMs': page.evaluate('commandClick'), 'browserReadyMs': ready,
              'searchReadyMs': page.evaluate('performance.now()-restoreClick')}), flush=True)
        if not any(k.startswith('browser') for k in keys):
            browser.locator('[data-close]').click()
    for key in keys:
        window = page.locator(f'.window[data-key="{key}"]')
        expect(window).to_be_visible()
        assert '이 창의 실제 기능을 다시 연결해야 합니다' not in window.inner_text(), key
        if key in expected:
            expect(window.locator('[data-property-value]').first).to_be_editable()
    assert property_snapshot(page, keys) == expected
    page.wait_for_function('keys=>["workspace","commands",...keys.map(k=>k+"-editable")].every(k=>k in restoreMarks)', arg=list(expected))
    if cdp:
        (f.root / f'{label}.cpuprofile').write_text(json.dumps(cdp.send('Profiler.stop')['profile']))
        cdp.detach()
    marks = page.evaluate('restoreMarks')
    edits = [marks[key + '-editable'] for key in expected]
    wire = page.evaluate("()=>{const rows=performance.getEntriesByType('resource').filter(r=>r.name.endsWith('/api/request'));return {wireRequests:rows.length,wireBytes:rows.reduce((n,r)=>n+r.encodedBodySize,0)}}")
    print(json.dumps({'run': label, 'windows': count, 'objects': objects, 'pendingSummaryCards': pending, **wire,
                      'workspaceMs': marks['workspace'], 'firstEditableMs': min(edits, default=None),
                      'lastEditableMs': max(edits, default=None), 'commandsMs': marks['commands'],
                      'marks': marks}), flush=True)
    print('trace', json.dumps(page.evaluate('confectoryWebUITrace')), flush=True)
    if expected:
        # Actual input after the captured ready mark, without changing source.
        key = next(k for k in expected if k.startswith('editor-'))
        field = r.floating.property_value(page.locator(f'.window[data-key="{key}"]'), 'Note')
        original = field.input_value()
        field.press('End'); field.press('Space')
        expect(field).to_have_value(original + ' ')
        field.press('Backspace'); expect(field).to_have_value(original)
    f.original()
    if '--verify-state-reuse' in flags:
        mounted = f.mount()
        try:
            hashes = mounted.get('stateFieldHashes', {})
            assert hashes.get('inventory') and mounted['state']['inventory']['status']=='available', mounted.keys()
            request = {'op':'update','view':mounted['view'],'scope':mounted['scope']}
            full = f.raw(request)
            assert full['ok'] and full['state']['inventory'] == mounted['state']['inventory']
            wrong = f.raw(dict(request, knownStateFields={'inventory':'0'*64}))
            assert wrong['ok'] and wrong['state']['inventory']==full['state']['inventory']
            exact = f.raw(dict(request, knownStateFields={'inventory':hashes['inventory']}))
            assert exact['ok'] and 'inventory' not in exact['state'] and exact['reusedStateFields']['inventory']==hashes['inventory'], exact.keys()
            stale = f.raw(dict(request, scope=dict(mounted['scope'], projectActivation='invalid-activation'), knownStateFields=hashes))
            assert not stale['ok']
            print('PASS exact public metadata reuse; legacy/full, wrong token and project scope guards', flush=True)
        finally:
            f.raw({'op':'dispose','view':mounted['view']})
    if {'--verify-no-speculative-model', '--verify-restore-completion'} & flags:
        page.remove_listener('request', capture_prepare)
    if '--verify-restore-completion' in flags and label == 'cold':
        assert len(opened_requests) == 3 and all(row.get('completion') is True and row['input'].get('restoreSaved') is True for row in opened_requests), opened_requests
        print('PASS exact three ordinary restored owner admissions use bounded completion replies', flush=True)
    if '--verify-no-speculative-model' in flags:
        assert all(row.get('restoreStatuses') is True for row in prepared_requests), prepared_requests
        if label == 'cold' and count == 8:
            assert len(prepared_requests) == 1, prepared_requests
        print('PASS large inventory avoids impossible speculative property preparation; restore still uses verified admission', flush=True)


try:
    with sync_playwright() as p, p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox']) as browser:
        start(0)
        page = new_page(browser)
        expect(page.locator('.work-body')).to_be_visible()
        if count == 8:
            window = r.browser_window(page)
            r.choose_tree_location(window, f'[data-tree-id="{d.NS}::ExtraFolder2"]')
            r.search(window, d.LABEL, 'Extra2')
            window.locator(f'[data-object="{d.NS}::Extra2"]').click(button='right')
            page.locator('.context-menu').get_by_role('button', name='스키마 열기', exact=True).click()
            expect(page.locator('.window[data-key="schema"] [data-property-value]').first).to_be_editable()
        for name, folder in [(d.TARGET, 'StockFolder'), (d.PEER, 'PeerFolder'), ('Extra1', 'ExtraFolder1')][:min(count, 3)]:
            r.floating.open_properties(page, name, folder)
        if count == 8:
            for label, key in [('개념 맵', 'map'), ('빌드 작업', 'builds'), ('의미 편집 이력', 'history')]:
                expect(page.locator('#project-menu')).to_be_enabled()
                page.locator('#title').click()
                page.locator('.context-menu').get_by_role('button', name='프로젝트 도구', exact=True).click()
                page.locator('.nav-menu').get_by_role('button', name=label, exact=True).click()
                expect(page.locator(f'.window[data-key="{key}"]')).to_be_visible()
        else:
            for key in page.locator('.window:visible').evaluate_all('rows=>rows.map(w=>w.dataset.key).filter(Boolean)'):
                window = page.locator(f'.window[data-key="{key}"]:visible')
                if not key.startswith('editor-') and window.count() and window.locator('[data-close]').count():
                    window.locator('[data-close]').first.click()
        if '--working-copy' in flags:
            restored_browser = r.browser_window(page)
            restored_browser.locator('[data-catalog-root]').click()
            r.search(restored_browser, d.TARGET, d.TARGET)
        keys = page.locator('.window:visible').evaluate_all('rows=>rows.map(w=>w.dataset.key).filter(Boolean)')
        keys = [key for key in keys if key.startswith('editor-') or count == 8 and (key.startswith('browser') or key in ('schema', 'map', 'builds', 'history'))]
        assert len(keys) == count, keys
        expected = property_snapshot(page, keys)
        assert len(expected) == (4 if count == 8 else count)
        page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"')
        page.evaluate('()=>confectoryFlushPresentation()')
        page.evaluate('()=>globalThis.confectoryWebUITrace=[]')
        d.leave_to_home(page)
        measure(page, 'warm', keys, expected)
        if '--working-copy' in flags:
            # The measured command navigates into catalogue mode. Restore the
            # working-copy filter again so cold startup tests the same mode.
            restored_browser = r.browser_window(page)
            restored_browser.locator('[data-catalog-root]').click()
            r.search(restored_browser, d.TARGET, d.TARGET)
        page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"')
        page.evaluate('()=>confectoryFlushPresentation()')
        page.close(); f.stop(); f.env.pop('CONFECTORY_WEB_PROJECT', None)
        start(1)
        page = new_page(browser)
        expect(page.locator('.home-grid')).to_be_visible()
        measure(page, 'cold', keys, expected)
        if '--verify-restored-map' in flags:
            graph = page.locator('.window[data-key="map"]')
            expect(graph.locator('[data-map-scene]')).to_be_visible()
            # The common initial projection is an actual host response; no extra
            # map read is necessary when it satisfies the pending restoration.
            trace = page.evaluate('confectoryWebUITrace')
            assert any(row.get('endpoint') == 'localInventory' and row.get('code') == 'completed' for row in trace), trace
            assert not any(row.get('endpoint') == 'relationsMap' for row in trace), trace
            schema = f.projects[0].parent / 'private-source-StockInfo.celem'
            original = schema.read_bytes()
            primary = page.locator('.window[data-key="schema"]')
            note = r.floating.property_value(primary, 'Note')
            note.fill('Retained unsaved primary input')
            detached_key = next(key for key in expected if key.startswith('editor-'))
            detached = page.locator(f'.window[data-key="{detached_key}"]')
            r.floating.property_value(detached, 'Note').fill('Retained unsaved detached input')
            schema.write_text(schema.read_text().rstrip()[:-1] + ' field MapReloadProbe single general string;\n}\n')
            try:
                if '--verify-filter-freshness' in flags:
                    filtered = r.browser_window(page)
                    page.evaluate('()=>globalThis.confectoryWebUITrace=[]')
                    filtered.locator('[data-catalog-root]').click()
                    page.wait_for_function("()=>confectoryWebUITrace.some(r=>r.endpoint==='objects'&&r.code==='completed')")
                    expect(page.locator('#project-menu')).to_be_enabled()
                    # The relation projection itself may correctly be stale until
                    # explicit map reload. Here require the actual filtered view's
                    # fresh schema, not a search result from the old projection.
                    expect(d.field(detached, 'MapReloadProbe')).to_be_visible()
                    expect(r.floating.property_value(detached, 'Note')).to_have_value('Retained unsaved detached input')
                    print('PASS working-copy filter revalidates externally changed detached schema and retains local input', flush=True)
                page.evaluate('()=>globalThis.confectoryWebUITrace=[]')
                graph.locator('[data-map-reload]').press('Enter')
                page.wait_for_function("()=>confectoryWebUITrace.some(r=>r.endpoint==='relationsMap'&&r.code==='completed')")
                expect(d.field(page.locator('.window[data-key="schema"]'), 'MapReloadProbe')).to_be_visible()
                expect(r.floating.property_value(primary, 'Note')).to_have_value('Retained unsaved primary input')
                expect(r.floating.property_value(detached, 'Note')).to_have_value('Retained unsaved detached input')
                expect(d.field(detached, 'MapReloadProbe')).to_be_visible()
                print('PASS shared initial map projection and explicit fresh external-schema reload', flush=True)
                if '--repeat-map' in flags:
                    expect(page.locator('#project-menu')).to_be_enabled()
                    def delta_counts():
                        rows = [json.loads(line.split(' ', 1)[1]) for line in (f.root / 'host-1.log').read_text().splitlines() if line.startswith('CONFECTORY_RELATION_ROWS ')]
                        return rows[-1] if rows else None
                    if '--verify-relation-delta' in flags:
                        delta = delta_counts()
                        assert delta and delta['parsed'] <= 1 and delta['reused'] >= 400, delta
                        print('PASS unchanged draft rows retained; authoritative external schema reread separately', delta, flush=True)
                    page.evaluate('()=>globalThis.confectoryWebUITrace=[]')
                    graph.locator('[data-map-reload]').evaluate("el=>el.addEventListener('keydown',()=>globalThis.mapRepeatStart=performance.now(),{once:true,capture:true})")
                    graph.locator('[data-map-reload]').press('Enter')
                    page.wait_for_function("()=>confectoryWebUITrace.some(r=>r.endpoint==='relationsMap'&&r.code==='completed')")
                    expect(page.locator('#project-menu')).to_be_enabled()
                    print('repeat-map-ms', page.evaluate('performance.now()-mapRepeatStart'), flush=True)
                    if '--verify-relation-delta' in flags:
                        delta = delta_counts()
                        assert delta and delta['parsed'] == 0 and delta['reused'] >= 400, delta
                        print('PASS unchanged relation rows need no authoring request', delta, flush=True)

            finally:
                schema.write_bytes(original)
            f.original()
finally:
    f.stop()
    print('evidence', f.root, flush=True)
