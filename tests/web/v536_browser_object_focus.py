"""A real delayed status response must not lose a focused Browser object card."""
import json
import sys
import time
from playwright.sync_api import sync_playwright, expect
import v536_information_shared_io_fixture as x

f=x.f
held=[]
reproduce='reproduce' in sys.argv[3:]
keep_input='input' in sys.argv[4:]
try:
    f.start(0);f.invoke('select',{'id':x.owner});f.invoke('saveDraft',{})
    baseline=next(f.project.glob('.confectory/edit-workspaces/*/draft.json')).read_bytes()
    with sync_playwright() as pw:
        expect.set_options(timeout=30000)
        f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700})
        def delay(route):
            body=route.request.post_data_json
            if not held and body.get('op')=='invoke' and body.get('endpoint')=='browserDrafts' and x.f.n+'FunctionParent' in body.get('input',{}).get('ids',[]):
                held.append(route)
            else:route.fallback()
        f.page.route('**/api/request',delay)
        try:
            f.page.locator('#workspace').click(button='right',position={'x':80,'y':100})
            f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click()
            b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=info]').click()
            deadline=time.monotonic()+20
            while not held and time.monotonic()<deadline:f.page.wait_for_timeout(20)
            assert held,'Expected the actual background information-status request'
            b.locator('[data-browser-control=object-query]').fill('FreeInfo')
            b.locator('[data-browser-control=object-search]').click()
            row=b.locator('[data-object="'+x.owner+'"]');expect(row).to_have_attribute('aria-disabled','false');row.focus()
            row.evaluate('el=>globalThis.focusedObjectBeforeStatus=el')
            before=f.page.evaluate('()=>({focused:document.activeElement.dataset.object,connected:focusedObjectBeforeStatus.isConnected})')
            assert before=={'focused':x.owner,'connected':True},before
            if keep_input:
                query=b.locator('[data-browser-control=object-query]');query.focus();query.evaluate('el=>el.setSelectionRange(2,6)')
            held[0].continue_()
            f.page.wait_for_function('()=>!focusedObjectBeforeStatus.isConnected',timeout=30000)
            f.idle()
            after=f.page.evaluate('()=>({focused:document.activeElement.dataset.object||null,tag:document.activeElement.tagName,oldConnected:focusedObjectBeforeStatus.isConnected})')
            (f.case/'browser-focus.json').write_text(json.dumps({'before':before,'after':after,'reproduce':reproduce},ensure_ascii=False,indent=2))
            f.page.screenshot(path=str(f.case/'browser-after-status.png'))
            expect(b.locator('[data-browser-control=object-query]')).to_have_value('FreeInfo')
            if keep_input:
                assert f.page.evaluate('()=>document.activeElement.dataset.browserControl')=='object-query'
                assert f.page.evaluate('()=>[document.activeElement.selectionStart,document.activeElement.selectionEnd]')==[2,6]
                assert next(f.project.glob('.confectory/edit-workspaces/*/draft.json')).read_bytes()==baseline
                x.unchanged();f.checked('목록 재렌더는 사용자가 옮긴 검색 입력 포커스·caret·검색어와 기존 checkpoint를 보존한다')
            elif reproduce:
                assert after['focused'] is None and after['tag']=='BODY',after
                mark=len(f.traffic);f.page.keyboard.press('Enter');f.page.wait_for_timeout(300)
                assert not any(row.get('invoke',{}).get('endpoint')=='select' for row in f.traffic[mark:])
                expect(f.owner()).to_have_count(0)
                f.checked('실제 배경 상태응답의 Browser 재렌더가 카드 포커스를 BODY로 잃고 Enter 선택을 보내지 않는 원인을 재현한다')
            else:
                assert after['focused']==x.owner,after
                f.page.keyboard.press('Enter')
                expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo')
                expect(f.owner().get_by_label('Power 기본값',exact=True)).to_have_value('9223372036854775806')
                assert next(f.project.glob('.confectory/edit-workspaces/*/draft.json')).read_bytes()==baseline
                x.unchanged()
                f.checked('배경 상태응답의 재렌더 뒤 같은 카드 포커스와 단일 Enter 열기를 보존하며 입력·checkpoint·원문은 바꾸지 않는다')
        finally:
            if held:
                try:held[0].continue_()
                except Exception:pass
            f.page.unroute_all(behavior='wait');f.browser.close()
finally:
    (f.case/'browser-focus-traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2))
    print(json.dumps({'checks':f.checks,'evidence':str(f.case),'reproduce':reproduce,'actualWindows':False},ensure_ascii=False))
    f.stop()
