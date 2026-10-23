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
 def originals():return all((project/k).read_bytes()==v for k,v in original.items())
 def flush():page.evaluate('async()=>await confectoryFlushPresentation()')
 def choices():flush();return [(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if v.get('kind')=='copy-selection']
 def pending():flush();return [(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if '|v508-author|' in k]
 def close_author():
  author=page.locator('.window[data-key=blueprint]')
  if author.is_visible():
   close=author.locator(':scope > header [data-close]');close.click() if close.count() else author.locator(':scope > header button').last.click()
 def open_owner(target):
  close_author();b=page.locator('.window[data-key^="browser:project:"]');b.locator('[data-object="'+target+'"]').get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=schema]');expect(w).to_be_visible();return w
 def edit_slot(w,feature,source):
  slot=w.locator('[data-module-method="'+feature+'"]');button=slot.locator('[data-function-edit]');button.click() if button.count() else slot.locator('[data-function-write-direct]').click();author=page.locator('.window[data-key=blueprint]');picker=page.locator('.feature-import-dialog')
  page.wait_for_function('()=>!!document.querySelector(".feature-import-dialog")?.offsetParent||!!document.querySelector(".window[data-key=blueprint] [data-bp-node=body]")?.offsetParent')
  if picker.is_visible():picker.locator('[data-copy-source="'+source+'"][data-copy-target=common]').click()
  expect(author.locator('[data-bp-node=body]')).to_be_visible(timeout=30000);expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);return author
 def code(author,text=None):
  author.locator('[data-bp-node=body] [data-internal-code]').click();dialog=page.locator('.bp-script-dialog');input=dialog.locator('[data-code-source]');expect(input).to_be_visible()
  if text is not None:
   input.evaluate('(el,d)=>{el.focus();el.setSelectionRange(el.value.indexOf(d[0])+3,el.value.lastIndexOf(d[1]));}',["\n{\n","\n}\n"]);page.keyboard.insert_text(text);dialog.locator('[data-code-save]').click()
  else:
   value=input.input_value();dialog.locator('[data-code-cancel]').click();return value

 page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();w=open_owner(id);a='slotCount=amount;slotReady=true;return amount+61;';b='slotCount=amount;slotReady=false;return amount+62;';c='slotCount=amount;slotReady=true;return amount+63;';code(edit_slot(w,n+'Slot',n+'AliasBody'),a);w=open_owner(id);code(edit_slot(w,n+'Slot2',n+'SlotBody2'),b);own_choices=choices();ids={v['copy']['function']:v['copy']['implementation'] for k,v in own_choices};w=open_owner(n+'Monster');code(edit_slot(w,n+'Slot',n+'AliasBody'),c);w=open_owner(id);before=pending();before_choices=choices();file=project/'Slot.csbody';old=file.read_bytes();file.write_bytes(old+b' ');mark=len(traffic);w.locator('[data-element-action=save]').click();expect(w.locator('[data-element-error]')).to_contain_text('바뀌었습니다',timeout=30000);assert pending()==before and choices()==before_choices;assert not any(row.get('invoke',{}).get('input',{}).get('action')=='applySlots' for row in traffic[mark:]);file.write_bytes(old);assert originals();checked('original object Save rejects a changed source before any batch write and preserves two own-slot choices plus other-object C# input')
 mark=len(traffic);w.locator('[data-element-action=save]').click();expect(w.locator('[data-module-method] .function-implementation-status')).to_have_text(['구현 연결','구현 연결'],timeout=30000);expect(w.locator('[data-element-action=save]')).to_be_disabled(timeout=30000);calls=[row['invoke']['input'] for row in traffic[mark:] if row.get('invoke',{}).get('input',{}).get('action')=='applySlots'];assert len(calls)==1 and len(calls[0]['rows'])==2;assert len(choices())==1 and choices()[0][1]['copy']['owner']==n+'Monster' and len(pending())==1 and pending()[0][1]['text']==c and originals();assert not [k for k,v in state()['presentation']['inputs']['blueprint'] if '|v508-copy-attempt|' in k];checked('retry through original object Save sends one two-row transaction, clears only accepted own inputs, updates both cards and retains the other owner without partial Save')
 for feature,text in [(n+'Slot',a),(n+'Slot2',b)]:
  g=invoke('blueprint',{'action':'read','id':ids[feature]+'/body:common'})['result']['result'];assert g['nodes'][0]['source']==text
 w=open_owner(n+'Monster');author=edit_slot(w,n+'Slot',n+'AliasBody');assert c in code(author);checked('another object sharing the source/function reopens its unchanged private input after the first object saved both slots')
 w=open_owner(id);flush();page.close();stop();start(1);page=setup();w=page.locator('.window[data-key=schema]');expect(w.locator('[data-module-method] .function-implementation-status')).to_have_text(['구현 연결','구현 연결'],timeout=30000);assert len(choices())==1 and len(pending())==1 and originals();checked('real restart restores both saved slot cards and the remaining other-owner private draft without re-creating either copy')
 w=open_owner(id);page.locator('.window[data-key^="browser:project:"] [data-close]').first.click();w.locator('[data-element-action=confirm]').click();creation=page.get_by_role('dialog',name='새 선언과 등록 변경 검토',exact=True);expect(creation).to_be_visible(timeout=30000);creation.locator('#review-creation').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=30000)
 for cb in review.locator('[data-review-id]').all():cb.check()
 if review.locator('[data-additional-changes]').count():
  review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
  if ack.count():ack.check()
 expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);assert any(row.get('result',{}).get('result',{}).get('sourceConfirmed') for row in traffic);assert all((project/k).read_bytes()==v for k,v in original.items() if k not in ['Slime.celem','project.cproj']);assert len(choices())==1 and pending()[0][1]['text']==c;page.wait_for_function('()=>!document.querySelector("#app").inert');page.screenshot(path=str(case/'two-slot-ui-confirmed.png'));checked('original explicit exact-group Confirm compiles both saved copies and preserves other-owner input plus every parent/default/other-target source')
 page.close();stop();browser.close();assert not errors and not external,(errors,external)

except Exception:
 try:page.screenshot(path=str(case/'failure.png'));(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop();p.stop()
record={'checks':checks,'actualEngine':True,'backendAPIs':True,'renderer':True,'uiCopyFlowConnected':True,'nativeWindows':False,'accountOrInference':False,'errors':errors,'external':external,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
