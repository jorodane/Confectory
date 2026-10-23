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
   for _ in range(6000):
    u=raw({'op':'update','view':v['view'],'scope':v['scope']});rows=[r for r in u.get('results',[]) if r['requestId']==rid]
    if rows:break
    if u.get('error',{}).get('code')=='scope_changed':
     observed=state()
     if endpoint=='projectHelpers' and observed['projectHelperIds']==body['helpers']:return {'observedAfterScopeChange':True,'state':observed}
     if endpoint=='closeProject' and not observed['projectId']:return {'observedAfterScopeChange':True,'state':observed}
     raise AssertionError(('unresolved_scope_change',endpoint,u))
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
  page.locator('#add-agent').click();c=page.get_by_role('dialog',name='Agent 추가',exact=True);c.get_by_role('button',name='OpenAI Responses',exact=True).click()
  for key,value in [('model','fixture-no-inference'),('endpoint','http://127.0.0.1:9'),('credentialReference','')]:c.locator('[data-connection-field="'+key+'"]').fill(value)
  c.locator('[data-agent-register]').click();expect(c.locator('[data-agent-registration-state]')).to_contain_text('Agent 등록됨');c.locator('[data-connection-cancel]').click()
  def create(name):
   page.locator('#add-helper').click();r=page.locator('[data-reference-version="536"]');r.locator('#participant-name').fill(name);r.locator('button[type=submit]').click();expect(r).to_have_count(0);return next(h['id'] for h in state()['helpers'] if h['presentation']['value']['name']==name)
  helper=create('보관할 도우미');other=create('남길 도우미');agent='Confectory.Agent.Responses::Connection';s=state();other_profile=next(h for h in s['helpers'] if h['id']==other)['presentation'];agents=s['helperAgents']['agents'];original_helpers=(storage/'helpers/helpers.json').read_bytes()
  def settings(id):
   page.locator('.home-side [data-helper="'+id+'"]').first.click();card=page.locator('.participant-expanded-card[data-helper-id="'+id+'"]');expect(card.locator('form')).to_be_visible();card.locator('.helper-window-settings').click();r=page.locator('[data-reference-version="536"]');expect(r.locator('[data-helper-delete]')).to_be_visible();return r
  r=settings(helper);r.locator('#participant-description').fill('저장하지 않은 설정 입력');r.locator('[data-helper-delete]').click();confirm=r.get_by_role('alertdialog',name='도우미 삭제 확인');expect(confirm).to_be_visible();expect(confirm).to_contain_text('대화·기억·채팅 입력은 보관');assert page.evaluate('document.querySelector("#app").inert');confirm.get_by_role('button',name='취소',exact=True).click();expect(confirm).to_have_count(0);expect(r.locator('#participant-description')).to_have_value('저장하지 않은 설정 입력');assert len(state()['helpers'])==2;r.locator('[data-close]').click();checked('원본 설정창 삭제 버튼과 중첩 확인/취소가 저장본·입력·다른 Helper·inert를 보존한다')
  # Ordinary server route, explicitly chosen fixture project and roster. No inference/account call.
  # The fixture project is opened by the ordinary startup path on the next cold start.
  # Seed known fixture-only local memories/history on cold storage; no real credentials or provider.
  page.close();stop();helpers_doc=json.loads((storage/'helpers/helpers.json').read_text());helpers_doc['helpers'][helper]['memory'].append({'memoryID':'fixture-private','text':'보관할 비공개 기억','scope':'common','projectId':''});(storage/'helpers/helpers.json').write_text(json.dumps(helpers_doc,ensure_ascii=False));original_helpers=(storage/'helpers/helpers.json').read_bytes()
  import hashlib
  journal=storage/'helper-conversations'/(hashlib.sha256(helper.encode()).hexdigest()+'.json');journal.parent.mkdir(exist_ok=True);journal.write_text(json.dumps({'version':1,'helper':helper,'conversationId':uuid.uuid4().hex,'records':[{'requestId':uuid.uuid4().hex,'agent':agent,'message':'fixture 이전 질문','output':'fixture 이전 응답','state':'completed'}]},ensure_ascii=False));journal_bytes=journal.read_bytes()
  env['CONFECTORY_WEB_PROJECT']=str(project/'project.cproj');start(1);page=setup();s=state();project_id=s['projectId'];invoke('projectHelpers',{'helpers':[helper,other]});s=state();assert s['mainHelperId']==helper and s['projectHelperIds']==[helper,other];page.reload();goto_editor(page,url);r=settings(helper);r.locator('[data-helper-delete]').click();confirm=r.get_by_role('alertdialog',name='도우미 삭제 확인');expect(confirm).to_be_visible()
  plan_calls=[t['invoke'] for t in traffic if t.get('invoke',{}).get('endpoint')=='helperGlobal' and t['invoke'].get('input',{}).get('action')=='archive-plan'];assert plan_calls
  before=(storage/'helper-agents.json').read_bytes();invoke('helperGlobal',{'action':'archive','helper':helper,'token':'0'*32},False);assert (storage/'helper-agents.json').read_bytes()==before;checked('위조 삭제 토큰을 서버가 거부하고 계정/배치/원본을 변경하지 않는다')
  # The deliberately invalid request does not consume the genuine in-memory plan.
  confirm.get_by_role('button',name='삭제',exact=True).click();expect(r).to_have_count(0);expect(page.locator('.home-side [data-helper="'+helper+'"]')).to_have_count(0);expect(page.locator('.participant-expanded-card[data-helper-id="'+helper+'"]')).to_have_count(0);assert not page.evaluate('document.querySelector("#app").inert');s=state();assert s['mainHelperId']==other and s['projectHelperIds']==[other];assert helper not in s['helperAgents']['assignments'];assert any(h['helper']==helper for h in s['retainedHelpers']);assert (storage/'helpers/helpers.json').read_bytes()==original_helpers and journal.read_bytes()==journal_bytes;assert next(h for h in s['helpers'] if h['id']==other)['presentation']==other_profile;assert s['helperAgents']['agents']==agents;receipt=json.loads(next((storage/'helper-archives').glob('*.json')).read_text());assert receipt['helper']==helper and receipt['placements'][project_id]['helpers']==[helper,other];checked('실제 삭제는 여러 Helper 배치의 해당 항목만 원자적으로 해제하고 대화·기억·프로필·복구기록·다른 Helper·Agent를 보존한다')
  invoke('helperGlobal',{'action':'prepare','helper':helper,'message':'실행되어서는 안 됨'},False);invoke('selectHelperConversation',{'helper':helper},False);assert journal.read_bytes()==journal_bytes;checked('삭제된 Helper의 전역 요청과 프로젝트 대화 선택을 서버가 차단한다; 모델 호출 없음')
  page.close();stop();start(2);page=setup();s=state();assert not any(h['id']==helper for h in s['helpers']);assert any(h['helper']==helper for h in s['retainedHelpers']);assert (storage/'helpers/helpers.json').read_bytes()==original_helpers and journal.read_bytes()==journal_bytes
  # Restore via the existing explicit import surface, no automatic placement/grant restoration.
  page.locator('.brand').click();page.wait_for_selector('.home-grid');page.locator('#add-helper').click();r=page.locator('[data-reference-version="536"]');r.locator('[data-helper-import]').click();imp=page.get_by_role('dialog',name='Helper 가져오기',exact=True);imp.locator('[data-import-helper="'+helper+'"]').click();expect(imp).to_have_count(0);s=state();assert s['helperAgents']['assignments'][helper]==agent;page.locator('[data-enter]').first.click();page.wait_for_selector('.work-body');s=state();assert s['projectHelperIds']==[other] and s['mainHelperId']==other;assert (storage/'helpers/helpers.json').read_bytes()==original_helpers and journal.read_bytes()==journal_bytes;checked('실제 프로세스 재시작 후 삭제 상태를 유지하고 기존 가져오기로 대화·기억을 복구하되 프로젝트 배치·권한을 자동 복구하지 않는다')
  page.locator('.brand').click();page.wait_for_selector('.home-grid');r=settings(helper);r.locator('[data-helper-delete]').click();confirm=r.get_by_role('alertdialog',name='도우미 삭제 확인');expect(confirm).to_be_visible();page.screenshot(path=str(case/'helper-delete-desktop.png'));page.set_viewport_size({'width':600,'height':800});expect(confirm.get_by_role('button',name='취소',exact=True)).to_be_visible();page.screenshot(path=str(case/'helper-delete-600.png'));confirm.press('Escape');expect(confirm).to_have_count(0);expect(r).to_be_visible();r.locator('[data-close]').click();assert not page.evaluate('document.querySelector("#app").inert');checked('600 너비 삭제 확인의 취소·Escape·포커스/모달 정리가 작동한다')
  page.set_viewport_size({'width':1280,'height':900});a=invoke('helperGlobal',{'action':'archive-plan','helper':other})['result']['result'];b=invoke('helperGlobal',{'action':'archive-plan','helper':other})['result']['result'];assert a['token']!=b['token'];invoke('helperGlobal',{'action':'archive','helper':other,'token':a['token']},False);assert state()['helperAgents']['assignments'][other]==agent;assert journal.read_bytes()==journal_bytes;checked('새 검토 이후 오래된 삭제 토큰은 거부하며 다른 Helper의 소속·기록을 보존한다')
  assert not [t for t in traffic if t.get('invoke',{}).get('endpoint') in ['startAI','startGlobalHelperAi']];page.close();browser.close();assert not errors and not external,(errors,external)
except Exception:
 try:(case/'failure-state.json').write_text(json.dumps(state(),ensure_ascii=False,indent=2));page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 print('격리 실패 자료 '+str(case),flush=True);raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'referenceVersion':536,'nativeWindows':False,'accountOrInference':False,'actualScopedGrant':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
