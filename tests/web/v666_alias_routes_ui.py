"""Original output-name editor and explicit next connections share one atomic draft."""
import ast,copy,json,pathlib,sys,time,traceback,uuid
from playwright.sync_api import sync_playwright,expect
import v666_alias_routes_fixture as t
x=t.x;f=t.f;mode=sys.argv[3];node=t.node;_held={};_interceptor=None
for file,names in [('v666_async_transition_ui.py',{'panel','open_graph'}),('v666_alias_source_ui.py',{'private','show','focus','reveal','naming','selected_alias','bind_alias','save','restart','history','review'}),('v666_route_group_recovery_ui.py',{'connect','disconnect','stage'})]:
 p=pathlib.Path(__file__).with_name(file);exec(compile(ast.Module(body=[n for n in ast.parse(p.read_text()).body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),str(p),'exec'))
def has(routes):return {v['node']:v['text']for _,v in private()if v.get('type')=='route'}==routes
def has_alias(name):return any(v.get('type')=='local-alias'and json.loads(v['text'])['name']==name for _,v in private())
def typed():return [(key,v)for key,v in private()if v.get('type')]
def main():
 global _interceptor
 show();stage(t.selected);naming(t.name);bind_alias();alias_id=selected_alias()['id'];assert len(typed())==5 and has(t.selected)and checkpoint.read_bytes()==before;x.original()
 restart(1);assert has(t.selected)and has_alias(t.name)and len(typed())==5
 if mode=='baseline':
  held=copy.deepcopy(private());save();assert private()==held and checkpoint.read_bytes()==before and t.current()==t.original and not t.aliases();d=t.read();q=dict(action='authorBatch',id=t.graph,attempt=uuid.uuid4().hex,checkpointHash=d['checkpointHash'],sourceProof=x.proof(d),edits=t.edits(t.selected)+[dict(action='aliasPlan',node='$locals',definition=dict(aliases=[selected_alias()],bindings=[dict(kind='exit',name='return',valueJson=json.dumps(dict(local=alias_id)))]))]);assert not f.invoke('blueprint',q,False)['result']['ok'];assert checkpoint.read_bytes()==before;x.original();f.checked('published dc230cb5 UI/native reject actual output name/consumer plus three explicit next edits, retaining all inputs/originals');return
 f.checked('five authored output-name/consumer and next inputs survive cold without changing original C# bytes or IDs')
 if mode=='conflict':
  d=t.read();f.invoke('blueprint',dict(action='route',id=t.graph,basis=d['basis'],node='third',port='next',to=''));f.invoke('saveDraft',{});held=checkpoint.read_bytes();peer=t.current();save();assert has(t.selected)and has_alias(t.name)and checkpoint.read_bytes()==held and t.current()==peer and not t.aliases();restart(2);save();assert has(t.selected)and has_alias(t.name)and checkpoint.read_bytes()==held and t.current()==peer and not t.aliases();x.original();f.checked('peer checkpoint rejects the entire alias/route candidate on Save/retry/cold without partial application');return
 if mode=='storage':
  checkpoint.chmod(0o400)
  try:save();assert has(t.selected)and has_alias(t.name)and checkpoint.read_bytes()==before and t.current()==t.original and not t.aliases();x.original()
  finally:checkpoint.chmod(0o600)
  stage(t.late);naming(t.late_name);restart(2);assert has(t.late)and has_alias(t.late_name);f.checked('actual write denial retains all inputs; explicit same-storage name and route corrections survive cold')
 if mode in ['loss','late']:
  requests=set();queries=set();paused={};lost=[]
  def interrupt(route):
   body=route.request.post_data_json
   if body.get('op')=='invoke'and body.get('endpoint')=='blueprint':
    a=body.get('input',{}).get('action')
    if a=='authorBatch':requests.add(body['requestId'])
    elif requests and a=='settledAuthorBatch':queries.add(body['requestId'])
   response=route.fetch();payload=response.json()
   if mode=='late'and not paused and any(r.get('ok')and r.get('requestId')in requests for r in payload.get('results',[])):paused.update(route=route,response=response);_held.update(paused);return
   if mode=='loss':
    for r in payload.get('results',[]):
     if r['requestId']in requests|queries:rid=r['requestId'];lost.append(rid);r.clear();r.update(requestId=rid,ok=False,error={'code':'transport-interrupted'})
   route.fulfill(response=response,json=payload)
  _interceptor=interrupt;f.page.route('**/api/request',interrupt);panel().locator('[data-bp-save]').click();deadline=time.monotonic()+120
  while time.monotonic()<deadline:
   if paused or requests and any(r in queries for r in lost):break
   f.page.wait_for_timeout(30)
  assert len(requests)==1
  if mode=='late':assert paused;stage(t.late,False);naming(t.late_name,False);paused['route'].fulfill(response=paused['response']);_held.clear();f.page.unroute('**/api/request',interrupt);f.idle();assert has(t.late)and has_alias(t.late_name)
  else:assert any(r in queries for r in lost);f.page.unroute('**/api/request',interrupt);f.idle();assert has(t.selected)and has_alias(t.name)
  restart(3);mark=len(f.traffic);save()
  if typed():save()
  assert not private();writes=[r['invoke']['input']for r in f.traffic[mark:]if r.get('invoke',{}).get('endpoint')=='blueprint'and r['invoke']['input'].get('action')=='authorBatch']
  if mode=='loss':assert not writes,writes
  else:assert writes and all(e.get('to')==t.late[e['node']]for q in writes for e in q['edits']if e['action']=='route')
  f.checked('combined '+mode+' receipt separates accepted route/name choices and late edits without replay after cold')
 else:save();assert not private()
 routes=t.late if mode in ['storage','late']else t.selected;name=t.late_name if mode in ['storage','late']else t.name;assert t.current()==routes and t.aliases()[0]['id']==alias_id and t.aliases()[0]['name']==name and json.loads(t.read()['exits'][0]['valueJson'])==dict(local=alias_id);x.original()
 if mode=='repeat':
  save();restart(8);assert not private()and t.current()==routes and t.aliases()[0]['id']==alias_id;naming(name);save();restart(9);assert not private()and t.current()==routes and t.aliases()[0]['id']==alias_id;x.original();f.checked('empty and same-name repeated saves preserve the complete checkpoint and exact C# across cold')
 if mode not in ['normal','package']:
  f.invoke('saveDraft',{});restart(4);assert not private()and t.current()==routes and t.aliases()[0]['name']==name;x.original();assert not f.errors and not f.external;f.page.screenshot(path=str(f.case/'alias-routes-checkpoint.png'),timeout=5000);f.checked('full candidate and original C# survive another cold; physical publication remains separate');return
 if mode=='normal':
  history('undo');assert t.current()==t.original and not t.aliases();history('redo');assert t.current()==routes and t.aliases()[0]['name']==name;restart(4);assert not private();x.original();f.checked('one shared Undo/Redo restores route group, alias ID/name/source and consumer together')
  r=review();r.locator('[data-reject]').click();x.original();r=review();p=f.project/t.graph_file;raw=p.read_bytes();held=checkpoint.read_bytes();p.write_bytes(raw+b' ')
  try:r.locator('#confirm').click();f.idle();assert p.read_bytes()==raw+b' 'and checkpoint.read_bytes()==held and all(p.read_bytes()==v for p,v in t.physical.items()if p!=f.project/t.graph_file)
  finally:p.write_bytes(raw)
  if r.is_visible():r.locator('[data-reject]').click()
 r=review();r.locator('#confirm').click();expect(r).to_be_hidden(timeout=120000);f.idle();t.physical_confirmed(name,routes,alias_id);x.build('alias-routes-execution',*t.result(routes));restart(5);assert not private()and t.current()==routes;t.physical_confirmed(name,routes,alias_id);assert not f.errors and not f.external;f.checked('reviewed Confirm and real execution publish the explicit next order and value 10 with unchanged C# bytes/contracts')
 if mode=='normal':
  files={p:p.read_bytes()for p in t.physical};naming(name);save();restart(6);assert not private()and t.aliases()[0]['id']==alias_id and all(p.read_bytes()==v for p,v in files.items());save();restart(7);assert not private()and all(p.read_bytes()==v for p,v in files.items());f.checked('same-value/empty Save and cold preserve stable storage and physical originals')
 f.page.screenshot(path=str(f.case/'alias-routes-final.png'),timeout=5000)

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
print('ALIAS_ROUTES_FIXTURE',f.case,flush=True)
