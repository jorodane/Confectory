"""Immutable private snapshot + explicit stale ABI + minimum mixed UI, isolated real engine; no account/inference/run."""
import json,re,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
nested='nested' in sys.argv[4:];is_view='view' in sys.argv[4:];general='remap' in sys.argv[4:]
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-private-copy-ui-'));project=case/'owned project';project.mkdir();storage=case/'profile';storage.mkdir();n='Owned.Elements::';id=n+'Monster'
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
if is_view:items['FreeInfo']=('schema','schema '+n+'FreeInfo {field HP single general long;value editorInformationDefaults="typed-json-v1";value editorFieldDefault_HP="100";module '+n+'Rules;provide '+n+'Slot with '+n+'AliasBody;}')
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
 page=browser.new_page(viewport={'width':2300,'height':1700} if is_view else {'width':1280,'height':900});page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',observe);page.route('**/*',route);goto_editor(page,url);return page
def metadata(operation,**request):
 r=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':operation,**request}),text=True,capture_output=True,env=env,check=True);v=json.loads(r.stdout);assert v['ok'],v;return v['result']
# A current wrapped imported call is copied, not repaired in its donor. Windows
# remains a separate untouched source body; only common is explicitly chosen.
native='function '+n+'Native (ref long input) -> long {provide '+n+'Native with '+n+'NativeBody;}'
(project/'Native.celem').write_text(native);(project/'NativeBody.celem').write_text('implementation '+n+'NativeBody for '+n+'Native (ref long input) -> long {body common "Native.csbody";}');(project/'Native.csbody').write_text('return input+3;');manifest=project/'project.cproj';manifest.write_text(manifest.read_text().replace('registry Confectory.Build.DotNet','element Native function "Native.celem";element NativeBody implementation "NativeBody.celem";registry Confectory.Build.DotNet'))
registered=len(sys.argv)>3 and sys.argv[3]=='registered-callee';callee='Lib::Native' if registered else n+'Native';lib=case/'Lib';foreign_original={}
if registered:
 lib.mkdir();native=native.replace(n+'Native',callee);(lib/'Native.celem').write_text(native);(lib/'NativeBody.celem').write_text('implementation Lib::NativeBody for Lib::Native (ref long input) -> long {body common "Native.csbody";}');(lib/'Native.csbody').write_text('return input+3;');(lib/'pack.cpack').write_text('pack Lib version "1" {element Native function "Native.celem";element NativeBody implementation "NativeBody.celem";}');manifest.write_text(manifest.read_text().replace('registry Confectory.Build.DotNet','registry Lib "../Lib/pack.cpack";dependency Lib version "1";registry Confectory.Build.DotNet'));foreign_original={p:p.read_bytes() for p in lib.iterdir()}
fn='function '+n+'Slot (long amount,out long slotCount,out bool slotReady) -> long {}';initial=metadata('blueprintPrepareFeature',id=n+'Slot',text=fn,implementation=n+'SlotBody',graphPath='Slot.graph.json',nodePath='Slot.node.json');initial['implementation']=initial['implementation'].replace('{','{\nimport '+n+'Donor as Gift (long,out long,out bool) -> long in '+n+'Unit;\n',1).replace('\n}\n','\nbody windows "SlotWindows.csbody";\n}\n')
prepared=metadata('blueprintPrepareCall',id=n+'SlotBody',text=initial['implementation'],targetText=native,graph=initial['graph'],definition={'id':'native','feature':callee,'intent':'원본 호출','control':'next'});g=prepared['graph'];g['profile']='sync-acyclic-switch-v1';node=next(v for v in g['nodes'] if v['id']=='native');node['arguments']={'input':{'input':'amount'}};node['control']='switch';enum={'primary':'next','members':[{'id':'next','name':'NoBranch','value':0}]};wrapper=metadata('blueprintCallWrapper',functionText=native,executionEnum=enum,returnMapping='native-return-out-v1',source='return Result.NoBranch;');node['executionEnum']=enum;node['postCall']={'mode':'execution-enum','returnMapping':'native-return-out-v1','contractHash':wrapper['contractHash'],'source':wrapper['source'],'helpers':''};g['entry']='native';g['edges'].append({'from':'native','port':'next','to':'body'});next(v for v in g['nodes'] if v['id']=='body')['arguments']['amount']={'node':'native'}
if nested:
 child={'schema':1,'profile':'sync-acyclic-switch-v1','entry':'native','nodes':[json.loads(json.dumps(node))],'edges':[{'from':'native','port':'next','to':'exit:return'}],'exits':{'return':{'node':'native'}},'locals':[{'id':'kept','name':'정확한 private 값','type':'long','initial':{'constant':9223372036854775806}}]};child['nodes'][0]['arguments']={'input':{'input':'amount'}}
 body_node=next(v for v in g['nodes'] if v['id']=='body');body_node['arguments']['amount']={'node':'frame'};g.update(profile='sync-acyclic-nested-v1',entry='frame',nodes=[{'id':'frame','kind':'graph','control':'next','intent':'기존 private 호출','signature':{'args':[{'name':'amount','type':'long'}],'return':'long'},'arguments':{'amount':{'input':'amount'}},'graph':child},*[v for v in g['nodes'] if v['id']!='native']],edges=[{**e,'from':'frame' if e['from']=='native' else e['from']} for e in g['edges']])
defs=metadata('featureBlueprintNodes',featureSource=fn,graph=g,featureContracts={callee:native,n+'Donor':items['Donor'][1]});(project/'SlotBody.celem').write_text(prepared['implementation']);(project/'Slot.graph.json').write_text(json.dumps(g));body='slotCount=amount+1;slotReady=false;return amount+3;';record={'schema':1,'node':'body','definitionHash':next(v for v in defs['nodes'] if v['id']=='body')['definitionHash'],'source':body};(project/'Slot.node.json').write_text(json.dumps(record));original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file()}
assert metadata('featureBlueprintDescribe',featureSource=fn,graph=g,featureContracts={callee:native,n+'Donor':items['Donor'][1]},implementations={'body':record})['state']=='source-ready'
def originals():assert all((project/k).read_bytes()==v for k,v in original.items()) and all(p.read_bytes()==v for p,v in foreign_original.items())
def idle():expect(page.locator('.brand')).to_be_enabled(timeout=60000)
def pending():page.evaluate('async()=>await confectoryFlushPresentation()');return state()['presentation']['inputs']
def owner():return page.locator('.window[data-key=editor-1]' if is_view else '.window[data-key=schema]')
def schema_state():return next(v for v in state()['editorViews'] if v['view']=='1')['schema'] if is_view else state()['schema']
def view_basis():
 if not is_view:return {}
 row=next(v for v in state()['editorViews'] if v['view']=='1');return {'view':'1','viewBinding':row['authorBinding']}

def author():return page.locator('.window[data-key=blueprint]')
def close_author():
 if author().is_visible():author().locator('[data-close]').first.click()
def edit_region(button,before,replacement):
 node=button.evaluate('(el)=>el.closest("[data-bp-node]").dataset.bpNode');author().locator(':scope > .window-title').click(position={'x':700,'y':12});author().locator('[data-bp-overview-node="'+node+'"]').click();button.click();dialog=page.locator('.bp-script-dialog');value=dialog.locator('[data-code-source]');expect(value).to_be_visible();assert before in value.input_value();value.evaluate('(el,text)=>{el.focus();const start=el.value.indexOf(text);el.setSelectionRange(start,start+text.length);}',before);page.keyboard.insert_text(replacement);dialog.locator('[data-code-save]').click();expect(dialog).to_be_hidden()
def retained(captured):
 now=pending()
 for group in ['schema','blueprint','views']:
  assert all(dict(now[group]).get(k)==v for k,v in captured.get(group,[])),(group,now[group])
 return now
def no_mixed_membership():
 invoke('schema',{'id':id});d=schema_state();assert d['description']!='함께 저장할 객체 설명';assert not any(v['origin']==id for v in d['providers']);originals()
def rejected_save():
 page.evaluate('''()=>{globalThis.boundaryMessages=[];globalThis.boundaryObserver=new MutationObserver(()=>{for(const el of document.querySelectorAll('[data-element-error],#status')){const text=el.textContent;if(text&&!boundaryMessages.includes(text))boundaryMessages.push(text)}});boundaryObserver.observe(document.body,{subtree:true,childList:true,characterData:true})}''')
 owner().locator('[data-element-action=save]').click();page.wait_for_function('()=>boundaryMessages.some(text=>/바뀌|입력.*유지|실패|완료하지|consumer_error|stale|changed/i.test(text))',timeout=30000);page.evaluate('()=>boundaryObserver.disconnect()');idle()
def restart(i):
 global page
 pending();page.close();stop();start(i);page=setup();expect(owner().locator('[aria-label="HP 기본값"]')).to_be_visible(timeout=60000);idle()
def advance():
 global original,foreign_original
 source_root=lib if registered else project;before=(source_root/'Native.celem').read_text();replacement='(long input) -> long' if nested and not general else '(int step,double renamed,out long total) -> bool';after=before.replace('(ref long input) -> long',replacement);(source_root/'Native.celem').write_text(after);(source_root/'NativeBody.celem').write_text((source_root/'NativeBody.celem').read_text().replace('(ref long input) -> long',replacement));(source_root/'Native.csbody').write_text('return input+3;' if nested and not general else 'total=checked((long)renamed);return step>0;')
 if registered:foreign_original={p:p.read_bytes() for p in lib.iterdir()}
 text=(project/'SlotBody.celem').read_text();current=json.loads((project/'Slot.graph.json').read_text());defs=metadata('featureBlueprintNodes',featureSource=fn,graph=current,featureContracts={callee:after,n+'Donor':items['Donor'][1]},inspectStalePostCalls=True);row=next(v for v in defs['nestedNodes' if nested else 'nodes'] if v['id']==('frame/native' if nested else 'native'));single=text.replace('body windows "SlotWindows.csbody";','');changed=metadata('blueprintCallAbi',id=n+'SlotBody',text=single,graph=current,node='native',signature=row['currentCallSignature'],contractHash=row['postCallEditor']['contractHash'],**({'privatePath':'frame'} if nested else {}),**({'remap':{'inputs':{'step':{'valueJson':'3'},'renamed':'input'},'outputs':{'return':'total'}}} if not nested or general else {}));(project/'SlotBody.celem').write_text(changed['implementation'].replace('\n}', '\nbody windows "SlotWindows.csbody";\n}'));(project/'Slot.graph.json').write_text(json.dumps(changed['graph']));defs=metadata('featureBlueprintNodes',featureSource=fn,graph=changed['graph'],featureContracts={callee:after,n+'Donor':items['Donor'][1]});(project/'Slot.node.json').write_text(json.dumps({'schema':1,'node':'body','definitionHash':next(v for v in defs['nodes'] if v['id']=='body')['definitionHash'],'source':'slotCount=amount+99;slotReady=true;return amount+99;'}));original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts}
def seed_snapshot():
 checkpoint=next(project.glob('.confectory/edit-workspaces/*/draft.json'));data=json.loads(checkpoint.read_text());seeds=data.get('privateCopies',{});assert len(seeds)==1,seeds;return checkpoint,data,next(iter(seeds.values()))
