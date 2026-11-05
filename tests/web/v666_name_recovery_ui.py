"""Real ordinary owned node name Save and validation/failure/receipt recovery."""
import ast,copy,json,pathlib,sys,uuid
from playwright.sync_api import sync_playwright,expect
import v666_root_execution_fixture as x
f=x.f;mode=sys.argv[3];text='명시한 동작 이름 α 😀';late='늦게 입력한 동작 이름 β'
helper=pathlib.Path(__file__).with_name('v666_async_transition_ui.py');names={'panel','open_graph'}
exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),str(helper),'exec'))
def private():return f.pending()['blueprint']
def has(value):return any(v.get('text')==value for _,v in private())
def current():return next(n.get('displayName',n['id'])for n in x.read(x.caller)['nodes']if n['id']=='after')
def show():
 f.page.set_viewport_size({'width':1800,'height':1400});open_graph(x.main_id,'after');f.page.set_viewport_size({'width':390,'height':844});expect(panel().locator('[data-flow-node=after]')).to_be_visible()
def stage(value,verify=True,undo=False):
 if verify:show()
 panel().locator('[data-flow-node=after]').click();field=f.page.locator('.bp-flow-inspector:visible [data-flow-node-name]');old=field.input_value();field.press('Control+a');f.page.keyboard.insert_text(value)
 if undo:
  field.press('Control+z');assert field.input_value()==old;field.press('Control+Shift+z');assert field.input_value()==value
 f.page.locator('.bp-flow-inspector:visible [data-flow-done]').click()
 if verify:assert has(value)
def save():show();panel().locator('[data-bp-save]').click();f.idle()
def saved():save();assert not has(text)and not has(late);x.original()
def restart(i):
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle();show()
def check_editor(value):
 show();panel().locator('[data-flow-node=after]').click();field=f.page.locator('.bp-flow-inspector:visible [data-flow-node-name]');assert field.input_value()==value;f.page.locator('.bp-flow-inspector:visible [data-flow-done]').click()
def review():
 show();f.page.set_viewport_size({'width':1800,'height':1400});panel().locator('[data-bp-complete]').click();f.idle()
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
 stage(text,undo=True);x.original();assert checkpoint.read_bytes()==before;restart(1);assert has(text);check_editor(text);f.checked('existing compact name inspector: native Undo/Redo and exact pending display name cold restoration')
 if mode=='conflict':
  data=x.read(x.caller);peer='동료가 저장한 이름';f.invoke('blueprint',dict(action='rename',id=x.caller,basis=data['basis'],node='after',text=peer));f.invoke('saveDraft',{});held=checkpoint.read_bytes();save();assert has(text)and checkpoint.read_bytes()==held and current()==peer;x.original();restart(2);assert has(text)and checkpoint.read_bytes()==held;check_editor(text);x.original();f.checked('stale display name input never overwrites peer checkpoint or silently rebinds after cold');return
 if mode=='storage-new':
  checkpoint.chmod(0o400)
  try:save();assert has(text)and checkpoint.read_bytes()==before and current()=='after';x.original();(f.case/'storage-failure-inputs.json').write_text(json.dumps(private(),ensure_ascii=False))
  finally:checkpoint.chmod(0o600)
  stage(late);restart(2);assert has(late);check_editor(late);x.original();f.checked('failed display name checkpoint retains input/live state; newer name survives cold and explicit retry')
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
  else:assert all(edit.get('text')!=text for write in writes for edit in write['edits'])
  f.checked('display name '+mode+': exact receipt/new name separation without replay of earlier name')
 else:saved()
 value=late if mode in ['storage-new','late']else text;assert current()==value and not has(value);history('undo');assert current()==(text if mode=='late'else 'after');history('redo');assert current()==value;f.invoke('saveDraft',{});restart(4);assert not has(value);check_editor(value);x.original();f.checked('display name supports shared draft Undo/Redo/cold with unchanged contracts and physical originals')
 if mode=='invalid':
  stage(' ');held=checkpoint.read_bytes();save();assert has(' ')and checkpoint.read_bytes()==held and current()==value;x.original();stage(value);saved();f.checked('invalid blank name retains exact input/checkpoint/originals until explicit correction')

 r=review();r.locator('[data-reject]').click();x.original();r=review();p=f.project/'Main.graph.json';physical=p.read_bytes();held=checkpoint.read_bytes();p.write_bytes(physical+b' ')
 try:r.locator('#confirm').click();f.idle();assert p.read_bytes()==physical+b' 'and checkpoint.read_bytes()==held;assert all(path.read_bytes()==raw for path,raw in x.physical.items()if path!=p)
 finally:p.write_bytes(physical)
 if r.is_visible():r.locator('[data-reject]').click()
 r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();expected=copy.deepcopy(x.cg);next(n for n in expected['nodes']if n['id']=='after')['displayName']=value;assert json.loads(p.read_text())==expected;assert all(path.read_bytes()==raw for path,raw in x.physical.items()if path.name!='Main.graph.json');x.build('ordinary-name-execution',10,x.initial_stdout);restart(5);check_editor(value);assert not private()and not f.errors and not f.external,(private(),f.errors,f.external);f.page.screenshot(path=str(f.case/'name-final.png'),timeout=5000,full_page=True);f.checked('display name Review cancel/final CAS/new Confirm/actual execution/cold preserve original C# bytes, IDs, profile and connections')
 if mode=='normal':
  physical_now={p:p.read_bytes()for p in x.physical};data=x.read(x.caller);q=dict(action='authorBatch',id=x.caller,attempt=uuid.uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=[dict(action='rename',node='after',text=value)]);assert f.invoke('blueprint',q)['result']['result']['checkpointSaved'];raw=checkpoint.read_bytes();doc=json.loads(raw);assert not any(u['draft']!=u['original']for u in doc['changes']);g=next(u for u in doc['changes']if u['id']==x.caller);assert g['authorSaveReceipt']['ownedRename']is True;restart(6);assert f.invoke('blueprint',{**q,'action':'settledAuthorBatch'})['result']['result']['settled'];assert checkpoint.read_bytes()==raw and all(p.read_bytes()==v for p,v in physical_now.items());assert not private();f.checked('unchanged display name Save keeps a durable receipt even with zero dirty source files; cold settles without physical writes')
try:
 f.start(0);f.invoke('select',dict(id=x.main_id));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400})
  try:main()
  except Exception:
   (f.case/'failure-inputs.json').write_text(json.dumps(private(),ensure_ascii=False));f.page.screenshot(path=str(f.case/'failure.png'),timeout=5000);raise
  f.browser.close()
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));f.stop()
print('NAME_RECOVERY_FIXTURE',f.case,flush=True)
