"""Actual isolated multi-target ABI UI/CAS/Review/Confirm; no accounts or project run."""
import copy,hashlib,json,os,pathlib,subprocess,sys,signal,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();dotnet=os.environ.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet');dll=repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'
def metadata(operation,ok=True,**data):
 p=subprocess.run([dotnet,str(dll)],input=json.dumps({'operation':operation,**data}),text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,(operation,v);return v.get('result') if ok else v
n='Owned.Multi::';feature='function '+n+'Calc (long amount) -> long {provide '+n+'Calc with '+n+'Caller;}';before='function '+n+'Native (ref long amount) -> long {}';after=before.replace('(ref long','(long')
base=metadata('blueprintPrepareFeature',id=n+'Calc',text='function '+n+'Calc (long amount) -> long {}',implementation=n+'Caller',graphPath='common.graph.json',nodePath='common.node.json');base=metadata('blueprintPrepareCall',id=n+'Caller',text=base['implementation'],targetText=before,graph=base['graph'],definition={'id':'native','feature':n+'Native','intent':'명시적 호출','control':'next'})
g=base['graph'];g['profile']='sync-acyclic-switch-v1';g['entry']='native';g['edges'].append({'from':'native','port':'next','to':'body'});native=next(row for row in g['nodes'] if row['id']=='native');native['arguments']={'amount':{'input':'amount'}};next(row for row in g['nodes'] if row['id']=='body')['arguments']={'amount':{'node':'native'}};enum={'primary':'next','members':[{'id':'next','name':'NoBranch','value':0}]};wrapper=metadata('blueprintCallWrapper',functionText=before,executionEnum=enum,returnMapping='native-return-out-v1',source='return Result.NoBranch;');native.update(control='switch',executionEnum=enum,postCall={'mode':'execution-enum','returnMapping':'native-return-out-v1','contractHash':wrapper['contractHash'],'source':wrapper['source'],'helpers':''})
text=base['implementation'].replace('\n}', '\nblueprint windows "windows.graph.json";\n}');assert 'blueprint windows' in text,text
bodies={}
for target in ['common','windows']:
 graph=copy.deepcopy(g);next(row for row in graph['nodes'] if row['id']=='body')['implementation']=target+'.node.json';defs=metadata('featureBlueprintNodes',featureSource=feature,graph=graph,featureContracts={n+'Native':before});record={'schema':1,'node':'body','definitionHash':next(row for row in defs['nodes'] if row['id']=='body')['definitionHash'],'source':'return amount+'+('7' if target=='common' else '9')+';'};bodies[target]={'path':target+'.graph.json','graph':graph,'records':{'body':{'path':target+'.node.json','record':record}}}
request={'id':n+'Caller','text':text,'functionText':feature,'feature':n+'Native','featureContracts':{n+'Native':after},'bodies':bodies}

report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-multi-abi-'));project=case/'owned project';project.mkdir()
items={'Main':('function','function '+n+'Main () -> int {provide '+n+'Main with '+n+'MainBody;}'),'MainBody':('implementation','implementation '+n+'MainBody for '+n+'Main () -> int {import '+n+'Calc as Chosen (long) -> long;body common "Main.csbody";}'),'Calc':('function',feature),'Caller':('implementation',text),'Native':('function',after[:-1]+'provide '+n+'Native with '+n+'NativeBody;}'),'NativeBody':('implementation','implementation '+n+'NativeBody for '+n+'Native (long amount) -> long {body common "Native.csbody";}')}
for name,(kind,source) in items.items():(project/(name+'.celem')).write_text(source)
(project/'Main.csbody').write_text('return checked((int)calls.Chosen.Invoke(1));');(project/'Native.csbody').write_text('return amount+3;')
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
def refresh():
 a=graph_window();a.locator(':scope > .window-title .caption').click(position={'x':5,'y':8});a.locator('[data-bp-overview-node=native]').click();a.locator('[data-bp-node=native] [data-wrapper-refresh]').click();expect(page.locator('[data-abi-group-accept]')).to_be_visible(timeout=30000)
def accept_review(review):
 if review.locator('[data-review-advanced]').count():
  review.locator('[data-review-advanced]').click()
  if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
 review.locator('#confirm').click();expect(review).to_have_count(0,timeout=120000);idle()
try:
 start(0);call('saveDraft',{})
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=setup(browser);open_row('Calc','feature');decl=page.locator('.window[data-key=declaration]');decl.locator('[data-function-write-direct]').click();a=graph_window();expect(a).to_have_attribute('data-blueprint-body',n+'Caller/body:common',timeout=60000);expect(a.locator('[data-wrapper-refresh]')).to_be_enabled(timeout=60000);before_data=read();node=next(v for v in before_data['nodes'] if v['id']=='native');assert node['callAbiAvailable'] and set(node['callAbiGroupPlans'])=={'common','windows'};assert {s['id'] for s in before_data['sources']} >= {n+'Caller/body:windows',n+'Caller/body:windows/node:body',n+'Native'};unchanged();checked('실제 엔진 read는 두 target·모든 record·공유 callee를 관측하고 기존 갱신 버튼을 연결한다')
  refresh();expect(page.get_by_text('common · windows',exact=True)).to_be_visible();page.locator('[data-abi-group-cancel]').click();assert not pending();unchanged();refresh();page.locator('[data-abi-group-accept]').click();held=pending();assert len(held)==1;plan=json.loads(held[0][1]['text']);assert set(plan['abi']['targetPlans'])=={'common','windows'} and plan['abi']['targetGroup']==node['callAbiGroupBinding'];unchanged();page.screenshot(path=str(case/'explicit-all-targets.png'));checked('원본 modal에서 전체 target을 명시적으로 취소/수락하며 두 wrapper 계획만 초안에 결부한다')
  mode=sys.argv[3] if len(sys.argv)>3 else 'normal'
  if mode=='cancel':
   a.locator('.bp-viewport').focus();page.keyboard.press('Control+z');assert not pending();assert all(next(v for v in read(t)['nodes'] if v['id']=='native')['signature']['args'][0].get('mode')=='ref' for t in ['common','windows']);unchanged();page.close();stop();start(1);page=setup(browser);a=graph_window();expect(a.locator('[data-bp-save]')).to_be_enabled(timeout=60000);assert not pending();unchanged();checked('원본 Undo는 전체 target 갱신 계획만 취소하며 cold에도 원래 호출/연결과 모든 source를 보존한다');browser.close();sys.exit(0)
  if mode=='invalid':
   changed=[]
   def bad_target(route):
    q=route.request.post_data_json
    if q.get('op')=='invoke' and q.get('endpoint')=='blueprint' and q.get('input',{}).get('action')=='authorBatch':q['input']['edits'][0]['definition']['abi']['targetPlans']['windows']['contractHash']='0'*64;changed.append(q['requestId']);route.continue_(post_data=json.dumps(q));return
    route.continue_()
   page.route('**/api/request',bad_target);mark=len(traffic);a.locator('[data-bp-save]').click()
   for _ in range(1800):
    if changed and any(results.get(r,{}).get('ok') is False for r in changed):break
    page.wait_for_timeout(20)
   assert len(changed)==1 and not results[changed[0]]['ok'];idle();page.unroute('**/api/request',bad_target);assert dict(pending()).get(held[0][0])==held[0][1];assert all(next(v for v in read(t)['nodes'] if v['id']=='native')['signature']['args'][0].get('mode')=='ref' for t in ['common','windows']);unchanged();checked('실제 second target 계약 위조는 첫 target/import까지 전체 미적용하고 정상 입력을 cold 재시도할 수 있게 보존한다')
  if mode=='conflict':
   call('select',{'id':n+'Caller'});d=state()['draft'];call('editDescription',{'id':n+'Caller','revision':d['revision'],'hash':hashlib.sha256(d['text'].encode()).hexdigest(),'value':'먼저 저장한 동료 설명'});call('saveDraft',{});checkpoint=next(project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();a.locator('[data-bp-save]').click();expect(a.locator('.bp-status')).to_contain_text('공유 호출 저장을 마치지 못했어요',timeout=30000);assert dict(pending()).get(held[0][0])==held[0][1];assert checkpoint.read_bytes()==before;assert all(next(v for v in read(target)['nodes'] if v['id']=='native')['signature']['args'][0].get('mode')=='ref' for target in ['common','windows']);unchanged();page.close();stop();start(1);page=setup(browser);a=graph_window();expect(a.locator('[data-bp-save]')).to_be_enabled(timeout=60000);assert dict(pending()).get(held[0][0])==held[0][1];assert checkpoint.read_bytes()==before;unchanged();checked('동료 implementation 저장 뒤 오래된 전체 target 계획은 모두 거절하고 입력·동료 checkpoint·양쪽 원래 ABI를 cold에서도 보존한다');browser.close();sys.exit(0)
  if mode=='storage':
   checkpoint=next(project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();checkpoint.chmod(0o400);mark=len(traffic);a.locator('[data-bp-save]').click()
   for _ in range(1800):
    r=[results[v['requestId']] for v in traffic[mark:] if v['endpoint']=='blueprint' and v.get('input',{}).get('action')=='authorBatch' and v['requestId'] in results and not results[v['requestId']].get('ok') and results[v['requestId']].get('error',{}).get('code')!='stale_revision']
    if r:break
    page.wait_for_timeout(20)
   assert r,'actual storage refusal missing';idle();assert checkpoint.read_bytes()==before;assert dict(pending()).get(held[0][0])==held[0][1];assert all(next(v for v in read(t)['nodes'] if v['id']=='native')['signature']['args'][0].get('mode')=='ref' for t in ['common','windows']);unchanged();checkpoint.chmod(0o600);checked('실제 checkpoint 쓰기 거절은 두 graph·공유 import 모두 미적용하고 입력/이전 checkpoint를 보존한다')
  page.close();stop();start(1);page=setup(browser);a=graph_window();expect(a.locator('[data-bp-save]')).to_be_enabled(timeout=60000);assert dict(pending()).get(held[0][0])==held[0][1];unchanged();checked('미적용 전체 target 계획은 실제 재시작에서 target 선택과 wrapper 입력을 보존한다')
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
  mark=len(traffic);a.locator(':scope > .window-title .caption').click(position={'x':5,'y':8});a.locator('[data-bp-save]').click()
  if mode=='response-loss':
   for _ in range(1800):
    if lost and not pending():break
    page.wait_for_timeout(20)
   assert lost and len(ids)==1;page.unroute('**/api/request',intercept);idle();assert not pending();checked('실제 성공 응답 유실은 같은 plan receipt로 두 target 전체의 완료를 한 번 확인한다')
  else:completed('blueprint','authorBatch',mark);assert not pending()
  unchanged()
  for target in ['common','windows']:
   data=read(target);assert next(v for v in data['nodes'] if v['id']=='native')['signature']['args'][0].get('mode') is None;assert data['diagnostics']['state'] in ['source-ready','source-assembled'];assert len(data['reviewIds'])==7
  checked('한 실제 authorBatch/CAS는 두 graph·typed import·wrapper를 함께 저장하고 전체 7개 검토 그룹을 결부한다')
  page.close();stop();start(2);page=setup(browser);a=graph_window();expect(a.locator('[data-bp-save]')).to_be_enabled(timeout=60000);assert not pending();assert all(next(v for v in read(target)['nodes'] if v['id']=='native')['signature']['args'][0].get('mode') is None for target in ['common','windows']);unchanged();a.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000);assert {v['id'] for v in state()['review']['units']} <= set(data['reviewIds']);review.locator('[data-reject]').click();expect(review).to_be_hidden();unchanged();a.locator('[data-bp-complete]').click();expect(review).to_be_visible(timeout=60000);accept_review(review);assert '확정 후 다른 원본' not in a.locator('.bp-status').inner_text();changed={k for k,v in original.items() if (project/k).read_bytes()!=v};assert changed=={'Caller.celem','common.graph.json','windows.graph.json'},changed;checked('저장 그룹의 cold 복원·Review 취소·명시 compiler Confirm은 공유 import/두 graph만 반영하고 함수·본문·다른 소스를 보존한다');assert not errors and not external,(errors,external);browser.close()
except Exception:
 evidence={'checks':checks,'traffic':traffic[-25:],'results':results,'errors':errors}
 try:evidence['state']=state()
 except Exception:pass
 try:evidence['status']=page.locator('.bp-status').all_text_contents();page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 (case/'failure.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2));print('EVIDENCE '+str(case),flush=True);raise
finally:stop()
print(json.dumps({'checks':checks,'actualEngine':True,'renderer':True,'windowsExecuted':False,'actualAccountOrInference':False,'evidence':str(case)},ensure_ascii=False,indent=2))
