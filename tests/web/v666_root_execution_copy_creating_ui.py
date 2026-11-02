"""A new copy edits existing public returns before its atomic first Save."""
import ast,copy,json,pathlib,shutil,sys,time,uuid
from playwright.sync_api import sync_playwright,expect
registered='--registered-creating' in sys.argv
if registered:import v666_root_execution_registered_creating_fixture as c
else:import v666_root_execution_copy_creating_fixture as c
f=c.f;mode=sys.argv[3] if len(sys.argv)>3 else 'normal';is_view='view' in sys.argv[4:]
if is_view:f.owner=lambda:f.page.locator('.window[data-key=editor-1]')
viewport={'width':2300 if is_view else 1800,'height':1700 if is_view else 1400}
def panel():return f.author()
helper=pathlib.Path(__file__).with_name('v666_root_execution_ui.py');exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='review'],type_ignores=[]),str(helper),'exec'))
root_review=review
def review():
 if not is_view:return root_review()
 f.close_author();f.owner().locator('.object-title-name').click(position={'x':4,'y':4});f.owner().locator('[data-element-action=confirm]').click();f.page.locator('#review-creation:visible,.window[data-key=review]:visible,.window[data-key=targets]:visible').first.wait_for(state='visible',timeout=90000)
 target=f.page.locator('.window[data-key=targets]')
 if target.is_visible():target.locator('[data-target-choice]').select_option('portable');target.locator('[data-close]').click();f.owner().locator('[data-element-action=confirm]').click()
 if f.page.locator('#review-creation').count():f.page.locator('#review-creation').click()
 r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=90000);advanced=r.locator('[data-review-advanced]')
 if advanced.is_visible():advanced.click();r.locator('[data-advanced-reviewed]').check()
 return r
def pending():return [(k,v) for k,v in f.pending()['blueprint'] if v.get('type')=='branch-exits']
def selected():return json.loads(pending()[0][1]['text'])
def choose(branch):
 panel().locator('[data-bp-node="$exit:yes"] [data-bp-branch-select]').click();f.page.get_by_role('listbox',name='기존 분기 선택',exact=True).locator('[data-branch-option="'+branch+'"]').click()
def view_rejections():
 if not is_view:return
 binding=next(v['invoke']['input'] for v in reversed(f.traffic) if v.get('invoke',{}).get('input',{}).get('view')=='1' and v['invoke']['input'].get('viewBinding'));current=c.read();owner=c.binding();before=checkpoint.read_bytes();plan={'entry':current['entry'],'edges':copy.deepcopy(current['edges']),'exits':{r['name']:json.loads(r['valueJson']) for r in current['exits']}}
 request={'id':c.graph,'owner':c.owner,'ownerHash':owner['hash'],'ownerRevision':owner['revision'],'view':'1','viewBinding':binding['viewBinding'],'checkpointHash':current['checkpointHash'],'sourceProof':c.x.proof(current)}
 for kind in ['public-contract','wrong-node','extra-contract','wrong-owner','surface-spoof']:
  bad=copy.deepcopy(request);bad.update(action='authorBatch',attempt=uuid.uuid4().hex,edits=[{'action':'branchExits','node':'$branches','definition':copy.deepcopy(plan)}])
  if kind=='public-contract':bad['edits']=[{'action':'rootExecution','node':'$root','definition':{'branches':[]}}]
  elif kind=='wrong-node':bad['edits'][0]['node']='$root'
  elif kind=='extra-contract':bad['edits'][0]['definition']['branches']=[]
  elif kind=='wrong-owner':bad['owner']=f.n+'Monster'
  else:bad['uiSurface']='view:1'
  f.invoke('blueprint',bad,False);assert checkpoint.read_bytes()==before;c.original()
 f.idle();f.checked('독립 창은 정확한 소유 반환 계획만 전달하며 공개 계약·다른 소유자·서버 surface 위조를 거절한다')
def save():
 expected=copy.deepcopy(selected());panel().locator('[data-bp-save]').click();deadline=time.monotonic()+120
 while time.monotonic()<deadline:
  f.page.wait_for_timeout(60)
  if not f.pending()['blueprint'] and '저장 중' not in panel().locator('.bp-status').inner_text():break
 assert not f.pending()['blueprint'],panel().locator('.bp-status').inner_text();f.idle();rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']};stored=json.loads(rows[c.graph]['draft']);assert {k:stored[k] for k in ['entry','edges','exits']}==expected;assert c.read()['diagnostics']['state']=='source-ready'
