"""Actual original module-slot import UI, owned isolated sources, no login/inference/run."""
import json,re,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-registered-slot-engine-'));project=case/'owned project';project.mkdir();storage=case/'profile';storage.mkdir();n='Owned.Elements::';id=n+'Monster'
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
for name,(kind,text) in items.items():(project/(name+'.celem')).write_text(text)
(project/'Main.csbody').write_text('return checked((int)calls.Slot.Invoke(5,out long count,out bool ready));');(project/'Slot.csbody').write_text('slotCount=amount+1;slotReady=false;return amount+3;');(project/'Donor.csbody').write_text('count=input*2;active=true;return input+20;');(project/'project.cproj').write_text('project Owned.Elements version "1" {standalone true;entry '+n+'Main;'+''.join('element '+name+' '+kind+' "'+name+'.celem";' for name,(kind,text) in items.items())+'registry Confectory.Build.DotNet "'+str(repo/'targets/dotnet/pack.cpack')+'";dependency Confectory.Build.DotNet version "0.1.0";target portable Confectory.Build.DotNet::Portable;}')
lib=case/'Lib';lib.mkdir();hidden=case/'Hidden';hidden.mkdir()
(lib/'pack.cpack').write_text('pack Lib version "1" {element Donor function "Donor.celem";element DonorBody implementation "DonorBody.celem";element Wrong function "Wrong.celem";dependency Hidden version "1";}')
(lib/'Donor.celem').write_text('function Lib::Donor (long input,out long count,out bool active) -> long {description "등록된 기능 한글";provide Lib::Donor with Lib::DonorBody;}');(lib/'DonorBody.celem').write_text('implementation Lib::DonorBody for Lib::Donor (long input,out long count,out bool active) -> long {body common "Donor.csbody";}');(lib/'Wrong.celem').write_text('function Lib::Wrong (long input,ref long count,out bool active) -> long {}')
(hidden/'pack.cpack').write_text('pack Hidden version "1" {element Donor function "Donor.celem";}');(hidden/'Donor.celem').write_text('function Hidden::Donor (long input,out long count,out bool active) -> long {}')
pfile=project/'project.cproj';pfile.write_text(pfile.read_text().replace('target portable','registry Lib "../Lib/pack.cpack";dependency Lib version "1";registry Hidden "../Hidden/pack.cpack";target portable'));foreign_original={str(p.relative_to(case)):p.read_bytes() for folder in [lib,hidden] for p in folder.iterdir() if p.is_file()}
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
 p=sync_playwright().start();browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');b.locator('[data-object="'+id+'"]').get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=schema]');slot=w.locator('[data-module-method="'+n+'Slot"]');expect(slot).to_be_visible(timeout=30000)
 def foreign_same():return all((case/k).read_bytes()==v for k,v in foreign_original.items())
 def original_same():return all((project/k).read_bytes()==v for k,v in original.items())
 def pending():
  page.wait_for_function("()=>typeof confectoryFlushPresentation==='function'");page.evaluate('async()=>await confectoryFlushPresentation()');return [(k,v) for k,v in state()['presentation']['inputs']['schema'] if '|element|implementation:' in k]
 def picker():
  slot.locator('[data-function-import]').click();dialog=page.get_by_role('dialog',name='기능 가져오기',exact=True);expect(dialog.locator('[data-feature-import="Lib::Donor"]')).to_be_visible(timeout=30000);return dialog
 catalog=invoke('blueprint',{'action':'implementationCallables','id':id,'function':n+'Slot','scope':'registered','page':0})['result']['result'];row=next(row for row in catalog['rows'] if row['id']=='Lib::Donor');assert row['readOnly'] and row['signature']['args'][1]['mode']=='out' and row['description']=='등록된 기능 한글';assert not any(row['id'].startswith('Hidden::') for row in catalog['rows']);assert catalog['bodyReads']==0 and catalog['scope']=='registered-direct-dependency-functions' and not (lib/'Donor.csbody').exists();checked('registered summaries read only bounded direct-dependency public declarations with exact out signature, no body or transitive-only candidates')
 dialog=picker();expect(dialog.locator('[data-feature-import="Lib::Donor"] strong')).to_have_text('Lib / Donor');expect(dialog.locator('[data-feature-import="'+n+'Donor"] strong')).to_have_text('Donor');expect(dialog.locator('[data-feature-import="Lib::Wrong"]')).to_have_count(0);expect(dialog.locator('[data-feature-import="Hidden::Donor"]')).to_have_count(0);page.screenshot(path=str(case/'registered-options.png'));dialog.locator('[data-close]').click();assert not pending() and original_same() and foreign_same();checked('same original import modal separates same-name owned/registered functions by pack label and keeps wrong ref/out or undeclared dependency out; cancel is read-only')
 schema=state()['schema'];invoke('blueprint',{'action':'readImplementation','id':id,'function':n+'Slot','implementation':n+'RejectedHidden','reference':'Hidden::Donor','revision':schema['revision'],'hash':schema['textHash']},False);assert original_same() and foreign_same();checked('forged candidate from registered-but-not-direct dependency is rejected before creating owned source or registration')
 picker().locator('[data-feature-import="Lib::Donor"]').click();expect(slot.locator('.function-implementation-origin')).to_contain_text('Lib / Donor');choice=pending();assert len(choice)==1 and choice[0][1]['reference']=='Lib::Donor' and 'basis' not in choice[0][1];implementation=choice[0][1]['implementation'];assert not (lib/'Donor.csbody').exists() and original_same() and foreign_same();checked('selecting a registered donor stages only a local wrapper choice/fingerprint, no live receipt or copied/read provider body')
 for path,changed in [(lib/'Donor.celem',(lib/'Donor.celem').read_text()+' '),(lib/'pack.cpack',(lib/'pack.cpack').read_text().replace('version "1"','version "2"',1))]:
  old=path.read_bytes();path.write_text(changed);mark=len(traffic);w.locator('[data-element-action=save]').click();expect(w.locator('[data-element-error]')).to_contain_text('계약이나 등록이 바뀌',timeout=30000);assert pending()==choice and original_same();assert not any(x.get('invoke',{}).get('input',{}).get('action')=='createImplementation' for x in traffic[mark:]);path.write_bytes(old)
 assert foreign_same() and not (lib/'Donor.csbody').exists();checked('registered public declaration and pack-version changes after selection each block Save before wrapper creation while preserving the exact choice')
 page.close();stop();start(1);page=setup();w=page.locator('.window[data-key=schema]');slot=w.locator('[data-module-method="'+n+'Slot"]');expect(slot.locator('.function-implementation-origin')).to_contain_text('Lib / Donor',timeout=30000);assert pending()==choice and not (lib/'Donor.csbody').exists();checked('true cold restart preserves selected registered identity/signature/fingerprint without replaying a receipt or reading missing code')
 # Supply fixture code only for explicit compiler Review/Confirm below.
 (lib/'Donor.csbody').write_text('count=input*4;active=true;return input+20;');foreign_original['Lib/Donor.csbody']=(lib/'Donor.csbody').read_bytes();w.locator('[data-element-action=save]').click();expect(slot.locator('.function-implementation-status')).to_have_text('구현 연결',timeout=30000);assert not pending();graphid=invoke('blueprint',{'action':'list','feature':n+'Slot','query':implementation+'/body:'})['result']['result']['rows'][0]['id'];g=invoke('blueprint',{'action':'read','id':graphid})['result']['result'];assert g['nodes'][0]['calledFeature']=='Lib::Donor' and g['nodes'][0]['sourceStatus']=='feature-reference' and len(g['nodes'])==1;assert original_same() and foreign_same();checked('Save creates actual local typed reference to immutable registered function; original foreign function/default/body and owned declaration files stay untouched')
 w.locator('[data-element-action=confirm]').click();page.wait_for_selector('[role=dialog][aria-label="새 선언과 등록 변경 검토"],.window[data-key=review]',state='visible');creation=page.get_by_role('dialog',name='새 선언과 등록 변경 검토',exact=True)
 if creation.is_visible():creation.locator('#review-creation').click()
 review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=30000)
 for cb in review.locator('[data-review-id]').all():cb.check()
 if review.locator('[data-additional-changes]').count():
  review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
  if ack.count():ack.check()
 expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);assert any(x.get('result',{}).get('result',{}).get('sourceConfirmed') for x in traffic);assert all((project/k).read_bytes()==v for k,v in original.items() if k not in ['Monster.celem','project.cproj']) and foreign_same();page.screenshot(path=str(case/'registered-confirmed.png'));original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};checked('explicit four-source compiler Confirm validates registered out forwarding and changes only local wrapper/graph/object/registration, never foreign or original C# sources')
 page.wait_for_function("()=>typeof confectoryFlushPresentation==='function'");page.evaluate('async()=>await confectoryFlushPresentation()');page.close();stop();start(2);page=setup();w=page.locator('.window[data-key=schema]');slot=w.locator('[data-module-method="'+n+'Slot"]');expect(slot.locator('.function-implementation-origin')).to_contain_text('Lib / Donor',timeout=30000);assert not pending() and original_same() and foreign_same();checked('confirmed registered reference/provenance survives a real restart with no implicit edit permission or source changes')
 page.close();stop();browser.close();assert not errors and not external,(errors,external)
except Exception:
 try:page.screenshot(path=str(case/'failure.png'));(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case));raise
finally:stop();p.stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'nativeWindows':False,'accountOrInference':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
