"""Original name inspector plus C# editor, saved as one explicit owned pair."""
import ast,copy,json,pathlib,sys,time,traceback
from playwright.sync_api import sync_playwright,expect
import v666_alias_source_fixture as t
x=t.x;f=t.f;mode=sys.argv[3];node=t.node;_held={};_interceptor=None
helper=pathlib.Path(__file__).with_name('v666_async_transition_ui.py');names={'panel','open_graph'}
exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),str(helper),'exec'))
def private():return f.pending()['blueprint']
def has(kind,text):return any(v.get('type')==kind and v.get('node')==node and v.get('text')==text for _,v in private())
def show():f.page.set_viewport_size({'width':1800,'height':1400});open_graph(t.feature,node)
def focus():panel().locator('[data-bp-overview-node="'+node+'"]').click()
def reveal(button):
 vp=panel().locator('.bp-viewport');rect=vp.bounding_box();delta=button.evaluate('(el)=>{const a=el.getBoundingClientRect(),v=el.closest(".bp-viewport").getBoundingClientRect();return {x:a.x+a.width/2-v.x-v.width/2,y:a.y+a.height/2-v.y-v.height/2}}');f.page.mouse.move(rect['x']+rect['width']/2,rect['y']+rect['height']/2);f.page.mouse.wheel(delta['x'],delta['y']);f.page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
def naming(value,verify=True):
 if verify:show()
 focus();button=panel().locator('.bp-inline-pin[data-node="body"][data-side="out"][data-port="field:return"] .bp-pin-value');reveal(button);button.click();d=f.page.get_by_role('dialog',name='출력 핀 설정',exact=True);expect(d).to_be_visible();d.get_by_role('textbox',name='지역변수 이름',exact=True).fill(value);f.page.keyboard.press('Enter');expect(d).to_have_count(0)
 if verify:assert any(v.get('type')=='local-alias'and json.loads(v['text'])['name']==value for _,v in private())
def selected_alias():return json.loads(next(v['text']for _,v in private()if v.get('type')=='local-alias'))
def bind_alias():
 panel().locator('[data-bp-overview-node="$exit:return"]').click();button=panel().locator('.bp-inline-pin[data-node="$exit:return"] [aria-label="값 목록 열기"]');reveal(button);button.click();d=f.page.get_by_role('dialog',name='핀 값 선택');d.get_by_role('button',name='지역변수 · '+selected_alias()['name'],exact=True).click();expect(d).to_have_count(0)
def value(text,verify=True,undo=False):
 focus();panel().locator('[data-bp-node="'+node+'"] [data-internal-code]').click();d=f.page.locator('.bp-script-dialog');expect(d).to_be_visible();field=d.locator('[data-code-source]');old=d.locator('[data-code-region=body]').text_content();field.evaluate('(el,text)=>{const i=el.value.indexOf(text);if(i<0)throw Error("body missing");el.focus();el.setSelectionRange(i,i+text.length)}',old);f.page.keyboard.insert_text(text)
 if undo:field.press('Control+z');assert 'amount+4'not in field.input_value();field.press('Control+y');assert 'amount+4'in field.input_value()
 d.locator('[data-code-save]').click();expect(d).to_be_hidden()
 if verify:assert has('source',text)
def save():show();panel().locator('[data-bp-save]').click();expect(f.page.locator('.brand')).to_be_enabled(timeout=120000)
def restart(i):f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size({'width':1800,'height':1400});f.idle();show()
def history(direction):
 s=f.invoke('draftHistory',dict(action='inspect'))['result']['result'];assert s[direction]['available'];assert f.invoke('draftHistory',dict(action=direction,token=s[direction]['token']))['result']['result']['accepted'];x.original()
def review():
 show();panel().locator('[data-bp-complete]').click();f.idle()
 if f.page.locator('#review-creation').is_visible():f.page.locator('#review-creation').click();f.idle()
 f.page.locator('.window[data-key=review]:visible,.window[data-key=targets]:visible').first.wait_for(state='visible',timeout=90000);targets=f.page.locator('.window[data-key=targets]')
 if targets.is_visible():targets.locator('[data-target-choice]').select_option('portable');targets.locator('[data-close]').click();panel().locator('[data-bp-complete]').click();f.idle()
 r=f.page.locator('.window[data-key=review]');expect(r).to_be_visible(timeout=90000)
 if r.locator('[data-review-advanced]').is_visible():r.locator('[data-review-advanced]').click()
 if r.locator('[data-advanced-reviewed]').count():r.locator('[data-advanced-reviewed]').check()
 return r
