"""Root return display-position Save: fixed positional ABI, explicit remap and late-order separation."""
import ast,copy,json,pathlib,sys,uuid,time,traceback
from playwright.sync_api import sync_playwright,expect
import v666_root_return_position_recovery_fixture as t
x=t.x;f=x.f;mode=sys.argv[3];text=t.selected;late=t.late_order;_held={};_interceptor=None
p=pathlib.Path(__file__).with_name('v666_async_transition_ui.py');names={'panel','open_graph'};exec(compile(ast.Module(body=[n for n in ast.parse(p.read_text()).body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),str(p),'exec'))
def private():return f.pending()['blueprint']
def has(order):return any(v.get('type')=='root-parameters'and json.loads(v['text'])['outputOrder']==order for _,v in private())
def show():open_graph(t.feature,'body')
def displayed():return panel().locator('[data-output-entry-id]').evaluate_all('(xs)=>xs.map(x=>x.dataset.outputEntryId)')
def stage(order,verify=True):
 if verify:show()
 for _ in range(len(order)):
  actual=displayed()
  if actual==order:break
  row=panel().locator('[data-output-entry-id=return]');row.focus();row.press('Alt+ArrowUp'if actual.index('return')>order.index('return')else'Alt+ArrowDown')
 assert displayed()==order
 if verify:assert has(order)
def save():show();panel().locator('[data-bp-save]').click();expect(f.page.locator('.brand')).to_be_enabled(timeout=120000)
def canvas_history(direction):
 for _ in range(abs(t.original_order.index('return')-text.index('return'))):
  canvas=panel().locator('.bp-viewport');canvas.focus();canvas.press('Control+z'if direction=='undo'else'Control+y')
def restart(i):
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle();show()
def history(direction):
 state=f.invoke('draftHistory',{'action':'inspect'})['result']['result'];assert state[direction]['available'],state;assert f.invoke('draftHistory',{'action':direction,'token':state[direction]['token']})['result']['result']['accepted'];x.original()
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
 stage(text);canvas_history('undo');assert not private()and displayed()==t.original_order and t.current()==t.original_order;canvas_history('redo');assert has(text)and displayed()==text;x.original();assert checkpoint.read_bytes()==before
 if mode!='storage-new':restart(1)
 assert has(text)and displayed()==text and t.current()==t.original_order;f.checked('original root return display position editing/local Undo/Redo preserves selected position with unchanged positional input/output types/modes and caller and physical sources; cold recovery is checked before or after the failure path')
 if mode=='conflict':
  data=t.read();f.invoke('blueprint',dict(action='rootParameters',id=t.graph,basis=data['basis'],plan=json.dumps(t.plan(late))));f.invoke('saveDraft',{});held=checkpoint.read_bytes();save();assert has(text)and checkpoint.read_bytes()==held and t.current()==late;x.original();restart(2);save();assert has(text)and checkpoint.read_bytes()==held and t.current()==late;x.original();f.checked('stale root return display position never overwrites peer root-group checkpoint across restart/retry');return
 if mode in ['storage-new','unapplied-new']:
  checkpoint.chmod(0o400)
  try:save();assert has(text)and checkpoint.read_bytes()==before and t.current()==t.original_order;x.original();(f.case/'storage-failure-inputs.json').write_text(json.dumps(private(),ensure_ascii=False))
  finally:checkpoint.chmod(0o600)
  if mode=='unapplied-new':
   f.page.set_viewport_size({'width':390,'height':844});panel().locator('[data-flow-node=body]').click();field=f.page.locator('.bp-flow-inspector:visible [data-flow-node-name]');field.fill('무관한 새 동작 이름');f.page.locator('.bp-flow-inspector:visible [data-flow-done]').click();f.page.set_viewport_size({'width':1800,'height':1400});held=checkpoint.read_bytes();save();assert has(text)and any(v.get('type')=='rename'and v.get('text')=='무관한 새 동작 이름'for _,v in private())and sum(bool(v.get('type'))for _,v in private())==2 and checkpoint.read_bytes()==held and t.current()==t.original_order;restart(2);save();assert has(text)and any(v.get('type')=='rename'and v.get('text')=='무관한 새 동작 이름'for _,v in private())and sum(bool(v.get('type'))for _,v in private())==2 and checkpoint.read_bytes()==held and t.current()==t.original_order;x.original();f.checked('unapplied root return position plus unrelated display name retains both inputs across cold and never runs legacy live root/graph edits');return
  attempts=[v for _,v in private()if v.get('kind')=='author-attempt'];assert len(attempts)==1
  canvas_history('undo');assert not any(v.get('type')for _,v in private())and displayed()==t.original_order and [v for _,v in private()if v.get('kind')=='author-attempt']==attempts
  mark=len(f.traffic);save();assert not any(v.get('type')for _,v in private())and checkpoint.read_bytes()==before and t.current()==t.original_order
  assert not any(row.get('invoke',{}).get('endpoint')=='blueprint'and row['invoke']['input'].get('action')=='authorBatch'for row in f.traffic[mark:])
  canvas_history('redo');assert has(text);stage(late);restart(2);assert has(late)and displayed()==late and t.current()==t.original_order;f.checked('failed root checkpoint keeps private order/live graph and retry journal; Undo does not replay cancelled order, Redo/corrected order cold retry preserve all sources')
 if mode in ['loss','late']:
  requests=set();queries=set();paused={};lost=[]
  def interrupt(route):
   body=route.request.post_data_json
   if body.get('op')=='invoke'and body.get('endpoint')=='blueprint':
    op=body.get('input',{}).get('action')
    if op=='authorBatch':requests.add(body['requestId'])
    elif requests and op=='settledAuthorBatch':queries.add(body['requestId'])
   response=route.fetch();payload=response.json()
   if mode=='late'and not paused and any(r.get('ok')and r.get('requestId')in requests for r in payload.get('results',[])):paused.update(route=route,response=response);_held.update(paused);return
   if mode=='loss':
    for row in payload.get('results',[]):
     if row['requestId']in requests|queries:rid=row['requestId'];lost.append(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
   route.fulfill(response=response,json=payload)
  _interceptor=interrupt;f.page.route('**/api/request',interrupt);panel().locator('[data-bp-save]').click()
  deadline=time.monotonic()+120
  while time.monotonic()<deadline:
   if paused or requests and any(r in queries for r in lost):break
   f.page.wait_for_timeout(30)
  assert len(requests)==1
  if mode=='late':assert paused;stage(late,False);paused['route'].fulfill(response=paused['response']);_held.clear();f.page.unroute('**/api/request',interrupt);f.idle();assert has(late)and not has(text)
  else:assert any(r in queries for r in lost);f.page.unroute('**/api/request',interrupt);f.idle();assert has(text)
  restart(3);wanted=late if mode=='late'else text;assert has(wanted);mark=len(f.traffic);save()
  if has(wanted):save()
  assert not has(wanted)and t.current()==wanted
  writes=[r['invoke']['input']for r in f.traffic[mark:]if r.get('invoke',{}).get('endpoint')=='blueprint'and r['invoke']['input'].get('action')=='authorBatch']
  if mode=='loss':assert not writes,writes
  else:assert writes and all(e['definition']==t.plan(late)for w in writes for e in w['edits'])
  f.checked('root return position '+mode+': exact receipt/new-order separation, no replay of earlier order or type/arity/mode/return change')
 else:save();assert not has(text)and not has(late);x.original()
 selected=late if mode in ['storage-new','late']else text;assert t.current()==selected;history('undo');assert t.current()==(text if mode=='late'else t.original_order);history('redo');assert t.current()==selected;f.invoke('saveDraft',{});restart(4);assert not private()and t.current()==selected and displayed()==selected;x.original();f.checked('shared root-return-position Undo/Redo/cold keeps grouped declarations and C# bytes unchanged')
 r=review();r.locator('[data-reject]').click();x.original();r=review();p=f.project/t.graph_file;physical=p.read_bytes();held=checkpoint.read_bytes();p.write_bytes(physical+b' ')
 try:r.locator('#confirm').click();f.idle();assert p.read_bytes()==physical+b' 'and checkpoint.read_bytes()==held;assert all(path.read_bytes()==raw for path,raw in x.physical.items()if path!=p)
 finally:p.write_bytes(physical)
 if r.is_visible():r.locator('[data-reject]').click()
 r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();expected=t.after(selected);assert json.loads(p.read_text())==expected['graph'];assert (f.project/'Pair.celem').read_text()==expected['function'] and (f.project/'PairBody.celem').read_text()==expected['implementation'];assert all(path.read_bytes()==raw for path,raw in x.physical.items()if path.name not in {t.graph_file,'Pair.celem','PairBody.celem'});x.build('ordinary-root-return-position-execution',*t.expected);restart(5);assert not private()and t.current()==selected and displayed()==selected and not f.errors and not f.external,(private(),f.errors,f.external);f.page.screenshot(path=str(f.case/'root-return-position-final.png'),timeout=5000,full_page=True);f.checked('Review cancel/final graph CAS/new Confirm/actual .NET execution/cold alter only root return display position; original C# bytes, positional ABI, IDs, edges, values and profile remain identical')
 if mode=='normal':
  physical_now={p:p.read_bytes()for p in x.physical};data=t.read();q=dict(action='authorBatch',id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=[dict(action='rootParameters',node='$root',definition=t.plan(selected))]);assert f.invoke('blueprint',q)['result']['result']['checkpointSaved'];raw=checkpoint.read_bytes();doc=json.loads(raw);assert not any(u['draft']!=u['original']for u in doc['changes']);g=next(u for u in doc['changes']if u['id']==t.graph);assert g['authorSaveReceipt']['ownedRootOutputOrder']is True;assert set(g['rootContractGroup'])=={t.feature,t.n+'PairBody',t.graph} and set(g['rootContractGroup'])<={u['id']for u in doc['changes']};restart(6);assert f.invoke('blueprint',{**q,'action':'settledAuthorBatch'})['result']['result']['settled'];assert checkpoint.read_bytes()==raw and all(p.read_bytes()==v for p,v in physical_now.items());assert not private();f.checked('unchanged root-return-position Save preserves complete three-member root group and durable receipt with zero dirty files; cold settles without physical writes')
  data=t.read();q=dict(action='authorBatch',id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=[dict(action='source',node='body',text=t.original_source)]);assert f.invoke('blueprint',q)['result']['result']['checkpointSaved'];raw=checkpoint.read_bytes();doc=json.loads(raw);g=next(u for u in doc['changes']if u['id']==t.graph);assert g['authorSaveReceipt']['ownedSource']is True and set(g['rootContractGroup'])<={u['id']for u in doc['changes']};restart(7);assert f.invoke('blueprint',{**q,'action':'settledAuthorBatch'})['result']['result']['settled']and t.current()==selected and not private()and all(p.read_bytes()==v for p,v in physical_now.items());f.checked('a later unchanged ordinary C# Save retains the complete multi-input zero-dirty root group and receipt across cold')
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
print('ROOT_RETURN_POSITION_RECOVERY_FIXTURE',f.case,flush=True)