def save_owner():
 owner().locator('[data-element-action=save]').click()
 for _ in range(2400):
  now=pending()
  if not now['schema'] and not any(v.get('kind') in ['copy-selection','copy-attempt'] or '|v508-author|' in k for k,v in now['blueprint']):return
  error=owner().locator('[data-element-error]').inner_text()
  if error:raise AssertionError(error)
  page.wait_for_timeout(20)
 raise AssertionError('save did not settle')
seed_lost={};seed_request_ids=set()
def initial_boundary_setup():
 mode=sys.argv[3] if len(sys.argv)>3 else ''
 if mode=='seed-storage':
  checkpoint=next(project.glob('.confectory/edit-workspaces/*/draft.json'));seed_lost['before']=checkpoint.read_bytes();seed_lost['checkpoint']=checkpoint;checkpoint.chmod(0o400)
 elif mode=='seed-response-loss':
  def intercept(route):
   body=route.request.post_data_json
   if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('action')=='readImplementationCopy':seed_request_ids.add(body['requestId']);seed_lost['implementation']=body['input']['implementation']
   response=route.fetch();payload=response.json()
   if not seed_lost.get('lost') and body.get('op')=='update' and any(v.get('requestId') in seed_request_ids for v in payload.get('results',[])):
    assert all(v.get('ok') for v in payload['results'] if v.get('requestId') in seed_request_ids);seed_lost['lost']=True;seed_lost['snapshot']=seed_snapshot()[2];payload['results']=[{'requestId':v['requestId'],'ok':False,'error':{'code':'transport-interrupted'}} if v.get('requestId') in seed_request_ids else v for v in payload['results']];route.fulfill(response=response,json=payload);return
   route.fulfill(response=response)
  seed_lost['intercept']=intercept;page.route('**/api/request',intercept)
