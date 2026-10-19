from editor_navigation import goto_editor
"""Actual novice Home flow; legacy installations and preparation are owned fixtures only."""
import hashlib,json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time,urllib.request
from playwright.sync_api import sync_playwright,expect
expect.set_options(timeout=30000)
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text());root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-install-guide-ui-'))
profile=root/'profile';profile.mkdir();default_home=profile/'.codex';default_home.mkdir();home=root/'account-home';home.mkdir();data=root/'local-app-data';bin_dir=root/'tools';bin_dir.mkdir()
triple=('aarch64' if os.uname().machine=='aarch64' else 'x86_64')+'-unknown-linux-musl';package='codex-linux-'+('arm64' if triple.startswith('aarch64') else 'x64')
def fixture(path,version):
 path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(repo/'tests/protocol/codex_owned_stdio.py',path);path.chmod(0o700);(path.parent/'owned-control.json').write_text(json.dumps({'version':version}));return path
legacy=fixture(data/'Confectory/Codex/node_modules/@openai'/package/'vendor'/triple/'bin/codex','0.159.2')
packengine=fixture(data/'PackEngine/Codex/node_modules/@openai/codex/vendor'/triple/'codex/codex','0.159.0-alpha.3')
environment=fixture(root/'environment-only/codex','0.159.2');hint=fixture(root/'hint-only/codex','0.159.0-alpha.3');binaries=[legacy,packengine,environment,hint]
preferences=[data/'Confectory/codex-path.txt',data/'PackEngine/codex-path.txt']
for path,target in zip(preferences,[hint,packengine]):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(str(target)+'\n')
before={path:path.read_bytes() for path in binaries+preferences}
installer=bin_dir/'npm';installer.write_text('#!/bin/sh\ntouch "'+str(root/'installation-was-run')+'"\nexit 1\n');installer.chmod(0o700)
env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(repo),CONFECTORY_ENTRY_STORAGE=str(root/'storage'),CONFECTORY_HOME_STORAGE=str(root/'storage'),HOME=str(profile),CODEX_HOME=str(home),LOCALAPPDATA=str(data),CONFECTORY_CODEX=str(environment),PACKENGINE_CODEX=str(environment),PATH=os.pathsep.join([str(bin_dir),str(pathlib.Path(env['CONFECTORY_DOTNET']).parent),'/usr/bin','/bin']))
for name in ['CONFECTORY_WEB_PROJECT','NPM_CONFIG_PREFIX','npm_config_prefix']:env.pop(name,None)
def requests(path):
 log=path.parent/'owned-requests.jsonl';return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
def total():return sum(len(requests(path)) for path in binaries)
def boot(label):
 log=(root/(label+'.log')).open('w');host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);deadline=time.monotonic()+60
 while time.monotonic()<deadline:
  text=(root/(label+'.log')).read_text()
  for line in text.splitlines():
   if line.startswith('CONFECTORY_WEB_UI '):return host,log,line.split(' ',1)[1]
  assert host.poll() is None,text;time.sleep(.1)
 raise AssertionError('Home host did not start')
def state(url):
 origin,token=url.split('/#')
 def send(body):
  request=urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token})
  with urllib.request.urlopen(request,timeout=20) as response:return json.load(response)
 for _ in range(400):
  view=send({'op':'mount'})
  if view.get('error',{}).get('code')=='busy':time.sleep(.01);continue
  assert view['ok'],view;break
 else:raise AssertionError('State stayed busy')
 try:return view['state']
 finally:assert send({'op':'dispose','view':view['view']})['ok']
