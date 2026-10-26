"""Explicit ABI repair inside a saved local copy implementing a registered function.
The external implemented contract is immutable evidence, not a writable group member.
"""
import hashlib,json,re,os,pathlib,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-saved-copy-abi-'));project=case/'owned project';project.mkdir();n='Owned.Context::';root_feature='Root.Contracts::Calc'
env=os.environ.copy();env.update(CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'))
def metadata(operation,**data):
 r=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':operation,**data}),text=True,capture_output=True,env=env,check=True);v=json.loads(r.stdout);assert v['ok'],v;return v['result']
items={
 'Main':('function','function '+n+'Main () -> int {provide '+n+'Main with '+n+'MainBody;}'),
 'MainBody':('implementation','implementation '+n+'MainBody for '+n+'Main () -> int {import '+root_feature+' as Chosen (long) -> long in '+n+'A;body common "Main.csbody";}'),
 'Calc':('function','function '+root_feature+' (long amount) -> long {provide '+root_feature+' with '+n+'Copy;}'),
 'Native':('function','function '+n+'Native (ref long amount) -> long {provide '+n+'Native with '+n+'NativeBody;}'),
 'NativeBody':('implementation','implementation '+n+'NativeBody for '+n+'Native (ref long amount) -> long {body common "Native.csbody";}'),
 'Other':('implementation','implementation '+n+'Other for '+root_feature+' (long amount) -> long {body common "Other.csbody";}'),
 'Rules':('module','module '+n+'Rules {require '+root_feature+' (long) -> long;}'),
 'A':('schema','schema '+n+'A {module '+n+'Rules;provide '+root_feature+' with '+n+'Copy;}'),
 'B':('object','object '+n+'B {module '+n+'Rules;provide '+root_feature+' with '+n+'Other;}')}
registered='registered' in sys.argv[3:];callee='Lib::Native' if registered else n+'Native';callee_text=items['Native'][1].replace(n+'Native','Lib::Native') if registered else items['Native'][1]
lib=case/'Lib'
if registered:
 lib.mkdir();(lib/'Native.celem').write_text(callee_text.replace('(ref long','(long'));(lib/'NativeBody.celem').write_text('implementation Lib::NativeBody for Lib::Native (long amount) -> long {body common \"Native.csbody\";}');(lib/'Native.csbody').write_text('return amount+3;');(lib/'pack.cpack').write_text('pack Lib version \"1\" {element Native function \"Native.celem\";element NativeBody implementation \"NativeBody.celem\";}')
prepared=metadata('blueprintPrepareImplementation',owner=n+'A',ownerText=items['A'][1],id=root_feature,text='function '+root_feature+' (long amount) -> long {}',implementation=n+'Copy',graphPath='Copy.graph.json',nodePath='Copy.node.json')
defs=metadata('featureBlueprintNodes',featureSource=items['Calc'][1],graph=prepared['graph'])
record={'schema':1,'node':'body','definitionHash':defs['nodes'][0]['definitionHash'],'source':'return amount;'}
prepared=metadata('blueprintPrepareCall',id=n+'Copy',text=prepared['implementation'],targetText=callee_text,graph=prepared['graph'],definition={'id':'native','feature':callee,'intent':'기존 호출 계약 갱신','control':'next'})
g=prepared['graph'];g['profile']='sync-acyclic-switch-v1';node=next(v for v in g['nodes'] if v['id']=='native');node['arguments']={'amount':{'input':'amount'}};g['entry']='native';g['edges'].append({'from':'native','port':'next','to':'body'});next(v for v in g['nodes'] if v['id']=='body')['arguments']={'amount':{'node':'native'}}
enum={'primary':'next','members':[{'id':'next','name':'NoBranch','value':0}]}
wrapper=metadata('blueprintCallWrapper',functionText=callee_text,executionEnum=enum,returnMapping='native-return-out-v1',source='return Result.NoBranch;')
node.update(control='switch',executionEnum=enum,postCall={'mode':'execution-enum','returnMapping':'native-return-out-v1','contractHash':wrapper['contractHash'],'source':wrapper['source'],'helpers':''})
items['Copy']=('implementation',prepared['implementation'])
items['Native']=(items['Native'][0],items['Native'][1].replace('(ref long','(long'));items['NativeBody']=(items['NativeBody'][0],items['NativeBody'][1].replace('(ref long','(long'))
# The saved independent donor/copy snapshot predates the callee ABI change.
# This is not a claim that the new-copy API already supports wrapped graphs.
provenance={'implementation':n+'Donor','target':'common','bodyOrigin':n+'Donor','sourceKind':'blueprint'}
donor=__import__('copy').deepcopy(g);next(v for v in donor['nodes'] if v['id']=='body')['implementation']='Donor.node.json';items['Donor']=('implementation',prepared['implementation'].replace(n+'Copy',n+'Donor').replace('Copy.graph.json','Donor.graph.json'));g['copySource']=provenance
# The donor has independently adopted the current ABI; the saved copy still
# carries its older snapshot. The product repair must never rewrite the donor.
if 'stale-donor' not in sys.argv[3:]:
 current_wrapper=metadata('blueprintCallWrapper',functionText=callee_text.replace('(ref long','(long'),executionEnum=enum,returnMapping='native-return-out-v1',source=wrapper['source'])
 current_donor=metadata('blueprintCallAbi',id=n+'Donor',text=items['Donor'][1],graph=donor,node='native',signature={'args':[{'type':'long','name':'amount'}],'return':'long'},contractHash=current_wrapper['contractHash'])
 items['Donor']=('implementation',current_donor['implementation']);donor=current_donor['graph']
sources={'Donor.graph.json':json.dumps(donor),'Donor.node.json':json.dumps(record),'Main.csbody':'return checked((int)calls.Chosen.Invoke(1));','Other.csbody':'return amount+8;','Native.csbody':'return amount+3;','Copy.graph.json':json.dumps(g),'Copy.node.json':json.dumps(record)}
root_pack=case/'Root.Contracts';root_pack.mkdir();root_text='function '+root_feature+' (long amount) -> long {}';(root_pack/'Calc.celem').write_text(root_text);(root_pack/'pack.cpack').write_text('pack Root.Contracts version "1" {element Calc function "Calc.celem";}');del items['Calc']
for name,(kind,text) in items.items():sources[name+'.celem']=text
sources['project.cproj']='project Owned.Context version "1" {standalone true;entry '+n+'Main;'+''.join('element '+name+' '+kind+' "'+name+'.celem";' for name,(kind,text) in items.items())+'registry Confectory.Build.DotNet "'+str(repo/'targets/dotnet/pack.cpack')+'";dependency Confectory.Build.DotNet version "0.1.0";target portable Confectory.Build.DotNet::Portable;target linux Confectory.Build.DotNet::Linux;}'
sources['project.cproj']=sources['project.cproj'].replace('registry Confectory.Build.DotNet','registry Root.Contracts \"../Root.Contracts/pack.cpack\";dependency Root.Contracts version \"1\";registry Confectory.Build.DotNet')
if registered:sources['project.cproj']=sources['project.cproj'].replace('registry Confectory.Build.DotNet', 'registry Lib \"../Lib/pack.cpack\";dependency Lib version \"1\";registry Confectory.Build.DotNet')
foreign_original={p:p.read_bytes() for p in lib.iterdir()} if registered else {};foreign_original.update({p:p.read_bytes() for p in root_pack.iterdir()})
for name,text in sources.items():(project/name).write_bytes(text.encode())
original={p.name:p.read_bytes() for p in project.iterdir()};env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(case/'profile'),CONFECTORY_ENTRY_STORAGE=str(case/'profile'),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;traffic=[];results={};errors=[];external=[];checks=[]
def stop():
 global host,log
 if host and host.poll() is None:os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=15)
 if log:log.close()
