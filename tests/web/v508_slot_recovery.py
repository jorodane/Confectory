"""Actual original module-slot import UI, owned isolated sources, no login/inference/run."""
import json,re,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-slot-recovery-'));project=case/'owned project';project.mkdir();storage=case/'profile';storage.mkdir();n='Owned.Elements::';id=n+'Monster'
items={
'Main':('function','function '+n+'Main () -> int {provide '+n+'Main with '+n+'MainBody;}'),
'MainBody':('implementation','implementation '+n+'MainBody for '+n+'Main () -> int {import '+n+'Slot as Slot (long,out long,out bool) -> long in '+id+';body common "Main.csbody";}'),
'Unit':('object','object '+n+'Unit {}'),'Monster':('object','object '+id+' extends '+n+'Unit {module '+n+'Rules;}'),'Slime':('object','object '+n+'Slime extends '+id+' {}'),
'Slot':('function','function '+n+'Slot (long amount,out long slotCount,out bool slotReady) -> long {provide '+n+'Slot with '+n+'SlotBody;}'),
'SlotBody':('implementation','implementation '+n+'SlotBody for '+n+'Slot (long amount,out long slotCount,out bool slotReady) -> long {body common "Slot.csbody";}'),
'Donor':('function','function '+n+'Donor (long input,out long count,out bool active) -> long {description "참조할 기능 한글";provide '+n+'Donor with '+n+'DonorBody;}'),
'DonorBody':('implementation','implementation '+n+'DonorBody for '+n+'Donor (long input,out long count,out bool active) -> long {body common "Donor.csbody";}'),
'Wrong':('function','function '+n+'Wrong (long input,ref long count,out bool active) -> long {}'),
'Rules':('module','module '+n+'Rules {require '+n+'Slot (long,out long,out bool) -> long;default '+n+'Slot with '+n+'SlotBody;}')}
items['Slot2']=('function','function '+n+'Slot2 (long amount,out long slotCount,out bool slotReady) -> long {provide '+n+'Slot2 with '+n+'SlotBody2;}')
items['SlotBody2']=('implementation','implementation '+n+'SlotBody2 for '+n+'Slot2 (long amount,out long slotCount,out bool slotReady) -> long {body common "Slot.csbody";}')
items['Rules']=('module','module '+n+'Rules {require '+n+'Slot (long,out long,out bool) -> long;default '+n+'Slot with '+n+'SlotBody;require '+n+'Slot2 (long,out long,out bool) -> long;default '+n+'Slot2 with '+n+'SlotBody2;}')
for name,(kind,text) in items.items():(project/(name+'.celem')).write_text(text)
(project/'Main.csbody').write_text('return checked((int)calls.Slot.Invoke(5,out long count,out bool ready));');(project/'Slot.csbody').write_text('slotCount=amount+1;slotReady=false;return amount+3;');(project/'Donor.csbody').write_text('count=input*2;active=true;return input+20;');(project/'project.cproj').write_text('project Owned.Elements version "1" {standalone true;entry '+n+'Main;'+''.join('element '+name+' '+kind+' "'+name+'.celem";' for name,(kind,text) in items.items())+'registry Confectory.Build.DotNet "'+str(repo/'targets/dotnet/pack.cpack')+'";dependency Confectory.Build.DotNet version "0.1.0";target portable Confectory.Build.DotNet::Portable;}')
original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file()};env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET='/workspace/toolchains/dotnet-10.0.401/dotnet');env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
def stop():
 global host,log
 if host and host.poll() is None:os.killpg(host.pid,signal.SIGTERM)
 if host:host.wait(timeout=15)
 if log:log.close()
def start(i):
 global host,log,origin,token,url
 file=case/f'host-{i}.log';log=file.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 for _ in range(600):
  urls=[l.split(' ',1)[1] for l in file.read_text().splitlines() if l.startswith('CONFECTORY_WEB_UI ')]
  if urls:url=urls[-1];origin,token=url.split('/#');return
  assert host.poll() is None,file.read_text()[-1000:];time.sleep(.05)
 raise AssertionError('startup timeout')
def raw(body):return json.load(urllib.request.urlopen(urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token}),timeout=30))
def mount():
 for _ in range(300):
  v=raw({'op':'mount'})
  if v.get('ok'):return v
  assert v.get('error',{}).get('code')=='busy',v;time.sleep(.02)
 raise AssertionError('busy transport')
def state():
 v=mount()
 try:return v['state']
 finally:raw({'op':'dispose','view':v['view']})
