from editor_navigation import goto_editor
"""Actual Home and Helper flow; owned stdio protocol simulation, no real account/model."""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request
from playwright.sync_api import sync_playwright,expect
expect.set_options(timeout=30000)
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-codex-ui-'))
project=root/'ordinary-button-game';shutil.copytree(repo/'examples/button-game',project,ignore=shutil.ignore_patterns('.confectory'));manifest=project/'project.cpack';manifest.write_text(manifest.read_text().replace('../../',str(repo)+'/'))
before={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file()}
fixture=root/'owned-codex-protocol.py';shutil.copyfile(repo/'tests/protocol/codex_owned_stdio.py',fixture);fixture.chmod(0o700);managed=root/'owned-managed-home';managed.mkdir();control=root/'owned-control.json'
def configure(**values):control.write_text(json.dumps(values))
def requests():
 p=root/'owned-requests.jsonl';return [json.loads(line) for line in p.read_text().splitlines()] if p.exists() else []
def turns():return len([row for row in requests() if row.get('method')=='turn/start'])
configure()
env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_ENTRY_STORAGE=str(root/'storage'),CONFECTORY_HOME_STORAGE=str(root/'storage'),CONFECTORY_WEB_PROJECT=str(manifest))
stream=(root/'host.log').open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
errors=[]
try:
 deadline=time.monotonic()+60;url=None
 while time.monotonic()<deadline:
  for line in (root/'host.log').read_text().splitlines():
   if line.startswith('CONFECTORY_WEB_UI '):url=line.split(' ',1)[1]
  if url:break
  assert host.poll() is None,(root/'host.log').read_text();time.sleep(.1)
 assert url,(root/'host.log').read_text();origin,token=url.split('/#')
 def send(body):
  request=urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token})
  with urllib.request.urlopen(request,timeout=20) as response:return json.load(response)
 def state():
  for _ in range(400):
   view=send({'op':'mount'})
   if view.get('error',{}).get('code')=='busy':time.sleep(.01);continue
   assert view['ok'],view;break
  else:raise AssertionError('Read-only mount remained busy')
  try:return view['state']
  finally:assert send({'op':'dispose','view':view['view']})['ok']
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu']);page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda error:errors.append(str(error)))
  def capture(request):
   if request.url.endswith('/api/request') and request.post_data:
    value=request.post_data_json
    if value.get('op')=='invoke':
     with (root/'ui-requests.jsonl').open('a') as log:log.write(json.dumps(value)+'\n')
  page.on('request',capture)
  try:
   goto_editor(page,url);expect(page.locator('.work-body')).to_be_visible();project_id=state()['projectId']
   page.locator('.brand').click();expect(page.locator('.home-grid')).to_be_visible();assert state()['projectId']==''
   def setup(home=False):
    if home:page.locator('#add-agent').click()
    else:page.locator('.agent-home[data-agent="Confectory.Agent.Codex::Connection"]').click()
    dialog=page.get_by_role('dialog',name='사용할 AI',exact=True)
    if home:dialog.get_by_role('button',name='Codex',exact=True).click()
    dialog.locator('[data-codex-route="provider"]').click();dialog.locator('[data-connection-advanced] > summary').click()
    expect(dialog.locator('[data-connection-field="model"]')).to_be_visible();return dialog
   dialog=setup(True)
   for name,value in {'model':'owned-protocol-fixture','executable':str(fixture),'managedHome':str(managed),'credentialReference':'codex:managed'}.items():dialog.locator('[data-connection-field="'+name+'"]').fill(value)
   def conditions(dialog):
    previous=state()['connectionSetup']['outcome'];old_token=previous.get('token') if previous else None;dialog.locator('[data-connection-attempt]').click()
    deadline=time.monotonic()+30
    while (state()['connectionSetup']['outcome'] or {}).get('token')==old_token:
     assert time.monotonic()<deadline,'Readiness form did not refresh its pinned token';time.sleep(.03)
    expect(dialog.locator('[data-check-consent]')).to_have_count(4)
   def check(dialog,outcome,code=None):
    for consent in dialog.locator('[data-check-consent]').all():consent.check()
    dialog.locator('[data-connection-check-start]').click();expect(dialog.locator('[data-connection-result]')).to_have_attribute('data-connection-outcome',outcome)
    if code:expect(dialog.locator('[data-connection-result]')).to_have_attribute('data-connection-code',code)
   conditions(dialog);assert not requests()
   dialog.locator('[data-connection-check-start]').click();assert not requests();expect(dialog.locator('[data-check-consent]')).to_have_count(4)
   check(dialog,'verified');assert turns()==0 and state()['projectId']==''
   assert state()['connectionSetup']['outcome']['accountMetadataVerified'] is True and state()['connectionSetup']['outcome']['authenticated'] is False
   expect(dialog.locator('[data-connection-result]')).to_contain_text('기존 로그인 메타데이터 확인');assert 'OWNED FIXTURE, NOT A REAL ACCOUNT' not in json.dumps(state())
   dialog.locator('[data-connection-cancel]').click();page.locator('[data-enter]').first.click();expect(page.locator('.work-body')).to_be_visible();assert state()['projectId']==project_id
   dialog=setup();dialog.locator('[data-connection-use]').click();expect(page.locator('#status')).to_contain_text('설정 선택됨');dialog.locator('[data-connection-cancel]').click()
   page.locator('#add-helper').click();page.locator('[data-recruit="global"]').click();page.locator('#helper-list button').first.click();page.locator('.modal [data-close]').click()
   def helper():
    page.locator('.home-side [data-helper="main-helper"]').first.click();return page.locator('.participant-expanded-card[data-helper-id="main-helper"]')
   def prepare(card,message):card.locator('textarea').fill(message);card.locator('button[type="submit"]').click();expect(page.locator('#ai-start')).to_be_disabled()
   def approve():
    for choice in page.locator('[data-permission]').all():choice.check()
    expect(page.locator('#ai-start')).to_be_enabled();page.locator('#ai-start').click()
   def wait_ai(expected):
    deadline=time.monotonic()+35
    while time.monotonic()<deadline:
     actual=state()
     if actual['aiState']==expected:return actual
     time.sleep(.05)
    raise AssertionError(state())
   card=helper();prepare(card,'ui-success');assert turns()==0
   page.locator('#cancel-preview').click();assert turns()==0
   prepare(card,'ui-success');approve();actual=wait_ai('completed');assert turns()==1 and actual['aiHelperId']=='main-helper'
   expect(card.locator('.messages')).to_contain_text('OWNED UI FIXTURE: no real Codex account or inference.')
   # Changed effective settings after preview: retained grant is rejected before turn/start.
   prepare(card,'ui-stale');configure(configRevision=1);approve();actual=wait_ai('error');assert actual['aiErrorCode']=='provider-verification-stale' and turns()==1
   card.locator('[data-close]').click();dialog=setup();conditions(dialog);check(dialog,'verified')
   dialog.locator('[data-connection-check-cancel]').click();conditions(dialog);configure(noAccount=True);check(dialog,'unauthenticated');assert turns()==1
   expect(dialog.locator('[data-connection-result]')).to_contain_text('로그인 정보가 없습니다')
   conditions(dialog);configure(unsafeTools=True);check(dialog,'blocked','provider-tool-policy-unsupported');assert state()['connectionSetup']['outcome']['code']=='provider-tool-policy-unsupported' and turns()==1
   conditions(dialog);configure(runtimeUnsafe=True);check(dialog,'blocked','provider-tool-policy-unsupported');expect(dialog.locator('[data-connection-result]')).to_contain_text('runtime-control:apps');assert turns()==1
   conditions(dialog);configure(version='0.1.0-unsupported');check(dialog,'blocked','provider-protocol-unsupported');assert state()['connectionSetup']['outcome']['code']=='provider-protocol-unsupported' and turns()==1
   # A saved model change invalidates the previous check; the new model is checked, not silently substituted.
   configure();dialog.locator('[data-connection-field="model"]').fill('owned-unlisted-model');conditions(dialog);check(dialog,'blocked','provider-model-unsupported');assert state()['connectionSetup']['outcome']['code']=='provider-model-unsupported' and turns()==1
   dialog.locator('[data-connection-field="model"]').fill('owned-protocol-fixture');conditions(dialog);configure(holdCheck=True)
   for consent in dialog.locator('[data-check-consent]').all():consent.check()
   dialog.locator('[data-connection-check-start]').click();expect(dialog.locator('[data-connection-result]')).to_have_attribute('data-connection-outcome','checking');dialog.locator('[data-connection-check-cancel]').click();expect(dialog.locator('[data-connection-result]')).to_have_attribute('data-connection-outcome','cancelled');configure();assert turns()==1
   conditions(dialog);check(dialog,'verified');assert turns()==1
   dialog.locator('[data-connection-check-cancel]').click();conditions(dialog);configure(holdCheck=True)
   for consent in dialog.locator('[data-check-consent]').all():consent.check()
   dialog.locator('[data-connection-check-start]').click();expect(dialog.locator('[data-connection-result]')).to_have_attribute('data-connection-outcome','checking');dialog.press('Escape');expect(dialog).to_have_count(0);configure()
   dialog=setup();expect(dialog.locator('[data-connection-field="model"]')).to_have_value('owned-protocol-fixture');conditions(dialog);check(dialog,'verified');dialog.locator('[data-connection-cancel]').click()
   card=helper();prepare(card,'ui-hold');approve()
   deadline=time.monotonic()+20
   while turns()<2 and time.monotonic()<deadline:time.sleep(.05)
   assert turns()==2;card.locator('[data-helper-stop]').click();actual=wait_ai('stopped');assert (root/'owned-interrupt-marker').exists()
   assert not errors,errors;assert all((project/name).read_bytes()==data for name,data in before.items())
   assert all(row.get('method') not in ('account/login/start','thread/resume','config/value/write','config/batchWrite') for row in requests())
   assert all(row['params']=={'refreshToken':False} for row in requests() if row.get('method')=='account/read')
   (root/'verification.json').write_text(json.dumps({'homeEntry':True,'verifiedViaProduct':True,'actualHelperTurns':turns(),'cases':['success','unapproved-preflight','missing-login','unsupported-tools','unsupported-version','model-change','cancel-check','escape-check','changed-effective-config','request-cancel'],'realAccountOrInference':False,'sourceUnchanged':True},indent=2)+'\n')
   print('PASS actual Home Codex verification and Helper grants: owned protocol fixtures only',root)
  except Exception:
   print('Evidence',root,flush=True);page.screenshot(path=str(root/'failure.png'));print('State',json.dumps(state()),flush=True);raise
  finally:browser.close()
finally:
 if host.poll() is None:os.killpg(host.pid,signal.SIGTERM)
 host.wait(timeout=15);stream.close()
