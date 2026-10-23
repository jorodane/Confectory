"""Actual per-view process/control fixture. No account, grant, paid inference or user project."""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());root=pathlib.Path(sys.argv[3]).resolve();assert str(root).startswith('/tmp/confectory-run-followup-')
projects=[root/'first/project.cpack',root/'second/project.cpack']
before={str(p):p.read_bytes() for m in projects for p in m.parent.rglob('*') if p.is_file() and '.confectory' not in p.parts and '.build' not in p.parts};env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(root/'profile'),CONFECTORY_ENTRY_STORAGE=str(root/'profile'),CONFECTORY_MCP_DIRECTORY=str(root/'instances'),CONFECTORY_WEB_PROJECT=str(projects[0]));env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];host=None;stream=None;checks=[]
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
errors=[];external=[];requests=[];page=None
try:
 start(10)
 with sync_playwright() as p:
  import fcntl
  from playwright.sync_api import expect
  expect.set_options(timeout=30000)
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  def setup():
   global page
   page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
   def route(r):
    if not r.request.url.startswith(origin+'/'):external.append(r.request.url);r.abort();return
    body=r.request.post_data_json if r.request.method=='POST' else None
    if isinstance(body,dict) and body.get('op')=='invoke':requests.append(body)
    r.continue_()
   page.route('**/*',route);goto_editor(page,url);expect(page.locator('.work-body')).to_be_visible();return page
  setup();result=page.locator('.window[data-key="build-result"]');expect(result).to_have_count(0);a_listing=state()['listingId'];a_input=page.locator('#chat-input').input_value();assert not [r for r in requests if r['endpoint']=='startBuild'];history=call('buildHistory',{'page':0});stored=next(row for row in history['rows'] if row['state']=='built');receipt=call('buildInfo',{'job':stored['job'],'verify':True});assert receipt['artifactState']=='verified';checked('원본처럼 결과창을 재시작에 자동 복원하지 않고 저장된 빌드 산출물 조회만 하며 새 빌드는 시작하지 않는다')

  tab=page.locator('[data-window-tab^="run:instance:"]').last;tab.click();key=tab.get_attribute('data-window-tab');w=page.locator('.window[data-key="'+key+'"]');n=len([r for r in requests if r['endpoint']=='startBuild']);w.locator('[data-run-export]').click();page.get_by_role('button',name='Android',exact=True).click();assert len([r for r in requests if r['endpoint']=='startBuild'])==n;expect(page.locator('#toast')).to_contain_text('선언되지');unknown=call('buildInfo',{'command':uuid.uuid4().hex,'verify':True});assert unknown['state']=='owner-unavailable';assert not [r for r in requests if r['endpoint']=='startBuild'];checked('미선언 Android와 이전 호스트에 없는 요청 조회는 빌드를 만들거나 이전 권한을 복원하지 않는다')
  lock=projects[0].parent/'.confectory/source-transaction.lock'
  with lock.open('a+b') as held:
   fcntl.flock(held,fcntl.LOCK_EX);w.locator('[data-run-export]').click();page.get_by_role('button',name='Linux',exact=True).click();result=page.locator('.window[data-key="build-result"]');expect(result.locator('[data-export-state]')).to_have_text('빌드 중',timeout=60000);building=state()['buildJobs'][-1];job=building['job'];assert building['phase']=='waiting-for-lease',building;result.locator('[data-close]').click();expect(result).to_be_hidden();page.locator('[data-window-tab="'+key+'"]').click();w.locator('[data-run-export]').click();page.get_by_role('button',name='Linux',exact=True).click();expect(result.locator('[data-export-state]')).to_have_text('빌드 중');assert len([r for r in requests if r['endpoint']=='startBuild'])==n+1;assert state()['buildJobs'][-1]['job']==job;fcntl.flock(held,fcntl.LOCK_UN)
  expect(result.locator('[data-export-state]')).to_have_text('빌드 완료',timeout=180000);expect(result.locator('[data-export-artifacts]')).to_contain_text('파일 일치 확인');command=[r['input']['command'] for r in requests if r['endpoint']=='startBuild'][-1];info=call('buildInfo',{'command':command,'verify':True});assert info['job']==job and info['artifactState']=='verified';assert not (root/'export-must-not-run').exists();expect(page.locator('#chat-input')).to_have_value(a_input);page.evaluate('()=>confectoryFlushPresentation()');page.screenshot(path=str(root/'export-reopened.png'));checked('빌드 중 결과창 닫기/다시 열기는 같은 owned job을 조회하고 산출물 일치·입력을 보존하며 프로젝트를 실행하지 않는다')
  page.close();stop();env['CONFECTORY_WEB_PROJECT']=str(projects[1]);start(11);setup();b_id=state()['projectId'];assert state()['listingId']!=a_listing;expect(page.locator('.window[data-key="build-result"]')).to_have_count(0);call('buildInfo',{'job':job,'verify':True},False);page.locator('#chat-input').fill('B 프로젝트만의 입력');page.locator('.brand').click();expect(page.locator('.home-grid')).to_be_visible();page.locator('[data-enter="'+a_listing+'"]').click();expect(page.locator('.work-body')).to_be_visible();expect(page.locator('#chat-input')).to_have_value(a_input);expect(page.locator('.window[data-key="build-result"]')).to_have_count(0);assert call('buildInfo',{'job':job,'verify':True})['artifactState']=='verified';assert state()['projectId']!=b_id;assert not [r for r in requests if r['endpoint']=='startBuild' and r['input'].get('command')!=command];assert not (root/'export-must-not-run').exists();checked('같은 이름의 다른 프로젝트로 재시작·전환해도 결과창/입력/산출물 문맥을 서로 섞거나 실행하지 않는다')
  assert not errors and not external,(errors,external);assert all(pathlib.Path(path).read_bytes()==value for path,value in before.items());print(json.dumps({'root':str(root),'checks':checks,'errors':errors,'external':external,'nativeWindows':False},ensure_ascii=False),flush=True);page.close();browser.close()
except Exception:
 print('FAILURE '+str(root)+' '+json.dumps({'errors':errors},ensure_ascii=False),flush=True);raise
finally:stop()
