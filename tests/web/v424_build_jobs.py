"""Actual compiler jobs with a public lease probe, independent Run ownership and durable receipts."""
import fcntl,json,pathlib,subprocess,time,uuid
from playwright.sync_api import expect

def verify_build_jobs(page,project,report,env,mount,send,envelope,settle,restart):
 originals={p:p.read_bytes() for p in project.iterdir() if p.is_file()};sentinel=pathlib.Path(env['CONFECTORY_BUILD_UI_SENTINEL'])
 def state():
  view=mount();value=view['state'];assert send(envelope(view,'dispose'))['ok'];return value
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=120000)
 def nav(name):
  if not page.locator('.nav-menu').count():page.locator('#nav').click()
  page.locator('.nav-menu').get_by_role('button',name=name,exact=True).click();ready()
 def panel():return page.locator('.window[data-key="builds"]')
 def run():return page.locator('.window[data-key="run"]')
 def show_run():page.locator('#run').click();expect(run()).to_be_visible();ready()
 def outcome(text):expect(panel().locator('[data-build-result-state]')).to_have_text(text,timeout=180000);ready()
 show_run();expect(run().locator('[data-run-build]')).to_be_enabled();run().locator('[data-run-build]').click();expect(panel()).to_be_visible();outcome('빌드 완료');assert state()['executionState']=='idle' and not sentinel.exists()
 first=state()['buildJobs'][0]['job'];panel().locator('[data-build-verify]').click();ready();expect(panel().locator('[data-build-artifacts]')).to_contain_text('기록된 파일 일치');expect(panel().locator('[data-build-error]')).to_have_text('')
 for button in panel().locator('[data-build-read],[data-build-start],[data-build-stop],[data-build-verify]').all():
  box=button.bounding_box();dock=page.locator('#dock').bounding_box();assert box and (box['x']+box['width']<=dock['x'] or box['y']+box['height']<=dock['y']),(box,dock)
 # Interoperate with the actual public FileStream lease contract, without copying its implementation.
 lease=pathlib.Path(json.loads(subprocess.check_output([*report['leaseProbe'],str(project)],env=env,text=True)));lease.parent.mkdir(parents=True,exist_ok=True)
 with lease.open('a+b') as held:
  fcntl.flock(held,fcntl.LOCK_EX)
  panel().locator('[data-build-start]').click();outcome('소스 잠금 대기');waiting=next(row['job'] for row in state()['buildJobs'] if row['state']=='building');assert waiting!=first and state()['executionState']=='idle'
  panel().locator('[data-close]').click();assert state()['hasActiveBuilds'];nav('빌드 작업');outcome('소스 잠금 대기');panel().locator('[data-build-stop]').click();outcome('중지됨');assert next(row for row in state()['buildJobs'] if row['job']==waiting)['state']=='stopped' and not sentinel.exists()
  fcntl.flock(held,fcntl.LOCK_UN)
 # A new actual compiler failure has its own job and never presents the earlier successful artifact key.
 body=project/'main.csbody';before=body.read_bytes();body.write_bytes(before+b'\nthis is deliberately invalid C#;\n')
 try:
  panel().locator('[data-build-start]').click();outcome('실패');expect(panel().locator('[data-build-error]')).not_to_have_text('');failed=next(row for row in state()['buildJobs'] if row['state']=='failed');assert failed['job'] not in [first,waiting] and 'key' not in failed and not sentinel.exists()
 finally:body.write_bytes(before)
 # The existing actual runtime stays owned/running while an independent build completes.
 show_run();run().locator('[data-run-play]').click();expect(run().locator('.run-status')).to_contain_text('running',timeout=180000);ready()
 deadline=time.monotonic()+15
 while not sentinel.exists() and time.monotonic()<deadline:time.sleep(.05)
 assert sentinel.exists() and sentinel.read_text()=='run\n'
 stable=False
 for attempt in range(5):
  first_observation=mount();assert send(envelope(first_observation,'dispose'))['ok'];time.sleep(.35);next_observation=mount();assert send(envelope(next_observation,'dispose'))['ok']
  if first_observation['state']==next_observation['state']:
   assert first_observation['revision']==next_observation['revision'],('No-op observation changed revision for identical public state',first_observation['revision'],next_observation['revision']);stable=True;break
 assert stable,'No stable actual runtime observation pair'
 expect(run().locator('[data-run-build]')).to_be_enabled();run().locator('[data-run-build]').click();outcome('빌드 완료');assert state()['executionState']=='running' and sentinel.read_text()=='run\n';expect(panel().locator('[data-build-stop]')).to_be_disabled()
 page.screenshot(path='/tmp/confectory-v424-build-jobs.png',full_page=True);show_run();expect(run().locator('[data-run-stop]')).to_be_enabled();run().locator('[data-run-stop]').click();expect(run().locator('.run-status')).to_contain_text('stopped',timeout=30000);ready();assert any(row['job']==first and row['state']=='built' for row in state()['buildJobs'])
 nav('빌드 작업');expect(panel().locator('[data-build-status]')).to_contain_text('4개 작업');page.evaluate('()=>globalThis.confectoryFlushPresentation()');restart();expect(panel()).to_be_visible(timeout=30000);expect(panel().locator('[data-build-status]')).to_contain_text('다시 읽으세요');expect(panel().locator('[data-build-stop]')).to_be_disabled();nav('빌드 작업');outcome('빌드 완료');expect(panel().locator('[data-build-status]')).to_contain_text('4개 작업');expect(panel().locator('[data-build-owner]')).to_contain_text('중지 권한이 없');expect(panel().locator('[data-build-stop]')).to_be_disabled();panel().locator('[data-build-verify]').click();ready();expect(panel().locator('[data-build-artifacts]')).to_contain_text('기록된 파일 일치');assert state()['executionState']=='idle' and sentinel.read_text()=='run\n'
 for path,content in originals.items():assert path.read_bytes()==content,path.name
 print('PASS actual build-only jobs: real success/no run, public lease wait/owned stop, panel reopen, distinct failed receipt, independent actual runtime, artifacts, and cold history without replay',flush=True)
