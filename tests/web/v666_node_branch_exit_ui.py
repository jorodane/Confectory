"""원본 분기 반환 카드의 생성·선택·연결·저장과 실패 복구."""
import ast,copy,json,sys
from playwright.sync_api import sync_playwright,expect
import v666_node_branch_exit_fixture as e
n=e.n;x=e.x;f=e.f;feature=n.feature;graph=n.root;child=n.child;mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
helper=f.repo/'tests/web/v666_node_internal_ui.py';names={'original','panel','pending','restart','save','review','open_graph'};exec(compile(ast.Module(body=[r for r in ast.parse(helper.read_text()).body if isinstance(r,ast.FunctionDef) and r.name in names],type_ignores=[]),str(helper),'exec'))
def pending():return [(key,value) for key,value in f.pending()['blueprint'] if value.get('type')=='branch-exits']
def add(y,member=None):
 before=set(panel().locator('[data-bp-node^="$exit:"]').evaluate_all('(els)=>els.map(el=>el.dataset.bpNode)'));panel().locator('.bp-viewport').click(button='right',position={'x':700,'y':y});p=f.page.get_by_role('dialog',name='블루프린트 노드 검색',exact=True);p.locator('[data-resource-kind]').select_option('branch-exit');p.locator('[data-resource-branch-exit]').click();ids=panel().locator('[data-bp-node^="$exit:"]').evaluate_all('(els)=>els.map(el=>el.dataset.bpNode)');id=next(v for v in ids if v not in before)
 if member:select(id,member)
 return id
def card(id):return panel().locator('[data-bp-node="'+id+'"]')
def select(id,member):
 card(id).locator('[data-bp-branch-select]').click();f.page.get_by_role('listbox',name='기존 분기 선택',exact=True).locator('[data-branch-option="'+member+'"]').click()
def connect(port,id):
 panel().locator('[data-bp-node=body] .bp-port[data-side=out][data-port="'+port+'"]').click();card(id).locator('.bp-port[data-side=in]').click();a=panel().locator('[data-bp-node=body] .bp-port[data-side=out][data-port="'+port+'"]').bounding_box();b=card(id).locator('.bp-port[data-side=in]').bounding_box();assert abs(a['y']+a['height']/2-b['y']-b['height']/2)<2,(a,b)
