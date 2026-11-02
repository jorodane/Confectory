"""A public branch definition needs no fabricated Blueprint caller."""
import json
from playwright.sync_api import sync_playwright,expect
import v666_root_execution_multi_fixture as x
f=x.f
def panel():return f.author()
def open_graph():
 f.idle();f.page.locator('#workspace').click(button='right',position={'x':1300,'y':300});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.get_by_role('button',name='기능',exact=True).click();b.locator('[data-browser-control=object-query]').fill('Flow');b.locator('[data-browser-control=object-search]').click();b.locator('[data-object="'+x.feature+'"]').press('Enter');b.locator('[data-close]').first.click();f.idle();f.page.locator('[data-operation=feature-author-open]').first.click();expect(panel().locator('[data-bp-node=choose]')).to_be_visible()
def restart(i):
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle();expect(panel()).to_be_visible()
try:
 f.start(0);f.invoke('select',{'id':x.feature});f.invoke('saveDraft',{})
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph();expect(panel().locator('[data-root-callers] option')).to_have_count(0)
  for _ in range(2):panel().locator('[data-root-branch-add]').click()
  plan=json.loads(next(v['text'] for _,v in f.pending()['blueprint'] if v['type']=='root-execution'));ids=[b['id'] for b in plan['branches']]
  for id,name in zip(ids,['성공','실패']):field=panel().locator('[data-root-branch="'+id+'"] [data-root-branch-name]');field.fill(name);field.press('Tab')
  panel().locator('[data-bp-percent]').click();zoom=f.page.get_by_role('dialog',name='노드 화면 배율',exact=True);zoom.locator('[data-zoom-preset="25"]').click();zoom.locator('[data-zoom-value]').press('Escape')
  for name,id in zip(['yes','no'],ids):panel().locator('[data-bp-node="$exit:'+name+'"] [data-bp-branch-select]').click();f.page.locator('[data-branch-option="'+id+'"]').click()
  held=f.pending()['blueprint'];restart(1);assert f.pending()['blueprint']==held;x.original();panel().locator('[data-bp-save]').click();expect(panel().locator('.bp-status')).to_have_text('저장됨',timeout=90000);f.idle();x.original();f.checked('연결된 Blueprint 호출자가 없어도 직접 지정한 분기·반환을 저장하고 cold 입력을 복구한다')
  for cancel in [True,False]:
   panel().locator('[data-bp-complete]').click();f.page.locator('.window[data-key=review]:visible,.window[data-key=targets]:visible').first.wait_for(state='visible',timeout=90000);t=f.page.locator('.window[data-key=targets]')
   if t.is_visible():t.locator('[data-target-choice]').select_option('portable');t.locator('[data-close]').click();panel().locator('[data-bp-complete]').click()
   r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=90000)
   if r.locator('[data-review-advanced]').is_visible():r.locator('[data-review-advanced]').click();r.locator('[data-advanced-reviewed]').check()
   r.locator('[data-reject]' if cancel else '#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle()
   if cancel:x.original()
  x.original_code();x.build('zero-ui-after');restart(2);assert x.read()['diagnostics']['state']=='source-ready';x.original_code();f.checked('Review 취소/Confirm·원문 보존·기존 C# IInvoke 실행과 확정 후 cold 복원을 확인한다');assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'zero-final.png'));f.browser.close()
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
print('M12_ZERO_FIXTURE '+str(f.case),flush=True)
