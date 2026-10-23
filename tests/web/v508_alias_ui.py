"""Original existing root output controls against an isolated owned-element engine.
Save/Cancel/cold/Confirm and genuine-source-change guards; no account or inference.
"""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());fixture=pathlib.Path(sys.argv[3]).resolve();assert fixture==repo.parent/'scratch/v508-elements/actual13-source-fixture'
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-node-contract-engine-'));project=case/'owned project';shutil.copytree(fixture/'owned project',project,ignore=shutil.ignore_patterns('.confectory','.build'));storage=case/'profile';storage.mkdir();original={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.confectory' not in p.parts};id='Owned.Elements::Serial';text='9223372036854775804';description='재시작할 미적용 설명 한글';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'),CONFECTORY_WEB_PROJECT=str(project/'project.cproj'),CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;log=None;errors=[];external=[];checks=[]
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

def settled():
 expect(w.locator('[data-feature-action=save]')).to_be_enabled(timeout=30000)
 for _ in range(600):
  s=state();d=s.get('declaration')
  if d and d['id']==id and d['revision']==s['draft']['revision']:return s
  page.wait_for_timeout(20)
 raise AssertionError('feature inspect did not settle')

# 별칭의 관련 없는 overview 겹침을 피하는 격리 자료다.
fixture_graph=next((project/'blueprints').glob('*.graph.json'));g=json.loads(fixture_graph.read_text());g['nodes']=[n for n in g['nodes'] if n['id']=='body'];fixture_graph.write_text(json.dumps(g))
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup()
  def idle():page.evaluate('async()=>await confectoryFlushPresentation()')
  def browse():
   page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();return page.locator('.window[data-key^="browser:project:"]:visible')
  b=browse();b.locator('[data-tab=feature]').click();b.locator('[data-object="Owned.Elements::Main"]').get_by_role('button',name='정의 열기',exact=True).click();main=page.locator('.window[data-key=declaration]');expect(main.locator('[data-inline-description]')).to_be_visible(timeout=30000);b.locator('[data-close]').click();main.locator('[data-inline-description]').fill('별칭과 다른 함수 입력');main.locator('[data-close]').click();idle();b=browse();b.locator('[data-tab=feature]').click();b.locator('[data-object="'+id+'"]').get_by_role('button',name='정의 열기',exact=True).click();b.locator('[data-close]').click();page.locator('.window[data-key=declaration] [data-function-write-direct]').click();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);graphid=invoke('blueprint',{'action':'list','feature':id})['result']['result']['rows'][0]['id'];graphfile=fixture_graph;initial_graph=graphfile.read_bytes()
  def graph():return invoke('blueprint',{'action':'read','id':graphid})['result']['result']
  def private():idle();return state()['presentation']['inputs']['blueprint']
  def peers():return {k:v for k,v in state()['presentation']['inputs'].items() if k not in ('blueprint','target') and (k!='source' or v.get('dirty'))}
  peer=peers()
  def reveal(button):
   vp=author.locator('.bp-viewport');rect=vp.bounding_box();delta=button.evaluate('(el)=>{const a=el.getBoundingClientRect(),v=el.closest(".bp-viewport").getBoundingClientRect();return {x:a.x+a.width/2-v.x-v.width/2,y:a.y+a.height/2-v.y-v.height/2}}');page.mouse.move(rect['x']+rect['width']/2,rect['y']+rect['height']/2);page.mouse.wheel(delta['x'],delta['y']);page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
  def naming():
   author.locator('[data-bp-overview-node=body]').click();page.evaluate('()=>new Promise(requestAnimationFrame)');button=author.locator('.bp-inline-pin[data-node=body][data-side=out][data-port="field:return"] .bp-pin-value');reveal(button);button.click();panel=page.get_by_role('dialog',name='출력 핀 설정',exact=True);expect(panel).to_be_visible();return panel
  def enter_name(name):
   panel=naming();panel.get_by_role('textbox',name='지역변수 이름',exact=True).fill(name);page.keyboard.press('Enter');expect(panel).to_have_count(0)
  def save():author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=30000)
  def confirm():
   author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=30000)
   if review.locator('[data-additional-changes]').count():
    review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
    if ack.count():ack.check()
   expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000)
  initial=private();panel=naming();panel.get_by_role('textbox',name='지역변수 이름').fill('취소할 이름');page.keyboard.press('Escape');assert private()==initial and graphfile.read_bytes()==initial_graph and peers()==peer;panel=naming();panel.get_by_role('textbox',name='지역변수 이름').fill('단계 결과');unfinished=private();idle();page.close();stop();start(1);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert private()==unfinished;panel=naming();expect(panel.get_by_role('textbox',name='지역변수 이름')).to_have_value('단계 결과');page.keyboard.press('Enter');expect(panel).to_have_count(0);expect(author.locator('.bp-inline-pin[data-node=body][data-side=out] .bp-pin-label')).to_have_text('단계 결과');assert any(v['type']=='local-alias' for k,v in private()) and not graph()['locals'] and graphfile.read_bytes()==initial_graph;checked('원본 출력 이름 입력창의 취소와 미완성 이름 재시작 복원은 원본·함수 계약·다른 입력을 보존한다')
  retained=private();panel=naming();(case/'alias-form-geometry.json').write_text(json.dumps({'popup':panel.evaluate('(el)=>({width:el.offsetWidth,height:el.offsetHeight})'),'inline':page.get_by_role('group',name='출력 핀 이름 입력',exact=True).evaluate('(el)=>({width:el.offsetWidth,height:el.offsetHeight,remove:!!el.querySelector(\".bp-pin-remove\")})')}));page.screenshot(path=str(case/'alias-form-original.png'));page.get_by_role('group',name='출력 핀 이름 입력',exact=True).get_by_role('button',name='결과 삭제',exact=True).click();expect(panel).to_have_count(0);assert private()==retained and graphfile.read_bytes()==initial_graph
  before_type=private();author.locator('[data-bp-overview-node=body]').click();page.evaluate('()=>new Promise(requestAnimationFrame)');typed=author.locator('.bp-inline-pin[data-node=body][data-port=\"field:narrow\"] [aria-label=\"값 목록 열기\"]');reveal(typed);typed.click();typed_menu=page.get_by_role('dialog',name='핀 값 선택',exact=True);expect(typed_menu.get_by_role('button',name='지역변수 · 단계 결과',exact=True)).to_have_count(0);page.keyboard.press('Escape');assert private()==before_type
  author.locator('[data-bp-overview-node="$exit:return"]').click();page.evaluate('()=>new Promise(requestAnimationFrame)');button=author.locator('.bp-inline-pin[data-node="$exit:return"] [aria-label="값 목록 열기"]');reveal(button);button.click();menu=page.get_by_role('dialog',name='핀 값 선택',exact=True);expect(menu.get_by_role('button',name='지역변수 · 단계 결과',exact=True)).to_be_visible();menu.get_by_role('searchbox',name='값 검색').fill('단계 결과');page.keyboard.press('Enter');expect(menu).to_have_count(0);pending=private();observed=graph();proof=json.dumps(sorted([[row['id'],row['revision'],row['hash']] for row in observed['sources']]),separators=(',',':'));evil={'aliases':[{'id':'bad','name':'위조 이름','type':'long','sourceJson':'{"node":"다른프로젝트","output":"return"}'}],'bindings':[]};checkpoints=list(project.glob('.confectory/edit-workspaces/*/draft.json'));old={str(p):p.read_bytes() for p in checkpoints};invoke('blueprint',{'action':'authorBatch','id':graphid,'attempt':uuid.uuid4().hex,'checkpointHash':observed['checkpointHash'],'sourceProof':proof,'edits':[{'action':'aliasPlan','node':'$locals','definition':evil}]},False);assert private()==pending and {str(p):p.read_bytes() for p in project.glob('.confectory/edit-workspaces/*/draft.json')}==old and graphfile.read_bytes()==initial_graph and peers()==peer;self_plan={'aliases':[{'id':'self_alias','name':'순환 사용','type':'long','sourceJson':'{\"node\":\"body\",\"output\":\"return\"}'}],'bindings':[{'kind':'argument','node':'body','name':'seed','valueJson':'{\"local\":\"self_alias\"}'}]};invoke('blueprint',{'action':'authorBatch','id':graphid,'attempt':uuid.uuid4().hex,'checkpointHash':observed['checkpointHash'],'sourceProof':proof,'edits':[{'action':'aliasPlan','node':'$locals','definition':self_plan}]},False);assert private()==pending and {str(p):p.read_bytes() for p in project.glob('.confectory/edit-workspaces/*/draft.json')}==old and graphfile.read_bytes()==initial_graph;save();actual=graph();alias=actual['locals'][0];assert alias['name']=='단계 결과' and json.loads(alias['sourceJson'])=={'node':'body','output':'return'} and json.loads(actual['exits'][0]['valueJson'])=={'local':alias['id']} and graphfile.read_bytes()==initial_graph and peers()==peer;checked('원본 목록에서 별칭을 선택하고 이름+연결을 한 체크포인트로 저장하며 잘못된 소스는 전체 거부한다')
  confirm();saved=json.loads(graphfile.read_text());assert saved['locals'][0]['name']=='단계 결과' and saved['exits']['return']=={'local':alias['id']} and 'seed' in saved['nodes'][0]['arguments'];idle();page.close();stop();start(2);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert graph()['locals'][0]['name']=='단계 결과' and peers()==peer;checked('실제 컴파일 검토·명시적 확정·재시작에서 별칭 ID와 소비 연결을 유지한다')
  panel=naming();panel.get_by_role('textbox',name='지역변수 이름').fill('');page.keyboard.press('Enter');expect(panel).to_be_visible();page.keyboard.press('Escape');assert not private();panel=naming();panel.get_by_role('textbox',name='지역변수 이름').fill('다시 이름');page.keyboard.press('Control+s');expect(panel).to_have_count(0);expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=30000);confirm();now=json.loads(graphfile.read_text());assert now['locals'][0]['id']==alias['id'] and now['locals'][0]['name']=='다시 이름' and now['exits']==saved['exits'] and now['nodes']==saved['nodes'] and peers()==peer;checked('저장된 이름의 잘못된 수정 취소와 올바른 이름 변경·확정은 기존 저장소·소비자·핀 계약을 보존한다')
  idle();page.close();stop();start(3);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert graph()['locals'][0]['id']==alias['id'] and graph()['locals'][0]['name']=='다시 이름' and peers()==peer;page.screenshot(path=str(case/'alias-confirmed.png'));checked('마지막 재시작에서도 변경한 별칭 이름·고정 ID·다른 함수 입력을 복원한다');page.close();browser.close();assert not errors and not external,(errors,external)
except Exception:
 try:(case/'failure-state.json').write_text(json.dumps(state(),ensure_ascii=False,indent=2));(case/'failure.json').write_text(json.dumps({'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2));page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 print('격리 실패 자료 '+str(case));raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'nativeWindows':False,'accountOrInference':False,'projectRun':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
