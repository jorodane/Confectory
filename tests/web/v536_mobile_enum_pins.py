"""Original v536 enum execution-pin identities, mobile branch editing, no account/inference/run."""
import hashlib,json,re,os,pathlib,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-mobile-enum-pins-'));project=case/'owned project';project.mkdir();n='Owned.Context::'
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
enum={'primary':'next','members':[{'id':'next','name':'NoBranch','value':0},{'id':'ready','name':'Ready','value':1},{'id':'done','name':'Done','value':2}]}
wrapper=metadata('blueprintCallWrapper',functionText=items['Native'][1],executionEnum=enum,returnMapping='native-return-out-v1',source='return Result.Ready;')
node.update(control='switch',executionEnum=enum,postCall={'mode':'execution-enum','returnMapping':'native-return-out-v1','contractHash':wrapper['contractHash'],'source':wrapper['source'],'helpers':''})
items['Caller']=('implementation',prepared['implementation'])

sources={'Main.csbody':'return checked((int)calls.Chosen.Invoke(1));','Other.csbody':'return amount+8;','Native.csbody':'return amount+3;','Caller.graph.json':json.dumps(g),'Caller.node.json':json.dumps(record)}
for name,(kind,text) in items.items():sources[name+'.celem']=text
sources['project.cproj']='project Owned.Context version "1" {standalone true;entry '+n+'Main;'+''.join('element '+name+' '+kind+' "'+name+'.celem";' for name,(kind,text) in items.items())+'registry Confectory.Build.DotNet "'+str(repo/'targets/dotnet/pack.cpack')+'";dependency Confectory.Build.DotNet version "0.1.0";target portable Confectory.Build.DotNet::Portable;}'
for name in ['ready','readyTail','done']:
 g['nodes'].append({'id':name,'kind':'code','control':'next','branchOwner':'native','intent':'기존 '+name+' 실행 줄','signature':{'args':[],'return':'void'},'arguments':{},'implementation':name+'.node.json'})
g['edges'] += [{'from':'native','port':'case:ready','to':'ready'},{'from':'ready','port':'next','to':'readyTail'},{'from':'readyTail','port':'next','to':'return:native'},{'from':'native','port':'case:done','to':'done'},{'from':'done','port':'next','to':'return:native'}]
definitions=metadata('featureBlueprintNodes',featureSource=items['Calc'][1],featureContracts={n+'Native':items['Native'][1]},graph=g);assert definitions['state']=='node-definitions',definitions
for definition in definitions['nodes']:
 if definition['definition']['kind']!='code':continue
 name=definition['id'];sources['Caller.node.json' if name=='body' else name+'.node.json']=json.dumps({'schema':1,'node':name,'definitionHash':definition['definitionHash'],'source':'return amount;' if name=='body' else '// 기존 '+name+' 본문 한글 😀'})
sources['Caller.graph.json']=json.dumps(g)
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
def open_author():
 open_row('Calc','feature');page.locator('.window[data-key=declaration] [data-function-write-direct]').click();a=page.locator('.window[data-key=blueprint]');expect(a).to_have_attribute('data-blueprint-owner','');expect(a).to_have_attribute('data-blueprint-body',n+'Caller/body:common');idle();return a
def current():return call('blueprint',{'action':'read','id':n+'Caller/body:common'})
def native(data):return next(v for v in data['nodes'] if v['id']=='native')
def code_dialog():
 author.locator('[data-flow-tab=flow]').click();author.locator('[data-flow-node=native]').click();page.locator('.bp-flow-overlay-host:visible [data-flow-code]').click();return page.get_by_role('dialog',name='분기 기능 편집 · Native',exact=True)
def edit(d,region,text):
 field=d.locator('[data-code-source]');field.evaluate('(el,region)=>{const spans=[...el.closest(".bp-script-editor").querySelectorAll("[data-code-highlight]>span")],part=spans.find(p=>p.dataset.codeRegion===region);if(!part)throw Error("source region missing");const start=spans.slice(0,spans.indexOf(part)).reduce((n,p)=>n+p.textContent.length,0);el.setSelectionRange(start,start+part.textContent.length)}',region);page.keyboard.insert_text(text)
