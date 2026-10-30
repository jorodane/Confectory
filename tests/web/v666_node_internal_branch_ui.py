"""실행 분기 원본 UI의 전환·편집·원자 Save와 실패·cold·Confirm."""
import ast,copy,json,pathlib,shutil,sys
from playwright.sync_api import sync_playwright,expect
import v666_node_internal_branch_fixture as n
x=n.x;f=n.f;feature=n.feature;graph=n.root;child=n.child;mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
helper=pathlib.Path(__file__).with_name('v666_node_internal_ui.py');names={'original','panel','pending','restart','save','review'};exec(compile(ast.Module(body=[row for row in ast.parse(helper.read_text()).body if isinstance(row,ast.FunctionDef) and row.name in names],type_ignores=[]),str(helper),'exec'))
def open_graph():
 f.idle()
 if not panel().is_visible():
  f.page.locator('#workspace').click(button='right',position={'x':1300,'y':300});f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.get_by_role('button',name='기능',exact=True).click();b.locator('[data-browser-control=object-query]').fill('Flow');b.locator('[data-browser-control=object-search]').click();b.locator('[data-object="'+feature+'"]').press('Enter');b.locator('[data-close]').first.click();f.idle();f.page.locator('[data-operation=feature-author-open]').first.click()

 if n.nested and not panel().locator('[data-bp-node=calculate]').count():panel().locator('[data-bp-node=frame] [data-internal-code]').click()
 expect(panel().locator('[data-bp-node=calculate]')).to_be_visible()
def code(text,cancel=False):
 panel().locator('[data-bp-node=body] [data-internal-code]').click();p=f.page.get_by_role('dialog',name='C# Script · body',exact=True);editor=p.locator('[data-code-source]');raw=editor.input_value()
 assert 'public static Result Execute(' in raw
 for arg in n.args:assert (arg.get('mode','')+' '+arg['type']+' '+arg['name']).strip() in raw
 for member in n.execution['members']:assert member['name']+' = '+str(member['value']) in raw
 assert p.locator('[data-code-region=enum]').count()==0
 # The inherited execution enum remains a protected declaration, not a data type editor.
 editor.evaluate('(el)=>{const at=el.value.indexOf("Alternate = 17");if(at<0)throw Error("enum not found");el.focus();el.setSelectionRange(at,at+14)}');f.page.keyboard.insert_text('Changed = 18');assert editor.input_value()==raw
 for region,value in [('body',text),('helpers',n.helpers.replace('EditDelta()=>0','EditDelta()=>1'))]:
  before=p.locator('[data-code-region='+region+']').text_content();editor.evaluate('(el,body)=>{const at=el.value.indexOf(body);if(at<0)throw Error("region not found");el.focus();el.setSelectionRange(at,at+body.length)}',before);f.page.keyboard.insert_text(value);assert value.replace("\r\n","\n") in editor.input_value()
 p.locator('[data-code-cancel]' if cancel else '[data-code-save]').click()