def start(index):
 global host,log,url,origin,token
 f=case/f'host-{index}.log';log=f.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 for _ in range(600):
  urls=[v.split(' ',1)[1] for v in f.read_text().splitlines() if v.startswith('CONFECTORY_WEB_UI ')]
  if urls:url=urls[-1];origin,token=url.split('/#');return
  assert host.poll() is None,f.read_text();time.sleep(.05)
 raise AssertionError('host startup')
def raw(body):return json.load(urllib.request.urlopen(urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token}),timeout=30))
def mount():
 for _ in range(1000):
  row=raw({'op':'mount'})
  if row.get('ok'):return row
  assert row.get('error',{}).get('code')=='busy',row;time.sleep(.02)
 raise AssertionError('mount admission deadline')
def state():
 v=mount()
 try:return v['state']
 finally:raw({'op':'dispose','view':v['view']})
def call(endpoint,body,ok=True):
 for _ in range(4):
  v=mount();rid=uuid.uuid4().hex
  try:
   assert raw({'op':'invoke','view':v['view'],'scope':v['scope'],'expectedRevision':v['revision'],'requestId':rid,'endpoint':endpoint,'input':body})['ok']
   for _ in range(12000):
    r=raw({'op':'update','view':v['view'],'scope':v['scope']});rows=[row for row in r.get('results',[]) if row['requestId']==rid]
    if rows:break
    time.sleep(.01)
   assert rows,(endpoint,r)
   if rows[0].get('error',{}).get('code')=='stale_revision':continue
   assert bool(rows[0].get('ok'))==ok,rows
   return rows[0].get('result') if ok else rows[0]
  finally:raw({'op':'dispose','view':v['view']})
 raise AssertionError('transport revision changed before execution')
