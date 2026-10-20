"""Production CLI onboarding with owned runtimes/accounts and a loopback archive.

Only Discover/PreparationInfo are fixture providers. Every state transition,
installer, official browser/device login, account/model validation and Helper transport is real
Confectory code. No real OAuth, user credentials, inference or external relay.
"""
import hashlib,http.server,socket,select,io,json,os,pathlib,re,shutil,signal,subprocess,sys,tarfile,tempfile,threading,time,urllib.request,uuid
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
        case=pathlib.Path(json.loads((root/'active.json').read_text())['case']);(case/'download-started').write_text('owned');count=case/'download-count';count.write_text(str(int(count.read_text())+1 if count.exists() else 1))
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
cases=['restart-mismatch','restart-expired-auth','restart-offline','restart-unverified','restart-renewal-failure','turn-remote-bad-request','turn-rpc-error','turn-exit','turn-bad-json','turn-foreign-event','turn-remote-http','turn-completed-error','authenticated','logged-out','install','multiple-accounts','model-selection','single-model','configured-model','no-models','cancel-login','cancel-install','bad-install','cancel-probe','unsupported-runtime','identity-change','failed-login','switch-provider','install-empty-home','install-process-exit','install-initialize-error','install-account-error','install-model-error','install-mixed-homes','install-process-start-error','bundled-policy','user-bundle-settings','unexpected-extension','web-search-policy','browser-open-failed','login-expired','callback-port-conflict','callback-rpc-conflict','invalid-login-url','device-fallback','device-cancel','device-retry','method-cleanup-failed','plugins-existing','install-plugins','plugins-browser','plugins-change','plugins-budget','plugins-cancel','plugins-login-blocked','plugins-restart-exit','plugins-restart-initialize','plugins-restart-config','plugins-login-restart-exit','plugins-post-browser','plugins-restart-start','plugins-restart-file-change','plugins-login-restart-start']
if os.environ.get('CONFECTORY_ONBOARDING_CASES'):cases=os.environ['CONFECTORY_ONBOARDING_CASES'].split(',')
evidence=[];errors=[];external=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'])
 try:
  for name in cases:
   case=root/name;case.mkdir();storage=case/'profile';control={'isolationFailure':{'plugins-restart-start':'start','plugins-restart-file-change':'file-change','plugins-restart-exit':'exit','plugins-restart-initialize':'initialize','plugins-restart-config':'config/read'}.get(name,''),'postLoginPlugins':name=='plugins-post-browser','pluginPreset':'changed-after-override' if name=='plugins-change' else 'budget' if name=='plugins-budget' else 'multiple' if name in ('plugins-existing','install-plugins','plugins-browser','plugins-cancel','plugins-login-blocked','plugins-restart-exit','plugins-restart-initialize','plugins-restart-config','plugins-login-restart-exit','plugins-post-browser','plugins-restart-start','plugins-restart-file-change','plugins-login-restart-start') else '', 'holdIsolation':name=='plugins-cancel','loginExpired':name=='login-expired','loginPortError':name=='callback-rpc-conflict','invalidBrowserUrl':name=='invalid-login-url','rejectExtension':name=='unexpected-extension','rejectSearch':name=='web-search-policy','bundledPolicy':name in ('bundled-policy','user-bundle-settings'),'singleModel':name=='single-model','noDefault':name in ('model-selection','single-model'),'noModels':name=='no-models','configuredModel':'fixture-two' if name=='configured-model' else '', 'preAuthFailure':'mixed-account-error' if name=='install-mixed-homes' else name.removeprefix('install-') if name in ('install-process-exit','install-initialize-error','install-account-error','install-model-error','install-process-start-error') else '', 'failLogin':name=='failed-login','holdVersion':name=='cancel-probe','holdDownload':name=='cancel-install','badArchive':name=='bad-install','version':'0.159.2' if name=='unsupported-runtime' else '0.159.0-alpha.3'}
   def write_control(**values):control.update(values);(case/'control.json').write_text(json.dumps(control))
   write_control(turnFailure=name.removeprefix('turn-') if name.startswith('turn-') else '');(root/'active.json').write_text(json.dumps({'case':str(case)}))
   absent=name.startswith('install-') or name in ('install','cancel-install','bad-install');logged_out=name.startswith('install-') and name!='install-model-error' or name in ('plugins-browser','plugins-login-blocked','plugins-login-restart-exit','plugins-post-browser','plugins-login-restart-start','logged-out','install','cancel-login','cancel-install','bad-install','failed-login','switch-provider','browser-open-failed','login-expired','callback-port-conflict','callback-rpc-conflict','invalid-login-url','device-fallback','device-cancel','device-retry','method-cleanup-failed')
   discovery={'executables':[] if absent else [{'path':str(runtime),'selectable':True,'source':'owned fixture'}],'homes':[]}
   homes=[]
   for index in range(0 if name=='install-empty-home' else 2 if name in ('multiple-accounts','install-mixed-homes') else 1):
    home=case/('account-'+str(index));home.mkdir();(home/'original.keep').write_bytes(b'owned original account state\x00');homes.append(home);discovery['homes'].append({'path':str(home),'selectable':True,'source':'owned fixture'})
    if name=='user-bundle-settings':(home/'config.toml').write_text('[plugins."unified-computer-use@openai-bundled"]\nenabled = true\n')
    if not logged_out:(home/'.owned-account.json').write_text(json.dumps({'type':'chatgpt','email':('alice' if index==0 else 'bob')+'@fixture.invalid','planType':'plus'}))
   (root/'active-discovery.json').write_text(json.dumps(discovery))
   spec={'supported':True,'publisher':'OWNED FIXTURE','version':'0.159.0-alpha.3','target':'linux-x64','asset':'codex-owned.tar.gz','url':'http://127.0.0.1:'+str(server.server_port)+'/runtime','sha256':hashlib.sha256(archive).hexdigest(),'archiveKind':'tar.gz','archiveExecutable':'codex-owned','binaryName':'codex','rootBase':str(case/'managed'),'maxDownloadBytes':268435456,'maxUnpackedBytes':1073741824,'maxEntries':128,'downloadTimeoutSeconds':60}
   (root/'active-info.json').write_text(json.dumps(spec));run_env=env.copy();run_env.update(CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'));log_path=case/'host.log';log=log_path.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=run_env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   port_lease=None
   page=browser.new_page(viewport={'width':1440,'height':1000});page.add_init_script('''globalThis.__ownedBrowserOpens=[];globalThis.__ownedBrowserFailure=FAIL;Object.defineProperty(window,'confectoryWebUI',{value:Object.freeze({openCodexLogin(handle){globalThis.__ownedBrowserOpens.push(handle);return Promise.resolve({ok:!globalThis.__ownedBrowserFailure});}})});'''.replace('FAIL','true' if name=='browser-open-failed' else 'false'));page.on('pageerror',lambda e:errors.append(str(e)));invocations=[]
   page.on('request',lambda r:invocations.append(r.post_data_json.get('endpoint')) if r.url.endswith('/api/request') and r.post_data_json.get('op')=='invoke' else None)
   def expect_browser():
    expect(dialog.locator('[data-cli-official-login]')).to_be_visible();expect(dialog.locator('[data-cli-code]')).to_have_count(0)
    assert state()['codexOnboarding']['loginMethod']=='browser'
    assert [r for r in requests() if r['method']=='account/login/start'][-1]['params']=={'type':'chatgpt'}
    assert 'auth.openai.com/oauth/authorize?' in dialog.locator('[data-cli-official-login]').get_attribute('href')
    page.wait_for_function('globalThis.__ownedBrowserOpens.length>0')
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
    def clean_codex():
     forbidden='[data-connection-advanced],[data-discover-connection],[data-basic-check],[data-install-prepare],[data-login-prepare],[data-discover-models],[data-installation-candidates],[data-home-candidates],[data-candidate-kind],[data-install-target],[data-install-guide],[data-connection-field],[data-connection-save],[data-connection-attempt],[data-agent-register],[data-connection-refresh],[data-connection-back],[data-method-choice],input,select,textarea'
     expect(dialog.locator(forbidden)).to_have_count(0)
     text=dialog.inner_text()
     for phrase in ('이전 PackEngine','새로 준비한 AI','고급 설정','수동 지정','계정 참조','계정 정보 위치','실행 파일','플랫폼 선택','목록 새로 고침','설정 저장','조건 확인','준비 확인을 눌러'):
      assert phrase not in text,(phrase,text)
    clean_codex()
    # Initial repeated clicks never start a second workflow.
    dialog.locator('[data-cli-login]').evaluate('(b)=>{b.click();b.click();}')
    if name=='bundled-policy' and os.environ.get('CONFECTORY_ONBOARDING_EXPECT_BUNDLED_FAILURE')=='1':
     expect(dialog.locator('[data-cli-retry]')).to_be_visible();diagnostic=state()['codexOnboarding']['diagnostics'];assert diagnostic['failure']['code']=='provider-tool-policy-unsupported' and diagnostic['failure']['stage']=='policy-check' and diagnostic['failure']['errorType']=='PlatformNotSupportedException' and diagnostic['failure']['processStarted'] is True,diagnostic
     assert 'detail' not in diagnostic['failure'];assert not [r for r in requests() if r['method'] in ('model/list','account/login/start','turn/start')];(case/'safe-diagnostics.json').write_text(json.dumps(diagnostic,indent=2));print('PASS reproduced bundled default plugin policy-check PlatformNotSupportedException',flush=True);continue
    if name in ('plugins-restart-exit','plugins-restart-initialize','plugins-restart-config','plugins-restart-start','plugins-restart-file-change'):
     expect(dialog.locator('[data-cli-retry]')).to_be_visible();blocked=state()['codexOnboarding']['diagnostics'];summary=blocked['failure']['pluginIsolation'];assert summary['overrideRequested'] is True and summary['overrideVerified'] is False and summary['effectiveRechecked'] is False;assert 'PRIVATE' not in json.dumps(blocked);assert len([r for r in requests() if r['method']=='process'])==(1 if name in ('plugins-restart-start','plugins-restart-file-change') else 2);assert not [r for r in requests() if r['method'] in ('model/list','account/login/start','thread/start','turn/start')];(case/'safe-diagnostics.json').write_text(json.dumps(blocked,indent=2));clean_codex();write_control(isolationFailure='');runtime.chmod(0o700);dialog.locator('[data-cli-retry]').click()
    if name=='plugins-cancel':
     wait_file(case/'isolation-started');dialog.locator('[data-cli-stop]').click();expect(dialog.locator('[data-cli-login]')).to_be_visible();write_control(holdIsolation=False);assert not [r for r in requests() if r['method'] in ('model/list','account/login/start','turn/start')];dialog.locator('[data-cli-login]').click()
    if name in ('plugins-change','plugins-budget'):
     expect(dialog.locator('[data-cli-retry]')).to_be_visible();blocked=state()['codexOnboarding']['diagnostics'];summary=blocked['failure']['pluginIsolation'];assert blocked['failure']['detail']=='enabled-plugin-entry';assert summary['overrideVerified'] is False and summary['overrideRequested']==(name=='plugins-change');assert 'PRIVATE' not in json.dumps(blocked);assert not [r for r in requests() if r['method'] in ('model/list','account/login/start','turn/start')];(case/'safe-diagnostics.json').write_text(json.dumps(blocked,indent=2));clean_codex();page.screenshot(path=str(case/'policy-blocked.png'));write_control(pluginPreset='multiple');dialog.locator('[data-cli-retry]').click()
    if name=='cancel-probe':
     wait_file(case/'version-started');dialog.locator('[data-cli-stop]').click();expect(dialog.locator('[data-codex-onboarding]')).to_have_attribute('data-step',re.compile('cancelled|cancelling'));write_control(holdVersion=False);expect(dialog.locator('[data-cli-login]')).to_be_enabled();dialog.locator('[data-cli-login]').click()
    if absent or name=='unsupported-runtime':
     expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 설치');clean_codex();page.screenshot(path=str(case/'install-consent.png'))
     if name=='unsupported-runtime':
      assert not [r for r in requests() if r['method']=='account/read'];dialog.locator('[data-connection-cancel]').click();print('PASS scenario unsupported-runtime',flush=True);continue
     consent=state()['codexOnboarding']['token']
     dialog.locator('[data-cli-consent]').click();assert api('approve',token=consent)['ok']
     if name=='cancel-install':
      wait_file(case/'download-started');clean_codex();page.screenshot(path=str(case/'installing.png'));dialog.locator('[data-cli-stop]').click();expect(dialog.locator('[data-codex-onboarding]')).to_have_attribute('data-step',re.compile('cancelled|cancelling'));write_control(holdDownload=False)
      expect(dialog.locator('[data-cli-login]')).to_be_enabled();dialog.locator('[data-cli-login]').click();expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 설치');dialog.locator('[data-cli-consent]').click()
     if name=='bad-install':
      expect(dialog.locator('[data-cli-retry]')).to_be_visible();clean_codex();page.screenshot(path=str(case/'install-failed.png'));write_control(badArchive=False);dialog.locator('[data-cli-retry]').click();expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 설치');dialog.locator('[data-cli-consent]').click()
    if name in ('install-process-exit','install-initialize-error','install-account-error','install-model-error','install-mixed-homes','install-process-start-error'):
     expect(dialog.locator('[data-cli-retry]')).to_be_visible();failure=state()['codexOnboarding'];assert len(state()['helperAgents']['agents'])==0;assert not [r for r in requests() if r['method'] in ('account/login/start','turn/start')]
     if os.environ.get('CONFECTORY_ONBOARDING_EXPECT_LEGACY_FAILURES')=='1':
      assert failure['message']=='기존 Codex 설정으로 연결 준비를 마치지 못했어요. 다시 시도하거나 별도 계정으로 로그인할 수 있습니다.',failure
      clean_codex();page.screenshot(path=str(case/'legacy-post-install-failed.png'));print('PASS reproduced legacy '+name+' code='+failure['code'],flush=True);continue
     diagnostic=failure['diagnostics'];expected={'install-process-start-error':('provider-start-failed','process-start'),'install-process-exit':('provider-protocol-unsupported','initialize'),'install-initialize-error':('provider-protocol-unsupported','initialize'),'install-account-error':('provider-account-query-failed','account-read'),'install-model-error':('provider-model-catalog-unavailable','model-list'),'install-mixed-homes':('provider-account-query-failed','account-read')}[name]
     assert (diagnostic['failure']['code'],diagnostic['failure']['stage'])==expected,diagnostic
     assert diagnostic['installation']=={'state':'prepared','version':'0.159.0-alpha.3'} and failure['installation']['state']=='prepared',failure
     assert len(diagnostic['attempts'])==(2 if name=='install-mixed-homes' else 1),diagnostic
     if name=='install-mixed-homes':assert diagnostic['attempts'][1]['code']=='provider-auth-required'
     if name=='install-process-exit':assert diagnostic['failure'].get('exitCode')==23,diagnostic
     elif name=='install-process-start-error':assert diagnostic['failure']['processStarted'] is False and diagnostic['failure']['nativeErrorCode']==13 and 'exitCode' not in diagnostic['failure'],diagnostic
     else:assert diagnostic['failure']['rpcErrorCode']==-32603,diagnostic
     clean_codex();safe=json.dumps(diagnostic);assert not any(x in safe for x in ('PRIVATE','NEVER-EXPOSE','/tmp','/home','@','token=','accountIdentity','executable','managedHome')),safe
     expect(dialog.locator('[data-cli-installation-result]')).to_be_visible();details=dialog.locator('[data-cli-diagnostics]');details.locator('summary').click();expect(details.locator('pre')).to_contain_text(expected[0]);clean_codex();page.screenshot(path=str(case/'post-install-failed.png'));(case/'safe-diagnostics.json').write_text(json.dumps(diagnostic,indent=2))
     write_control(preAuthFailure='')
     if name=='install-process-start-error':
      for prepared in (case/'managed/installations').rglob('codex'):prepared.chmod(0o700)
     dialog.locator('[data-cli-retry]').click()
     if name=='install-model-error':expect(dialog.locator('[data-cli-account]')).to_have_count(1)
     else:expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 로그인')
     assert (case/'download-count').read_text()=='1','retry repeated completed installation'
     for home in homes:assert (home/'original.keep').read_bytes()==b'owned original account state\x00'
     assert not [r for r in requests() if r['method'] in ('account/login/start','turn/start')]
     assert 'mcpBridge' not in invocations
     print('PASS scenario '+name,flush=True);continue
    if name in ('unexpected-extension','web-search-policy'):
     expect(dialog.locator('[data-cli-retry]')).to_be_visible();blocked=state()['codexOnboarding']['diagnostics'];assert blocked['failure']['stage']=='policy-check' and blocked['failure']['detail']==('enabled-plugin-entry' if name=='unexpected-extension' else 'startup-web-search'),blocked
     assert not [r for r in requests() if r['method'] in ('model/list','account/login/start','turn/start')];clean_codex();page.screenshot(path=str(case/'policy-blocked.png'));write_control(rejectExtension=False,rejectSearch=False);dialog.locator('[data-cli-retry]').click()
    if logged_out or name=='multiple-accounts':
     if logged_out:assert not [r for r in requests() if r['method'] in ('model/list','account/login/start','turn/start')],'model/auth request before explicit login consent'
     expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 로그인');clean_codex();page.screenshot(path=str(case/'login-consent.png'));consent=state()['codexOnboarding']['token']
     if name=='callback-port-conflict':port_lease=socket.socket();port_lease.bind(('127.0.0.1',1455));port_lease.listen(1)
     if name=='plugins-login-blocked':write_control(rejectExtension=True)
     if name in ('plugins-login-restart-exit','plugins-login-restart-start'):write_control(isolationFailure='exit' if name=='plugins-login-restart-exit' else 'start')
     dialog.locator('[data-cli-consent]').click();assert api('approve',token=consent)['ok']
     if name in ('plugins-login-restart-exit','plugins-login-restart-start'):
      expect(dialog.locator('[data-cli-retry]')).to_be_visible();blocked=state()['codexOnboarding']['diagnostics'];assert blocked['failure']['pluginIsolation']['overrideRequested'] is True and blocked['failure']['pluginIsolation']['overrideVerified'] is False;assert 'PRIVATE' not in json.dumps(blocked);assert not [r for r in requests() if r['method'] in ('model/list','account/login/start','thread/start','turn/start')];write_control(isolationFailure='');runtime.chmod(0o700);dialog.locator('[data-cli-retry]').click();expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 로그인');dialog.locator('[data-cli-consent]').click()
     if name=='plugins-login-blocked':
      expect(dialog.locator('[data-cli-retry]')).to_be_visible();blocked=state()['codexOnboarding']['diagnostics'];assert blocked['failure']['code']=='login_plugin_isolation_failed' and blocked['failure']['detail']=='enabled-plugin-entry';assert blocked['failure']['pluginIsolation']['effectiveRechecked'] is True and blocked['failure']['pluginIsolation']['overrideVerified'] is False;assert 'PRIVATE' not in json.dumps(blocked);assert not [r for r in requests() if r['method'] in ('account/login/start','model/list','turn/start')];write_control(rejectExtension=False);dialog.locator('[data-cli-retry]').click();expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 로그인');dialog.locator('[data-cli-consent]').click()
     if name in ('callback-port-conflict','callback-rpc-conflict','invalid-login-url'):
      expect(dialog.locator('[data-cli-retry]')).to_be_visible();failed=state()['codexOnboarding'];assert failed['diagnostics']['failure']['code']==('login_url_rejected' if name=='invalid-login-url' else 'login_callback_unavailable'),failed
      assert page.evaluate('globalThis.__ownedBrowserOpens')==[] and state()['helperAgents']['agents']==[]
      if name=='callback-port-conflict':
       assert not [r for r in requests() if r['method']=='account/login/start'];assert not select.select([port_lease],[],[],0)[0];port_lease.close();port_lease=None
      safe=str(failed['diagnostics']);assert 'PRIVATE' not in safe and 'oauth/authorize' not in safe and 'owned-state' not in safe
      clean_codex();page.screenshot(path=str(case/'browser-unavailable.png'));write_control(loginPortError=False,invalidBrowserUrl=False);dialog.locator('[data-cli-retry]').click();expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 로그인');dialog.locator('[data-cli-consent]').click()
     expect_browser();clean_codex();page.screenshot(path=str(case/'browser-login.png'))
     if name in ('browser-open-failed','device-fallback','device-cancel','device-retry','method-cleanup-failed'):
      page.wait_for_timeout(250);assert len(page.evaluate('globalThis.__ownedBrowserOpens'))==1
      if name=='browser-open-failed':
       expect(dialog.locator('[data-cli-browser-error]')).to_be_visible();dialog.locator('[data-cli-official-login]').click();page.wait_for_function('globalThis.__ownedBrowserOpens.length===2');expect(dialog.locator('[data-cli-browser-error]')).to_be_visible();page.screenshot(path=str(case/'browser-open-failed.png'))
      browser_handle=state()['codexOnboarding']['openHandle'];browser_home=pathlib.Path([r for r in requests() if r['method']=='account/login/start'][-1]['home']);before=len([r for r in requests() if r['method']=='account/login/start'])
      if name=='method-cleanup-failed':browser_home.chmod(0)
      dialog.locator('[data-cli-login-alternative]>summary').click();dialog.locator('[data-cli-device-login]').click()
      if name=='method-cleanup-failed':
       try:
        expect(dialog.locator('[data-cli-diagnostics]')).to_be_visible();blocked=state()['codexOnboarding'];assert blocked['diagnostics']['failure']['code']=='login_cleanup_pending' and blocked['retryable'] is False;expect(dialog.locator('[data-cli-retry],[data-cli-device-login],[data-cli-new-login]')).to_have_count(0)
        assert not api('new-login')['ok'] and not api('retry',approved=True)['ok'];assert len([r for r in requests() if r['method']=='account/login/start'])==before and state()['helperAgents']['agents']==[]
        page.screenshot(path=str(case/'cleanup-blocked.png'))
       finally:browser_home.chmod(0o700)
       print('PASS scenario '+name,flush=True);continue
      expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 로그인');assert '기기 코드 방식' in dialog.inner_text();assert len([r for r in requests() if r['method']=='account/login/start'])==before;assert not browser_home.exists();assert any(r['method']=='account/login/cancel' for r in requests());assert state()['helperAgents']['agents']==[];assert not api('device-login',token=browser_handle)['ok'];assert len([r for r in requests() if r['method']=='account/login/start'])==before
      page.screenshot(path=str(case/'device-consent.png'));page.evaluate('globalThis.__ownedBrowserFailure=false');dialog.locator('[data-cli-consent]').click();expect(dialog.locator('[data-cli-code]')).to_have_text('TEST-4240');assert [r for r in requests() if r['method']=='account/login/start'][-1]['params']=={'type':'chatgptDeviceCode'};clean_codex();page.screenshot(path=str(case/'device-login.png'))
      if name=='device-fallback':
       device_home=pathlib.Path([r for r in requests() if r['method']=='account/login/start'][-1]['home']);before_back=len([r for r in requests() if r['method']=='account/login/start']);dialog.locator('[data-cli-browser-login]').click();expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 로그인');assert '기본 브라우저' in dialog.inner_text() and not device_home.exists();assert len([r for r in requests() if r['method']=='account/login/start'])==before_back;dialog.locator('[data-cli-consent]').click();expect_browser();page.screenshot(path=str(case/'browser-after-device.png'))
      if name=='device-cancel':
       dialog.locator('[data-cli-stop]').click();expect(dialog.locator('[data-cli-login]')).to_be_visible();(case/'complete-login').write_text('late');page.wait_for_timeout(200);assert state()['helperAgents']['agents']==[];assert not list((case/'managed/accounts').glob('account-*'));print('PASS scenario '+name,flush=True);continue
      if name=='device-retry':
       write_control(failLogin=True);(case/'complete-login').write_text('failed');expect(dialog.locator('[data-cli-retry]')).to_be_visible();(case/'complete-login').unlink();write_control(failLogin=False);dialog.locator('[data-cli-retry]').click();expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 로그인');assert '기기 코드 방식' in dialog.inner_text();dialog.locator('[data-cli-consent]').click();expect(dialog.locator('[data-cli-code]')).to_have_text('TEST-4240');assert [r for r in requests() if r['method']=='account/login/start'][-1]['params']=={'type':'chatgptDeviceCode'}
     if name=='switch-provider':
      dialog.get_by_role('button',name='OpenAI Responses',exact=True).click();expect(dialog.locator('[data-codex-onboarding]')).to_have_count(0);(case/'complete-login').write_text('owned');page.wait_for_timeout(500);assert state()['helperAgents']['agents']==[];dialog.get_by_role('button',name='Codex',exact=True).click();expect(dialog.locator('[data-cli-login]')).to_be_enabled();clean_codex();page.screenshot(path=str(case/'switched-cancelled.png'));print('PASS scenario switch-provider',flush=True);continue
     if name=='cancel-login':
      dialog.locator('[data-connection-cancel]').click();page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);dialog.get_by_role('button',name='Codex',exact=True).click();expect(dialog.locator('[data-cli-login]')).to_be_enabled();dialog.locator('[data-cli-login]').click();expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 로그인');dialog.locator('[data-cli-consent]').click();expect_browser()
     (case/'complete-login').write_text('owned')
     if name in ('failed-login','login-expired'):
      expect(dialog.locator('[data-cli-retry]')).to_be_visible();clean_codex();page.screenshot(path=str(case/'login-failed.png'));assert state()['codexOnboarding']['diagnostics']['failure']['code']==('login_timeout' if name=='login-expired' else 'login_not_completed');write_control(failLogin=False,loginExpired=False);(case/'complete-login').unlink();dialog.locator('[data-cli-retry]').click();expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 로그인');dialog.locator('[data-cli-consent]').click();expect_browser();(case/'complete-login').write_text('owned')
    else:
     if name=='no-models':
      expect(dialog.locator('[data-cli-retry]')).to_be_visible();assert state()['helperAgents']['agents']==[];clean_codex();page.screenshot(path=str(case/'models-empty.png'));write_control(noModels=False);dialog.locator('[data-cli-retry]').click()
     expect(dialog.locator('[data-cli-account]')).to_have_count(1);clean_codex();page.screenshot(path=str(case/'account-choice.png'))
     assert 'alice@fixture.invalid' in dialog.locator('[data-cli-account]').first.inner_text()
     # A foreign selection token cannot become an account or registration.
     rejected=api('choose-account',token='foreign-token',account='foreign-account');assert not rejected['ok'];assert state()['helperAgents']['agents']==[]
     choice=state()['codexOnboarding'];rejected=api('choose-account',token=choice['token'],account='foreign-account');assert not rejected['ok'];assert state()['helperAgents']['agents']==[]
     dialog.locator('[data-cli-account]').first.click();assert api('choose-account',token=choice['token'],account=choice['accounts'][0]['id'])['ok']
    expect(dialog.locator('[data-cli-done]')).to_be_enabled(timeout=40000);clean_codex();page.screenshot(path=str(case/'ready.png'));ready=state();assert ready['projectId']=='' and len(ready['helperAgents']['agents'])==1;agent=ready['helperAgents']['agents'][0];assert agent['state']=='ready' and agent['accountVerified'] is False and agent['accountMetadataVerified'] is True,agent
    assert agent['model']==('fixture-two' if name=='configured-model' else 'fixture-one')
    expected_email='new-account@fixture.invalid' if logged_out or name=='multiple-accounts' else 'alice@fixture.invalid';assert agent['accountIdentity']['email']==expected_email,agent
    assert not [r for r in requests() if r['method']=='turn/start']
    before=len(requests());dialog.locator('[data-cli-done]').click();expect(dialog).to_have_count(0)
    page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);dialog.get_by_role('button',name='Codex',exact=True).click();expect(dialog.locator('[data-cli-done]')).to_be_enabled();assert len(requests())==before,'reopen repeated completed steps'
    dialog.locator('[data-cli-offline]').click();expect(dialog.locator('[data-cli-login]')).to_have_text('다시 연결');assert state()['helperAgents']['agents'][0]['state']=='offline';dialog.locator('[data-cli-login]').click();expect(dialog.locator('[data-cli-done]')).to_be_enabled();assert state()['helperAgents']['agents'][0]['state']=='ready' and len(requests())==before
    dialog.locator('[data-cli-done]').click()
    if name=='authenticated' or name.startswith(('turn-','restart-')):
     page.locator('#add-helper').click();creator=page.locator('[data-v508-helper]');creator.locator('#participant-name').fill('Owned CLI Helper');creator.locator('#participant-description').fill('Owned account metadata and protocol only');creator.locator('button[type=submit]').click();expect(creator).to_have_count(0);page.locator('.home-side [data-helper]').first.click();card=page.locator('.participant-expanded-card');card.locator('textarea').fill('owned CLI message');card.locator('[data-global-send]').click();expect(page.locator('[data-global-approval]')).to_have_count(0);expect(card.locator('textarea')).to_have_value('')
     if name.startswith('turn-'):
      expected={'turn-remote-bad-request':('provider-error','response-events','badRequest'),'turn-rpc-error':('provider-error','turn-start','rpcErrorCode=-32602'),'turn-exit':('provider-error','turn-start','exitCode=37'),'turn-bad-json':('provider-error','response-events',None),'turn-foreign-event':('provider-error','response-events',None),'turn-remote-http':('provider-http-error','response-events','httpStatusCode=503'),'turn-completed-error':('provider-auth-required','response-events','httpStatusCode=403')}[name]
      for value in expected:
       if value:expect(card.locator('.messages')).to_contain_text(value)
      terminal=next(iter(state()['helperAgents']['turns'].values()));assert terminal['state']=='error' and terminal['errorCode']==expected[0];assert terminal['errorDiagnostics']['stage']==expected[1];assert 'PRIVATE' not in json.dumps(terminal) and 'NEVER-EXPOSE' not in json.dumps(terminal);assert not any(k in terminal['errorDiagnostics'] for k in ('message','path','stderr','accountIdentity','fingerprint'))
      card.locator('[data-close]').click();page.locator('.home-side [data-helper]').first.click();expect(card.locator('.messages')).to_contain_text(expected[0]);page.screenshot(path=str(case/'safe-helper-error.png'))
     else:expect(card.locator('.messages')).to_contain_text('OWNED CLI HELPER REPLY',timeout=30000);page.screenshot(path=str(case/'helper-reply.png'))
     assert len([r for r in requests() if r['method']=='turn/start'])==1
    if name=='identity-change':
     write_control(loginEmail='changed@fixture.invalid');page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);dialog.get_by_role('button',name='Codex',exact=True).click();expect(dialog.locator('[data-cli-change-account]')).to_be_enabled();dialog.locator('[data-cli-change-account]').click();expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 로그인');clean_codex();assert state()['helperAgents']['agents'][0]['accountIdentity']['email']=='alice@fixture.invalid';dialog.locator('[data-cli-consent]').click();expect_browser();(case/'complete-login').write_text('owned');expect(dialog.locator('[data-cli-done]')).to_be_enabled();assert state()['helperAgents']['agents'][0]['accountIdentity']['email']=='changed@fixture.invalid';clean_codex();page.screenshot(path=str(case/'changed-account.png'));dialog.locator('[data-cli-done]').click()
     page.locator('#add-helper').click();creator=page.locator('[data-v508-helper]');creator.locator('#participant-name').fill('Re-logged CLI Helper');creator.locator('button[type=submit]').click();expect(creator).to_have_count(0);page.locator('.home-side [data-helper]').first.click();card=page.locator('.participant-expanded-card');card.locator('textarea').fill('new confirmed identity');card.locator('textarea').press('Enter');expect(card.locator('.messages')).to_contain_text('OWNED CLI HELPER REPLY');expect(card.locator('textarea')).to_have_value('');assert state()['helperAgents']['agents'][0]['accountIdentity']['email']=='changed@fixture.invalid';page.screenshot(path=str(case/'relogin-helper-reply.png'))
    if name=='authenticated' or name.startswith('restart-'):
     # A new engine process restores the confirmed account identity, then renews
     # readiness without asking for another OAuth login or account choice.
     registry_file=storage/'helper-agents.json';registry=json.loads(registry_file.read_text())
     if name=='restart-offline':registry['agents']['Confectory.Agent.Codex::Connection']['offline']=True;registry_file.write_text(json.dumps(registry))
     if name=='restart-unverified':registry['agents']['Confectory.Agent.Codex::Connection'].pop('identity',None);registry_file.write_text(json.dumps(registry))
     if name=='restart-mismatch':write_control(readEmail='different@fixture.invalid')
     if name=='restart-expired-auth':write_control(hideAccount=True)
     if name=='restart-renewal-failure':write_control(preAuthFailure='account-error')
     registered_bytes=registry_file.read_bytes();login_count=len([r for r in requests() if r['method']=='account/login/start']);page.close();os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=15);log.close();log=log_path.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=run_env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
     for _ in range(600):
      urls=[line.split(' ',1)[1] for line in log_path.read_text().splitlines() if line.startswith('CONFECTORY_WEB_UI ')]
      if urls:url=urls[-1];break
      assert host.poll() is None;time.sleep(.1)
     origin,token=url.split('/#');page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)));page.route('**/*',route);page.goto(url);expect(page.locator('#add-agent')).to_be_enabled(timeout=30000)
     before=len(requests());page.locator('.home-side [data-helper]').first.click();card=page.locator('.participant-expanded-card');expect(card.locator('.messages')).to_contain_text('owned CLI message');expect(card.locator('.messages')).to_contain_text('OWNED CLI HELPER REPLY');assert len(requests())==before;card.locator('textarea').fill('owned after restart')
     if name=='restart-offline':card.locator('form').evaluate('e=>e.requestSubmit()')
     else:card.locator('textarea').press('Enter')
     if name.startswith('restart-'):
      expected={'restart-mismatch':'codex-account-mismatch','restart-expired-auth':'provider-auth-required','restart-offline':'codex-readiness-changed','restart-unverified':'codex-registration-unverified','restart-renewal-failure':'provider-account-query-failed'}[name];expect(page.locator('#toast')).to_contain_text(expected);expect(card.locator('textarea')).to_have_value('owned after restart');assert len([r for r in requests() if r['method']=='turn/start'])==1
      if name in ('restart-offline','restart-unverified'):assert len(requests())==before
      page.screenshot(path=str(case/'cold-blocked.png'))
     else:
      expect(card.locator('.messages')).to_contain_text('owned after restart');expect(card.locator('textarea')).to_have_value('');expect(card.locator('[data-global-send]')).to_have_text('보내기');assert len([r for r in requests() if r['method']=='turn/start'])==2;page.screenshot(path=str(case/'cold-auto-reply.png'))
      # Repeated sends use the renewed lease without another preflight process.
      checks=sum(r['method']=='account/read' for r in requests());card.locator('textarea').fill('same verified session');card.locator('textarea').press('Enter');expect(card.locator('textarea')).to_have_value('');expect(card.locator('[data-global-send]')).to_have_text('보내기');assert sum(r['method']=='account/read' for r in requests())==checks+1
     assert registry_file.read_bytes()==registered_bytes,'readiness changed saved registration';assert len([r for r in requests() if r['method']=='account/login/start'])==login_count;assert (state().get('codexOnboarding') or {}).get('state','idle')=='idle';assert page.locator('[data-codex-onboarding]').count()==0
    if name=='user-bundle-settings':assert (homes[0]/'config.toml').read_text()=='[plugins."unified-computer-use@openai-bundled"]\nenabled = true\n'
    if name in ('plugins-existing','install-plugins','plugins-browser','plugins-change','plugins-budget','plugins-cancel','plugins-login-blocked','plugins-restart-exit','plugins-restart-initialize','plugins-restart-config','plugins-login-restart-exit','plugins-post-browser','plugins-restart-start','plugins-restart-file-change','plugins-login-restart-start'):
     events=requests();processes={r['pid']:r['params'] for r in events if r['method']=='process'}
     assert any(p['isolationOverride'] for p in processes.values())
     for r in events:
      if r['method'] in ('model/list','account/login/start','thread/start','turn/start'):assert processes[r['pid']]['isolationOverride'],r
     assert 'PRIVATE' not in json.dumps(ready['codexOnboarding'])
    for home in homes:assert (home/'original.keep').read_bytes()==b'owned original account state\x00'
    assert 'mcpBridge' not in invocations and not any('site' in x.lower() for x in invocations if x)
    print('PASS scenario '+name,flush=True)
   except BaseException:
    page.screenshot(path=str(case/'failure.png'));print('FAILED '+name+' '+str(case),flush=True);print('HOST '+log_path.read_text()[-2500:],flush=True);print('STATE '+json.dumps(state(),ensure_ascii=False)[-9000:],flush=True);print('PAGE '+page.locator('body').inner_text()[-3000:],flush=True);raise
   finally:
    if port_lease is not None:port_lease.close()
    evidence.append({'scenario':name,'requests':requests(),'uiInvocations':invocations});write_control(holdVersion=False,holdDownload=False);page.close()
    if host.poll() is None:os.killpg(host.pid,signal.SIGTERM)
    host.wait(timeout=15);log.close();(root/'evidence.json').write_text(json.dumps({'cases':evidence,'pageErrors':errors,'externalRequests':external},ensure_ascii=False,indent=2))
 finally:browser.close();server.shutdown()
assert not errors and not external,(errors,external)
print('PASS owned CLI login-first integration '+str(root),flush=True)
