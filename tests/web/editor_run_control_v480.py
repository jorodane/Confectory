import json,os,pathlib,subprocess,tempfile,time,shutil,sys,signal,urllib.request
from playwright.sync_api import sync_playwright,expect
expect.set_options(timeout=30000)
repo=pathlib.Path(sys.argv[1]).resolve();report=json.load(open(sys.argv[2]));root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-run-control-v480-'))
project=root/'ordinary-frame-loop';shutil.copytree(repo/'examples/frame-loop',project,ignore=shutil.ignore_patterns('.confectory'));manifest=project/'project.cpack';manifest.write_text(manifest.read_text().replace('../../',str(repo)+'/'))
before={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file()}
env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_HOME_STORAGE=str(root/'storage'),CONFECTORY_ENTRY_STORAGE=str(root/'storage'),CONFECTORY_WEB_PROJECT=str(manifest),PATH=str(pathlib.Path(env.get('CONFECTORY_DOTNET','dotnet')).parent)+os.pathsep+env['PATH'])
def start(n):
 log=root/f'host-{n}.log';stream=log.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
 deadline=time.monotonic()+60
 while time.monotonic()<deadline:
  for line in log.read_text().splitlines():
   if line.startswith('CONFECTORY_WEB_UI '):return host,stream,line.split(' ',1)[1]
  if host.poll() is not None:raise AssertionError(log.read_text())
  time.sleep(.1)
 os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=10);stream.close();raise AssertionError(log.read_text())
def stop(host,stream):
 os.killpg(host.pid,signal.SIGTERM)
 try:host.wait(timeout=10)
 except subprocess.TimeoutExpired:os.killpg(host.pid,signal.SIGKILL);host.wait()
 stream.close()
def saved():
 files=list((root/'storage/presentations').glob('*.json'));assert len(files)==1,files
 return json.loads(files[0].read_text())
def public_state(url):
 token=url.split('#',1)[1];endpoint=url.split('#',1)[0]+'api/request'
 def send(body):
  request=urllib.request.Request(endpoint,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token})
  with urllib.request.urlopen(request,timeout=30) as reply:return json.load(reply)
 for _ in range(150):
  mounted=send({'op':'mount'})
  if mounted['ok']:break
  assert mounted.get('error',{}).get('code')=='busy',mounted
  time.sleep(.02)
 else:raise AssertionError(mounted)
 try:return mounted['state']
 finally:assert send({'op':'dispose','view':mounted['view']})['ok']
def rpc(url,endpoint,input):
 token=url.split('#',1)[1];address=url.split('#',1)[0]+'api/request'
 def send(body):
  req=urllib.request.Request(address,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token})
  with urllib.request.urlopen(req,timeout=30) as response:return json.load(response)
 for attempt in range(8):
  view=send({'op':'mount'});assert view['ok'],view;rid='owned-run-probe-'+str(time.time_ns());envelope={'view':view['view'],'scope':view['scope']}
  try:
   accepted=send(dict(envelope,op='invoke',endpoint=endpoint,input=input,expectedRevision=view['revision'],requestId=rid));assert accepted['ok'],accepted
   for _ in range(300):
    result=send(dict(envelope,op='update'));assert result['ok'],result
    rows=[row for row in result['results'] if row['requestId']==rid]
    if rows:
     if rows[0].get('error',{}).get('code')=='stale_revision':break
     return rows[0],result['state']
    time.sleep(.01)
   else:raise AssertionError('pending actual command')
  finally:assert send(dict(envelope,op='dispose'))['ok']
 raise AssertionError('stale actual request after explicit fixture retries')
def child_ids(pid):
 parents={}
 for line in subprocess.check_output(['ps','-eo','pid=,ppid='],text=True).splitlines():
  child,parent=map(int,line.split());parents.setdefault(parent,[]).append(child)
 def walk(parent):
  result=[]
  for child in parents.get(parent,[]):result.append(child);result.extend(walk(child))
  return result
 return walk(pid)
def live(pid):
 try:return pathlib.Path('/proc/'+str(pid)+'/stat').read_text().split(') ',1)[1].split()[0]!='Z'
 except FileNotFoundError:return False
