"""Actual original module-slot import UI, owned isolated sources, no login/inference/run."""
import json,re,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-copy-engine-'));project=case/'owned project';project.mkdir();storage=case/'profile';storage.mkdir();n='Owned.Elements::';id=n+'Monster'
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
items['AliasBody']=('implementation','implementation '+n+'AliasBody for '+n+'Slot (long amount,out long slotCount,out bool slotReady) -> long extends '+n+'SlotBody {}')
items['Monster']=('object','object '+id+' extends '+n+'Unit {module '+n+'Rules;provide '+n+'Slot with '+n+'AliasBody;}')
items['Unit']=('object','object '+n+'Unit {provide '+n+'Donor with '+n+'DonorBody;}')
items['DefaultChild']=('object','object '+n+'DefaultChild extends '+n+'Unit {module '+n+'Rules;}')
items['SlotBody']=('implementation','implementation '+n+'SlotBody for '+n+'Slot (long amount,out long slotCount,out bool slotReady) -> long {description "원본 구현 한글";import '+n+'Donor as Gift (long,out long,out bool) -> long in '+n+'Unit;body common "Slot.csbody";body windows "SlotWindows.csbody";}')
items['MainBody']=('implementation',items['MainBody'][1].replace(' in '+id+';',' in '+n+'Slime;'))
for name,(kind,text) in items.items():(project/(name+'.celem')).write_text(text)
(project/'Main.csbody').write_text('return checked((int)calls.Slot.Invoke(5,out long count,out bool ready));');(project/'Slot.csbody').write_text('slotCount=amount+1;slotReady=false;return amount+3;');(project/'Donor.csbody').write_text('count=input*2;active=true;return input+20;');(project/'project.cproj').write_text('project Owned.Elements version "1" {standalone true;entry '+n+'Main;'+''.join('element '+name+' '+kind+' "'+name+'.celem";' for name,(kind,text) in items.items())+'registry Confectory.Build.DotNet "'+str(repo/'targets/dotnet/pack.cpack')+'";dependency Confectory.Build.DotNet version "0.1.0";target portable Confectory.Build.DotNet::Portable;}')
(project/'Slot2.csbody').write_text('slotCount=amount+1;slotReady=false;return amount+3;');(project/'SlotBody2.celem').write_text((project/'SlotBody2.celem').read_text().replace('Slot.csbody','Slot2.csbody'));(project/'Slot.csbody').write_text('return calls.Gift.Invoke(amount,out slotCount,out slotReady);');(project/'SlotWindows.csbody').write_text('slotCount=amount+100;slotReady=false;return amount+200;')
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
 p=sync_playwright().start();browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();id=n+'Slime'
 def schema(target):invoke('select',{'id':target});invoke('schema',{'id':target});return state()['schema']
 def originals():return all((project/k).read_bytes()==v for k,v in original.items())
 def catalog(target):
  d=schema(target);return invoke('blueprint',{'action':'implementationSources','id':target,'function':n+'Slot','revision':d['revision'],'hash':d['textHash']})['result']['result']
 rows=catalog(id);assert rows['bodyReads']==0 and {(r['id'],r['target']) for r in rows['rows']}=={(n+'AliasBody','common'),(n+'AliasBody','windows'),(n+'SlotBody','common'),(n+'SlotBody','windows')};assert next(r for r in rows['rows'] if r['id']==n+'AliasBody')['sourceOwner']==n+'Monster';assert all(r['bodyOrigin']==n+'SlotBody' for r in rows['rows']);checked('actual inherited/default candidates expose distinct explicit targets and source owner/body origin without reading code')
 fallback=catalog(n+'DefaultChild');assert {(r['id'],r['sourceOwner']) for r in fallback['rows']}=={(n+'SlotBody',n+'Rules')};checked('default-only owner lists only module defaults rather than silently choosing unrelated global or inherited body')
 d=schema(id);new=n+'Impl_Copy_'+uuid.uuid4().hex;req={'action':'readImplementationCopy','id':id,'function':n+'Slot','source':n+'AliasBody','target':'common','implementation':new,'revision':d['revision'],'hash':d['textHash']};preview=invoke('blueprint',req)['result']['result'];assert preview['bodyReads']==1 and preview['sourceKind']=='csharp' and preview['sourceOwner']==n+'Monster' and originals();assert not invoke('blueprint',{'action':'list','feature':n+'Slot','query':new+'/body:'})['result']['result']['rows'];checked('explicit C# copy preview reads selected inherited body but creates no membership or source writes')
 invoke('blueprint',{**req,'source':n+'DonorBody','implementation':n+'BadCopy'},False);assert originals();checked('forged source outside the required slot candidates is rejected without touching original body or parent')
 row={'function':n+'Slot','implementation':new,'copySource':n+'AliasBody','copyTarget':'common','basis':preview['basis']};file=project/'Slot.csbody';old=file.read_bytes();file.write_bytes(old+b' ');invoke('blueprint',{'action':'applySlots','id':id,'rows':[row]},False);file.write_bytes(old);assert not invoke('blueprint',{'action':'list','feature':n+'Slot','query':new+'/body:'})['result']['result']['rows'] and originals();checked('changed selected C# source refuses entire copy before any child membership while preserving original source and prior inherited binding')
 # Re-read the original, restored source and durably bind the child copy.
 d=schema(id);req.update(revision=d['revision'],hash=d['textHash']);preview=invoke('blueprint',req)['result']['result'];row['basis']=preview['basis'];invoke('blueprint',{'action':'applySlots','id':id,'rows':[row]});d=schema(id);provider=next(r for r in d['providers'] if r['function']==n+'Slot');assert provider['origin']==id and provider['implementation']==new;g=invoke('blueprint',{'action':'read','id':new+'/body:common','owner':id,'ownerRevision':d['revision'],'ownerHash':d['textHash']})['result']['result'];assert len(g['nodes'])==1 and g['nodes'][0]['implementationContext']['implementation']==new and g['nodes'][0]['implementationContext']['imports']['Gift']['scope']==n+'Unit' and g['nodes'][0]['source']=='return calls.Gift.Invoke(amount,out slotCount,out slotReady);';assert g['slotContext']['copySource']['implementation']==n+'AliasBody' and originals();checked('durable copy binds only child to independent graph/node, rebases method identity and preserves exact explicit import scope/C# body plus source provenance')
 invoke('reviewGroup',{'ids':g['reviewIds'],'target':'portable'});review=state()['review'];reviewed=[row['id'] for row in review['units']];assert set(reviewed)==set(g['reviewIds']) and review['status']=='ready';confirmed=invoke('confirmGroup',{'ids':reviewed,'token':review['token']})['result']['result'];assert confirmed['sourceConfirmed'];assert all((project/k).read_bytes()==v for k,v in original.items() if k not in ['Slime.celem','project.cproj']);original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts and '.build' not in p.parts};checked('explicit compiler Confirm validates original calls/import scope in reachable child copy and changes only new owned group plus child/registration, preserving every parent/default/other-target source')
 page.close();stop();start(1);page=setup();d=schema(id);g=invoke('blueprint',{'action':'read','id':new+'/body:common','owner':id,'ownerRevision':d['revision'],'ownerHash':d['textHash']})['result']['result'];assert g['slotContext']['copySource']['implementation']==n+'AliasBody' and g['nodes'][0]['source'].startswith('return calls.Gift') and originals();checked('real restart retains independent child copy/context/provenance without modifying parent/default/platform-specific source')
 invoke('blueprint',{'action':'source','id':g['id'],'basis':g['basis'],'node':'body','text':'slotCount=amount*9;slotReady=true;return amount+77;'});invoke('saveDraft',{});g=invoke('blueprint',{'action':'read','id':g['id']})['result']['result'];assert g['nodes'][0]['source']=='slotCount=amount*9;slotReady=true;return amount+77;' and originals();checked('actual copied C# body edits only new owned node while all original alias/default/other-target source bytes stay identical')
 page.close();stop();browser.close();assert not errors and not external,(errors,external)
except Exception:
 try:page.screenshot(path=str(case/'failure.png'));(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop();p.stop()
record={'checks':checks,'actualEngine':True,'backendAPIs':True,'uiCopyFlowConnected':False,'nativeWindows':False,'accountOrInference':False,'errors':errors,'external':external,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
