"""whole-body 문맥 원본 UI의 전환·편집·원자 Save와 실패·cold·Confirm."""
import ast,copy,json,pathlib,shutil,sys,time
from playwright.sync_api import sync_playwright,expect
if '--copy' in sys.argv:import v666_node_internal_copy_context_fixture as n
else:import v666_node_internal_context_fixture as n
x=n.x;f=n.f;feature=n.feature;graph=n.root;child=n.child;node=getattr(n,'node','calculate');is_copy=hasattr(n,'owner');graph_file=getattr(n,'graph_file','Flow.graph.json');guard=getattr(n,'guard',f.project/'Flow.node.json');mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
helper=pathlib.Path(__file__).with_name('v666_node_internal_ui.py');names={'original','panel','pending','restart','save','review'};exec(compile(ast.Module(body=[row for row in ast.parse(helper.read_text()).body if isinstance(row,ast.FunctionDef) and row.name in names],type_ignores=[]),str(helper),'exec'))
def open_graph():
 f.idle()
 if not panel().is_visible():
  if is_copy:
   n.d.open_info();title=f.owner().locator('.object-title-name').bounding_box();box=f.owner().bounding_box();f.page.mouse.move(title['x']+5,title['y']+5);f.page.mouse.down();f.page.mouse.move(1780+title['x']-box['x']+5,80+title['y']-box['y']+5,steps=10);f.page.mouse.up();slot=f.owner().locator('[data-module-method="'+feature+'"]')
   if not slot.locator('[data-function-edit],[data-function-write-direct]').first.is_visible():f.owner().locator('[data-behavior-toggle="'+n.module+'"]').click()
   slot.locator('[data-function-edit],[data-function-write-direct]').first.click()
  else:
   f.page.locator('#workspace').click(button='right',position={'x':1300,'y':300});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.get_by_role('button',name='기능',exact=True).click();b.locator('[data-browser-control=object-query]').fill('Flow');b.locator('[data-browser-control=object-search]').click();b.locator('[data-object="'+feature+'"]').press('Enter');b.locator('[data-close]').first.click();f.idle();f.page.locator('[data-operation=feature-author-open]').first.click()
 expect(panel().locator('[data-bp-node="'+node+'"]')).to_be_visible()
if is_copy:
 def save():
  panel().locator('[data-bp-save]').click();deadline=time.monotonic()+90;observer=f.mount();snapshot=observer['state']
  try:
   while time.monotonic()<deadline:
    f.page.evaluate('async()=>await confectoryFlushPresentation()')
    update=f.raw({'op':'update','view':observer['view'],'scope':observer['scope']})
    assert not update.get('error'),update;snapshot=update.get('state') or snapshot;remaining=snapshot['presentation']['inputs']['blueprint']
    if not remaining and '저장 중' not in panel().locator('.bp-status').inner_text():break
    f.page.wait_for_timeout(250)
   assert not remaining,{'status':panel().locator('.bp-status').inner_text(),'remaining':remaining}
  finally:f.raw({'op':'dispose','view':observer['view']})
  f.idle();assert not pending();changes={r['id']:r for r in json.loads(checkpoint.read_text())['changes']};assert json.loads(changes[n.root]['draft'])['copySource']==n.graph['copySource']
def code(text,cancel=False):
 panel().locator('[data-bp-node=body] [data-internal-code]').click();p=f.page.get_by_role('dialog',name='C# Script · body',exact=True);editor=p.locator('[data-code-source]');raw=editor.input_value();body=p.locator('[data-code-region=body]').text_content()
 assert 'public '+n.signature['return']+' Invoke(' in raw
 for arg in n.args:assert (arg.get('mode','')+' '+arg['type']+' '+arg['name']).strip() in raw
 editor.evaluate('(el,body)=>{const at=el.value.indexOf(body);if(at<0)throw Error("body not found");el.focus();el.setSelectionRange(at,at+body.length)}',body);f.page.keyboard.insert_text(text);assert text.replace("\r\n","\n") in editor.input_value();p.locator('[data-code-cancel]' if cancel else '[data-code-save]').click()
