"""원본 컨텍스트 메뉴에서 명시적으로 async 전환하고 checkpoint/Review로 확정한다."""
import copy,json,sys
from playwright.sync_api import sync_playwright,expect
import v666_async_function_fixture as x
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
 f.start(0);f.invoke('select',{'id':x.feature});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();identity=x.read()['asyncTransition']['rootCompletion']['id']
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph();toggle();branch=panel().locator('[data-root-branch="'+identity+'"] [data-root-branch-name]');expect(branch).to_have_value('완료 시');assert pending();panel().locator('.bp-viewport').press('Control+z');expect(branch).to_have_count(0);assert not pending();panel().locator('.bp-viewport').press('Control+y');expect(branch).to_have_value('완료 시');x.original();assert checkpoint.read_bytes()==before;f.checked('원본 기능 heading의 동기 복귀는 같은 완료 ID의 일반 공개 분기를 미리 보고 Undo/Redo한다')
  held=copy.deepcopy(pending());restart(1);assert pending()==held;branch=panel().locator('[data-root-branch="'+identity+'"] [data-root-branch-name]');expect(branch).to_have_value('완료 시');x.original();f.checked('기능 전환 미리보기와 완료 정체성을 cold에서 복원한다')
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:panel().locator('[data-bp-save]').click();f.idle();assert retained(held) and checkpoint.read_bytes()==before;x.original()
   finally:checkpoint.chmod(0o600)
   restart(2);f.checked('저장 실패는 공개 전환·기존 호출자·작성 입력을 함께 보존한다')
  if mode=='conflict':
   path=f.project/'PublicDone.node.json';path.write_bytes(x.physical[path]+b' ')
   try:panel().locator('[data-bp-save]').click();f.idle();assert retained(held) and checkpoint.read_bytes()==before
   finally:path.write_bytes(x.physical[path])
   x.original();f.checked('호출자의 완료 원문 경합은 전체 전환을 원자 거절한다')
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
      if r['requestId']in requests|queries:rid=r['requestId'];lost.append(rid);r.clear();r.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',interrupt);panel().locator('[data-bp-save]').click()
   for _ in range(1000):
    if paused or requests and any(r in queries for r in lost):break
    f.page.wait_for_timeout(30)
   assert len(requests)==1
   if mode=='late':
    assert paused;toggle();paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',interrupt);f.idle();assert pending();restart(3);mark=len(f.traffic);panel().locator('[data-bp-save]').click();f.idle();assert pending();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch'for r in f.traffic[mark:]);save();assert x.read()['asyncTransition']['enabled'];toggle();save();f.checked('늦은 전체 함수 재전환은 cold 후 기존 결과부터 조회하고 같은 완료를 별도 저장한다')
   else:
    assert any(r in queries for r in lost)and pending();f.page.unroute_all(behavior='wait');restart(3);mark=len(f.traffic);save();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch'for r in f.traffic[mark:]);f.checked('응답 유실 재시작은 공개 분기와 호출자 갱신을 중복 저장하지 않는다')
  else:save()
  m=x.check_demoted();assert m['id']==identity;assert not pending();x.original();f.checked('Save는 함수 완료와 호출자의 literal 연결·기존 IO/지역 Result·C#을 함께 보존한다')
  r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();x.original();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();x.code_unchanged();x.build('ui-public-demoted',10,'callee:1\nafter:10');f.checked('Review 취소/Confirm은 원문을 보존하고 일반 완료를 자동 실행하지 않는다')
  restart(4);assert x.check_demoted()['id']==identity;x.code_unchanged();f.checked('최종 cold 복원에서도 공개 완료 ID/값과 호출자의 기존 목적지가 같다')
  if mode=='normal':
   field=panel().locator('[data-root-branch="'+identity+'"] [data-root-branch-name]');field.fill('공개 완료');field.press('Tab');panel().locator('[data-bp-percent]').click();z=f.page.get_by_role('dialog',name='노드 화면 배율',exact=True);z.get_by_role('button',name='전체 보기',exact=True).click();z.locator('[data-zoom-value]').press('Escape');panel().locator('[data-bp-node="$exit:yes"] [data-bp-branch-select]').click();f.page.locator('[data-branch-option="'+identity+'"]').click();panel().locator('[data-root-caller]').select_option(x.caller);save();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();x.code_unchanged();x.build('ui-public-selected',10,'callee:1\npublic:10\nafter:10');assert x.marker()['name']=='공개 완료';f.checked('기존 반환 카드·명시 호출자 배정·분기 이름 UI가 같은 일반 완료 줄을 실행한다')
  assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'public-completion-final.png'),full_page=True);f.browser.close()
except Exception:
 (f.case/'failure-details.json').write_text(json.dumps({'errors':f.errors,'checks':f.checks},ensure_ascii=False,indent=2));raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2));f.stop()
print('PUBLIC_COMPLETION_FIXTURE '+str(f.case),flush=True)