def checked(message):checks.append(message);(case/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2));print('PASS '+message,flush=True)
def unchanged():
 assert all((project/k).read_bytes()==v for k,v in original.items())
 assert all(p.read_bytes()==v for p,v in foreign_original.items())
def setup(browser):
 page=browser.new_page(viewport={'width':1480,'height':1050});page.on('pageerror',lambda e:errors.append(str(e)))
 def observe(response):
  try:
   body=response.request.post_data_json
   if isinstance(body,dict) and body.get('op')=='invoke':traffic.append(body)
   elif isinstance(body,dict) and body.get('op')=='update':
    for result in response.json().get('results',[]):results[result['requestId']]=result
  except Exception:pass
 page.on('response',observe);page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin+'/') else (external.append(r.request.url),r.abort()));goto_editor(page,url);return page
def idle():expect(page.locator('.brand')).to_be_enabled(timeout=60000)
def completed(endpoint,action,mark):
 for _ in range(3000):
  requests=[r for r in traffic[mark:] if r['endpoint']==endpoint and r.get('input',{}).get('action')==action]
  rows=[results[r['requestId']] for r in requests if r['requestId'] in results]
  good=[r for r in rows if r.get('ok')]
  if good:idle();return good[-1]
  refused=[r for r in rows if r.get('error',{}).get('code')!='stale_revision'];assert not refused,refused
  page.wait_for_timeout(20)
 raise AssertionError((endpoint,action,'actual response not observed',page.get_by_role('status').all_text_contents()))
def pending():page.evaluate('async()=>await confectoryFlushPresentation()');return state()['presentation']['inputs']['blueprint']
def open_row(name,group):
 idle();page.locator('#workspace').click(button='right',position={'x':1240,'y':650});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab="'+group+'"]').click();row=b.locator('[data-object="'+n+name+'"]');expect(row).to_have_attribute('aria-disabled','false');
 if 'view' in sys.argv[3:]:
  row.click(button='right');page.locator('.context-menu').get_by_role('button',name='새 창으로 열기',exact=True).click();expect(page.locator('.window[data-key=editor-1] .object-title-name')).to_have_text('A')
 else:row.press('Enter')
 idle();b.locator('[data-close]').click();return b
