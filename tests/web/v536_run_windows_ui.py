"""Actual per-view process/control fixture. No account, grant, paid inference or user project."""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-run-windows-ui-'))
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
errors=[];external=[];traffic=[]
try:
 start(0)
 with sync_playwright() as p:
  from playwright.sync_api import expect
  expect.set_options(timeout=30000)
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)));page.route('**/*',lambda route:route.continue_() if route.request.url.startswith(origin+'/') else (external.append(route.request.url),route.abort()))
  def observe(response):
   try:
    request=response.request.post_data_json
    if isinstance(request,dict) and request.get('op')=='update':
     for row in response.json().get('results',[]):
      if row.get('ok') and isinstance(row.get('result'),dict) and 'lease' in row['result']:traffic.append(row['result'])
   except Exception:pass
  page.on('response',observe);goto_editor(page,url);page.locator('.work-body').wait_for();page.locator('#chat-input').fill('실행창을 열어도 보존할 한글 입력');page.locator('#run').click();first=page.locator('.run-window').last;expect(first).to_be_visible();key=first.get_attribute('data-key');expect(first.locator('[data-run-play]')).to_be_enabled();expect(first.locator('[data-run-pause]')).to_be_disabled();assert key.startswith('run:instance:');expect(first.locator('.run-controls')).to_have_count(1);assert first.locator(':scope > .window-title .run-controls').count()==1;expect(first.locator('.run-fps')).to_have_text('(—fps)');expect(first.locator('[data-run-project]')).to_be_visible();expect(first.locator('[data-run-surface]')).to_contain_text('자동 확정 없음');assert first.locator('.run-entity,.run-horizon,[data-run-target],[data-run-disconnect],[data-run-logs]').count()==0
  initial=[row for row in traffic if row['view']==key[13:]][-1];assert initial['state']=='idle' and not initial['handle'];checked('원본 v536 헤더 버튼/문서 탭에 연결하고 단순 열기는 실행하지 않으며 가짜 렌더/FPS·이전 개발용 폼을 표시하지 않는다')
  first.locator('[data-run-play]').click();expect(first.locator('.caption strong')).to_have_text('실행 중',timeout=180000);expect(first.locator('[data-run-pause]')).to_be_enabled(timeout=30000);first.locator('[data-run-pause]').click();expect(first.locator('.caption strong')).to_have_text('일시 정지');expect(first.locator('[data-run-step]')).to_be_enabled();data=[row for row in traffic if row['view']==key[13:] and row['control'].get('mode')=='paused'][-1];frame=int(data['control']['frame']);first.locator('[data-run-step]').click();expect(first.locator('[data-run-frame]')).to_contain_text('프레임 '+str(frame+1));checked('실제 UI 재생→Pause→한 프레임 Step이 실제 협력적 프로세스의 ACK와 프레임에 반영된다')
  page.get_by_role('tab',name='Workspace',exact=True).click();page.locator('#run').click();second=page.locator('.run-window').last;second_key=second.get_attribute('data-key');assert key!=second_key;expect(second.locator('[data-run-play]')).to_be_enabled();second.locator('[data-run-play]').click();expect(second.locator('.caption strong')).to_have_text('실행 중',timeout=180000);expect(second.locator('[data-run-pause]')).to_be_enabled();second.locator('[data-run-pause]').click();expect(second.locator('.caption strong')).to_have_text('일시 정지');second_data=[row for row in traffic if row['view']==second_key[13:] and row['control'].get('mode')=='paused'][-1];assert second_data['handle']!=data['handle'];before_frame=int(second_data['control']['frame']);tab=page.locator('[data-window-tab="'+second_key+'"]');tab.locator('..').locator('.workspace-tab-close').click();expect(second).to_be_hidden();assert run('read',second_data)['closed'];first_tab=page.locator('[data-window-tab="'+key+'"]');first_tab.click();expect(first).to_be_visible();expect(first.locator('.caption strong')).to_have_text('일시 정지');assert run('read',data)['state']=='running';expect(page.locator('#chat-input')).to_have_value('실행창을 열어도 보존할 한글 입력');checked('두 탭은 별도 실행이며 한 탭 닫기는 그 실행만 종료하고 다른 실행·프로젝트 입력을 보존한다')
  page.screenshot(path=str(root/'run-desktop.png'));first.locator('[data-run-play]').click();expect(first.locator('.caption strong')).to_have_text('실행 대기중');expect(first.locator('[data-run-pause]')).to_be_disabled();assert run('read',data)['state']=='stopped';page.evaluate('()=>confectoryFlushPresentation()');page.reload();goto_editor(page,url);first=page.locator('.window[data-key="'+key+'"]');expect(first).to_be_visible(timeout=60000);expect(first.locator('[data-run-play]')).to_be_enabled();expect(first.locator('.caption strong')).to_have_text('실행 대기중');assert run('read',data)['state']=='stopped';expect(page.locator('#chat-input')).to_have_value('실행창을 열어도 보존할 한글 입력');checked('중단·실제 페이지 재진입은 자동 실행 없이 같은 창과 미저장 채팅 입력을 복원한다')
  page.set_viewport_size({'width':390,'height':844});expect(first).to_be_visible();box=first.bounding_box();assert box['x']>=0 and box['x']+box['width']<=391,box;assert first.locator('.run-controls').evaluate('(e)=>e.getBoundingClientRect().bottom')<=first.locator('.window-title').evaluate('(e)=>e.getBoundingClientRect().bottom');page.screenshot(path=str(root/'run-mobile.png'));checked('390px 브라우저 폭에서 원본 헤더 줄바꿈과 실제 문서 패널 경계를 확인했다')
  assert not errors and not external,(errors,external);assert all(pathlib.Path(path).read_bytes()==value for path,value in before.items());print(json.dumps({'root':str(root),'checks':checks,'errors':errors,'external':external,'nativeWindows':False},ensure_ascii=False),flush=True);page.close();browser.close()
except Exception:
 print("FAILURE "+str(root)+" "+json.dumps({"errors":errors,"external":external,"traffic":traffic[-6:]},ensure_ascii=False),flush=True)
 raise
finally:stop()