def cell():return next(v for _,v in pending() if v['type']=='branch-exits')
try:
 f.start(0);f.invoke('select',{'id':feature});f.invoke('saveDraft',{});
 if mode!='draft':e.wrap()
 checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright() as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});open_graph();resize=panel().locator('[data-resize=se]').bounding_box();f.page.mouse.move(resize['x']+resize['width']/2,resize['y']+resize['height']/2);f.page.mouse.down();f.page.mouse.move(1740,1250,steps=12);f.page.mouse.up();f.idle();panel().locator('[data-bp-node=calculate] [data-internal-flow]').click();expect(panel().locator('[data-bp-node=body]')).to_be_visible();f.page.screenshot(path=str(f.case/'exit-before-create.png'),full_page=True)
  cancelled=add(240);card(cancelled).locator('[data-bp-remove]').click();assert not pending() and panel().locator('[data-bp-node^="$exit:"]').count()==0 and checkpoint.read_bytes()==before
  proceed=add(240);assert card(proceed).locator('[data-bp-branch-name]').input_value()=='';held=copy.deepcopy(pending());panel().locator('[data-bp-save]').click();f.idle();assert pending()==held and checkpoint.read_bytes()==before;original();f.checked('분기 선택/연결 없는 새 반환 카드는 입력을 보존하고 원자 Save를 거절한다')
  card(proceed).locator('[data-bp-branch-select]').click();f.page.keyboard.press('Escape');assert pending()==held and card(proceed).locator('[data-bp-branch-name]').input_value()=='';select(proceed,'next');connect('next',proceed);finish=add(460,'alternate');connect('case:alternate',finish);held=copy.deepcopy(pending());panel().locator('.bp-viewport').press('Control+z');assert json.loads(cell()['text'])['edges']!=json.loads(held[0][1]['text'])['edges'];panel().locator('.bp-viewport').press('Control+y');assert pending()==held;original();f.checked('원본 반환 카드의 기존 ID 선택·실행선 연결·Undo/Redo는 공개 계약과 원문을 바꾸지 않는다')
  panel().locator('[data-bp-node=body] [data-internal-code]').click();dialog=f.page.get_by_role('dialog',name='C# Script · body',exact=True);expect(dialog.locator('.bp-script-guide')).to_contain_text('바깥 반환 분기는');dialog.locator('[data-code-cancel]').click();assert pending()==held
  card(finish).locator('[data-bp-remove]').click();assert pending()==held and card(finish).is_visible();restart(1);assert pending()==held and card(finish).locator('[data-bp-branch-name]').input_value()=='Alternate';original();f.checked('연결 중 반환 카드 삭제는 거절하고 재시작에서도 선택 ID·실행선·입력을 보존한다')
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:panel().locator('[data-bp-save]').click();f.idle();assert pending()==held and checkpoint.read_bytes()==before;original()
   finally:checkpoint.chmod(0o600)
   restart(2);assert pending()==held
  if mode=='conflict':
   p=f.project/'Flow.node.json';p.write_bytes(x.physical[p]+b' ');x.physical[p]=p.read_bytes();panel().locator('[data-bp-save]').click();f.idle();assert pending()==held and checkpoint.read_bytes()==before;original();f.checked('원문 충돌은 종료점 계획 전체를 거절하고 늦은 입력과 기존 파일을 보존한다')
  else:
   if mode in ['loss','late']:
    applies=set();queries=set();lost=[];paused={}
    def interrupt(route):
     request=route.request.post_data_json
     if request.get('op')=='invoke' and request.get('endpoint')=='blueprint':
      action=request.get('input',{}).get('action')
      if action=='authorBatch':applies.add(request['requestId'])
      elif applies and action=='settledAuthorBatch':queries.add(request['requestId'])
     response=route.fetch();payload=response.json()
     if mode=='late' and not paused and any(r.get('ok') and r.get('requestId') in applies for r in payload.get('results',[])):paused.update(route=route,response=response);return
     for row in payload.get('results',[]):
      if mode=='loss' and row['requestId'] in applies|queries:rid=row['requestId'];lost.append(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
     route.fulfill(response=response,json=payload)
    f.page.route('**/api/request',interrupt);panel().locator('[data-bp-save]').click()
    for _ in range(1000):
     if paused or applies and any(r in queries for r in lost):break
     f.page.wait_for_timeout(30)
    assert len(applies)==1
    if mode=='late':
     assert paused;select(proceed,'alternate');select(finish,'next');assert card(proceed).locator('[data-bp-branch-name]').input_value()=='Alternate' and card(finish).locator('[data-bp-branch-name]').input_value()=='Continue';paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',interrupt);f.idle();later=json.loads(cell()['text']);assert later['exits'][proceed[6:]]['executionBranch']=='alternate' and later['exits'][finish[6:]]['executionBranch']=='next';restart(3);panel().locator('[data-bp-save]').click();f.idle();assert pending();save()
    else:
     assert any(r in queries for r in lost);f.page.unroute_all(behavior='wait');f.idle();restart(3);mark=len(f.traffic);save();assert not any(r.get('invoke',{}).get('input',{}).get('action')=='authorBatch' for r in f.traffic[mark:])
   else:
    if mode=='root':panel().locator('.bp-breadcrumbs button').first.click()
    save()
   assert not pending();original();r=review();r.locator('[data-reject]').click();expect(r).to_be_hidden();original();r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();e.run('exit-ui-confirm',swapped=mode=='late');stored=json.loads((f.project/'Flow.graph.json').read_text());outer=next(r for r in n.at(stored)['nodes'] if r['id']=='calculate');assert outer['executionEnum']==n.execution and n.at(stored)['edges']==n.at(n.graph)['edges'];body=outer['graph']['nodes'][0];record=json.loads((f.project/body['implementation']).read_text());assert record['source']==n.source and record['helpers']==n.helpers;restart(4);assert e.read()['diagnostics']['state']=='source-ready';f.checked('종료점 Save·Review 취소/Confirm·cold는 명시 ID만 반환하고 C# 원문·바깥 계약과 저장소를 보존한다')
  assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'branch-exit-final.png'),full_page=True);f.browser.close()
except Exception:
 try:f.page.screenshot(path=str(f.case/'branch-exit-failure.png'),timeout=5000)
 except Exception:pass
 raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False,indent=2));f.stop()
print('M11_BRANCH_EXIT_UI_FIXTURE '+str(f.case),flush=True)
