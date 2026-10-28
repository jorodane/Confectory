"""v536 Set desktop/mobile UI, private input restoration and atomic compiler boundary; isolated project."""
import hashlib,json,os,pathlib,signal,subprocess,sys,tempfile,time,urllib.request,uuid,copy
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-set-plan-'));project=case/'owned project';project.mkdir();n='Owned.Set::';env=os.environ.copy()
items={'Main':('function','function '+n+'Main () -> int {provide '+n+'Main with '+n+'MainBody;}'),'MainBody':('implementation','implementation '+n+'MainBody for '+n+'Main () -> int {import '+n+'Calc as Calc (long) -> long;body common "Main.csbody";}'),'Calc':('function','function '+n+'Calc (long amount) -> long {provide '+n+'Calc with '+n+'CalcBody;}'),'CalcBody':('implementation','implementation '+n+'CalcBody for '+n+'Calc (long amount) -> long {blueprint common "Calc.graph.json";}')}
g={'schema':1,'profile':'sync-acyclic-locals-v1','feature':n+'Calc','contractHash':hashlib.sha256(json.dumps({'feature':n+'Calc','signature':{'args':[{'type':'long','name':'amount'}],'return':'long'}},separators=(',',':')).encode()).hexdigest(),'entry':'finish','locals':[{'id':'counter','name':'현재 값','type':'long','initial':{'constant':0}}],'nodes':[{'id':'finish','kind':'export','control':'next','intent':'결과 내보내기','output':'return','signature':{'args':[{'name':'value','type':'long'}],'return':'void'},'arguments':{'value':{'constant':0}}}],'edges':[],'exits':{}}
# Ask the pure compiler metadata to provide its canonical feature contract hash.
q=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':'blueprintPrepareFeature','id':n+'Calc','text':'function '+n+'Calc (long amount) -> long {}','implementation':n+'Unused','graphPath':'unused.graph.json','nodePath':'unused.node.json'}),text=True,capture_output=True,check=True);v=json.loads(q.stdout);assert v['ok'],v;g['contractHash']=v['result']['graph']['contractHash']
if 'copy-boundary' in sys.argv[3:] or 'readonly' in sys.argv[3:]:g['copySource']={'implementation':n+'Origin','target':'common','bodyOrigin':n+'Origin','sourceKind':'blueprint'}
g['profile']='sync-acyclic-alias-locals-v1';g['locals'].append({'id':'readonlyAlias','name':'읽기 전용 입력 별칭','type':'long','source':{'input':'amount'}})
g['locals'] += [{'id':'firstValue','name':'첫 저장값','type':'long','initial':{'constant':0}},{'id':'secondValue','name':'다음 저장값','type':'long','initial':{'constant':0}}]
g['nodes'][:0]=[{'id':i,'kind':'set','control':'next','intent':'중간저장','local':'counter','outputLocal':out,'signature':{'args':[{'name':'value','type':'long'}],'return':'void'},'arguments':{'value':{'constant':v}}} for i,out,v in [('first','firstValue',1),('second','secondValue',9)]]
g['entry']='first';g['edges']=[{'from':'first','port':'next','to':'second'},{'from':'second','port':'next','to':'finish'}];g['nodes'][-1]['arguments']['value']={'node':'first','output':'stored'}
if 'legacy' in sys.argv[3:]:
 g['nodes'][0].pop('outputLocal');g['nodes'][-1]['arguments']['value']={'constant':1}