def initial_boundary_finish():
 global page
 mode=sys.argv[3] if len(sys.argv)>3 else ''
 if mode not in ['seed-storage','seed-response-loss']:return
 page.wait_for_function('()=>document.querySelector(".window[data-key=blueprint] .bp-load-error")||[...document.querySelectorAll(".window[data-key=blueprint] [role=alert],#status")].some(e=>e.textContent.trim())',timeout=60000);idle();retained({'schema':held_owner,'blueprint':[]})
 if mode=='seed-storage':
  checkpoint=seed_lost['checkpoint'];assert checkpoint.read_bytes()==seed_lost['before'];assert not json.loads(checkpoint.read_text()).get('privateCopies');originals();checkpoint.chmod(0o600);checked('최초 snapshot metadata 쓰기 실패는 기존 checkpoint/owner 입력을 유지하고 등록/반쪽 seed를 만들지 않는다')
 else:
  assert seed_lost.get('lost') and len(seed_request_ids)==1;page.unroute('**/api/request',seed_lost['intercept']);checkpoint,_,seed=seed_snapshot();assert seed['snapshot']['implementation']==seed_lost['implementation'];originals();checked('최초 선택의 실제 성공 응답 유실 뒤에도 원래 seed는 source 등록 없이 한 번만 보관된다')
 pending();page.close();stop();start(3);page=setup();expect(author().locator('[data-bp-node=native]')).to_be_visible(timeout=60000);idle();checkpoint,_,seed=seed_snapshot();assert pending()['schema']==held_owner
 if mode=='seed-response-loss':assert seed==seed_lost['snapshot']
 assert len(json.loads(checkpoint.read_text())['privateCopies'])==1;originals();checked('최초 선택 재시작 재시도는 보관한 동일 copy identity/원래 snapshot을 사용하고 owner 입력·원본/부모/다른 target을 유지한다');finish_boundary()
