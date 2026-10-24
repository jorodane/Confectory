"""Atomic same-owner declaration and new-copy candidate UI, isolated real engine; no account/inference/run."""
import json,re,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-wide-mixed-'));project=case/'owned project';project.mkdir();storage=case/'profile';storage.mkdir();n='Owned.Elements::';id=n+'Monster'
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
   deadline=time.monotonic()+60;rows=[]
   while time.monotonic()<deadline:
    assert host.poll() is None,{'endpoint':endpoint,'action':body.get('action'),'reason':'fixture engine exited','evidence':str(case)}
    u=raw({'op':'update','view':v['view'],'scope':v['scope']});rows=[r for r in u.get('results',[]) if r['requestId']==rid]
    if rows:break
    time.sleep(.01)
   assert rows,{'endpoint':endpoint,'action':body.get('action'),'reason':'bounded result deadline','evidence':str(case)}
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
# Real source fixture for all object controls currently connected by v536.
extra={
 'Details':('schema','schema '+n+'Details {field Power single general long;field Label single general string;}'),
 'Vitals':('schema','schema '+n+'Vitals {field HP single general long;field MP single general long;field Combat single compound '+n+'Details;field Loadout single compound '+n+'Details;field Counts multiple general long;field Target single reference '+n+'Details;field Targets multiple reference '+n+'Details;}'),
 'Target1':('object','object '+n+'Target1 {use schema '+n+'Details;data Power=1;data Label="첫 대상";}'),
 'Target2':('object','object '+n+'Target2 {use schema '+n+'Details;data Power=2;data Label="둘째 대상";}'),
 'Alternate':('object','object '+n+'Alternate extends '+n+'Monster {data HP=200;}'),
 'Extra':('module','module '+n+'Extra {}'),
 'Slime':('object','object '+n+'Slime extends '+n+'Monster {data HP=101;data MP=4;data Combat={Power=9223372036854775804;Label="원래";};data Counts=[9223372036854775804,2];data Target='+n+'Target1;data Targets=['+n+'Target1];}'),
 'Unit':('object','object '+n+'Unit {use schema '+n+'Vitals;data HP=100;data MP=3;data Loadout={Power=7;Label="부모";};provide '+n+'Donor with '+n+'DonorBody;}')}
for name,(kind,text) in extra.items():
 (project/(name+'.celem')).write_text(text)
 if name not in items:manifest.write_text(manifest.read_text().replace('registry Confectory.Build.DotNet','element '+name+' '+kind+' "'+name+'.celem";registry Confectory.Build.DotNet'))
