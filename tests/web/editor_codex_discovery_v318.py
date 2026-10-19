"""Actual Home discovery and approved catalogue; all installations/accounts are owned fixtures."""
import json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request
from playwright.sync_api import sync_playwright,expect
expect.set_options(timeout=30000)
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-discovery-ui-'))
profile=root/'owned-profile';profile.mkdir();physical_home=root/'owned-default-home';physical_home.mkdir();default_home=profile/'.codex';default_home.symlink_to(physical_home,target_is_directory=True);managed=root/'owned-CODEX_HOME';managed.mkdir();bins=[root/'bin-a',root/'bin-b']
for directory in bins:
 directory.mkdir();shutil.copyfile(repo/'tests/protocol/codex_owned_stdio.py',directory/'codex');(directory/'codex').chmod(0o700)
npm=root/'owned-npm-prefix';npm_bin=npm/'bin';npm_bin.mkdir(parents=True);wrapper=npm/'lib/node_modules/@openai/codex/bin/codex.js';wrapper.parent.mkdir(parents=True);wrapper.write_text('throw new Error("OWNED WRAPPER MUST NEVER EXECUTE");\n');npm_link=npm_bin/'codex';npm_link.symlink_to(wrapper)
triple=('aarch64' if os.uname().machine=='aarch64' else 'x86_64')+'-unknown-linux-musl';native=npm/'lib/node_modules/@openai'/('codex-linux-arm64' if triple.startswith('aarch64') else 'codex-linux-x64')/'vendor'/triple/'bin/codex';native.parent.mkdir(parents=True);shutil.copyfile(repo/'tests/protocol/codex_owned_stdio.py',native);native.chmod(0o700)
fixture_paths=[*(directory/'codex' for directory in bins),npm_link,native]
def control(index,**values):(bins[index]/'owned-control.json').write_text(json.dumps(values))
def requests(index):
 p=bins[index]/'owned-requests.jsonl';return [json.loads(line) for line in p.read_text().splitlines()] if p.exists() else []
env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_ENTRY_STORAGE=str(root/'storage'),CONFECTORY_HOME_STORAGE=str(root/'storage'),CODEX_HOME=str(managed),HOME=str(profile),NPM_CONFIG_PREFIX=str(npm),PATH=os.pathsep.join([str(x) for x in bins]+[str(pathlib.Path(env['CONFECTORY_DOTNET']).parent),'/usr/bin','/bin']));env.pop('CONFECTORY_WEB_PROJECT',None);env.pop('npm_config_prefix',None)
for name in ['LOCALAPPDATA','CONFECTORY_CODEX','PACKENGINE_CODEX']:env.pop(name,None)
errors=[]
def boot(label):
 stream=(root/(label+'.log')).open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True);deadline=time.monotonic()+60
 while time.monotonic()<deadline:
  for line in (root/(label+'.log')).read_text().splitlines():
   if line.startswith('CONFECTORY_WEB_UI '):return host,stream,line.split(' ',1)[1]
  assert host.poll() is None,(root/(label+'.log')).read_text();time.sleep(.1)
 raise AssertionError('Actual host did not start')
