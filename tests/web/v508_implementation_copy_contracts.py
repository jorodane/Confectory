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
(project/'Slot.celem').write_text('function '+n+'Slot (long amount) -> long {provide '+n+'Slot with '+n+'SlotBody;}')
(project/'SlotBody.celem').write_text('implementation '+n+'SlotBody for '+n+'Slot (long amount) -> long {description "원본 Blueprint";blueprint common "Slot.graph.json";body windows "SlotWindows.csbody";}')
(project/'AliasBody.celem').write_text('implementation '+n+'AliasBody for '+n+'Slot (long amount) -> long extends '+n+'SlotBody {}')
(project/'Rules.celem').write_text('module '+n+'Rules {require '+n+'Slot (long) -> long;default '+n+'Slot with '+n+'SlotBody;}')
(project/'MainBody.celem').write_text('implementation '+n+'MainBody for '+n+'Main () -> int {import '+n+'Slot as Slot (long) -> long in '+n+'Slime;body common "Main.csbody";}');(project/'Main.csbody').write_text('return checked((int)calls.Slot.Invoke(5));');(project/'SlotWindows.csbody').write_text('return amount+200;')
def metadata(v):
 proc=subprocess.run(['/workspace/toolchains/dotnet-10.0.401/dotnet',str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(v),capture_output=True,text=True);result=json.loads(proc.stdout);assert result.get('ok'),result;return result['result']
prepared=metadata({'operation':'blueprintPrepareFeature','id':n+'Slot','text':'function '+n+'Slot (long amount) -> long {}','implementation':n+'SlotBody','graphPath':'Slot.graph.json','nodePath':'body.node.json'});source_graph=prepared['graph'];source_graph['profile']='sync-acyclic-implicit-v1';source_graph['nodes'][0]['intent']='원본 첫 동작';source_graph['nodes'].append({'id':'extra','kind':'code','control':'next','intent':'원본 두 번째 동작','signature':{'args':[{'name':'value','type':'long'}],'return':'long'},'arguments':{'value':{'node':'body'}},'implementation':'extra.node.json'});source_graph['edges']=[{'from':'body','port':'next','to':'extra'},{'from':'extra','port':'next','to':'exit:return'}];source_graph['exits']={'return':{'node':'extra'}}
definitions=metadata({'operation':'featureBlueprintNodes','featureSource':(project/'Slot.celem').read_text(),'graph':source_graph})
for node,code in [('body','return amount+1;'),('extra','return value*2;')]:
 record={'schema':1,'node':node,'definitionHash':next(d['definitionHash'] for d in definitions['nodes'] if d['id']==node),'source':code};(project/(node+'.node.json')).write_text(json.dumps(record,ensure_ascii=False))
(project/'Slot.graph.json').write_text(json.dumps(source_graph,ensure_ascii=False))

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
 def originals():return all((project/k).read_bytes()==v for k,v in original.items())
 def schema():invoke('select',{'id':id});invoke('schema',{'id':id});return state()['schema']
 d=schema();new=n+'EditedCopy';req={'action':'readImplementationCopy','id':id,'function':n+'Slot','source':n+'AliasBody','target':'common','implementation':new,'revision':d['revision'],'hash':d['textHash']};prepared=invoke('blueprint',req)['result']['result'];row={'function':n+'Slot','implementation':new,'copySource':n+'AliasBody','copyTarget':'common','basis':prepared['basis']}
 bad={'args':[{'name':'seed','type':'int'}],'returnType':'long','remap':{'amount':'seed'}};invoke('blueprint',{'action':'applySlots','id':id,'rows':[{**row,'edits':[{'type':'parameters','node':'body','text':json.dumps(bad)}]}]},False);assert originals() and not invoke('blueprint',{'action':'list','feature':n+'Slot','query':new+'/body:'})['result']['result']['rows'];checked('copy parameter transaction rejects changing connected long to int and creates no partial owned group')
 bad={'args':[{'name':'seed','type':'long'}],'returnType':'void','remap':{'amount':'seed'}};invoke('blueprint',{'action':'applySlots','id':id,'rows':[{**row,'edits':[{'type':'parameters','node':'body','text':json.dumps(bad)}]}]},False);assert originals() and not invoke('blueprint',{'action':'list','feature':n+'Slot','query':new+'/body:'})['result']['result']['rows'];checked('copy parameter transaction rejects removing a return still consumed by another copied node')
 good={'args':[{'name':'seed','type':'long'}],'returnType':'long','remap':{'amount':'seed'}};edits=[{'type':'parameters','node':'body','text':json.dumps(good)},{'type':'source','node':'body','text':'return seed+8;'}];invoke('blueprint',{'action':'applySlots','id':id,'rows':[{**row,'edits':edits}]});g=invoke('blueprint',{'action':'read','id':new+'/body:common'})['result']['result'];body=next(n for n in g['nodes'] if n['id']=='body');extra=next(n for n in g['nodes'] if n['id']=='extra');assert body['signature']['args']==[{'type':'long','name':'seed'}] and body['source']=='return seed+8;' and json.loads(body['arguments'][0]['valueJson'])=={'input':'amount'} and json.loads(extra['arguments'][0]['valueJson'])=={'node':'body'} and originals();checked('ordinary copied-node pin rename with explicit re-applied source saves atomically, keeping root input mapping, downstream value and physical originals')
 d=schema();new2=n+'StaleEditedCopy';prepared=invoke('blueprint',{**req,'source':n+'SlotBody','implementation':new2,'revision':d['revision'],'hash':d['textHash']})['result']['result'];invoke('blueprint',{'action':'applySlots','id':id,'rows':[{**row,'copySource':n+'SlotBody','implementation':new2,'basis':prepared['basis'],'edits':[{'type':'intent','node':'body','text':'새 설명 계약'}]}]});g=invoke('blueprint',{'action':'read','id':new2+'/body:common'})['result']['result'];body=next(n for n in g['nodes'] if n['id']=='body');assert body['sourceStatus']=='stale' and body['source']=='return amount+1;' and originals();checked('definition-only copied-node change retains old source as stale and never silently authorizes or restamps it for compiler Confirm')
 page.close();stop();browser.close();assert not errors and not external,(errors,external)

except Exception:
 try:page.screenshot(path=str(case/'failure.png'));(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop();p.stop()
record={'checks':checks,'actualEngine':True,'backendAPIs':True,'renderer':True,'uiCopyFlowConnected':False,'privateGraphBackendEdits':True,'nativeWindows':False,'accountOrInference':False,'errors':errors,'external':external,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
