"""Original node title editors: one atomic Save for existing ordinary display names."""
import ast,json,pathlib,sys,uuid,time,traceback
from playwright.sync_api import sync_playwright,expect
import v666_node_names_recovery_fixture as t
x=t.x;f=t.f;mode=sys.argv[3];text=t.selected;late=t.late;_held={};_interceptor=None
p=pathlib.Path(__file__).with_name('v666_async_transition_ui.py');names={'panel','open_graph'};exec(compile(ast.Module(body=[n for n in ast.parse(p.read_text()).body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),str(p),'exec'))
def private():return f.pending()['blueprint']
def has(names):return all(any(v.get('type')=='rename'and v.get('node')==node and v.get('text')==value for _,v in private())for node,value in names.items())
def show():f.page.set_viewport_size({'width':1800,'height':1400});open_graph(t.feature,'body')
def stage(names,verify=True,undo=False):
 if verify:show()
 f.page.set_viewport_size({'width':390,'height':844})
 for node,value in names.items():
  panel().locator('[data-flow-node="'+node+'"]').click();field=f.page.locator('.bp-flow-inspector:visible [data-flow-node-name]');original=field.input_value();field.press('Control+a');f.page.keyboard.insert_text(value)
  if undo:field.press('Control+z');expect(field).to_have_value(original);field.press('Control+Shift+z');expect(field).to_have_value(value)
  f.page.locator('.bp-flow-inspector:visible [data-flow-done]').click()
 f.page.set_viewport_size({'width':1800,'height':1400})
 if verify:assert has(names)
def save():show();panel().locator('[data-bp-save]').click();expect(f.page.locator('.brand')).to_be_enabled(timeout=120000)
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
 stage(text,undo=True);assert has(text)and t.current()==t.original and checkpoint.read_bytes()==before;x.original();restart(1);assert has(text)and t.current()==t.original;f.checked('original title inspectors/native Undo/Redo retain both exact private names across cold without live/source changes')
 if mode=='conflict':
  data=t.read();peer={**t.original,'after':'동료가 저장한 후속 이름'};f.invoke('blueprint',dict(action='rename',id=t.graph,basis=data['basis'],node='after',text=peer['after']));f.invoke('saveDraft',{});held=checkpoint.read_bytes();save();assert has(text)and checkpoint.read_bytes()==held and t.current()==peer;x.original();restart(2);save();assert has(text)and checkpoint.read_bytes()==held and t.current()==peer;x.original();f.checked('stale name group never overwrites a peer checkpoint across cold/retry');return
 if mode in ['storage-new','unapplied-new']:
  checkpoint.chmod(0o400)
  try:save();assert has(text)and checkpoint.read_bytes()==before and t.current()==t.original;x.original();(f.case/'storage-failure-inputs.json').write_text(json.dumps(private(),ensure_ascii=False))
  finally:checkpoint.chmod(0o600)
  if mode=='unapplied-new':
   panel().locator('[data-bp-overview-node="$exit:return"]').click();panel().locator('[data-bp-node="$exit:return"] [data-exit-value]').click();q=f.page.get_by_role('dialog',name='핀 값 선택').get_by_role('searchbox',name='값 검색');q.fill('99');q.press('Enter');held=checkpoint.read_bytes();save();assert has(text)and sum(bool(v.get('type'))for _,v in private())==3 and checkpoint.read_bytes()==held and t.current()==t.original;restart(2);save();assert has(text)and sum(bool(v.get('type'))for _,v in private())==3 and checkpoint.read_bytes()==held and t.current()==t.original;x.original();f.checked('extra root input preserves all three cells and original failed attempt across cold without legacy live edits');return
  stage(late);restart(2);assert has(late)and t.current()==t.original;x.original();f.checked('failed name checkpoint preserves both inputs/live/originals; corrected names survive cold explicit retry')
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
  else:assert writes and all(w['edits']==t.edits(late)for w in writes)
  f.checked('node names '+mode+': exact receipt separates late names without replaying earlier names or other fields')
 else:save();assert not has(text)and not has(late);x.original()
 selected=late if mode in ['storage-new','late']else text;assert t.current()==selected;history('undo');assert t.current()==(text if mode=='late'else t.original);history('redo');assert t.current()==selected;f.invoke('saveDraft',{});restart(4);assert not private()and t.current()==selected;x.original();f.checked('shared name Undo/Redo/cold moves all names together with identical source/IDs/contracts/connections')
 r=review();r.locator('[data-reject]').click();x.original();r=review();p=f.project/t.graph_file;physical=p.read_bytes();held=checkpoint.read_bytes();p.write_bytes(physical+b' ')
 try:r.locator('#confirm').click();f.idle();assert p.read_bytes()==physical+b' 'and checkpoint.read_bytes()==held;assert all(path.read_bytes()==raw for path,raw in x.physical.items()if path!=p)
 finally:p.write_bytes(physical)
 if r.is_visible():r.locator('[data-reject]').click()
 r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();t.confirmed(selected);x.build('ordinary-node-names-execution',*t.expected);restart(5);assert not private()and t.current()==selected and not f.errors and not f.external,(private(),f.errors,f.external);f.page.screenshot(path=str(f.case/'node-names-final.png'),timeout=5000,full_page=True);f.checked('Review cancel/final graph CAS/new Confirm/actual .NET execution/cold changes only display names; C#/caller bytes, IDs, ABI, values, edges and profile stay fixed')
 if mode=='normal':
  physical_now={p:p.read_bytes()for p in x.physical};data=t.read();q=dict(action='authorBatch',id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=t.edits(selected));assert f.invoke('blueprint',q)['result']['result']['checkpointSaved'];raw=checkpoint.read_bytes();doc=json.loads(raw);assert not any(u['draft']!=u['original']for u in doc['changes']);g=next(u for u in doc['changes']if u['id']==t.graph);assert g['authorSaveReceipt']['ownedRename']is True;restart(6);assert f.invoke('blueprint',{**q,'action':'settledAuthorBatch'})['result']['result']['settled'];assert checkpoint.read_bytes()==raw and all(p.read_bytes()==v for p,v in physical_now.items());assert not private();f.checked('no-op names Save preserves durable ownedRename receipt across cold with zero dirty and no physical writes')
try:
 f.start(0);f.invoke('select',dict(id=t.feature));f.invoke('saveDraft',{});checkpoint=t.checkpoint();before=checkpoint.read_bytes()
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
print('NODE_NAMES_RECOVERY_FIXTURE',f.case,flush=True)
