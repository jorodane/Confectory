"""Original create/describe/write/connect UI, atomic failure and receipt recovery."""
import ast,copy,json,pathlib,sys,time,traceback
from playwright.sync_api import sync_playwright,expect
import v666_direct_creation_recovery_fixture as t
x=t.x;f=t.f;mode=sys.argv[3];node=None
_observe=f.observe;_save_timings=[];_held={};_interceptor=None
def timed_observe(response):
 before=len(f.traffic);_observe(response)
 for row in f.traffic[before:]:row['observedAtSeconds']=time.monotonic()
f.observe=timed_observe
helper=pathlib.Path(__file__).with_name('v666_async_transition_ui.py');names={'panel','open_graph'}
exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),str(helper),'exec'))
def private():return f.pending()['blueprint']
def created():return any(v.get('type')=='create'and v.get('node')==node for _,v in private())
def has(value):return any(v.get('type')=='source'and v.get('node')==node and v.get('text')==value for _,v in private())
def show():open_graph(t.feature,'body')
def focus(id):panel().locator('[data-bp-overview-node="'+id+'"]').click()
def value(text,verify=True):
 focus(node);panel().locator('[data-bp-node="'+node+'"] [data-internal-code]').click();d=f.page.locator('.bp-script-dialog');expect(d).to_be_visible();field=d.locator('[data-code-source]');old=d.locator('[data-code-region=body]').text_content()
 if old:field.evaluate('(el,text)=>{const i=el.value.indexOf(text);if(i<0)throw Error("body missing");el.focus();el.setSelectionRange(i,i+text.length)}',old)
 f.page.keyboard.insert_text(text);d.locator('[data-code-save]').click();expect(d).to_be_hidden()
 if verify:assert has(text)
def menu():
 box=panel().locator('.bp-viewport').bounding_box();panel().locator('.bp-viewport').click(button='right',position={'x':box['width']*.8,'y':box['height']*.85});return f.page.get_by_role('dialog',name='블루프린트 노드 검색')
def connect(a,b):focus(a);panel().locator('[data-bp-node="'+a+'"] .bp-exec-line-out[data-port=next]').click();focus(b);panel().locator('[data-bp-node="'+b+'"] .bp-exec-header-in').click()
def stage():
 global node
 show();menu().press('Escape');assert not private();menu().get_by_role('button',name='동작 만들기',exact=True).click();node=next(v['node']for _,v in private()if v['type']=='create');assert node.startswith('action_')and len(private())==2
 canvas=panel().locator('.bp-viewport');canvas.focus();canvas.press('Control+z');assert not private();canvas=panel().locator('.bp-viewport');canvas.focus();canvas.press('Control+y');assert created();focus(node);panel().locator('[data-bp-node="'+node+'"] [data-inline-description]').fill(t.intent);value(t.text);link=panel().locator('[data-bp-link="route:body"]');link.focus();link.press('Delete');connect(node,'$exit:return');connect('body',node);held=private();assert len(held)==6 and sorted(v['type']for _,v in held)==['create','intent','rename','route','route','source'];snapshot=copy.deepcopy(held);canvas=panel().locator('.bp-viewport');canvas.focus();canvas.press('Control+z');assert private()==snapshot;canvas=panel().locator('.bp-viewport');canvas.focus();canvas.press('Control+y');assert private()==snapshot
 return snapshot
def save():
 show();started=time.monotonic()
 # Cold corrected creation includes two baseline observations, validation and
 # receipt/read verification; one measured success took 73.6s end to end.
 try:panel().locator('[data-bp-save]').click();expect(f.page.locator('.brand')).to_be_enabled(timeout=120000)
 finally:
  _save_timings.append(dict(start=started,end=time.monotonic(),brandDisabled=f.page.locator('.brand').is_disabled(),status=panel().locator('.bp-status').inner_text()));(f.case/'save-timings.json').write_text(json.dumps(_save_timings,ensure_ascii=False))
