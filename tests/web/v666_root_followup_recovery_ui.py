"""Real ordinary owned C# body Save and compiler/failure/receipt recovery."""
import ast,copy,json,pathlib,sys,uuid
from playwright.sync_api import sync_playwright,expect
import v666_root_followup_recovery_fixture as t
x=t.x
f=x.f;mode=sys.argv[3];text=t.text;late=t.late
helper=pathlib.Path(__file__).with_name('v666_async_transition_ui.py');names={'panel','open_graph'}
exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),str(helper),'exec'))
def private():return f.pending()['blueprint']
def has(value):return any(v.get('text')==value for _,v in private())
def current():return next(n['source']for n in t.read()['nodes']if n['id']=='body')
def show():
 open_graph(t.feature,'body');panel().locator('.window-title').click(position={'x':190,'y':16});panel().locator('[data-bp-overview-node=body]').click()
def editor(ensure=True):
 if ensure:show()
 panel().locator('[data-bp-node=body] [data-internal-code]').click();d=f.page.locator('.bp-script-dialog');expect(d).to_be_visible();return d
def stage(value,verify=True,undo=False):
 d=editor(verify);field=d.locator('[data-code-source]');old=d.locator('[data-code-region=body]').text_content();field.evaluate('(el,text)=>{el.focus();const i=el.value.indexOf(text);if(i<0)throw Error("Editable body missing");el.setSelectionRange(i,i+text.length)}',old);f.page.keyboard.insert_text(value)
 if undo:
  field.press('Control+z');assert value not in field.input_value();field.press('Control+y');assert value in field.input_value()
 d.locator('[data-code-save]').click();expect(d).to_be_hidden()
 if verify:assert has(value)
def save():show();panel().locator('[data-bp-save]').click();f.idle()
def saved():save();assert not has(text)and not has(late);x.original()
def restart(i):
 t.complete_group()
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle();show()
def check_editor(value):
 d=editor();assert d.locator('[data-code-region=body]').text_content()==value;d.locator('[data-code-cancel]').click()