def invoke(endpoint,body,success=True):
 for _ in range(4):
  v=mount();rid=uuid.uuid4().hex
  try:
   assert raw({'op':'invoke','view':v['view'],'scope':v['scope'],'expectedRevision':v['revision'],'requestId':rid,'endpoint':endpoint,'input':body})['ok']
   for _ in range(600):
    u=raw({'op':'update','view':v['view'],'scope':v['scope']});rows=[r for r in u.get('results',[]) if r['requestId']==rid]
    if rows:break
    time.sleep(.01)
   assert rows
   if rows[0].get('error',{}).get('code')=='stale_revision':continue
   assert bool(rows[0].get('ok')) is success,rows;return {'result':rows[0],'state':u.get('state')}
  finally:raw({'op':'dispose','view':v['view']})
 raise AssertionError('admission failed')
traffic=[];injected=0

def checked(text):
 checks.append(text);(case/'progress.json').write_text(json.dumps(checks,indent=2));print('PASS '+text,flush=True)
def observe(response):
 try:
  request=response.request.post_data_json
  if not isinstance(request,dict):return
  if request.get('op')=='invoke':traffic.append({'invoke':request})
  elif request.get('op')=='update':
   for result in response.json().get('results',[]):
    if not any(row.get('result',{}).get('requestId')==result['requestId'] for row in traffic):traffic.append({'result':result})
 except Exception:pass

def route(request):
 global injected
 if not request.request.url.startswith(origin):external.append(request.request.url);request.abort();return
 body=request.request.post_data_json if request.request.method=='POST' else None
 if isinstance(body,dict) and body.get('op')=='invoke' and body.get('endpoint')=='reviewDraft' and False:
  # Actual server rejects an explicitly stale transport revision before execution.
  injected+=1;body['expectedRevision']-=1;request.continue_(post_data=json.dumps(body));return
 request.continue_()

