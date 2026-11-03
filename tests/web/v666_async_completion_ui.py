"""원본 컨텍스트 메뉴에서 명시적으로 async 전환하고 checkpoint/Review로 확정한다."""
import copy,json,sys
from playwright.sync_api import sync_playwright,expect
import v666_async_completion_fixture as x
f=x.f;mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
def panel():return f.author()
def pending():return f.pending()['blueprint']
def retained(held):return all(dict(pending()).get(key)==value for key,value in held)
def open_graph(feature=x.feature,node='choose'):
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
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph();toggle('choose');label=panel().locator('[data-bp-node=choose] [data-branch-name]').first;expect(label).to_have_value('완료 시');expect(panel().locator('[data-bp-node=choose] .function-node-heading .function-async-clock')).to_have_count(0);expect(panel().locator('[data-bp-node=choose] [data-port=completion]')).to_be_visible();assert pending();panel().locator('.bp-viewport').press('Control+z');expect(panel().locator('[data-bp-node=choose] .function-node-heading .function-async-clock')).to_be_visible();assert not pending();panel().locator('.bp-viewport').press('Control+y');expect(panel().locator('[data-bp-node=choose] [data-branch-name]').first).to_have_value('완료 시');x.original();assert checkpoint.read_bytes()==before;f.checked('완료 줄 위치/표시명과 포트는 유지하고 동기 복귀 Undo/Redo는 private 입력만 바꾼다')
  held=copy.deepcopy(pending());restart(1);assert pending()==held;x.original();f.checked('연결된 완료의 일반 분기 미리보기와 입력을 cold에서 복원한다')
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:panel().locator('[data-bp-save]').click();f.idle();assert retained(held) and checkpoint.read_bytes()==before;x.original()
   finally:checkpoint.chmod(0o600)
   restart(2);f.checked('저장 실패는 기존 async 원본/완료 연결과 동기 복귀 입력을 보존한다')
  if mode=='conflict':
   path=f.project/'After.node.json';path.write_bytes(x.physical[path]+b' ')
   try:panel().locator('[data-bp-save]').click();f.idle();assert retained(held) and checkpoint.read_bytes()==before
   finally:path.write_bytes(x.physical[path])
   x.original();f.checked('다른 호출자의 실제 원문 경합은 전체 후보/입력을 보존한다')
  if mode in ['loss','late']:
   requests=set();queries=set();paused={};lost=[]
   def interrupt(route):
    data=route.request.post_data_json
    if data.get('op')=='invoke' and data.get('endpoint')=='blueprint':
     action=data.get('input',{}).get('action')
     if action=='authorBatch':requests.add(data['requestId'])
     elif requests and action=='settledAuthorBatch':queries.add(data['requestId'])
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
    assert paused;toggle('choose');paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',interrupt);f.idle();assert pending();restart(3);mark=len(f.traffic);panel().locator('[data-bp-save]').click();f.idle();assert pending();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for r in f.traffic[mark:]);save();assert next(n for n in x.read()['nodes']if n['id']=='choose')['async'];toggle('choose');save();f.checked('늦은 async 재전환은 cold 뒤 이전 결과를 먼저 조회하고 별도 Save 뒤 같은 완료로 복귀한다')
   else:
    assert any(r in queries for r in lost) and pending();f.page.unroute_all(behavior='wait');restart(3);mark=len(f.traffic);save();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for r in f.traffic[mark:]);f.checked('응답 유실 뒤 cold 재조회는 완료 분기를 중복 발급하거나 저장하지 않는다')
  else:save()
  assert not pending();marker=x.check_demoted();assert marker['label']=='완료 시';x.original();f.checked('Save는 원래 completion 연결과 C#을 유지하며 같은 ID의 일반 Result 후보를 저장한다')
  panel().locator('[data-bp-node=choose] [data-branch-remove="'+marker['id']+'"]').click();f.idle();assert not pending();x.original();f.checked('연결된 일반 완료 분기 삭제는 입력/연결을 폐기하지 않고 거절한다')
  if mode=='normal':
   field=panel().locator('[data-bp-node=choose] [data-branch-name="'+marker['id']+'"]');field.fill('완료 경로');field.press('Tab');save();renamed=x.check_demoted();assert renamed['id']==marker['id'] and renamed['value']==marker['value'] and renamed['label']=='완료 경로';f.checked('완료 표시명과 유효한 C# 이름은 분리하고 기존 ID/정수값은 유지한다')
  r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();x.original();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();x.run('ui-demoted');x.run('ui-explicit-completion',True);f.checked('Review 취소/Confirm 뒤 기존 원문은 완료를 자동 실행하지 않고 명시 Result 선택만 완료 줄을 실행한다');restart(4);assert x.read()['diagnostics']['state']=='source-ready';assert x.check_demoted()['id']==marker['id'];x.code_unchanged();f.checked('최종 재시작에서도 완료 ID/값/연결과 원래 C#·out를 복원한다');assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'completion-final.png'),full_page=True);f.browser.close()
except Exception:
 (f.case/'failure-details.json').write_text(json.dumps({'errors':f.errors,'checks':f.checks},ensure_ascii=False,indent=2))
 raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2));f.stop()
print('ASYNC_COMPLETION_FIXTURE '+str(f.case),flush=True)
