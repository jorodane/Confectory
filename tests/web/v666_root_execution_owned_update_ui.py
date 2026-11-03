"""Authored all-target copy/child return updates with durable private input."""
import copy,json,sys
from playwright.sync_api import sync_playwright,expect
import v666_root_execution_owned_update_fixture as o
x=o.x;c=o.c;f=o.f;mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
def panel():return f.author()
def pending():return f.pending()['blueprint']
def open_graph(feature):
 f.idle();f.page.locator('#workspace').click(button='right',position={'x':1300,'y':300});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.get_by_role('button',name='기능',exact=True).click();b.locator('[data-browser-control=object-query]').fill(feature.split('::')[-1]);b.locator('[data-browser-control=object-search]').click();b.locator('[data-object="'+feature+'"]').press('Enter');b.locator('[data-close]').first.click();f.idle();f.page.locator('[data-operation=feature-author-open]').first.click();expect(panel().locator('[data-bp-node]')).not_to_have_count(0)
def restart(i):
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle();expect(panel()).to_be_visible()
def save():panel().locator('[data-bp-save]').click();expect(panel().locator('.bp-status')).to_have_text('저장됨',timeout=90000);f.idle()
def review():
 panel().locator('[data-bp-complete]').click();f.page.locator('.window[data-key=review]:visible,.window[data-key=targets]:visible').first.wait_for(state='visible',timeout=90000);t=f.page.locator('.window[data-key=targets]')
 if t.is_visible():t.locator('[data-target-choice]').select_option('portable');t.locator('[data-close]').click();panel().locator('[data-bp-complete]').click()
 r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=90000)
 if r.locator('[data-review-advanced]').is_visible():r.locator('[data-review-advanced]').click();r.locator('[data-advanced-reviewed]').check()
 return r
def current_plan():return json.loads(next(v["text"] for _,v in pending() if v["type"]=="root-execution"))
try:
 f.start(0);f.invoke('select',{'id':x.feature});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph(x.feature);field=panel().locator('[data-root-branch=success] [data-root-branch-name]');field.fill('같은 계약 전체 갱신');field.press('Tab');p=current_plan();assert p['branches'][0]['id']=='success';panel().locator('.bp-viewport').press('Control+z');assert not pending();panel().locator('.bp-viewport').press('Control+y');assert current_plan()==p;o.original();assert checkpoint.read_bytes()==before
  panel().locator('[data-bp-save]').click();f.idle();assert pending() and checkpoint.read_bytes()==before;choices=o.read()['rootExecution'];assert len(choices['targets'])==4;panel().locator('[data-root-callers]').select_option([r['key'] for r in choices['callers']]);panel().locator('[data-bp-percent]').click();zoom=f.page.get_by_role('dialog',name='노드 화면 배율',exact=True);zoom.locator('[data-bp-fit]').click();zoom.locator('[data-zoom-value]').press('Escape');panel().locator('[data-bp-node="$exit:yes"] [data-bp-branch-select]').click();f.page.locator('[data-branch-option=failure]').click()
  for target in current_plan()['targets']:panel().locator('[data-root-target="'+target['graph']+'"][data-root-target-exit=yes]').select_option('failure')
  assert all(t['exits']['yes']['executionBranch']=='failure' for t in current_plan()['targets']);inputs=copy.deepcopy(pending());restart(1);assert pending()==inputs;o.original();f.checked('원래 루트 계약 UI에서 copy·자식 target의 반환과 모든 caller를 직접 지정하고 Undo/Redo·cold는 원문과 입력을 보존한다')
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:panel().locator('[data-bp-save]').click();f.idle();assert pending() and checkpoint.read_bytes()==before;o.original()
   finally:checkpoint.chmod(0o600)
   restart(2);f.checked('checkpoint 권한 실패는 전체 소유 그룹을 미적용하고 cold 입력을 보존한다')
  if mode=='conflict':
   path=f.project/'M12ChildInfo.celem';path.write_bytes(o.physical[path]+b' ')
   try:panel().locator('[data-bp-save]').click();f.idle();assert pending() and checkpoint.read_bytes()==before
   finally:path.write_bytes(o.physical[path])
   o.original();f.checked('owner/schema 관측의 Save 전 경합은 copy·자식 전체를 미적용하고 대응 입력을 보존한다')
  if mode in ['loss','late']:
   requests=set();queries=set();paused={};lost=[]
   def interrupt(route):
    q=route.request.post_data_json
    if q.get('op')=='invoke' and q.get('endpoint')=='blueprint':
     action=q.get('input',{}).get('action')
     if action=='authorBatch':requests.add(q['requestId'])
     elif requests and action=='settledAuthorBatch':queries.add(q['requestId'])
    response=route.fetch();data=response.json()
    if mode=='late' and not paused and any(r.get('ok') and r.get('requestId') in requests for r in data.get('results',[])):paused.update(route=route,response=response);return
    if mode=='loss':
     for r in data.get('results',[]):
      if r['requestId'] in requests|queries:key=r['requestId'];lost.append(key);r.clear();r.update(requestId=key,ok=False,error={'code':'transport-interrupted'})
    route.fulfill(response=response,json=data)
   f.page.route('**/api/request',interrupt);panel().locator('[data-bp-save]').click()
   for _ in range(1000):
    if paused or requests and any(key in queries for key in lost):break
    f.page.wait_for_timeout(30)
   assert len(requests)==1
   if mode=='late':
    assert paused;field=panel().locator('[data-root-branch=success] [data-root-branch-name]');field.fill('전체 갱신 늦은 입력');field.press('Tab');paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',interrupt);f.idle();restart(3);assert current_plan()['branches'][0]['name']=='전체 갱신 늦은 입력';mark=len(f.traffic);panel().locator('[data-bp-save]').click();f.idle();assert pending() and not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for r in f.traffic[mark:]);save();f.checked('늦은 분기명은 cold 뒤 기존 receipt만 먼저 확인하고 별도 명시 Save로 보존한다')
   else:
    assert any(key in queries for key in lost) and pending();f.page.unroute_all(behavior='wait');restart(3);mark=len(f.traffic);save();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for r in f.traffic[mark:]);f.checked('저장 응답 유실과 cold receipt 조회는 전체 copy/자식 후보를 중복 적용하지 않는다')
  else:save()
  assert not pending();o.original();assert o.read()['diagnostics']['state']=='source-ready';f.checked('Save는 공개 계약·모든 소유 target·상속/배정 관측을 하나의 checkpoint와 최종 CAS 그룹에 결합한다')
  r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();o.original();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();o.retained();assert json.loads((f.project/c.graph_path).read_text())['copySource']==c.provenance;o.build('ui-owned-update',True);f.checked('Review 취소/Confirm 뒤 원래 C#/IO·provenance·상속 소유자를 보존하고 out10→실패 분기→다음 동작을 실제 실행한다')
  restart(4);assert o.read()['diagnostics']['state']=='source-ready';o.retained();f.checked('확정 후 cold도 copy·직접 자식·inherited-only의 계약/ID/연결과 원본을 유지한다');f.page.screenshot(path=str(f.case/'owned-update-final.png'),full_page=True);assert not f.errors and not f.external,(f.errors,f.external);f.browser.close()
except Exception:
 try:(f.case/'failure-state.json').write_text(json.dumps(f.state(),ensure_ascii=False));f.page.screenshot(path=str(f.case/'owned-update-failure.png'),timeout=5000)
 except Exception:pass
 raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2));f.stop()
print('M12_OWNED_UPDATE_FIXTURE '+str(f.case),flush=True)