errors=[];external=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'])
 try:
  for phase in ['fresh','saved']:
   host,log,url=boot(phase);page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda error:errors.append(str(error)));page.route('https://**/*',lambda route:(external.append(route.request.url),route.abort()))
   try:
    goto_editor(page,url);expect(page.locator('.home-grid')).to_be_visible();page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='사용할 AI',exact=True);dialog.get_by_role('button',name='Codex',exact=True).click();dialog.locator('[data-codex-route="provider"]').click()
    expect(dialog.locator('[data-candidate-kind="executable"]')).to_have_count(len(binaries));expect(dialog.locator('[data-connection-advanced]')).not_to_have_attribute('open','');expect(dialog.locator('[data-connection-field="executable"]')).not_to_be_visible()
    def simple():
     visible=dialog.inner_text()
     for technical in [str(root),'app-server','local-cli','codex:managed','CODEX_HOME','0.159.2','0.159.0-alpha.3']:
      assert technical not in visible,(technical,visible)
    simple()
    if phase=='saved':
     setup=state(url)['connectionSetup'];assert next(row['value'] for row in setup['schema']['rows'] if row['name']=='model')=='owned-protocol-fixture';assert next(row['value'] for row in setup['schema']['rows'] if row['name']=='executable')==str(packengine);assert total()==saved_requests;dialog.locator('[data-connection-cancel]').click();continue
    discovery=state(url)['connectionSetup']['discovery'];assert discovery['pathHintFilesRead']==2;assert discovery['credentialRead'] is False and discovery['processStarted'] is False;assert not total()
    assert {row['path'] for row in discovery['executables']}=={str(path) for path in binaries}
    def choose(kind,path):
     candidates=state(url)['connectionSetup']['discovery']['homes' if kind=='home' else 'executables'];candidate=next(row['id'] for row in candidates if row['path']==str(path));dialog.locator('[data-candidate-choice="'+candidate+'"]').click()
    def prepare():
     dialog.locator('[data-basic-check]').click();expect(dialog.locator('[data-check-consent]')).to_have_count(4)
    def approve(outcome):
     for box in dialog.locator('[data-check-consent]').all():box.check()
     dialog.locator('[data-connection-check-start]').click();expect(dialog.locator('[data-connection-result]')).to_have_attribute('data-connection-outcome',outcome)
    choose('executable',legacy);choose('home',home);simple();prepare();simple();assert not total();approve('blocked');expect(dialog.locator('[data-connection-result]')).to_have_attribute('data-connection-code','provider-version-unverified');simple();assert state(url)['connectionSetup']['outcome']['version']=='0.159.2';assert not any(row['method']=='account/read' for row in requests(legacy));expect(dialog.locator('[data-install-guide]')).to_have_attribute('open','')
    dialog.locator('[data-connection-diagnostics] > summary').click();expect(dialog.locator('[data-connection-diagnostics]')).to_contain_text('0.159.2');expect(dialog.locator('[data-connection-diagnostics]')).to_contain_text('비호환으로 입증된 것은 아닙니다');dialog.locator('[data-connection-diagnostics] > summary').click()
    choose('executable',packengine);simple();prepare();approve('models-found');simple();expect(dialog.locator('[data-catalogue-model]')).to_have_value('');dialog.locator('[data-catalogue-model]').select_option('owned-protocol-fixture');dialog.locator('[data-catalogue-select]').click();expect(dialog.locator('[data-check-consent]')).to_have_count(4);assert all(not box.is_checked() for box in dialog.locator('[data-check-consent]').all());assert state(url)['connectionSetup']['outcome']['supported'] is False
    assert not any(row['method'] in ['thread/start','turn/start'] for path in binaries for row in requests(path));simple();dialog.locator('[data-connection-cancel]').click()
    page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='사용할 AI',exact=True);dialog.get_by_role('button',name='Codex',exact=True).click();dialog.locator('[data-codex-route="provider"]').click();simple();before_rescan=total()
    hidden=list(binaries)
    for path in hidden:path.rename(path.with_name(path.name+'-hidden'))
    dialog.locator('[data-discover-connection]').click();expect(dialog.locator('[data-candidate-kind="executable"]')).to_have_count(0);assert state(url)['connectionSetup']['discovery']['state']=='not-found';expect(dialog.locator('[data-install-guide]')).to_have_attribute('open','');simple();assert total()==before_rescan
    dialog.locator('[data-installation-details] > summary').click();dialog.locator('[data-install-target]').select_option('windows-x64');expect(dialog.locator('[data-install-download]')).to_have_attribute('href','https://github.com/openai/codex/releases/download/rust-v0.159.0-alpha.3/codex-x86_64-pc-windows-msvc.exe.zip');dialog.locator('[data-install-target]').select_option('windows-arm64');expect(dialog.locator('[data-install-download]')).to_have_attribute('href','https://github.com/openai/codex/releases/download/rust-v0.159.0-alpha.3/codex-aarch64-pc-windows-msvc.exe.zip');expect(dialog.locator('[data-supported-version]')).to_have_text('0.159.0-alpha.3');dialog.locator('[data-install-target]').select_option(state(url)['connectionSetup']['installationGuide']['defaultTarget']);dialog.locator('[data-installation-details] > summary').click();simple()
    # Simulate user preparation with an owned fixture, rather than running an installer.
    parallel=fixture(data/'Confectory/Codex-0.159.0-alpha.3/codex','0.159.0-alpha.3');binaries.append(parallel);dialog.locator('[data-guide-rescan]').click();expect(dialog.locator('[data-candidate-kind="executable"]')).to_have_count(1);expect(dialog.locator('[data-install-guide]')).to_have_attribute('open','');assert total()==before_rescan;assert next(row['value'] for row in state(url)['connectionSetup']['schema']['rows'] if row['name']=='executable')==str(packengine)
    for path in hidden:path.with_name(path.name+'-hidden').rename(path)
    dialog.locator('[data-discover-connection]').click();expect(dialog.locator('[data-candidate-kind="executable"]')).to_have_count(len(binaries));simple();dialog.locator('[data-connection-cancel]').click();saved_requests=total()
    assert state(url)['projectId']=='' and state(url)['cards']==[]
   except Exception:
    print('Evidence',root,flush=True);page.screenshot(path=str(root/'failure.png'));print('State',json.dumps(state(url)),flush=True);raise
   finally:
    page.close()
    if host.poll() is None:os.killpg(host.pid,signal.SIGTERM)
    host.wait(timeout=15);log.close()
  assert not errors and not external,(errors,external);assert all(path.read_bytes()==contents for path,contents in before.items());assert not (root/'installation-was-run').exists();assert not list(home.iterdir()) and not list(default_home.iterdir());assert not any(row['method'] in ['account/login/start','thread/start','turn/start'] for path in binaries for row in requests(path))
  (root/'verification.json').write_text(json.dumps({'noviceFlowWithoutPathsIdsVersions':True,'legacyManagedFoldersAndPathHints':True,'multipleVersions':True,'unvalidated1592BeforeAccount':True,'missingDistinctFromUnvalidated':True,'officialOsPreparationGuide':True,'cancelAndRediscovery':True,'existingInstallationAndSavedSettingsPreserved':True,'realAccountTokenPaidCallOrInstaller':False},indent=2)+'\n');print('PASS actual Home legacy Codex discovery and novice preparation guide; owned fixtures only',root)
 finally:browser.close()
