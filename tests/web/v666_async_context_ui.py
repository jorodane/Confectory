"""원본 컨텍스트 메뉴에서 명시적으로 async 전환하고 checkpoint/Review로 확정한다."""
import copy,json,sys
from playwright.sync_api import sync_playwright,expect
import v666_async_context_fixture as x
f=x.f;mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
def panel():return f.author()
def pending():return f.pending()['blueprint']
def retained(held):return all(dict(pending()).get(key)==value for key,value in held)
def open_graph(feature=x.feature,node='body'):
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
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph();toggle();assert pending();panel().locator('.bp-viewport').press('Control+z');assert not pending();panel().locator('.bp-viewport').press('Control+y');assert pending();x.original();assert checkpoint.read_bytes()==before;f.checked('원본 함수 전환 메뉴의 Undo/Redo는 원본과 checkpoint를 바꾸지 않는다')
  panel().locator('[data-bp-node=body] .function-node-heading').click(button='right');expect(f.page.locator('[data-bp-async=body]')).to_be_disabled();f.page.keyboard.press('Escape');held=copy.deepcopy(pending());restart(1);assert pending()==held;x.original();f.checked('원래 native Invoke의 별도 async 버튼은 보호하고 함수 전환 입력을 cold에서 복원한다')
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:
    panel().locator('[data-bp-save]').click();f.idle();actual=pending();(f.case/'storage-proof.json').write_text(json.dumps(dict(held=held,actual=actual,checkpointSame=checkpoint.read_bytes()==before,status=panel().locator('.bp-status').inner_text()),ensure_ascii=False,indent=2));assert retained(held) and checkpoint.read_bytes()==before;x.original()
   finally:checkpoint.chmod(0o600)
   restart(2);f.checked('저장 권한 실패는 모든 입력과 원본을 보존한다')
  if mode=='conflict':
   p=f.project/'After.node.json';p.write_bytes(x.physical[p]+b' ')
   try:panel().locator('[data-bp-save]').click();f.idle();assert retained(held) and checkpoint.read_bytes()==before
   finally:p.write_bytes(x.physical[p])
   x.original();f.checked('다른 호출자 원문 충돌에서 전체 후보와 입력을 보존한다')
  if mode in ['loss','late']:
   requests=set();queries=set();paused={};lost=[]
   def interrupt(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
     action=body.get('input',{}).get('action')
     if action=='authorBatch':requests.add(body['requestId'])
     elif requests and action=='settledAuthorBatch':queries.add(body['requestId'])
    response=route.fetch();payload=response.json()
    if mode=='late' and not paused and any(r.get('ok') and r.get('requestId') in requests for r in payload.get('results',[])):paused.update(route=route,response=response);return
    if mode=='loss':
     for r in payload.get('results',[]):
      if r['requestId'] in requests|queries:rid=r['requestId'];lost.append(rid);r.clear();r.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',interrupt);panel().locator('[data-bp-save]').click()
   for _ in range(1000):
    if paused or requests and any(r in queries for r in lost):break
    f.page.wait_for_timeout(30)
   assert len(requests)==1
   if mode=='late':
    assert paused;toggle();paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',interrupt);f.idle();assert pending();restart(3);mark=len(f.traffic);panel().locator('[data-bp-save]').click();f.idle();assert pending();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch'for r in f.traffic[mark:]);(f.case/'late-input-after-query.json').write_text(json.dumps(pending(),ensure_ascii=False,indent=2));save();applied=[r['invoke']['input']for r in f.traffic[mark:]if r.get('invoke',{}).get('input',{}).get('action')=='authorBatch'];assert len(applied)==1 and applied[0]['edits'][0]['definition']['enabled'] is False;assert not x.read()['asyncTransition']['enabled'];toggle();save();f.checked('늦은 명시 전환은 cold 뒤 이전 receipt만 조회하고 새 입력은 별도 Save로 보존한다')
   else:
    assert any(r in queries for r in lost) and pending();f.page.unroute_all(behavior='wait');restart(3);mark=len(f.traffic);save();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for r in f.traffic[mark:]);f.checked('응답 유실 뒤 cold 재조회는 동일 async 전환을 중복 저장하지 않는다')
  else:save()
  assert not pending();x.original();assert 'GRAPH_ASYNC_CALLER_REQUIRED' in json.dumps(x.read(x.caller)['diagnostics']);f.checked('첫 명시 Save는 원본을 유지하고 동기 호출자를 실제 오류로 표시한다')
  if mode=='normal':
   panel().locator('[data-bp-node=body] [data-internal-code]').click();dialog=f.page.locator('.bp-script-dialog');expect(dialog).to_be_visible();shown=dialog.locator('[data-code-source]').input_value();assert 'Invoke(object marker, long input, out long copied)' in shown and 'this.Invoke' in shown and 'IImports same=this.calls' in shown;dialog.locator('[data-code-cancel]').click();assert not pending();x.original();f.checked('원래 Invoke 서명·this·scoped import를 그대로 표시하고 편집 취소는 원문을 보존한다')
  open_graph(f.n+'Main','invoke');toggle();save();assert not pending();x.original();r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();x.original();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();x.build('async-ui')
  x.unchanged();assert x.read()['edges']==x.initial_edges
  f.checked('명시 호출자 전환과 Review 취소/Confirm을 거쳐 원래 C#·출력을 실제 Task로 실행한다');restart(4);assert x.read()['diagnostics']['state']=='source-ready' and x.read(x.caller)['diagnostics']['state']=='source-ready';f.checked('최종 확정 후 재시작에서 함수와 호출자의 비동기 상태를 복원한다');assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'async-final.png'),full_page=True);f.browser.close()
except Exception:
 (f.case/'failure-details.json').write_text(json.dumps({'errors':f.errors,'checks':f.checks},ensure_ascii=False,indent=2))
 try:f.page.screenshot(path=str(f.case/'async-failure.png'),timeout=5000);(f.case/'failure.html').write_text(f.page.content())
 except Exception:pass
 raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2));f.stop()
print('ASYNC_CONTEXT_FIXTURE '+str(f.case),flush=True)
