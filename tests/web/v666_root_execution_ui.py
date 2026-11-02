"""M12 authored sidebar, return cards and explicit caller; interrupted UI saves."""
import copy,json,sys
from playwright.sync_api import sync_playwright,expect
if '--multi-root' in sys.argv:
 import v666_root_execution_multi_fixture as x
else:
 import v666_root_execution_fixture as x
f=x.f;mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
def panel():return f.author()
def pending():return f.pending()['blueprint']
def open_graph(feature=x.feature,node="choose"):
 f.idle()
 if panel().is_visible() and panel().locator('[data-bp-node="'+node+'"]').count():return
 f.page.locator('#workspace').click(button='right',position={'x':1300,'y':300});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.get_by_role('button',name='기능',exact=True).click();b.locator('[data-browser-control=object-query]').fill(feature.split('::')[-1]);b.locator('[data-browser-control=object-search]').click();b.locator('[data-object="'+feature+'"]').press('Enter');b.locator('[data-close]').first.click();f.idle();f.page.locator('[data-operation=feature-author-open]').first.click()
 try:expect(panel().locator('[data-bp-node="'+node+'"]')).to_be_visible()
 except Exception:
  (f.case/'open-dom.html').write_text(f.page.content());(f.case/'open-text.txt').write_text(f.page.locator('body').inner_text());f.page.screenshot(path=str(f.case/'open-failure.png'));raise
def restart(i):
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle();expect(panel()).to_be_visible()
def current_plan():return json.loads(next(v['text'] for _,v in pending() if v['type']=='root-execution'))
def save():
 panel().locator('[data-bp-save]').click();expect(panel().locator('.bp-status')).to_have_text('저장됨',timeout=90000);f.idle()
def verify_run():
 if not getattr(x,'multi_mode',False):x.build('ui-after',x.result_code,x.final_stdout);return
 routed=[]
 for file,target,code,stdout in [('Main.graph.json','portable',20,'callee:1\ncallee:2'),('MainLinux.graph.json','linux',100,'linux:4\nlinux:5')]:
  graph=json.loads((f.project/file).read_text());route=any(e['from']==x.route_node and e['port'].startswith('case:') and e['to']=='exit:return' for e in graph['edges']);routed.append(route)
  x.build('ui-after-'+target,code,stdout+('' if route else '\nafter:'+str(code)),target=target)
 assert sum(routed)==1,'Only the explicitly edited caller target gets its return route'
 x.original_code();f.checked('현재 편집 target의 반환 연결만 반영하고 다른 target의 기존 다음 줄과 모든 C# 바이트를 실제 실행으로 보존한다')
def review():
 panel().locator('[data-bp-complete]').click();f.page.locator('.window[data-key=review]:visible,.window[data-key=targets]:visible').first.wait_for(state='visible',timeout=90000);t=f.page.locator('.window[data-key=targets]')
 if t.is_visible():t.locator('[data-target-choice]').select_option('portable');t.locator('[data-close]').click();panel().locator('[data-bp-complete]').click()
 r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=90000);advanced=r.locator('[data-review-advanced]')
 if advanced.is_visible():advanced.click();r.locator('[data-advanced-reviewed]').check()
 return r
