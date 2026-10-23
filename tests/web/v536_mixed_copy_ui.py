"""Atomic same-owner declaration and new-copy candidate UI, isolated real engine; no account/inference/run."""
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
def metadata(operation,**request):
 r=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':operation,**request}),text=True,capture_output=True,env=env,check=True);v=json.loads(r.stdout);assert v['ok'],v;return v['result']
# A current wrapped imported call is copied, not repaired in its donor. Windows
# remains a separate untouched source body; only common is explicitly chosen.
native='function '+n+'Native (long input) -> long {provide '+n+'Native with '+n+'NativeBody;}'
(project/'Native.celem').write_text(native);(project/'NativeBody.celem').write_text('implementation '+n+'NativeBody for '+n+'Native (long input) -> long {body common "Native.csbody";}');(project/'Native.csbody').write_text('return input+3;');manifest=project/'project.cproj';manifest.write_text(manifest.read_text().replace('registry Confectory.Build.DotNet','element Native function "Native.celem";element NativeBody implementation "NativeBody.celem";registry Confectory.Build.DotNet'))
fn='function '+n+'Slot (long amount,out long slotCount,out bool slotReady) -> long {}';initial=metadata('blueprintPrepareFeature',id=n+'Slot',text=fn,implementation=n+'SlotBody',graphPath='Slot.graph.json',nodePath='Slot.node.json');initial['implementation']=initial['implementation'].replace('{','{\nimport '+n+'Donor as Gift (long,out long,out bool) -> long in '+n+'Unit;\n',1).replace('\n}\n','\nbody windows "SlotWindows.csbody";\n}\n')
prepared=metadata('blueprintPrepareCall',id=n+'SlotBody',text=initial['implementation'],targetText=native,graph=initial['graph'],definition={'id':'native','feature':n+'Native','intent':'원본 호출','control':'next'});g=prepared['graph'];g['profile']='sync-acyclic-switch-v1';node=next(v for v in g['nodes'] if v['id']=='native');node['arguments']={'input':{'input':'amount'}};node['control']='switch';enum={'primary':'next','members':[{'id':'next','name':'NoBranch','value':0}]};wrapper=metadata('blueprintCallWrapper',functionText=native,executionEnum=enum,returnMapping='native-return-out-v1',source='return Result.NoBranch;');node['executionEnum']=enum;node['postCall']={'mode':'execution-enum','returnMapping':'native-return-out-v1','contractHash':wrapper['contractHash'],'source':wrapper['source'],'helpers':''};g['entry']='native';g['edges'].append({'from':'native','port':'next','to':'body'});next(v for v in g['nodes'] if v['id']=='body')['arguments']['amount']={'node':'native'}
defs=metadata('featureBlueprintNodes',featureSource=fn,graph=g,featureContracts={n+'Native':native,n+'Donor':items['Donor'][1]});(project/'SlotBody.celem').write_text(prepared['implementation']);(project/'Slot.graph.json').write_text(json.dumps(g));body='slotCount=amount+1;slotReady=false;return amount+3;';record={'schema':1,'node':'body','definitionHash':next(v for v in defs['nodes'] if v['id']=='body')['definitionHash'],'source':body};(project/'Slot.node.json').write_text(json.dumps(record));original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file()}
def originals():assert all((project/k).read_bytes()==v for k,v in original.items())
def idle():expect(page.locator('.brand')).to_be_enabled(timeout=60000)
def pending():page.evaluate('async()=>await confectoryFlushPresentation()');return state()['presentation']['inputs']
def owner():return page.locator('.window[data-key=schema]')
def author():return page.locator('.window[data-key=blueprint]')
def close_author():
 if author().is_visible():author().locator('[data-close]').first.click()
def edit_region(button,before,replacement):
 node=button.evaluate('(el)=>el.closest("[data-bp-node]").dataset.bpNode');author().locator(':scope > .window-title .caption').click(position={'x':5,'y':8});author().locator('[data-bp-overview-node="'+node+'"]').click();button.click();dialog=page.locator('.bp-script-dialog');value=dialog.locator('[data-code-source]');expect(value).to_be_visible();assert before in value.input_value();value.evaluate('(el,text)=>{el.focus();const start=el.value.indexOf(text);el.setSelectionRange(start,start+text.length);}',before);page.keyboard.insert_text(replacement);dialog.locator('[data-code-save]').click();expect(dialog).to_be_hidden()
def retained(captured):
 now=pending()
 for group in ['schema','blueprint']:
  assert all(dict(now[group]).get(k)==v for k,v in captured[group]),(group,now[group])
 return now