def has_alias(value):return any(v.get('type')=='local-alias'and json.loads(v['text'])['name']==value for _,v in private())
def typed():return[(key,v)for key,v in private()if v.get('type')]
def main():
 global _interceptor
 show();naming(t.name);value(t.text,undo=True);assert len(typed())==2 and t.current()['source']==t.original_source and not t.aliases()and checkpoint.read_bytes()==before;x.original()
 if mode=='baseline':
  held=copy.deepcopy(private());save();assert private()==held and checkpoint.read_bytes()==before and t.current()['source']==t.original_source and not t.aliases();data=t.read();alias=selected_alias();q=dict(action='authorBatch',id=t.graph,attempt=__import__('uuid').uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=[dict(action='source',node=node,text=t.text),dict(action='aliasPlan',node='$locals',definition=dict(aliases=[alias],bindings=[]))]);f.invoke('blueprint',q,False);assert checkpoint.read_bytes()==before;x.original();f.checked('published bc8e743a rejects combined authored output name and C# body in actual UI and native batch, preserving both inputs/checkpoint/originals');return
 bind_alias();alias_id=selected_alias()['id'];assert len(typed())==3;restart(1);assert has_alias(t.name)and has('source',t.text)and len(typed())==3;x.original();f.checked('original output-name/C# editors and real alias consumer retain Unicode names, source bytes and three inputs across cold; no public contract or new identity format')
 if mode=='conflict':
  data=t.read();peer=t.original_source+'// peer body';q=dict(action='authorBatch',id=t.graph,attempt=__import__('uuid').uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=[dict(action='source',node=node,text=peer)]);assert f.invoke('blueprint',q)['result']['result']['checkpointSaved'];saved=checkpoint.read_bytes();save();assert has_alias(t.name)and has('source',t.text)and checkpoint.read_bytes()==saved and t.current()['source']==peer and not t.aliases();x.original();restart(2);save();assert has_alias(t.name)and has('source',t.text)and checkpoint.read_bytes()==saved and t.current()['source']==peer and not t.aliases();x.original();f.checked('peer checkpoint rejects entire old alias/body candidate after retry/cold, preserving all inputs and original files');return
 if mode=='storage':
  checkpoint.chmod(0o400)
  try:save();assert has_alias(t.name)and has('source',t.text)and checkpoint.read_bytes()==before and t.current()['source']==t.original_source and not t.aliases();x.original()
  finally:checkpoint.chmod(0o600)
  naming(t.late_name);value(t.late);restart(2);assert has_alias(t.late_name)and has('source',t.late);f.checked('actual checkpoint write denial keeps name/body/binding and original baseline; corrected same-owner names and source survive cold')
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
  _interceptor=interrupt;f.page.route('**/api/request',interrupt);panel().locator('[data-bp-save]').click();deadline=time.monotonic()+120
  while time.monotonic()<deadline:
   if paused or requests and any(r in queries for r in lost):break
   f.page.wait_for_timeout(30)
  assert len(requests)==1
  if mode=='late':
   assert paused;naming(t.late_name,False);value(t.late,False);paused['route'].fulfill(response=paused['response']);_held.clear();f.page.unroute('**/api/request',interrupt);f.idle();assert has_alias(t.late_name)and has('source',t.late)
  else:assert any(r in queries for r in lost);f.page.unroute('**/api/request',interrupt);f.idle();assert has_alias(t.name)and has('source',t.text)
  restart(3);mark=len(f.traffic);save()
  if typed():save()
  assert not private();writes=[r['invoke']['input']for r in f.traffic[mark:]if r.get('invoke',{}).get('endpoint')=='blueprint'and r['invoke']['input'].get('action')=='authorBatch']
  if mode=='loss':assert not writes,writes
  else:assert writes and all(e['action']!='source'or e['text']==t.late for w in writes for e in w['edits'])
  f.checked('combined '+mode+': full settled receipt separates late names/body and avoids replaying accepted old texts after cold')
 else:save();assert not private()
 wanted_name=t.late_name if mode in ['storage','late']else t.name;wanted_source=t.late if mode in ['storage','late']else t.text;data=t.read();alias=next(a for a in data['locals']if a['id']==alias_id);assert alias['name']==wanted_name and json.loads(alias['sourceJson'])==dict(node=node,output='return')and t.current()['source']==wanted_source and json.loads(data['exits'][0]['valueJson'])==dict(local=alias_id);x.original()
 if mode not in ['normal','package','compiler']:
  f.invoke('saveDraft',{});restart(4);assert not private()and t.current()['source']==wanted_source and t.aliases()[0]['id']==alias_id and t.aliases()[0]['name']==wanted_name;x.original();assert not f.errors and not f.external;f.page.screenshot(path=str(f.case/'alias-source-checkpoint.png'),timeout=5000);f.checked('focused '+mode+' preserves the complete checkpoint and both authored values across another cold; physical publication remains separate');return
 if mode=='normal':
  history('undo');assert t.current()['source']==(t.text if mode=='late'else t.original_source)
  if mode=='late':assert t.aliases()[0]['name']==t.name
  else:assert not t.aliases()
  history('redo');assert t.current()['source']==wanted_source and t.aliases()[0]['name']==wanted_name;f.invoke('saveDraft',{});restart(4);assert not private()and t.current()['source']==wanted_source and t.aliases()[0]['name']==wanted_name;x.original();f.checked('one shared Undo/Redo and cold checkpoint restore name, stable alias ID/source/consumer and explicit C# body together')
 if mode=='compiler':
  naming('검토할 결과');invalid='UnknownAliasSourceSymbol();\n'+wanted_source;value(invalid);save();assert not private();r=review();saved=checkpoint.read_bytes();mark=len(f.traffic);r.locator('#confirm').click();f.idle();raw=[f.state(),f.traffic[mark:]];assert 'CS0103'in json.dumps(raw)and'UnknownAliasSourceSymbol'in json.dumps(raw)and checkpoint.read_bytes()==saved;x.original();r.locator('[data-reject]').click();naming(wanted_name);value(wanted_source);save();f.checked('compiler rejection preserves verbatim C# diagnostic and entire alias/body draft until explicit correction');assert not private()and t.current()['source']==wanted_source and t.aliases()[0]['name']==wanted_name;x.original();f.page.screenshot(path=str(f.case/'alias-source-compiler.png'),timeout=5000);return
 if mode=='normal':
  r=review();r.locator('[data-reject]').click();x.original();r=review();physical=f.project/t.graph_file;original=physical.read_bytes();saved=checkpoint.read_bytes();physical.write_bytes(original+b' ')
  try:r.locator('#confirm').click();f.idle();assert physical.read_bytes()==original+b' 'and checkpoint.read_bytes()==saved and all(path.read_bytes()==raw for path,raw in x.physical.items()if path!=physical)
  finally:physical.write_bytes(original)
  if r.is_visible():r.locator('[data-reject]').click()
 r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();t.physical_confirmed(wanted_name,wanted_source,alias_id);result=12 if wanted_source==t.late else 11;x.build('alias-body-execution',result,'body\n'+str(result));restart(5);assert not private()and t.current()['source']==wanted_source and t.aliases()[0]['id']==alias_id;t.physical_confirmed(wanted_name,wanted_source,alias_id);assert not f.errors and not f.external,(f.errors,f.external);f.checked('Review cancel/physical final CAS/reviewed Confirm and real execution preserve caller/source/contracts/IDs and yield the explicitly authored result')
 if mode=='normal':
  files={path:path.read_bytes()for path in x.physical};naming(wanted_name);value(wanted_source);save();restart(6);assert not private()and t.aliases()[0]['id']==alias_id and all(path.read_bytes()==raw for path,raw in files.items());save();restart(7);assert not private()and all(path.read_bytes()==raw for path,raw in files.items());f.checked('repeated same-value and empty Save/cold preserve alias identity, exact source and physical originals')
 f.page.screenshot(path=str(f.case/'alias-source-final.png'),timeout=5000)

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
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));(f.case/'traffic.json').write_text(json.dumps(f.traffic,ensure_ascii=False));f.stop()
print('ALIAS_SOURCE_FIXTURE',f.case,flush=True)
