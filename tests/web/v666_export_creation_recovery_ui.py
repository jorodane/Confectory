"""Create/value/connect one export before first Save; preserve pending plan and late value."""
import ast,copy,json,pathlib,sys
from playwright.sync_api import sync_playwright,expect
import v666_export_creation_recovery_fixture as t
x=t.x;f=x.f;mode=sys.argv[3];node=None;text='{"constant":37}';late='{"constant":41}'
helper=pathlib.Path(__file__).with_name('v666_async_transition_ui.py');names={'panel','open_graph'}
exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),str(helper),'exec'))
def private():return f.pending()['blueprint']
def has(value):return any(v.get('node')==node and v.get('type')=='argument:value'and v.get('text')==value for _,v in private())
def created():return any(v.get('node')==node and v.get('type')=='export-create'for _,v in private())
def show():open_graph(t.feature,'body')
def menu():
 box=panel().locator('.bp-viewport').bounding_box();panel().locator('.bp-viewport').click(button='right',position={'x':box['width']*.85,'y':box['height']*.9});m=f.page.get_by_role('dialog',name='블루프린트 노드 검색');m.locator('[data-resource-kind]').select_option('export');return m
def value(value,verify=True):
 panel().locator('[data-bp-overview-node="'+node+'"]').click();panel().locator('[data-bp-node="'+node+'"] [data-exit-value]').click();q=f.page.get_by_role('dialog',name='핀 값 선택').get_by_role('searchbox',name='값 검색');q.fill(str(json.loads(value)['constant']));q.press('Enter')
 if verify:assert has(value)
def connect(start,end):
 panel().locator('[data-bp-overview-node="'+start+'"]').click();panel().locator('[data-bp-node="'+start+'"] .bp-exec-line-out[data-port=next]').click();panel().locator('[data-bp-overview-node="'+end+'"]').click();panel().locator('[data-bp-node="'+end+'"] .bp-exec-header-in').click()
def stage():
 global node
 show();menu().press('Escape');assert not private();menu().locator('[data-resource-output=spare]').click();cells=private();node=next(v['node']for _,v in cells if v['type']=='export-create');assert node.startswith('export_')and len(cells)==1
 canvas=panel().locator('.bp-viewport');canvas.focus();canvas.press('Control+z');assert not private();canvas=panel().locator('.bp-viewport');canvas.focus();canvas.press('Control+y');assert created()
 value(text);link=panel().locator('[data-bp-link="route:body"]');link.focus();link.press('Delete');connect(node,'publish');connect('body',node);cells=private();assert len(cells)==4 and {v['type']for _,v in cells}=={'export-create','argument:value','route'};snapshot=copy.deepcopy(cells);canvas=panel().locator('.bp-viewport');canvas.focus();canvas.press('Control+z');assert private()==snapshot;canvas=panel().locator('.bp-viewport');canvas.focus();canvas.press('Control+y');assert private()==snapshot
 return node
def save():show();panel().locator('[data-bp-save]').click();f.idle()
def restart(i):
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle();show()
def history(direction):
 state=f.invoke('draftHistory',{'action':'inspect'})['result']['result'];assert state[direction]['available'];assert f.invoke('draftHistory',{'action':direction,'token':state[direction]['token']})['result']['result']['accepted'];x.original()
def review():
 show();panel().locator('[data-bp-complete]').click();f.idle()
 if f.page.locator('#review-creation').is_visible():f.page.locator('#review-creation').click();f.idle()
 f.page.locator('.window[data-key=review]:visible,.window[data-key=targets]:visible').first.wait_for(state='visible',timeout=90000);targets=f.page.locator('.window[data-key=targets]')
 if targets.is_visible():targets.locator('[data-target-choice]').select_option('portable');targets.locator('[data-close]').click();panel().locator('[data-bp-complete]').click();f.idle()
 r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=90000)
 if r.locator('[data-review-advanced]').is_visible():r.locator('[data-review-advanced]').click()
 if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
 return r
