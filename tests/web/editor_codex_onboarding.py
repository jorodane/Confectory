"""Production CLI onboarding with owned runtimes/accounts and a loopback archive.

Only Discover/PreparationInfo are fixture providers. Every state transition,
installer, device login, account/model validation and Helper transport is real
Confectory code. No real OAuth, user credentials, inference or external relay.
"""
import hashlib,http.server,io,json,os,pathlib,re,shutil,signal,subprocess,sys,tarfile,tempfile,threading,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor

expect.set_options(timeout=30000)
repo=pathlib.Path(sys.argv[1]).resolve();root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-cli-flow-'));print('FIXTURE '+str(root),flush=True)
owned=root/'engine';editor=owned/'examples/editor-home';shutil.copytree(repo/'examples/editor-home',editor,ignore=shutil.ignore_patterns('.confectory'))
(owned/'targets/dotnet').mkdir(parents=True);(owned/'targets/dotnet/pack.cpack').write_text('pack Owned.Marker version "1" {standalone false;}')
pack=root/'codex-pack';shutil.copytree(repo/'packs/agent-codex',pack)
for file in editor.glob('*.cpack'):
    text=file.read_text().replace('../../',str(repo)+'/').replace(json.dumps(str(repo/'packs/agent-codex/pack.cpack')),json.dumps(str(pack/'pack.cpack')));file.write_text(text)
(pack/'PreparationInfo.csbody').write_text('return System.IO.File.ReadAllText('+json.dumps(str(root/'active-info.json'))+');')
(pack/'Discover.csbody').write_text('''
var result=System.Text.Json.Nodes.JsonNode.Parse(System.IO.File.ReadAllText(PATH))!;
var prepared=System.Text.Json.Nodes.JsonNode.Parse(calls.Storage.Invoke("scan","{}"))!;
foreach(var path in prepared["installations"]!.AsArray())result["executables"]!.AsArray().Add(new System.Text.Json.Nodes.JsonObject{["path"]=path!.DeepClone(),["selectable"]=true,["source"]="Confectory prepared installation"});
foreach(var path in prepared["homes"]!.AsArray())result["homes"]!.AsArray().Add(new System.Text.Json.Nodes.JsonObject{["path"]=path!.DeepClone(),["selectable"]=true,["source"]="Confectory prepared account"});
return result.ToJsonString();
'''.replace('PATH',json.dumps(str(root/'active-discovery.json'))))
runtime=root/'codex';runtime.write_text((repo/'tests/protocol/codex_onboarding_owned.py').read_text().replace('__FIXTURE_ROOT__',str(root)));runtime.chmod(0o700)
archive=io.BytesIO()
with tarfile.open(fileobj=archive,mode='w:gz') as tar:
    info=tarfile.TarInfo('codex-owned');data=runtime.read_bytes();info.size=len(data);info.mode=0o700;tar.addfile(info,io.BytesIO(data))
archive=archive.getvalue()
class Assets(http.server.BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        case=pathlib.Path(json.loads((root/'active.json').read_text())['case']);(case/'download-started').write_text('owned')
        payload=(bytes([archive[0]^1])+archive[1:]) if json.loads((case/'control.json').read_text()).get('badArchive') else archive
        try:
            self.send_response(200);self.send_header('Content-Length',str(len(payload)));self.end_headers()
            while json.loads((case/'control.json').read_text()).get('holdDownload'):time.sleep(.02)
            self.wfile.write(payload)
        except (BrokenPipeError,ConnectionResetError):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Assets);threading.Thread(target=server.serve_forever,daemon=True).start()