old_group=None
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);errors=[]
 try:
  host,stream,url=start(0);old_group=host.pid;page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url);page.locator('.work-body').wait_for();page.locator('#run').click();run=page.locator('.window[data-key="run"]');expect(run).to_be_visible();expect(run.locator('[data-run-pause]')).to_be_disabled();expect(run.locator('[data-run-step]')).to_be_disabled()
  # Actual ordinary source compiler failure, without a control handshake or fake frame.
  source=project/'Main.celem';original=source.read_bytes();source.write_text('invalid owned declaration')
  run.locator('[data-run-play]').click();expect(run.locator('.run-status')).to_contain_text('failed',timeout=180000);expect(run.locator('[data-run-frame]')).to_have_text('');source.write_bytes(original)
  run.locator('[data-run-play]').click();expect(run.locator('.run-status')).to_contain_text('running',timeout=180000);expect(run.locator('[data-run-pause]')).to_be_enabled(timeout=30000)
  def enter_home():
   expect(page.locator('.home-grid')).to_be_visible();expect(page.locator('[data-stat="objects"]').first).to_have_attribute('data-status','available');expect(page.locator('[data-enter]').first).to_be_enabled();page.locator('[data-enter]').first.click();expect(page.locator('.work-body')).to_be_visible()
  def control():return public_state(url)['executionControl']
  def wait_control(condition):
   end=time.monotonic()+15
   while time.monotonic()<end:
    value=control()
    if condition(value):return value
    time.sleep(.025)
   raise AssertionError(value)
  def payload(snapshot,action):return {'handle':public_state(url)['executionHandle'],'action':action,'runtime':snapshot.get('runtime',''),'ack':str(snapshot.get('ack',0)),'sequence':str(snapshot.get('sequence',0))}
  active=public_state(url);first_handle=active['executionHandle'];initial=wait_control(lambda s:s['available'] and int(s['frame'])>2)
  run.locator('[data-run-pause]').click();paused=wait_control(lambda s:s.get('mode')=='paused' and s.get('ack')==1);frame=int(paused['frame']);time.sleep(.15);assert int(control()['frame'])==frame
  expect(run.locator('[data-run-play]')).to_be_enabled();expect(run.locator('[data-run-step]')).to_be_enabled();expect(run.locator('[data-run-control]')).to_contain_text('일시정지')
  stale=payload(paused,'step');run.locator('[data-run-step]').dblclick();stepped=wait_control(lambda s:s.get('ack')==2);assert int(stepped['frame'])==frame+1;frame+=1
  rejected,_=rpc(url,'runControl',stale);assert not rejected['ok'];time.sleep(.1);assert int(control()['frame'])==frame
  # Invalid action and a foreign execution owner cannot affect the real callback loop.
  for bad in [dict(payload(stepped,'step'),handle='0'*32),payload(stepped,'not-an-operation')]:
   denied,_=rpc(url,'runControl',bad);assert not denied['ok'];assert int(control()['frame'])==frame
  page.evaluate('()=>globalThis.confectoryFlushPresentation()');expect(run.locator('[data-run-frame]')).to_contain_text('ACK 2');expect(run.locator('[data-run-play]')).to_have_attribute('aria-label','실행 재개');expect(run.locator('[data-run-play]')).to_be_enabled();run.locator('[data-run-play]').click();playing=wait_control(lambda s:s.get('ack')==3 and s.get('mode')=='running' and int(s['frame'])>frame)
  run.locator('[data-run-disconnect]').click();expect(run.locator('[data-run-control]')).to_contain_text('연결을 확인할 수 없습니다');expect(run.locator('[data-run-step]')).to_be_disabled();time.sleep(2.4);run.locator('[data-run-reconnect]').click();reconnected=wait_control(lambda s:s.get('connected') and s.get('mode')=='paused');assert reconnected['ack']==3;frame=int(reconnected['frame']);time.sleep(.15);assert int(control()['frame'])==frame
  run.locator('[data-run-step]').click();stepped=wait_control(lambda s:s.get('ack')==4);assert int(stepped['frame'])==frame+1;frame+=1;expect(run.locator('[data-run-logs]')).to_contain_text('LOCAL_FRAME');page.screenshot(path=str(root/'actual-frame-pause-step.png'))
  # Presentation close/reopen, hide/return and browser reload retain the same owner without replay.
  run.locator('[data-close]').click();page.locator('#run').click();expect(run.locator('[data-run-step]')).to_be_enabled();assert control()['runtime']==stepped['runtime'];page.locator('.brand').click();expect(page.locator('[data-stat="objects"]').first).to_have_attribute('data-status','available');expect(page.locator('[data-enter]').first).to_be_enabled();enter_home();expect(run.locator('[data-run-step]')).to_be_enabled();page.reload();expect(run.locator('[data-run-step]')).to_be_enabled(timeout=30000);assert int(control()['frame'])==frame
  # Close confirmation cancellation keeps the paused execution, then owned Stop retires it.
  run.locator('[data-run-close-project]').click();page.locator('.modal [data-cancel]').click();assert public_state(url)['executionHandle']==first_handle;assert int(control()['frame'])==frame
  run.locator('[data-run-stop]').click();expect(run.locator('.run-status')).to_contain_text('stopped');expect(run.locator('[data-run-step]')).to_be_disabled();assert control()['connected']==False
  # A new run has a fresh identity; stale Stop and Step from the previous run must fail.
  tick=project/'Tick.csbody';original_tick=tick.read_bytes();tick.write_text('System.Threading.Thread.Sleep(1000);\n'+original_tick.decode())
  run.locator('[data-run-play]').click();expect(run.locator('[data-run-pause]')).to_be_enabled(timeout=180000);fresh=wait_control(lambda s:s.get('connected'));assert public_state(url)['executionHandle']!=first_handle and fresh['runtime']!=stepped['runtime']
  for endpoint,bad in [('stopProject',{'handle':first_handle}),('runControl',dict(stale,handle=first_handle))]:
   denied,after=rpc(url,endpoint,bad);assert not denied['ok'] and after['executionState']=='running'
  run.locator('[data-run-pause]').click();blocked=wait_control(lambda s:s.get('ack')==1 and s.get('mode')=='paused');fresh_handle=public_state(url)['executionHandle'];accepted,pending=rpc(url,'runControl',payload(blocked,'step'));assert accepted['ok'] and pending['executionControl']['ack']==1 and pending['executionControl']['pending']==2
  stopped,stopped_state=rpc(url,'stopProject',{'handle':fresh_handle});assert stopped['ok'] and stopped_state['executionState']=='stopped' and stopped_state['executionControl']['ack']==1;time.sleep(1.1);assert control()['ack']==1,'Stop must not fabricate an unfinished Step acknowledgement';tick.write_bytes(original_tick)
  # A real callback exception ends the child without acknowledging its incomplete Step.
  marker=root/'fail-next-frame';tick.write_text('if(System.IO.File.Exists('+json.dumps(str(marker))+'))throw new InvalidOperationException("owned frame callback failure");\n'+original_tick.decode());run.locator('[data-run-play]').click();expect(run.locator('[data-run-pause]')).to_be_enabled(timeout=180000);run.locator('[data-run-pause]').click();fault_ready=wait_control(lambda s:s.get('ack')==1 and s.get('mode')=='paused');marker.write_text('fail');run.locator('[data-run-step]').click();expect(run.locator('.run-status')).to_contain_text('failed',timeout=30000);assert control()['ack']==1 and not control()['connected'];expect(run.locator('[data-run-logs]')).to_contain_text('owned frame callback failure');tick.write_bytes(original_tick);marker.unlink()
  run.locator('[data-run-play]').click();expect(run.locator('[data-run-pause]')).to_be_enabled(timeout=180000);run.locator('[data-run-pause]').click();wait_control(lambda s:s.get('ack')==1 and s.get('mode')=='paused');run.locator('[data-run-close-project]').click();page.locator('.modal [data-complete-close]').click();expect(page.locator('.home-grid')).to_be_visible();assert not child_ids(host.pid)
  enter_home();expect(run.locator('.run-status')).to_have_text('idle');expect(run.locator('[data-run-step]')).to_be_disabled();assert not child_ids(host.pid)
  # Cold host has no borrowed control identity and launches nothing automatically.
  page.evaluate('()=>globalThis.confectoryFlushPresentation()');stop(host,stream);page.close();host,stream,url=start(1);page=browser.new_page(viewport={'width':1440,'height':1000});page.goto(url);run=page.locator('.window[data-key="run"]');expect(run.locator('.run-status')).to_have_text('idle');assert not child_ids(host.pid);assert not public_state(url).get('executionHandle');expect(run.locator('[data-run-step]')).to_be_disabled();assert not errors,errors
  assert all((project/name).read_bytes()==data for name,data in before.items())
  (root/'actual-frame-observation.json').write_text(json.dumps({'initial':initial,'paused':paused,'stepped':stepped,'afterReconnect':reconnected,'freshRun':fresh,'coldState':public_state(url)['executionState']},indent=2));page.screenshot(path=str(root/'actual-cold-frame-owner.png'));print('PASS actual v480 local Run frame/ack pause/Step, disconnect/lease/reconnect, same-owner reload, stale/foreign/repeated commands, close cancel/confirm, Stop and cold no replay '+str(root),flush=True)
 except Exception:
  if 'page' in locals() and not page.is_closed():page.screenshot(path=str(root/'failure.png'))
  raise
 finally:
  if 'host' in locals() and host.poll() is None:stop(host,stream)
  if old_group:
   try:os.killpg(old_group,signal.SIGTERM)
   except ProcessLookupError:pass
  browser.close()