def main():
 stage();assert t.current(node)is None;x.original();assert checkpoint.read_bytes()==before;restart(1);assert created()and has(text)and t.current(node)is None;f.checked('existing canvas creation Undo/Redo precedes value/connections; later inputs block older local Undo and retain exact ID/four cells across cold without physical writes')
 if mode=='conflict':
  data=t.read();f.invoke('blueprint',dict(action='outputNodes',id=t.graph,basis=data['basis'],edits=[dict(kind='value',node='keep',valueJson=late)]));f.invoke('saveDraft',{});held=checkpoint.read_bytes();save();assert created()and has(text)and checkpoint.read_bytes()==held and t.current(node)is None;x.original();restart(2);save();assert created()and has(text)and t.current(node)is None and checkpoint.read_bytes()==held;x.original();f.checked('stale creation plan never overwrites peer checkpoint or allocates another ID across cold/retry');return
 if mode in ['storage-new','unapplied-new']:
  checkpoint.chmod(0o400)
  try:save();assert created()and has(text)and checkpoint.read_bytes()==before and t.current(node)is None;x.original();(f.case/'storage-failure-inputs.json').write_text(json.dumps(private(),ensure_ascii=False))
  finally:checkpoint.chmod(0o600)
  if mode=='unapplied-new':
   panel().locator('[data-bp-overview-node=keep]').click();panel().locator('[data-bp-node=keep] [data-exit-value]').click();q=f.page.get_by_role('dialog',name='핀 값 선택').get_by_role('searchbox',name='값 검색');q.fill('41');q.press('Enter');held=checkpoint.read_bytes();save();assert created()and has(text)and sum(bool(v.get('type'))for _,v in private())==5 and any(v.get('kind')=='author-attempt'for _,v in private()) and checkpoint.read_bytes()==held and t.current(node)is None;restart(2);save();assert created()and has(text)and sum(bool(v.get('type'))for _,v in private())==5 and any(v.get('kind')=='author-attempt'for _,v in private()) and t.current(node)is None and checkpoint.read_bytes()==held;x.original();f.checked('unapplied creation with unrelated input fails closed and keeps all five cells across cold instead of live structural fallback');return
  value(late);restart(2);assert created()and has(late)and t.current(node)is None;f.checked('failed creation checkpoint keeps graph/physical originals and exact ID; corrected new-node value survives cold for explicit retry')
 if mode in ['loss','late']:
  requests=set();queries=set();paused={};lost=[]
  def interrupt(route):
   body=route.request.post_data_json
   if body.get('op')=='invoke'and body.get('endpoint')=='blueprint':
    op=body.get('input',{}).get('action')
    if op=='authorBatch':requests.add(body['requestId'])
    elif requests and op=='settledAuthorBatch':queries.add(body['requestId'])
   response=route.fetch();payload=response.json()
   if mode=='late'and not paused and any(r.get('ok')and r.get('requestId')in requests for r in payload.get('results',[])):paused.update(route=route,response=response);return
   if mode=='loss':
    for row in payload.get('results',[]):
     if row['requestId']in requests|queries:rid=row['requestId'];lost.append(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
   route.fulfill(response=response,json=payload)
  f.page.route('**/api/request',interrupt);panel().locator('[data-bp-save]').click()
  for _ in range(1000):
   if paused or requests and any(r in queries for r in lost):break
   f.page.wait_for_timeout(30)
  assert len(requests)==1
  if mode=='late':assert paused;value(late,False);paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',interrupt);f.idle();assert has(late)and not created()
  else:assert any(r in queries for r in lost);f.page.unroute_all(behavior='wait');f.idle();assert created()and has(text)
  restart(3);assert has(late)if mode=='late'else created()and has(text);mark=len(f.traffic);save()
  if created()or has(late)or has(text):save()
  assert not created()and not has(late)and not has(text)and t.current(node)
  writes=[r['invoke']['input']for r in f.traffic[mark:]if r.get('invoke',{}).get('endpoint')=='blueprint'and r['invoke']['input'].get('action')=='authorBatch']
  if mode=='loss':assert not writes,writes
  else:assert writes and all(e['definition']['edits']==[dict(kind='value',node=node,valueJson=late)]for w in writes for e in w['edits'])
  f.checked('export creation '+mode+': receipt verifies existing new ID; retry never recreates or rewires; late value is separate')
 else:save();assert not created()and not has(late)and not has(text)and t.current(node);x.original()
 selected=41 if mode in ['late','storage-new']else 37;history('undo')
 if mode=='late':assert t.current_value(node)=={'constant':37};history('undo')
 assert t.current(node)is None;history('redo');assert t.current_value(node)=={'constant':41 if mode=='storage-new'else 37}
 if mode=='late':history('redo')
 assert t.current_value(node)=={'constant':selected};f.invoke('saveDraft',{});restart(4);assert not private()and t.current(node);x.original();f.checked('shared history atomically removes/restores new export and both routes, with independent late-value Undo and exact cold restoration')
 r=review();r.locator('[data-reject]').click();x.original();r=review();p=f.project/t.graph_file;physical=p.read_bytes();held=checkpoint.read_bytes();p.write_bytes(physical+b' ')
 try:r.locator('#confirm').click();f.idle();assert p.read_bytes()==physical+b' 'and checkpoint.read_bytes()==held;assert all(path.read_bytes()==raw for path,raw in x.physical.items()if path!=p)
 finally:p.write_bytes(physical)
 if r.is_visible():r.locator('[data-reject]').click()
 r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();assert json.loads(p.read_text())==t.after(node,selected);assert all(path.read_bytes()==raw for path,raw in x.physical.items()if path!=p);x.build('ordinary-export-creation-execution',*t.expected(selected));restart(5);assert not private()and t.current(node)and not f.errors and not f.external,(private(),f.errors,f.external);f.page.screenshot(path=str(f.case/'export-creation-final.png'),timeout=5000,full_page=True);f.checked('Review cancel/final physical CAS/new Confirm/actual .NET execution/cold preserve original code, contracts, profile, remaining nodes and outputs')
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400})
  try:main()
  except Exception:
   (f.case/'failure-inputs.json').write_text(json.dumps(private(),ensure_ascii=False));f.page.screenshot(path=str(f.case/'failure.png'),timeout=5000);raise
  f.browser.close()
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));f.stop()
print('EXPORT_CREATION_RECOVERY_FIXTURE',f.case,flush=True)
