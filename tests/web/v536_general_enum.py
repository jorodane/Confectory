"""Original v536 ordinary code enum contract/body transaction; isolated mobile engine, no account/inference/run."""
import hashlib,json,re,os,pathlib,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-general-enum-'));project=case/'owned project';project.mkdir();n='Owned.Context::'
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
node.clear();node.update(id='native',kind='code',displayName='일반 실행 기능',control='switch',intent='순차 실행 줄을 선택하는 일반 C#',executionEnum=enum,signature={'args':[{'name':'amount','type':'long'}],'return':'void'},arguments={'amount':{'input':'amount'}},implementation='native.node.json');next(v for v in g['nodes'] if v['id']=='body')['arguments']={'amount':{'input':'amount'}}
items['Caller']=('implementation',prepared['implementation'])

sources={'Main.csbody':'return checked((int)calls.Chosen.Invoke(1));','Other.csbody':'return amount+8;','Native.csbody':'return amount+3;','Caller.graph.json':json.dumps(g),'Caller.node.json':json.dumps(record)}
for name,(kind,text) in items.items():sources[name+'.celem']=text
sources['project.cproj']='project Owned.Context version "1" {standalone true;entry '+n+'Main;'+''.join('element '+name+' '+kind+' "'+name+'.celem";' for name,(kind,text) in items.items())+'registry Confectory.Build.DotNet "'+str(repo/'targets/dotnet/pack.cpack')+'";dependency Confectory.Build.DotNet version "0.1.0";target portable Confectory.Build.DotNet::Portable;}'
for name in ['ready','readyTail','done']:
 g['nodes'].append({'id':name,'kind':'code','control':'next','branchOwner':'native','intent':'기존 '+name+' 실행 줄','signature':{'args':[],'return':'void'},'arguments':{},'implementation':name+'.node.json'})
g['edges'] += [{'from':'native','port':'case:ready','to':'ready'},{'from':'ready','port':'next','to':'readyTail'},{'from':'readyTail','port':'next','to':'return:native'},{'from':'native','port':'case:done','to':'done'},{'from':'done','port':'next','to':'return:native'}]
if 'copy-boundary' in sys.argv[3:]:g['copySource']={'implementation':n+'Other','target':'common','bodyOrigin':n+'Other','sourceKind':'blueprint'}
definitions=metadata('featureBlueprintNodes',featureSource=items['Calc'][1],featureContracts={n+'Native':items['Native'][1]},graph=g);assert definitions['state']=='node-definitions',definitions
for definition in definitions['nodes']:
 if definition['definition']['kind']!='code':continue
 name=definition['id'];sources['Caller.node.json' if name=='body' else name+'.node.json']=json.dumps({'schema':1,'node':name,'definitionHash':definition['definitionHash'],'source':'return amount;' if name=='body' else 'return Result.Ready;' if name=='native' else '// 기존 '+name+' 본문 한글 😀'})
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
 author.locator('[data-flow-tab=flow]').click();author.locator('[data-flow-node=native]').click();page.locator('.bp-flow-overlay-host:visible [data-flow-code]').click();return page.get_by_role('dialog',name='C# Script · 일반 실행 기능',exact=True)
def edit(d,region,text):
 field=d.locator('[data-code-source]');field.evaluate('(el,region)=>{const spans=[...el.closest(".bp-script-editor").querySelectorAll("[data-code-highlight]>span")],part=spans.find(p=>p.dataset.codeRegion===region);if(!part)throw Error("source region missing");const start=spans.slice(0,spans.indexOf(part)).reduce((n,p)=>n+p.textContent.length,0);el.setSelectionRange(start,start+part.textContent.length)}',region);page.keyboard.insert_text(text)
def done_editor():
 overlay=page.locator('.bp-flow-overlay-host:visible')
 if overlay.count():overlay.locator('[data-flow-done]').click()