original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file()};id=n+'Slime'
shape=lambda kind,cardinality,type:dict(kind=kind,cardinality=cardinality,type=type)
changes=[{'type':'description','text':'넓은 혼합 저장 한글'}, {'type':'data','path':['Combat'],'contract':shape('compound','single',n+'Details'),'valueJson':'{"Power":9223372036854775805,"Label":"함께 한글"}'}, {'type':'data','path':['Loadout'],'contract':shape('compound','single',n+'Details'),'valueJson':'{"Power":9223372036854775806,"Label":"부모 재정의"}'}, {'type':'data','path':['Counts'],'contract':shape('general','multiple','long'),'valueJson':'[2,9223372036854775804,3]'}, {'type':'data','path':['Target'],'contract':shape('reference','single',n+'Details'),'valueJson':json.dumps({'$ref':n+'Target2'})}, {'type':'data','path':['Targets'],'contract':shape('reference','multiple',n+'Details'),'valueJson':json.dumps([{'$ref':n+'Target2'},{'$ref':n+'Target1'}])}, {'type':'unset','path':['HP'],'contract':shape('general','single','long')}, {'type':'parent','value':n+'Alternate'}, {'type':'modules','ids':[n+'Extra']}, {'type':'definition','name':'Bonus','nativeType':'long','valueJson':'9007199254740993'}]
def backend():
 start(0);invoke('select',{'id':id});invoke('saveDraft',{});invoke('schema',{'id':id});d=state()['schema'];rows=[]
 for feature,source,new,text in [('Slot','AliasBody','WideCopy1','slotCount=amount+5;slotReady=true;return amount+70;'),('Slot2','SlotBody2','WideCopy2','slotCount=amount+9;slotReady=true;return amount+90;')]:
  view=invoke('blueprint',{'action':'readImplementationCopy','id':id,'function':n+feature,'source':n+source,'target':'common','implementation':n+new,'revision':d['revision'],'hash':d['textHash']})['result']['result'];rows.append({'function':n+feature,'implementation':n+new,'copySource':n+source,'copyTarget':'common','fingerprint':view['fingerprint'],'basis':view['basis'],'edits':[{'type':'source','node':'body','text':text}]})
 # Preparing the second selection changes metadata checkpoint only; obtain fresh bases for both.
 for row in rows:
  view=invoke('blueprint',{'action':'readImplementationCopy','id':id,'function':row['function'],'source':row['copySource'],'target':'common','implementation':row['implementation'],'revision':d['revision'],'hash':d['textHash']})['result']['result'];row.update(basis=view['basis'],fingerprint=view['fingerprint'])
 checkpoint=next(project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();declaration={'id':id,'hash':d['textHash'],'changes':changes};command={'action':'applySlots','id':id,'rows':rows,'declaration':declaration};bad=json.loads(json.dumps(command));bad['rows'][-1]['edits'][0]['node']='not-owned';invoke('blueprint',bad,False);assert checkpoint.read_bytes()==before;invoke('schema',{'id':id});assert state()['schema']['parent']==n+'Monster';assert not any(p['origin']==id for p in state()['schema']['providers']);originals();checked('마지막 copy 본문이 부적합하면 앞 copy/새 schema/부모/모듈/typed값/등록 모두 미적용이고 원래 checkpoint·소스를 보존한다')
 accepted=invoke('blueprint',command)['result']['result'];assert accepted['atomic'] and accepted['checkpointSaved'];invoke('schema',{'id':id});d=state()['schema'];assert d['parent']==n+'Alternate' and d['description']=='넓은 혼합 저장 한글';assert len([p for p in d['providers'] if p['origin']==id])==2;assert '9007199254740993' in state()['draft']['text'] and '9223372036854775805' in state()['draft']['text'];saved=json.loads(checkpoint.read_text());assert not saved['privateCopies'];assert len([u for u in saved['changes'] if u['kind']=='schema' and u.get('creationOwner')==id])==1;originals();checked('두 copy와 구조/복합/배열/ref/로컬해제/새 속성이 같은 후보/CAS에 저장되고 정확한 숫자·순서·parent/원본을 보존한다')
 request={'action':'settledSlots','id':id,'rows':rows,'declaration':declaration};assert invoke('blueprint',request)['result']['result']['settled'];assert not invoke('blueprint',{**request,'rows':rows[:1]})['result']['result']['settled'];checked('원자 receipt는 전체 copy 목록과 선언 계획을 결부하며 부분 목록을 전체 저장으로 승인하지 않는다')
 stop();start(1);invoke('select',{'id':id});invoke('schema',{'id':id});d=state()['schema'];assert d['parent']==n+'Alternate' and len([p for p in d['providers'] if p['origin']==id])==2;g=invoke('blueprint',{'action':'read','id':n+'WideCopy1/body:common','owner':id,'ownerHash':d['textHash']})['result']['result'];invoke('reviewGroup',{'ids':g['reviewIds'],'target':'linux'});assert state()['review']['status']=='ready',state()['review'];review=state()['review'];invoke('confirmGroup',{'ids':g['reviewIds'],'token':review['token']});assert {k for k,v in original.items() if (project/k).read_bytes()!=v}=={'Slime.celem','project.cproj'};checked('실제 cold/그룹 compiler Confirm은 두 copy+새 속성+owner 등록만 반영하고 donor/부모/다른 대상은 바꾸지 않는다')
def field(path):return owner().locator("[data-property-path='"+json.dumps(path,separators=(',',':'))+"']")
def open_owner(target=id):
 page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');b.locator('[data-browser-control="object-query"]').fill(target.split('::')[-1]);b.locator('[data-browser-control="object-search"]').click();row=b.locator('[data-object="'+target+'"]');expect(row).to_have_attribute('aria-disabled','false');row.press('Enter');b.locator('[data-close]').first.click();idle()
def choose_reference(button,target):button.click();page.get_by_role('dialog',name='기본값 선택',exact=True).locator('[data-reference-choice="'+n+target+'"]').click()
def select_copy(feature,source,wanted,wrapped=False):
 slot=owner().locator('[data-module-method="'+n+feature+'"]');edit=slot.locator('[data-function-edit]');edit.click() if edit.count() else slot.locator('[data-function-write-direct]').click();picker=page.locator('.feature-import-dialog');expect(picker).to_be_visible(timeout=60000);picker.locator('[data-copy-source="'+n+source+'"][data-copy-target=common]').click();expect(author().locator('[data-bp-node=body]')).to_be_visible(timeout=60000);edit_region(author().locator('[data-bp-node=body] [data-internal-code]'),body,wanted)
 if wrapped:edit_region(author().locator('[data-bp-node=native] [data-wrapper-edit]'),'return Result.NoBranch;','return Result.NoBranch; // 넓은 혼합 복사')
 close_author()
def edit_owner():
 owner().locator('.object-title-description').fill('넓은 혼합 저장 한글');owner().locator('[aria-label="MP 기본값"]').fill('9007199254740995');field(['Combat','Power']).locator('input').fill('9223372036854775805');field(['Combat','Label']).locator('input').fill('함께 한글');field(['Loadout','Power']).locator('input').click();page.get_by_role('dialog',name='부모 값 재정의',exact=True).locator('[data-override]').click();field(['Loadout','Power']).locator('input').fill('9223372036854775806');field(['Loadout','Label']).locator('input').fill('부모 재정의')
 counts=field(['Counts']);counts.locator(':scope>.property-content-box>.object-property-default>.property-add-value').click();counts.locator('[data-value-path=\'["Counts",2]\']').fill('3');entry=counts.locator(':scope>.property-content-box>.property-expanded-content>.property-multi-item').first;entry.focus();entry.press('ArrowDown');choose_reference(field(['Target']).locator('.property-reference-value'), 'Target2');targets=field(['Targets']);choose_reference(targets.locator('.property-reference-value').first,'Target2');targets.locator(':scope>.property-content-box>.object-property-default>.property-add-value').click();page.get_by_role('dialog',name='기본값 선택',exact=True).locator('[data-reference-choice="'+n+'Target1"]').click();owner().locator('[aria-label="HP 부모 기본값으로 되돌리기"]').click()
 owner().locator('.object-parent-change').click();page.get_by_role('dialog',name='부모 변경',exact=True).locator('[data-parent-choice="'+n+'Alternate"]').click();owner().locator('[data-module-link]').click();page.get_by_role('dialog',name='모듈 연결',exact=True).locator('[data-link-id="'+n+'Extra"]').click();owner().locator('[data-schema-add]').click();definition=owner().locator('[data-definition-key]').last;definition.locator('[data-property-name]').fill('Bonus');definition.locator('[data-property-type]').click();page.get_by_role('dialog',name='속성 타입 선택',exact=True).locator('[data-type=long]').click();owner().locator('[data-definition-key]').last.locator('[data-property-value]').fill('9007199254740993');owner().locator('[data-schema-add]').click();definition=owner().locator('[data-definition-key]').last;definition.locator('[data-property-name]').fill('Note');definition.locator('[data-property-value]').fill('새 속성 "한글"')
def wait_saved():
 for _ in range(3000):
  now=pending()
  if not any('|'+id+'|element|' in key for key,_ in now['schema']) and not now['blueprint']:idle();return
  error=owner().locator('[data-element-error]').inner_text()
  if error:raise AssertionError(error)
  page.wait_for_timeout(20)
 raise AssertionError('wide UI save did not settle')
def no_partial(before):
 checkpoint=next(project.glob('.confectory/edit-workspaces/*/draft.json'));assert checkpoint.read_bytes()==before;invoke('schema',{'id':id});assert state()['schema']['parent']==n+'Monster';assert not any(p['origin']==id for p in state()['schema']['providers']);assert not any(u.get('creationOwner')==id for u in json.loads(checkpoint.read_text())['changes']);originals()
def complete_ui():
 owner().locator('[data-element-action=confirm]').click();expect(page.locator('#review-creation')).to_be_visible(timeout=60000);page.locator('#review-creation').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000);return review
