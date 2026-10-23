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
traffic=[];injected=0;fail_read_id=None;read_failures=0

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
 global injected,read_failures
 if not request.request.url.startswith(origin):external.append(request.request.url);request.abort();return
 body=request.request.post_data_json if request.request.method=='POST' else None
 if isinstance(body,dict) and body.get('op')=='invoke' and body.get('endpoint')=='reviewDraft' and False:
  # Actual server rejects an explicitly stale transport revision before execution.
  injected+=1;body['expectedRevision']-=1;request.continue_(post_data=json.dumps(body));return
 if isinstance(body,dict) and body.get('op')=='invoke' and body.get('endpoint')=='battleLog' and body.get('input',{}).get('action')=='read' and body.get('input',{}).get('id')==fail_read_id and read_failures<3:
  read_failures+=1;body['expectedRevision']-=1;request.continue_(post_data=json.dumps(body));return
 request.continue_()

def setup():
 page=browser.new_page(viewport={'width':1280,'height':900});page.add_init_script("""window.__battleLifecycle=[];window.confectoryWebUITrace=[];const html=Object.getOwnPropertyDescriptor(Element.prototype,'innerHTML');Object.defineProperty(Element.prototype,'innerHTML',{get:html.get,set(value){if(this.id==='app'&&this.querySelector('[data-key=conflict-log]'))window.__battleLifecycle.push({kind:'app-replace',stack:new Error().stack});return html.set.call(this,value);}});""");page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',observe);page.route('**/*',route);goto_editor(page,url);return page

def settled():
 expect(w.locator('[data-feature-action=save]')).to_be_enabled(timeout=30000)
 for _ in range(600):
  s=state();d=s.get('declaration')
  if d and d['id']==id and d['revision']==s['draft']['revision']:return s
  page.wait_for_timeout(20)
 raise AssertionError('feature inspect did not settle')

def sdk(op,**data):
 p=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':op,**data}),text=True,capture_output=True,check=True,env=env);v=json.loads(p.stdout);assert v['ok'],v;return v['result']


try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);start(0);page=setup();project_id=state()['projectId'];agent='Confectory.Agent.Responses::Connection'
  def close_window(key):
   tab=page.locator('[data-window-tab-close="'+key+'"]')
   if tab.is_visible():tab.click()
   else:page.locator('.window[data-key="'+key+'"] >.window-title [data-close]').click()
   if key=='conflict-detail' and page.locator('[data-window-tab="conflict-log"]').count():page.locator('[data-window-tab="conflict-log"]').click()
  def log_window():
   page.locator('#conflict-log').click();w=page.locator('.window[data-key="conflict-log"]')
   try:expect(w.locator('.conflict-log-list')).to_be_visible(timeout=15000)
   except Exception:
    (case/'live-failure.json').write_text(json.dumps(page.evaluate('''()=>({events:window.__battleLifecycle,trace:window.confectoryWebUITrace,windows:[...document.querySelectorAll('.window')].map(w=>({key:w.dataset.key,hidden:w.hidden,text:w.innerText})),toast:document.querySelector('#toast')?.textContent})'''),ensure_ascii=False,indent=2));(case/'live-traffic.json').write_text(json.dumps(traffic,ensure_ascii=False,indent=2));(case/'live-errors.json').write_text(json.dumps(errors));raise
   return w
  w=log_window();expect(w).to_contain_text('진행 중인 기록이 없어요.');assert not (project/'.confectory/ai-development').exists();close_window('conflict-log');checked('빈 프로젝트에서 원본 전투 로그·필터·빈 상태를 표시하며 Task/Agent/작업 저장소를 만들지 않는다')
  page.locator('#add-agent').click();c=page.get_by_role('dialog',name='Agent 추가',exact=True);c.get_by_role('button',name='OpenAI Responses',exact=True).click()
  for key,value in [('model','fixture-no-inference'),('endpoint','http://127.0.0.1:9'),('credentialReference','')]:c.locator('[data-connection-field="'+key+'"]').fill(value)
  c.locator('[data-agent-register]').click();expect(c.locator('[data-agent-registration-state]')).to_contain_text('Agent 등록됨');c.locator('[data-connection-cancel]').click()
  def recruit(name):return invoke('helperGlobal',{'action':'create','creationId':uuid.uuid4().hex,'name':name,'personality':'fixture local profile','speciality':'fixture','agent':agent})['result']['result']['helper']
  chief=recruit('기록 도우미');bad=recruit('잘못된 저장소 도우미');link=recruit('링크 확인 도우미');invoke('projectHelpers',{'helpers':[chief]});page.close();stop();import hashlib
  base=project/'.confectory/ai-development';directory=base/'helpers'/hashlib.sha256(chief.encode()).hexdigest()[:16];directory.mkdir(parents=True);tasks={};journal=[];worker_ids={};titles={'ready':'검토를 기다리는 작업','completed':'소스 검증을 마친 작업','running':'재시작 상태를 확인할 작업'}
  for n,(status,title) in enumerate(titles.items()):
   tid='fixture-'+status;worker=uuid.uuid4().hex;worker_ids[status]=worker;tasks[tid]={'task':tid,'worker':worker,'ownerHelper':chief,'project':project_id,'status':status,'specification':{'goal':title,'stage':'fixture stage','completion':'fixture acceptance','rationale':'RAW-REQUEST-CANARY','privateRequest':'TOKEN-CANARY'},'progress':'PRIVATE-PROGRESS-CANARY','checkpoint':'PRIVATE-CHECKPOINT-CANARY'};journal.extend([{'sequence':n*2+1,'kind':'chief-assigned','task':tid,'detail':'SECRET-DETAIL-CANARY','actor':chief,'project':project_id},{'sequence':n*2+2,'kind':'worker-started' if status=='running' else 'worker-completed' if status=='completed' else 'checkpoint','task':tid,'detail':'SECRET-DETAIL-CANARY','actor':chief,'project':project_id}])
  tasks['foreign']={'task':'foreign','worker':uuid.uuid4().hex,'ownerHelper':'not-owned-helper','project':project_id,'status':'ready','specification':{'goal':'FOREIGN-HELPER-CANARY'}}
  document={'schema':1,'project':project_id,'owner':'local-user','chief':chief,'tasks':tasks,'journal':journal,'chiefJournal':[],'commands':{},'leases':{}};task_path=directory/'tasks.json';task_path.write_text(json.dumps(document,ensure_ascii=False));development=directory/'development-log.json';development.write_text(json.dumps([{'projectId':project_id,'task':'fixture-completed','worker':worker_ids['completed'],'status':'completed-with-source-verification','compilerStatus':'passed','timestamp':'2026-10-23T00:00:00Z','goalEvidence':'PRIVATE-EVIDENCE-CANARY'}]));stored={task_path:task_path.read_bytes(),development:development.read_bytes()}
  bad_dir=base/'helpers'/hashlib.sha256(bad.encode()).hexdigest()[:16];bad_dir.mkdir();(bad_dir/'tasks.json').write_text(json.dumps({**document,'chief':bad,'project':'foreign-project','tasks':{'foreign':{'goal':'OTHER-PROJECT-CANARY'}}}));outside=case/'outside-task.json';outside.write_text(json.dumps({**document,'chief':link}));link_dir=base/'helpers'/hashlib.sha256(link.encode()).hexdigest()[:16];link_dir.mkdir();(link_dir/'tasks.json').symlink_to(outside)
  start(1);page=setup();page.locator('#chat-input').fill('로그를 보는 동안 보존할 입력');w=log_window();expect(w.locator('[data-open-conflict]')).to_have_count(3);expect(w).to_contain_text('현재 상태 확인 필요');expect(w).to_contain_text('일부 저장 기록을 읽지 못했어요.');data=invoke('battleLog',{'action':'list'})['result']['result'];assert data['total']==3 and data['discussionSupported'] is False;public=json.dumps(data,ensure_ascii=False);assert not any(word in public for word in ['CANARY','privateRequest','executionKey','checkpoint']);assert 'task-scope-unavailable' in data['warnings'];assert all(f.read_bytes()==v for f,v in stored.items());checked('저장 작업만 조회하고 다른 Helper/프로젝트·링크를 제외하며 원문 요청/진행 내용과 가짜 협의를 노출하지 않는다')
  ids={row['title']:row['id'] for row in data['records']};fail_read_id=ids[titles['ready']];w.locator('[data-open-conflict="'+fail_read_id+'"]').click();failed=page.locator('.window[data-key="conflict-detail"]');expect(failed.locator('[data-battle-retry]')).to_be_visible();expect(failed).to_contain_text('기록을 읽지 못했어요.');assert read_failures==3;expect(w.locator('[data-open-conflict="'+fail_read_id+'"]')).to_have_attribute('aria-label',titles['ready']);fail_read_id=None;failed.locator('[data-battle-retry]').click();expect(failed.locator('.conflict-discussion-messages')).to_be_visible();expect(w.locator('[data-open-conflict="'+ids[titles['ready']]+'"]')).to_have_attribute('aria-label',titles['ready']+' · 읽음');close_window('conflict-detail');checked('실패한 상세 조회는 읽음으로 표시하지 않으며 제한 재시도 후 명시적 다시 읽기가 정상 복구한다');running=ids[titles['running']];finished=ids[titles['completed']];w.locator('[data-conflict-filter="history"]').click();expect(w.locator('[data-open-conflict]')).to_have_count(1);w.locator('[data-open-conflict="'+finished+'"]').click();d=page.locator('.window[data-key="conflict-detail"]');expect(d.locator('.conflict-discussion-messages')).to_be_visible();expect(d).to_contain_text('작업 완료를 검증했어요.');expect(d).to_contain_text('협의 결과나 새 Confirm 승인이 아닙니다.');expect(d.locator('textarea')).to_have_count(0);assert not any(word in d.inner_text() for word in ['CANARY','승자가','합의했']);expect(page.locator('#chat-input')).to_have_value('로그를 보는 동안 보존할 입력');read=invoke('battleLog',{'action':'read','id':finished})['result']['result'];assert not any(word in json.dumps(read) for word in ['CANARY','goalEvidence','request']);checked('원본 목록·상세에서 필터/실제 이벤트/채택 검증을 읽기만 하며 기존 입력과 권한을 보존한다')
  close_window('conflict-detail');w.locator('[data-conflict-filter="all"]').click();expect(w.locator('[data-open-conflict="'+finished+'"]')).to_have_attribute('aria-label',titles['completed']+' · 읽음');close_window('conflict-log');w=log_window();expect(w.locator('[data-open-conflict="'+finished+'"]')).to_have_attribute('aria-label',titles['completed']+' · 읽음');w.locator('[data-open-conflict="'+running+'"]').click();d=page.locator('.window[data-key="conflict-detail"]');expect(d).to_contain_text('현재 상태 확인 필요');expect(d).to_contain_text('Worker 실행을 시작했어요.');assert all(f.read_bytes()==v for f,v in stored.items());checked('닫기/재진입은 읽은 기록과 선택을 보존하고 stored running을 재개하거나 Task 상태를 쓰지 않는다')
  page.screenshot(path=str(case/'battle-log-desktop.png'));page.evaluate('async()=>await confectoryFlushPresentation()');page.close();stop();start(2);page=setup();w=page.locator('.window[data-key="conflict-log"]');expect(w.locator('[data-open-conflict="'+finished+'"]')).to_have_attribute('aria-label',titles['completed']+' · 읽음',timeout=30000);d=page.locator('.window[data-key="conflict-detail"]');expect(d).to_contain_text('현재 상태 확인 필요',timeout=30000);expect(page.locator('#chat-input')).to_have_value('로그를 보는 동안 보존할 입력');assert all(f.read_bytes()==v for f,v in stored.items());checked('실제 프로세스 재시작에서 목록/상세/읽음/채팅 입력을 복원하며 저널 바이트를 보존한다')
  invoke('battleLog',{'action':'read','id':finished,'path':str(outside)},False);invoke('battleLog',{'action':'send','id':finished},False);checked('임의 경로/협의 전송 같은 위조 요청을 서버에서 차단한다')
  page.close();stop();other=case/'same-name project';shutil.copytree(project,other,ignore=shutil.ignore_patterns('.confectory','.build'));env['CONFECTORY_WEB_PROJECT']=str(other/'project.cproj');start(3);page=setup();assert state()['projectId']!=project_id;w=log_window();expect(w.locator('[data-open-conflict]')).to_have_count(0);invoke('battleLog',{'action':'read','id':finished},False);expect(page.locator('#chat-input')).not_to_have_value('로그를 보는 동안 보존할 입력');assert all(f.read_bytes()==v for f,v in stored.items());checked('같은 이름의 다른 프로젝트에서 이전 기록/입력을 표시하거나 record id로 읽지 못한다')
  page.set_viewport_size({'width':390,'height':844});page.locator('[data-mobile-more]').click();page.locator('.context-menu').get_by_role('button',name='전투 로그',exact=True).click();expect(page.locator('.conflict-log-list').first).to_be_visible();panel=page.locator('.window[data-key="conflict-log"]');expect(panel).to_have_class(__import__('re').compile(r'window-document'));box=panel.bounding_box();assert box['x']>=-1 and box['x']+box['width']<=391 and box['y']>=-1 and box['y']+box['height']<=845,box;assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(case/'battle-log-mobile.png'))
  assert not errors and not external,(errors,external);page.close();browser.close()
except Exception:
 try:(case/'failure-state.json').write_text(json.dumps(state(),ensure_ascii=False,indent=2));page.screenshot(path=str(case/'failure.png'))
 except Exception:pass
 try:(case/'failure-traffic.json').write_text(json.dumps(traffic,ensure_ascii=False,indent=2));(case/'failure-lifecycle.json').write_text(json.dumps(page.evaluate('({events:window.__battleLifecycle,windows:[...document.querySelectorAll(\'.window\')].map(w=>({key:w.dataset.key,hidden:w.hidden,text:w.innerText}))})'),ensure_ascii=False,indent=2));(case/'failure-errors.json').write_text(json.dumps(errors))
 except Exception:pass
 print('격리 실패 자료 '+str(case),flush=True);raise
finally:stop()
record={'checks':checks,'errors':errors,'external':external,'actualEngine':True,'referenceVersion':536,'nativeWindows':False,'liveWorkerOrInference':False,'actualScopedGrant':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
