"""Actual per-view process/control fixture. No account, grant, paid inference or user project."""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-run-followup-'))
projects=[]
for name in ['first','second']:
 p=root/name;shutil.copytree(repo/'examples/frame-loop',p,ignore=shutil.ignore_patterns('.confectory','.build'));m=p/'project.cpack';m.write_text(m.read_text().replace('../../',str(repo)+'/'));projects.append(m)
before={str(p):p.read_bytes() for m in projects for p in m.parent.rglob('*') if p.is_file()};env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(root/'profile'),CONFECTORY_ENTRY_STORAGE=str(root/'profile'),CONFECTORY_MCP_DIRECTORY=str(root/'instances'),CONFECTORY_WEB_PROJECT=str(projects[0]));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;stream=None;checks=[]
def checked(message):
 checks.append(message);(root/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2));print('PASS '+message,flush=True)
def stop():
 global host,stream
 if host and host.poll() is None:os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=15)
 if stream:stream.close()
def start(n):
 global host,stream,origin,token,url
 log=root/f'host-{n}.log';stream=log.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
 for _ in range(600):
  urls=[v.split(' ',1)[1] for v in log.read_text().splitlines() if v.startswith('CONFECTORY_WEB_UI ')]
  if urls:url=urls[-1];origin,token=url.split('/#');return
  assert host.poll() is None,log.read_text()[-2000:];time.sleep(.05)
 raise AssertionError('startup deadline')
def raw(body):return json.load(urllib.request.urlopen(urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token}),timeout=30))
def mount():
 for _ in range(500):
  v=raw({'op':'mount'})
  if v.get('ok'):return v
  assert v.get('error',{}).get('code')=='busy',v;time.sleep(.02)
 raise AssertionError('mount busy')
def state():
 v=mount()
 try:return v['state']
 finally:raw({'op':'dispose','view':v['view']})
def call(endpoint,body,ok=True):
 for attempt in range(4):
  v=mount();rid=uuid.uuid4().hex
  try:
   assert raw({'op':'invoke','view':v['view'],'scope':v['scope'],'expectedRevision':v['revision'],'requestId':rid,'endpoint':endpoint,'input':body})['ok']
   for _ in range(18000):
    u=raw({'op':'update','view':v['view'],'scope':v['scope']});rows=[r for r in u.get('results',[]) if r['requestId']==rid]
    if rows:break
    if u.get('error',{}).get('code')=='scope_changed':
     assert endpoint in ['openProject','leaveProject','closeProject'],(endpoint,u)
     return {'scopeChanged':True}
    time.sleep(.01)
   assert rows,(endpoint,u)
   r=rows[0]
   if r.get('error',{}).get('code')=='stale_revision':continue # refused before execution only
   assert bool(r.get('ok'))==ok,(endpoint,r)
   return r.get('result') if ok else r
  finally:raw({'op':'dispose','view':v['view']})
 raise AssertionError('admission changed')
def run(operation,row=None,ok=True,**values):return call('runWindow',{'operation':operation,**({'view':row['view'],'lease':row['lease'],'handle':row.get('handle','')} if row else {}),**values},ok)
def wait(row,condition,timeout=180):
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  s=run('read',row)
  if condition(s):return s
  time.sleep(.05)
 raise AssertionError(s)
def start_run(row):return run('start',row,target='portable',command=uuid.uuid4().hex)
def connected(row):return wait(row,lambda s:s['state']=='running' and s['control'].get('connected') and int(s['control']['frame'])>1)
def control(row,action,ok=True):
 c=row['control'];return run('control',row,ok,action=action,**{k:str(c[k]) for k in ['runtime','ack','sequence']})
