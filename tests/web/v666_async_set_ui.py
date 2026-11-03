"""기존 Set 원자 계획을 async 소유 함수에서도 동일한 저장 의미로 편집한다."""
import copy,json,uuid
from playwright.sync_api import sync_playwright,expect
import v666_async_completion_fixture as x
f=x.f
plan={'locals':[{'id':'beforeValue','name':'저장한 입력','type':'int','initialJson':'0'}], 'nodes':[{'id':'store','local':'beforeValue','outputLocal':'beforeValue','type':'int','valueJson':'{"node":"choose","output":"result"}','branchOwner':'choose'}], 'routes':[{'node':'choose','port':'completion','to':'store'},{'node':'store','port':'next','to':'completed'}], 'bindings':[{'node':'completed','name':'value','valueJson':'{"node":"store","output":"stored"}'}]}
def command(data,definition):return dict(id=x.graph,attempt=uuid.uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=[dict(action='setPlan',node='$sets',definition=definition)])
def panel():return f.author()
def open_graph():
 f.idle()
 if panel().is_visible() and panel().locator('[data-bp-node=store]').count():return
 f.page.locator('#workspace').click(button='right',position={'x':1300,'y':300});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.get_by_role('button',name='기능',exact=True).click();b.locator('[data-browser-control=object-query]').fill(x.feature.split('::')[-1]);b.locator('[data-browser-control=object-search]').click();b.locator('[data-object="'+x.feature+'"]').press('Enter');b.locator('[data-close]').first.click();f.idle();f.page.locator('[data-operation=feature-author-open]').first.click();expect(panel().locator('[data-bp-node=store]')).to_be_visible();panel().locator('[data-bp-percent]').click();z=f.page.get_by_role('dialog',name='노드 화면 배율',exact=True);z.get_by_role('button',name='전체 보기',exact=True).click();z.locator('[data-zoom-value]').press('Escape')
def save():
 panel().locator('[data-bp-save]').click();expect(panel().locator('.bp-status')).to_have_text('저장됨',timeout=90000);f.idle()
try:
 f.start(0);data=x.read();assert data['profile']=='async-acyclic-switch-v1';x.rpc('authorBatch',**command(data,plan));data=x.read();assert data['profile']=='async-acyclic-switch-v1';x.original();f.checked('async에서 Set·출력 저장소·입력 binding·실행선을 한 checkpoint로 저장하고 원본은 보존한다')
 before=copy.deepcopy(data);bad={'locals':[{'id':'beforeValue','name':'실패한 이름','type':'int'}],'nodes':[{'id':'store','local':'beforeValue','outputLocal':'beforeValue','type':'long','valueJson':'{"constant":2}','branchOwner':'choose'}]};x.rpc('authorBatch',False,**command(data,bad));assert x.read()['checkpointHash']==data['checkpointHash'];x.original();f.checked('Set 타입 실패는 앞선 이름 변경까지 원자적으로 거절한다')
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph();f.page.screenshot(path=str(f.case/'async-set-open.png'));(f.case/'open.html').write_text(f.page.content());field=panel().locator('[data-bp-node=store] [data-signature-name]');expect(field).to_be_enabled();expect(field).to_have_value('저장한 입력');panel().locator('[data-bp-node=store] .bp-pin-plug[data-side=out] .bp-pin-value').click();name=panel().get_by_role('textbox',name='지역변수 이름',exact=True);name.fill('기다리기 전 저장값');name.press('Enter');panel().locator('.bp-viewport').press('Control+z');assert not any(v['type']=='set-plan'for _,v in f.pending()['blueprint']);assert any(v['type']=='set-name-draft' and v['text']=='기다리기 전 저장값'for _,v in f.pending()['blueprint']);panel().locator('.bp-viewport').press('Control+y');expect(field).to_have_value('기다리기 전 저장값');save();data=x.read();assert next(l for l in data['locals']if l['id']=='beforeValue')['name']=='기다리기 전 저장값';assert data['edges']==before['edges'];x.original();f.checked('기존 Set 출력 이름 UI와 Undo/Redo·Save가 async에서도 ID·타입·연결을 보존한다')
  f.page.close();f.stop();f.start(1);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph();expect(panel().locator('[data-bp-node=store] [data-signature-name]')).to_have_value('기다리기 전 저장값');x.original();f.checked('cold에서 Set 표시명과 async·completion 계약을 함께 복원한다')
  panel().locator('[data-bp-complete]').click();f.page.locator('.window[data-key=review]:visible,.window[data-key=targets]:visible').first.wait_for(state='visible',timeout=90000);t=f.page.locator('.window[data-key=targets]')
  if t.is_visible():t.locator('[data-target-choice]').select_option('portable');t.locator('[data-close]').click();panel().locator('[data-bp-complete]').click()
  r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=90000);a=r.locator('[data-review-advanced]')
  if a.is_visible():a.click();r.locator('[data-advanced-reviewed]').check()
  r.locator('#confirm').click();expect(r).to_be_hidden(timeout=90000);f.idle();x.code_unchanged();x.build('async-set-confirmed',10,'callee:1\ncompleted:10\nafter:10');f.checked('Confirm 후 실제 실행은 Set 출력→await 결과→완료→결과→다음 순서를 보존한다')
  assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'async-set-final.png'));f.browser.close()
 print(json.dumps({'checks':f.checks,'actualEngine':True,'actualWindows':False,'evidence':str(f.case)},ensure_ascii=False))
except Exception:
 (f.case/'failure-state.json').write_text(json.dumps(f.state(),ensure_ascii=False,indent=2));raise
finally:f.stop()