def open_slot():
 open_row('A','info');w=page.locator('.window[data-key=editor-1]' if 'view' in sys.argv[3:] else '.window[data-key=schema]');slot=w.locator('[data-module-method="'+root_feature+'"]');expect(slot.locator('[data-function-edit]')).to_be_enabled();slot.locator('[data-function-edit]').click();a=page.locator('.window[data-key=blueprint]');expect(a).to_have_attribute('data-blueprint-owner',n+'A');expect(a).to_have_attribute('data-blueprint-body',n+'Copy/body:common');idle();return a
# Pure receipt tests: the helper verifies source ownership and exact shape, no I/O.
receipt_request={'id':n+'Copy','text':prepared['implementation'],'implementationPath':'Copy.celem','functionText':root_text,'graphId':n+'Copy/body:common','graphPath':'Copy.graph.json','graph':g,'owner':n+'A','ownerText':items['A'][1],'objects':[{'id':n+k,'path':k+'.celem','text':v[1]} for k,v in items.items() if v[0] in ['object','schema']],'requirements':[{'function':root_feature,'signature':{'Args':[{'Type':'long','Name':'amount'}],'return':'long'},'moduleSignature':{'Args':[{'Type':'long','Name':'arg0'}],'return':'long'}}],'providers':[{'function':root_feature,'implementation':n+'Copy','origin':n+'A','contract':{'status':'valid'}}]}
receipt_request.update(project=str(project/'project.cproj'),manifest=sources['project.cproj'])
legacy=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':'blueprintCopyAbiBinding',**receipt_request,'registeredFunction':{'readOnly':True}}),text=True,capture_output=True,env=env,check=True);assert not json.loads(legacy.stdout)['ok']
proof=metadata('blueprintRegisteredCopyAbiBinding',**receipt_request);assert proof['provenance']==provenance and proof['target']=='common';readonly=proof['registeredFunction'];assert readonly['readOnly'] and readonly['bodyReads']==0 and readonly['receipt']['id']==root_feature and readonly['receipt']['textHash']==hashlib.sha256(root_text.encode()).hexdigest()

for boundary in ['target','path','multi-target','provenance','unit-provenance','external-owner','shared-owner','no-requirement','invalid-provider','external-function']:
 r=__import__('copy').deepcopy(receipt_request)
 if boundary=='target':r['graphId']=n+'Copy/body:windows'
 elif boundary=='path':r['graphPath']='Donor.graph.json'
 elif boundary=='multi-target':r['text']=r['text'].replace('blueprint common','body windows "Other.csbody";blueprint common')
 elif boundary=='provenance':r['graph']['copySource']['implementation']=n+'Copy'
 elif boundary=='unit-provenance':r['unitProvenance']={**provenance,'target':'windows'}
 elif boundary=='external-owner':r['owner']='Other.Namespace::A'
 elif boundary=='shared-owner':r['objects'][1]['text']=r['objects'][1]['text'].replace(n+'Other',n+'Copy')
 elif boundary=='no-requirement':r['requirements']=[]
 elif boundary=='invalid-provider':r['providers'][0]['contract']['status']='invalid'
 else:r['text']=r['text'].replace(root_feature,'Unregistered.Pack::Calc')
 result=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':'blueprintRegisteredCopyAbiBinding',**r}),text=True,capture_output=True,env=env,check=True);assert not json.loads(result.stdout)['ok'],boundary
