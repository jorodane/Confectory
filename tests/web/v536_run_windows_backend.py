"""Actual per-view process/control fixture. No account, grant, paid inference or user project."""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request,uuid
from playwright.sync_api import sync_playwright
from editor_navigation import goto_editor
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-run-windows-backend-'))
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
try:
 env['CONFECTORY_WEB_PROJECT']=str(projects[1]);start(-1)
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page();goto_editor(page,url);page.locator('.work-body').wait_for();second_listing=state()['listingId'];page.close();browser.close()
 stop();env['CONFECTORY_WEB_PROJECT']=str(projects[0]);start(0)
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page();goto_editor(page,url);page.locator('.work-body').wait_for();page.close();browser.close()
 first_listing=state()['listingId'];first=run('open');second=run('open');assert first['view']!=second['view'] and first['lease']!=second['lease'];assert first['state']=='idle' and not first['handle'] and first['surfaceSupported'] is False and first['fpsSupported'] is False
 for values in [{'operation':'close-all'},{'operation':'open','context':'forged'},{'operation':'start','view':uuid.uuid4().hex}]:call('runWindow',values,False)
 checked('단순 창 열기는 실행하지 않고 내부 종료·프로젝트/소유자 위조를 거절한다')
 command=uuid.uuid4().hex;first=run('start',first,target='portable',command=command);again=run('start',first,target='portable',command=command);assert first['handle']==again['handle'];first=connected(first);first=control(first,'pause');first=wait(first,lambda s:s['control'].get('mode')=='paused' and s['control'].get('ack')==1);frame=int(first['control']['frame'])
 # Pause before second compile so its own heartbeat/frame lease remains independently observable.
 second=start_run(second);second=connected(second);assert second['handle']!=first['handle'];second=control(second,'pause');second=wait(second,lambda s:s['control'].get('mode')=='paused' and s['control'].get('ack')==1)
 first=run('read',first);assert int(first['control']['frame'])==frame;first=control(first,'step');first=wait(first,lambda s:s['control'].get('ack')==2);assert int(first['control']['frame'])==frame+1;assert run('read',second)['control']['ack']==1
 checked('두 실제 프로세스는 독립 handle/프레임을 가지며 반복 시작은 한 번만 실행하고 한 창 Step은 다른 창을 바꾸지 않는다')
 for values in [dict(lease=uuid.uuid4().hex),dict(handle=second['handle'])]:run('stop',first,False,**values)
 stale=dict(first);stale['control']=dict(first['control'],ack=0);control(stale,'step',False);control(first,'unknown',False)
 assert run('read',first)['control']['ack']==2;second=run('stop',second);assert second['state']=='stopped' and run('read',first)['state']=='running';closed=run('close',second);assert closed['closed'];assert run('close',second)['closed'];second=run('open',view=second['view']);assert not second['handle'] and second['lease']!=closed['lease'];run('stop',closed,False)
 checked('잘못된 handle/lease/과거 ACK와 무효 동작은 차단하며 Stop/Close는 자기 창만 정리하고 재열기는 새 권한을 쓴다')
 # Explicit declared target only. Real compiler error is not a successful process or fake preview.
 run('start',second,False,target='not-declared',command=uuid.uuid4().hex);source=projects[0].parent/'Main.celem';original=source.read_bytes();source.write_text('invalid fixture declaration');second=start_run(second);second=wait(second,lambda s:s['state']=='failed');assert second['failed'];source.write_bytes(original);second=start_run(second);second=connected(second);assert second['state']=='running'
 checked('잘못된 target을 거절하고 실제 컴파일 실패를 failed로 표시하며 명시적 재시도는 새 프로세스로 복구한다')
 # Scope change closes original-v536 views, but no stored layout can launch/restore a child.
 old_first=dict(first);old_second=dict(second);call('leaveProject',{});call('openProject',{'id':second_listing});assert state()['projectId'];run('open',ok=False,view=old_first['view']);third=run('open');assert third['state']=='idle';call('leaveProject',{});call('openProject',{'id':first_listing});assert run('read',old_first)['closed'];assert run('read',old_second)['closed'];fresh=run('open',view=old_first['view']);assert fresh['state']=='idle' and not fresh['handle'] and fresh['lease']!=old_first['lease']
 checked('프로젝트 전환 시 원래 창 실행을 정리하고 같은 이름의 다른 프로젝트는 이전 창 소유권을 재사용하지 못한다')
 # Restart with active owned child must not revive any handle; process tree cleanup is checked via process event tooling separately.
 fresh=start_run(fresh);fresh=connected(fresh);old_lease=fresh['lease'];old_handle=fresh['handle'];stop();start(1)
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page();goto_editor(page,url);page.locator('.work-body').wait_for();page.close();browser.close()
 assert run('read',fresh)['state']=='owner-unavailable';run('stop',fresh,False);restored=run('open',view=fresh['view']);assert restored['lease']!=old_lease and restored['state']=='idle' and not restored['handle']
 checked('엔진 재시작은 화면 id만 복원할 수 있고 실행·lease·프레임 제어 권한을 자동 복원하지 않는다')
 assert all(pathlib.Path(path).read_bytes()==value for path,value in before.items());checked('격리 fixture의 원본 소스·manifest 바이트와 기존 최종 반영 경계를 보존한다')
 print(json.dumps({'root':str(root),'checks':checks},ensure_ascii=False),flush=True)
finally:stop()
