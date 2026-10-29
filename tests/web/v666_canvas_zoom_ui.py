"""500% navigation over a real isolated engine. No grants, inference or project execution."""
import json,time
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f

snapshot={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts}
def original():assert all(p.read_bytes()==value for p,value in snapshot.items())
def popup():
    f.author().locator('[data-bp-percent]').click()
    dialog=f.page.get_by_role('dialog',name='노드 화면 배율',exact=True)
    expect(dialog).to_be_visible();return dialog
def scale():return float(f.author().locator('[data-bp-percent]').inner_text().removesuffix('%'))/100
def flush():f.page.evaluate('()=>globalThis.confectoryFlushPresentation()');f.idle()
def zoom_to(value):
    dialog=popup();dialog.locator('[data-zoom-preset="'+str(value)+'"]').click()
    expect(f.author().locator('[data-bp-percent]')).to_have_text(str(value)+'%')
    dialog.locator('[data-zoom-value]').press('Escape');return dialog
def guarded():
    original()
    writes=[row['invoke'] for row in f.traffic if row.get('invoke',{}).get('endpoint') in ('confirm','confirmGroup','saveDraft','editDraft','authorBatch')]
    assert not writes,writes

try:
    f.start(0)
    with sync_playwright() as pw:
        expect.set_options(timeout=60000)
        f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1200})
        workspace_zoom=f.page.locator('#workspace .workspace-zoom').first
        workspace_zoom.click();workspace_menu=f.page.locator('.workspace-zoom-menu:not(.bp-zoom-menu)')
        workspace_menu.locator('[data-zoom-preset="500"]').click();expect(workspace_zoom).to_have_text('500%')
        workspace_menu.locator('[data-zoom-value]').press('Escape');flush();original()
        f.page.close();f.stop();f.start(1);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1200})
        workspace_zoom=f.page.locator('#workspace .workspace-zoom').first;expect(workspace_zoom).to_have_text('500%')
        workspace_zoom.click();workspace_menu=f.page.locator('.workspace-zoom-menu:not(.bp-zoom-menu)');workspace_menu.locator('[data-zoom-preset="100"]').click();workspace_menu.locator('[data-zoom-value]').press('Escape')
        f.checked('Workspace의 원본 프리셋·개인 저장·엔진 재시작도 500%를 복원하며 원본 파일을 보존한다')
        f.page.locator('#workspace').click(button='right',position={'x':700,'y':300});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click()
        browser=f.page.locator('.window[data-key^="browser:project:"]');browser.get_by_role('button',name='기능',exact=True).click();browser.locator('[data-browser-control="object-query"]').fill('Slot');browser.locator('[data-browser-control="object-search"]').click()
        row=browser.locator('[data-object="'+f.n+'Slot"]');expect(row).to_have_attribute('aria-disabled','false');row.press('Enter');browser.locator('[data-close]').first.click();f.idle()
        f.page.locator('[data-operation=feature-author-open]').first.click()
        expect(f.author().locator('.bp-viewport')).to_be_visible()
        f.traffic.clear()
        zoom_to(500);guarded();f.checked('기존 원본 배율 팝오버의 400/500% 선택은 실제 Blueprint에 적용하며 source·CAS·Confirm을 호출하지 않는다')
        dialog=popup();control=dialog.locator('[data-zoom-value]');control.fill('900');control.press('Enter');expect(f.author().locator('[data-bp-percent]')).to_have_text('500%');control.fill('200');control.press('Escape');expect(f.author().locator('[data-bp-percent]')).to_have_text('500%');guarded();f.checked('상한을 넘는 직접 입력은 500%로 제한하고 Escape는 미적용 배율 입력만 취소한다')
        node=f.author().locator('[data-bp-node=body] [data-inline-description]');held='저장하지 않은 확대 검사 입력 9223372036854775807';node.fill(held)
        zoom_to(400);zoom_to(500);expect(node).to_have_value(held);guarded()
        viewport=f.author().locator('.bp-viewport');box=viewport.bounding_box();x=box['x']+box['width']/2;y=box['y']+box['height']/2
        f.page.mouse.move(x,y);f.page.keyboard.down('Control');f.page.mouse.wheel(0,-1000);f.page.keyboard.up('Control');expect(f.author().locator('[data-bp-percent]')).to_have_text('500%');expect(node).to_have_value(held);guarded();f.checked('최대 확대의 Ctrl+wheel과 반복 배율 변경은 기존 미저장 본문 설명·정확한 원문을 보존한다')
        f.page.mouse.wheel(0,100);expect(f.author().locator('[data-bp-percent]')).to_have_text('475%');assert f.author().locator('.bp-plane').evaluate('el=>new DOMMatrix(getComputedStyle(el).transform).a')==4.75
        f.page.keyboard.down('Control');f.page.mouse.wheel(0,-100);f.page.keyboard.up('Control');expect(f.author().locator('[data-bp-percent]')).to_have_text('500%');expect(node).to_have_value(held);guarded();f.checked('일반 휠과 Ctrl 휠은 원본의 500→475→500% 단계를 실제 plane에 적용하고 source 쓰기를 하지 않는다')
        dialog=popup();dialog.screenshot(path=str(f.case/'zoom-popup.png'));dialog.locator('[data-zoom-value]').press('Escape')
        zoom_to(400);f.page.set_viewport_size({'width':430,'height':900})
        flow=f.author().locator('[aria-label="카드 흐름 편집"]');expect(flow).to_be_visible();flow.locator('[data-flow-graph]').click()
        viewport=f.author().locator('.bp-viewport');expect(viewport).to_be_visible()
        (f.case/'mobile-before-touch.json').write_text(json.dumps(viewport.evaluate('el=>({rect:el.getBoundingClientRect().toJSON(),rootClass:el.closest(".blueprint-editor").className,bodyClass:document.body.className})'),ensure_ascii=False,indent=2)+'\n')
        point=viewport.evaluate('''el=>{const r=el.getBoundingClientRect();for(let y=Math.max(8,r.top+12);y<Math.min(innerHeight-8,r.bottom-8);y+=12)for(let x=Math.max(28,r.left+28);x<Math.min(innerWidth-28,r.right-28);x+=12){const eligible=p=>{const target=document.elementFromPoint(p,y);return target&&el.contains(target)&&!target.closest('input,textarea,select,[contenteditable=true]');};if(eligible(x-20)&&eligible(x+20))return {x,y};}throw Error('No eligible two-touch viewport position');}''');cx=point['x'];cy=point['y'];cdp=f.page.context.new_cdp_session(f.page)
        cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'id':1,'x':cx-20,'y':cy},{'id':2,'x':cx+20,'y':cy}]})
        cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'id':1,'x':cx-55,'y':cy},{'id':2,'x':cx+55,'y':cy}]})
        cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});cdp.detach()
        expect(f.author().locator('[data-bp-percent]')).to_have_text('500%');guarded();f.checked('모바일 폭의 두 접점 확대도 동일한 500% 상한과 입력·소유 경계를 유지한다')
        f.page.set_viewport_size({'width':1800,'height':1200});flush();f.page.screenshot(path=str(f.case/'zoom-before-cold.png'))
        f.page.close();f.stop();f.start(2);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1200})
        expect(f.author().locator('[data-bp-percent]')).to_have_text('500%');expect(f.author().locator('[data-bp-node=body] [data-inline-description]')).to_have_value(held);guarded();f.checked('엔진 재시작은 500% 개인 화면과 같은 문서의 미저장 입력을 복원하며 초안/원본을 저장하지 않는다')
        dialog=popup();button=dialog.locator('[data-zoom-preset="400"]');f.author().locator('[data-close]').first.click();expect(dialog).to_have_count(0);assert not f.errors and not f.external,(f.errors,f.external);guarded();f.checked('창 종료는 배율 팝오버와 콜백을 폐기하며 다른 창이나 문서에 적용하지 않는다')
        f.page.screenshot(path=str(f.case/'zoom-closed.png'));f.browser.close()
except Exception:
    try:f.page.screenshot(path=str(f.case/'zoom-failure.png'))
    except Exception:pass
    raise
finally:
    f.stop();(f.case/'zoom-evidence.json').write_text(json.dumps({'checks':f.checks,'errors':f.errors,'actualEngine':True,'actualWindows':False,'actualMobile':False,'fixture':str(f.case)},ensure_ascii=False,indent=2)+'\n')
print('EVIDENCE',f.case,flush=True)
