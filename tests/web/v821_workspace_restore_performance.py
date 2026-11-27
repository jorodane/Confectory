"""Measure actual restored workspace readiness; no latency threshold.

Run on Linux with the ordinary EditorHome build report and authoring host:
  python tests/web/v821_workspace_restore_performance.py REPO BUILD_REPORT 8
Repeat with 0 or 1, or repeat the same command for a no-op comparison.
All projects, including the eight recent listings, are disposable synthetic copies.
The default waits for Home summaries to finish before timing the actual tile click.
Use --during-summary to measure contention instead. Optional --trace-files is a
separate diagnostic run (strace overhead makes its timings incomparable).
"""
import json
import shutil
import sys

from playwright.sync_api import expect, sync_playwright
from editor_navigation import goto_editor
import v821_property_window_reopen_ui as r

f, d = r.fixture, r.fallback
count = int(sys.argv[3])
assert count in (0, 1, 8), 'Choose 0, 1, or 8 restored windows'
flags = set(sys.argv[4:])
assert flags <= {'--during-summary', '--trace-files'}, flags
expect.set_options(timeout=90000)
f.env['CONFECTORY_UI_TRACE'] = '1'
r.seed()
for manifest in f.projects:
    registrations = []
    for i in range(36):
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
      button.addEventListener('click',()=>{const start=performance.now();function mark(name,ok){if(ok&&!(name in restoreMarks))restoreMarks[name]=performance.now()-start;}
      const visible=e=>!!e&&e.getClientRects().length>0&&!e.closest('[hidden]');
      const editable=e=>visible(e)&&!e.disabled&&!e.readOnly&&!e.closest('[inert]');
      function frame(){mark('workspace',visible(document.querySelector('.work-body'))&&editable(document.querySelector('#chat-input')));
        mark('commands',visible(document.querySelector('#project-menu'))&&!document.querySelector('#project-menu').disabled);
        for(const w of document.querySelectorAll('.window[data-key]')){const key=w.dataset.key;if(!keys.includes(key))continue;
          if(key==='schema'||key.startsWith('editor-'))mark(key+'-editable',visible(w)&&editable(w.querySelector('[data-property-value]'))&&!w.textContent.includes('이 창의 실제 기능을 다시 연결해야 합니다'));}
        if(performance.now()-start<60000)requestAnimationFrame(frame);}
      requestAnimationFrame(frame);},{once:true,capture:true});}''', keys)
    tile.click()
    expect(page.locator('.work-body')).to_be_visible()
    expect(page.locator('#project-menu')).to_be_enabled()
    for key in keys:
        window = page.locator(f'.window[data-key="{key}"]')
        expect(window).to_be_visible()
        assert '이 창의 실제 기능을 다시 연결해야 합니다' not in window.inner_text(), key
        if key in expected:
            expect(window.locator('[data-property-value]').first).to_be_editable()
    assert property_snapshot(page, keys) == expected
    page.wait_for_function('keys=>["workspace","commands",...keys.map(k=>k+"-editable")].every(k=>k in restoreMarks)', arg=list(expected))
    marks = page.evaluate('restoreMarks')
    edits = [marks[key + '-editable'] for key in expected]
    print(json.dumps({'run': label, 'windows': count, 'pendingSummaryCards': pending,
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
        page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"')
        page.evaluate('()=>confectoryFlushPresentation()')
        page.close(); f.stop(); f.env.pop('CONFECTORY_WEB_PROJECT', None)
        start(1)
        page = new_page(browser)
        expect(page.locator('.home-grid')).to_be_visible()
        measure(page, 'cold', keys, expected)
finally:
    f.stop()
    print('evidence', f.root, flush=True)