try:
 f.start(0);f.invoke('select',{'id':feature});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph();panel().locator('[data-bp-node=calculate] [data-internal-flow]').click();expect(panel().locator('[data-bp-node=body]')).to_be_visible();panel().locator('.bp-viewport').press('Control+z');expect(panel().locator('[data-bp-node=calculate]')).to_be_visible();panel().locator('.bp-viewport').press('Control+y');expect(panel().locator('[data-bp-node=body]')).to_be_visible();original();assert checkpoint.read_bytes()==before;f.checked('기존 실행 분기 동작의 내부 진입·Undo/Redo는 핀 역할·저장소·물리 원본을 변경하지 않는다')
  text=n.source.replace('+EditDelta();','+EditDelta()+1;');code(text,True);assert not pending();code(text);held=copy.deepcopy(pending());assert len(held)==1;restart(1);expect(panel().locator('[data-bp-node=body]')).to_be_visible();assert pending()==held;original();f.checked('C# 고정 선언의 실행 분기를 유지하며 본문 취소/편집·cold에서 사용자 입력과 원문을 보존한다')
  if mode=='project':
   other=f.case/'same IDs other project';shutil.copytree(f.project,other,ignore=shutil.ignore_patterns('.confectory'));f.pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(other/'project.cproj');f.start(10);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph();assert not pending();f.page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(x.manifest);f.start(11);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle();expect(panel().locator('[data-bp-node=body]')).to_be_visible();assert pending()==held;original();f.checked('동일 ID의 다른 프로젝트 왕복에서도 실행 분기 입력과 전환 대상이 섞이지 않는다')
  if mode not in ['late','loss-edit']:panel().locator('.bp-breadcrumbs button').first.click()
  if mode=='conflict':
   p=f.project/'Flow.node.json';p.write_bytes(x.physical[p]+b' ');x.physical[p]=p.read_bytes();panel().locator('[data-bp-save]').click();f.idle();assert pending()==held and checkpoint.read_bytes()==before;original();f.checked('원문 경합은 실행 분기 후보를 전체 미적용하고 입력과 기존 연결을 유지한다')
  else:
   if mode=='storage':
    checkpoint.chmod(0o400)
    try:panel().locator('[data-bp-save]').click();f.idle();assert pending()==held and checkpoint.read_bytes()==before;original()
    finally:checkpoint.chmod(0o600)
    restart(2);assert pending()==held;f.checked('checkpoint 실패 후 cold·재시도는 실행 분기 전환과 편집 입력을 잃지 않는다')
   if mode in ['loss','loss-edit']:
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
    assert len(applies)==1 and any(r in queries for r in lost) and pending()==held;f.page.unroute_all(behavior='wait');f.idle()
    if mode=='loss-edit':
     code(n.source.replace('+EditDelta();','+EditDelta()+2;'));later=copy.deepcopy(pending());assert '+2' in later[0][1]['text'];restart(3);mark=len(f.traffic);panel().locator('[data-bp-save]').click();f.idle();assert pending() and pending()[0][1]['text']==later[0][1]['text'];assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for r in f.traffic[mark:]);save();f.checked('성공 응답을 잃은 뒤의 새 본문 입력은 cold receipt 확인만으로 원본을 대응하고 명시한 다음 Save에서만 적용한다')
    else:
     restart(3);mark=len(f.traffic);save();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for r in f.traffic[mark:]);f.checked('실행 분기 저장·조회 응답 유실은 cold receipt로 확인하고 중복 래핑을 하지 않는다')
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
    assert paused and len(ids)==1;code(n.source.replace('+EditDelta();','+EditDelta()+2;'));paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',hold);f.idle();assert pending() and '+2' in pending()[0][1]['text'];restart(3);save();f.checked('저장 중 늦은 본문 입력은 실행 분기 선언을 유지하며 다음 Save로만 적용한다')
   else:save()
   assert not pending();original();r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();original();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();published=json.loads((f.project/'Flow.graph.json').read_text());outer=next(row for row in n.at(published)['nodes'] if row['id']=='calculate');before_node=next(row for row in n.at(n.graph)['nodes'] if row['id']=='calculate');assert outer['retainedCode']['definition']==before_node and outer['signature']==before_node['signature'] and outer['arguments']==before_node['arguments'];assert outer.get('forwardCallerStorage')==before_node.get('forwardCallerStorage') and outer['control']=='switch' and outer['executionEnum']==n.execution and outer['executionSource']=='body' and outer.get('branchOwner')==before_node.get('branchOwner') and n.at(published)['edges']==n.at(n.graph)['edges'];assert outer['graph']['profile']==n.graph['profile'];body=next(row for row in outer['graph']['nodes'] if row['id']=='body');assert body['control']=='switch' and body['executionEnum']==n.execution;stored=json.loads((f.project/body['implementation']).read_text());assert stored['source']==n.source.replace('+EditDelta();','+EditDelta()+'+str(2 if mode in ['late','loss-edit'] else 1)+';') and stored['helpers']==n.helpers.replace('EditDelta()=>0','EditDelta()=>1');assert all((f.project/name).read_bytes()==x.physical[f.project/name] for name in ['other.csbody','FlowBody.celem','chosen.node.json','fallback.node.json','after.node.json']);assert (f.project/'Flow.node.json').read_bytes()==x.physical[f.project/'Flow.node.json'];n.build('branch-ui-after',3 if mode in ['late','loss-edit'] else 2);f.checked('Review 취소/Confirm은 원문·실행 분기 ID/출구/바깥 연결을 보존하고 실제 반환/출력은 명시한 본문·helpers 편집만 반영한다');restart(4);assert n.read(n.child)['diagnostics']['state']=='source-ready';f.checked('Confirm 뒤 cold는 저장된 실행 분기 내부 흐름을 복원한다')
  assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'branch-internal-final.png'),full_page=True);f.browser.close()
except Exception:
 try:f.page.screenshot(path=str(f.case/'branch-internal-failure.png'),timeout=5000)
 except Exception:pass
 raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2));f.stop()
print('M11_BRANCH_UI_FIXTURE '+str(f.case),flush=True)
