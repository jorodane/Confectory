"""The first graph Save binds pending C# and explicit async before allocation."""
import copy,json,sys
from playwright.sync_api import sync_playwright,expect
if '--leaf'in sys.argv:import v666_async_creating_fixture as x
elif '--information'in sys.argv:import v666_async_information_fixture as x
else:import v666_async_new_function_fixture as x
leaf='--leaf'in sys.argv;information='--information'in sys.argv
f=x.f;mode=sys.argv[3] if len(sys.argv)>3 else 'normal';expected_source=x.new_source
def panel():return f.author()
def pending():return f.pending()['blueprint']
def retained(held):
 now=dict(pending());return all(key in now and all(now[key].get(field)==value.get(field)for field in ['type','node','text'])for key,value in held)
def open_graph(feature=x.feature,node=x.node):
 f.idle()
 if panel().is_visible() and panel().locator('[data-bp-node="'+node+'"]').count():return
 if information:
  x.d.open_info();f.owner().locator('[data-inline-method="'+feature+'"]').locator('[data-function-edit],[data-function-write-direct]').click();expect(panel().locator('[data-bp-node="'+node+'"]')).to_be_visible();return
 f.page.locator('#workspace').click(button='right',position={'x':1300,'y':300});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.get_by_role('button',name='기능',exact=True).click();b.locator('[data-browser-control=object-query]').fill(feature.split('::')[-1]);b.locator('[data-browser-control=object-search]').click();b.locator('[data-object="'+feature+'"]').press('Enter');b.locator('[data-close]').first.click();f.idle();f.page.locator('[data-operation=feature-author-open]').first.click();expect(panel().locator('[data-bp-node="'+node+'"]')).to_be_visible()
def toggle(node=None):
 target=panel().locator('[data-bp-node="'+node+'"] .function-node-heading') if node else panel().locator('.bp-identity')
 panel().locator('[data-bp-overview-node="'+node+'"]').click() if node else None
 target.click(button='right');f.page.screenshot(path=str(f.case/('menu-'+(node or 'root')+'.png')));(f.case/'menu.html').write_text(f.page.content());f.page.locator('[data-bp-async="'+(node or '$root')+'"]').click()
def save():
 panel().locator('[data-bp-save]').click();expect(panel().locator('.bp-status')).to_have_text('저장됨',timeout=90000);f.idle()
def restart(i):
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle();expect(panel()).to_be_visible()
 if i==2 and mode=='storage':
  f.page.screenshot(path=str(f.case/'storage-cold.png'));(f.case/'storage-cold.html').write_text(f.page.content())
def review():
 panel().locator('[data-bp-complete]').click();f.page.locator('.window[data-key=review]:visible,.window[data-key=targets]:visible').first.wait_for(state='visible',timeout=90000);t=f.page.locator('.window[data-key=targets]')
 if t.is_visible():t.locator('[data-target-choice]').select_option('portable');t.locator('[data-close]').click();panel().locator('[data-bp-complete]').click()
 r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=90000);a=r.locator('[data-review-advanced]')
 if a.is_visible():a.click();r.locator('[data-advanced-reviewed]').check()
 return r
def bind_created():
 if x.graph is not None:
  assert x.read()['id']==x.graph;return
 rows=[u for u in x.units()if u['kind']=='blueprint'and u['id'].startswith(x.feature+'BlueprintBody/body:')];assert len(rows)==1,rows
 x.graph=rows[0]['id'];x.impl=x.graph.split('/body:')[0];x.paths={u['id']:f.project/u['path']for u in x.units()if u['id']in[x.feature,x.impl,x.graph,x.graph+'/node:body']};assert len(x.paths)==4
 if information:x.owner_draft=next(u['draft']for u in x.units()if u['id']==x.owner)

def editor():
 panel().locator('[data-bp-overview-node="'+x.node+'"]').click();panel().locator('[data-bp-node="'+x.node+'"] [data-internal-code]').click();d=f.page.locator('.bp-script-dialog');expect(d).to_be_visible();return d