checked('외부 root 선언만 읽는 receipt와 기존 소유/출처/target 위조 10종 거절을 확인하고 JSON으로 legacy 권한을 우회할 수 없다')
def read_copy():return call('blueprint',{'action':'read','id':n+'Copy/body:common','owner':n+'A','ownerHash':hashlib.sha256((project/'A.celem').read_bytes()).hexdigest()})
def batch(data,plan):return {'action':'authorBatch','id':data['id'],'attempt':uuid.uuid4().hex,'checkpointHash':data['checkpointHash'],'sourceProof':json.dumps(sorted([[v['id'],v['revision'],v['hash']] for v in data['sources']])),'edits':[{'action':'rebindCopyAbi','node':'native','definition':plan}],'owner':n+'A','ownerHash':hashlib.sha256((project/'A.celem').read_bytes()).hexdigest()}
try:
 start(0)
 call('saveDraft',{})
 call('select',{'id':n+'A'});call('schema',{'id':n+'A'});(case/'schema.json').write_text(json.dumps(state().get('schema'),ensure_ascii=False))
 with sync_playwright() as p:
  expect.set_options(timeout=30000);browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=setup(browser);author=open_slot();card=author.locator('[data-bp-node=native]');refresh=card.locator('[data-wrapper-refresh]');data=read_copy();row=next(v for v in data['nodes'] if v['id']=='native');(case/'initial-read.json').write_text(json.dumps(data,ensure_ascii=False));assert row['callAbiAvailable'] and row['copyAbiBinding']['provenance']==provenance;expect(refresh).to_be_enabled();unchanged();checked('실제 직접 배치된 저장 복사본에만 기존 원본 계약 갱신 버튼을 연결하고 출처를 표시 데이터에 보존한다')
  # Root access without selected direct owner still cannot edit a copied body.
  root=call('blueprint',{'action':'read','id':n+'Copy/body:common'});assert not next(v for v in root['nodes'] if v['id']=='native')['callAbiAvailable']
  # The original detached information window remains in the floating layer.
  # Move it by its title bar before operating the Blueprint behind it.
  if 'view' in sys.argv[3:]:
   w=page.locator('.window[data-key=editor-1]');title=w.locator('.object-title-name').bounding_box();box=w.bounding_box();assert title and box
   page.mouse.move(title['x']+5,title['y']+5);page.mouse.down();page.mouse.move(1100+title['x']-box['x']+5,800+title['y']-box['y']+5,steps=10);page.mouse.up();idle()
  author.locator(':scope > .window-title .caption').click(position={'x':5,'y':8});author.locator('[data-bp-overview-node=native]').click();refresh.click();held=pending();assert len(held)==1;plan=json.loads(held[0][1]['text']);assert plan['abi']['copyBinding']==row['copyAbiBinding'];unchanged();page.screenshot(path=str(case/'copy-abi-explicit-refresh.png'));checked('명시적 갱신은 복사 소유자·target·출처와 원본 callee hash를 함께 초안에 고정하고 파일은 쓰지 않는다')
  if 'cancel' in sys.argv[3:]:
   author.locator('.bp-viewport').focus();page.keyboard.press('Control+z');assert pending()==[];unchanged();page.keyboard.press('Control+y');assert pending()==held;unchanged();page.keyboard.press('Control+z');assert pending()==[];unchanged();assert next(v for v in read_copy()['nodes'] if v['id']=='native')['signature']['args'][0].get('mode')=='ref';page.close();stop();start(1);page=setup(browser);author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled();assert not pending();assert next(v for v in read_copy()['nodes'] if v['id']=='native')['signature']['args'][0].get('mode')=='ref';unchanged();checked('명시적 갱신 Undo/Redo·취소는 복사 ABI 입력만 취소하고 cold 재시작에서도 원본 계약·소스·다른 객체를 보존한다');assert not errors,errors;browser.close();print(json.dumps({'checks':checks,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
  if 'storage' in sys.argv[3:]:
   checkpoint=next(project.glob('.confectory/edit-workspaces/*/draft.json'));before_bytes=checkpoint.read_bytes();before=read_copy();checkpoint.chmod(0o400);mark=len(traffic);author.locator('[data-bp-save]').click()
   for _ in range(1800):
    attempts=[r for r in traffic[mark:] if r['endpoint']=='blueprint' and r.get('input',{}).get('action')=='authorBatch'];refused=[results[r['requestId']] for r in attempts if r['requestId'] in results and not results[r['requestId']].get('ok') and results[r['requestId']].get('error',{}).get('code')!='stale_revision']
    if refused:break
    page.wait_for_timeout(20)
   assert refused,'missing real storage refusal';idle();assert checkpoint.read_bytes()==before_bytes;assert read_copy()['sources']==before['sources'];retained=dict(pending());assert all(retained.get(k)==v for k,v in held);unchanged();checkpoint.chmod(0o600);page.close();stop();start(1);page=setup(browser);author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled();retained=dict(pending());assert all(retained.get(k)==v for k,v in held);mark=len(traffic);author.locator('[data-bp-save]').click();completed('blueprint','authorBatch',mark);assert pending()==[];assert not next(v for v in read_copy()['nodes'] if v['id']=='native')['postCallStale'];unchanged();checked('실제 checkpoint 쓰기 거절은 복사 선언/import/graph 전체를 미적용하고 입력을 보존하며 cold 재시도는 한 번만 저장한다');assert not errors,errors;browser.close();print(json.dumps({'checks':checks,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
  if 'root-conflict' in sys.argv[3:]:
   checkpoint=next(project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();path=root_pack/'Calc.celem';path.write_text(root_text.replace('{}','{description "외부 소유자의 새 설명";}'));foreign_original[path]=path.read_bytes();mark=len(traffic);author.locator('[data-bp-save]').click()
   for _ in range(1800):
    attempts=[r for r in traffic[mark:] if r['endpoint']=='blueprint' and r.get('input',{}).get('action')=='authorBatch'];refused=[results[r['requestId']] for r in attempts if r['requestId'] in results and not results[r['requestId']].get('ok') and results[r['requestId']].get('error',{}).get('code')!='stale_revision']
    if refused:break
    page.wait_for_timeout(20)
   assert refused and checkpoint.read_bytes()==before;retained=dict(pending());assert all(retained.get(k)==v for k,v in held);unchanged();page.close();stop();start(1);page=setup(browser);expect(page.locator('.window[data-key=blueprint] [data-bp-save]')).to_be_enabled();retained=dict(pending());assert all(retained.get(k)==v for k,v in held);assert checkpoint.read_bytes()==before;unchanged();checked('소유 copy 외부 root 선언이 바뀌면 전체 저장을 거절하고 외부 새 버전·입력·원래 checkpoint를 cold에서도 보존한다');browser.close();print(json.dumps({'checks':checks,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
  if 'conflict' in sys.argv[3:]:
   # Existing peer edit is intentionally kept: no new-baseline automatic retry.
   before=read_copy();call('select',{'id':n+'B'});peer_basis=state()['draft'];call('editDeclaration',{'id':n+'B','revision':peer_basis['revision'],'hash':hashlib.sha256(peer_basis['text'].encode()).hexdigest(),'edit':{'action':'properties','values':{'description':'동료 편집자의 보관 설명'}}});call('saveDraft',{});peer_text=state()['draft']['text'];peer=read_copy();mark=len(traffic);author.locator('[data-bp-save]').click()
   for _ in range(1800):
    attempts=[r for r in traffic[mark:] if r['endpoint']=='blueprint' and r.get('input',{}).get('action')=='authorBatch'];refused=[results[r['requestId']] for r in attempts if r['requestId'] in results and not results[r['requestId']].get('ok') and results[r['requestId']].get('error',{}).get('code')!='stale_revision']
    if refused:break
    page.wait_for_timeout(20)
   assert refused,'missing actual stale checkpoint refusal';idle();retained=dict(pending());assert all(retained.get(k)==v for k,v in held);after=read_copy();assert after['sources']==peer['sources'] and after['checkpointHash']==peer['checkpointHash'];call('select',{'id':n+'B'});assert state()['draft']['text']==peer_text;assert next(v for v in after['nodes'] if v['id']=='native')['signature']['args'][0].get('mode')=='ref';unchanged();page.close();stop();start(1);page=setup(browser);author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled();retained=dict(pending());assert all(retained.get(k)==v for k,v in held);assert read_copy()['checkpointHash']==peer['checkpointHash'];unchanged();checked('실제 peer Save 이후 오래된 복사 ABI 저장은 CAS로 전체 거절하고 두 입력·기존 checkpoint를 cold 복원에서도 보존한다');assert not errors,errors;browser.close();print(json.dumps({'checks':checks,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
  if 'response-loss' in sys.argv[3:]:
   ids=set();lost={}
   def intercept(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('action')=='authorBatch':ids.add(body['requestId'])
    response=route.fetch();payload=response.json()
    if not lost and body.get('op')=='update' and any(v.get('requestId') in ids for v in payload.get('results',[])):
     assert all(v.get('ok') for v in payload['results'] if v.get('requestId') in ids);payload['results']=[{'requestId':v['requestId'],'ok':False,'error':{'code':'transport-interrupted'}} if v.get('requestId') in ids else v for v in payload['results']];lost['changed']=True;route.fulfill(response=response,json=payload);return
    route.fulfill(response=response)
   page.route('**/api/request',intercept);author.locator('[data-bp-save]').click()
   for _ in range(1800):
    if lost:break
    page.wait_for_timeout(20)
   assert lost,'missing real successful reply to lose';idle();page.unroute('**/api/request',intercept);assert pending()==[];saved=read_copy();assert not next(v for v in saved['nodes'] if v['id']=='native')['postCallStale'];checkpoint=saved['checkpointHash'];page.close();stop();start(1);page=setup(browser);author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled();assert not pending();assert read_copy()['checkpointHash']==checkpoint;unchanged();checked('실제 성공 응답을 유실해도 복사 ABI receipt가 완료를 확인하며 cold 복원에 중복·부분 저장이나 재전송 입력을 남기지 않는다');assert not errors,errors;browser.close();print(json.dumps({'checks':checks,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
  # Client cannot downgrade to legacy action or forge copy evidence.
  base=batch(read_copy(),plan)
  for mutation in ['legacy','no-binding','target','donor','no-owner','root-receipt','root-observations','mixed']:
   b=__import__('copy').deepcopy(base);b['attempt']=uuid.uuid4().hex
   if mutation=='legacy':b['edits'][0]['action']='rebindCallAbi'
   elif mutation=='no-binding':del b['edits'][0]['definition']['abi']['copyBinding']
   elif mutation=='target':b['edits'][0]['definition']['abi']['copyBinding']['target']='windows'
   elif mutation=='donor':b['edits'][0]['definition']['abi']['copyBinding']['provenance']['implementation']=n+'Other'
   elif mutation=='no-owner':del b['owner'];del b['ownerHash']
   elif mutation=='root-receipt':b['edits'][0]['definition']['abi']['copyBinding']['registeredFunction']['receipt']['textHash']='0'*64
   elif mutation=='root-observations':b['edits'][0]['definition']['abi']['copyBinding']['registeredFunction']['observations']=[]
   else:b['edits'].append({'action':'intent','node':'native','text':'not silently mixed'})
   call('blueprint',b,False);unchanged();assert pending()==held
  checked('legacy 우회·binding 누락/위조·소유자 누락·외부 root receipt/관측 위조·혼합 요청은 전체 미적용이고 UI 입력과 donor를 보존한다 (8건)')
  if 'view' in sys.argv[3:]:
   route=next(r['input'] for r in reversed(traffic) if r['endpoint']=='blueprint' and r.get('input',{}).get('view')=='1' and r['input'].get('viewBinding'))
   for mutation in ['binding','owner','other-action']:
    b=batch(data,plan);b.update(view='1',viewBinding=route['viewBinding'])
    if mutation=='binding':b['viewBinding']='stale-binding'
    elif mutation=='owner':b['owner']=n+'B'
    else:b['edits'][0]['action']='rebindCallAbi'
    call('blueprint',b,False);unchanged();assert pending()==held
   checked('독립 정보 창은 원래 view binding·owner와 단일 copy ABI만 허용하며 다른 binding/owner/일반 ABI 위조 3종을 입력 손실 없이 거절한다')
  # A rejected compiler review cannot bypass technical contract validation.
  page.close();stop();start(1);page=setup(browser);author=page.locator('.window[data-key=blueprint]');expect(author).to_have_attribute('data-blueprint-owner',n+'A');expect(author.locator('[data-bp-save]')).to_be_enabled();assert pending()==held;unchanged();checked('저장 전 명시적 copy ABI 초안은 cold 재시작에서 소유자·출처·대상과 함께 복원한다')
  mark=len(traffic);author.locator('[data-bp-save]').click();completed('blueprint','authorBatch',mark);assert pending()==[];unchanged();saved=read_copy();node=next(v for v in saved['nodes'] if v['id']=='native');assert node['signature']['args'][0].get('mode') is None and not node['postCallStale'];assert node['copyAbiBinding']==row['copyAbiBinding'];assert saved['slotContext']['copySource']==provenance;checked('한 authorBatch 후보/CAS에서 복사본 typed import·wrapper·graph만 저장하고 출처·객체·donor 파일은 유지한다')
  accepted=next(r['input'] for r in traffic[mark:] if r['endpoint']=='blueprint' and r.get('input',{}).get('action')=='authorBatch' and results.get(r['requestId'],{}).get('ok'));replay=call('blueprint',{**accepted,'action':'settledAuthorBatch'});assert replay['settled'];again=call('blueprint',accepted);assert again['settled'];unchanged();assert not pending();checked('동일 attempt 재조회·재시도는 receipt로 이미 저장한 결과를 확인하며 중복 변경하지 않는다')
  page.close();stop();start(2);page=setup(browser);author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled();assert not pending();saved=read_copy();assert saved['slotContext']['copySource']==provenance;author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000);assert state()['review']['status']=='ready';review.locator('[data-reject]').click();expect(review).to_be_hidden();unchanged();checked('저장된 복사 ABI cold 복원·컴파일 Review와 취소는 원본 파일을 보존한다')
  author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000)
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  mark=len(traffic);review.locator('#confirm').click();result=completed('confirmGroup',None,mark)
  if 'stale-donor' in sys.argv[3:]:
   assert not result['result'].get('sourceConfirmed');unchanged();assert any('CONTRACT_MISMATCH' in v for v in state()['logs']);assert not next(v for v in read_copy()['nodes'] if v['id']=='native')['postCallStale'];checked('다른 donor 자체가 오래된 계약이면 compiler Confirm은 안전하게 거절하고 원본을 자동 수정하거나 복사 저장 초안을 버리지 않는다');assert not errors,errors;browser.close();print(json.dumps({'checks':checks,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
  assert result['result'].get('sourceConfirmed');expect(review).to_have_count(0,timeout=90000);changed={k for k,v in original.items() if (project/k).read_bytes()!=v};assert changed=={'Copy.celem','Copy.graph.json'},changed;assert json.loads((project/'Copy.graph.json').read_text())['copySource']==provenance;checked('명시적 compiler Confirm은 Copy 선언과 graph만 반영하고 donor·callee·부모/다른 객체·원본 node 본문은 byte 보존한다')
  assert not errors and not external,(errors,external);page.close();browser.close()
except Exception:
 try:(case/'failure-state.json').write_text(json.dumps({k:v for k,v in state().items() if k in ['review','sourceError','logs','operationError']},ensure_ascii=False,indent=2))
 except Exception:pass
 (case/'transport.json').write_text(json.dumps({'traffic':traffic,'results':results},ensure_ascii=False,indent=2));(case/'failure.json').write_text(json.dumps({'checks':checks,'errors':errors,'external':external,'evidence':str(case)},ensure_ascii=False,indent=2));print('EVIDENCE '+str(case),flush=True);raise
finally:stop()
record={'checks':checks,'actualEngine':True,'nativeWindows':False,'accountOrInference':False,'projectRun':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
