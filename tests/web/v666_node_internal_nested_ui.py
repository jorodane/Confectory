"""중첩 C# 진입의 원본 UI, 조상 왕복/Undo와 원자 Save·실패·cold·Confirm."""
import ast,copy,json,pathlib,shutil,sys,time
from playwright.sync_api import sync_playwright,expect
import v666_node_internal_nested_fixture as n
x=n.x;f=n.f;feature=n.feature;graph=n.root;child=n.child;mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
helper=pathlib.Path(__file__).with_name('v666_node_internal_ui.py');names={'original','panel','pending','code','restart','save','review'};exec(compile(ast.Module(body=[row for row in ast.parse(helper.read_text()).body if isinstance(row,ast.FunctionDef) and row.name in names],type_ignores=[]),str(helper),'exec'))
def open_root():
 f.idle()
 if panel().is_visible():
  if panel().locator('.bp-breadcrumbs button').count():panel().locator('.bp-breadcrumbs button').first.click()
 else:
  f.page.locator('#workspace').click(button='right',position={'x':1300,'y':300});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.get_by_role('button',name='기능',exact=True).click();b.locator('[data-browser-control=object-query]').fill('Flow');b.locator('[data-browser-control=object-search]').click();b.locator('[data-object="'+feature+'"]').press('Enter');b.locator('[data-close]').first.click();f.idle();f.page.locator('[data-operation=feature-author-open]').first.click()
 expect(panel().locator('[data-bp-node=frame0]')).to_be_visible()
def open_parent():
 open_root()
 for part in n.parts:panel().locator('[data-bp-node="'+part+'"] [data-function-write-direct]').click()
 expect(panel().locator('[data-bp-node=calculate]')).to_be_visible()
def enter():
 panel().locator('[data-bp-node=calculate] [data-internal-flow]').click();expect(panel().locator('[data-bp-node=body]')).to_be_visible();expect(panel().locator('.bp-status')).to_contain_text('미리보기')
