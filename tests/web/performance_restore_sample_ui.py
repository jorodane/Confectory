"""Actual Home-card 8-window restore capture; no compiler, account, or web service.
Run with the ordinary Linux EditorHome build report and authoring host.
The Windows batch and native WebView2 are not executed by this test.
"""
import json
import shutil
import time
from pathlib import Path

from playwright.sync_api import expect, sync_playwright
from editor_navigation import goto_editor
from v821_project_browser_search_labels import browser_window
import v666_workspace_finder_fixture as f

sample = f.root / 'performance-restore-sample'
shutil.copytree(f.repo / 'examples/performance-restore-sample', sample)
original = {p: p.read_bytes() for p in sample.rglob('*') if p.is_file()}
local = f.root / 'local-appdata'; local.mkdir()
profile = f.root / 'restore-profile'; profile.mkdir()
(profile / 'projects.json').write_text(json.dumps([{'path':str(sample/'project.cpack'),'title':'Restore sample','description':''}]))
f.env.update(XDG_DATA_HOME=str(local), CONFECTORY_HOME_STORAGE=str(profile), CONFECTORY_ENTRY_STORAGE=str(f.root/'restore-entry'), CONFECTORY_PERFORMANCE='1')
f.env.pop('CONFECTORY_WEB_PROJECT', None)
logs=local/'Confectory'/'Performance'; ns='Confectory.PerformanceRestoreSample'; secret='SYNTHETIC_PRIVATE_RESTORE_SENTINEL'
expect.set_options(timeout=60000)

def page_for(browser,n):
    f.start(n); page=browser.new_page(viewport={'width':2000,'height':1200})
    page.route('**/*',lambda route:route.continue_() if route.request.url.startswith(f.origin+'/') else route.abort())
    goto_editor(page,f.url)
    card=page.locator('.project-card').filter(has=page.get_by_role('heading',name='Restore sample',exact=True))
    expect(card.locator('[data-stat="objects"]')).to_have_text('40')
    card.locator('[data-enter]').click(); expect(page.locator('#project-menu')).to_be_enabled()
    return page

def find(page,name):
    w=browser_window(page); w.get_by_role('textbox',name='의미 객체 검색',exact=True).fill('Sample '+name)
    w.get_by_role('button',name='검색 확정',exact=True).click()
    row=w.locator(f'[data-object="{ns}::Sample{name}"]');expect(row).to_be_visible();expect(page.locator('#project-menu')).to_be_enabled();return row

def events(page,expected):
    path=max(logs.glob('*/engine.jsonl'),key=lambda p:p.stat().st_mtime_ns); deadline=time.monotonic()+30
    while time.monotonic()<deadline:
        try: rows=[json.loads(line) for line in path.read_text().splitlines()]
        except (OSError,json.JSONDecodeError):page.wait_for_timeout(100);continue
        if expected <= {r['stage'] for r in rows}:
            assert all(set(r)=={'stage','operation','elapsedMs','atMs','pageMs'} for r in rows)
            raw=path.read_text();assert secret not in raw and str(sample) not in raw and ns not in raw and 'Restore sample' not in raw
            return path,rows
        page.wait_for_timeout(100)
    raise AssertionError((path,expected))

try:
    with sync_playwright() as p,p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) as browser:
        # Normal profile remains uninstrumented. Use another disposable profile.
        off=f.root/'off-profile';off.mkdir();(off/'projects.json').write_bytes((profile/'projects.json').read_bytes())
        f.env.pop('CONFECTORY_PERFORMANCE',None);f.env['CONFECTORY_HOME_STORAGE']=str(off)
        page=page_for(browser,9);page.close();f.stop();assert not logs.exists()
        f.env.update(CONFECTORY_HOME_STORAGE=str(profile),CONFECTORY_PERFORMANCE='1')
        page=page_for(browser,0)
        row=find(page,'D');row.click(button='right');page.locator('.context-menu').get_by_role('button',name='스키마 열기',exact=True).click()
        expect(page.locator('.window[data-key="schema"] [data-property-value]').first).to_be_editable()
        for name in 'ABC':
            row=find(page,name);row.click(button='right');page.locator('.context-menu').get_by_role('button',name='새 창으로 열기',exact=True).click()
            expect(page.locator(f'.window[data-element-owner="{ns}::Sample{name}"] [data-property-value]').first).to_be_editable()
            if name=='A':
                a=page.locator(f'.window[data-element-owner="{ns}::SampleA"]');a.locator('[data-close]').click();expect(a).to_be_hidden();find(page,'A').press('Enter');expect(a).to_be_visible();expect(a.locator('[data-property-value]').first).to_be_editable()

        for label,key in [('개념 맵','map'),('빌드 작업','builds'),('의미 편집 이력','history')]:
            expect(page.locator('#project-menu')).to_be_enabled();page.locator('#title').click();page.locator('.context-menu').get_by_role('button',name='프로젝트 도구',exact=True).click();page.locator('.nav-menu').get_by_role('button',name=label,exact=True).click();expect(page.locator(f'.window[data-key="{key}"]')).to_be_visible()
        a.get_by_label('Note 기본값',exact=True).fill(secret)
        page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"');page.evaluate('()=>confectoryFlushPresentation()')
        first,rows=events(page,{'window-ready','browser-open-ready','browser-search-ready'});assert {r['operation'] for r in rows if r['stage']=='window-ready'} >= {'openEditorView','reopenEditorView'}
        page.close();f.stop()
        page=page_for(browser,1)
        for key in ('browser','schema','editor-1','editor-2','editor-3','map','builds','history'):expect(page.locator(f'.window[data-key="{key}"]')).to_be_visible()
        for key in ('schema','editor-1','editor-2','editor-3'):expect(page.locator(f'.window[data-key="{key}"] [data-property-value]').first).to_be_editable()
        a=page.locator(f'.window[data-element-owner="{ns}::SampleA"]');expect(a.get_by_label('Note 기본값',exact=True)).to_have_value(secret);field=a.get_by_label('Note 기본값',exact=True);field.press('End');field.press('Space');expect(field).to_have_value(secret+' ');field.press('Backspace')
        find(page,'A')
        second,rows=events(page,{'restore-workspace-ready','restore-first-editable','restore-last-editable','restore-commands-ready','browser-open-ready','browser-search-ready'})
        assert first!=second
        for stage in ('restore-workspace-ready','restore-first-editable','restore-last-editable','restore-commands-ready','browser-open-ready','browser-search-ready'):
            print(stage,next(r['elapsedMs'] for r in rows if r['stage']==stage),flush=True)
        assert all(path.read_bytes()==raw for path,raw in original.items())
        print('PASS isolated 8-window cold restore, real keyboard/search, private input absent from timing logs',flush=True)
finally:f.stop();print('evidence',f.root,flush=True)