errors=[];external=[];traffic=[];requests=[];page=None;deny_close=False
try:
 start(0)
 with sync_playwright() as p:
  from playwright.sync_api import expect
  import fcntl
  expect.set_options(timeout=30000)
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
  def route(r):
   if not r.request.url.startswith(origin+'/'):external.append(r.request.url);r.abort();return
   body=r.request.post_data_json if r.request.method=='POST' else None
   if isinstance(body,dict) and body.get('op')=='invoke':
    requests.append(body)
    if deny_close and body.get('endpoint')=='runWindow' and body.get('input',{}).get('operation')=='close':body['input']['lease']='f'*32;r.continue_(post_data=json.dumps(body));return
   r.continue_()
  def observe(response):
   try:
    request=response.request.post_data_json
    if isinstance(request,dict) and request.get('op')=='update':
     for row in response.json().get('results',[]):
      if row.get('ok') and isinstance(row.get('result'),dict) and 'lease' in row['result']:traffic.append(row['result'])
   except Exception:pass
  page.route('**/*',route);page.on('response',observe);goto_editor(page,url);page.locator('#run').click();w=page.locator('.run-window:visible');expect(w.locator('[data-run-play]')).to_be_enabled();key=w.get_attribute('data-key');w.locator('[data-run-play]').click();expect(w.locator('.caption strong')).to_have_text('실행 중',timeout=180000);expect(w.locator('[data-run-pause]')).to_be_enabled()
  def data(key):return [row for row in traffic if row['view']==key[13:]][-1]
  def open_run():
   page.get_by_role('tab',name='Workspace',exact=True).click();page.locator('#run').click();value=page.locator('.run-window:visible');expect(value.locator('[data-run-play]')).to_be_enabled();return value,value.get_attribute('data-key')
  def close_tab(key):page.locator('[data-window-tab-close="'+key+'"]').click()
  def project_close():
   page.locator('#title').click();page.get_by_role('button',name='프로젝트 완전 종료',exact=True).click()
  page.evaluate("""()=>{const base=fetch;const reads=new Set(),lost=new Set();globalThis.__holdRunRead=true;globalThis.fetch=async(...args)=>{let envelope;try{envelope=JSON.parse(args[1]?.body||'{}')}catch{}if(envelope?.op==='invoke'&&envelope.endpoint==='runWindow'){if(envelope.input?.operation==='read'&&__holdRunRead)reads.add(envelope.requestId);if(envelope.input?.operation==='start'&&globalThis.__loseRunStart){lost.add(envelope.requestId);__loseRunStart=false;}}const response=await base(...args);if(envelope?.op==='update'){const result=await response.clone().json();if(__holdRunRead&&result.results?.some(r=>reads.has(r.requestId))){globalThis.__heldRunRead=true;await new Promise(resolve=>globalThis.__releaseRunRead=()=>{__holdRunRead=false;resolve()});}let modified=false;for(const row of result.results||[])if(lost.delete(row.requestId)){row.ok=false;row.error={code:'request_failed'};delete row.result;modified=true;globalThis.__lostRunResult=true;}if(modified)return new Response(JSON.stringify(result),{status:200,headers:{'Content-Type':'application/json'}});}return response;};}""")
  page.wait_for_function('()=>globalThis.__heldRunRead===true');assert page.locator('#title').is_enabled(), 'Passive Run status read disabled normal project controls';page.locator('#chat-input').fill('상태 조회 중에도 보존할 새 입력');w.locator('[data-run-pause]').click();page.evaluate('()=>__releaseRunRead()');expect(w.locator('.caption strong')).to_have_text('일시 정지');expect(w.locator('[data-run-step]')).to_be_enabled();expect(page.locator('#chat-input')).to_have_value('상태 조회 중에도 보존할 새 입력');checked('대기 중인 상태조회가 일반 버튼/입력을 비활성화하지 않고 그 뒤 실제 Pause 명령을 잃지 않는다')
  owner=data(key);project_close();expect(page.locator('[data-keep-project]')).to_be_visible();assert run('read',owner)['state']=='running';page.locator('[data-keep-project]').click();expect(page.locator('.modal')).to_have_count(0);assert run('read',owner)['state']=='running';expect(page.locator('#chat-input')).to_have_value('상태 조회 중에도 보존할 새 입력');checked('새 실행창도 전체 종료 확인에 포함하며 취소는 실제 프로세스와 입력을 그대로 유지한다')
  deny_close=True;close_tab(key);expect(w.locator('[data-run-retry]')).to_be_visible();assert run('read',owner)['state']=='running';expect(w).to_be_visible();deny_close=False;w.locator('[data-run-retry]').click();expect(w.locator('[data-run-retry]')).to_be_hidden();close_tab(key);expect(w).to_be_hidden();assert run('read',owner)['closed'];checked('실제 서버가 닫기 권한을 거절하면 창/프로세스를 유지하고 다시 확인 후 명시적 닫기로 정상 정리한다')
  w,key=open_run();page.evaluate('()=>globalThis.__loseRunStart=true');n=len([r for r in requests if r['endpoint']=='runWindow' and r['input']['operation']=='start']);w.locator('[data-run-play]').click();expect(w.locator('[data-run-retry]')).to_be_visible();owner=data(key);assert owner['handle'];w.locator('[data-run-retry]').click();expect(w.locator('[data-run-retry]')).to_be_hidden();expect(w.locator('.caption strong')).to_have_text('실행 중',timeout=180000);assert data(key)['handle']==owner['handle'];assert len([r for r in requests if r['endpoint']=='runWindow' and r['input']['operation']=='start'])==n+1;close_tab(key);expect(w).to_be_hidden();checked('실제로 시작된 뒤 결과 전달이 실패해도 다시 확인은 기존 handle을 복구하고 실행을 재전송하지 않는다')
  w,key=open_run();source=projects[0].parent/'Main.celem';original=source.read_bytes();source.write_text('invalid isolated fixture declaration');w.locator('[data-run-play]').click();expect(w.locator('.caption strong')).to_have_text('실행 실패',timeout=180000);failed=data(key);source.write_bytes(original);w.locator('[data-run-play]').click();expect(w.locator('.caption strong')).to_have_text('실행 중',timeout=180000);assert data(key)['handle']!=failed['handle'];project_close();page.locator('[data-confirm-project-close]').click();expect(page.locator('.home-grid')).to_be_visible(timeout=60000);assert not state()['projectId'];checked('실제 컴파일 실패 후 명시적 재시도와 전체 종료 확정은 해당 프로젝트 실행만 정리한다')
  listing=state()['cards'][0]['id'];page.locator('[data-enter="'+listing+'"]').click();expect(page.locator('.work-body')).to_be_visible();w,key=open_run();lease=projects[0].parent/'.confectory/source-transaction.lock';lease.parent.mkdir(exist_ok=True)
  with lease.open('a+b') as held:
   fcntl.flock(held,fcntl.LOCK_EX);w.locator('[data-run-play]').click();expect(w.locator('.caption strong')).to_have_text('빌드 중');owner=data(key);close_tab(key);expect(w).to_be_hidden(timeout=30000);assert run('read',owner)['closed'];fcntl.flock(held,fcntl.LOCK_UN)
  checked('소스 잠금을 기다리는 실제 빌드 중 창 닫기가 owned process를 정리하며 자동 재실행하지 않는다')
  w,key=open_run();body=projects[0].parent/'Main.csbody';body_original=body.read_bytes();marker=root/'export-must-not-run';body.write_text('System.IO.File.AppendAllText('+json.dumps(str(marker))+',"run");\n'+body_original.decode());w.locator('[data-run-export]').click();page.get_by_role('button',name='Linux',exact=True).click();result=page.locator('.window[data-key="build-result"]');expect(result.locator('[data-export-state]')).to_have_text('빌드 완료',timeout=180000);expect(result.locator('[data-export-artifacts]')).to_contain_text('파일 일치 확인');expect(result.locator('h2')).to_have_text('Linux');assert not marker.exists();assert result.locator('.build-jobs,[data-build-start],[data-build-files]').count()==0;expect(page.locator('#chat-input')).to_have_value('상태 조회 중에도 보존할 새 입력');export_request=[r['input'] for r in requests if r['endpoint']=='startBuild'][-1];job=state()['buildJobs'][-1]['job'];same=call('startBuild',export_request);assert same['job']==job;call('startBuild',dict(export_request,target='windows'),False);assert not marker.exists();page.screenshot(path=str(root/'export-result.png'));checked('원본 결과창에서 실제 산출물 검증을 표시하고 프로젝트 실행/배포 없이 같은 요청을 중복 빌드하지 않는다')
  count=len([r for r in requests if r['endpoint']=='startBuild']);page.locator('[data-window-tab="'+key+'"]').click();w.locator('[data-run-export]').click();page.get_by_role('button',name='Android',exact=True).click();assert len([r for r in requests if r['endpoint']=='startBuild'])==count;expect(page.locator('#toast')).to_contain_text('선언되지');page.evaluate('()=>confectoryFlushPresentation()');page.reload();goto_editor(page,url);result=page.locator('.window[data-key="build-result"]');expect(result).to_have_count(0);assert call('buildInfo',{'job':job,'verify':True})['artifactState']=='verified';assert len([r for r in requests if r['endpoint']=='startBuild'])==count;body.write_bytes(body_original);checked('미선언 Android는 작업을 만들지 않으며 원본처럼 결과창은 재시작에 자동 복원하지 않고 산출물 기록을 보존한다')
  assert not errors and not external,(errors,external);assert all(pathlib.Path(path).read_bytes()==value for path,value in before.items());print(json.dumps({'root':str(root),'checks':checks,'errors':errors,'external':external,'nativeWindows':False},ensure_ascii=False),flush=True);page.close();browser.close()
except Exception:
 print('FAILURE '+str(root)+' '+json.dumps({'errors':errors,'traffic':traffic[-3:]},ensure_ascii=False),flush=True)
 if page:
  try:page.evaluate('()=>globalThis.__releaseRunRead?.()')
  except Exception:pass
 raise
finally:stop()
