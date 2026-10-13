"""Ordinary Home Agent entry, inline declared settings and exact readiness boundaries."""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request
from playwright.sync_api import sync_playwright,expect
expect.set_options(timeout=30000)
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-connection-entry-'))
assert report['entry']=='Confectory.EditorHome::Main'
managed=root/'owned-empty-managed';managed.mkdir()
storage=root/'storage';env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_HOME_STORAGE=str(storage));env.pop('CONFECTORY_WEB_PROJECT',None)
errors=[];profiles=[]
def boot(label):
 log=(root/(label+'.log')).open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 deadline=time.monotonic()+60
 while time.monotonic()<deadline:
  for line in (root/(label+'.log')).read_text().splitlines():
   if line.startswith('CONFECTORY_WEB_UI '):return host,log,line.split(' ',1)[1]
  assert host.poll() is None,(root/(label+'.log')).read_text();time.sleep(.1)
 raise AssertionError('Ordinary host did not start')
def stop(host,log):
 if host.poll() is None:os.killpg(host.pid,signal.SIGTERM)
 host.wait(timeout=15);log.close()
def public_state(url):
 origin,token=url.split('/#')
 def send(body):
  request=urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token})
  with urllib.request.urlopen(request,timeout=20) as response:return json.load(response)
 for _ in range(400):
  view=send({'op':'mount'})
  if view.get('error',{}).get('code')=='busy':time.sleep(.01);continue
  assert view['ok'],view;break
 else:raise AssertionError('Read-only mount stayed busy')
 try:return view['state']
 finally:assert send({'op':'dispose','view':view['view']})['ok']
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'])
 try:
  for phase in ('fresh','existing'):
   host,log,url=boot(phase);page=browser.new_page(viewport={'width':1360,'height':900});page.on('pageerror',lambda error:errors.append(str(error)))
   try:
    page.goto(url);expect(page.locator('.home-grid')).to_be_visible()
    if phase=='existing':
     # Keep existing layout data; it must not select/hide a provider or be cleared.
     page.evaluate("localStorage.setItem('confectory-participant-layout',JSON.stringify({participantSidebarWidth:211,homeSidebarCollapsed:false,legacyAgent:'Confectory.Agent.Responses::Connection'}))")
     page.reload();expect(page.locator('.home-grid')).to_be_visible()
    page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='AI Agent 연결',exact=True);expect(dialog).to_be_visible()
    expect(dialog.get_by_role('button',name='OpenAI Responses',exact=True)).to_be_visible();expect(dialog.get_by_role('button',name='Codex',exact=True)).to_be_visible()
    assert public_state(url)['projectId']==''
    dialog.get_by_role('button',name='OpenAI Responses',exact=True).click();expect(dialog.locator('[data-connection-field="model"]')).to_be_visible()
    if phase=='fresh':
     dialog.locator('[data-connection-field="model"]').fill('owned-not-called-response-model');dialog.locator('[data-connection-field="credentialReference"]').fill('env:CONFECTORY_AI_ENTRY_OWNED_BINDING')
    else:expect(dialog.locator('[data-connection-field="model"]')).to_have_value('owned-not-called-response-model')
    dialog.locator('[data-connection-attempt]').click();expect(dialog.locator('[data-connection-result]')).to_have_attribute('data-connection-outcome','approval-required')
    state=public_state(url);assert state['projectId']=='' and state['cards']==[] and state['connectionSetup']['outcome']['authenticated'] is False and state['connectionSetup']['outcome']['networkContacted'] is False
    dialog.locator('[data-connection-back]').click();expect(dialog.locator('[data-connection-form]')).to_be_empty()
    dialog.get_by_role('button',name='Codex',exact=True).click();expect(dialog.locator('[data-method-choice]')).to_have_count(3)
    for method in ('local-cli','desktop-ide','chatgpt-work'):
     dialog.locator('[data-method-choice="'+method+'"]').click();expect(dialog.locator('[data-method-choice="'+method+'"]').first).to_have_attribute('aria-pressed','true')
     values={'local-cli':{'model':'owned-not-called-codex-model','executable':'/usr/bin/python3','managedHome':str(managed),'credentialReference':'codex:managed'},'desktop-ide':{'sessionSocket':str(root/'owned-not-started.sock')},'chatgpt-work':{'workspaceTriggerId':'agtch_owned_entry','workspaceCredentialReference':'env:CONFECTORY_AI_ENTRY_WORK_BINDING'}}[method]
     for name,value in values.items():dialog.locator('[data-connection-field="'+name+'"]').fill(value)
     dialog.locator('[data-connection-attempt]').click();expect(dialog.locator('[data-connection-result]')).to_have_attribute('data-connection-outcome','blocked')
     state=public_state(url);assert state['projectId']=='' and state['cards']==[];outcome=state['connectionSetup']['outcome'];assert outcome['authenticated'] is False and outcome['networkContacted'] is False
     expect(dialog.locator('[data-connection-result]')).to_contain_text('실계정 연결은 차단')
    dialog.locator('[data-connection-cancel]').click();expect(dialog).to_have_count(0);expect(page.locator('.home-grid')).to_be_visible()
    page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='AI Agent 연결',exact=True);dialog.get_by_role('button',name='Codex',exact=True).click()
    expect(dialog.locator('[data-method-choice="chatgpt-work"]')).to_have_attribute('aria-pressed','true');expect(dialog.locator('[data-connection-field="workspaceTriggerId"]')).to_have_value('agtch_owned_entry')
    dialog.locator('[data-connection-back]').click();dialog.get_by_role('button',name='OpenAI Responses',exact=True).click();expect(dialog.locator('[data-connection-field="model"]')).to_have_value('owned-not-called-response-model')
    dialog.locator('[data-connection-cancel]').click();expect(page.locator('.home-grid')).to_be_visible()
    if phase=='existing':assert json.loads(page.evaluate("localStorage.getItem('confectory-participant-layout')"))['legacyAgent']=='Confectory.Agent.Responses::Connection'
    profiles.append({'phase':phase,'homeEntry':True,'providers':['OpenAI Responses','Codex'],'methods':['local-cli','desktop-ide','chatgpt-work'],'projectUnchanged':True,'cancelReenter':True,'actualAccountOrRequest':False})
   except Exception:
    print('Evidence',root,flush=True);print('Public state',json.dumps(public_state(url)),flush=True);raise
   finally:page.close();stop(host,log)
  assert not errors,errors;assert not list(managed.iterdir())
 finally:browser.close()
(root/'verification.json').write_text(json.dumps(profiles,indent=2)+'\n')
print('PASS actual Home AI Agent entry: inline providers/methods/settings/readiness, fresh and saved state, back/cancel/reentry; no account or request',root)
