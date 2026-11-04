"""Owned private Task menus, exact checkpoint and interrupted Save lifecycle."""
import copy,json,sys
from playwright.sync_api import sync_playwright,expect
import v666_async_private_fixture as x
f=x.f;mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
def panel():return f.author()
def pending():return f.pending()['blueprint']
def retained(held):return all(dict(pending()).get(key)==value for key,value in held)
def open_graph(feature=x.feature,node='task'):
 f.idle()
 if panel().is_visible() and panel().locator('[data-bp-node="'+node+'"]').count():return
 f.page.locator('#workspace').click(button='right',position={'x':1300,'y':300});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.get_by_role('button',name='기능',exact=True).click();b.locator('[data-browser-control=object-query]').fill(feature.split('::')[-1]);b.locator('[data-browser-control=object-search]').click();b.locator('[data-object="'+feature+'"]').press('Enter');b.locator('[data-close]').first.click();f.idle();f.page.locator('[data-operation=feature-author-open]').first.click();expect(panel().locator('[data-bp-node="'+node+'"]')).to_be_visible()
def toggle(node=None):
 target=panel().locator('[data-bp-node="'+node+'"] .function-node-heading') if node else panel().locator('.bp-identity')
 target.click(button='right');f.page.screenshot(path=str(f.case/('menu-'+(node or 'root')+'.png')));(f.case/'menu.html').write_text(f.page.content());f.page.locator('[data-bp-async="'+(node or '$root')+'"]').click()
def save():
 panel().locator('[data-bp-save]').click();expect(panel().locator('.bp-status')).to_have_text('저장됨',timeout=90000);f.idle()
def restart(i):
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle();expect(panel()).to_be_visible()
def review():
 panel().locator('[data-bp-complete]').click();f.page.locator('.window[data-key=review]:visible,.window[data-key=targets]:visible').first.wait_for(state='visible',timeout=90000);t=f.page.locator('.window[data-key=targets]')
 if t.is_visible():t.locator('[data-target-choice]').select_option('portable');t.locator('[data-close]').click();panel().locator('[data-bp-complete]').click()
 r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=90000);a=r.locator('[data-review-advanced]')
 if a.is_visible():a.click();r.locator('[data-advanced-reviewed]').check()
 return r

try:
 f.start(0);f.invoke('select',{'id':x.feature});f.invoke('saveDraft',{})
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph();toggle('task');assert pending();panel().locator('.bp-viewport').press('Control+z');assert not pending();panel().locator('.bp-viewport').press('Control+y');assert pending();x.original();save();assert x.read()['asyncTransition']['enabled'];panel().locator('[data-bp-node=task] [data-internal-flow]').click();expect(panel().locator('[data-bp-node=body]')).to_be_visible();toggle('body');held=copy.deepcopy(pending());assert held;x.original();checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();restart(1);assert retained(held);f.checked('내부 Task 메뉴·Undo/Redo·leaf 전환과 cold 복원은 공개 계약과 C# 원문을 보존한다')
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:panel().locator('[data-bp-save]').click();f.idle();assert retained(held)and checkpoint.read_bytes()==before;x.original()
   finally:checkpoint.chmod(0o600)
   restart(2);f.checked('private Task 저장 권한 실패는 모든 입력과 원본을 보존한다')
  if mode=='conflict':
   p=f.project/'Flow.node.json';old=p.read_bytes();p.write_bytes(old+b' ')
   try:panel().locator('[data-bp-save]').click();f.idle();assert retained(held)and checkpoint.read_bytes()==before
   finally:p.write_bytes(old)
   x.original();f.checked('private 원문 충돌은 전체 후보 저장을 거절하고 입력을 보존한다')
  if mode in ['loss','late']:
   requests=set();queries=set();paused={};lost=[]
   def interrupt(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke'and body.get('endpoint')=='blueprint':
     action=body.get('input',{}).get('action')
     if action=='authorBatch':requests.add(body['requestId'])
     elif requests and action=='settledAuthorBatch':queries.add(body['requestId'])
    response=route.fetch();payload=response.json()
    if mode=='late'and not paused and any(r.get('ok')and r.get('requestId')in requests for r in payload.get('results',[])):paused.update(route=route,response=response);return
    if mode=='loss':
     for r in payload.get('results',[]):
      if r['requestId']in requests|queries:rid=r['requestId'];lost.append(rid);r.clear();r.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',interrupt);panel().locator('[data-bp-save]').click()
   for _ in range(1000):
    if paused or requests and any(r in queries for r in lost):break
    f.page.wait_for_timeout(30)
   assert len(requests)==1
   if mode=='late':
    assert paused;toggle('body');paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',interrupt);f.idle();assert pending();restart(3);mark=len(f.traffic);panel().locator('[data-bp-save]').click();f.idle();assert pending();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch'for r in f.traffic[mark:]);save();assert not x.read()['asyncTransition']['nodes'][0]['enabled'];toggle('body');save();f.checked('private 늦은 입력은 cold 뒤 이전 receipt 조회와 별도 명시 Save로 보존된다')
   else:
    assert any(r in queries for r in lost)and pending();f.page.unroute_all(behavior='wait');restart(3);mark=len(f.traffic);save();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch'for r in f.traffic[mark:]);f.checked('private 응답 유실 뒤 cold 복원은 같은 후보를 중복 저장하지 않는다')
  else:save()
  assert not pending();save();x.original();assert x.read()['asyncTransition']['nodes'][0]['enabled'];panel().locator('[data-bp-node=body] [data-internal-code]').click();dialog=f.page.locator('.bp-script-dialog');expect(dialog).to_be_visible();assert'Task'in dialog.locator('[data-code-source]').input_value();dialog.locator('[data-code-cancel]').click();assert not pending();f.checked('private 반복 Save와 Task 코드 편집 취소는 원문과 새 상태를 보존한다')
  r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();x.original();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();x.unchanged();x.build('ui-confirmed');restart(4);assert x.read()['diagnostics']['state']=='source-ready';x.unchanged();f.checked('private Review 취소/Confirm·실제 await 실행·확정 cold는 공개 계약/원문/연결을 보존한다');assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'private-final.png'),full_page=True);f.browser.close()
except Exception:
 try:f.page.screenshot(path=str(f.case/'private-failure.png'),timeout=5000);(f.case/'failure.html').write_text(f.page.content())
 except Exception:pass
 raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
print('ASYNC_PRIVATE_FIXTURE',f.case,flush=True)
