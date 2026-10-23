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

# 표현식 묶음의 격리 자료에서는 관련 없는 미연결 노드만 제외한다.
fixture_graph=next((project/'blueprints').glob('*.graph.json'));g=json.loads(fixture_graph.read_text());g['nodes']=[n for n in g['nodes'] if n['id']=='body'];fixture_graph.write_text(json.dumps(g))

try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup()
  def idle():page.evaluate('async()=>await confectoryFlushPresentation()')
  def browse():
   page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();return page.locator('.window[data-key^="browser:project:"]:visible')
  b=browse();b.locator('[data-tab=feature]').click();b.locator('[data-object="Owned.Elements::Main"]').get_by_role('button',name='정의 열기',exact=True).click();main=page.locator('.window[data-key=declaration]');expect(main.locator('[data-inline-description]')).to_be_visible(timeout=30000);b.locator('[data-close]').click();main.locator('[data-inline-description]').fill('연산과 별개로 보관할 입력');main.locator('[data-close]').click();idle()
  b=browse();b.locator('[data-tab=feature]').click();b.locator('[data-object="'+id+'"]').get_by_role('button',name='정의 열기',exact=True).click();b.locator('[data-close]').click();page.locator('.window[data-key=declaration] [data-function-write-direct]').click();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);graphid=invoke('blueprint',{'action':'list','feature':id})['result']['result']['rows'][0]['id'];graphfile=next((project/'blueprints').glob('*.graph.json'));original_graph=graphfile.read_bytes()
  def graph():return invoke('blueprint',{'action':'read','id':graphid})['result']['result']
  def arg(name):return next(a['valueJson'] for n in graph()['nodes'] if n['id']=='body' for a in n['arguments'] if a['name']==name)
  def private():idle();return state()['presentation']['inputs']['blueprint']
  def peer():return {k:v for k,v in state()['presentation']['inputs'].items() if k not in ('blueprint','target') and (k!='source' or v.get('dirty'))}
  before_peer=peer()
  def menu(name,path='',operator=False):
   author.locator('[data-bp-overview-node=body]').click();page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');plug=author.locator('.bp-inline-pin[data-node=body][data-side=in][data-port="field:'+name+'"]');button=plug.locator('[data-expression-group="'+path+'"] > .bp-expression-terminal > button.bp-expression-operator') if operator else plug.locator('input[data-expression-path="'+path+'"]').locator('..').locator('[aria-label="값 목록 열기"]');vp=author.locator('.bp-viewport');box=vp.bounding_box();delta=button.evaluate('(el)=>{const a=el.getBoundingClientRect(),v=el.closest(".bp-viewport").getBoundingClientRect();return {x:a.x+a.width/2-v.x-v.width/2,y:a.y+a.height/2-v.y-v.height/2}}');page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2);page.mouse.wheel(delta['x'],delta['y']);page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');button.click();d=page.get_by_role('dialog',name='핀 값 선택',exact=True);expect(d).to_be_visible();return d
  def choose(name,path,label):menu(name,path).get_by_role('button',name=label,exact=True).click()
  def literal(name,path,value):
   d=menu(name,path);d.get_by_role('searchbox',name='값 검색').fill(value);page.keyboard.press('Enter');expect(d).to_have_count(0)
  def save():author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=30000)
  def confirm():
   author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=30000)
   if review.locator('[data-additional-changes]').count():
    review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
    if ack.count():ack.check()
   expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000)
  # 원본도 양의 카메라 이동을 막는다. 기존 헤더 드래그로 넓은 식의 배치 여백을 둔다.
  author.locator('[data-bp-overview-node=body]').click();page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');body=author.locator('[data-bp-node=body]');prior=body.evaluate('(el)=>parseFloat(el.style.left)');header=body.locator('.function-node-heading').bounding_box();page.mouse.move(header['x']+70,header['y']+22);page.mouse.down();page.mouse.move(header['x']+370,header['y']+22,steps=10);page.mouse.up();page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');assert body.evaluate('(el)=>parseFloat(el.style.left)')>=prior+280
  initial=private();menu('seed').get_by_role('button',name='연산자 +',exact=True).click();expect(author.locator('[data-port="field:seed"].has-expression-tree')).to_have_count(1);pending=private();assert pending!=initial;author.locator('[data-bp-save]').click();idle();assert graphfile.read_bytes()==original_graph and private()==pending and peer()==before_peer;author.locator('.bp-viewport').focus();page.keyboard.press('Control+z');assert private()==initial;checked('원본 연산자 버튼·트리·구조 Undo가 연결되며 미완성 연산 저장은 입력과 기존 소스를 보존하고 거부한다')
  menu('seed').get_by_role('button',name='연산자 +',exact=True).click();literal('seed','0','9223372036854775700');menu('seed','1').get_by_role('button',name='연산자 *',exact=True).click();choose('seed','1.0','입력 · other');literal('seed','1.1','7');pending=private();d=menu('seed','0');d.get_by_role('searchbox',name='값 검색').fill('잘못된 정수');page.keyboard.press('Enter');expect(d.locator('[aria-invalid=true]')).to_be_visible();page.keyboard.press('Escape');assert private()==pending and graphfile.read_bytes()==original_graph and peer()==before_peer;checked('중첩 연산의 피연산자를 실제 원본 메뉴로 선택하며 64비트 토큰·다른 입력과 잘못된 입력 취소를 보존한다')
  # 원본 조건 체크박스와 글자 연산 트리도 실제 화면에서 연결한다.
  menu('flag').get_by_role('button',name='연산자 XOR',exact=True).click()
  def check_bool(path):
   author.locator('[data-bp-overview-node=body]').click();page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');plug=author.locator('.bp-inline-pin[data-node=body][data-port=\"field:flag\"]');control=plug.locator('[data-bool-path=\"'+path+'\"]');vp=author.locator('.bp-viewport');box=vp.bounding_box();delta=control.evaluate('(el)=>{const a=el.getBoundingClientRect(),v=el.closest(\".bp-viewport\").getBoundingClientRect();return {x:a.x+a.width/2-v.x-v.width/2,y:a.y+a.height/2-v.y-v.height/2}}');page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2);page.mouse.wheel(delta['x'],delta['y']);page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');(case/('bool-hit-'+path+'.json')).write_text(json.dumps(control.evaluate('(el)=>{const r=el.getBoundingClientRect(),p=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return {rect:{x:r.x,y:r.y,w:r.width,h:r.height},hit:p?.outerHTML.slice(0,300),parent:el.closest(\".bp-inline-pin\").getBoundingClientRect().toJSON()}}')));page.screenshot(path=str(case/('bool-before-'+path+'.png')));control.click()
  check_bool('0');check_bool('1');check_bool('1');menu('title').get_by_role('button',name='연산자 +',exact=True).click();literal('title','0','한글 \"원본\" ');literal('title','1','😀');pending=private();checked('원본 조건 체크박스와 글자 더하기도 실제 원본 연산 트리에서 선택한다')
  idle();page.close();stop();start(1);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert private()==pending and graphfile.read_bytes()==original_graph and peer()==before_peer;expect(author.locator('[data-port="field:seed"].has-expression-tree')).to_have_count(1);save();expected={'binary':{'operator':'+','operands':[{'constant':9223372036854775700},{'binary':{'operator':'*','operands':[{'input':'other'},{'constant':7}]}}]}};assert json.loads(arg('seed'))==expected and json.loads(arg('flag'))=={'binary':{'operator':'XOR','operands':[{'constant':True},{'constant':False}]}} and json.loads(arg('title'))=={'binary':{'operator':'+','operands':[{'constant':'한글 \"원본\" '},{'constant':'😀'}]}} and graphfile.read_bytes()==original_graph;confirm();assert next(n for n in json.loads(graphfile.read_text())['nodes'] if n['id']=='body')['arguments']['seed']==expected;checked('실제 재시작·Save·컴파일 검토·명시적 Confirm으로 중첩 연산과 정확한 정수 값을 저장한다')
  idle();page.close();stop();start(2);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert json.loads(arg('seed'))==expected and peer()==before_peer;expect(author.locator('[data-port="field:seed"].has-expression-tree')).to_have_count(1);author.locator('[data-bp-overview-node=body]').click();page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');target=author.locator('.bp-inline-pin[data-node=body][data-port=\"field:seed\"] .bp-expression-root');vp=author.locator('.bp-viewport');box=vp.bounding_box();delta=target.evaluate('(el)=>{const a=el.getBoundingClientRect(),v=el.closest(\".bp-viewport\").getBoundingClientRect();return {x:a.x+a.width/2-v.x-v.width/2,y:a.y+a.height/2-v.y-v.height/2}}');page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2);page.mouse.wheel(delta['x'],delta['y']);page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');(case/'expression-geometry.json').write_text(json.dumps(target.evaluate('(el)=>({width:el.offsetWidth,height:el.offsetHeight,groups:el.querySelectorAll(\".bp-expression-binary\").length})')));page.screenshot(path=str(case/'expression-confirmed.png'));checked('확정 후 다시 실행해도 원본 연산 트리·연결·별개 입력을 복원한다');page.close();browser.close();assert not errors and not external,(errors,external)
except Exception:
 try:(case/'failure-state.json').write_text(json.dumps(state(),ensure_ascii=False,indent=2));(case/'failure.json').write_text(json.dumps({'traffic':traffic,'errors':errors},indent=2));page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 print('격리 실패 자료 '+str(case));raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'nativeWindows':False,'accountOrInference':False,'projectRun':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
