"""Connected completion survives explicit sync return and native/out selection."""
import copy,json,sys
from playwright.sync_api import sync_playwright,expect
import v666_async_private_returns_fixture as x
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
 f.start(0);f.invoke('select',{'id':x.feature});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph();panel().locator('[data-bp-node=task] [data-internal-flow]').click();expect(panel().locator('[data-bp-node=body]')).to_be_visible();toggle();held=copy.deepcopy(pending());assert held;panel().locator('.bp-viewport').press('Control+z');assert not pending();panel().locator('.bp-viewport').press('Control+y');assert pending();x.original();assert checkpoint.read_bytes()==before;restart(1);assert retained(held);f.checked('완료 실행선이 연결된 내부 Root의 동기 전환·Undo/Redo·cold는 원문과 native/out 계약을 보존한다')
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:panel().locator('[data-bp-save]').click();f.idle();assert retained(held)and checkpoint.read_bytes()==before;x.original()
   finally:checkpoint.chmod(0o600)
   restart(2);f.checked('동기 복귀 저장 권한 실패는 전체 입력과 원본을 보존한다')
  if mode=='conflict':
   p=f.project/'Flow.node.json';old=p.read_bytes();p.write_bytes(old+b' ')
   try:panel().locator('[data-bp-save]').click();f.idle();assert retained(held)and checkpoint.read_bytes()==before
   finally:p.write_bytes(old)
   x.original();f.checked('동기 복귀 원문 충돌은 전체 후보를 거절하고 완료 연결/입력을 보존한다')
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
    assert paused;toggle();paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',interrupt);f.idle();assert pending();restart(3);mark=len(f.traffic);panel().locator('[data-bp-save]').click();f.idle();assert pending();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch'for r in f.traffic[mark:]);save();assert x.read()['asyncTransition']['enabled'];toggle();save();f.checked('늦은 재전환 입력은 cold 뒤 이전 결과 조회와 별도 Save로 보존한다')
   else:
    assert any(r in queries for r in lost)and pending();f.page.unroute_all(behavior='wait');restart(3);mark=len(f.traffic);save();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch'for r in f.traffic[mark:]);f.checked('동기 복귀 응답 유실 뒤 cold 조회는 같은 전환을 중복 저장하지 않는다')
  else:save()
  m=x.marker();assert not x.read()['asyncTransition']['enabled'];assert x.read(x.graph)['edges']==x.original_edges;x.original();save();f.page.screenshot(path=str(f.case/'saved-sync.png'));(f.case/'saved-sync.html').write_text(f.page.content());end=panel().locator('[data-bp-node="$exit:done"]');assert end.count(),panel().locator('[data-bp-node]').evaluate_all('(rows)=>rows.map(r=>r.dataset.bpNode)');panel().locator('[data-bp-percent]').click();zoom=f.page.get_by_role('dialog',name='노드 화면 배율',exact=True);zoom.locator('[data-bp-fit]').click();zoom.locator('[data-zoom-value]').press('Escape');expect(end).to_be_visible();end.locator('[data-bp-branch-select]').click();f.page.locator('[data-branch-option="'+m['id']+'"]').click();save();choice=json.loads(next(e['valueJson']for e in x.read()['exits']if e['name']=='done'));assert choice==dict(executionBranch=m['id'],value=x.original_value);x.original();f.checked('기존 반환 노드에서 일반 완료 결과를 선택해도 native 값과 out 연결을 보존한다')
  r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();x.original();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();x.unchanged();x.build('ui-completed',True);restart(4);assert not x.read()['asyncTransition']['enabled']and x.marker()==m;x.unchanged();assert x.read(x.graph)['edges']==x.original_edges;f.checked('Review 취소/Confirm·실제 일반 완료 실행·확정 cold는 같은 분기 ID/연결/원문과 native/out 값을 보존한다');assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'private-returns-final.png'),full_page=True);f.browser.close()
except Exception:
 try:f.page.screenshot(path=str(f.case/'private-returns-failure.png'),timeout=5000);(f.case/'failure.html').write_text(f.page.content())
 except Exception:pass
 raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
print('ASYNC_PRIVATE_RETURNS_FIXTURE',f.case,flush=True)
