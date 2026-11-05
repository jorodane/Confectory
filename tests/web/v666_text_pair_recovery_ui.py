"""Original name inspector plus C# editor, saved as one explicit owned pair."""
import ast,copy,json,pathlib,sys,time,traceback
from playwright.sync_api import sync_playwright,expect
import v666_text_pair_recovery_fixture as t
x=t.x;f=t.f;mode=sys.argv[3];node=t.node;_held={};_interceptor=None
helper=pathlib.Path(__file__).with_name('v666_async_transition_ui.py');names={'panel','open_graph'}
exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),str(helper),'exec'))
def private():return f.pending()['blueprint']
def has(kind,text):return any(v.get('type')==kind and v.get('node')==node and v.get('text')==text for _,v in private())
def show():f.page.set_viewport_size({'width':1800,'height':1400});open_graph(t.feature,node)
def focus():panel().locator('[data-bp-overview-node="'+node+'"]').click()
def name(value,verify=True):
 if verify:show()
 f.page.set_viewport_size({'width':390,'height':844});panel().locator('[data-flow-node="'+node+'"]').click();field=f.page.locator('.bp-flow-inspector:visible [data-flow-node-name]');field.fill(value);f.page.locator('.bp-flow-inspector:visible [data-flow-done]').click();f.page.set_viewport_size({'width':1800,'height':1400})
 if verify:assert has('rename',value)
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
def main():
 global _interceptor
 show();focus();panel().locator('[data-bp-node="'+node+'"] [data-internal-code]').click();d=f.page.locator('.bp-script-dialog');field=d.locator('[data-code-source]');held=field.input_value();field.evaluate('el=>{el.focus();el.setSelectionRange(0,0)}');f.page.keyboard.insert_text('RejectedHeader');assert field.input_value()==held;d.locator('[data-code-cancel]').click();assert not private();name(t.name);value(t.text,undo=True);assert len(private())==2 and t.current()['displayName']==t.original_name and t.current()['source']==t.original_source and checkpoint.read_bytes()==before;x.original();restart(1);assert has('rename',t.name)and has('source',t.text);f.checked('original compact name and C# editors preserve fixed declaration/cancel/Undo/Redo and exact two private texts across cold')
 if mode=='conflict':
  data=t.read();peer=t.original_source+'// 명시한 동료 본문';q=dict(action='authorBatch',id=t.graph,attempt=__import__('uuid').uuid4().hex,checkpointHash=data['checkpointHash'],sourceProof=x.proof(data),edits=[dict(action='source',node=node,text=peer)]);assert f.invoke('blueprint',q)['result']['result']['checkpointSaved'];saved=checkpoint.read_bytes();save();assert has('rename',t.name)and has('source',t.text)and checkpoint.read_bytes()==saved and t.current()['source']==peer;x.original();restart(2);save();assert has('rename',t.name)and has('source',t.text)and checkpoint.read_bytes()==saved and t.current()['source']==peer;x.original();f.checked('stale paired input cannot overwrite peer checkpoint or silently rebind after cold/retry');return
 if mode in ['storage-new','unapplied-new']:
  checkpoint.chmod(0o400)
  try:save();assert has('rename',t.name)and has('source',t.text)and checkpoint.read_bytes()==before and t.current()['displayName']==t.original_name and t.current()['source']==t.original_source;x.original();(f.case/'storage-failure-inputs.json').write_text(json.dumps(private(),ensure_ascii=False))
  finally:checkpoint.chmod(0o600)
  if mode=='unapplied-new':
   panel().locator('[data-bp-overview-node="$exit:return"]').click();panel().locator('[data-bp-node="$exit:return"] [data-exit-value]').click();q=f.page.get_by_role('dialog',name='핀 값 선택').get_by_role('searchbox',name='값 검색');q.fill('99');q.press('Enter');save();assert sum(bool(v.get('type'))for _,v in private())==3 and has('rename',t.name)and has('source',t.text)and checkpoint.read_bytes()==before;restart(2);save();assert sum(bool(v.get('type'))for _,v in private())==3 and has('rename',t.name)and has('source',t.text)and checkpoint.read_bytes()==before and t.current()['displayName']==t.original_name and t.current()['source']==t.original_source;x.original();f.checked('an extra root value preserves all three cells and unapplied journal across cold instead of live fallback');return
  name(t.late_name);value(t.late);restart(2);assert has('rename',t.late_name)and has('source',t.late);f.checked('failed paired checkpoint preserves both inputs/live/originals; corrected name and body survive cold for explicit retry')
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
  if mode=='late':assert paused;name(t.late_name,False);value(t.late,False);paused['route'].fulfill(response=paused['response']);_held.clear();f.page.unroute('**/api/request',interrupt);f.idle();assert has('rename',t.late_name)and has('source',t.late)
  else:assert any(r in queries for r in lost);f.page.unroute('**/api/request',interrupt);f.idle();assert has('rename',t.name)and has('source',t.text)
  restart(3);mark=len(f.traffic);save()
  if has('rename',t.late_name)or has('source',t.late)or has('rename',t.name)or has('source',t.text):save()
  assert not private();writes=[r['invoke']['input']for r in f.traffic[mark:]if r.get('invoke',{}).get('endpoint')=='blueprint'and r['invoke']['input'].get('action')=='authorBatch']
  if mode=='loss':assert not writes,writes
  else:assert writes and all(e['text']in [t.late_name,t.late]for w in writes for e in w['edits'])
  f.checked('paired '+mode+': exact receipt separates late name/body without replaying accepted texts')
 else:save();assert not private()
 wanted_name=t.late_name if mode in ['late','storage-new']else t.name;wanted_source=t.late if mode in ['late','storage-new']else t.text;assert t.current()['displayName']==wanted_name and t.current()['source']==wanted_source;x.original();history('undo');assert t.current()['displayName']==(t.name if mode=='late'else t.original_name)and t.current()['source']==(t.text if mode=='late'else t.original_source);history('redo');assert t.current()['displayName']==wanted_name and t.current()['source']==wanted_source;f.invoke('saveDraft',{});restart(4);assert not private()and t.current()['displayName']==wanted_name and t.current()['source']==wanted_source;x.original();f.checked('shared paired Undo/Redo/cold changes both texts together with unchanged owned IDs/contracts/connections')
 if mode=='compiler':
  invalid='UnknownV666PairedSourceSymbol();\n'+wanted_source;name('컴파일 검사 이름');value(invalid);save();assert not private()and t.current()['displayName']=='컴파일 검사 이름'and t.current()['source']==invalid;r=review();saved=checkpoint.read_bytes();mark=len(f.traffic);r.locator('#confirm').click();f.idle();raw=[f.state(),f.traffic[mark:]];assert 'CS0103'in json.dumps(raw)and'UnknownV666PairedSourceSymbol'in json.dumps(raw);assert checkpoint.read_bytes()==saved;x.original();(f.case/'compiler-failure.json').write_text(json.dumps(raw,ensure_ascii=False));r.locator('[data-reject]').click();name(wanted_name);value(wanted_source);save();assert not private();f.checked('paired compiler rejection preserves verbatim CS0103 and both stored draft texts/originals until explicit correction')
 r=review();r.locator('[data-reject]').click();x.original();r=review();p=f.project/t.graph_file;physical=p.read_bytes();saved=checkpoint.read_bytes();p.write_bytes(physical+b' ')
 try:r.locator('#confirm').click();f.idle();assert p.read_bytes()==physical+b' 'and checkpoint.read_bytes()==saved;assert all(path.read_bytes()==raw for path,raw in x.physical.items()if path!=p)
 finally:p.write_bytes(physical)
 if r.is_visible():r.locator('[data-reject]').click()
 r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();t.physical_confirmed(wanted_name,wanted_source);result=12 if wanted_source==t.late else 11;x.build('paired-text-execution',result,'body\n'+str(result));restart(5);assert not private()and t.current()['displayName']==wanted_name and t.current()['source']==wanted_source;t.physical_confirmed(wanted_name,wanted_source);assert not f.errors and not f.external,(f.errors,f.external);f.page.screenshot(path=str(f.case/'paired-final.png'),timeout=5000,full_page=True);f.checked('Review cancel/post-Review physical CAS/new Confirm/actual execution/cold changes only authored display name/body; all other originals fixed')
 if mode=='normal':
  files={p:p.read_bytes()for p in x.physical};name(wanted_name);value(wanted_source);assert has('rename',wanted_name)and has('source',wanted_source);save();restart(6);assert not private()and t.current()['displayName']==wanted_name and t.current()['source']==wanted_source and all(p.read_bytes()==raw for p,raw in files.items());save();restart(7);assert not private()and all(p.read_bytes()==raw for p,raw in files.items());f.checked('unchanged paired Save and repeated empty Save/cold retain complete receipt without physical writes or new IDs')
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
print('TEXT_PAIR_RECOVERY_FIXTURE',f.case,flush=True)
