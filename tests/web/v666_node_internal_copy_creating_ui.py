"""First-save copy flow in the authored UI; interrupted saves retain the exact selection."""
import copy,json,shutil,sys,time
from playwright.sync_api import sync_playwright,expect
import v666_node_internal_copy_creating_fixture as n
f=n.f;mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
def panel():return f.page.locator('.window[data-key=blueprint]')
def cells():return [(k,v) for k,v in f.pending()['blueprint'] if v.get('type') in ['internal-flow','source','enum-code']]
def open_copy():
 f.idle()
 if panel().is_visible():return
 n.d.open_info();title=f.owner().locator('.object-title-name').bounding_box();box=f.owner().bounding_box();f.page.mouse.move(title['x']+5,title['y']+5);f.page.mouse.down();f.page.mouse.move(1780+title['x']-box['x']+5,80+title['y']-box['y']+5,steps=10);f.page.mouse.up();slot=f.owner().locator('[data-module-method="'+n.feature+'"]')
 if not slot.locator('[data-function-edit],[data-function-write-direct]').first.is_visible():f.owner().locator('[data-behavior-toggle="'+n.module+'"]').click()
 slot.locator('[data-function-edit],[data-function-write-direct]').first.click();picker=f.page.get_by_role('dialog',name='구현 선택',exact=True)
 expect(picker).to_be_visible();f.idle();picker.locator('[data-copy-source="'+n.x.impl+'"][data-copy-target=common]').click();f.idle()
 for part in n.frame_path.split('/') if n.frame_path else []:
  f.idle();panel().locator('[data-bp-node="'+part+'"] [data-internal-flow]').click();f.idle();f.page.screenshot(path=str(f.case/('open-'+part+'.png')));(f.case/('open-'+part+'.html')).write_text(f.page.content());(f.case/('open-'+part+'.json')).write_text(json.dumps(f.pending(),ensure_ascii=False,indent=2))
 expect(panel().locator('[data-bp-node="'+n.node+'"]')).to_be_visible();choices=[v['copy'] for _,v in f.pending()['blueprint'] if v.get('kind')=='copy-selection' and v['copy']['owner']==n.owner];assert len(choices)==1; n.set_copy(choices[0]['implementation'])
def restart(i):
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});f.idle()
def code(text,cancel=False):
 panel().locator('[data-bp-node=body] [data-internal-code]').click();dialog=f.page.get_by_role('dialog',name='C# Script · body',exact=True);editor=dialog.locator('[data-code-source]');body=dialog.locator('[data-code-region=body]').text_content();raw=editor.input_value();assert (' Invoke(' if n.context else ' Execute(') in raw
 editor.evaluate('(el,body)=>{const at=el.value.indexOf(body);if(at<0)throw Error("body not found");el.focus();el.setSelectionRange(at,at+body.length)}',body);f.page.keyboard.insert_text(text)
 if n.branch:
  helper=dialog.locator('[data-code-region=helpers]').text_content();editor.evaluate('(el,helper)=>{const at=el.value.lastIndexOf(helper);if(at<0)throw Error("helpers not found");el.focus();el.setSelectionRange(at,at+helper.length)}',helper);f.page.keyboard.insert_text(n.helpers+'// explicit UI helper input\r\n')
 dialog.locator('[data-code-cancel]' if cancel else '[data-code-save]').click()
 if n.branch and not cancel and not hasattr(n,'expected_helpers'):n.expected_helpers=json.loads(next(v['text'] for _,v in cells() if v['type']=='enum-code'))['helpers']
def save(owner=False):
 if owner:f.close_author();f.owner().locator('[data-element-action=save]').click()
 else:panel().locator('[data-bp-save]').click()
 observer=f.mount();snapshot=observer['state'];deadline=time.monotonic()+120
 try:
  while time.monotonic()<deadline:
   f.page.evaluate('async()=>await confectoryFlushPresentation()');update=f.raw({'op':'update','view':observer['view'],'scope':observer['scope']});assert not update.get('error'),update;snapshot=update.get('state') or snapshot
   remaining=snapshot['presentation']['inputs']['blueprint']
   if not remaining and (owner or '저장 중' not in panel().locator('.bp-status').inner_text()):break
   f.page.wait_for_timeout(250)
  assert not remaining,{'status':panel().locator('.bp-status').inner_text(),'remaining':remaining}
 finally:f.raw({'op':'dispose','view':observer['view']})
 f.idle();assert not cells()
