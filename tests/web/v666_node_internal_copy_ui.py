"""Same-contract saved copy Root/private internal-flow UI; no donor/override contract conversion."""
import ast,copy,json,pathlib,sys,time,shutil
from playwright.sync_api import sync_playwright,expect
import v666_node_internal_copy_fixture as n
f=n.f;x=n.x;feature=n.feature;graph=n.graph;mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
helper=pathlib.Path(__file__).with_name('v666_node_internal_ui.py');names={'panel','code','review'};exec(compile(ast.Module(body=[r for r in ast.parse(helper.read_text()).body if isinstance(r,ast.FunctionDef) and r.name in names],type_ignores=[]),str(helper),'exec'))
def pending():return [(k,v) for k,v in f.pending()['blueprint'] if v.get('type')=='source']
def original():n.original()
def open_parent():
 for part in n.parts:panel().locator('[data-bp-node="'+part+'"] [data-function-write-direct]').click()
 expect(panel().locator('[data-bp-node=calculate]')).to_be_visible()
def root_visible():expect(panel().locator('[data-bp-node="'+(n.parts[0] if n.parts else 'calculate')+'"]').first).to_be_visible()
def save():
 panel().locator('[data-bp-save]').click();deadline=time.monotonic()+90
 while time.monotonic()<deadline:
  f.page.wait_for_timeout(60)
  if not pending() and '저장 중' not in panel().locator('.bp-status').inner_text():break
 assert not pending(),panel().locator('.bp-status').inner_text();f.idle();rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']};assert json.loads(rows[n.graph]['draft'])['copySource']==n.provenance;assert json.loads(rows[n.leaf]['draft'])['source']==('return amount+9;' if mode=='late' else 'return amount+8;')
def restart(i):
 held=copy.deepcopy(pending());f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});f.idle();expect(panel()).to_be_visible();assert pending()==held
try:
 f.start(0);f.invoke('select',{'id':n.owner});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});n.d.open_info();title=f.owner().locator('.object-title-name').bounding_box();box=f.owner().bounding_box();f.page.mouse.move(title['x']+5,title['y']+5);f.page.mouse.down();f.page.mouse.move(1780+title['x']-box['x']+5,80+title['y']-box['y']+5,steps=10);f.page.mouse.up();slot=f.owner().locator('[data-module-method="'+feature+'"]')
  if not slot.locator('[data-function-edit],[data-function-write-direct]').first.is_visible():f.owner().locator('[data-behavior-toggle="'+n.module+'"]').click()
  slot.locator('[data-function-edit],[data-function-write-direct]').first.click();open_parent();expect(panel().locator('[data-bp-node=calculate] [data-internal-flow]')).to_be_enabled();panel().locator('[data-bp-node=calculate] [data-internal-flow]').click();expect(panel().locator('[data-bp-node=body]')).to_be_visible();panel().locator('.bp-viewport').press('Control+z');expect(panel().locator('[data-bp-node=calculate]')).to_be_visible();panel().locator('.bp-viewport').press('Control+y');expect(panel().locator('[data-bp-node=body]')).to_be_visible();assert checkpoint.read_bytes()==before;original();f.checked('저장된 copy의 기존 내부 진입과 Undo/Redo는 원문·출처·소유 배정·공개 계약을 보존한다')
  code('return amount+8;',True);assert not pending();code('return amount+8;');assert len(pending())==1;assert '|private:'+(n.path+'/' if n.path else '')+'calculate|' in pending()[0][0];held=copy.deepcopy(pending());original();restart(1);assert pending()==held;f.checked('copy 내부 C# 취소·편집·cold는 slot/frame 키와 늦은 입력의 소유 범위를 유지한다')
  if mode=='project':
   other=f.case/'same IDs other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory'));f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(other/'project.cproj');f.start(10);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});f.idle();assert not pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(n.f.manifest);f.start(11);f.page=f.setup();f.page.set_viewport_size({'width':2300,'height':1700});f.idle();expect(panel().locator('[data-bp-node=body]')).to_be_visible();assert pending()==held;original();f.checked('동일 namespace·copy ID·private 경로의 다른 프로젝트와 왕복해도 입력/owner/provenance를 섞지 않는다')
  if mode!='late':panel().locator('.bp-breadcrumbs button').first.click();root_visible();assert pending()
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:panel().locator('[data-bp-save]').click();f.idle();assert pending() and checkpoint.read_bytes()==before;original()
   finally:checkpoint.chmod(0o600)
   restart(2);f.checked('copy checkpoint 쓰기 실패와 재시작에서도 래핑/본문 입력은 미적용 상태로 남는다')
  if mode=='conflict':
   file=n.guard;file.write_bytes(n.physical[file]+b' ');n.physical[file]=file.read_bytes();panel().locator('[data-bp-save]').click();f.idle();assert checkpoint.read_bytes()==before and pending();original();f.checked('copy 원문 경합은 후보를 전체 거절하고 외부 수정과 미저장 본문을 보존한다')
  else:
   if mode in ['loss','late']:
    applies=set();queries=set();lost=[];paused={}
    def intercept(route):
     request=route.request.post_data_json
     if request.get('op')=='invoke' and request.get('endpoint')=='blueprint':
      if request.get('input',{}).get('action')=='authorBatch':applies.add(request['requestId'])
      elif applies and request.get('input',{}).get('action')=='settledAuthorBatch':queries.add(request['requestId'])
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
     assert paused;code('return amount+9;');paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',intercept);f.idle();assert pending() and pending()[0][1]['text']=='return amount+9;';restart(3);save()
    else:
     assert any(v in queries for v in lost);f.page.unroute_all(behavior='wait');f.idle();restart(3);mark=len(f.traffic);save();assert not any(v.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for v in f.traffic[mark:])
   else:save()
   assert not pending();original();r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();original();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();assert all(p.read_bytes()==v for p,v in n.physical.items() if p!=f.project/n.graph_path);published=json.loads((f.project/n.graph_path).read_text());expected=copy.deepcopy(n.prepared['graph']);n.at(expected)['nodes'][0]=copy.deepcopy(n.at(published)['nodes'][0]);assert published==expected;n.build('copy-ui-after',12 if mode=='late' else 11);
   if not panel().locator('[data-bp-node=body]').count():open_parent();panel().locator('[data-bp-node=calculate] [data-internal-flow]').click();expect(panel().locator('[data-bp-node=body]')).to_be_visible()
   restart(4);expect(panel().locator('[data-bp-node=body]')).to_be_visible();f.checked('Root Save/receipt·Review 취소/Confirm·cold는 같은 copy ID·출처와 실제 호출 결과를 유지한다')
  assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'m11-copy-final.png'),full_page=True);f.browser.close()
except Exception:
 try:f.page.screenshot(path=str(f.case/'m11-copy-failure.png'),timeout=5000)
 except Exception:pass
 raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2));f.stop()
print('M11_COPY_UI '+str(f.case),flush=True)
