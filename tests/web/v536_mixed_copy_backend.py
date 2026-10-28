"""Atomic same-owner declaration and new-copy candidate API, isolated real engine; no account/inference/run."""
import json,re,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-mixed-copy-'));project=case/'owned project';project.mkdir();storage=case/'profile';storage.mkdir();n='Owned.Elements::';id=n+'Monster'
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
items['Unit']=('object','object '+n+'Unit {use schema '+n+'Vitals;data HP=100;provide '+n+'Donor with '+n+'DonorBody;}')
items['DefaultChild']=('object','object '+n+'DefaultChild extends '+n+'Unit {module '+n+'Rules;}')
items['SlotBody']=('implementation','implementation '+n+'SlotBody for '+n+'Slot (long amount,out long slotCount,out bool slotReady) -> long {description "원본 구현 한글";import '+n+'Donor as Gift (long,out long,out bool) -> long in '+n+'Unit;body common "Slot.csbody";body windows "SlotWindows.csbody";}')
items['MainBody']=('implementation',items['MainBody'][1].replace(' in '+id+';',' in '+n+'Slime;'))
items['Vitals']=('schema','schema '+n+'Vitals {field HP single general long;}')
for name,(kind,text) in items.items():(project/(name+'.celem')).write_text(text)
(project/'Main.csbody').write_text('return checked((int)calls.Slot.Invoke(5,out long count,out bool ready));');(project/'Slot.csbody').write_text('slotCount=amount+1;slotReady=false;return amount+3;');(project/'Donor.csbody').write_text('count=input*2;active=true;return input+20;');(project/'project.cproj').write_text('project Owned.Elements version "1" {standalone true;entry '+n+'Main;'+''.join('element '+name+' '+kind+' "'+name+'.celem";' for name,(kind,text) in items.items())+'registry Confectory.Build.DotNet "'+str(repo/'targets/dotnet/pack.cpack')+'";dependency Confectory.Build.DotNet version "0.1.0";target portable Confectory.Build.DotNet::Portable;target linux Confectory.Build.DotNet::Linux;}')
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
def originals():return all((project/k).read_bytes()==v for k,v in original.items())
def schema():invoke('select',{'id':id});invoke('schema',{'id':id});return state()['schema']
try:
 start(0);id=n+'Slime';invoke('select',{'id':id});invoke('saveDraft',{});d=schema();new=n+'MixedCopy';prepared=invoke('blueprint',{'action':'readImplementationCopy','id':id,'function':n+'Slot','source':n+'AliasBody','target':'common','implementation':new,'revision':d['revision'],'hash':d['textHash']})['result']['result'];row={'function':n+'Slot','implementation':new,'copySource':n+'AliasBody','copyTarget':'common','fingerprint':prepared['fingerprint'],'basis':prepared['basis'],'edits':[{'type':'source','node':'body','text':'slotCount=amount+5;slotReady=true;return amount+70;'}]};declaration={'id':id,'hash':d['textHash'],'changes':[{'type':'description','text':'함께 저장한 설명'},{'type':'scalar','path':['HP'],'nativeType':'long','valueJson':'9007199254740993'}]};command={'action':'applySlots','id':id,'rows':[row],'declaration':declaration};before=state()['draft']['text']
 for boundary in ['owner','hash','type','wrong-value','structure','nested','unknown','copy-node','duplicate','extra-copy']:
  bad=json.loads(json.dumps(command))
  if boundary=='owner':bad['declaration']['id']=n+'Unit'
  elif boundary=='hash':bad['declaration']['hash']='0'*64
  elif boundary=='type':bad['declaration']['changes'][1]['nativeType']='double'
  elif boundary=='wrong-value':bad['declaration']['changes'][1]['valueJson']='"text is not a long"'
  elif boundary=='structure':bad['declaration']['changes'][0]={'type':'parent','parent':n+'Unit'}
  elif boundary=='nested':bad['declaration']['changes'][1]['path'].append('child')
  elif boundary=='unknown':bad['declaration']['text']='object '+id+' {}'
  elif boundary=='copy-node':bad['rows'][0]['edits'][0]['node']='not-owned'
  elif boundary=='duplicate':bad['declaration']['changes'].append(bad['declaration']['changes'][0])
  else:bad['rows'].append(bad['rows'][0])
  invoke('blueprint',bad,False);assert originals();assert schema()['description']==d['description'];assert state()['draft']['text']==before;assert not invoke('blueprint',{'action':'list','feature':n+'Slot','query':new+'/body:'})['result']['result']['rows']
 checked('혼합 owner/hash/schema/type/구조/중복/복사 본문 위조 10개는 선언·새 membership·소스를 모두 미적용한다')
 result=invoke('blueprint',command)['result']['result'];assert result['atomic'] and result['checkpointSaved'];d=schema();assert d['description']=='함께 저장한 설명';assert '9007199254740993' in state()['draft']['text'];g=invoke('blueprint',{'action':'read','id':new+'/body:common','owner':id,'ownerHash':d['textHash']})['result']['result'];assert g['nodes'][0]['source']==row['edits'][0]['text'];assert originals();checked('실제 한 후보/CAS로 설명·64비트 기본값·새 복사 선언/import/graph/본문을 저장하고 원본·부모 소스를 유지한다')
 settled={'action':'settledSlots','id':id,'rows':[row],'declaration':declaration};assert invoke('blueprint',settled)['result']['result']['settled'];bad={k:v for k,v in settled.items() if k!='declaration'};assert not invoke('blueprint',bad)['result']['result']['settled'];bad=json.loads(json.dumps(settled));bad['declaration']['changes'][0]['text']='다른 시도';assert not invoke('blueprint',bad)['result']['result']['settled'];checked('복사 receipt는 같은 선언 계획까지 결부하며 누락·다른 계획을 이미 저장한 것으로 승인하지 않는다')
 stop();start(1);d=schema();assert d['description']=='함께 저장한 설명' and '9007199254740993' in state()['draft']['text'];assert invoke('blueprint',settled)['result']['result']['settled'];g=invoke('blueprint',{'action':'read','id':new+'/body:common','owner':id,'ownerHash':d['textHash']})['result']['result'];assert g['nodes'][0]['source']==row['edits'][0]['text'];assert originals();checked('cold 복원에서 혼합 선언·복사 본문·결부된 저장 receipt를 함께 복구한다')
 ids=g['reviewIds'];invoke('reviewGroup',{'ids':ids,'target':'linux'});assert state()['review']['status']=='ready'
 review=state()['review'];result=invoke('confirmGroup',{'ids':ids,'token':review['token']})['result']['result'];assert result['sourceConfirmed'],state()['logs'];changed={name for name,b in original.items() if (project/name).read_bytes()!=b};assert changed=={'Slime.celem','project.cproj'},changed;checked('명시적 compiler Confirm은 새 복사 파일과 해당 owner/등록만 반영하고 기존 donor/부모/다른 대상은 byte 보존한다')
except Exception:
 (case/'failure.json').write_text(json.dumps({'checks':checks,'state':{k:v for k,v in state().items() if k in ['logs','sourceError','review']},'evidence':str(case)},ensure_ascii=False,indent=2));print('EVIDENCE '+str(case),flush=True);raise
finally:stop()
print(json.dumps({'checks':checks,'actualEngine':True,'nativeWindows':False,'accountOrInference':False,'projectRun':False,'evidence':str(case)},ensure_ascii=False,indent=2))