def restored_proof():
 held=next(v['proof']for _,v in private()if v.get('type')=='source');now=x.proof(t.read());assert held!=now
 assert [(v[0],v[2])for v in json.loads(held)]==[(v[0],v[2])for v in json.loads(now)]
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
 show();root_input=panel().locator('[data-signature-id] [data-signature-name]');root_input.fill(t.base.selected);root_input.press('Enter');expect(panel().locator('[data-signature-id=units]')).to_be_visible();root_input=panel().locator('[data-signature-id] [data-signature-name]');root_input.fill(t.original_name);root_input.press('Enter');expect(panel().locator('[data-signature-id=amount]')).to_be_visible();save();assert not private();root_checkpoint=checkpoint.read_bytes();root_doc,_=t.complete_group();assert not any(u['draft']!=u['original']for u in root_doc['changes']);x.original();f.checked('existing root rename/back/Save retains a complete zero-dirty root group before subsequent ordinary C# editing');d=editor();field=d.locator('[data-code-source]');old=field.input_value();field.evaluate('el=>{el.focus();el.setSelectionRange(0,0)}');f.page.keyboard.insert_text('RejectedHeader');assert field.input_value()==old;d.locator('[data-code-cancel]').click();assert not private();stage(text,undo=True);x.original();assert checkpoint.read_bytes()==root_checkpoint;restart(1);assert has(text);check_editor(text);f.checked('ordinary C#: fixed declaration, editor Undo/Redo/cancel and exact pending source cold restoration')
 if mode=='conflict':
  data=t.read();peer=t.original_source+'\n// 명시한 동료 본문';peer_request=dict(action='authorBatch',id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=[dict(action='source',node='body',text=peer)]);assert f.invoke('blueprint',peer_request)['result']['result']['checkpointSaved'];t.complete_group();held=checkpoint.read_bytes();save();assert has(text)and checkpoint.read_bytes()==held and current()==peer;x.original();restart(2);assert has(text)and checkpoint.read_bytes()==held;check_editor(text);x.original();f.checked('stale C# input never overwrites peer checkpoint or silently rebinds after cold');return
 if mode=='storage-new':
  checkpoint.chmod(0o400)
  try:save();assert has(text)and checkpoint.read_bytes()==root_checkpoint and current()==t.original_source;x.original();(f.case/'storage-failure-inputs.json').write_text(json.dumps(private(),ensure_ascii=False))
  finally:checkpoint.chmod(0o600)
  stage(late);restart(2);assert has(late);check_editor(late);x.original();f.checked('failed C# checkpoint retains input/live state; newer source survives cold and explicit retry')
 if mode in ['loss','late']:
  restored_proof()
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
  f.checked('C# '+mode+': exact receipt/new source separation without replay of earlier source')
 else:saved()
 value=late if mode in ['storage-new','late']else text;assert current()==value and not has(value);history('undo');assert current()==(text if mode=='late'else t.original_source);history('redo');assert current()==value;f.invoke('saveDraft',{});restart(4);assert not has(value);check_editor(value);x.original();f.checked('C# source supports shared draft Undo/Redo/cold with unchanged contracts and physical originals')
 if mode=='compiler':
  invalid='UnknownV666SourceSymbol();\n'+value;stage(invalid);save();assert not has(invalid);r=review();held=checkpoint.read_bytes();mark=len(f.traffic);r.locator('#confirm').click();f.idle();raw=[f.state(),f.traffic[mark:]];assert 'CS0103'in json.dumps(raw)and'UnknownV666SourceSymbol'in json.dumps(raw);assert checkpoint.read_bytes()==held;x.original();(f.case/'compiler-failure.json').write_text(json.dumps(raw,ensure_ascii=False));r.locator('[data-reject]').click();stage(value);saved();f.checked('compiler rejection preserves verbatim CS0103, private C# and originals until explicit correction')
 r=review();r.locator('[data-reject]').click();x.original();r=review();p=f.project/t.source_file;physical=p.read_bytes();held=checkpoint.read_bytes();p.write_bytes(physical+b' ')
 try:r.locator('#confirm').click();f.idle();assert p.read_bytes()==physical+b' 'and checkpoint.read_bytes()==held;assert all(path.read_bytes()==raw for path,raw in x.physical.items()if path!=p)
 finally:p.write_bytes(physical)
 if r.is_visible():r.locator('[data-reject]').click()
 r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();assert json.loads(p.read_text())['source']==value;assert json.loads((f.project/t.graph_file).read_text())==t.base.definition;assert all(path.read_bytes()==raw for path,raw in x.physical.items()if path.name!=t.source_file);x.build('root-followup-source-execution',*t.expected);restart(5);check_editor(value);assert not private()and not f.errors and not f.external,(private(),f.errors,f.external);f.page.screenshot(path=str(f.case/'root-followup-final.png'),timeout=5000,full_page=True);f.checked('C# Review cancel/final CAS/new Confirm/actual execution/cold preserve untouched C#, IDs, profile and connections')
 if mode=='normal':
  physical_now={p:p.read_bytes()for p in x.physical};data=t.read();q=dict(action='authorBatch',id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=[dict(action='source',node='body',text=value)]);assert f.invoke('blueprint',q)['result']['result']['checkpointSaved'];raw=checkpoint.read_bytes();doc=json.loads(raw);assert not any(u['draft']!=u['original']for u in doc['changes']);g=next(u for u in doc['changes']if u['id']==t.graph);assert g['authorSaveReceipt']['ownedSource']is True;t.complete_group();restart(6);assert f.invoke('blueprint',{**q,'action':'settledAuthorBatch'})['result']['result']['settled'];assert checkpoint.read_bytes()==raw and all(p.read_bytes()==v for p,v in physical_now.items());assert not private();f.checked('unchanged C# source Save keeps a durable receipt even with zero dirty source files; cold settles without physical writes')
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
print('ROOT_FOLLOWUP_RECOVERY_FIXTURE',f.case,flush=True)