def no_mixed_membership():
 invoke('schema',{'id':id});d=state()['schema'];assert d['description']!='함께 저장할 객체 설명';assert not any(v['origin']==id for v in d['providers']);originals()
def rejected_save():
 page.evaluate('''()=>{globalThis.boundaryMessages=[];globalThis.boundaryObserver=new MutationObserver(()=>{for(const el of document.querySelectorAll('[data-element-error],#status')){const text=el.textContent;if(text&&!boundaryMessages.includes(text))boundaryMessages.push(text)}});boundaryObserver.observe(document.body,{subtree:true,childList:true,characterData:true})}''')
 owner().locator('[data-element-action=save]').click();page.wait_for_function('()=>boundaryMessages.some(text=>/바뀌|입력.*유지|실패|완료하지|consumer_error|stale|changed/i.test(text))',timeout=30000);page.evaluate('()=>boundaryObserver.disconnect()');idle()
def restart(i):
 global page
 pending();page.close();stop();start(i);page=setup();expect(owner().locator('[aria-label="HP 기본값"]')).to_be_visible(timeout=60000);idle()
def finish_boundary():
 assert not errors and not external,(errors,external);browser.close();p.stop();print(json.dumps({'checks':checks,'actualEngineRenderer':True,'nativeWindows':False,'actualAccountOrInference':False,'projectRun':False,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
def boundary(mode,captured):
 if mode in ['storage','storage-cancel']:
  checkpoint=next(project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();checkpoint.chmod(0o400)
  try:
   rejected_save();assert checkpoint.read_bytes()==before;retained(captured);no_mixed_membership();assert any(v.get('kind')=='copy-attempt' and v.get('declaration') for _,v in pending()['blueprint'])
  finally:checkpoint.chmod(0o600)
  checked('실제 체크포인트 쓰기 거절은 설명·정확한 long·복사본을 모두 미적용하고 원본/부모/다른 target과 두 종류 입력을 보존한다')
  restart(1);retained(captured);no_mixed_membership();expect(owner().locator('[aria-label="HP 기본값"]')).to_have_value('9007199254740993');checked('실패한 혼합 저장은 실제 재시작 뒤에도 두 입력과 원래 체크포인트를 함께 보존한다')
  if mode=='storage-cancel':
   owner().locator('[data-element-action=discard]').click();expect(owner().locator('[data-element-action=discard]')).to_be_disabled(timeout=30000);now=pending();assert not now['schema'] and not now['blueprint'];no_mixed_membership();assert checkpoint.read_bytes()==before;restart(2);assert not pending()['schema'] and not pending()['blueprint'];no_mixed_membership();checked('실패 뒤 원본 변경취소는 저장 여부를 확인한 뒤 미적용 혼합 입력만 정리하며 cold 복원에도 부분 copy/선언을 남기지 않는다');finish_boundary()
 elif mode=='wrapper-invalid':
  checkpoint=next(project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();mutated=[]
  def invalid_wrapper(route):
   request=route.request.post_data_json
   if request.get('op')=='invoke' and request.get('endpoint')=='blueprint' and request.get('input',{}).get('action')=='applySlots':
    edit=next(v for v in request['input']['rows'][0]['edits'] if v['type']=='wrapper');plan=json.loads(edit['text']);plan['contractHash']='0'*64;edit['text']=json.dumps(plan);mutated.append(request['requestId']);route.continue_(post_data=json.dumps(request));return
   route.continue_()
  page.route('**/api/request',invalid_wrapper);rejected_save();page.unroute('**/api/request',invalid_wrapper);assert len(mutated)==1;retained(captured);no_mixed_membership();assert checkpoint.read_bytes()==before;restart(1);retained(captured);no_mixed_membership();checked('실제 전송된 wrapper 계약 위조는 선언 staging 뒤에도 전체 거절하며 copy/import/본문·정확한 long 입력과 기존 checkpoint를 보존한다');finish_boundary()
 elif mode=='conflict':
  invoke('schema',{'id':id});d=state()['schema'];invoke('editDescription',{'id':id,'revision':d['revision'],'hash':d['textHash'],'value':'다른 편집자가 먼저 저장한 설명'});invoke('saveDraft',{});before=next(project.glob('.confectory/edit-workspaces/*/draft.json')).read_bytes();rejected_save();retained(captured);no_mixed_membership();assert state()['schema']['description']=='다른 편집자가 먼저 저장한 설명';assert next(project.glob('.confectory/edit-workspaces/*/draft.json')).read_bytes()==before;restart(1);retained(captured);no_mixed_membership();assert state()['schema']['description']=='다른 편집자가 먼저 저장한 설명';checked('같은 owner의 동료 저장 뒤 오래된 혼합 입력은 재기준화 없이 전체 거절하며 동료 체크포인트·로컬 입력·cold 복원을 보존한다');finish_boundary()
 elif mode=='response-loss':
  ids=set();lost={}
  def intercept(route):
   body=route.request.post_data_json
   if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('action')=='applySlots':ids.add(body['requestId'])
   response=route.fetch();payload=response.json()
   if not lost and body.get('op')=='update' and any(v.get('requestId') in ids for v in payload.get('results',[])):
    assert all(v.get('ok') for v in payload['results'] if v.get('requestId') in ids);lost.update(route=route,response=response,payload=payload);return
   route.fulfill(response=response)
  page.route('**/api/request',intercept);owner().locator('[data-element-action=save]').click()
  for _ in range(1800):
   if lost:break
   page.wait_for_timeout(20)
  assert lost,'actual successful mixed result not observed';owner().locator('.object-title-description').fill('저장 응답 대기 중 새 설명');owner().locator('[aria-label="HP 기본값"]').fill('9007199254740995');payload=lost['payload'];payload['results']=[{'requestId':v['requestId'],'ok':False,'error':{'code':'transport-interrupted'}} if v.get('requestId') in ids else v for v in payload['results']];lost['route'].fulfill(response=lost['response'],json=payload)
  expect(owner().locator('[data-element-error]')).not_to_be_empty(timeout=30000);idle();page.unroute('**/api/request',intercept);now=pending();assert len(ids)==1 and len(now['schema'])==2 and not now['blueprint'];assert {v['text'] for _,v in now['schema']}=={'저장 응답 대기 중 새 설명','9007199254740995'};d=state()['schema'];assert d['description']=='함께 저장할 객체 설명' and '9007199254740993' in state()['draft']['text'];assert all(v['hash']==d['textHash'] for _,v in now['schema']);originals();checked('실제 성공 응답 유실은 receipt로 한 번만 확인하고 늦은 설명/정확한 long 입력을 유지하며 접수한 혼합 결과만 저장한다')
  restart(1);expect(owner().locator('.object-title-description')).to_have_value('저장 응답 대기 중 새 설명');expect(owner().locator('[aria-label="HP 기본값"]')).to_have_value('9007199254740995');assert len(pending()['schema'])==2 and not pending()['blueprint'];new=next(v['implementation'] for v in state()['schema']['providers'] if v['function']==n+'Slot' and v['origin']==id);mark=len(traffic);owner().locator('[data-element-action=save]').click()
  for _ in range(1800):
   requests={r['invoke']['requestId'] for r in traffic[mark:] if r.get('invoke',{}).get('endpoint')=='saveDraft'}
   if any(r.get('result',{}).get('requestId') in requests for r in traffic[mark:]) or owner().locator('[data-element-error]').inner_text():break
   page.wait_for_timeout(20)
  idle();assert not owner().locator('[data-element-error]').inner_text(),owner().locator('[data-element-error]').inner_text();assert not pending()['schema'];assert state()['schema']['description']=='저장 응답 대기 중 새 설명' and '9007199254740995' in state()['draft']['text'];rows=invoke('blueprint',{'action':'list','feature':n+'Slot','query':new+'/body:'})['result']['result']['rows'];assert len(rows)==1;originals();checked('cold 복원 뒤 늦은 입력의 다음 명시적 Save는 같은 owner만 갱신하고 복사본을 중복 생성하지 않는다');finish_boundary()
try:
 start(0);p=sync_playwright().start();browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=setup();id=n+'Slime';invoke('select',{'id':id});invoke('saveDraft',{});page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');b.locator('[data-browser-control="object-query"]').fill('Slime');b.locator('[data-browser-control="object-search"]').click();row=b.locator('[data-object="'+id+'"]');expect(row).to_have_attribute('aria-disabled','false');row.press('Enter');idle();b.locator('[data-close]').first.click();expect(owner().locator('[aria-label="HP 기본값"]')).to_have_value('100');owner().locator('.object-title-description').fill('함께 저장할 객체 설명');owner().locator('[aria-label="HP 기본값"]').fill('9007199254740993');held_owner=pending()['schema'];assert len(held_owner)==2;originals()
 slot=owner().locator('[data-module-method="'+n+'Slot"]');edit=slot.locator('[data-function-edit]');edit.click() if edit.count() else slot.locator('[data-function-write-direct]').click();picker=page.locator('.feature-import-dialog');expect(picker).to_be_visible(timeout=60000);picker.locator('[data-copy-source="'+n+'AliasBody"][data-copy-target=common]').click();expect(author().locator('[data-bp-node=native]')).to_be_visible(timeout=60000);expect(author().locator('[data-bp-save]')).to_be_enabled();originals();assert pending()['schema']==held_owner;checked('원본 객체 입력을 먼저 쓴 뒤 같은 owner의 새 복사 common을 선택하며 데이터·다른 target·source를 보존한다')
 new_source='slotCount=amount+5;slotReady=true;return amount+70;';edit_region(author().locator('[data-bp-node=body] [data-internal-code]'),body,new_source);edit_region(author().locator('[data-bp-node=native] [data-wrapper-edit]'),'return Result.NoBranch;','return Result.NoBranch; // 복사본 후처리');held=pending();assert len([v for k,v in held['blueprint'] if v.get('type')=='wrapper'])==1;assert held['schema']==held_owner;close_author();page.screenshot(path=str(case/'mixed-copy-owner-before-save.png'))
 if len(sys.argv)>3:boundary(sys.argv[3],held)
 owner().locator('[data-element-action=save]').click()
 for _ in range(3000):
  saved=pending()
  if not saved['schema'] and not any(v.get('kind') in ['copy-selection','copy-attempt'] or '|v508-author|' in k for k,v in saved['blueprint']):break
  if owner().locator('[data-element-error]').inner_text():raise AssertionError(owner().locator('[data-element-error]').inner_text())
  page.wait_for_timeout(20)
 assert not saved['schema'] and not any(v.get('kind') in ['copy-selection','copy-attempt'] or '|v508-author|' in k for k,v in saved['blueprint']),saved;idle();originals();d=state()['schema'];new=next(v['implementation'] for v in d['providers'] if v['function']==n+'Slot' and v['origin']==id);result=invoke('blueprint',{'action':'read','id':new+'/body:common','owner':id,'ownerHash':d['textHash']})['result']['result'];assert next(v for v in result['nodes'] if v['id']=='body')['source']==new_source;assert next(v for v in result['nodes'] if v['id']=='native')['postCall']['source'].endswith('// 복사본 후처리');assert d['description']=='함께 저장할 객체 설명';expect(owner().locator('[aria-label="HP 기본값"]')).to_have_value('9007199254740993');checked('실제 원본 Save가 객체 설명·정확한 long값·새 copy import/wrapper/본문을 한 번에 저장하고 captured 입력만 정리한다')
 page.close();stop();start(1);page=setup();expect(owner().locator('[aria-label="HP 기본값"]')).to_have_value('9007199254740993',timeout=60000);expect(owner().locator('.object-title-description')).to_have_value('함께 저장할 객체 설명');idle();assert not pending()['schema'];originals();owner().locator('[data-element-action=confirm]').click();expect(page.locator('#review-creation')).to_be_visible(timeout=60000);page.locator('#review-creation').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000);review.locator('[data-reject]').click();expect(review).to_be_hidden();originals();checked('혼합 저장의 실제 재시작과 Review 취소는 선언·복사 내용을 보존하고 원본 파일을 반영하지 않는다')
 owner().locator('[data-element-action=confirm]').click();expect(page.locator('#review-creation')).to_be_visible(timeout=60000);page.locator('#review-creation').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000)
 if review.locator('[data-review-advanced]').count():
  review.locator('[data-review-advanced]').click()
  if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
 review.locator('#confirm').click();expect(review).to_have_count(0,timeout=120000);idle();changed={k for k,v in original.items() if (project/k).read_bytes()!=v};assert changed=={'Slime.celem','project.cproj'},changed;checked('실제 명시적 compiler Confirm은 해당 owner·등록과 새 copy 파일만 반영하고 원본 wrapper·부모·Windows 본문을 보존한다');assert not errors and not external,(errors,external);browser.close();p.stop()
except Exception:
 evidence={'checks':checks,'errors':errors,'traffic':traffic[-30:]}
 try:evidence['messages']=owner().locator('[data-element-error]').all_text_contents();page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 try:evidence['state']={k:v for k,v in state().items() if k in ['logs','sourceError','review']}
 except Exception:pass
 (case/'failure-state.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2))
 print('EVIDENCE '+str(case),flush=True);raise
finally:stop()
print(json.dumps({'checks':checks,'actualEngineRenderer':True,'nativeWindows':False,'actualAccountOrInference':False,'projectRun':False,'evidence':str(case)},ensure_ascii=False,indent=2))