def restart(i,receipt=False):
 held=copy.deepcopy(pending());plan=copy.deepcopy(selected()) if held else None;f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size(viewport);f.idle();arrange()
 if receipt:
  if pending():assert selected()==plan
  else:
   assert mode=='loss';rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']};stored=json.loads(rows[c.graph]['draft']);assert {k:stored[k] for k in ['entry','edges','exits']}==plan;assert c.read()['diagnostics']['state']=='source-ready'
 else:assert pending()==held
def arrange():
 if not is_view or not f.owner().is_visible():return
 title=f.owner().locator('.object-title-name').bounding_box();box=f.owner().bounding_box();f.page.mouse.move(title['x']+5,title['y']+5);f.page.mouse.down();f.page.mouse.move(1780+title['x']-box['x']+5,80+title['y']-box['y']+5,steps=10);f.page.mouse.up()
def open_copy():
 f.page.locator('#workspace').click(button='right',position={'x':80,'y':100});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=info]').click();b.locator('[data-browser-control="object-query"]').fill('FreeInfo');b.locator('[data-browser-control="object-search"]').click();row=b.locator('[data-object="'+c.owner+'"]')
 if is_view:row.click(button='right');f.page.locator('.context-menu').get_by_role('button',name='새 창으로 열기',exact=True).click()
 else:row.press('Enter')
 b.locator('[data-close]').first.click();f.idle();arrange();slot=f.owner().locator('[data-module-method="'+c.x.feature+'"]')
 if not slot.locator('[data-function-edit],[data-function-write-direct]').first.is_visible():f.owner().locator('[data-behavior-toggle="'+c.module+'"]').click()
 slot.locator('[data-function-edit],[data-function-write-direct]').first.click();picker=f.page.get_by_role('dialog',name='구현 선택',exact=True);expect(picker).to_be_visible();picker.locator('[data-copy-source="'+c.x.impl+'"][data-copy-target=common]').click();f.idle();choices=[v['copy'] for _,v in f.pending()['blueprint'] if v.get('kind')=='copy-selection'];assert len(choices)==1;c.implementation=choices[0]['implementation'];c.graph=c.implementation+'/body:common';expect(panel().locator('[data-bp-node=choose]')).to_be_visible()
