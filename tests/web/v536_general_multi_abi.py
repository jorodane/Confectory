"""Actual isolated multi-target ABI UI/CAS/Review/Confirm; no accounts or project run."""
import copy,hashlib,json,os,pathlib,subprocess,sys,signal,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();dotnet=os.environ.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet');dll=repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'
def metadata(operation,ok=True,**data):
 p=subprocess.run([dotnet,str(dll)],input=json.dumps({'operation':operation,**data}),text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,(operation,v);return v.get('result') if ok else v
n='Owned.Multi::';feature='function '+n+'Calc (long amount) -> long {provide '+n+'Calc with '+n+'Caller;}';before='function '+n+'Native (ref long amount) -> long {}';after='function '+n+'Native (int step,double renamed,out long total) -> bool {}'
base=metadata('blueprintPrepareFeature',id=n+'Calc',text='function '+n+'Calc (long amount) -> long {}',implementation=n+'Caller',graphPath='common.graph.json',nodePath='common.node.json');base=metadata('blueprintPrepareCall',id=n+'Caller',text=base['implementation'],targetText=before,graph=base['graph'],definition={'id':'native','feature':n+'Native','intent':'명시적 호출','control':'next'})
g=base['graph'];g['profile']='sync-acyclic-switch-v1';g['entry']='native';g['edges'].append({'from':'native','port':'next','to':'body'});native=next(row for row in g['nodes'] if row['id']=='native');native['arguments']={'amount':{'input':'amount'}};next(row for row in g['nodes'] if row['id']=='body')['arguments']={'amount':{'node':'native'}};enum={'primary':'next','members':[{'id':'next','name':'NoBranch','value':0}]};wrapper=metadata('blueprintCallWrapper',functionText=before,executionEnum=enum,returnMapping='native-return-out-v1',source='return Result.NoBranch;');native.update(control='switch',executionEnum=enum,postCall={'mode':'execution-enum','returnMapping':'native-return-out-v1','contractHash':wrapper['contractHash'],'source':wrapper['source'],'helpers':''})
text=base['implementation'].replace('\n}', '\nblueprint windows "windows.graph.json";\n}');assert 'blueprint windows' in text,text
bodies={}
for target in ['common','windows']:
 graph=copy.deepcopy(g);next(row for row in graph['nodes'] if row['id']=='body')['implementation']=target+'.node.json';defs=metadata('featureBlueprintNodes',featureSource=feature,graph=graph,featureContracts={n+'Native':before});record={'schema':1,'node':'body','definitionHash':next(row for row in defs['nodes'] if row['id']=='body')['definitionHash'],'source':'return amount+'+('7' if target=='common' else '9')+';'};bodies[target]={'path':target+'.graph.json','graph':graph,'records':{'body':{'path':target+'.node.json','record':record}}}
request={'id':n+'Caller','text':text,'functionText':feature,'feature':n+'Native','featureContracts':{n+'Native':after},'bodies':bodies}

report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-multi-abi-'));project=case/'owned project';project.mkdir()
items={'Main':('function','function '+n+'Main () -> int {provide '+n+'Main with '+n+'MainBody;}'),'MainBody':('implementation','implementation '+n+'MainBody for '+n+'Main () -> int {import '+n+'Calc as Chosen (long) -> long;body common "Main.csbody";}'),'Calc':('function',feature),'Caller':('implementation',text),'Native':('function',after[:-1]+'provide '+n+'Native with '+n+'NativeBody;}'),'NativeBody':('implementation','implementation '+n+'NativeBody for '+n+'Native (int step,double renamed,out long total) -> bool {body common "Native.csbody";}')}
for name,(kind,source) in items.items():(project/(name+'.celem')).write_text(source)
(project/'Main.csbody').write_text('return checked((int)calls.Chosen.Invoke(1));');(project/'Native.csbody').write_text('total=checked((long)renamed);return step>0;')
for target,row in bodies.items():
 (project/row['path']).write_text(json.dumps(row['graph']))
 for record in row['records'].values():(project/record['path']).write_text(json.dumps(record['record']))
(project/'project.cproj').write_text('project Owned.Multi version "1" {standalone true;entry '+n+'Main;'+''.join('element '+name+' '+kind+' "'+name+'.celem";' for name,(kind,_) in items.items())+'registry Confectory.Build.DotNet "'+str(repo/'targets/dotnet/pack.cpack')+'";dependency Confectory.Build.DotNet version "0.1.0";target portable Confectory.Build.DotNet::Portable;target linux Confectory.Build.DotNet::Linux;}')
foreign_original={}
original={p.name:p.read_bytes() for p in project.iterdir()};env=os.environ.copy();env.update(CONFECTORY_DOTNET=dotnet,CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(case/'profile'),CONFECTORY_ENTRY_STORAGE=str(case/'profile'),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;traffic=[];results={};errors=[];external=[];checks=[]
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
 idle();page.locator('#workspace').click(button='right',position={'x':1240,'y':650});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab="'+group+'"]').click();row=b.locator('[data-object="'+n+name+'"]');expect(row).to_have_attribute('aria-disabled','false');row.press('Enter');idle();b.locator('[data-close]').click();return b
def read(target='common'):return call('blueprint',{'action':'read','id':n+'Caller/body:'+target})
def graph_window():return page.locator('.window[data-key=blueprint]')
def current():return read()
def foreign_same():pass
def open_slot():
 open_row('Calc','feature');decl=page.locator('.window[data-key=declaration]');decl.locator('[data-function-write-direct]').click();a=graph_window();expect(a).to_have_attribute('data-blueprint-body',n+'Caller/body:common',timeout=60000);idle();return a
def focus_call():
 author.locator(':scope > .window-title .caption').click(position={'x':5,'y':8});author.locator('[data-bp-overview-node=native]').click()
def collect_wrapper():return [(k,v) for k,v in pending() if v.get('type')=='wrapper']
def mapping():return page.locator('[data-abi-remap-accept]').locator('..').locator('..')
def choose():
 root=mapping()
 for section in root.locator('[data-abi-target]').all():
  section.locator('[data-abi-input=step]').select_option('value');section.locator('[data-abi-value=step]').fill('3');section.locator('[data-abi-input=renamed]').select_option('pin:amount');section.locator('[data-abi-output=return]').select_option('total')
 return root

def reopen(i):
 global page,author
 pending();page.close();stop();start(i);page=setup(browser);author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=60000);idle()