def data(id=n.parent):return n.read(id)
try:
 f.start(0);f.invoke('select',{'id':feature});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_parent();enter();original();assert checkpoint.read_bytes()==before
  panel().locator('.bp-viewport').press('Control+z');expect(panel().locator('[data-bp-node=calculate]')).to_be_visible();panel().locator('.bp-viewport').press('Control+y');expect(panel().locator('[data-bp-node=body]')).to_be_visible();original();f.checked('원본 직접 작성 진입은 선택한 중첩 동작만 단일 코드로 미리보고 Undo/Redo와 원문·조상 연결을 보존한다')
  code('return amount+8;',True);assert not pending();code('return amount+8;');held=copy.deepcopy(pending());assert len(held)==1 and '|private:'+n.path+'/calculate|' in held[0][0];original();restart(1);expect(panel().locator('[data-bp-node=body]')).to_be_visible();assert pending()==held;f.checked('C# 취소/편집 및 cold는 전체 중첩 경로로 입력을 보관하며 동일 local ID의 형제를 건드리지 않는다')
  # Walk every original breadcrumb, not just an arbitrarily chosen depth.
  for name in reversed(n.parts):
   panel().locator('.bp-breadcrumbs button').filter(has_text=name).click();expect(panel().locator('[data-bp-name]')).to_have_value(name);assert pending()==held;original()
  panel().locator('.bp-breadcrumbs button').first.click();expect(panel().locator('[data-bp-node=frame0]')).to_be_visible();panel().locator('.bp-viewport').press('Control+z');expect(panel().locator('[data-bp-node=calculate]')).to_be_visible();assert not pending();panel().locator('.bp-viewport').press('Control+y');expect(panel().locator('[data-bp-node=body]')).to_be_visible();assert pending()==held;original();f.checked('모든 조상/Root 왕복에서도 전환 Undo/Redo와 편집한 내부 코드가 함께 복원된다')
  if mode=='project':
   other=f.case/'same IDs other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory'));f.pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(other/'project.cproj');f.start(10);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_parent();assert not pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(x.manifest);f.start(11);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle();expect(panel().locator('[data-bp-node=body]')).to_be_visible();assert pending()==held;original();f.checked('동일 namespace/경로/ID의 다른 프로젝트 왕복도 중첩 입력과 전환 의도를 섞지 않는다')
  if mode!='late':panel().locator('.bp-breadcrumbs button').first.click();expect(panel().locator('[data-bp-node=frame0]')).to_be_visible()
  if mode=='conflict':
   file=f.project/'Flow.node.json';file.write_bytes(x.physical[file]+b' ');x.physical[file]=file.read_bytes();panel().locator('[data-bp-save]').click();f.idle();assert pending()==held and checkpoint.read_bytes()==before;original();f.checked('중첩 원문 경합은 전체 후보를 미적용하고 모든 입력과 부모·형제 파일을 유지한다')
  else:
   if mode=='storage':
    checkpoint.chmod(0o400)
    try:panel().locator('[data-bp-save]').click();f.idle();assert pending()==held and checkpoint.read_bytes()==before;original()
    finally:checkpoint.chmod(0o600)
    restart(2);assert pending()==held;f.checked('checkpoint 쓰기 실패와 cold는 전체 경로의 입력·전환 의도·원문을 그대로 보존한다')
   if mode=='loss':
    applies=set();queries=set();lost=[]
    def interrupt(route):
     body=route.request.post_data_json
     if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
      action=body.get('input',{}).get('action')
      if action=='authorBatch':applies.add(body['requestId'])
      elif applies and action=='settledAuthorBatch':queries.add(body['requestId'])
     response=route.fetch();payload=response.json()
     for v in payload.get('results',[]):
      if v['requestId'] in applies|queries:rid=v['requestId'];lost.append(rid);v.clear();v.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
     route.fulfill(response=response,json=payload)
    f.page.route('**/api/request',interrupt);panel().locator('[data-bp-save]').click()
    for _ in range(1000):
     if applies and any(r in queries for r in lost):break
     f.page.wait_for_timeout(30)
    assert len(applies)==1 and any(r in queries for r in lost) and pending()==held;f.page.unroute_all(behavior='wait');restart(3);mark=len(f.traffic);save();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for r in f.traffic[mark:]);f.checked('중첩 저장/조회 응답 유실은 cold receipt로 확인하며 같은 동작을 다시 래핑하지 않는다')
   elif mode=='late':
    ids=set();paused={}
    def hold(route):
     body=route.request.post_data_json
     if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('action')=='authorBatch':ids.add(body['requestId'])
     response=route.fetch();payload=response.json()
     if not paused and any(v.get('ok') and v.get('requestId') in ids for v in payload.get('results',[])):paused.update(route=route,response=response);return
     route.fulfill(response=response)
    f.page.route('**/api/request',hold);panel().locator('[data-bp-save]').click()
    for _ in range(1000):
     if paused:break
     f.page.wait_for_timeout(30)
    assert paused and len(ids)==1;code('return amount+9;');paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',hold);f.idle();assert pending() and pending()[0][1]['text']=='return amount+9;';restart(3);save();f.checked('늦은 C# 입력은 정확한 중첩 후보로 재기준하고 cold 뒤 다음 Save에서만 적용한다')
   else:save()
   assert not pending();assert next(row for row in data(n.child)['nodes'] if row['id']=='body')['source']==('return amount+9;' if mode=='late' else 'return amount+8;');original();f.checked('Root 또는 내부 Save는 선택한 private frame의 변환·본문·원문 guard를 하나의 후보/CAS로 저장한다')
   r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();original();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();published=json.loads((f.project/'Flow.graph.json').read_text());selected=next(row for row in n.at(published)['nodes'] if row['id']=='calculate');expected=copy.deepcopy(n.graph);at=n.at(expected);at['nodes'][next(i for i,row in enumerate(at['nodes']) if row['id']=='calculate')]=copy.deepcopy(selected);assert published==expected;assert selected['graph']['profile']=='sync-acyclic-methods-v1';n.assert_wrapper(selected);assert (f.project/'Flow.node.json').read_bytes()==x.physical[f.project/'Flow.node.json'] and (f.project/'Peer.node.json').read_bytes()==x.physical[f.project/'Peer.node.json'];x.build('nested-ui-after',12 if mode=='late' else 11);f.checked('Review 취소/컴파일 Confirm은 부모·형제·혼합 profile을 보존하고 선택한 내부 C#만 활성화한다')
   restart(4);assert data(n.child)['diagnostics']['state']=='source-ready';f.checked('확정 cold는 전체 중첩 경로의 활성 구현을 복원한다')
  assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'nested-internal-final.png'),full_page=True);f.browser.close()
except Exception:
 try:f.page.screenshot(path=str(f.case/'nested-internal-failure.png'),timeout=5000)
 except Exception:pass
 raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2));f.stop()
print('M11_NESTED_UI_FIXTURE '+str(f.case),flush=True)
