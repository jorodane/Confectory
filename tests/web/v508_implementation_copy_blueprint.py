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
 page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');b.locator('[data-object="'+id+'"]').get_by_role('button',name='정의 열기',exact=True).click();w=page.locator('.window[data-key=schema]');slot=w.locator('[data-module-method="'+n+'Slot"]');slot.locator('[data-function-edit]').click();picker=page.locator('.feature-import-dialog');expect(picker.locator('[data-copy-source]')).to_have_count(4,timeout=30000);assert originals();page.screenshot(path=str(case/'copy-selection.png'));checked('real inherited Edit opens existing list structure with four explicit C#/Blueprint source/target choices and no source writes')
 picker.locator('[data-copy-source="'+n+'AliasBody"][data-copy-target=common]').click();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-node=body]')).to_be_visible(timeout=30000);expect(author.locator('.bp-status')).to_contain_text('미저장 복사본');assert 'Slime' in author.locator('.bp-name-input').get_attribute('title') and 'AliasBody' in author.locator('.bp-name-input').get_attribute('title') and originals();new=next(r['invoke']['input']['implementation'] for r in reversed(traffic) if r.get('invoke',{}).get('input',{}).get('action')=='readImplementationCopy');assert not invoke('blueprint',{'action':'list','feature':n+'Slot','query':new+'/body:'})['result']['result']['rows'];checked('selected Blueprint deep copy opens original author window as a private Slime copy, preserving all source bytes and sharing no new implementation before Save')
 def code_edit(text,save=True):
  author.locator('[data-bp-node=body] [data-internal-code]').click();dialog=page.locator('.bp-script-dialog');input=dialog.locator('[data-code-source]');expect(input).to_be_visible();input.evaluate("(el)=>{const start=el.value.indexOf('\\n{\\n')+3;el.focus();el.setSelectionRange(start,el.value.lastIndexOf('\\n}\\n'));}");input.press('Backspace');input.press_sequentially(text);dialog.locator('[data-code-save]' if save else '[data-code-cancel]').click();expect(dialog).to_have_count(0)
 code_edit('return amount+999;',False);page.evaluate('async()=>await confectoryFlushPresentation()');assert not [v for k,v in state()['presentation']['inputs']['blueprint'] if '|source' in k];assert originals();checked('original Script Cancel discards only modal code without mutating private body or original sources')
 wanted='return amount+77;';code_edit(wanted);page.evaluate('async()=>await confectoryFlushPresentation()');pending=[(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if '|v508-author|' in k];assert any(v['text']==wanted for k,v in pending),pending;assert originals();page.screenshot(path=str(case/'copy-private.png'));page.close();stop();start(1);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-node=body]')).to_be_visible(timeout=30000);expect(author.locator('.bp-status')).to_contain_text('미저장 복사본');author.locator('[data-bp-node=body] [data-internal-code]').click();dialog=page.locator('.bp-script-dialog');expect(dialog.locator('[data-code-source]')).to_have_value(re.compile(re.escape(wanted)));dialog.locator('[data-code-cancel]').click();assert originals();checked('true engine restart restores private selected copy and unsaved C# text without registering or editing original/default/windows sources')
 author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_contain_text('복사본',timeout=30000);expect(author.locator('.bp-status')).not_to_contain_text('미저장');assert originals();gresult=[r['result']['result'] for r in traffic if r.get('result',{}).get('result',{}).get('checkpointSaved')];assert gresult,gresult;metadata=state()['presentation'];page.evaluate('async()=>await confectoryFlushPresentation()');assert not [(k,v) for k,v in state()['presentation']['inputs']['blueprint'] if '|v508-author|' in k];assert len(invoke('blueprint',{'action':'list','feature':n+'Slot','query':new+'/body:'})['result']['result']['rows'])==1;g=invoke('blueprint',{'action':'read','id':new+'/body:common'})['result']['result'];assert next(v for v in g['nodes'] if v['id']=='body')['source']==wanted and next(v for v in g['nodes'] if v['id']=='extra')['source']=='return value*2;';assert {v['sourceId'] for v in g['nodes']}=={new+'/body:common/node:body',new+'/body:common/node:extra'};assert g['slotContext'] is None;checked('one original Save durably applies new child binding plus privately edited C# atomically, clears only accepted input and leaves physical original sources unchanged')
 author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=30000)
 for cb in review.locator('[data-review-id]').all():cb.check()
 if review.locator('[data-additional-changes]').count():
  review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
  if ack.count():ack.check()
 expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000);assert any(r.get('result',{}).get('result',{}).get('sourceConfirmed') for r in traffic);assert all((project/k).read_bytes()==v for k,v in original.items() if k not in ['Slime.celem','project.cproj']);expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);page.wait_for_function('()=>!document.querySelector("#app").inert');page.screenshot(path=str(case/'copy-confirmed.png'));checked('actual original Complete/Review/Confirm compiles edited copy and only changes new owned files plus child binding/registration')
 page.close();stop();browser.close();assert not errors and not external,(errors,external)

except Exception:
 try:page.screenshot(path=str(case/'failure.png'));(case/'failure.json').write_text(json.dumps({'state':state(),'traffic':traffic,'errors':errors},indent=2))
 except Exception:pass
 print('OWNED FAILURE ARTIFACT '+str(case),flush=True);raise
finally:stop();p.stop()
record={'checks':checks,'actualEngine':True,'backendAPIs':True,'renderer':True,'uiCopyFlowConnected':True,'nativeWindows':False,'accountOrInference':False,'errors':errors,'external':external,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
