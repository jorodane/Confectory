#!/usr/bin/env python3
"""Actual GTK creation -> Chromium authored timing-rule project -> entry Review -> Run.

Use an owned local Xorg display and the ordinary lightweight EditorHome build.
The optional second argument locates that build's repository (no source seeding).
The puzzle uses three deterministic sample tap times; interactive runtime
input/rendering is a subsequent experiment, not a simulated product UI.
"""
import json
from pathlib import Path
import sys

from playwright.sync_api import expect,sync_playwright
import editor_local_first_workflow as f
from editor_logic_workflow import find_project_item,review,run_from_dock
from editor_navigation import open_workspace_menu

f.TITLE='Timing Puzzle'
if len(sys.argv)>2:
    f.repo=Path(sys.argv[2]).resolve()
    f.ENV.update(CONFECTORY_EDITOR_REPO=str(f.repo),
        CONFECTORY_ELEMENT_AUTHORING_HOST=str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'),
        CONFECTORY_PROJECT_EXECUTION_HOST=str(f.repo/'targets/project-execution-host/bin/Release/net10.0/Confectory.ProjectExecutionHost.dll'))
MARKER=f.ROOT/'puzzle-score.txt'
FEATURE='PlayTimingPuzzle'
CONCEPT='TimingRules'

def confirm(page,control):
    r=review(page,control);r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000)
    expect(page.locator('#status')).to_have_text('검토한 변경을 최종 소스에 반영했습니다.')

def browser(page):
    open_workspace_menu(page).get_by_role('button',name='프로젝트 브라우저',exact=True).click()
    return page.locator('.window[data-key^="browser:project:"]:visible').last

def settings(page):
    page.locator('#project-menu').click()
    page.get_by_role('button',name='실행 설정',exact=True).click()
    w=page.locator('.window[data-key=targets]');expect(w.locator('[data-project-entry-choice]')).to_be_visible()
    return w

def stage_entry(page,id):
    w=settings(page)
    w.locator('[data-project-entry-choice]').select_option(id)
    w.locator('[data-project-entry-review]').click()
    r=page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=120000)
    expect(r).to_contain_text('프로젝트 실행 진입점')
    expect(r).to_contain_text(id)
    return r,w

def close_run(page):
    key=page.locator('.run-window:visible').get_attribute('data-key')
    page.locator('[data-window-tab-close="'+key+'"]').click()
    expect(page.locator('.run-window')).to_have_count(0)