def state(url,endpoint=None,payload=None):
 origin,token=url.split('/#')
 def send(body):
  req=urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token})
  with urllib.request.urlopen(req,timeout=20) as response:return json.load(response)
 for _ in range(400):
  view=send({'op':'mount'})
  if view.get('error',{}).get('code')=='busy':time.sleep(.01);continue
  assert view['ok'],view;break
 else:raise AssertionError('Read-only state remained busy')
 try:
  if endpoint is None:return view['state']
  request_id='owned-cancelled-catalogue-'+str(time.monotonic_ns());envelope={'view':view['view'],'scope':view['scope']}
  assert send(dict(envelope,op='invoke',endpoint=endpoint,requestId=request_id,expectedRevision=view['revision'],input=payload))['ok']
  for _ in range(400):
   updated=send(dict(envelope,op='update'));assert updated['ok'],updated
   for row in updated.get('results',[]):
    if row['requestId']==request_id:return row
   time.sleep(.01)
  raise AssertionError('Cancelled catalogue replay remained pending')
 finally:assert send({'op':'dispose','view':view['view']})['ok']
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'])
 try:
  for phase in ['fresh','saved']:
   host,stream,url=boot(phase);page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda error:errors.append(str(error)))
   try:
    page.goto(url);expect(page.locator('.home-grid')).to_be_visible();page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='사용할 AI',exact=True);dialog.get_by_role('button',name='Codex',exact=True).click();dialog.locator('[data-codex-route="provider"]').click();dialog.locator('[data-connection-advanced] > summary').click();expect(dialog.locator('[data-discover-connection]')).to_be_visible()
    if phase=='saved':
     expect(dialog.locator('[data-connection-field="model"]')).to_have_value('owned-protocol-fixture');expect(dialog.locator('[data-connection-field="executable"]')).to_have_value(str(bins[0]/'codex'));expect(dialog.locator('[data-connection-field="managedHome"]')).to_have_value(str(managed));before=sum(len(requests(i)) for i in range(2));dialog.locator('[data-discover-connection]').click();expect(dialog.locator('[data-candidate-kind="executable"]')).to_have_count(4);assert sum(len(requests(i)) for i in range(2))==before;dialog.locator('[data-connection-cancel]').click();continue
    dialog.locator('[data-connection-field="model"]').fill('manual-saved-model');dialog.locator('[data-connection-save]').click();expect(dialog.locator('[data-connection-result]')).to_have_attribute('data-connection-outcome','saved')
    dialog.locator('[data-discover-connection]').click();expect(dialog.locator('[data-candidate-kind="executable"]')).to_have_count(4);expect(dialog.locator('[data-candidate-kind="home"]')).to_have_count(2);expect(dialog.locator('[data-connection-field="model"]')).to_have_value('manual-saved-model');assert not requests(0) and not requests(1)
    found=state(url)['connectionSetup']['discovery'];assert found['processStarted'] is False and found['credentialRead'] is False and found['accountVerified'] is False
    assert next(row for row in found['executables'] if row['path']==str(wrapper))['selectable'] is False;assert next(row for row in found['executables'] if row['path']==str(native))['selectable'] is True
    expect(dialog.locator('[data-candidate-kind="executable"][data-supported="false"]')).to_be_disabled();expect(dialog.locator('[data-candidate-kind="home"][data-supported="false"]')).to_be_disabled()
    def choose(kind,path):
     rows=state(url)['connectionSetup']['discovery']['homes' if kind=='home' else 'executables'];candidate=next(row['id'] for row in rows if row['path']==str(path));dialog.locator('[data-candidate-choice="'+candidate+'"]').click();expect(dialog.locator('[data-connection-field="'+('managedHome' if kind=='home' else 'executable')+'"]').first).to_have_value(str(path))
    choose('executable',bins[0]/'codex');choose('home',managed);expect(dialog.locator('[data-connection-field="credentialReference"]')).to_have_value('codex:managed');assert not requests(0)
    def prepare():
     old=(state(url)['connectionSetup']['outcome'] or {}).get('token');dialog.locator('[data-discover-models]').click();deadline=time.monotonic()+30
     while (state(url)['connectionSetup']['outcome'] or {}).get('token')==old:assert time.monotonic()<deadline;time.sleep(.03)
     expect(dialog.locator('[data-check-consent]')).to_have_count(4)
    def approve(outcome):
     for box in dialog.locator('[data-check-consent]').all():box.check()
     dialog.locator('[data-connection-check-start]').click();expect(dialog.locator('[data-connection-result]')).to_have_attribute('data-connection-outcome',outcome)
    dialog.locator('[data-connection-field="model"]').fill('');dialog.locator('[data-connection-save]').click();expect(dialog.locator('[data-connection-field="model"]')).to_have_value('');control(0,modelPages=[['owned-other-fixture'],['owned-protocol-fixture']])
    prepare();cancelled_token=state(url)['connectionSetup']['outcome']['token'];dialog.locator('[data-connection-cancel]').click();expect(dialog).not_to_be_visible()
    rejected=state(url,'startConnectionCheck',{'connection':'Confectory.Agent.Codex::Connection','token':cancelled_token,'approvals':{name:True for name in ['checkProcessApproved','checkAccountApproved','checkConfigurationApproved','checkStorageApproved']}});assert not rejected['ok'] and rejected['error']['code']=='consumer_error',rejected;assert not requests(0)
    page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='사용할 AI',exact=True);dialog.get_by_role('button',name='Codex',exact=True).click();dialog.locator('[data-codex-route="provider"]').click();dialog.locator('[data-connection-advanced] > summary').click();expect(dialog.locator('[data-connection-field="model"]')).to_have_value('')
    prepare();dialog.locator('[data-connection-check-start]').click();expect(dialog.locator('[data-check-consent]')).to_have_count(4);assert not requests(0)
    approve('models-found');expect(dialog.locator('[data-catalogue-model]')).to_be_visible();assert not any(row['method'] in ['thread/start','turn/start'] for row in requests(0));assert state(url)['connectionSetup']['outcome']['supported'] is False
    expect(dialog.locator('[data-connection-field="model"]')).to_have_value('');expect(dialog.locator('[data-catalogue-model]')).to_have_value('');assert [row['model'] for row in state(url)['connectionSetup']['outcome']['models']]==['owned-other-fixture','owned-protocol-fixture'];assert sum(row['method']=='model/list' for row in requests(0))==2;dialog.locator('[data-catalogue-model]').select_option('owned-protocol-fixture');dialog.locator('[data-catalogue-select]').click();expect(dialog.locator('[data-connection-field="model"]')).to_have_value('owned-protocol-fixture')
    # A different discovered installation is not executed or trusted until this explicit approval.
    choose('executable',bins[1]/'codex');control(1,version='0.1.0-unsupported');prepare();approve('blocked');expect(dialog.locator('[data-connection-result]')).to_have_attribute('data-connection-code','provider-protocol-unsupported');expect(dialog.locator('[data-connection-result]')).to_contain_text('0.1.0-unsupported');assert not any(row['method']=='account/read' for row in requests(1))
    choose('executable',bins[0]/'codex');control(0,holdCheck=True);prepare();approve('checking');dialog.locator('[data-connection-check-cancel]').click();expect(dialog.locator('[data-connection-result]')).to_have_attribute('data-connection-outcome','cancelled');control(0)
    # Rediscovery after disappearance preserves the selected path and manual/saved settings.
    for path in fixture_paths:path.rename(path.with_name(path.name+'-hidden'))
    dialog.locator('[data-discover-connection]').click();expect(dialog.locator('[data-candidate-kind="executable"]')).to_have_count(0);expect(dialog.locator('[data-installation-candidates]')).to_contain_text('고급 설정');expect(dialog.locator('[data-connection-field="model"]')).to_have_value('owned-protocol-fixture');expect(dialog.locator('[data-connection-field="executable"]')).to_have_value(str(bins[0]/'codex'))
    for path in fixture_paths:path.with_name(path.name+'-hidden').rename(path)
    dialog.locator('[data-discover-connection]').click();expect(dialog.locator('[data-candidate-kind="executable"]')).to_have_count(4);dialog.locator('[data-connection-cancel]').click();page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='사용할 AI',exact=True);dialog.get_by_role('button',name='Codex',exact=True).click();dialog.locator('[data-codex-route="provider"]').click();dialog.locator('[data-connection-advanced] > summary').click();expect(dialog.locator('[data-connection-field="model"]')).to_have_value('owned-protocol-fixture');dialog.locator('[data-connection-cancel]').click()
    assert state(url)['projectId']=='' and state(url)['cards']==[]
   except Exception:
    print('Evidence',root,flush=True);page.screenshot(path=str(root/'failure.png'));print('State',json.dumps(state(url)),flush=True);raise
   finally:
    page.close()
    if host.poll() is None:os.killpg(host.pid,signal.SIGTERM)
    host.wait(timeout=15);stream.close()
  assert not errors,errors;assert not any(row['method'] in ['account/login/start','turn/start'] for i in range(2) for row in requests(i));assert not list(managed.iterdir()) and not list(default_home.iterdir());assert not (native.parent/'owned-launch.json').exists()
  (root/'verification.json').write_text(json.dumps({'homeEntry':True,'multipleCandidates':True,'officialNpmNativeAndWrapper':True,'symlinkHomeDiagnostic':True,'blankModelAndPagedCatalogue':True,'cancelledConsentReplayRejected':True,'noInstallationManualFallback':True,'supportedAndUnsupportedVersion':True,'consentBeforeAccountAndModels':True,'catalogueNotGrant':True,'cancelAndRediscover':True,'freshAndSavedRetention':True,'realAccountTokenPaidRequest':False},indent=2)+'\n')
  print('PASS actual Home Codex candidate discovery and approved official catalogue; owned fixtures only',root)
 finally:browser.close()