def finish_boundary():
 assert not errors and not external,(errors,external);browser.close();p.stop();print(json.dumps({'checks':checks,'actualEngineRenderer':True,'nativeWindows':False,'actualAccountOrInference':False,'projectRun':False,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
def no_membership():
 invoke('schema',{'id':id});d=schema_state();assert d['description']!='비공개 ABI 함께 저장';assert not any(v['origin']==id for v in d['providers']);originals()
def boundaries(mode,held,checkpoint,immutable):
 if mode=='storage':
  before=checkpoint.read_bytes();checkpoint.chmod(0o400)
  try:
   rejected_save();assert checkpoint.read_bytes()==before;retained(held);no_membership();assert json.dumps(seed_snapshot()[2],sort_keys=True)==immutable;checked('실제 체크포인트 쓰기 거절은 새 copy/import/ABI/owner 값을 모두 미적용하고 원래 seed와 입력을 보존한다');restart(2);retained(held);assert checkpoint.read_bytes()==before;no_membership();assert json.dumps(seed_snapshot()[2],sort_keys=True)==immutable;checked('저장 실패 뒤 cold 복원은 원래 private 기준과 모든 입력을 유지하며 자동 재기준화하지 않는다')
  finally:checkpoint.chmod(0o600)
  save_owner();assert not json.loads(checkpoint.read_text()).get('privateCopies');originals();checked('같은 입력의 다음 명시적 재시도는 한 번만 전체 수용하며 원래 donor/부모/다른 target을 유지한다');finish_boundary()
 if mode in ['callee-conflict','owner-conflict']:
  if mode=='callee-conflict':
   # A real file change after explicit review. Do not invent a compatible new plan.
   native=project/'Native.celem';native.write_text(native.read_text().replace('{','{description \"갱신 뒤 바뀐 실제 호출 계약 문서\";',1));original[str(native.relative_to(project))]=native.read_bytes()
  else:
   invoke('schema',{'id':id});d=schema_state();invoke('editDescription',{'id':id,'revision':d['revision'],'hash':d['textHash'],'value':'다른 편집자의 저장'});invoke('saveDraft',{})
  before=checkpoint.read_bytes();rejected_save();retained(held);no_membership();assert checkpoint.read_bytes()==before;assert json.dumps(seed_snapshot()[2],sort_keys=True)==immutable;checked('명시적 갱신 뒤 실제 '+mode+' 변경은 전체 거절하고 peer 저장·원래 snapshot·모든 private 입력을 보존한다');restart(2);retained(held);assert checkpoint.read_bytes()==before;assert json.dumps(seed_snapshot()[2],sort_keys=True)==immutable;originals();checked('실제 충돌 뒤 재시작해도 낡은 계획을 새 기준으로 승격하거나 copy를 부분 생성하지 않는다');finish_boundary()
 if mode=='cancel':
  owner().locator('[data-element-action=discard]').click();expect(owner().locator('[data-element-action=discard]')).to_be_disabled(timeout=30000);now=pending();assert not now['schema'] and not now['blueprint'];assert not json.loads(checkpoint.read_text()).get('privateCopies');no_membership();checked('원본 변경취소는 presentation 입력 보관 정리 뒤 정확한 seed만 제거하고 source/membership를 만들지 않는다');restart(2);assert not pending()['schema'] and not pending()['blueprint'];no_membership();expect(owner().locator('[aria-label="HP 기본값"]')).to_have_value('100');checked('취소 뒤 실제 재시작에는 copy/owner 변경이 없고 기존 원본과 입력창 상태가 복원된다');finish_boundary()
 if mode=='cancel-late':
  before=checkpoint.read_bytes();checkpoint.chmod(0o400)
  try:rejected_save()
  finally:checkpoint.chmod(0o600)
  retained(held);assert checkpoint.read_bytes()==before;slot=owner().locator('[data-module-method="'+n+'Slot"]');edit=slot.locator('[data-function-edit]');edit.click() if edit.count() else slot.locator('[data-function-write-direct]').click();expect(author().locator('[data-bp-node=body]')).to_be_visible(timeout=60000);idle();ids=set();paused={}
  def intercept(route):
   command=route.request.post_data_json
   if command.get('op')=='invoke' and command.get('endpoint')=='blueprint' and command.get('input',{}).get('action')=='readImplementationCopy':ids.add(command['requestId'])
   response=route.fetch();payload=response.json()
   if not paused and command.get('op')=='update' and any(v.get('requestId') in ids for v in payload.get('results',[])):paused.update(route=route,response=response);return
   route.fulfill(response=response)
  page.route('**/api/request',intercept);author().locator(':scope > .window-title [data-fold]').first.click();owner().locator('[data-element-action=discard]').click()
  for _ in range(1800):
   if paused:break
   page.wait_for_timeout(20)
  assert paused,'cancel live-state check not observed';author().locator(':scope > .window-title [data-fold]').first.click();author().locator('[data-bp-overview-node="body"]').click();author().locator('[data-bp-node=body] [data-inline-description]').fill('취소 대기 중 새 복사 입력');paused['route'].fulfill(response=paused['response']);expect(owner().locator('[data-element-error]')).not_to_be_empty(timeout=30000);idle();page.unroute('**/api/request',intercept);retained(held);now=pending();assert any(v.get('type')=='intent' and v.get('text')=='취소 대기 중 새 복사 입력' for _,v in now['blueprint']);assert checkpoint.read_bytes()==before and json.dumps(seed_snapshot()[2],sort_keys=True)==immutable;no_membership();checked('취소의 비동기 확인 중 새 copy 입력이 생기면 취소 전체를 거절하고 원래 seed/기존 입력/새 입력을 유지한다');restart(3);retained(held);assert any(v.get('type')=='intent' and v.get('text')=='취소 대기 중 새 복사 입력' for _,v in pending()['blueprint']);assert json.dumps(seed_snapshot()[2],sort_keys=True)==immutable;no_membership();checked('늦은 입력으로 거절된 취소는 cold 재시작에서도 원래 snapshot과 새 입력을 복원하며 부분 등록을 남기지 않는다');finish_boundary()
 if mode=='response-loss':
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
  assert lost,'actual successful private Save result not observed';owner().locator('.object-title-description').fill('응답 대기 중 새 입력');owner().locator('[aria-label="HP 기본값"]').fill('9007199254740995');payload=lost['payload'];payload['results']=[{'requestId':v['requestId'],'ok':False,'error':{'code':'transport-interrupted'}} if v.get('requestId') in ids else v for v in payload['results']];lost['route'].fulfill(response=lost['response'],json=payload);expect(owner().locator('[data-element-error]')).not_to_be_empty(timeout=30000);idle();page.unroute('**/api/request',intercept);now=pending();assert len(ids)==1 and len(now['schema'])==2 and not now['blueprint'];assert {v['text'] for _,v in now['schema']}=={'응답 대기 중 새 입력','9007199254740995'};assert not json.loads(checkpoint.read_text()).get('privateCopies');originals();checked('실제 성공 응답 유실은 한 번의 receipt로 확인하고 늦은 owner 입력을 보존하며 같은 private snapshot을 중복 생성하지 않는다');restart(2);expect(owner().locator('.object-title-description')).to_have_value('응답 대기 중 새 입력');expect(owner().locator('[aria-label="HP 기본값"]')).to_have_value('9007199254740995');assert not pending()['blueprint'];d=schema_state();new=next(v['implementation'] for v in d['providers'] if v['function']==n+'Slot' and v['origin']==id);save_owner();assert state()['schema']['description']=='응답 대기 중 새 입력';assert len(invoke('blueprint',{'action':'list','feature':n+'Slot','query':new+'/body:'})['result']['result']['rows'])==1;originals();checked('응답 유실 뒤 cold 재시도는 새 owner 입력만 반영하고 copy/호출 연결을 중복하거나 원래 소스를 변경하지 않는다');finish_boundary()
try:
 start(0);p=sync_playwright().start();expect.set_options(timeout=60000);browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=setup();id=n+'Slime';invoke('select',{'id':id});invoke('saveDraft',{});page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');b.locator('[data-browser-control="object-query"]').fill('Slime');b.locator('[data-browser-control="object-search"]').click();row=b.locator('[data-object="'+id+'"]');expect(row).to_have_attribute('aria-disabled','false');row.press('Enter');idle();b.locator('[data-close]').first.click()
 if is_view:
  id=n+'FreeInfo';invoke('select',{'id':n+'Monster'});invoke('saveDraft',{});primary_text=state()['draft']['text'];invoke('openEditorView',{'view':'1','id':id,'viewMode':'properties'});expect(owner().locator('.object-title-name')).to_have_text('FreeInfo');idle()
 owner().locator('.object-title-description').fill('비공개 ABI 함께 저장');owner().locator('[aria-label="HP 기본값"]').fill('9007199254740993');held_owner=pending()['schema'];before=json.loads(next(project.glob('.confectory/edit-workspaces/*/draft.json')).read_text());slot=owner().locator('[data-module-method="'+n+'Slot"]');edit=slot.locator('[data-function-edit]');edit.click() if edit.count() else slot.locator('[data-function-write-direct]').click();picker=page.locator('.feature-import-dialog');expect(picker).to_be_visible(timeout=60000);initial_boundary_setup();picker.locator('[data-copy-source="'+n+'AliasBody"][data-copy-target=common]').click();initial_boundary_finish();expect(author().locator('[data-bp-node='+('body' if nested else 'native')+']')).to_be_visible(timeout=60000);checkpoint,data,seed=seed_snapshot();immutable=json.dumps(seed,sort_keys=True);assert data['changes']==before['changes'];assert pending()['schema']==held_owner;assert not any(v['id']==seed['snapshot']['implementation'] for v in data['changes']);originals();checked('최초 명시적 복사 선택은 원래 snapshot만 서버 checkpoint에 보관하고 미저장 owner 입력·원본·소스 등록을 변경하지 않는다')
 edit_region(author().locator('[data-bp-node=body] [data-internal-code]'),body,'slotCount=amount+5;slotReady=true;return amount+70;');held=pending()
 if nested:
  author().locator('[data-bp-overview-node=frame]').click();author().locator('[data-bp-node=frame] [data-function-write-direct]').click();expect(author().locator('[data-bp-node=native]')).to_be_visible();idle()
 page.screenshot(path=str(case/'private-before-callee-change.png'));pending();page.close();stop();advance();start(1);page=setup();
 expect(author().locator('[data-bp-node=native]')).to_be_visible(timeout=60000);idle();assert json.dumps(seed_snapshot()[2],sort_keys=True)==immutable;retained(held);refresh=author().locator('[data-bp-node=native] [data-wrapper-refresh]');expect(refresh).to_be_visible();expect(refresh).to_be_enabled();checked('실제 재시작에서 원래 snapshot·미저장 본문·정확한 long 입력을 복원하며 현재 donor의 새 본문으로 바꾸지 않고 ABI 갱신만 제시한다')
 author().locator(':scope > .window-title').click(position={'x':700,'y':12});author().locator('[data-bp-overview-node="native"]').click();refresh.click()
 if not nested or general:
  dialog=page.locator('[data-abi-remap-accept]').locator('..').locator('..');dialog.locator('[data-abi-input=step]').select_option('value');dialog.locator('[data-abi-value=step]').fill('3');dialog.locator('[data-abi-input=renamed]').select_option('pin:input');dialog.locator('[data-abi-output=return]').select_option('total');dialog.locator('[data-abi-remap-accept]').click()
 now=pending();wrapper_edit=next(v for _,v in now['blueprint'] if v.get('type')=='wrapper');plan=json.loads(wrapper_edit['text']);assert plan['abi']['privateCopyBinding']['seed']==seed['snapshot']['hash'];assert not plan['abi']['signature']['args'][0].get('mode');assert not registered or plan['abi']['receipt']['id']==callee;assert json.dumps(seed_snapshot()[2],sort_keys=True)==immutable;page.screenshot(path=str(case/'private-explicit-abi-refresh.png'))
 if nested:
  binding=plan['abi']['privateCopyBinding'];assert binding['privatePath']=='frame' and binding['node']=='frame/native';assert wrapper_edit['node']=='native';before_undo=dict(held['blueprint']);after_redo=dict(now['blueprint']);author().locator('.bp-viewport').focus();page.keyboard.press('Control+z');assert dict(pending()['blueprint'])==before_undo;author().locator('.bp-viewport').focus();page.keyboard.press('Control+Shift+z');assert dict(pending()['blueprint'])==after_redo;assert json.dumps(seed_snapshot()[2],sort_keys=True)==immutable;checked('private 호출의 기존 명시 갱신과 Undo/Redo는 qualified frame만 바꾸며 원래 snapshot/다른 본문 입력을 보존한다')
 close_author();held=pending();
 if len(sys.argv)>3:boundaries(sys.argv[3],held,checkpoint,immutable)
 save_owner();d=schema_state();new=next(v['implementation'] for v in d['providers'] if v['function']==n+'Slot' and v['origin']==id);result=invoke('blueprint',{'action':'read','id':new+'/body:common','owner':id,'ownerHash':d['textHash'],**view_basis()})['result']['result'];assert next(v for v in result['nodes'] if v['id']=='body')['source']=='slotCount=amount+5;slotReady=true;return amount+70;';private=invoke('blueprint',{'action':'read','id':new+'/body:common/graph:frame','owner':id,'ownerHash':d['textHash'],**view_basis()})['result']['result'] if nested else result;assert not next(v for v in private['nodes'] if v['id']=='native')['signature']['args'][0].get('mode');
 if is_view:assert state()['draft']['text']==primary_text and not pending()['views'];checked('독립 정보 창의 복사 갱신·저장은 primary 프로젝트 문맥과 원문을 변경하지 않는다')
 if nested:
  assert private['locals'][0]['initialJson']=='9223372036854775806';assert private['edges']==seed['snapshot']['graph']['nodes'][0]['graph']['edges'];assert private['nodes'][0]['postCall']['source']==seed['snapshot']['graph']['nodes'][0]['graph']['nodes'][0]['postCall']['source']
 assert d['description']=='비공개 ABI 함께 저장';expect(owner().locator('[aria-label="HP 기본값"]')).to_have_value('9007199254740993');assert not json.loads(checkpoint.read_text()).get('privateCopies');originals();checked('명시적 갱신은 원래 private 본문+현재 import/wrapper+owner 설명/정확한 long을 한 후보/CAS로 저장하고 접수한 seed만 제거한다')
 page.close();stop();start(2);page=setup();expect(owner().locator('[aria-label="HP 기본값"]')).to_have_value('9007199254740993',timeout=60000);idle();originals();owner().locator('[data-element-action=confirm]').click();expect(page.locator('#review-creation')).to_be_visible(timeout=60000);page.locator('#review-creation').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000);review.locator('[data-reject]').click();expect(review).to_be_hidden();originals();checked('혼합 저장의 cold 복원과 실제 Review 취소는 입력 결과·연결과 원본/부모/다른 target을 유지한다')
 owner().locator('[data-element-action=confirm]').click();expect(page.locator('#review-creation')).to_be_visible(timeout=60000);page.locator('#review-creation').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000)
 if review.locator('[data-review-advanced]').count():
  review.locator('[data-review-advanced]').click()
  if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
 review.locator('#confirm').click();expect(review).to_have_count(0,timeout=120000);idle();changed={k for k,v in original.items() if (project/k).read_bytes()!=v};assert changed=={('FreeInfo.celem' if is_view else 'Slime.celem'),'project.cproj'},changed;checked('실제 compiler Confirm은 새 copy/owner/등록만 반영하며 현재 donor·부모·Windows target bytes를 보존한다');assert not errors and not external,(errors,external);browser.close();p.stop()
except Exception:
 evidence={'checks':checks,'errors':errors,'traffic':traffic[-25:]}
 try:evidence['messages']=owner().locator('[data-element-error]').all_text_contents();page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 try:evidence['state']={k:v for k,v in state().items() if k in ['logs','sourceError','review']}
 except Exception:pass
 (case/'failure-state.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2));print('EVIDENCE '+str(case),flush=True);raise
finally:stop()
print(json.dumps({'checks':checks,'actualEngineRenderer':True,'nativeWindows':False,'accountOrInference':False,'projectRun':False,'evidence':str(case)},ensure_ascii=False,indent=2))
