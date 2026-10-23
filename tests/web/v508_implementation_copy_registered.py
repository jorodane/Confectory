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
lib=case/'Lib';lib.mkdir()
foreign={
'Slot':('function','function Lib::Slot (long amount,out long slotCount,out bool slotReady) -> long {provide Lib::Slot with Lib::SlotBody;}'),
'SlotBody':('implementation','implementation Lib::SlotBody for Lib::Slot (long seed,out long tally,out bool ok) -> long {description "등록 팩 구현";import Lib::Gift as Gift (long,out long,out bool) -> long in Lib::Owner;body common "Slot.csbody";body windows "SlotWindows.csbody";}'),
'Gift':('function','function Lib::Gift (long input,out long count,out bool active) -> long {provide Lib::Gift with Lib::GiftBody;}'),
'GiftBody':('implementation','implementation Lib::GiftBody for Lib::Gift (long input,out long count,out bool active) -> long {body common "Gift.csbody";}'),
'Owner':('object','object Lib::Owner {provide Lib::Gift with Lib::GiftBody;}'),
'Rules':('module','module Lib::Rules {require Lib::Slot (long,out long,out bool) -> long;default Lib::Slot with Lib::SlotBody;}')}
for name,(kind,text) in foreign.items():(lib/(name+'.celem')).write_text(text)
(lib/'pack.cpack').write_text('pack Lib version "1" {'+''.join('element '+name+' '+kind+' "'+name+'.celem";' for name,(kind,text) in foreign.items())+'}')
(lib/'Slot.csbody').write_text('return calls.Gift.Invoke(seed,out tally,out ok);');(lib/'SlotWindows.csbody').write_text('tally=seed+100;ok=false;return seed+200;');(lib/'Gift.csbody').write_text('count=input*2;active=true;return input+20;')
(project/'Monster.celem').write_text('object '+n+'Monster extends '+n+'Unit {module Lib::Rules;}')
(project/'MainBody.celem').write_text('implementation '+n+'MainBody for '+n+'Main () -> int {import Lib::Slot as Slot (long,out long,out bool) -> long in '+n+'Slime;body common "Main.csbody";}')
pfile=project/'project.cproj';pfile.write_text(pfile.read_text().replace('target portable','registry Lib "../Lib/pack.cpack";dependency Lib version "1";target portable'));foreign_original={str(p.relative_to(lib)):p.read_bytes() for p in lib.iterdir() if p.is_file()}

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
 def foreign_same():return all((lib/k).read_bytes()==v for k,v in foreign_original.items())
 def originals():return all((project/k).read_bytes()==v for k,v in original.items())
 page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');b.locator('[data-object="'+id+'"]').get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=schema]');slot=w.locator('[data-module-method="Lib::Slot"]');slot.locator('[data-function-write-direct]').click();picker=page.locator('.feature-import-dialog');expect(picker.locator('[data-copy-source]')).to_have_count(2,timeout=30000);expect(picker.locator('[data-copy-target=common] strong')).to_have_text('Lib / SlotBody · common · C#');picker.locator('[data-close]').click();assert originals() and foreign_same();checked('registered module default shows only explicit common/windows sources with pack label in original selector; closing selector changes no owned or foreign source')
 slot.locator('[data-function-write-direct]').click();picker=page.locator('.feature-import-dialog');picker.locator('[data-copy-target=common]').click();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-node=body]')).to_be_visible(timeout=30000);new=next(r['invoke']['input']['implementation'] for r in reversed(traffic) if r.get('invoke',{}).get('input',{}).get('action')=='readImplementationCopy');assert not invoke('blueprint',{'action':'list','feature':'Lib::Slot','query':new+'/body:'})['result']['result']['rows'];assert originals() and foreign_same();checked('registered C# body becomes child-owned private author preview without changing dependency membership or reading an unrelated implementation')
 wanted='tally=seed*3;ok=true;return seed+77;';author.locator('[data-internal-code]').click();dialog=page.locator('.bp-script-dialog');input=dialog.locator('[data-code-source]');expect(input).to_have_value(re.compile('calls.Gift'));input.evaluate('(el,d)=>{el.focus();el.setSelectionRange(el.value.indexOf(d[0])+3,el.value.lastIndexOf(d[1]));}',["\n{\n","\n}\n"]);page.keyboard.insert_text(wanted);dialog.locator('[data-code-save]').click();page.evaluate('async()=>await confectoryFlushPresentation()');pending=[(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if '|v508-author|' in k];old=(lib/'pack.cpack').read_bytes();(lib/'pack.cpack').write_bytes(old+b' ');author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_contain_text('바뀌었습니다',timeout=30000);page.evaluate('async()=>await confectoryFlushPresentation()');assert [(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if '|v508-author|' in k]==pending;(lib/'pack.cpack').write_bytes(old);assert originals() and foreign_same();checked('registered pack change invalidates private copy Save, retaining code and rejecting membership before any partial application')
 page.close();stop();start(1);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-node=body]')).to_be_visible(timeout=30000);author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('복사본 · Slime · common',timeout=30000);g=invoke('blueprint',{'action':'read','id':new+'/body:common'})['result']['result'];assert g['nodes'][0]['source']==wanted and g['nodes'][0]['implementationContext']['imports']['Gift']['scope']=='Lib::Owner';assert originals() and foreign_same();checked('actual restart and atomic Save preserve copied registered C# parameter names and explicit foreign import scope while all physical originals remain unchanged')
 author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=30000)
 for cb in review.locator('[data-review-id]').all():cb.check()
 if review.locator('[data-additional-changes]').count():
  review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
  if ack.count():ack.check()
 expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);assert any(r.get('result',{}).get('result',{}).get('sourceConfirmed') for r in traffic);assert all((project/k).read_bytes()==v for k,v in original.items() if k not in ['Slime.celem','project.cproj']) and foreign_same();page.screenshot(path=str(case/'registered-copy-confirmed.png'));checked('actual original Complete/Review/Confirm compiles reachable child copy with immutable registered source/function/default/other-target bytes')
 page.close();stop();browser.close();assert not errors and not external,(errors,external)

except Exception:
 try:page.screenshot(path=str(case/'failure.png'));(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop();p.stop()
record={'checks':checks,'actualEngine':True,'backendAPIs':True,'renderer':True,'uiCopyFlowConnected':True,'nativeWindows':False,'accountOrInference':False,'errors':errors,'external':external,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
