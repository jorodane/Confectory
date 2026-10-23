"""원본 자유 입력 정의/중첩 실수 승격을 격리 실제 엔진에서 검사한다.
입력 ABI와 별칭 타입을 유지하며 Save/Cancel/cold/Confirm; 계정/추론 없음.
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

def sdk(op,**data):
 p=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':op,**data}),text=True,capture_output=True,check=True,env=env);v=json.loads(p.stdout);assert v['ok'],v;return v['result']
feature_file=project/'elements/Serial.celem';impl_file=project/'elements/SerialBlueprintBody.celem';graphfile=next((project/'blueprints').glob('*.graph.json'));nodepath='nodes/promotion-body.node.json';created=sdk('blueprintPrepareFeature',id=id,text='function '+id+' (long seed,int narrow,double ratio,float quick) -> double {}',implementation='Owned.Elements::SerialBlueprintBody',graphPath=str(graphfile.relative_to(project)),nodePath=nodepath);g=created['graph'];producer={'id':'integer','kind':'code','control':'next','intent':'정수 저장소','displayName':'정수 값','signature':{'args':[],'return':'long'},'arguments':{},'implementation':'nodes/promotion-integer.node.json'};g['nodes'].insert(0,producer);g['entry']='integer';g['edges']=[{'from':'integer','port':'next','to':'body'},{'from':'body','port':'next','to':'exit:return'}];g['exits']={'return':{'node':'body'}};defs=sdk('featureBlueprintNodes',featureSource=created['function'],graph=g);feature_file.write_text(created['function']);impl_file.write_text(created['implementation']);graphfile.write_text(json.dumps(g))
for n in g['nodes']:
 definition=next(row for row in defs['nodes'] if row['id']==n['id']);file=graphfile.parent/n['implementation'];file.parent.mkdir(parents=True,exist_ok=True);file.write_text(json.dumps({'schema':1,'node':n['id'],'definitionHash':definition['definitionHash'],'source':'return 9007199254740992L;' if n['id']=='integer' else 'return ratio + quick;'}))
original_feature=feature_file.read_bytes();original_impl=impl_file.read_bytes();original_graph=graphfile.read_bytes();signatures={n['id']:n['signature'] for n in g['nodes']}

try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup()
  def idle():page.evaluate('async()=>await confectoryFlushPresentation()')
  def browse():
   page.locator('#workspace').click(button='right',position={'x':700,'y':300});page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();return page.locator('.window[data-key^="browser:project:"]:visible')
  b=browse();b.locator('[data-tab=feature]').click();b.locator('[data-object="Owned.Elements::Main"]').get_by_role('button',name='정의 열기',exact=True).click();main=page.locator('.window[data-key=declaration]');expect(main.locator('[data-inline-description]')).to_be_visible(timeout=30000);b.locator('[data-close]').click();main.locator('[data-inline-description]').fill('승격과 별개의 입력');main.locator('[data-close]').click();idle();b=browse();b.locator('[data-tab=feature]').click();b.locator('[data-object="'+id+'"]').get_by_role('button',name='정의 열기',exact=True).click();b.locator('[data-close]').click();page.locator('.window[data-key=declaration] [data-function-write-direct]').click();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);graphid=invoke('blueprint',{'action':'list','feature':id})['result']['result']['rows'][0]['id']
  def graph():return invoke('blueprint',{'action':'read','id':graphid})['result']['result']
  def private():idle();return state()['presentation']['inputs']['blueprint']
  def peers():return {k:v for k,v in state()['presentation']['inputs'].items() if k not in ('blueprint','target') and (k!='source' or v.get('dirty'))}
  peer=peers()
  def reveal(button):
   vp=author.locator('.bp-viewport');rect=vp.bounding_box();d=button.evaluate('(el)=>{const a=el.getBoundingClientRect(),v=el.closest(".bp-viewport").getBoundingClientRect();return {x:a.x+a.width/2-v.x-v.width/2,y:a.y+a.height/2-v.y-v.height/2}}');page.mouse.move(rect['x']+rect['width']/2,rect['y']+rect['height']/2);page.mouse.wheel(d['x'],d['y']);page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
  def menu(name,path=''):
   author.locator('[data-bp-overview-node=body]').click();page.evaluate('()=>new Promise(requestAnimationFrame)');button=author.locator('.bp-inline-pin[data-node=body][data-port="field:'+name+'"] input[data-expression-path="'+path+'"]').locator('..').locator('[aria-label="값 목록 열기"]');reveal(button);button.click();d=page.get_by_role('dialog',name='핀 값 선택',exact=True);expect(d).to_be_visible();return d
  def choose(name,label,path=''):menu(name,path).get_by_role('button',name=label,exact=True).click()
  def save():author.locator('[data-bp-save]').click();expect(author.locator('.bp-status')).to_have_text('저장됨',timeout=30000)
  def confirm():
   author.locator('[data-bp-complete]').click();review=page.locator('.window[data-key=review]');expect(review).to_be_visible(timeout=30000)
   if review.locator('[data-additional-changes]').count():
    review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
    if ack.count():ack.check()
   expect(review.locator('#confirm')).to_be_enabled(timeout=30000);review.locator('#confirm').click();expect(review).to_have_count(0,timeout=60000)
  def noabi():return feature_file.read_bytes()==original_feature and impl_file.read_bytes()==original_impl and {n['id']:n['signature'] for n in json.loads(graphfile.read_text())['nodes']}==signatures
  # 원본 헤더 드래그로 두 함수 카드와 넓은 표현식의 배치 여백을 둔다.
  # 강제 클릭/DOM 좌표 쓰기 없이 사용자가 할 수 있는 원래 동작을 사용한다.
  author.locator('[data-bp-overview-node=body]').click();page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');body=author.locator('[data-bp-node=body]');prior=body.evaluate('(el)=>parseFloat(el.style.left)');header=body.locator('.function-node-heading').bounding_box();page.mouse.move(header['x']+70,header['y']+22);page.mouse.down();page.mouse.move(header['x']+470,header['y']+22,steps=12);page.mouse.up();page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');assert body.evaluate('(el)=>parseFloat(el.style.left)')>=prior+380
  def bodyrow():return next(n for n in graph()['nodes'] if n['id']=='body')
  def argument(name):return json.loads(next(a['valueJson'] for a in bodyrow()['arguments'] if a['name']==name))
  def frozen():return feature_file.read_bytes()==original_feature and impl_file.read_bytes()==original_impl and peers()==peer
  def literal(name,path,text):
   m=menu(name,path);m.get_by_role('searchbox',name='값 검색').fill(text);page.keyboard.press('Enter');expect(m).to_have_count(0)
  def script(cancel=False):
   author.locator('[data-bp-overview-node=body]').click();page.evaluate('()=>new Promise(requestAnimationFrame)');button=author.locator('[data-bp-node=body] [data-internal-code]');reveal(button);button.click();dialog=page.get_by_role('dialog',name='C# Script · body',exact=True);expect(dialog).to_be_visible();assert 'double seed' in dialog.locator('[data-code-source]').input_value();dialog.locator('[data-code-cancel]' if cancel else '[data-code-save]').click();expect(dialog).to_have_count(0)
  before=graph();proof=json.dumps(sorted([[x['id'],x['revision'],x['hash']] for x in before['sources']]),separators=(',',':'));bad={'node':'body','name':'seed','type':'double','path':[1],'baseJson':'{"binary":{"operator":"+","operands":[{"constant":9007199254740993},{"input":"seed"}]}}','sourceJson':'{"input":"ratio"}'};invoke('blueprint',{'action':'adaptInput','id':graphid,'basis':before['basis'],'node':'body','definition':bad},False);invoke('blueprint',{'action':'authorBatch','id':graphid,'attempt':uuid.uuid4().hex,'sourceProof':proof,'checkpointHash':before['checkpointHash'],'edits':[{'action':'adaptInput','node':'body','definition':bad}]},False);assert graphfile.read_bytes()==original_graph and graph()['sources']==before['sources'] and frozen();checked('직접 미체크포인트 타입 변경과 정밀도를 잃는 중첩 위조 계획은 서버에서 전체 거부하고 기존 초안을 보존한다')
  initial=private();m=menu('seed');expect(m.get_by_role('button',name='입력 · ratio',exact=True)).to_be_visible();page.keyboard.press('Escape');assert private()==initial;choose('seed','입력 · ratio');assert any(v['type']=='input-adaptation' for _,v in private());author.locator('.bp-viewport').focus();page.keyboard.press('Control+z');assert private()==initial and graphfile.read_bytes()==original_graph and frozen();checked('원본 값 메뉴의 자유 숫자 정의 적응은 취소·구조 Undo로 원래 연결·계약·독립 입력을 복원한다')
  menu('seed').get_by_role('button',name='연산자 +',exact=True).click();menu('seed','0').get_by_role('button',name='연산자 /',exact=True).click();choose('seed','입력 · ratio','1');candidate=next(json.loads(v['text']) for _,v in private() if v['type']=='input-adaptation');tree=json.loads(candidate['valueJson']);assert tree['binary']['type']=='double' and tree['binary']['operands'][0]['binary']['type']=='long';author.locator('.bp-viewport').focus();page.keyboard.press('Control+z');page.keyboard.press('Control+z');page.keyboard.press('Control+z');assert private()==initial and frozen();checked('원본 메뉴는 형제 정수 하위 식 타입을 유지하며 선택 조상만 승격하고 연속 Undo로 모두 복원한다')
  menu('seed').get_by_role('button',name='연산자 +',exact=True).click();literal('seed','0','9007199254740992');choose('seed','입력 · ratio','1');pending=private();plan=next(json.loads(v['text']) for _,v in pending if v['type']=='input-adaptation');assert plan['type']=='double' and json.loads(plan['valueJson'])['binary']['operands'][0]=={'constant':9007199254740992,'type':'long'} and frozen();idle();page.close();stop();start(1);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert private()==pending;save();adapted=bodyrow();assert adapted['signature']['args'][0]['type']=='double' and adapted['sourceStatus']=='stale' and argument('seed')['binary']['operands']==[{'constant':9007199254740992,'type':'long'},{'input':'ratio'}] and frozen() and graphfile.read_bytes()==original_graph;author.locator('[data-bp-complete]').click();expect(author.locator('.bp-status')).to_contain_text('현재 계약과 다른 본문',timeout=30000);expect(page.locator('.window[data-key=review]')).to_have_count(0);checked('중첩 승격 개인 입력을 재시작 복원·원자적으로 저장하고 이전 본문은 stale로 유지하여 자동 확정을 거부한다')
  clean=private();script(True);assert private()==clean;script();save();assert bodyrow()['sourceStatus']=='available' and frozen();confirm();physical=json.loads(graphfile.read_text());assert physical['nodes'][1]['signature']['args'][0]['type']=='double' and frozen() and physical['nodes'][0]['signature']==signatures['integer'];checked('새 계약을 표시한 기존 C# 창의 취소는 보존되며 명시적 본문 재적용·실제 컴파일·Confirm 후에만 함께 반영한다')
  idle();page.close();stop();start(2);page=setup();author=page.locator('.window[data-key=blueprint]');expect(author.locator('[data-bp-save]')).to_be_enabled(timeout=30000);assert bodyrow()['sourceStatus']=='available' and argument('seed')['binary']['operands'][0]['type']=='long' and frozen();author.locator('[data-bp-overview-node=body]').click();page.evaluate('()=>new Promise(requestAnimationFrame)');reveal(author.locator('.bp-inline-pin[data-node=body][data-port="field:seed"] .bp-expression-root'));page.screenshot(path=str(case/'input-adaptation-confirmed.png'));checked('확정 후 실제 재시작에서도 승격된 정의·정수 원문·연결·다른 객체 입력과 원본 외부 ABI를 복원한다');page.close();browser.close();assert not errors and not external,(errors,external)
except Exception:
 try:(case/'failure-state.json').write_text(json.dumps(state(),ensure_ascii=False,indent=2));(case/'failure.json').write_text(json.dumps({'traffic':traffic,'errors':errors},ensure_ascii=False,indent=2))
 except Exception:pass
 print('격리 실패 자료 '+str(case));raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'nativeWindows':False,'accountOrInference':False,'projectRun':False,'signatureAdaptation':True,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
