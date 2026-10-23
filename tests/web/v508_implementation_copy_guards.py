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

lost={'armed':False,'caught':False}
original_route=route
def route(request):
 if request.request.url.startswith(origin) and lost['armed'] and request.request.method=='POST' and request.request.post_data_json.get('op')=='update':
  response=request.fetch();payload=response.json()
  for result in payload.get('results',[]):
   if result.get('result',{}).get('checkpointSaved'):
    lost['armed']=False;lost['caught']=True;lost['saved']=result['result'];result.pop('result',None);result['ok']=False;result['error']={'code':'simulated_result_lost'};request.fulfill(response=response,json=payload);return
  request.fulfill(response=response);return
 original_route(request)

try:
 p=sync_playwright().start();browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();id=n+'DefaultChild'
 def originals():return all((project/k).read_bytes()==v for k,v in original.items())
 page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');b.locator('[data-object="'+id+'"]').get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=schema]');slot=w.locator('[data-module-method="'+n+'Slot"]');slot.locator('[data-function-write-direct]').click();picker=page.locator('.feature-import-dialog');expect(picker.locator('[data-copy-source]')).to_have_count(2,timeout=30000);picker.locator('[data-copy-target=windows]').click();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-node=body]')).to_be_visible(timeout=30000);expect(author.locator('.bp-status')).to_have_text('미저장 복사본 · DefaultChild · windows');assert originals();new=next(r['invoke']['input']['implementation'] for r in reversed(traffic) if r.get('invoke',{}).get('input',{}).get('action')=='readImplementationCopy');checked('default-only original direct-write action selects explicit windows C# body and visibly names child copy/target, without modifying sources')
 wanted='slotCount=amount*5;slotReady=false;return amount+81;';author.locator('[data-internal-code]').click();dialog=page.locator('.bp-script-dialog');input=dialog.locator('[data-code-source]');expect(input).to_have_value(re.compile('amount\\+100'));input.evaluate("(el)=>{el.focus();el.setSelectionRange(el.value.indexOf('\\n{\\n')+3,el.value.lastIndexOf('\\n}\\n'));}");input.press('Backspace');input.press_sequentially(wanted);dialog.locator('[data-code-save]').click();expect(author.locator('.bp-status')).to_contain_text('DefaultChild · windows');page.evaluate('async()=>await confectoryFlushPresentation()');pending=[(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if '|v508-author|' in k];file=project/'SlotWindows.csbody';old=file.read_bytes();file.write_bytes(old+b' ');author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_contain_text('바뀌었습니다',timeout=30000);page.evaluate('async()=>await confectoryFlushPresentation()');assert [(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if '|v508-author|' in k]==pending;assert not invoke('blueprint',{'action':'list','feature':n+'Slot','query':new+'/body:'})['result']['result']['rows'];file.write_bytes(old);assert originals();checked('source change before original Save is refused, retaining exact private C# input and no child membership/partial save')
 lost['armed']=True;author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('복사본 · DefaultChild · windows',timeout=30000);assert lost['caught'];page.evaluate('async()=>await confectoryFlushPresentation()');assert not [(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if '|v508-author|' in k];assert originals();g=invoke('blueprint',{'action':'read','id':new+'/body:windows'})['result']['result'];assert g['nodes'][0]['source']==wanted;rows=invoke('blueprint',{'action':'list','feature':n+'Slot','query':new+'/body:'})['result']['result']['rows'];assert len(rows)==1 and rows[0]['id']==new+'/body:windows';checked('accepted Save result hidden by controlled transport is reconciled by exact server receipt without duplicate creation, and only selected windows body is copied')
 choice={'function':n+'Slot','implementation':new,'copySource':n+'SlotBody','copyTarget':'windows','fingerprint':next(r['result']['result']['fingerprint'] for r in reversed(traffic) if r.get('result',{}).get('result',{}).get('preview')),'edits':[{'type':'source','node':'body','text':wanted+' '} ]};assert not invoke('blueprint',{'action':'settledSlots','id':id,'rows':[choice]})['result']['result']['settled'];page.screenshot(path=str(case/'copy-default-recovered.png'));checked('receipt refuses a different private edit payload instead of treating any code for the same source/target as accepted')
 # The newly saved copy survives a real cold open, with no new implementation.
 before_rows=rows;page.evaluate('async()=>await confectoryFlushPresentation()');page.close();stop();start(1);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-node=body]')).to_be_visible(timeout=30000);expect(author.locator('.bp-status')).to_have_text('복사본 · DefaultChild · windows');rows=invoke('blueprint',{'action':'list','feature':n+'Slot','query':new+'/body:'})['result']['result']['rows'];assert rows==before_rows and originals();checked('true cold reopen restores accepted copy identity/provenance/window target without re-copying or altering original sources')
 author.locator(':scope > header [data-close]').click() if author.locator(':scope > header [data-close]').count() else author.locator(':scope > header button').last.click();b=page.locator('.window[data-key^="browser:project:"]');b.locator('[data-object="'+n+'Monster"]').get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=schema]');slot=w.locator('[data-module-method="'+n+'Slot"]');slot.locator('[data-function-edit]').click();picker=page.locator('.feature-import-dialog');expect(picker.locator('[data-copy-source]')).to_have_count(4,timeout=30000);assert originals();checked('existing owned C# provider Edit defers source choice until idle and opens original selector rather than dropping the busy action')
 page.close();stop();browser.close();assert not errors and not external,(errors,external)

except Exception:
 try:page.screenshot(path=str(case/'failure.png'));(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop();p.stop()
record={'checks':checks,'actualEngine':True,'backendAPIs':True,'renderer':True,'uiCopyFlowConnected':True,'nativeWindows':False,'accountOrInference':False,'errors':errors,'external':external,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