sources={'Calc.graph.json':json.dumps(g,ensure_ascii=False),'Main.csbody':'return checked((int)calls.Calc.Invoke(4));'}
for name,(kind,text) in items.items():sources[name+'.celem']=text
sources['project.cproj']='project Owned.Set version "1" {standalone true;entry '+n+'Main;'+''.join('element '+name+' '+kind+' "'+name+'.celem";' for name,(kind,text) in items.items())+'registry Confectory.Build.DotNet "'+str(repo/'targets/dotnet/pack.cpack')+'";dependency Confectory.Build.DotNet version "0.1.0";target portable Confectory.Build.DotNet::Portable;}'
for name,text in sources.items():(project/name).write_bytes(text.encode())
original={p.name:p.read_bytes() for p in project.iterdir()};env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(case/'profile'),CONFECTORY_ENTRY_STORAGE=str(case/'profile'),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;checks=[]
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
def current():return call('blueprint',{'action':'read','id':n+'CalcBody/body:common'})
def request(data,plan):return {'id':data['id'],'attempt':uuid.uuid4().hex,'sourceProof':json.dumps(sorted([[v['id'],v['revision'],v['hash']] for v in data['sources']]),separators=(',',':')),'checkpointHash':data['checkpointHash'],'edits':[{'action':'setPlan','node':'$sets','definition':plan}]}

from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
errors=[];traffic=[];results={}
def setup(browser):
 page=browser.new_page(viewport={'width':1480,'height':1050});page.on('pageerror',lambda e:errors.append(str(e)))
 def observe(response):
  try:
   body=response.request.post_data_json
   if isinstance(body,dict) and body.get('op')=='invoke':traffic.append(body)
   elif isinstance(body,dict) and body.get('op')=='update':
    for result in response.json().get('results',[]):results[result['requestId']]=result
  except Exception:pass
 page.on('response',observe);page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin+'/') else r.abort());goto_editor(page,url);return page
def idle():expect(page.locator('.brand')).to_be_enabled(timeout=60000)
def pending():page.evaluate('async()=>await confectoryFlushPresentation()');return state()['presentation']['inputs']['blueprint']
def author():return page.locator('.window[data-key=blueprint]')
def open_author():
 idle();page.locator('#workspace').click(button='right',position={'x':1240,'y':650});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab="feature"]').click();row=b.locator('[data-object="'+n+'Calc"]');expect(row).to_have_attribute('aria-disabled','false');row.press('Enter');idle();b.locator('[data-close]').click();page.locator('.window[data-key=declaration] [data-function-write-direct]').click();expect(author().locator('[data-bp-save]')).to_be_enabled();idle()
def value(id,text):
 author().locator('[data-bp-node="'+id+'"] .bp-pin-plug[data-side=in] input').click();menu=page.get_by_role('dialog',name='핀 값 선택',exact=True);menu.get_by_role('searchbox',name='값 검색').fill(text);menu.get_by_role('searchbox',name='값 검색').press('Enter');expect(menu).not_to_be_visible()
def saved(mark):
 for _ in range(3000):
  requests=[r for r in traffic[mark:] if r['endpoint']=='blueprint' and r.get('input',{}).get('action')=='authorBatch'];rows=[results[r['requestId']] for r in requests if r['requestId'] in results]
  if any(r.get('ok') for r in rows):idle();return requests
  refused=[r for r in rows if r.get('error',{}).get('code')!='stale_revision'];assert not refused,refused
  page.wait_for_timeout(20)
 raise AssertionError(('save response missing',page.get_by_role('status').all_text_contents()))
