"""Actual authored runtime window with explicit registered provider.

Run after project_installed_pack_registration.py on its disposable UI-created
Timing Puzzle evidence directory. No feature/source files are seeded or edited.
"""
import sys
from pathlib import Path
from playwright.sync_api import expect, sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'gui'))
import editor_local_first_workflow as f

repo = Path(sys.argv[2]).resolve()
root = Path(sys.argv[3]).resolve()
project = root / 'projects' / 'Timing Puzzle'
assert root.name.startswith('confectory-local-first-') and project.is_dir()
manifest = project / 'project.cproj'
old = f.ROOT
f.ROOT, f.PROFILE, f.PROJECTS, f.TITLE, f.repo = root, root/'profile', root/'projects', 'Timing Puzzle', repo
f.ENV = {key: str(value).replace(str(old), str(root)) for key, value in f.ENV.items()}
f.ENV.update(CONFECTORY_EDITOR_REPO=str(repo), CONFECTORY_ELEMENT_AUTHORING_HOST=str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'), CONFECTORY_PROJECT_EXECUTION_HOST=str(repo/'targets/project-execution-host/bin/Release/net10.0/Confectory.ProjectExecutionHost.dll'))
expect.set_options(timeout=30000)


def select_search(picker, search, expected):
    picker.locator('[data-resource-query]').fill(search)
    candidate = picker.locator(f'[data-resource-feature="{expected}"]')
    expect(candidate).to_be_visible()
    return candidate


from editor_new_game_workflow import browser as project_browser, confirm, stage_entry
from editor_logic_workflow import find_project_item
import subprocess,time
FEATURE='ShowTimingWindow'
ns=manifest.read_text().split()[1]
def run_window(page):
    page.evaluate('async()=>await confectoryFlushPresentation()')
    tab=page.get_by_role('tab',name='Workspace',exact=True)
    if tab.is_visible() and tab.get_attribute('aria-selected')!='true':tab.click();expect(tab).to_have_attribute('aria-selected','true')
    page.get_by_role('button',name='프로젝트 실행',exact=True).click()
    deadline=time.monotonic()+120
    while time.monotonic()<deadline:
        tree=subprocess.check_output(['xwininfo','-root','-tree'],text=True)
        if 'Timing Puzzle Window' in tree:break
        page.wait_for_timeout(100)
    else:raise AssertionError('Native window not observed')
    print('PASS actual X11 Timing Puzzle Window',flush=True)
    expect(page.locator('.run-window:visible [data-run-frame]')).to_have_text('종료 코드 0',timeout=120000)
with sync_playwright() as pw, pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox']) as browser:
    if "--cold-only" not in sys.argv:
        with f.web(browser, 'provider-window') as page:
            page.evaluate('async()=>await confectoryFlushPresentation()')
            page.get_by_role('tab',name='Workspace',exact=True).click()
            for key in ('targets','packs','blueprint','declaration'):
                other=page.locator(f'.window[data-key={key}]')
                if other.is_visible():other.locator('[data-close]').first.click()
            if not (project/'elements'/f'{FEATURE}.celem').exists():
                b=project_browser(page);b.get_by_role('button',name='기능',exact=True).click();b.locator('[data-new]').click()
                page.get_by_role('button',name='기능 생성',exact=True).click()
                d=page.get_by_role('dialog',name='새 기능 만들기',exact=True)
                d.locator('#object-name').fill(FEATURE);d.get_by_role('button',name='생성',exact=True).click();expect(d).to_be_hidden()
                dec=page.locator('.window[data-key=declaration]');expect(dec.locator('.object-title-name')).to_have_text(FEATURE)
                dec.locator('[data-function-write-direct]').click();panel=page.locator('.window[data-key=blueprint]');expect(panel.locator('.function-document')).to_be_visible()
                panel.locator('[data-document-code=body]').click();dialog=page.locator('.bp-script-dialog');src=dialog.locator('[data-code-source]');expect(src).to_be_visible()
                src.evaluate("""el=>{const p=[...el.closest('.bp-script-editor').querySelectorAll('[data-code-highlight]>span')];const i=p.findIndex(x=>x.dataset.codeRegion==='body');const n=p.slice(0,i).reduce((a,x)=>a+x.textContent.length,0);el.focus();el.setSelectionRange(n,n+p[i].textContent.length)}""")
                page.keyboard.insert_text('return 0; // Window entry');dialog.locator('[data-code-save]').click();expect(dialog).to_be_hidden()
                panel.locator('[data-bp-save]').click();expect(panel.locator('.bp-status')).to_have_text('저장됨',timeout=120000);confirm(page,panel.locator('[data-bp-complete]'))
                panel.locator('[data-close]').first.click()
                if b.is_visible():b.locator('[data-close]').first.click()
                if dec.is_visible():dec.locator('[data-close]').first.click()
            find_project_item(page,ns+'::'+FEATURE,'기능')
            dec=page.locator('.window[data-key=declaration]');expect(dec.locator('.object-title-name')).to_have_text(FEATURE)
            page.evaluate('async()=>await confectoryFlushPresentation()')
            dec.locator('[data-registered-provider]').click()
            d=page.get_by_role('dialog',name='등록 팩 구현 지정',exact=True)
            d.locator('[data-provider-function]').fill('Confectory.Window::Open');d.locator('[data-provider-implementation]').fill('Confectory.Window::Native');d.locator('[data-provider-apply]').click()
            expect(d).to_be_hidden(timeout=30000)
            assert 'provide Confectory.Window::Open with' not in (project/'elements'/f'{FEATURE}.celem').read_text()
            print('PASS provider staged without writing source',flush=True)
            confirm(page,dec.locator('[data-feature-action=confirm]'))
            print('PASS provider confirmed',flush=True)
            dec.locator('[data-function-write-direct]').click();panel=page.locator('.window[data-key=blueprint]');doc=panel.locator('.function-document');expect(doc).to_be_visible()
            doc.locator('[data-document-insert-call="$entry"]').click();picker=page.get_by_role('dialog',name='블루프린트 노드 검색');select_search(picker,'Confectory.Window::Open','Confectory.Window::Open').click()
            cell=doc.locator('[data-document-cell^="call_"]');expect(cell).to_be_visible()
            for k,v in [('title','"Timing Puzzle Window"'),('width','640'),('height','480'),('closeAfterMilliseconds','10000')]:
                value=cell.locator(f'[data-document-value][data-document-port="field:{k}"]');value.click();search=page.get_by_role('dialog',name='핀 값 선택').get_by_role('searchbox',name='값 검색');search.fill(v);search.press('Enter')
            panel.locator('[data-bp-save]').click();expect(panel.locator('.bp-status')).to_have_text('저장됨',timeout=120000);confirm(page,panel.locator('[data-bp-complete]'))
            panel.locator('[data-close]').first.click()
            if dec.is_visible():dec.locator('[data-close]').first.click()
            r,w=stage_entry(page,ns+'::'+FEATURE);r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);w.locator('[data-close]').click()
            run_window(page)
    with f.web(browser,'cold-provider-window') as page:
        assert f'entry {ns}::{FEATURE};' in manifest.read_text()
        assert 'provide Confectory.Window::Open with Confectory.Window::Native;' in (project/'elements'/f'{FEATURE}.celem').read_text()
        page.evaluate('async()=>await confectoryFlushPresentation()')
        tab=page.get_by_role('tab',name='Workspace',exact=True)
        if tab.get_attribute('aria-selected')!='true':tab.click();expect(tab).to_have_attribute('aria-selected','true')
        for key in ('targets','packs','blueprint','declaration'):
            other=page.locator(f'.window[data-key={key}]')
            if other.is_visible():other.locator('[data-close]').first.click()
        find_project_item(page,ns+'::'+FEATURE,'기능')
        dec=page.locator('.window[data-key=declaration]');expect(dec.locator('[data-registered-provider-list]')).to_contain_text('Confectory.Window::Open')
        source=project/'elements'/f'{FEATURE}.celem';before=source.read_bytes()
        dec.locator('[data-registered-provider]').click()
        dialog=page.get_by_role('dialog',name='등록 팩 구현 지정',exact=True)
        dialog.locator('[data-provider-function]').fill('Confectory.Window::Open')
        dialog.locator('[data-provider-implementation]').fill('Confectory.Window::CloseBody')
        dialog.locator('[data-provider-apply]').click()
        expect(dialog.locator('[data-provider-error]')).not_to_have_text('')
        assert source.read_bytes()==before
        dialog.locator('[data-close]').click()
        dec.locator('[data-close]').first.click()
        print('PASS cold binding visible and mismatched provider rejected without writing',flush=True)
        run_window(page)
        print('PASS cold editor runs native window',flush=True)
