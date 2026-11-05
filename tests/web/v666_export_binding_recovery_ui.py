"""Real ordinary owned export binding Save and validation/failure/receipt recovery."""
import ast,copy,json,pathlib,sys,uuid
from playwright.sync_api import sync_playwright,expect
import v666_export_binding_recovery_fixture as t
x=t.x
f=x.f;mode=sys.argv[3];text='right';late='spare'
helper=pathlib.Path(__file__).with_name('v666_async_transition_ui.py');names={'panel','open_graph'}
exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),str(helper),'exec'))
def private():return f.pending()['blueprint']
def has(value):return any(v.get('text')==value for _,v in private())
def current():return t.current()
def show():open_graph(t.feature,'body')
def begin():
 panel().locator('[data-bp-overview-node=publish]').click();panel().locator('[data-bp-node=publish] [data-bp-export-names]').click()
def finish(value):
 menu=f.page.get_by_role('listbox',name='출력 이름 선택');menu.locator('[data-export-output-id="'+value+'"]').click()
def stage(value,verify=True):
 if verify:show()
 begin();finish(value)
 if verify:assert has(value)
def save():show();panel().locator('[data-bp-save]').click();f.idle()
def saved():save();assert not has(text)and not has(late);x.original()
def restart(i):
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle();show()
def check_editor(value):
 show();assert has(value)or current()==value
def review():
 show();panel().locator('[data-bp-complete]').click();f.idle()
 if f.page.locator('#review-creation').is_visible():f.page.locator('#review-creation').click();f.idle()
 f.page.locator('.window[data-key=review]:visible,.window[data-key=targets]:visible').first.wait_for(state='visible',timeout=90000);t=f.page.locator('.window[data-key=targets]')
 if t.is_visible():t.locator('[data-target-choice]').select_option('portable');t.locator('[data-close]').click();panel().locator('[data-bp-complete]').click();f.idle()
 r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=90000)
 if r.locator('[data-review-advanced]').is_visible():r.locator('[data-review-advanced]').click()
 if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
 return r
def history(direction):
 state=f.invoke('draftHistory',{'action':'inspect'})['result']['result'];assert state[direction]['available'];assert f.invoke('draftHistory',{'action':direction,'token':state[direction]['token']})['result']['result']['accepted'];x.original()
def main():
 show();begin();f.page.get_by_role('listbox',name='출력 이름 선택').press('Escape');assert not private();stage(text);show();begin();finish('flag');assert has(text)and current()==t.original_output;x.original();assert checkpoint.read_bytes()==before;restart(1);assert has(text);check_editor(text);f.checked('original export binding-menu cancel and exact pending output choice cold restoration')
 if mode=='conflict':
  data=t.read();peer=late;f.invoke('blueprint',dict(action='outputNodes',id=t.graph,basis=data['basis'],edits=[dict(kind='bind',node=t.node,output=peer)]));f.invoke('saveDraft',{});held=checkpoint.read_bytes();save();assert has(text)and checkpoint.read_bytes()==held and current()==peer;x.original();restart(2);assert has(text)and checkpoint.read_bytes()==held;check_editor(text);x.original();f.checked('stale export binding input never overwrites peer checkpoint or silently rebinds after cold');return
 if mode=='storage-new':
  checkpoint.chmod(0o400)
  try:save();assert has(text)and checkpoint.read_bytes()==before and current()==t.original_output;x.original();(f.case/'storage-failure-inputs.json').write_text(json.dumps(private(),ensure_ascii=False))
  finally:checkpoint.chmod(0o600)
  stage(late);restart(2);assert has(late);check_editor(late);x.original();f.checked('failed export binding checkpoint retains input/live state; newer export binding survives cold and explicit retry')
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
  if mode=='late':assert paused;stage(late,verify=False);paused['route'].fulfill(response=paused['response']);f.page.unroute('**/api/request',interrupt);f.idle();assert has(late)
  else:assert any(r in queries for r in lost);f.page.unroute_all(behavior='wait');f.idle();assert has(text)
  restart(3);wanted=late if mode=='late'else text;assert has(wanted);check_editor(wanted);mark=len(f.traffic);save()
  if has(wanted):save()
  assert not has(wanted)and current()==wanted
  writes=[r['invoke']['input']for r in f.traffic[mark:]if r.get('invoke',{}).get('endpoint')=='blueprint'and r['invoke']['input'].get('action')=='authorBatch']
  if mode=='loss':assert not writes,writes
  else:assert writes and all(edit['definition']['edits']==[dict(kind='bind',node=t.node,output=late)] for write in writes for edit in write['edits'])
  f.checked('export binding '+mode+': exact receipt/new export binding separation without replay of earlier output choice')
 else:saved()
 value=late if mode in ['storage-new','late']else text;assert current()==value and not has(value);history('undo');assert current()==(text if mode=='late'else t.original_output);history('redo');assert current()==value;f.invoke('saveDraft',{});restart(4);assert not has(value);check_editor(value);x.original();f.checked('export binding supports shared draft Undo/Redo/cold with unchanged contracts and physical originals')

 r=review();r.locator('[data-reject]').click();x.original();r=review();p=f.project/t.graph_file;physical=p.read_bytes();held=checkpoint.read_bytes();p.write_bytes(physical+b' ')
 try:r.locator('#confirm').click();f.idle();assert p.read_bytes()==physical+b' 'and checkpoint.read_bytes()==held;assert all(path.read_bytes()==raw for path,raw in x.physical.items()if path!=p)
 finally:p.write_bytes(physical)
 if r.is_visible():r.locator('[data-reject]').click()
 r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();actual=json.loads(p.read_text());expected=copy.deepcopy(t.definition);next(n for n in expected['nodes']if n['id']==t.node)['output']=value;assert actual==expected;assert all(path.read_bytes()==raw for path,raw in x.physical.items()if path.name!=t.graph_file);x.build('ordinary-export-binding-execution',*t.expected(value));restart(5);check_editor(value);assert not private()and not f.errors and not f.external,(private(),f.errors,f.external);f.page.screenshot(path=str(f.case/'export-binding-final.png'),timeout=5000,full_page=True);f.checked('export binding Review cancel/final CAS/new Confirm/actual execution/cold preserve original C# bytes, IDs, profile and connections')
 if mode=='normal':
  physical_now={p:p.read_bytes()for p in x.physical};data=t.read();q=dict(action='authorBatch',id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=[dict(action='outputNodes',node='$exports',definition=dict(edits=[dict(kind='bind',node=t.node,output=value)]))]);assert f.invoke('blueprint',q)['result']['result']['checkpointSaved'];raw=checkpoint.read_bytes();doc=json.loads(raw);assert not any(u['draft']!=u['original']for u in doc['changes']);g=next(u for u in doc['changes']if u['id']==t.graph);assert g['authorSaveReceipt']['ownedOutputBinding']is True;restart(6);assert f.invoke('blueprint',{**q,'action':'settledAuthorBatch'})['result']['result']['settled'];assert checkpoint.read_bytes()==raw and all(p.read_bytes()==v for p,v in physical_now.items());assert not private();f.checked('unchanged export binding Save keeps a durable receipt even with zero dirty source files; cold settles without physical writes')
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
print('EXPORT_BINDING_RECOVERY_FIXTURE',f.case,flush=True)
