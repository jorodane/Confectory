"""Actual v536 multiple implementation contexts, C# conversion, no accounts/inference/run."""
import hashlib,json,re,os,pathlib,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-slot-call-abi-'));project=case/'owned project';project.mkdir();n='Owned.Context::'
env=os.environ.copy();env.update(CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'))
def metadata(operation,**data):
 r=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':operation,**data}),text=True,capture_output=True,env=env,check=True);v=json.loads(r.stdout);assert v['ok'],v;return v['result']
items={
 'Main':('function','function '+n+'Main () -> int {provide '+n+'Main with '+n+'MainBody;}'),
 'MainBody':('implementation','implementation '+n+'MainBody for '+n+'Main () -> int {import '+n+'Calc as Chosen (long) -> long in '+n+'A;body common "Main.csbody";}'),
 'Calc':('function','function '+n+'Calc (long amount) -> long {provide '+n+'Calc with '+n+'Caller;}'),
 'Native':('function','function '+n+'Native (ref long amount) -> long {provide '+n+'Native with '+n+'NativeBody;}'),
 'NativeBody':('implementation','implementation '+n+'NativeBody for '+n+'Native (ref long amount) -> long {body common "Native.csbody";}'),
 'Other':('implementation','implementation '+n+'Other for '+n+'Calc (long amount) -> long {body common "Other.csbody";}'),
 'Rules':('module','module '+n+'Rules {require '+n+'Calc (long) -> long;}'),
 'A':('object','object '+n+'A {module '+n+'Rules;provide '+n+'Calc with '+n+'Caller;}'),
 'B':('object','object '+n+'B {module '+n+'Rules;provide '+n+'Calc with '+n+'Other;}')}
prepared=metadata('blueprintPrepareFeature',id=n+'Calc',text='function '+n+'Calc (long amount) -> long {}',implementation=n+'Caller',graphPath='Caller.graph.json',nodePath='Caller.node.json')
defs=metadata('featureBlueprintNodes',featureSource=items['Calc'][1],graph=prepared['graph'])
record={'schema':1,'node':'body','definitionHash':defs['nodes'][0]['definitionHash'],'source':'return amount;'}
prepared=metadata('blueprintPrepareCall',id=n+'Caller',text=prepared['implementation'],targetText=items['Native'][1],graph=prepared['graph'],definition={'id':'native','feature':n+'Native','intent':'기존 호출 계약 갱신','control':'next'})
g=prepared['graph'];g['profile']='sync-acyclic-switch-v1';node=next(v for v in g['nodes'] if v['id']=='native');node['arguments']={'amount':{'input':'amount'}};g['entry']='native';g['edges'].append({'from':'native','port':'next','to':'body'});next(v for v in g['nodes'] if v['id']=='body')['arguments']={'amount':{'node':'native'}}
enum={'primary':'next','members':[{'id':'next','name':'NoBranch','value':0}]}
wrapper=metadata('blueprintCallWrapper',functionText=items['Native'][1],executionEnum=enum,returnMapping='native-return-out-v1',source='return Result.NoBranch;')
node.update(control='switch',executionEnum=enum,postCall={'mode':'execution-enum','returnMapping':'native-return-out-v1','contractHash':wrapper['contractHash'],'source':wrapper['source'],'helpers':''})
items['Caller']=('implementation',prepared['implementation'])
items['Native']=(items['Native'][0],items['Native'][1].replace('(ref long','(long'));items['NativeBody']=(items['NativeBody'][0],items['NativeBody'][1].replace('(ref long','(long'))
sources={'Main.csbody':'return checked((int)calls.Chosen.Invoke(1));','Other.csbody':'return amount+8;','Native.csbody':'return amount+3;','Caller.graph.json':json.dumps(g),'Caller.node.json':json.dumps(record)}
for name,(kind,text) in items.items():sources[name+'.celem']=text
sources['project.cproj']='project Owned.Context version "1" {standalone true;entry '+n+'Main;'+''.join('element '+name+' '+kind+' "'+name+'.celem";' for name,(kind,text) in items.items())+'registry Confectory.Build.DotNet "'+str(repo/'targets/dotnet/pack.cpack')+'";dependency Confectory.Build.DotNet version "0.1.0";target portable Confectory.Build.DotNet::Portable;}'
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
def unchanged():assert all((project/k).read_bytes()==v for k,v in original.items())
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
def open_slot():
 open_row('A','concept');w=page.locator('.window[data-key=schema]');slot=w.locator('[data-module-method="'+n+'Calc"]');expect(slot.locator('[data-function-edit]')).to_be_enabled();slot.locator('[data-function-edit]').click();a=page.locator('.window[data-key=blueprint]');expect(a).to_have_attribute('data-blueprint-owner',n+'A');expect(a).to_have_attribute('data-blueprint-body',n+'Caller/body:common');idle();return a
# Pure finite scope boundary: metadata has no disk writes and never guesses ABI fields.
base_plan={'id':n+'Caller','text':prepared['implementation'],'graph':g,'node':'native','signature':{'args':[{'type':'long','name':'amount'}],'return':'long'},'contractHash':'1'*64}
for target in ['common','windows']:
 plan=__import__('copy').deepcopy(base_plan);plan['text']=plan['text'].replace('blueprint common','blueprint '+target);result=metadata('blueprintCallAbi',**plan);assert result['graph']['edges']==g['edges'] and not result['sourceWritten'] and not result['compiled']
for boundary in ['other-target','other-call','type','name','out','return']:
 plan=__import__('copy').deepcopy(base_plan)
 if boundary=='other-target':plan['text']=plan['text'].replace('blueprint common','body windows "Other.csbody";blueprint common')
 elif boundary=='other-call':extra=__import__('copy').deepcopy(node);extra['id']='other';plan['graph']['nodes'].append(extra)
 elif boundary=='type':plan['signature']['args'][0]['type']='double'
 elif boundary=='name':plan['signature']['args'][0]['name']='renamed'
 elif boundary=='out':plan['signature']['args'][0]['mode']='out'
 else:plan['signature']['return']='bool'
 response=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':'blueprintCallAbi',**plan}),text=True,capture_output=True,env=env,check=True);assert not json.loads(response.stdout)['ok'],boundary
checked('순수 준비의 단일 common/windows 대상은 유지하고 다중 본문·동일 호출 중복·이름/타입/out/반환 변화는 추측 없이 거절한다 (native 실행 검증 아님)')
try:
 start(0)
 with sync_playwright() as p:
  expect.set_options(timeout=30000);browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=setup(browser);author=open_slot();card=author.locator('[data-bp-node=native]');refresh=card.locator('[data-wrapper-refresh]');expect(refresh).to_be_enabled();unchanged();data=call('blueprint',{'action':'read','id':n+'Caller/body:common'});node=next(v for v in data['nodes'] if v['id']=='native');assert node['callAbiAvailable'] and not node['postCallSignatureMatches'];checked('소유 슬롯의 값/ref ABI 변화는 기존 갱신 버튼만 활성화하며 원본은 쓰지 않는다')
  author.locator(':scope > .window-title .caption').click(position={'x':5,'y':8});author.locator('[data-bp-overview-node=native]').click();refresh.click();held=pending();assert len(held)==1 and held[0][1]['type']=='wrapper' and json.loads(held[0][1]['text'])['abi']['signature']['args'][0].get('mode') is None;unchanged();page.screenshot(path=str(case/'explicit-slot-abi.png'));page.close();stop();start(1);page=setup(browser);author=page.locator('.window[data-key=blueprint]');expect(author).to_have_attribute('data-blueprint-owner',n+'A');expect(author.locator('[data-bp-save]')).to_be_enabled();assert pending()==held;unchanged();checked('명시적 갱신 입력은 슬롯 소유자에 묶여 cold 복원되고 원본·다른 객체를 보존한다')
  owner=call('blueprint',{'action':'read','id':n+'Caller/body:common','owner':n+'A','ownerHash':__import__('hashlib').sha256((project/'A.celem').read_bytes()).hexdigest()});plan=json.loads(held[0][1]['text']);batch={'action':'authorBatch','id':owner['id'],'attempt':uuid.uuid4().hex,'checkpointHash':owner['checkpointHash'],'sourceProof':json.dumps(sorted([[v['id'],v['revision'],v['hash']] for v in owner['sources']])),'edits':[{'action':'rebindCallAbi','node':'native','definition':plan}],'owner':n+'B','ownerHash':__import__('hashlib').sha256((project/'B.celem').read_bytes()).hexdigest()};call('blueprint',batch,False);batch['owner']=n+'A';batch['ownerHash']='0'*64;call('blueprint',batch,False);batch['ownerHash']=__import__('hashlib').sha256((project/'A.celem').read_bytes()).hexdigest();batch['edits']=[{'action':'createNode','node':'illegal','definition':{}}];call('blueprint',batch,False);assert pending()==held;unchanged();checked('다른 슬롯·위조 owner hash·슬롯의 비ABI 배치 요청을 서버에서 거절하고 원본과 보관 입력을 유지한다')
  author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=60000);assert not pending();unchanged();data=call('blueprint',{'action':'read','id':n+'Caller/body:common'});node=next(v for v in data['nodes'] if v['id']=='native');assert node['signature']['args'][0].get('mode') is None and not node['postCallStale'];assert next(v for v in data['sources'] if v['id']==n+'Caller');checked('실제 슬롯 Save는 호출 서명과 typed import를 원자적으로 저장하며 원본 파일은 Confirm 전 보존한다')
  page.close();stop();start(2);page=setup(browser);author=page.locator('.window[data-key=blueprint]');expect(author).to_have_attribute('data-blueprint-owner',n+'A');expect(author.locator('[data-bp-save]')).to_be_enabled();assert pending()==[];author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000);assert state()['review']['status']=='ready';review.locator('[data-reject]').click();expect(review).to_be_hidden();unchanged();checked('저장한 슬롯 ABI는 재시작 후 복원되고 Review 취소는 디스크 원본을 보존한다')
  author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000)
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  mark=len(traffic);review.locator('#confirm').click();result=completed('confirmGroup',None,mark);assert result['result'].get('sourceConfirmed');expect(review).to_have_count(0,timeout=90000);changed={name for name,b in original.items() if (project/name).read_bytes()!=b};assert changed=={'Caller.celem','Caller.graph.json'},changed;assert '(long)' in (project/'Caller.celem').read_text();original={name:(project/name).read_bytes() for name in original};checked('명시적 compiler Confirm은 선택한 소유 Caller 선언·graph만 반영하고 원본 callee·모듈·객체·다른 구현을 보존한다')
  # Actual stale source and owner mutation: never execute or log account data.
  old=(project/'Native.celem').read_text();page.close();stop();(project/'Native.celem').write_text(old.replace('(long amount)','(ref long amount)'));f=project/'NativeBody.celem';f.write_text(f.read_text().replace('(long amount)','(ref long amount)'));start(3);page=setup(browser);author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-node=native] [data-wrapper-refresh]')).to_be_enabled();author.locator(':scope > .window-title .caption').click(position={'x':5,'y':8});author.locator('[data-bp-overview-node=native]').click();author.locator('[data-bp-node=native] [data-wrapper-refresh]').click();held=pending();before={name:(project/name).read_bytes() for name in original};call('select',{'id':n+'A'});call('schema',{'id':n+'A'});owner=state()['schema'];call('editDeclaration',{'id':n+'A','revision':owner['revision'],'hash':owner['textHash'],'edit':{'action':'provide-function','function':n+'Calc','implementation':n+'Other'}});author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_contain_text('[slot-source-operation-failed]',timeout=60000);retained=pending();assert all(row in retained for row in held);extra=[v for k,v in retained if not any(k==key for key,value in held)];assert len(extra)==1 and extra[0]['kind']=='author-attempt' and extra[0]['graph']==n+'Caller/body:common' and [[key,{k:v for k,v in value.items() if k!='basis'}] for key,value in extra[0]['cells']]==held;data=call('blueprint',{'action':'read','id':n+'Caller/body:common'});assert next(v for v in data['nodes'] if v['id']=='native')['signature']['args'][0].get('mode') is None;assert all((project/name).read_bytes()==b for name,b in before.items());checked('슬롯 연결이 다른 구현으로 바뀌면 오래된 ABI Save를 차단하고 입력·기존 저장본·다른 소스를 보존한다')
  assert not errors and not external,(errors,external);page.close();browser.close()
except Exception:
 (case/'failure.json').write_text(json.dumps({'checks':checks,'errors':errors,'external':external,'evidence':str(case)},ensure_ascii=False,indent=2));print('EVIDENCE '+str(case),flush=True);raise
finally:stop()
record={'checks':checks,'actualEngine':True,'nativeWindows':False,'accountOrInference':False,'projectRun':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