def pending_enums():return [(k,v) for k,v in pending() if v.get('type')=='enum-code']
if 'copy-boundary' in sys.argv[3:]:
 try:
  start(0);data=current();before=data['sources'];proof=json.dumps(sorted([[v['id'],v['revision'],v['hash']] for v in before]),separators=(',',':'));plan={'executionEnum':native(data)['executionEnum'],'source':'return Result.Done;','helpers':''};refused=call('blueprint',{'action':'authorBatch','id':data['id'],'attempt':uuid.uuid4().hex,'sourceProof':proof,'checkpointHash':data['checkpointHash'],'edits':[{'action':'enumCode','node':'native','definition':plan}]},ok=False);assert not refused['ok'] and current()['sources']==before and current()['checkpointHash']==data['checkpointHash'];unchanged();checked('graph가 복사 출처를 가진 경우 소유 슬롯 문맥을 생략해도 일반 enum batch를 거절하고 전체 원본/초안을 보존한다')
 finally:stop()
 print(json.dumps({'actualEngine':True,'checks':checks,'copyBoundaryOnly':True,'evidence':str(case)},ensure_ascii=False));sys.exit(0)
try:
 start(0)
 with sync_playwright() as p:
  expect.set_options(timeout=30000);browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=setup(browser);author=open_author();page.set_viewport_size({'width':390,'height':844});expect(author.locator('[data-flow-tab=flow]')).to_be_visible();initial=current();edges=initial['edges'];d=code_dialog();edit(d,'enum','    NoBranch = 0,\n    Done = 2,\n');d.locator('[data-code-save]').click();expect(d.locator('[data-code-error]')).to_contain_text('실행 줄');assert pending()==[];unchanged();d.locator('[data-code-cancel]').click();done_editor();checked('일반 C# 원본 enum에서 연결된 실행 핀 삭제를 거절하고 취소 시 원본/연결을 보존한다')
  d=code_dialog();edit(d,'enum','    NoBranch = 0,\n    Done = 1,\n    Ready = 2,\n');edit(d,'body','// 일반 enum 한글 😀\nreturn Choose();');edit(d,'helpers','private static Result Choose() => Result.Ready;');d.locator('[data-code-save]').click();held=pending_enums();assert len(held)==1;value=json.loads(held[0][1]['text']);assert {v['id']:(v['name'],v['value']) for v in value['executionEnum']['members']}=={'next':('NoBranch',0),'done':('Done',1),'ready':('Ready',2)};assert current()['edges']==edges and native(current())['source']=='return Result.Ready;';done_editor();pending();page.screenshot(path=str(case/'mobile-general-enum.png'));page.close();stop();start(1);page=setup(browser);page.set_viewport_size({'width':390,'height':844});author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled();assert pending_enums()==held;unchanged();checked('일반 enum 이름/값/순서·본문·보조 함수의 미저장 입력을 실제 재시작으로 복원하며 저장 전에 계약/본문을 부분 적용하지 않는다')
  done_editor();mark=len(traffic);author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=60000);data=current();row=native(data);assert row['source']==value['source'] and row['helpers']==value['helpers'] and row['executionEnum']==value['executionEnum'] and data['edges']==edges and data['diagnostics']['state'] in ['source-ready','source-assembled'],data;assert pending()==[];batch=[r for r in traffic[mark:] if r.get('endpoint')=='blueprint' and r.get('input',{}).get('action')=='authorBatch'];assert len(batch)==1 and [e['action'] for e in batch[0]['input']['edits']]==['enumCode'];unchanged();checked('일반 enum 계약·본문·보조 함수를 한 authorBatch/checkpoint로 저장하고 기존 핀 식별성·연결과 다른 소스를 보존한다')
  author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000);assert state()['review']['status']=='ready';review.locator('[data-reject]').click();expect(review).to_be_hidden();unchanged();page.locator('[data-tab-order-key="window:blueprint"] [role=tab]').click();author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=60000)
  if review.locator('[data-review-advanced]').count():
   review.locator('[data-review-advanced]').click()
   if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
  mark=len(traffic);review.locator('#confirm').click();result=completed('confirmGroup',None,mark);assert result['result']['sourceConfirmed'];expect(review).to_have_count(0,timeout=90000);assert {name for name,b in original.items() if (project/name).read_bytes()!=b}=={'Caller.graph.json','native.node.json'};assert json.loads((project/'native.node.json').read_text())['helpers']==value['helpers'];original={name:(project/name).read_bytes() for name in original};checked('실제 compiler Review 취소와 새 명시적 Confirm을 분리하고 일반 enum 계약/본문만 확정한다')
  page.locator('[data-tab-order-key="window:blueprint"] [role=tab]').click();page.set_viewport_size({'width':1480,'height':1050});viewport=author.locator('.bp-viewport');vp=viewport.bounding_box();nodebox=author.locator('[data-bp-node=ready]').bounding_box();page.mouse.move(vp['x']+vp['width']/2,vp['y']+vp['height']/2);page.mouse.wheel(nodebox['x']-vp['x']-150,0);author.locator('[data-bp-node=ready] [data-bp-add-branch]').click();assert len(pending_enums())==1;author.locator('[data-bp-node=ready] [data-internal-code]').click();d=page.get_by_role('dialog',name='C# Script · ready',exact=True);edit(d,'body','return Result.NoBranch;');d.locator('[data-code-save]').click();author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=60000);created=next(v for v in current()['nodes'] if v['id']=='ready');assert created['control']=='switch' and created['source']=='return Result.NoBranch;' and len(created['executionEnum']['members'])==2;assert all(e in current()['edges'] for e in edges);unchanged();checked('기존 원본 분기 생성 버튼으로 void 일반 노드를 enum으로 전환하고 C# Result 본문과 기존 next 연결을 함께 저장한다')
  data=current();proof=json.dumps(sorted([[v['id'],v['revision'],v['hash']] for v in data['sources']]),separators=(',',':'));checkpoint=data['checkpointHash'];before=data['sources'];bad={'executionEnum':value['executionEnum'],'source':'return Result.Ready;','helpers':''};direct=call('blueprint',{'action':'enumCode','id':data['id'],'node':'native','definition':bad},ok=False);assert not direct['ok'];refused=call('blueprint',{'action':'authorBatch','id':data['id'],'attempt':uuid.uuid4().hex,'sourceProof':proof,'checkpointHash':checkpoint,'edits':[{'action':'enumCode','node':'body','definition':bad}]},ok=False);assert not refused['ok'] and current()['sources']==before;unchanged();checked('외부 직접 enum 적용 및 데이터 반환 노드의 enum 위조 요청은 원자 후보를 거절하고 저장본을 보존한다')
  page.set_viewport_size({'width':390,'height':844});d=code_dialog();edit(d,'enum','    NoBranch = 0,\n    Ready = 1,\n    Done = 2,\n');d.locator('[data-code-save]').click();held=pending();done_editor();peer=current();call('blueprint',{'action':'intent','id':data['id'],'basis':peer['basis'],'node':'done','text':'다른 편집자의 보관된 변경'});call('saveDraft',{});author.locator('[data-bp-save]').click();page.wait_for_function("()=>{const text=document.querySelector('.window[data-key=blueprint] .bp-status')?.textContent;return text&&!['저장됨','저장 중…','미저장 초안'].includes(text)}");now=pending();assert [[k,v] for k,v in now if v.get('kind')!='author-attempt']==held,(held,now);journals=[v for k,v in now if v.get('kind')=='author-attempt'];assert len(journals)==1 and journals[0]['edits'][0]['action']=='enumCode';assert next(v for v in current()['nodes'] if v['id']=='done')['intent']=='다른 편집자의 보관된 변경';assert native(current())['executionEnum']==value['executionEnum'];unchanged();checked('실제 다른 편집자/checkpoint 변경 시 enum 계약·본문의 부분 저장 없이 충돌을 거절하고 사용자 입력과 peer 초안을 보존한다')
  assert not errors and not external,(errors,external);page.close();browser.close()
except Exception:
 print('EVIDENCE '+str(case),flush=True);raise
finally:stop()
record={'checks':checks,'actualEngine':True,'browserWidth':[390,1480],'nativeWindowsOrMobile':False,'accountOrInference':False,'projectRun':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
