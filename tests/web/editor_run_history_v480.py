from editor_navigation import goto_editor
import json,os,pathlib,subprocess,tempfile,time,shutil,sys,signal,urllib.request
from playwright.sync_api import sync_playwright,expect
expect.set_options(timeout=30000)
repo=pathlib.Path(sys.argv[1]).resolve();report=json.load(open(sys.argv[2]));root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-run-history-v480-'))
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
  host,stream,url=start(0);old_group=host.pid;page=browser.new_page(viewport={'width':1600,'height':1200});page.on('pageerror',lambda e:errors.append(str(e)));goto_editor(page,url);page.locator('.work-body').wait_for();page.locator('#run').click();run=page.locator('.window[data-key="run"]');expect(run).to_be_visible()
  def state():return public_state(url)
  def wait_state(predicate):
   end=time.monotonic()+30
   while time.monotonic()<end:
    value=state()
    if predicate(value):return value
    time.sleep(.025)
   raise AssertionError(value)
  def receipts():
   paths=list((project/'.confectory/run-history').glob('*.json'));assert len(paths)==1,paths;return paths[0]
  def visible_history():
   if not run.locator('[data-run-history]').get_attribute('open'):run.locator('[data-run-history] summary').click()
  visible_history();expect(run.locator('[data-run-history-status]')).to_contain_text('저장된 실행 기록이 없습니다');assert state()['executionState']=='idle'
  # A real compiler failure records only outcome facts, never diagnostics.
  source=project/'Main.celem';original=source.read_bytes();source.write_text('invalid CANARY_PRIVATE_DIAGNOSTIC declaration');run.locator('[data-run-play]').click();expect(run.locator('.run-status')).to_contain_text('failed',timeout=180000);failed=state()['executionHandle'];expect(run.locator('[data-run-history-execution="'+failed+'"]')).to_contain_text('failed');assert 'CANARY_PRIVATE_DIAGNOSTIC' not in receipts().read_text();source.write_bytes(original)
  run.locator('[data-run-play]').click();expect(run.locator('[data-run-pause]')).to_be_enabled(timeout=180000);run.locator('[data-run-pause]').click();paused=wait_state(lambda s:s['executionControl'].get('ack')==1 and s['executionControl'].get('mode')=='paused');owned=paused['executionHandle'];run.locator('[data-run-step]').click();stepped=wait_state(lambda s:s['executionControl'].get('ack')==2);frame=stepped['executionControl']['frame'];expect(run.locator('[data-run-frame]')).to_contain_text('ACK 2');row=run.locator('[data-run-history-execution="'+owned+'"]');expect(row).to_contain_text('FRAME '+frame+' / ACK 2');expect(row).to_contain_text('현재 호스트 소유 기록')
  path=receipts();raw=path.read_bytes();record=json.loads(raw);assert set(record)=={'version','scope','manifest','sequence','rows'}
  for value in record['rows']:assert set(value)=={'execution','revision','order','observedUtc','recordedState','frame','ack','frameState','exitCode'}
  run.locator('[data-run-close-project]').click();page.locator('.modal [data-cancel]').click();assert path.read_bytes()==raw and state()['executionHandle']==owned
  run.locator('[data-run-history-refresh]').click();assert path.read_bytes()==raw;expect(run.locator('[data-run-frame]')).to_contain_text('ACK 2');page.evaluate('()=>globalThis.confectoryFlushPresentation()');page.screenshot(path=str(root/'actual-owned-run-history.png'))
  # Crash only this owned host. A new host must read facts without pinging/adopting its children.
  before_children=child_ids(host.pid);assert before_children;host.kill();host.wait(timeout=10);stream.close();page.close();host,stream,url=start(1);page=browser.new_page(viewport={'width':1600,'height':1200});page.on('pageerror',lambda e:errors.append(str(e)));goto_editor(page,url);run=page.locator('.window[data-key="run"]');expect(run.locator('.run-status')).to_have_text('idle');visible_history();row=run.locator('[data-run-history-execution="'+owned+'"]');expect(row).to_contain_text('owner-unavailable');expect(row).to_contain_text('마지막 확인: running');expect(row).to_contain_text('FRAME '+frame+' / ACK 2');expect(run.locator('[data-run-owner]')).to_contain_text('owner-unavailable');expect(run.locator('[data-run-stop]')).to_be_disabled();expect(run.locator('[data-run-step]')).to_be_disabled();expect(run.locator('[data-run-reconnect]')).to_be_disabled();assert not child_ids(host.pid) and not state()['executionHandle'];assert path.read_bytes()==raw
  for endpoint,bad in [('stopProject',{'handle':owned}),('runControl',{'handle':owned,'action':'step','runtime':stepped['executionControl']['runtime'],'ack':'2','sequence':'2'})]:
   denied,after=rpc(url,endpoint,bad);assert not denied['ok'] and after['executionState']=='idle' and not after['executionOwnerAvailable']
  for _ in range(2):run.locator('[data-run-history-refresh]').click();assert path.read_bytes()==raw and not child_ids(host.pid)
  page.screenshot(path=str(root/'actual-cold-owner-unavailable.png'))
  # Corruption remains visible and unchanged; it neither restores control nor prevents a separate explicit Run/Stop.
  corrupt=b'{"token":"CANARY_MUST_NOT_EXPOSE"}';path.write_bytes(corrupt);run.locator('[data-run-history-refresh]').click();expect(run.locator('[data-run-history-status]')).to_contain_text('읽을 수 없습니다');assert path.read_bytes()==corrupt and 'CANARY_MUST_NOT_EXPOSE' not in json.dumps(state())
  run.locator('[data-run-play]').click();expect(run.locator('[data-run-pause]')).to_be_enabled(timeout=180000);fresh=state()['executionHandle'];assert fresh!=owned;run.locator('[data-run-pause]').click();wait_state(lambda s:s['executionControl'].get('mode')=='paused');assert path.read_bytes()==corrupt;run.locator('[data-run-stop]').click();expect(run.locator('.run-status')).to_contain_text('stopped');assert path.read_bytes()==corrupt;page.screenshot(path=str(root/'actual-corrupt-history.png'))
  path.write_bytes(raw);run.locator('[data-run-history-refresh]').click();expect(run.locator('[data-run-history-execution="'+owned+'"]')).to_contain_text('owner-unavailable');assert state()['executionHandle']==fresh and state()['executionState']=='stopped'
  assert not errors,errors;assert all((project/name).read_bytes()==data for name,data in before.items());assert state()['aiState']=='idle' and not state()['workers']
  (root/'actual-history-observation.json').write_text(json.dumps({'oldExecution':owned,'lastConfirmedFrame':frame,'lastConfirmedAck':2,'coldOwnerAvailable':False,'coldProcessState':'idle','coldHostChildren':[],'freshExplicitExecution':fresh,'savedFacts':record,'corruptBytesPreserved':True,'noAdoptionOrReplay':True},indent=2));print('PASS actual Run history: compiler failure/verified frame facts, close cancel, cold owner-unavailable/no capability/Stop/replay, corruption preserved and independent explicit Run/Stop '+str(root),flush=True)
 except Exception:
  if 'page' in locals() and not page.is_closed():page.screenshot(path=str(root/'failure.png'))
  raise
 finally:
  if 'host' in locals() and host.poll() is None:stop(host,stream)
  if old_group:
   try:os.killpg(old_group,signal.SIGTERM)
   except ProcessLookupError:pass
  browser.close()
