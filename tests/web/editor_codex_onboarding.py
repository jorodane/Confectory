"""Production CLI onboarding with owned runtimes/accounts and a loopback archive.

Only Discover/PreparationInfo are fixture providers. Every state transition,
installer, official browser/device login, account/model validation and Helper transport is real
Confectory code. No real OAuth, user credentials, inference or external relay.
"""
import hashlib,http.server,socket,select,io,json,os,pathlib,re,shutil,signal,subprocess,sys,tarfile,tempfile,threading,time,urllib.request,uuid
from playwright.sync_api import sync_playwright,expect
from editor_navigation import goto_editor

expect.set_options(timeout=30000)
repo=pathlib.Path(sys.argv[1]).resolve();reuse=os.environ.get('CONFECTORY_ONBOARDING_REUSE','');root=pathlib.Path(reuse).resolve() if reuse else pathlib.Path(tempfile.mkdtemp(prefix='confectory-cli-flow-'));assert root.parent==pathlib.Path('/tmp') and root.name.startswith('confectory-cli-flow-');print('FIXTURE '+str(root),flush=True)
owned=root/'engine';editor=owned/'examples/editor-home';runtime=root/'codex'
if not reuse:
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
 # Owned lifecycle fixture supplies native parent selection and technical expiry only.
 if any(n in ('chat-use','agent-common') or n.startswith('intro-') for n in os.environ.get('CONFECTORY_ONBOARDING_CASES','').split(',')):
  browser_pack=root/'browser-host';shutil.copytree(repo/'packs/browser-host',browser_pack)
  for f in editor.glob('*.cpack'):f.write_text(f.read_text().replace(json.dumps(str(repo/'packs/browser-host/pack.cpack')),json.dumps(str(browser_pack/'pack.cpack'))))
  p=browser_pack/'ServeBody.celem';p.write_text(p.read_text().replace('body common','import Confectory.WebUI::NativeRequest as NativeRequest (string,string,string) -> string;\nbody common'))
  verification=pack/'Verification.csbody';vs=verification.read_text();expiry='if(System.IO.File.Exists(PATH)){proof["expires"]=DateTime.UtcNow.AddSeconds(-1);System.IO.File.Delete(PATH);}'.replace('PATH',json.dumps(str(root/'expire-next')));verification.write_text(vs.replace('if(record[2] is System.Text.Json.Nodes.JsonObject proof){','if(record[2] is System.Text.Json.Nodes.JsonObject proof){'+expiry,1))
  parent=root/'projects';parent.mkdir();p=browser_pack/'Serve.csbody';text=p.read_text();needle='if(request.Url.AbsolutePath=="/api/request")'
  owned_route='if(request.Url.AbsolutePath is "/fixture/native-create" or "/fixture/expire"){\n if(request.Headers["X-Confectory-Session"]!=session||request.HttpMethod!="POST")throw new UnauthorizedAccessException();\n if(request.Url.AbsolutePath=="/fixture/native-create"){using var read=new System.IO.StreamReader(request.InputStream);var args=System.Text.Json.Nodes.JsonNode.Parse(read.ReadToEnd())!.AsObject();foreach(var field in args)if(field.Key is not ("title" or "description" or "bucket"))throw new ArgumentException("Owned fixture creation only");string bucket=args["bucket"]?.ToString()??"default";if(bucket is not ("one" or "two" or "default"))throw new ArgumentException("Owned fixture bucket");args.Remove("bucket");string selectedParent=System.IO.Path.Combine(PARENT,bucket);System.IO.Directory.CreateDirectory(selectedParent);args["directory"]=selectedParent;bytes=System.Text.Encoding.UTF8.GetBytes(calls.NativeRequest.Invoke(owner,"create-project",args.ToJsonString()));}\n else{System.IO.File.WriteAllText(EXPIRE,"owned expiry");bytes=System.Text.Encoding.UTF8.GetBytes("{\\\"ok\\\":true}");}\n response.ContentType="application/json";\n}else '.replace('PARENT',json.dumps(str(parent))).replace('EXPIRE',json.dumps(str(root/'expire-next')));p.write_text(text.replace(needle,owned_route+needle,1))
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
if any(n in ('chat-use','agent-common') or n.startswith('intro-') for n in os.environ.get('CONFECTORY_ONBOARDING_CASES','').split(',')):env['CONFECTORY_EDITOR_REPO']=str(repo)
built=None
if not reuse:
 with (root/'build.json').open('w') as out,(root/'build.err').open('w') as err:built=subprocess.run([env['CONFECTORY_DOTNET'],str(repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(editor/'project.cpack'),'linux'],env=env,cwd=repo,stdout=out,stderr=err,timeout=180)
report=json.loads((root/'build.json').read_text());assert (built is None or built.returncode==0) and report.get('tool',{}).get('ok'),report.get('diagnostics')
cases=['first-unverified','first-policy-block','post-login-policy-block','restart-cancel','unicode','turn-bad-json-after-delta','turn-invalid-utf8','restart-missing-runtime','restart-mismatch','restart-expired-auth','restart-offline','restart-unverified','restart-renewal-failure','turn-remote-bad-request','turn-rpc-error','turn-exit','turn-bad-json','turn-foreign-event','turn-remote-http','turn-completed-error','authenticated','logged-out','install','multiple-accounts','model-selection','single-model','configured-model','no-models','cancel-login','cancel-install','bad-install','cancel-probe','unsupported-runtime','identity-change','failed-login','switch-provider','install-empty-home','install-process-exit','install-initialize-error','install-account-error','install-model-error','install-mixed-homes','install-process-start-error','bundled-policy','user-bundle-settings','unexpected-extension','web-search-policy','browser-open-failed','login-expired','callback-port-conflict','callback-rpc-conflict','invalid-login-url','device-fallback','device-cancel','device-retry','method-cleanup-failed','plugins-existing','install-plugins','plugins-browser','plugins-change','plugins-budget','plugins-cancel','plugins-login-blocked','plugins-restart-exit','plugins-restart-initialize','plugins-restart-config','plugins-login-restart-exit','plugins-post-browser','plugins-restart-start','plugins-restart-file-change','plugins-login-restart-start']
if os.environ.get('CONFECTORY_ONBOARDING_CASES'):cases=os.environ['CONFECTORY_ONBOARDING_CASES'].split(',')
evidence=[];errors=[];external=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'])
 try:
  for name in cases:
   case=root/(name+'-'+uuid.uuid4().hex[:8] if reuse else name);case.mkdir();storage=case/'profile';control={'isolationFailure':{'plugins-restart-start':'start','plugins-restart-file-change':'file-change','plugins-restart-exit':'exit','plugins-restart-initialize':'initialize','plugins-restart-config':'config/read'}.get(name,''),'postLoginPlugins':name=='plugins-post-browser','pluginPreset':'changed-after-override' if name=='plugins-change' else 'budget' if name=='plugins-budget' else 'multiple' if name in ('plugins-existing','install-plugins','plugins-browser','plugins-cancel','plugins-login-blocked','plugins-restart-exit','plugins-restart-initialize','plugins-restart-config','plugins-login-restart-exit','plugins-post-browser','plugins-restart-start','plugins-restart-file-change','plugins-login-restart-start') else '', 'holdIsolation':name=='plugins-cancel','loginExpired':name=='login-expired','loginPortError':name=='callback-rpc-conflict','invalidBrowserUrl':name=='invalid-login-url','rejectExtension':name in ('unexpected-extension','first-policy-block','intro-policy-block'),'rejectSearch':name=='web-search-policy','bundledPolicy':name in ('bundled-policy','user-bundle-settings'),'singleModel':name=='single-model','noDefault':name in ('model-selection','single-model'),'noModels':name=='no-models','configuredModel':'fixture-two' if name=='configured-model' else '', 'preAuthFailure':'mixed-account-error' if name=='install-mixed-homes' else name.removeprefix('install-') if name in ('install-process-exit','install-initialize-error','install-account-error','install-model-error','install-process-start-error') else '', 'failLogin':name=='failed-login','holdVersion':name=='cancel-probe','holdDownload':name=='cancel-install','badArchive':name=='bad-install','version':'0.159.2' if name=='unsupported-runtime' else '0.159.0-alpha.3'}
   def write_control(**values):control.update(values);(case/'control.json').write_text(json.dumps(control))
   write_control(turnFailure=name.removeprefix('turn-') if name.startswith('turn-') else '');(root/'active.json').write_text(json.dumps({'case':str(case)}))
   absent=name.startswith('install-') or name in ('install','cancel-install','bad-install','intro-install');logged_out=name.startswith('install-') and name!='install-model-error' or name in ('intro-new-login','intro-install','intro-close-race','intro-stop-race','first-unverified','post-login-policy-block','plugins-browser','plugins-login-blocked','plugins-login-restart-exit','plugins-post-browser','plugins-login-restart-start','logged-out','install','cancel-login','cancel-install','bad-install','failed-login','switch-provider','browser-open-failed','login-expired','callback-port-conflict','callback-rpc-conflict','invalid-login-url','device-fallback','device-cancel','device-retry','method-cleanup-failed')
   discovery={'executables':[] if absent else [{'path':str(runtime),'selectable':True,'source':'owned fixture'}],'homes':[]}
   homes=[]
   for index in range(0 if name=='install-empty-home' else 2 if name in ('multiple-accounts','install-mixed-homes') else 1):
    home=case/('account-'+str(index));home.mkdir();(home/'original.keep').write_bytes(b'owned original account state\x00');homes.append(home);discovery['homes'].append({'path':str(home),'selectable':True,'source':'owned fixture'})
    if name=='user-bundle-settings':(home/'config.toml').write_text('[plugins."unified-computer-use@openai-bundled"]\nenabled = true\n')
    if not logged_out:(home/'.owned-account.json').write_text(json.dumps({'type':'chatgpt','email':('alice' if index==0 else 'bob')+'@fixture.invalid','planType':'plus'}))
   (root/'active-discovery.json').write_text(json.dumps(discovery))
   spec={'supported':True,'publisher':'OWNED FIXTURE','version':'0.159.0-alpha.3','target':'linux-x64','asset':'codex-owned.tar.gz','url':'http://127.0.0.1:'+str(server.server_port)+'/runtime','sha256':hashlib.sha256(archive).hexdigest(),'archiveKind':'tar.gz','archiveExecutable':'codex-owned','binaryName':'codex','rootBase':str(case/'managed'),'maxDownloadBytes':268435456,'maxUnpackedBytes':1073741824,'maxEntries':128,'downloadTimeoutSeconds':60}
   (root/'active-info.json').write_text(json.dumps(spec))
   if name=='first-unverified':
    storage.mkdir();(storage/'helper-agents.json').write_text(json.dumps({'version':1,'agents':{'Confectory.Agent.Codex::Connection':{'connection':'Confectory.Agent.Codex::Connection','config':{'connectionMethod':'local-cli','executable':str(runtime),'managedHome':str(homes[0]),'credentialReference':'codex:managed','model':'fixture-one'}}},'assignments':{}}))
   run_env=env.copy();run_env.update(CONFECTORY_ENTRY_STORAGE=str(storage),CONFECTORY_HOME_STORAGE=str(storage),CONFECTORY_MCP_DIRECTORY=str(case/'instances'));log_path=case/'host.log';log=log_path.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=run_env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   port_lease=None;login_recovery=False
   page=browser.new_page(viewport={'width':1440,'height':1000});page.add_init_script('''globalThis.__ownedBrowserOpens=[];globalThis.__ownedBrowserFailure=FAIL;Object.defineProperty(window,'confectoryWebUI',{value:Object.freeze({openCodexLogin(handle){globalThis.__ownedBrowserOpens.push(handle);return Promise.resolve({ok:!globalThis.__ownedBrowserFailure});}})});'''.replace('FAIL','true' if name=='browser-open-failed' else 'false').replace('Object.freeze({', '''Object.freeze({async chooseProjectParent(){return {ok:true,parent:'owned-parent',label:'Owned fixture projects'};},async createProject(title,description){const token=sessionStorage.getItem('confectory.webui.session');return (await fetch('/fixture/native-create',{method:'POST',headers:{'Content-Type':'application/json','X-Confectory-Session':token},body:JSON.stringify({title,description,bucket:globalThis.__projectBucket||'one'})})).json();},''' if name=='agent-common' else 'Object.freeze({'));page.on('pageerror',lambda e:errors.append(str(e)));invocations=[]
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
    page.route('**/*',route)
    if name in ('agent-common',) or name.startswith('intro-'):
     if name=='agent-common':from agent_common_consent import run as run_intro
     else:from intro_connection import run as run_intro
     context={'page':page,'browser':browser,'host':host,'log':log,'url':url,'origin':origin,'token':token,'case':case,'storage':storage,'repo':repo,'report':report,'run_env':run_env,'log_path':log_path,'requests':requests,'control':write_control,'errors':errors,'external':external,'scenario':name}
     try:run_intro(context)
     finally:page=context['page'];host=context['host'];log=context['log'];origin=context['origin'];token=context['token'];url=context['url']
     print('PASS scenario '+name,flush=True);continue
    goto_editor(page,url);page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);dialog.get_by_role('button',name='Codex',exact=True).click();expect(dialog.locator('[data-cli-login]')).to_be_enabled();assert not requests();expect(dialog.locator('[data-discover-connection]')).to_have_count(0);expect(dialog.locator('[data-mcp-panel]')).to_have_count(0);page.screenshot(path=str(case/'initial.png'))
    initial=state()
    if name=='first-unverified':
     expect(dialog.locator('[data-cli-login]')).to_have_text('로그인');expect(dialog.locator('[data-cli-retry],[data-cli-new-login],[data-cli-change-account]')).to_have_count(0);assert not requests();assert initial['helperAgents']['agents'][0]['readiness']['state']=='unverified';page.screenshot(path=str(case/'unverified-initial.png'));print('PASS scenario first-unverified',flush=True);continue
    assert initial['helperAgents']['agents']==[] and initial['projectId']==''
    expect(dialog.locator('[data-cli-login]')).to_have_text('로그인');expect(dialog.locator('[data-cli-retry],[data-cli-new-login],[data-cli-change-account]')).to_have_count(0)
    def clean_codex():
     forbidden='[data-connection-advanced],[data-discover-connection],[data-basic-check],[data-install-prepare],[data-login-prepare],[data-discover-models],[data-installation-candidates],[data-home-candidates],[data-candidate-kind],[data-install-target],[data-install-guide],[data-connection-field],[data-connection-save],[data-connection-attempt],[data-agent-register],[data-connection-refresh],[data-connection-back],[data-method-choice],input,select,textarea'
     expect(dialog.locator(forbidden)).to_have_count(0)
     text=dialog.inner_text()
     for phrase in ('이전 PackEngine','새로 준비한 AI','고급 설정','수동 지정','계정 참조','계정 정보 위치','실행 파일','플랫폼 선택','목록 새로 고침','설정 저장','조건 확인','준비 확인을 눌러'):
      assert phrase not in text,(phrase,text)
    def precheck_block():
     expect(dialog.locator('[data-codex-onboarding]')).to_have_attribute('data-step','preparation-blocked');expect(dialog.locator('[data-cli-login]')).to_have_text('로그인');expect(dialog.locator('[data-cli-retry],[data-cli-new-login]')).to_have_count(0);failure=state()['codexOnboarding'];assert failure['failureAction']=='setup' and failure['loginAttempted'] is False;return failure.get('canLogin',False)
    clean_codex()
    # Initial repeated clicks never start a second workflow.
    dialog.locator('[data-cli-login]').evaluate('(b)=>{b.click();b.click();}')
    if name=='first-policy-block':
     expect(dialog.locator('[data-cli-login]')).to_have_text('로그인');expect(dialog.locator('[data-codex-onboarding]')).to_have_attribute('data-step','preparation-blocked');expect(dialog.locator('[data-cli-retry],[data-cli-new-login]')).to_have_count(0);expect(dialog).to_contain_text('로그인은 아직 시작하지 않았어요');f=state()['codexOnboarding'];assert f['failureAction']=='setup' and f['loginAttempted'] is False;assert f['diagnostics']['failure']['detail']=='enabled-plugin-entry';assert not [r for r in requests() if r['method'] in ('account/read','account/login/start','model/list','turn/start')];page.screenshot(path=str(case/'preparation-blocked.png'));dialog.locator('[data-cli-login]').click();expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 로그인');assert not [r for r in requests() if r['method']=='account/login/start'];dialog.locator('[data-connection-cancel]').click();page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);dialog.get_by_role('button',name='Codex',exact=True).click();expect(dialog.locator('[data-cli-login]')).to_have_text('로그인');expect(dialog.locator('[data-cli-retry],[data-cli-new-login]')).to_have_count(0);print('PASS scenario first-policy-block',flush=True);continue
    if name=='bundled-policy' and os.environ.get('CONFECTORY_ONBOARDING_EXPECT_BUNDLED_FAILURE')=='1':
     expect(dialog.locator('[data-cli-retry]')).to_be_visible();diagnostic=state()['codexOnboarding']['diagnostics'];assert diagnostic['failure']['code']=='provider-tool-policy-unsupported' and diagnostic['failure']['stage']=='policy-check' and diagnostic['failure']['errorType']=='PlatformNotSupportedException' and diagnostic['failure']['processStarted'] is True,diagnostic
     assert 'detail' not in diagnostic['failure'];assert not [r for r in requests() if r['method'] in ('model/list','account/login/start','turn/start')];(case/'safe-diagnostics.json').write_text(json.dumps(diagnostic,indent=2));print('PASS reproduced bundled default plugin policy-check PlatformNotSupportedException',flush=True);continue
    if name in ('plugins-restart-exit','plugins-restart-initialize','plugins-restart-config','plugins-restart-start','plugins-restart-file-change'):
     login_recovery=precheck_block();blocked=state()['codexOnboarding']['diagnostics'];summary=blocked['failure']['pluginIsolation'];assert summary['overrideRequested'] is True and summary['overrideVerified'] is False and summary['effectiveRechecked'] is False;assert 'PRIVATE' not in json.dumps(blocked);assert len([r for r in requests() if r['method']=='process'])==(1 if name in ('plugins-restart-start','plugins-restart-file-change') else 2);assert not [r for r in requests() if r['method'] in ('model/list','account/login/start','thread/start','turn/start')];(case/'safe-diagnostics.json').write_text(json.dumps(blocked,indent=2));clean_codex();write_control(isolationFailure='');runtime.chmod(0o700);dialog.locator('[data-cli-login]').click()
    if name=='plugins-cancel':
     wait_file(case/'isolation-started');dialog.locator('[data-cli-stop]').click();expect(dialog.locator('[data-cli-login]')).to_be_visible();write_control(holdIsolation=False);assert not [r for r in requests() if r['method'] in ('model/list','account/login/start','turn/start')];dialog.locator('[data-cli-login]').click()
    if name in ('plugins-change','plugins-budget'):
     login_recovery=precheck_block();blocked=state()['codexOnboarding']['diagnostics'];summary=blocked['failure']['pluginIsolation'];assert blocked['failure']['detail']=='enabled-plugin-entry';assert summary['overrideVerified'] is False and summary['overrideRequested']==(name=='plugins-change');assert 'PRIVATE' not in json.dumps(blocked);assert not [r for r in requests() if r['method'] in ('model/list','account/login/start','turn/start')];(case/'safe-diagnostics.json').write_text(json.dumps(blocked,indent=2));clean_codex();page.screenshot(path=str(case/'policy-blocked.png'));write_control(pluginPreset='multiple');dialog.locator('[data-cli-login]').click()
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
     login_recovery=precheck_block();failure=state()['codexOnboarding'];assert len(state()['helperAgents']['agents'])==0;assert not [r for r in requests() if r['method'] in ('account/login/start','turn/start')]
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
     dialog.locator('[data-cli-login]').click()
     if name=='install-model-error' and not login_recovery:expect(dialog.locator('[data-cli-account]')).to_have_count(1)
     else:expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 로그인')
     assert (case/'download-count').read_text()=='1','retry repeated completed installation'
     for home in homes:assert (home/'original.keep').read_bytes()==b'owned original account state\x00'
     assert not [r for r in requests() if r['method'] in ('account/login/start','turn/start')]
     assert 'mcpBridge' not in invocations
     print('PASS scenario '+name,flush=True);continue
    if name in ('unexpected-extension','web-search-policy'):
     login_recovery=precheck_block();blocked=state()['codexOnboarding']['diagnostics'];assert blocked['failure']['stage']=='policy-check' and blocked['failure']['detail']==('enabled-plugin-entry' if name=='unexpected-extension' else 'startup-web-search'),blocked
     assert not [r for r in requests() if r['method'] in ('model/list','account/login/start','turn/start')];clean_codex();page.screenshot(path=str(case/'policy-blocked.png'));write_control(rejectExtension=False,rejectSearch=False);dialog.locator('[data-cli-login]').click()
    if name=='no-models':
     login_recovery=precheck_block();assert state()['helperAgents']['agents']==[];clean_codex();page.screenshot(path=str(case/'models-empty.png'));write_control(noModels=False);dialog.locator('[data-cli-login]').click()
    if logged_out or login_recovery or name=='multiple-accounts':
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
     if name=='post-login-policy-block':write_control(rejectSearch=True)
     (case/'complete-login').write_text('owned')
     if name=='post-login-policy-block':
      expect(dialog.locator('[data-cli-retry]')).to_have_text('연결 다시 확인');expect(dialog).to_contain_text('로그인 절차는 끝났어요');expect(dialog.locator('[data-cli-new-login]')).to_have_count(0);f=state()['codexOnboarding'];assert f['failureAction']=='connection' and f['loginAttempted'] is True and f['loginCompleted'] is True;assert f['diagnostics']['failure']['detail']=='startup-web-search';page.screenshot(path=str(case/'login-complete-connection-blocked.png'));before=len([r for r in requests() if r['method']=='account/login/start']);account_checks=sum(r['method']=='account/read' for r in requests());dialog.locator('[data-cli-retry]').click()
      for _ in range(500):
       if sum(r['method']=='account/read' for r in requests())>account_checks:break
       page.wait_for_timeout(10)
      else:raise AssertionError('connection retry did not perform fresh account check')
      expect(dialog.locator('[data-cli-retry]')).to_be_enabled();expect(dialog.locator('[data-cli-retry]')).to_have_text('연결 다시 확인');assert state()['codexOnboarding']['loginCompleted'] is True;assert len([r for r in requests() if r['method']=='account/login/start'])==before;write_control(rejectSearch=False);dialog.locator('[data-cli-retry]').click()
     if name in ('failed-login','login-expired'):
      expect(dialog.locator('[data-cli-retry]')).to_be_visible();clean_codex();page.screenshot(path=str(case/'login-failed.png'));assert state()['codexOnboarding']['diagnostics']['failure']['code']==('login_timeout' if name=='login-expired' else 'login_not_completed');write_control(failLogin=False,loginExpired=False);(case/'complete-login').unlink();dialog.locator('[data-cli-retry]').click();expect(dialog.locator('[data-cli-consent]')).to_have_text('동의하고 로그인');dialog.locator('[data-cli-consent]').click();expect_browser();(case/'complete-login').write_text('owned')
    else:
     expect(dialog.locator('[data-cli-account]')).to_have_count(1);clean_codex();page.screenshot(path=str(case/'account-choice.png'))
     assert 'alice@fixture.invalid' in dialog.locator('[data-cli-account]').first.inner_text()
     # A foreign selection token cannot become an account or registration.
     rejected=api('choose-account',token='foreign-token',account='foreign-account');assert not rejected['ok'];assert state()['helperAgents']['agents']==[]
     choice=state()['codexOnboarding'];rejected=api('choose-account',token=choice['token'],account='foreign-account');assert not rejected['ok'];assert state()['helperAgents']['agents']==[]
     dialog.locator('[data-cli-account]').first.click();assert api('choose-account',token=choice['token'],account=choice['accounts'][0]['id'])['ok']
    expect(dialog.locator('[data-cli-done]')).to_be_enabled(timeout=40000);clean_codex();page.screenshot(path=str(case/'ready.png'));ready=state();assert ready['projectId']=='' and len(ready['helperAgents']['agents'])==1;agent=ready['helperAgents']['agents'][0];assert agent['state']=='ready' and agent['accountVerified'] is False and agent['accountMetadataVerified'] is True,agent
    assert agent['model']==('fixture-two' if name=='configured-model' else 'fixture-one')
    expected_email='new-account@fixture.invalid' if logged_out or login_recovery or name=='multiple-accounts' else 'alice@fixture.invalid';assert agent['accountIdentity']['email']==expected_email,agent
    assert not [r for r in requests() if r['method']=='turn/start']
    before=len(requests());dialog.locator('[data-cli-done]').click();expect(dialog).to_have_count(0)
    page.locator('#add-agent').click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True);dialog.get_by_role('button',name='Codex',exact=True).click();expect(dialog.locator('[data-cli-done]')).to_be_enabled();assert len(requests())==before,'reopen repeated completed steps'
    dialog.locator('[data-cli-offline]').click();expect(dialog.locator('[data-cli-login]')).to_have_text('다시 연결');assert state()['helperAgents']['agents'][0]['state']=='offline';dialog.locator('[data-cli-login]').click();expect(dialog.locator('[data-cli-done]')).to_be_enabled();assert state()['helperAgents']['agents'][0]['state']=='ready' and len(requests())==before
    dialog.locator('[data-cli-done]').click()
    if name=='chat-use':
     from codex_chat_use import run as run_chat_use
     context={'page':page,'browser':browser,'host':host,'log':log,'url':url,'origin':origin,'token':token,'case':case,'root':root,'storage':storage,'repo':repo,'report':report,'run_env':run_env,'log_path':log_path,'requests':requests,'control':write_control,'errors':errors,'external':external}
     try:run_chat_use(context)
     finally:page=context['page'];host=context['host'];log=context['log'];origin=context['origin'];token=context['token'];url=context['url']
     print('PASS scenario chat-use',flush=True);continue
    if name in ('authenticated','unicode') or name.startswith(('turn-','restart-')):
     if name=='unicode':write_control(replyText='OWNED CLI HELPER REPLY 한글 😀 "따옴표"\n{plain delta: [not JSON]}',splitUtf8=True)
     page.locator('#add-helper').click();creator=page.locator('[data-v508-helper]');creator.locator('#participant-name').fill('Owned CLI Helper');creator.locator('#participant-description').fill('Owned account metadata and protocol only');creator.locator('button[type=submit]').click();expect(creator).to_have_count(0);page.locator('.home-side [data-helper]').first.click();card=page.locator('.participant-expanded-card');card.locator('textarea').fill('owned CLI message');card.locator('[data-global-send]').click();expect(page.locator('[data-chat-use-consent]')).to_be_visible();page.locator('[data-chat-use-allow]').click();expect(page.locator('[data-global-approval]')).to_have_count(0);expect(card.locator('textarea')).to_have_value('')
     if name.startswith('turn-'):
      expected={'turn-remote-bad-request':('provider-error','response-events','badRequest'),'turn-rpc-error':('provider-error','turn-start','rpcErrorCode=-32602'),'turn-exit':('provider-error','turn-start','exitCode=37'),'turn-bad-json':('provider-error','response-events','frame-parse'),'turn-bad-json-after-delta':('provider-error','response-events','frame-parse'),'turn-invalid-utf8':('provider-error','response-events','frame-read'),'turn-foreign-event':('provider-error','response-events',None),'turn-remote-http':('provider-http-error','response-events','httpStatusCode=503'),'turn-completed-error':('provider-auth-required','response-events','httpStatusCode=403')}[name]
      for value in expected:
       if value and not (name=='turn-invalid-utf8' and value=='response-events'):expect(card.locator('.messages')).to_contain_text(value)
      terminal=next(iter(state()['helperAgents']['turns'].values()));assert terminal['state']=='error' and terminal['errorCode']==expected[0];assert terminal['errorDiagnostics']['stage'] in (('turn-start','response-events') if name=='turn-invalid-utf8' else (expected[1],));assert 'PRIVATE' not in json.dumps(terminal) and 'NEVER-EXPOSE' not in json.dumps(terminal);assert not any(k in terminal['errorDiagnostics'] for k in ('message','path','stderr','accountIdentity','fingerprint'))
      if name in ('turn-bad-json','turn-bad-json-after-delta','turn-invalid-utf8'):
       assert terminal['errorDiagnostics'].get('protocolEvent','')==''
       assert terminal['errorDiagnostics']['errorType']==('DecoderFallbackException' if name=='turn-invalid-utf8' else 'JsonException')
      card.locator('[data-close]').click();page.locator('.home-side [data-helper]').first.click();expect(card.locator('.messages')).to_contain_text(expected[0]);page.screenshot(path=str(case/'safe-helper-error.png'))
     else:
      expect(card.locator('.messages')).to_contain_text('OWNED CLI HELPER REPLY',timeout=30000)
      if name=='unicode':
       expect(card.locator('.messages')).to_contain_text('한글 😀 "따옴표"');expect(card.locator('.messages')).to_contain_text('{plain delta: [not JSON]}');assert next(iter(state()['helperAgents']['turns'].values()))['output']=='OWNED CLI HELPER REPLY 한글 😀 "따옴표"\n{plain delta: [not JSON]}'
      page.screenshot(path=str(case/'helper-reply.png'))
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
     if name=='restart-cancel':write_control(holdAccount=True)
     if name=='restart-missing-runtime':runtime.rename(root/'codex-hidden')
     if name=='restart-mismatch':write_control(readEmail='different@fixture.invalid')
     if name=='restart-expired-auth':write_control(hideAccount=True)
     if name=='restart-renewal-failure':write_control(preAuthFailure='account-error')
     registered_bytes=registry_file.read_bytes();login_count=len([r for r in requests() if r['method']=='account/login/start']);page.close();os.killpg(host.pid,signal.SIGTERM);host.wait(timeout=15);log.close();log=log_path.open('w');host=subprocess.Popen(report['run'],cwd=repo,env=run_env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
     for _ in range(600):
      urls=[line.split(' ',1)[1] for line in log_path.read_text().splitlines() if line.startswith('CONFECTORY_WEB_UI ')]
      if urls:url=urls[-1];break
      assert host.poll() is None;time.sleep(.1)
     origin,token=url.split('/#');page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)));page.route('**/*',route);page.goto(url)
     # No settings/Helper click or send triggers readiness: wait at Home first.
     expected_state={'restart-cancel':'checking','restart-mismatch':'account-mismatch','restart-expired-auth':'auth-required','restart-offline':'offline','restart-unverified':'unverified','restart-renewal-failure':'blocked','restart-missing-runtime':'missing-runtime'}.get(name,'ready')
     for _ in range(600):
      if state()["helperAgents"]["agents"][0]["readiness"]["state"]==expected_state:break
      time.sleep(.05)
     else:raise AssertionError(state()["helperAgents"])
     settled=state()['helperAgents']['agents'][0];assert settled['readiness']['state']==expected_state
     if expected_state!='ready':
      expect(page.locator('.welcome #later')).to_be_enabled();assert not page.locator('.home-grid').count();page.locator('.welcome #later').click()
     expect(page.locator('#add-agent')).to_be_enabled(timeout=30000)
     page.screenshot(path=str(case/'startup-home.png'))
     checks_before=len(requests());page.locator('.home-side [data-agent]').first.click();dialog=page.get_by_role('dialog',name='Agent 추가',exact=True)
     if expected_state=='checking':expect(dialog.locator('[data-cli-stop]')).to_be_enabled()
     elif expected_state=='ready':expect(dialog.locator('[data-cli-done]')).to_be_enabled();expect(dialog.locator('[data-cli-login]')).to_have_count(0);expect(dialog.locator('[data-cli-account]')).to_have_count(0)
     elif expected_state=='offline':expect(dialog.locator('[data-cli-login]')).to_have_text('다시 연결')
     elif expected_state=='unverified':expect(dialog.locator('[data-cli-login]')).to_have_text('로그인');expect(dialog.locator('[data-cli-retry],[data-cli-new-login]')).to_have_count(0)
     else:expect(dialog.locator('[data-codex-onboarding]')).to_have_attribute('data-step','connection-blocked')
     assert len(requests())==checks_before,'opening settings repeated startup/login work';page.screenshot(path=str(case/'startup-settings.png'))
     if name=='restart-cancel':
      dialog.locator('[data-cli-stop]').click();expect(dialog.locator('[data-cli-retry]')).to_be_enabled();assert state()['helperAgents']['agents'][0]['readiness']['state']=='cancelled';checks=len(requests());page.wait_for_timeout(300);assert len(requests())==checks;page.screenshot(path=str(case/'startup-cancelled.png'));write_control(holdAccount=False);dialog.locator('[data-cli-retry]').click();expect(dialog.locator('[data-cli-done]')).to_be_enabled();assert state()['helperAgents']['agents'][0]['readiness']['state']=='ready'

     dialog.locator('[data-close]').click()
     expect(dialog).to_have_count(0)
     before=len(requests());page.locator('.home-side [data-helper]').first.click();card=page.locator('.participant-expanded-card');expect(card.locator('.messages')).to_contain_text('owned CLI message');expect(card.locator('.messages')).to_contain_text('OWNED CLI HELPER REPLY');assert len(requests())==before;card.locator('textarea').fill('owned after restart')
     if name=='restart-offline':card.locator('form').evaluate('e=>e.requestSubmit()')
     else:card.locator('textarea').press('Enter')
     if name.startswith('restart-') and name!='restart-cancel':
      expected={'restart-mismatch':'codex-account-mismatch','restart-expired-auth':'provider-auth-required','restart-offline':'codex-readiness-changed','restart-unverified':'codex-registration-unverified','restart-renewal-failure':'provider-account-query-failed','restart-missing-runtime':'codex-runtime-missing'}[name];expect(page.locator('#toast')).to_contain_text(expected);expect(card.locator('textarea')).to_have_value('owned after restart');assert len([r for r in requests() if r['method']=='turn/start'])==1
      if name in ('restart-offline','restart-unverified','restart-missing-runtime'):assert len(requests())==before
      page.screenshot(path=str(case/'cold-blocked.png'))
     else:
      expect(card.locator('.messages')).to_contain_text('owned after restart');expect(card.locator('textarea')).to_have_value('');expect(card.locator('[data-global-send]')).to_have_text('보내기');assert len([r for r in requests() if r['method']=='turn/start'])==2;page.screenshot(path=str(case/'cold-auto-reply.png'))
      # Repeated sends use the renewed lease without another preflight process.
      checks=sum(r['method']=='account/read' for r in requests());card.locator('textarea').fill('same verified session');card.locator('textarea').press('Enter');expect(card.locator('textarea')).to_have_value('');expect(card.locator('[data-global-send]')).to_have_text('보내기');assert sum(r['method']=='account/read' for r in requests())==checks+1
     assert registry_file.read_bytes()==registered_bytes,'readiness changed saved registration';assert len([r for r in requests() if r['method']=='account/login/start'])==login_count;assert page.locator('[data-codex-onboarding]').count()==0
     if name=='restart-missing-runtime':(root/'codex-hidden').rename(runtime)
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