try:
 f.start(0);f.invoke('select',{'id':n.owner if is_copy else feature});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':2300 if is_copy else 1800,'height':1700 if is_copy else 1400});open_graph();crumbs=panel().locator('.bp-breadcrumbs button').count();panel().locator('[data-bp-node="'+node+'"] [data-internal-flow]').click();expect(panel().locator('[data-bp-node=body]')).to_be_visible();panel().locator('.bp-viewport').press('Control+z');expect(panel().locator('[data-bp-node="'+node+'"] [data-internal-flow]')).to_be_enabled();panel().locator('.bp-viewport').press('Control+y');expect(panel().locator('[data-bp-node=body]')).to_be_visible();expect(panel().locator('.bp-breadcrumbs button')).to_have_count(crumbs+1);original();assert checkpoint.read_bytes()==before;f.checked('기존 whole-body 문맥 동작의 내부 진입·Undo/Redo는 핀 역할·저장소·물리 원본을 변경하지 않는다')
  text=n.source.replace('+proof','+proof+1');code(text,True);assert not pending();code(text);held=copy.deepcopy(pending());assert len(held)==1;restart(1);expect(panel().locator('[data-bp-node=body]')).to_be_visible();assert pending()==held;original();f.checked('C# 고정 선언의 whole-body 문맥을 유지하며 본문 취소/편집·cold에서 사용자 입력과 원문을 보존한다')
  if mode=='project':
   other=f.case/'same IDs other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory'));f.pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(other/'project.cproj');f.start(10);f.page=f.setup();f.page.set_viewport_size({'width':2300 if is_copy else 1800,'height':1700 if is_copy else 1400});open_graph();assert not pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(x.manifest);f.start(11);f.page=f.setup();f.page.set_viewport_size({'width':2300 if is_copy else 1800,'height':1700 if is_copy else 1400});f.idle();expect(panel().locator('[data-bp-node=body]')).to_be_visible();assert pending()==held;original();f.checked('동일 ID의 다른 프로젝트 왕복에서도 whole-body 문맥 입력과 전환 대상이 섞이지 않는다')
  if mode!='late':panel().locator('.bp-breadcrumbs button').first.click()
  if mode=='conflict':
   p=guard;p.write_bytes(x.physical[p]+b' ');x.physical[p]=p.read_bytes();panel().locator('[data-bp-save]').click();f.idle();assert pending()==held and checkpoint.read_bytes()==before;original();f.checked('원문 경합은 whole-body 문맥 후보를 전체 미적용하고 입력과 기존 연결을 유지한다')
  else:
   if mode=='storage':
    checkpoint.chmod(0o400)
    try:panel().locator('[data-bp-save]').click();f.idle();assert pending()==held and checkpoint.read_bytes()==before;original()
    finally:checkpoint.chmod(0o600)
    restart(2);assert pending()==held;f.checked('checkpoint 실패 후 cold·재시도는 whole-body 문맥 전환과 편집 입력을 잃지 않는다')
   if mode=='loss':
    applies=set();queries=set();lost=[]
    def interrupt(route):
     body=route.request.post_data_json
     if body.get('op')=='invoke' and body.get('endpoint')=='blueprint':
      action=body.get('input',{}).get('action')
      if action=='authorBatch':applies.add(body['requestId'])
      elif applies and action=='settledAuthorBatch':queries.add(body['requestId'])
     response=route.fetch();payload=response.json()
     for row in payload.get('results',[]):
      if row['requestId'] in applies|queries:rid=row['requestId'];lost.append(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
     route.fulfill(response=response,json=payload)
    f.page.route('**/api/request',interrupt);panel().locator('[data-bp-save]').click()
    for _ in range(1000):
     if applies and any(r in queries for r in lost):break
     f.page.wait_for_timeout(30)
    assert len(applies)==1 and any(r in queries for r in lost) and pending()==held;f.page.unroute_all(behavior='wait');restart(3);mark=len(f.traffic);save();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for r in f.traffic[mark:]);f.checked('whole-body 문맥 저장·조회 응답 유실은 cold receipt로 확인하고 중복 래핑을 하지 않는다')
   elif mode=='late':
    ids=set();paused={}
    def hold(route):
     body=route.request.post_data_json
     if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('action')=='authorBatch':ids.add(body['requestId'])
     response=route.fetch();payload=response.json()
     if not paused and any(row.get('ok') and row.get('requestId') in ids for row in payload.get('results',[])):paused.update(route=route,response=response);return
     route.fulfill(response=response)
    f.page.route('**/api/request',hold);panel().locator('[data-bp-save]').click()
    for _ in range(1000):
     if paused:break
     f.page.wait_for_timeout(30)
    assert paused and len(ids)==1;code(n.source.replace('+proof','+proof+2'));paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',hold);f.idle();assert pending() and '+2' in pending()[0][1]['text'];restart(3);save();f.checked('저장 중 늦은 본문 입력은 whole-body 문맥 선언을 유지하며 다음 Save로만 적용한다')
   else:save()
   assert not pending();original();r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();original();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();published=json.loads((f.project/graph_file).read_text());outer=next(row for row in published['nodes'] if row['id']==node);before_node=next(row for row in n.graph['nodes'] if row['id']==node);assert outer['retainedCode']['definition']==before_node and outer['signature']==before_node['signature'] and outer['arguments']==before_node['arguments'];assert bool(outer.get('forwardCallerStorage'))==any(a.get('mode') in ['ref','out'] for a in n.args);assert outer['graph']['profile']==n.graph['profile'];body=next(row for row in outer['graph']['nodes'] if row['id']=='body');assert body['implementationContext']==before_node['implementationContext'] and body['sourceIdentity']==before_node['sourceIdentity'];stored=json.loads((n.source_path(body) if is_copy else f.project/body['implementation']).read_text());assert stored['source']==n.source.replace('+proof','+proof+'+str(2 if mode=='late' else 1));assert all(p.read_bytes()==v for p,v in x.physical.items() if p!=f.project/graph_file);n.build('context-ui-after',2 if mode=='late' else 1);f.checked('Review 취소/Confirm은 원문·바깥 저장소 배정을 보존하고 실제 별칭/반환/출력은 명시한 편집만 반영한다');restart(4);assert n.read(n.child)['diagnostics']['state']=='source-ready';f.checked('Confirm 뒤 cold는 저장된 whole-body 문맥 내부 흐름을 복원한다')
   if is_copy and mode=='normal':
    if not panel().locator('[data-bp-node=body] [data-internal-code]:enabled').count():panel().locator('[data-bp-node="'+node+'"] [data-function-write-direct]').click()
    expect(panel().locator('[data-bp-node=body] [data-internal-code]')).to_be_enabled();expect(panel().locator('[data-bp-node=body] [data-internal-flow]')).to_be_enabled();f.idle()
    count=panel().locator('.bp-breadcrumbs button').count();published_files={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts};panel().locator('[data-bp-node=body] [data-internal-flow]').click();expect(panel().locator('.bp-breadcrumbs button')).to_have_count(count+1);expect(panel().locator('[data-bp-node=body] [data-internal-flow]')).to_be_disabled();panel().locator('.bp-viewport').press('Control+z');expect(panel().locator('[data-bp-node=body] [data-internal-flow]')).to_be_enabled();expect(panel().locator('.bp-breadcrumbs button')).to_have_count(count);assert all(p.read_bytes()==v for p,v in published_files.items());assert not pending();f.checked('확정한 copy의 같은 whole-body에서 다시 내부 진입·취소해도 receiver/원문/활성 소스를 유지한다')
  assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'context-internal-final.png'),full_page=True);f.browser.close()
except Exception:
 if is_copy:
  try:(f.case/'copy-context-ui-diagnostic.json').write_text(json.dumps({'data':n.read(n.child),'state':f.state()},ensure_ascii=False))
  except Exception as error:(f.case/'copy-context-ui-diagnostic-error.txt').write_text(str(error))
 try:f.page.screenshot(path=str(f.case/'context-internal-failure.png'),timeout=5000)
 except Exception:pass
 raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2));f.stop()
print('M11_CONTEXT_UI_FIXTURE '+str(f.case),flush=True)
