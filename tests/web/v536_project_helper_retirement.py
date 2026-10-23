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

# Every injected memory, helper and account-less Agent below belongs to this temporary profile.
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();project_id=state()['projectId'];listing=state()['listingId'];agent='Confectory.Agent.Responses::Connection'
  page.locator('#add-agent').click();c=page.get_by_role('dialog',name='Agent 추가',exact=True);c.get_by_role('button',name='OpenAI Responses',exact=True).click()
  for key,value in [('model','fixture-no-inference'),('endpoint','http://127.0.0.1:9'),('credentialReference','')]:c.locator('[data-connection-field="'+key+'"]').fill(value)
  c.locator('[data-agent-register]').click();expect(c.locator('[data-agent-registration-state]')).to_contain_text('Agent 등록됨');c.locator('[data-connection-cancel]').click();other=invoke('helperGlobal',{'action':'create','creationId':uuid.uuid4().hex,'name':'남길 전역 도우미','personality':'fixture only','speciality':'fixture','agent':agent})['result']['result']['helper'];invoke('projectHelpers',{'helpers':[other]});page.close();stop()
  helper='fixture-project-helper';membership={'kind':'project','projectId':project_id};doc=json.loads((storage/'helpers/helpers.json').read_text());doc['helpers'][helper]={'template':json.dumps({'helper':helper,'owner':'local-user','personality':'프로젝트 전용 원본 성격','speciality':'원본 역할','membership':membership},ensure_ascii=False),'membership':membership,'memory':[{'memoryID':'kept','scope':'project','projectId':project_id,'text':'fixture 프로젝트 기억'}]};(storage/'helpers/helpers.json').write_text(json.dumps(doc,ensure_ascii=False));memory_bytes=(storage/'helpers/helpers.json').read_bytes();registry=storage/'helper-agents.json';reg=json.loads(registry.read_text());reg['assignments'][helper]=agent;registry.write_text(json.dumps(reg));selections=storage/'helper-selections.json';rosters=json.loads(selections.read_text());rosters[project_id]['helper']=helper;rosters[project_id]['helpers']=[helper,other];selections.write_text(json.dumps(rosters));import hashlib;profile=storage/'helper-presentations'/(hashlib.sha256(helper.encode()).hexdigest()+'.json');profile.parent.mkdir(exist_ok=True);profile.write_text(json.dumps({'version':1,'helper':helper,'name':'프로젝트 보관 도우미','shortDescription':'전용 역할','description':'전용 설명','globalDraft':''},ensure_ascii=False));profile_bytes=profile.read_bytes()
  def settings():
   page.locator('.home-side [data-helper="'+helper+'"]').click();card=page.locator('.participant-expanded-card[data-helper-id="'+helper+'"]');expect(card.locator('form')).to_be_visible();card.locator('.helper-window-settings').click();r=page.locator('[data-reference-version="536"]');expect(r.locator('[data-helper-delete]')).to_be_enabled();return r
  def deleting():
   r=settings();r.locator('[data-helper-delete]').click();d=r.get_by_role('alertdialog',name='도우미 삭제 확인');expect(d).to_be_visible();return r,d
  start(1);page=setup();r,d=deleting();r.locator('#participant-description').fill('삭제 실패 때 보존할 입력');d.get_by_role('button',name='취소',exact=True).click();expect(r.locator('#participant-description')).to_have_value('삭제 실패 때 보존할 입력');r.locator('[data-helper-delete]').click();d=r.get_by_role('alertdialog',name='도우미 삭제 확인');expect(d).to_be_visible();before_selections=selections.read_bytes();external_registry=registry.read_bytes()+b'\n';registry.write_bytes(external_registry);d.get_by_role('button',name='삭제',exact=True).click();expect(page.locator('#toast')).to_contain_text('도우미를 삭제하지 못했어요.',timeout=30000);expect(r).to_be_visible();expect(r.locator('#participant-description')).to_have_value('삭제 실패 때 보존할 입력');assert registry.read_bytes()==external_registry and selections.read_bytes()==before_selections and not (storage/'helper-archives').exists();assert (storage/'helpers/helpers.json').read_bytes()==memory_bytes and profile.read_bytes()==profile_bytes;checked('프로젝트 전용 삭제 취소와 실제 디스크 CAS 충돌은 입력·외부 변경·전체 배치를 보존하며 부분 삭제하지 않는다')
  page.close();stop();start(2);page=setup();r,d=deleting();d.get_by_role('button',name='삭제',exact=True).click();expect(r).to_have_count(0);expect(page.locator('.home-side [data-helper="'+helper+'"]').first).to_have_count(0);s=state();assert s['projectHelperIds']==[other] and s['mainHelperId']==other and helper not in s['helperAgents']['assignments'];assert any(h['helper']==helper and h['membership']['projectId']==project_id for h in s['retainedHelpers']);receipt=json.loads((storage/'helper-archives'/(hashlib.sha256(helper.encode()).hexdigest()+'.json')).read_text());assert receipt['project']==project_id and receipt['placements'][project_id]['helpers']==[helper,other];baseline={str(f.relative_to(storage)):f.read_bytes() for f in [registry,selections,profile,storage/'helpers/helpers.json']};reply=invoke('helperGlobal',{'action':'archive-status','helper':helper,'token':receipt['operationId']})['result']['result'];assert reply['retained'];reply=invoke('helperGlobal',{'action':'archive','helper':helper,'token':receipt['operationId']})['result']['result'];assert reply['retained'];assert all((storage/f).read_bytes()==b for f,b in baseline.items());checked('충돌 후 cold 재시작·새 검토의 명시적 삭제가 성공하며 동일 토큰 상태조회/재요청은 중복 반영하지 않는다')
  def placement():
   page.locator('#add-helper').click();r=page.get_by_role('dialog',name='프로젝트 도우미 배치',exact=True);expect(r.locator('[data-project-helper="'+helper+'"][data-selected="false"]')).to_be_visible();return r
  r=placement();r.locator('[data-project-helper="'+helper+'"]').click();restore=page.locator('[data-reference-version="536"]');expect(restore.get_by_role('button',name='복구',exact=True)).to_be_visible();expect(restore.locator('#participant-name')).to_have_value('프로젝트 보관 도우미');expect(restore.locator('.helper-agent-dropdown summary')).to_contain_text('Responses');restore.locator('[data-close]').click();assert helper not in state()['helperAgents']['assignments'];r=placement();r.locator('[data-project-helper="'+helper+'"]').click();restore=page.locator('[data-reference-version="536"]');restore.get_by_role('button',name='복구',exact=True).click();r=page.get_by_role('dialog',name='프로젝트 도우미 배치',exact=True);expect(r).to_be_visible();expect(r.locator('#project-helper-roster [data-project-helper="'+helper+'"]')).to_be_visible();s=state();assert s['helperAgents']['assignments'][helper]==agent and s['projectHelperIds']==[other];r.locator('[data-project-cancel]').click();assert state()['projectHelperIds']==[other];checked('기존 배치 후보→원본 공용 설정창에서 Agent를 확인해 복구하며 취소와 복구만으로 프로젝트 권한/배치를 만들지 않는다')
  page.locator('#add-helper').click();r=page.get_by_role('dialog',name='프로젝트 도우미 배치',exact=True);r.locator('button[type=submit]').click();expect(r).to_have_count(0);s=state();assert s['projectHelperIds']==[other,helper] and s['mainHelperId']==other;assert (storage/'helpers/helpers.json').read_bytes()==memory_bytes and profile.read_bytes()==profile_bytes;checked('복구한 도우미는 별도의 명시적 배치 적용 후에만 참여하며 모집·기억·프로필·다른 Helper를 보존한다')
  r,d=deleting();page.screenshot(path=str(case/'project-helper-delete.png'));d.get_by_role('button',name='삭제',exact=True).click();expect(r).to_have_count(0);assert state()['helperProfile']['helper']==other;page.locator('.brand').click();page.wait_for_selector('.home-grid');s=state();assert all(h['helper']!=helper for h in s['retainedHelpers']);invoke('helperGlobal',{'action':'import','helper':helper,'agent':agent},False);invoke('helperGlobal',{'action':'archive-plan','helper':helper},False);checked('프로젝트를 나가면 전용 보관 Helper를 전역 목록/가져오기로 노출하지 않고 서버도 복구/삭제를 거부한다')
  page.close();stop();other_project=case/'same-name project';shutil.copytree(project,other_project,ignore=shutil.ignore_patterns('.confectory','.build'));env['CONFECTORY_WEB_PROJECT']=str(other_project/'project.cproj');start(3);page=setup();s=state();assert s['projectId']!=project_id and s['title']=='Owned.Elements';assert all(h['helper']!=helper for h in s['retainedHelpers']);invoke('helperGlobal',{'action':'import','helper':helper,'agent':agent},False);assert (storage/'helpers/helpers.json').read_bytes()==memory_bytes and helper not in state()['helperAgents']['assignments'];checked('같은 표시 이름의 다른 실제 프로젝트와 cold 재시작에서도 전용 Helper의 소유/복구 범위를 유지한다')
  page.close();stop();env['CONFECTORY_WEB_PROJECT']=str(project/'project.cproj');start(4);page=setup();r=placement();page.set_viewport_size({'width':600,'height':800});r.locator('[data-project-helper="'+helper+'"]').click();restore=page.locator('[data-reference-version="536"]');expect(restore.get_by_role('button',name='복구',exact=True)).to_be_visible();box=restore.bounding_box();assert box['x']>=0 and box['x']+box['width']<=601;page.screenshot(path=str(case/'project-helper-restore-600.png'));restore.locator('[data-close]').click();assert helper not in state()['helperAgents']['assignments'];assert (storage/'helpers/helpers.json').read_bytes()==memory_bytes and profile.read_bytes()==profile_bytes;checked('원래 프로젝트로 재시작하면 보관 후보가 복구되며 600 너비 원본 폼 취소·inert 정리가 유지된다')
  assert not errors and not external,(errors,external);assert not [t for t in traffic if t.get('invoke',{}).get('endpoint') in ['startAI','startGlobalHelperAi']];page.close();browser.close()
except Exception:
 try:(case/'failure-state.json').write_text(json.dumps(state(),ensure_ascii=False,indent=2));page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 print('격리 실패 자료 '+str(case),flush=True);raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'referenceVersion':536,'nativeWindows':False,'accountOrInference':False,'actualScopedGrant':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