def finish_boundary():
 assert not errors and not external,(errors,external);browser.close();p.stop();print(json.dumps({'checks':checks,'actualEngineRenderer':True,'nativeWindows':False,'actualAccountOrInference':False,'projectRun':False,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
def held_other():return [(key,value) for key,value in pending()['schema'] if '|'+n+'Target1|element|' in key]
def boundaries(mode,held,before):
 checkpoint=next(project.glob('.confectory/edit-workspaces/*/draft.json'))
 if mode=='scope-change':
  owner().locator('.object-parent-change').click();page.get_by_role('dialog',name='부모 변경',exact=True).locator('[data-parent-choice="'+n+'Unit"]').click();captured=pending();rejected_save();retained(captured);no_partial(before);checked('부모 변경으로 copy의 요구 슬롯이 사라지면 두 copy 준비 뒤 최종 전체 검증에서 선언/schema/등록/모든 copy를 미적용한다');restart(1);retained(captured);no_partial(before);owner().locator('.object-parent-change').click();page.get_by_role('dialog',name='부모 변경',exact=True).locator('[data-parent-choice="'+n+'Alternate"]').click();owner().locator('[data-element-action=save]').click();wait_saved();originals();checked('실제 cold 뒤 사용자가 호환 부모를 명시적으로 다시 선택하면 원래 두 copy/입력만 함께 저장한다');finish_boundary()
 if mode=='storage':
  checkpoint.chmod(0o400)
  try:rejected_save();retained(held);no_partial(before);checked('실제 저장 거절은 두 copy/선언/새 schema/모든 값을 미적용하고 원래 source와 다른 객체 입력을 보존한다');restart(1);retained(held);no_partial(before);checked('저장 실패 cold 복원은 구조와 정확한 typed 입력/순서/두 private snapshot을 그대로 유지한다')
  finally:checkpoint.chmod(0o600)
  owner().locator('[data-element-action=save]').click();wait_saved();assert held_other()==other_input;originals();checked('명시적 재시도는 한 후보만 수용하고 다른 객체 미저장 입력을 유지한다');finish_boundary()
 if mode=='conflict':
  invoke('schema',{'id':id});d=state()['schema'];invoke('editDescription',{'id':id,'revision':d['revision'],'hash':d['textHash'],'value':'동료가 먼저 저장'});invoke('saveDraft',{});peer=checkpoint.read_bytes();rejected_save();retained(held);assert checkpoint.read_bytes()==peer;invoke('schema',{'id':id});assert state()['schema']['description']=='동료가 먼저 저장' and not any(p['origin']==id for p in state()['schema']['providers']);originals();checked('다른 편집자의 실제 owner 저장 뒤 전체 혼합 요청은 거절되고 동료 checkpoint/모든 private 입력을 보존한다');restart(1);retained(held);assert checkpoint.read_bytes()==peer and held_other()==other_input;originals();checked('실제 충돌 후 cold 복원은 오래된 계획을 자동 재기준화하거나 두 copy 중 일부를 만들지 않는다');finish_boundary()
 if mode=='cancel':
  owner().locator('[data-element-action=discard]').click();expect(owner().locator('[data-element-action=discard]')).to_be_disabled(timeout=30000);now=pending();assert not any('|'+id+'|element|' in key for key,_ in now['schema']) and not now['blueprint'];assert held_other()==other_input;assert not json.loads(checkpoint.read_text())['privateCopies'];originals();checked('원본 취소는 해당 owner의 구조/typed 값/두 copy만 정리하고 다른 객체 입력·부모·원본을 유지한다');restart(1);assert held_other()==other_input;assert not pending()['blueprint'];expect(owner().locator('[aria-label="HP 기본값"]')).to_have_value('101');expect(owner().locator('[aria-label="MP 기본값"]')).to_have_value('4');originals();checked('취소 cold 복원에 새 schema/부분 copy/선언 반영이 없고 다른 객체 입력은 그대로 남는다');finish_boundary()
 if mode=='response-loss':
  ids=set();lost={}
  def intercept(route):
   command=route.request.post_data_json
   if command.get('op')=='invoke' and command.get('endpoint')=='blueprint' and command.get('input',{}).get('action')=='applySlots':ids.add(command['requestId'])
   response=route.fetch();payload=response.json()
   if not lost and command.get('op')=='update' and any(v.get('requestId') in ids for v in payload.get('results',[])):
    assert all(v.get('ok') for v in payload['results'] if v.get('requestId') in ids);lost.update(route=route,response=response,payload=payload);return
   route.fulfill(response=response)
  page.route('**/api/request',intercept);owner().locator('[data-element-action=save]').click()
  for _ in range(2400):
   if lost:break
   page.wait_for_timeout(20)
  assert lost,'real successful wide result not received';owner().locator('.object-title-description').fill('응답 대기 중 새 설명');owner().locator('[aria-label="MP 기본값"]').fill('9007199254740997');field(['Combat','Power']).locator('input').fill('9223372036854775807');payload=lost['payload'];payload['results']=[{'requestId':v['requestId'],'ok':False,'error':{'code':'transport-interrupted'}} if v.get('requestId') in ids else v for v in payload['results']];lost['route'].fulfill(response=lost['response'],json=payload);expect(owner().locator('[data-element-error]')).not_to_be_empty(timeout=30000);idle();page.unroute('**/api/request',intercept);now=pending();assert len(ids)==1 and not now['blueprint'];owned=[v for key,v in now['schema'] if '|'+id+'|element|' in key];assert len(owned)==3 and {v['kind'] for v in owned}=={'field','description'};assert any('9223372036854775807' in v['text'] for v in owned);assert held_other()==other_input;originals();checked('실제 성공 응답 유실은 전체 receipt로 한 번 확인하고 늦은 compound/정확한 long/설명을 유지하며 두 copy를 중복 생성하지 않는다');restart(1);expect(field(['Combat','Power']).locator('input')).to_have_value('9223372036854775807');expect(owner().locator('[aria-label="MP 기본값"]')).to_have_value('9007199254740997');owner().locator('[data-element-action=save]').click();wait_saved();assert held_other()==other_input;assert len([u for u in json.loads(checkpoint.read_text())['changes'] if u.get('creationOwner')==id and u['kind']=='implementation'])==2;originals();checked('cold 복원 후 늦은 typed 입력의 다음 Save가 유효한 동일 필드에만 적용되고 다른 객체·순서·원본을 보존한다');finish_boundary()
def ui():
 global page,browser,p,other_input
 other_input=[]
 start(0);p=sync_playwright().start();browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=setup();invoke('select',{'id':id});invoke('saveDraft',{});
 if len(sys.argv)>3 and sys.argv[3] in ['storage','conflict','cancel','response-loss']:
  open_owner(n+'Target1');owner().locator('.object-title-description').fill('다른 객체의 보관 입력');other_input=held_other();owner().locator('[data-close]').first.click()
 open_owner();edit_owner();held_owner=pending()['schema'];assert {v['kind'] for _,v in held_owner}=={'field','description','unset','parent','modules','definition'};select_copy('Slot','AliasBody','slotCount=amount+5;slotReady=true;return amount+70;',True);assert pending()['schema']==held_owner;select_copy('Slot2','SlotBody2','slotCount=amount+9;slotReady=true;return '+('MissingCompilerSymbol' if len(sys.argv)>3 and sys.argv[3]=='compiler' else 'amount+90')+';');held=pending();assert len([v for _,v in held['blueprint'] if v.get('kind')=='copy-selection'])==2;originals();page.screenshot(path=str(case/'wide-mixed-pending.png'));checked('원본 UI에서 구조/스칼라/복합·배열·ref·local reset·새 속성 입력 뒤 두 copy 본문/wrapper를 골라도 모든 입력과 원본을 보존한다')
 checkpoint=next(project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();mode=sys.argv[3] if len(sys.argv)>3 else 'ui'
 if mode in ['storage','conflict','cancel','response-loss','scope-change']:boundaries(mode,held,before)
 if mode=='last-copy':
  injected=[]
  def invalid(route):
   request=route.request.post_data_json
   if request.get('op')=='invoke' and request.get('endpoint')=='blueprint' and request.get('input',{}).get('action')=='applySlots':
    assert len(request['input']['rows'])==2;request['input']['rows'][-1]['edits'][0]['node']='not-owned';injected.append(request['requestId']);route.continue_(post_data=json.dumps(request));return
   route.continue_()
  page.route('**/api/request',invalid);rejected_save();page.unroute('**/api/request',invalid);assert len(injected)==1;retained(held);no_partial(before);checked('실제 전송 마지막 copy만 부적합해도 앞 copy/새 schema/부모/모듈/값/manifest를 모두 미적용하고 입력을 보존한다');restart(1);retained(held);no_partial(before);checked('마지막 copy 거절 뒤 실제 재시작에서도 전체 원래 snapshot/입력/순서를 복원하고 부분 저장을 남기지 않는다')
 owner().locator('[data-element-action=save]').click();wait_saved();expect(owner().locator('[aria-label="Bonus 기본값"]')).to_have_value('9007199254740993');expect(owner().locator('[aria-label="MP 기본값"]')).to_have_value('9007199254740995');expect(field(['Combat','Power']).locator('input')).to_have_value('9223372036854775805');expect(field(['Loadout','Power']).locator('input')).to_have_value('9223372036854775806');expect(owner().locator('[aria-label="HP 기본값"]')).to_have_value('200');expect(owner().locator('.object-parent-reference')).to_contain_text('Alternate');originals();saved=json.loads(checkpoint.read_text());assert not saved['privateCopies'];assert len([u for u in saved['changes'] if u['kind']=='implementation' and u.get('creationOwner')==id])==2;assert len([u for u in saved['changes'] if u['kind']=='schema' and u.get('creationOwner')==id])==1;checked('원본 Save 한 번이 두 copy/import/wrapper/본문과 구조·모든 typed 값·새 schema/등록을 한 후보/CAS로 수용한다')
 restart(2);expect(owner().locator('[aria-label="Bonus 기본값"]')).to_have_value('9007199254740993');expect(owner().locator('[aria-label="MP 기본값"]')).to_have_value('9007199254740995');expect(field(['Combat','Label']).locator('input')).to_have_value('함께 한글');expect(owner().locator('[aria-label="Note 기본값"]')).to_have_value('새 속성 "한글"');originals();review=complete_ui();
 if mode=='compiler':
  assert state()['review']['status']=='ready' # Review captures the group; C# validation occurs at explicit Confirm.
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  before_confirm=checkpoint.read_bytes();review.locator('#confirm').click();expect(review.locator('#confirm')).to_be_disabled(timeout=120000);idle();rejected=state()['review'];assert rejected['status']=='invalid',rejected;assert 'MissingCompilerSymbol' in json.dumps(rejected);assert checkpoint.read_bytes()==before_confirm;originals();checked('마지막 copy의 실제 C# 컴파일 실패는 전체 그룹의 최종 반영을 막고 첫 copy/선언/원본 파일을 바꾸지 않으며 전체 임시 초안을 보존한다');review.locator('[data-reject]').click();expect(review).to_be_hidden();slot=owner().locator('[data-module-method="'+n+'Slot2"]');slot.locator('[data-function-edit]').click();expect(author().locator('[data-bp-node=body]')).to_be_visible(timeout=60000);edit_region(author().locator('[data-bp-node=body] [data-internal-code]'),'slotCount=amount+9;slotReady=true;return MissingCompilerSymbol;','slotCount=amount+9;slotReady=true;return amount+90;');author().locator('[data-bp-save]').click();expect(author().locator('.bp-status')).to_have_text('복사본 · Slime · common',timeout=30000);close_author();originals();review=complete_ui();checked('같은 저장 그룹에서 마지막 본문을 명시적으로 고친 뒤 재검토하며 다른 copy/typed값/새 schema를 보존한다')
 review.locator('[data-reject]').click();expect(review).to_be_hidden();originals();checked('cold 복원과 그룹 Review 취소가 두 구현·정확한 숫자·한글·새 속성/부모/순서를 보존하고 원본에 반영하지 않는다');review=complete_ui()
 if review.locator('[data-review-advanced]').count():
  review.locator('[data-review-advanced]').click()
  if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
 review.locator('#confirm').click();expect(review).to_have_count(0,timeout=120000);idle();assert {k for k,v in original.items() if (project/k).read_bytes()!=v}=={'Slime.celem','project.cproj'};checked('실제 명시적 compiler Confirm은 해당 owner/등록/새 schema/두 copy만 반영하고 donor/부모/다른 target 소스를 보존한다');assert not errors and not external,(errors,external);browser.close();p.stop()
if __name__=='__main__':
 try:
  if len(sys.argv)>3 and sys.argv[3]=='backend':backend()
  else:ui()
 except Exception:
  evidence={'checks':checks,'errors':errors,'traffic':traffic[-30:]}
  try:evidence['messages']=owner().locator('[data-element-error]').all_text_contents();page.screenshot(path=str(case/'failure.png'))
  except Exception:pass
  (case/'failure.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2));print('EVIDENCE '+str(case),flush=True);raise
 finally:stop()
 print(json.dumps({'checks':checks,'actualEngine':True,'renderer':len(sys.argv)<4 or sys.argv[3]!='backend','nativeWindows':False,'accountOrInference':False,'projectRun':False,'evidence':str(case)},ensure_ascii=False,indent=2))