try:
 f.start(0)
 if mode!='no-checkpoint':f.invoke('saveDraft',{})
 if information:
  f.invoke('select',dict(id=x.owner));owner=x.owner_proof();basis=x.rpc('readOwnerEdits',id=x.owner,hash=owner['ownerHash']);x.rpc('applySlots',id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=owner['ownerHash'],changes=[dict(type='function-add',id=x.feature,name='첫 결합 함수',description='직접 소유 함수')]))
 elif not leaf:
  f.invoke('createDeclaration',dict(id=x.feature,kind='function'))
  if mode not in ['unsaved-declaration','no-checkpoint']:f.invoke('saveDraft',{})
 checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'),None);before=x.checkpoint();assert leaf or not[u for u in x.units()if u['kind']=='blueprint'and x.feature in u['id']]if checkpoint else True
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph(node='body')
  if information:
   bind_created();before=x.checkpoint();checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));x.original();f.checked('정보 직접 작성 진입의 기존 소유 구현 checkpoint를 유지하고 첫 Blueprint Save 전 입력을 작성한다')
  if leaf:
   v=panel().locator('.bp-viewport').bounding_box();panel().locator('.bp-viewport').click(button='right',position={'x':v['width']*.65,'y':v['height']*.8});f.page.get_by_role('button',name='동작 만들기',exact=True).click();x.node=next(v['node']for _,v in pending()if v['type']=='create');panel().locator('[data-bp-overview-node="'+x.node+'"]').click();panel().locator('[data-bp-node="'+x.node+'"] [data-inline-description]').fill('첫 저장에 함께 만들 비동기 동작');panel().locator('[data-bp-overview-node="$entry"]').click();panel().locator('.bp-port[data-node="$entry"][data-side=out]:not([data-kind])').click();panel().locator('[data-bp-overview-node="'+x.node+'"]').click();panel().locator('[data-bp-node="'+x.node+'"] .bp-exec-header-in').click();panel().locator('[data-bp-overview-node="'+x.node+'"]').click();panel().locator('[data-bp-node="'+x.node+'"] .bp-exec-line-out[data-port=next]').click();panel().locator('[data-bp-overview]').press('Home');panel().locator('[data-bp-node=body] .bp-exec-header-in').click()
  else:toggle()
  toggle(x.node)
  if mode=='normal':
   flags=copy.deepcopy(pending());toggle(x.node);panel().locator('.bp-viewport').press('Control+z');assert retained(flags);panel().locator('.bp-viewport').press('Control+y');assert not retained(flags);panel().locator('.bp-viewport').press('Control+z');assert retained(flags);d=editor();f.page.keyboard.insert_text('// cancelled input');d.locator('[data-code-cancel]').click();assert retained(flags)and not any(v['type']=='source'for _,v in pending());f.checked('첫 생성 전 명시 전환 Undo/Redo와 C# 편집 취소는 원래 입력을 보존하고 저장하지 않는다')
  d=editor();assert 'Task'in d.locator('[data-code-source]').input_value();f.page.keyboard.insert_text(x.new_source);d.locator('[data-code-save]').click();held=copy.deepcopy(pending());assert any(v['type']=='source'for _,v in held)and any(v['type']=='async-plan'for _,v in held);assert x.checkpoint()==before;x.original();restart(1);assert retained(held);f.checked('그래프 생성 전 Root/동작 async와 C# 입력을 첫 Save 없이 작성·cold 복원하고 원본/초안을 보존한다')
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:panel().locator('[data-bp-save]').click();f.idle();assert retained(held)and x.checkpoint()==before;x.original()
   finally:checkpoint.chmod(0o600)
   restart(2);f.checked('최초 결합 저장 실패 뒤 cold는 모든 입력과 생성 전 checkpoint를 보존한다')
  if mode=='conflict':
   path=f.project/'project.cproj';old=path.read_bytes();path.write_bytes(old+b' ')
   try:panel().locator('[data-bp-save]').click();f.idle();assert retained(held)and x.checkpoint()==before
   finally:path.write_bytes(old)
   x.original();restart(2);f.checked('생성 전 등록 충돌은 첫 후보 전체와 원문/입력을 보존하며 cold 뒤 명시 재시도한다')
  mark=len(f.traffic);saved=False
  if mode in ['loss','late','create-loss','create-late']:
   requests=set();queries=set();paused={};lost=[];target='createFeature'if mode.startswith('create-')else'authorBatch'
   def interrupt(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke'and body.get('endpoint')=='blueprint':
     action=body.get('input',{}).get('action')
     if action==target:requests.add(body['requestId'])
     elif requests and action=='settledAuthorBatch':queries.add(body['requestId'])
    response=route.fetch();payload=response.json()
    if mode.endswith('late')and not paused and any(r.get('ok')and r.get('requestId')in requests for r in payload.get('results',[])):paused.update(route=route,response=response);return
    if mode.endswith('loss'):
     for row in payload.get('results',[]):
      if row['requestId']in requests|queries:rid=row['requestId'];lost.append(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
    route.fulfill(response=response,json=payload)
   f.page.route('**/api/request',interrupt);panel().locator('[data-bp-save]').click()
   for _ in range(1000):
    if paused or mode=='create-loss'and lost or mode=='loss'and any(r in queries for r in lost):break
    f.page.wait_for_timeout(30)
   assert len(requests)==1
   if mode.endswith('late'):
    assert paused;expected_source='// late first Save input\n'+x.new_source;d=editor();d.locator('[data-code-source]').evaluate('(el,text)=>{const i=el.value.indexOf(text);if(i<0)throw Error("original editable body missing");el.focus();el.setSelectionRange(i,i+text.length)}',x.new_source);f.page.keyboard.insert_text(expected_source);d.locator('[data-code-save]').click();paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',interrupt);f.idle();assert pending();restart(2)
    if target=='authorBatch':
     bind_created();assert json.loads(x.draft_unit()['draft'])['source']==x.new_source;unsettled=any(v.get('kind')=='author-attempt'for _,v in pending());query_mark=len(f.traffic)
     if unsettled:
      panel().locator('[data-bp-save]').click();f.idle();assert pending();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch'for r in f.traffic[query_mark:])
     f.checked('최초 저장 중 새 C#은 확인된 이전 결과와 구별해 cold 뒤 별도 Save로 보존한다')
    save();saved=True
   else:
    assert lost;f.page.unroute_all(behavior='wait');f.idle();assert pending();restart(2);save();saved=True
   f.checked('최초 '+target+' 응답 중단/새 입력은 원래 소유 경계에서 복구하고 저장을 중복하지 않는다')
  if not saved:save()
  bind_created();applied=[r['invoke']['input']for r in f.traffic[mark:]if r.get('invoke',{}).get('input',{}).get('action')=='authorBatch'];assert len(applied)==(2 if information and mode=='late'else 1),applied;assert len({a['attempt']for a in applied})==len(applied);assert sum(any(e['action']=='asyncTransition'for e in a['edits'])for a in applied)==1;assert len(applied)==1 or applied[1]['edits']==[dict(action='source',node=x.node,text=expected_source)];assert applied[0]['edits'][-1]['action']=='asyncTransition'and any(e['action']=='source'for e in applied[0]['edits']);assert json.loads(x.draft_unit()['draft'])['source']==expected_source;assert x.read()['asyncTransition']['enabled'];assert not pending();x.original();assert not x.path().exists()if leaf else not any(p.exists()for p in x.paths.values());f.checked('첫 Save 한 번은 생성된 소유 graph·원문·명시 Task를 같은 author 후보/checkpoint CAS로 저장한다')
  restart(3);bind_created();assert json.loads(x.draft_unit()['draft'])['source']==expected_source;save();r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();x.original();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();x.build('first-save-execution',True)if leaf else x.build_new('first-save-execution');None if leaf else x.run(f.project,'original-entry',7,'');x.unchanged();assert json.loads(x.path().read_text())['source']==expected_source;restart(4);bind_created();assert x.read()['asyncTransition']['enabled'];x.unchanged();assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'coupled-first-save.png'),full_page=True);f.checked('반복 Save·Review 취소/Confirm·실제 Task 실행·확정 cold는 원래 진입점과 새 원문/등록/입출력을 보존한다');f.browser.close()
except Exception:
 try:f.page.screenshot(path=str(f.case/'failure.png'));(f.case/'failure.html').write_text(f.page.content())
 except Exception:pass
 raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'page-errors.json').write_text(json.dumps(f.errors));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));f.stop()
print('ASYNC_COUPLED_FIRST_FIXTURE',f.case,flush=True)