try:
 f.start(0);f.invoke('select',{'id':c.owner});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size(viewport);open_copy();before=checkpoint.read_bytes();expect(panel().locator('[data-root-branch-add]')).to_be_disabled();expect(panel().locator('[data-root-branch]')).to_have_count(2)
  for row in panel().locator('[data-root-branch]').all():assert row.locator('input').get_attribute('readonly') is not None;expect(row.locator('[data-root-branch-remove]')).to_be_disabled()
  panel().locator('[data-bp-percent]').click();zoom=f.page.get_by_role('dialog',name='노드 화면 배율',exact=True);zoom.locator('[data-zoom-preset="25"]').click();zoom.locator('[data-zoom-value]').press('Escape');panel().locator('[data-bp-node="$exit:yes"] [data-bp-branch-select]').click();f.page.keyboard.press('Escape');assert not pending();choose('failure');held=copy.deepcopy(pending());panel().locator('.bp-viewport').press('Control+z');assert not pending();panel().locator('.bp-viewport').press('Control+y');assert pending()==held;panel().locator('[data-root-branch="success"] [data-root-branch-place]').click();assert len(selected()['exits'])==4;panel().locator('.bp-viewport').press('Control+z');assert pending()==held;c.original();assert checkpoint.read_bytes()==before;f.checked('첫 Save 전 공개 정의는 readonly이며 기존 분기 반환 선택·배치·Escape·Undo/Redo는 소유 선택과 원문을 유지한다')
  restart(1);expect(panel()).to_be_visible();c.original()
  if mode=='cancel':
   f.close_author();f.owner().locator('[data-element-action=discard]').click();expect(f.owner().locator('[data-element-action=discard]')).to_be_disabled(timeout=30000);assert not f.pending()['blueprint'] and not json.loads(checkpoint.read_text()).get('privateCopies');c.original();restart(2);assert not f.pending()['blueprint'];c.original();f.checked('명시 취소는 이번 copy 선택·반환 입력만 제거하며 cold에도 등록·배정·파일을 만들지 않는다')
  else:
   if mode=='project':
    other=f.case/'same IDs other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory'));f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(other/'project.cproj');f.start(10);f.page=f.setup();f.page.set_viewport_size(viewport);f.idle();assert not f.pending()['blueprint'];f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(c.x.manifest);f.start(11);f.page=f.setup();f.page.set_viewport_size(viewport);f.idle();assert pending()==held;f.checked('동일 ID의 다른 프로젝트와 왕복해도 새 copy 선택과 반환 입력을 섞지 않는다')
   if mode=='storage':
    checkpoint.chmod(0o400)
    try:panel().locator('[data-bp-save]').click();f.idle();assert pending() and checkpoint.read_bytes()==before;c.original()
    finally:checkpoint.chmod(0o600)
    restart(2);f.checked('첫 Save 쓰기 실패는 등록·배정·반환을 모두 미적용하고 입력을 cold에도 보존한다')
   if mode=='conflict':
    source=c.source_file if registered else f.project/'Flow.celem';c.mutate_source() if registered else source.write_bytes(c.physical[source]+b' ');c.physical[source]=source.read_bytes();panel().locator('[data-bp-save]').click();f.idle();assert pending() and checkpoint.read_bytes()==before;c.original();f.checked('첫 Save 원문 경합은 외부 수정과 copy 입력을 유지하며 새 구현을 만들지 않는다')
   else:
    if mode in ['loss','late']:
     applies=set();queries=set();lost=[];paused={}
     def intercept(route):
      request=route.request.post_data_json
      if request.get('op')=='invoke' and request.get('endpoint')=='blueprint':
       if request.get('input',{}).get('action')=='applySlots':applies.add(request['requestId'])
       elif applies and request.get('input',{}).get('action')=='settledSlots':queries.add(request['requestId'])
      response=route.fetch();payload=response.json()
      if mode=='late' and not paused and any(v.get('ok') and v.get('requestId') in applies for v in payload.get('results',[])):paused.update(route=route,response=response);return
      for row in payload.get('results',[]):
       if mode=='loss' and row['requestId'] in applies|queries:rid=row['requestId'];lost.append(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
      route.fulfill(response=response,json=payload)
     f.page.route('**/api/request',intercept);panel().locator('[data-bp-save]').click()
     for _ in range(1000):
      if paused or applies and any(v in queries for v in lost):break
      f.page.wait_for_timeout(30)
     assert len(applies)==1
     if mode=='late':
      assert paused;choose('none');paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',intercept);f.idle();assert pending();mark=len(f.traffic);restart(3,True);assert pending() and selected()['exits']['yes']['executionBranch']=='none';assert not any(v.get('invoke',{}).get('input',{}).get('action') in ['applySlots','authorBatch'] for v in f.traffic[mark:]);mark=len(f.traffic);panel().locator('[data-bp-save]').click();f.idle();actions=[v.get('invoke',{}).get('input',{}).get('action') for v in f.traffic[mark:]]
      if pending():assert 'settledSlots' in actions and not any(a in ['applySlots','authorBatch'] for a in actions);save()
      assert not f.pending()['blueprint'];assert not any(v.get('invoke',{}).get('input',{}).get('action')=='applySlots' for v in f.traffic[mark:]);assert sum(v.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for v in f.traffic[mark:])==1;rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']};assert json.loads(rows[c.graph]['draft'])['exits']['yes']['executionBranch']=='none';f.checked('생성 중 늦은 입력은 cold에서 보존하고 기존 소유 copy의 명시 Save 한 번으로 별도 반영하며 자동 저장·중복 생성하지 않는다')
     else:
      assert any(v in queries for v in lost);f.page.unroute_all(behavior='wait');f.idle();mark=len(f.traffic);restart(3,True)
      if pending():save()
      assert not f.pending()['blueprint'];assert not any(v.get('invoke',{}).get('input',{}).get('action') in ['applySlots','authorBatch'] for v in f.traffic[mark:]);f.checked('첫 Save 응답 유실·cold receipt 조회는 copy 생성·배정·반환을 중복 적용하지 않는다')
    else:save()
    c.original();view_rejections();r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();c.original();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();c.retained();c.build('creating-ui-after','none' if mode=='late' else 'failure');restart(4);assert c.read()['diagnostics']['state']=='source-ready';c.retained();f.checked('Review 취소/Confirm·확정 뒤 cold와 실제 호출은 원계약·C#·donor를 보존하고 out→분기→다음 줄을 실행한다')
  assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'m12-creating-copy-final.png'),full_page=True);f.browser.close()
except Exception:
 try:f.page.screenshot(path=str(f.case/'m12-creating-copy-failure.png'),timeout=5000);(f.case/'failure-dom.html').write_text(f.page.content())
 except Exception:pass
 raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2));f.stop()
print('M12_CREATING_COPY_UI '+str(f.case),flush=True)