def restart(i):f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle();show()
def history(direction):
 s=f.invoke('draftHistory',dict(action='inspect'))['result']['result'];assert f.invoke('draftHistory',dict(action=direction,token=s[direction]['token']))['result']['result']['accepted'];x.original()
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
 stage();assert t.current(node)is None and checkpoint.read_bytes()==before;x.original();restart(1);assert created()and has(t.text)and t.current(node)is None;f.checked('original canvas creation/cancel/Undo/Redo plus explicit description/source/two routes preserve six exact cells and ID across cold')
 if mode=='conflict':
  data=t.read();q=dict(action='authorBatch',id=t.graph,attempt=__import__('uuid').uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=[dict(action='source',node='body',text=t.base.original_source+'\n// 명시한 동료 수정')]);assert f.invoke('blueprint',q)['result']['result']['checkpointSaved'];held=checkpoint.read_bytes();save();assert created()and has(t.text)and checkpoint.read_bytes()==held and t.current(node)is None;x.original();restart(2);save();assert created()and has(t.text)and checkpoint.read_bytes()==held and t.current(node)is None;x.original();f.checked('stale direct creation cannot overwrite peer checkpoint or silently allocate a new ID across cold/retry');return
 if mode in ['storage-new','unapplied-new']:
  checkpoint.chmod(0o400)
  try:save();assert created()and has(t.text)and checkpoint.read_bytes()==before and t.current(node)is None;x.original();(f.case/'storage-failure-inputs.json').write_text(json.dumps(private(),ensure_ascii=False))
  finally:checkpoint.chmod(0o600)
  if mode=='unapplied-new':
   focus('$exit:return');panel().locator('[data-bp-node="$exit:return"] [data-exit-value]').click();q=f.page.get_by_role('dialog',name='핀 값 선택').get_by_role('searchbox',name='값 검색');q.fill('99');q.press('Enter');save();assert created()and has(t.text)and sum(bool(v.get('type'))for _,v in private())==7 and checkpoint.read_bytes()==before and t.current(node)is None;restart(2);save();assert created()and has(t.text)and sum(bool(v.get('type'))for _,v in private())==7 and checkpoint.read_bytes()==before and t.current(node)is None;x.original();f.checked('unapplied creation with unrelated root value keeps all seven cells/journal across cold instead of falling back to live mutations');return
  value(t.late);restart(2);assert created()and has(t.late)and t.current(node)is None;f.checked('failed checkpoint preserves all six inputs and unchanged live/physical graph; corrected body survives cold for explicit retry')
 if mode in ['loss','late']:
  requests=set();queries=set();paused={};lost=[]
  def interrupt(route):
   body=route.request.post_data_json
   if body.get('op')=='invoke'and body.get('endpoint')=='blueprint':
    action=body.get('input',{}).get('action')
    if action=='authorBatch':requests.add(body['requestId'])
    elif requests and action=='settledAuthorBatch':queries.add(body['requestId'])
   response=route.fetch();payload=response.json()
   if mode=='late'and not paused and any(r.get('ok')and r.get('requestId')in requests for r in payload.get('results',[])):paused.update(route=route,response=response);_held.update(paused);return
   if mode=='loss':
    for row in payload.get('results',[]):
     if row['requestId']in requests|queries:rid=row['requestId'];lost.append(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
   route.fulfill(response=response,json=payload)
  _interceptor=interrupt;f.page.route('**/api/request',interrupt);panel().locator('[data-bp-save]').click()
  deadline=time.monotonic()+90
  while time.monotonic()<deadline:
   if paused or requests and any(r in queries for r in lost):break
   f.page.wait_for_timeout(30)
  assert len(requests)==1
  if mode=='late':assert paused;value(t.late,False);paused['route'].fulfill(response=paused['response']);_held.clear();f.page.unroute('**/api/request',interrupt);f.idle();assert has(t.late)and not created()
  else:assert any(r in queries for r in lost);f.page.unroute_all(behavior='wait');f.idle();assert created()and has(t.text)
  restart(3);mark=len(f.traffic);save()
  if created()or has(t.text)or has(t.late):save()
  assert not created()and not has(t.text)and not has(t.late)and t.current(node)
  writes=[r['invoke']['input']for r in f.traffic[mark:]if r.get('invoke',{}).get('endpoint')=='blueprint'and r['invoke']['input'].get('action')=='authorBatch']
  if mode=='loss':assert not writes,writes
  else:assert writes and all(e['action']=='source'and e['node']==node and e['text']==t.late for w in writes for e in w['edits'])
  f.checked('direct creation '+mode+': exact receipt prevents duplicate ID/source/routes; late body saves separately')
 else:save();assert not created()and not has(t.text)and not has(t.late)and t.current(node);x.original()
 selected=t.late if mode in ['late','storage-new']else t.text;assert t.current(node)['source']==selected;assert not t.path(node).exists()
 if mode=='late':history('undo');assert t.current(node)['source']==t.text;history('redo');assert t.current(node)['source']==selected
 else:
  state=f.invoke('draftHistory',dict(action='inspect'))['result']['result'];assert state['boundary']=='OWNERSHIP_CHANGED'and not state['undo']['available']and not state['redo']['available']
 f.invoke('saveDraft',{});restart(4);assert not private()and t.current(node)['source']==selected;x.original();f.checked('existing creation ownership boundary/cold preserves new source and routes; a separate accepted late source retains bounded shared Undo/Redo')
 r=review();r.locator('[data-reject]').click();x.original();r=review();p=t.path(node);assert not p.exists();held=checkpoint.read_bytes();p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'peer new-file collision')
 try:r.locator('#confirm').click();f.idle();assert p.read_bytes()==b'peer new-file collision'and checkpoint.read_bytes()==held;x.original()
 finally:p.unlink()
 if r.is_visible():r.locator('[data-reject]').click()
 r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();t.physical_confirmed(node,selected);x.build('direct-creation-execution',10,'body\n'+('placed-late'if selected==t.late else'placed')+'\n10');restart(5);assert not private()and t.current(node)['source']==selected;t.physical_confirmed(node,selected);assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'direct-creation-final.png'),timeout=5000,full_page=True);f.checked('Review cancel/expected-missing final CAS/new Confirm/execution/cold create only the explicit node file and graph splice, preserving original C#/contracts/IDs')
 if mode=='normal':
  files={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts};save();restart(6);assert t.current(node)['source']==selected and all(p.read_bytes()==raw for p,raw in files.items());assert not private();f.checked('repeated empty Save/cold never reallocates creation ID or changes confirmed physical files')
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
   try:
    f.page.screenshot(path=str(f.case/'failure.png'),timeout=5000);f.page.evaluate('()=>Promise.race([confectoryFlushPresentation(),new Promise((_,reject)=>setTimeout(()=>reject(Error("capture flush deadline")),15000))])');(f.case/'failure-inputs.json').write_text(json.dumps(f.state()['presentation']['inputs']['blueprint'],ensure_ascii=False))
   except Exception as capture:(f.case/'failure-capture.json').write_text(json.dumps(dict(error=repr(capture)),ensure_ascii=False))
   raise
  f.browser.close()
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));f.stop()
print('DIRECT_CREATION_RECOVERY_FIXTURE',f.case,flush=True)