def setup():
 page=browser.new_page(viewport={'width':1280,'height':900});page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',observe);page.route('**/*',route);goto_editor(page,url);return page

try:
 p=sync_playwright().start();browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');b.locator('[data-object="'+id+'"]').get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=schema]')
 def pending():
  page.wait_for_function("()=>typeof confectoryFlushPresentation==='function'");page.evaluate('async()=>await confectoryFlushPresentation()');return [(k,v) for k,v in state()['presentation']['inputs']['schema'] if '|element|implementation:' in k]
 def providers():
  data=state()
  if data.get('schema') is None:schema_of(id);data=state()
  return {r['function']:r['implementation'] for r in data['schema'].get('providers',[]) if r['origin']==id}
 def original_same():return all((project/k).read_bytes()==v for k,v in original.items())
 def choose(name):
  slot=w.locator('[data-module-method="'+n+name+'"]');expect(slot).to_be_visible(timeout=30000);slot.locator('[data-function-import]').click();dialog=page.get_by_role('dialog',name='기능 가져오기',exact=True);dialog.locator('[data-feature-import="'+n+'Donor"]').click();expect(slot.locator('.function-implementation-status')).to_have_text('미저장 구현')
 def remove(name):
  slot=w.locator('[data-module-method="'+n+name+'"]');slot.locator('[data-function-delete-implementation]').click();page.get_by_role('dialog',name='구현 삭제',exact=True).locator('[data-implementation-confirm]').click();expect(slot.locator('[data-function-import]')).to_be_visible()
 def schema_of(target):
  invoke('select',{'id':target});invoke('schema',{'id':target});return state()['schema']
 def edit_description(target,text):
  invoke('select',{'id':target});invoke('inspectDeclaration',{'id':target});d=state()['declaration'];invoke('editDeclaration',{'id':target,'revision':d['revision'],'hash':d['textHash'],'edit':{'action':'properties','values':{'description':text}}});return state()['draft']
 def reload_owner():
  schema_of(id);page.wait_for_function("id=>document.querySelector('.window[data-key=schema]')?.querySelector('[data-module-method]')?.dataset.moduleMethod.startsWith(id)",arg=n)
 def prepare(names):
  schema=schema_of(id);rows=[]
  for name in names:
   implementation=n+'Impl_'+uuid.uuid4().hex;result=invoke('blueprint',{'action':'readImplementation','id':id,'function':n+name,'implementation':implementation,'reference':n+'Donor','revision':schema['revision'],'hash':schema['textHash']})['result']['result'];rows.append({'function':n+name,'implementation':implementation,'reference':n+'Donor','basis':result['basis']})
  return rows
 # Preserve an existing independent saved draft before creating the new group.
 edit_description(n+'Slime','saved peer 한글');peer=state()['draft']['text'];invoke('saveDraft',{});reload_owner();rows=[]
 for fn in ['Slot','Slot2']:
  row=prepare([fn])[0];invoke('blueprint',{'action':'createImplementation','id':id,**row});rows.append(row)
 reload_owner();assert len(providers())==2
 status=invoke('browserDrafts',{'action':'status','ids':[id]})['result']['result'];invoke('select',{'id':n+'Slime'});invoke('inspectDeclaration',{'id':n+'Slime'});d=state()['declaration'];invoke('editDeclaration',{'id':d['id'],'revision':d['revision'],'hash':d['textHash'],'edit':{'action':'provide-function','function':n+'Slot','implementation':rows[0]['implementation']}});reload_owner();blocked={'action':'discard','ids':status['ids'],'revisions':[r['revision'] for r in status['rows']],'hashes':[r['hash'] for r in status['rows']],'checkpointHash':status['checkpointHash'],'ownerHash':status['ownerHash']};invoke('browserDrafts',blocked,False);reload_owner();assert len(providers())==2;checked('another declaration referencing new implementation blocks whole-group Cancel without dropping either mapping or source')
 invoke('select',{'id':n+'Slime'});invoke('inspectDeclaration',{'id':n+'Slime'});d=state()['declaration'];invoke('editDeclaration',{'id':d['id'],'revision':d['revision'],'hash':d['textHash'],'edit':{'action':'provide-function','function':n+'Slot','implementation':None}});peer=state()['draft']['text'];reload_owner()
 status=invoke('browserDrafts',{'action':'status','ids':[id]})['result']['result'];payload={'action':'discard','ids':status['ids'],'revisions':[r['revision'] for r in status['rows']],'hashes':[r['hash'] for r in status['rows']],'checkpointHash':status['checkpointHash'],'ownerHash':status['ownerHash']};invoke('browserDrafts',payload);reload_owner();graphs=[]
 for row in rows:graphs+=invoke('blueprint',{'action':'list','feature':row['function'],'query':row['implementation']+'/body:'})['result']['result']['rows']
 observed={'providers':providers(),'graphs':graphs,'rows':rows};(case/'cancel-observed.json').write_text(json.dumps(observed,indent=2));print(json.dumps({'case':str(case),'providerCount':len(providers()),'remainingGraphCount':len(graphs)}),flush=True);assert not providers() and not graphs,observed
 checked('new uncheckpointed group Cancel removes both mappings and all new membership together')
 invoke('select',{'id':n+'Slime'});assert state()['draft']['text']==peer;reload_owner();invoke('saveDraft',{});page.evaluate('async()=>await confectoryFlushPresentation()');page.close();stop();start(1);page=setup();w=page.locator('.window[data-key=schema]');expect(w.locator('[data-module-method]')).to_have_count(2,timeout=30000);assert not providers()
 for row in rows:assert not invoke('blueprint',{'action':'list','feature':row['function'],'query':row['implementation']+'/body:'})['result']['result']['rows']
 invoke('select',{'id':n+'Slime'});assert state()['draft']['text']==peer;reload_owner();checked('canceled membership stays absent after Save and real restart; independent newer peer draft survives')
 # A changed newly created implementation must never be silently discarded, even after a fresh status read.
 row=prepare(['Slot'])[0];invoke('blueprint',{'action':'createImplementation','id':id,**row});edit_description(row['implementation'],'new implementation edited by another editor');changed=state()['draft']['text'];reload_owner();status=invoke('browserDrafts',{'action':'status','ids':[id]})['result']['result'];payload={'action':'discard','ids':status['ids'],'revisions':[r['revision'] for r in status['rows']],'hashes':[r['hash'] for r in status['rows']],'checkpointHash':status['checkpointHash'],'ownerHash':status['ownerHash']};invoke('browserDrafts',payload,False);reload_owner();assert len(providers())==1;invoke('select',{'id':row['implementation']});assert state()['draft']['text']==changed;checked('fresh Cancel still rejects new group members edited after creation, preserving other editor implementation work')
 page.close();stop();browser.close()
except Exception:
 try:page.screenshot(path=str(case/'failure.png'));(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop();p.stop()
record={'checks':checks,'actualEngine':True,'nativeWindows':False,'accountOrInference':False,'errors':errors,'external':external,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
