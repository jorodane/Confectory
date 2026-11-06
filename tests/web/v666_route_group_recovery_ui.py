"""Explicit multi-next edits: checkpoint failures, cold receipts and late input stay distinct."""
import ast,copy,json,pathlib,sys,uuid,time,traceback
from playwright.sync_api import sync_playwright,expect
import v666_route_group_recovery_fixture as t
x=t.x;f=t.f;mode=sys.argv[3];_held={};_interceptor=None
p=pathlib.Path(__file__).with_name('v666_async_transition_ui.py');exec(compile(ast.Module(body=[n for n in ast.parse(p.read_text()).body if isinstance(n,ast.FunctionDef)and n.name in {'panel','open_graph'}],type_ignores=[]),str(p),'exec'))
def private():return f.pending()['blueprint']
def has(routes):return {v['node']:v['text']for _,v in private()if v.get('type')=='route'}==routes
def show():open_graph(t.feature,'body')
def connect(source,target):
 panel().locator('[data-bp-overview-node="'+source+'"]').click();port=panel().locator('.bp-port[data-node="'+source+'"][data-side=out][data-port=next]:not([data-kind=data])').first;port.focus();port.press('Enter');expect(port).to_have_attribute('aria-pressed','true');panel().locator('[data-bp-overview-node="'+target+'"]').click();port=panel().locator('.bp-port[data-node="'+target+'"][data-side=in]:not([data-kind=data])').first;port.focus();port.press('Enter')
def disconnect(source):
 port=panel().locator('[data-bp-link="route:'+source+'"]');port.focus();port.press('Delete')
def stage(routes,verify=True):
 if verify:show()
 if routes==t.selected:disconnect('first');connect('body','second');disconnect('second');connect('first','third');connect('second','first')
 else:disconnect('second');connect('body','first');disconnect('first');connect('second','third');connect('first','second')
 if verify:assert has(routes),private()
