"""Connect installed Window/Input packs in an already UI-authored disposable project.

Pass the Linux editor report, repo and evidence directory from
editor_new_game_workflow.py. The existing Timing Puzzle source is not edited
by this test outside ordinary Pack Manager Review/Confirm.
"""
import json,sys
from pathlib import Path
from playwright.sync_api import expect,sync_playwright
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"gui"))
import editor_local_first_workflow as f
from editor_logic_workflow import run_from_dock

repo=Path(sys.argv[2]).resolve()
root=Path(sys.argv[3]).resolve();project=root/'projects'/'Timing Puzzle'
assert root.name.startswith('confectory-local-first-') and project.is_dir()
manifest=project/'project.cproj';marker=root/'puzzle-score.txt'
old=f.ROOT;f.ROOT=root;f.PROFILE=root/'profile';f.PROJECTS=root/'projects';f.TITLE='Timing Puzzle';f.repo=repo
f.ENV={key:str(value).replace(str(old),str(root)) for key,value in f.ENV.items()}
f.ENV.update(CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_ELEMENT_AUTHORING_HOST=str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'),CONFECTORY_PROJECT_EXECUTION_HOST=str(repo/'targets/project-execution-host/bin/Release/net10.0/Confectory.ProjectExecutionHost.dll'))

def review_pack(page,id):
    page.get_by_role('tab',name='Pack Manager',exact=True).click()
    page.evaluate('async()=>await confectoryFlushPresentation()');expect(page.locator('#home-pack-connect')).to_be_enabled();page.locator('#home-pack-connect').click()
    dialog=page.get_by_role('dialog',name='설치된 팩 연결',exact=True)
    try: dialog.locator('[data-installed-pack-choice]').select_option(id)
    except Exception: print('Editor status:',page.locator('#status').all_text_contents(),flush=True);raise
    dialog.locator('[data-installed-pack-review]').click()
    review=page.locator('.window[data-key=review]')
    expect(review).to_be_visible(timeout=120000);expect(review).to_contain_text(id)
    if review.locator('[data-review-advanced]').is_visible():review.locator('[data-review-advanced]').click()
    if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
    return review

def confirm(page,review):
    review.locator('#confirm').click();expect(review).to_be_hidden(timeout=120000)
    expect(page.locator('#status')).to_have_text('검토한 변경을 최종 소스에 반영했습니다.')

with sync_playwright() as pw,pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) as browser:
    if "--cold-only" not in sys.argv:
        with f.web(browser,"pack-connect") as page:
            before=manifest.read_bytes()
            assert b'dependency Confectory.Window ' not in before
            review=review_pack(page,'Confectory.Window');review.locator('[data-reject]').click();expect(review).to_be_hidden()
            assert manifest.read_bytes()==before
            review=review_pack(page,'Confectory.Window');confirm(page,review)
            window=manifest.read_text()
            assert 'dependency Confectory.Window version' in window and 'registry Confectory.RenderInput ' in window
            assert 'dependency Confectory.RenderInput ' not in window
            review=review_pack(page,'Confectory.RenderInput');confirm(page,review)
            after=manifest.read_text()
            assert 'dependency Confectory.RenderInput version' in after
            assert after.count('registry Confectory.RenderInput ')==1
            assert all(line in after for line in before.decode().splitlines() if line.strip())
            page.evaluate('async()=>await confectoryFlushPresentation()')
            print('PASS cancel, Window closure, direct RenderInput, no duplicate registry',flush=True)
    with f.web(browser,"cold-pack-connect") as page:
        page.evaluate('async()=>await confectoryFlushPresentation()')
        tab=page.get_by_role('tab',name='Pack Manager',exact=True);tab.click();expect(tab).to_have_attribute("aria-selected","true",timeout=30000)
        expect(page.locator('.home-pack-row[data-pack="Confectory.Window"]')).to_be_visible(timeout=30000)
        expect(page.locator('.home-pack-row[data-pack="Confectory.RenderInput"]')).to_be_visible()
        page.get_by_role('tab',name='Workspace',exact=True).click();run_from_dock(page,marker,'1')
        print('PASS cold editor shows both confirmed packs; original authored score still runs',flush=True)
