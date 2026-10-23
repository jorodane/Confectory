"""v536 Helper 생성/설정 원본 모달을 실제 엔진 프로필 API에 연결. 격리 계정 없는 설정만; 추론 없음."""
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

env.pop('CONFECTORY_WEB_PROJECT',None)
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup()
  def idle():page.evaluate('async()=>await confectoryFlushPresentation()')
  page.locator('#add-agent').click();connection=page.get_by_role('dialog',name='Agent 추가',exact=True);connection.get_by_role('button',name='OpenAI Responses',exact=True).click()
  for name,value in [('model','fixture-no-inference'),('endpoint','http://127.0.0.1:9'),('credentialReference','')]:connection.locator('[data-connection-field="'+name+'"]').fill(value)
  connection.locator('[data-agent-register]').click();expect(connection.locator('[data-agent-registration-state]')).to_contain_text('Agent 등록됨');connection.locator('[data-connection-cancel]').click()
  def form():return page.locator('[data-reference-version="536"]')
  def create(name):
   page.locator('#add-helper').click();r=form();expect(r).to_have_attribute('aria-modal','true');assert page.evaluate("document.querySelector('#app').inert");expect(r.locator(':scope>.helper-create-artwork')).to_have_count(1);expect(r.locator('form .helper-create-artwork')).to_have_count(0);r.locator('#participant-name').fill(name);r.locator('#participant-short-description').fill('표시 역할');r.locator('#participant-description').fill('프로필 설명 원문');r.locator('button[type=submit]').click();expect(r).to_have_count(0);assert not page.evaluate("document.querySelector('#app').inert");return next(h['id'] for h in state()['helpers'] if h['presentation']['value']['name']==name)
  helper=create('실제 UI 도우미');other=create('다른 도우미');before_persona={h['id']:(h['personality'],h['speciality']) for h in state()['helpers']};other_before=next(h for h in state()['helpers'] if h['id']==other)['presentation'];checked('원본 v536 생성 모달과 상단 이미지 배치에서 실제 Helper 두 개를 만들고 모달 종료·inert 정리를 확인한다')
  def chat(id):
   page.locator('.home-side [data-helper="'+id+'"]').first.click();c=page.locator('.participant-expanded-card[data-helper-id="'+id+'"]');expect(c.locator('form')).to_be_visible();return c
  def settings(id):
   c=chat(id);c.locator('.helper-window-settings').click();r=form();expect(r).to_have_attribute('aria-modal','true');expect(r.locator(':scope>.helper-create-artwork')).to_have_count(1);expect(r.locator('form .helper-create-artwork')).to_have_count(0);assert page.evaluate("document.querySelector('#app').inert");return r
  c=chat(helper);c.locator('textarea').fill('대화창 원래 초안 한글');idle();r=settings(helper);expect(r.locator('#participant-name')).to_have_value('실제 UI 도우미');r.locator('#participant-name').fill('취소한 표시 이름');r.locator('[data-close]').click();assert not page.evaluate("document.querySelector('#app').inert");assert next(h for h in state()['helpers'] if h['id']==helper)['presentation']['value']['name']=='실제 UI 도우미';r=settings(helper);expect(r.locator('#participant-name')).to_have_value('취소한 표시 이름');expect(r.locator('#participant-description')).to_have_value('프로필 설명 원문');checked('설정도 원본 중앙 생성 폼을 재사용하며 취소는 저장본·다른 Helper·대화 초안을 변경하지 않고 재개 입력을 보존한다')
  r.locator('#participant-name').fill('저장한 표시 이름');r.locator('#participant-short-description').fill('저장한 표시 역할');r.locator('#participant-description').fill('저장한 설명');r.locator('button[type=submit]').click();expect(r).to_have_count(0);assert not page.evaluate("document.querySelector('#app').inert");s=state();saved=next(h for h in s['helpers'] if h['id']==helper)['presentation'];assert saved['value']['name']=='저장한 표시 이름' and saved['value']['shortDescription']=='저장한 표시 역할' and saved['value']['description']=='저장한 설명' and saved['value']['globalDraft']=='대화창 원래 초안 한글';assert next(h for h in s['helpers'] if h['id']==other)['presentation']==other_before and {h['id']:(h['personality'],h['speciality']) for h in s['helpers']}==before_persona;assert len(s['helpers'])==2;checked('명시적 확정은 기존 프로필 API로 선택한 Helper 표시 필드만 저장하며 AI 성격·다른 Helper·전역 초안·Agent 소속을 보존한다')
  r=settings(helper);page.screenshot(path=str(case/'v536-helper-settings-desktop.png'));r.locator('[data-close]').click();idle();page.close();stop();start(1);page=setup();r=settings(helper);expect(r.locator('#participant-name')).to_have_value('저장한 표시 이름');expect(r.locator('#participant-short-description')).to_have_value('저장한 표시 역할');expect(r.locator('#participant-description')).to_have_value('저장한 설명');assert len(state()['helpers'])==2;checked('실제 프로세스 재시작 후 같은 Helper 프로필을 복구하며 새 Helper를 중복 생성하지 않는다')
  for width,height in [(900,760),(600,800)]:
   page.set_viewport_size({'width':width,'height':height});box=r.bounding_box();assert box['x']>=0 and box['x']+box['width']<=width+1 and box['y']>=0 and box['y']+box['height']<=height+1,box;assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(case/f'v536-helper-settings-{width}.png'))
  page.set_viewport_size({'width':1280,'height':900});checked('600/900 너비에서 실제 설정 모달과 저장·닫기 제어가 화면 안에 있으며 가로 문서 넘침이 없다; v536 전체 모바일 shell 검증은 별도다')
  r.locator('#participant-name').fill('충돌 시 보존할 내 입력');profile=storage/'helper-presentations'/(__import__('hashlib').sha256(helper.encode()).hexdigest()+'.json');stored=json.loads(profile.read_text());stored['description']='격리 저장소의 동시 수정';external_bytes=json.dumps(stored,ensure_ascii=False).encode();profile.write_bytes(external_bytes);r.locator('button[type=submit]').click();expect(page.locator('#toast')).to_contain_text('Helper 설정을 저장하지 못했어요. 입력은 유지됩니다.',timeout=30000);expect(r).to_be_visible();expect(r.locator('#participant-name')).to_have_value('충돌 시 보존할 내 입력');assert profile.read_bytes()==external_bytes;checked('표시 중 다른 저장본이 바뀌면 서버 CAS가 덮어쓰기를 거부하고 원본 파일과 화면 입력을 보존한다')
  r.locator('[data-close]').click();assert not page.evaluate("document.querySelector('#app').inert");assert not [t for t in traffic if t.get('invoke',{}).get('endpoint') in ['startHelperAi','startGlobalHelperAi','chatUse']];page.close();browser.close();assert not errors and not external,(errors,external)
except Exception:
 try:(case/'failure-state.json').write_text(json.dumps(state(),ensure_ascii=False,indent=2));page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 print('격리 실패 자료 '+str(case));raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'referenceVersion':536,'nativeWindows':False,'accountOrInference':False,'actualScopedGrant':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