from contextlib import contextmanager
@contextmanager
def recorded_playwright():
 with sync_playwright() as pw:
  try:yield pw
  except Exception:
   try:
    f.page.screenshot(path=str(f.case/'creating-copy-failure.png'),timeout=5000);(f.case/'creating-copy-failure.html').write_text(f.page.content());(f.case/'creating-copy-failure-inputs.json').write_text(json.dumps(f.pending(),ensure_ascii=False,indent=2))
   except Exception:pass
   raise
def review():
 f.close_author();r=n.d.review()
 if r.locator('[data-additional-changes]').count():r.locator('[data-review-advanced]').click();r.locator('[data-advanced-reviewed]').check()
 return r
try:
 n.build('before');f.start(0);f.invoke('select',{'id':n.owner});f.invoke('saveDraft',{})
 with recorded_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});open_copy();checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();seed=json.loads(before)['privateCopies'][n.impl]['snapshot'];original_node=next(r for r in n.at(seed['graph'])['nodes'] if r['id']==n.node)
  panel().locator('[data-bp-node="'+n.node+'"] [data-internal-flow]').click();f.idle();expect(panel().locator('[data-bp-node=body]')).to_be_visible();assert len(cells())==1;panel().locator('.bp-viewport').press('Control+z');expect(panel().locator('[data-bp-node="'+n.node+'"] [data-internal-flow]')).to_be_enabled();assert not cells();panel().locator('.bp-viewport').press('Control+y');expect(panel().locator('[data-bp-node=body]')).to_be_visible();assert len(cells())==1 and checkpoint.read_bytes()==before;n.unchanged();f.checked('아직 등록되지 않은 copy도 내부 진입·Undo/Redo는 선택/원문/체크포인트를 보존한다')
  code(n.edited(),True);assert len(cells())==1;code(n.edited());held=copy.deepcopy(cells());assert len(held)==2;restart(1);expect(panel().locator('[data-bp-node=body]')).to_be_visible();assert cells()==held and checkpoint.read_bytes()==before;n.unchanged();f.checked('첫 Save 전 본문 취소·편집·cold는 sealed copy 선택과 내부 전환 입력을 함께 복원한다')
  if mode in ['normal','owner']:
   for name in reversed([p for p in n.frame_path.split('/') if p]):
    f.idle();panel().locator('.bp-breadcrumbs button').filter(has_text=name).click();f.idle();assert cells()==held
   f.idle();panel().locator('.bp-breadcrumbs button').first.click();f.idle();assert cells()==held
   if mode=='normal':
    for part in [p for p in n.frame_path.split('/') if p]+[n.node]:
     f.idle();panel().locator('[data-bp-node="'+part+'"] [data-internal-flow]').click();f.idle()
    panel().locator('.bp-breadcrumbs button').first.click();f.idle()
   f.checked('선택한 기존 중첩 frame의 조상/Root 왕복은 같은 qualified 원문과 전환 입력을 보존한다')
  if mode=='cancel':
   panel().locator('.bp-viewport').press('Control+z');assert not cells();f.close_author();f.owner().locator('[data-element-action=discard]').click();expect(f.owner().locator('[data-element-action=discard]')).to_be_disabled(timeout=30000);assert not f.pending()['blueprint'] and not json.loads(checkpoint.read_text()).get('privateCopies');n.unchanged();restart(2);assert not f.pending()['blueprint'];n.unchanged();f.checked('첫 copy 전환의 명시 취소는 자기 선택/내부 입력만 제거하고 cold에도 등록·배정·파일을 남기지 않는다')
  else:
   if mode=='project':
    other=f.case/'same IDs other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory'));f.pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(other/'project.cproj');f.start(10);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});f.idle();assert not f.pending()['blueprint'];f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(n.manifest);f.start(11);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});f.idle();expect(panel().locator('[data-bp-node=body]')).to_be_visible();assert cells()==held;n.unchanged();f.checked('동일 ID의 다른 프로젝트에는 새 copy 선택과 내부 입력을 전달하지 않고 왕복 뒤 원래 초안을 복원한다')
   if mode!='late':
    if panel().locator('.bp-breadcrumbs button').count():f.idle();panel().locator('.bp-breadcrumbs button').first.click();f.idle()
    expect(panel().locator('[data-bp-node="'+(n.frame_path.split('/')[0] if n.frame_path else n.node)+'"]')).to_be_visible()
   if mode=='conflict':
    original=f.project/'Flow.node.json';original.write_bytes(n.physical[original]+b' ');panel().locator('[data-bp-save]').click();f.idle();assert cells()==held and checkpoint.read_bytes()==before;original.write_bytes(n.physical[original]);n.unchanged();f.checked('donor 원문 경합은 copy 생성·배정·내부 후보를 전체 거절하고 입력을 보존한다')
   else:
    if mode=='storage':
     checkpoint.chmod(0o400)
     try:panel().locator('[data-bp-save]').click();f.idle();assert cells()==held and checkpoint.read_bytes()==before;n.unchanged()
     finally:checkpoint.chmod(0o600)
     restart(2);assert cells()==held;f.checked('첫 Save 쓰기 실패·cold는 미등록 copy와 내부 코드 입력을 잃지 않는다')
    if mode=='loss':
     applies=set();queries=set();lost=[]
     def interrupt(route):
      body=route.request.post_data_json
      if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
       action=body.get('input',{}).get('action')
       if action=='applySlots':applies.add(body['requestId'])
       elif applies and action=='settledSlots':queries.add(body['requestId'])
      response=route.fetch();payload=response.json()
      for row in payload.get('results',[]):
       if row['requestId'] in applies|queries:rid=row['requestId'];lost.append(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
      route.fulfill(response=response,json=payload)
     f.page.route('**/api/request',interrupt);panel().locator('[data-bp-save]').click()
     for _ in range(1000):
      if applies and any(r in queries for r in lost):break
      f.page.wait_for_timeout(30)
     assert len(applies)==1 and any(r in queries for r in lost) and cells()==held;f.page.unroute_all(behavior='wait');restart(3);f.idle();assert not cells();n.unchanged();f.checked('첫 copy 저장·조회 응답 유실은 cold receipt로 같은 등록/배정/래핑을 한 번만 복구한다')
    elif mode=='late':
     ids=set();paused={}
     def hold(route):
      body=route.request.post_data_json
      if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('action')=='applySlots':ids.add(body['requestId'])
      response=route.fetch();payload=response.json()
      if not paused and any(row.get('ok') and row.get('requestId') in ids for row in payload.get('results',[])):paused.update(route=route,response=response);return
      route.fulfill(response=response)
     f.page.route('**/api/request',hold);panel().locator('[data-bp-save]').click()
     for _ in range(1000):
      if paused:break
      f.page.wait_for_timeout(30)
     assert paused and len(ids)==1;code(n.edited(2));paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',hold);f.idle();assert len(cells())==1 and (json.loads(cells()[0][1]['text'])['source'] if cells()[0][1]['type']=='enum-code' else cells()[0][1]['text'])==n.edited(2);restart(3);save();f.checked('첫 copy Save 중 늦은 C# 입력은 accepted 후보와 분리해 보존하고 다음 Save에만 적용한다')
    else:save(owner=mode=='owner')
    assert not cells();rows=n.changes();graph=json.loads(rows[n.root]['draft']);outer=next(r for r in n.at(graph)['nodes'] if r['id']==n.node);assert outer['retainedCode']['definition']==original_node;expected=copy.deepcopy(seed['graph']);n.at(expected)['nodes'][n.at(expected)['nodes'].index(original_node)]=copy.deepcopy(outer);assert graph==expected
    if n.branch:assert json.loads(rows[n.leaf]['draft'])['helpers']==n.expected_helpers
    n.unchanged();r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();n.unchanged();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();assert all(p.read_bytes()==v for p,v in n.physical.items() if p.name not in ['FreeInfo.celem','project.cproj']);n.build('after',2 if mode=='late' else 1);f.checked('명시 Review 취소/Confirm은 원계약·donor·출처·기존 연결을 보존하며 새 copy 편집 결과만 실행한다');restart(4);assert n.read(n.child)['diagnostics']['state']=='source-ready';f.checked('확정 뒤 cold는 새 소유 copy의 같은 내부 frame과 활성 소스를 복원한다')
  assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'creating-copy-final.png'));f.browser.close()
except Exception:
 try:f.page.screenshot(path=str(f.case/'creating-copy-failure.png'),timeout=5000)
 except Exception:pass
 raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
