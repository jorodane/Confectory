from editor_navigation import goto_editor
import json,os,pathlib,subprocess,tempfile,time,shutil,sys,signal,urllib.request
from playwright.sync_api import sync_playwright,expect
expect.set_options(timeout=30000)
repo=pathlib.Path(sys.argv[1]).resolve();report=json.load(open(sys.argv[2]));root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-run-v318-'))
project=root/'ordinary-button-game';shutil.copytree(repo/'examples/button-game',project,ignore=shutil.ignore_patterns('.confectory'));manifest=project/'project.cpack';manifest.write_text(manifest.read_text().replace('../../',str(repo)+'/'))
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
 mounted=send({'op':'mount'});assert mounted['ok'],mounted
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
  host,stream,url=start(0);old_group=host.pid;page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)));goto_editor(page,url);page.locator('.work-body').wait_for();page.locator('#run').click();run=page.locator('.window[data-key="run"]');expect(run).to_be_visible();expect(run.locator('[data-run-pause]')).to_be_disabled();expect(run.locator('[data-run-step]')).to_be_disabled();expect(run.locator('[data-run-build]')).to_be_enabled();expect(run.locator('[data-run-owner]')).to_contain_text('소유 실행 기록이 없습니다');assert public_state(url)['executionState']=='idle'
  run.locator('[data-run-target]').select_option('windows');page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"');page.evaluate('()=>globalThis.confectoryFlushPresentation()');expect(page.locator('#workspace-save-state')).to_have_text('');assert saved()['inputs']['target']=='windows';run.locator('[data-run-target]').select_option('linux')
  # Break only the owned ordinary source, observe a real compiler failure, restore it.
  source=project/'main.celem';original=source.read_bytes();source.write_text('invalid owned declaration for compiler failure')
  run.locator('[data-run-play]').click();expect(run.locator('.run-status')).to_contain_text('failed',timeout=180000);expect(run.locator('[data-run-exit]')).to_contain_text('실제 종료 코드: 1');run.locator('.run-log-view summary').click();expect(run.locator('[data-run-logs]')).to_contain_text('Execution: failed');page.screenshot(path=str(root/'actual-build-failed.png'));source.write_bytes(original)
  run.locator('[data-run-play]').click();expect(run.locator('.run-status')).to_contain_text('building');building_ids=child_ids(host.pid);assert building_ids;run.locator('[data-run-stop]').click();expect(run.locator('.run-status')).to_contain_text('stopped');assert not any(live(pid) for pid in building_ids)
  run.locator('[data-run-play]').click();expect(run.locator('.run-status')).to_contain_text('running',timeout=240000);state=public_state(url);assert state['executionOwnerAvailable'] and state['executionTarget']=='linux';expect(run.locator('[data-run-play]')).to_be_disabled();expect(run.locator('[data-run-stop]')).to_be_enabled();expect(run.locator('[data-run-target]')).to_be_disabled();children=child_ids(host.pid);assert children,'no actual process tree';before_ids=set(children)
  duplicate,after=rpc(url,'runProject',{'target':'linux'});assert not duplicate['ok'] and duplicate['error']['code']=='consumer_error',duplicate;assert after['executionState']=='running';assert set(child_ids(host.pid)).issubset(before_ids),'duplicate execution created a process';assert public_state(url)['aiState']=='idle';assert not public_state(url)['workers']
  run.locator('[data-close]').click();expect(run).to_have_count(0);assert public_state(url)['executionState']=='running';assert any(live(pid) for pid in before_ids);page.locator('#run').click();expect(run.locator('.run-status')).to_contain_text('running');page.locator('.brand').click();expect(page.locator('.home-grid')).to_be_visible();assert any(live(pid) for pid in before_ids);page.locator('[data-enter]').first.click();expect(run.locator('.run-status')).to_contain_text('running')
  run.locator('[data-run-stop]').click();expect(run.locator('.run-status')).to_contain_text('stopped');expect(run.locator('[data-run-play]')).to_be_enabled();assert not any(live(pid) for pid in before_ids),'owned tree remained after Stop';expect(run.locator('[data-run-logs]')).to_contain_text('Stopped this project execution')
  run.locator('[data-run-play]').click();expect(run.locator('.run-status')).to_contain_text('running',timeout=240000);closing_ids=child_ids(host.pid);assert closing_ids;denied,denied_state=rpc(url,'closeProject',{'confirmed':False});assert not denied['ok'] and denied_state['executionState']=='running';run.locator('[data-run-close-project]').click();page.locator('.modal [data-cancel]').click();assert public_state(url)['executionState']=='running';assert any(live(pid) for pid in closing_ids);run.locator('[data-run-close-project]').click();page.locator('.modal [data-complete-close]').click();expect(page.locator('.home-grid')).to_be_visible();assert not any(live(pid) for pid in closing_ids),'complete close left owned processes';page.locator('[data-enter]').first.click();expect(run.locator('.run-status')).to_have_text('idle');run.locator('[data-run-play]').click();expect(run.locator('.run-status')).to_contain_text('running',timeout=240000);active_ids=child_ids(host.pid);assert active_ids;box=run.bounding_box();page.mouse.move(box['x']+180,box['y']+18);page.mouse.down();page.mouse.move(box['x']+240,box['y']+58,steps=10);page.mouse.up();run.locator('[data-resize="se"]').press('ArrowRight');run.locator('[data-resize="se"]').press('ArrowDown');run.locator('[data-fold]').click();expect(run.locator('[data-run-play]')).not_to_be_visible();page.wait_for_function('()=>typeof globalThis.confectoryFlushPresentation==="function"');page.evaluate('()=>globalThis.confectoryFlushPresentation()');expect(page.locator('#workspace-save-state')).to_have_text('');saved_run=next(row for row in saved()['layout'] if row['key']=='run');assert saved_run['folded'];assert saved_run['width']==522 and saved_run['height']==368;assert saved_run['x']!=70 and saved_run['y']!=107;page.screenshot(path=str(root/'actual-running-folded.png'))
  # Crash only this owned host. Observe its real children; a cold host must not claim them.
  host.kill();host.wait(timeout=10);stream.close();page.close();remaining=[pid for pid in active_ids if live(pid)]
  host2,stream2,url2=start(1)
  try:
   page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url2);run=page.locator('.window[data-key="run"]');expect(run).to_have_class(__import__('re').compile('folded'));styles=run.evaluate('el=>({x:parseFloat(el.style.left),y:parseFloat(el.style.top),width:parseFloat(el.style.width),height:parseFloat(el.style.height)})');assert all(abs(styles[key]-saved_run[key])<.1 for key in styles),(styles,saved_run);run.locator('[data-fold]').click();expect(run.locator('.run-status')).to_have_text('idle');expect(run.locator('[data-run-owner]')).to_contain_text('이전 호스트');expect(run.locator('[data-run-stop]')).to_be_disabled();state=public_state(url2);assert not state['executionOwnerAvailable'] and state['executionState']=='idle';assert state['executionTarget'] is None;assert saved()['inputs']['target']=='linux';assert not child_ids(host2.pid),'cold host automatically started execution';time.sleep(.6);assert public_state(url2)['executionState']=='idle';page.screenshot(path=str(root/'actual-cold-run.png'));assert not errors,errors;assert all((project/name).read_bytes()==data for name,data in before.items())
   (root/'actual-process-observation.json').write_text(json.dumps({'ownedHostPid':old_group,'observedChildPids':active_ids,'liveAfterHostCrash':remaining,'coldHostChildPids':child_ids(host2.pid),'coldState':state['executionState'],'coldOwnerAvailable':state['executionOwnerAvailable']},indent=2))
  finally:page.close();stop(host2,stream2)
 except Exception:
  if 'page' in locals() and not page.is_closed():page.screenshot(path=str(root/'failure.png'))
  raise
 finally:
  if old_group:
   try:os.killpg(old_group,signal.SIGTERM)
   except ProcessLookupError:pass
  browser.close()
print('PASS ordinary ProjectPack actual Run failure, process ownership and presentation restart '+str(root))