def done_editor():
 overlay=page.locator('.bp-flow-overlay-host:visible')
 if overlay.count():overlay.locator('[data-flow-done]').click()
def pending_wrappers():return [(k,v) for k,v in pending() if v.get('type')=='wrapper']
try:
 start(0)
 with sync_playwright() as p:
  expect.set_options(timeout=30000);browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=setup(browser);author=open_author();page.set_viewport_size({'width':390,'height':844});expect(author.locator('[data-flow-tab=flow]')).to_be_visible();initial=current();edges=initial['edges'];assert any(e['port']=='case:ready' for e in edges);d=code_dialog();edit(d,'enum','    NoBranch = 0,\n    Done = 2,\n');d.locator('[data-code-save]').click();expect(d.locator('[data-code-error]')).to_contain_text('실행 줄');assert pending()==[];unchanged();d.locator('[data-code-cancel]').click();done_editor();checked('모바일 후속 C#에서 연결된 특수 실행 핀 삭제를 거절하고 편집 취소 시 입력/원본/연결을 유지한다')
  d=code_dialog();edit(d,'enum','    NoBranch = 0,\n    Done = 1,\n    Ready = 2,\n');d.locator('[data-code-save]').click();held=pending_wrappers();assert len(held)==1;value=json.loads(held[0][1]['text']);members=value['executionEnum']['members'];assert {v['id']:(v['name'],v['value']) for v in members}=={'next':('NoBranch',0),'done':('Done',1),'ready':('Ready',2)},members;assert [v['id'] for v in members]==['next','done','ready'];assert value['source']=='return Result.Ready;';done_editor();author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=60000);assert current()['edges']==edges;assert native(current())['executionEnum']==value['executionEnum'];unchanged();checked('원본처럼 이름 우선 대응으로 enum 이름/값/순서 변경에도 핀 ID와 기존 case 연결을 그대로 저장한다')
  # Source original branch gap, no new panel or execution meaning.
  details=author.locator('[data-flow-fold="native:case:ready"]');details.locator('summary').click();gap=details.locator('[data-flow-insert][data-from=native][data-port="case:ready"]');gap.click();search=page.get_by_role('dialog',name='블루프린트 노드 검색',exact=True);expect(search).to_be_visible();search.locator('[data-resource-close]').click();assert pending()==[];unchanged();checked('기존 모바일 특수 실행 줄의 검색 열기/취소는 연결과 저장된 enum을 바꾸지 않는다')
  gap.click();search=page.get_by_role('dialog',name='블루프린트 노드 검색',exact=True);search.get_by_role('button',name='동작 만들기',exact=True).click();overlay=page.locator('.bp-flow-overlay-host:visible');expect(overlay.locator('[data-flow-node-description]')).to_be_visible();created=next(json.loads(v['text']) for k,v in pending() if v.get('type')=='create');assert created['branchOwner']=='native';done_editor();author.locator('[data-flow-graph]').click();expect(author.locator('.bp-viewport')).to_be_visible();author.locator('.bp-viewport').focus();page.keyboard.press('Control+z');assert pending()==[],page.get_by_role('status').all_text_contents();assert current()['edges']==edges;unchanged();checked('분기 줄에 추가한 미편집 노드는 원본 구조 취소로 되돌리고 원래 successor/두 case 연결을 보존한다')
  if author.locator('[data-mobile-flow]').is_visible():author.locator('[data-mobile-flow]').click()
  expect(author.locator('[data-flow-tab=flow]')).to_be_visible();details=author.locator('[data-flow-fold="native:case:ready"]');
  if details.get_attribute('open') is None:details.locator('summary').click()
  details.locator('[data-flow-insert][data-from=native][data-port="case:ready"]').click();page.get_by_role('dialog',name='블루프린트 노드 검색',exact=True).get_by_role('button',name='동작 만들기',exact=True).click();overlay=page.locator('.bp-flow-overlay-host:visible');overlay.locator('[data-flow-node-description]').fill('기존 Ready 경로 앞에 연결하는 동작');new_id=next(v['node'] for k,v in pending() if v.get('type')=='create');overlay.locator('[data-flow-code]').click();d=page.get_by_role('dialog',name='C# Script · 내부 기능',exact=True);edit(d,'body','// 새 분기 앞부분 한글 😀');d.locator('[data-code-save]').click();held=pending();done_editor();page.screenshot(path=str(case/'mobile-enum-pin-flow.png'));pending();page.close();stop();start(1);page=setup(browser);page.set_viewport_size({'width':390,'height':844});author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled();assert pending()==held;assert not any(v['id']==new_id for v in current()['nodes']);unchanged();checked('특수 핀에 추가한 branchOwner/설명/본문/원래 successor 입력은 실제 재시작 후 복원되며 저장 전 live graph에 부분 적용되지 않는다')
  done_editor();author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=60000);data=current();new_node=next(v for v in data['nodes'] if v['id']==new_id);assert new_node['branchOwner']=='native' and new_node['source']=='// 새 분기 앞부분 한글 😀';assert {'from':'native','port':'case:ready','to':new_id} in data['edges'] and {'from':new_id,'port':'next','to':'ready'} in data['edges'];assert all(e in data['edges'] for e in edges if not(e['from']=='native' and e['port']=='case:ready'));assert pending()==[];unchanged();checked('실제 원자 Save는 정확한 case scope 안에만 새 노드를 삽입하고 기존 Ready 꼬리·Done·main continuation과 다른 소스를 보존한다')
  author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000);assert state()['review']['status']=='ready';review.locator('[data-reject]').click();expect(review).to_be_hidden();unchanged();page.locator('[data-tab-order-key="window:blueprint"] [role=tab]').click();author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000)
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  mark=len(traffic);review.locator('#confirm').click();result=completed('confirmGroup',None,mark);assert result['result']['sourceConfirmed'];expect(review).to_have_count(0,timeout=90000);assert {name for name,b in original.items() if (project/name).read_bytes()!=b}=={'Caller.graph.json'};record_path=next(r['path'] for r in current()['sources'] if r['id'].endswith('/node:'+new_id));assert json.loads((project/record_path).read_text())['source']=='// 새 분기 앞부분 한글 😀';original={name:(project/name).read_bytes() for name in original};checked('모바일 Review 취소와 명시적 compiler Confirm은 분리되고 graph/새 source만 반영하며 callee·기존노드·객체·main 소스를 유지한다')
  page.locator('[data-tab-order-key="window:blueprint"] [role=tab]').click();d=code_dialog();edit(d,'enum','    NoBranch = 0,\n    Ready = 1,\n    Done = 2,\n');d.locator('[data-code-save]').click();held=pending();done_editor();peer=current();call('blueprint',{'action':'intent','id':data['id'],'basis':peer['basis'],'node':'ready','text':'다른 편집자가 보관한 Ready 설명'});call('saveDraft',{});author.locator('[data-bp-save]').click();page.wait_for_function("()=>{const text=document.querySelector('.window[data-key=blueprint] .bp-status')?.textContent;return text&&!['저장됨','저장 중…','미저장 초안'].includes(text)}");assert pending()==held;assert next(v for v in current()['nodes'] if v['id']=='ready')['intent']=='다른 편집자가 보관한 Ready 설명';assert native(current())['executionEnum']==value['executionEnum'];unchanged();checked('다른 편집자의 graph/checkpoint 변경은 오래된 특수 핀 Save를 거절하고 새 peer 설명·기존 연결·사용자 enum 입력을 보존한다')
  assert not errors and not external,(errors,external);page.close();browser.close()
except Exception:
 print('EVIDENCE '+str(case),flush=True);raise
finally:stop()
record={'checks':checks,'actualEngine':True,'browserWidth':390,'nativeWindowsOrMobile':False,'accountOrInference':False,'projectRun':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