def save():show();panel().locator('[data-bp-save]').click();expect(f.page.locator('.brand')).to_be_enabled(timeout=120000)
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
 global _interceptor
 show();port=panel().locator('.bp-port[data-node=body][data-side=out][data-port=next]:not([data-kind=data])').first;port.focus();port.press('Enter');expect(port).to_have_attribute('aria-pressed','true');panel().locator('.bp-viewport').press('Escape');assert not private();connect('body','body');panel().locator('.bp-viewport').press('Escape');assert not private();connect('third','body');panel().locator('.bp-viewport').press('Escape');assert not private();connect('body','second');panel().locator('.bp-viewport').press('Escape');assert not private();stage(t.selected);x.original();assert checkpoint.read_bytes()==before;restart(1);assert has(t.selected)and t.current()==t.original;f.checked('self/cycle/occupied-destination rejection and explicit disconnect/reconnect preserve three selected routes across cold with unchanged IDs/contracts/C#')
 if mode=='conflict':
  data=t.read();f.invoke('blueprint',dict(action='route',id=t.graph,basis=data['basis'],node='third',port='next',to=''));f.invoke('saveDraft',{});held=checkpoint.read_bytes();peer=t.current();save();assert has(t.selected)and checkpoint.read_bytes()==held and t.current()==peer;x.original();restart(2);save();assert has(t.selected)and checkpoint.read_bytes()==held and t.current()==peer;x.original();f.checked('stale route group never overwrites peer checkpoint across cold/retry');return
 if mode in ['storage-new','unapplied-new']:
  checkpoint.chmod(0o400)
  try:save();assert has(t.selected)and checkpoint.read_bytes()==before and t.current()==t.original;x.original();(f.case/'storage-failure-inputs.json').write_text(json.dumps(private(),ensure_ascii=False))
  finally:checkpoint.chmod(0o600)
  if mode=='unapplied-new':
   f.page.set_viewport_size({'width':390,'height':844});panel().locator('[data-flow-node=body]').click();field=f.page.locator('.bp-flow-inspector:visible [data-flow-node-name]');field.fill('무관한 새 동작 이름');f.page.locator('.bp-flow-inspector:visible [data-flow-done]').click();f.page.set_viewport_size({'width':1800,'height':1400});held=checkpoint.read_bytes();save();assert has(t.selected)and any(v.get('type')=='rename'for _,v in private())and checkpoint.read_bytes()==held and t.current()==t.original;restart(2);save();assert has(t.selected)and any(v.get('type')=='rename'for _,v in private())and checkpoint.read_bytes()==held and t.current()==t.original;x.original();f.checked('failed group plus unrelated name retains all four inputs across cold without legacy partial route writes');return
  stage(t.late);restart(2);assert has(t.late)and t.current()==t.original;f.checked('failed route checkpoint retains entire private group/live graph; explicitly corrected group survives cold and retry')
 if mode in ['loss','late']:
  requests=set();queries=set();paused={};lost=[]
  def interrupt(route):
   body=route.request.post_data_json
   if body.get('op')=='invoke'and body.get('endpoint')=='blueprint':
    op=body.get('input',{}).get('action')
    if op=='authorBatch':requests.add(body['requestId'])
    elif requests and op=='settledAuthorBatch':queries.add(body['requestId'])
   response=route.fetch();payload=response.json()
   if mode=='late'and not paused and any(row.get('ok')and row.get('requestId')in requests for row in payload.get('results',[])):paused.update(route=route,response=response);_held.update(paused);return
   if mode=='loss':
    for row in payload.get('results',[]):
     if row['requestId']in requests|queries:rid=row['requestId'];lost.append(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
   route.fulfill(response=response,json=payload)
  _interceptor=interrupt;f.page.route('**/api/request',interrupt);panel().locator('[data-bp-save]').click();deadline=time.monotonic()+120
  while time.monotonic()<deadline:
   if paused or requests and any(r in queries for r in lost):break
   f.page.wait_for_timeout(30)
  assert len(requests)==1
  if mode=='late':assert paused;stage(t.late,False);paused['route'].fulfill(response=paused['response']);_held.clear();f.page.unroute('**/api/request',interrupt);f.idle();assert has(t.late)
  else:assert any(r in queries for r in lost);f.page.unroute('**/api/request',interrupt);f.idle();assert has(t.selected)
  restart(3);wanted=t.late if mode=='late'else t.selected;assert has(wanted);mark=len(f.traffic);save()
  if has(wanted):save()
  assert not private()and t.current()==wanted,(private(),t.current())
  writes=[row['invoke']['input']for row in f.traffic[mark:]if row.get('invoke',{}).get('endpoint')=='blueprint'and row['invoke']['input'].get('action')=='authorBatch']
  if mode=='loss':assert not writes,writes
  else:assert writes and all(write['edits']==t.edits(t.late)for write in writes),writes
  f.checked('route group '+mode+': exact durable receipt/new-route separation prevents replay or deletion of later edits')
 else:save();assert not private();x.original()
 wanted=t.late if mode in ['storage-new','late']else t.selected;assert t.current()==wanted
 if mode=='storage-new':
  state=f.invoke('draftHistory',{'action':'inspect'})['result']['result']
  if state['undo']['available']:history('undo');assert t.current()==t.original;history('redo');assert t.current()==t.original
  f.checked('explicitly restoring original route choices preserves execution; ordinary edge serialization history, if present, also restores the same choices')
 else:history('undo');assert t.current()==(t.selected if mode=='late'else t.original);history('redo');assert t.current()==wanted
 f.invoke('saveDraft',{});restart(4);assert not private()and t.current()==wanted;x.original();f.checked('whole-group shared draft Undo/Redo or corrected no-op cold preserves all C# sources and original contracts')
 r=review();r.locator('[data-reject]').click();x.original();r=review();p=f.project/t.graph_file;physical=p.read_bytes();held=checkpoint.read_bytes();p.write_bytes(physical+b' ')
 try:r.locator('#confirm').click();f.idle();assert p.read_bytes()==physical+b' 'and checkpoint.read_bytes()==held;assert all(path.read_bytes()==raw for path,raw in x.physical.items()if path!=p)
 finally:p.write_bytes(physical)
 if r.is_visible():r.locator('[data-reject]').click()
 r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();actual=json.loads(p.read_text());expected=t.after(wanted);key=lambda edge:(edge['from'],edge['port'],edge['to']);assert sorted(actual.pop('edges'),key=key)==sorted(expected.pop('edges'),key=key);assert actual==expected;assert all(path.read_bytes()==raw for path,raw in x.physical.items()if path!=p);x.build('explicit-route-group-execution',*t.result(wanted));restart(5);assert not private()and t.current()==wanted and not f.errors and not f.external,(private(),f.errors,f.external);f.page.screenshot(path=str(f.case/'route-group-final.png'),timeout=5000,full_page=True);f.checked('Review cancel/final physical CAS/new Confirm/actual .NET execution/cold change only explicitly selected next edges; C# bytes/IDs/data/ABI/profile unchanged')
 if mode=='normal':
  physical_now={p:p.read_bytes()for p in x.physical};data=t.read();q=dict(action='authorBatch',id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=t.edits(wanted));assert f.invoke('blueprint',q)['result']['result']['checkpointSaved'];raw=checkpoint.read_bytes();doc=json.loads(raw);assert not any(row['draft']!=row['original']for row in doc['changes']);g=next(row for row in doc['changes']if row['id']==t.graph);assert g['authorSaveReceipt']['ownedRoute']is True;restart(6);assert f.invoke('blueprint',{**q,'action':'settledAuthorBatch'})['result']['result']['settled'];assert checkpoint.read_bytes()==raw and all(p.read_bytes()==v for p,v in physical_now.items())and not private();f.checked('unchanged route group Save retains durable zero-dirty receipt across cold with no physical write')
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400})
  try:main()
  except Exception as error:
   (f.case/'failure-exception.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc(),errors=f.errors),ensure_ascii=False));print(traceback.format_exc(),flush=True)
   if _held:
    try:_held['route'].fulfill(response=_held['response'])
    except Exception:pass
    _held.clear()
   if _interceptor:
    try:f.page.unroute('**/api/request',_interceptor)
    except Exception:pass
   try:f.page.screenshot(path=str(f.case/'failure.png'),timeout=5000);f.page.evaluate('()=>Promise.race([confectoryFlushPresentation(),new Promise((_,reject)=>setTimeout(()=>reject(Error("capture deadline")),15000))])');(f.case/'failure-inputs.json').write_text(json.dumps(f.state()['presentation']['inputs']['blueprint'],ensure_ascii=False))
   except Exception as capture:(f.case/'failure-capture.json').write_text(json.dumps(dict(error=repr(capture)),ensure_ascii=False))
   raise
  f.browser.close()
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));f.stop()
print('ROUTE_GROUP_RECOVERY_FIXTURE',f.case,flush=True)