try:
 f.start(0);f.invoke('select',{'id':x.feature});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph();expect(panel().locator('[data-root-branch-add]')).to_be_enabled();panel().locator('[data-root-branch-add]').click();assert len(current_plan()['branches'])==1;panel().locator('.bp-viewport').press('Control+z');assert not pending();panel().locator('.bp-viewport').press('Control+y');assert len(current_plan()['branches'])==1;x.original();assert checkpoint.read_bytes()==before;f.checked('원본 사이드바의 공개 루트 분기 추가와 Undo/Redo는 private 입력만 보존한다')
  panel().locator('[data-root-branch-add]').click();branches=current_plan()['branches'];ids=[b['id'] for b in branches]
  for id,name in zip(ids,['성공','실패']):
   field=panel().locator('[data-root-branch="'+id+'"] [data-root-branch-name]');field.fill(name);field.press('Tab')
  panel().locator('[data-bp-percent]').click();zoom=f.page.get_by_role('dialog',name='노드 화면 배율',exact=True);zoom.locator('[data-zoom-preset="25"]').click();zoom.locator('[data-zoom-value]').press('Escape')
  for exit,id in zip(['yes','no'],ids):
   panel().locator('[data-bp-node="$exit:'+exit+'"] [data-bp-branch-select]').click();f.page.locator('[data-branch-option="'+id+'"]').click()
  assert {current_plan()['exits'][name]['executionBranch'] for name in ['yes','no']}==set(ids) and current_plan()['exits']['none']['executionBranch']=='none';panel().locator('[data-bp-save]').click();f.idle();assert pending() and checkpoint.read_bytes()==before;x.original();f.checked('기존 반환 카드를 정확한 공개 ID에 배정하며 호출자 미선택 Save는 전체 입력을 유지한다')
  if getattr(x,'multi_mode',False):
   choices=x.read()['rootExecution'];keys=[c['key'] for c in choices['callers']]
   assert not current_plan()['callers'];assert all(v is None for t in current_plan()['targets'] for v in t['exits'].values())
   panel().locator('[data-root-callers]').select_option(keys[:-1]);panel().locator('[data-bp-save]').click();f.idle();assert pending() and checkpoint.read_bytes()==before;x.original()
   panel().locator('[data-root-callers]').select_option(keys);panel().locator('[data-bp-save]').click();f.idle();assert pending() and checkpoint.read_bytes()==before;x.original()
   for target in current_plan()['targets']:
    for name in target['exits']:panel().locator('[data-root-target="'+target['graph']+'"][data-root-target-exit="'+name+'"]').select_option({'yes':ids[0],'no':ids[1],'none':'none'}[name])
   assert len(current_plan()['callers'])==len(keys);f.checked('복수 호출자 선택 누락과 다른 target의 미지정 반환은 전체 입력을 유지하며, 모든 대응은 직접 선택한다')
  else:
   panel().locator('[data-root-caller]').select_option(x.caller);assert current_plan()['caller']=={'graph':x.caller,'node':'invoke'}
  held=copy.deepcopy(pending());restart(1);assert pending()==held;x.original();f.checked('명시 호출자 선택·한글 분기명·반환 연결을 cold 재시작에서 같은 ID와 source proof로 복원한다')
  if mode=='cancel':
   panel().locator('.bp-viewport').press('Control+z');assert pending();panel().locator('.bp-viewport').press('Control+y');assert pending()==held;x.original();f.checked('재시작 후 편집 Undo/Redo도 동일 후보와 원본을 보존한다')
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:panel().locator('[data-bp-save]').click();f.idle();assert pending() and checkpoint.read_bytes()==before;x.original()
   finally:checkpoint.chmod(0o600)
   restart(2);f.checked('저장 권한 실패와 재시작은 루트/호출자 원본 및 private 입력을 보존한다')
  if mode=='conflict':
   file=f.project/'After.node.json';file.write_bytes(x.physical[file]+b' ');x.physical[file]=file.read_bytes();panel().locator('[data-bp-save]').click();f.idle();assert pending() and checkpoint.read_bytes()==before;x.original();f.checked('다른 frame인 호출자 물리 원문 충돌도 전체 미적용하고 입력을 유지한다')
  else:
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
     assert paused;field=panel().locator('[data-root-branch="'+ids[0]+'"] [data-root-branch-name]');field.fill('성공 새 입력');field.press('Tab');paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',interrupt);f.idle();assert pending();restart(3);mark=len(f.traffic);panel().locator('[data-bp-save]').click();f.idle();assert pending() and current_plan()['branches'][0]['name']=='성공 새 입력';assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for r in f.traffic[mark:]);assert x.read()['rootExecution']['branches'][0]['name']=='성공';save();assert x.read()['rootExecution']['branches'][0]['name']=='성공 새 입력';f.checked('늦은 분기명은 cold 뒤 먼저 이전 receipt만 조회하고 새 입력을 유지한 채 두 번째 명시 Save로 별도 반영한다')
    else:
     assert any(r in queries for r in lost) and pending();f.page.unroute_all(behavior='wait');restart(3);mark=len(f.traffic);save();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for r in f.traffic[mark:]);f.checked('응답 유실 뒤 cold receipt 조회는 공개 분기/호출자 결합을 중복 저장하지 않는다')
   else:save()
   assert not pending();x.original();assert x.read()['diagnostics']['state']=='source-ready';assert x.read(x.caller)['diagnostics']['state']=='source-ready';f.checked('저장은 루트 계약·반환과 명시 호출자의 실행 포트를 한 checkpoint 후보로 결합한다')
   open_graph(f.n+'Main',getattr(x,'route_node','invoke'));call_node=panel().locator('[data-bp-node="'+getattr(x,'route_node','invoke')+'"]');expect(call_node.locator('[data-port="case:'+ids[0]+'"]')).to_be_visible();expect(call_node.locator('[data-branch-name]')).to_have_count(2);assert call_node.locator('[data-branch-name]').first.get_attribute('readonly') is not None
   call_node.locator('[data-port="case:'+ids[0]+'"]').click();panel().locator('[data-bp-node="$exit:return"] .bp-exec-header-in').click();assert pending();save();x.original();f.checked('명시 호출자 화면의 readonly 공개 분기 포트를 기존 반환 카드에 연결해 같은 그룹으로 저장한다')
   r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();x.original();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();verify_run();assert (f.project/'Flow.node.json').read_bytes()==x.physical[f.project/'Flow.node.json'];assert (f.project/'After.node.json').read_bytes()==x.physical[f.project/'After.node.json'];f.checked('Review 취소와 최종 Confirm을 구별하고 원문 바이트 및 미연결 다음 줄 실행을 보존한다')
   if x.out_mode:f.checked('공개 성공 포트에서 다음 줄을 건너뛰어도 이미 발행한 정수 out을 기존 데이터 반환 카드로 읽는다')
   restart(4);assert x.read()['diagnostics']['state']=='source-ready';assert x.read(x.caller)['diagnostics']['state']=='source-ready';f.checked('최종 반영 뒤 재시작에서 공개 분기·반환·직접 호출자 포트를 복원한다')
  assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'m12-final.png'),full_page=True);f.browser.close()
except Exception:
 (f.case/'failure-details.json').write_text(json.dumps({'errors':f.errors,'checks':f.checks},ensure_ascii=False,indent=2))
 try:f.page.screenshot(path=str(f.case/'m12-failure.png'),timeout=5000)
 except Exception:pass
 raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2));f.stop()
print('M12_FIXTURE '+str(f.case),flush=True)