try:
 start(0)
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=setup(browser);open_author();expect(author().locator('.bp-kind-set')).to_have_count(2);assert pending()==[];unchanged();assert not errors,errors;checked('기존 두 Set은 원본 260px 카드와 별도 저장한 값 출력으로 열리고 단순 열기는 초안을 만들지 않는다')
  if 'readonly' in sys.argv[3:]:
   assert current()['requiresCoupledCopy'];first=author().locator('[data-bp-node=first]');expect(first.locator('[data-set-target]')).to_be_disabled();expect(first.locator('[data-bp-remove]')).to_be_disabled();expect(first.locator('.bp-pin-plug[data-side=in] input')).to_have_attribute('readonly','');assert pending()==[];unchanged();checked('복사 provenance가 있는 원본은 서버 표시와 함께 Set 대상/입력/삭제를 읽기 전용으로 표시하고 개인·공유 변경을 만들지 않는다')
   before=current();command=request(before,{'nodes':[{'id':'first','local':'counter','outputLocal':'firstValue','type':'long','valueJson':'{"constant":6}'}]});call('blueprint',{'action':'authorBatch',**command},ok=False);assert current()['sources']==before['sources'];unchanged();assert not errors,errors;checked('클라이언트의 읽기 전용 UI를 우회한 Set 후보도 기존 서버 복사 소유권 검사로 거절한다');browser.close();print(json.dumps({'checks':checks,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
  if 'legacy' in sys.argv[3:]:
   assert not author().locator('[data-bp-node=first] .bp-port[data-side=out][data-kind=data]').count();assert not next(v for v in current()['nodes'] if v['id']=='first').get('outputLocal'),next(v for v in current()['nodes'] if v['id']=='first');unchanged();checked('이전 void Set을 열기만 해서는 새 출력/저장소나 원본 이행을 만들지 않는다')
   value('first','18');held=pending();plan=next(json.loads(v['text']) for _,v in held if v['type']=='set-plan');assert plan['outputLocal'] not in [v['id'] for v in current()['locals']];mark=len(traffic);author().locator('[data-bp-save]').click();saved(mark);after=current();node=next(v for v in after['nodes'] if v['id']=='first');assert node['local']=='counter' and node['outputLocal']==plan['outputLocal'] and node['arguments'][0]['valueJson']=='{"constant":18}';assert len(after['locals'])==len(g['locals'])+1;unchanged();checked('이전 Set의 명시적 값 편집만 새 보관 출력으로 이행하며 기존 대상/다른 저장소를 보존해 원자 저장한다');browser.close();print(json.dumps({'checks':checks,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
  if 'cancel-raw' in sys.argv[3:]:
   page.set_viewport_size({'width':390,'height':844});author().locator('[data-flow-insert][data-from=first][data-port=next]').click();page.get_by_role('dialog',name='블루프린트 노드 검색',exact=True).get_by_role('button',name='중간저장 만들기',exact=True).click();overlay=page.locator('.bp-flow-overlay-host:visible');overlay.locator('[data-flow-done]').click();author().locator('[data-flow-graph]').click();author().locator('.bp-viewport').focus();page.keyboard.press('Control+z');assert pending()==[];expect(author().locator('.bp-kind-set')).to_have_count(2);assert len(current()['nodes'])==3;unchanged();checked('새 Set와 실행 삽입을 원본 구조 Undo로 함께 취소하며 새 저장소나 부분 경로를 남기지 않는다')
   page.set_viewport_size({'width':1480,'height':1050});author().locator('[data-bp-node=first] .bp-pin-plug[data-side=out] .bp-pin-value').click();name=author().get_by_role('textbox',name='지역변수 이름',exact=True);name.fill('  ');name.press('Enter');held=pending();assert any(v['type']=='set-name-draft' and v['text']=='  ' for _,v in held);page.close();stop();start(1);page=setup(browser);expect(author().locator('[data-bp-save]')).to_be_enabled();idle();assert pending()==held;mark=len(traffic);author().locator('[data-bp-save]').click();idle();assert pending()==held;assert not any(r['endpoint']=='blueprint' and r.get('input',{}).get('action')=='authorBatch' for r in traffic[mark:]);author().locator('[data-bp-node=first] .bp-pin-plug[data-side=out] .bp-pin-value').click();name=author().get_by_role('textbox',name='지역변수 이름',exact=True);expect(name).to_have_value('  ');name.press('Escape');assert pending()==held;assert next(v for v in current()['locals'] if v['id']=='firstValue')['name']=='첫 저장값';unchanged();checked('불완전 이름은 실제 재시작·재진입 후 원문 그대로 복구하고 이번 편집 취소는 기존 보관 입력/서버 이름을 유지한다');browser.close();print(json.dumps({'checks':checks,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
  if 'response-loss' in sys.argv[3:]:
   value('first','24');submitted=pending();lost={};ids=set()
   def intercept(route):
    body=route.request.post_data_json
    if body.get('op')=='invoke' and body.get('endpoint')=='blueprint' and body.get('input',{}).get('action')=='authorBatch':ids.add(body['requestId'])
    response=route.fetch();payload=response.json()
    if not lost and body.get('op')=='update' and any(v.get('requestId') in ids for v in payload.get('results',[])):
     lost.update(route=route,response=response,payload=payload);return
    route.fulfill(response=response)
   page.route('**/api/request',intercept);author().locator('[data-bp-save]').click()
   for _ in range(1500):
    if lost:break
    page.wait_for_timeout(20)
   assert lost,'actual authorBatch result was not observed';assert all(v.get('ok') for v in lost['payload']['results'] if v.get('requestId') in ids)
   value('first','27');payload=lost['payload'];payload['results']=[{'requestId':v['requestId'],'ok':False,'error':{'code':'transport-interrupted'}} if v.get('requestId') in ids else v for v in payload['results']];lost['route'].fulfill(response=lost['response'],json=payload);idle();page.unroute('**/api/request',intercept);held=pending();assert any(v['type']=='argument:value' and v['text']=='{"constant":27}' for _,v in held);assert next(v for v in current()['nodes'] if v['id']=='first')['arguments'][0]['valueJson']=='{"constant":24}';unchanged();checked('실제 저장 성공 응답을 유실시켜도 저장 중 새로 입력한27과 기존 요청 기록을 보존하고 디스크에는 접수된24만 저장한다')
   assert not any(v.get('kind')=='author-attempt' for _,v in held),'lost reply must be settled by receipt before retry';page.close();stop();start(1);page=setup(browser);expect(author().locator('[data-bp-save]')).to_be_enabled();idle();retained=pending();assert any(v['type']=='argument:value' and v['text']=='{"constant":27}' for _,v in retained);assert next(v for v in current()['nodes'] if v['id']=='first')['arguments'][0]['valueJson']=='{"constant":24}';mark=len(traffic);author().locator('[data-bp-save]').click();saved(mark);assert pending()==[];data=current();assert next(v for v in data['nodes'] if v['id']=='first')['arguments'][0]['valueJson']=='{"constant":27}';assert len(data['nodes'])==3 and len(data['locals'])==len(g['locals']);unchanged();checked('receipt로 유실된24의 완료를 확인한 뒤 실제 재시작은 늦은27을 보존하고 다음 명시적 저장에서 중복 없이 적용한다');assert not errors,errors;browser.close();print(json.dumps({'checks':checks,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
  if 'conflict' in sys.argv[3:]:
   value('first','24');held=pending();before=current();call('blueprint',{'action':'intent','id':before['id'],'basis':before['basis'],'node':'second','text':'다른 편집자의 보관한 설명'});call('saveDraft',{});peer=current();mark=len(traffic);author().locator('[data-bp-save]').click()
   for _ in range(1500):
    attempts=[r for r in traffic[mark:] if r['endpoint']=='blueprint' and r.get('input',{}).get('action')=='authorBatch'];refused=[results[r['requestId']] for r in attempts if r['requestId'] in results and not results[r['requestId']].get('ok') and results[r['requestId']].get('error',{}).get('code')!='stale_revision']
    if refused:break
    page.wait_for_timeout(20)
   assert refused,('missing actual conflict rejection',page.get_by_role('status').all_text_contents());idle();retained=dict(pending());assert all(retained.get(key)==v for key,v in held);after=current();assert after['sources']==peer['sources'] and after['checkpointHash']==peer['checkpointHash'];assert next(v for v in after['nodes'] if v['id']=='first')['arguments'][0]['valueJson']=='{"constant":1}';assert next(v for v in after['nodes'] if v['id']=='second')['intent']=='다른 편집자의 보관한 설명';unchanged();checked('오래된 화면의 Set 저장은 실제 peer 변경을 CAS로 거절하고 사용자 입력/상대 설명/기존 checkpoint를 보존한다')
   page.close();stop();start(1);page=setup(browser);expect(author().locator('[data-bp-save]')).to_be_enabled();idle();retained=dict(pending());assert all(retained.get(key)==v for key,v in held);assert next(v for v in current()['nodes'] if v['id']=='first')['arguments'][0]['valueJson']=='{"constant":1}';assert current()['checkpointHash']==peer['checkpointHash'];assert not errors,errors;unchanged();checked('충돌 후 실제 재시작도 거절된 Set 입력과 저장 결과 기록을 보존하며 새 버전으로 자동 덮어쓰지 않는다');browser.close();print(json.dumps({'checks':checks,'evidence':str(case),'fixtureOnly':True},ensure_ascii=False));sys.exit(0)
  if 'create' in sys.argv[3:]:
   page.set_viewport_size({'width':390,'height':844});expect(author().locator('[data-flow-insert][data-from=first][data-port=next]')).to_be_visible();author().locator('[data-flow-insert][data-from=first][data-port=next]').click();page.get_by_role('dialog',name='블루프린트 노드 검색',exact=True).get_by_role('button',name='중간저장 만들기',exact=True).click();overlay=page.locator('.bp-flow-overlay-host:visible');expect(overlay.locator('[data-flow-set-target]')).to_be_visible();created=next(v['node'] for _,v in pending() if v['type']=='set-plan');overlay.locator('[data-signature-type]').click();page.get_by_role('dialog',name='속성 타입 선택',exact=True).locator('[data-type=long]').click();overlay.locator('[data-flow-set-target]').select_option('counter');overlay.locator('[data-signature-name]').fill('새 보관값');overlay.locator('[data-signature-name]').press('Tab');overlay.locator('[data-flow-value]').click();menu=page.get_by_role('dialog',name='핀 값 선택',exact=True);menu.get_by_role('searchbox',name='값 검색').fill('17');menu.get_by_role('searchbox',name='값 검색').press('Enter');expect(menu).not_to_be_visible();overlay.locator('[data-flow-done]').click();held=pending();assert any(v['type']=='set-plan' and json.loads(v['text'])['local']=='counter' and json.loads(v['text'])['type']=='long' for _,v in held);assert all(v['id']!=created for v in current()['nodes']);unchanged();checked('원본 검색/모바일 삽입으로 새 Set의 자료형·기존 대상·출력 이름·값을 함께 편집하고 기존 successor를 보존한다')
   page.close();stop();start(1);page=setup(browser);page.set_viewport_size({'width':390,'height':844});expect(author().locator('[data-bp-save]')).to_be_enabled();idle();assert pending()==held;mark=len(traffic);author().locator('[data-bp-save]').click();requests=saved(mark);data=current();node=next(v for v in data['nodes'] if v['id']==created);assert node['local']=='counter' and node['outputLocal']!='counter' and node['outputs']==[{'name':'stored','type':'long'}] and node['arguments'][0]['valueJson']=='{"constant":17}';assert {'from':'first','port':'next','to':created} in data['edges'] and {'from':created,'port':'next','to':'second'} in data['edges'];assert len(data['nodes'])==4;assert pending()==[];unchanged();checked('신규 Set와 새 출력 셀/이름/타입/값/직렬 삽입은 실제 재시작 후 하나의 Set 후보로 저장된다')
   assert not errors,errors;browser.close();print(json.dumps({'checks':checks,'evidence':str(case),'fixtureOnly':True},ensure_ascii=False));sys.exit(0)
  first=author().locator('[data-bp-node=first]');assert first.evaluate('(e)=>e.offsetWidth')==260;page.screenshot(path=str(case/'set-desktop.png'))
  first.locator('.bp-pin-plug[data-side=out] .bp-pin-value').click();name=author().get_by_role('textbox',name='지역변수 이름',exact=True);name.fill('');name.press('Enter');assert any(v['type']=='set-name-draft' and v['text']=='' for _,v in pending());assert next(v for v in current()['locals'] if v['id']=='firstValue')['name']=='첫 저장값';name.press('Escape');assert pending()==[];checked('불완전한 출력 이름은 비공개 입력에 보관하고 Escape는 서버나 기존 이름을 바꾸지 않고 취소한다')
  value('first','9223372036854775807');p=pending();assert any(v['type']=='set-plan' for _,v in p);assert any(v['type']=='argument:value' and '9223372036854775807' in v['text'] for _,v in p);assert next(v for v in current()['nodes'] if v['id']=='first')['arguments'][0]['valueJson']=='{"constant":1}';checked('Set 값 편집은 64비트 정수 원문과 별도 출력 저장소를 비공개 계획으로 유지하며 저장 전에 부분 적용하지 않는다')
  page.set_viewport_size({'width':390,'height':844});expect(author().locator('.bp-flow-card[data-flow-node=first]')).to_be_visible();author().locator('.bp-flow-card[data-flow-node=first]').click();overlay=page.locator('.bp-flow-overlay-host:visible');expect(overlay.locator('[data-flow-set-target]')).to_have_value('counter');expect(overlay.locator('[data-signature-name]')).to_have_value('첫 저장값');page.screenshot(path=str(case/'set-mobile.png'));held=pending();page.close();stop();start(1);page=setup(browser);page.set_viewport_size({'width':390,'height':844});expect(author().locator('[data-bp-save]')).to_be_enabled();idle();assert pending()==held;assert next(v for v in current()['nodes'] if v['id']=='first')['arguments'][0]['valueJson']=='{"constant":1}';checked('모바일 원본 저장 대상/출력 편집과 폭 전환 뒤 실제 엔진 재시작이 저장 전 입력 및 대상/출력 정체성을 복원한다')
  overlay=page.locator('.bp-flow-overlay-host:visible');
  if not overlay.is_visible():author().locator('.bp-flow-card[data-flow-node=first]').click()
  overlay.locator('[data-flow-done]').click();mark=len(traffic);author().locator('[data-bp-save]').click();requests=saved(mark);assert len(requests[-1]['input']['edits'])==1 and requests[-1]['input']['edits'][0]['action']=='setPlan';assert pending()==[];after=current();assert next(v for v in after['nodes'] if v['id']=='first')['arguments'][0]['valueJson']=='{"constant":9223372036854775807}';assert next(v for v in after['nodes'] if v['id']=='second')['local']=='counter';unchanged();checked('실제 모바일 저장은 값·대상·별도 출력 셀을 단일 Set 후보/CAS로 저장하고 원본 파일과 두 번째 Set을 보존한다')
  author().locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review.locator('[data-reject]')).to_be_visible(timeout=120000);idle();review.locator('[data-reject]').click();unchanged();page.locator('[data-tab-order-key="window:blueprint"] [role=tab]').click();author().locator('[data-bp-complete]').click();expect(review).to_be_visible(timeout=120000);
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  expect(review.locator('#confirm')).to_be_enabled(timeout=120000);review.locator('#confirm').click();idle();expect(review).not_to_be_visible(timeout=120000);assert json.loads((project/'Calc.graph.json').read_text())['nodes'][0]['arguments']['value']=={'constant':9223372036854775807};assert {name for name,b in original.items() if (project/name).read_bytes()!=b}=={'Calc.graph.json'};checked('컴파일 검토 취소는 원본을 유지하고 새 검토의 명시적 Confirm만 graph를 반영한다')
  assert not errors,errors;browser.close()
except Exception:
 print('EVIDENCE '+str(case),flush=True);print('PAGE_ERRORS '+str(errors),flush=True);raise
finally:stop()
record={'checks':checks,'actualEngine':True,'renderer':True,'nativeWindows':False,'nativeMobile':False,'accountOrInference':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