def workflow():
    with f.gtk('first-native') as app:
        assert app.state()['model']['cards']==[]
        selected=app.create(f.TITLE,'Unsent game project draft')
        manifest=Path(selected['path']);ns=selected['namespace']
        assert manifest.is_relative_to(f.PROJECTS)
        original=manifest.read_bytes()
        app.run_project();assert not MARKER.exists()
    print('PASS normal GTK project creation, folder selection and original Main Run',flush=True)
    with sync_playwright() as pw,pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) as chromium:
        with f.web(chromium,'author') as page:
            find_project_item(page,ns+'::ProjectInfo','개념')
            p=page.locator('.window[data-key=schema]');confirm(page,p.locator('[data-element-action=confirm]'));p.locator('[data-close]').first.click()
            b=browser(page);b.get_by_role('button',name='개념',exact=True).click();b.locator('[data-new]').click()
            page.get_by_role('button',name='개념 생성',exact=True).click()
            d=page.get_by_role('dialog',name='새 개념 만들기',exact=True)
            d.locator('#new-declaration-name').fill(CONCEPT);d.locator('#new-declaration').click();expect(d).to_be_hidden()
            p=page.locator('.window[data-key=schema]');expect(p.locator('.object-title-name')).to_have_text(CONCEPT)
            confirm(page,p.locator('[data-element-action=confirm]'));p.locator('[data-close]').first.click()
            b.get_by_role('button',name='기능',exact=True).click();b.locator('[data-new]').click()
            page.get_by_role('button',name='기능 생성',exact=True).click()
            d=page.get_by_role('dialog',name='새 기능 만들기',exact=True);d.locator('#object-name').fill(FEATURE)
            d.get_by_role('button',name='생성',exact=True).click();expect(d).to_be_hidden()
            dec=page.locator('.window[data-key=declaration]');expect(dec.locator('.object-title-name')).to_have_text(FEATURE)
            dec.locator('[data-function-write-direct]').click()
            panel=page.locator('.window[data-key=blueprint]');expect(panel.locator('.function-document')).to_be_visible()
            text='int[] taps = new[]{ 50, 495, 850 };\nint score = 0;\nforeach(int tap in taps) if(System.Math.Abs(tap - 500) <= 50) score++;\nSystem.IO.File.WriteAllText('+json.dumps(str(MARKER))+', score.ToString());\nreturn 0;'
            panel.locator('[data-document-code=body]').click();dialog=page.locator('.bp-script-dialog')
            src=dialog.locator('[data-code-source]');expect(src).to_be_visible()
            src.evaluate('''el=>{const p=[...el.closest('.bp-script-editor').querySelectorAll('[data-code-highlight]>span')];const i=p.findIndex(x=>x.dataset.codeRegion==='body');const n=p.slice(0,i).reduce((a,x)=>a+x.textContent.length,0);el.focus();el.setSelectionRange(n,n+p[i].textContent.length)}''')
            page.keyboard.insert_text(text);dialog.locator('[data-code-save]').click();expect(dialog).to_be_hidden()
            panel.locator('[data-bp-save]').click();expect(panel.locator('.bp-status')).to_have_text('저장됨',timeout=120000)
            assert FEATURE not in manifest.read_text()
            confirm(page,panel.locator('[data-bp-complete]'))
            assert 'element '+CONCEPT+' object' in manifest.read_text() and 'element '+FEATURE+' function' in manifest.read_text()
            assert 'entry '+ns+'::Main;' in manifest.read_text()
            panel.locator('[data-close]').first.click()
            if dec.is_visible():dec.locator('[data-close]').first.click()
            if b.is_visible():b.locator('[data-close]').first.click()
            print('PASS actual concept object and new Logic Code feature authored/confirmed',flush=True)
            before=manifest.read_bytes()
            r,w=stage_entry(page,ns+'::'+FEATURE);r.locator('[data-reject]').click();expect(r).to_be_hidden()
            assert manifest.read_bytes()==before
            w.locator('[data-close]').click()
            page.get_by_role('button',name='프로젝트 실행',exact=True).click()
            expect(page.locator('.run-window:visible [data-run-frame]')).to_have_text('종료 코드 0',timeout=120000)
            assert not MARKER.exists()
            close_run(page)
            print('PASS canceled entry draft still runs original Main',flush=True)
            r,w=stage_entry(page,ns+'::'+FEATURE);r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000)
            assert manifest.read_bytes()==before.replace(('entry '+ns+'::Main;').encode(),('entry '+ns+'::'+FEATURE+';').encode())
            expect(w.locator('[data-current-project-entry]')).to_have_text(ns+'::'+FEATURE)
            w.locator('[data-close]').click()
            run_from_dock(page,MARKER,'1');close_run(page)
            print('PASS explicit entry Confirm changes only entry clause; same-session score 1/3',flush=True)
            page.evaluate('async()=>await confectoryFlushPresentation()')
        with f.web(chromium,'cold') as page:
            w=settings(page);expect(w.locator('[data-current-project-entry]')).to_have_text(ns+'::'+FEATURE)
            w.locator('[data-close]').click()
            run_from_dock(page,MARKER,'1')
            print('PASS cold new Chromium editor restores entry and executes score 1/3',flush=True)
    with f.gtk('cold-native') as app:
        app.click(100);app.wait(lambda row:row['screen']=='project' and row['model']['selected'] is not None,'GTK open Recent')
        MARKER.unlink();app.run_project();assert MARKER.read_text()=='1'
    print('PASS cold GTK Recent project runs the same confirmed entry',flush=True)

if __name__=='__main__':
    expect.set_options(timeout=30000)
    try:workflow()
    finally:print('Evidence:',f.ROOT,flush=True)