env=os.environ.copy();env.update(CONFECTORY_DOTNET=env.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'),CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(owned),CONFECTORY_ELEMENT_AUTHORING_HOST=str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'),CONFECTORY_PROJECT_EXECUTION_HOST=str(repo/'targets/project-execution-host/bin/Release/net10.0/Confectory.ProjectExecutionHost.dll'))
env['PATH']=str(pathlib.Path(env['CONFECTORY_DOTNET']).parent)+os.pathsep+env['PATH'];env.pop('CONFECTORY_WEB_PROJECT',None)
with (root/'build.json').open('w') as out,(root/'build.err').open('w') as err:built=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(editor/'project.cpack'),'linux'],env=env,cwd=repo,stdout=out,stderr=err,timeout=180)
report=json.loads((root/'build.json').read_text());assert built.returncode==0 and report.get('tool',{}).get('ok'),report.get('diagnostics')
cases=['authenticated','logged-out','install','multiple-accounts','model-selection','single-model','configured-model','no-models','cancel-login','cancel-install','bad-install','cancel-probe','unsupported-runtime','identity-change','failed-login','switch-provider']
if os.environ.get('CONFECTORY_ONBOARDING_CASES'):cases=os.environ['CONFECTORY_ONBOARDING_CASES'].split(',')
evidence=[];errors=[];external=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'])
 try:
  for name in cases:
   case=root/name;case.mkdir();storage=case/'profile';control={'singleModel':name=='single-model','noDefault':name in ('model-selection','single-model'),'noModels':name=='no-models','configuredModel':'fixture-two' if name=='configured-model' else '', 'failLogin':name=='failed-login','holdVersion':name=='cancel-probe','holdDownload':name=='cancel-install','badArchive':name=='bad-install','version':'0.159.2' if name=='unsupported-runtime' else '0.159.0-alpha.3'}
   def write_control(**values):control.update(values);(case/'control.json').write_text(json.dumps(control))
   write_control();(root/'active.json').write_text(json.dumps({'case':str(case)}))
   absent=name in ('install','cancel-install','bad-install');logged_out=name in ('logged-out','install','cancel-login','cancel-install','bad-install','failed-login','switch-provider')
   discovery={'executables':[] if absent else [{'path':str(runtime),'selectable':True,'source':'owned fixture'}],'homes':[]}
   homes=[]
   for index in range(2 if name=='multiple-accounts' else 1):
    home=case/('account-'+str(index));home.mkdir();(home/'original.keep').write_bytes(b'owned original account state\x00');homes.append(home);discovery['homes'].append({'path':str(home),'selectable':True,'source':'owned fixture'})
    if not logged_out:(home/'.owned-account.json').write_text(json.dumps({'type':'chatgpt','email':('alice' if index==0 else 'bob')+'@fixture.invalid','planType':'plus'}))
   (root/'active-discovery.json').write_text(json.dumps(discovery))
   spec={'supported':True,'publisher':'OWNED FIXTURE','version':'0.159.0-alpha.3','target':'linux-x64','asset':'codex-owned.tar.gz','url':'http://127.0.0.1:'+str(server.server_port)+'/runtime','sha256':hashlib.sha256(archive).hexdigest(),'archiveKind':'tar.gz','archiveExecutable':'codex-owned','binaryName':'codex','rootBase':str(case/'managed'),'maxDownloadBytes':268435456,'maxUnpackedBytes':1073741824,'maxEntries':128,'downloadTimeoutSeconds':60}
   (root/'active-info.json').write_text(json.dumps(spec));run_env=env.copy();run_env.update(CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'));log_path=case/'host.log';log=log_path.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=run_env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)));invocations=[]
   page.on('request',lambda r:invocations.append(r.post_data_json.get('endpoint')) if r.url.endswith('/api/request') and r.post_data_json.get('op')=='invoke' else None)
   def requests():return [json.loads(line) for line in (case/'requests.jsonl').read_text().splitlines()] if (case/'requests.jsonl').exists() else []
   def wait_file(file):
    for _ in range(500):
     if file.exists():return
     page.wait_for_timeout(20)
    raise AssertionError('owned fixture marker missing: '+str(file))
   try:
    for _ in range(600):
     urls=[line.split(' ',1)[1] for line in log_path.read_text().splitlines() if line.startswith('CONFECTORY_WEB_UI ')]
     if urls:url=urls[-1];break
     assert host.poll() is None,log_path.read_text()[-2000:];time.sleep(.1)
    else:raise AssertionError('host timeout')
    origin,token=url.split('/#')
    def send(body):
     req=urllib.request.Request(origin+'/api/request',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Confectory-Session':token})
     with urllib.request.urlopen(req,timeout=20) as response:return json.load(response)
    def mount():
     for _ in range(400):
      value=send({'op':'mount'})
      if value.get('error',{}).get('code')=='busy':time.sleep(.01);continue
      assert value['ok'],value;return value
     raise AssertionError('mount busy')
    def state():
     value=mount()
     try:return value['state']
     finally:assert send({'op':'dispose','view':value['view']})['ok']
    def api(action,**args):
     for attempt in range(4):
      view=mount();rid=uuid.uuid4().hex
      try:
       accepted=send({'op':'invoke','view':view['view'],'scope':view['scope'],'requestId':rid,'expectedRevision':view['revision'],'endpoint':'codexOnboarding','input':{'action':action,**args}});assert accepted['ok'],accepted
       for _ in range(600):
        result=send({'op':'update','view':view['view'],'scope':view['scope']})
        rows=[r for r in result.get('results',[]) if r['requestId']==rid]
        if rows:break
        time.sleep(.01)
       else:raise AssertionError('API pending')
       row=rows[0]
      finally:send({'op':'dispose','view':view['view']})
      if row.get('error',{}).get('code')=='stale_revision' and attempt<3:continue
      return row
    def route(request):
     if request.request.url.startswith(origin+'/') or request.request.url.startswith('data:'):request.continue_()
     else:external.append(request.request.url);request.abort()
    page.route('**/*',route);goto_editor(page,url);page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);dialog.get_by_role('button',name='Codex',exact=True).click();expect(dialog.locator('[data-cli-login]')).to_be_enabled();assert not requests();expect(dialog.locator('[data-discover-connection]')).to_have_count(0);expect(dialog.locator('[data-mcp-panel]')).to_have_count(0);page.screenshot(path=str(case/'initial.png'))
    initial=state();assert initial['helperAgents']['agents']==[] and initial['projectId']==''
    # Initial repeated clicks never start a second workflow.
    dialog.locator('[data-cli-login]').evaluate('(b)=>{b.click();b.click();}')
    if name=='cancel-probe':
     wait_file(case/'version-started');dialog.locator('[data-cli-stop]').click();expect(dialog.locator('[data-codex-onboarding]')).to_have_attribute('data-step',re.compile('cancelled|cancelling'));write_control(holdVersion=False);expect(dialog.locator('[data-cli-login]')).to_be_enabled();dialog.locator('[data-cli-login]').click()
    if absent or name=='unsupported-runtime':
     expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 설치');page.screenshot(path=str(case/'install-consent.png'))
     if name=='unsupported-runtime':
      assert not [r for r in requests() if r['method']=='account/read'];dialog.locator('[data-connection-cancel]').click();print('PASS scenario unsupported-runtime',flush=True);continue
     consent=state()['codexOnboarding']['token'];dialog.locator('[data-cli-consent]').click();assert api('approve',token=consent)['ok']
     if name=='cancel-install':
      wait_file(case/'download-started');page.screenshot(path=str(case/'installing.png'));dialog.locator('[data-cli-stop]').click();expect(dialog.locator('[data-codex-onboarding]')).to_have_attribute('data-step',re.compile('cancelled|cancelling'));write_control(holdDownload=False)
      expect(dialog.locator('[data-cli-login]')).to_be_enabled();dialog.locator('[data-cli-login]').click();expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 설치');dialog.locator('[data-cli-consent]').click()
     if name=='bad-install':
      expect(dialog.locator('[data-cli-retry]')).to_be_visible();page.screenshot(path=str(case/'install-failed.png'));write_control(badArchive=False);dialog.locator('[data-cli-retry]').click();expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 설치');dialog.locator('[data-cli-consent]').click()
    if logged_out:
     expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 로그인');page.screenshot(path=str(case/'login-consent.png'));consent=state()['codexOnboarding']['token'];dialog.locator('[data-cli-consent]').click();assert api('approve',token=consent)['ok'];expect(dialog.locator('[data-cli-code]')).to_have_text('TEST-4240');expect(dialog.locator('[data-cli-official-login]')).to_have_attribute('href','https://auth.openai.com/codex/device');page.screenshot(path=str(case/'device-login.png'))
     if name=='switch-provider':
      dialog.get_by_role('button',name='OpenAI Responses',exact=True).click();expect(dialog.locator('[data-codex-onboarding]')).to_have_count(0);(case/'complete-login').write_text('owned');page.wait_for_timeout(500);assert state()['helperAgents']['agents']==[];dialog.get_by_role('button',name='Codex',exact=True).click();expect(dialog.locator('[data-cli-login]')).to_be_enabled();page.screenshot(path=str(case/'switched-cancelled.png'));print('PASS scenario switch-provider',flush=True);continue
     if name=='cancel-login':
      dialog.locator('[data-connection-cancel]').click();page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);dialog.get_by_role('button',name='Codex',exact=True).click();expect(dialog.locator('[data-cli-login]')).to_be_enabled();dialog.locator('[data-cli-login]').click();expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 로그인');dialog.locator('[data-cli-consent]').click();expect(dialog.locator('[data-cli-code]')).to_have_text('TEST-4240')
     (case/'complete-login').write_text('owned')
     if name=='failed-login':
      expect(dialog.locator('[data-cli-retry]')).to_be_visible();page.screenshot(path=str(case/'login-failed.png'));write_control(failLogin=False);(case/'complete-login').unlink();dialog.locator('[data-cli-retry]').click();expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 로그인');dialog.locator('[data-cli-consent]').click();expect(dialog.locator('[data-cli-code]')).to_have_text('TEST-4240');(case/'complete-login').write_text('owned')
    else:
     if name=='no-models':
      expect(dialog.locator('[data-cli-retry]')).to_be_visible();assert state()['helperAgents']['agents']==[];page.screenshot(path=str(case/'models-empty.png'));write_control(noModels=False);dialog.locator('[data-cli-retry]').click()
     expect(dialog.locator('[data-cli-account]')).to_have_count(2 if name=='multiple-accounts' else 1);page.screenshot(path=str(case/'account-choice.png'))
     assert 'alice@fixture.invalid' in dialog.locator('[data-cli-account]').first.inner_text()
     if name=='multiple-accounts':expect(dialog.locator('[data-cli-account]').nth(1)).to_contain_text('bob@fixture.invalid')
     # A foreign selection token cannot become an account or registration.
     rejected=api('choose-account',token='foreign-token',account='foreign-account');assert not rejected['ok'];assert state()['helperAgents']['agents']==[]
     choice=state()['codexOnboarding'];rejected=api('choose-account',token=choice['token'],account='foreign-account');assert not rejected['ok'];assert state()['helperAgents']['agents']==[]
     dialog.locator('[data-cli-account]').nth(1 if name=='multiple-accounts' else 0).click();assert api('choose-account',token=choice['token'],account=choice['accounts'][1 if name=='multiple-accounts' else 0]['id'])['ok']
    if name=='model-selection':
     expect(dialog.locator('[data-cli-model]')).to_be_visible();page.screenshot(path=str(case/'model-choice.png'));dialog.locator('[data-cli-model]').select_option('fixture-two');dialog.locator('[data-cli-model-confirm]').click()
    expect(dialog.locator('[data-cli-done]')).to_be_enabled(timeout=40000);page.screenshot(path=str(case/'ready.png'));ready=state();assert ready['projectId']=='' and len(ready['helperAgents']['agents'])==1;agent=ready['helperAgents']['agents'][0];assert agent['state']=='ready' and agent['accountVerified'] is False and agent['accountMetadataVerified'] is True,agent
    assert agent['model']==('fixture-two' if name in ('model-selection','configured-model') else 'fixture-one')
    expected_email='new-account@fixture.invalid' if logged_out else ('bob@fixture.invalid' if name=='multiple-accounts' else 'alice@fixture.invalid');assert agent['accountIdentity']['email']==expected_email,agent
    assert not [r for r in requests() if r['method']=='turn/start']
    before=len(requests());dialog.locator('[data-cli-done]').click();expect(dialog).to_have_count(0)
    page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);dialog.get_by_role('button',name='Codex',exact=True).click();expect(dialog.locator('[data-cli-done]')).to_be_enabled();assert len(requests())==before,'reopen repeated completed steps'
    dialog.locator('[data-cli-offline]').click();expect(dialog.locator('[data-cli-login]')).to_have_text('다시 연결');assert state()['helperAgents']['agents'][0]['state']=='offline';dialog.locator('[data-cli-login]').click();expect(dialog.locator('[data-cli-done]')).to_be_enabled();assert state()['helperAgents']['agents'][0]['state']=='ready' and len(requests())==before
    dialog.locator('[data-cli-done]').click()
    if name=='authenticated':
     page.locator('#add-helper').click();creator=page.locator('[data-v508-helper]');creator.locator('#participant-name').fill('Owned CLI Helper');creator.locator('#participant-description').fill('Owned account metadata and protocol only');creator.locator('button[type=submit]').click();expect(creator).to_have_count(0);page.locator('.home-side [data-helper]').first.click();card=page.locator('.participant-expanded-card');card.locator('textarea').fill('owned CLI message');card.locator('[data-global-prepare]').click();approval=page.locator('[data-global-approval]');expect(approval.locator('[data-global-start]')).to_be_disabled()
     for item in approval.locator('[data-global-permission]').all():item.check()
     expect(approval.locator('[data-global-start]')).to_be_enabled();approval.locator('[data-global-start]').click();expect(card.locator('.global-helper-messages')).to_contain_text('OWNED CLI HELPER REPLY',timeout=30000);page.screenshot(path=str(case/'helper-reply.png'));assert len([r for r in requests() if r['method']=='turn/start'])==1
    if name=='identity-change':
     write_control(changedIdentity=True);page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);dialog.get_by_role('button',name='Codex',exact=True).click();expect(dialog.locator('[data-cli-change-account]')).to_be_enabled();dialog.locator('[data-cli-change-account]').click();expect(dialog.locator('[data-cli-account]')).to_have_count(1);expect(dialog.locator('[data-cli-account]')).to_contain_text('changed@fixture.invalid');assert state()['helperAgents']['agents'][0]['accountIdentity']['email']=='alice@fixture.invalid';dialog.locator('[data-cli-account]').click();expect(dialog.locator('[data-cli-done]')).to_be_enabled();assert state()['helperAgents']['agents'][0]['accountIdentity']['email']=='changed@fixture.invalid';page.screenshot(path=str(case/'changed-account.png'))
    if name=='authenticated':
     # A new engine process restores the confirmed account identity, then renews
     # readiness without asking for another OAuth login or account choice.
     login_count=len([r for r in requests() if r['method']=='account/login/start']);page.close();os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=15);log.close();log=log_path.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=run_env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
     for _ in range(600):
      urls=[line.split(' ',1)[1] for line in log_path.read_text().splitlines() if line.startswith('CONFECTORY_WEB_UI ')]
      if urls:url=urls[-1];break
      assert host.poll() is None;time.sleep(.1)
     origin,token=url.split('/#');page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)));page.route('**/*',route);page.goto(url);expect(page.locator('#add-agent')).to_be_enabled(timeout=30000);page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);dialog.get_by_role('button',name='Codex',exact=True).click();expect(dialog.locator('[data-cli-login]')).to_be_enabled();dialog.locator('[data-cli-login]').click();expect(dialog.locator('[data-cli-done]')).to_be_enabled(timeout=40000);assert len([r for r in requests() if r['method']=='account/login/start'])==login_count;assert state()['helperAgents']['agents'][0]['accountIdentity']['email']=='alice@fixture.invalid';page.screenshot(path=str(case/'cold-ready.png'))
    for home in homes:assert (home/'original.keep').read_bytes()==b'owned original account state\x00'
    assert 'mcpBridge' not in invocations and not any('site' in x.lower() for x in invocations if x)
    print('PASS scenario '+name,flush=True)
   except BaseException:
    page.screenshot(path=str(case/'failure.png'));print('FAILED '+name+' '+str(case),flush=True);print('HOST '+log_path.read_text()[-2500:],flush=True);print('STATE '+json.dumps(state(),ensure_ascii=False)[-9000:],flush=True);print('PAGE '+page.locator('body').inner_text()[-3000:],flush=True);raise
   finally:
    evidence.append({'scenario':name,'requests':requests(),'uiInvocations':invocations});write_control(holdVersion=False,holdDownload=False);page.close()
    if host.poll() is None:os.killpg(host.pid,signal.SIGTERM)
    host.wait(timeout=15);log.close();(root/'evidence.json').write_text(json.dumps({'cases':evidence,'pageErrors':errors,'externalRequests':external},ensure_ascii=False,indent=2))
 finally:browser.close();server.shutdown()
assert not errors and not external,(errors,external)
print('PASS owned CLI login-first integration '+str(root),flush=True)