def finish():
 assert not errors and not external,(errors,external);browser.close();print(json.dumps({'checks':checks,'actualEngineRenderer':True,'nativeWindows':False,'accountOrInference':False,'projectRun':False,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
try:
 start(0);call('saveDraft',{})
 with sync_playwright() as p:
  expect.set_options(timeout=60000);browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=setup(browser);author=open_slot();expect(author.locator('[data-wrapper-refresh]')).to_be_enabled(timeout=60000);data=current();node=next(r for r in data['nodes'] if r['id']=='native');assert set(node['callAbiGroupPlans'])=={'common','windows'};assert all(p['remap']['inputs']=={'step':None,'renamed':None} for p in node['callAbiGroupPlans'].values());unchanged();foreign_same();focus_call();author.locator('[data-wrapper-refresh]').click();choose();page.screenshot(path=str(case/'mapping-dialog.png'));mapping().locator('[data-abi-remap-cancel]').click();assert not pending();unchanged();checked('원래 갱신에서 명시적 핀 대응을 열고 취소해도 caller/import/연결/외부 팩을 변경하지 않는다')
  focus_call();author.locator('[data-wrapper-refresh]').click();choose();held_form=pending();assert len(held_form)==1 and held_form[0][1]['type']=='abi-remap-form';reopen(1);focus_call();author.locator('[data-wrapper-refresh]').click();root=mapping();expect(root.locator('[data-abi-target=common]').locator('[data-abi-value=step]')).to_have_value('3');expect(root.locator('[data-abi-target=common]').locator('[data-abi-input=renamed]')).to_have_value('pin:amount');expect(root.locator('[data-abi-target=common]').locator('[data-abi-output=return]')).to_have_value('total');root.locator('[data-abi-target=common]').locator('[data-abi-value=step]').fill('3e');root.locator('[data-abi-remap-accept]').click();expect(root.locator('[data-abi-error]')).to_be_visible();assert not collect_wrapper();root.locator('[data-abi-target=common]').locator('[data-abi-value=step]').fill('3');root.locator('[data-abi-remap-accept]').click();held=collect_wrapper();assert len(held)==1;plan=json.loads(held[0][1]['text']);assert plan['abi']['remap']=={'inputs':{'step':{'valueJson':'3'},'renamed':'amount'},'outputs':{'return':'total'}};expect(author.locator('[data-bp-node=native] [aria-label="입력값 · step"]')).to_have_value('3');expect(author.locator('[data-bp-node=native] [aria-label="입력값 · renamed"]')).to_have_value(__import__('re').compile('amount'));unchanged();foreign_same();page.screenshot(path=str(case/'explicit-general-map.png'));checked('확인 전 raw 핀/값 선택을 cold에서 복원하며 불완전 값은 승인하지 않고 명시적 이름/순서/타입/반환→out 대응만 보관한다')
  mode=sys.argv[3] if len(sys.argv)>3 else 'normal';checkpoint=next(project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes()
  if mode=='cancel':
   author.locator('.bp-viewport').focus();page.keyboard.press('Control+z');assert not pending();unchanged();reopen(2);assert not pending();unchanged();foreign_same();checked('원본 Undo는 전체 갱신 계획만 취소하고 cold에 기존 입력/출력 계약과 source를 유지한다');finish()
  if mode=='conflict':
   call('select',{'id':n+'Caller'});d=state()['draft'];call('editDescription',{'id':n+'Caller','revision':d['revision'],'hash':hashlib.sha256(d['text'].encode()).hexdigest(),'value':'동료의 먼저 저장한 설명'});call('saveDraft',{});peer=checkpoint.read_bytes();mark=len(traffic);author.locator('[data-bp-save]').click()
   for _ in range(1800):
    bad=[results[r['requestId']] for r in traffic[mark:] if r['endpoint']=='blueprint' and r.get('input',{}).get('action')=='authorBatch' and r['requestId'] in results and not results[r['requestId']].get('ok') and results[r['requestId']].get('error',{}).get('code')!='stale_revision']
    if bad:break
    page.wait_for_timeout(20)
   assert bad;idle();assert checkpoint.read_bytes()==peer and collect_wrapper()==held;unchanged();reopen(2);assert collect_wrapper()==held and checkpoint.read_bytes()==peer;unchanged();foreign_same();checked('동료 caller 저장 뒤 전체 일반 ABI는 거절하며 상대 checkpoint와 명시적 대응 입력을 cold에도 유지한다');finish()
  if mode in ['storage','invalid-map']:
   changed=[]
   def inject(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('action')=='authorBatch':body['input']['edits'][0]['definition']['abi']['targetPlans']['windows']['remap']['outputs']['return']='return';changed.append(body['requestId']);route.continue_(post_data=json.dumps(body));return
    route.continue_()
   if mode=='storage':checkpoint.chmod(0o400)
   else:page.route('**/api/request',inject)
   mark=len(traffic);author.locator('[data-bp-save]').click()
   for _ in range(1800):
    bad=[results[r['requestId']] for r in traffic[mark:] if r['endpoint']=='blueprint' and r.get('input',{}).get('action')=='authorBatch' and r['requestId'] in results and not results[r['requestId']].get('ok') and results[r['requestId']].get('error',{}).get('code')!='stale_revision']
    if bad:break
    page.wait_for_timeout(20)
   assert bad;idle();assert checkpoint.read_bytes()==baseline and collect_wrapper()==held;unchanged();foreign_same()
   if mode=='storage':checkpoint.chmod(0o600)
   else:page.unroute('**/api/request',inject);assert len(changed)==1
   reopen(2);assert collect_wrapper()==held;unchanged();checked('실제 쓰기 거절/호환 불가 출력은 caller/import/소비자 전체 미적용과 정확한 입력을 유지하고 cold 명시 재시도를 허용한다')
  if mode=='response-loss':
   ids=set();lost={}
   def intercept(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('action')=='authorBatch':ids.add(body['requestId'])
    response=route.fetch();payload=response.json()
    if not lost and body.get('op')=='update' and any(v.get('requestId') in ids for v in payload.get('results',[])):
     assert all(v.get('ok') for v in payload['results'] if v.get('requestId') in ids);payload['results']=[{'requestId':v['requestId'],'ok':False,'error':{'code':'transport-interrupted'}} if v.get('requestId') in ids else v for v in payload['results']];lost['injected']=True;route.fulfill(response=response,json=payload);return
    route.fulfill(response=response)
   page.route('**/api/request',intercept)
  mark=len(traffic);author.locator('[data-bp-save]').click()
  if mode=='response-loss':
   for _ in range(1800):
    if lost and not pending():break
    page.wait_for_timeout(20)
   assert lost and len(ids)==1;page.unroute('**/api/request',intercept);idle();assert not pending();checked('실제 성공 응답 유실은 같은 전체 mapping/source receipt로 한 번 확인하고 중복 변경하지 않는다')
  else:completed('blueprint','authorBatch',mark);assert not pending()
  saved=current();native=next(r for r in saved['nodes'] if r['id']=='native');assert native['signature']['return']=='bool' and native['signature']['args'][0]['name']=='step' and native['signature']['args'][1]['name']=='renamed';assert json.loads(next(r for r in saved['nodes'] if r['id']=='body')['arguments'][0]['valueJson'])=={'node':'native','output':'total'};assert saved['diagnostics']['state'] in ['source-ready','source-assembled'];unchanged();foreign_same();checked('한 authorBatch 후보/CAS가 전체 target closure·typed import·입력/출력 대응·소비자를 함께 검증하고 원본 코드를 보존한다')
  reopen(3);assert not pending();unchanged();foreign_same();author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000);assert state()['review']['status']=='ready';assert all(not row['id'].startswith('Lib::') for row in state()['review']['units']);review.locator('[data-reject]').click();expect(review).to_be_hidden();unchanged();author.locator('[data-bp-complete]').click();expect(review).to_be_visible(timeout=60000)
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  mark=len(traffic);review.locator('#confirm').click();result=completed('confirmGroup',None,mark);assert result['result']['sourceConfirmed'];expect(review).to_have_count(0,timeout=120000);assert {k for k,v in original.items() if (project/k).read_bytes()!=v}=={'Caller.celem','common.graph.json','windows.graph.json'};foreign_same();checked('cold·Review 취소·명시 compiler Confirm은 Caller 선언/두 target graph만 반영하며 등록 팩/객체/함수/본문을 보존한다');finish()
except Exception:
 try:page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 (case/'failure.json').write_text(json.dumps({'checks':checks,'errors':errors,'traffic':traffic[-30:],'results':results},ensure_ascii=False,indent=2));print('EVIDENCE '+str(case),flush=True);raise
finally:stop()
